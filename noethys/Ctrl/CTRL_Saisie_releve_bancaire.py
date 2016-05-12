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

    
class CTRL_Choix(wx.Choice):
    def __init__(self, parent, IDcompte_bancaire=None):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDcompte_bancaire = IDcompte_bancaire
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        listeItems = [u"",]
        self.dictDonnees = { 0 : {"ID":None}, }
        if self.IDcompte_bancaire == None :
            return listeItems
        DB = GestionDB.DB()
        req = """SELECT IDreleve, nom, date_debut, date_fin
        FROM compta_releves
        WHERE IDcompte_bancaire=%d
        ORDER BY date_debut; """ % self.IDcompte_bancaire
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDreleve, nom, date_debut, date_fin in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDreleve }
            label = nom
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, IDcompte_bancaire=None, afficherBouton=True):
        wx.Panel.__init__(self, parent, id=-1, name="ctrl_saisie_releve_bancaire", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.afficherBouton = afficherBouton
        
        self.ctrl_releve = CTRL_Choix(self, IDcompte_bancaire=IDcompte_bancaire)
        
        if self.afficherBouton == True :
            self.bouton_releve = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
            self.Bind(wx.EVT_BUTTON, self.OnBoutonReleve, self.bouton_releve)
            self.bouton_releve.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des relevés bancaires"))

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_releve, 1, wx.EXPAND|wx.ALL, 0)
        if self.afficherBouton == True :
            grid_sizer_base.Add(self.bouton_releve, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def OnBoutonReleve(self, event):  
        IDreleve = self.ctrl_releve.GetID()
        from Dlg import DLG_Releves_compta
        dlg = DLG_Releves_compta.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_releve.MAJ()
        self.ctrl_releve.SetID(IDreleve)
        
    def SetIDcompte_bancaire(self, IDcompte_bancaire=None):
        self.ctrl_releve.IDcompte_bancaire = IDcompte_bancaire

    def SetID(self, ID=0):
        self.ctrl_releve.SetID(ID)

    def GetID(self):
        return self.ctrl_releve.GetID()
    
    def MAJ(self):
        IDreleve = self.ctrl_releve.GetID()
        self.ctrl_releve.MAJ()
        self.ctrl_releve.SetID(IDreleve)
        
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="panel_test")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl1 = CTRL(panel)
        self.ctrl2 = CTRL(panel, afficherBouton=False)
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