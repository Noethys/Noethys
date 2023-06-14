#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import datetime
import GestionDB

from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros



class Dialog(wx.Dialog):
    def __init__(self, parent, nomTypeCotisation=u"", dictDonnees={}):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_unite_cotisation", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDunite_cotisation = None
        self.defaut = 0
        self.nomTypeCotisation = nomTypeCotisation
        self.dictDonnees = dictDonnees
        
        # Nom
        self.staticbox_nom_staticbox = wx.StaticBox(self, -1, _(u"Nom de l'unité"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        # Dates validité
        self.staticbox_validite_staticbox = wx.StaticBox(self, -1, _(u"Dates de validité"))

        self.radio_periode = wx.RadioButton(self, -1, _(u"La période suivante : "), style=wx.RB_GROUP)

        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        self.radio_duree = wx.RadioButton(self, -1, _(u"La durée suivante : "))

        self.label_jours = wx.StaticText(self, -1, _(u"Jours :"))
        self.spin_jours = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.label_mois = wx.StaticText(self, -1, _(u"Mois :"))
        self.spin_mois = wx.SpinCtrl(self, -1, "", min=0, max=100)
        self.label_annees = wx.StaticText(self, -1, _(u"Années :"))
        self.spin_annees = wx.SpinCtrl(self, -1, "", min=0, max=100)

        # Prestation
        self.staticbox_prestation_staticbox = wx.StaticBox(self, -1, _(u"Prestation"))
        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        self.label_label_prestation = wx.StaticText(self, -1, _(u"Label de la\nprestation :"), style=wx.ALIGN_RIGHT)
        self.radio_label_defaut = wx.RadioButton(self, -1, _(u"Par défaut :"), style=wx.RB_GROUP)
        self.ctrl_label_defaut = wx.StaticText(self, -1, u"")
        self.radio_label_personnalise = wx.RadioButton(self, -1, _(u"Personnalisé :"))
        self.ctrl_label_personnalise = wx.TextCtrl(self, -1, u"")
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.OnTextNom, self.ctrl_nom)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLabel, self.radio_label_defaut)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLabel, self.radio_label_personnalise)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioValidite, self.radio_periode)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioValidite, self.radio_duree)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Init contrôles
        if len(dictDonnees) == 0 :
            self.SetTitle(_(u"Saisie d'une nouvelle unité de cotisation"))
            self.SetLabelPrestationDefaut() 
        else:
            self.SetTitle(_(u"Modification d'une unité de cotisation"))
            self.Importation()
        self.OnRadioLabel(None)
        self.OnRadioValidite(None)

    def __set_properties(self):
        self.ctrl_label_defaut.SetForegroundColour((100, 100, 100))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom de l'unité")))
        self.spin_jours.SetMinSize((60, -1))
        self.spin_mois.SetMinSize((60, -1))
        self.spin_annees.SetMinSize((60, -1))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de début de validité")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de fin de validité")))
        self.ctrl_montant.SetToolTip(wx.ToolTip(_(u"Saisissez ici le montant en euros de l'unité de cotisation")))
        self.radio_label_defaut.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour utiliser le label de prestation par défaut")))
        self.radio_label_personnalise.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour utiliser un label de prestation personnalisé")))
        self.ctrl_label_personnalise.SetToolTip(wx.ToolTip(_(u"Saisissez ici un label personnalisé")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((470, 360))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Nom
        staticbox_nom = wx.StaticBoxSizer(self.staticbox_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        staticbox_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Validité
        staticbox_validite = wx.StaticBoxSizer(self.staticbox_validite_staticbox, wx.VERTICAL)

        grid_sizer_validite = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        grid_sizer_validite.Add(self.radio_periode, 0, 0, 0)

        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_validite.Add(grid_sizer_periode, 0, wx.LEFT, 17)

        grid_sizer_validite.Add(self.radio_duree, 0, 0, 0)

        grid_sizer_duree = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_duree.Add(self.label_jours, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_duree.Add(self.spin_jours, 0, 0, 0)
        grid_sizer_duree.Add(self.label_mois, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree.Add(self.spin_mois, 0, 0, 0)
        grid_sizer_duree.Add(self.label_annees, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree.Add(self.spin_annees, 0, 0, 0)
        grid_sizer_validite.Add(grid_sizer_duree, 0, wx.LEFT, 17)

        staticbox_validite.Add(grid_sizer_validite, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_validite, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Prestation
        staticbox_prestation = wx.StaticBoxSizer(self.staticbox_prestation_staticbox, wx.VERTICAL)

        grid_sizer_prestation = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_prestation.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_prestation.Add(self.label_label_prestation, 0, wx.ALIGN_RIGHT, 0)

        grid_sizer_label_prestation = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_label_prestation.Add(self.radio_label_defaut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_label_prestation.Add(self.ctrl_label_defaut, 0, wx.EXPAND, 0)
        grid_sizer_label_prestation.Add(self.radio_label_personnalise, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_label_prestation.Add(self.ctrl_label_personnalise, 0, wx.EXPAND, 0)
        grid_sizer_label_prestation.AddGrowableCol(1)
        grid_sizer_prestation.Add(grid_sizer_label_prestation, 1, wx.EXPAND, 0)

        grid_sizer_prestation.AddGrowableCol(1)
        staticbox_prestation.Add(grid_sizer_prestation, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_prestation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnTextNom(self, event): 
        self.SetLabelPrestationDefaut()

    def OnRadioLabel(self, event): 
        if self.radio_label_defaut.GetValue() == True :
            self.ctrl_label_personnalise.Enable(False)
        else:
            self.ctrl_label_personnalise.Enable(True)
            self.ctrl_label_personnalise.SetFocus() 

    def OnRadioValidite(self, event):
        self.label_date_debut.Enable(self.radio_periode.GetValue())
        self.ctrl_date_debut.Enable(self.radio_periode.GetValue())
        self.label_date_fin.Enable(self.radio_periode.GetValue())
        self.ctrl_date_fin.Enable(self.radio_periode.GetValue())
        self.label_jours.Enable(self.radio_duree.GetValue())
        self.spin_jours.Enable(self.radio_duree.GetValue())
        self.label_mois.Enable(self.radio_duree.GetValue())
        self.spin_mois.Enable(self.radio_duree.GetValue())
        self.label_annees.Enable(self.radio_duree.GetValue())
        self.spin_annees.Enable(self.radio_duree.GetValue())

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Cotisations")

    def OnBoutonOk(self, event):         
        # Vérification des données
        date_debut = None
        date_fin = None
        duree = None

        nom  = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour cette unité de cotisation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        if self.radio_periode.GetValue() == True :
            date_debut = self.ctrl_date_debut.GetDate()
            date_fin = self.ctrl_date_fin.GetDate()

            if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None:
                dlg = wx.MessageDialog(self, _(u"La date de début de validité n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_debut.SetFocus()
                return False

            if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None:
                dlg = wx.MessageDialog(self, _(u"La date de fin de validité n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False

            if date_debut > date_fin:
                dlg = wx.MessageDialog(self, _(u"La date de début de validité est supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        if self.radio_duree.GetValue() == True :
            jours = int(self.spin_jours.GetValue())
            mois = int(self.spin_mois.GetValue())
            annees = int(self.spin_annees.GetValue())

            if jours == 0 and mois == 0 and annees == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez donc saisir un nombre de jours et/ou de mois et/ou d'années."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.spin_jours.SetFocus()
                return False

            duree = "j%d-m%d-a%d" % (jours, mois, annees)

        montant = self.ctrl_montant.GetValue()
        try :
            montant = float(montant)
        except :
            dlg = wx.MessageDialog(self, _(u"Le montant que vous avez saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return False

        if self.radio_label_defaut.GetValue() == True :
            label_prestation = None
        else:
            label_prestation = self.ctrl_label_personnalise.GetValue()

        # Sauvegarde
        self.dictDonnees["IDunite_cotisation"] = self.IDunite_cotisation
        self.dictDonnees["date_debut"] = date_debut
        self.dictDonnees["date_fin"] = date_fin
        self.dictDonnees["duree"] = duree
        self.dictDonnees["defaut"] = self.defaut
        self.dictDonnees["nom"] = nom 
        self.dictDonnees["montant"] = montant
        self.dictDonnees["label_prestation"] = label_prestation
        self.dictDonnees["etat"] = "MODIF"
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetIDunite_cotisation(self):
        return self.IDunite_cotisation
    
    def GetDictDonnees(self):
        return self.dictDonnees
    
    def SetLabelPrestationDefaut(self):
        if self.radio_label_defaut.GetValue() == True :
            label = u"'%s - %s'" % (self.nomTypeCotisation, self.ctrl_nom.GetValue()) 
            self.ctrl_label_defaut.SetLabel(label)
    
    def Importation(self):
        self.IDunite_cotisation = self.dictDonnees["IDunite_cotisation"]
        date_debut = self.dictDonnees["date_debut"]
        date_fin = self.dictDonnees["date_fin"]
        duree = self.dictDonnees["duree"]
        self.defaut = self.dictDonnees["defaut"]
        nom = self.dictDonnees["nom"]
        montant = self.dictDonnees["montant"]
        label_prestation = self.dictDonnees["label_prestation"]

        if date_debut != None and date_fin != None :
            self.radio_periode.SetValue(True)
            self.ctrl_date_debut.SetDate(date_debut)
            self.ctrl_date_fin.SetDate(date_fin)

        if duree != None :
            self.radio_duree.SetValue(True)
            posM = duree.find("m")
            posA = duree.find("a")
            self.spin_jours.SetValue(int(duree[1:posM-1]))
            self.spin_mois.SetValue(int(duree[posM+1:posA-1]))
            self.spin_annees.SetValue(int(duree[posA+1:]))

        self.ctrl_nom.SetValue(nom)
        self.ctrl_montant.SetMontant(montant)
        
        if label_prestation == None :
            self.radio_label_defaut.SetValue(True)
        else:
            self.radio_label_personnalise.SetValue(True)
            self.ctrl_label_personnalise.SetValue(label_prestation)


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
