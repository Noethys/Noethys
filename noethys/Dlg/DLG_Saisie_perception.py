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
from Ctrl import CTRL_Saisie_adresse


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent      
        
        self.staticbox_identite_staticbox = wx.StaticBox(self, -1, _(u"Nom"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        self.ctrl_nom.SetMinSize((400, -1))

        self.staticbox_adresse_staticbox = wx.StaticBox(self, -1, _(u"Adresse postale"))
        self.label_service = wx.StaticText(self, -1, _(u"Service :"))
        self.ctrl_service = wx.TextCtrl(self, -1, "")
        self.label_numero = wx.StaticText(self, -1, _(u"Numéro :"))
        self.ctrl_numero = wx.TextCtrl(self, -1, "")
        self.label_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_rue = wx.TextCtrl(self, -1, "")
        self.label_batiment = wx.StaticText(self, -1, _(u"Bâtiment :"))
        self.ctrl_batiment = wx.TextCtrl(self, -1, "")
        self.label_etage = wx.StaticText(self, -1, _(u"Etage :"))
        self.ctrl_etage = wx.TextCtrl(self, -1, "")
        self.label_boite = wx.StaticText(self, -1, _(u"Boîte :"))
        self.ctrl_boite = wx.TextCtrl(self, -1, "")
        self.label_cp = wx.StaticText(self, -1, _(u"CP :"))
        self.ctrl_cp = wx.TextCtrl(self, -1, "")
        self.label_ville = wx.StaticText(self, -1, _(u"Ville :"))
        self.ctrl_ville = wx.TextCtrl(self, -1, "")
        self.label_pays = wx.StaticText(self, -1, _(u"Code pays :"))
        self.ctrl_pays = wx.TextCtrl(self, -1, "")

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une perception"))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Nom de la perception. Exemple : Perception de Brest.")))
        self.ctrl_service.SetToolTip(wx.ToolTip(_(u"Identité du destinataire ou du service. Exemple : Service comptabilité.")))
        self.ctrl_numero.SetToolTip(wx.ToolTip(_(u"Numéro de la voie. Exemple : 14.")))
        self.ctrl_rue.SetToolTip(wx.ToolTip(_(u"Libellé de la voie sans le numéro. Exemple : Rue des alouettes.")))
        self.ctrl_batiment.SetToolTip(wx.ToolTip(_(u"Nom de l'immeuble, du bâtiment ou de la résidence, etc... Exemple : Résidence les acacias.")))
        self.ctrl_etage.SetToolTip(wx.ToolTip(_(u"Numéro de l'étage, de l'annexe, etc... Exemple : Etage 4.")))
        self.ctrl_boite.SetToolTip(wx.ToolTip(_(u"Boîte postale, tri service arrivée, etc... Exemple : BP64.")))
        self.ctrl_cp.SetToolTip(wx.ToolTip(_(u"Code postal. Exemple : 29200.")))
        self.ctrl_ville.SetToolTip(wx.ToolTip(_(u"Nom de la ville. Exemple : BREST.")))
        self.ctrl_pays.SetToolTip(wx.ToolTip(_(u"Code du pays. Exemple : FR.")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Nom
        staticbox_identite = wx.StaticBoxSizer(self.staticbox_identite_staticbox, wx.VERTICAL)
        grid_sizer_identite = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_identite.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_identite.AddGrowableCol(1)
        staticbox_identite.Add(grid_sizer_identite, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_identite, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Adresse
        staticbox_adresse = wx.StaticBoxSizer(self.staticbox_adresse_staticbox, wx.VERTICAL)
        grid_sizer_adresse = wx.FlexGridSizer(rows=9, cols=2, vgap=5, hgap=5)
        grid_sizer_adresse.Add(self.label_service, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_service, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_numero, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_numero, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_rue, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_batiment, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_batiment, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_etage, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_etage, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_boite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_boite, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_cp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_cp, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_ville, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_ville, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_pays, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_pays, 0, wx.EXPAND, 0)
        grid_sizer_adresse.AddGrowableCol(1)
        staticbox_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_adresse, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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

    def GetValeurs(self):
        return {
            "nom": self.ctrl_nom.GetValue(),
            "service": self.ctrl_service.GetValue(),
            "numero": self.ctrl_numero.GetValue(),
            "rue": self.ctrl_rue.GetValue(),
            "batiment": self.ctrl_batiment.GetValue(),
            "etage": self.ctrl_etage.GetValue(),
            "boite": self.ctrl_boite.GetValue(),
            "cp": self.ctrl_cp.GetValue(),
            "ville": self.ctrl_ville.GetValue(),
            "pays": self.ctrl_pays.GetValue(),
        }

    def SetValeurs(self, valeurs={}):
        self.ctrl_nom.SetValue(valeurs["nom"])
        self.ctrl_service.SetValue(valeurs["service"])
        self.ctrl_numero.SetValue(valeurs["numero"])
        self.ctrl_rue.SetValue(valeurs["rue"])
        self.ctrl_batiment.SetValue(valeurs["batiment"])
        self.ctrl_etage.SetValue(valeurs["etage"])
        self.ctrl_boite.SetValue(valeurs["boite"])
        self.ctrl_cp.SetValue(valeurs["cp"])
        self.ctrl_ville.SetValue(valeurs["ville"])
        self.ctrl_pays.SetValue(valeurs["pays"])
    
    def OnBoutonOk(self, event):
        if self.ctrl_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun nom pour cette perception !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Perceptions")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
