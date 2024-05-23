import discord
import os
from dotenv import load_dotenv

load_dotenv()

class EchoClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = EchoClient(intents=intents)
client.run(os.getenv("CLIENT_TOKEN"))
