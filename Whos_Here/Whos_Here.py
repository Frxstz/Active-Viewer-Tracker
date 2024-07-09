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
from datetime import datetime
from pyfiglet import Figlet


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
                if endContext in resp:
                    #formulating report
                    f = Figlet(font='slant')
                    header = f.renderText("Who's watching?")

                    

                    print("Bot has been shut down successfuly, you can close this terminal window.")

                    exit()

        except:
            print("ERROR/////", resp)
