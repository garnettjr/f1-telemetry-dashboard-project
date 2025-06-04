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
- Gunicorn
- Nginx

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
- The first script is a console based application and was built to learn the api and python simultaneously as I had no prior experience with either. In order to learn the api and how to use the correct functions I followed some of the examples from Fastf1 and changed it to do what I wanted. Used to compare two drivers laps againnst each other.
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

# Second Script
-This script is for downloading the fastests laps of all drivers from a session chosen by the user. It's another console based application. From the knowledge gained making the last script this one was much easier.
- Import the libraries:

```
import fastf1
from fastf1.core import Laps
import pandas as pd
```

- Next we get the choices of what session the user wants to use:

```
year = int(input("Select a year 2018-now inclusive: "))
events = fastf1.get_event_schedule(year, include_testing = False)
print("select an event from these: ")
print(events[['EventName', 'Location']])
gp = input("Select a race event: ")
sess = input("Select a session FP1 FP2 FP3 Q R: ")

```

- Then load the session with the paramters chosen by the user:

```
session = fastf1.get_session(year, gp, sess)
session.load()
```

- Create a list of all the drivers in that session and print it:

```
drivers = pd.unique(session.laps['Driver'])
print(drivers)
```

- Create a list of the fastest laps, then use a for loop to iterate through the drivers laps, append that lap to the list and then make a list with the ordered laps from fastest to slowest:

```
list_fastest_laps = list()
for drv in drivers:
    drvs_fastest_lap = session.laps.pick_drivers(drv).pick_fastest()
    list_fastest_laps.append(drvs_fastest_lap)
fastest_laps = Laps(list_fastest_laps) \
    .sort_values(by='LapTime') \
    .reset_index(drop=True)
```

- Print that list into the console:

```
print(fastest_laps[['Driver', 'LapTime']])
```

- Finally the main part of this script:

```
fastest_laps[['Driver', 'LapTime']].to_csv('fastestlaps.csv', index=False)
```

- This creates a csv file with the fastest laps inside it. The index=False makes the list cleaner by removing the index of each driver from the output.

# Flask application
- This was one of the more difficult parts of the project as I had to learn multiple different things like routing the backend and variables passing through the different routes. 
- Import the libraries:

```
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
```

- You should notice some new libaries for the backend. Matplotlib use 'Agg' allows us to put the graph onto webpage instead of just locally, base64 and BytesIO are for the csv download and putting the graph into html. 

- Create an instance of Flask so it knows where to look for templates and static files:

```
app = Flask(__name__)
```

- Enable caching into a directory:

```
fastf1.Cache.enable_cache('<directory of choice>') 
```

- First route is the page we see when we visit the webpage, this is a 'GET' request, because of this we include this in our methods and have a html template for when the method used to access this route is a 'GET'. 

```
@app.route('/', methods=['GET', 'POST'])
def landing(): #landing page
    if request.method == 'POST':
        choice = request.form['choice']
        if choice == 'compare':
            return render_template('yearcompare.html')#gets year for comparing inside and passes foward
        elif choice == 'download': 
            return render_template('index.html')
    return render_template('landing.html')
```

- as you see the landing page is what the user will see first, then when an option is selected it becomes a 'POST' method. The selection is stored in a variable and an if statement is used to route correctly to the next page.

- From the first page, the year the user wants to use is passed through to the next route, which for either choice is the same but lead to different places:

```
@app.route('/select_event', methods=['POST']) #getting event for fastests laps
def index(): 
    if request.method == 'POST':
        year = request.form['year']
        events = fastf1.get_event_schedule(int(year), include_testing=False)
        event_names = events['EventName'].tolist()
        return render_template('select_event.html', events=event_names, year=year)

@app.route('/comparelaps', methods=['POST'])#gets event for comparing laps
def comparelaps():
    if request.method == 'POST':
        year = request.form['year']
        events = fastf1.get_event_schedule(int(year), include_testing=False)
        event_names = events['EventName'].tolist()
        return render_template('compare_laps.html', events=event_names, year=year)
```

- This is where the user selects the event and session from the year, looking now it could definitly be improved into one route.

- If the user chose to download the fastest lap csv, then the next step is displaying the table of fastest laps:

```
@app.route('/results', methods=['POST']) #creating fastest laps table
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
```

- As you can see this is very similar to the console script that was made excpet used in a flask application. As it will be hosted on a weak AWS instance, instead of making two lists for laps I made one to save some memory. The table is served to the frontend with a url attached to activate the download button.

- Download csv route:

```
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
    
    csv = BytesIO()
    fastest_laps[['Driver', 'LapTime']].to_csv(csv, index=False)
    csv.seek(0)
    
    return send_file(
        csv,
        mimetype='text/csv',
        as_attachment=True,
        download_name='fastestlaps.csv'
    )
```

- This is the same as the previous route except now we save the table into a csv file in memory, name the file and the user can download it. Similar to the previous routes there is definitely room for improvement here, but this was the solution at the time.

- If comparing laps was chosen this is the next step, create a list of drivers from the session, serve it to the frontend and let the user choose:

```
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
```

- Now for displaying the graph on the webpage:

```
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
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
    img_buffer.seek(0)
    plt.close(fig)
        
        
    img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')#put into html
        
    return render_template('comparison_result.html', img=img, driver1=driver1, driver2=driver2, event_name=session.event['EventName'], year=year, sess=sess, gp=gp)
```

- Again this is the same as the script except we use bytesIO to save the image and then base64 to embedd into html, it all gets passed to the frontend as variable parameters. 

- In order to have the app run we need:

```
if __name__ == '__main__':
    app.run(debug=True)
```

- If you would like you can change what port it runs on in the parameters here. The defualt is 5000. 

# IMPORTANT Flask information
- HTML templates need to be in a folder called templates in the same directory as your flask application, also if any static files are used they need to be in a folder called static in the same directory as your application. Names can be changed as long as you change the path accordingly, but for good practice use these. 

# Webpage Visuals Documentation
- As I didn't use wordpress or anything similar, I made the webpage from scratch, using html and bootstrap css.

- All of the html pages I used are in the templates folder of this repository and the images for the pages are in the static folder.

- Using bootstrap you need to include this at the top: 

```
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.6/dist/css/bootstrap.min.css" rel="stylesheet">
```

- and this at the bottom

```
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.6/dist/js/bootstrap.bundle.min.js"></script>
```
- The link comes just before the styling of the webpage and the script is included in the body tags of the html, these allow you to use boostraps classes. You can use the html pages I made, modify them or completly make your own.

- all of my templates will have something like this in them

```
<style>
        body {
          padding: 20px;
          background-image: url("{{url_for('static', filename='f1mon.png')}}");
          background-size: cover;
          background-attachment: fixed;
        }
        .container {
          max-width: 500px;
          margin-top: 10px;
        }
        h1 {
          margin-bottom: 10px;
          text-align: center;
          color: black;
        }
        .form-select {
          margin-bottom: 20px;
        }
    </style>
```

- These are classes you make to then use on the webpage. It makes up the visual styling of the webpage. Body is just the main part of the webpage, use it to control things like the bakcground. Container is the main area on the webpage that displays the text and has the button in it. Changing the value of px you can change the size of each part. Bootstrap also comes with classes pre made for you to use straight away, like the button preset I used. When you have "." infront of the name you use it as a class, otherwise its styling. 

```
<body>
    <div class="container">
        <div class="card shadow">
            <div class="card-body">
                <h1 class="card-title">Select Event</h1>
```

- in order to use these classes you put them inside a "div" tag, as seen above. 

- you can see I've used the container class to hold everything below it, the styling of h1 with also be used as I'm using the tag.

# Deploying webserver to aws instance
- make sure ports 80, 443, and 5000 are open in your aws instance
- in virtual environment run:

```
pip install gunicorn
```

- then:

```
sudo apt install nginx -y
```

- run gunicorn to test app:

```
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

- test it at your-server-ip:5000

# Setup nginx

- create a config file:

```
sudo vi /etc/nginx/sites-available/f1-telemetry
```

- paste this in, change <your-server-ip>:

```
server {
    listen 80;
    server_name <your-server-ip>;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

- enable the site using a symlink, run:

```
sudo ln -s /etc/nginx/sites-available/f1-telemetry /etc/nginx/sites-enabled
sudo nginx -t       
sudo systemctl restart nginx
```

- now visit your webpage at your-server-ip

- you may get a 502 bad gateway error which means gunicorn isn't running
- to fix run:

```
screen -S gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

- this creates a detached screen, then you enable gunicorn, to detach from the screen press CTRL+A and then D, then restart nginx

# Adding SSL 

- create an elastic ip and point to it with your domain usng an A record
- install certbot:

```
sudo apt install certbot python3-certbot-nginx -y
```

- run certbot with nginx:

```
sudo certbot --nginx -d yourdomain.com
```

- should get a response to say certificate recieved
 
- now to update enginx config

- access config file we made eariler and add this:

```
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

- after this the config file we made will not be used so we need to remove the default config and create a symlink again:

```
sudo rm /etc/nginx/sites-enabled/default
```

```
sudo ln -sf /etc/nginx/sites-available/f1-telemetry /etc/nginx/sites-enabled/
sudo nginx -t              
sudo systemctl restart nginx
```

- restart nginx

- visit your domain and there should be a padlock in the browser

- you can verify the SSL with:

```
sudo certbot certificates
```

- will display domain and the expiration date


