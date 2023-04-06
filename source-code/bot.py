import discord

ACTIVITY: str = 'Hello, World!'


class Bot:
    client: discord.Client
    tree: discord.app_commands.CommandTree


    def __init__(self):
        self.client = discord.Client(intents=discord.Intents.all(), activity=discord.Game(ACTIVITY))
        self.tree = discord.app_commands.CommandTree(self.client)
