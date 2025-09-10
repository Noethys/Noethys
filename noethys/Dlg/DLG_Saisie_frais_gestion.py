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
from Ctrl import CTRL_Saisie_euros

LISTE_METHODES_ARRONDI = [
    (_(u"Arrondi au centime supérieur"), "centimesup"),
    (_(u"Arrondi au centime inférieur"), "centimeinf"),
    ]


class Dialog(wx.Dialog):
    def __init__(self, parent, dictFrais={}):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_frais_gestion", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.dictFrais = dictFrais
        
        # Méthode de calcul
        self.box_calcul = wx.StaticBox(self, -1, _(u"Méthode de calcul"))
        self.radio_frais_aucun = wx.RadioButton(self, -1, _(u"Aucun"), style=wx.RB_GROUP)
        self.radio_frais_fixe = wx.RadioButton(self, -1, _(u"Montant fixe :"))
        self.ctrl_frais_fixe = CTRL_Saisie_euros.CTRL(self)
        self.radio_frais_prorata = wx.RadioButton(self, -1, _(u"Montant au prorata :"))
        self.ctrl_frais_prorata = wx.TextCtrl(self, -1, u"0.0", style=wx.TE_RIGHT)
        self.label_pourcentage = wx.StaticText(self, -1, u"%")
        listeLabelsArrondis = []
        for labelArrondi, code in LISTE_METHODES_ARRONDI :
            listeLabelsArrondis.append(labelArrondi)
        self.ctrl_frais_arrondi = wx.Choice(self, -1, choices=listeLabelsArrondis)
        self.ctrl_frais_arrondi.SetSelection(0)
        
        # Label de la prestation
        self.box_prestation = wx.StaticBox(self, -1, _(u"Prestation"))
        self.label_frais_label = wx.StaticText(self, -1, _(u"Label :"))
        self.ctrl_frais_label = wx.TextCtrl(self, -1, _(u"Frais de gestion"))
                
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFrais, self.radio_frais_aucun)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFrais, self.radio_frais_fixe)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFrais, self.radio_frais_prorata)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Initialisation des contrôles
        self.Importation()
        self.OnRadioFrais(None)


    def __set_properties(self):
        self.ctrl_frais_fixe.SetMinSize((60, -1))
        self.ctrl_frais_prorata.SetMinSize((50, -1))
        self.radio_frais_aucun.SetToolTip(wx.ToolTip(_(u"Cochez ici si aucun frais de gestion n'est applicable pour ce mode de règlement")))
        self.radio_frais_fixe.SetToolTip(wx.ToolTip(_(u"Cochez ici si des frais d'un montant fixe sont applicables")))
        self.ctrl_frais_fixe.SetToolTip(wx.ToolTip(_(u"Saisissez le montant fixe des frais de gestion")))
        self.radio_frais_prorata.SetToolTip(wx.ToolTip(_(u"Cochez ici si des frais de gestion d'un montant au prorata est applicable")))
        self.ctrl_frais_prorata.SetToolTip(wx.ToolTip(_(u"Saisissez ici le pourcentage du montant du règlement")))
        self.ctrl_frais_arrondi.SetToolTip(wx.ToolTip(_(u"Selectionnez une méthode de calcul de l'arrondi")))
        self.ctrl_frais_label.SetToolTip(wx.ToolTip(_(u"Vous avez ici la possibilité de modifier le label de la prestation qui sera créée pour les frais de gestion")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider la saisie")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler la saisie")))
        self.SetMinSize((350, -1))
        self.SetTitle(_(u"Appliquer des frais de gestion"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Calcul
        staticbox_calcul = wx.StaticBoxSizer(self.box_calcul, wx.VERTICAL)
        
        grid_sizer_calcul = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_calcul_label = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_calcul_prorata = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_calcul_fixe = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)

        grid_sizer_calcul.Add(self.radio_frais_aucun, 0, 0, 0)
        grid_sizer_calcul_fixe.Add(self.radio_frais_fixe, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_calcul_fixe.Add(self.ctrl_frais_fixe, 0, 0, 0)
        grid_sizer_calcul.Add(grid_sizer_calcul_fixe, 1, wx.EXPAND, 0)
        grid_sizer_calcul_prorata.Add(self.radio_frais_prorata, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_calcul_prorata.Add(self.ctrl_frais_prorata, 0, 0, 0)
        grid_sizer_calcul_prorata.Add(self.label_pourcentage, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_calcul_prorata.Add(self.ctrl_frais_arrondi, 0, 0, 0)        
        grid_sizer_calcul.Add(grid_sizer_calcul_prorata, 1, wx.EXPAND, 0)

        staticbox_calcul.Add(grid_sizer_calcul, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_calcul, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 10)
        
        # Prestations
        staticbox_prestation = wx.StaticBoxSizer(self.box_prestation, wx.VERTICAL)
        grid_sizer_prestation = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_prestation.Add(self.label_frais_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_frais_label, 0, wx.EXPAND, 0)
        grid_sizer_prestation.AddGrowableCol(1)

        staticbox_prestation.Add(grid_sizer_prestation, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_prestation, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 10)

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
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnRadioFrais(self, event): 
        if self.radio_frais_aucun.GetValue() == True :
            self.ctrl_frais_fixe.Enable(False)
            self.ctrl_frais_prorata.Enable(False)
            self.label_pourcentage.Enable(False)
            self.ctrl_frais_arrondi.Enable(False)
            self.label_frais_label.Enable(False)
            self.ctrl_frais_label.Enable(False)
        else:
            self.label_frais_label.Enable(True)
            self.ctrl_frais_label.Enable(True)
        
        if self.radio_frais_fixe.GetValue() == True :
            self.ctrl_frais_fixe.Enable(True)
            self.ctrl_frais_fixe.SetFocus()
            self.ctrl_frais_prorata.Enable(False)
            self.label_pourcentage.Enable(False)
            self.ctrl_frais_arrondi.Enable(False)
        
        if self.radio_frais_prorata.GetValue() == True :
            self.ctrl_frais_fixe.Enable(False)
            self.ctrl_frais_prorata.Enable(True)
            self.ctrl_frais_prorata.SetFocus()
            self.label_pourcentage.Enable(True)
            self.ctrl_frais_arrondi.Enable(True)
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Rglements1")

    def OnBoutonOk(self, event): 
        frais_gestion = None
        frais_montant = None 
        frais_pourcentage = None 
        frais_arrondi = None 
        frais_label = None
        if self.radio_frais_fixe.GetValue() == True :
            frais_gestion = "FIXE"
            frais_montant = self.ctrl_frais_fixe.GetMontant()
            validation, erreur = self.ctrl_frais_fixe.Validation()
            if frais_montant == 0.0 or validation == False :
                dlg = wx.MessageDialog(self, _(u"Le montant que vous avez saisi pour les frais de gestion n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_frais_fixe.SetFocus()
                return
        if self.radio_frais_prorata.GetValue() == True :
            frais_gestion = "PRORATA"
            frais_pourcentage = self.ctrl_frais_prorata.GetValue()
            try :
                frais_pourcentage = float(frais_pourcentage) 
            except :
                dlg = wx.MessageDialog(self, _(u"Le pourcentage que vous avez saisi pour les frais de gestion n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_frais_prorata.SetFocus()
                return
            if frais_pourcentage == 0.0 :
                dlg = wx.MessageDialog(self, _(u"Le pourcentage que vous avez saisi pour les frais de gestion n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_frais_prorata.SetFocus()
                return
            frais_arrondi = LISTE_METHODES_ARRONDI[self.ctrl_frais_arrondi.GetSelection()][1]
        if frais_gestion != None :
            frais_label = self.ctrl_frais_label.GetValue() 
            if frais_label == "" :
                dlg = wx.MessageDialog(self, _(u"Le label de prestation que vous avez saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_frais_label.SetFocus()
                return
        
        # Mémorisation
        self.dictFrais = {  
            "frais_gestion" : frais_gestion,
            "frais_montant" : frais_montant,
            "frais_pourcentage" : frais_pourcentage,
            "frais_arrondi" : frais_arrondi,
            "frais_label" : frais_label,
            }
                
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
        
    def Importation(self):
        """ Importation des données """
        if len(self.dictFrais) == 0 :
            return        
        frais_gestion = self.dictFrais["frais_gestion"]
        frais_montant = self.dictFrais["frais_montant"]
        frais_pourcentage = self.dictFrais["frais_pourcentage"]
        frais_arrondi = self.dictFrais["frais_arrondi"]
        frais_label = self.dictFrais["frais_label"]
        
        if frais_gestion == "LIBRE" :
            self.radio_frais_fixe.SetValue(True)
            if frais_montant != None :
                self.ctrl_frais_fixe.SetMontant(frais_montant)
        if frais_gestion == "FIXE" :
            self.radio_frais_fixe.SetValue(True)
            if frais_montant != None :
                self.ctrl_frais_fixe.SetMontant(frais_montant)
        if frais_gestion == "PRORATA" :
            self.radio_frais_prorata.SetValue(True)
            if frais_pourcentage != None :
                self.ctrl_frais_prorata.SetValue(str(frais_pourcentage))
            if frais_arrondi != None :
                index = 0
                for labelArrondi, code in LISTE_METHODES_ARRONDI :
                    if frais_arrondi == code :
                        self.ctrl_frais_arrondi.SetSelection(index)
                    index += 1
        if frais_gestion != None and frais_label != None :
            self.ctrl_frais_label.SetValue(frais_label)

    def GetDictFrais(self):
        return self.dictFrais




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
