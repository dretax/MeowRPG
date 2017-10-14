# Impulse-Skill by Rennnyyy
#
# Version 1.0


# Imports

# Python-Imports
import math

# ES-Imports
import es
import playerlib
import gamethread

# RPG-Imports
from rpg.rpg import playerlist, skillhandler


# Script
skillname = 'Medic'


def unload():
    gamethread.cancelDelayed('rpg_%s' %(skillname))    


def round_start(ev):
    gamethread.delayedname(3.0, 'rpg_%s' %(skillname), rpg_medic, ())
    
    
def round_end(ev):
    gamethread.cancelDelayed('rpg_%s' %(skillname)) 

        
def rpg_medic():
    gamethread.delayedname(3.0, 'rpg_%s' %(skillname), rpg_medic, ())
    for i in playerlib.getUseridList('#ct, #alive'):
        x1, y1, z1 = es.getplayerlocation(i)
        # Get level of that skill
        level = playerlist[i].GetSkillLevel(skillname)
        if level == 0:
            continue
        for j in playerlib.getUseridList('#ct, #alive'):
            if i == j:
                continue
            x2, y2, z2 = es.getplayerlocation(j)
            if math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2) <= 300:
                rpg_heal(level, playerlist[j])   
    for i in playerlib.getUseridList('#t, #alive'):
        x1,y1,z1 = es.getplayerlocation(i)
        healer = playerlist[i]  
        for j in playerlib.getUseridList('#t, #alive'):
            if i == j:
                continue
            x2, y2, z2 = es.getplayerlocation(j)
            if math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2) <= 300:
                rpg_heal(level, playerlist[j])                                   


def rpg_heal(level, player):
    # Get maxHealth and playerlib instance
    maxHealth = player.properties['maxhealth']
    player = player.player 
    # Set armor or health
    if player.getHealth() == maxHealth:  
        armor = player.getArmor() + level * 10
        if armor <= 100:
            player.setArmor(armor)
        else:
            player.setArmor(100)   
    else:
        hp = player.getHealth() + level * 5 
        if hp <= maxHealth:
            player.setHealth(hp) 
        else:
            player.setHealth(maxHealth)   