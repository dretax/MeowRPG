# Parachute-Skill by *meow*
#
# Orginal Parachute Mod by L'In20Cible (http://addons.eventscripts.com/addons/view/parachute)
#
# Thanks to L'In20Cible for the permission to use his source code
# Thanks to SWAT_88 for the permission to use his models and materials
#
# Please notice: This skill requires Source Python Extensions (SPE) to work proper
#
# Version 1.0


# Imports

# Python-Imports
import random

# ES-Imports
import es

# Source-Python-Extensions
import spe

# RPG-Imports
from meowrpg import playerlist, config



# Script
skillname = 'Parachute'


# Load config values
rpgParachuteValue = config.GetInt('rpgParachuteValue')
rpgParachuteModels = config.GetList('rpgParachuteModels')
rpgParachuteDownloads = config.GetList('rpgParachuteDownloads')


# Global variables
parachuted = {}
amounts = {}
buttonPressedOffset = 2648
if spe.platform != "nt":
    buttonPressedOffset += 20


# Events
def load():    
    es.addons.registerTickListener(OnTick)
   
    for i in rpgParachuteDownloads:
        es.stringtable("downloadables", i) 
    

def unload():
    es.addons.unregisterTickListener(OnTick)
        
        
def es_map_start(ev):   
    for i in rpgParachuteDownloads:
        es.stringtable("downloadables", i) 
        

def round_end(ev):
    amounts.clear()  
         
        
def rpg_player_spawn(ev):
    player = playerlist[ev['userid']]
    amounts[player.userid] = player.GetSkillLevel(skillname) * rpgParachuteValue
    
    
def rpg_skill_level_changed(ev):
    if ev['skill'] == skillname:   
        userid = int(ev['userid'])
        if userid in amounts: 
            amounts[userid] += (int(ev['level']) - int(ev['old_level'])) * rpgParachuteValue
            if amounts[userid] < 0:
                amounts[userid] = 0   
        elif int(ev['level']) > 0:
            amounts[userid] += int(ev['level']) * rpgParachuteValue         
            

def OnTick():
    for i in amounts:
        if i not in parachuted and not es.getplayerprop(i, "CBasePlayer.pl.deadflag") and spe.getLocVal("i", spe.getPlayer(i) + buttonPressedOffset) & 32 and es.getplayerprop(i, "CBasePlayer.localdata.m_Local.m_flFallVelocity") >= 1.0 and amounts[i] > 0:
            index = es.createentity("prop_dynamic_override")
            parachuted[i] = index
            es.entitysetvalue(index, "solid", 0)
            es.entitysetvalue(index, "model", random.choice(rpgParachuteModels))
            es.server.insertcmd("es_xspawnentity %i" % index)
            amounts[i] -= 1             
    for i in parachuted.copy():
        if not es.exists("userid", i) or es.getplayerprop(i, "CBasePlayer.pl.deadflag") or es.getplayerprop(i, "CBasePlayer.localdata.m_hGroundEntity") != -1 or es.getplayerprop(i, "CBasePlayer.localdata.m_nWaterLevel") > 1 or not spe.getLocVal("i", spe.getPlayer(i) + buttonPressedOffset) & 32:
            spe.removeEntityByIndex(parachuted[i])
            del parachuted[i]
        else:
            es.entitysetvalue(parachuted[i], "angles", "0 %f 0" % es.getplayerprop(i, "CCSPlayer.m_angEyeAngles[1]"))
            es.entitysetvalue(parachuted[i], "origin", es.getplayerprop(i, "CBaseEntity.m_vecOrigin").replace(",", " "))
            es.setplayerprop(i, "CBasePlayer.localdata.m_vecBaseVelocity", "0,0,%f" % es.getplayerprop(i, "CBasePlayer.localdata.m_Local.m_flFallVelocity"))
  