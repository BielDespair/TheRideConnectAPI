from flask import Flask, request, jsonify
import secrets
from models import Event, Readings, db
import dotenv

dotenv.load_dotenv()
from app import app, db

# Prevents unnecessary warning
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.before_request
def create_tables():
    db.create_all()

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

@app.route('/events/<int:event_id>/readings', methods=['GET'])
def get_and_delete_readings(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    api_token = request.args.get('api_token')
    if not api_token or api_token != event.api_token:
        return jsonify({'message': 'Token do aplicativo inválido ou ausente'}), 403
    
    readings = Readings.query.filter_by(event_id=event_id).all()
    if not readings:
        return jsonify({'message': 'Nenhuma leitura encontrada'}), 404
    
if __name__ == "__main__":
    app.run(debug=True)