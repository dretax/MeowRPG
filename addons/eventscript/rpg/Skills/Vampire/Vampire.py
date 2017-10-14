# Vampire-Skill by Rennnyyy
#
# Version 1.0


# Imports

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Vampire'
            
            
def player_hurt(ev):
    # Get userid, level, maxHealth and plyerlib instance
    userid = int(ev['attacker']) 
    player = playerlist[userid] 
    maxHealth = player.properties['maxhealth']     
    level = player.GetSkillLevel(skillname)
    player = player.player
    # Calculate and set hp
    hp = player.getHealth() + int(int(ev['dmg_health']) * 0.05 * level)
    if hp < maxHealth: 
        player.setHealth(hp) 
    else:
        player.setHealth(maxHealth)