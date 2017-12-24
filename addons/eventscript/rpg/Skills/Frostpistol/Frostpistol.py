# Frostpistol-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import es
import gamethread

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Frostpistol'


# Load config values
rpgFrostpistolTime = config.GetInt('rpgFrostpistolTime')  
rpgFrostpistolEffect = {'usp' : config.GetFloat('rpgFrostpistolUsp'), 
                        'glock' : config.GetFloat('rpgFrostpistolGlock'),
                        'p228' : config.GetFloat('rpgFrostpistolP228'),
                        'deagle' : config.GetFloat('rpgFrostpistolDeagle'),
                        'fiveseven' : config.GetFloat('rpgFrostpistolFiveseven'),
                        'elite' : config.GetFloat('rpgFrostpistolElite')}
  
  
# Events      
def unload():
    for i in playerlist.GetPlayerlist():
        gamethread.cancelDelayed('rpg_frostpistol_%s' %(i.userid))
        rpg_unfrost(i.userid)
    
    
def player_hurt(ev):    
    if ev['weapon'] in ('usp', 'glock', 'p228', 'deagle', 'fiveseven', 'elite'):
        # Get level of that skill and playerlib instance of the victim
        level = playerlist[ev['attacker']].GetSkillLevel(skillname)
        userid = int(ev['userid'])
        player = playerlist[userid]        
        if level > 0:
            # Set delayname         
            delayname = 'rpg_frostpistol_%s' %(userid)      
            # Set speed
            player.player.setSpeed(player.properties['speed'] - rpgFrostpistolEffect[ev['weapon']])                 
            # Set delay                    
            gamethread.cancelDelayed(delayname)
            gamethread.delayedname(level, delayname, rpg_unfrost, userid)                                                              
                    
                    
def player_death(ev):
    gamethread.cancelDelayed('rpg_frostpistol_%s' %(ev['userid']))
            
            
def player_disconnect(ev):
    gamethread.cancelDelayed('rpg_frostpistol_%s' %(ev['userid']))
            
            
def rpg_unfrost(userid):
    player = playerlist[userid]
    player.player.setSpeed(player.properties['speed'])  