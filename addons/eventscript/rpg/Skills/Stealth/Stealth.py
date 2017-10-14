# Stealth-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import es
import playerlib

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Stealth'


def load():
    es.loadevents('declare', 'addons/eventscripts/rpg/Events/rpg_events.res')
    es.loadevents('addons/eventscripts/rpg/Events/rpg_events.res') 


def unload():
    for i in playerlist.GetPlayerlist():
        i.player.setColor(255,255,255,255)
        del i.properties['colour']
        
        
def es_map_start(ev):
    es.loadevents('addons/eventscripts/rpg/Events/rpg_events.res')
         
        
def player_spawn(ev):
    player = playerlist[ev['userid']]
    player.player.setColor(255,255,255,255 - player.GetSkillLevel(skillname)*40) 
    player.properties['color'] = (255,255,255,255 - player.GetSkillLevel(skillname)*40)     
    
    
def rpg_skill_level_changed(ev):
    if ev['skill'] == skillname:    
        playerlib.getPlayer(ev['userid']).setColor(255,255,255,255 - int(ev['level'])*40) 
        playerlist[ev['userid']].properties['colour'] = (255,255,255,255 - player.GetSkillLevel(skillname)*40)  