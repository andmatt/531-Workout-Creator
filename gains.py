import datetime as dt
import string

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from functions.funcs import loc_convert as lc
from functions.funcs import google_sheet_pull, recolor, week_finder

#First you need to pull the entire sheet
token = 'C:/Users/Matt/Documents/Secure/client_secret.json'
sheet = '5-3-1 Workout Weights'
name = 'Matt'

df = google_sheet_pull(sheet, name, token)

#Manually Input the bounds of your import tables form google sheets ; Best to not change this
loc_dict = {'main': ['b', 'g', 7, 19],
            'time': ['i', 'p', 7, 20],
            'accessory': ['d', 'g', 22, 27]}

class Generator:
    ''' Class designed to generate the standard weekly workout HTML file from an imported google sheet
    '''
    def __init__(self, df, loc_dict):
        self.df = df
        self.loc_dict = loc_dict 
        self._main = lc(df, loc_dict['main'])
        self._time = lc(df, loc_dict['time'])
        self._accessory = lc(df, loc_dict['accessory'])

    def date_finder(self):
        '''Returns the current week'''
        self._names = self._time.iloc[0, 0:6].tolist() + ['End', 'Tag']
        self._time.columns = self._names
        self._time = self._time.reset_index(drop=True).iloc[1:]
        self._dcheck = self._time[self._time.Tag=='1'][['Start', 'End']]
        self._dcheck = self._dcheck.apply(pd.to_datetime, axis=1)
        self._week = week_finder(self._dcheck)
    
    def start_end(self):
        '''Returns week start and end dates'''
        wdiff = int(self._week)-1
        self._dcheck['Start'] = self._dcheck['Start'] + dt.timedelta(weeks = wdiff)
        self._dcheck['End'] = self._dcheck['End'] + dt.timedelta(weeks = wdiff)
        self._start = self._dcheck['Start'][1].strftime('%m/%d/%Y')
        self._end = self._dcheck['End'][1].strftime('%m/%d/%Y')

    def main_gen(self):
        '''Generates main workout + subsets for correct week'''
        self._main.columns = self._main.iloc[0]
        self._main = self._main.reset_index(drop = True)
        self._main.columns.name = None
        self._main[self._main==""] = None
        self._main.fillna(method='ffill', inplace = True)

        self._main_f = self._main[self._main['Week:'].str.contains(self._week)]
        self._main_f = self._main_f.drop('Week:', 1)

    def ref_gen(self):
        '''
        Generates workout reference sheet
        '''
        self._ref = self._main_f.iloc[:, 1:]
        self._ref = self._ref.applymap(lambda x: int(x.split(' lb', 1)[0]))
        self._ref = pd.DataFrame(self._ref.stack()).reset_index()
        self._ref = self._ref[['level_1', 'level_0', 0]]
        self._ref.columns = [['Exercise', 'Set', 'Weight']]
        self._ref['Set'] = self._ref['Set']
        self._ref['Weight (no bar)'] = self._ref['Weight'] - 45
        self._ref['Weight (each side)'] = -(self._ref['Weight (no bar)'] // -2)
        self._ref = self._ref.sort_values('Exercise').reset_index(drop = True)

    def accessory_gen(self):
        '''
        Generates final accessory workout DF
        '''
        self._accessory.columns = self._main.columns[2:6]
        self._accessory.iloc[1:].reset_index(drop = True)
        self._accessory.columns.name = None
        self.accessory = self._accessory

test = Generator(df, loc_dict)
test.date_finder()
test.start_end()
test.main_gen()
test.ref_gen()
test.accessory_gen()

#HTML Generator
a_html = (test.accessory.style
        .set_properties(**{'text-align': 'center',
                          'border':'1px solid',
                          'border-collapse': 'collapse',
                          'border-color': 'slategray'})
        .applymap(recolor, subset = pd.IndexSlice[[21,23,25],]))
a_html = a_html.render()

m_html = test.main_f.style.set_properties(**{'text-align': 'center',
                                       'border':'1px solid',
                                       'border-collapse': 'collapse',
                                       'border-color': 'slategray'})
m_html = m_html.render()

r_html = test.ref.style.set_properties(**{'text-align': 'center',
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
output = open('C:/Users/Matt/Dropbox/1. test.html', 'w')
output.write(html)
output.close()
