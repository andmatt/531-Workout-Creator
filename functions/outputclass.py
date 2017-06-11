import datetime as dt
import string
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from functions.funcs import google_sheet_pull, recolor, week_finder, loc_convert as lc

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
        self._time.columns = self._time.iloc[0]
        self._time = self._time.reset_index(drop=True).iloc[1:]
        self._time.columns.name = None
        self._dcheck = self._time[self._time.Tag=='1'][['Start', 'End']]
        self._dcheck = self._dcheck.apply(pd.to_datetime, axis=1)
        self._week = week_finder(self._dcheck)
    
    def start_end(self):
        '''Returns week start and end dates'''
        if int(self._week) >1:
            wdiff = int(self._week)-1
        else:
            wdiff = 0
        self._dcheck['W_Start'] = self._dcheck['Start'] + dt.timedelta(weeks = wdiff)
        self._dcheck['W_End'] = self._dcheck['W_Start'] + dt.timedelta(days = 6)
        self._start = self._dcheck['W_Start'][1].strftime('%m/%d/%Y')
        self._end = self._dcheck['W_End'][1].strftime('%m/%d/%Y')

    def main_gen(self):
        '''Generates main workout + subsets for correct week'''
        self._main.columns = self._main.iloc[0]
        self._main = self._main.reset_index(drop = True).iloc[1:]
        self._main.columns.name = None
        self._main[self._main==""] = None
        self._main.fillna(method='ffill', inplace = True)

        self._main_f = self._main[self._main['Week:'].str.contains(self._week)]
        self._main_f = self._main_f.drop('Week:', 1)
        self._main_f.index = [1,2,3]

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
    
    @property
    def final_output(self):
        print('retrieving output dictionary...')
        self.date_finder()
        self.start_end()
        self.main_gen()
        self.ref_gen()
        self.accessory_gen()
        self.output_dict = {'main': self._main_f,
                            'ref': self._ref,
                            'accessory': self._accessory,
                            'week': self._week,
                            'start': self._start,
                            'end': self._end}
        print('success')
        return self.output_dict