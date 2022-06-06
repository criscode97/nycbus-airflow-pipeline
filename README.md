# nycbus-airflow-pipeline
An Automate airflow pipeline for the weekly data extraction of the Bus Breakdown and Delay system, which collects information from school bus vendors operating out in the field in real time.

## Architecture
![nycbusdataflow](https://user-images.githubusercontent.com/92554847/172236991-f660c3fd-0b81-466e-898a-d2fab8d7398d.jpg)
## ETL Flow - Weekly
![nycbusdag](https://user-images.githubusercontent.com/92554847/172236938-8e23fac9-d893-45d0-bc7b-b0af55fe16f3.gif)

## [Plotly Dashboard](https://nycbusweeklyreport.herokuapp.com/)
![nycbusweeklyreport](https://user-images.githubusercontent.com/92554847/172236955-1261b7ca-b773-40d6-9c4d-277e62aefb09.gif)

## App Structure
```bash
│   .env
│   docker-compose.yaml
│   weekly_report.py
│
├───dags
│   │   nycbus_etl.py
│   │
│   └───etls
│           email_reports.py
│           helpers.py
│           sql_queries.py
│           transformations.py
│
├───logs
│   ├───dag_processor_manager
│   │       
│   └───scheduler
|
└───plugins
```
## Technologies
- Pandas
- Airflow
- AWS (S3, RDS Postgres)
- Dash by Plotly
- SMTP

## [Data Insights](https://docs.google.com/presentation/d/1SJt3RG8Wf37v_mg00TM423DSFkN3jBYMJPAQ58Zwx_Y/edit?usp=sharing)

### Data Quality: 
The CSV data has a total of 21 Columns and 495,144 Rows. There were a total of 0 repeated rows found in the file. Three Columns were found to have a significant amount of null values, namely Incident_Number  with 98% null values, How_Long_Delayed with 10.5% null values, and Boro with 2.2%. Column Incident_Number was dropped as the missing data would only take up more memory in the dataset with very little insights to offer for the decision making process.
It is strongly recommended to require a valid input, in minutes, on the submissions for the How_Long_Delayed column. The column was transformed by extracting the number of minutes, and renamed to Minutes_Delayed.

### Reasons for Delays and Breakdowns
Heavy traffic is the leading reason behind Delays and Breakdowns, with over 300k delays caused by traffic (62%), followed by Mechanical Problems (10%), and Other (14%).

### Breakdowns and Delays per Borough, County, or State
Manhattan leads in Breakdowns and Delays with 26%, followed by The Bronx, with 25.5%, and Brooklyn, with 23.6%

### Chances of Delay or Breakdown Per Hour
Data shows chances of delays are greater in the morning hours, with over 75% of delays and breakdowns occurring between the hours of 6am and 9am

### Breakdowns and Delays per Hour of the Day by Reason (24hr)
Reasons behind follow a similar pattern throughout the day, with every category increasing during the morning hours.

### Breakdowns and Delays per Hour by Weekday
Breakdowns and Delays follow a consistent hourly pattern per weekday, with most delays and breakdowns occurring during the morning hours(6 to 9 am). A noticeable difference can be observed on mondays, with the number of breakdowns and delays during the morning hours significantly increasing with respect to other weekdays

### Breakdowns and Delays per Month
Number of delays and breakdowns remain relatively similar between September and May, which corresponds with the active months of the school year

### Breakdowns and Delays per Month by Reason
The leading cause of delays across every month is Heavy Traffic by a large margin, and the other categories seem to follow the same trend per month

### Breakdowns and Delays per Month due to Weather Conditions
One category in particular deviates from all others in terms of trends by month. Delays and Breakdowns due to Weather Conditions highly increase in the winter months (58.9 % of weather related delays & breakdowns) and decrease during the summer months (2.2% of weather related delays and breakdowns), as compared to the months corresponding to other seasons

