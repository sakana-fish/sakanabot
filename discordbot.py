import discord
import datetime
import os
import random
import asyncio
from discord.ext import commands
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials 
import re
import requests

#https://ja.wikipedia.org/wiki/Unicode%E3%81%AEEmoji%E3%81%AE%E4%B8%80%E8%A6%A7

sheet = os.environ['SHEETKEY']
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']    
credential = {
                "type": "service_account",
                "project_id": os.environ['SHEET_PROJECT_ID'],
                "private_key_id": os.environ['SHEET_PRIVATE_KEY_ID'],
                "private_key": os.environ['SHEET_PRIVATE_KEY'],
                "client_email": os.environ['SHEET_CLIENT_EMAIL'],
                "client_id": os.environ['SHEET_CLIENT_ID'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url":  os.environ['SHEET_CLIENT_X509_CERT_URL']
             }

credentials = ServiceAccountCredentials.from_json_keyfile_dict(credential, scope)
gc = gspread.authorize(credentials)
wb = gc.open_by_key(sheet)
ws = wb.worksheet("挙手管理") 
ws2 = wb.worksheet("メモ")
ws3 = wb.worksheet("フレコ")
ws4 = wb.worksheet("vote") 
ws5 = wb.worksheet("vote2") 


botid=758555841296203827 #sakanabotのid

client = commands.Bot(command_prefix='.')
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')  
    guilds = await client.fetch_guilds(limit=150).flatten()
    text=f'{len(guilds)}匹でおさかな天国'
    await client.change_presence(activity=discord.Game(name=text))

    
@client.command()
async def suse(ctx): #.sの説明
    text='交流戦挙手方法\n挙手: 指定時間に対応するスタンプ(↓↓↓)を押す\n補欠挙手に変更: 変更する時間のスタンプを再び押す\n挙手取り下げ: 取り下げる時間のスタンプを再び押す(挙手→補欠→取り下げのループ)\n↩: 募集文をチャンネルの一番下に持ってくる\n🔁: 募集時間帯の切り替え(21~24 or 20~26)\n\n20→🇴 21→🇦 22→🇧 23→🇨 24→🇩 25→🇪 26→🇫'
    await ctx.send(text)
    
    
@client.command()
async def fish(ctx, about = "🐟🐟🐟 使い方 🐟🐟🐟"):
  text=".s: 交流戦募集開始※再び.sすることでリセット 英語スタンプ→の/補欠/へ\n.suse: .sの使い方\n.l <時間>: 指定時間に挙手した人の名前\n.m <時間>: 指定時間に挙手した人にメンション\n.cal: 即時集計。順位は16進数でも入力可(入力例:123456,1357911,789abc)、<call>or<777>で呼び戻し、<end>で終了、<back>or<333>で一回分だけ修正可能\n.set <数字>: メモ登録\n.memo <数字> or <登録名>: メモ呼び出し\n.ran <数字>: ランダムに数字出力\n.div <数字> <リスト...>: 組み分け\n.choose <リスト...>: 選択\n.v/.v2: 匿名or非匿名アンケート(2択)、募集者の👋で終了\n.mt: ラウンジの集計\n作成者: さかな(@sakana8dx)\nさかなBot導入: https://discord.com/api/oauth2/authorize?client_id=758555841296203827&permissions=223296&scope=bot"
  help1 = discord.Embed(title=about,color=0xe74c3c,description=text)
  await ctx.send(embed=help1)       

#-----------------------------------------------------

@client.command()
async def setfc(ctx): 
    def check(m):
        return m.author.id == ctx.author.id

    if  ctx.author.bot == False:
        try:
            a=str(ctx.author.id)
            list=ws3.col_values(1)
            row=list.index(a)+1
        except ValueError:
            ws3.append_row([a])
            list=ws3.col_values(1)
            row=list.index(a)+1
        
        await ctx.send('フレンドコードを入力してください')
        msg = await client.wait_for('message',check=check)
        ws3.update_cell(row,2,msg.content)
        await ctx.send('登録が完了しました')    

#-----------------------------------------------------

@client.command()
async def fc(ctx,*n):
    a=str(ctx.author.id)
    if len(n)==1:
        if '@' in n[0]:
            a=re.sub("\\D", "", n[0])
    list=ws3.col_values(1)
    row=list.index(a)+1
    msg = await ctx.send(ws3.cell(row,2).value) 
    await asyncio.sleep(10)
    await msg.delete()
  
#-----------------------------------------------------

@client.command()
async def set(ctx,n): 
    def check(m):
        return m.author.id == ctx.author.id
    def check2(m):
        try:
            m=int(m)
        except ValueError:
            return False
        else:
            if m>0 and m<11:
                return True
            else:
                return False

    if check2(n)==True:
        n=int(n)        
        a=str(ctx.guild.id)
        try:
            list=ws2.col_values(1)
            row=list.index(a)+1
        except:
            ws2.append_row([str(ctx.guild.id)])
            list=ws2.col_values(1)
            row=list.index(a)+1
            ws2.update_cell(row,22,0)
        
        await ctx.send('名前を入力してください')
        msg = await client.wait_for('message',check=check)
        await ctx.send('内容を入力してください')
        msg2 = await client.wait_for('message',check=check)
        ws2.update_cell(row,2*n,msg.content)
        ws2.update_cell(row,2*n+1,msg2.content)
        await ctx.send('登録が完了しました')
     
    else:
        await ctx.send('1~10の数字を入力してください (.set <数字>)')
      
#-----------------------------------------------------

@client.command()
async def memo(ctx,n): 
    def check2(m):
        try:
            m=int(m)
        except ValueError:
            return False
        else:
            if m>0 and m<11:
                return True
            else:
                return False
    a=str(ctx.guild.id)
    list=ws2.col_values(1)
    row=list.index(a)+1
    b=ws2.row_values(row)
    if n=='all':
        text=''
        for i in range(10):
            text=f'{text}memo{i+1} {b[2*i+1]}: {b[2*i+2]}\n'
        await ctx.send(text)
    elif check2(n)==True:
        if b[2*int(n)]!='':
            await ctx.send(b[2*int(n)])
        else:
            await ctx.send(f'メモ{n}は未登録です')    
    elif n in b:
        n=b.index(n)+1
        await ctx.send(b[n])
    else:
        await ctx.send('未登録の内容です')
        
#-----------------------------------------------------  
 

@client.command()
async def ran(ctx,arg):
  a=int(arg)
  await ctx.send(1+random.randrange(a))

    
@client.command()
async def choose(ctx,*args):
  b=len(args)
  await ctx.send(args[random.randrange(b)])

    
@client.command()
async def div(ctx,*args):
  a=int(args[0])
  b=len(args)-1
  c=b%a
  list = []
  #print(a,b,c,list,"\n")

  for i in range(b):
    list.append(args[i+1])
  result2 = ''
  for i in range(a):
    result = ''
    for j in range(b//a):
      d = list[random.randrange(len(list))]
      result += str(d)+" "
      #print(result,list,"\n")
      list.remove(d)       
      if c!= 0 :
        d = list[random.randrange(len(list))]
        result += str(d)+" "
        list.remove(d)   
        c -= 1
    result2 +=str(i+1) + " | " + result + "\n"
  await ctx.send(result2)
 
@client.command()
async def v(ctx):

    def check(reaction, user):
        emoji = str(reaction.emoji)
        if user.bot == True:    # botは無視
            pass
        else:          
            return emoji

    def check3(m):
      return m.author.id == ctx.author.id     

    text = discord.Embed(title="内容を入力してください")
    msg = await ctx.send(embed=text)
    about = await client.wait_for('message',check=check3)
    msg2 = about.content
    await about.delete()
    text = discord.Embed(title=f'{msg2}')
    text.add_field(name='投票進行中',value=f'🙆:0 🙅:0',inline=False)
    await msg.edit(embed=text)
    await msg.edit(embed=text)
    await msg.add_reaction('🙆')
    await msg.add_reaction('🙅')
    await msg.add_reaction('👋')

    a=str(ctx.channel.id)
    try:
      list=ws4.col_values(1)
      row=list.index(a)+1
    except:
      ws4.append_row([str(ctx.channel.id)])
      list=ws4.col_values(1)
      row=list.index(a)+1

    b=ws4.range(row,2,row,8)
    b[0].value=str(msg.id)
    b[1].value=str(ctx.author.id)
    b[2].value=str(msg2)
    b[3].value=''
    b[4].value=''
    b[5].value=0
    b[6].value=0
    
    ws4.update_cells(b)


@client.command()
async def v2(ctx):

    def check(reaction, user):
        emoji = str(reaction.emoji)
        if user.bot == True:    # botは無視
            pass
        else:          
            return emoji

    def check3(m):
      return m.author.id == ctx.author.id     

    text = discord.Embed(title="内容を入力してください")
    msg = await ctx.send(embed=text)
    about = await client.wait_for('message',check=check3)
    msg2 = about.content
    await about.delete()
    text = discord.Embed(title=f'{msg2}')
    text.add_field(name='投票進行中',value=f'🙆:0 🤷:0 🙅:0',inline=False)
    await msg.edit(embed=text)
    await msg.edit(embed=text)
    await msg.add_reaction('🙆')
    await msg.add_reaction('🤷')
    await msg.add_reaction('🙅')
    await msg.add_reaction('👋')
    await msg.add_reaction('📢')
    await msg.add_reaction('↩')


    a=str(ctx.channel.id)
    try:
      list=ws5.col_values(1)
      row=list.index(a)+1
    except:
      ws5.append_row([str(ctx.channel.id)])
      list=ws5.col_values(1)
      row=list.index(a)+1

    b=ws5.range(row,2,row,14)
    b[0].value=str(msg.id)
    b[1].value=str(ctx.author.id)
    b[2].value=str(msg2)
    b[3].value='> '
    b[4].value='> '
    b[5].value='> '
    b[6].value=0
    b[7].value=0
    b[8].value=0
    b[9].value='> '
    b[10].value='> '
    b[11].value='> '
    b[12].value='> '
    
    ws5.update_cells(b)
    
@client.command()
async def cal(ctx,*enemy):
    def check(m): 
        return m.author.id == ctx.author.id
        
    def is_int(s):
        try:
            int(s,16)
            return True
        except ValueError:
            return False

    def is_under12(b):
        return all(elem < 13 for elem in b)
    
    title='🐟即時集計🐟'
    if len(enemy)==1:
        enemy2=enemy[0]
        title=f'🐟vs {enemy2}🐟'
    
    cal = discord.Embed(title=title,color=0xe74c3c,description="0-0 @12")
    result = await ctx.send(embed=cal)
    text='結果を入力してください(例:<123456>, <call> or <777>で一番上に, <back> or <333>で修正)'
    moji = await ctx.send(text)
    msg = await ctx.send('おすすめ機能は.vと.v2だよ！🐟')
    #msg = await ctx.send("🐟")

    f=0 #tatal
    g=0 #enemytotal
    h=''
    j=0 #race
    while j!=12:
        ok1 = 0
        while ok1 == 0:
            try:
                rank = await client.wait_for('message',timeout=900, check=check)
            except asyncio.TimeoutError:        
                await moji.delete()     
                break
            else:
                a = rank.content
                b = []      
                if len(a)==6 or len(a)==7 or len(a)==8 or len(a)==9:
                    if is_int(a)==True:
                        await rank.delete()
                        ok2=1
                        try:
                            if len(a)==6:
                                for i in range(6):
                                    b.append(int(a[i],16))    

                            elif len(a)==7:
                                for i in range(5):
                                    b.append(int(a[i]))
                                b.append(int(a[5:]))

                            elif len(a)==8:
                                for i in range(4):
                                    b.append(int(a[i]))
                                b.append(int(a[4:6]))
                                b.append(int(a[6:]))

                            elif len(a)==9:
                                for i in range(3):
                                    b.append(int(a[i]))
                                b.append(int(a[3:5]))
                                b.append(int(a[5:7]))
                                b.append(int(a[7:]))
                               
                            else:
                                await(await ctx.send("try again")).delete(delay=3)
                                ok2=0

                        except ValueError:
                            await(await ctx.send("try again")).delete(delay=3)
                            ok2=0
                         
                        if ok2==1:
                            if is_under12(b)==True:
                                ok1=1
                            else:
                                await(await ctx.send("try again")).delete(delay=3)                                   

                elif a == 'back' or a == '333':
                    await rank.delete()
                    h=h.replace(h2,'')
                    f-=d
                    g-=e              
                    k = str(f)+"-"+str(g)+"\t("+str(f-g)+")"
                    cal = discord.Embed(title=title,color=0xe74c3c,description="{} @{}\n---------------------\n{}".format(k,11-j+2,h))    
                    await result.edit(embed=cal)
                    await(await ctx.send("修正しました")).delete(delay=3)
                    j-=1    

                elif a == 'call' or a == '777':
                    await rank.delete()
                    await result.delete()
                    await moji.delete()
                    result = await ctx.send(embed=cal)
                    moji = await ctx.send(text)
                        
                elif a == 'end':              
                    ok1=-1
                    j=12
                    await msg.delete()
                    await moji.delete()
                    await ctx.send("即時終了")

                elif '.cal' in a:               
                    ok1=-1
                    j=12      
                    await msg.delete()
                    await moji.delete()   
        
        if ok1==1:
            await msg.delete()   
            c=str(b[0])+' '+str(b[1])+' '+str(b[2])+' '+str(b[3])+' '+str(b[4])+' '+str(b[5])
            d=0 #こっちの追加点

            for i in range(6):
                point=b[i]
                if point == 1:
                    point = 15
                elif point == 2:
                    point = 12
                else:
                    point = 13-point
                d+=point
            e=82-d #あっちの追加点
            f+=d
            g+=e

            h2= "race"+str(j+1).ljust(2)+" | "+str(d)+"-"+str(e)+" ("+str(d-e)+") | "+c+"\n"
            h += h2
            k = str(f)+"-"+str(g)+"\t("+str(f-g)+")"
            cal = discord.Embed(title=title,color=0xe74c3c,description="{} @{}\n----------------------\n{}".format(k,11-j,h))    
            await result.edit(embed=cal)
            msg = await ctx.send(h2)   
            j+=1

    if ok1==1:
        await msg.delete()
        await moji.delete()
        await ctx.send("即時終了")

        if len(enemy)==1:
            #try:
                ch=client.get_channel(729490828619284581)
                n=f-g
                if n>0:
                    text=f'win (+{n})'
                elif n==0:
                    text=f'draw'
                elif n<0:
                    text=f'lose ({n})'   
                title=f'vs {enemy2} {text}' 
                cal = discord.Embed(title=title,description=h)
                await result.edit(embed=cal)
                for i in range(len(ctx.guild.channels)):
                    if ctx.guild.channels[i].name=='戦績':
                        await result.delete()
                        await ctx.guild.channels[i].send(embed=cal)
                        break

@client.command()
async def caluse(ctx):
    text='.calに敵チームをメモれるようにしました「.cal <敵チーム名>」\n＋α：「戦績」という名前のテキストチャンネルを作成しておくと、集計終了時に集計内容が自動で転送されます.'
    await ctx.send(text)
     
@client.command()
async def l(ctx,n): #.sの機能
    if int(n)>19 and int(n)<27: 
        a=str(ctx.guild.id)
        list=ws.col_values(1)
        row=list.index(a)+1
        b=ws.row_values(row)
        await ctx.send(b[int(n)-18])


@client.command()
async def m(ctx,n): #.sの機能
    if int(n)>19 and int(n)<27: 
        a=str(ctx.guild.id)
        list=ws.col_values(1)
        row=list.index(a)+1
        b=ws.row_values(row)
        await ctx.send(b[int(n)-11])
        

async def add(channel,row,n,name,mention):
    """
    b=ws.range(row,1,row,24)
    if mention in b[n-11].value: #21→3,10,17
        b[n-18].value=b[n-18].value.replace(name,'')
        b[n-11].value=b[n-11].value.replace(mention,'')
        b[n-4].value = int(b[n-4].value)+1

    else:
        b[n-18].value += name
        b[n-11].value += mention
        b[n-4].value = int(b[n-4].value)-1
        if b[n-4].value == 0:
            await channel.send(f'{n}〆 {b[n-11].value}')
    
    ws.update_cells(b)
    """
    b=ws.range(row,1,row,24)
    if mention in b[n-11].value: #21→3,10,17
        b[n-18].value=b[n-18].value.replace(name,f'( {name}) ')
        b[n-11].value=b[n-11].value.replace(mention,'')
        b[n-4].value = int(b[n-4].value)+1

    else:
        if name in b[n-18].value:
            b[n-18].value=b[n-18].value.replace(f'( {name}) ',' ')
        else:
            b[n-18].value += name
            b[n-11].value += mention
            b[n-4].value = int(b[n-4].value)-1
            if b[n-4].value == 0:
                await channel.send(f'{n}〆 {b[n-11].value}')
        
    ws.update_cells(b)

@client.command()
async def s(ctx): #.sの機能
    a=str(ctx.guild.id)
    try:
      list=ws.col_values(1)
      row=list.index(a)+1
    except:
      ws.append_row([str(ctx.guild.id)])
      list=ws.col_values(1)
      row=list.index(a)+1
      #for i in range(22):
      #ws.update_cell(row,23,0)

    b=ws.range(row,3,row,26)
    #b=ws.row_values(row)
    for i in range(7):
        b[i].value='> '
    for i in range(7):
        b[i+7].value=''
    for i in range(7):
        b[i+14].value=6
    b[21].value=1
    now=datetime.datetime.now()
    month=now.month
    day=now.day
    text=f"{month}月{day}日"
    b[23].value=text
    ws.update_cells(b)
    
    text=f"交流戦募集 {month}月{day}日" 
    test = discord.Embed(title=text,colour=0x1e90ff)
    test.add_field(name=f"21@6 ", value='>', inline=False)
    test.add_field(name=f"22@6 ", value='>', inline=False)
    test.add_field(name=f"23@6 ", value='>', inline=False)
    test.add_field(name=f"24@6 ", value='>', inline=False)
    msg = await ctx.send(embed=test)
    await msg.add_reaction('🇦')
    await msg.add_reaction('🇧')
    await msg.add_reaction('🇨')
    await msg.add_reaction('🇩')
    await msg.add_reaction('↩')
    await msg.add_reaction('🔁')
    msg2=await ctx.send(f"21@6 22@6 23@6 24@6")
    ws.update_cell(row,2,str(msg.id))                
    ws.update_cell(row,25,str(msg2.id))                

"""
#-----------------------------------------------------
@client.event  
async def on_raw_reaction_add(payload):
    #print(payload.guild_id)
    channel = client.get_channel(payload.channel_id)
    msg=await channel.fetch_message(payload.message_id)
    if msg.author.id == botid:
        if payload.member.bot == False:
            list=ws.col_values(1)
            row=list.index(str(payload.guild_id))+1
            b=ws.row_values(row)
            if msg.id == int(b[1]):
                await msg.remove_reaction(str(payload.emoji),payload.member)
                name=payload.member.name+' '
                mention='<@!'+str(payload.member.id)+'>'+' '
                if str(payload.emoji) == '🇴':
                    n=20
                    await add(channel,row,n,name,mention)
                if str(payload.emoji) == '🇦':
                    n=21
                    await add(channel,row,n,name,mention)
                if str(payload.emoji) == '🇧':
                    n=22
                    await add(channel,row,n,name,mention)
                if str(payload.emoji) == '🇨':
                    n=23
                    await add(channel,row,n,name,mention)
                if str(payload.emoji) == '🇩':
                    n=24
                    await add(channel,row,n,name,mention)
                if str(payload.emoji) == '🇪':
                    n=25
                    await add(channel,row,n,name,mention)
                if str(payload.emoji) == '🇫':
                    n=26
                    await add(channel,row,n,name,mention)                   
                      
                b=ws.row_values(row) #21→3,10,17
                now=datetime.datetime.now()
                month=now.month
                day=now.day
                text=f"交流戦募集 {month}月{day}日"
                test = discord.Embed(title=text,colour=0x1e90ff)
                if int(b[23])==2:
                    test.add_field(name=f"20@{b[16]} ", value=b[2], inline=False)
                test.add_field(name=f"21@{b[17]} ", value=b[3], inline=False)
                test.add_field(name=f"22@{b[18]} ", value=b[4], inline=False)
                test.add_field(name=f"23@{b[19]} ", value=b[5], inline=False)
                test.add_field(name=f"24@{b[20]} ", value=b[6], inline=False)
                if int(b[23])==2:
                    test.add_field(name=f"25@{b[21]} ", value=b[7], inline=False)
                    test.add_field(name=f"26@{b[22]} ", value=b[8], inline=False)

                if str(payload.emoji) == '🔁':
                    if int(b[23])==2:
                      ws.update_cell(row,24,1)
                      b[23]=1
                    else:
                      ws.update_cell(row,24,2)  
                      b[23]=2
                    await msg.delete()
                    test = discord.Embed(title=text,colour=0x1e90ff)
                    if int(b[23])==2:
                        test.add_field(name=f"20@{b[16]} ", value=b[2], inline=False)
                    test.add_field(name=f"21@{b[17]} ", value=b[3], inline=False)
                    test.add_field(name=f"22@{b[18]} ", value=b[4], inline=False)
                    test.add_field(name=f"23@{b[19]} ", value=b[5], inline=False)
                    test.add_field(name=f"24@{b[20]} ", value=b[6], inline=False)
                    if int(b[23])==2:
                        test.add_field(name=f"25@{b[21]} ", value=b[7], inline=False)
                        test.add_field(name=f"26@{b[22]} ", value=b[8], inline=False)
                    msg = await channel.send(embed=test)
                    if int(b[23])==2:
                        await msg.add_reaction('🇴')
                    await msg.add_reaction('🇦')
                    await msg.add_reaction('🇧')
                    await msg.add_reaction('🇨')
                    await msg.add_reaction('🇩')
                    if int(b[23])==2:
                        await msg.add_reaction('🇪')
                        await msg.add_reaction('🇫')
                    await msg.add_reaction('↩')
                    await msg.add_reaction('🔁')
                    ws.update_cell(row,2,str(msg.id)) 

                if str(payload.emoji) == '↩':
                    await msg.delete()
                    msg = await channel.send(embed=test)
                    if int(b[23])==2:
                        await msg.add_reaction('🇴')
                    await msg.add_reaction('🇦')
                    await msg.add_reaction('🇧')
                    await msg.add_reaction('🇨')
                    await msg.add_reaction('🇩')
                    if int(b[23])==2:
                        await msg.add_reaction('🇪')
                        await msg.add_reaction('🇫')
                    await msg.add_reaction('↩')
                    await msg.add_reaction('🔁')
                    ws.update_cell(row,2,str(msg.id))
                else:
                    await msg.edit(embed=test)

                msg2=await channel.fetch_message(int(b[24]))
                await msg2.delete()
                if int(b[23])==1:
                    msg2=await channel.send(f"21@{b[17]} 22@{b[18]} 23@{b[19]} 24@{b[20]}")
                else:
                    msg2=await channel.send(f"20@{b[16]} 21@{b[17]} 22@{b[18]} 23@{b[19]} 24@{b[20]} 25@{b[21]} 26@{b[22]}")
                ws.update_cell(row,25,str(msg2.id))
                
            else:
                list=ws4.col_values(1)
                try:
                    row=list.index(str(payload.channel_id))+1
                    b=ws4.row_values(row)
                    if msg.id == int(b[1]): #.vote関連の時
                        await msg.remove_reaction(str(payload.emoji),payload.member)
                        
                        if str(payload.emoji) == '🙆':
                            if str(payload.member.id) in b[4]:
                                pass
                            else:
                                b=ws4.range(row,4,row,8)
                                if str(payload.member.id) in b[2].value:
                                    b[2].value=b[2].value.replace(str(payload.member.id),'')
                                    b[4].value=int(b[4].value)-1
                                b[1].value=b[1].value+str(payload.member.id)
                                b[3].value=int(b[3].value)+1
                                ws4.update_cells(b)
                                text = discord.Embed(title=f'{b[0].value}')
                                text.add_field(name='投票進行中', value=f'🙆:{b[3].value} 🙅:{b[4].value}',inline=False)
                                await msg.edit(embed=text)

                        if str(payload.emoji) == '🙅':
                            if str(payload.member.id) in b[5]:
                                pass
                            else:
                                b=ws4.range(row,4,row,8)
                                if str(payload.member.id) in b[1].value:
                                    b[1].value=b[1].value.replace(str(payload.member.id),'')
                                    b[3].value=int(b[3].value)-1
                                b[2].value=b[2].value+str(payload.member.id)
                                b[4].value=int(b[4].value)+1
                                ws4.update_cells(b)
                                text = discord.Embed(title=f'{b[0].value}')
                                text.add_field(name='投票進行中', value=f'🙆:{b[3].value} 🙅:{b[4].value}',inline=False)
                                await msg.edit(embed=text)

                        if str(payload.emoji) == '👋':
                            if b[2] == str(payload.member.id):
                                ws4.delete_rows(row)
                                text = discord.Embed(title=f'{b[3]}',color=0xff0000)
                                text.add_field(name='投票終了', value=f'🙆:{b[6]} 🙅:{b[7]}',inline=False)
                                await msg.edit(embed=text)                                                                
                except:
                    pass
"""
#-----------------------------------------------------
@client.event  
async def on_raw_reaction_add(payload):
    #print(payload.guild_id)
    channel = client.get_channel(payload.channel_id)
    msg=await channel.fetch_message(payload.message_id)
    if msg.author.id == botid:
        if payload.member.bot == False:
            list=ws.col_values(1)
            check=0
            try:
                row=list.index(str(payload.guild_id))+1
                b=ws.row_values(row)
                if msg.id == int(b[1]):
                    check=1
                    await msg.remove_reaction(str(payload.emoji),payload.member)
                    name=payload.member.name+' '
                    mention='<@!'+str(payload.member.id)+'>'+' '
                    if str(payload.emoji) == '🇴':
                        n=20
                        await add(channel,row,n,name,mention)
                    if str(payload.emoji) == '🇦':
                        n=21
                        await add(channel,row,n,name,mention)
                    if str(payload.emoji) == '🇧':
                        n=22
                        await add(channel,row,n,name,mention)
                    if str(payload.emoji) == '🇨':
                        n=23
                        await add(channel,row,n,name,mention)
                    if str(payload.emoji) == '🇩':
                        n=24
                        await add(channel,row,n,name,mention)
                    if str(payload.emoji) == '🇪':
                        n=25
                        await add(channel,row,n,name,mention)
                    if str(payload.emoji) == '🇫':
                        n=26
                        await add(channel,row,n,name,mention)                   
                        
                    b=ws.row_values(row) #21→3,10,17
                    now=datetime.datetime.now()
                    month=now.month
                    day=now.day
                    text=f"交流戦募集 {month}月{day}日"
                    test = discord.Embed(title=text,colour=0x1e90ff)
                    if int(b[23])==2:
                        test.add_field(name=f"20@{b[16]} ", value=b[2], inline=False)
                    test.add_field(name=f"21@{b[17]} ", value=b[3], inline=False)
                    test.add_field(name=f"22@{b[18]} ", value=b[4], inline=False)
                    test.add_field(name=f"23@{b[19]} ", value=b[5], inline=False)
                    test.add_field(name=f"24@{b[20]} ", value=b[6], inline=False)
                    if int(b[23])==2:
                        test.add_field(name=f"25@{b[21]} ", value=b[7], inline=False)
                        test.add_field(name=f"26@{b[22]} ", value=b[8], inline=False)

                    if str(payload.emoji) == '🔁':
                        if int(b[23])==2:
                            ws.update_cell(row,24,1)
                            b[23]=1
                        else:
                            ws.update_cell(row,24,2)  
                            b[23]=2
                        await msg.delete()
                        test = discord.Embed(title=text,colour=0x1e90ff)
                        if int(b[23])==2:
                            test.add_field(name=f"20@{b[16]} ", value=b[2], inline=False)
                        test.add_field(name=f"21@{b[17]} ", value=b[3], inline=False)
                        test.add_field(name=f"22@{b[18]} ", value=b[4], inline=False)
                        test.add_field(name=f"23@{b[19]} ", value=b[5], inline=False)
                        test.add_field(name=f"24@{b[20]} ", value=b[6], inline=False)
                        if int(b[23])==2:
                            test.add_field(name=f"25@{b[21]} ", value=b[7], inline=False)
                            test.add_field(name=f"26@{b[22]} ", value=b[8], inline=False)
                        msg = await channel.send(embed=test)
                        if int(b[23])==2:
                            await msg.add_reaction('🇴')
                        await msg.add_reaction('🇦')
                        await msg.add_reaction('🇧')
                        await msg.add_reaction('🇨')
                        await msg.add_reaction('🇩')
                        if int(b[23])==2:
                            await msg.add_reaction('🇪')
                            await msg.add_reaction('🇫')
                        await msg.add_reaction('↩')
                        await msg.add_reaction('🔁')
                        ws.update_cell(row,2,str(msg.id)) 

                    if str(payload.emoji) == '↩':
                        await msg.delete()
                        msg = await channel.send(embed=test)
                        if int(b[23])==2:
                            await msg.add_reaction('🇴')
                        await msg.add_reaction('🇦')
                        await msg.add_reaction('🇧')
                        await msg.add_reaction('🇨')
                        await msg.add_reaction('🇩')
                        if int(b[23])==2:
                            await msg.add_reaction('🇪')
                            await msg.add_reaction('🇫')
                        await msg.add_reaction('↩')
                        await msg.add_reaction('🔁')
                        ws.update_cell(row,2,str(msg.id))
                    else:
                        await msg.edit(embed=test)

                    msg2=await channel.fetch_message(int(b[24]))
                    await msg2.delete()
                    if int(b[23])==1:
                        msg2=await channel.send(f"21@{b[17]} 22@{b[18]} 23@{b[19]} 24@{b[20]}")
                    else:
                        msg2=await channel.send(f"20@{b[16]} 21@{b[17]} 22@{b[18]} 23@{b[19]} 24@{b[20]} 25@{b[21]} 26@{b[22]}")
                    ws.update_cell(row,25,str(msg2.id))
            except:
                    pass

            if check==0:
                list=ws4.col_values(1)
                try:
                    row=list.index(str(payload.channel_id))+1
                    b=ws4.row_values(row)
                    if msg.id == int(b[1]): #.vote関連の時
                        await msg.remove_reaction(str(payload.emoji),payload.member)
                        check=1

                        if str(payload.emoji) == '🙆':
                            if str(payload.member.id) in b[4]:
                                pass
                            else:
                                b=ws4.range(row,4,row,8)
                                if str(payload.member.id) in b[2].value:
                                    b[2].value=b[2].value.replace(str(payload.member.id),'')
                                    b[4].value=int(b[4].value)-1
                                b[1].value=b[1].value+str(payload.member.id)
                                b[3].value=int(b[3].value)+1
                                ws4.update_cells(b)
                                text = discord.Embed(title=f'{b[0].value}')
                                text.add_field(name='投票進行中', value=f'🙆:{b[3].value} 🙅:{b[4].value}',inline=False)
                                await msg.edit(embed=text)

                        if str(payload.emoji) == '🙅':
                            if str(payload.member.id) in b[5]:
                                pass
                            else:
                                b=ws4.range(row,4,row,8)
                                if str(payload.member.id) in b[1].value:
                                    b[1].value=b[1].value.replace(str(payload.member.id),'')
                                    b[3].value=int(b[3].value)-1
                                b[2].value=b[2].value+str(payload.member.id)
                                b[4].value=int(b[4].value)+1
                                ws4.update_cells(b)
                                text = discord.Embed(title=f'{b[0].value}')
                                text.add_field(name='投票進行中', value=f'🙆:{b[3].value} 🙅:{b[4].value}',inline=False)
                                await msg.edit(embed=text)

                        if str(payload.emoji) == '👋':
                            if b[2] == str(payload.member.id):
                                ws4.delete_rows(row)
                                text = discord.Embed(title=f'{b[3]}',color=0xff0000)
                                text.add_field(name='投票終了', value=f'🙆:{b[6]} 🙅:{b[7]}',inline=False)
                                await msg.edit(embed=text)                                                                
                except:
                    pass

            if check==0:
                list=ws5.col_values(1)
                try:
                    row=list.index(str(payload.channel_id))+1
                    b=ws5.row_values(row)    
                    if msg.id == int(b[1]): #.vote2関連の時
                        await msg.remove_reaction(str(payload.emoji),payload.member)
                        
                        if str(payload.emoji) == '🙆':
                            if str(payload.member.id) in b[4]:
                                pass
                            else:
                                b=ws5.range(row,4,row,14)
                                if str(payload.member.id) in b[2].value:
                                    b[2].value=b[2].value.replace(str(payload.member.id),'')
                                    b[8].value=b[8].value.replace(str(payload.member.name),'')
                                    b[5].value=int(b[5].value)-1
                                elif str(payload.member.id) in b[3].value:
                                    b[3].value=b[3].value.replace(str(payload.member.id),'')
                                    b[9].value=b[9].value.replace(str(payload.member.name),'')
                                    b[6].value=int(b[6].value)-1
                                b[1].value=b[1].value+str(payload.member.id)
                                b[4].value=int(b[4].value)+1
                                b[7].value=b[7].value+str(payload.member.name)
                                b[10].value=b[10].value+str(payload.member.mention)
                                ws5.update_cells(b)
                                text = discord.Embed(title=f'{b[0].value}')
                                text.add_field(name=f'🙆:{b[4].value}', value=f'{b[7].value}',inline=False)
                                text.add_field(name=f'🤷:{b[5].value}', value=f'{b[8].value}',inline=False)
                                text.add_field(name=f'🙅:{b[6].value}', value=f'{b[9].value}',inline=False)
                                await msg.edit(embed=text)

                        if str(payload.emoji) == '🤷':
                            if str(payload.member.id) in b[5]:
                                pass
                            else:
                                b=ws5.range(row,4,row,14)
                                if str(payload.member.id) in b[3].value:
                                    b[3].value=b[3].value.replace(str(payload.member.id),'')
                                    b[9].value=b[9].value.replace(str(payload.member.name),'')
                                    b[6].value=int(b[6].value)-1
                                elif str(payload.member.id) in b[1].value:
                                    b[1].value=b[1].value.replace(str(payload.member.id),'')
                                    b[7].value=b[7].value.replace(str(payload.member.name),'')
                                    b[10].value=b[10].value.replace(str(payload.member.mention),'')                                    
                                    b[4].value=int(b[4].value)-1
                                b[2].value=b[2].value+str(payload.member.id)
                                b[5].value=int(b[5].value)+1
                                b[8].value=b[8].value+str(payload.member.name)
                                ws5.update_cells(b)
                                text = discord.Embed(title=f'{b[0].value}')
                                text.add_field(name=f'🙆:{b[4].value}', value=f'{b[7].value}',inline=False)
                                text.add_field(name=f'🤷:{b[5].value}', value=f'{b[8].value}',inline=False)
                                text.add_field(name=f'🙅:{b[6].value}', value=f'{b[9].value}',inline=False)
                                await msg.edit(embed=text)

                        if str(payload.emoji) == '🙅':
                            if str(payload.member.id) in b[6]:
                                pass
                            else:
                                b=ws5.range(row,4,row,14)
                                if str(payload.member.id) in b[1].value:
                                    b[1].value=b[1].value.replace(str(payload.member.id),'')
                                    b[7].value=b[7].value.replace(str(payload.member.name),'')
                                    b[10].value=b[10].value.replace(str(payload.member.mention),'')
                                    b[4].value=int(b[4].value)-1
                                elif str(payload.member.id) in b[2].value:
                                    b[2].value=b[2].value.replace(str(payload.member.id),'')
                                    b[8].value=b[8].value.replace(str(payload.member.name),'')
                                    b[5].value=int(b[5].value)-1
                                b[3].value=b[3].value+str(payload.member.id)
                                b[6].value=int(b[6].value)+1
                                b[9].value=b[9].value+str(payload.member.name)
                                ws5.update_cells(b)
                                text = discord.Embed(title=f'{b[0].value}')
                                text.add_field(name=f'🙆:{b[4].value}', value=f'{b[7].value}',inline=False)
                                text.add_field(name=f'🤷:{b[5].value}', value=f'{b[8].value}',inline=False)
                                text.add_field(name=f'🙅:{b[6].value}', value=f'{b[9].value}',inline=False)
                                await msg.edit(embed=text)

                        if str(payload.emoji) == '👋':
                            if b[2] == str(payload.member.id):
                                ws5.delete_rows(row)
                                text = discord.Embed(title=f'{b[3]}(投票終了)',color=0xff0000)
                                text.add_field(name=f'🙆:{b[7]}', value=f'{b[10]}',inline=False)
                                text.add_field(name=f'🤷:{b[8]}', value=f'{b[11]}',inline=False)
                                text.add_field(name=f'🙅:{b[9]}', value=f'{b[12]}',inline=False)
                                await msg.edit(embed=text)   

                        if str(payload.emoji) == '📢':
                            if b[2] == str(payload.member.id):
                                await channel.send(b[13])
                                                        
                        if str(payload.emoji) == '↩':
                            if b[2] == str(payload.member.id):
                                await msg.delete()
                                text = discord.Embed(title=f'{b[3]}')
                                text.add_field(name=f'🙆:{b[7]}', value=f'{b[10]}',inline=False)
                                text.add_field(name=f'🤷:{b[8]}', value=f'{b[11]}',inline=False)
                                text.add_field(name=f'🙅:{b[9]}', value=f'{b[12]}',inline=False)
                                msg = await channel.send(embed=text)
                                ws5.update_cell(row,2,str(msg.id))
                                await msg.add_reaction('🙆')
                                await msg.add_reaction('🤷')
                                await msg.add_reaction('🙅')
                                await msg.add_reaction('👋')
                                await msg.add_reaction('📢')
                                await msg.add_reaction('↩')
                                
                except:
                    pass  

#-----------------------------------------------------    
@client.command()
async def mt(ctx): #ラウンジの集計
    def check(m):
        return m.author.id == ctx.author.id

    await ctx.send("MogiBotの'Poll Ended!'から始まる文章をコピーして貼り付けてください.\ncopy the message, starts with 'Poll Ended!'' and paste here")
    msg = await client.wait_for('message',check=check)
    msg=msg.content
    if '!scoreboard' in msg and 'Poll Ended!' in msg:
        a=msg.find('!scoreboard')
        msg2=msg[a+12:]
        if msg2[len(msg2)-1]=='`':
            msg2=msg2[0:len(msg2)-1]
        msg=msg2.split()
        team=int(msg[0])
        num=int(12/team)
        ok=0
        ok2=0
        while ok==0:
            await ctx.send(f'下記順番通りに得点を入力してください. Type scores.(例: 100 90 12+70 ...)\n{msg2[2:]}')
            try:
                score=await client.wait_for('message',timeout=300,check=check)
            except asyncio.TimeoutError:
                await ctx.send('timeout') 
                ok2=1
                break
            else:
                score=score.content
                score=score.replace('+','%2B')                
                score=score.split()
                if len(score)==12:
                    ok=1
                else:
                    await ctx.send('エラー: もう一度入力してください. 12名分の得点を正しく入力してください.')
        if ok2==0:
            text=''
            k=0
            if team==1:
                for i in range(12):
                    text=f'{text}{msg[i+1]} {score[i]}\n'
            else:
                for i in range(team):
                    text=f'{text}Team{i+1}\n'
                    for j in range(num):
                        k=k+1
                        text=f'{text}{msg[k]} {score[k-1]}\n'
            await ctx.send(text)
            await ctx.send("上記内容をコピーし 'https://hlorenzi.github.io/mk8d_ocr/table.html' にペーストしてください")
        
    else:
        await ctx.send('エラー')
        
@client.command()
async def test(ctx):
    guilds = await client.fetch_guilds(limit=150).flatten()
    print(len(guilds))
    id = 704597398550478881
    ch1 = client.get_channel(id) 
    await ch1.send(len(guilds))
 
@client.command()
async def ta(ctx):
    get_url_info = requests.get('https://mkwrs.com/mk8dx/wrs.php')
    data=get_url_info.text.split('\n\n')
    data=data[1]
    data=data.split('display.php?track=')
    j=0
    pretrack='None'
    text=''
    for i in range(48):
        if i==16:
            text3=text
            text=''
        if i==32:
            text2=text
            text=''
        ok=0
        while(ok==0):
            data2=data[j+1].split('\n')
            track=re.search('>.*</a',data2[0])
            track=track.group()
            track=track.replace('>','')
            track=track.replace('</a','')
            if track!=pretrack:
                time=re.search('\'',data2[1])
                time=data2[1][time.start()-1:time.end()+6]
                if i==40:
                    timesec=data2[11][26:86]
                else:
                    timesec=data2[11][26:52]
                timesec=timesec.replace("'",'')
                text+=f'{i+1}: {track}| {time}  ({timesec})\n'
                pretrack=track
                ok=1
            j+=1
    msg=discord.Embed(title='WR')
    msg.add_field(name=f'1', value=text3, inline=False)
    msg.add_field(name=f'2', value=text2, inline=False)
    msg.add_field(name=f'3', value=text, inline=False)
    await ctx.send(embed=msg)

"""                       
@client.command()
async def fish2(ctx, about = "🐟🐟🐟 戦績記録使い方 🐟🐟🐟"):
  help1 = discord.Embed(title=about,color=0xe74c3c,description=".p 点数: 個人の結果記録,符号＋点数を入力する(負けた試合は負),例:.p 100,.p -77\n.r 点差 チーム名: 交流戦の結果記録,例:.r 40 IsK,.r -50 Lv\n.revise 点数: 個人の結果修正,例:.p -80を消す→.revise -80\n.stats/.teamstats/.history: 戦績\n.vs チーム名: 対象チームとの戦績確認\n.rename/.teamrename: 名前の変更\n.reset/.teamreset: 戦績(statsの内容)リセット\n.teamdelete: 対戦履歴削除\n作成者: さかな(@sakana8dx)\nさかなBot導入: https://discord.com/oauth2/authorize?client_id=619351049752543234&permissions=473152&scope=bot")
  await ctx.send(embed=help1)


@client.command()
async def p(ctx,a):

  def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
  try:
    cell=ws.find(str(ctx.author.id+ctx.guild.id)) 
  except:
    ws.append_row([str(ctx.author.id+ctx.guild.id),ctx.guild.name,ctx.author.name])
    cell=ws.find(str(ctx.author.id+ctx.guild.id))
    for i in range(10):
      ws.update_cell(cell.row,len(ws.row_values(cell.row))+1,0)

  #C2:totalnum	D3:winnum	E4:losenum	F5:winrate	G6:ave	H7:winave	I8:loseave	J9:total	K10:wintotal	L11:losetotal

  b=ws.row_values(cell.row)
  if is_int(a)==False:
    msg = await ctx.send("エラー")
    await asyncio.sleep(3)
    await msg.delete()
  else:
    b[3]=int(b[3])+1
    a=int(a)
    if a>0:
      b[4]=int(b[4])+1
      b[11]=int(b[11])+a
      b[8]=b[11]//b[4]
    else:
      a=-1*int(a)
      b[5]=int(b[5])+1
      b[12]=int(b[12])+a
      b[9]=b[12]//b[5]
    b[10]=int(b[10])+a
    b[6]=int(b[4])*100//b[3]
    b[7]=b[10]//b[3]
    for i in range(13):
      ws.update_cell(cell.row,i+1,b[i])
 
    msg = await ctx.send("記録しました")
    await asyncio.sleep(3)
    await msg.delete()
  
  await ctx.channel.purge(limit=1)


@client.command()
async def stats(ctx):
  cell=ws.find(str(ctx.author.id+ctx.guild.id))
  b=ws.row_values(cell.row)
  msg = discord.Embed(title="stats",colour=0x1e90ff)
  msg.add_field(name="name", value=b[2], inline=True)
  msg.add_field(name="play", value=b[3], inline=True)
  msg.add_field(name="win rate", value=b[6]+"%", inline=True)
  msg.add_field(name="average", value=b[7], inline=True)
  msg.add_field(name="win-ave", value=b[8], inline=True)
  msg.add_field(name="lose-ave", value=b[9], inline=True)
  await ctx.channel.purge(limit=1)  
  msg = await ctx.send(embed=msg)  
  await asyncio.sleep(15)
  await msg.delete() 


@client.command()
async def rename(ctx):
  cell=ws.find(str(ctx.author.id+ctx.guild.id))
  ws.update_cell(cell.row,2,ctx.author.name)
  msg = await ctx.send("名前を修正しました")
  await asyncio.sleep(3)
  await msg.delete()


@client.command()
async def revise(ctx,a):
  def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

  try:
    cell=ws.find(str(ctx.author.id+ctx.guild.id)) 
  except:
    ws.append_row([str(ctx.author.id+ctx.guild.id),ctx.guild.name,ctx.author.name])
    cell=ws.find(str(ctx.author.id+ctx.guild.id))
    for i in range(10):
      ws.update_cell(cell.row,len(ws.row_values(cell.row))+1,0)

  #C2:totalnum	D3:winnum	E4:losenum	F5:winrate	G6:ave	H7:winave	I8:loseave	J9:total	K10:wintotal	L11:losetotal

  b=ws.row_values(cell.row)
  if is_int(a)==False:
    msg = await ctx.send("エラー")
    await asyncio.sleep(3)
    await msg.delete()
  else:
    b[3]=int(b[3])-1
    a=int(a)
    if a>0:
      b[4]=int(b[4])-1
      b[11]=int(b[11])-a
      b[8]=b[11]//b[4]
    else:
      a=-1*int(a)
      b[5]=int(b[5])-1
      b[12]=int(b[12])-a
      b[9]=b[12]//b[5]
    b[10]=int(b[10])-a
    b[6]=int(b[4])*100//b[3]
    b[7]=b[10]//b[3]
    for i in range(13):
      ws.update_cell(cell.row,i+1,b[i])
 
    msg = await ctx.send("修正しました")
    await asyncio.sleep(3)
    await msg.delete()
  
  await ctx.channel.purge(limit=1)


@client.command()
async def result(ctx):
  cell=ws.find(str(ctx.guild.id))
  b=ws.row_values(cell.row)
  msg = discord.Embed(title="stats",colour=0x1e90ff)
  msg.add_field(name="name", value=b[2], inline=True)
  msg.add_field(name="play", value=b[3], inline=True)
  msg.add_field(name="win rate", value=b[6]+"%", inline=True)
  await ctx.channel.purge(limit=1)  
  msg = await ctx.send(embed=msg)  
  await asyncio.sleep(15)
  await msg.delete() 


@client.command()
async def reset(ctx):
  cell=ws.find(str(ctx.author.id+ctx.guild.id))
  for i in range(10):
    ws.update_cell(cell.row,i+4,0)

  msg = await ctx.send("リセットしました")
  await asyncio.sleep(3)
  await msg.delete()


@client.command()
async def r(ctx,a,a2):
  def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

  try:
    cell=ws.find(str(ctx.guild.id)) 
  except:
    ws.append_row([str(ctx.guild.id),ctx.guild.name,"None"])
    cell=ws.find(str(ctx.guild.id))
    for i in range(4):
      ws.update_cell(cell.row,len(ws.row_values(cell.row))+1,0)

  b=ws.row_values(cell.row)
  if is_int(a)==False:
    msg = await ctx.send("エラー ※.r 点差 チーム名")
    await asyncio.sleep(3)
    await msg.delete()
  else:
    date=str(datetime.date.today())
    ws2.append_row([date,str(ctx.guild.id),ctx.guild.name,a,a2])

    b[3]=int(b[3])+1
    a=int(a)
    if a>0:
      b[4]=int(b[4])+1      
    else:      
      b[5]=int(b[5])+1
    b[6]=int(b[4])*100//int(b[3])
  for i in range(7):
      ws.update_cell(cell.row,i+1,b[i])
  
  msg = await ctx.send("記録しました")
  await asyncio.sleep(3)
  await msg.delete()
  
  await ctx.channel.purge(limit=1)


@client.command()
async def teamstats(ctx):
  cell=ws.find(str(ctx.guild.id))
  b=ws.row_values(cell.row)
  msg = discord.Embed(title="stats",colour=0x1e90ff)
  msg.add_field(name="name", value=b[1], inline=True)
  msg.add_field(name="play", value=b[3], inline=True)
  msg.add_field(name="win rate", value=b[6]+"%", inline=True)
  await ctx.channel.purge(limit=1)  
  msg = await ctx.send(embed=msg)  
  await asyncio.sleep(15)
  await msg.delete()


@client.command()
async def vs(ctx,a):
  w=0
  l=0
  b=''
  cell=ws2.findall(str(ctx.guild.id))
  for i in range(len(cell)):
    c=ws2.row_values(cell[i].row)
    if c[4]==a:
      if int(c[3])>0:
        w+=1
      else:
        l+=1
      b+=c[0]+" "+c[3]+"\n"
  b=f'戦績: vs {a} {w}-{l}\n'+b
  msg = await ctx.send(b)
  await asyncio.sleep(20)
  await msg.delete() 


@client.command()
async def teamreset(ctx):
  cell=ws.find(str(ctx.guild.id))
  for i in range(4):
    ws.update_cell(cell.row,i+4,0)
  msg = await ctx.send("リセットしました")
  await asyncio.sleep(3)
  await msg.delete()


@client.command()
async def teamdelete(ctx):
  cell=ws.find(str(ctx.guild.id))
  b=ws.row_values(cell.row)
  msg = discord.Embed(title="stats",colour=0x1e90ff)
  msg.add_field(name="name", value=b[1], inline=True)
  msg.add_field(name="play", value=b[3], inline=True)
  msg.add_field(name="win rate", value=b[6]+"%", inline=True)
  await ctx.channel.purge(limit=1)  
  msg = await ctx.send(embed=msg)
  
  for i in range(4):
    ws.update_cell(cell.row,i+4,0)
  cell=ws2.findall(str(ctx.guild.id))
  for i in range(len(cell)):    
    ws2.delete_row(cell[len(cell)-i-1].row)
  msg = await ctx.send("リセットしました")
  await asyncio.sleep(3)
  await msg.delete()


@client.command()
async def history(ctx):
  b=''
  cell=ws2.findall(str(ctx.guild.id))
  a=min(len(cell),100)
  for i in range(a):
    c=ws2.row_values(cell[a-i-1].row)
    b+=c[4]+" "+c[3]+" , "
  b=f'戦績:\n'+b
  msg = await ctx.send(b)


@client.command()
async def teamrename(ctx):
  cell=ws.find(str(ctx.guild.id))
  ws.update_cell(cell.row,2,ctx.guild.name)
  msg = await ctx.send("名前を修正しました")
  await asyncio.sleep(3)
  await msg.delete()
"""

token = os.environ['DISCORD_BOT_TOKEN']
client.run(token)
