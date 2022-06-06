class sql_queries:
        create_aws_s3_extension="CREATE EXTENSION IF NOT EXISTS aws_s3 CASCADE;"
        delete_table="DROP TABLE nyc_bus_breakdowns_and_delays;"
        create_table=''' 
        CREATE TABLE IF NOT EXISTS nyc_bus_breakdowns_and_delays (
        Busbreakdown_ID INTEGER PRIMARY KEY,
        School_Year TEXT,
        Run_Type TEXT,
        Bus_No TEXT,
        Route_Number TEXT,
        Reason TEXT,
        Schools_Serviced TEXT,
        Occurred_On TIMESTAMP,
        Created_On TIMESTAMP,
        Boro TEXT,
        Bus_Company_Name TEXT,
        Number_Of_Students_On_The_Bus INTEGER,
        Has_Contractor_Notified_Schools CHAR(1), 
        Has_Contractor_Notified_Parents CHAR(1),
        Have_You_Alerted_OPT CHAR(1),
        Informed_On TIMESTAMP,
        Last_Updated_On TIMESTAMP,
        Breakdown_or_Running_Late TEXT,
        School_Age_or_PreK TEXT,
        Minutes_Delayed DECIMAL,
        Service_type TEXT);
        '''

        s3_to_postgres_sql = """
        SELECT aws_s3.table_import_from_s3( 'nyc_bus_breakdowns_and_delays', '', '(format csv, delimiter "|", header)' , '{bucket_name}', '/{week}_bus_data.csv', 'us-east-1' );
        """