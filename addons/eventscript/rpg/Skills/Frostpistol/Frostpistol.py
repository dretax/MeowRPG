# Frostpistol-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import es
import gamethread

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Frostpistol'
 
        
def unload():
    for i in playerlist.GetPlayerlist():
        gamethread.cancelDelayed('rpg_%s_%s' %(skillname, i.userid))
        rpg_unfrost(i)
    
    
def player_hurt(ev):    
    if ev['weapon'] in ('usp', 'glock', 'p228', 'deagle', 'fiveseven', 'elite'):
        # Get level of that skill and playerlib instance of the victim
        level = playerlist[ev['attacker']].GetSkillLevel(skillname)
        userid = int(ev['userid'])
        player = playerlist[userid].player        
        if level > 0:
            # Set delayname         
            delayname = 'rpg_%s_%s' %(skillname,userid)      
            # Set speed
            if ev['weapon'] in ('usp', 'glock', 'p228'):
                player.setSpeed(0.4)  
            else:
                player.setSpeed(0.6)  
            # Set delay                    
            gamethread.cancelDelayed(delayname)
            gamethread.delayedname(level, delayname, rpg_unfrost, userid)                                                              
                    
                    
def player_death(ev):
    gamethread.cancelDelayed('rpg_%s_%s' %(skillname, ev['userid']))
            
            
def player_disconnect(ev):
    gamethread.cancelDelayed('rpg_%s_%s' %(skillname, ev['userid']))
            
            
def rpg_unfrost(userid):
    playerlist[userid].player.setSpeed(1)  