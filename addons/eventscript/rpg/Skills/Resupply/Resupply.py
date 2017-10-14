# Resupply-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import playerlib
import gamethread

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Resupply'

def unload():
    gamethread.cancelDelayed('rpg_%s' %(skillname))    

def round_start(ev):
    gamethread.delayedname(3.0, 'rpg_%s' %(skillname), rpg_resupply, ())
    
def round_end(ev):
    gamethread.cancelDelayed('rpg_%s' %(skillname)) 
    
def rpg_resupply(): 
    gamethread.delayedname(3.0, 'rpg_%s' %(skillname), rpg_resupply, ())   
    for i in playerlib.getUseridList('#alive'):
        # Get level of that skill and playerlib instance
        player = playerlist[i]
        level = player.GetSkillLevel(skillname)
        player = player.player
        try:
            player.setPrimaryAmmo(player.getAmmo('1') + level)
        except:
            pass 
        try:
            player.setSecondaryAmmo(player.getAmmo('2') + level) 
        except:
            pass 