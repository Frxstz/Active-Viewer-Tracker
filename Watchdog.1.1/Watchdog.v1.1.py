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
from collections import defaultdict


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
print("\nWatch established. Bot is Successfully running.. ...\n-------------------\n")

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
                now = datetime.now().strftime("%Y-%m-%d_%I-%M-%S%p")
                
                currentList.append(user)
                ToFile(spokenFile, user+" -- "+now+"\n", "a")

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

                now = datetime.now().strftime("%Y-%m-%d_%I-%M-%S%p")
                for b in range(len(new_joiners)):
                    temp = new_joiners[b].strip("\n")
                    ToFile(presentLogFile, "Joined -- " + temp +" -- "+now+"\n", "a")

                print("leavers",leavers)

                now = datetime.now().strftime("%Y-%m-%d_%I-%M-%S%p")
                for b in range(len(leavers)):
                    temp = leavers[b].strip("\n")
                    ToFile(presentLogFile, "Left -- " + temp +" -- "+now+"\n", "a")

                presentList = stayers + new_joiners

                print("current viewers", presentList)

            
            messenger = resp.split('!')[0][1:]
            #check if messenger is one of the possible bots responsible for queue change
            if messenger in adminBots:
                #kill the queue bot after stream ends
                if endContext[0] in resp:
                    logfile = f'logs/Stream_{datetime.now().strftime("%Y-%m-%d_%I-%M-%S%p")}.txt'
                    with open(logfile, 'a') as file:  
                        # Fixing my Dumb ass way I did this
                        for i in range(len(presentList)):
                            temp = presentList[i].strip("\n")
                            ToFile(presentLogFile, "Left -- " + temp +" -- "+now+"\n", "a")
                            with open(spokenFile, "r") as f:
                                FCLlines2 = f.readlines()
                            with open(presentLogFile, "r") as f:
                                PLFLines2 = f.readlines()

                            PLFLines, FCLlines = [], []

                            for i in range(len(PLFLines2)):
                                PLFLines.append(PLFLines2[i].strip(' \n'))

                            for i in range(len(FCLlines2)):
                                FCLlines.append(FCLlines2[i].strip(' \n'))

                            first_chat_lines = [f"First chat -- {line.split(' ')[0]} -- {line.split(' ')[-1]}" for line in FCLlines]

                            # Combine both datasets
                            PLFLines.extend(first_chat_lines)
                            # Helper function to convert timestamp to datetime object
                            def parse_timestamp(timestamp_str):
                                return datetime.strptime(timestamp_str, "%Y-%m-%d_%I-%M-%S%p")

                            # Dictionary to store user data with lists for multiple logs
                            users = defaultdict(lambda: defaultdict(list))

                            # Process each line to populate user data
                            for line in PLFLines:
                                parts = line.split(' -- ')
                                action = parts[0]
                                detail = parts[1]
                                timestamp = parts[2]

                                username_full = detail.strip()
                                username = username_full.split('.')[0]  # Remove .tmi.twitch.tv if present
                                
                                users[username][action.lower()].append((timestamp, action))  # Store tuple of (timestamp, action)

                            # Get current time for users who haven't left yet
                            now = datetime.now()

                            # Generate report
                            report = []
                            for username, actions in users.items():
                                join_logs = actions['joined']
                                left_logs = actions['left']
                                first_chat_logs = actions['first chat']

                                # Keep track of the last left_time_dt for streamelements
                                last_left_time_dt = None
                                
                                for i in range(len(join_logs)):
                                    joined_time, _ = join_logs[i]
                                    joined_time_dt = parse_timestamp(joined_time)

                                    # Find the corresponding 'left' log for this 'joined' log
                                    left_time_dt = None
                                    for left_time, _ in left_logs:
                                        left_time_dt = parse_timestamp(left_time)
                                        if left_time_dt > joined_time_dt:
                                            last_left_time_dt = left_time_dt
                                            break
                                    
                                    # If no corresponding 'left' log found, use the last known left_time_dt for streamelements
                                    if left_time_dt is None and last_left_time_dt:
                                        left_time_dt = last_left_time_dt
                                    elif left_time_dt is None and i == len(join_logs) - 1:
                                        left_time_dt = now
                                    elif left_time_dt is None:
                                        continue  # Skip this join event as there's no matching leave event
                                    
                                    # Calculate duration
                                    duration = left_time_dt - joined_time_dt
                                    duration_str = str(duration)

                                    # Find first chat time
                                    if first_chat_logs:
                                        first_chat_time, _ = first_chat_logs[0]
                                        first_chat_time_dt = parse_timestamp(first_chat_time)
                                        first_chat_str = first_chat_time_dt.strftime("%I:%M:%S%p %Z")
                                    else:
                                        first_chat_str = "User has no message sent in chat"
                                
                                    report.append((username, joined_time, left_time_dt, duration_str, first_chat_str))

                            # Print the report
                            for entry in report:
                                username, joined_time, left_time, duration_str, first_chat_str = entry
                                file.write(f"Username: {username}\n")
                                file.write(f"  Time Joined: {joined_time}\n")
                                file.write(f"  Time Left: {left_time.strftime('%Y-%m-%d_%I-%M-%S%p')}\n")
                                if left_time == now:
                                    file.write(f"  Duration: {duration_str} (Stayed until end of stream)\n")
                                else:
                                    file.write(f"  Duration: {duration_str}\n")
                                file.write(f"  First Chat: {first_chat_str}\n")
                                file.write("-" * 50)
                                file.write("\n")
                            print("Bot has been shut down successfuly, you can close this terminal window.")
                            file.close()
                            exit()
        except Exception as e:
            print("Error:", e)