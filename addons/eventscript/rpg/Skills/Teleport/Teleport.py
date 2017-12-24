# Teleport-Skill by *meow*
#
# Version 1.0


# Imports

# Python-Imports
import time

# ES-Imports
import es
import gamethread
import effectlib

# RPG-Imports
from meowrpg import playerlist, config, tell



# Script
skillname = 'Teleport'


# Load config values
rpgTeleportValue = config.GetInt('rpgTeleportValue')
rpgTeleportTime = config.GetFloat('rpgTeleportTime')
rpgTeleportInterval = config.GetInt('rpgTeleportInterval')
rpgTeleportEffects = config.GetBool('rpgTeleportEffects')
rpgTeleportSetcommand = config.GetList('rpgTeleportSetcommand')
rpgTeleportCommand = config.GetList('rpgTeleportCommand')


# Global variables
teleportStore = {}
teleporting = set()
teleportingAllowed = False


# Classes
class TeleportStore(object):
    def __init__(self):
        self.last = 0
        self.amount = 0
        self.pos = None


# Events
def es_map_start(ev):
    teleportStore.clear()  
    
    
def round_start(ev):
    global teleportingAllowed
    teleportingAllowed = True   
    
    
def round_end(ev):
    global teleportingAllowed
    teleportingAllowed = False
    for i in teleporting:
        gamethread.cancelDelayed('rpg_teleport_%s' %(i))
        es.setplayerprop(i, 'CBaseEntity.movetype', 2)
    teleporting.clear()
    

def player_say(ev):
    text = ev['text'].lower()
    userid = int(ev['userid'])
    if text in rpgTeleportSetcommand:
        if not bool(es.getplayerprop(userid, "CCSPlayer.baseclass.pl.deadflag")):        
            if userid not in teleportStore:
                teleportStore[userid] = TeleportStore()   
            teleportStore[userid].pos = es.getplayerlocation(userid) 
            tell(userid, 'Teleport target set')
        else:
            tell(userid, 'You cannot set the teleport target when you are dead')
    elif text in rpgTeleportCommand:
        if teleportingAllowed and (not bool(es.getplayerprop(userid, "CCSPlayer.baseclass.pl.deadflag"))) and userid in teleportStore and playerlist[userid].GetSkillLevel(skillname) * rpgTeleportValue > teleportStore[userid].amount and userid not in teleporting and time.time() - teleportStore[userid].last >= rpgTeleportInterval:
            rpg_teleport(userid)
        elif userid not in teleportStore:
            tell(userid, 'You must set a teleport target first')
        elif playerlist[userid].GetSkillLevel(skillname) * rpgTeleportValue <= teleportStore[userid].amount:
            tell(userid, 'You have already reached the maximum teleports on this map')
        elif time.time() - teleportStore[userid].last < rpgTeleportInterval:
            tell(userid, 'You have to wait %s seconds until you can teleport again' %(rpgTeleportInterval - int(time.time() - teleportStore[userid].last)))        
        elif not teleportingAllowed:
            tell(userid, 'You cannot teleport when the round is over')
        elif bool(es.getplayerprop(userid, "CCSPlayer.baseclass.pl.deadflag")):
            tell(userid, 'You cannot teleport when you are dead')
        
                     
def player_hurt(ev):
    userid = int(ev['userid'])
    if userid in teleporting:
        gamethread.cancelDelayed('rpg_teleport_%s' %(userid))
        es.setplayerprop(userid, 'CBaseEntity.movetype', 2)
        teleporting.remove(userid)
        tell(userid, 'Teleport aborted')
        
        
def rpg_teleport(userid):
    tell(userid, 'Teleporting in %s seconds' %(rpgTeleportTime))
    teleporting.add(userid)
    name = 'rpg_teleport_%s' %(userid)
    es.setplayerprop(userid, 'CBaseEntity.movetype', 0)
    
    if rpgTeleportEffects:  
        x,y,z = es.getplayerlocation(userid)
        z += 40   
        pX, pY, pZ = teleportStore[userid].pos
        pZ += 40 
        if es.getplayerteam(userid) == 2:               
            for i in xrange(rpgTeleportTime * 10):
                move = int(30 / (rpgTeleportTime * 10) * i)
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((x,y,z), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 255, 0, 0))
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((x,y,z+move), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 255, 0, 0))
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((x,y,z-move), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 255, 0, 0))
        
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((pX,pY,pZ), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 255, 0, 0))
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((pX,pY,pZ+move), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 255, 0, 0))
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((pX,pY,pZ-move), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 255, 0, 0))
        else:
            for i in xrange(rpgTeleportTime * 10):
                move = int(30 / (rpgTeleportTime * 10) * i)
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((x,y,z), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 0, 0, 255))
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((x,y,z+move), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 0, 0, 255))
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((x,y,z-move), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 0, 0, 255))
        
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((pX,pY,pZ), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 0, 0, 255))
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((pX,pY,pZ+move), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 0, 0, 255))
                gamethread.delayedname(i * 0.1, name, effectlib.drawCircle, ((pX,pY,pZ-move), 30, 5, (1,0,0), (0,1,0), None, "materials/sprites/laser.vmt", "materials/sprites/halo01.vmt", 0.1, 10, 10, 0, 0, 255))         
            
    gamethread.delayedname(rpgTeleportTime, name, teleporting.remove, userid)
    gamethread.delayedname(rpgTeleportTime + 0.1, name, rpg_do_teleport, (userid))
    

def rpg_do_teleport(userid):  
    store = teleportStore[userid] 
    store.last = time.time()
    store.amount += 1
    playerlist[userid].player.setLocation(list(store.pos))
    es.setplayerprop(userid, 'CBaseEntity.movetype', 2)
    tell(userid, 'Teleported')