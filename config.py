#configuration settings
import os
import sys
#from SETTINGS import *

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

#load configuration settings
with open(os.path.join(script_dir, "./SETTINGS.py")) as f:
    exec(f.read())

#THREADS = 10
tokenFile = os.path.join(script_dir, "./AUTH_TOKEN")
with open(tokenFile, "a") as f: #create the file if it doesn't exist
    pass
with open(tokenFile, "r") as f:
    TOKEN = f.read().strip()
    if len(TOKEN) < 1000:
        print(f"Your auth token is either missing or likely invalid. Please update the AUTH_TOKEN file if the program fails.")
    #print(TOKEN)

'''
settingsFile = "SETTINGS"
with open(settingsFile, "r") as f:
    lines = f.readlines()
    for line in lines:
        if line[:7] == "THREADS":
            THREADS = int(line.split("=").strip())
'''

#modPath = "%localappdata%\\Pavlov\\Saved\\Mods"
#PLATFORM = "windows"

#Don't attempt to download/update these mod IDs
#Useful for some mods we can't manually install due to corrupted ZIP files, but that Pavlov can somehow still install
#example: IGNORE = [1234567, 7654321]
#IGNORE = [3051820]

#Don't touch anything below here or the program will break
apiBase = "https://api.mod.io/v1"
modPath = os.path.expandvars(modPath)
header = {"Authorization": "Bearer " + TOKEN}
AUTH_HEADER = {"Authorization": "Bearer " + TOKEN}
PLATFORM = PLATFORM.lower()
API_HEADER = {"Authorization": "Bearer " + TOKEN, "X-Modio-Platform" : PLATFORM.lower()}
gameID = 3959
PAGE_LIMIT = str(500)
