import discord
from discord.ext import commands
import time
import os
import subprocess
import io
from google.cloud import speech
from google.cloud import storage

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Set up Google Cloud Speech-to-Text API credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_secret_key.json'

# bot = discord.Bot(command_prefix='?', intents=intents)
bot = commands.Bot(command_prefix='?', intents=intents)
connections = {}
t0 = 0
t_total = 0


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def start_rec(ctx):  # If you're using commands.Bot, this will also work.
    async def once_done(sink: discord.sinks, channel: discord.TextChannel,
                        *args):  # Our voice client already passes these in.
        recorded_users = [  # A list of recorded users
            f"<@{user_id}>"
            for user_id, audio in sink.audio_data.items()
        ]
        await sink.vc.disconnect()  # Disconnect from the voice channel.
        files = []  # List to store the file paths.

        directory = os.path.join(os.getcwd(),
                                 "recordings")  # Create a directory named recordings in the same path as the script.
        if not os.path.exists(directory):  # Check if the directory exists or not.
            os.makedirs(directory)  # If not, create the directory.

        for user_id, audio in sink.audio_data.items():
            filename = f"{user_id}.{sink.encoding}"
            filepath = os.path.join(directory, filename)

            with open(filepath, 'wb') as f:
                f.write(audio.file.read())

            files.append(discord.File(filepath, filename=filename))  # Append the file path to the list.
        await channel.send(f"finished recording audio for: {', '.join(recorded_users)}.",
                           files=files)  # Send a message with the accumulated files.

        transcribe_audio()

    voice = ctx.author.voice

    if not voice:
        await ctx.send("You aren't in a voice channel!")

    vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
    connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.

    vc.start_recording(
        discord.sinks.MP3Sink(),  # The sink type to use.
        once_done,  # What to do once done.
        ctx.channel  # The channel to disconnect from.
    )
    await ctx.send("Started recording!")
    global t0
    t0 = time.time()


@bot.command()
async def stop_rec(ctx):
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        vc = connections[ctx.guild.id]
        vc.stop_recording()  # Stop recording, and call the callback (once_done).
        del connections[ctx.guild.id]  # Remove the guild from the cache.
        # await ctx.delete()  # And delete.
    else:
        await ctx.send("I am currently not recording here.")  # Respond with this if we aren't recording.


@bot.command()
async def rec_time(ctx):
    await ctx.send("Recording time: {}".format(time.time() - t0))


def transcribe_audio():
    # Set up audio files directory
    audio_files_dir = "recordings/"

    # Use FFmpeg to convert audio files to LINEAR16 encoding format and upload to Google Cloud Storage
    for audio_file_name in os.listdir(audio_files_dir):
        audio_file_path = os.path.join(audio_files_dir, audio_file_name)
        if audio_file_name.endswith(".mp3"):
            # Convert audio file to LINEAR16 format using FFmpeg
            subprocess.run(
                ['ffmpeg', '-i', audio_file_path, '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', 'audio.wav'],
                check=True)

            # Upload the converted audio file to Google Cloud Storage
            storage_client = storage.Client()
            bucket_name = 'discord_speech_to_text'
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(audio_file_name.replace(".mp3", ".wav"))
            blob.upload_from_filename('audio.wav')

            # Define audio file configuration
            audio_config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code='en-US',
                enable_automatic_punctuation=True,
                audio_channel_count=1,
                enable_word_time_offsets=True,
            )

            # Define recognition job configuration
            job_config = speech.LongRunningRecognizeRequest(
                audio=speech.RecognitionAudio(
                    uri='gs://' + bucket_name + '/' + audio_file_name.replace(".mp3", ".wav")),
                config=audio_config,
            )

            # Create client object
            client = speech.SpeechClient()

            # Start recognition job
            operation = client.long_running_recognize(request=job_config)

            # Wait for recognition job to complete
            response = operation.result()

            # Get transcribed text from response
            transcription = ''
            word_timestamps = []
            for result in response.results:
                transcription += result.alternatives[0].transcript
                for word in result.alternatives[0].words:
                    word_timestamps.append((word.word, word.start_time.total_seconds(), word.end_time.total_seconds()))

            print(transcription)
            print(word_timestamps)

            # Write transcribed text and word timestamps to a text file
            with open(audio_file_name.replace(".mp3", ".txt"), "w") as f:
                f.write("Transcription:\n{}\n\nWord Timestamps:\n".format(transcription))
                for word_timestamp in word_timestamps:
                    f.write("{}, {:.2f}, {:.2f}\n".format(word_timestamp[0], word_timestamp[1], word_timestamp[2]))

            # Delete the converted audio file from local storage
            os.remove('audio.wav')

            # delete the transcript recordings
            for filename in os.listdir(audio_files_dir):
                os.remove(os.path.join(audio_files_dir, filename))


bot.run('')
