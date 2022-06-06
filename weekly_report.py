from gc import callbacks
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, html, dcc, Input, Output, State, dash_table, ALL
import boto3
import io
import dash_daq as daq
from datetime import date, datetime
import plotly.express as px
import numpy as np
import time
from dateutil.relativedelta import relativedelta
import os

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

app.card = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Title", id="card-title"),
            html.H2("100", id="card-value"),
            html.P("Description", id="card-description")
        ]
    )
)
my_date = date.today()
year, week_num, day_of_week = my_date.isocalendar()
week = week_num - 1
app.layout = html.Div([
    html.H1("NYC Bus Breakdowns and Delays Weekly Report\n", style={"text-align": "center"}),
     html.H3(f"{date(year,1,1)+relativedelta(weeks=+week)}", style={"text-align": "center"}),
    dbc.Row([
        dbc.Col([dcc.Graph(id='reasons-per-boro')], width=6), dbc.Col([dcc.Graph(id='monthly-delays-by-reason')], width=6)
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(id='weekdays-by-reason')]), dbc.Col([dcc.Graph(id='reasons-per-hour')]), dbc.Col([dcc.Graph(id='breakdowns-by-vendor')])
    ], align='center'),
     # dcc.Store inside the user's current browser session
    dcc.Store(id='store-data', data=[], storage_type='memory') # 'local' or 'session'
])

@app.callback(
    Output('store-data', 'data'),
    Input(dict(name="form-input", idx=ALL), "value"))
def data(value1):
    my_date = date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    week = week_num - 1

    REGION = 'us-east-1'
    ACCESS_KEY_ID = os.environ['ACCESS_KEY_ID']
    SECRET_ACCESS_KEY = os.environ['SECRET_ACCESS_KEY']
    BUCKET_NAME = os.environ['BUCKET_NAME']
    KEY = f'{week}_bus_data.csv'

    s3c = boto3.client(
            's3', 
            region_name = REGION,
            aws_access_key_id = ACCESS_KEY_ID,
            aws_secret_access_key = SECRET_ACCESS_KEY
        )

    obj = s3c.get_object(Bucket= BUCKET_NAME , Key = KEY)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8')
    return df.to_dict('records')

@app.callback(
    Output('reasons-per-boro', 'figure'),
    Input('store-data', 'data')
)
def reason_per_boro(data):
    df = pd.DataFrame(data)
    
    reason_per_boro= pd.DataFrame()
    reason_per_boro["Reason"] = df["Reason"]
    reason_per_boro["Boro"] = df["Boro"]
    reason_per_boro= reason_per_boro.groupby('Reason')["Boro"].value_counts()
    reason_per_boro= reason_per_boro.to_frame()
    reason_per_boro= reason_per_boro.rename(columns={"Boro":"Total", "level_1":"Boro"})
    reason_per_boro= reason_per_boro.reset_index(level=[0,1])

    fig = px.sunburst(reason_per_boro, path=['Boro', 'Reason'], values='Total', color = "Total", title='<b>Breakdowns and Delays by Borough</b>', color_continuous_scale='RdBu')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    autosize=True,
                    font=dict(
                    color='white'
                ))
    return fig

@app.callback(
    Output('reasons-per-hour', 'figure'),
    Input('store-data', 'data')
)
def reason_per_hour(data):
    # graph delay per hour by reason
    df = pd.DataFrame(data)
    hourly_delays = pd.DataFrame()
    hourly_delays["Reason"] = df["Reason"]
    df["Occurred_On"] = pd.to_datetime(df["Occurred_On"])
    hourly_delays["Occurred_On"] = df["Occurred_On"].apply(lambda dt: datetime(dt.year, dt.month, dt.day, dt.hour,30*(dt.minute // 30)))
    hourly_delays["Hour"] = hourly_delays["Occurred_On"].dt.strftime("%H:%M")
    hourly_delays.pop("Occurred_On")
    hourly_delays = hourly_delays.groupby('Reason')["Hour"].value_counts()
    hourly_delays = hourly_delays.to_frame()
    hourly_delays = hourly_delays.rename(columns={"Hour":"Total"})
    hourly_delays = hourly_delays.reset_index(level=[0,1])
    hourly_delays = hourly_delays.sort_values('Hour')

    fig = px.line(hourly_delays,  x="Hour", y="Total", color="Reason",  
    labels={"Total": "Number of Breakdowns and Delays"}, title='<b>Breakdowns and Delays per Hour</b>')
    fig.update_xaxes(dtick=4)
    fig.update_yaxes(tick0=0)
    fig.update_xaxes(showline=False, gridcolor='rgba(0,0,0,0)')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    autosize=True,
                    font=dict(
                    color='white'
                ))
    return fig


@app.callback(
    Output('monthly-delays-by-reason', 'figure'),
    Input('store-data', 'data')
)
def monthly_delays_by_reason(data):
    # monthly breakdowns and delays by reason
    df = pd.DataFrame(data)
    fig = px.bar(df["Reason"].value_counts(), title='<b>Leading Reasons for Delays and Breakdowns</b>')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    autosize=True,
                    font=dict(
                    color='white'
                ))
    return fig

@app.callback(
    Output('weekdays-by-reason', 'figure'),
    Input('store-data', 'data')
)
def weekdays_by_reason(data):
    # delays and breakdowsn per weekday by reason
    df = pd.DataFrame(data)
    weeks = pd.DataFrame()
    df["Occurred_On"] = pd.to_datetime(df["Occurred_On"])
    weeks["Occurred_On"] = df["Occurred_On"]
    weeks["Week"] = weeks["Occurred_On"].dt.day_name()
    weeks["Occurred_On"] = weeks["Occurred_On"].apply(lambda dt: datetime(dt.year, dt.month, dt.day, dt.hour,15*(dt.minute // 15)))
    weeks["Hour"] = weeks["Occurred_On"].dt.strftime("%H:%M")
    weeks.pop("Occurred_On")

    weeks = weeks.groupby('Week')["Hour"].value_counts()
    weeks = weeks.to_frame()
    weeks = weeks.rename(columns={"Hour":"Total"})
    weeks = weeks.reset_index(level=[0,1])
    weeks = weeks.sort_values('Hour')

    fig = px.line(weeks,  x="Hour", y="Total", color="Week", title='<b>Breakdowns and Delays by Day of The Week</b>',
    labels={"0": "Number of Breakdowns and Delays"})
    fig.update_xaxes(dtick=6)
    fig.update_yaxes(tick0=0)
    fig.update_xaxes(showline=False, gridcolor='rgba(0,0,0,0)')
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    autosize=True,
                    font=dict(
                    color='white'
                ))
    return fig

@app.callback(
    Output('breakdowns-by-vendor', 'figure'),
    Input('store-data', 'data')
)
def breakdowns_by_vendors(data):
    df = pd.DataFrame(data)
    # top 10 vendor by total delays and breakdowns
    vendors = df['Bus_Company_Name'].value_counts()
    vendors = vendors.to_frame()
    vendors = vendors.reset_index(level=[0]).rename(columns={"index":"Company", "Bus_Company_Name": "Total %"})
    vendors['Total %'] = vendors['Total %'].value_counts(normalize=True) * 100
    vendors['Total %'] = vendors['Total %'].round(decimals=2)
    vendors = vendors.sort_values(by=['Total %'], axis=0, ascending=False)
    fig = px.bar(vendors.head(10), x='Total %', y='Company', text='Total %', title='<b>Total Breakdowns and Delays by Vendors</b>', template='simple_white')
    fig.update_traces(marker_color='#3EB595')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', autosize=True, title_x=0.7, title_font_family ="Calibri")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    autosize=True,
                    font=dict(
                    color='white'
                ))
    return fig

if __name__ == '__main__':
   app.run_server(debug=True)