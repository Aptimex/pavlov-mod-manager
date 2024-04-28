#configuration settings
import os
import sys
import json

#Just prompts for input before calling exit() so you can read the error message before the window closes
def stop(exitCode = 0):
    print("Press ENTER to exit")
    input()
    exit(exitCode)

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

#load configuration settings
try:
    with open(os.path.join(script_dir, "SETTINGS.json")) as f:
        settings = json.loads(f.read())
except FileNotFoundError as e:
    print(f"Cannot find SETTINGS.json in {script_dir}, exiting")
    stop(1)


try:
    modPath = settings["mods_path"]
    PLATFORM = settings["game_platform"]
    THREADS = settings["download_threads"]
    IGNORE = settings["ignore_mods"]
    
    if THREADS < 1:
        THREADS = 1
except Exception as e:
    print(f"Missing or invalid settings, check the SETTINGS.json file in {script_dir}")
    print(f"Error: {e}")
    stop(1)


tokenFile = os.path.join(script_dir, "AUTH_TOKEN")
with open(tokenFile, "a") as f: #create the file if it doesn't exist
    pass
with open(tokenFile, "r") as f:
    TOKEN = f.read().strip()
    if len(TOKEN) == 0:
        print(f"Your AUTH_TOKEN file is empty, possibly was just created. Please follow the README instructions to put your API key in it.")
        stop()
    elif len(TOKEN) < 1000:
        print(f"Your AUTH_TOKEN is likely invalid. Please fix the AUTH_TOKEN file in {script_dir} if the program fails. Details in the README")



#Don't touch anything below here or the program will break
apiBase = "https://api.mod.io/v1"
modPath = os.path.expandvars(modPath)
header = {"Authorization": "Bearer " + TOKEN}
AUTH_HEADER = {"Authorization": "Bearer " + TOKEN}
PLATFORM = PLATFORM.lower()
API_HEADER = {"Authorization": "Bearer " + TOKEN, "X-Modio-Platform" : PLATFORM.lower()}
gameID = 3959
PAGE_LIMIT = str(500)
