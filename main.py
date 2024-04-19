from dotenv import load_dotenv
load_dotenv()
import discord, os, requests, json
from discord.ext import commands
from flask import Flask, request
from threading import Thread
from models import Verification_codes

app = Flask(__name__)
bot_token = os.getenv("bot_token")


TOKEN_PROMPT_MESSAGE = "Welcome to the server! Please provide a token to gain access:"

intents = discord.Intents(messages=True, message_content=True, members=True)

bot = commands.Bot(command_prefix='/', intents=intents)
server_id = os.getenv("server_id")

global roles

@bot.event
async def on_ready():
    print("Bot is ready")

@bot.event
async def on_member_join(member):
    print("A new member just joined the Channel", member)


def verify_order_id(order_id):
    url = "https://hook.eu2.make.com/o8c11k9xco3f2yu64jnim22ase78th33"

    payload = json.dumps({"order_id": str(order_id)})
    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=payload)
    try:
        response = response.json()
        if response.get("customer_id"):
            return True
    except Exception as e:
        return False


@bot.event
async def on_message(message):
    if str(message.channel.type) == "private" and message.author != bot.user:
        text_message = message.content

        code_exist = Verification_codes.find_one({"code": text_message})
        if code_exist:
            await message.author.send("Verification Code has already been used")
        else:

            if verify_order_id(text_message):
                Verification_codes.insert_one({"user_id":  str(message.author.id), "code": text_message})
                guild = await bot.fetch_guild(int(server_id))
                member = await guild.fetch_member(message.author.id)
                role = discord.utils.get(guild.roles, name="premium")
                await member.add_roles(role)
                await message.author.send("You've been verified!")
                await message.author.send("You can check the Discord Server to View your Role")

@app.get('/')
def home():
    return {"status":"up and running"}
def start_bot():
    bot.run(bot_token)

if __name__ == "__main__":
    Thread(target=start_bot).start()
    app.run()