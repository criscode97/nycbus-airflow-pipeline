from .helpers import clean_data, yes_or_no, regex_number_finder, regex_checker

import pandas as pd
import io 
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.hooks.S3_hook import S3Hook


dtypes = {"number_of_students_on_the_bus": "int8",
                   "school_year" : "object",
                    "busbreakdown_id": "int64",
                    "run_type": "category",
                    "reason": "category",
                    "boro":"category",
                    "bus_no":"object",
                    "route_number": "object",
                    "how_long_delayed": "object",
                    "schools_serviced": "object",
                    "bus_company_name": "object",
                    "has_contractor_notified_schools": "category",
                    "has_contractor_notified_parents": "category",
                    "have_you_alerted_opt": "category",
                    "breakdown_or_running_late": "category",
                    "school_age_or_prek": "category",
                    "last_updated_on" :'datetime64[ns]',
                    "informed_on":'datetime64[ns]',
                    'occurred_on':'datetime64[ns]', 
                    'created_on':'datetime64[ns]'
                    }


index_col = "Busbreakdown_ID"

# rename columns
new_column_names = {
        "school_year":'School_Year',
        "busbreakdown_id":  'Busbreakdown_ID',
        "run_type": 'Run_Type',
        "bus_no": 'Bus_No',
        'route_number': 'Route_Number',
        'reason': 'Reason',
        'schools_serviced': 'Schools_Serviced',
        'occurred_on': 'Occurred_On',
        'created_on': 'Created_On',
        'boro': 'Boro',
        'bus_company_name': 'Bus_Company_Name',
        'how_long_delayed': 'Minutes_Delayed',
        'number_of_students_on_the_bus': 'Number_Of_Students_On_The_Bus',
        'has_contractor_notified_schools': 'Has_Contractor_Notified_Schools',
        'has_contractor_notified_parents': 'Has_Contractor_Notified_Parents',
        'have_you_alerted_opt': 'Have_You_Alerted_OPT',
        'informed_on': 'Informed_On',
        'last_updated_on': 'Last_Updated_On',
        'breakdown_or_running_late': 'Breakdown_or_Running_Late',
        'school_age_or_prek': 'School_Age_or_PreK'}

def processing_data(ti, key, bucket_name):
    data = ti.xcom_pull(task_ids=['extracting_data'])

    df = pd.concat(pd.json_normalize(p) for p in data)

    df = df.drop('incident_number', axis=1)

    df = df.astype(dtypes, errors='raise')

    # drop repeated rows and and Nan Columns
    df = clean_data(df)

    # Transform the values in column How_Long_Delayed to keep only the first number string. Here we are assuming that the all if not most inputs were given in minutes
    df["Minutes_Delayed"] = df["how_long_delayed"].apply(lambda x: regex_number_finder(x))
    
    # all columns will be rename to match the column on the database is renamed to Minutes_Delayed
    df.rename(new_column_names, axis=1, inplace=True)
    
    df = df.set_index(index_col)

    # # transform Yes/No columns to Y/N as a way to improve speed and memory
    yn_columns = ['Have_You_Alerted_OPT', 'Has_Contractor_Notified_Schools', 'Has_Contractor_Notified_Parents']
    for i in yn_columns:
        df[i] = df[i].apply(lambda x: yes_or_no(x))

    # create a new column, "Service type", to collect information based on the Route_Nuber indetifier:
    df["Service_type"]=df["Route_Number"].apply(lambda x: regex_checker(x))

    hook=S3Hook('s3_conn')
    
    with io.BytesIO() as buffer:                                
        buffer.write(
            bytes(
                df.to_csv(None, sep=",", quotechar='"'),
                encoding="utf-8"
            )
        )               
        hook.load_bytes(
            buffer.getvalue(),
            bucket_name=bucket_name,
            key=key, 
            replace=True
        )