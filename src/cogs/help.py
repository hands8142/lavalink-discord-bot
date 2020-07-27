import discord
import os
from discord.ext import commands

prefix = os.getenv('PREFIX')

colour = discord.Colour.blue()

class 도움말(commands.Cog):
    """도움말을 보여줍니다"""

    def __init__(self, client):
        self.client = client

    @commands.command(name='도움')
    async def help(self, ctx, *cog):
        if not cog:
            embed = discord.Embed(description='도움말', color=colour)
            cog_desc = ''
            for x in self.client.cogs:
                cog_desc += f'**{prefix}도움 {x}** - {self.client.cogs[x].__doc__}\n'
            embed.add_field(name='카테고리', value=cog_desc[0:len(cog_desc)-1], inline=False)
            await ctx.message.add_reaction(emoji='✉')
            await ctx.send(embed=embed)
        else:
            if len(cog) > 1:
                embed = discord.Embed(title='에러', color=colour)
                await ctx.message.author.send('', embed=embed)
            else:
                found = False
                for x in self.client.cogs:
                    for y in cog:
                        if x == y:
                            embed = discord.Embed(color=colour)
                            scog_info = ''
                            for c in self.client.get_cog(y).get_commands():
                                if not c.hidden:
                                    scog_info += f'**{prefix}{c.name}** - {c.help}\n'
                            embed.add_field(name=f'{cog[0]}모델 - {self.client.cogs[cog[0]].__doc__}', value=scog_info)
                            found = True
                if not found:
                    for x in self.client.cogs:
                        for c in self.client.get_cog(x).get_commands():
                            if c.name == cog[0]:
                                embed = discord.Embed(color=colour)
                                embed.add_field(name=f'{c.name} - {c.help}', value=f'올바른 구문:\n{prefix}{c.qualified_name} {c.signature}')
                                found = True
                    if not found:
                        embed = discord.Embed(title='에러', description='없는 카테고리입니다.', color=colour)
                else:
                    await ctx.message.add_reaction(emoji='✉')
                await ctx.send(embed=embed)



def setup(client):
    client.add_cog(도움말(client))