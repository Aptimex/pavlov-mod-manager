#!/usr/bin/env python3

#Multi-threaded download logic is modified from the example here: https://www.geeksforgeeks.org/simple-multithreaded-download-manager-in-python/#

import os
import json
import time
#import winsound
import textwrap
from sys import exit #otherwise PyInstaller complains
import argparse

#local files
#from config import modPath, gameID, apiBase
from config import *
import api
import downloads

#Mods to downloads and install will go in here
toDownload = []


def queueSubscriptionUpdates():
    print("Fetching mod subscriptions, this may take a moment...")
    
    r = api.makeAPIRequest("/me/subscribed", AUTH_HEADER) #API doesn't like it if you include the platform header here
    if r.status_code != 200:
        print(f"Error getting user subscriptions: code {r.status_code}")
        stop()
    #print(json.dumps(r.json(), indent=2))
    
    if r.json()["result_count"] < 1:
        print("No subscriptions")
        return
    
    subs = r.json()["data"]
    subIDs = []
    for sub in subs:
        if sub["game_id"] != gameID: #skip non-pavlov stuff
            continue
        subIDs.append(sub["id"])
    
    #print(subIDs)
    
    mods = api.getAllModsData(subIDs)
    for mod in mods:
        mod.currentVersion = -1 #indicate this is a subscription check, not an on-disk check
    
    print(f"Subscribed mods: {len(mods)}")
    queueDownloads(mods)
    return

def queueDownloads(mods):
    print(f'{"Mod Name" :<50} {"Mod ID" :<10} {"Size" :<10} {"Status" :<8}')
    print("-------------------------------------------------------------------------------")
    #print(mods[0])
    for mod in mods:
        if not mod.currentVersion:
            mod.currentVersion = 0
        
        if int(mod.id) in IGNORE:
            action = "In IGNORE list"
        elif mod.modfile_live == mod.currentVersion:
            action = "Up to date"
        else:
            if mod.currentVersion == -1: #identified from subscription, not from disk
                if os.path.exists(mod.modFolder):
                    action = "Subscribed (already downloaded)"
                else:
                    action = "Subscribed (needs download)"
                    toDownload.append(mod)
            else:
                action = "Update available"
                toDownload.append(mod)
        
        #print(f'{mod.name :<25} {mod.id :<12} {action :<1}')
        
        modName = textwrap.fill(mod.name, width=49)
        modLines = modName.split('\n')
        numLines = len(modLines)
        #print(modLines[0])
        
        for i, line in enumerate(modLines):
            if i == 0:
                print(f"{line :<50}", end="")
            else:
                print(f"\n {line :<49}", end="")
            
        print(f'{mod.id :<10} {downloads.size(mod.downloadSize) :<10} {action :<1}')
        
        time.sleep(.01) # Totally unecessary, but makes long lists less visually jarring.
    
    return

def queueOnDiskUpdates():
    print(f"Reading mods from disk ({modPath})")
    
    modIDs = []
    modVersions = []
    
    #Only process folders that start with UGC as expected
    modFolders = [f[0] for f in os.walk(modPath) if os.path.isdir(f[0]) and f[0].split(os.sep)[-1].startswith("UGC")]
    
    for folder in modFolders:
        modID = folder.split("UGC")[-1]
        
        #skip folders that don't follow the valid mod folder name format
        #avoids craches if the user has backups of folders, e.g. ending in .bak or similar
        if not modID.isdigit():
            continue
        modIDs.append(modID)
        #mod = api.getModData(modID)
        
        try:
            with open(os.path.join(folder, "taint"), "r") as taint:
                installed = int(taint.read())
        except Exception as e:
            print(f"Unable to identify installed version of {modID} via taint file; mod will be treated as needing an update.")
            installed = 0
        
        modVersions.append(installed)
    
    #print(modIDs)
    print(f"Total local mods identified: {len(modIDs)}")
    print()
    print(f"Retrieving online info about {len(modIDs)} local mods...")
    print()
    
    mods = api.getAllModsData(modIDs)
    for mod in mods:
        id = mod.id
        mod.currentVersion = modVersions[modIDs.index(str(id))]
        
    queueDownloads(mods)
    print()
    print(f"{len(toDownload)} mods need updates")
    return

def selectOperation():
    print("Select an operation (default is 1):")
    #print("[0] Watch for mod downloads, download them faster")
    print("[1] Update all installed mods")
    print("[2] Download missing subscribed mods")
    print("[3] Do 1 then 2")
    print("[4] List currently installed mods")
    print("[5] List currently subscribed mods")
    print("[0] Exit")
    print("Select: ", end="")
    
    x = input()
    if x == "":
        x = 1
    print()
    
    try:
        select = int(x)
    except Exception as e:
        print("Selection must be a single digit")
        return selectOperation()
    
    if select == 0:
        exit()
    if select == 1:
        return "local"
    if select == 2:
        return "subs"
    if select == 3:
        return "both"
    if select == 4:
        print("Tip: you can search the ID value at https://mod.io/g/pavlov to find and subscribe to each installed mod.")
        queueOnDiskUpdates() #This prints the relevant info
        stop()
    if select == 5:
        queueSubscriptionUpdates()
        stop()
    

def main(args=None):
    global toDownload
    
    if not os.path.exists(modPath):
        print(f"Root mod path ({modPath}) doesn't exist, can't continue. Verify your config settings.")
        
    
    #make sure auth token works before proceeding
    r = api.makeAPIRequest("/me")
    if r.status_code != 200:
        print(f"Error using token to get user data: status code {r.status_code}")
        if r.status_code >= 400 and r.status_code < 500:
            print("Your OAuth token may be invalid or missing.")
        stop()
    
    op = selectOperation()
    
    if op == "local" or op == "both":
        print()
        queueOnDiskUpdates()
        updateCount = len(toDownload)
        
        print()
        #print(f"{len(toDownload)} mods queued for update")
        for i, mod in enumerate(toDownload):
            print(f"[{i+1}/{updateCount}] Updating {mod.name} (ID {mod.id}), downloading {downloads.size(mod.downloadSize)}... ", flush=True)
            
            if args.test:
                downloads.downloadMod(mod, test=True)
                break
            else:
                downloads.downloadMod(mod)
            
            print("Done!")
            print()
        
        toDownload = []
        print("Local mod updates complete!")
        print()
    
    if op == "subs" or op == "both":
        queueSubscriptionUpdates()
        print()
        for mod in toDownload:
            print(f"Installing missing subscription {mod.name} (ID {mod.id}), downloading {downloads.size(mod.downloadSize)}... ", flush=True)
            downloads.downloadMod(mod)
            print("Done!")
            print()
            
        toDownload = []
        print("Subscription downloads complete!")
    
    stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", action="store_true", help="Flag used for internal testing; don't use this")
    
    args = parser.parse_args()
    main(args)
