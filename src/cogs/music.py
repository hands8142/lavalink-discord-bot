from discord.ext import commands
import lavalink
import os
import asyncio
from discord import utils
from discord import Embed
from playlist import playlist

class 음악(commands.Cog):
  """음악 기능을 보여 줍니다."""
  def __init__(self, bot):
    self.bot = bot
    self.bot.music = lavalink.Client(self.bot.user.id)
    self.bot.music.add_node('localhost', int(os.getenv('PORT')), str(os.getenv('PASSWORD')), 'na', 'music-node')
    self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
    self.bot.music.add_event_hook(self.track_hook)
  
  @commands.command(name='join')
  async def join(self, ctx):
    """음악 채널에 들어옵니다."""
    print("join")
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    if member == None or member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    if member is not None and member.voice is not None:
      vc = member.voice.channel
      player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
      if not player.is_connected:
        player.store('channel', ctx.channel.id)
        await self.connect_to(ctx.guild.id, str(vc.id))

  @commands.command(name='play')
  async def play(self, ctx, *, query):
    """음악을 플레이합니다 10초 안에 번호를 말해 주세요."""
    try:
      player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
      if not player.is_connected:
        await ctx.invoke(self.join)
      player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
      query = f'ytsearch:{query}'
      results = await player.node.get_tracks(query)
      if results['loadType'] == "LOAD_FAILED":
        return await ctx.send("해당 이름의 음악을 찾을 수 없습니다.")
      tracks = results['tracks'][0:10]
      i = 0
      query_result = ''
      for track in tracks:
        i = i + 1
        query_result = query_result + f'{i}) {track["info"]["title"]} - {track["info"]["uri"]}\n'
      embed = Embed()
      embed.description = query_result
      embed.set_footer(text="10초 안에 말해 주세요")

      meg = await ctx.channel.send(embed=embed)

      def check(m):
        return m.author.id == ctx.author.id

      response = await self.bot.wait_for('message', timeout=10, check=check)
      track = tracks[int(response.content)-1]

      player.add(requester=ctx.author.id, track=track)
      title = track["info"]["title"]
      uri = track["info"]["uri"]
      if not player.is_playing:
        await meg.delete()
        embed = Embed(title="플레이")
        embed.description = f'[{title}](<{uri}>)'
        await ctx.send(embed=embed)
        await player.play()
      else:
        await meg.delete()
        embed = Embed(title="리스트 추가")
        embed.description = f'[{title}](<{uri}>)'
        await ctx.send(embed=embed)

    except asyncio.TimeoutError:
      await meg.delete()
      await ctx.send("시간이 지났습니다.")
    except Exception as error:
      print(error)

  @commands.command(name='skip')
  async def skip(self, ctx):
    """음악을 스킵 합니다."""
    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    if not player.is_connected:
      return await ctx.send("봇이 음성 채널에 들어가 있지않습니다.")
    if not player.is_playing:
      return await ctx.send("음악이 재생중이지 않습니다.")
    if member == None or member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    for i in member.voice.channel.members:
      if str(self.bot.user.id) in str(i.id):
        await player.skip()
        return await ctx.send("음악을 스킵 하였습니다.")
    await ctx.send("봇과 같은 채널에 있지 않습니다.")

  
  @commands.command(name="stop")
  async def stop(self, ctx):
    """음악을 끕니다."""
    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    i = [str(i) for i in member.voice.channel.members]
    if not player.is_connected:
      return await ctx.send("봇이 음성 채널에 들어가 있지않습니다.")
    if not player.is_playing:
      return await ctx.send("음악이 재생중이지 않습니다.")
    if member == None or member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    for i in member.voice.channel.members:
      if str(self.bot.user.id) in str(i.id):
        await player.stop()
        return await ctx.send("음악을 끕니다.")
    await ctx.send("봇과 같은 채널에 있지 않습니다.")
      
  
  @commands.command(name="pause")
  async def pause(self, ctx):
    """음악을 일시 정지 합니다."""
    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    i = [str(i) for i in member.voice.channel.members]
    if not player.is_connected:
      return await ctx.send("봇이 음성 채널에 들어가 있지않습니다.")
    if not player.is_playing:
      return await ctx.send("음악이 재생중이지 않습니다.")
    if member == None or member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    for i in member.voice.channel.members:
      if str(self.bot.user.id) in str(i.id):
        await player.set_pause(pause=True)
        return await ctx.send("음악을 일시 정지하였습니다.")
    await ctx.send("봇과 같은 채널에 있지 않습니다.")

  @commands.command(name="resume")
  async def resume(self, ctx):
    """음악을 다시 재생합니다."""
    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    i = [str(i) for i in member.voice.channel.members]
    if not player.is_connected:
      return await ctx.send("봇이 음성 채널에 들어가 있지않습니다.")
    if not player.is_playing:
      return await ctx.send("음악이 재생중이지 않습니다.")
    if member == None or member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    for i in member.voice.channel.members:
      if str(self.bot.user.id) in str(i.id):
        await player.set_pause(pause=False)
        return await ctx.send("음악을 다시 재생합니다.")
    await ctx.send("봇과 같은 채널에 있지 않습니다.")
  
  @commands.command(name="volume")
  async def volume(self, ctx, vol: int):
    """음악의 볼륨을 조절합니다."""
    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    i = [str(i) for i in member.voice.channel.members]
    if not player.is_connected:
      return await ctx.send("봇이 음성 채널에 들어가 있지않습니다.")
    if not player.is_playing:
      return await ctx.send("음악이 재생중이지 않습니다.")
    if member == None or member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    if vol > 100 and vol < 0:
      return await ctx.send("0~100까지만 설정이 가능합니다.")
    for i in member.voice.channel.members:
      if str(self.bot.user.id) in str(i.id):
        await player.set_volume(vol=vol)
        return await ctx.send(f"소리를 {vol}로 설정하였습니다.")
    await ctx.send("봇과 같은 채널에 있지 않습니다.")

  @commands.command(name="queue")
  async def queue(self, ctx):
    """재생목록을 보여줍니다"""
    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    i = [str(i) for i in member.voice.channel.members]
    if not player.is_connected:
      return await ctx.send("봇이 음성 채널에 들어가 있지않습니다.")
    if not player.is_playing:
      return await ctx.send("음악이 재생중이지 않습니다.")
    a = 0
    plist = ''
    for i in player.queue:
      a = a + 1
      plist = plist + f"{a} {i['title']}\n"
    embed = Embed(title="재생 목록")
    embed.description = plist
    await ctx.send(embed=embed)

  @commands.command(name="current")
  async def current(self, ctx):
    """현재 재생중인 음악을 보여 줍니다"""
    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    i = [str(i) for i in member.voice.channel.members]
    if not player.is_connected:
      return await ctx.send("봇이 음성 채널에 들어가 있지않습니다.")
    if not player.is_playing:
      return await ctx.send("음악이 재생중이지 않습니다.")
    await ctx.send(f"현재 재생중인 음악: {player.current['title']}")
  
  @commands.command(name="find")
  async def find(self, ctx, *, query):
    """음악을 찾습니다.(음악을 재생하지는 않습니다.)"""
    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    if not player.is_connected:
        await ctx.invoke(self.join)
    query = f'ytsearch:{query}'
    results = await player.node.get_tracks(query)
    if results['loadType'] == "LOAD_FAILED":
      return await ctx.send("해당 이름의 음악을 찾을 수 없습니다.")
    tracks = results['tracks'][0:10]
    i = 0
    query_result = ''
    for track in tracks:
      i = i + 1
      query_result = query_result + f'{i}) {track["info"]["title"]} - {track["info"]["uri"]}\n'
    embed = Embed()
    embed.description = query_result
    await ctx.channel.send(embed=embed)

  @commands.command(name="loop")
  async def loop(self, ctx):
    """으악의 재생목록을 반복합니다."""
    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    i = [str(i) for i in member.voice.channel.members]
    if not player.is_connected:
      return await ctx.send("봇이 음성 채널에 들어가 있지않습니다.")
    if not player.is_playing:
      return await ctx.send("음악이 재생중이지 않습니다.")
    if member == None or member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    for i in member.voice.channel.members:
      if str(self.bot.user.id) in str(i.id):
        player.repeat = not player.repeat
        return await ctx.send('루프 ' + ('활성화' if player.repeat else '비활성화'))
    await ctx.send("봇과 같은 채널에 있지 않습니다.")

  
  @commands.command(name="shuffle")
  async def shuffle(self, ctx):
    """재생목록을 뒤섞습니다."""
    player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
    member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
    i = [str(i) for i in member.voice.channel.members]
    if not player.is_connected:
      return await ctx.send("봇이 음성 채널에 들어가 있지않습니다.")
    if not player.is_playing:
      return await ctx.send("음악이 재생중이지 않습니다.")
    if member == None or member.voice == None:
      return await ctx.send("음성 채널에 들어가 있지않습니다.")
    for i in member.voice.channel.members:
      if str(self.bot.user.id) in str(i.id):
        player.shuffle = not player.shuffle
        return await ctx.send('셔플 ' + ('활성화' if player.shuffle else '비활성화'))
    await ctx.send("봇과 같은 채널에 있지 않습니다.")

  @commands.command(name="listplay")
  async def listplay(self, ctx):
    """리스트에 있는 음악을 재생합니다"""
    try:
      player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
      if not player.is_connected:
        await ctx.invoke(self.join)
      player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
      for query in playlist:
        query = f'ytsearch:{query}'
        results = await player.node.get_tracks(query)
        if results['loadType'] == "LOAD_FAILED":
          return await ctx.send("해당 이름의 음악을 찾을 수 없습니다.")
        tracks = results['tracks'][0:10]
        i = 0
        query_result = ''
        for track in tracks:
          i = i + 1
          query_result = query_result + f'{i}) {track["info"]["title"]} - {track["info"]["uri"]}\n'
        embed = Embed()
        embed.description = query_result
        embed.set_footer(text="10초 안에 말해 주세요")

        meg = await ctx.channel.send(embed=embed)

        def check(m):
          return m.author.id == ctx.author.id

        response = await self.bot.wait_for('message', timeout=10, check=check)
        track = tracks[int(response.content)-1]

        player.add(requester=ctx.author.id, track=track)
        title = track["info"]["title"]
        uri = track["info"]["uri"]
        if not player.is_playing:
          await meg.delete()
          embed = Embed(title="플레이")
          embed.description = f'[{title}](<{uri}>)'
          await ctx.send(embed=embed)
          await player.play()
        else:
          await meg.delete()
          embed = Embed(title="리스트 추가")
          embed.description = f'[{title}](<{uri}>)'
          await ctx.send(embed=embed)

    except asyncio.TimeoutError:
      await meg.delete()
      await ctx.send("시간이 지났습니다.")

    except Exception as error:
      print(error)


  
  async def track_hook(self, event):
    if isinstance(event, lavalink.events.QueueEndEvent):
      guild_id = int(event.player.guild_id)
      await self.connect_to(guild_id, None)
      
  async def connect_to(self, guild_id: int, channel_id: str):
    ws = self.bot._connection._get_websocket(guild_id)
    await ws.voice_state(str(guild_id), channel_id)
    

def setup(bot):
    bot.add_cog(음악(bot))