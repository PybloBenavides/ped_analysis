import pandas as pd
import holoviews as hv
import numpy as np
from config import PED_ID, FLOW, SPEED, DENSITY, TIME, X, Y, PERS_ID
from holoviews import opts
hv.extension('bokeh')
default_opts = opts(height=600, width=800, tools=['hover'], active_tools=['wheel_zoom'])

class Proband():
    '''
    Baseclass for person who took part in the experiment (Proband)
    '''
    def __init__(self, pers_id, data, test_field):
        self.pers_id = pers_id
        self.data = data
        self.test_field = test_field
        self.avg_speed = self.average_speed()

    def average_speed(self):
        subdata = self.data[(self.data['X']> self.test_field.XMIN) & (self.data['X']<= self.test_field.XMAX)].reset_index()
        lapse = subdata.iloc[-1][TIME] - subdata.iloc[0][TIME]
        speed = self.test_field.XDISTANCE / lapse # metros por segundo
        return speed
    
    def speed_at_time(self, time):
        subdata = self.data[(self.data[TIME] >= (time -1)) & (self.data[TIME] <= (time +1))]
        if subdata.empty:
            return np.nan
        speed = (subdata.X.max() - subdata.X.min() )/ (subdata.TIME.max() - subdata.TIME.min())
        return speed

    def draw_trajectory(self):
        return hv.Points(self.data, kdims=[X,Y], vdims=[TIME]).opts( color=TIME, cmap='Reds')
    def crossed_lim(self, lim):
        try:
            crossed_time = self.data[self.data[X] >= lim].iloc[0][TIME]
            return crossed_time
        except:
            return self.data[TIME].max() + 0.5
    
    def __str__(self):
        string =  f"{self.pers_id} activo entre {self.data.TIME.min()} y {self.data.TIME.max()},\n"
        string += "velocidad media: {self.avg_speed} m/s, count his flow out at {self.crossed_lim(TEST_SCOPE[1])}"
        return string





class Test_Field():
    '''
    Base class for test field
    '''
    def __init__(self,df):
        self.YMAX = df.Y.max()
        self.YMIN = df.Y.min()
        self.XMIN = df.X.min() +1
        self.XMAX = df.X.max() -1
        self.XDISTANCE = self.XMAX - self.XMIN
        self.AREA = self.XDISTANCE + (self.YMAX - self.YMIN)
    def __str__(self):
        return f"poligono de X entre {self.XMIN} y {self.XMAX} e Y entre {self.YMIN} y {self.YMAX}"

def get_speed(data):
    prev_data = data.shift()
    return ((data[X] - prev_data[X]) / (data[TIME] - prev_data[TIME])).values[-1] 

class Ped_Experiment():
    def __init__(self, data, name):
        self.name = name
        self.data = data
        self.test_field = Test_Field(data)
        self.people = {}
        flow = {}
        speed = {}
        for person_id in data.PERS_ID.unique():
            person = Proband(person_id, data[data[PERS_ID] == person_id], self.test_field)
            self.people[person_id] = person

            flow_time = int(person.crossed_lim(self.test_field.XMAX))
            if flow_time not in flow.keys():
                flow[flow_time] = 0
                sub_df = data[data[TIME].isin([flow_time, flow_time+1])].reset_index()
                speeds = sub_df.groupby(PERS_ID).apply(get_speed)
                if not speeds.empty:
                    speed[flow_time] = speeds.mean() 
            flow[flow_time] += 1

        self.fddata = self.get_fd(speed, flow)

    def get_fd(self, speed, flow):
        speed_df = pd.DataFrame.from_dict(speed,orient='index',columns=[SPEED]).sort_index()
        speed_df['TIME'] = speed_df.index
        speed_df = speed_df.reset_index(drop=True)
        flow_df = pd.DataFrame.from_dict(flow,orient='index',columns=[FLOW]).sort_index()
        flow_df['TIME'] = flow_df.index
        flow_df = flow_df.reset_index(drop=True)
        speed_flow_df = speed_df.set_index(TIME).join(flow_df.set_index(TIME)).reset_index()
        time_count = self.data.groupby(TIME).count()[PERS_ID].reset_index().rename(columns={PERS_ID: 'PEOPLE'})
        time_count['DENSITY'] = time_count['PEOPLE'] / self.test_field.AREA
        time_count = time_count[time_count[TIME].isin(range(0,200))].reset_index(drop=True)
        fddata = time_count.set_index('TIME').join(speed_flow_df.set_index('TIME'),how='outer')
        fddata.reset_index(inplace=True)
        fddata[FLOW] = fddata.FLOW / (self.test_field.YMAX - self.test_field.YMIN)
        return fddata
        

        # self.density = self.groupby(TIME)[PERS_ID].count() / self.test_field.AREA
    

    # Drawing
    def draw( self ):
        return hv.Points(self.data, kdims=[X,Y]).opts(default_opts)

    def draw_timestamp(self, timestamp):
        return hv.Points(self.data[self.data[TIME] == timestamp], kdims=[X,Y], vdims=[PERS_ID]).opts( marker='asterisk', size=50,
                                title=f"Ped exp {self.name} at {timestamp}", width=800, height=600, tools=['hover'],
                                active_tools=['wheel_zoom'])

    def draw_most_dense(self):
        timestamp = self.data.groupby(TIME)[PERS_ID].count().max()
        return self.draw_timestamp(timestamp)


