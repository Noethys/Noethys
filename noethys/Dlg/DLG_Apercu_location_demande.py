#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Locations_demandes_options
from Utils import UTILS_Config



class Dialog(wx.Dialog):
    def __init__(self, parent, provisoire=False, titre=_(u"Aperçu d'une demande de location"), intro=_(u"Vous pouvez ici créer un aperçu PDF du document sélectionné.")):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        # Bandeau
        if provisoire == True :
            intro += _(u" <FONT COLOR = '#FF0000'>Attention, il ne s'agit que d'un document provisoire avant génération !</FONT>")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Apercu.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_options = CTRL_Locations_demandes_options.CTRL(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)


    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_haut.Add(self.ctrl_options, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        box_parametres.Add(grid_sizer_haut, 0, wx.ALL|wx.EXPAND, 10)

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
        UTILS_Aide.Aide("Imprimerdesdemandes")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def GetParametres(self):
        """ Retourne les paramètres sélectionnés """
        return self.ctrl_options.GetOptions()

        dictParametres = {} 
        
        # Modèle
        dictParametres["IDmodele"] = self.ctrl_modele.GetID() 
        if dictParametres["IDmodele"] == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un modèle !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        dictParametres["nomModele"] = self.ctrl_modele.GetStringSelection()

        return dictParametres


    def OnBoutonOk(self, event):
        # Validaion des paramètres
        dictParametres = self.GetParametres()
        if dictParametres == False :
            return

        # Mémorisation des paramètres
        self.ctrl_options.MemoriserParametres()

        self.EndModal(wx.ID_OK)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, provisoire=True)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
