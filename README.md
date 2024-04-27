# Pavlov Mod Updater
Keep your Pavlop mods from Mod.io up to date on Windows. Only tested on Windows with the Steam game. Seems to work well for map and non-map mods.

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

There's also a `SETTINGS.json` file that contains a few things you can tweak, including the folder where your mods are location if they aren't in the default location. For most people the defaults should be fine.

Run `python ./update.py` and select what your want to do from the prompts. An example of what this looks like is provided below.
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
Total local mods identified: 102

Retrieving online info about 102 local mods...

Mod Name                                           Mod ID     Size       Status
-------------------------------------------------------------------------------
Gravity                                           2773760    13.0 MB    Up to date
Tuscan 2022                                       2788214    1.6 GB     Up to date
Pipes                                             2788277    868.0 MB   Up to date
de_basalt                                         2803820    954.7 MB   Up to date
MW3: Dome                                         2804210    151.6 MB   Up to date
McDonalds                                         2804322    223.7 MB   Up to date
Dust 2 CSGO                                       2804502    774.4 MB   Up to date
Stash House                                       2810348    387.8 MB   Up to date
Atlas                                             2811148    346.7 MB   Up to date
007 Casino Royale                                 2814416    195.6 MB   Update available
...
[truncated for brevity]
...
BananaGun                                         3931603    5.8 MB     Update available
[MOD] Modify Items                                3943563    9.5 KB     Up to date

12 mods need updates

[1/12] Updating 007 Casino Royale (ID 2814416), downloading 195.6 MB...
Download complete, installing...
Done!

...
[truncated for brevity]
...

[12/12] Updating BananaGun (ID 3931603), downloading 5.8 MB...
Download complete, installing...
Done!

Local mod updates complete!

PS C:\Users\USERNAME\git\pavlov-mod-manager>
```

## Uh, why does this exist when several other repos do the same thing?
Because I like Python better than having to rely on .net or other dependencies. Eventually I'll use PyInstaller to generate a nice standalone executable that can be published in a release so you won't even have to have Python installed to run this.

Also, I wanted to improve on existing projects (like presenting options in a menu format instead of CLI arguments), but couldn't find a project that was written in Python or another language I like.
