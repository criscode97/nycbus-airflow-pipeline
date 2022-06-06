from .helpers import quality_report
import pandas as pd
from airflow.utils.email import send_email_smtp


def email_callback(ti, email):
    data = ti.xcom_pull(task_ids=['extracting_data'])
    df = pd.concat(pd.json_normalize(p) for p in data)

    send_email_smtp(
        to=[email],
        subject='subject',
        html_content=quality_report(df),
    )


