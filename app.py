from flask import Flask, request, jsonify,render_template
import requests
import csv
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import aiohttp
import asyncio

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/event_database'
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100))
    city_name = db.Column(db.String(100))
    event_date = db.Column(db.Date)
    event_time = db.Column(db.Time)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

events=[]
latitude=0.0
longitude=0.0

def fetch_weather(city, date):
    api_url = "https://gg-backend-assignment.azurewebsites.net/api/Weather"
    params = {
        "code": "Your_Code",
        "city": city,
        "date": date.strftime('%Y-%m-%d')
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()['weather']
    else:
        return "N/A"

def calculate_distance(lat1, lon1, lat2, lon2):
    api_url = "https://gg-backend-assignment.azurewebsites.net/api/Distance"
    params = {
        "code": "Your_Code",
        "latitude1": lat1,
        "longitude1": lon1,
        "latitude2": lat2,
        "longitude2": lon2
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()['distance']
    else:
        return "N/A"
    
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/events/add')
def add_events():
    file_path = r'C:\Users\laksh\OneDrive\Desktop\python\Event_Management\Backend_assignment_gg_dataset - dataset.csv'
    if file_path and file_path.endswith('.csv'):
        try:
            with open(file_path, 'r') as csv_file:
                csv_data = csv.reader(csv_file)
                count=0
                for row in csv_data:
                    if count==0:
                        count=1
                        continue
                    if len(row) >= 6:
                        event_date = datetime.strptime(row[2], '%Y-%m-%d')
                        event = Event(
                            event_name=row[0],
                            city_name=row[1],
                            event_date=event_date,
                            event_time=row[3],
                            latitude=float(row[4]),
                            longitude=float(row[5])
                        )
                        db.session.add(event)
                    else:
                        return jsonify({"error": "Invalid row format"}), 400
                db.session.commit()
            return jsonify({"message": "Events added successfully"}), 201
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404
        except ValueError:
            return jsonify({"error": "Invalid date format in CSV"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format or file path"}), 400


async def fetch_weather_async(session, city, date):
    api_url = "https://gg-backend-assignment.azurewebsites.net/api/Weather"
    params = {
        "code": "Your_Code",
        "city": city,
        "date": date.strftime('%Y-%m-%d')
    }
    async with session.get(api_url, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            return "N/A"

async def calculate_distance_async(session, lat1, lon1, lat2, lon2):
    api_url = "https://gg-backend-assignment.azurewebsites.net/api/Distance"
    params = {
        "code": "Your_Code",
        "latitude1": lat1,
        "longitude1": lon1,
        "latitude2": lat2,
        "longitude2": lon2
    }
    async with session.get(api_url, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            return "N/A"

async def process_event_async(session, event, latitude, longitude):
    weather_task = fetch_weather_async(session, event.city_name, event.event_date)
    distance_task = calculate_distance_async(session, latitude, longitude, event.latitude, event.longitude)
    weather_result = await weather_task
    distance_result = await distance_task
    return {
        "event_name": event.event_name,
        "city_name": event.city_name,
        "date": event.event_date.strftime('%Y-%m-%d'),
        "weather": weather_result['weather'] if 'weather' in weather_result else "N/A",
        "distance_km": distance_result['distance'] if 'distance' in distance_result else "N/A"
    }

async def fetch_events_async(events, latitude, longitude):
    async with aiohttp.ClientSession() as session:
        tasks = [process_event_async(session, event, latitude, longitude) for event in events]
        return await asyncio.gather(*tasks)

@app.route('/events/find', methods=['POST'])
async def find_events_async():
    global events
    global latitude
    global longitude
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    end_date = date + timedelta(days=14)

    events = Event.query.filter(Event.event_date.between(date, end_date)).order_by(Event.event_date).all()

    page = 1
    per_page = 10
    total_events = len(events)
    total_pages = (total_events + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page

    events_data = await fetch_events_async(events[start:end], latitude, longitude)

    response_data = {
        "events": events_data,
        "page": page,
        "pageSize": per_page,
        "totalEvents": total_events,
        "totalPages": total_pages
    }

    return render_template('fetch.html', data=response_data)


@app.route('/events/fetch',methods=['POST'])
async def fetch():
    page = int(request.form['page'])
    per_page = 10
    total_events = len(events)
    total_pages = (total_events + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = min(start + per_page, total_events)

    events_data = await fetch_events_async(events[start:end], latitude, longitude)

    response_data = {
        "events": events_data,
        "page": page,
        "pageSize": per_page,
        "totalEvents": total_events,
        "totalPages": total_pages
    }

    return render_template('fetch.html', data=response_data)

if __name__ == '__main__':
    app.run(debug=True)
