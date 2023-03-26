import io
import os
from google.cloud import speech
from google.cloud import storage
import subprocess

# Set up Google Cloud Speech-to-Text API credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_secret_key.json'

# Set up audio file path
audio_uri = "audio_1.mp3"
# gs://discord_speech_to_text/audio_1.mp3

# Use FFmpeg to convert audio file to LINEAR16 encoding format
subprocess.run(['ffmpeg', '-i', audio_uri, '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', 'audio.wav'], check=True)


# Upload the converted audio file to Google Cloud Storage
storage_client = storage.Client()
bucket_name = 'discord_speech_to_text'
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob('audio.wav')
blob.upload_from_filename('audio.wav')

# Create client object
client = speech.SpeechClient()

# Define audio file configuration
audio_config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code='en-US',
    enable_automatic_punctuation=True,
    audio_channel_count=1,
)

# Define recognition job configuration
job_config = speech.LongRunningRecognizeRequest(
    audio=speech.RecognitionAudio(uri='gs://' + bucket_name + '/audio.wav'),
    config=audio_config,
)

# Start recognition job
operation = client.long_running_recognize(request=job_config)

# Wait for recognition job to complete
response = operation.result()

# Get transcribed text from response
transcription = ''
for result in response.results:
    transcription += result.alternatives[0].transcript

# Print transcribed text
print(transcription)

# Delete the converted audio file from local storage
os.remove('audio.wav')
