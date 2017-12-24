# Impulse-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import weaponlib
import gamethread

# RPG-Imports
from meowrpg import playerlist, skillhandler, config



# Script
skillname = 'Impulse'


# Load config values
rpgImpulseSpeed = config.GetFloat('rpgImpulseSpeed') 
rpgImpulseAmmo = config.GetInt('rpgImpulseAmmo')
rpgImpulseActiveOnly = config.GetBool('rpgImpulseActiveOnly')


# Events    
def unload():
    for i in playerlist.GetPlayerlist():
        gamethread.cancelDelayed('rpg_%s_%s' %(skillname, i.userid))
        rpg_repulse(i.userid)


def player_hurt(ev):
    if (ev['weapon'] not in ('usp', 'glock', 'p228', 'deagle', 'fiveseven', 'elite') or not skillhandler.IsLoaded('Frostpistol') or (ev['weapon'] in ('usp', 'glock', 'p228', 'deagle', 'fiveseven', 'elite') and playerlist[ev['attacker']].GetSkillLevel('Frostpistol') == 0)) and ev['weapon'] != 'knife' and int(ev['attacker']) != 0:
        # Get userid, level of this skill and playelib instance
        userid = int(ev['userid'])   
        player = playerlist[userid]
        level = player.GetSkillLevel(skillname)
        # Set speed
        player.player.setSpeed(player.properties['speed'] + rpgImpulseSpeed * level)
        player = player.player
        # Set ammo
        if rpgImpulseActiveOnly:
            activeWeapon = es.entitygetvalue(es.getindexfromhandle(es.getplayerprop(userid, "CBasePlayer.baseclass.m_hActiveWeapon")), "classname")
            if activeWeapon in weaponlib.getWeaponList('#primary'):
                try:
                    player.setPrimaryClip(int(player.getClip('1')) + level * rpgImpulseAmmo)
                except:
                    pass 
            elif activeWeapon in weaponlib.getWeaponList('#secondary'): 
                try:   
                    player.setSecondaryClip(int(player.getClip('2')) + level * rpgImpulseAmmo)
                except:
                    pass      
        else:
            try:
                player.setPrimaryClip(int(player.getClip('1')) + level * rpgImpulseAmmo)
            except:
                pass
            try:   
                player.setSecondaryClip(int(player.getClip('2')) + level * rpgImpulseAmmo)
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
    player = playerlist[userid]
    player.player.setSpeed(player.properties['speed'])  