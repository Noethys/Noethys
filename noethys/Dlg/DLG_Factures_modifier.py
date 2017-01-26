#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Dlg.DLG_Factures_generation_parametres import CTRL_Lot_factures


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Sélectionnez une ou plusieurs caractéristiques à modifier. Cliquez sur Ok pour appliquer les modifications aux factures sélectionnées.")
        titre = _(u"Modification des caractéristiques des factures")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Facture.png")
        
        # Filtres
        self.check_lot = wx.CheckBox(self, -1, _(u"Lot de factures :"))
        self.ctrl_lot = CTRL_Lot_factures(self)
        self.ctrl_lot.SetMinSize((250, -1))

        self.check_emission = wx.CheckBox(self, -1, _(u"Date d'émission :"))
        self.ctrl_emission = CTRL_Saisie_date.Date2(self)

        self.check_echeance = wx.CheckBox(self, -1, _(u"Date d'échéance :"))
        self.ctrl_echeance = CTRL_Saisie_date.Date2(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_lot)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_emission)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_echeance)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        self.OnCheck(None)
        

    def __set_properties(self):
        self.check_lot.SetToolTipString(_(u"Cochez pour modifier cette caractéristique"))
        self.ctrl_lot.SetToolTipString(_(u"Sélectionnez un lot de factures dans la liste"))
        self.check_emission.SetToolTipString(_(u"Cochez pour modifier cette caractéristique"))
        self.ctrl_emission.SetToolTipString(_(u"Sélectionnez une date d'émission"))
        self.check_echeance.SetToolTipString(_(u"Cochez pour modifier cette caractéristique"))
        self.ctrl_echeance.SetToolTipString(_(u"Sélectionnez une date d'échéance"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=20, hgap=20)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Filtres
        grid_sizer_contenu = wx.FlexGridSizer(rows=10, cols=1, vgap=10, hgap=10)
                
        grid_sizer_lot = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_lot.Add(self.check_lot, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_lot.Add(self.ctrl_lot, 0, wx.EXPAND, 0)
        grid_sizer_lot.AddGrowableCol(1)
        grid_sizer_contenu.Add(grid_sizer_lot, 1, wx.EXPAND, 0)
        
        grid_sizer_emission = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_emission.Add(self.check_emission, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_emission.Add(self.ctrl_emission, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_emission, 1, wx.EXPAND, 0)
        
        grid_sizer_echeance = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_echeance.Add(self.check_echeance, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_echeance.Add(self.ctrl_echeance, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_echeance, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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

    def OnCheck(self, event): 
        self.ctrl_lot.Enable(self.check_lot.GetValue())
        self.ctrl_emission.Enable(self.check_emission.GetValue())
        self.ctrl_echeance.Enable(self.check_echeance.GetValue())
    
    def OnBoutonOk(self, event): 
        # Validation
        dict_valeurs = self.GetValeurs()
        if dict_valeurs == False :
            return False

        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetValeurs(self):
        dict_valeurs = {}

        # Lots de factures
        if self.check_lot.GetValue() == True:
            IDlot = self.ctrl_lot.GetID()
            if IDlot == None:
                dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun lot dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            dict_valeurs["IDlot"] = IDlot

        # Date d'émission
        if self.check_emission.GetValue() == True:
            date_emission = self.ctrl_emission.GetDate()
            if date_emission == None:
                dlg = wx.MessageDialog(self, _(u"La date d'émission saisie n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            dict_valeurs["date_emission"] = date_emission

        # Date d'échéance
        if self.check_echeance.GetValue() == True:
            date_echeance = self.ctrl_echeance.GetDate()
            if date_echeance == None:
                dlg = wx.MessageDialog(self, _(u"La date d'échéance saisie n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            dict_valeurs["date_echeance"] = date_echeance

        if len(dict_valeurs) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez choisir au moins une caractéristique à modifier !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        return dict_valeurs





if __name__ == '__main__':
    app = wx.App(0)
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
