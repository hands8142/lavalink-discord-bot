from discord.ext import commands
import lavalink
import os
from discord import utils
from discord import Embed

class MusicCog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bot.music = lavalink.Client(self.bot.user.id)
    self.bot.music.add_node('localhost', int(os.getenv('PORT')), str(os.getenv('PASSWORD')), 'na', 'music-node')
    self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
    self.bot.music.add_event_hook(self.track_hook)
  
  @commands.command(name='join')
  async def join(self, ctx):
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    if member == None and member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    if member is not None and member.voice is not None:
      vc = member.voice.channel
      player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
      if not player.is_connected:
        player.store('channel', ctx.channel.id)
        await self.connect_to(ctx.guild.id, str(vc.id))

  @commands.command(name='play')
  async def play(self, ctx, *, query):
    try:
      if ctx.voice_client is None or not ctx.voice_client.is_connected():
        await ctx.invoke(self.join)
      player = self.bot.music.player_manager.get(ctx.guild.id)
      query = f'ytsearch:{query}'
      results = await player.node.get_tracks(query)
      if results['loadType'] == "LOAD_FAILED":
        return await ctx.send("해당 이름의 동영상을 찾을 수 없습니다.")
      tracks = results['tracks'][0:10]
      i = 0
      query_result = ''
      for track in tracks:
        i = i + 1
        query_result = query_result + f'{i}) {track["info"]["title"]} - {track["info"]["uri"]}\n'
      embed = Embed()
      embed.description = query_result

      meg = await ctx.channel.send(embed=embed)

      def check(m):
        return m.author.id == ctx.author.id
      
      response = await self.bot.wait_for('message', check=check)
      track = tracks[int(response.content)-1]

      player.add(requester=ctx.author.id, track=track)
      if not player.is_playing:
        await meg.delete()
        await ctx.send(f'플레이 {track["info"]["title"]} - {track["info"]["uri"]}')
        await player.play()
      else:
        await meg.delete()
        await ctx.send(f'플레이 리스트 추가 {track["info"]["title"]} - {track["info"]["uri"]}')

    except Exception as error:
      print(error)

  @commands.command(name='skip')
  async def skip(self, ctx):
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    player = self.bot.music.player_manager.get(ctx.guild.id)
    if member == None and member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    if player == None:
      return await ctx.send("음악이 재생중이지 않습니다.")
    await player.skip()
    await ctx.send("음악을 스킵 합니다.")
  
  @commands.command(name="stop")
  async def stop(self, ctx):
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    player = self.bot.music.player_manager.get(ctx.guild.id)
    if member == None and member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    if player == None:
      return await ctx.send("음악이 재생중이지 않습니다.")
    await player.stop()
    await ctx.send("음악을 끕니다.")
  
  @commands.command(name="pause")
  async def pause(self, ctx):
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    player = self.bot.music.player_manager.get(ctx.guild.id)
    if member == None and member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    if player == None:
      return await ctx.send("음악이 재생중이지 않습니다.")
    await player.set_pause(pause=True)
    await ctx.send("음악을 일시 정지하였습니다.")

  @commands.command(name="resume")
  async def resume(self, ctx):
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    player = self.bot.music.player_manager.get(ctx.guild.id)
    if member == None and member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    if player == None:
      return await ctx.send("음악이 재생중이지 않습니다.")
    await player.set_pause(pause=False)
    await ctx.send("음악을 다시 재생합니다.")
  
  @commands.command(name="volume")
  async def volume(self, ctx, vol: int):
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    player = self.bot.music.player_manager.get(ctx.guild.id)
    if member == None and member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    if player == None:
      return await ctx.send("음악이 재생중이지 않습니다.")
    if vol > 100 and vol < 0:
      return await ctx.send("0~100까지만 설정이 가능합니다.")
    await player.set_volume(vol=vol)
    await ctx.send(f"소리를 {vol}로 설정하였습니다.")

  @commands.command(name="queue")
  async def queue(self, ctx):
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    player = self.bot.music.player_manager.get(ctx.guild.id)
    if member == None and member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    if player == None:
      return await ctx.send("음악이 재생중이지 않습니다.")
    embed = Embed(title="재생 목록")
    a = 1
    for i in player.queue:
      playlist = f"{a} {str(i['title'])}" 
      a = a + 1
    embed.description = playlist
    await ctx.send(embed=embed)

  @commands.command(name="current")
  async def current(self, ctx):
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    player = self.bot.music.player_manager.get(ctx.guild.id)
    if member == None and member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    if player == None:
      return await ctx.send("음악이 재생중이지 않습니다.")
    await ctx.send(f"현재 재생중인 음악: {player.current['title']}")


  
  async def track_hook(self, event):
    if isinstance(event, lavalink.events.QueueEndEvent):
      guild_id = int(event.player.guild_id)
      await self.connect_to(guild_id, None)
      
  async def connect_to(self, guild_id: int, channel_id: str):
    ws = self.bot._connection._get_websocket(guild_id)
    await ws.voice_state(str(guild_id), channel_id)
    

def setup(bot):
    bot.add_cog(MusicCog(bot))