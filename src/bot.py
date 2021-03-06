import discord
import os
from discord.ext import commands

bot = commands.Bot(command_prefix=os.getenv('PREFIX'))

if __name__ == '__main__':
  @bot.event
  async def on_ready():
      print(f'{bot.user} has logged in.')
      bot.load_extension('cogs.music')
      bot.load_extension('cogs.help')

  bot.run(os.getenv('BOT_TOKEN'))