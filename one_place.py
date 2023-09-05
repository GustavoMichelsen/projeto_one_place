import streamlit            as st
import pandas               as pd
import plotly_express       as px
import plotly.graph_objects as go
import numpy                as np

import base64
import datetime
import inflection

st.set_page_config(layout='wide')

# Código CSV
csv = """
<style>
    .centralizacao{
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .row {
        display: flex;
    }
    .column {
        padding: 5px;
        box-sizing: border-box;
        
        border-top:1px solid #ccc;
        border-bottom:1px solid #ccc;
        margin-bottom: 5px;
    }
    .head-l {
        width: 20%;
        border-left:1px solid #ccc;
    }
    .head-l img {
        width: 100%;
        height: auto;
        object-fit: cover;
    }
    .head-r {
        width: 80%;
        border-right:1px solid #ccc;

        margin-bottom: 5px;
    }

    .head-r h2 {
        text-align: center;
    }

    .rel-geral{
        width: 100%;
        border-left:1px solid #ccc;
        border-right:1px solid #ccc;
    }
    
    .rel-geral-col1{
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .block{
        width: 80%;
        height: 175px;
        margin-bottom: 5px;
    }

    .block p{
        text-indent:5%;
        color: white;
        font-size:18px;
        font-weight:bold;
    }

    .resultado{
        color: white;
        font-size:28px;
        font-weight:bold;
        display: block;
        text-align: center;
        margin: 0 auto;
    }
    
    .barra {
        width: 100%;
        height: 55px;
        display: flex;
        margin-bottom: 5px;
    }

    .segmento {
        flex: 1;
        display: flex;
        text-align: center;
        padding-top:15px;;
    }

    .segmento:nth-child(1) { background-color: #6e0a98; }
    .segmento:nth-child(2) { background-color: #7d3b97; }
    .segmento:nth-child(3) { background-color: #8825b1; }
    .segmento:nth-child(4) { background-color: #8d4ba7; }
    .segmento:nth-child(5) { background-color: #a140cb; }
    .segmento:nth-child(6) { background-color: #9e5ab8; }
    .segmento:nth-child(7) { background-color: #bb5ae4; }
    .segmento:nth-child(8) { background-color: #d475fd; }

    .segmento p{
        color: white;
        font-weight:bold;
        font-size:16px;
    }

    .grupo_fidelidade_col1 {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top:20px;
    }

    .block_gf{
        width: 80%;
        height: 100px;
        margin-bottom: 5px;
    }

    .block_gf p{
        text-indent:5%;
        color: white;
        font-size:18px;
        font-weight:bold;
    }

    /* Elementos do StreamLit*/
    .css-j5r0tf {
        border:1px solid #ccc;
    }

    .css-keje6w {
        border:1px solid #ccc;
    }

    .css-1bzkvni {
        border:1px solid #ccc;
    }
    
    .st-b8{
        width: 99.5%;
    }

    .css-fplge5 {
        border:1px solid #ccc;
    }

</style>
"""

def load_data(path):
    df = pd.read_csv(path)
    df['total_price'] = df['unit_price'] * df['quantity']
    df['invoice_date'] = pd.to_datetime(df['invoice_date'])
    df['day'] = df['invoice_date'].dt.day
    df['month'] = df['invoice_date'].dt.month
    df['year'] = df['invoice_date'].dt.year
    # Troca de nome dos países
    df['country'] = df['country'].apply(lambda x: 'Ireland'        if x == 'EIRE'               else
                                                  'United Kingdom' if x == 'Channel Islands'    else
                                                  'United States'  if x == 'USA'                else
                                                  'South Africa'   if x == 'RSA'                else
                                                  'Luxembourg'     if x == 'European Community' else x)
    return df

# ------------------------------
#             Head
# ------------------------------
def head(df):  
    # Renderiza o código csv
    st.markdown(csv, unsafe_allow_html=True)

    # Carrega imagem png para o código html
    file_ = open("image/one_place.png", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    # Insere o código HTML
    st.markdown(f'''
                <div class="row">
                    <div class="column head-l">
                        <img src="data:image/gif;base64,{data_url}" alt="">
                    </div>
                    <div class="column head-r centralizacao">
                        <h2> Faturamento dos Grupos </h2>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
    
# ------------------------------
#       Relatório Geral
# ------------------------------
def general_report(df):


    with st.container():
        st.markdown(f'''
                    <div class="row">
                        <div class="column rel-geral centralizacao">
                        <h4>Visão Geral</h4>
                    </div>
                    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 5, 3])

    with col1:
        total_billing = st.date_input(  "Período de Faturamento",
                                        (datetime.date(2017, 12, 1), datetime.date(2017, 12, 7)),
                                        datetime.date(2016, 11, 29),
                                        datetime.date(2017, 12, 7)
                                    )
        
        if len(total_billing) == 1:
            date_begin = total_billing[0]
            date_end = total_billing[0]
        else:
            date_begin, date_end = total_billing

        fat_total = df[(df['invoice_date'] >= date_begin.strftime('%Y-%m-%d')) & (df['invoice_date'] <= date_end.strftime('%Y-%m-%d'))]['total_price'].sum()
        sales_total = df[(df['invoice_date'] >= date_begin.strftime('%Y-%m-%d')) & (df['invoice_date'] <= date_end.strftime('%Y-%m-%d'))]['quantity'].sum()
        unique_sales = len(df[(df['invoice_date'] >= date_begin.strftime('%Y-%m-%d')) & (df['invoice_date'] <= date_end.strftime('%Y-%m-%d'))][['invoice_no','customer_id']].groupby('invoice_no').count())
        mean_ticket = fat_total/unique_sales

        st.markdown(f'''
                    <div class="rel-geral-col1">
                        <div class="block" style="background-color: #ffc000;">
                            <p>Vendas</p>
                            <span class="resultado"> {sales_total} </span>
                        </div> 
                        <div class="block" style="background-color: #00b050;">
                            <p>
                                Faturamento
                            </p>
                            <span class="resultado"> $ {fat_total:.02f} </span>
                        </div> 
                        <div class="block" style="background-color: #0070c0;">
                            <p>
                                Ticket Médio
                            </p>
                            <span class="resultado"> $ {mean_ticket:.02f} </span>
                        </div> 
                    </div>
                    ''', unsafe_allow_html=True)
        st.title("")

    with col2:
        st.title("")
        st.title("")
        st.title("")
        # ------    VENDAS    ------
        aux1 = df[['year', 'month', 'quantity', 'total_price']].groupby(['year', 'month']).sum().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=aux1[aux1['year'] == 2016]['month'],
                             y=aux1[aux1['year'] == 2016]['quantity'],
                             name='2016',
                             marker_color='#ffd966'))
        fig.add_trace(go.Bar(x=aux1[aux1['year'] == 2017]['month'],
                             y=aux1[aux1['year'] == 2017]['quantity'],
                             name='2017',
                             marker_color='#ffc000'))
        fig.update_layout(height=150,
                          title="Vendas",
                          xaxis_title = "Mês",
                          yaxis_title = "Vendas",
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)')
        fig.update_layout(margin={'r': 0, 't': 25, 'l': 0, 'b': 0}, coloraxis_showscale=False)

        st.plotly_chart(fig, use_container_width=True)

        # ------ FATURAMENTO  ------
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=aux1[aux1['year'] == 2016]['month'],
                             y=aux1[aux1['year'] == 2016]['total_price'],
                             name='2016',
                             marker_color='#a9d08e'))
        fig.add_trace(go.Bar(x=aux1[aux1['year'] == 2017]['month'],
                             y=aux1[aux1['year'] == 2017]['total_price'],
                             name='2017',
                             marker_color='#00b050'))
        fig.update_layout(height=150,
                          title="Faturamento",
                          xaxis_title = "Mês",
                          yaxis_title = "Faturamento",
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)')
        fig.update_layout(margin={'r': 0, 't': 25, 'l': 0, 'b': 0}, coloraxis_showscale=False)

        st.plotly_chart(fig, use_container_width=True)

        # ------ TICKET MEDIO ------
        aux1 = df[['year', 'month', 'total_price']].groupby(['year', 'month']).sum().reset_index()
        aux1 = aux1.merge(df.drop_duplicates(subset='invoice_no')[['year', 'month', 'invoice_no']].groupby(['year', 'month']).count().reset_index(), how='left', on=['year', 'month'])
        aux1['mean_ticket'] = aux1['total_price'] / aux1['invoice_no']

        fig = go.Figure()
        fig.add_trace(go.Bar(x=aux1[aux1['year'] == 2016]['month'],
                             y=aux1[aux1['year'] == 2016]['mean_ticket'],
                             name='2016',
                             marker_color='#8ea9db'))
        fig.add_trace(go.Bar(x=aux1[aux1['year'] == 2017]['month'],
                             y=aux1[aux1['year'] == 2017]['mean_ticket'],
                             name='2017',
                             marker_color='#0070c0'))
        fig.update_layout(height=150,
                          title="Ticket Médio",
                          xaxis_title = "Mês",
                          yaxis_title = "Ticket Médio",
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)')
        fig.update_layout(margin={'r': 0, 't': 25, 'l': 0, 'b': 0}, coloraxis_showscale=False)

        st.plotly_chart(fig, use_container_width=True)

    
    with col3:
        st.markdown(f'''
                    <div class="centralizacao">
                    <h4>Países Atendidos</h4>
                    </div>
                    ''', unsafe_allow_html=True)

        aux1 = df[['country', 'invoice_no', 'customer_id']].groupby(['country', 'invoice_no']).count().reset_index()
        aux1 = aux1[['country', 'invoice_no']].groupby('country').count().sort_values(by='invoice_no', ascending=False).reset_index()

        s = 0
        for i in range(20, len(aux1)):
            s = s + aux1.loc[i, 'invoice_no']
            
        aux1.drop(range(20, len(aux1)), axis=0, inplace=True)

        aux1 = pd.concat([aux1,pd.DataFrame(data={'country':['Outros'], 'invoice_no':[s]})], axis=0, ignore_index=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=aux1['invoice_no'],
                             y=aux1['country'],
                             name='Pedidos',
                             marker_color='#f89402',
                             orientation='h'))
        fig.update_layout(height=575,
                          title="Total de Pedidos",
                          xaxis_title = "Total",
                          yaxis_title = "País",
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)')
        fig.update_layout(margin={'r': 0, 't': 25, 'l': 0, 'b': 0}, 
                          coloraxis_showscale=False,
                          yaxis={'categoryorder':'total ascending'})

        st.plotly_chart(fig, use_container_width=True)

# ------------------------------
#     Grupos de Fidelidade
# ------------------------------
def loyalty_groups(df):
    # ------ TÍTULO ------
    with st.container():
        st.markdown(f'''
                    <div class="row">
                        <div class="column rel-geral centralizacao">
                        <h4>Grupos de Fidelidade</h4>
                    </div>
                    ''', unsafe_allow_html=True)
    
    # ------ TABELA AUXILIARES ------

    aux1 = df[df['customer_id'] < 100000][['customer_id', 'labels']].drop_duplicates(subset='customer_id').reset_index(drop=True)
    aux1 = aux1.groupby('labels').count().sort_values(by='customer_id', ascending=False).reset_index()
    aux1['perc'] = aux1['customer_id'] / aux1['customer_id'].sum()
    aux1['labels'] = aux1['labels'].apply(lambda x: inflection.titleize(x))

    aux2 = aux1.copy()
    perc = 0
    cust = 0
    for n in range(len(aux2)):
        if aux2.loc[n, 'perc'] < 0.1:
            perc = perc + aux2.loc[n, 'perc']
            cust = cust + aux2.loc[n, 'customer_id']
            aux2 = aux2.drop(labels=n, axis=0)
    aux2 = pd.concat([aux2, pd.DataFrame(data={'labels': ['outros'],
                                        'customer_id' : [cust],
                                        'perc' : [perc]})], ignore_index=True)

    # ------ BARRA DOS PRINCIPAIS GRUPOS ------

    html = ''
    for n in range(len(aux2)):
        html = html + f'''<div class="segmento centralizacao" style="flex: {aux2.loc[n, 'perc'] * 100}%;">
                            <p>
                                {(aux2.loc[n, 'perc'] * 100):.02f} %
                                <br>{aux2.loc[n, 'labels']}
                            </p>
                        </div>'''
    st.markdown(f'''
                <div class="barra">
                    {html}
                </div>
                ''', unsafe_allow_html=True)
    
    # ------ ANÁLISE DOS GRUPOS ------

    col1, col2 = st.columns([5, 5])

    with col1:
        total_billing_ga = st.date_input(  "Período de Faturamento",
                                        (datetime.date(2017, 12, 1), datetime.date(2017, 12, 7)),
                                        datetime.date(2016, 11, 29),
                                        datetime.date(2017, 12, 7),
                                        key=99
                                    )
        if len(total_billing_ga) == 1:
            date_begin_ga = total_billing_ga[0]
            date_end_ga = total_billing_ga[0]
        else:
            date_begin_ga, date_end_ga = total_billing_ga

    with col2:
        labels_ga = st.multiselect("Grupo de Comparação:",
                                    np.append(aux1['labels'].values, 'Todos'),
                                    ['Todos'])
        if len(labels_ga) == 0:
            labels_ga = ['Todos']

    df2 = df[(df['invoice_date'] >= date_begin_ga.strftime('%Y-%m-%d')) & (df['invoice_date'] <= date_end_ga.strftime('%Y-%m-%d'))]

    # Somas - Itens vendidos e Faturamento
    aux1 = df2[df2['customer_id'] < 100000][['day','month', 'year', 'labels', 'total_price', 'quantity']].groupby(['day','month', 'year', 'labels']).sum().reset_index()

    # Ticket Médio
    aux2 = df2[df2['customer_id'] < 100000][['invoice_no', 'total_price']].groupby('invoice_no').sum().reset_index().rename(columns={'total_price':'total_invoice'})
    aux3 = df2[df2['customer_id'] < 100000].drop_duplicates(subset='invoice_no')[['day','month', 'year', 'labels','invoice_no']].reset_index(drop=True)

    aux2 = aux2.merge(aux3, on=['invoice_no'], how='left')
    aux2 = aux2.groupby(['day','month', 'year', 'labels']).mean().reset_index().rename(columns={'total_invoice':'avg_ticket'})
    aux1 = aux1.merge(aux2, on=['day','month', 'year', 'labels'], how='left')

    # Frequencia média
    aux2 = df2[df2['customer_id'] < 100000][['day','month', 'year','customer_id', 'labels', 'invoice_no']].groupby(['day','month', 'year','customer_id', 'labels']).count().reset_index().rename(columns={'invoice_no':'avg_frequency'})
    aux2 = aux2[['day','month', 'year', 'labels', 'avg_frequency']].groupby(['day','month', 'year','labels']).mean()
    aux1 = aux1.merge(aux2, on=['day','month', 'year', 'labels'], how='left')

    # Recência média
    aux2 = df2[df2['customer_id'] < 100000][['invoice_date','day', 'month', 'year', 'labels', 'customer_id', 'invoice_no']].drop_duplicates(subset='invoice_no').reset_index(drop=True)
    aux2['recency'] = aux2[aux2['customer_id'] == aux2['customer_id']]['invoice_date'].max()
    aux2['recency'] = (aux2['recency'] - aux2['invoice_date']).dt.days
    aux2 = aux2[['invoice_date','day', 'month', 'year', 'labels', 'customer_id', 'invoice_no']].merge(aux2[['customer_id', 'recency']].groupby(['customer_id']).max().reset_index(), how='left', on='customer_id')
    aux2 = aux2[['day', 'month', 'year', 'labels', 'customer_id', 'invoice_date', 'recency']].groupby(['day', 'month', 'year', 'labels', 'customer_id', 'invoice_date']).min().reset_index()
    aux2 = aux2[['day', 'month', 'year', 'labels', 'invoice_date', 'recency']].groupby(['day', 'month', 'year', 'labels', 'invoice_date']).mean().reset_index()
    aux1 = aux1.merge(aux2, on=['day','month', 'year', 'labels'], how='left')

    # Total de vendas
    aux2 = df2[df2['customer_id'] < 100000].drop_duplicates(subset='invoice_no')[['day','month', 'year', 'labels', 'invoice_no']].groupby(['day','month', 'year', 'labels']).count().reset_index().rename(columns={'invoice_no':'sales'})
    aux1 = aux1.merge(aux2, on=['day','month', 'year', 'labels'], how='left')

    # Ajuste dos labels
    aux1['labels'] = aux1['labels'].apply(lambda x: inflection.titleize(x))

    # Ordenação
    aux1 = aux1.sort_values(by='invoice_date')

    col1, col2, col3 = st.columns([2, 6, 2])

    with col1:
        if labels_ga == ['Todos']:
            sales_total_ga = aux1['sales'].sum()
            fat_total_ga = aux1['total_price'].sum()
            mean_ticket_ga = aux1['avg_ticket'].mean()
            avg_frequency_ga = aux1['avg_frequency'].mean()
            avg_recency_ga = aux1['recency'].mean()
        else:
            sales_total_ga = aux1[aux1['labels'].isin(labels_ga)]['sales'].sum()
            fat_total_ga = aux1[aux1['labels'].isin(labels_ga)]['total_price'].sum()
            mean_ticket_ga = aux1[aux1['labels'].isin(labels_ga)]['avg_ticket'].mean()
            avg_frequency_ga = aux1[aux1['labels'].isin(labels_ga)]['avg_frequency'].mean()
            avg_recency_ga = aux1[aux1['labels'].isin(labels_ga)]['recency'].mean()


        st.markdown(f'''
                    <div class="grupo_fidelidade_col1">
                        <div class="block_gf" style="background-color: #6e0a98;">
                            <p>Vendas</p>
                            <span class="resultado"> {sales_total_ga} </span>
                        </div> 
                        <div class="block_gf" style="background-color: #7d3b97;">
                            <p>
                                Faturamento
                            </p>
                            <span class="resultado"> $ {fat_total_ga:.02f} </span>
                        </div> 
                        <div class="block_gf" style="background-color: #8d4ba7;">
                            <p>
                                Ticket Médio
                            </p>
                            <span class="resultado"> $ {mean_ticket_ga:.02f} </span>
                        </div>
                        <div class="block_gf" style="background-color: #9e5ab8;">
                            <p>
                                Frequência Média
                            </p>
                            <span class="resultado"> {avg_frequency_ga:.0f} compras </span>
                        </div> 
                        <div class="block_gf" style="background-color: #d475fd;">
                            <p>
                                Recência Média
                            </p>
                            <span class="resultado"> {avg_recency_ga:.0f} dias</span>
                        </div> 
                    </div>
                    ''', unsafe_allow_html=True)
        st.title('')
    
    with col2:
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            radio_gran = st.radio("Granularidade", ["Dia", "Mês", "Ano"], horizontal=True)
        with sub_col2:
            radio_group = st.radio("Abrir por Grupo?", ["Sim", "Não"], horizontal=True, index=1)
        
        # --- VENDAS ---

        for info, rotulo, single_color in zip(['sales', 'total_price', 'avg_ticket', 'avg_frequency', 'recency'], 
                                              ['Vendas', 'Faturamento', 'Ticket Médio', 'Frequência', 'Recência'],
                                              ['#6e0a98', '#7d3b97', '#8d4ba7', '#9e5ab8', '#d475fd']):
            fig = go.Figure()

            aux2 = aux1.copy()
            x_title = 'Dia'
            if radio_gran == 'Mês':
                aux2['invoice_date'] = aux2['invoice_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m'))
                x_title = 'Mês'
            if radio_gran == 'Ano':
                aux2['invoice_date'] = aux2['year']
                x_title = 'Ano'

            if radio_group == 'Sim':
                colors = ['#ed1b24', '#f78e1d', '#fef200', '#8efc07', '#00a3a8', '#0154a4', '#6b439b', '#e44097']
                for label, color in zip(aux2['labels'].unique(), colors):
                    fig.add_trace(go.Bar(x=aux2[aux2['labels'] == label]['invoice_date'],
                                        y=aux2[aux2['labels'] == label][info],
                                        name=label,
                                        marker_color=color))
                    fig.update_layout(barmode='stack')
            else:
                fig.add_trace(go.Bar(x=aux2['invoice_date'],
                                    y=aux2[info],
                                    name='Vendas',
                                    marker_color=single_color))
                
            fig.update_layout(height = 250,
                            title = rotulo,
                            xaxis_title = x_title,
                            yaxis_title = rotulo,
                            plot_bgcolor='rgba(0, 0, 0, 0)',
                            paper_bgcolor='rgba(0, 0, 0, 0)')
            fig.update_layout(margin={'r': 0, 't': 25, 'l': 0, 'b': 0}, coloraxis_showscale=False)

            st.plotly_chart(fig, use_container_width=True)
    
    with col3:

        # Quandidade de clientes por grupo
        aux_col3 = df2[df2['customer_id'] < 100000][['labels', 'customer_id']].drop_duplicates(subset=['customer_id']).groupby('labels').count().reset_index().rename(columns={'customer_id':'customers'}).sort_values('customers', ascending=False).reset_index(drop=True)
        aux_col3['perc_customers'] = (aux_col3['customers']/aux_col3['customers'].sum())*100

        # Valor total gasto pelo grupo
        aux2 = df2[df2['customer_id'] < 100000][['labels', 'total_price']].groupby('labels').sum().reset_index()
        aux_col3 = aux_col3.merge(aux2, on=['labels'], how='left')
        aux_col3['perc_total_price'] = (aux_col3['total_price'] / df[(df['invoice_date'] >= date_begin_ga.strftime('%Y-%m-%d')) & (df['invoice_date'] <= date_end_ga.strftime('%Y-%m-%d'))]['total_price'].sum())*100

        st.title('')

        fig = go.Figure()
        fig.add_trace(go.Bar(x=aux_col3['customers'],
                             y=aux_col3['labels'],
                             text=aux_col3['perc_customers'],
                             name='Pedidos',
                             marker_color='#6e0a98',
                             orientation='h'))
        fig.update_traces(texttemplate='%{text:.1f} %')
        fig.update_layout(height=250,
                          title="Clientes por Grupo",
                          xaxis_title = "Total",
                          yaxis_title = "Grupo",
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)')
        fig.update_layout(margin={'r': 0, 't': 25, 'l': 0, 'b': 0}, 
                          coloraxis_showscale=False,
                          yaxis={'categoryorder':'total ascending'})

        st.plotly_chart(fig, use_container_width=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=aux_col3['total_price'],
                             y=aux_col3['labels'],
                             text=aux_col3['perc_total_price'],
                             name='Pedidos',
                             marker_color='#6e0a98',
                             orientation='h'))
        fig.update_traces(texttemplate='%{text:.1f} %')
        fig.update_layout(height=250,
                          title="Faturamento Total por Grupo",
                          xaxis_title = "Total",
                          yaxis_title = "Faturamento",
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)')
        fig.update_layout(margin={'r': 0, 't': 25, 'l': 0, 'b': 0}, 
                          coloraxis_showscale=False,
                          yaxis={'categoryorder':'total ascending'})

        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    # ------ Data import ------
    path = 'dataset/one_place.csv'
    df = load_data(path)
    head(df)
    general_report(df)
    loyalty_groups(df)