# Firegrenade-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Firegrenade'

def player_hurt(ev):
    # Get level of that skill
    level = playerlist[ev['attacker']].GetSkillLevel(skillname)
    if ev['weapon'] == 'hegrenade' and level > 0:          
        es.server.queuecmd('es_fire %s !self IgniteLifetime %s' %(ev['userid'], level))