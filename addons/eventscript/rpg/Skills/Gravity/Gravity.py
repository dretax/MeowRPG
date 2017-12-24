# Gravity-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Gravity'


# Load config values
rpgGravityValue = config.GetFloat('rpgGravityValue') 


# Events
def unload():
    for i in playerlist.GetPlayerlist():
        es.server.queuecmd('es_fire %s !self addoutput "gravity 1"' %(i.userid))   
        
        
def rpg_player_spawn(ev):
    player = playerlist[ev['userid']]
    es.server.queuecmd('es_fire %s !self addoutput "gravity %s"' %(player.userid, 1 - player.GetSkillLevel(skillname) * rpgGravityValue))   
    

def rpg_skill_level_changed(ev):
    if ev['skill'] == skillname:
        es.server.queuecmd('es_fire %s !self addoutput "gravity %s"' %(ev['userid'], 1 - int(ev['level']) * rpgGravityValue))          