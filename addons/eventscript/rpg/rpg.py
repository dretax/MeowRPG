###################################################################################
#                                                                                 #
# Meow RPG by *meow*                                                              #
#                                                                                 #
# Version 1.0.5                                                                   #
#                                                                                 #
###################################################################################



###############################
#                             #
#   Includes                  #
#                             #
###############################

# Python includes
import os
import sys
import sqlite3 
import time
import pickle
import base64
import socket
import select
import math
import urllib
import urllib2
import thread
import calendar


# ES includes
import es
import playerlib
import usermsg
import popuplib
import cmdlib
import gamethread



###############################
#                             #
#   Global variables          #
#                             #
###############################

# Version info
version = '1.0.5'

# Main paths
pluginPath = os.path.join(os.getcwd(), 'cstrike/addons/eventscripts/meowrpg')
configPath = os.path.join(os.getcwd(), 'cstrike/cfg/meowrpg')



###############################
#                             #
#   Classes                   #
#                             #
###############################       
     
# Language (provides a simple class for config-file reading)  
class Config(object):
    '''This class provides access to the configuration of Meow RPG.
    
    You should not create any instance of this class. A instance called "config" is available in the Meow RPG core script.

    Example:

    >>> from meowrpg import config
    >>> config.GetBool('rpgHealthLoad')
    True'''
    
    def __init__(self, path):
        # Config values
        self.config = {}
    
        # Read along all files in the given path, which end with cfg
        for i in os.listdir(path):
            if i.endswith('.cfg'):
                f = file(os.path.join(path, i))          
                for line in f:
                    line = line.replace('\n', '').replace('\r', '').replace(' ', '')
                    # Only accept lines which do not start with "#", are not empty and contain a "="
                    if (not (line.startswith('#') or len(line) == 0)) and '=' in line:
                        # Split into key and value
                        line = line.split('=')
                        if len(line) == 2:
                            self.config[line[0]] = line[1].replace('"', '')
                f.close()
                            
                            
    def GetString(self, key):
        '''Returns a configuration value related to the given key converted as a string. 
        
        You can find valid keys in the configuration files, which can be found in the folder "cstrike/cfg/meowrpg".'''
        
        return self.config[key]
        
        
    def GetFloat(self, key):
        '''Returns a configuration value related to the given key converted as a float. 
        
        You can find valid keys in the configuration files, which can be found in the folder "cstrike/cfg/meowrpg".'''
        
        return float(self.GetString(key))
        
    
    def GetInt(self, key):
        '''Returns a configuration value related to the given key onverted as an integer. 
        
        You can find valid keys in the configuration files, which can be found in the folder "cstrike/cfg/meowrpg".'''
        
        return int(self.GetString(key))
        
    
    def GetBool(self, key):
        '''Returns a configuration value related to the given key converted as boolean. 
        
        You can find valid keys in the configuration files, which can be found in the folder "cstrike/cfg/meowrpg".'''    
        
        return bool(self.GetInt(key))
        
    
    def GetList(self, key):
        '''Returns more configuration values related to the given key converted as list.
        
        The configuration value related to the given key is split by the comma character (,) and all spaces are deleted. 
        
        You can find valid keys in the configuration files, which can be found in the folder "cstrike/cfg/meowrpg".'''
        
        return self.GetString(key).replace(' ', '').split(',')   
        
       
    def HasKey(self, key):
        '''Returns True if there is a configuration value related to the given key. 
        
        You can find valid keys in the configuration files, which can be found in the folder "cstrike/cfg/meowrpg".'''
        
        return key in self.config.keys()     
        
        
# Language (provides a multi-language class)
class Language(object):  
    def __init__(self, path): 
        self.tokens = {}
        self.table = {}
        
        # Open language file
        f = file(os.path.join(path, 'language.ini'))
        curTok = None
            
        for line in f: 
            line = line.replace('\n', '').replace('\r', '')
            if not line.startswith('#'):
                if line.startswith('['):
                    curTok = line.replace('[','').replace(']','')
                    if curTok != 'table':
                        self.tokens[curTok] = {}
                elif len(line.split('=')) == 2:
                    line = line.split('=')
                    lang = line[0].replace(' ','')
                    tok = line[1].partition('"')[2].partition('"')[0]
                    if curTok != 'table':                        
                        self.tokens[curTok][lang] = tok 
                    else:
                        self.table[lang] = tok               
        f.close()


    def GetLanguage(self, token, speech, inserts = {}):
        if token in self.tokens and speech in self.tokens[token]:
            tmp = self.tokens[token][speech]
            for i in inserts:
                tmp = tmp.replace('$%s' %(i), str(inserts[i]))
            return tmp
        elif token not in self.tokens:
            return 'Token not defined'
        else: 
            return 'Language not defined'  
            
            
    def GetAllLanguages(self):
        return self.table.keys()  


    def GetLanguageByShortcut(self, name):
        if name in self.table.keys():
            return self.table[name]
        return None
        
        
# Internet (provides a handling for connections to the internet
class Internet(object):
    def __init__(self):
        self.updateAvailable = False
        self.currentVersion = version
        
        self.connected = False
        
        self.Connect() 
        
        self.CheckVersion()       
    
    
    def Connect(self):        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.socket.connect((socket.gethostbyname('meow-rpg.com'), 44545))  
            self.connected = True
            es.server.queuecmd('echo "[Meow RPG] Connected to Master Server"')
        except:
            self.connected = False
            
            
    def IsConnected(self):
        return self.connected
        
    
    def RegisterServer(self): 
        if self.connected and config.GetBool('rpgListServer'): 
            try:
                self.socket.send('server_add#%s#%s' %(str(es.ServerVar('hostport')), base64.encodestring(str(es.ServerVar('hostname')))))
                self.socket.recv(1024)
            except:
                self.socket.close()
                self.connected = False
        
        
    def Close(self):
        self.connected = False
        self.socket.close()        
    
    
    def IsPremium(self, steamid):
        if self.connected:
            try:
                self.socket.send('premium_get#%s' %(steamid.replace(':', '_')))
                data = self.socket.recv(1024).split('#')
                if bool(int(data[0])): 
                    return bool(int(data[1]))
                else:
                    return False
            except:
                self.socket.close()
                self.connected = False
                return False
        else:
            return False
            
    
    def GetPremiumExpire(self, steamid):
        if self.connected:
            try:
                self.socket.send('premium_expire#%s' %(steamid.replace(':', '_')))
                data = self.socket.recv(1024).split('#')
                if bool(int(data[0])):
                    data = data[1].split(' ') 
                    return '%s %s %s' %(data[2], calendar.month_name[int(data[1])], data[0])
                else:
                    return 'Expire date could not be found'
            except:
                self.socket.close()
                self.connected = False
                return 'Expire date could not be found'   
        return 'Expire date could not be found'
               
            
    def CheckVersion(self):
        if self.connected:
            try:
                self.socket.send('version_get')
                data = self.socket.recv(1024).split('#')  
                if bool(int(data[0])):
                    self.currentVersion = data[1]
                    self.updateAvailable = version != self.currentVersion
            except:
                self.socket.close()
                self.connected = False    
            
                       
    def UpdateAvailable(self):
        return self.updateAvailable, self.currentVersion
        
        
    def SendRank(self, steamid, name, xp, level):
        request = urllib2.Request(config.GetString('rpgRankURL'), urllib.urlencode([('steamid', steamid), ('name', base64.encodestring(name)), ('xp', xp), ('level', level)]))
        url = urllib2.urlopen(request)  
        url.close()       
                        
                        
# Skillhandler (provides a handling for all skills)
class Skillhandler(object):
    '''This class provides access to all Skills of Meow RPG.
    
    You should not create any instance of this class. A instance called "skillhandler" is available in the Meow RPG core script.

    Example:

    >>> from meowrpg import skillhandler
    >>> skillhandler.GetSkills()
    ['Gravity', 'Health', 'Vampire']
    >>> skillhandler.GetLoadedSkills()
    ['Health', 'Vampire']
    >>> skillhandler.Load('Gravity')
    'Loaded skill: Gravity'
    >>> skillhandler.GetLoadedSkills()
    ['Gravity', 'Health', 'Vampire']
    '''
    
    def __init__(self, path):
        path = os.path.join(path)
        self.skills = {}
        
        # Read along the given path for skills
        for i in os.listdir(path):
            try:
                tmp = os.listdir(os.path.join(path, i))                
                if ('%s.py' %(i) in tmp or '%s.pyc' %(i) in tmp) and ('__init__.py' in tmp or '__init__.pyc' in tmp):
                    if config.HasKey('rpg%sLoad' %(i)) and config.HasKey('rpg%sCredits' %(i)) and config.HasKey('rpg%sAmount' %(i)) and config.HasKey('rpg%sMax' %(i)):  
                        self.skills[i.capitalize()] = False
            except:
                pass   
        
        
    def LoadAll(self):
        '''Loads all available Skills.
        
        You can get a list of available Skills with GetSkills().'''
        
        for i in [i for i in self.skills.keys() if not self.skills[i]]:
            if config.GetBool('rpg%sLoad' %(i)):
                es.server.queuecmd('es_xload meowrpg/Skills/%s' %(i))
                self.skills[i] = True   
              
                
    def Load(self, skill):
        '''Loads the given Skill. 
        
        Returns a string with a message of success (or failure).        
        
        You can get a list of available Skills with GetSkills().'''
        
        skill = skill.capitalize()
        if skill in self.skills.keys():
            if not self.skills[skill]:
                es.server.queuecmd('es_xload meowrpg/Skills/%s' %(skill))
                self.skills[skill] = True  
                
                # We have to renew all upgrade popups!
                for i in playerlist.GetPlayerlist():
                    i.upgradePopup.Renew()
                
                return 'Loaded skill: "%s"' %(skill)
            return 'Skill "%s" already loaded' %(skill)
        return 'Skill "%s" does not exist: See rpg_skills for further details' %(skill)
                
    
    def UnloadAll(self):
        '''Unloads all Skills.
        
        You can get a list of available Skills with GetSkills().'''
        
        for i in [i for i in self.skills.keys() if self.skills[i]]:
            es.server.queuecmd('es_xunload meowrpg/Skills/%s' %(i))
            self.skills[i] = False  
            
            
    def Unload(self, skill):
        '''Unloads the given Skill. 
        
        Returns a string with a message of success (or failure).
        
        You can get a list of available Skills with GetSkills().'''
        
        skill = skill.capitalize()
        if skill in self.skills.keys():
            if self.skills[skill]:
                es.server.queuecmd('es_xunload meowrpg/Skills/%s' %(skill))
                self.skills[skill] = False
                
                # We have to renew all upgrade popups!
                for i in playerlist.GetPlayerlist():
                    i.upgradePopup.Renew()
                 
                return 'Unloaded skill: "%s"' %(skill) 
            return 'Skill "%s" already unloaded' %(skill)
        return 'Skill "%s" does not exist: See rpg_skills for further details' %(skill)
        
    
    def IsLoaded(self, skill):
        '''Returns True if the given Skill is already loaded.
        
        You can get a list of available Skills with GetSkills().'''
        
        try:
            return self.skills[skill.capitalize()]
        except:
            return False
        
        
    def GetLoadedSkills(self):
        '''Returns a list of all loaded Skills.
        
        The list is sorted ascending'''
        
        ret = [i for i in self.skills.keys() if self.skills[i]]
        ret.sort()
        return ret
        

    def GetSkills(self):
        '''Returns a list of all available Skills.
        
        The list is sorted ascending'''
        
        ret = [i for i in self.skills.keys()]
        ret.sort()
        return ret
        

# Ranking (provides displaying the ranking of all players)
class Ranking(object):               
    # Getters
    def GetPlace(self, steamid):
        return saving.GetPlace(steamid)
        

    # Send the popup
    def SendPopup(self, userid):
        if popuplib.exists('rpg_record'):
            popuplib.delete('rpg_record')
        popup = popuplib.create('rpg_record')
        popup.addline('[Meow RPG] Top 10')
        for i in xrange(1,11):
            data = saving.GetRank(i)
            if data != None:
                popup.addline('%s. %s - %s XP' %(i, data[0], data[1]))
            else:
                popup.addline('%s. Empty - 0 XP' %(i))  
        popup.addline('->0. Exit')
        popup.send(userid)    
    
        
# MultiPopup (provides a popup with automatic option adding and title)        
class MultiPopup(object):
    def __init__(self, language, popupname, title, callback, showBack = True):
        # Language
        self.language = language        
    
        # Name and title
        self.popupname = popupname
        self.title = title
        
        # Callback method
        self.callback = callback
        
        # Show the "Back" text
        self.showBack = showBack
        
        # List of popups
        self.popupList = []
        
        # Callback Agruments
        self.optionList = {}
        
        # Is it the first time we sent this popup?    
        self.firstSend = True  
        
        # Current option number
        self.currentOptionNumber = 1 
                                                                                                                                                                                    
        self.CreateNewSubpopup()
        
        
    def AddOption(self, option, callbackArg, canUse = True):
        # Maximum of options for this subpopup is reached, so created a new one
        if self.currentOptionNumber == 8:
            self.CreateNewSubpopup()    
        # Add the line and add the callback argument 
        if canUse:
            self.popupList[len(self.popupList) - 1].addline('->%s. %s' %(self.currentOptionNumber, option))
            self.optionList['%s.%s' %(len(self.popupList) - 1, self.currentOptionNumber)] = callbackArg
        else:
            self.popupList[len(self.popupList) - 1].addline('%s. %s' %(self.currentOptionNumber, option))  
            self.optionList['%s.%s' %(len(self.popupList) - 1, self.currentOptionNumber)] = None
        self.currentOptionNumber += 1 
             
        
    def CreateNewSubpopup(self):
        subpopupNumber = len(self.popupList) 
        # Delete old popup with this name
        if popuplib.exists('%s_%s' %(self.popupname, subpopupNumber)):
            popuplib.delete('%s_%s' %(self.popupname, subpopupNumber))
        # Create the new popup
        currentSubpopup = popuplib.create('%s_%s' %(self.popupname, subpopupNumber))
        # If the title is a tuple () or list [], we add multiple lines as title
        if isinstance(self.title, (list, tuple)):
            for i in self.title:
                currentSubpopup.addline(i)  
        else:
            currtenSubpopup.addline(self.title)
        # Add the new subpopup to the list
        self.popupList.append(currentSubpopup)
        # Add Back, Next and Exit to the previous subpopup
        if subpopupNumber > 0:
            previousSubpopup = self.popupList[subpopupNumber - 1] 
            if currentSubpopup != 1 or (currentSubpopup == 1 and self.showBack):
                previousSubpopup.addline('->8. %s' %(language.GetLanguage('back', self.language)))
            previousSubpopup.addline('->9. %s' %(language.GetLanguage('next', self.language)))    
            previousSubpopup.addline('->0. %s' %(language.GetLanguage('exit', self.language)))   
            previousSubpopup.menuselect = self.Menuselect
        # Next option is the first option in this subpopup
        self.currentOptionNumber = 1 
     
        
        
    def Send(self, userid):
        # If this is the first time we send this popup we have to finish the last popup
        if self.firstSend:
            currentSubpopup = self.popupList[len(self.popupList) - 1]
            if self.showBack or len(self.popupList) != 1:  
                currentSubpopup.addline('->8. %s' %(language.GetLanguage('back', self.language))) 
            currentSubpopup.addline('->0. %s' %(language.GetLanguage('exit', self.language)))   
            currentSubpopup.menuselect = self.Menuselect                            
            self.firstSend = False
        # Send the first subpopup
        self.popupList[0].send(userid)
        
    
    def SendPage(self, userid, subpopupNumber):
        # If this is the first time we send this popup we have to finish the last popup
        if self.firstSend:
            currentSubpopup = self.popupList[len(self.popupList) - 1]
            if self.showBack or len(self.popupList) != 1:  
                currentSubpopup.addline('->8. %s' %(language.GetLanguage('back', self.language))) 
            currentSubpopup.addline('->0. %s' %(language.GetLanguage('exit', self.language)))   
            currentSubpopup.menuselect = self.Menuselect                            
            self.firstSend = False
        # If the subpopup number is higher than the existing subpupups send the last subpopup
        if subpopupNumber >= len(self.popupList):
            self.popupList[-1].send(userid)
        else:
            self.popupList[subpopupNumber].send(userid)
        
        
    def Menuselect(self, userid, choice, id):
        # A option was chosen
        if choice < 8:
            id = int(id.replace('%s_' %(self.popupname), ''))
            option = '%s.%s' %(id, choice) 
            try:
                self.callback(userid, self.optionList[option], self.popupname, id)
            except:
                self.popupList[id].send(userid)     
        # Back was chosen
        elif choice == 8:
            id = int(id.replace('%s_' %(self.popupname), ''))
            if id == 0:
                if self.showBack:
                    self.callback(userid, 'back', self.popupname, id) 
                else:
                    self.popupList[id].send(userid)     
            else:
                self.popupList[id - 1].send(userid) 
        # Next was chosen 
        elif choice == 9:
            id = int(id.replace('%s_' %(self.popupname), ''))
            if id  == len(self.popupList) - 1:
                self.popupList[-1].send(userid)
            else:
                self.popupList[id + 1].send(userid)
        # Exit was chosen
        elif choice == 10:
            id = int(id.replace('%s_' %(self.popupname), ''))
            self.callback(userid, 'exit', self.popupname, id)    
     
     
    def Delete(self):
        try:
            # Clean!
            self.callback = None 
            for i in xrange(len(self.popupList)):            
                self.popupList[i].menuselect = None
                popuplib.delete('%s_%s' %(self.popupname, i))
            del self.popupList[:]
            self.optionList.clear()  
        except:
            pass        
 
 
# MainPopup (the main popup)        
class MainPopup(object):
    def __init__(self, player):
        self.player = player
        self.userid = player.userid
        self.language = player.language 
        
        self.popupname = '%s_rpg_main' %(self.userid)
        
        self.renew = True
        
        self.CreatePopup(True)
        
        
    def Renew(self):
        if not self.renew:
            self.renew = True
        
        
    def CreatePopup(self, first=False):  
        # Delete old popups
        try:
            if not first:
                self.popup.menuselect = None
                self.popup.delete()
            if popuplib.exists(self.popupname):
                popuplib.delete(self.popupname)
        except:
            pass
             
        # Check language
        if self.language != self.player.language:
            self.language = self.player.language
    
        # Create new popup
        self.popup = popuplib.create(self.popupname)
        self.popup.addline('[Meow RPG] %s' %(language.GetLanguage('main', self.language)))
        self.popup.addline('->1. %s' %(language.GetLanguage('upgrade', self.language)))  
        self.popup.addline('->2. %s' %(language.GetLanguage('sell', self.language)))  
        self.popup.addline('->3. %s' %(language.GetLanguage('statistic', self.language)))  
        self.popup.addline('->4. %s' %(language.GetLanguage('settings', self.language)))  
        self.popup.addline('->5. %s' %(language.GetLanguage('information', self.language)))
        self.popup.addline('->6. %s' %(language.GetLanguage('help', self.language)))   
        self.popup.addline('->0. %s' %(language.GetLanguage('exit', self.language)))            
        self.popup.menuselect = self.Menuselect
        
        self.renew = False
        
        
    def Send(self):
        # Send the popup
        if self.renew:
            self.CreatePopup()
        self.popup.send(self.userid)        
        
        
    def Menuselect(self, userid, choice, id):
        # No options on this choice -> resend
        if choice in (7,8,9):
            self.Send()
        # If choice was not exit -> send the next popup
        elif choice != 10:
            if choice == 1:
                self.player.upgradePopup.Send() 
            elif choice == 2:
                self.player.sellPopup.Send() 
            elif choice == 3:
                self.player.statisticPopup.Send() 
            elif choice == 4:
                self.player.settingsPopup.Send()  
            elif choice == 5:
                self.player.infoPopup.Send()  
            elif choice == 6:
                self.player.helpPopup.Send()     
                
                
    def Delete(self):
        # Delete the popups
        try:
            self.popup.menuselect = None
            self.popup.delete()
            if popuplib.exists(self.popupname):
                popuplib.delete(self.popupname) 
        except:
            pass
             
                                      
# UpgradePopup (the upgrade popup)        
class UpgradePopup(object):
    def __init__(self, player):
        self.player = player
        self.userid = player.userid
        self.language = player.language 
        
        self.popupname = '%s_rpg_upgrade' %(self.userid)
        
        self.renew = True
        
        self.CreatePopup(True)
    
        
    def Renew(self):        
        if not self.renew:
            self.renew = True 
               
    
    def CreatePopup(self, first=False):  
        # Delete old popups
        if not first:
            self.popup.Delete() 
            
        # Check language
        if self.language != self.player.language:
            self.language = self.player.language         
         
        # Create new popup     
        self.popup = MultiPopup(self.language, self.popupname, ('[Meow RPG] %s' %(language.GetLanguage('upgrade', self.language)), language.GetLanguage('current_credits', self.language, {'credits' : self.player.GetCredits()})), self.Menuselect) 
  
        for i in skillhandler.GetLoadedSkills():
            if not self.player.IsSkillMax(i):
                level = self.player.GetSkillLevel(i) + 1
                if config.GetInt('rpg%sMax' %(i)) == level:  
                    self.popup.AddOption(language.GetLanguage('upgrade_level_max', self.language, {'skill' : i, 'level' : level, 'cost' : self.player.GetSkillCredits(i)}), i, self.player.HasSkillCredits(i))
                else:
                    self.popup.AddOption(language.GetLanguage('upgrade_level', self.language, {'skill' : i, 'level' : level, 'cost' : self.player.GetSkillCredits(i)}), i, self.player.HasSkillCredits(i))                         
        self.renew = False
         
        
    def Send(self):
        if self.renew:
            self.CreatePopup()
        self.popup.Send(self.userid)
        
        
    def SendPage(self, subpopupNumber):
        if self.renew:
            self.CreatePopup()
        self.popup.SendPage(self.userid, subpopupNumber)  
        
        
    def Menuselect(self, userid, choice, id, page):
        if choice not in ('back', 'exit', None):              
            # Raise the skill level
            if self.player.RaiseSkillLevel(choice):
                tell(self.userid, language.GetLanguage('skill_level_change', self.language, {'skill' : choice, 'level' : self.player.GetSkillLevel(choice)}))
            else:
                tell(self.userid, language.GetLanguage('not_enough_credits', self.language))
            if not self.player.GetAutomaticPopupClose():             
                self.SendPage(page) 
        elif choice == 'back':
            self.player.mainPopup.Send()  
        elif choice != 'exit':
            tell(self.userid, language.GetLanguage('not_enough_credits', self.language))
            if not self.player.GetAutomaticPopupClose():
                self.SendPage(page) 
                
                
    def Delete(self):     
        self.popup.Delete()   
  
                       
# SellPopup (the upgrade popup)          
class SellPopup(object):
    def __init__(self, player):
        self.player = player
        self.userid = player.userid
        self.language = player.language 
        
        self.popupname = '%s_rpg_sell' %(self.userid)
        
        self.renew = True
        
        self.CreatePopup(True)
     
        
    def Renew(self):
        if not self.renew:
            self.renew = True
        
        
    def CreatePopup(self, first=False):  
        # Delete old popups
        if not first:
            self.popup.Delete() 
            
        # Check language
        if self.language != self.player.language:
            self.language = self.player.language         
        
        # Create new popup     
        self.popup = MultiPopup(self.language, self.popupname, ('[Meow RPG] %s' %(language.GetLanguage('sell', self.language)),  language.GetLanguage('current_credits', self.language, {'credits' : self.player.GetCredits()})), self.Menuselect) 
        
        for i in self.player.GetSkills():
            self.popup.AddOption(language.GetLanguage('sell_level', self.language, {'skill' : i, 'level' : self.player.GetSkillLevel(i, False), 'cost' : self.player.GetSkillSellCredits(i)}), i)    
        
        self.renew = False
               
                
    def Send(self):
        if self.renew:
            self.CreatePopup()
        self.popup.Send(self.userid)  
            
            
    def SendPage(self, subpopupNumber):
        if self.renew:
            self.CreatePopup()
        self.popup.SendPage(self.userid, subpopupNumber)    
           
                                
    def Menuselect(self, userid, choice, id, page):  
        if choice != 'back' and choice != 'exit':
            self.player.DecrementSkillLevel(choice)
            tell(self.userid, language.GetLanguage('skill_level_change', self.language, {'skill' : choice, 'level' : self.player.GetSkillLevel(choice, False)}))
            if not self.player.GetAutomaticPopupClose():
                self.SendPage(page) 
        elif choice != 'exit':
            self.player.mainPopup.Send()    
        
        
    def Delete(self):
        self.popup.Delete()  
        

# StatisticPopup (the statistic popup)           
class StatisticPopup(object):
    def __init__(self, player):
        self.player = player
        self.userid = player.userid
        self.language = player.language 
        
        self.popupname = '%s_rpg_statistic' %(self.userid)
        
        self.renew = True
        
        self.CreatePopup(True)
        
    def Renew(self):
        if not self.renew:
            self.renew = True
        
        
    def CreatePopup(self, first=False):  
        # Delete old popups
        try:
            if not first:
                self.popup.menuselect = None
                self.popup.delete()
            if popuplib.exists(self.popupname):
                popuplib.delete(self.popupname)
        except:
            pass
             
        # Check language
        if self.language != self.player.language:
            self.language = self.player.language
    
        # Create new popup
        self.popup = popuplib.create(self.popupname)
        self.popup.addline('[Meow RPG] %s' %(language.GetLanguage('statistic', self.language)))
        self.popup.addline(language.GetLanguage('level', self.language, {'level' : self.player.GetLevel()}))
        self.popup.addline(language.GetLanguage('xp_status', self.language, {'currentXP' : self.player.xp, 'nextXP' : self.player.nextLevelXP}))
        self.popup.addline(language.GetLanguage('credits', self.language, {'credits' : self.player.GetCredits()}))
        self.popup.addline(language.GetLanguage('total_xp', self.language, {'totalXP' : self.player.GetTotalXP()}))
        if config.GetBool('rpgPremium'):
            if self.player.premium:
                self.popup.addline('Premium: %s' %(self.player.premiumExpire))
            else:
                self.popup.addline('Premium: No')
        else:
            self.popup.addline('Premium: Not supported on this server')
        self.popup.addline('->8. %s' %(language.GetLanguage('back', self.language)))
        self.popup.addline('->0. %s' %(language.GetLanguage('exit', self.language)))           
        self.popup.menuselect = self.Menuselect
        
        self.renew = False
     
        
    def Send(self):
        if self.renew:
            self.CreatePopup()
        self.popup.send(self.userid)            
            
        
    def Menuselect(self, userid, choice, id):
        if choice == 8:
            self.player.mainPopup.Send()
        elif choice <= 9:
            self.Send()    
            
            
    def Delete(self):
        # Delete the popups
        try:
            self.popup.menuselect = None
            self.popup.delete()
            if popuplib.exists(self.popupname):
                popuplib.delete(self.popupname) 
        except:
            pass    
             
             
# SettingsPopup (the settings popup)           
class SettingsPopup(object):
    def __init__(self, player):
        self.player = player
        self.userid = player.userid
        self.language = player.language 
        
        self.popupname = '%s_rpg_settings' %(self.userid)
        
        self.renew = True
        
        self.CreatePopup(True)
        
    def Renew(self):
        if not self.renew:
            self.renew = True
        
        
    def CreatePopup(self, first=False):  
        # Delete old popups
        try:
            if not first:
                self.popup.menuselect = None
                self.popup.delete()
            if popuplib.exists(self.popupname):
                popuplib.delete(self.popupname)
        except:
            pass
             
        # Check language
        if self.language != self.player.language:
            self.language = self.player.language
            
        self.popup = popuplib.create(self.popupname) 
        self.popup.addline('[Meow RPG] %s' %(language.GetLanguage('settings', self.language)))
        if self.player.GetAutomaticPopupClose():
            self.popup.addline('->1. %s' %(language.GetLanguage('turn_popup_close_off', self.language)))
        else:
            self.popup.addline('->1. %s' %(language.GetLanguage('turn_popup_close_on', self.language)))
        self.popup.addline('->2. %s' %(language.GetLanguage('language_select', self.language)))         
        self.popup.addline('->3. %s' %(language.GetLanguage('reset', self.language)))        
        self.popup.addline('->8. %s' %(language.GetLanguage('back', self.language))) 
        self.popup.addline('->0. %s' %(language.GetLanguage('exit', self.language)))  
        self.popup.menuselect = self.Menuselect 
        
        
    def Send(self):
        if self.renew:
            self.CreatePopup()
        self.popup.send(self.userid)            
            
        
    def Menuselect(self, userid, choice, id):
        if choice == 1:
            automaticPopupClose = not self.player.GetAutomaticPopupClose()
            self.player.SetAutomaticPopupClose(automaticPopupClose)
            if automaticPopupClose:
                tell(self.userid, language.GetLanguage('popup_close_on', self.language))
            else:
                tell(self.userid, language.GetLanguage('popup_close_off', self.language))
                self.Send() 
        elif choice == 2:
            self.player.languagePopup.Send()              
        elif choice == 3:
            self.player.Reset()
            tell(self.userid, language.GetLanguage('resetted', self.language))
            if not self.player.GetAutomaticPopupClose(): 
                self.Send()
        elif choice == 8:
            self.player.mainPopup.Send() 
        elif choice <= 9:
            self.Send() 
       
            
    def Delete(self):
        # Delete the popups
        try:
            self.popup.menuselect = None
            self.popup.delete()
            if popuplib.exists(self.popupname):
                popuplib.delete(self.popupname) 
        except:
            pass 
             
             
# LanguagePopup (the language popup)           
class LanguagePopup(object):
    def __init__(self, player):
        self.player = player
        self.userid = player.userid
        self.language = player.language 
        
        self.popupname = '%s_rpg_language' %(self.userid)
        
        self.renew = True
        
        self.CreatePopup(True)
        
    def Renew(self):
        if not self.renew:
            self.renew = True
        
        
    def CreatePopup(self, first=False):  
        # Delete old popups
        if not first:
            self.popup.Delete() 
             
        # Check language
        if self.language != self.player.language:
            self.language = self.player.language
            
        self.popup = MultiPopup(self.language, self.popupname, ('[Meow RPG] %s' %(language.GetLanguage('language_headline', self.language)),  language.GetLanguage('language_current', self.language, {'language' : language.GetLanguageByShortcut(self.language)})), self.Menuselect) 
        
        for i in language.GetAllLanguages():
            self.popup.AddOption(language.GetLanguageByShortcut(i), i)    
                
                
    def Send(self):
        if self.renew:
            self.CreatePopup()
        self.popup.Send(self.userid)  
            
            
    def SendPage(self, subpopupNumber):
        if self.renew:
            self.CreatePopup()
        self.popup.SendPage(self.userid, subpopupNumber)    
           
                                
    def Menuselect(self, userid, choice, id, page):  
        if choice != 'back' and choice != 'exit':
            self.player.SetLanguage(choice)
            tell(self.userid, language.GetLanguage('language_selected', choice, {'language' : language.GetLanguageByShortcut(choice)}))
            if not self.player.GetAutomaticPopupClose():
                self.SendPage(page) 
        elif choice != 'exit':
            self.player.settingsPopup.Send()
            
            
    def Delete(self):
        self.popup.Delete()    
        
        
# InfoPopup (the info popup)           
class InfoPopup(object):
    def __init__(self, player):
        self.player = player
        self.userid = player.userid
        self.language = player.language 
        
        self.popupname = '%s_rpg_info' %(self.userid)
        
        self.renew = True
        
        self.CreatePopup(True)
        
    def Renew(self):
        if not self.renew:
            self.renew = True
        
        
    def CreatePopup(self, first=False):  
        # Delete old popups
        try:
            if not first:
                self.popup.menuselect = None
                self.popup.delete()
            if popuplib.exists(self.popupname):
                popuplib.delete(self.popupname)
        except:
            pass
            
        # Check language
        if self.language != self.player.language:
            self.language = self.player.language
            
        self.popup = popuplib.create(self.popupname)
        self.popup.addline('[Meow RPG] %s' %(language.GetLanguage('information', self.language)))
        self.popup.addline('->1. %s' %(language.GetLanguage('skill_info', self.language)))  
        if config.GetBool('rpgPremium'):
            self.popup.addline('->2. %s' %(language.GetLanguage('premium_info', self.language)))       
        self.popup.addline('->Version: %s' %(version)) 
        self.popup.addline('->Scripter: *meow*')
        self.popup.addline('->Thanks to: DreTax, H4v0c, BackRaw')
        self.popup.addline('->HP: www.meow-rpg.com')
    #    self.popup.addline('->%s: www.forum.meow-rpg.com' %(language.GetLanguage('bug_report', self.language)))     
        self.popup.addline('->8. %s' %(language.GetLanguage('back', self.language)))
        self.popup.addline('->0. %s' %(language.GetLanguage('exit', self.language)))
        self.popup.menuselect = self.Menuselect
       
        
    def Send(self):
        if self.renew:
            self.CreatePopup()
        self.popup.send(self.userid)  
        
        
    def Menuselect(self, userid, choice, id):
        if choice == 1:
            usermsg.motd(userid, 2, 'Meow RPG Skills', 'http://meow-rpg.com/en/skills.html')
        elif choice == 2 and config.GetBool('rpgPremium'):
            usermsg.motd(userid, 2, 'Meow RPG Premium', 'http://meow-rpg.com/en/premium.php')  
        elif choice != 8 and choice != 10:
            self.Send()
        elif choice == 8:
            self.player.mainPopup.Send()      
        
            
    def Delete(self):
        # Delete the popups
        try:
            self.popup.menuselect = None
            self.popup.delete()
            if popuplib.exists(self.popupname):
                popuplib.delete(self.popupname) 
        except:
            pass
            
            
# HelpPopup (the help popup)           
class HelpPopup(object):
    def __init__(self, player):
        self.player = player
        self.userid = player.userid
        self.language = player.language 
        
        self.popupname = '%s_rpg_help' %(self.userid)
        
        self.renew = True
        
        self.CreatePopup(True)
        
    def Renew(self):
        if not self.renew:
            self.renew = True
        
        
    def CreatePopup(self, first=False):  
        # Delete old popups
        try:
            if not first:
                self.popup.menuselect = None
                self.popup.delete()
            if popuplib.exists(self.popupname):
                popuplib.delete(self.popupname)
        except:
            pass
            
        # Check language
        if self.language != self.player.language:
            self.language = self.player.language
            
        self.popup = popuplib.create(self.popupname)
        self.popup.addline('[Meow RPG] %s' %(language.GetLanguage('help', self.language)))
        
        self.popup.addline('%s - %s' %(', '.join(config.GetList('rpgSayMainMenu')), language.GetLanguage('main_menu_info', self.language)))
        self.popup.addline('%s - %s' %(', '.join(config.GetList('rpgSayRankMenu')), language.GetLanguage('rank_menu_info', self.language)))
        self.popup.addline('%s - %s' %(', '.join(config.GetList('rpgSayRankOwn')), language.GetLanguage('rank_own_info', self.language)))
        self.popup.addline('%s - %s' %(', '.join(config.GetList('rpgSayInfoMenu')), language.GetLanguage('info_menu_info', self.language)))
        self.popup.addline('%s - %s' %(', '.join(config.GetList('rpgSaySettingsMenu')), language.GetLanguage('settings_menu_info', self.language)))
        self.popup.addline('%s - %s' %(', '.join(config.GetList('rpgSayFastXP')), language.GetLanguage('xp_menu_info', self.language)))
        
        self.popup.addline('->8. %s' %(language.GetLanguage('back', self.language)))
        self.popup.addline('->0. %s' %(language.GetLanguage('exit', self.language)))
        self.popup.menuselect = self.Menuselect
       
        
    def Send(self):
        if self.renew:
            self.CreatePopup()
        self.popup.send(self.userid)  
        
        
    def Menuselect(self, userid, choice, id):
        if choice != 8 and choice != 10:
            self.Send()
        elif choice == 8:
            self.player.mainPopup.Send()      
        
            
    def Delete(self):
        # Delete the popups
        try:
            self.popup.menuselect = None
            self.popup.delete()
            if popuplib.exists(self.popupname):
                popuplib.delete(self.popupname) 
        except:
            pass  
            
            
# AdminPopup (the admin popup)           
class AdminPopup(object):
    def __init__(self): 
        self.choices = {}
        self.playerPopups = {}
           
        try:
            if popuplib.exists('rpg_admin_basic'):
                popuplib.delete('rpg_admin_basic')
        except:
            pass
            
        self.basicPopup = popuplib.create('rpg_admin_basic') 
        self.basicPopup.addline('[Meow RPG] Admin') 
        self.basicPopup.addline('What do you want to do?')
        self.basicPopup.addline('->1. Give XP')
        self.basicPopup.addline('->2. Give Level')
        self.basicPopup.addline('->3. Give Credits')
        self.basicPopup.addline('->4. Reset a Player')
        self.basicPopup.addline('->0. Exit')
        self.basicPopup.menuselect = self.MenuselectBasic
        
        self.xpAmountPopup = MultiPopup('en', 'rpg_admin_amount', ('[aiuto] Admin', 'Select an amount of XP'), self.MenuselectAmount) 
        for i in (100,500,1000,2000,5000,10000,50000,100000,500000):
            self.xpAmountPopup.AddOption(str(i), i)
            
        self.levelAmountPopup = MultiPopup('en', 'rpg_admin_amount', ('[Meow RPG] Admin', 'Select an amount of Level'), self.MenuselectAmount) 
        for i in (1,5,10,15,20,25,50,100,500):
            self.levelAmountPopup.AddOption(str(i), i)
            
        self.creditsAmountPopup = MultiPopup('en', 'rpg_admin_amount', ('[Meow RPG] Admin', 'Select an amount of Credits'), self.MenuselectAmount) 
        for i in (1,5,10,15,20,25,50,100,500):
            self.creditsAmountPopup.AddOption(str(i), i)
     
        
    def CreatePlayerPopup(self, userid):  
        # Delete old popups
        try:
            self.playerPopups[userid].Delete()
        except:
            pass
            
        popup = MultiPopup('en', 'rpg_admin_player', ('[Meow RPG] Admin', 'Select a Player'), self.MenuselectPlayer)
        for i in playerlist.GetPlayerlist():
            popup.AddOption(es.getplayername(i.userid), i) 
        self.playerPopups[userid] = popup 
       
        
    def Send(self, userid):
        self.basicPopup.send(userid)  
        
        
    def MenuselectBasic(self, userid, choice, id):
        userid = int(userid)
        self.choices[userid] = []
        if choice == 1:
            self.choices[userid].append('xp')
            self.xpAmountPopup.Send(userid)
        elif choice == 2:
            self.choices[userid].append('level')
            self.levelAmountPopup.Send(userid)
        elif choice == 3:
            self.choices[userid].append('credits')
            self.creditsAmountPopup.Send(userid)
        elif choice == 4:
            self.choices[userid].append('reset')
            self.CreatePlayerPopup(userid)
            self.playerPopups[userid].Send(userid)        
        elif choice != 10:
            self.Send()  
            
    
    def MenuselectAmount(self, userid, choice, id, page):
        userid = int(userid)
        if choice != 'back' and choice != 'exit':
            self.choices[userid].append(choice)
            self.CreatePlayerPopup(userid)
            self.playerPopups[userid].Send(userid)            
        elif choice == 'back':
            self.Send(userid)
            
    
    def MenuselectPlayer(self, userid, choice, id, page):
        userid = int(userid)
        if choice != 'back' and choice != 'exit':
            self.choices[userid].append(choice)
            self.Execute(userid, self.choices[userid])                        
        elif choice == 'back':
            if self.choices[userid][0] == 'xp':
                del self.choices[userid][-1]
                self.xpAmountPopup.Send(userid)
            elif self.choices[userid][0] == 'level':
                del self.choices[userid][-1]
                self.levelAmountPopup.Send(userid) 
            elif self.choices[userid][0] == 'credits':
                del self.choices[userid][-1]
                self.creditsAmountPopup.Send(userid)  
            elif self.choices[userid][0] == 'reset':
                self.Send(userid)
                
    
    def Execute(self, userid, params):
        player = params[-1]
        command = params[0]
        playerUserid = player.userid
        playerName = es.getplayername(playerUserid)
        adminName = es.getplayername(userid)    
        if len(params) == 3: 
            amount = params[1]                      
            if command == 'xp':
                player.RaiseXP(amount, True)
                tell(playerUserid, '%s gave you %s XP' %(adminName, amount))
                tell(userid, 'You gave %s %s XP' %(playerName, amount)) 
            elif command == 'level':
                player.RaiseLevel(amount)
                tell(playerUserid, '%s gave you %s Level' %(adminName, amount))
                tell(userid, 'You gave %s %s Level' %(playerName, amount)) 
            elif command == 'credits':
                player.RaiseCredits(amount)
                tell(playerUserid, '%s gave you %s Credits' %(adminName, amount))
                tell(userid, 'You gave %s %s Credits' %(playerName, amount)) 
        elif command == 'reset':
            player.Reset()
            tell(playerUserid, '%s resetted you' %(adminName))
            tell(userid, 'You resetted %s' %(playerName)) 
        
            
    def Delete(self):
        # Delete the popups
        try:
            self.basicPopup.menuselect = None
            if popuplib.exists('rpg_admin_basic'):
                popuplib.delete('rpg_admin_basic') 
            self.xpAmountPopup.Delete()
            self.levelAmountPopup.Delete()
            self.creditsAmountPopup.Delete()
            for i in self.playerPopups.values():
                i.Delete()
            self.playerPopups.clear()
        except:
            pass  
           
            
# Saving class (provides saving of a player via SQL)
class Saving(object):     
    def __init__(self, path):   
        # Check if there is a database
        exist = os.path.exists(path)
        
        # Open connection and cursor
        self.connection = sqlite3.connect(path)
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()
        
        # Create new table, if the database was created
        if not exist:
            self.Execute('''CREATE TABLE rpg_version_1_0_1  
                           (steamid text, name text, xp int, totalxp int, level int, credits int, rank int, language text, automaticPopupClose text, skills text)''')
            self.connection.commit()
        else:
            # Check if an old version exists
            try:
                data = self.Execute('SELECT * FROM rpg_version_1_0_0')
                # Success - there is till an old table, let's convert it
                dbg('Converting database from version 1.0.0 to 1.0.1 ...')     
            
                # Changings from 1_0_0 to 1_0_1:
                # - name is not saved as converted unicode string, but as base64 string            
                tmp = []
                for i in data:
                    tmp.append((i[0], base64.encodestring(i[1]), i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9]))
                    
                # Create the 1_0_1 table
                self.Execute('''CREATE TABLE rpg_version_1_0_1  
                               (steamid text, name text, xp int, totalxp int, level int, credits int, rank int, language text, automaticPopupClose text, skills text)''')                

                # Add new data
                for i in tmp:
                    self.Execute('INSERT INTO rpg_version_1_0_1 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', i)
                self.connection.commit()  
            
                # Drop the old table
                self.Execute('DROP TABLE rpg_version_1_0_0')  
                self.connection.commit()
                
                # Debug the rank (if it has lacks maybe)
                self.Debug()
               
                dbg('Success: Database is now on version 1.0.1')              
            except:
                pass

        
    def Close(self):
        for i in playerlist.GetPlayerlist():
            self.Store(i) 
    
        self.connection.commit()
        self.connection.close()
        
        
    def Commit(self):
        self.connection.commit() 
        
    
    def Debug(self):
        # A debugging method
        # We fix the ranking, because it maybe is wrong
        data = self.Execute('SELECT steamid FROM rpg_version_1_0_1 ORDER BY totalxp DESC')
        cnt = 1
        tmp = []
        for i in data:
            tmp.append(str(i[0]))          
        for i in tmp:  
            self.Execute('UPDATE rpg_version_1_0_1 SET rank = ? WHERE steamid = ?', (cnt,i))
            cnt += 1   
      
       
    def Load(self, player):
        # Get the data from the database
        data = self.Execute('SELECT * FROM rpg_version_1_0_1 WHERE steamid = ?', (player.steamid,)) 
        
        # Did we found one?
        found = False
        
        # Add the data to the player
        for i in data:
        
            # XP, Level, Credits, Language and PopupClose are always at the beginning            
            player.xp = int(i[2])
            player.totalxp = int(i[3])
            player.level = int(i[4])
            player.credits = int(i[5])
            player.language = str(i[7])
            player.automaticPopupClose = bool(int(i[8]))
            
            # Split the skill levels
            skills = str(i[9]).split(',')
            for j in skills:
                tmp = j.split('=')
                player.skills[str(tmp[0])] = int(tmp[1]) 
                
            # Yeah, found a player
            found = True          
            break
            
        # Not found
        if not found:
            # Get the rank of this player
            rank = int(self.Execute('SELECT COUNT(*) FROM rpg_version_1_0_1 WHERE totalxp >= ?', (player.totalxp,)).next()[0]) + 1
            self.Execute('UPDATE rpg_version_1_0_1 SET rank = rank + 1 WHERE rank >= ?', (rank,))    
            self.Execute('INSERT INTO rpg_version_1_0_1 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, "")', (player.steamid, base64.encodestring(player.name), player.xp, player.totalxp, player.level, player.credits, rank, player.language, int(player.automaticPopupClose)))
            
        # Call the Loaded function of the player
        player.Loaded()
                     
            
    def Store(self, player):
        # Create the skills saving
        tmp = []
        for i in player.skills:
            tmp.append('%s=%s' %(i, player.skills[i]))
        skills = ','.join(tmp)
        
        steamid = player.steamid
        totalxp = player.totalxp
        
        data = self.Execute('SELECT rank, totalxp FROM rpg_version_1_0_1 WHERE steamid = ?', (steamid,)).next()
        oldrank = int(data[0])
        oldtotalxp = int(data[1])
        if oldtotalxp < totalxp:
            moved = self.Execute('UPDATE rpg_version_1_0_1 SET rank = rank + 1 WHERE rank < ? AND totalxp < ?', (oldrank, totalxp)).rowcount
            self.Execute('UPDATE rpg_version_1_0_1 SET name=?, xp=?, totalxp=?, level=?, credits=?, rank=rank-?, language=?, automaticPopupClose=?, skills=? WHERE steamid=?', (base64.encodestring(player.name), player.xp, totalxp, player.level, player.credits, moved, player.language, int(player.automaticPopupClose), skills, steamid))
        elif oldtotalxp > totalxp:
            moved = self.Execute('UPDATE rpg_version_1_0_1 SET rank = rank - 1 WHERE rank > ? AND totalxp > ?', (oldrank, totalxp)).rowcount
            self.Execute('UPDATE rpg_version_1_0_1 SET name=?, xp=?, totalxp=?, level=?, credits=?, rank=rank+?, language=?, automaticPopupClose=?, skills=? WHERE steamid=?', (base64.encodestring(player.name), player.xp, totalxp, player.level, player.credits, moved, player.language, int(player.automaticPopupClose), skills, steamid))
        else:
            self.Execute('UPDATE rpg_version_1_0_1 SET name=?, xp=?, totalxp=?, level=?, credits=?, language=?, automaticPopupClose=?, skills=? WHERE steamid=?', (base64.encodestring(player.name), player.xp, totalxp, player.level, player.credits, player.language, int(player.automaticPopupClose), skills, steamid))    
               

    def GetPlace(self, steamid):
        # Get a place of the player with this steamid        
        data = self.Execute('SELECT rank, totalxp, level, name FROM rpg_version_1_0_1 WHERE steamid = ?', (steamid,))
        for i in data:
            return int(i[0]), int(i[1]), int(i[2]), str(i[3])
            
    
    def GetRank(self, place):
        # Get ranking details of the player with this place    
        data = self.Execute('SELECT name, totalxp, level FROM rpg_version_1_0_1 WHERE rank = ?', (place,))
        for i in data:
            try:
                return base64.decodestring(str(i[0])), int(i[1]), int(i[2])  
            except:
                return None
        return None     
                
        
    def Execute(self, command, args = ()):
        # Call without arguments    
        if args == ():
            return self.cursor.execute(command)
        # Call with arguments
        else:
            return self.cursor.execute(command, args) 
            
            
# Player (provides a class for handling the player's attributes)  
class Player(object): 
    '''This class provides access to every player (and his achievements).
    
    You should not create any instance of this class. You can access instances related to a player with using the Playerlist class.

    Example:

    >>> from meowrpg import playerlist
    >>> player = playerlist[5] # This is a instance of the Player class which contains information about the player with userid 5
    >>> player.GetSkillLevel('Health')
    7
    >>> player.GetLevel()
    123'''

    # Internal class for properties
    class Properties(dict, object):   
        '''This class provides access to player specific properties.
        
        You should not create any instance of this class. You can access instances related to a player with using the properties variable in a Player class instance.
        
        The class is designed to share information between different skills (like color of the player).
        
        You can define default properties in the Properties.res file, which can be found at "cstrike/addons/eventscripts/meowrpg/Includes". 
        
        Example:
        
        >>> from meowrpg import playerlist
        >>> player = playerlist[5] # This is a instance of the Player class which contains information about the player with userid 5
        >>> player.properties['color']
        [255, 255, 255, 255]
        >>> player.properties['armor'] = 123
        >>> player.properties['armor']
        123'''     
        
        # Static defaults
        defaultProperties = {}
        
        # Load the default properties
        def Load(path):
            f = file(path)     
            for line in f:
                line = line.replace('\n', '').replace('\r', '').replace(' ', '')
                # Only accept lines which do not start with "#", are not empty and contain a "="
                if (not (line.startswith('#') or len(line) == 0)) and '=' in line:
                    # Split into key and value
                    line = line.split('=')
                    if len(line) == 2:
                        if ',' in line[1]:
                            Player.Properties.defaultProperties[line[0]] = tuple([int(i) for i in line[1].split(',')])
                        else:
                            try:
                                Player.Properties.defaultProperties[line[0]] = int(line[1])
                            except:
                                Player.Properties.defaultProperties[line[0]] = line[1] 
        # Static
        Load = staticmethod(Load)
          
        
        def __setitem__(self, key, value):
            '''Store a property from a player related to the given key.
            
            You can define default properties in the Properties.res file, which can be found at "cstrike/addons/eventscripts/meowrpg/Includes".'''
            
            dict.__setitem__(self, key, value) 
          
    
        def __getitem__(self, key):
            '''Returns a property of a player related to the given key.
            
            You can find default properties in the Properties.res file, which can be found at "cstrike/addons/eventscripts/meowrpg/Includes".'''
            
            if key in self.keys():
                return dict.__getitem__(self, key)
            else:
                try:
                    return Player.Properties.defaultProperties[key]
                except:
                    return None
    
    # Load defaullt properties (static)                
    LoadDefaultProperties = staticmethod(Properties.Load)        
        
 
    def __init__(self, userid):
        # Some settings 
        self.userid = userid
        self.name = es.getplayername(self.userid)
        self.player = playerlib.getPlayer(self.userid) 
        self.steamid = es.getplayersteamid(self.userid)      
        
        self.premium = internet.IsPremium(self.steamid) and config.GetBool('rpgPremium')
        if self.premium:
            self.premiumExpire = internet.GetPremiumExpire(self.steamid)
            self.premiumAmount = 2
        else:
            self.premiumAmount = 1
        
        # XP, Level, Credits Language and PopupClose       
        self.xp = 0
        self.totalxp = 0
        self.level = 1
        self.credits = config.GetInt('rpgFirstLevelCredits')
        self.language = 'en'
        self.automaticPopupClose = False
    
        # All skill levels
        self.skills = {} 
        self.skillCredits = {}
        
        # Properties for the skills (like maxhealth ... it's global!)
        self.properties = Player.Properties()
        
        
    # Events
    def Loaded(self):
        # Calculate amount of xp for the next level       
        self.nextLevelXP =  int(config.GetInt('rpgFirstLevelXP') + config.GetFloat('rpgRaiseXPAmount') * (self.level -1))
        
        # Calculate all skill credits
        for i in skillhandler.GetSkills():  
            self.CalculateSkillCredits(i)    
        
        # Create popups
        self.mainPopup = MainPopup(self)
        self.upgradePopup = UpgradePopup(self)
        self.sellPopup = SellPopup(self)    
        self.statisticPopup = StatisticPopup(self)  
        self.settingsPopup = SettingsPopup(self)
        self.languagePopup = LanguagePopup(self)
        self.infoPopup = InfoPopup(self)
        self.helpPopup = HelpPopup(self)
        
    
    def Delete(self):
        self.mainPopup.Delete()
        self.upgradePopup.Delete()
        self.sellPopup.Delete()
        self.statisticPopup.Delete()
        self.settingsPopup.Delete()
        self.languagePopup.Delete()
        self.infoPopup.Delete()
        self.helpPopup.Delete()
        
  
    # Calculate the credits for a skill  
    def CalculateSkillCredits(self, skill):
        # Linear
        if config.GetBool('rpgRaiseCreditLinear'):
            self.skillCredits[skill] = int(config.GetInt('rpg%sCredits' %(skill)) + self.GetSkillLevel(skill) * config.GetFloat('rpg%sAmount' %(skill))) 
            if self.GetSkillLevel(skill) > 0:
                self.skillCredits['%s_sell' %(skill)] = int((config.GetInt('rpg%sCredits' %(skill)) + (self.GetSkillLevel(skill, False)-1) * config.GetFloat('rpg%sAmount' %(skill))) * config.GetFloat('rpgSellAmount'))    
        # Exponential
        else:
            self.skillCredits[skill] = int(config.GetInt('rpg%sCredits' %(skill)) * config.GetFloat('rpg%sAmount' %(skill)) ** self.GetSkillLevel(skill))
            if self.GetSkillLevel(skill) > 0:
                self.skillCredits['%s_sell' %(skill)] = int((config.GetInt('rpg%sCredits' %(skill)) * config.GetFloat('rpg%sAmount' %(skill)) ** (self.GetSkillLevel(skill, False)-1)) * config.GetFloat('rpgSellAmount')) 
           
    
    # Getters  
    def GetNextLevelXP(self):
        '''Returns the amount of xp needed for the next levelup (as integer).'''
        return self.nextLevelXP
    
    
    def GetTotalXP(self):
        '''Returns the total amount of xp a player gained since playing or resetting (as integer).'''
        return self.totalxp
        
    
    def GetLevel(self):
        '''Returns the current level of a player (as integer).'''
        return self.level
        
        
    def GetCredits(self):
        '''Returns the current amount of credits of a player (as integer).'''
        return self.credits
    
         
    def GetAutomaticPopupClose(self):
        return self.automaticPopupClose   
        
        
    def GetSkillLevel(self, skill, checkMax=True):
        '''Returns the current level of the given Skill of a player (as integer).

        Set checkMax to True, if you want to no more than the maximum level defined in the configuration file. Only change that, if you are sure what you are doing! 
        
        As a result of changing the configuration a player can have at least a higher level in a skill than the maximum level of this skill.'''
        
        try:
            if checkMax:
                max = config.GetInt('rpg%sMax' %(skill))
                lvl = self.skills[skill]
                if lvl > max:
                    return max            
                return lvl
            return self.skills[skill]  
        except:
            self.skills[skill] = 0
            return 0        
        
        
    def GetSkillCredits(self, skill):
        '''Returns the amount of credits needed for the next level of given Skill (as integer).''' 
        
        return self.skillCredits[skill]
        
        
    def GetSkillSellCredits(self, skill):
        '''Returns the amount of credits a player recieves when selling a level of the given Skill (as integer).''' 
        
        return self.skillCredits['%s_sell' %(skill)]
        
        
    def GetSkills(self):
        '''Returns a list of Skills, whose level is higher than 0.
        
        The list ist sorted ascending.'''
        
        ret = [i for i in self.skills.keys() if self.skills[i] > 0]
        ret.sort()
        return ret 
        
    def GetLanguage(self):
        return self.language
        
               
    # Setter
    def SetAutomaticPopupClose(self, automaticPopupClose):
        self.automaticPopupClose = automaticPopupClose
        self.settingsPopup.Renew()
        
        
    def SetLanguage(self, language):    
        # Set new language and renew all popups
        self.language = language
        
        self.mainPopup.Renew()
        self.upgradePopup.Renew()
        self.sellPopup.Renew()
        self.statisticPopup.Renew()
        self.settingsPopup.Renew() 
        self.languagePopup.Renew()
        self.infoPopup.Renew()
        self.helpPopup.Renew()
    

    # Raise      
    def RaiseXP(self, amount, noPremium = False):
        '''Adds the given amount to the player's xp.
        
        If you set noPremium to False the amount is doubled, if a player is a premium player.'''
        
        if not noPremium:
            amount *= self.premiumAmount 
        self.xp += amount
        self.totalxp += amount
        while True:
            if self.xp >= self.nextLevelXP:
                self.level += 1
                self.credits += config.GetInt('rpgRaiseCredits') * self.premiumAmount
                self.xp -= self.nextLevelXP
                self.nextLevelXP =  int(config.GetInt('rpgFirstLevelXP') + config.GetFloat('rpgRaiseXPAmount') * (self.level -1))
                
                self.upgradePopup.Renew()
                self.sellPopup.Renew()
            else:
                break   
        self.statisticPopup.Renew()  
          
 
    def RaiseLevel(self, amount):    
        '''Adds the given amount to the players's level.'''
                     
        for i in xrange(amount):
            self.RaiseXP(self.nextLevelXP, True)
            
            
    def RaiseCredits(self, amount):
        '''Adds the given amount to the player's credits.'''
        
        self.credits += amount
        self.upgradePopup.Renew()
        self.sellPopup.Renew()
        self.statisticPopup.Renew() 
        
        
    def RaiseSkillLevel(self, skill):     
        if self.GetSkillCredits(skill) <= self.credits:
            self.credits -= self.GetSkillCredits(skill)
            self.skills[skill] += 1
            self.CalculateSkillCredits(skill)
            
            # Renew popups
            self.upgradePopup.Renew()
            self.sellPopup.Renew()
            
            # Fire event
            es.event('initialize', 'rpg_skill_level_changed')
            es.event('setstring', 'rpg_skill_level_changed', 'userid', self.userid) 
            es.event('setstring', 'rpg_skill_level_changed', 'skill', skill)
            es.event('setstring', 'rpg_skill_level_changed', 'level', self.skills[skill])
            es.event('setstring', 'rpg_skill_level_changed', 'old_level', self.skills[skill] - 1)
            es.event('fire', 'rpg_skill_level_changed')           
            
            return True
        return False   
        
    
    # Popup functions
    def IsSkillMax(self, skill):
        '''Returns True if the given Skill is on it's maximum level, otherwise returns False.'''  
        
        return self.GetSkillLevel(skill) >= config.GetInt('rpg%sMax' %(skill)) 
        
        
    def HasSkillCredits(self, skill):
        return self.credits >= self.GetSkillCredits(skill)

          
    # Decrement
    def DecrementSkillLevel(self, skill, useSellValue = True):
        if self.GetSkillLevel(skill) > 0:
            self.skills[skill] -= 1
            self.CalculateSkillCredits(skill)
            if useSellValue:
                self.credits += int(self.GetSkillCredits(skill) * config.GetFloat('rpgSellAmount'))
            else:
                self.credits += self.GetSkillCredits(skill) 
                
            # Renew popups
            self.upgradePopup.Renew()
            self.sellPopup.Renew()
            self.statisticPopup.Renew()  
            
            # Fire event
            es.event('initialize', 'rpg_skill_level_changed')
            es.event('setstring', 'rpg_skill_level_changed', 'userid', self.userid) 
            es.event('setstring', 'rpg_skill_level_changed', 'skill', skill)
            es.event('setstring', 'rpg_skill_level_changed', 'level', self.skills[skill])
            es.event('setstring', 'rpg_skill_level_changed', 'old_level', self.skills[skill] + 1)
            es.event('fire', 'rpg_skill_level_changed')
                      
 
    #Reset
    def Reset(self):
        '''Resets the whole achievements of a player (xp, level, Skills and credits). 

        Handle with care!'''
        
        # Reset the savings
        self.xp = 0
        self.totalxp = 0
        self.level = 1
        self.credits = config.GetInt('rpgFirstLevelCredits')
        
        for i in self.skills.keys():
            # Fire event
            es.event('initialize', 'rpg_skill_level_changed')
            es.event('setstring', 'rpg_skill_level_changed', 'userid', self.userid) 
            es.event('setstring', 'rpg_skill_level_changed', 'skill', i)
            es.event('setstring', 'rpg_skill_level_changed', 'level', 0)
            es.event('setstring', 'rpg_skill_level_changed', 'old_level', self.skills[i])
            es.event('fire', 'rpg_skill_level_changed')
            
        self.skills.clear()
        
        # Recalculate the xp for the next level
        self.nextLevelXP =  int(config.GetInt('rpgFirstLevelXP') + config.GetFloat('rpgRaiseXPAmount') * (self.level -1))
        
        # Calculate all skill credits
        for i in skillhandler.GetLoadedSkills():  
            self.CalculateSkillCredits(i)          
        
        # Popups
        self.upgradePopup.Renew()
        self.sellPopup.Renew()
        self.statisticPopup.Renew() 
        
        saving.Store(self)
        
        
# Playerlist (provides a list with all current players on the server)
class Playerlist(object):
    '''This class provides access to all players which are currently online.
    
    You should not create any instance of this class. A instance called "playerlist" is available in the Meow RPG core script.

    Example:

    >>> from meowrpg import playerlist
    >>> player = playerlist[5] # This is a instance of the Player class which contains information about the player with userid 5'''
    
    def __init__(self):
        self.players = {} 
        self.added = set()  
        
    def Add(self, userid):
        userid = int(userid)
        player = Player(userid) 
        self.players[userid] = player 
        saving.Load(player)
        self.added.add(userid)
        
    def Remove(self, userid):
        userid = int(userid)
        self.added.remove(userid)
        player = self.players[userid]  
        saving.Store(player)
        player.Delete()
        del self.players[userid]
        
    def Clear(self):
        for i in self.players.keys():
            self.Remove(i)
    
    def Exists(self, userid):
        return int(userid) in self.added
        
    def __getitem__(self, userid):
        '''Returns a instance of the Player class related to the given userid.'''
        return self.players[int(userid)]
        
    def GetPlayerlist(self):
        return self.players.values()
        
        
# Eventhandler (provides a handling for the most events that matter)
class Eventhandler(object):
    def __init__(self):        
        self.xpGaining = {}
        self.levelGaining = {}
        
        self.advertiseCounter = 0       
        
        
    def OnPlayerDisconnect(self, ev): 
        # Add the player to the ranking
        userid = int(ev['userid'])
        player = playerlist[userid]
        
        try:
            del self.xpGaining[userid]
            del self.levelGaining[userid]
        except:
            pass
        
        
    def OnPlayerSpawn(self, ev):
        # Reset the gainings
        userid = int(ev['userid'])
        player = playerlist[userid]
        self.xpGaining[userid] = 0
        self.levelGaining[userid] = player.GetLevel()   
        
        # Spawnprotection
        player.player.godmode(1)
        gamethread.delayed(0.1, player.player.setColor, (0, 0, 255, 125))
        gamethread.delayed(config.GetFloat('rpgSpawnprotection'), player.player.godmode, 0)
        gamethread.delayed(config.GetFloat('rpgSpawnprotection'), player.player.setColor, player.properties['color'])
          
          
    def OnPlayerHurt(self, ev):
        # Add XP
        if int(ev['health']) > 0 and ev['attacker'] != ev['userid']:
            attacker = playerlist[ev['attacker']]
            victim = playerlist[ev['userid']]
            if attacker.GetLevel() > victim.GetLevel():      
                xp = int(config.GetFloat('rpgGainXPDmg') / 100 * int(ev['dmg_health']))
            else:
                xp = int((victim.GetLevel() / float(attacker.GetLevel())) * config.GetFloat('rpgGainXPDmg') / 100 * int(ev['dmg_health']))
            if es.isbot(ev['userid']):
                xp = int(xp * config.GetFloat('rpgGainXPBotAmount'))         
            attacker.RaiseXP(xp)
            self.xpGaining[attacker.userid] += xp
        
            
    def OnPlayerDeath(self, ev):
        # Add XP
        userid = int(ev['userid'])
        victim = playerlist[userid]
        if ev['attacker'] != ev['userid']:
            attacker = playerlist[ev['attacker']]
            headshotMulti = 1.0
            if bool(int(ev['headshot'])):
                headshotMulti = config.GetFloat('rpgGainXPHeadshot') 
            if attacker.GetLevel() > victim.GetLevel():      
                xp = int(config.GetFloat('rpgGainXPKill') * headshotMulti)
            else:
                xp = int((victim.GetLevel() / float(attacker.GetLevel())) * config.GetFloat('rpgGainXPKill') * headshotMulti) 
            if es.isbot(ev['userid']):
                xp = int(xp * config.GetFloat('rpgGainXPBotAmount'))        
            attacker.RaiseXP(xp)
            self.xpGaining[attacker.userid] += xp
            
        # If deathmatch, show their advantages in this life and save the player
        if config.GetBool('rpgDeathmatch'):
            #try:
            victimLanguage = victim.language
            level = victim.GetLevel()
            tell(userid, language.GetLanguage('xp_gaining', victimLanguage, {'xp' : self.xpGaining[userid]}))
            if level == self.levelGaining[userid]:
                tell(userid, language.GetLanguage('no_levelup', victimLanguage, {'level' : level})) 
            else:            
                tell(userid, language.GetLanguage('levelup', victimLanguage, {'level' : level})) 
                                
            del self.xpGaining[userid]
            del self.levelGaining[userid] 
               
            saving.Store(victim)                              
            
        # Show announcement for premium
        if not victim.premium: 
            gamethread.delayed(1.5, tell, (userid, language.GetLanguage('premium', victim.language))) 
                      
            
    def OnBombPlanted(self, ev):
        # Add XP
        player = playerlist[ev['userid']]     
        xp = int(player.GetNextLevelXP() * config.GetFloat('rpgGainXPBombPlanted'))
        player.RaiseXP(xp)
        self.xpGaining[player.userid] += xp
        
        
    def OnBombDefused(self, ev):
        # Add XP
        player = playerlist[ev['userid']]     
        xp = int(player.GetNextLevelXP() * config.GetFloat('rpgGainXPBombDefused'))
        player.RaiseXP(xp)
        self.xpGaining[player.userid] += xp 
            
            
    def OnHostageRescued(self, ev):    
        # Add XP
        player = playerlist[ev['userid']]     
        xp = int(player.GetNextLevelXP() * config.GetFloat('rpgGainXPHostageRescued'))
        player.RaiseXP(xp)
        self.xpGaining[player.userid] += xp 
        
        
    def OnRoundStart(self, ev):
        # We need a loop for saving the data (when we use deathmatch) 
        if config.GetBool('rpgDeathmatch'):
            gamethread.delayedname(60, 'rpgDeathmatchLoop', eventhandler.DeathmatchLoop, ())
        update, version = internet.UpdateAvailable()
        if update:
            msg('A new version (%s) is available' %(version))
            msg('Download at: www.meow-rpg.com')
        if config.GetBool('rpgAdvertise'):
            self.advertiseCounter += 1
            if config.GetInt('rpgAdvertise') == self.advertiseCounter:
                for i in playerlist.GetPlayerlist():
                    tell(i.userid, language.GetLanguage('advertise', i.language, {'rpgmenu' : config.GetString('rpgSayMainMenu'), 'rpghelp' : config.GetString('rpgSayHelpMenu')}))
                self.advertiseCounter = 0
            
            
    def OnRoundEnd(self, ev):
        # End the saving loop
        if config.GetBool('rpgDeathmatch'):
            gamethread.cancelDelayed('rpgDeathmatchLoop')
            
        # Show the gainings and add them to the ranking        
        for i in playerlist.GetPlayerlist():
            try:
                userid = i.userid
                currentLanguage = i.language
                level = i.GetLevel()
                
                if i.premium:
                    tell(userid, language.GetLanguage('xp_gaining', currentLanguage, {'xp' : self.xpGaining[userid]*2}))
                else:
                    tell(userid, language.GetLanguage('xp_gaining', currentLanguage, {'xp' : self.xpGaining[userid]}))
                if level == self.levelGaining[userid]:
                    tell(userid, language.GetLanguage('no_levelup', currentLanguage, {'level' : level})) 
                else:            
                    tell(userid, language.GetLanguage('levelup', currentLanguage, {'level' : level})) 
            except:
                pass                                
                
        # Clear gainings          
        self.xpGaining.clear()  
        self.levelGaining.clear()
        
        # Store all players (experimental!)
        for i in playerlist.GetPlayerlist(): 
            saving.Store(i) 
        saving.Commit() 
        
            
    def OnMapStart(self, ev):
        if not internet.IsConnected():
            internet.Connect()
        gamethread.delayed(1, internet.RegisterServer, ())  
        internet.CheckVersion()     
        
    
    def DeathmatchLoop(self):
        # A loop for deathmatch
        gamethread.cancelDelayed('rpgDeathmatchLoop')
        gamethread.delayedname(60, 'rpgDeathmatchLoop', eventhandler.DeathmatchLoop, ())
        saving.Commit()
                 
        
        
# CommandHandler (provides a handing for say and cmd commands)
class Commandhandler(object):
    # Events
    def Load(self):
        cmdlib.registerServerCommand('rpg_version', self.OnVersion, 'Return the version of Meow RPG')
        cmdlib.registerServerCommand('rpg_load', self.OnLoad, 'Load a Meow RPG skill')
        cmdlib.registerServerCommand('rpg_unload', self.OnUnload, 'Unload a Meow RPG skill')       
        cmdlib.registerServerCommand('rpg_skills', self.OnSkills, 'Print all the Meow RPG skills')
        cmdlib.registerServerCommand('rpg_debug', self.OnDebug, 'Debug the Meow RPG savings') 
         
        
    def Unload(self):
        cmdlib.unregisterServerCommand('rpg_version')
        cmdlib.unregisterServerCommand('rpg_load')
        cmdlib.unregisterServerCommand('rpg_unload')
        cmdlib.unregisterServerCommand('rpg_skills') 
        cmdlib.unregisterServerCommand('rpg_debug')


    def OnPlayerSay(self, ev):
        userid = int(ev['userid'])
        player = playerlist[userid]
        text = ev['text'].lower()
        # Menus
        if text in config.GetList('rpgSayMainMenu'):
            player.mainPopup.Send()       
        elif text in config.GetList('rpgSayInfoMenu'):
            player.infoPopup.Send()
        elif text in config.GetList('rpgSaySettingsMenu'):
            player.settingsPopup.Send()
        elif text in config.GetList('rpgSayHelpMenu'):
            player.helpPopup.Send()
        # XP Status      
        elif text in config.GetList('rpgSayFastXP'):       
            tell(userid, language.GetLanguage('level_status', player.language, {'level' : player.GetLevel()}))
            tell(userid, language.GetLanguage('xp_status', player.language, {'currentXP' : player.xp, 'nextXP' : player.nextLevelXP})) 
        #Ranks         
        elif text in config.GetList('rpgSayRankMenu'):
            ranking.SendPopup(userid)            
        elif text in config.GetList('rpgSayRankOwn'):
            data = ranking.GetPlace(player.steamid)             
            name = es.getplayername(userid)
            if data != None:
                place = data[0]
                xp = data[1]
                level = data[2]                
                tell(userid, language.GetLanguage('self_rank', player.language, {'place' : place, 'xp' : xp, 'level' : level}))   
                for i in playerlist.GetPlayerlist():
                    if i.userid != userid:
                        tell(i.userid, language.GetLanguage('other_rank', i.language, {'name' : name, 'place' : place, 'xp' : xp, 'level' : level}))      
            else:
                tell(userid, language.GetLanguage('self_no_rank', player.language))
                for i in playerlist.GetPlayerlist():
                    if i.userid != userid:
                        tell(i.userid, language.GetLanguage('other_no_rank', i.language, {'name' : name}))
        elif True in [text.startswith(i) for i in config.GetList('rpgSayRankOwn')]:
            args = ev['text'].split(' ')
            if len(args) != 2:
                tell(userid, language.GetLanguage('wrong_rank', player.language, {'command' : config.GetList('rpgSayRankOwn')[0]}))
            else:
                name = args[1].lower()
                found = False
                for i in playerlist.GetPlayerlist():
                   if name in es.getplayername(i.userid).lower():
                        found = True                       
                        data = ranking.GetPlace(i.steamid)      
                        if data != None: 
                            place = data[0]
                            xp = data[1]
                            level = data[2]
                            name = data[3]
                        
                            for j in playerlist.GetPlayerlist(): 
                                tell(j.userid, language.GetLanguage('other_rank', j.language, {'name' : base64.decodestring(name), 'place' : place, 'xp' : xp, 'level' : level}))  
                if not found:
                    tell(ev['userid'], language.GetLanguage('no_rank_found', player.language))                        
        elif text in config.GetList('rpgSayAdminMenu'):
            if player.steamid in config.GetList('rpgAdmins'):
                adminPopup.Send(userid)  
            else:
                tell(userid, language.GetLanguage('not_authorized', player.language))                           
        
     
    # Methodes    
    def OnVersion(self, args):
        dbg('Version: %s' %(version))
        
        
    def OnLoad(self, args):
        if len(args) != 1:
            dbg('Syntax: rpg_load <skillname>')
        else:
            dbg(skillhandler.Load(args[0]))   
            
            
    def OnUnload(self, args):
        if len(args) != 1:
            dbg('Syntax: rpg_unload <skillname>') 
        else:
            dbg(skillhandler.Unload(args[0]))
            
            
    def OnSkills(self, args):
        dbg('Skills: %s' %(', '.join(skillhandler.skills.keys())))   
        
    
    def OnDebug(self, args):
        # Debug the savings of Meow RPG
        # Especially the ranking
        dbg('Debugging ...') 
        saving.Debug()
        dbg('Debugging successfull') 
        
    
    # Client-Command
    def OnClientCmd(self, userid, args):
        if args != None:
            args = args.split(' ') 
            if args[0] == 'admin':      
                if len(args) > 1 and es.getplayersteamid(userid) in config.GetString('rpgAdmins'):
                    if args[1] in ('xp', 'level', 'credits'): 
                        if len(args) == 4:
                            try:
                                playerUserid = args[2]
                                playerName = es.getplayername(playerUserid)
                                player = playerlist[playerUserid]     
                                adminName = es.getplayername(userid)                          
                                if args[1] == 'xp':
                                    player.RaiseXP(int(args[3]), True)
                                    tell(playerUserid, '%s gave you %s XP' %(adminName, args[3]))
                                    echo(userid, 'You gave %s %s XP' %(playerName, args[3])) 
                                elif args[1] == 'level':
                                    player.RaiseLevel(int(args[3]))
                                    tell(playerUserid, '%s gave you %s Level' %(adminName, args[3]))
                                    echo(userid, 'You gave %s %s Level' %(playerName, args[3])) 
                                else:
                                    player.RaiseCredits(int(args[3]))
                                    tell(playerUserid, '%s gave you %s Credits' %(adminName, args[3]))
                                    echo(userid, 'You gave %s %s Credits' %(playerName, args[3])) 
                            except: 
                                echo(userid, 'Syntax: rpg admin [xp|level|credits] <userid> <amount>')
                        else:
                            echo(userid, 'Syntax: rpg admin [xp|level|credits] <userid> <amount>')
                    elif args[1] == 'reset':
                        if len(args) == 3:
                            try:
                                playerUserid = args[2]
                                playerlist[playerUserid].Reset()
                                tell(playerUserid, '%s resetted you' %(es.getplayername(userid)))
                                echo(userid, 'You resetted %s' %(es.getplayername(playerUserid))) 
                            except:
                                echo(userid, 'Syntax: rpg admin reset <userid>')   
                        else:
                            echo(userid, 'Syntax: rpg admin reset <userid>')
                    else:
                        echo(userid, 'Syntax: rpg admin [xp|level|credits|reset]')
                elif len(args) > 1:
                    echo(userid, language.GetLanguage('not_authorized', playerlist[userid].language))    
                else:
                    echo(userid, 'Syntax: rpg admin [xp|level|credits|reset]')    
            else:
                echo(userid, 'Valid parameters are: admin')     
        else:
            echo(userid, 'Valid parameters are: admin')
        


###############################
#                             #
#   Methodes                  #
#                             #
###############################        
        
# Messages      
def msg(text):
    '''Display a text to all players (like es.msg, but with a prefix for Meow RPG).'''   
    es.msg('#multi', '#green[Meow RPG]#default %s' %(text))
    
def tell(userid, text):
    '''Display a text to the player related to the userid (like es.tell, but with a prefix for Meow RPG).'''   
    es.tell(userid, '#multi', '#green[Meow RPG]#default %s' %(text))
    
def dbg(text):
    '''Display a text in the console of the server (like es.dbgmsg, but with a prefix for Meow RPG).'''   
    es.dbgmsg(0, '[Meow RPG] %s' %(text))
    
def echo(userid, text):
    '''Display a text in the console of the player related to the userid (like usermsg.echo, but with a prefix for Meow RPG).'''   
    usermsg.echo(userid, '[Meow RPG] %s' %(text))           



###############################
#                             #
#   Initialization            #
#                             #
############################### 


# Load load, config and language
config = Config(configPath)             
language = Language(os.path.join(pluginPath, 'Includes'))

# Load internet
internet = Internet()

# Ranking
ranking = Ranking()

# Saving and playerlist
saving = Saving(os.path.join(pluginPath, 'Saving/Saving.rpg'))
playerlist = Playerlist()

# Handler
skillhandler = Skillhandler(os.path.join(pluginPath, 'Skills'))
eventhandler = Eventhandler()
commandhandler = Commandhandler()

# Admin Popup
adminPopup = AdminPopup()



###############################
#                             #
#   Eventhandling             #
#                             #
###############################      
   
# ES-Events
def load():     
    # Load rpg events
    es.loadevents('declare', 'addons/eventscripts/meowrpg/Includes/rpg_events.res')    
    es.loadevents('addons/eventscripts/meowrpg/Includes/rpg_events.res') 
    
    # Register client filter
    es.regclientcmd('rpg', 'meowrpg/ClientFilter', 'All RPG Console commands')    
    
    # Load default properties
    Player.LoadDefaultProperties(os.path.join(pluginPath, 'Includes/properties.res'))       

    # Load important things
    skillhandler.LoadAll()
    commandhandler.Load()
    gamethread.delayed(1, internet.RegisterServer, ()) 
    
    # Add all existing players
    for i in es.getUseridList():
        playerlist.Add(i)
    
    
def unload():
    # Stop deathmatch loop
    if config.GetBool('rpgDeathmatch'):
        gamethread.cancelDelayed('rpgDeathmatchLoop')
    
    # Delete admin popup
    adminPopup.Delete()

    # Unreigster client filter
    es.unregclientcmd('rpg')

    # Close all things
    internet.Close()
    commandhandler.Unload()  
    skillhandler.UnloadAll() 
    saving.Close() 
    
# Server-Events
def es_map_start(ev):  
    es.loadevents('addons/eventscripts/meowrpg/Includes/rpg_events.res')     
    eventhandler.OnMapStart(ev)
    playerlist.Clear()   
    
def server_shutdown(ev):
    # Unload all things
    internet.Close()
    commandhandler.Unload()  
    skillhandler.UnloadAll() 
    saving.Close()

# Player-Events
def player_activate(ev):
    es.server.mp_disable_autokick(ev['userid'])
    playerlist.Add(ev['userid'])
    
def player_disconnect(ev):    
    eventhandler.OnPlayerDisconnect(ev)          
    playerlist.Remove(ev['userid'])     
    
def player_say(ev):
    commandhandler.OnPlayerSay(ev)
            
def player_spawn(ev):      
    if playerlist.Exists(ev['userid']):
        eventhandler.OnPlayerSpawn(ev) 
        
        # We have to execute the custon spawn event
        es.event('initialize', 'rpg_player_spawn')
        es.event('setstring', 'rpg_player_spawn', 'userid', ev['userid']) 
        es.event('setstring', 'rpg_player_spawn', 'es_username', ev['es_username']) 
        es.event('setstring', 'rpg_player_spawn', 'es_steamid', ev['es_steamid']) 
        es.event('setstring', 'rpg_player_spawn', 'es_userteam', ev['es_userteam']) 
        es.event('setstring', 'rpg_player_spawn', 'es_userhealth', ev['es_userhealth']) 
        es.event('setstring', 'rpg_player_spawn', 'es_userarmor', ev['es_userarmor']) 
        es.event('setstring', 'rpg_player_spawn', 'es_userdeaths', ev['es_userdeaths']) 
        es.event('setstring', 'rpg_player_spawn', 'es_userkills', ev['es_userkills']) 
        es.event('fire', 'rpg_player_spawn')      
        
            
def player_hurt(ev):
    eventhandler.OnPlayerHurt(ev)  
              
def player_death(ev):
    eventhandler.OnPlayerDeath(ev)
    
# Round-Events              
def bomb_planted(ev):
    eventhandler.OnBombPlanted(ev)        
        
def bomb_defused(ev):
    eventhandler.OnBombDefused(ev)         
            
def hostage_rescued(ev):    
    eventhandler.OnHostageRescued(ev)    
    
def round_start(ev):
    eventhandler.OnRoundStart(ev)       
            
def round_end(ev):
    eventhandler.OnRoundEnd(ev)     
    
# Client-Command-Filter    
def ClientFilter():
    commandhandler.OnClientCmd(es.getcmduserid(), es.getargs())