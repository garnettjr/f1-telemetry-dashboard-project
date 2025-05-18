import fastf1
import matplotlib.pyplot as plt
import fastf1.plotting
from timple.timedelta import strftimedelta

driver1 = input("Select first driver(THREE LETTER ABBREVIATION): ")
driver2 = input("Select second driver(THREE LETTER ABBREVIATION): ")
year = int(input("Select a year 2018-now inclusive: "))
gp = input("Select a race event: ")
sess = input("Select a session FP1 FP2 FP3 Q R: ")

fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme=None)
session = fastf1.get_session(year, gp, sess)
session.load()
circuit_info = session.get_circuit_info()

driv1_lap = session.laps.pick_drivers(driver1).pick_fastest()
driv2_lap = session.laps.pick_drivers(driver2).pick_fastest()

driv1_tel = driv1_lap.get_car_data().add_distance()
driv2_tel = driv2_lap.get_car_data().add_distance()

drv1_color = fastf1.plotting.get_team_color(driv1_lap['Team'], session=session)
drv2_color = fastf1.plotting.get_team_color(driv2_lap['Team'], session=session)

lap_time_string = strftimedelta(driv1_lap['LapTime'], '%m:%s.%ms')
lap_time_string2 = strftimedelta(driv2_lap['LapTime'], '%m:%s.%ms')

fig, ax = plt.subplots()
ax.plot(driv1_tel['Distance'], driv1_tel['Speed'], color=drv1_color, label=driver1)
ax.plot(driv2_tel['Distance'], driv2_tel['Speed'], color=drv2_color, label=driver2)
v_min = driv1_tel['Speed'].min()
v_max = driv1_tel['Speed'].max()

ax.vlines(x=circuit_info.corners['Distance'], ymin=v_min-20, ymax=v_max+20,
          linestyles='dotted', colors='grey')

for _, corner in circuit_info.corners.iterrows():
    txt = f"{corner['Number']}{corner['Letter']}"
    ax.text(corner['Distance'], v_min-30, txt,
            va='center_baseline', ha='center', size='small')

ax.set_xlabel('Distance in m')
ax.set_ylabel('Speed in km/h')

ax.legend()
plt.suptitle(f"Fastest Lap Comparison \n "
             f"{session.event['EventName']} {session.event.year} {sess}\n"f"{driver1} lap is {lap_time_string}\n{driver2} lap is {lap_time_string2}")

plt.show()



