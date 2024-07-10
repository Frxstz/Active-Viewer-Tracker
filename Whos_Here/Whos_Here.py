"""
Who's watchin?
Author: frxstz on discord
    C# StreamerBot assistance from Bop on Discord, Krausader on Discord

Dependencies: 
- Python3
- pip (usually installed with python)
- emoji (use "python -m pip install emoji --upgrade")
"""

import socket
from emoji import demojize
import logging
import os
from datetime import datetime, timedelta
from pyfiglet import Figlet
import pytz


DIR              = os.getcwd()
server           = 'irc.chat.twitch.tv'
port             = 6667
nickname         = 'frostqbot'
token            = 'oauth:d0sktoon2hp5cycavtyog9nz2pshld'
spokenFile       = 'lists\has_spoken.txt'
presentFile      = 'lists\current_users.txt'
presentLogFile   = 'lists\was_present.txt'
currentList, presentList = [], []


with open("chat.log", 'w') as f:
    pass

def GetContextFileInfo():
    global adminBots, channels, endContext, usersFile

    path = os.path.join(DIR,'settings','channels.txt')
    with open(path, "r") as f:
        channels = f.read().splitlines()

    path = os.path.join(DIR,'settings','bots.txt')
    with open(path, "r") as f:
        adminBots = f.read().splitlines()

    path = os.path.join(DIR,'context','end_stream_context.txt')
    with open(path, "r") as f:
        endContext = f.read().splitlines()

    path = os.path.join(DIR,'lists','current_users.txt')
    with open(path, "r") as f:
        usersFile = f.read().splitlines()

# Parses out the user from the chat response. Depends on the 
# user being '@' in chat in order to correctly locate the correct user
def GetUser(response):
    username = response.split('@')[-1]
    username = (username.split()[0]).split(',')[0]
    return username


# Determines the index in a list where a substring is located regardless of case
def IndexContainingSubstring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring.lower() in s.lower():
            return i
    return -1

# Given a file, data, and type (where type is 'r', 'w' aka fil actions) 
# # writes to the file
def ToFile(file, data, type):
    with open(file, type) as file1:
        file1.write(data)



GetContextFileInfo()

# SOME QUICK VALIDATION
if not len(channels):
    print("FAILURE - The channels.txt file is empty! This must have at least 1 channel. MSG Frxstz for more info.")
    exit()

if not len(adminBots):
    print("FAILURE - The bots.txt file is empty! This must have at least 1 username. MSG Frxstz for more info.")
    exit()

if not len(endContext):
    print("FAILURE - The end_stream_context.txt file is empty! This must have context for an ending stream message. MSG Frxstz for more info.")
    exit()

sock = socket.socket()
sock.connect((server, port))
sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
chnloutput = '\n-------------------\nConnected Twitch Chats: '
for chnl in channels:
    chnloutput += '\n'+chnl
    sock.send(f"JOIN {'#'+chnl}\n".encode('utf-8'))
print(chnloutput)

resp = sock.recv(2048).decode('utf-8')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s — %(message)s',
                    datefmt='%Y-%m-%d_%H:%M:%S',
                    handlers=[logging.FileHandler('chat.log', encoding='utf-8')])

logging.info(resp)
print("\nQueue established. Bot is Successfully running.. ...\n-------------------\n")

# clear files
with open(spokenFile, 'w') as f:
    pass 
with open(presentFile, 'w') as f:
    pass 
with open(presentLogFile, 'w') as f:
    pass 


while True:
    resp = sock.recv(2048).decode('utf-8')
    print(resp)

    if resp.startswith('PING'):
        sock.send("PONG\n".encode('utf-8'))

    elif len(resp) > 0:
        logging.info(demojize(resp))
        try:
            GetContextFileInfo()

            # Has Spoken
            if GetUser(resp) not in currentList:
                user = GetUser(resp)
                now = datetime.now().strftime("%I:%M:%S%p %Z")
                
                currentList.append(user)
                ToFile(spokenFile, user+" - "+now+"\n", "a")

            # was present

            stayers = []

            with open(presentFile, "r") as f:
                plines = f.readlines()

                for i in range(len(plines)):
                    for k in range(len(presentList)):
                        if plines[i] == presentList[k]:
                            stayers.append(presentList[k])

                new_joiners = plines
                leavers = presentList 

                for x in range(len(stayers)):
                    new_joiners.remove(stayers[x])

                for x in range(len(stayers)):
                    leavers.remove(stayers[x])  

                print("new_joiners",new_joiners)

                now = datetime.now().strftime("%I:%M:%S%p %Z")
                for b in range(len(new_joiners)):
                    temp = new_joiners[b].strip("\n")
                    ToFile(presentLogFile, "Joined -- " + temp +" - "+now+"\n", "a")

                print("leavers",leavers)

                now = datetime.now().strftime("%I:%M:%S%p %Z")
                for b in range(len(leavers)):
                    temp = leavers[b].strip("\n")
                    ToFile(presentLogFile, "left -- " + temp +" - "+now+"\n", "a")

                presentList = stayers + new_joiners

                print("current viewers", presentList)

            
            messenger = resp.split('!')[0][1:]
            #check if messenger is one of the possible bots responsible for queue change
            if messenger in adminBots:
                #kill the queue bot after stream ends
                if endContext[0] in resp:

                    with open(spokenFile, "r") as f:
                        FCLlines2 = f.readlines()
                    with open(presentLogFile, "r") as f:
                        PLFLines2 = f.readlines()

                    PLFLines, FCLlines = [], []

                    for i in range(len(PLFLines2)):
                        PLFLines.append(PLFLines2[i].strip(' \n'))

                    for i in range(len(FCLlines2)):
                        FCLlines.append(FCLlines2[i].strip(' \n'))


                    first_chat_lines = [f"First chat -- {line.split(' ')[0]} - {line.split(' ')[-1]}" for line in FCLlines]

                    # Combine both datasets
                    PLFLines.extend(first_chat_lines)

                    # Formulating report
                    f = Figlet(font='slant')
                    header = f.renderText("Who's watching?")
                    # Define CDT timezone
                    cdt = pytz.timezone('America/Chicago')

                    # File Initialization
                    logfile = f'logs/Stream_{datetime.now().strftime("%Y-%m-%d_%I-%M-%S%p")}.txt'

                    try:
                        # Open the file in 'append' mode ('a')
                        with open(logfile, 'a') as file:
                            # Optionally, write some initial data to the file
                            file.write(f"{header}\n")
                            file.write(f"Created by Frxstz\n \n ")

                            # Initialize variables to track join and leave times
                            join_times = {}
                            leave_times = {}
                            first_chat_times = {}

                            # Process each line in the dataset
                            for line in PLFLines:
                                parts = line.split(" -- ")
                                action, details = parts[0], parts[1]
                                username, timestamp = details.split(" - ")

                                # Parse the timestamp (assuming all times are in CDT)
                                naive_time_obj = datetime.strptime(timestamp, "%I:%M:%S%p")
                                cdt_time_obj = cdt.localize(naive_time_obj)

                                # Record join, leave, or first chat time
                                if action == "Joined":
                                    join_times[username] = cdt_time_obj
                                elif action == "left":
                                    leave_times[username] = cdt_time_obj
                                elif action == "First chat":
                                    first_chat_times[username] = cdt_time_obj

                            # Calculate total time spent for each user
                            user_total_times = {}

                            # Iterate over join and leave times to calculate total time spent
                            for username, join_time in join_times.items():
                                if username in leave_times:
                                    leave_time = leave_times[username]
                                    duration = leave_time - join_time
                                else:
                                    duration = datetime.now(cdt) - join_time

                                # Add total duration to user_total_times dictionary
                                if username in user_total_times:
                                    user_total_times[username] += duration
                                else:
                                    user_total_times[username] = duration

                            # Sort users by total time spent (descending)
                            sorted_users = sorted(user_total_times.items(), key=lambda x: x[1], reverse=True)

                            # Print sorted report
                            file.write("Clock Out Report: \n")
                            file.write("-------------------------\n")
                            for username, total_time in sorted_users:
                                join_time = join_times[username]
                                join_formatted = join_time.strftime("%I:%M:%S%p %Z")

                                if username in leave_times:
                                    leave_time = leave_times[username]
                                    leave_formatted = leave_time.strftime("%I:%M:%S%p %Z")
                                    duration = leave_time - join_time
                                    duration_str = f"{duration.seconds // 3600} hours, {(duration.seconds % 3600) // 60} minutes, {duration.seconds % 60} seconds"
                                    file.write(f"{username} joined at {join_formatted} and left at {leave_formatted}\n")
                                    file.write(f"Duration: {duration_str}\n")
                                else:
                                    current_time = datetime.now(cdt)
                                    current_formatted = current_time.strftime("%I:%M:%S%p %Z")
                                    duration = current_time - join_time
                                    duration_str = f"{duration.seconds // 3600} hours, {(duration.seconds % 3600) // 60} minutes, {duration.seconds % 60} seconds"
                                    file.write(f"{username} joined at {join_formatted} and is still active, clocked out at {current_formatted}\n")
                                    file.write(f"Duration so far: {duration_str}\n")

                                # Check if there's a first chat entry for this user
                                if username in first_chat_times:
                                    first_chat_time = first_chat_times[username]
                                    first_chat_formatted = first_chat_time.strftime("%I:%M:%S%p %Z")
                                    file.write(f"First chat: {first_chat_formatted}\n")
                                else:
                                    file.write(f"First chat: User has not typed in chat\n")

                                file.write("-------------------------\n")
                            print("Bot has been shut down successfuly, you can close this terminal window.")
                            file.close()
                            exit()

                    except OSError as e:
                        print(f"Error: {e}")
        except Exception as e:
            print("Error:", e)

