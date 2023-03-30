import discord
import os
import io
import asyncio
import aiohttp
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
# Discord bot token
TOKEN = 'MTA5MDY5Mjk2NjY1NTQ2NzU0MA.GsjN7W.R5EB-7gtkoUyyV1Z7ld5TgQg99annFVo51d9EY'

# Google Cloud credentials
CREDENTIALS_FILE = 'path/to/credentials.json'
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE)

# Language codes supported by Google Cloud Speech-to-Text
LANGUAGES = {
    'en-US': 'English (United States)',
    'es-ES': 'Spanish (Spain)',
    'fr-FR': 'French (France)',
    'de-DE': 'German (Germany)',
    'it-IT': 'Italian (Italy)',
    'ja-JP': 'Japanese (Japan)',
    'ko-KR': 'Korean (South Korea)',
    'pt-BR': 'Portuguese (Brazil)',
    'ru-RU': 'Russian (Russia)',
    'zh-CN': 'Chinese (Simplified, China)',
    'zh-TW': 'Chinese (Traditional, Taiwan)'
}

# Maximum recording duration in seconds
MAX_RECORDING_DURATION = 300

# Voice channels where the bot is allowed to join and record
ALLOWED_CHANNELS = ['voice_channel_1', 'voice_channel_2']

# Google Cloud Speech-to-Text configuration
client = speech.SpeechClient(credentials=credentials)
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
    sample_rate_hertz=48000,
    language_code='en-US',
    use_enhanced=True,
    model='phone_call'
)




