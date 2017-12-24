# Firegrenade-Skill by *meow*
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Firegrenade'


# Load config values
rpgFiregrenadeTime = config.GetInt('rpgFiregrenadeTime') 
rpgFiregrenadeTeamignite = config.GetBool('rpgFiregrenadeTeamignite')


# Events
def player_hurt(ev):
    # Get level of that skill
    level = playerlist[ev['attacker']].GetSkillLevel(skillname)
    if ev['weapon'] == 'hegrenade' and level > 0 and (rpgFiregrenadeTeamignite or es.getplayerteam(ev['attacker']) != es.getplayerteam(ev['userid'])):          
        es.server.queuecmd('es_fire %s !self IgniteLifetime %s' %(ev['userid'], level * rpgFiregrenadeTime))