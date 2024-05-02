import discord
from discord.ext import commands,tasks
from typing import Optional
import time
import os
from replit import db
import requests
from io import BytesIO
from PIL import Image, ImageDraw
import aiohttp 
from discord.ui import Button,Select,View
from discord import app_commands
import base64
import ast
from datetime import datetime, timedelta
import traceback
from discord.ui import Button,Select,View

import io

import re

funcdict={
    "albedobaseXL_v13": "basic",
    "Deliberate_v2": "basic",
    "dreamlabsoil_V2_v2": "basic",
    "DreamShaper_6.31_BakedVae": "basic",
    "dreamshaper_8": "basic",
    "dreamshaper_8LCM": "basic",
    "juggernautXL_v8Rundiffusion": "basic",
    "LCM_Dreamshaper_v7_4k": "basic",
    "proteus_v02": "basic",
    "proteus_v03": "anime",
    "RealVisXL_V2.0": "basic",
    "RealVisXL_V3.0": "real",
    "Realistic_Vision_V5.1": "basic",
    "Realistic_Vision_V6.0_NV_B1_fp16": "basic",
    "SSD-1B": "basic",
    "sd_xl": "default",
    "starlightXLAnimated_v3": "basic",
    "turbovisionxlSuperFastXLBasedOnNew_tvxlV32Bakedvae": "basic",
    "v1-5-pruned-emaonly": "basic",
    "v2-1_768-ema-pruned": "basic"
}

import requests
import time
import os

def runrep(url,payload):
  res=requests.post(url,json=payload)
  resp=res.json()
  url=resp['urls']['get'].replace("https://api.replicate.com/v1/predictions/","https://replicate.com/api/predictions/")
  print(url)
  time.sleep(1)
  chun=requests.get(url)
  while chun.json()['status'] != 'succeeded':
    chun=requests.get(url)

    print(chun.json()['status'])
  output=chun.json()['output']
  return output



def anime(prompt,negative,num,seed,gs):
  #num def 20 gs 7.5
  url="https://replicate.com/api/models/lucataco/proteus-v0.3/versions/b28b79d725c8548b173b6a19ff9bffd16b9b80df5b18b8dc5cb9e1ee471bfa48/predictions"
  payload={"input":{"width":1024,"height":1024,"prompt":prompt,"scheduler":"DPM++2MSDE","num_outputs":4,"guidance_scale":gs,"apply_watermark":False,"negative_prompt":negative,"prompt_strength":0.8,"num_inference_steps":num},"stream":False}
  res=runrep(url,payload)
  return res


def basic(prompt,negative,model,sampler,num,seed,gs):
  #def gs 7.5
  url="https://replicate.com/api/models/fofr/txt2img/versions/18f1d88376233fef85e7289d65326b9ceabd3a78215a6833bfb7775792f42b79/predictions"
  payload={"input":{"seed":seed,"model":model,"seed":seed,"width":768,"height":768,"prompt":prompt,"scheduler":"normal","num_outputs":4,"sampler_name":sampler,"guidance_scale":gs,"negative_prompt":negative,"num_inference_steps":num},"stream":False}
  res=runrep(url,payload)
  return res

def real(prompt,negative,num,seed,gs):
  #def gs 2
  url="https://replicate.com/api/models/adirik/realvisxl-v3.0-turbo/versions/3dc73c805b11b4b01a60555e532fd3ab3f0e60d26f6584d9b8ba7e1b95858243/predictions"
  payload={"input":{"seed":seed,"width":768,"height":768,"prompt":prompt,"refine":"no_refiner","scheduler":"DPM++_SDE_Karras","num_outputs":4,"guidance_scale":gs,"apply_watermark":False,"high_noise_frac":0.8,"negative_prompt":negative,"prompt_strength":0.8,"num_inference_steps":num},"stream":False}
  res=runrep(url,payload)
  return res

def default(prompt,negative,num,seed,gs):
  #def gs 2
  url="https://replicate.com/api/models/adirik/realvisxl-v3.0-turbo/versions/3dc73c805b11b4b01a60555e532fd3ab3f0e60d26f6584d9b8ba7e1b95858243/predictions"
  payload={"input":{"seed":seed,"width":768,"height":768,"prompt":prompt,"refine":"expert_ensemble_refiner","scheduler":"K_EULER","lora_scale":0.6,"num_outputs":4,"guidance_scale":gs,"apply_watermark":False,"high_noise_frac":0.8,"negative_prompt":negative,"prompt_strength":0.8,"num_inference_steps":num},"stream":False}
  res=runrep(url,payload)
  return res

async def imagine(ctx,prompt: str):
  
  promptt=prompt
  msg = await ctx.send(f"Generating - **{promptt}** - {ctx.author.name} (waiting to start)")
  num=50
  arg_regex = re.compile(r"--(\w+)\s+(\S+)")
  print(101)# regular expression to match optional arguments
  arg_dict = {}
  matches = arg_regex.findall(prompt)
  for match in matches:
    key, value = match
    arg_dict[key] = value
  prompt = arg_regex.sub("", prompt).strip()
  negative = arg_dict.get("neg", "nsfw")
    # Extract the values of the optional arguments
  num = arg_dict.get("nis", "25")
  seed = arg_dict.get("seed", "-1")
  gs = arg_dict.get("gs", "7")
  waifu = arg_dict.get("w", "off")
  mod = arg_dict.get("mod", "sd_xl")
  print(mod)
  sampl= arg_dict.get('samp',None)
  if mod =='RealVisXL_V3.0':
    gs=2
  
  mod=funcdict[mod]
  if mod=='basic':

    print('basic')
    output=basic(prompt,negative,mod,sampl,num,seed,gs)
    
  elif mod =='anime':
    print('anime')
    output=anime(prompt,negative,num,seed,gs)
    
  elif mod =='real':
    print('real')
    output=real(prompt,negative,num,seed,gs)
     
  elif mod =='default':
    print('default')
    output=default(prompt,negative,num,seed,gs)
    

  



  
  
  
  files=[]
  print(output)
  async with aiohttp.ClientSession() as session:
    for i in output:
      print(i)
      async with session.get(i) as resp:
        img = await resp.read()
        with io.BytesIO(img) as file:
          files.append(discord.File(file, "whatever.png"))
  button1 = Button(label="U1", style=discord.ButtonStyle.grey)
  button2 = Button(label="U2", style=discord.ButtonStyle.grey)
  button3 = Button(label="U3", style=discord.ButtonStyle.grey)
  button4 = Button(label="U4", style=discord.ButtonStyle.grey)
  button6 = Button(label="V1", style=discord.ButtonStyle.grey)
  button7 = Button(label="V2", style=discord.ButtonStyle.grey)
  button8 = Button(label="V3", style=discord.ButtonStyle.grey)
  button9 = Button(label="V4", style=discord.ButtonStyle.grey)

  async def yet(interaction):
    gid=ctx.guild.id
    ch=interaction.channel.id
    if interaction.user.id!=ctx.author.id:
      return
    else:
      await ctx.send("This feature isn't ready yet, will be available soon.",ephemeral=True)
  button1.callback = yet
  button2.callback = yet
  button3.callback = yet
  button4.callback = yet
  button6.callback = yet
  button7.callback = yet
  button8.callback = yet
  button9.callback = yet
  view = View(timeout=600) 
  view.add_item(button1)
  view.add_item(button2)
  view.add_item(button3)
  view.add_item(button4)
  view.add_item(button6)
  view.add_item(button7)
  view.add_item(button8)
  view.add_item(button9)
  await ctx.send(content=f"**{prompt}** - **By {ctx.author.name}** (fast) ")
  time.sleep(2)
  await ctx.send(content=f"**{prompt}** - **By {ctx.author.mention}** ",files=files,view=view)


#https://discord.com/api/oauth2/authorize?client_id=1101185668249571368&permissions=8&scope=bot






