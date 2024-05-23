import asyncio
import time
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime
from discord.sinks import RecordingException
from bot.voice_client_culler import VoiceClientCuller 
from bot import connection_manager

load_dotenv()
bot = commands.Bot(command_prefix='/', intents=discord.Intents.default(), help_command=None)
voice_client_culler = VoiceClientCuller(bot)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is ready to scribble!')
    asyncio.create_task(voice_client_culler.start())

@bot.slash_command()
async def start_transcription(ctx):
    voice = ctx.author.voice
    if not voice:
        await ctx.respond("You aren't in a voice channel!")
        return

    bot_voice_client = ctx.guild.voice_client

    if bot_voice_client:
        if bot_voice_client.is_connected():
            await ctx.respond("I'm already in your voice channel!")
            return

    await ctx.respond("Joining channel to take notes")
    try:
        await connection_manager.connect_to_voice_channel(ctx.guild, voice.channel)
        voice_client_culler.last_voice_activity_times[ctx.guild.id] = datetime.now()
    except Exception as e:
        print(f"Failed to connect to voice channel: {e}")

@bot.slash_command()
async def stop_transcription(ctx):
    server_id = ctx.guild.id

    if server_id in connection_manager.voice_connections:  
        voice_connection = connection_manager.voice_connections[server_id]
        voice_connection.mark_for_deletion()
        voice_client = voice_connection.voice_client
        sink = voice_connection.sink

        try:
            voice_client.stop_recording() 
        except RecordingException as e:
            print(f"Tried to stop recording but couldn't: {e}")
            await sink.vc.disconnect()

        sink.speech_to_text_converter.audio_cost_calculator.session_end_time = time.time()
        await ctx.respond("Stopping transcription tasks")
        try:
            with open("current_transcription.txt", "r") as f:
                transcription_contents = f.read()
            await ctx.respond(transcription_contents)
        except FileNotFoundError:
            print("Transcription file not found.")
        except Exception as e:
            print(f"An error occurred while reading the transcription file: {e}")
        await sink.stop_transcription_tasks()

        del connection_manager.voice_connections[server_id]
        del voice_client_culler.last_voice_activity_times[server_id]
        
if __name__ == "__main__":
    bot.run(os.getenv("CLIENT_TOKEN"))