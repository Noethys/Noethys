#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx

import CTRL_Saisie_euros

class Dialog(wx.Dialog):
    def __init__(self, parent, IDdeduction=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_deduction", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDdeduction = IDdeduction
        
        if self.IDdeduction == None :
            self.SetTitle(u"Saisie d'une déduction")
        else:
            self.SetTitle(u"Modification d'une déduction")
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, u"")
        self.label_label = wx.StaticText(self, -1, u"Label :")
        self.ctrl_label = wx.TextCtrl(self, -1, u"")
        self.label_montant = wx.StaticText(self, -1, u"Montant :")
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self, font=wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, u""))
        
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.ctrl_label.SetToolTipString(u"Saisissez ici un label pour cette déduction")
        self.ctrl_montant.SetToolTipString(u"Saisissez ici le montant de la déduction")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((400, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        staticbox.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 
    
    def SetLabel(self, label=u""):
        self.ctrl_label.SetValue(label)
        
    def GetLabel(self):
        return self.ctrl_label.GetValue() 

    def SetMontant(self, montant=0.0):
        self.ctrl_montant.SetMontant(montant)
            
    def GetMontant(self):
        return self.ctrl_montant.GetMontant()
    
    def OnBoutonOk(self, event):
        # Vérification des données
        if self.GetLabel() == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un label !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_label.SetFocus()
            return

        if self.GetMontant() == None or self.GetMontant() == 0.0 :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un montant !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDdeduction=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
