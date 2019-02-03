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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB

try: import psyco; psyco.full()
except: pass


class CTRL_Choice(wx.Choice):
    def __init__(self, parent, categorie=""):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.categorie = categorie
        self.defaut = None
        self.MAJ() 
    
    def SetCategorie(self, categorie=""):
        self.categorie = categorie
        self.defaut = None
        self.MAJ() 
        self.SetID(self.defaut)
    
    def MAJ(self):
        selectionActuelle = self.GetID()
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
        # Re-sélection après MAJ
        if selectionActuelle != None :
            self.SetID(selectionActuelle)
        else:
            # Sélection par défaut
            self.SetID(self.defaut)
                                        
    def GetListeDonnees(self):
        listeItems = []
        self.dictDonnees = {}
        DB = GestionDB.DB()
        req = """SELECT IDmodele, nom, largeur, hauteur, observations, defaut
        FROM documents_modeles
        WHERE categorie='%s'
        ORDER BY nom;""" % self.categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 0
        for IDmodele, nom, largeur, hauteur, observations, defaut in listeDonnees :
            listeItems.append(nom)
            self.dictDonnees[index] = {"ID" : IDmodele}
            if defaut == 1 :
                self.defaut = IDmodele
            index += 1
        return listeItems

    def SetID(self, ID=None):
        for index, values in self.dictDonnees.items():
            if values != None and values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
            
# -------------------------------------------------------------------------------------------------------------------------------------------
    

def DemandeModele(categorie=""):
    IDmodele = None
    DB = GestionDB.DB()
    req = """SELECT IDmodele, nom, defaut
    FROM documents_modeles
    WHERE categorie='%s'
    ORDER BY nom;""" % categorie
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    listeLabels = []
    indexDefaut = None
    index = 0
    for IDmodele, nom, defaut in listeDonnees :
        listeLabels.append(nom)
        if defaut == 1 :
            indexDefaut = index
        index += 1
    dlg = wx.SingleChoiceDialog(None, _(u"Veuillez sélectionner un modèle dans la liste :"), _(u"Sélection d'un modèle"), listeLabels, wx.CHOICEDLG_STYLE)
    if indexDefaut != None :
        dlg.SetSelection(indexDefaut)        
    if dlg.ShowModal() == wx.ID_OK:
        selection = dlg.GetSelection()
        IDmodele = listeDonnees[selection][0]
        dlg.Destroy()
    else:
        dlg.Destroy()
        dlg = wx.MessageDialog(None, _(u"Sans modèle, l'édition est annulée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return None
    return IDmodele






class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL_Choice(panel, categorie="facture")
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