# Stealth-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Stunnade'


stun = []


def player_blind(ev):
    stun.append(ev['userid'])
    playerlist[ev['userid']].player.flash(0, 0)
   
   
def flashbang_detonate(ev):  
    level = playerlist[ev['userid']].GetSkillLevel(skillname)
    team = 5 - int(ev['es_userteam'])      
    if level > 0:
        time = level * 2
        power = level * 100
        for i in stun:
            if int(es.getplayerteam(i)) == team:
                es.usermsg('create', 'shake', 'Shake')
                es.usermsg('write',  'byte',  'shake', 0)
                es.usermsg('write',  'float', 'shake', power)
                es.usermsg('write',  'float', 'shake', 1.0)
                es.usermsg('write',  'float', 'shake', time)
                es.usermsg('send',   'shake', i)
                es.usermsg('delete', 'shake')
    del stun[:]