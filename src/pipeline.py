import pandas as pd
import One_Place.One_Place as One_place

from sqlalchemy import create_engine


def insiders():
    endpoint = 'postgresql://gtv_michelsen:5B8X3A9K1Y7Z@one-place.cue7vx85kv3s.us-east-1.rds.amazonaws.com/one_place'
    conn = create_engine(endpoint)
    querry = """
        SELECT * FROM one_place op;
    """
    df_raw = pd.read_sql(querry, con=conn)
    
    pipeline = One_place()

    df = pipeline.data_cleaning(df_raw)
    df = pipeline.fearture_engineering(df)
    df = pipeline.data_preparation(df)
    df = pipeline.get_prediction(df)
    
    df[['customer_id', 'labels']].to_sql('insiders', con=conn, if_exists='replace', index=False)

if __name__ == "__main__":
    insiders