# Gravity-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Gravity'


def load():
    es.loadevents('declare', 'addons/eventscripts/rpg/Includes/rpg_events.res')
    es.loadevents('addons/eventscripts/rpg/Includes/rpg_events.res') 


def unload():
    for i in playerlist.GetPlayerlist():
        es.server.queuecmd('es_fire %s !self addoutput "gravity 1"' %(i.userid))  
        
        
def es_map_start(ev):
    es.loadevents('addons/eventscripts/rpg/Includes/rpg_events.res')    
        
        
def player_spawn(ev):
    player = playerlist[ev['userid']]
    es.server.queuecmd('es_fire %s !self addoutput "gravity %s"' %(player.userid, 1 - player.GetSkillLevel(skillname) * 0.05))   
    

def rpg_skill_level_changed(ev):
    if ev['skill'] == skillname:
        es.server.queuecmd('es_fire %s !self addoutput "gravity %s"' %(ev['userid'], 1 - int(ev['level']) * 0.05))          