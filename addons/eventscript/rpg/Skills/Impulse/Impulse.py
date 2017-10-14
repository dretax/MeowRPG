# Impulse-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import gamethread

# RPG-Imports
from rpg.rpg import playerlist, skillhandler


# Script
skillname = 'Impulse'


def unload():
    for i in playerlist.GetPlayerlist():
        gamethread.cancelDelayed('rpg_%s_%s' %(skillname, i.userid))
        rpg_repulse(i)


def player_hurt(ev):
    if (ev['weapon'] not in ('usp', 'glock', 'p228', 'deagle', 'fiveseven', 'elite') or not skillhandler.IsLoaded('Frostpistol') or (ev['weapon'] in ('usp', 'glock', 'p228', 'deagle', 'fiveseven', 'elite') and playerlist[ev['attacker']].GetSkillLevel('Frostpistol') == 0)) and ev['weapon'] != 'knife' and int(ev['attacker']) != 0:
        # Get userid, level of this skill and playelib instance
        userid = int(ev['userid'])   
        player = playerlist[userid]
        level = player.GetSkillLevel(skillname)
        player = player.player
        # Set speed
        player.setSpeed(1 + 0.2 * level)
        # Set ammo
        try:
            player.setPrimaryClip(int(player.getClip('1')) + level)
        except:
            pass
        try:   
            player.setSecondaryClip(int(player.getClip('2')) + level)
        except:
            pass 
        # Delay
        delayname = 'rpg_%s_%s' %(skillname, userid)
        gamethread.cancelDelayed(delayname)
        gamethread.delayedname(1, delayname, rpg_repulse, (userid))
                
                
def player_death(ev):
    gamethread.cancelDelayed('rpg_%s_%s' %(skillname, ev['userid']))
            
            
def player_disconnect(ev):
    gamethread.cancelDelayed('rpg_%s_%s' %(skillname, ev['userid']))
        
                
def rpg_repulse(userid):
    playerlist[userid].player.setSpeed(1)  