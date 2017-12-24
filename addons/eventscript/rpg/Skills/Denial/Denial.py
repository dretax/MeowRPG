# Denial-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import es
import playerlib
import gamethread
import weaponlib

# RPG-Imports
from meowrpg import playerlist


# Script
skillname = 'Denial'


# Global variables
weaponList = {}
allowChange = []


def load():
    es.ServerVar('eventscripts_noisy').set('1')
    es.addons.registerClientCommandFilter(clientFilter)     
    
    
def unload():
    es.addons.unregisterClientCommandFilter(clientFilter)
    
    
def es_map_start(ev):
    weaponList.clear()
    del allowChange[:] 
    

def rpg_player_spawn(ev):
    userid = int(ev['userid'])
    player = playerlist[userid]
    level = player.GetSkillLevel(skillname) 
    player = player.player
    
    # Give old weapons!
    if userid in weaponList.keys() and level > 0:
        # Strip the player
        if level > 1:
            hasC4 = player.hasC4()
        
            es.server.queuecmd('es_give %s player_weaponstrip' %(userid))    
            es.server.queuecmd('es_fire %s player_weaponstrip strip' %(userid))
        
            es.server.queuecmd('es_give %s weapon_knife' %(userid))    
        
            if hasC4:
                es.server.queuecmd('es_give %s weapon_c4' %(userid))
       
        giveBack = weaponList[userid]
        for i in giveBack.keys():
            if i == 'items':
                for j in giveBack[i]:
                    if j == 'weapon_vest':
                        gamethread.delayed(0.1, es.server.queuecmd, ('es_give %s item_kevlar' %(userid)))
                    elif j == 'weapon_vesthelm':
                        gamethread.delayed(0.1, es.server.queuecmd, ('es_give %s item_assaultsuit' %(userid)))
                    else:
                        gamethread.delayed(0.1, es.server.queuecmd, ('es_give %s %s' %(userid, j)))   
            elif i == 'secondary' and level >= 2:
                gamethread.delayed(0.1, es.server.queuecmd, ('es_give %s %s' %(userid, giveBack[i])))    
            elif i == 'primary' and level >= 3:
                gamethread.delayed(0.1, es.server.queuecmd, ('es_give %s %s' %(userid, giveBack[i])))    
                        
    
    # Reset weapon list
    weaponList[userid] = {}
    weaponList[userid]['items'] = []
    
    allowChange.append(userid)
    
    gamethread.delayed(0.5, get_weapons, (userid))
    
        
def round_end(ev):
    del allowChange[:]
    
    
def weapon_fire(ev):
    if ev['weapon'] in ('flashbang', 'smokegrenade', 'hegrenade'):
        weaponList[int(ev['userid'])]['items'].remove('weapon_%s' %(ev['weapon']))
    
    
def item_pickup(ev):
    userid = int(ev['userid'])
    if userid in allowChange:
        item = 'weapon_%s' %(ev['item'])
        if item not in ('weapon_knife', 'weapon_c4'):
            if item in weaponlib.getWeaponList('#primary'):
                weaponList[userid]['primary'] = item
            elif item in weaponlib.getWeaponList('#secondary'):
                weaponList[userid]['secondary'] = item
            else:
                if not item == 'weapon_defuser':
                    weaponList[userid]['items'].append(item)
                else:
                    weaponList[userid]['items'].append('item_defuser')   


def clientFilter(userid, args):
    if args[0].lower() == 'drop':
        weapon = es.createplayerlist(userid)[userid]['weapon']
        if weapon not in ('weapon_knife', 'weapon_flashbang', 'weapon_smokegrenade', 'weapon_hegrenade'):
            if weapon in weaponlib.getWeaponList('#primary'):
                del weaponList[int(userid)]['primary']
            elif weapon in weaponlib.getWeaponList('#secondary'):
                del weaponList[int(userid)]['secondary']  
    return True


def get_weapons(userid):
    # Get weapons a player holds
    player = playerlib.getPlayer(userid)
    
    weapons = weaponList[userid]    
    tmp = player.getSecondary()
    if tmp != '0':
        weapons['secondary'] = tmp
    tmp = player.getPrimary()
    if tmp != '0':  
        weapons['primary'] = tmp
    # Get greandes
    weapons['items'] = []
    items = weapons['items']
    for i in xrange(int(player.getHE())):
        items.append('weapon_hegrenade')
    for i in xrange(int(player.getFB())):
        items.append('weapon_flashbang')
    for i in xrange(int(player.getSG())):
        items.append('weapon_smokegrenade')
    if bool(int(player.hasNightvision())):
        items.append('weapon_nvgs')
    if bool(int(player.hasDefuser())):
        items.append('item_defuser') 