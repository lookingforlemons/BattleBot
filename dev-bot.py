# DEVELOPMENT ONLY

# Clone Hero: Battle Royale Management System for FrostedGH's Igloo
# last modified: 04-01-19
# MAKE SURE PERMISSIONS ARE GOOD FOR BOT IN BOTH MOD AND BR CHANNELS
from typing import BinaryIO
import discord
from discord.ext import commands
from PIL import Image
import pytesseract
from sql_tools import db_connect, create_contestant, get_current_score, update_score, get_all_scores, get_discord_id
import re
import math
from datetime import timedelta, datetime

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
con = db_connect()

song_name = "Sidney's Fanatical Solo Frenzy"

bot = commands.Bot("!")
# discord bot token (DEV VALUES CURRENTLY)
token = "NTU3Mzc2Njg3MDYzNTY0MzA1.D33KZw.sWSPTwerQoNKHTRhAU47VHCaGk8"
mgmt_channel = 559112691881345030


@bot.command()
async def submit(ctx):
    message_author = ctx.author
    author_id = ctx.author.id
    message_channel = ctx.channel
    mod_channel = bot.get_channel(mgmt_channel)
    player_score = 123456789
    player_speed = 100

    if str(message_channel) != 'brtest':
        print("not in channel")
        return

    if len(ctx.message.attachments) < 1:
        print("This message contains no attachments")
        await message_channel.send(f'{message_author.mention}, You have attached no submission, F')
        await ctx.message.delete()
        return
    message_attachment = ctx.message.attachments[0]
    # creates file in br directory for read/write
    f: BinaryIO = open(f'c:\\temp\\chbr\\dev\\{message_author}-{ctx.message.created_at.strftime("%m-%d-%M")}.png',
                       "ab+")
    await message_attachment.save(fp=f)
    await ctx.message.delete()

    # iterates through the tesseract img to string function to find
    # score and speed based on score screen
    image_text = pytesseract.image_to_string(Image.open(
        f'c:\\temp\\chbr\\dev\\{message_author}-{ctx.message.created_at.strftime("%m-%d-%M")}.png'))
    for line in image_text.splitlines(True):
        words = line.split(" ")
        for word in words:
            no_comma = word.replace(",", "")
            no_comma_no_period = no_comma.replace(".", "")
            d = l = 0
            for c in no_comma_no_period:
                if c.isdigit():
                    d = d + 1
                elif c.isalpha():
                    l = l + 1
                else:
                    pass

            if d >= 6:
                if d <= 8:
                    if "/" in no_comma_no_period:
                        continue
                    if "x" in no_comma_no_period:
                        continue
                    if "%" in no_comma_no_period:
                        continue
                    player_score = no_comma_no_period
            else:
                pass

            if d == 3:
                if "%" in no_comma_no_period:
                    if "(" in no_comma_no_period:
                        speed = no_comma_no_period
                        player_speed = re.sub("[^0-9]", "", speed)
                    continue
            else:
                pass

    await message_channel.send(f'Thanks {message_author.mention}, Submission Recorded!')
    multiplier = float(player_speed) * .01
    total_score_float = float(player_score) * multiplier
    total_score = math.ceil(float(total_score_float))
    print(f"{message_author} has made a submission of {total_score} "
          f"to Clone Hero: Battle Royale")

    # analyzes the score if it needs to be updated
    current_score = get_current_score(con, message_author)
    if current_score != 0:
        updated_id = update_score(con, message_author, int(total_score))
        print(f"Database ID: {updated_id}")
    else:
        # pushes new score to database
        submission_id = create_contestant(con, int(author_id), str(message_author), int(total_score), int(player_speed))
        print(f"Database ID: {submission_id}")
    # sends the message to the mod channel
    await mod_channel.send(file=discord.File(fp=f), content=f"From: {message_author.mention}\nScore w/ Speed Bonus "
    f"(if applicable): {int(total_score)}")

    con.commit()

    f.close()


# tallies all scores and prints and mentions in order of descending score in the mod channel
@bot.command()
async def tally(ctx):
    message_author = ctx.author

    if str(ctx.channel) != 'moderators':
        await ctx.channel.send(f'You cannot do this in this channel.')
        print("not in channel")
        return

    await ctx.channel.send("Okay, Retrieving Final Scores!")
    all_scores = get_all_scores(con)
    for row in all_scores:
        id_unstripped = get_discord_id(con, str(row[0]))
        id_stripped = re.sub("[^0-9]", "", str(id_unstripped))
        user_object = bot.get_user(int(id_stripped))
        await ctx.channel.send(f"{user_object.mention} with a score of {str(row[1])}")

    await ctx.message.delete()
    print(f"The scores have been tallied and sent by {message_author}")


# sends a close message to the submission channel
@bot.command()
async def close_round(ctx):
    if str(ctx.channel) != 'brtest':
        print("not in channel")
        return
    print("Submissions Closed for this round.")
    await ctx.message.delete()
    await ctx.channel.send('ALL SUBMISSIONS CLOSED FOR THIS ROUND. Please await the mods for the tally and next chart.')


@bot.command()
async def start_round(ctx):
    if str(ctx.channel) != 'brtest':
        print("not in channel")
        return
    print(f"Submissions open for this round. Cross your fingers")
    await ctx.message.delete()
    date_time = datetime.now() + timedelta(days=3)
    date_time_formatted = date_time.strftime("%A, %B %d")
    await ctx.channel.send(f"Submissions Open for {song_name}. Entries due by {date_time_formatted} at 10:00PM CST.")


@bot.event
async def on_ready():  # the event `on_ready` is triggered when the bot is ready to function
    print("The bot is READY!")
    print(f"Logged in as: {bot.user.name}")


bot.run(token)
