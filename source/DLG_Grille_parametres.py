#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import wx.propgrid as wxpg
import sys

import CTRL_Bandeau
import GestionDB



class EditeurAvecBoutons(wxpg.PyTextCtrlEditor):
    def __init__(self):
        wxpg.PyTextCtrlEditor.__init__(self)

    def CreateControls(self, propGrid, property, pos, sz):
        # Create and populate buttons-subwindow
        buttons = wxpg.PGMultiButton(propGrid, sz)

        # Add two regular buttons
        buttons.AddBitmapButton(wx.Bitmap("Images/16x16/Actualiser2.png", wx.BITMAP_TYPE_PNG))
        buttons.GetButton(0).SetToolTipString(u"Cliquez ici pour rétablir la valeur par défaut")
        
        # Create the 'primary' editor control (textctrl in this case)
        wnd = self.CallSuperMethod("CreateControls", propGrid, property, pos, buttons.GetPrimarySize())
        buttons.Finalize(propGrid, pos);
        self.buttons = buttons
        return (wnd, buttons)

    def OnEvent(self, propGrid, prop, ctrl, event):
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            buttons = self.buttons
            evtId = event.GetId()

            if evtId == buttons.GetButtonId(0):
                propGrid.GetPanel().ReinitPropriete(prop)

        return self.CallSuperMethod("OnEvent", propGrid, prop, ctrl, event)





class CTRL_Proprietes(wxpg.PropertyGrid) :
    def __init__(self, parent, listeDonnees=[]):
        wxpg.PropertyGrid.__init__(self, parent, -1, style=wxpg.PG_SPLITTER_AUTO_CENTER)
        self.listeDonnees = listeDonnees

        # Définition des éditeurs personnalisés
        if not getattr(sys, '_PropGridEditorsRegistered', False):
            self.RegisterEditor(EditeurAvecBoutons)
            # ensure we only do it once
            sys._PropGridEditorsRegistered = True
        
        # Remplissage des valeurs               
        for nom, listeProprietes in self.listeDonnees :
            self.Append( wxpg.PropertyCategory(nom) )
        
            for dictTemp in listeProprietes :
                propriete = wxpg.IntProperty(label=dictTemp["label"], name=dictTemp["code"], value=dictTemp["valeur"])
                self.Append(propriete)
                self.SetPropertyAttribute(propriete, "Min", 0)
                self.SetPropertyAttribute(propriete, "Max", 800)
                self.SetPropertyEditor(propriete, "EditeurAvecBoutons")
    
    def ReinitPropriete(self, propriete=None):
        code = propriete.GetName()
        for nom, listeProprietes in self.listeDonnees :
            for dictTemp in listeProprietes :
                if dictTemp["code"] == code :
                    self.SetPropertyValue(propriete, dictTemp["defaut"])
    
    def ReinitTout(self):
        """ Rétablit toutes les valeurs par défaut """
        for nom, listeProprietes in self.listeDonnees :
            for dictTemp in listeProprietes :
                propriete = self.GetPropertyByName(dictTemp["code"])
                self.SetPropertyValue(propriete, dictTemp["defaut"])
        
        
    
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, listeDonnees=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.listeDonnees = listeDonnees
        
        intro = u"Vous pouvez ici modifier les hauteurs de lignes et largeurs des colonnes. Pour rétablir la valeur initiale d'une ligne, cliquez sur celle-ci et cliquez sur le bouton Réinitialiser situé à droite de la colonne."
        titre = u"Paramètres de la grille"
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Configuration2.png")
        
        self.ctrl_proprietes = CTRL_Proprietes(self, listeDonnees)
                
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_reinit = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Reinitialiser.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReinit, self.bouton_reinit)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
    def __set_properties(self):
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_reinit.SetToolTipString(u"Cliquez ici pour rétablir toutes les valeurs par défaut")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((600, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_proprietes, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_reinit, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Optionsdaffichage")

    def OnBoutonReinit(self, event): 
        self.ctrl_proprietes.ReinitTout()

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
        
    def OnBoutonOk(self, event): 
        self.EndModal(wx.ID_OK)
    
    def GetDonnees(self):
        return self.ctrl_proprietes.GetPropertyValues()
        
        
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
