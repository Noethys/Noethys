#!/usr/bin/env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image

from Data import DATA_Civilites as Civilites
LISTE_CIVILITES = Civilites.LISTE_CIVILITES
    
class Civilite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, choices=self.GetListeCivilites()) 
        self.parent = parent
        self.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici la civilité de l'individu s'il s'agit\nd'un adulte ou le genre s'il s'agit d'un enfant")))
    
    def GetListeCivilites(self):
        self.dictCivilites = {}
        listeCivilites = []
        index = 0
        for rubrique, civilites in LISTE_CIVILITES :
            listeCivilites.append(u"--- %s ---" % rubrique)
            self.dictCivilites[index] = {"ID" : None, "type" : "rubrique", "rubrique" : rubrique, "civilite" : None, "abrege" : None, "photo" : None, "sexe" : None}
            index += 1
            for ID, civiliteLong, civiliteAbrege, photo, sexe in civilites :
                listeCivilites.append(civiliteLong)
                self.dictCivilites[index] = {"ID" : ID, "type" : "civilite", "rubrique" : rubrique, "civilite" : civiliteLong, "abrege" : civiliteAbrege, "photo" : photo, "sexe" : sexe}
                index += 1
        return listeCivilites
    
    def GetIndex(self):
        index = self.GetSelection()
        return index

    def SetID(self, ID=0):
        for index, values in self.dictCivilites.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetIndex()
        if index == -1 : return None
        return self.dictCivilites[index]["ID"]
    
    def GetType(self):
        index = self.GetIndex()
        if index == -1 : return None
        return self.dictCivilites[index]["type"]
    
    def GetRubrique(self):
        index = self.GetIndex()
        if index == -1 : return None
        return self.dictCivilites[index]["rubrique"]
    
    def GetCivilite(self):
        index = self.GetIndex()
        if index == -1 : return None
        return self.dictCivilites[index]["civilite"]

    def GetAbrege(self):
        index = self.GetIndex()
        if index == -1 : return None
        return self.dictCivilites[index]["abrege"]
        
    def GetPhoto(self):
        index = self.GetIndex()
        if index == -1 : return None
        return self.dictCivilites[index]["photo"]
    
    def GetSexe(self):
        index = self.GetIndex()
        if index == -1 : return None
        return self.dictCivilites[index]["sexe"]




class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Civilite(panel)
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