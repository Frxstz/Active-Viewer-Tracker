from datetime import datetime
from collections import defaultdict

# Provided lines of data
lines = ['Joined -- chimeraxts -- 2024-07-10_09-56-34AM', 
         'Joined -- frxstz_ -- 2024-07-10_09-56-34AM', 
         'Joined -- streamelements -- 2024-07-10_09-56-34AM', 
         'Left -- streamelements -- 2024-07-10_11-56-34AM',
         'First chat -- frostqbot.tmi.twitch.tv -- 2024-07-10_09-55-09AM', 
         'First chat -- frxstz_.tmi.twitch.tv -- 2024-07-10_09-56-02AM', 
         'First chat -- chimeraxts.tmi.twitch.tv -- 2024-07-10_09-56-38AM']

# Helper function to convert timestamp to datetime object
def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, "%Y-%m-%d_%I-%M-%S%p")


# Dictionary to store user data
users = defaultdict(dict)

# Process each line to populate user data
for line in lines:
    parts = line.split(' -- ')
    action = parts[0]
    detail = parts[1]
    timestamp = parts[2]

    if action == 'Joined':
        username = detail.strip()
        users[username]['joined'] = timestamp
    elif action == 'Left':
        username = detail.strip()
        users[username]['left'] = timestamp
    elif action == 'First chat':
        username_full = detail.strip()
        username = username_full.split('.')[0]  # Remove .tmi.twitch.tv if present
        users[username]['first_chat'] = timestamp

# Get current time for users who haven't left yet
now = datetime.now().strftime("%Y-%m-%d_%I-%M-%S%p")

# Generate report
report = []
for username, data in users.items():
    joined_time = data.get('joined')
    left_time = data.get('Left', now)
    first_chat_time = data.get('first_chat')

    if joined_time is not None:
        joined_time = datetime.strptime(joined_time, "%Y-%m-%d_%I-%M-%S%p")

    if left_time is not None:
        left_time = datetime.strptime(left_time, "%Y-%m-%d_%I-%M-%S%p")
        
    if first_chat_time is not None:
        first_chat_time = datetime.strptime(first_chat_time, "%Y-%m-%d_%I-%M-%S%p")

    if joined_time:
        duration = left_time - joined_time
        duration_str = str(duration)
    else:
        duration_str = "User was here until end of broadcast"

    if first_chat_time:
        first_chat_str = first_chat_time.strftime("%I:%M:%S%p %Z")
    else:
        first_chat_str = "User has no message sent in chat"

    report.append((username, duration_str, first_chat_str))

# Sort report by duration spent (descending order)
report_sorted = sorted(report, key=lambda x: (x[1] != "User was here until end of broadcast", x[1]), reverse=True)

# Print the sorted report
for entry in report_sorted:
    username, duration_str, first_chat_str = entry
    print(f"Username: {username}")
    if 'joined' in users[username]:
        print(f"  Time Joined: {users[username]['joined']}")
    if 'left' in users[username]:
        print(f"  Time Left: {users[username]['left']}")
    print(f"  Duration: {duration_str}")
    print(f"  First Chat: {first_chat_str}")
    print()


