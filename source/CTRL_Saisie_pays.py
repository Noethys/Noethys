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
import sys
import sqlite3

try: import psyco; psyco.full()
except: pass

    
class SaisiePays(wx.Panel):
    def __init__(self, parent, mode="pays"):
        """ Selection d'un pays ou d'une nationalite """
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.mode = mode # Mode = "pays" ou "nationalite"
        self.IDpays = None
        self.image_pays = wx.StaticBitmap(self, -1, wx.Bitmap("Images/Drapeaux/france.png", wx.BITMAP_TYPE_PNG), size=(22, 20))
        self.bouton_pays = wx.Button(self, -1, "...", size=(20, 20))
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonPays, self.bouton_pays)
        
        self.SetValue(100)

    def __set_properties(self):
        pass

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.image_pays, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_pays, 0, 0, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        
    def SetValue(self, IDpays=None, nomPays=None):
        """ Recherche par l'IDpays ou le nom du pays """
        if IDpays == None and nomPays == None : return
        if IDpays != None : pays = self.Recherche_Pays(IDpays=IDpays) 
        if nomPays != None : pays = self.Recherche_Pays(nomPays=nomPays)
        self.IDpays = pays[0]
        self.image_pays.SetBitmap(wx.Bitmap("Images/Drapeaux/" + pays[1] + ".png", wx.BITMAP_TYPE_PNG))
        self.image_pays.SetToolTipString(u"Pays de naissance : " + pays[2])
        if self.mode == "pays" :
            # Mode pays
            self.bouton_pays.SetToolTipString(u"Cliquez ici pour sélectionner un autre pays de naissance")
            self.image_pays.SetToolTipString(u"Pays de naissance : %s" % pays[2])
        else:
            # Mode nationalité
            self.image_pays.SetToolTipString(u"Nationalité : %s" % pays[3])
            self.bouton_pays.SetToolTipString(u"Cliquez ici pour sélectionner une autre nationalité")
    
    def GetValue(self):
        return self.IDpays

    def Recherche_Pays(self, IDpays=0, nomPays=""):
        """ Récupération de la liste des pays dans la base """
        con = sqlite3.connect("Geographie.dat")
        cur = con.cursor()
        if nomPays == "" :
            req = "SELECT IDpays, code_drapeau, nom, nationalite FROM pays WHERE IDpays=%d" % IDpays
        else:
            req = "SELECT IDpays, code_drapeau, nom, nationalite FROM pays WHERE nom='%s'" % nomPays
        cur.execute(req)
        listePays = cur.fetchall()
        con.close()
        if len(listePays) == 0 : return
        return listePays[0]

    def OnBoutonPays(self, event):
        import DLG_Saisie_pays
        dlg = DLG_Saisie_pays.Dialog_pays(None, typeSelection=self.mode)
        if dlg.ShowModal() == wx.ID_OK:
            IDpays = dlg.GetIDpays()
            self.SetValue(IDpays=IDpays)
        dlg.Destroy()


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= SaisiePays(panel)
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