import discord
import time
import asyncio
# External File
from discord.ext import commands

import load_json_variable as variable

# Define the prefix. All command can call after prefix.
profit = 0
stock_channel_id = 835453371062288404
prefix = "!"

bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_ready():
    game = discord.Game("waitting")
    await bot.change_presence(status=discord.Status.online, activity=game)
    print("READY")
    await bot.get_channel(stock_channel_id).send('나님등장')
    # await test_1()


@bot.event
async def on_disconncect():
    print('연결 끊김')
    await bot.get_channel(stock_channel_id).send('나님퇴장')


@bot.event
async def on_conncect():
    print('연결 ~')


@bot.event
async def on_message(message):
    # When bot sent message, do nothing.
    if message.author.bot:
        return None
    # Process Commands
    print('get_message')
    await bot.process_commands(message)


@bot.command(name="명령어")
async def react_help(ctx):
    embed = discord.Embed(title="명령어 목록", description="모든 명령어 앞에는 !를 붙여주세요.",
                          color=0x62c1cc)  # Embed의 기본 틀(색상, 메인 제목, 설명)을 잡아줍니다
    embed.add_field(name="수익률", value="수익률 설명이 나오겠지요?", inline=False)
    embed.add_field(name="수익률1", value="수익률 설명이 나오나?", inline=False)
    embed.add_field(name="노래", value="듣고싶은 노래", inline=False)

    # embed.set_footer(text="하단 설명")  # 하단에 들어가는 조그마한 설명을 잡아줍니다

    await ctx.message.channel.send(embed=embed)  # embed를 포함 한 채로 메시지를 전송합니다.
    # await ctx.message.channel.send("할 말", embed=embed)  # embed와 메시지를 함께 보내고 싶으시면 이렇게 사용하시면 됩니다.
    return None


@bot.command(name="노래")
async def react_song(ctx):
    print(ctx.message)

    embed = discord.Embed(title="메인 제목", description="설명", color=0x62c1cc)  # Embed의 기본 틀(색상, 메인 제목, 설명)을 잡아줍니다
    embed.set_footer(text="하단 설명")  # 하단에 들어가는 조그마한 설명을 잡아줍니다
    embed.add_field(name="소제목", value="설명", inline=True)
    await ctx.message.channel.send(embed=embed)  # embed를 포함 한 채로 메시지를 전송합니다.
    await ctx.message.channel.send("할 말", embed=embed)  # embed와 메시지를 함께 보내고 싶으시면 이렇게 사용하시면 됩니다.
    return None


@bot.command(name="수익률")
async def react_show(ctx):
    # Send a message to channel what user sent
    await ctx.channel.send('현재까지 수익률은 {}원 입니다.'.format(profit))
    return None


def set_profit(cur_profit):
    profit = cur_profit


# 종목, 가격, 수량
async def trade(buy, name, price, many):

    await bot.get_channel(stock_channel_id).send('{}을(를) {}원에 {}주를 매도했습니다.'.format(name, price, many))
    return None


def start_bot():
    bot.run(variable.get_token())


async def test_1():
    await trade(True, '샘숭전자', 100, 5)

async def test_2():
    await trade(False, '샘숭전자', 100, 5)

if __name__ == "__main__":
    # Referencing token in Json file and run the bot.
    bot.run(variable.get_token())
