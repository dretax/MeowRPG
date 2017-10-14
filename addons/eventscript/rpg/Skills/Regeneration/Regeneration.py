# Regeneration-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import playerlib
import gamethread

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Regeneration'
        
def unload():
    gamethread.cancelDelayed('rpg_%s' %(skillname))    

def round_start(ev):
    gamethread.delayedname(3.0, 'rpg_%s' %(skillname), rpg_regeneration, ())
    
def round_end(ev):
    gamethread.cancelDelayed('rpg_%s' %(skillname)) 
        
def rpg_regeneration():
    gamethread.delayedname(3.0, 'rpg_%s' %(skillname), rpg_regeneration, ())
    for i in playerlib.getPlayerList('#alive'):
        # Get the player's maxhealth, level of this skill and it's playerlib instance
        player = playerlist[i]
        level = player.GetSkillLevel(skillname)
        maxHealth = player.properties['maxhealth'] 
        player = player.player
      
        # Calculate new hp and set it 
        hp = player.getHealth() + level
        if hp < maxHealth:
            player.setHealth(hp)  
        else:
            player.setHealth(maxHealth)   