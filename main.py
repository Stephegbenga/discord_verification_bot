from dotenv import load_dotenv
load_dotenv()
import discord, os, requests, json
from discord.ext import commands
from flask import Flask, request
from threading import Thread
from models import Verification_codes, Settings

app = Flask(__name__)
bot_token = os.getenv("bot_token")

TOKEN_PROMPT_MESSAGE = "Welcome to the server! Please provide a token to gain access:"

intents = discord.Intents(messages=True, message_content=True, members=True)

bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)
server_id = os.getenv("server_id")
welcome_message = "Hello and welcome! I’m here to get you started. 🚀 To unlock full access to the TVT Community, please send me your personal code right here."
used_code_message = "Oops! This code has already been used. 😕 Please check your details and try again, or contact support for assistance."
success_message = "Verification complete! 🌟 You now have full access. Check out the channels to dive into all the resources and start connecting with fellow traders. Happy trading!"
invalid_code_message = "Hmm, that code doesn’t seem to be valid. 🤔 Please double-check your code and try again, or reach out to support for help."
already_verified_message = "You're already verified! 🎉 No further action is needed. Feel free to explore the channels and engage with the community. Happy trading!"




@bot.event
async def on_ready():
    print("Bot is ready")


@bot.event
async def on_member_join(member):
    try:
        await member.send(welcome_message)

    except Exception as e:
        print("Something went wrong", e)


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
    if message.content.startswith('/'):
        await bot.process_commands(message)
        return

    if str(message.channel.type) == "private" and message.author != bot.user:
        setting = Settings.find_one({})

        text_message = message.content

        code_exist = Verification_codes.find_one({"code": text_message})
        if code_exist:
            await message.author.send(used_code_message)
        else:

            verify = verify_order_id(text_message)
            if verify:
                Verification_codes.insert_one({"user_id":  str(message.author.id), "code": text_message})
                guild = await bot.fetch_guild(int(server_id))
                member = await guild.fetch_member(message.author.id)
                role = discord.utils.get(guild.roles, name="premium")
                if role in member.roles:
                    await message.author.send(setting['already_verified_message'])
                    return

                await member.add_roles(role)
                await message.author.send(setting['success_message'])
            else:
                await message.author.send(setting['invalid_code_message'])


@bot.tree.command(name='change_welcome_message', description='Change the welcome message')
async def change_welcome_message(interaction, *, new_message: str):
    Settings.update_one({},{"$set": {"welcome_message": new_message}})
    await interaction.response.send_message(f'Welcome message changed to: {new_message}')

@bot.tree.command(name='change_verified_message', description='Change the verified message')
async def change_verified_message(interaction, *, new_message: str):
    Settings.update_one({},{"$set": {"already_verified_message": new_message}})
    await interaction.response.send_message(f'Success verification message changed to: {new_message}')

@bot.tree.command(name='change_code_used_message', description='Change the code used error message')
async def change_code_used_message(interaction, *, new_message: str):
    Settings.update_one({},{"$set": {"used_code_message": new_message}})
    await interaction.response.send_message(f'Code used message changed to: {new_message}')

@bot.tree.command(name='change_invalid_code_message', description='Change the invlaid code error message')
async def change_invalid_code_message(interaction, *, new_message: str):
    Settings.update_one({},{"$set": {"invalid_code_message": new_message}})
    await interaction.response.send_message(f'Invalid code message changed to: {new_message}')

@bot.tree.command(name='change_already_verified_message', description='Change the already used error message')
async def change_already_used_message(interaction, *, new_message: str):
    Settings.update_one({},{"$set": {"already_verified_message": new_message}})
    await interaction.response.send_message.send(f'Already used message changed to: {new_message}')

bot.run(bot_token)

