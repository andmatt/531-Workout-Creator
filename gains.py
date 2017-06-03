import datetime as dt
import string

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from functions.funcs import loc_convert as lc
from functions.funcs import google_sheet_pull, recolor, week_finder
from functions.Generator import Generator

#First you need to pull the entire sheet
token = 'C:/Users/Matt/Documents/Secure/client_secret.json'
sheet = '5-3-1 Workout Weights'
name = 'Matt'

df = google_sheet_pull(sheet, name, token)

#Manually Input the bounds of your import tables form google sheets ; Best to not change this
loc_dict = {'main': ['b', 'g', 7, 19],
            'time': ['i', 'p', 6, 20],
            'accessory': ['d', 'g', 22, 27]}

test = Generator(df, loc_dict)
test_dict = test.final_output

#HTML Generator
a_html = (test_dict['accessory'].style
        .set_properties(**{'text-align': 'center',
                          'border':'1px solid',
                          'border-collapse': 'collapse',
                          'border-color': 'slategray'})
        .applymap(recolor, subset = pd.IndexSlice[[21,23,25],]))
a_html = a_html.render()

m_html = test_dict['main'].style.set_properties(**{'text-align': 'center',
                                       'border':'1px solid',
                                       'border-collapse': 'collapse',
                                       'border-color': 'slategray'})
m_html = m_html.render()

r_html = test_dict['ref'].style.set_properties(**{'text-align': 'center',
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
'''.format(week = test._week, start = test._start, end = test._end,
           main_f = m_html, accessory = a_html, ref = r_html)

#dropbox
output = open('C:/Users/Matt/Dropbox/1. test.html', 'w')
output.write(html)
output.close()
