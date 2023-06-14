#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
from Ctrl import CTRL_Bouton_image
import GestionDB



class CTRL(wx.Choice):
    def __init__(self, parent, IDcompte_bancaire=None, size=(-1, -1)):
        wx.Choice.__init__(self, parent, -1, size=size) 
        self.parent = parent
        self.IDdefaut = None
        self.MAJ() 
        self.SetID(IDcompte_bancaire)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
        self.SetID(self.IDdefaut)
    
    def GetListeDonnees(self):
        listeItems = []
        self.dictDonnees = {}
        DB = GestionDB.DB()
        req = """SELECT IDcompte, nom, defaut
        FROM comptes_bancaires
        ORDER BY nom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 0
        for IDcompte, nom, defaut in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcompte }
            label = nom
            listeItems.append(label)
            if defaut == 1 :
                self.IDdefaut = IDcompte
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="panel_test")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl1 = CTRL(panel)
        self.ctrl2 = CTRL(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl1, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.ctrl2, 1, wx.ALL|wx.EXPAND, 4)
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