from huggingface_hub import InferenceClient
from google.cloud import texttospeech
from google.cloud import speech
import os
import sounddevice as sd
import soundfile as sf
from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play
import io
import tempfile
from time import sleep


# Définir un dossier temporaire personnalisé
tempfile.tempdir = os.path.expanduser("~/temp_audio")
if not os.path.exists(tempfile.tempdir):
    os.makedirs(tempfile.tempdir)

# Load the API key from a separate file
with open("private/nebius_api_key.txt", "r") as key_file:
    nebius_api_key = key_file.read().strip()

llm_client = InferenceClient(
    provider="nebius",
    api_key=nebius_api_key,
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="private/key.json"

# Nouveau contexte
context = "Tu es une fausse victime d'arnaque. Tu es en train de discuter avec un arnaqueur qui prétend offrir un emploi. Ton objectif est de lui faire perdre du temps en lui posant des questions et en simulant un intérêt sincère."

# Nouvelle description de l'arnaque
arnaque = "L'arnaque consiste à faire croire à la victime qu'elle a été sélectionnée pour un emploi prestigieux, mais qu'elle doit payer des frais pour le traitement de son dossier ou pour une formation obligatoire."

# Nouvelle personnalité
personnalite = "Tu es une personne de 28 ans, qui vit à Lyon. Ton nom est MARTIN MARTIN. Tu es enthousiaste et tu sembles vraiment intéressée par l'offre d'emploi. Tu poses beaucoup de questions sur le poste, les responsabilités, et les avantages. Tu es polie mais parfois un peu naïve."

# Nouvelles instructions
instructions = "Tu dois faire perdre du temps à l'escroc. Pose-lui des questions détaillées sur l'emploi, les conditions, et les étapes du processus. Fais semblant d'être intéressée et enthousiaste. Donne des réponses courtes mais variées. Garde l'escroc engagé en montrant de l'intérêt pour son offre."

# Nouvelles instructions négatives
negative = "Tu ne dois pas dire que tu es une IA ni que tu es un robot. Si l'escroc te demande si tu es une IA, tu dois te montrer offensée et nier fermement. Ne révèle jamais que tu sais que c'est une arnaque."

# Nouveaux lapsus
lapsus = "Tu fais des lapsus et des erreurs de langage. Tu hésites parfois et tu reformules tes phrases. Ajoute des pauses et des hésitations comme [pause], [euh], [hum], ou [long silence]. Parfois, tu te contredis ou tu oublies ce que tu viens de dire."

messages=[
        {
            "role": "system",
            "content": context + "\n" + arnaque + "\n" + instructions + "\n" + negative + "\n" + lapsus,
        }
    ]


def record_and_transcribe():
        # Record audio from the microphone
        duration = 8  # seconds
        sample_rate = 44100  # Hz
        print("Recording...")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished
        print("Recording finished.")

        # Save the recorded audio to a file
        sf.write('cache/voice.flac', audio_data, sample_rate)
        
        # Transcribe the audio using Google Cloud Speech-to-Text
        speech_client = speech.SpeechClient()
        with open("cache/voice.flac", "rb") as audio_file:
            content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            sample_rate_hertz=44100,
            language_code="fr-FR",
        )
        speech_result = speech_client.recognize(config=config, audio=audio)
        
        if len(speech_result.results) == 0:
            print("Aucune voix détectée.")
            return None
        return speech_result.results[0].alternatives[0].transcript

def process_user_input(user_input, messages, llm_client):
    messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    completion = llm_client.chat.completions.create(
        model="Qwen/Qwen2.5-32B-Instruct",
        messages=messages,
        max_tokens=1512,
        temperature=0.9
    )

    reponse = completion.choices[0].message.content
    print(reponse)

    messages.append(
        {
            "role": "assistant",
            "content": reponse,
        }
    )
    return reponse

def process_user_input_streaming(user_input, messages, llm_client):
    messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    # Activer le streaming pour les réponses
    completion = llm_client.chat.completions.create(
        model="Qwen/Qwen2.5-32B-Instruct",
        messages=messages,
        max_tokens=1512,
        temperature=0.9,
        stream=True  # Activer le streaming
    )

    reponse = ""
    for chunk in completion:
        delta_content = chunk.choices[0].delta.content
        if delta_content:
            reponse += delta_content
            print(delta_content, end="", flush=True)  # Affiche en temps réel
            yield delta_content  # Retourne chaque morceau pour le traitement en streaming
    print()

    messages.append(
        {
            "role": "assistant",
            "content": reponse,
        }
    )

def synthesize_speech(reponse):
    tts_client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=reponse)

    # Build the voice request, select the language code ("fr-FR") 
    # and the ssml voice gender ("female")
    voice = texttospeech.VoiceSelectionParams(
        language_code='fr-FR',
        name='fr-FR-Chirp-HD-O',
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Ensure the cache directory exists
    if not os.path.exists('cache'):
        os.makedirs('cache')

    # Define the output path
    output_path = 'cache/output.mp3'

    # Remove the file if it already exists
    if os.path.exists(output_path):
        os.remove(output_path)

    # Write the response to the output file
    with open(output_path, 'wb') as out:
        out.write(response.audio_content)
        print(f'Audio content written to file \"{output_path}\"')

    # Lire le fichier audio
    playsound(output_path)  # Lecture du fichier audio
    return output_path

def synthesize_speech_streaming(text_stream):
    tts_client = texttospeech.TextToSpeechClient()

    # Accumuler les morceaux de texte pour former des phrases complètes
    accumulated_text = ""
    for text_chunk in text_stream:
        text_chunk = text_chunk.strip()
        if not text_chunk:
            continue

        # Ajouter le morceau au texte accumulé
        accumulated_text += text_chunk + " "

        # Si le morceau contient une ponctuation forte, on considère que la phrase est complète
        if any(punct in text_chunk for punct in [".", "!", "?"]):
            try:
                # Préparer la synthèse vocale pour la phrase complète
                synthesis_input = texttospeech.SynthesisInput(text=accumulated_text.strip())
                voice = texttospeech.VoiceSelectionParams(
                    language_code='fr-FR',  # Essayez 'fr-CA' pour un accent canadien
                    name='fr-FR-Standard-A',  # Essayez une voix standard ou canadienne
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=0.9,  # Réduire la vitesse pour une diction plus claire
                    pitch=-2  # Ajuster le ton pour un son plus naturel
                )

                # Effectuer la synthèse vocale
                response = tts_client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

                # Sauvegarder l'audio dans un fichier temporaire dans le dossier cache
                if not os.path.exists('cache'):
                    os.makedirs('cache')
                temp_audio_path = os.path.join('cache', 'temp_output.mp3')

                with open(temp_audio_path, 'wb') as temp_audio_file:
                    temp_audio_file.write(response.audio_content)

                # Lire le fichier audio avec playsound
                playsound(temp_audio_path)

                # Supprimer le fichier temporaire après lecture
                os.remove(temp_audio_path)

                # Réinitialiser le texte accumulé
                accumulated_text = ""
            except Exception as e:
                print(f"❌ Erreur lors de la synthèse ou de la lecture audio : {e}")

    # Si du texte reste accumulé après la boucle, le synthétiser
    if accumulated_text.strip():
        try:
            synthesis_input = texttospeech.SynthesisInput(text=accumulated_text.strip())
            voice = texttospeech.VoiceSelectionParams(
                language_code='fr-FR',
                name='fr-FR-Standard-A',
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.9,  # Réduire la vitesse pour une diction plus claire
                pitch=-2  # Ajuster le ton pour un son plus naturel
            )

            response = tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            temp_audio_path = os.path.join('cache', 'temp_output.mp3')
            with open(temp_audio_path, 'wb') as temp_audio_file:
                temp_audio_file.write(response.audio_content)

            playsound(temp_audio_path)
            os.remove(temp_audio_path)
        except Exception as e:
            print(f"❌ Erreur lors de la synthèse ou de la lecture audio : {e}")

# Boucle principale
while True:
    user_input = record_and_transcribe()
    if not user_input:
        continue
    print("Escroc : ", user_input)

    # Traiter l'entrée utilisateur et générer une réponse en streaming
    text_stream = process_user_input_streaming(user_input, messages, llm_client)

    # Synthétiser et lire la réponse en streaming
    synthesize_speech_streaming(text_stream)