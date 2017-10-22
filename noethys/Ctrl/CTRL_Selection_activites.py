#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import wx.lib.agw.customtreectrl as CT







class CTRL_Groupes(CT.CustomTreeCtrl):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SIMPLE_BORDER) :
        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.activation = True
        self.root = self.AddRoot(_(u"Racine"))
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT ) #CT.TR_AUTO_CHECK_CHILD
        self.EnableSelectionVista(True)
        self.mode_importation = False
        self.dictItems = {}
        
        # Binds
        self.Bind(CT.EVT_TREE_ITEM_CHECKED, self.OnCheck)

    def Activation(self, etat=True):
        """ Active ou désactive le contrôle """
        self.activation = etat
        self.MAJ() 

    def Importation(self):
        listeDonnees = []
        DB = GestionDB.DB()
        req = """SELECT groupes.IDgroupe, groupes.nom, groupes.ordre, activites.IDactivite, activites.nom, activites.date_fin
        FROM groupes
        LEFT JOIN activites ON activites.IDactivite = groupes.IDactivite
        ORDER BY activites.date_fin DESC;"""
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()      
        DB.Close() 
        return listeGroupes

    def MAJ(self):
        anciensCoches = self.GetGroupes() 
        
        self.listeDonnees = self.Importation()
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Données"))
        self.dictItems = {}
        
        # Préparation des données
        dictDonnees = {}
        for IDgroupe, nomGroupe, ordreGroupe, IDactivite, nomActivite, dateFinActivite in self.listeDonnees :
            if dictDonnees.has_key(IDactivite) == False :
                dictDonnees[IDactivite] = {"nom" : nomActivite, "IDactivite" : IDactivite, "dateFinActivite" : dateFinActivite, "groupes" : []}
            dictDonnees[IDactivite]["groupes"].append((ordreGroupe, IDgroupe, nomGroupe))

        # Tri des noms des activités par ordre alpha
        listeActivites = []
        for IDactivite, dictActivite in dictDonnees.iteritems() :
            listeActivites.append((dictActivite["dateFinActivite"], IDactivite))
        listeActivites.sort(reverse=True)         
        
        # Remplissage
        for dateFinActivite, IDactivite in listeActivites :
            
            # Branche activité
            dictActivite = dictDonnees[IDactivite]
            nomActivite = dictActivite["nom"]
            if nomActivite == None : nomActivite = u"Activité inconnue"
            brancheActivite = self.AppendItem(self.root, nomActivite, ct_type=1)
            dictData = {"type" : "activite", "IDactivite" : IDactivite, "nom" : nomActivite}
            self.SetPyData(brancheActivite, dictData)
##            self.SetItemBold(brancheActivite)
            self.dictItems[brancheActivite] = dictData
            
            # Branches groupes
            listeGroupes = dictActivite["groupes"]
            listeGroupes.sort() 
            
            for ordreGroupe, IDgroupe, nomGroupe in listeGroupes :
                brancheGroupe = self.AppendItem(brancheActivite, nomGroupe, ct_type=1)
                dictData = {"type" : "groupe", "IDgroupe" : IDgroupe, "nom" : nomGroupe}
                self.SetPyData(brancheGroupe, dictData)
                self.dictItems[brancheGroupe] = dictData
            
            self.EnableChildren(brancheActivite, False)
            
        if self.activation == False :
            self.EnableChildren(self.root, False)
        
        self.SetGroupes(anciensCoches)
        
    def OnCheck(self, event):
        item = event.GetItem()
        self.Coche(item=item)
    
    def Coche(self, item=None, etat=None):
        """ Coche ou décoche un item """
        dictData = self.GetItemPyData(item)
        itemParent = self.GetItemParent(item)
        
        if etat != None :
            self.CheckItem(item, etat) 
            
        if dictData["type"] == "activite" :
            if self.IsItemChecked(item) :
                self.EnableChildren(item, True)
                if self.mode_importation == False :
                    self.CheckChilds(item, True)
            else :
                self.EnableChildren(item, False)
                self.CheckChilds(item, False)
            
        if dictData["type"] == "groupe" :
            if self.IsItemChecked(item) :
                self.CheckItem(itemParent, True)
            else :
                listeCoches = self.GetCochesItem(itemParent)
                if len(listeCoches) == 0 :
                    self.CheckItem(itemParent, False)
        
    def GetCochesItem(self, item=None):
        """ Renvoie la liste des sous items cochés d'un item parent """
        listeItems = []
        itemTemp, cookie = self.GetFirstChild(item)
        for index in range(0, self.GetChildrenCount(item, recursively=False)) :
            if self.IsItemChecked(itemTemp) :
                dictData = self.GetPyData(itemTemp)
                listeItems.append(dictData)
            itemTemp, cookie = self.GetNextChild(item, cookie)
        return listeItems
    
    def GetGroupes(self):
        """ Renvoie la liste des groupes cochés """
        listeGroupes = []
        for item, dictData in self.dictItems.iteritems() :
            if self.IsItemEnabled(item) and self.IsItemChecked(item) and dictData["type"] == "groupe" :
                listeGroupes.append(dictData["IDgroupe"])
        listeGroupes.sort()
        return listeGroupes
        
    def SetGroupes(self, listeGroupes=[]):
        """ Coche les groupes donnés """
        self.mode_importation = True
        for item, dictData in self.dictItems.iteritems() :
            if dictData["type"] == "groupe" :
                if dictData["IDgroupe"] in listeGroupes :
                    self.Coche(item, etat=True)
                else :
                    self.Coche(item, etat=False)
        self.mode_importation = False
    
    def SetActivites(self, listeActivites=[]):
        """ Coche les activités """
        for item, dictData in self.dictItems.iteritems() :
            if dictData["type"] == "activite" :
                if dictData["IDactivite"] in listeActivites :
                    self.Coche(item, etat=True)
                else :
                    self.Coche(item, etat=False)
        
        
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Groupes_activites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.dictDonnees = {}
        self.dictActivites = {}
        self.dictIndex = {}
        self.listeDonnees = self.Importation()
        if self.listeDonnees == None : 
            self.listeDonnees = []
        self.MAJ() 
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def MAJ(self):
        self.listeDonnees = self.Importation()
        self.Clear()
        self.dictIndex = {}
        if self.listeDonnees == [] : return
        self.listeDonnees.sort()
        index = 0
        for nomGroupe, IDtype_groupe_activite in self.listeDonnees :
            if nomGroupe == None :
                nomGroupe = _(u"Groupe inconnu !")
            self.Append(nomGroupe) 
            self.dictIndex[index] = IDtype_groupe_activite
            index += 1

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDgroupe_activite, groupes_activites.IDactivite, activites.nom, types_groupes_activites.nom, groupes_activites.IDtype_groupe_activite
        FROM groupes_activites
        LEFT JOIN types_groupes_activites ON types_groupes_activites.IDtype_groupe_activite = groupes_activites.IDtype_groupe_activite
        LEFT JOIN activites ON activites.IDactivite = groupes_activites.IDactivite
        ORDER BY types_groupes_activites.nom;"""
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()
        DB.Close()
        if len(listeActivites) == 0 : return []
        listeDonnees = []
        self.dictDonnees = {}
        for IDgroupe_activite, IDactivite, nomActivite, nomGroupe, IDtype_groupe_activite in listeActivites :
            listeTemp = (nomGroupe, IDtype_groupe_activite)
            if listeTemp not in listeDonnees : 
                listeDonnees.append(listeTemp)
            if self.dictDonnees.has_key(IDtype_groupe_activite) == False :
                self.dictDonnees[IDtype_groupe_activite] = []
            self.dictDonnees[IDtype_groupe_activite].append(IDactivite)    
            self.dictActivites[IDactivite] = nomActivite        
        return listeDonnees
    
    def GetDictActivites(self):
        return self.dictActivites
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeDonnees)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                IDtype_groupe_activite = self.dictIndex[index]
                listeActivites = self.dictDonnees[IDtype_groupe_activite]
                for IDactivite in listeActivites :
                    if IDactivite not in listeIDcoches :
                        listeIDcoches.append(IDactivite)
        listeIDcoches.sort() 
        return listeIDcoches

    def GetIDgroupesCoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeDonnees)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                IDtype_groupe_activite = self.dictIndex[index]
                listeIDcoches.append(IDtype_groupe_activite)
        listeIDcoches.sort() 
        return listeIDcoches

    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            ID = self.dictIndex[index]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def OnCheck(self, event):
        self.parent.OnCheck() 
    
    def GetLabelsGroupes(self):
        """ Renvoie les labels des groupes d'activités sélectionnés """
        listeLabels = []
        index = 0
        for nomGroupe, IDtype_groupe_activite in self.listeDonnees :
            if self.IsChecked(index):
                listeLabels.append(nomGroupe)
            index += 1
        return listeLabels

# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Activites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.dictActivites = {}
        self.listeDonnees = []
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def MAJ(self):
        self.listeDonnees = self.Importation()
        self.SetListeChoix()

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        self.dictActivites = {}
        self.dictIndex = {}
        index = 0
        for IDactivite, nom in self.listeDonnees :
            if nom == None : nom = u"Activité inconnue"
            self.Append(nom)
            self.dictIndex[index] = IDactivite
            self.dictActivites[IDactivite] = nom
            index += 1

    def Importation(self):
        listeDonnees = []
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom
        FROM activites
        ORDER BY date_fin DESC
        ;"""
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()      
        DB.Close() 
        return listeActivites
    
    def GetDictActivites(self):
        return self.dictActivites

    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeDonnees)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.dictIndex[index])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            ID = self.dictIndex[index]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def OnCheck(self, event):
        self.parent.OnCheck() 

# -----------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, afficheToutes=False, modeGroupes=False):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.afficheToutes = afficheToutes
        self.modeGroupes = modeGroupes
        
        # Contrôles
        self.radio_toutes = wx.RadioButton(self, -1, _(u"Toutes les activités"), style=wx.RB_GROUP)
        if self.afficheToutes == False :
            style = wx.RB_GROUP
        else :
            style = 0
        self.radio_groupes_activites = wx.RadioButton(self, -1, _(u"Les groupes d'activités suivants :"), style=style)
        self.ctrl_groupes_activites = CTRL_Groupes_activites(self)
        self.ctrl_groupes_activites.SetMinSize((200, 40))
        self.radio_activites = wx.RadioButton(self, -1, _(u"Les activités suivantes :"))
        
        self.ctrl_activites = CTRL_Activites(self)
        self.ctrl_activites.SetMinSize((200, 40))
        
        self.ctrl_groupes = CTRL_Groupes(self)
        self.ctrl_groupes.SetMinSize((200, 40))
        
        if self.modeGroupes == False :
            self.ctrl_activites.MAJ() 
            self.ctrl_activites.Enable(self.radio_activites.GetValue())
        else :
            self.ctrl_groupes.Activation(self.radio_activites.GetValue())
            
        self.ctrl_activites.Show(not self.modeGroupes)
        self.ctrl_groupes.Show(self.modeGroupes)
        
        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_toutes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_groupes_activites)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_activites)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.radio_toutes, 0, wx.BOTTOM, 5)
        grid_sizer_base.Add(self.radio_groupes_activites, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_groupes_activites, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_base.Add((1, 1), 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_activites, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_activites, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_base.Add(self.ctrl_groupes, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableRow(5)
        grid_sizer_base.AddGrowableRow(6)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        
        # Init Contrôles
        self.ctrl_groupes_activites.Enable(self.radio_groupes_activites.GetValue())
        if self.afficheToutes == False :
            self.radio_toutes.Show(False)
        
    def OnRadioActivites(self, event): 
        if self.ctrl_activites.IsShown() :
            self.ctrl_activites.Enable(self.radio_activites.GetValue())
        if self.ctrl_groupes.IsShown() :
            self.ctrl_groupes.Activation(self.radio_activites.GetValue())
        self.ctrl_groupes_activites.Enable(self.radio_groupes_activites.GetValue())
        self.OnCheck()
    
    def Validation(self):
        """ Vérifie que des données ont été sélectionnées """
        if self.afficheToutes == True and self.radio_toutes.GetValue() == True :
            return True
        if self.radio_groupes_activites.GetValue() == True and len(self.GetActivites()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if self.radio_activites.GetValue() == True and ((self.modeGroupes == False and len(self.GetActivites()) == 0) or (self.modeGroupes == True and len(self.GetGroupes()) == 0)) :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True
    
    def SetActivites(self, listeActivites=[]):
        if self.modeGroupes == False :
            self.ctrl_activites.SetIDcoches(listeActivites)
        else :
            self.ctrl_groupes.SetActivites(listeActivites)
        if len(listeActivites) > 0 :
            self.radio_activites.SetValue(True)
            self.OnRadioActivites(None)
        
    def GetActivites(self):
        """ Retourne la liste des IDactivité sélectionnés """
        # Vérifie les activités sélectionnées
        if self.radio_groupes_activites.GetValue() == True :
            listeActivites = self.ctrl_groupes_activites.GetIDcoches()
        else:
            if self.modeGroupes == False :
                listeActivites = self.ctrl_activites.GetIDcoches()
            else :
                listeActivites = []
        return listeActivites
    
    def SetGroupes(self, listeGroupes=[]):
        self.ctrl_groupes.SetGroupes(listeGroupes)
        if len(listeGroupes) > 0 :
            self.radio_activites.SetValue(True)
            self.OnRadioActivites(None)
    
    def GetGroupes(self):
        if self.radio_activites.GetValue() == True and self.modeGroupes == True :
            listeGroupes = self.ctrl_groupes.GetGroupes()
        else:
            listeGroupes = []
        return listeGroupes
        
    def GetDictActivites(self):
        if self.radio_groupes_activites.GetValue() == True :
            dictActivites = self.ctrl_groupes_activites.GetDictActivites()
        else:
            dictActivites = self.ctrl_activites.GetDictActivites()
        return dictActivites
        
    def OnCheck(self):
        try :
            self.parent.OnCheckActivites()
        except :
            pass

    def GetLabelActivites(self):
        """ Renvoie les labels des groupes ou activités sélectionnées """
        if self.radio_groupes_activites.GetValue() == True :
            # Groupe d'activités
            listeTemp = self.ctrl_groupes_activites.GetLabelsGroupes()
        else :
            # Activités
            listeTemp = []
            dictActivites = self.GetDictActivites()
            for IDactivite in self.GetActivites()  :
                listeTemp.append(dictActivites[IDactivite])
        return listeTemp

    def GetValeurs(self):
        """ Retourne les valeurs sélectionnées """
        if self.afficheToutes == True and self.radio_toutes.GetValue() == True :
            mode = "toutes"
            listeID = []
        elif self.radio_groupes_activites.GetValue() == True :
            mode = "groupes"
            listeID = self.ctrl_groupes_activites.GetIDgroupesCoches()
        else:
            mode = "activites"
            if self.modeGroupes == False :
                listeID = self.ctrl_activites.GetIDcoches()
            else :
                listeID = self.ctrl_groupes.GetGroupes()
        return mode, listeID
    
    def SetValeurs(self, mode="", listeID=[]):
        if mode == "toutes" :
            self.radio_toutes.SetValue(True)
        if mode == "groupes" :
            self.radio_groupes_activites.SetValue(True)
            self.ctrl_groupes_activites.SetIDcoches(listeID)
        if mode == "activites" :
            self.radio_activites.SetValue(True)
            if self.modeGroupes == False :
                self.ctrl_activites.SetIDcoches(listeID)
            else :
                self.ctrl_groupes.SetGroupes(listeID)
        self.OnRadioActivites(None)
            
            
            
            
            
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        bouton_test = wx.Button(panel, -1, u"Test")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, modeGroupes=True)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetMinSize((300, 600))
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBouton, bouton_test) 
        
    def OnBouton(self, event):
        self.ctrl.ctrl_groupes.SetGroupes([1, 3])
        print self.ctrl.ctrl_groupes.GetGroupes()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()