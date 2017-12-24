# Resupply-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import playerlib
import gamethread

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Resupply'


# Load config values
rpgResupplyAmmo = config.GetInt('rpgResupplyAmmo') 
rpgResupplyActiveOnly = config.GetBool('rpgResupplyActiveOnly') 
rpgResupplyInterval = config.GetFloat('rpgResupplyInterval') 


# Events  
def unload():
    gamethread.cancelDelayed('rpg_%s' %(skillname))    

def round_start(ev):
    gamethread.delayedname(rpgResupplyInterval, 'rpg_%s' %(skillname), rpg_resupply, ())
    
def round_end(ev):
    gamethread.cancelDelayed('rpg_%s' %(skillname)) 
    
def rpg_resupply(): 
    gamethread.delayedname(rpgResupplyInterval, 'rpg_%s' %(skillname), rpg_resupply, ())   
    for i in playerlib.getUseridList('#alive'):
        # Get level of that skill and playerlib instance
        player = playerlist[i]
        level = player.GetSkillLevel(skillname)
        player = player.player
        if rpgResupplyActiveOnly:
            activeWeapon = es.entitygetvalue(es.getindexfromhandle(es.getplayerprop(userid, "CBasePlayer.baseclass.m_hActiveWeapon")), "classname")
            if activeWeapon in weaponlib.getWeaponList('#primary'):
                try:
                    player.setPrimaryAmmo(player.getAmmo('1') + level * rpgResupplyAmmo)
                except:
                    pass 
            elif activeWeapon in weaponlib.getWeaponList('#secondary'): 
                try:   
                    player.setSecondaryAmmo(player.getAmmo('2') + level * rpgResupplyAmmo) 
                except:
                    pass 
        else:
            try:
                player.setPrimaryAmmo(player.getAmmo('1') + level * rpgResupplyAmmo)
            except:
                pass 
            try:
                player.setSecondaryAmmo(player.getAmmo('2') + level * rpgResupplyAmmo) 
            except:
                pass 