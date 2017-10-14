# Longjump-Skill by Rennnyyy
#
# Version 1.0


# Imports

# ES-Imports
import es

# RPG-Imports
from rpg.rpg import playerlist


# Script
skillname = 'Longjump'
        
def player_jump(ev):
    # Get userid and level for that skill
    userid = int(ev['userid'])
    level = playerlist[userid].GetSkillLevel(skillname) 
    
    # Calculate jump vector and set it       
    horizontalVector = es.getplayerprop(userid, 'CBasePlayer.localdata.m_vecVelocity[0]')
    verticalVector   = es.getplayerprop(userid, 'CBasePlayer.localdata.m_vecVelocity[1]')       
    horizontalVector = (level * horizontalVector) * 0.25
    verticalVector   = (level * verticalVector)   * 0.25
    vector = '%s,%s,0' % (horizontalVector, verticalVector)        
    es.setplayerprop(userid, 'CBasePlayer.localdata.m_vecBaseVelocity', vector) 