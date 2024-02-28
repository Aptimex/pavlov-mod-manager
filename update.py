#!/usr/bin/env python3

#Multi-threaded download logic is modified from the example here: https://www.geeksforgeeks.org/simple-multithreaded-download-manager-in-python/#

import os
import json
import time
import winsound
from sys import exit #otherwise PyInstaller complains

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
        exit()
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
    #col1 = 15
    #col2 = 12
    #col3 = 1
    print(f'{"Mod Name" :<25} {"Mod ID" :<12} {"Status" :<8}')
    print("----------------------------------------------")
    #print(mods[0])
    for mod in mods:
        #id = mod.id
        if not mod.currentVersion:
            mod.currentVersion = 0
        
        #print(f"{mod.name} ({id}): \t", end="")
        if mod.modfile_live == mod.currentVersion:
            action = "Up to date"
        else:
            if mod.currentVersion == -1: #identified from subscription, not from disk
                if os.path.exists(mod.modFolder):
                    action = "Subscribed (already downloaded)"
                else:
                    action = "Subscribed (needs download)"
                    toDownload.append(mod)
            else:
                #print("Update available, adding to queue")
                action = "Update available, adding to queue"
                toDownload.append(mod)
        
        print(f'{mod.name :<25} {mod.id :<12} {action :<1}')
        time.sleep(.01) # Totally unecessary, but makes long lists less visually jarring.
    
    return

def queueOnDiskUpdates():
    print(f"Reading mods from disk ({modPath})")
    
    modIDs = []
    modVersions = []
    for folder in [f[0] for f in os.walk(modPath) if os.path.isdir(f[0]) and f[0].split("\\")[-1].startswith("UGC")]:
        modID = folder.split("UGC")[-1]
        modIDs.append(modID)
        #mod = api.getModData(modID)
        
        try:
            with open(folder + "\\taint", "r") as taint:
                installed = int(taint.read())
        except Exception as e:
            print("Unable to identify installed version via taint file; mod will be treated as needing an update")
            installed = 0
        
        modVersions.append(installed)
    
    #print(modIDs)
    print(f"Total local mods identified: {len(modIDs)}")
    print()
    print("Retrieving online info about local mods, this may take a moment...")
    print()
    
    mods = api.getAllModsData(modIDs)
    for mod in mods:
        id = mod.id
        mod.currentVersion = modVersions[modIDs.index(str(id))]
        
    queueDownloads(mods)
    return
    
    
    
    
    
    '''
    mods = []
    for i in range(((len(modIDs)-1) // 100) + 1):
        modBatch = modIDs[i*100:(i+1)*100]
        mods += api.getAllModsData(modBatch)
    '''
    
    #col1 = 15
    #col2 = 12
    #col3 = 1
    print(f'{"Mod Name" :<25} {"Mod ID" :<12} {"Status" :<8}')
    print("----------------------------------------------")
    #print(mods[0])
    for mod in mods:
        id = mod.id
        currentVersion = modVersions[modIDs.index(str(id))]
        
        #print(f"{mod.name} ({id}): \t", end="")
        if mod.modfile_live != currentVersion:
            #print("Update available, adding to queue")
            action = "Update available, adding to queue"
            toDownload.append(mod)
        else:
            #print("Up to date")
            action = "Up to date"
        
        print(f'{mod.name :<25} {mod.id :<12} {action :<1}')
    
    return
    
    
    
    
    #list folders in the modPath that start with UGC
    for folder in [f[0] for f in os.walk(modPath) if os.path.isdir(f[0]) and f[0].split("\\")[-1].startswith("UGC")]:
        modID = folder.split("UGC")[-1]
        mod = api.getModData(modID)
        if not mod:
            print("Couldn't find mod data associated with folder '{}', skipping".format(folder))
            continue
        print(mod.name + ": ", end="")
        
        try:
            with open(folder + "\\taint", "r") as taint:
                installed = int(taint.read())
        except Exception as e:
            print("Unable to verify installed version via taint file. Adding to queue to be safe.")
            toDownload.append(mod)
            continue
        
        if installed != mod.modfile_live:
            print("Update available, adding to queue")
            toDownload.append(mod)
            continue
        
        #also check the installed size to possibly detect and fix corrupted mods
        #pakName = ""
        onDiskSize = 0
        dataFolder = mod.modFolder + "\\Data"
        if not os.path.exists(dataFolder):
            print("Mod folder missing Data subdir, adding to queue")
            toDownload.append(mod)
            continue
            
        for file in os.listdir(dataFolder):
            onDiskSize += os.path.getsize(dataFolder + "\\" + file)
        
        if onDiskSize != mod.extractedSize:
            print("Installed mod size is wrong, possibly corrupted. Adding to queue")
            #print("{} (actual) vs {} (expected)".format(onDiskSize, expectedSize))
            toDownload.append(mod)
            continue
        else:
            print("Up to date!")



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
        print("Tip: you can search the ID value at https://mod.io/g/pavlov to find and subscribe to each installed mod")
        queueOnDiskUpdates() #This prints the relevant info
        exit()
    if select == 5:
        queueSubscriptionUpdates()
        exit()
    

def main(args=None):
    global toDownload
    
    if not os.path.exists(modPath):
        print(f"Root mod path ({modPath}) doesn't exist, can't continue. Verify your config settings.")
        exit()
    
    #make sure auth token works before proceeding
    r = api.makeAPIRequest("/me")
    if r.status_code != 200:
        print(f"Error using token to get user data: status code {r.status_code}")
        if r.status_code >= 400 and r.status_code < 500:
            print("Your OAuth token may be invalid or missing.")
        exit()
    
    op = selectOperation()
    
    if op == "local" or op == "both":
        print()
        queueOnDiskUpdates()
        print()
        print(f"{len(toDownload)} mods queued for update")
        for mod in toDownload:
            print(f"Updating {mod.name} (ID {mod.id}), downloading {downloads.size(mod.downloadSize)}... ", flush=True)
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
    
    

if __name__ == '__main__':
    main()
