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

import CTRL_Bandeau
import CTRL_Saisie_euros



class Dialog(wx.Dialog):
    def __init__(self, parent, label=u"", montant=0.0):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        # Bandeau
        intro = u"Vous pouvez ici saisir un montant et un label personnalisés pour la prestation qui va être créée."
        titre = u"Prestation personnalisée"
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
        
        # Label
        self.label_label = wx.StaticText(self, -1, u"Label :")
        self.ctrl_label = wx.TextCtrl(self, -1, label)
        
        # Montant
        self.label_montant = wx.StaticText(self, -1, u"Montant :")
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self, font=wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD, 0, u""), style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER)
        self.ctrl_montant.SetMontant(montant)
        
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnterMontant, self.ctrl_montant)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.ctrl_label.SelectAll()
        self.ctrl_label.SetFocus() 

    def __set_properties(self):
        self.ctrl_label.SetToolTipString(u"Vous pouvez modifier ici un label personnalisé pour la prestation")
        self.ctrl_montant.SetToolTipString(u"Saisissez ici le montant de la prestation et tapez sur la touche Entrée pour valider rapidement")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSize((370, -1))
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event): 
        # Validation du montant
        validation, message = self.ctrl_montant.Validation() 
        if validation == False :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un montant valide pour cette prestation !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return
        # Validation du label
        if self.ctrl_label.GetValue() == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un label pour cette prestation !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_label.SetFocus()
            return
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetMontant(self):
        return self.ctrl_montant.GetMontant() 
    
    def GetLabel(self):
        return self.ctrl_label.GetValue()

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def OnEnterMontant(self, event):
        self.OnBoutonOk(None)
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None, label=u"Cinéma")
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
