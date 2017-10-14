# MEOW-RPG by Rennnyyy
# 
# Version 1.0

###################################################################################
#                                                                                 #
#   Do not change anything under this line (except you know what you are doing    #
#                                                                                 #
#   To change the behaviour of this rpg, change its config (cfg/rpg)              #
#                                                                                 #
###################################################################################



###############################
#                             #
#   Includes                  #
#                             #
###############################

# Python includes
import os
import sqlite3 
import time
import pickle
import base64
import socket
import select
import math


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
version = '1.0.0'

# Main paths
pluginPath = os.path.join(os.getcwd(), 'cstrike/addons/eventscripts/rpg')
configPath = os.path.join(os.getcwd(), 'cstrike/cfg/rpg')



###############################
#                             #
#   Classes                   #
#                             #
###############################

# Log (provides a simple log writer)
class Log(object):
    def __init__(self, path):
        # Create a file with the current time
        self.log = file(os.path.join(path, time.strftime('LOG_%d-%m-%y_%H-%M-%S.txt')), 'w')
        
        # Delete old logs (more than 50 are not allowed)
        logs = [i for i in os.listdir(path) if i.startswith('LOG')]
        logs.sort(reverse=True)
        for i in logs[50:len(logs)]:
            os.remove(os.path.join(path, i))
        
        
    def Close(self):
        self.log.close()
        
        
    def Write(self, text):
        self.log.write('%s %s\n' %(time.strftime('[%d %B %Y @ %H:%M]'), text))
        self.log.flush()
        
        
# Config (provides a simple config reader)
class Config(object):
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
        return self.config[key]
        
        
    def GetFloat(self, key):
        return float(self.GetString(key))
        
    
    def GetInt(self, key):
        return int(self.GetString(key))
        
    
    def GetBool(self, key):
        return bool(self.GetInt(key))
        
       
    def HasKey(self, key):
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
            es.server.queuecmd('echo "[MEOW-RPG] Connected to Master Server"')
        except:
            self.connected = False
            
            
    def IsConnected(self):
        return self.connected
        
    
    def RegisterServer(self): 
        if self.connected: 
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
                    return '%s' %(data[1])
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
                        
                        
# Skillhandler (provides a handling for all skills)
class Skillhandler(object):
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
        for i in [i for i in self.skills.keys() if not self.skills[i]]:
            if config.GetBool('rpg%sLoad' %(i)):
                es.server.queuecmd('es_xload rpg/Skills/%s' %(i))
                self.skills[i] = True   
              
                
    def Load(self, skill):
        skill = skill.capitalize()
        if skill in self.skills.keys():
            if not self.skills[skill]:
                es.server.queuecmd('es_xload rpg/Skills/%s' %(skill))
                self.skills[skill] = True  
                
                # We have to renew all upgrade popups!
                for i in playerlist.GetPlayerlist():
                    i.upgradePopup.Renew()
                
                return 'Loaded skill: "%s"' %(skill)
            return 'Skill "%s" already loaded' %(skill)
        return 'Skill "%s" does not exist: See rpg_skills for further details' %(skill)
                
    
    def UnloadAll(self):
        for i in [i for i in self.skills.keys() if self.skills[i]]:
            es.server.queuecmd('es_xunload rpg/Skills/%s' %(i))
            self.skills[i] = False  
            
            
    def Unload(self, skill):
        skill = skill.capitalize()
        if skill in self.skills.keys():
            if self.skills[skill]:
                es.server.queuecmd('es_xunload rpg/Skills/%s' %(skill))
                self.skills[skill] = False
                
                # We have to renew all upgrade popups!
                for i in playerlist.GetPlayerlist():
                    i.upgradePopup.Renew()
                 
                return 'Unloaded skill: "%s"' %(skill) 
            return 'Skill "%s" already unloaded' %(skill)
        return 'Skill "%s" does not exist: See rpg_skills for further details' %(skill)
 
 
    def IsLoaded(self, skill):
        try:
            return self.skills[skill.capitalize()]
        except:
            return False
        
        
    def GetLoadedSkills(self):
        ret = [i for i in self.skills.keys() if self.skills[i]]
        ret.sort()
        return ret
        

    def GetSkills(self):
        ret = [i for i in self.skills.keys()]
        ret.sort()
        return ret
        
        
# Ranking Details
class RankingDetails(object):
    def __init__(self, steamid, name, xp, level):
        self.steamid = steamid
        self.name = name  
        self.xp = xp
        self.level = level
            
            
    def Update(self, name, xp, level):   
        self.name = name  
        self.xp = xp
        self.level = level 
        

# Ranking (provides saving and displaying the ranking of all players)
class Ranking(object):   
    def __init__(self, path):
        self.path = path
       
        self.ranking = {}
        
        self.currentRank = []

        # Try to load the old ranking
        try:
            self.Load()
        except:
            pass 
            
            
    def Load(self):
        # Load ranking from the pickled file
        f = file(self.path)
        self.ranking = pickle.load(f)
        f.close()   
        
        self.Update()
        
        
    def Store(self):
        # Store current ranking in a pickled file
        f = file(self.path, 'w')      
        pickle.dump(self.ranking, f)       
        f.close()    
        
        
    def UpdatePlayer(self, steamid, name, xp, level):
        # Update a existing player or create a new one
        try:
            self.ranking[steamid].Update(name, xp, level)
        except:
            self.ranking[steamid] = RankingDetails(steamid, name, xp, level)


    def DeletePlayer(self, steamid):
        del self.ranking[steamid]
        
        
    def Update(self):
        # Update the whole current ranking
        self.currentRanking = sorted(self.ranking.values(), key=lambda tmp: tmp.xp, reverse=True)
        

    # Getters
    def GetPlace(self, steamid):
        for i in xrange(len(self.currentRanking)):
            if self.currentRanking[i].steamid == steamid:
                return i+1    
       
                
    def GetDetails(self, place):
        return self.currentRanking[place-1] 
        

    # Send the popup
    def SendPopup(self, userid):
        if popuplib.exists('rpg_record'):
            popuplib.delete('rpg_record')
        popup = popuplib.create('rpg_record')
        popup.addline('[MEOW-RPG] Top 10')
        for i in range(10):
            try:
                details = self.currentRanking[i]
                popup.addline('%s. %s - %s XP' %(i+1, details.name, details.xp))
            except:
                popup.addline('%s. Empty - 0 XP' %(i+1))  
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
        self.popup.addline('[MEOW-RPG] Main')
        self.popup.addline('->1. %s' %(language.GetLanguage('upgrade', self.language)))  
        self.popup.addline('->2. %s' %(language.GetLanguage('sell', self.language)))  
        self.popup.addline('->3. %s' %(language.GetLanguage('statistic', self.language)))  
        self.popup.addline('->4. %s' %(language.GetLanguage('settings', self.language)))  
        self.popup.addline('->5. %s' %(language.GetLanguage('information', self.language)))   
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
        if choice in (6,7,8,9):
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
        self.popup = MultiPopup(self.language, self.popupname, ('[MEOW-RPG] %s' %(language.GetLanguage('upgrade', self.language)), language.GetLanguage('current_credits', self.language, {'credits' : self.player.GetCredits()})), self.Menuselect) 
  
        for i in skillhandler.GetLoadedSkills():
            if not self.player.IsSkillMax(i):
                self.popup.AddOption(language.GetLanguage('upgrade_level', self.language, {'skill' : i, 'level' : self.player.GetSkillLevel(i) + 1, 'cost' : self.player.GetSkillCredits(i)}), i, self.player.HasSkillCredits(i))
        
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
        self.popup = MultiPopup(self.language, self.popupname, ('[MEOW-RPG] %s' %(language.GetLanguage('sell', self.language)),  language.GetLanguage('current_credits', self.language, {'credits' : self.player.GetCredits()})), self.Menuselect) 
        
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
        self.popup.addline('[MEOW-RPG] %s' %(language.GetLanguage('statistic', self.language)))
        self.popup.addline('Level: %s' %(self.player.GetLevel()))
        self.popup.addline('XP Status: %s/%s' %(self.player.xp, self.player.nextLevelXP))
        self.popup.addline('Credits: %s' %(self.player.GetCredits()))
        self.popup.addline('Total XP: %s' %(self.player.GetTotalXP()))
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
        self.popup.addline('[MEOW-RPG] %s' %(language.GetLanguage('settings', self.language)))
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
            
        self.popup = MultiPopup(self.language, self.popupname, ('[MEOW-RPG] %s' %(language.GetLanguage('language_headline', self.language)),  language.GetLanguage('language_current', self.language, {'language' : language.GetLanguageByShortcut(self.language)})), self.Menuselect) 
        
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
            
        self.popup = popuplib.create(self.popupname)
        self.popup.addline('[MEOW-RPG] %s' %(language.GetLanguage('information', self.language))) 
        self.popup.addline('->Version: %s' %(version)) 
        self.popup.addline('->Scripter: Rennnyyy')
        self.popup.addline('->Thanks to: DreTax, H4v0c, BackRaw')
        self.popup.addline('->HP: www.meow-rpg.com')
        self.popup.addline('->%s: www.forum.meow-rpg.com' %(language.GetLanguage('bug_report', self.language)))
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
            
            
# InfoPopup (the info popup)           
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
        self.basicPopup.addline('[MEOW-RPG] Admin') 
        self.basicPopup.addline('What do you want to do?')
        self.basicPopup.addline('->1. Give XP')
        self.basicPopup.addline('->2. Give Level')
        self.basicPopup.addline('->3. Give Credits')
        self.basicPopup.addline('->4. Reset a Player')
        self.basicPopup.addline('->0. Exit')
        self.basicPopup.menuselect = self.MenuselectBasic
        
        self.xpAmountPopup = MultiPopup('en', 'rpg_admin_amount', ('[MEOW-RPG] Admin', 'Select an amount of XP'), self.MenuselectAmount) 
        for i in (100,500,1000,2000,5000,10000,50000,100000,500000):
            self.xpAmountPopup.AddOption(str(i), i)
            
        self.levelAmountPopup = MultiPopup('en', 'rpg_admin_amount', ('[MEOW-RPG] Admin', 'Select an amount of Level'), self.MenuselectAmount) 
        for i in (1,5,10,15,20,25,50,100,500):
            self.levelAmountPopup.AddOption(str(i), i)
            
        self.creditsAmountPopup = MultiPopup('en', 'rpg_admin_amount', ('[MEOW-RPG] Admin', 'Select an amount of Credits'), self.MenuselectAmount) 
        for i in (1,5,10,15,20,25,50,100,500):
            self.creditsAmountPopup.AddOption(str(i), i)
     
        
    def CreatePlayerPopup(self, userid):  
        # Delete old popups
        try:
            self.playerPopups[userid].Delete()
        except:
            pass
            
        popup = MultiPopup('en', 'rpg_admin_player', ('[MEOW-RPG] Admin', 'Select a Player'), self.MenuselectPlayer)
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
        self.cursor = self.connection.cursor()
        
        # Create new tabe, if the database was created
        if not exist:
            self.Execute('''CREATE TABLE rpg_version_1_0_0  
                           (steamid text, xp text, totalxp text, level text, credits text, language text, automaticPopupClose text, skills text)''')
            self.connection.commit()

        
    def Close(self):
        for i in playerlist.GetPlayerlist():
            self.Store(i)
    
        self.connection.commit()
        self.connection.close()
                
       
    def Load(self, player):
        # Get the data from the database
        data = self.Execute('SELECT * FROM rpg_version_1_0_0 WHERE steamid = ?', (player.steamid,)) 
        
        # Did we found one?
        found = False
        
        # Add the data to the player
        for i in data:
        
            # XP, Level, Credits, Language and PopupClose are always at the beginning            
            player.xp = int(i[1])
            player.totalxp = int(i[2])
            player.level = int(i[3])
            player.credits = int(i[4])
            player.language = str(i[5])
            player.automaticPopupClose = bool(int(i[6]))
            
            # Split the skill levels
            skills = str(i[7]).split(',')
            for j in skills:
                tmp = j.split('=')
                player.skills[str(tmp[0])] = int(tmp[1]) 
                
            # Yeah, found a player
            found = True          
            break
            
        # Not found
        if not found:
            self.Execute('INSERT INTO rpg_version_1_0_0 VALUES (?, ?, ?, ?, ?, ?, ?, "")', (player.steamid, player.xp, player.totalxp, player.level, player.credits, player.language, int(player.automaticPopupClose)))
            
        # Call the Loaded function of the player
        player.Loaded()
                     
            
    def Store(self, player):
        # Create the skills saving
        tmp = []
        for i in player.skills:
            tmp.append('%s=%s' %(i, player.skills[i]))
        skills = ','.join(tmp)
                
        # Store the data    
        self.Execute('UPDATE rpg_version_1_0_0 SET xp=?, totalxp=?, level=?, credits=?, language=?, automaticPopupClose=?, skills=? WHERE steamid=?', (player.xp, player.totalxp, player.level, player.credits, player.language, int(player.automaticPopupClose), skills, player.steamid))
        self.connection.commit() 
        
        
    def Execute(self, command, args = ()):
        # Call without arguments
        if args == ():
            return self.cursor.execute(command)
        # Call with arguments
        else:
            return self.cursor.execute(command, args) 
            
            
# Player (provides a class for handling the player's attributes)  
class Player(object): 
    # Internal class for properties
    class Properties(dict, object):        
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
                            Player.Properties.defaultProperties[line[0]] = [int(i) for i in line[1].split(',')]
                        else:
                            try:
                                Player.Properties.defaultProperties[line[0]] = int(line[1])
                            except:
                                Player.Properties.defaultProperties[line[0]] = line[1] 
        # Static
        Load = staticmethod(Load)
            
    
        def __getitem__(self, key):
            if key in self.keys():
                return dict.__getitem__(self, key)
            else:
                try:
                    return Properties.defaultProperties[key]
                except:
                    return None
    
    # Load defaullt properties (static)                
    LoadDefaultProperties = staticmethod(Properties.Load)        
        
 
    def __init__(self, userid):
        # Some settings 
        self.userid = userid
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
        
    
    def Delete(self):
        self.mainPopup.Delete()
        self.upgradePopup.Delete()
        self.sellPopup.Delete()
        self.statisticPopup.Delete()
        self.settingsPopup.Delete()
        self.languagePopup.Delete()
        self.infoPopup.Delete()
        
  
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
        return self.nextLevelXP
    
    
    def GetTotalXP(self):
        return self.totalxp
        
    
    def GetLevel(self):
        return self.level
        
        
    def GetCredits(self):
        return self.credits
    
         
    def GetAutomaticPopupClose(self):
        return self.automaticPopupClose   
        
        
    def GetSkillLevel(self, skill, checkMax=True):
        # If the skill is not listed, we add it with level 0
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
        return self.skillCredits[skill]
        
        
    def GetSkillSellCredits(self, skill):
        return self.skillCredits['%s_sell' %(skill)]
        
        
    def GetSkills(self):
        ret = [i for i in self.skills.keys() if self.skills[i] > 0]
        ret.sort()
        return ret 
        
               
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
    

    # Raise      
    def RaiseXP(self, xp, noPremium = False):
        if not noPremium:
            xp *= self.premiumAmount 
        self.xp += xp
        self.totalxp += xp
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
          
 
    def RaiseLevel(self, level):               
        for i in xrange(level):
            self.RaiseXP(self.nextLevelXP, True)
            
            
    def RaiseCredits(self, credits):
        self.credits += credits
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
    def __init__(self):
        self.players = {}   
        
    def Add(self, userid):
        userid = int(userid)
        player = Player(userid) 
        self.players[userid] = player 
        saving.Load(player)
        
    def Remove(self, userid):
        player = self.players[int(userid)]  
        saving.Store(player)
        player.Delete()
        del self.players[int(userid)]
        
    def Clear(self):
        for i in self.players.keys():
            self.Remove(i)
        
    def __getitem__(self, key):
        return self.players[int(key)]
        
    def GetPlayerlist(self):
        return self.players.values()
        
        
# Eventhandler (provides a handling for the most events that matter)
class Eventhandler(object):
    def __init__(self):        
        self.xpGaining = {}
        self.levelGaining = {}
        
        self.saveMod = 0       
        
        
    def OnPlayerDisconnect(self, ev): 
        # Add the player to the ranking
        userid = int(ev['userid'])
        player = playerlist[userid]
        ranking.UpdatePlayer(player.steamid, es.getplayername(userid), player.GetTotalXP(), player.GetLevel()) 
        
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
        gamethread.delayed(config.GetFloat('rpgSpawnprotection'), player.player.godmode, 0)
          
          
    def OnPlayerHurt(self, ev):
        # Add XP
        if int(ev['health']) > 0 and ev['attacker'] != ev['userid']:
            attacker = playerlist[ev['attacker']]
            victim = playerlist[ev['userid']]
            if attacker.GetLevel() > victim.GetLevel():      
                xp = int(config.GetFloat('rpgGainXPDmg') / 100 * int(ev['dmg_health']))
            else:
                xp = int((victim.GetLevel() / float(attacker.GetLevel())) * config.GetFloat('rpgGainXPDmg') / 100 * int(ev['dmg_health']))         
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
            attacker.RaiseXP(xp)
            self.xpGaining[attacker.userid] += xp
            
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
        update, version = internet.UpdateAvailable()
        if update:
            msg('A new version (%s) is available' %(version))
            msg('Download at: www.nem-rpg.com') 
            
            
    def OnRoundEnd(self, ev):
        # Show the gainings and add them to the ranking
        for i in playerlist.GetPlayerlist():
            try:
                userid = i.userid
                currentLanguage = i.language
                level = i.GetLevel()
                
                tell(userid, language.GetLanguage('xp_gaining', currentLanguage, {'xp' : self.xpGaining[userid]}))
                if level == self.levelGaining[userid]:
                    tell(userid, language.GetLanguage('no_levelup', currentLanguage, {'level' : level})) 
                else:            
                    tell(userid, language.GetLanguage('levelup', currentLanguage, {'level' : level})) 
                    
                ranking.UpdatePlayer(i.steamid, es.getplayername(userid), i.GetTotalXP(), level)  
            except:
                pass                                
                
        # Clear gainings          
        self.xpGaining.clear()  
        self.levelGaining.clear()
        
        # Update ranking and save it
        ranking.Update()
        ranking.Store()
        
        # Store all players (experimental!)
        for i in playerlist.GetPlayerlist(): 
            saving.Store(i)  
        
            
    def OnMapStart(self, ev):
        if not internet.IsConnected():
            internet.Connect()
        internet.RegisterServer() 
        internet.CheckVersion()              
        
        
# CommandHandler (provides a handing for say and cmd commands)
class Commandhandler(object):
    # Events
    def Load(self):
        cmdlib.registerServerCommand('rpg_version', self.OnVersion, 'Return the version of MEOW-RPG')
        cmdlib.registerServerCommand('rpg_load', self.OnLoad, 'Load a MEOW-RPG skill')
        cmdlib.registerServerCommand('rpg_unload', self.OnUnload, 'Unload a MEOW-RPG skill') 
        cmdlib.registerServerCommand('rpg_skills', self.OnSkills, 'Print all the MEOW-RPG skills')
         
        
    def Unload(self):
        cmdlib.unregisterServerCommand('rpg_version')
        cmdlib.unregisterServerCommand('rpg_load')
        cmdlib.unregisterServerCommand('rpg_unload')
        cmdlib.unregisterServerCommand('rpg_skills') 


    def OnPlayerSay(self, ev):
        userid = int(ev['userid'])
        player = playerlist[userid]
        # Menus
        if ev['text'] == config.GetString('rpgSayMainMenu'):
            player.mainPopup.Send()       
        elif ev['text'] == config.GetString('rpgSayInfoMenu'):
            player.infoPopup.Send()
        elif ev['text'] == config.GetString('rpgSaySettingsMenu'):
            player.settingsPopup.Send()
        # XP Status      
        elif ev['text'] == config.GetString('rpgSayFastXP'):       
            tell(userid, language.GetLanguage('level_status', player.language, {'level' : player.GetLevel()}))
            tell(userid, language.GetLanguage('xp_status', player.language, {'currentXP' : player.xp, 'nextXP' : player.nextLevelXP})) 
        #Ranks         
        elif ev['text'] == config.GetString('rpgSayRankMenu'):
            ranking.SendPopup(userid)            
        elif ev['text'] == config.GetString('rpgSayRankOwn'):
            place = ranking.GetPlace(player.steamid) 
            name = es.getplayername(userid)
            if place != None:
                details = ranking.GetDetails(place)
                xp = details.xp
                level = details.level
                
                tell(userid, language.GetLanguage('self_rank', player.language, {'place' : place, 'xp' : xp, 'level' : level}))   
                for i in playerlist.GetPlayerlist():
                    if i.userid != userid:
                        tell(i.userid, language.GetLanguage('other_rank', i.language, {'name' : name, 'place' : place, 'xp' : xp, 'level' : level}))      
            else:
                tell(userid, language.GetLanguage('self_no_rank', player.language))
                for i in playerlist.GetPlayerlist():
                    if i.userid != userid:
                        tell(i.userid, language.GetLanguage('other_no_rank', i.language, {'name' : name}))
        elif ev['text'].startswith(config.GetString('rpgSayRankOwn')):
            args = ev['text'].split(' ')
            if len(args) != 2:
                tell(userid, language.GetLanguage('wrong_rank', player.language, {'command' : config.GetString('rpgSayRankOwn')}))
            else:
                name = args[1].lower()
                found = False
                for i in playerlist.GetPlayerlist():
                   if name in es.getplayername(i.userid).lower():
                        found = True
                        
                        place = ranking.GetPlace(i.steamid)
                        details = ranking.GetDetails(place)
                        name = es.getplayername(i.userid)                         
                        xp = details.xp
                        level = details.level
                        
                        for j in playerlist.GetPlayerlist(): 
                            tell(j.userid, language.GetLanguage('other_rank', j.language, {'name' : name, 'place' : place, 'xp' : xp, 'level' : level})) 
                if not found:
                    tell(ev['userid'], language.GetLanguage('no_rank_found', player.language))                        
        elif ev['text'] == config.GetString('rpgSayAdminMenu'):
            if player.steamid in config.GetString('rpgAdmins'):
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
    es.msg('#multi', '#green[MEOW-RPG]#default %s' %(text))
    
def tell(userid, text):
    es.tell(userid, '#multi', '#green[MEOW-RPG]#default %s' %(text))
    
def dbg(text):
    es.dbgmsg(0, '[MEOW-RPG] %s' %(text))
    
def echo(userid, text):
    usermsg.echo(userid, '[MEOW-RPG] %s' %(text))        



###############################
#                             #
#   Initialization            #
#                             #
############################### 

# Load load, config and language
#log = Log(os.path.join(configPath, 'log'))
config = Config(configPath)             
language = Language(os.path.join(pluginPath, 'Includes'))

# Load internet
internet = Internet()

# Ranking
ranking = Ranking(os.path.join(pluginPath, 'Saving/Ranking.rpg'))

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
    es.loadevents('declare', 'addons/eventscripts/rpg/Includes/rpg_events.res')
    
    # Register client filter
    es.regclientcmd('rpg', 'rpg/ClientFilter', 'All RPG Console commands')
    
    # Load default properties
    Player.LoadDefaultProperties(os.path.join(pluginPath, 'Includes/properties.res'))

    # Load important things
    skillhandler.LoadAll()
    commandhandler.Load()
    internet.RegisterServer() 
    
def unload():
    # Delete admin popup
    adminPopup.Delete()

    # Unreigster client filter
    es.unregclientcmd('rpg')

    # Close all things
    internet.Close()
    commandhandler.Unload()  
    skillhandler.UnloadAll() 
    saving.Close()
    #log.Close()   
    
# Server-Events
def es_map_start(ev):       
    eventhandler.OnMapStart(ev)
    playerlist.Clear()   
    
def server_shutdown(ev):
    # Unload all things
    internet.Close()
    commandhandler.Unload()  
    skillhandler.UnloadAll() 
    saving.Close()
    #log.Close()   

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
    eventhandler.OnPlayerSpawn(ev)  
            
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