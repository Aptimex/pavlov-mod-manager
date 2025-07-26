
import threading
import shutil
import hashlib
import requests
from urllib.request import urlopen, Request
from zipfile import ZipFile, BadZipFile
import time
import os

#local files
from config import *

#Download a file chunk, save it with .partX appended to the name to make final reconstruction easy
#requests.get() appears to not be thread safe, it frequently resulted in corrupt data; urlopen() seems to work fine
def downloadHandler(start, end, url, filePath, part):
    # specify the starting and ending of the file
    # Don't need API authorization header to download files
    header = {"Range": "bytes={}-{}".format(start, end)}
    #print(header)
    #exit()
    
    # request the specified part and get into variable
    req = Request(url, headers=header)
    r = urlopen(req)
    #if r.status_code != 206:
    if r.code != 206:
        print("Status code error for download: {}".format(r.status_code))
        stop()
    
    #size = int(r.headers["content-length"])
    size = int(r.getheader("content-length"))
    if end != "":
        if size != int(end) - int(start) + 1:
            print("Server responded with wrong size {}, expected {} (start:{}, end:{}). Retrying chunk".format(size, end-start+1, start, end))
            #exit()
            downloadHandler(start, end, url, filePath, part)
        
  
    # open the file (create and write, binary) and write the content
    with open(filePath + ".part" + str(part), "w+b") as fp:
        fp.write(r.read())


#uses threading to download the file faster
def downloadFile(url, dir):
    #Follow any redirects to get the final download URL
    r = requests.head(url, allow_redirects=True)
    url = r.url
    try:
        fileSize = int(r.headers['content-length'])
    except Exception as e:
        print("Couldn't get content-length; might not be a download link?")
        return
    
    #Get the filename from URL, strip off parameters
    filename = url.split("/")[-1].split("?")[0].split("#")[0]
    filePath = os.path.join(dir, filename)
    
    #don't redownload if file already exists; if it's incomplete/invalid the hash check will catch it
    if os.path.exists(filePath):
        return filePath
    
    partSize = fileSize // THREADS
    for i in range(THREADS):
        start = partSize * i
        
        end = start + partSize - 1
        if i == THREADS - 1:
            end = "" #request all remaining bytes since integer division was floored
            #end = fileSize-1 #request all remaining bytes since integer division was floored
        
        # create a Thread with start and end locations
        t = threading.Thread(target=downloadHandler,
            kwargs={'start': start, 'end': end, 'url': url, 'filePath': filePath, "part": i})
        #t.setDaemon(True) #deprecated
        t.daemon = True
        t.start()
    
    i = 1
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        
        #print("Downloading part {} of {}".format(i, THREADS))
        t.join() #blocks until the thread (download) completes
        i += 1
    
    time.sleep(.5)
    i = 0
    #join each part into the final file
    with open(filePath, 'wb') as outfile:
        for i in range(THREADS):
            #print("Recombining part {}".format(i))
            partPath = filePath + ".part" + str(i)
            with open(partPath, "rb") as infile:
                data = infile.read()
                outfile.write(data)
            os.remove(partPath)
    
    print("Download complete, installing...")
    return filePath

def downloadMod(mod, test=False):
    #print(mod.md5)
    #exit()
    if int(mod.id) in IGNORE:
        print("Skipping, mod is in the IGNORE list")
        return False
    
    if CONFIRM_DOWNLOADS:
        confirm = input("Download/Update this mod? (Y/n): ")
        if confirm.lower() != "y" and confirm.lower() != "yes" and confirm != "":
            print("Skipping mod download")
            return False
        
    
    #zipPath = downloadFile(mod.url, modPath)
    zipPath = downloadFile(mod.downloadLink, modPath)
    if not zipPath:
        print("Error downloading mod file")
        return False
    
    hash = hashlib.md5(open(zipPath,'rb').read()).hexdigest()
    if hash != mod.md5:
        print("Downloaded file hash is wrong")
        print(f"Expected: {mod.md5}")
        print(f"Actual: {hash}")
        print(f"Size: {mod.downloadSize} (expected), {os.path.getsize(zipPath)} (actual)")
        
        print("Deleting downloaded file and skipping installation")
        os.remove(zipPath)
        return False
    
    dataPath = os.path.join(mod.modFolder, "Data")
    
    if test:
        print(f"TEST flag set, skipping installation")
        os.remove(zipPath)
        return True
    
    #clean old files to make sure we don't end up with leftovers
    if os.path.exists(mod.modFolder):
        shutil.rmtree(mod.modFolder)
    
    zipFail = False
    with ZipFile(zipPath, 'r') as zip:
        try:
            zip.extractall(dataPath)
        except BadZipFile as e:
            print(f"Mod ZIP file is invalid/corrupted and cannot be safely installed. Consider unsubscribing or adding ({mod.id}) to the ignore_mods list in SETTINGS.json")
            print("Installing/updating this mod through the Pavlov game may also work.")
            zipFail = True
    
    #Can't delete the bad file inside the with statement, causes another exception (file still in use)
    if zipFail:
        os.remove(zipPath)
        return False
            
    os.remove(zipPath)
    with open(os.path.join(mod.modFolder, "taint"), "w") as taint:
        taint.write(str(mod.modfile_live))
    
    return True
    
# Given a number of bytes, returns a human-friendly string representing that size
# Just uses powers of 1000 (rather than 1024) for simplicity
def size(num):
    sNum = str(num)
    digs = len(sNum)
    
    if digs <= 3:
        return sNum + "B"
    if digs <= 6:
        return f"{sNum[:-3]}.{sNum[-3]} KB"
    if digs <= 9:
        return f"{sNum[:-6]}.{sNum[-6]} MB"
    if digs <= 12:
        return f"{sNum[:-9]}.{sNum[-9]} GB"

#Just prompts for input before calling exit() so you can read the error message before the window closes
def stop(exitCode = 0):
    print("Press any key to exit")
    input()
    exit(exitCode)
