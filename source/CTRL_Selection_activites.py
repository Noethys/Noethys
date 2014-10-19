#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import GestionDB

    

class CTRL_Groupes(wx.CheckListBox):
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
                nomGroupe = u"Groupe inconnu !"
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
        self.MAJ() 
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
    def __init__(self, parent, afficheToutes=False):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.afficheToutes = afficheToutes
        
        # Contrôles
        self.radio_toutes = wx.RadioButton(self, -1, u"Toutes les activités", style=wx.RB_GROUP)
        if self.afficheToutes == False :
            style = wx.RB_GROUP
        else :
            style = 0
        self.radio_groupes = wx.RadioButton(self, -1, u"Les groupes d'activités suivants :", style=style)
        self.ctrl_groupes = CTRL_Groupes(self)
        self.ctrl_groupes.SetMinSize((200, 50))
        self.radio_activites = wx.RadioButton(self, -1, u"Les activités suivantes :")
        self.ctrl_activites = CTRL_Activites(self)
        self.ctrl_activites.SetMinSize((200, 50))
        
        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_toutes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_groupes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_activites)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.radio_toutes, 0, wx.BOTTOM, 5)
        grid_sizer_base.Add(self.radio_groupes, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_groupes, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_base.Add((1, 1), 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_activites, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_activites, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableRow(5)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        
        # Init Contrôles
        self.ctrl_activites.Enable(self.radio_activites.GetValue())
        self.ctrl_groupes.Enable(self.radio_groupes.GetValue())
        if self.afficheToutes == False :
            self.radio_toutes.Show(False)
        
    def OnRadioActivites(self, event): 
        self.ctrl_activites.Enable(self.radio_activites.GetValue())
        self.ctrl_groupes.Enable(self.radio_groupes.GetValue())
        self.OnCheck()
    
    def Validation(self):
        """ Vérifie que des données ont été sélectionnées """
        if self.afficheToutes == True and self.radio_toutes.GetValue() == True :
            return True
        if len(self.GetActivites()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune activité !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True
    
    def SetActivites(self, listeActivites=[]):
        self.ctrl_activites.SetIDcoches(listeActivites)
        if len(listeActivites) > 0 :
            self.radio_activites.SetValue(True)
            self.OnRadioActivites(None)
        
    def GetActivites(self):
        """ Retourne la liste des IDactivité sélectionnés """
        # Vérifie les activités sélectionnées
        if self.radio_groupes.GetValue() == True :
            listeActivites = self.ctrl_groupes.GetIDcoches()
        else:
            listeActivites = self.ctrl_activites.GetIDcoches()
        return listeActivites
    
    def GetDictActivites(self):
        if self.radio_groupes.GetValue() == True :
            dictActivites = self.ctrl_groupes.GetDictActivites()
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
        if self.radio_groupes.GetValue() == True :
            # Groupe d'activités
            listeTemp = self.ctrl_groupes.GetLabelsGroupes()
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
        elif self.radio_groupes.GetValue() == True :
            mode = "groupes"
            listeID = self.ctrl_groupes.GetIDgroupesCoches()
        else:
            mode = "activites"
            listeID = self.ctrl_activites.GetIDcoches()
        return mode, listeID
    
    def SetValeurs(self, mode="", listeID=[]):
        if mode == "toutes" :
            self.radio_toutes.SetValue(True)
        if mode == "groupes" :
            self.radio_groupes.SetValue(True)
            self.ctrl_groupes.SetIDcoches(listeID)
        if mode == "activites" :
            self.radio_activites.SetValue(True)
            self.ctrl_activites.SetIDcoches(listeID)
        self.OnRadioActivites(None)
            
            
            
            
            
            
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()