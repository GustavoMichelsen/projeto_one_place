import inflection
import re

import pandas     as pd
import numpy      as np
import umap.umap_ as umap


from sklearn.preprocessing   import MinMaxScaler, RobustScaler
from scipy.cluster.hierarchy import linkage, fcluster


class One_place(object):
    def __init__(self):
        pass

    # function for numbers extraction in stock_code
    def extraction(self, x):
        match = re.search('\d+', x)
        if match:
            return match.group(0)
        else:
            return None
    
    def data_cleaning(self, df):
        # Rename coluns
        old_columns = df.columns
        snekecase = lambda x: inflection.underscore(x)
        new_columns = list(map(snekecase, old_columns))
        df.columns = new_columns

        # replacement of missing customer_id
        aux1 = df[df['customer_id'].isna()][['invoice_no', 'customer_id']].drop_duplicates(subset='invoice_no').reset_index(drop=True)

        for i in range(len(aux1)):
            aux1.loc[i, 'customer_id'] = 100000 + i

        df = df.merge(aux1, on='invoice_no', how='left')

        df['customer_id'] = df['customer_id_x'].combine_first(df['customer_id_y'])
        df.drop(columns=['customer_id_x', 'customer_id_y'], inplace=True)

        # Charge Dtypes
        df['invoice_date'] = pd.to_datetime(df['invoice_date'])

        return df
        
    def fearture_engineering(self, df):
        # Rwithdrawal of stock items that contain only letters
        df = df[df['stock_code'].str.match('^(?![a-zA-Z]+$).+')].reset_index(drop=True)
        df = df[df['stock_code'] != 'BANK CHARGES']
        
        # Extraction of the number in the stock_code, keeping only the unique identification.
        df['stock'] = df['stock_code'].apply(lambda x: self.extraction(x))

        # Total purchase amount
        df['total_price'] = df['quantity'] * df['unit_price']

        # Variable count
        aux1 = df[['invoice_no', 'stock']].groupby('invoice_no').count().reset_index()
        aux1.columns = ['invoice_no', 'distinct_itens']

        # Variable sum
        aux2 = df.groupby('invoice_no').sum().reset_index()

        # Summarized DataFrame
        df_new = df[['invoice_no', 'customer_id', 'invoice_date', 'country']].merge(aux2[['invoice_no', 'quantity', 'total_price']], 
                                                                 how='left', 
                                                                 on='invoice_no')

        df_new = df_new.merge(aux1[['invoice_no', 'distinct_itens']], how='left', on='invoice_no')

        # Drop of duplicate items
        df_new.drop_duplicates(inplace=True, ignore_index=True)

        # ----------------------------------------------
        # The Feature Engineering are based in RFM model
        # ----------------------------------------------
        
        # -------------------------
        #          Recency
        # -------------------------
        
        # Average purchase recency (days elapsed between purchases)
        df_new['recency'] = df_new.apply(lambda x: (df_new[df_new['customer_id'] == x['customer_id']]['invoice_date'].max() - 
                                                      x['invoice_date']).days, axis=1)
        aux1 = df_new[['customer_id', 'recency']].groupby('customer_id').mean().reset_index().rename(columns={'recency':'recency_mean'})
        df_new = df_new.merge(aux1, how='left', on='customer_id')

        # Days of last purchase
        df_new['last_purchase_days'] = df_new['invoice_date'].apply(lambda x: (df_new['invoice_date'].max() - x).days)

        # -------------------------
        #         Frequency
        # -------------------------
        
        aux1 = df_new[['customer_id', 'invoice_no']].groupby('customer_id').count().reset_index().rename(columns={'invoice_no':'frequency'})
        df_new = df_new.merge(aux1, how='left', on='customer_id')

        # -------------------------
        #          Monetary
        # -------------------------

        # # Average of total items purchase
        # aux1 = df_new[['customer_id', 'quantity']][df_new['quantity'] >= 0].groupby('customer_id').mean().reset_index().rename(columns={'quantity':'mean_purchase_qtt'})
        # df_new = df_new.merge(aux1, how='left', on='customer_id')
        # df_new['mean_purchase_qtt'] = df_new['mean_purchase_qtt'].apply(lambda x: 0 if np.isnan(x) else x)

        # # Average of returned items
        # aux1 = df_new[['customer_id', 'quantity']][df_new['quantity'] < 0].groupby('customer_id').mean().reset_index().rename(columns={'quantity':'mean_return_qtt'})
        # df_new = df_new.merge(aux1, how='left', on='customer_id')
        # df_new['mean_return_qtt'] = df_new['mean_return_qtt'].apply(lambda x: 0 if np.isnan(x) else -(x))

        # Total of purchase items
        aux1 = df_new[['customer_id', 'quantity']][df_new['quantity'] >= 0].groupby('customer_id').sum().reset_index().rename(columns={'quantity':'total_itens_purchase'})
        df_new = df_new.merge(aux1, how='left', on='customer_id')
        df_new['total_itens_purchase'] = df_new['total_itens_purchase'].apply(lambda x: 0 if np.isnan(x) else x)

        # Total of returned items
        aux1 = df_new[['customer_id', 'quantity']][df_new['quantity'] < 0].groupby('customer_id').sum().reset_index().rename(columns={'quantity':'total_itens_return'})
        df_new = df_new.merge(aux1, how='left', on='customer_id')
        df_new['total_itens_return'] = df_new['total_itens_return'].apply(lambda x: 0 if np.isnan(x) else -(x))

        # Average of differente items in cart
        aux1 = df_new[['customer_id', 'distinct_itens']].groupby('customer_id').mean().reset_index().rename(columns={'distinct_itens':'distinct_itens_mean'})
        df_new = df_new.merge(aux1, how='left', on='customer_id')

        # Average purchase price
        aux1 = df_new[['customer_id', 'total_price']].groupby('customer_id').mean().reset_index().rename(columns={'total_price':'mean_price'})
        df_new = df_new.merge(aux1, how='left', on='customer_id')

        # Total purchase price
        df_new['total_sale_amount'] = df_new['customer_id'].apply(lambda x: df_new[df_new['customer_id'] == x]['total_price'].sum())

        # -------------------------
        #        Data Sumary
        # -------------------------
        
        df_new.columns

        df_new = df_new.drop_duplicates(subset=['customer_id'], ignore_index=True)
        df_new.drop(columns=['invoice_no', 'invoice_date', 'quantity', 'total_price', 'distinct_itens', 'recency'], inplace=True)

        # -------------------------
        #    Countries Lat-Long
        # -------------------------
        
        df_countries = pd.read_csv('countries.csv', sep=';')

        # Troca de nome dos países
        df_new['country'] = df_new['country'].apply(lambda x: 'Ireland'        if x == 'EIRE'               else
                                                              'United Kingdom' if x == 'Channel Islands'    else
                                                              'United States'  if x == 'USA'                else
                                                              'South Africa'   if x == 'RSA'                else
                                                              'Luxembourg'     if x == 'European Community' else x)
        # Drop of the rows where country are 'Unspecified'
        df_new = df_new[~(df_new['country'] == 'Unspecified')]

        # Setting the lat and long of the countries
        df_countries = df_countries[df_countries['name'].isin(df_new['country'].unique())].reset_index(drop=True)

        # Adding the lat and long in the DataFrame
        df_new = df_new.merge(df_countries[['name', 'latitude', 'longitude']], left_on='country', right_on='name', how='left')

        # Deleting duplicate information
        df_new.drop(columns=['name'], inplace=True)

        # -------------------------
        #           Drops
        # -------------------------
        
        # Drop the clients_id 13256, 103383, 103312 due to strange behavior
        df_new = df_new[~df_new['customer_id'].isin([13256, 103383, 103312])].reset_index(drop=True)
        
        return df_new
    
    def data_preparation(self, df):
        mm = MinMaxScaler()
        re = RobustScaler()

        df['recency_mean']         = re.fit_transform(df[['recency_mean'         ]])
        df['last_purchase_days']   = mm.fit_transform(df[['last_purchase_days'   ]])
        df['frequency']            = re.fit_transform(df[['frequency'            ]])
        # df['mean_purchase_qtt']    = re.fit_transform(df[['mean_purchase_qtt'    ]])
        # df['mean_return_qtt']      = re.fit_transform(df[['mean_return_qtt'      ]])
        df['total_itens_purchase'] = re.fit_transform(df[['total_itens_purchase' ]])
        df['total_itens_return']   = re.fit_transform(df[['total_itens_return'   ]])
        df['distinct_itens_mean']  = re.fit_transform(df[['distinct_itens_mean'  ]])
        df['mean_price']           = re.fit_transform(df[['mean_price'           ]])
        df['total_sale_amount']    = re.fit_transform(df[['total_sale_amount'    ]])
        df['latitude']             = mm.fit_transform(df[['latitude'             ]])
        df['longitude']            = mm.fit_transform(df[['longitude'            ]])
        
        return df
        
    def get_prediction( self, df):
        ## ------------------------------
        ##       Feature Selection
        ## ------------------------------
        X = df[[
               'recency_mean', 
               'last_purchase_days', 
               'frequency',
               'total_itens_purchase', 
               'total_itens_return',
               'distinct_itens_mean', 
               'mean_price', 
               'total_sale_amount', 
               'latitude',
               'longitude'
              ]].copy()


        ## ------------------------------
        ##           Embedding
        ## ------------------------------
        df_umap = pd.DataFrame()

        reducer = umap.UMAP( random_state=42 )
        embedding = reducer.fit_transform(X)

        # embedding
        df_umap['embedding_x'] = embedding[:, 0]
        df_umap['embedding_y'] = embedding[:, 1]

        ## ------------------------------
        ##       Modeling - HC model
        ## ------------------------------

        # model and Training
        hc_model = linkage(df_umap[['embedding_x', 'embedding_y']], 'ward')

        # Predict
        labels = fcluster(hc_model, 8, criterion='maxclust')
        
        ## ------------------------------
        ##            Labels
        ## ------------------------------
        
        df['labels'] = labels
        aux1 = df[['labels', 'total_sale_amount']].groupby('labels').sum().reset_index().sort_values('total_sale_amount', ascending=False).reset_index(drop=True)
        aux1['labels_name'] =  ['insiders', 'more_frequency', 'captivate_customer', 'more_itens',
                                'single_purchase','to_encourage', 'so_far_away', 'lost_clientes']
        groups = {}

        for n in range(len(aux1)):
            groups[aux1.loc[n, 'labels']] = aux1.loc[n, 'labels_name']

        df['labels'] = df['labels'].replace(groups)

        return df