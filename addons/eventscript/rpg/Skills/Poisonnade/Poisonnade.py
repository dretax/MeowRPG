# Poisonnade-Skill by *meow*
#
# Version 1.0


# Imports

#Python-Imports
import math

# ES-Imports
import es
import playerlib
import gamethread

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Poisonnade'


# Load config values
rpgPoisonnadeValue = config.GetInt('rpgPoisonnadeValue')  
rpgPoisonnadeInterval = config.GetFloat('rpgPoisonnadeInterval')


# Global variables
nades = []


# Events
def unload():
    gamethread.cancelDelayed('rpg_%s' %(skillname))    


def round_start(ev):
    gamethread.delayedname(rpgPoisonnadeInterval, 'rpg_%s' %(skillname), rpg_poison, ())
    
    
def round_end(ev):
    gamethread.cancelDelayed('rpg_%s' %(skillname)) 
    del nades[:]

   
def smokegrenade_detonate(ev): 
    userid = ev['userid']
    level = playerlist[userid].GetSkillLevel(skillname)
    if level > 0:
        team = int(ev['es_userteam'])
        save = (float(ev['x']), float(ev['y']), float(ev['z']), team, level) 
        nades.append(save)
        gamethread.delayed(19.0, rpg_remove_poison, (save,))
        
        # Make the smoke colourfull
        index = es.createentity("light_dynamic","mylight%s" % userid)
        es.entitysetvalue(index, "angles", "-90 0 0")
        if team == 3:
            es.entitysetvalue(index,"_light", "0 0 255")
        elif team == 2:
            es.entitysetvalue(index,"_light", "255 0 0")
        es.entitysetvalue(index, "_inner_cone","-89")
        es.entitysetvalue(index, "_cone","-89")
        es.entitysetvalue(index, "pitch","-90")
        es.entitysetvalue(index, "distance","256")
        es.entitysetvalue(index, "spotlight_radius","96")
        es.entitysetvalue(index, "origin","%s %s %s"% (ev['x'], ev['y'], ev['z']))
        es.entitysetvalue(index, "brightness","5")
        es.entitysetvalue(index, "style","6")
        es.entitysetvalue(index, "spawnflags","1")
        es.spawnentity(index)
        gamethread.delayed(20.0, es.remove, index)
        es.server.queuecmd('es_xfire %s mylight%s DisableShadow' % (userid,userid))
        es.server.queuecmd('es_xfire %s mylight%s addoutput "OnUser1 !self,kill,-1,24"' %  (userid,userid))
        es.server.queuecmd('es_xfire %s mylight%s addoutput "OnUser2 !self,Toggle,-1,21"' %  (userid,userid))
        es.server.queuecmd('es_xfire %s mylight%s addoutput "OnUser3 !self,TurnOff,-1,23"' %  (userid,userid))
        es.server.queuecmd('es_xfire %s mylight%s addoutput "OnUser4 !self,spawnflags,3,19"' %  (userid,userid))            
          
    
def rpg_poison():
    gamethread.delayedname(rpgPoisonnadeInterval, 'rpg_%s' %(skillname), rpg_poison, ())
    for i in nades:
        x = i[0]
        y = i[1]
        z = i[2]
        team = i[3]
        damage = i[4] * rpgPoisonnadeValue
        if team == 2:
            for j in playerlib.getUseridList('#ct, #alive'):
                xp, yp, zp = es.getplayerlocation(j)
                zp += 68 #the head is 68 units above a players feet
                # Inside the smoke
                if math.sqrt((xp-x)**2 + (yp-y)**2 + (zp-z)**2) <= 170:
                    es.server.queuecmd('damage %s %s' %(j, damage))
        elif team == 3:
            for j in playerlib.getUseridList('#t, #alive'):
                xp, yp, zp = es.getplayerlocation(j)
                # Inside the smoke
                if math.sqrt((xp-x)**2 + (yp-y)**2 + (zp-z)**2) <= 170:
                    es.server.queuecmd('damage %s %s' %(j, damage))
                                    
    
    
def rpg_remove_poison(save):
    try:
        nades.remove(save)
    except:
        pass 