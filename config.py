#configuration settings
import os
import sys
import json

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

#load configuration settings
with open(os.path.join(script_dir, "SETTINGS.json")) as f:
    settings = json.loads(f.read())

try:
    modPath = settings["mods_path"]
    PLATFORM = settings["game_platform"]
    THREADS = settings["download_threads"]
    IGNORE = settings["ignore_mods"]
except Exception as e:
    print(f"Missing or invalid settings, check the SETTINGS.json file in {script_dir}")
    print(f"Error: {e}")
    exit(1)


tokenFile = os.path.join(script_dir, "AUTH_TOKEN")
with open(tokenFile, "a") as f: #create the file if it doesn't exist
    pass
with open(tokenFile, "r") as f:
    TOKEN = f.read().strip()
    if len(TOKEN) < 1000:
        print(f"Your auth token is either missing or likely invalid. Please update the AUTH_TOKEN file in {script_dir} if the program fails.")



#Don't touch anything below here or the program will break
apiBase = "https://api.mod.io/v1"
modPath = os.path.expandvars(modPath)
header = {"Authorization": "Bearer " + TOKEN}
AUTH_HEADER = {"Authorization": "Bearer " + TOKEN}
PLATFORM = PLATFORM.lower()
API_HEADER = {"Authorization": "Bearer " + TOKEN, "X-Modio-Platform" : PLATFORM.lower()}
gameID = 3959
PAGE_LIMIT = str(500)
