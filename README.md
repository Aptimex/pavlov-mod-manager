# Pavlov Mod Updater
Keep your Pavlop map mods from Mod.io up to date on Windows. Only tested on Windows with the Steam game, and only with Map mods.

Primary Features:
- Detect and update out-of-date maps that are already installed
- Download all maps you've subscribed to on Mod.io
- List installed or subscribed mods
- Built-in download accelerator helps ensure you max out your bandwidth and download maps as fast as possible

Tip: If you want to trigger a re-install of a map, use this program to list installed mods (option 4) and note the map's `Mod ID`. Then navigate to `%localappdata%\Pavlov\Saved\Mods\UGC<MOD_ID>` (replace `<MOD_ID>` accordingly) and delete the `taint` file located there. Then run the updater (option 1) and the mod will be re-downloaded and re-installed.  

## Usage
Your mod.io API key needs to go in an AUTH_TOKEN file in the same folder as this program. Instructions curtesy of [RainOrigami's repo](https://github.com/RainOrigami/DownloadPavlovMapsFromModIo):

1. Go to https://mod.io/me/access
2. Under OAuth Access, enter any name (eg. Pavlov) and press Create
3. Now enter any name for the token (eg. Pavlov), choose Read from the dropdown, and press the + button
4. "TOKEN CREATED" will appear and you can copy that token using the copy button on the left side of the text field

Then run `python ./update.py` and select what your want to do from the prompts. An example of what this looks like is provided below.
```
PS C:\Users\USERNAME\git\pavlov-mod-manager> .\update.py
Select an operation (default is 1):
[1] Update all installed mods
[2] Download missing subscribed mods
[3] Do 1 then 2
[4] List currently installed mods
[5] List currently subscribed mods
[0] Exit
Select: 1


Reading mods from disk (C:\Users\USERNAME\AppData\Local\Pavlov\Saved\Mods)
Total local mods identified: 75

Retrieving online info about local mods, this may take a moment...

Mod Name                  Mod ID       Status
----------------------------------------------
Gravity                   2773760      Up to date
Tuscan 2022               2788214      Up to date
Pipes                     2788277      Up to date
de_basalt                 2803820      Up to date
MW3: Dome                 2804210      Update available, adding to queue
...
[truncated for brevity]
...
Yantar Facility           3560062      Update available, adding to queue
Battery                   3564015      Up to date
Crash                     3568020      Up to date
Train CSGO                3624316      Up to date
de_defcon (WIP)           3649233      Up to date

4 mods queued for update
Updating MW3: Dome (ID 2804210), downloading 152.6 MB...
Download complete, installing...
Done!

Updating Vertigo [CSGO] (ID 3188315), downloading 821.3 MB...
Download complete, installing...
Done!

Updating Pripyat CSGO (ID 3231288), downloading 423.7 MB...
Download complete, installing...
Done!

Updating Yantar Facility (ID 3560062), downloading 330.8 MB...
Download complete, installing...
Done!

Local mod updates complete!

PS C:\Users\USERNAME\git\pavlov-mod-manager>
```

## Uh, why does this exist when several other repos do the same thing?
Because I like Python better than having to rely on .net or other dependencies. Eventually I'll use PyInstaller to generate a nice standalone executable that can be published in a release so you won't even have to have have Python installed to run this.

Also, I wanted to improve on existing projects (like presenting options in a menu format instead of CLI arguments), but couldn't find a project that was written in Python or another language I like.
