#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent      
        
        self.box_contenu_staticbox = wx.StaticBox(self, -1, u"")
        
        self.label_label = wx.StaticText(self, -1, _(u"Label :"))
        self.ctrl_label = wx.TextCtrl(self, -1, u"")
        self.ctrl_label.SetMinSize((300, -1)) 
        
        self.label_visible = wx.StaticText(self, -1, _(u"Visible :"))
        self.ctrl_visible = wx.CheckBox(self, -1, u"")
        self.ctrl_visible.SetValue(True) 
        
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un choix"))
        self.ctrl_label.SetToolTip(wx.ToolTip(_(u"Saisissez ici un label")))
        self.ctrl_visible.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher ce choix")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        box_contenu = wx.StaticBoxSizer(self.box_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_ligne = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_visible, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_visible, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        box_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def SetVisible(self, etat=True):
        self.ctrl_visible.SetValue(etat)
    
    def GetVisible(self):
        return self.ctrl_visible.GetValue()
    
    def SetLabel(self, label=u""):
        self.ctrl_label.SetValue(label)
        
    def GetLabel(self):
        return self.ctrl_label.GetValue() 

    def OnBoutonOk(self, event): 
        label = self.ctrl_label.GetValue() 
        if label == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un label !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
