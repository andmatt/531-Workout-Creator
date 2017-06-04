import datetime as dt
import string

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from functions.funcs import loc_convert as lc
from functions.funcs import google_sheet_pull, recolor, week_finder
from functions.outputclass import Generator
from functions.htmlclass import HtmlMaker

#First you need to pull the entire sheet for each user
token = 'C:/Users/Matt/Documents/Secure/client_secret.json'
sheet = '5-3-1 Workout Weights'
names = ['Matt', 'Kri']

#Blank dictionary that will store the initial sheet pulls as well as all output dfs
sheet_dict = {}

for x in names:
  sheet_dict[x] = google_sheet_pull(sheet, x, token)

#Manually Input the bounds of your import tables form google sheets ; Best to not change this
loc_dict = {'main': ['b', 'g', 7, 19],
            'time': ['i', 'p', 6, 20],
            'accessory': ['d', 'g', 22, 27]}

#Generate output dataframes
for x in names:
    test = Generator(sheet_dict[x], loc_dict)
    sheet_dict['{}_output'.format(x)] = test.final_output

#Generate final html output & sync to dropbox
test = HtmlMaker(names, sheet_dict)
test.html_output
