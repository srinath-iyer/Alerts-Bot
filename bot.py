# Imports

# Discord, Replit DB, keep_alive, and other "key" bot operations
# from typing import ParamSpecArgs, TypeVarTuple
import discord, os
from replit import db
from keep_alive import keep_alive
from discord.ext import tasks

# APIs and other libraries to interact with data:
import icalendar, ics
import requests


# db.clear()
# A quick not on DB Stuff: The replit DB - for now, this is the easy solution I'm using, but it probably scales terribly. Maybe in the future I'll use an external DB.

client = discord.Client(intents=discord.Intents.default())

# Boolean toggles for bot features.
add_calendar = False
remove_calendar = False
add_loc = False
remove_loc = False
name_calendar = False
delete_for_sure = False

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # We want to start our background loops immediately because sometimes we might not get a message to start the loop.
    check_weather.start()
    # check_time.start()

@client.event
async def on_message(message):
    
    # Preset False values

    # Collect channel info for the background loops.
    channel_id = message.channel.id
    channel_user = message.author.id
    # Create new users
    if str(channel_id) not in list(db.keys()):
        print(list(db.keys()))
        print("New user found!" + str(channel_id))
        db[channel_id] = {"User": channel_user, "Locations": {} , "Calendars": {}} # Create a new key for the channel in the db.

    
    if message.author == client.user: # Prevents a loop due to the bot sending a message to itself
        return

    if message.content.startswith('!help'):
        await message.channel.send('Hello! Here are a few things I can help you with:\n\n- **!view_calendar_list**: View all the current calendars being tracked. \n- **!add_calendar**: Add a calendar either through an iCal link (Google Calendar and Outlook) or an .ics file (read more about .ics here: https://fileinfo.com/extension/ics, more about iCal here: )\n- **!remove_calendar**: remove a calendar being tracked. \n- **!view_locations**: View a list of tracked locations for weather alerts. \n- **!add_location**: Add a location to track weather for. \n- **!remove_location**: Remove a location being tracked.\n- **!view_weather**: View the current weather for all locations.\n- **!feedback**: Give us your feedback! \n**!delete_data**: Delete all your data in the DB. You will have to start fresh if you so choose.')

    if message.content.startswith('!view_calendar_list'):
        if(db[str(channel_id)]["Calendars"] != {}):
            await message.channel.send("Here are a list of calendars currently being tracked:\n\n"+ str(list(db[str(channel_id)]["Calendars"].keys())))
        else:
            await message.channel.send("You have no current calendars being tracked. Try **!add_calendar** to get started!")
    if message.content.startswith('!add_calendar'):
        global add_calendar
        add_calendar=True
        await message.channel.send("Please add a calendar in one of two ways:\n\n- **iCal link**: This method is recommended and works best with Google Calendar or Outlook. You can get the iCal link for both in calendar settings (Google Calendar: Settings > Settings for my Calendar > Select Calendar > Secret/Public (needs to be published) Address in iCal Format. Outlook: Need to publish the calendar to get the link). The Bot will update your calendar every hour.\n- **Upload an .ics file (read more about .ics here: https://fileinfo.com/extension/ics): Please note that by uploading a .ics file, you will be unable to make changes to events without deleting and reuploading a new .ics file. This format works best for things that will not change (Courses, Birthdays, Holidays, etc.)")
    if message.content.startswith('!remove_calendar'):
        await message.channel.send("Here are a list of calendars currently being tracked. Please enter the name of the calendar you would like to remove:\n\n"+ '\n'.join(list(db[str(channel_id)]["Calendars"].keys())))
        global remove_calendar
        remove_calendar=True
    if message.content.startswith('!view_locations'):
        await message.channel.send("Here are a list of locations currently being tracked:\n\n"+ '\n'.join(list(db[str(channel_id)]["Locations"].keys())))
    if message.content.startswith('!add_location'):
        global add_loc
        add_loc = True
        await message.channel.send("Which location would you like to add?")
    if message.content.startswith('!remove_location'):
        global remove_loc
        remove_loc=True
        await message.channel.send("Which location would you like to remove?")

    # If someone would like to see weather; idea --> 'nerd mode' (more detail), classic view (more simplified)?
    if message.content.startswith('!view_weather'):
        pass

    if message.content.startswith('!feedback'):
        await message.channel.send("Please fill out this form: [Insert Form]")

    # Delete stuff
    if message.content.startswith('!delete_data'):
        if delete_for_sure:
            await message.channel.send("We're sorry to see you go :cry:. Your data has now been removed from our DB. We hope to see you again soon!")
            del db[str(channel_id)]

            global delete_for_sure
            delete_for_sure = False
        else:
            await message.channel.send("Woah, there. That's a big decision. Please note that once you delete your data, you will have to start fresh. Are you sure you want to delete your data? Type 'delete' to confirm.")

    if message.content.startswith('delete'):
        global delete_for_sure
        delete_for_sure=True

    # Adding/Removing Sections:
    elif add_calendar: # The elif is really important to prevent if/if/if fall-through.
        await message.channel.send("You've attached a calendar. Please enter the name of the calendar you would like to add.")
        global add_calendar, name_calendar
        add_calendar = False
        name_calendar = True

    # Remove Calendar
    elif remove_calendar:
        if(message.content in list(db[str(channel_id)]["Calendars"].keys())):
            del db[str(channel_id)]["Calendars"][message.content]
            await message.channel.send(message.content + " has been removed.")
        else:
            await message.channel.send("That is not a valid calendar name. Please try again.")
        global remove_calendar
        remove_calendar = False
    elif add_loc:
        
        global add_loc
        add_loc = False

    # Remove loc
    elif remove_loc:
        if(message.content in list(db[str(channel_id)]["Locations"].keys())):
            del db[str(channel_id)]["Locations"][message.content]
            await message.channel.send(message.content + " has been removed.")
        else:
            await message.channel.send("That is not a valid location name. Please try again.")
        global remove_loc
        remove_loc = False

    # Actually name the calendar!
    elif name_calendar: # Replaces the placeholder dict item with the actual name, but does so by copying and deleting the old key:item.
        db[str(channel_id)]["Calendars"][message.content] = db[str(channel_id)]["Calendars"].pop(db[str(channel_id)]["Calendars"].keys()[-1])
        global name_calendar
        name_calendar=False

    
# Background loops:


@tasks.loop(seconds=5)
async def check_weather(): # An idea I have for this is to go into the DB, find all the locations and collect them in a list, and then use the weather API to mass get alerts, and then send them out if they apply to the user.

    # Get unique weather locations in a set:
    get_unique_locations = set()
    for i in db.keys():
        for j in list(db[i]["Locations"].keys()):
            get_unique_locations.add(j)

    
    # This code below sends a message to all channels. In the actual implementation, I'll need to only send to channels that have the specific city tracking, or modify in some way.
    await client.wait_until_ready()
    if list(db.keys()) != []:
        keys = db.keys()
        message="Hi"
        for i in keys:
            channel = client.get_channel(int(i))
            if channel is not None:
                print("Sending to Channel")
                #await channel.send(message)
            else:
                user_id = int(db[i]["User"])
                user = await client.fetch_user(user_id)
                print(user)
                #await user.send(message)
    else:
        print("No users to track")
    
# @tasks.loop(seconds=300) # Calendar Tracking Loop! Create a custom looping time that loops slowly as events are far in the future and then minute-by-minute in say, the final hour (just to make the code less resource-intensive)
# async def check_time():
#     channel = client.get_channel(channel_id)
#     print("Calendar Ping")

@tasks.loop(hours=1) # For users that provide an iCal link, this will update their calendar every hour.
async def get_cal():
    for i in db.keys():
        for j in db[i]["Calendar"].keys():
            if db[i]["Calendar"][j]["Type"] == "Link":
                cal = Calendar(requests.get(url).text)
    


# SUPER IMPORTANT:

# keep_alive()
client.run(os.environ['TOKEN'])
