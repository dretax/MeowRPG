# Stunnade-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Stunnade'


# Load config values
rpgStunnadeTime = config.GetInt('rpgStunnadeTime')
rpgStunnadePower = config.GetInt('rpgStunnadePower')


# Global variables
stun = []


# Events
def player_blind(ev):
    stun.append(ev['userid'])
   
   
def flashbang_detonate(ev):    
    level = playerlist[ev['userid']].GetSkillLevel(skillname)
    team = 5 - int(ev['es_userteam'])      
    if level > 0:
        time = level * rpgStunnadeTime
        power = level * rpgStunnadePower
        for i in stun:
            playerlist[i].player.flash(0,0)
            if int(es.getplayerteam(i)) == team:
                es.usermsg('create', 'shake', 'Shake')
                es.usermsg('write',  'byte',  'shake', 0)
                es.usermsg('write',  'float', 'shake', power)
                es.usermsg('write',  'float', 'shake', 1.0)
                es.usermsg('write',  'float', 'shake', time)
                es.usermsg('send',   'shake', i)
                es.usermsg('delete', 'shake')
    del stun[:]