#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import CTRL_Bandeau

class Dialog(wx.Dialog):
    def __init__(self, parent, nouveau=False):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        if nouveau == True :
            intro = u"Vous pouvez saisir ici une consommation de type quantité. Tapez la quantité dans le champ de saisie ou utilisez les flèches."
            titre = u"Saisie d'une quantité"
        else:
            intro = u"Vous pouvez modifier ici une consommation de type quantité. Tapez la quantité dans le champ de saisie ou utilisez les flèches."
            titre = u"Modification d'une quantité"
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Ctrl_nombre.png")
        
        self.label_quantite = wx.StaticText(self, -1, u"Quantité : ")
        self.label_quantite.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        
        self.ctrl_quantite = wx.SpinCtrl(self, -1, u"1", min=1, max=1000, style=wx.TE_PROCESS_ENTER)
        self.ctrl_quantite.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        self.ctrl_quantite.SetMinSize((250, 40))
        
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        if nouveau == True :
            self.bouton_supprimer.Enable(False)
            
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnBoutonOk, self.ctrl_quantite)
        
    def __set_properties(self):
        self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer cette consommation")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((350, 110))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=10, vgap=5, hgap=5)
        grid_sizer_contenu.Add(self.label_quantite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_quantite, 0, 0, 0) 
        grid_sizer_contenu.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 20)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
        
    def OnBoutonSupprimer(self, event):
        self.EndModal(3)

    def OnBoutonOk(self, event):
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def SetQuantite(self, quantite=1):
        if quantite == None : 
            quantite = 1
        self.ctrl_quantite.SetValue(quantite)
        wx.CallAfter(self.SetFocusQuantite)
    
    def SetFocusQuantite(self):
        self.ctrl_quantite.SetFocus() 
        self.ctrl_quantite.SetSelection(0, 5)
        
    def GetQuantite(self):
        return self.ctrl_quantite.GetValue()




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
