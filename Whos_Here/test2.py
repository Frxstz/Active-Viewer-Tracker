import socket
from emoji import demojize
import logging
import os
from datetime import datetime, timedelta
from pyfiglet import Figlet
import pytz

spokenFile       = 'lists\has_spoken.txt'
presentLogFile   = 'lists\was_present.txt'

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
