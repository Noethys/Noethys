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
from Ctrl import CTRL_Grille_periode
            

class Dialog(wx.Dialog):
    def __init__(self, parent, dictDonnees = {}):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Choix_periodes", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Périodes
        self.staticbox_periodes_staticbox = wx.StaticBox(self, -1, _(u"Sélectionnez une ou plusieurs périodes"))
        self.ctrl_periodes = CTRL_Grille_periode.CTRL(self)            
        self.ctrl_toutes = wx.CheckBox(self, -1, _(u"Toutes les périodes"))
        
        # Boutons de commandes 
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout() 
        
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckToutes, self.ctrl_toutes)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Applique les valeurs par défaut
        if len(dictDonnees) > 0 :
            self.ctrl_periodes.SetDictDonnees(dictDonnees)

    def __set_properties(self):
        self.SetTitle(_(u"Sélection de périodes"))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((350, 420))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        staticbox_periodes = wx.StaticBoxSizer(self.staticbox_periodes_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.ctrl_periodes, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_toutes, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(0)
        staticbox_periodes.Add(grid_sizer_contenu, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(staticbox_periodes, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnCheckToutes(self, event):
        if self.ctrl_toutes.GetValue() == True :
            self.ctrl_periodes.Enable(False)
        else:
            self.ctrl_periodes.Enable(True)
        
    def GetListePeriodes(self):
        if self.ctrl_toutes.GetValue() == True :
            return None
        else:
            return self.ctrl_periodes.GetDatesSelections() 
    
    def GetDictDonnees(self):
        if self.ctrl_toutes.GetValue() == True :
            return None
        else:
            dictDonnees = self.ctrl_periodes.GetDictDonnees()
            return dictDonnees

    def OnBoutonOk(self, event):
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dictDonnees = {
##        "page" : 0,
##        "listeSelections" : [2, 3, 5],
##        "annee" : 2009,
##        "dateDebut" : None,
##        "dateFin" : None,
##        "listePeriodes" : [],
##        "listeActivites" : [1, 17],
        }
    frame_1 = Dialog(None, dictDonnees)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
