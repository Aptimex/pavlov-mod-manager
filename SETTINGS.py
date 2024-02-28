modPath = "%localappdata%\\Pavlov\\Saved\\Mods"
PLATFORM = "windows"
THREADS = 10 #How many concurrent download streams to use

#Don't attempt to download/update these mod IDs
#Useful for some mods we can't manually install due to corrupted ZIP files, but that Pavlov can somehow still install
#example: IGNORE = [1234567, 7654321]
IGNORE = [3051820] #this one has issues
