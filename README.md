# Student Identification
- Name: Matthew Drew
- Student ID: 35575125

# f1-telemetry-dashboard-project
Analyze data from F1 events.

## Credits
- Telemetry data provided by [FastF1](https://github.com/theOehrly/Fast-F1) (MIT License).

## Dependencies
- FastF1
- Python 3.8 or higher
- Matplolib
- Flask
- Pandas

# Setup
- Before doing anything else make sure you have python installed and a text editor of your choice.
- Create a directory where you want the project to be stored.
- run:

```
python -m venv <directory you want>
```
- then activate the environment:

```
source bin/activate
```
- Once your virtual environment is created we need to install the dependencies:

```
pip install fastf1
pip install Flask
```

- this should cover everything but if you encounter errors when building just install remaining dependencies manually.

# First Script
- The first script is a console based application and was built to learn the api and python simultaneously as I had no prior experience with either. In order to learn the api and how to use the correct functions I followed some of the examples from Fastf1 and changed it to do what I wanted.
- Import the libraries:

```
import fastf1
import matplotlib.pyplot as plt
import fastf1.plotting
from timple.timedelta import strftimedelta
import pandas as pd
```

- Next we get the choices of what session the user wants to look at:

```
year = int(input("Select a year 2018-now inclusive: "))
events = fastf1.get_event_schedule(year, include_testing = False)
print("select an event from these: ")
print(events[['EventName', 'Location']])
gp = input("Select a race event: ")
sess = input("Select a session FP1 FP2 FP3 Q R: ")
```

- We get the year first, then print a list of the events from that year, then the user selects what event and session. 

- Now we setup matplotlib for our graph, load the session that the user has chosen and get the track info for corner numbers:

```
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme=None)
session = fastf1.get_session(year, gp, sess)
session.load()
circuit_info = session.get_circuit_info()
```

- Printing a list of available drivers from the session and getting the users selection:

```
drivers = pd.unique(session.laps['Driver'])
print("Select which drivers to compare out of these:")
print(drivers)
driver1 = input("Select first driver(THREE LETTER ABBREVIATION): ")
driver2 = input("Select second driver(THREE LETTER ABBREVIATION): ")
```

- Get drivers data from the session, fastest laps, team colour and distance:

```
driv1_lap = session.laps.pick_drivers(driver1).pick_fastest()
driv2_lap = session.laps.pick_drivers(driver2).pick_fastest()

driv1_tel = driv1_lap.get_car_data().add_distance()
driv2_tel = driv2_lap.get_car_data().add_distance()

drv1_color = fastf1.plotting.get_team_color(driv1_lap['Team'], session=session)
drv2_color = fastf1.plotting.get_team_color(driv2_lap['Team'], session=session)
```

- Setting up plot and adding label key for each driver:

```
fig, ax = plt.subplots()
ax.plot(driv1_tel['Distance'], driv1_tel['Speed'], color=drv1_color, label=driver1)
ax.plot(driv2_tel['Distance'], driv2_tel['Speed'], color=drv2_color, label=driver2)
```

- Vertical dotted lines at each corner and corner numbers:

```
v_min = driv1_tel['Speed'].min()
v_max = driv1_tel['Speed'].max()
ax.vlines(x=circuit_info.corners['Distance'], ymin=v_min-20, ymax=v_max+20, linestyles='dotted', colors='grey')

for _, corner in circuit_info.corners.iterrows():
    txt = f"{corner['Number']}{corner['Letter']}"
    ax.text(corner['Distance'], v_min-30, txt, va='center_baseline', ha='center', size='small')
```
- Formatting the graph with title and axis information:

```
ax.set_xlabel('Distance in m')
ax.set_ylabel('Speed in km/h')

ax.legend()
plt.suptitle(f"Fastest Lap Comparison\n "
             f"{session.event['EventName']} {session.event.year} {sess}\n"f"{driver1} lap is {lap_time_string}\n{driver2} lap is {lap_time_string2}")

plt.show()
```

















