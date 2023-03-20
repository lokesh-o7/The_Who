import io
import os
import wave
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage


# Set up Google Cloud Speech-to-Text API credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_secret_key.json'

# Set up the client and config for the API request
client = speech.SpeechClient()
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=44100,
    # audio_channel_count=2,
    language_code='en-US',
)

# Load the WAV file and convert it to LINEAR16 format
audio = AudioSegment.from_wav('OSR_us_000_0010_8k.wav')
audio = audio.set_channels(1)  # set to mono channel
audio = audio.set_frame_rate(44100)  # set to 44.1kHz
audio = audio.set_sample_width(2)  # set to 16-bit
raw_audio = audio.raw_data

# Prepare the API request with the LINEAR16 audio data
audio = speech.RecognitionAudio(content=raw_audio)

# Make the API request and print the transcription
response = client.recognize(config=config, audio=audio)
for result in response.results:
    print('Transcript: {}'.format(result.alternatives[0].transcript))

