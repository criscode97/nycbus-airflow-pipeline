import psycopg2
from .sql_queries import s3_to_postgres_sql
import os

def load_csv(week):
    conn = psycopg2.connect(database=os.environ['POSTGRES_DB'],
                            user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'], 
                            host=os.environ['POSTGRES_HOST'], port='5432'
    )
    
    conn.autocommit = True
    cursor = conn.cursor()
    
    sql = s3_to_postgres_sql(week)
    cursor.execute(sql)
    
    conn.commit()
    conn.close()