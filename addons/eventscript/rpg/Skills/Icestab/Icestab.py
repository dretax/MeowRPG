# Icestab-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import es
import gamethread

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Icestab'

       
def unload():
    for i in playerlist.GetPlayerlist():
        gamethread.cancelDelayed('rpg_%s_%s' %(skillname, i.userid))
        rpg_unfreeze(i)
    
    
def player_hurt(ev):
    if ev['weapon'] == 'knife' and int(ev['dmg_health']) >= 35:  
        player = playerlist[ev['attacker']]
        level = player.GetSkillLevel(skillname)
        if level > 0 and es.getplayerprop(player.userid, 'CBaseEntity.movetype') != 0:
            # Freeze the player
            player = playerlist[ev['userid']]
            userid = player.userid
            es.setplayerprop(userid, 'CBaseAnimating.m_nHitboxSet', 2)
            es.setplayerprop(userid, 'CBaseEntity.movetype', 0) 
            player.player.setColor(0,0,255,125)
            # Delay
            delayname = 'rpg_%s_%s' %(skillname, userid)
            gamethread.cancelDelayed(delayname)
            gamethread.delayedname(level, delayname, rpg_unfreeze, (player.userid))  
                    
                
def player_death(ev):
    player = playerlist[ev['userid']]
    es.setplayerprop(player.userid, 'CBaseAnimating.m_nHitboxSet', 0)
    player.player.setColor(*player.properties['colour'])
    gamethread.cancelDelayed('rpg_%s_%s' %(skillname, player.userid))
   
        
                
def rpg_unfreeze(userid):  
    player = playerlist[userid]
    es.setplayerprop(player.userid, 'CBaseAnimating.m_nHitboxSet', 0)
    es.setplayerprop(userid, 'CBaseEntity.movetype', 2)
    player.player.setColor(*player.properties['colour']) 