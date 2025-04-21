from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import base64
import os
from anti_scam import process_user_input_streaming, llm_client  # Importer la fonction et le client LLM

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Route pour servir l'interface HTML
@app.route('/')
def index():
    return render_template('index.html')

# Gérer les messages de chat envoyés par l'utilisateur
@socketio.on('chat_message')
def handle_chat_message(message):
    print(f"Message reçu : {message}")
    try:
        response = "Ceci est une réponse statique de l'IA."
        print(f"Réponse générée : {response}")
        emit('chat_message', {'user': 'AI', 'message': response}, broadcast=True)
    except Exception as e:
        print(f"Erreur : {e}")
        emit('chat_message', {'user': 'AI', 'message': "Désolé, une erreur est survenue."}, broadcast=True)

# Gérer les flux audio envoyés par l'utilisateur
@socketio.on('audio_stream')
def handle_audio_stream(data):
    print("Audio reçu")
    # Décoder l'audio base64 et le sauvegarder dans un fichier temporaire
    audio_data = base64.b64decode(data)
    temp_audio_path = 'cache/temp_audio.wav'
    with open(temp_audio_path, 'wb') as audio_file:
        audio_file.write(audio_data)

    # Simuler une détection d'émotion (par exemple, "neutre")
    detected_emotion = "neutre"
    emit('emotion_detected', detected_emotion, broadcast=True)

    # Supprimer le fichier temporaire après traitement
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)