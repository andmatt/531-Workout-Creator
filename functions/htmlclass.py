from functions.funcs import recolor
import pandas as pd

class HtmlMaker:
    def __init__(self, names, w_dict):
        self.dict = w_dict
        self.names = names
    
    def html_tables(self):
        '''
        Generates nested dictionaries within self.dict['Name'] containing the relevant html tables
        '''
        for x in self.names:
            for y in ['accessory', 'main', 'ref']:
                ref1 = '{}_output'.format(x)
                ref2 = '{}_html'.format(y)
                if y == 'accessory':                    
                    self.dict[ref1][ref2] = (self.dict[ref1][y].style
                    .set_properties(**{'text-align': 'center',
                    'border':'1px solid',
                    'border-collapse': 'collapse',
                    'border-color': 'slategray'})
                    .applymap(recolor, subset = pd.IndexSlice[[21,23,25],])).render()
                else:
                    self.dict[ref1][ref2] = (self.dict[ref1][y].style
                    .set_properties(**{'text-align': 'center',
                    'border':'1px solid',
                    'border-collapse': 'collapse',
                    'border-color': 'slategray'})).render()

    def full_html(self):
        '''
        Generates full html for each user and syncs to dropbox
        '''
        for x in self.names:
            ref1 = '{}_output'.format(x)
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
            '''.format(week = self.dict[ref1]['week'], start = self.dict[ref1]['start'], end = self.dict[ref1]['end'],
                       main_f = self.dict[ref1]['main_html'], accessory = self.dict[ref1]['accessory_html'],
                       ref = self.dict[ref1]['ref_html'])
            
            output = open('C:/Users/Matt/Dropbox/Workout/1. 531 Workout {}.html'.format(x), 'w')
            output.write(html)
            output.close()

    @property
    def html_output(self):
        '''
        Runs are relevant functions
        '''
        print('generating workouts...')
        self.html_tables()
        self.full_html()
        print('success! - now get off the computer and hit the gym')