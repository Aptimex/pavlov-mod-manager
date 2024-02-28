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

## Uh, why does this exist when several other repos do the same thing?
Because I like Python better than having to rely on .net or other dependencies. Eventually I'll use PyInstaller to generate a nice standalone executable that can be published in a release so you won't even have to have have Python installed to run this.

Also, I wanted to improve on existing projects (like presenting options in a menu format instead of CLI arguments), but couldn't find a project that was written in Python or another language I like. 
