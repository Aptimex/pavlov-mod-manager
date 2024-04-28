import requests
import json
from urllib.request import urlopen

#Config contains all the global variables we need
from config import *

class Mod:
    name = None
    id = None
    currentVersion = None
    modfile_live = None
    downloadLink = None
    url = None #deprecating this to speed up queries
    downloadSize = None
    extractedSize = None
    md5 = None
    filename = None #This isn't really needed/used since Pavlov uses its own file naming conventions
    modFolder = None
    
    def __init__(self):
        super(Mod).__init__()
    
    def __str__(self):
        attrs = vars(self)
        return '\n'.join("%s: %s" % item for item in attrs.items())
    
#Pass in the URL path starting with /
def makeAPIRequest(path, headers=API_HEADER):
    r = requests.get(apiBase + path, headers=headers)
    if r.status_code != 200:
        if r.status_code == 429: #Too Many Requests
            wait = int(r.headers["retry-after"]) + 1
            print(f"Rate limit detected, waiting {wait} seconds to continue")
            time.sleep(wait)
            return makeAPIRequest(url, headers)
            
        print(f"Request error, code {r.status_code}")
        #return (None, r.status_code)
    
    return r

def getModfileData(modID, modfile_live):
    #print(f"{modID}_{modfile_live}")
    
    path = f"/games/{gameID}/mods/{modID}/files?id={modfile_live}"
    #r = requests.get(url, headers=header)
    r = makeAPIRequest(path)
    if r.status_code != 200:
        print(f"Error getting mod data for Mod {modID}, modfile {modfile_live}. Code {r.status_code}")
        return None
    #print(json.dumps(r.json(), indent=2))
    
    data = r.json()["data"]
    #print(json.dumps(data, indent=2))
    if len(data) != 1:
        print(f"ERROR: Returned {len(data)} entries for Mod {modID}, modfile {modfile_live}. Expected 1 entry.")
        return None
    
    return data[0]

def getAllModsData(modIDs):
    modList = []
    
    done = False
    offset = 0
    while not done: #Handle pagination of results
    
        #Build the query string
        modsQuery = "id-in="
        for id in modIDs:
            modsQuery += str(id) + ","
            
        modsQuery = modsQuery[:-1] #remove trailing comma
        
        #Get generic data about the mods
        endpoint = f"/games/{gameID}/mods/?_offset={offset}&{modsQuery}"
        
        r = makeAPIRequest(endpoint)
        if r.status_code != 200:
            print(f"Error getting mods info: code {r.status_code}")
            return None
        
        data = r.json()
        if data["result_count"] + data["result_offset"] >= data["result_total"]:
            done = True
        else:
            offset += data["result_count"]

        '''
        for v in data:
            if v != "data":
                print(f"{v}:{data[v]}")
        print()
        '''
        
        for mod in data["data"]:
            modData = Mod()
            modData.name = mod["name"]
            modData.id = mod["id"]
            
            #get current (live) modfile ID for windows platform
            for p in mod["platforms"]:
                if p["platform"].lower() == PLATFORM:
                    modData.modfile_live = p["modfile_live"]
                    break
            if modData.modfile_live == None:
                print(f"Couldn't find '{PLATFORM}' version of mod {modID}, consider unsubscribing/deleting")
                continue
            
            
            # This should be for Windows due to a header we sent
            modfileData = mod["modfile"]
            if modfileData["id"] != modData.modfile_live:
                print(f"ERROR: Returned modfile data is not the one for {PLATFORM}")
                continue
                
            modData.downloadSize = modfileData["filesize"]
            modData.extractedSize = modfileData["filesize_uncompressed"]
            modData.md5 = modfileData["filehash"]["md5"]
            modData.downloadLink = modfileData["download"]["binary_url"]
            #modData.url = requests.head(modData.downloadLink, allow_redirects=True).url #resolve to final download URL
            #modData.filename = modData.url.split("/")[-1]
            modData.filename = modfileData["filename"]
            modData.modFolder = "{}\\UGC{}".format(modPath, modData.id)
            
            modList.append(modData)
        
    for modNum in modIDs:
        found = False
        for mod in modList:
            if mod.id == modNum or str(mod.id) == str(modNum):
                found = True
                break
        if not found:
            print(f"WARNING: No data returned for Mod ID {modNum}")
    
    return modList
