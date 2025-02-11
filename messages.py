"""
A file to hold/return longer bot messages to maintain clean code
"""
# Internal
from user import User

def help()->str:
    """Returns the help message"""
    return '''Hello! Here are a few things I can help you with:\n\n- **!view_calendar_list**: View all the current calendars being tracked. 
    \n- **!add_calendar**: Add a calendar either through an iCal link (Google Calendar and Outlook) or an .ics file (call this command for 
    more information) \n- **!remove_calendar**: remove a calendar being tracked. \n- **!view_locations**: View a list of tracked locations 
    for weather alerts. \n- **!add_location**: Add a location to track weather for. \n- **!remove_location**: Remove a location being tracked.
    \n- **!change_primary_location**: Your primary location is the main location that you get weather alerts and daily reports for. 
    You can use **!view_weather** to get all weather reports; by default the first location you input is the primary location. 
    \n- **!change_view_mode**: Toggle on/off simplified and comprehensive data viewing mode. \n- **!change_daily_report**: Toggle on/off 
    daily weather report (default is on). \n- **!view_weather**: View the current weather for all locations.\n- **!feedback**: Give us your 
    feedback! \n- **!delete_data**: Delete all user data. You will have to start fresh if you so choose.'''


def view_calendars(db:dict, user:User):
    pass