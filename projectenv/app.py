from flask import Flask, render_template, request, send_file, url_for
from io import BytesIO
import fastf1
import pandas as pd
from fastf1.core import Laps

app = Flask(__name__)
fastf1.Cache.enable_cache('cache')  # Enable caching for faster loading

@app.route('/', methods=['GET', 'POST'])
def landing():
    if request.method == 'POST':
        choice = request.form['choice']
        if choice == 'compare':
            return render_template('compare_laps.html')
        elif choice == 'download': 
            return render_template('index.html')
    return render_template('landing.html')

@app.route('/index', methods=['POST'])
def index():
    if request.method == 'POST':
        year = request.form['year']
        events = fastf1.get_event_schedule(int(year), include_testing=False)
        event_names = events['EventName'].tolist()
        return render_template('select_event.html', events=event_names, year=year)
    
@app.route('/results', methods=['POST'])
def results():
    year = request.form['year']
    gp = request.form['event']
    sess = request.form['session']
    
    
    session_f1 = fastf1.get_session(int(year), gp, sess)
    session_f1.load()
    
    # Get fastest laps
    drivers = pd.unique(session_f1.laps['Driver'])
    fastest_laps = Laps([session_f1.laps.pick_drivers(drv).pick_fastest() for drv in drivers]) \
        .sort_values(by='LapTime').reset_index(drop=True)
    
    # Generate HTML table
    html_table = fastest_laps[['Driver', 'LapTime']].to_html(index=False)
    download_url = url_for('download_csv', year=year, gp=gp, sess=sess)
    
    return render_template('results.html', table=html_table, download_url=download_url)

@app.route('/download_csv')
def download_csv():
    year = request.args.get('year')
    gp = request.args.get('gp')
    sess = request.args.get('sess')
    
    # Regenerate CSV
    session_f1 = fastf1.get_session(int(year), gp, sess)
    session_f1.load()
    
    drivers = pd.unique(session_f1.laps['Driver'])
    fastest_laps = Laps([session_f1.laps.pick_drivers(drv).pick_fastest() for drv in drivers]) \
        .sort_values(by='LapTime').reset_index(drop=True)
    
    # Create in-memory CSV
    csv_buffer = BytesIO()
    fastest_laps[['Driver', 'LapTime']].to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='fastestlaps.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
