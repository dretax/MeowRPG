# Respawn-Skill by Rennnyyy
#
# Version 1.0


# Imports

# Python-Imports
import random

# ES-Imports
import es
import gamethread

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Respawn'


def load():
    global allowed
    allowed = False


def round_start(ev):
    global allowed
    allowed = True
    
    
def round_end(ev):
    global allowed
    allowed = False
           
             
def player_death(ev):
    userid = int(ev['userid'])
    level = playerlist[userid].GetSkillLevel(skillname)
    if allowed and level > 0:
        if random.randint(1,100) <= level * 5:
            gamethread.delayed(1, rpg_respawn, (userid))
        
        
def rpg_respawn(userid):
    if allowed:
        es.setplayerprop(userid, 'CCSPlayer.m_iPlayerState', 0)
        es.setplayerprop(userid, 'CCSPlayer.baseclass.m_lifeState', 512)
        es.server.queuecmd('es_spawnplayer %s' % userid)   