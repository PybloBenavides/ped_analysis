import holoviews as hv
import numpy as np
from config import PED_ID, FLOW, SPEED, DENSITY, TIME, X, Y, PERS_ID

hv.extension('bokeh')
opts = hv.opts(width=800, height=600, tools=['hover'],active_tools=['wheel_zoom'])

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


class Ped_Experiment():
    def __init__(self, data):
        self.raw_data = data
        self.test_field = Test_Field(data)
        self.people = {}
        for person_id in data.PERS_ID.unique():
            person = Proband(person_id, data[data[PERS_ID] == person_id], self.test_field)
            self.people[person_id] = person
    def draw( self ):
        return hv.Points(self.raw_data, kdims=['X','Y']).opts(opts)

