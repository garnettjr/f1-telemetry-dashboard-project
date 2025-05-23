from flask import Flask, render_template, request, send_file, url_for
from io import BytesIO
import fastf1
import pandas as pd
from fastf1.core import Laps
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from timple.timedelta import strftimedelta
import fastf1.plotting
import base64

app = Flask(__name__)
fastf1.Cache.enable_cache('cache')  #caching

@app.route('/', methods=['GET', 'POST'])
def landing(): #landing page
    if request.method == 'POST':
        choice = request.form['choice']
        if choice == 'compare':
            return render_template('yearcompare.html')#gets year for comparing inside and passes foward
        elif choice == 'download': 
            return render_template('index.html')
    return render_template('landing.html')

@app.route('/select_event', methods=['POST']) #getting year for fastests laps
def index(): 
    if request.method == 'POST':
        year = request.form['year']
        events = fastf1.get_event_schedule(int(year), include_testing=False)
        event_names = events['EventName'].tolist()
        return render_template('select_event.html', events=event_names, year=year)
    
@app.route('/results', methods=['POST']) #getting event and session for fastest laps table
def results():
    year = request.form['year']
    gp = request.form['event']
    sess = request.form['session']
    
    
    session = fastf1.get_session(int(year), gp, sess)
    session.load()
    
    
    drivers = pd.unique(session.laps['Driver'])
    fastest_laps = Laps([session.laps.pick_drivers(drv).pick_fastest() for drv in drivers]) \
        .sort_values(by='LapTime').reset_index(drop=True)
    
    
    html_table = fastest_laps[['Driver', 'LapTime']].to_html(index=False)
    download_url = url_for('download_csv', year=year, gp=gp, sess=sess)
    
    return render_template('results.html', table=html_table, download_url=download_url, event=session.event['EventName'], sess=sess)

@app.route('/download_csv')
def download_csv():
    year = request.args.get('year')
    gp = request.args.get('gp')
    sess = request.args.get('sess')
    
    session = fastf1.get_session(int(year), gp, sess)
    session.load()
    
    drivers = pd.unique(session.laps['Driver'])
    fastest_laps = Laps([session.laps.pick_drivers(drv).pick_fastest() for drv in drivers]) \
        .sort_values(by='LapTime').reset_index(drop=True)
    
    csv_buffer = BytesIO()
    fastest_laps[['Driver', 'LapTime']].to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='fastestlaps.csv'
    )

@app.route('/comparelaps', methods=['POST'])#gets event for comparing laps
def comparelaps():
    if request.method == 'POST':
        year = request.form['year']
        events = fastf1.get_event_schedule(int(year), include_testing=False)
        event_names = events['EventName'].tolist()
        return render_template('compare_laps.html', events=event_names, year=year)

@app.route('/selectcomparison', methods=['POST'])#
def selectcomparison():
    if request.method == 'POST':
        year = request.form['year']
        gp = request.form['event']
        sess = request.form['session']
        
        session = fastf1.get_session(int(year), gp, sess)
        session.load()
        drivers = pd.unique(session.laps['Driver'])
        
        return render_template('selectcomparison.html', drivers=drivers, year=year, gp=gp, sess=sess)

@app.route('/generate_comparison', methods=['POST'])#creating comparison table
def generate_comparison():
    year = request.form['year']
    gp = request.form['gp']
    sess = request.form['sess']
    driver1 = request.form['driver1']
    driver2 = request.form['driver2']
    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')
    session = fastf1.get_session(int(year), gp, sess)
    session.load()
    circuit_info = session.get_circuit_info()#getting circuit for corner numbers
    driv1_lap = session.laps.pick_drivers(driver1).pick_fastest()#drivers fastest laps
    driv2_lap = session.laps.pick_drivers(driver2).pick_fastest()
        
    
    driv1_tel = driv1_lap.get_car_data().add_distance()#getting lap with distance for table
    driv2_tel = driv2_lap.get_car_data().add_distance()
        
        
    drv1_color = fastf1.plotting.get_team_color(driv1_lap['Team'], session=session)
    drv2_color = fastf1.plotting.get_team_color(driv2_lap['Team'], session=session)
        
        
    lap_time_string = strftimedelta(driv1_lap['LapTime'], '%m:%s.%ms')#total laptime of both 
    lap_time_string2 = strftimedelta(driv2_lap['LapTime'], '%m:%s.%ms')

        
    fig, ax = plt.subplots()#make the plot
    ax.plot(driv1_tel['Distance'], driv1_tel['Speed'], color=drv1_color, label=driver1)
    ax.plot(driv2_tel['Distance'], driv2_tel['Speed'], color=drv2_color, label=driver2)
        
        
    v_min = driv1_tel['Speed'].min()
    v_max = driv1_tel['Speed'].max()
    ax.vlines(x=circuit_info.corners['Distance'], ymin=v_min-20, ymax=v_max+20, linestyles='dotted', colors='grey')
        
    for _, corner in circuit_info.corners.iterrows():#corner numbers
        txt = f"{corner['Number']}{corner['Letter']}"
        ax.text(corner['Distance'], v_min-30, txt, va='center_baseline', ha='center', size='small')

        
        ax.set_xlabel('Distance in m')
        ax.set_ylabel('Speed in km/h')
        ax.legend()
        plt.suptitle(f"Fastest Lap Comparison \n "
                    f"{session.event['EventName']} {session.event.year} {sess}\n"
                    f"{driver1} lap is {lap_time_string} {driver2} lap is {lap_time_string2}")

        
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=175)
    img_buffer.seek(0)
    plt.close(fig)
        
        
    img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')#put into html
        
    return render_template('comparison_result.html', img_data=img_data, driver1=driver1, driver2=driver2, event_name=session.event['EventName'], year=year, sess=sess, gp=gp)


if __name__ == '__main__':
    app.run(debug=True)
