import discord, datetime, os
from replit import db
from keep_alive import keep_alive
from discord.ext import tasks
# Random Notes:
db.clear()
# DB Stuff: The replit DB - for now, this is the easy solution I'm using, but it probably scales terribly. Maybe in the future I'll use an external DB.
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    check_weather.start()
    # check_time.start()

@client.event
async def on_message(message):
    channel_id = message.channel.id
    channel_user = message.author.id
    print(channel_user)
    if str(channel_id) not in list(db.keys()):
        print(list(db.keys()))
        print("New user found!" + str(channel_id))
        db[channel_id] = {"User": channel_user, "Locations": {} , "Calendars": {}} # Create a new key for the channel in the db.
    if message.author == client.user: # Prevents a loop due to the bot sending a message to itself
        return
    if message.content.startswith('!help'):
        await message.channel.send('Hello! Here are a few things I can help you with:\n\n- **!view_calendar_list**: View all the current calendars being tracked. \n- **!add_calendar**: Add a calendar in .ics file format (read more about .ics here: https://fileinfo.com/extension/ics)\n- **!remove_calendar [Insert-Calendar-Name]**: remove a calendar being tracked. \n- **!view_locations**: View a list of tracked locations for weather alerts. \n- **!add_location**: Add a location to track weather for. \n- **!remove_location [Insert-Location-Name]**: Remove a location being tracked.')

    if message.content.startswith('!view_calendar_list'):
        await message.channel.send("Here are a list of calendars currently being tracked:\n\n"+ str(list(db[channel_id]["Calendars"].keys())))
    if message.content.startswith('!add_calendar'):
        pass
    if message.content.startswith('!remove_calendar'):
        pass
    if message.content.startswith('!view_locations'):
        pass
    if message.content.startswith('!add_location'):
        pass
    if message.content.startswith('!remove_location'):
        pass


@tasks.loop(seconds=5) # Weather Tracking Loop! Runs every 2 minutes.
async def check_weather():
    await client.wait_until_ready()
    if list(db.keys()) != []:
        keys = db.keys()
        message="Hi"
        for i in keys:
            channel = client.get_channel(int(i))
            if channel is not None:
                print("Sending to Channel")
                await channel.send(message)
            else:
                user_id = int(db[i]["User"])
                user = await client.fetch_user(user_id)
                print(user)
                await user.send(message)
    else:
        print("No users to track")
    
# @tasks.loop(seconds=300) # Calendar Tracking Loop! Create a custom looping time that loops slowly as events are far in the future and then minute-by-minute in say, the final hour (just to make the code less resource-intensive)
# async def check_time():
#     channel = client.get_channel(channel_id)
#     print("Calendar Ping")

# keep_alive()
    
client.run(os.environ['TOKEN'])
