from calendar import week
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.mssql_operator import MsSqlOperator


from datetime import timedelta, datetime, date



from etls.transformations import processing_data
from etls.loads import load_csv
from etls.sql_queries import s3_to_postgres_sql
from etls.email_reports import email_callback

description = 'a pipeline for the nyc open data on bus breakdowns and delays "https://data.cityofnewyork.us/Transportation/Bus-Breakdown-and-Delays/ez4e-fazm"'
app_token = "7FpHOFO4vFmrHxLG52leOInZ7"
row_limit = 50000 #Maximun number is 50000
my_date = date.today()
year, week_num, day_of_week = my_date.isocalendar()
week = week_num - 1
email = 'cristopher2547@gmail.com'

default_args = {
    "start_date": datetime(2022, 5, 1),
    'retry_delay': timedelta(seconds=5),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'depends_on_past': False,
    'retries': 1,
}
with DAG(
    'nyc_bus_breakdown_pipeline',
    default_args= default_args,
    description=description,
    schedule_interval=timedelta(weeks=1),
    catchup=False,
) as dag:

    # 1-. download data
    extracting_data = SimpleHttpOperator(
        task_id='extracting_data',
        http_conn_id='nycbus_soap_api',
        endpoint=f'resource/ez4e-fazm.json/?$$app_token={app_token}&$limit={row_limit}&$where=date_extract_woy(created_on)={week}',
        method='GET',
        response_filter= lambda r: r.json(),
        log_response=True
    )

    # 2-. Transform data and uload it to s3 Bucket
    processing_data = PythonOperator(
        task_id='processing_data',
        python_callable=processing_data,
        op_kwargs = {
            'key':f'{week}_bus_data.csv',
            'bucket_name': 'nycsbus-airflow'
        }
    )

    send_email_report = PythonOperator(
    task_id='send_email_report',
    python_callable=email_callback,
    provide_context=True,
    op_kwargs = {'email':email},
    dag=dag,
    )

    load_data = MsSqlOperator(
    task_id="load_data",
    sql=s3_to_postgres_sql(week),
    mssql_conn_id="aws_rds_conn",
    autocommit=True,
    dag=dag
    )

    extracting_data >> [processing_data,send_email_report] >> load_data
