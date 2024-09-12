# Random idea: create a user class or at least look at class architectures with discord.py

# Imports
# Discord, Replit DB, keep_alive, and other "key" bot operations
# from typing import ParamSpecArgs, TypeVarTuple
import discord, os
from replit import db
from keep_alive import keep_alive
from discord.ext import tasks

for i in db.keys():
    del db[i]
# APIs and other libraries to interact with data:
import icalendar, ics
from ics import Calendar
import requests
import datetime
import folium # Probably for map stuffs

# A quick not on DB Stuff: The replit DB - for now, this is the easy solution I'm using, but it probably scales terribly. Maybe in the future I'll use an external DB.

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # We want to start our background loops immediately because sometimes we might not get a message to start the loop.
    check_weather.start()
    # check_time.start()

@client.event
async def on_message(message):
    
    # Collect channel info for the background loops.
    channel_id = message.channel.id
    channel_user = message.author.id

    
    # Create new users
    if str(channel_id) not in list(db.keys()):
        print("New user found!" + str(channel_id))
        if message.author is not client.user:
            await message.channel.send("Welcome, " + str(message.author) + "!")
        db[channel_id] = {"User": channel_user, "Mode" : True, "Daily Report": True, "Primary Location" : "All", "Locations": {} , "Calendars": {}, "Toggles": {"add_calendar":False,"remove_calendar":False,
"add_loc" : False, "remove_loc": False, "name_calendar": False, "delete_for_sure": False, "change_primary_loc": False}} # Create a new key for the channel in the db. (Mode here can be simplified or comprehensive, which determines how much information is given to the user. Simplified = True, Comprehensive = False))



    # Get a user's Toggle values
    add_calendar = db[str(channel_id)]["Toggles"]["add_calendar"]
    remove_calendar = db[str(channel_id)]["Toggles"]["remove_calendar"]
    add_loc = db[str(channel_id)]["Toggles"]["add_loc"]
    remove_loc = db[str(channel_id)]["Toggles"]["remove_loc"]
    name_calendar = db[str(channel_id)]["Toggles"]["name_calendar"]
    delete_for_sure = db[str(channel_id)]["Toggles"]["delete_for_sure"]
    change_primary_loc = db[str(channel_id)]["Toggles"]["change_primary_loc"]
    add_calendar_but_not_name = False


    # Prevent Loop
    if message.author == client.user: # Prevents a loop due to the bot sending a message to itself
        return


    # Help/Get Started
    if message.content.startswith('!help'):
        await message.channel.send('Hello! Here are a few things I can help you with:\n\n- **!view_calendar_list**: View all the current calendars being tracked. \n- **!add_calendar**: Add a calendar either through an iCal link (Google Calendar and Outlook) or an .ics file (call this command for more information) \n- **!remove_calendar**: remove a calendar being tracked. \n- **!view_locations**: View a list of tracked locations for weather alerts. \n- **!add_location**: Add a location to track weather for. \n- **!remove_location**: Remove a location being tracked.\n- **!change_primary_location**: Your primary location is the main location that you get weather alerts and daily reports for. You can use **!view_weather** to get all weather reports; by default the first location you input is the primary location. \n- **!change_view_mode**: Toggle on/off simplified and comprehensive data viewing mode. \n- **!change_daily_report**: Toggle on/off daily weather report (default is on). \n- **!view_weather**: View the current weather for all locations.\n- **!feedback**: Give us your feedback! \n- **!delete_data**: Delete all your data in the DB. You will have to start fresh if you so choose.')




    # View Calendars
    if message.content.startswith('!view_calendar_list'):
        if(bool(db[str(channel_id)]["Calendars"])): # bool({}) = False
            await message.channel.send("Here are a list of calendars currently being tracked:\n\n"+ str(list(db[str(channel_id)]["Calendars"].keys())))
        else:
            await message.channel.send("You have no current calendars being tracked. Try **!add_calendar** to get started!")




    # Add Calendar, and Name it
    if message.content.startswith('!add_calendar'):
        add_calendar_but_not_name = True
        add_calendar=True
        await message.channel.send("Please add a calendar in one of two ways:\n\n- **iCal link [Preferred]**: This method is recommended and works best with Google Calendar or Outlook. You can get the iCal link for both in calendar settings (Google Calendar: Settings > Settings for my Calendar > Select Calendar > Secret/Public (needs to be published) Address in iCal Format. Outlook: Need to publish the calendar to get the link). The Bot will update your calendar every hour.\n- **Upload an .ics file** (read more about .ics here: https://fileinfo.com/extension/ics): Please note that by uploading a .ics file, you will be unable to make changes to events without deleting and reuploading a new .ics file. This format works best for things that will not change (Courses, Birthdays, Holidays, etc.)")

    elif not name_calendar and add_calendar: # The elif is really important to prevent if/if/if fall-through.
        if message.attachments:
                cal = Calendar(requests.get(message.attachments[0].url).text)
                await message.channel.send(requests.get(message.attachments[0].url).text)
        else:
            try:
                cal = Calendar(requests.get(message.content).text)
                await message.channel.send("You've attached a calendar. Please enter the name of the calendar you would like to add.")
                name_calendar = True
                add_calendar = False
            except:
                await message.channel.send("You've attached an invalid link. Please try again.")
                add_calendar = False
                name_calendar = False

    if name_calendar and not add_calendar_but_not_name: # Replaces the placeholder dict item with the actual name, but does so by copying and deleting the old key:item.
        add_calendar = False
        db[str(channel_id)]["Calendars"][message.content] = db[str(channel_id)]["Calendars"].pop(db[str(channel_id)]["Calendars"].keys()[-1])
        name_calendar=False


    # Remove Calendar
    if message.content.startswith('!remove_calendar'):
        await message.channel.send("Here are a list of calendars currently being tracked. Please enter the name of the calendar you would like to remove:\n\n"+ '\n'.join(list(db[str(channel_id)]["Calendars"].keys())))
        remove_calendar=True

    elif remove_calendar:
        if(message.content in list(db[str(channel_id)]["Calendars"].keys())):
            del db[str(channel_id)]["Calendars"][message.content]
            await message.channel.send(message.content + " has been removed.")
        else:
            await message.channel.send("That is not a valid calendar name. Please try again.")
        remove_calendar = False




    # View Location
    if message.content.startswith('!view_locations'):
        await message.channel.send("Here are a list of locations currently being tracked:\n\n"+ '\n'.join(list(db[str(channel_id)]["Locations"].keys())))



    
    # Add Location
    if message.content.startswith('!add_location'):
        add_loc = True
        await message.channel.send("Which location would you like to add? Giving as much specificity will be helpful: Ex. London, UK or Durham, NC.")

    elif add_loc: # Check if the location is valid using the Nominatim API, and if not, return an error message
        if get_coords(message.content)[0]:
            pass
        else:
            await message.channel.send("That is not a valid location. Please try again.")
        add_loc = False

    if message.content.startswith('!remove_location'):
        remove_loc=True
        await message.channel.send("Here are a list of current locations:")
        await message.channel.send('\n'.join(list(db[str(channel_id)]["Locations"].keys())))
        await message.channel.send("Which location would you like to remove?")


    elif remove_loc:
        if(message.content in list(db[str(channel_id)]["Locations"].keys())):
            del db[str(channel_id)]["Locations"][message.content]
            await message.channel.send(message.content + " has been removed.")
        else:
            await message.channel.send("That is not a valid location name. Please try again.")
            remove_loc = False


    # Change Primary Location
    if message.content.startswith('!change_primary_location'):
        await message.channel.send("Your primary location is currently **" + db[str(channel_id)]["Primary Location"] + "**. Please enter your new primary location.")
        change_primary_loc = True

    elif change_primary_loc:
        if message.content in list(db[str(channel_id)]["Locations"].keys()):
            await message.channel.send("Your primary location has been changed to " + message.content + ".")
            db[str(channel_id)]["Primary Location"] = message.content
        else:
            await message.channel.send("That location is either not in your current tracked list or an invalid location. Please try again.")
        change_primary_loc = False


    
    # Change view mode
    if message.content.startswith('!change_view_mode'):
        db[str(channel_id)]["Mode"] = not db[str(channel_id)]["Mode"]
        await message.channel.send("Your view mode is now " + "simplified." if db[str(channel_id)]["Mode"] else "comprehensive.")


    
    # Toggle On/Off daily report
    if message.content.startswith('!change_daily_report'):
        db[str(channel_id)]["Daily Report"] = not db[str(channel_id)]["Daily Report"]
        await message.channel.send("Daily report has been turned " + "on." if db[str(channel_id)]["Daily Report"] else "off.")



    # View the current weather for all locations:
    # If someone would like to see weather; idea --> 'nerd mode' (more detail), classic view (more simplified)?
    if message.content.startswith('!view_weather'):
        for i in db[str(channel_id)]["Locations"].keys():
            await message.channel.send(get_weather(channel_id, i, db[str(channel_id)]["Mode"]))
            



    # Feedback
    if message.content.startswith('!feedback'):
        await message.channel.send("Please fill out this form: [Insert Form]")



    
    # Delete stuff
    if message.content.startswith('!delete_data') or delete_for_sure:
        if delete_for_sure:
            await message.channel.send("We're sorry to see you go :cry:. Your data has now been removed from our DB. We hope to see you again soon!")
            del db[str(channel_id)]
        else:
            await message.channel.send("Woah, there. That's a big decision. Please note that once you delete your data, you will have to start fresh. Are you sure you want to delete your data? Type 'delete' to confirm.")

    if message.content.startswith('delete'):
        delete_for_sure=True



    # Reload the extracted vars into the db:
    db[str(channel_id)]["Toggles"]["add_calendar"] = add_calendar
    db[str(channel_id)]["Toggles"]["remove_calendar"] = remove_calendar
    db[str(channel_id)]["Toggles"]["add_loc"] = add_loc
    db[str(channel_id)]["Toggles"]["remove_loc"] = remove_loc
    db[str(channel_id)]["Toggles"]["name_calendar"] = name_calendar
    db[str(channel_id)]["Toggles"]["delete_for_sure"] = delete_for_sure
    db[str(channel_id)]["Toggles"]["change_primary_loc"] = change_primary_loc







# Background loops:



# Weather alerts!
@tasks.loop(seconds=5)
async def check_weather(): # An idea I have for this is to go into the DB, find all the locations and collect them in a list, and then use the weather API to mass get alerts, and then send them out if they apply to the user.

    # Get unique weather locations in a set:
    get_unique_locations = set()
    for i in db.keys():
        for j in list(db[i]["Locations"].keys()):
            get_unique_locations.add(j)

    # API Calls:

    # Part 1: Geolocation via Nominatim:
    

    
    # This code below sends a message to all channels. In the actual implementation, I'll need to only send to channels that have the specific city tracking, or modify in some way.
    await client.wait_until_ready()
    if list(db.keys()) != []:
        keys = db.keys()
        message="Hi"
        for i in keys:
            channel = client.get_channel(int(i))
            if channel is not None: # If it's a text channel in a server
                print("Sending to Channel")
                #await channel.send(message)
            else:
                user_id = int(db[i]["User"]) # If it's a DM, in which case it's not a channel, but tied to the specific user.
                user = await client.fetch_user(user_id)
                print(user)
                #await user.send(message)
    else:
        print("No users to track")





# @tasks.loop(seconds=300) # Calendar Tracking Loop! Create a custom looping time that loops slowly as events are far in the future and then minute-by-minute in say, the final hour (just to make the code less resource-intensive)
# async def check_time():
#     channel = client.get_channel(channel_id)
#     print("Calendar Ping")



# Update Calendar
@tasks.loop(hours=1) # For users that provide an iCal link, this will update their calendar every hour.
async def get_cal():
    for i in db.keys():
        for j in db[i]["Calendar"].keys():
            if db[i]["Calendar"][j]["Type"] == "Link":
                cal = Calendar(requests.get(db[i]["Calendar"][j]).text)
    




# Helper Functions:

def get_weather(channel_id, location, view_type): # Takes in a list of location and the view type, and returns the weather alert message 
    message = "**" + location + "** Current Weather\n\n"
    if view_type: # Simplified view:
        coords = db[str(channel_id)]["Locations"][location] # Get the coords for the location
        
    else: # Comprehensive view:
        pass
    return message


# Use the Nominatim API to get the coords for a location: Returns the first search result, and the user would have to play around with things.
def get_coords(location):
    search_str = '+'.join(location.replaceAll(',', ' ').split())
    loc_api_return = requests.get("https://nominatim.openstreetmap.org/search?q="+search_str+"&format=json").json()
    try:
        lat, long = loc_api_return[0]["lat"], loc_api_return[0]["lon"]
        it_worked = True
    except:
        it_worked = False
        lat, long = 0,0
    return [it_worked, lat, long]

# SUPER IMPORTANT:

# keep_alive()
client.run(os.environ['TOKEN'])
