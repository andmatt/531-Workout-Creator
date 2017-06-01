import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import datetime as dt

def google_sheet_pull(sheet, name, token):
    '''
    Inputs: sheet, name, scope, token
    sheet: Name of the actual google sheet
    name: Name of sheet to pull
    token: "client_secrets.json" file downloaded from google developer portal
    '''
    creds=ServiceAccountCredentials.from_json_keyfile_name(token, 'https://spreadsheets.google.com/feeds')
    client = gspread.authorize(creds)
    df = client.open(sheet).worksheet(name)
    df = pd.DataFrame(df.get_all_values())
    return df

def recolor(val):
    '''
    adds css color elements to df
    '''
    return 'color: white ; background-color: lightskyblue'

def week_finder(dcheck):
    '''
    References today's date to a "datecheck" dataframe pulled from the sheet
    "datecheck" is a Pandas dataframe with 2 columns - "Start" and "End" ;
    These are the start and end dates of the workout month
    '''
    for x in [1,2,3,4]:
        today = dt.datetime.today()
        start = dcheck['Start'] + dt.timedelta(weeks = x-1)
        end = dcheck['Start'] + dt.timedelta(weeks = x)
        if ((today >= start) & (today <= end)).any():
            return(str(x))
        if (today>dcheck['Start'] + dt.timedelta(weeks = 4)).any():
            raise ValueError('Date is out of Range!')