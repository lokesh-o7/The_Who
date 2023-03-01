import discord
from discord.ext import commands
import time

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

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
    async def once_done(sink: discord.sinks, channel: discord.TextChannel, *args):  # Our voice client already passes these in.
        recorded_users = [  # A list of recorded users
            f"<@{user_id}>"
            for user_id, audio in sink.audio_data.items()
        ]
        await sink.vc.disconnect()  # Disconnect from the voice channel.
        files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
        await channel.send(f"finished recording audio for: {', '.join(recorded_users)}.", files=files)  # Send a message with the accumulated files.

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

bot.run('MTA3NjY2MTQ3NjA5MTI0MDQ2OQ.GS7FJV.dtc_YY5SE_paTObKYUlljEUt86JCwOFCTV2K9c')