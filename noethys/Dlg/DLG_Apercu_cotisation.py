#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Choix_modele
from Utils import UTILS_Config



class Dialog(wx.Dialog):
    def __init__(self, parent, provisoire=False, titre=_(u"Aperçu d'une cotisation"), intro=_(u"Vous pouvez ici créer un aperçu PDF du document sélectionné.")):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        # Bandeau
        if provisoire == True :
            intro += _(u" <FONT COLOR = '#FF0000'>Attention, il ne s'agit que d'un document provisoire avant génération !</FONT>")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Apercu.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        
        self.label_modele = wx.StaticText(self, -1, _(u"Modèle :"))
        self.ctrl_modele = CTRL_Choix_modele.CTRL_Choice(self, categorie="cotisation")
        self.ctrl_modele.SetMinSize((260, -1))
        
##        self.check_coupons = wx.CheckBox(self, -1, _(u"Insérer les coupons-réponses"))
##        self.check_codesbarres = wx.CheckBox(self, -1, _(u"Insérer les codes-barres"))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
##        self.check_coupons.SetValue(UTILS_Config.GetParametre("impression_rappels_coupon", defaut=1))
##        self.check_codesbarres.SetValue(UTILS_Config.GetParametre("impression_rappels_codeBarre", defaut=1))


    def __set_properties(self):
        self.ctrl_modele.SetToolTipString(_(u"Sélectionnez ici le modèle de document"))
##        self.check_coupons.SetToolTipString(_(u"Cochez cette case pour insérer les coupons-réponses"))
##        self.check_codesbarres.SetToolTipString(_(u"Cochez cette case pour insérer les codes-barres"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_haut.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_modele, 0, wx.EXPAND, 0)
                
        box_parametres.Add(grid_sizer_haut, 0, wx.ALL|wx.EXPAND, 10)
        
##        grid_sizer_bas = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
##        grid_sizer_bas.Add(self.check_coupons, 0, 0, 0)
##        grid_sizer_bas.Add(self.check_codesbarres, 0, 0, 0)
##        box_parametres.Add(grid_sizer_bas, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def GetParametres(self):
        """ Retourne les paramètres sélectionnés """
        dictParametres = {} 
        
        # Modèle
        dictParametres["IDmodele"] = self.ctrl_modele.GetID() 
        if dictParametres["IDmodele"] == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un modèle !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
##        dictParametres["coupon"] = self.check_coupons.GetValue()
##        dictParametres["codeBarre"] = self.check_codesbarres.GetValue()
        
        return dictParametres


    def OnBoutonOk(self, event): 
        dictParametres = self.GetParametres()
        if dictParametres == False :
            return
        self.EndModal(wx.ID_OK)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, provisoire=True)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
