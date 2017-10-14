# Health-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Health'


def load():
    es.loadevents('declare', 'addons/eventscripts/rpg/Includes/rpg_events.res')
    es.loadevents('addons/eventscripts/rpg/Includes/rpg_events.res') 


def unload():
    for i in playerlist.GetPlayerlist():
        del i.properties['maxHealth']
        
        
def es_map_start(ev):
    es.loadevents('addons/eventscripts/rpg/Includes/rpg_events.res') 


def player_spawn(ev):
    # Get player and his maximal health
    player = playerlist[ev['userid']]
    maxHealth = 100 + player.GetSkillLevel(skillname) * 25
    
    # Set the player's "maxhealth" property (used by medic, regeneration and shop)   
    player.properties['maxhealth'] = maxHealth 
    player.player.setHealth(maxHealth)
    

def rpg_skill_level_changed(ev):
    if ev['skill'] == skillname:
        playerlist[ev['userid']].properties['maxhealth'] += (int(ev['level']) - int(ev['old_level'])) * 25