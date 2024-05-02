import discord
from discord.ext import commands
import os
import json
import inspect
import io
import textwrap
import traceback
import aiohttp
from contextlib import redirect_stdout
import base64
import json
from youtubesearchpython import VideosSearch
import datetime
from menn import getres
from sd import imagine
bot = commands.Bot(command_prefix=commands.when_mentioned_or('_'),intents=discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready():
    print("print('connected')")

    
    bot.allowed = True
    bot.session = aiohttp.ClientSession(loop=bot.loop)
    bot.owner_id = (await bot.application_info()).owner.id

import inspect

class Con:
    def __init__(self, message, bot):
        self.ctx = self
        self.channel = message.channel
        self.author = message.author
        self.guild = message.guild
        self.message = message
        self.bot=bot
        self.source = inspect.getsource
        self.session = bot.session
    async def send(self, content,files=None,view=None,embed=None):
      await self.channel.send(content=content,files=files,view=view,embed=embed)
      
@bot.event
async def on_message(message):
    if message.author.bot:
      return
    if message.guild is not None or message.author.id == bot.owner_id:
        if "write a code" in message.content or "generate a code" in message.content or "code " in message.content:
          return await message.channel.send("Sorry I can't help you with coding.Consult stacksoverflow.")
        if bot.user in message.mentions:
          result=getres(message.content.replace('<@897389679844917268>',' '))
        
          con=Con(message,bot)
          await _eval(con,result)


async def _eval(ctx,body):
    """Evaluates python code"""
    blocked_words = ['.hshhs', 'os', 'subprocess', 'history()', '("token")', "('token')",
                     'l5XoE9c9GMpC6_iREUClht8nD6zHYSW3ZUIgVs', 'aW1wb3J0IG9zCnByaW50KG9zLmVudmlyb24uZ2V0KCd0b2tlbicpKQ==',"main",".py"]
    if ".events" in body:
      await ctx.send("Events may not work properly.")
      
    if ctx.author.id != bot.owner_id:
        for x in blocked_words:
            if x in body:
                return await ctx.send('Your code contains certain blocked words.')
    env = {
        'ctx': ctx.ctx,
        'channel': ctx.channel,
        'author': ctx.author,
        'guild': ctx.guild,
        'message': ctx.message,
        'source': inspect.getsource,
        'session':bot.session
    }

    env.update(globals())

    body = cleanup_code(body)
    stdout = io.StringIO()
    err = out = None

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    def paginate(text: str):
        '''Simple generator that paginates text.'''
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text)-1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != '', pages))

    try:
        exec(to_compile, env)
        
    except Exception as e:
        err = print(f'```py\n{e.__class__.__name__}: {e}\n```')
        return await ctx.message.add_reaction('\u2049')

    func = env['func']
    try:
        with redirect_stdout(stdout):
            
            ret = await func()
    except Exception as e:
        value = stdout.getvalue()
        err = print(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        if ret is None:
            if value:
                try:

                    out = print(f'\n{value}\n')
           
                except:
                    paginated_text = paginate(value)
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = print(f'```py\n{page}\n```')
                            break
                        print(f'```py\n{page}\n```')
        else:
            bot._last_result = ret
            try:
                out = print(f'```py\n{value}{ret}\n```')
            except:
                paginated_text = paginate(f"{value}{ret}")
                for page in paginated_text:
                    if page == paginated_text[-1]:
                        out = print(f'```py\n{page}\n```')
                        break
                    
                    print(f'```py\n{page}\n```')

    if out:
        await ctx.message.add_reaction('\u2705')  # tick
    elif err:
        await ctx.message.add_reaction('\u2049')  # x
    else:
        await ctx.message.add_reaction('\u2705')

def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    # remove `foo`
    return content.strip('` \n')


def get_syntax_error(e):
    if e.text is None:
        return f'```py\n{e.__class__.__name__}: {e}\n```'
    return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

@commands.check(lambda ctx: ctx.author.id in bot.allowed)
@bot.command()
async def require(ctx, *, requirement):
    '''Add requirements into req.txt'''
    #fill up content
    with open('requirements.txt') as f:
        content = f.read() + '\n' + requirement
    #get gittoken
    with open('config/config.json') as f:
        token = json.load(f).get('gittoken') or os.environ.get('gittoken')
    #get username
    async with bot.session.get('https://api.github.com/user', headers={"Authorization": f"token {token}"}) as resp: #get username 
        if 300 > resp.status >= 200:
            username = (await resp.json())['login']
    #get sha (dont even know why this is a compulsory field)
    async with bot.session.get(f'https://api.github.com/repos/{username}/eval-bot/contents/requirements.txt', headers={"Authorization": f"token {token}"}) as resp2:
        if 300 > resp2.status >= 200:
            #push to path
            async with bot.session.put(f'https://api.github.com/repos/fourjr/eval-bot/contents/requirements.txt', headers={"Authorization": f"token {token}"}, json={"path":"requirements.txt", "message":f"Add {requirement} to req.txt", "content":base64.b64encode(bytes(content, 'utf-8')).decode('ascii'), "sha":(await resp2.json())['sha'], "branch":"master"}) as resp3:
                if 300 > resp3.status >= 200:
                    await ctx.send('Done! Restarting...')
                    #data pushed successfully
                else:
                    await ctx.send('Well, I failed somehow, send the following to `4JR#2713` (180314310298304512): ```py\n' + str(await resp3.json()) + '\n```')
        else:
            await ctx.send('Well, I failed somehow, send the following to `4JR#2713` (180314310298304512): ```py\n' + str(await resp2.json()) + '\n```')

@bot.command()
async def restart(ctx):
    '''Add requirements into req.txt'''
    #fill up content
    with open('restart.txt') as f:
        content = f.read() + '\n' + ctx.author.name
    #get gittoken
    with open('config/config.json') as f:
        token = json.load(f).get('gittoken') or os.environ.get('gittoken')
    #get username
    async with bot.session.get('https://api.github.com/user', headers={"Authorization": f"token {token}"}) as resp: #get username 
        if 300 > resp.status >= 200:
            username = (await resp.json())['login']
    #get sha (dont even know why this is a compulsory field)
    async with bot.session.get(f'https://api.github.com/repos/{username}/eval-bot/contents/restart.txt', headers={"Authorization": f"token {token}"}) as resp2:
        if 300 > resp2.status >= 200:
            #push to path
            async with bot.session.put(f'https://api.github.com/repos/fourjr/eval-bot/contents/restart.txt', headers={"Authorization": f"token {token}"}, json={"path":"requirements.txt", "message":f"Add {requirement} to req.txt", "content":base64.b64encode(bytes(content, 'utf-8')).decode('ascii'), "sha":(await resp2.json())['sha'], "branch":"master"}) as resp3:
                if 300 > resp3.status >= 200:
                    await ctx.send('Now, just give me a second!')
                    #data pushed successfully
                else:
                    await ctx.send('Well, I failed somehow, send the following to `4JR#2713` (180314310298304512): ```py\n' + str(await resp3.json()) + '\n```')
        else:
            await ctx.send('Well, I failed somehow, send the following to `4JR#2713` (180314310298304512): ```py\n' + str(await resp2.json()) + '\n```')


token=os.getenv('tkn')
bot.run(token)
