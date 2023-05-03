import discord
from discord.ext import commands
import time
import os
import subprocess
import io
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
import support_scripts
import pandas as pd
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Set up Google Cloud Speech-to-Text API credentials
this_dir = os.path.dirname(__file__)
key_path = os.path.join(this_dir, 'google_secret_key.json')
print(key_path, os.path.exists(key_path))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path

# bot = discord.Bot(command_prefix='?', intents=intents)
bot = commands.Bot(command_prefix='?', intents=intents)
connections = {}
t0 = 0
start_dt = None
t_total = 0


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def kill_bot(ctx):
    await bot.close()
    # exit()

@bot.command()
async def start_rec(ctx):  # If you're using commands.Bot, this will also work.
    global start_dt
    start_dt = datetime.today()#.strftime('%Y-%m-%d %H:%M:%S')
    # print(start_dt)
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
            user = bot.get_user(user_id)
            filename = f"{user.name}.{sink.encoding}"
            filepath = os.path.join(directory, filename)

            with open(filepath, 'wb') as f:
                f.write(audio.file.read())

            # files.append(discord.File(filepath, filename=filename))  # Append the file path to the list.
        await channel.send(f"finished recording audio for: {', '.join(recorded_users)}.")
                        #    files=files)  # Send a message with the accumulated files.

        await transcribe_and_send_to_discord(ctx)

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
        await vc.disconnect()
        del connections[ctx.guild.id]  # Remove the guild from the cache.
        # await ctx.delete()  # And delete.
    else:
        await ctx.send("I am currently not recording here.")  # Respond with this if we aren't recording.


@bot.command()
async def rec_time(ctx):
    await ctx.send("Recording time: {}".format(time.time() - t0))

@bot.command()
async def test(ctx):
    get_chan = "general_transcript"
    for chan_i in bot.get_all_channels():
        if chan_i.name == get_chan:
            chan_id = chan_i.id
    chan_obj = bot.get_channel(chan_id)
    await chan_obj.send("You have tested poting in a channel")

async def transcribe_and_send_to_discord(ctx):
    # Set up audio files directory
    audio_files_dir = "recordings/"
     # Define audio file configuration
    audio_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_automatic_punctuation=True,
        audio_channel_count=1,
        enable_word_time_offsets=True,
        alternative_language_codes=["de"],
    )

    # Use FFmpeg to convert audio files to LINEAR16 encoding format and upload to Google Cloud Storage
    user_transcripts = {}
    for audio_file_name in os.listdir(audio_files_dir):
        audio_file_path = os.path.join(audio_files_dir, audio_file_name)
        if audio_file_name.endswith(".mp3"):
            # Convert audio file to LINEAR16 format using FFmpeg
            subprocess.run(
                ['ffmpeg', '-y', '-i', audio_file_path, '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000',
                 'audio.wav'],
                check=True)

            # Upload the converted audio file to Google Cloud Storage
            storage_client = storage.Client()
            bucket_name = 'discord_speech_to_text'
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(audio_file_name.replace(".mp3", ".wav"))
            blob.upload_from_filename('audio.wav')

            audio=speech.RecognitionAudio(uri='gs://' + bucket_name + '/' + audio_file_name.replace(".mp3", ".wav"))
            # Define recognition job configuration
            job_config = speech.LongRunningRecognizeRequest(
                audio=audio,
                config=audio_config,
            )

            # Create client object
            client = speech.SpeechClient()

            # Start recognition job
            operation = client.long_running_recognize(request=job_config)
            # response = client.recognize(config=audio_config, audio=audio)

            # Wait for recognition job to complete
            response = operation.result()

            # Get transcribed text from response
            transcription = ''
            word_timestamps = []
            for result in response.results:
                transcription += result.alternatives[0].transcript
                lang = result.language_code
                for word in result.alternatives[0].words:
                    word_timestamps.append((word.word, word.start_time.total_seconds(), word.end_time.total_seconds()))

            user_name = audio_file_name.split('.')[0]
            user_transcripts[user_name] = {}
            user_transcripts[user_name]['text'] = transcription
            user_transcripts[user_name]['timestamps'] = word_timestamps
            try:
                user_transcripts[user_name] ['lang'] = lang
            except:
                user_transcripts[user_name] ['lang'] = "UNK"
            # print(transcription)
            # print(word_timestamps)

            # # Write transcribed text and word timestamps to a text file
            # with open(audio_file_name.replace(".mp3", ".txt"), "w") as f:
            #     f.write("Transcription:\n{}\n\nWord Timestamps:\n".format(transcription))
            #     for word_timestamp in word_timestamps:
            #         f.write("{}, {:.2f}, {:.2f}\n".format(word_timestamp[0], word_timestamp[1], word_timestamp[2]))
             
            # Delete the converted audio file from local storage
            # os.remove(audio_file_name)

    # merge transcripts
    final_transcript = support_scripts.stitch_transcripts(user_transcripts, start_dt)

    # post transcripts to general channel
    # chan_obj = get_channel_by_name('general')
    file_path = "final_transcript.txt"
    with open(file_path, 'w') as fout:
        fout.write(final_transcript)
    await ctx.send("Transcript: ", file=discord.File(file_path, "final_transcript.txt"))
    # await ctx.send(final_transcript)
    # await chan_obj.send("Transcript: ", file=discord.File(file_path, "final_transcript.txt"))
    # await chan_obj.send(final_transcript)

    # delete the transcript recordings after transcription has done
    for filename in os.listdir(audio_files_dir):
        os.remove(os.path.join(audio_files_dir, filename))

def get_channel_by_name(get_chan):
    # Send transcribed text to Discord channel
    for chan_i in bot.get_all_channels():
        if chan_i.name == get_chan:
            chan_id = chan_i.id
    return bot.get_channel(chan_id)
    
bot.run('')
