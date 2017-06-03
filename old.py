# Old .py file with the raw data manipulatoin (no class rollups)

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime as dt

from functions.funcs import google_sheet_pull, recolor, week_finder

token = 'C:/Users/Matt/Documents/Secure/client_secret.json'
sheet = '5-3-1 Workout Weights'
name = 'Matt'

#Main Workout
andmatt = google_sheet_pull(sheet, name, token)

main = andmatt.loc[6:18, 1:6]
main.columns = main.iloc[0]
main = main.reset_index(drop = True)
main.columns.name = None
main[main==""] = None
main.fillna(method='ffill', inplace = True)

#Date Finder
dates = andmatt.loc[5:19, 8:15]
names = dates.iloc[0, 0:6].tolist() + ['End', 'Tag']
dates.columns = names
dates = dates.reset_index(drop=True).ix[1:]

dcheck = dates[dates.Tag=='1'][['Start', 'End']]
dcheck = dcheck.apply(pd.to_datetime, axis=1)
week = week_finder(dcheck)

#Subset Main for Current Week
main_f = main[main['Week:'].str.contains(week)]
main_f = main_f.drop('Week:', 1)

#Workout Reference Cheat Sheet
workout = main_f.iloc[:, 1:]
workout = workout.applymap(lambda x: int(x.split(' lb', 1)[0]))

wstacked = pd.DataFrame(workout.stack()).reset_index()
wstacked = wstacked[['level_1', 'level_0', 0]]
wstacked.columns = [['Exercise', 'Set', 'Weight']]

wstacked['Set'] = wstacked['Set']
wstacked['Weight (no bar)'] = wstacked['Weight'] - 45
wstacked['Weight (each side)'] = -(wstacked['Weight (no bar)'] // -2)
wstacked = wstacked.sort_values('Exercise').reset_index(drop = True)

#Accessory Workout
accessory = andmatt.loc[21:26, 3:6]
accessory.columns = main.columns[2:6]
accessory.iloc[1:].reset_index(drop = True)
accessory.columns.name = None

#Get Week start and End
week_d = dcheck.copy()
wdiff = int(week)-1
week_d['Start'] = week_d['Start'] + dt.timedelta(weeks = wdiff)
week_d['End'] = week_d['End'] + dt.timedelta(weeks = wdiff)
start = week_d['Start'][1].strftime('%m/%d/%Y')
end = week_d['End'][1].strftime('%m/%d/%Y')

#HTML Generator
a_html = (accessory.style
        .set_properties(**{'text-align': 'center',
                          'border':'1px solid',
                          'border-collapse': 'collapse',
                          'border-color': 'slategray'})
        .applymap(recolor, subset = pd.IndexSlice[[21,23,25],]))
a_html = a_html.render()

m_html = main_f.style.set_properties(**{'text-align': 'center',
                                       'border':'1px solid',
                                       'border-collapse': 'collapse',
                                       'border-color': 'slategray'})
m_html = m_html.render()

r_html = wstacked.style.set_properties(**{'text-align': 'center',
                                       'border':'1px solid',
                                       'border-collapse': 'collapse',
                                       'border-color': 'slategray'})
r_html = r_html.render()

#Full HTML
html = '''\
<html>
  <head> 
  <title> 5-3-1 Workout of the Week </title> 
  </head>
  
  <body>
  <h2>5-3-1 Workout of the Week</h2>
  
    <p>PFA - the workout of the week. It is currently <b>Week {week}</b> <br>
       <b>Week {week}</b> goes from {start} till {end}
    </p>
    
    <h4>Main Workout:</h4>
    {main_f}
    <br>
    
    <h4>Accessory Exercises:</h4>
    {accessory}<br>
    
    <h4>Weight References:</h4>
    {ref}<br>
    
  </body>
</html>
'''.format(week = week, start = start, end = end,
           main_f = m_html, accessory = a_html, ref = r_html)

#dropbox
output = open('C:/Users\Matt/Dropbox/1. test.html', 'w')
output.write(html)
output.close()