import fastf1
from fastf1.core import Laps
import pandas as pd

year = int(input("Select a year 2018-now inclusive: "))
events = fastf1.get_event_schedule(year, include_testing = False)
print("select an event from these: ")
print(events[['EventName', 'Location']])
gp = input("Select a race event: ")
sess = input("Select a session FP1 FP2 FP3 Q R: ")


session = fastf1.get_session(year, gp, sess)
session.load()

drivers = pd.unique(session.laps['Driver'])
print(drivers)

list_fastest_laps = list()
for drv in drivers:
    drvs_fastest_lap = session.laps.pick_drivers(drv).pick_fastest()
    list_fastest_laps.append(drvs_fastest_lap)
fastest_laps = Laps(list_fastest_laps) \
    .sort_values(by='LapTime') \
    .reset_index(drop=True)
print(fastest_laps[['Driver', 'LapTime']])
fastest_laps[['Driver', 'LapTime']].to_csv('fastestlaps.csv', index=False)
