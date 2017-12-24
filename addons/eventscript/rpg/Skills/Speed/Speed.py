# Speed-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Speed'


# Load config values
rpgSpeedValue = config.GetFloat('rpgSpeedValue')


# Events
def unload():
    for i in playerlist.GetPlayerlist():
        i.player.setSpeed(1.0)
        try:
            del i.properties['speed']
        except:
            pass
         
        
def rpg_player_spawn(ev):
    player = playerlist[ev['userid']]
    speed = 1 + player.GetSkillLevel(skillname) * rpgSpeedValue
    player.player.setSpeed(speed) 
    player.properties['speed'] = speed 
    
    
def rpg_skill_level_changed(ev):
    if ev['skill'] == skillname:   
        player = playerlist[ev['userid']]
        speed = 1 + player.GetSkillLevel(skillname) * rpgSpeedValue
        player.player.setSpeed(speed) 
        player.properties['speed'] = speed