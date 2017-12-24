# Stealth-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Stealth'


# Load config values
rpgStealthValue = config.GetFloat('rpgStealthValue')


# Events
def unload():
    for i in playerlist.GetPlayerlist():
        i.player.setColor(255,255,255,255)
        try:
            del i.properties['color']
        except:
            pass
         
        
def rpg_player_spawn(ev):
    player = playerlist[ev['userid']]
    alpha = (1 - player.GetSkillLevel(skillname) * rpgStealthValue) * 255
    player.player.setColor(255,255,255,alpha) 
    player.properties['color'] = (255,255,255,alpha)     
    
    
def rpg_skill_level_changed(ev):
    if ev['skill'] == skillname:   
        player = playerlist[ev['userid']]
        alpha = (1 - int(ev['level']) * rpgStealthValue) * 255
        player.player.setColor(255,255,255,alpha)
        player.properties['color'] = (255,255,255,alpha) 