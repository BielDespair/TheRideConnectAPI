from flask import request, jsonify
import secrets
from models import Event, Readings, db

from server import app, db

# Prevents unnecessary warning
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.before_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Hello, World!'}), 200

@app.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    
    name = data.get('name')
    if not name:
        return jsonify({'message': 'Nome do evento ausente'}), 400
    api_token = secrets.token_hex(32)
    
    event = Event()
    event.name = name
    event.api_token = api_token
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify({
        'id': event.id, 
        'api_token': event.api_token  # Retorna a chave única
    }), 201

@app.route('/events/<event_id>/readings', methods=['POST'])
def handle_readings(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    data = request.get_json()
    api_token = data.get('api_token')
    
    if not api_token or api_token != event.api_token:
        return jsonify({'message': 'Token do aplicativo inválido ou ausente'}), 403
    readings = data.get('readings')
    if not readings or not isinstance(readings, list):
        return jsonify({'message': 'Leituras ausentes'}), 400
    
    for reading in readings:
        tag_epc = reading.get('tag_epc')
        timestamp = reading.get('timestamp')
        if not tag_epc or not timestamp:
            return jsonify({'message': 'Tag epc ou timestamp ausentes'}), 400
        
        new_reading = Readings()
        new_reading.tag_epc = tag_epc
        new_reading.timestamp = timestamp
        new_reading.event_id = event_id
        
        db.session.add(new_reading)
    db.session.commit()
    
    return jsonify({'message': f'{len(readings)} leituras adicionadas com sucesso'}, 200)

@app.route('/events/<event_id>/readings', methods=['GET'])
def get_event_readings(event_id):

    event = Event.query.get(event_id)
    
    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    data = request.get_json()
    api_token = data.get('api_token')
    
    if not api_token or api_token != event.api_token:
        return jsonify({'message': 'Token do aplicativo inválido ou ausente'}), 403
    
    readings = Readings.query.filter_by(event_id=event_id).all()
    json = {
        'readings': []
    }
    readings_ids = [reading.id for reading in readings]
    for reading in readings:
        if not reading.collected:
            print(reading.collected)
            reading_json = {
                'tag_epc': reading.tag_epc,
                'timestamp': reading.timestamp
            }
            json['readings'].append(reading_json)
    
    for reading in readings:
        reading.collected = 1
    db.session.commit()
    
    return jsonify(json), 200

@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    json = {
        'events': []
    }
    for event in events:
        json['events'].append({
            'id': event.id,
            'name': event.name
        })
    return jsonify(json), 200

if __name__ == "__main__":
    app.run()