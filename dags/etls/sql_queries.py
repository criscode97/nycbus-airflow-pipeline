def s3_to_postgres_sql(week):
    return  f'''CREATE TABLE IF NOT EXISTS nyc_bus_breakdowns_and_delays (\
        Busbreakdown_ID INTEGER PRIMARY KEY,\
        School_Year TEXT,\
        Run_Type TEXT,\
        Bus_No TEXT,\
        Route_Number TEXT,\
        Reason TEXT,\
        Schools_Serviced TEXT,\
        Occurred_On TIMESTAMP,\
        Created_On TIMESTAMP,\
        Boro TEXT,\
        Bus_Company_Name TEXT,\
        Minutes_Delayed INTEGER,\
        Number_Of_Students_On_The_Bus INTEGER,\
        Has_Contractor_Notified_Schools CHAR(1), \
        Has_Contractor_Notified_Parents CHAR(1),\
        Have_You_Alerted_OPT CHAR(1),\
        Informed_On TIMESTAMP,\
        Last_Updated_On TIMESTAMP,\
        Breakdown_or_Running_Late TEXT,\
        School_Age_or_PreK TEXT);
        
        SELECT aws_commons.create_s3_uri(
        'nycsbus-airflow',
        '{week}_bus_data.csv',
        'us-east-1'
        ) AS s3_uri \gset;

        SELECT aws_s3.table_import_from_s3(
        'nyc_bus_breakdowns_and_delays',
        '', 
        '(format csv)',
        :'s3_uri'
        );
        '''