## ETL Helper funtions

import pandas as pd
import numpy as np
import re


# Print custome quality reports using the pandas library
def quality_report(df):
    r, c = df.shape
    report = f""" DATA QUALITY REPORT:
    Columns:{c}
    Rows:{r}
    Number of Null Values per column: \n{df.isna().sum()}")
    Duplicated Rows: {df.duplicated().sum()}"""
    return report

# quick data cleanup to be ran after the quality of the data has been analize
def clean_data(df):
    return df.dropna(how="all").drop_duplicates()

#function that deletes any column with more than x% of NaN values (default 95%)
def drop_empty_columns(df, treshold=0.95):
    return df.dropna(thresh=df.shape[0]*treshold,how='all',axis=1)

# this funtion take a Yes or No string argument and return Y or N, allowing for memory optimization
def yes_or_no(string):
    return "Y" if string=="Yes" else "N"

# this dictionary is used on the regex_checker funtion by default to map the regex string to the corresponding service type
route_regex = {
    "^[a-zA-Z]([0-9]{3})$" : "curb-to-curb",
    "^[a-zA-Z]([0-9]{4})$" : "stop-to-school",
    "(.*?)" : "Pre-K/EI routes"
}

# this function takes for arguments a string and a dictionary that maps regex expressions with their corresponding value (default route_regex)
# the funtion return the value string that corresponds to the matching regex key 
def regex_checker(string, identifier=route_regex):
  for i in identifier:
    pattern = re.compile(i)
    if pattern.match(str(string)):
        return identifier[i]

# this funtion takes as argument a string and regex expresion, return the part of the string that matches the the regex if a match is found,
# else, it returns the string passes
def regex_number_finder(string, regex="(?m)^(\d+).*"):
    pattern = re.compile(regex)
    m = pattern.search(str(string))
    return m.group(1) if m else string