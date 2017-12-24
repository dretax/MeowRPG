# Damage-Skill by *meow*
#
# Thanks to L'In20Cible for the permission to use his source code
#
# Version 1.0


# Imports

# ES-Imports
import es
import playerlib

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Damage'


# Load config values
rpgDamageValue = config.GetFloat('rpgDamageValue') 
rpgDamageTeam = config.GetBool('rpgDamageTeam')


# Global variables
block = set()


# Events
def player_hurt(ev):
    # Get level of that skill
    level = playerlist[ev['attacker']].GetSkillLevel(skillname)
    userid = int(ev['userid'])
    if userid in block:
        block.remove(userid)
    else:
        if level > 0 and (rpgDamageTeam or es.getplayerteam(ev['attacker']) != es.getplayerteam(ev['userid'])):
            block.add(userid)          
            rpg_damage(ev['userid'], int(int(ev['dmg_health']) * level * rpgDamageValue), ev['attacker'], ev['weapon']) 
        

def rpg_damage(userid, damage, attacker, weapon):
    player = playerlib.getPlayer(userid)
    index = es.createentity('point_hurt')
    es.entitysetvalue(index, 'targetname', index)
    es.entitysetvalue(index, 'damage', damage)
    es.entitysetvalue(index, 'damagetype', 2)
    es.entitysetvalue(index, 'classname', weapon)
    targetname = es.entitygetvalue(player.index, 'targetname')
    es.entitysetvalue(player.index, 'targetname', player)
    es.fire(attacker, index, 'addoutput', 'damagetarget %s' %(userid))
    es.fire(attacker, index, 'hurt')
    es.fire(userid, '!self', 'addoutput', 'targetname %s' %(targetname))
    es.fire(userid, index, 'kill')