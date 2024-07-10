resp = ':chimeraxts!chimeraxts@chimeraxts.tmi.twitch.tv PRIVMSG #frxstz_ :Stream has Ended.'

import os
DIR              = os.getcwd()

path = os.path.join(DIR,'settings','bots.txt')
with open(path, "r") as f:
    adminBots = f.read().splitlines()

path = os.path.join(DIR,'context','end_stream_context.txt')
with open(path, "r") as f:
    endContext = f.read().splitlines()

messenger = resp.split('!')[0][1:]

print(messenger)
print(adminBots)
print(endContext)
print(resp)

print(type(endContext))

print(endContext)

if messenger in adminBots:
    if endContext[0] in resp:
        print('success')