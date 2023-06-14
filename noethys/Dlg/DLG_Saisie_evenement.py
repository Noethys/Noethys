#!/usr/bin/env python
# -*- coding: utf8 -*-
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
from Ctrl import CTRL_Saisie_heure
from Ctrl import CTRL_Saisie_euros
from Ol import OL_Evenements_tarifs



class Dialog(wx.Dialog):
    def __init__(self, parent, mode="ajout", track_evenement=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.mode = mode
        self.track_evenement = track_evenement

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))

        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")

        self.label_description = wx.StaticText(self, -1, _(u"Description :"))
        self.ctrl_description = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)

        self.label_horaires = wx.StaticText(self, -1, _(u"Horaires :"))
        self.ctrl_heure_debut = CTRL_Saisie_heure.Heure(self)
        self.label_a = wx.StaticText(self, -1, u"à")
        self.ctrl_heure_fin = CTRL_Saisie_heure.Heure(self)

        self.check_limitation_inscrits = wx.CheckBox(self, -1, _(u"Nombre d'inscrits max. :"))
        self.ctrl_limitation_inscrits = wx.SpinCtrl(self, -1, size=(80, -1), min=1, max=99999)

        # Tarification
        self.staticbox_tarification_staticbox = wx.StaticBox(self, -1, _(u"Tarification spécifique"))

        self.radio_tarification_aucune = wx.RadioButton(self, -1, _(u"Aucune"), style=wx.RB_GROUP)

        # Tarification simple
        self.radio_tarification_montant = wx.RadioButton(self, -1, _(u"Tarification simple :"))
        self.label_montant = wx.StaticText(self, -1, _(u"Montant fixe :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)

        # Tarification avancée
        self.radio_tarification_tarif = wx.RadioButton(self, -1, _(u"Tarification avancée :"))
        self.ctrl_tarifs = OL_Evenements_tarifs.ListView(self, id=-1, track_evenement=track_evenement, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_tarifs.SetMinSize((50, 80))
        self.ctrl_tarifs.MAJ()
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckLimitationInscrits, self.check_limitation_inscrits)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTarification, self.radio_tarification_aucune)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTarification, self.radio_tarification_montant)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTarification, self.radio_tarification_tarif)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_tarifs.Supprimer, self.bouton_supprimer)

        # Init
        if mode == "ajout" :
            self.SetTitle(_(u"Saisie d'un évènement"))
        else:
            self.SetTitle(_(u"Modification d'un évènement"))
            self.Importation()
        self.OnCheckLimitationInscrits(None)
        self.OnRadioTarification(None)


    def __set_properties(self):
        self.ctrl_nom.SetMinSize((420, -1))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici l'intitulé de l'évènement (Ex : 'Cinéma', 'Yoga'...)")))
        self.ctrl_description.SetToolTip(wx.ToolTip(_(u"[Optionnel] Saisissez ici une description pour cet évènement")))
        self.ctrl_heure_debut.SetToolTip(wx.ToolTip(_(u"[Optionnel] Saisissez l'heure de début de l'évènement (Ex : 08:30)")))
        self.ctrl_heure_fin.SetToolTip(wx.ToolTip(_(u"[Optionnel] Saisissez l'heure de fin de l'évènement (Ex : 09:30)")))
        self.radio_tarification_aucune.SetToolTip(wx.ToolTip(_(u"Aucune tarification spécifique pour cet évènement")))
        self.radio_tarification_montant.SetToolTip(wx.ToolTip(_(u"Un montant fixe est associé à cet évènement")))
        self.radio_tarification_tarif.SetToolTip(wx.ToolTip(_(u"Un ou plusieurs tarifs avancés sont associés à cet évènement")))
        self.ctrl_montant.SetToolTip(wx.ToolTip(_(u"Saisissez un montant fixe pour cet évènement")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un tarif")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le tarif sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le tarif sélectionné dans la liste")))
        self.check_limitation_inscrits.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour définir un nombre d'inscrits maximal pour cet évènement")))
        self.ctrl_limitation_inscrits.SetToolTip(wx.ToolTip(_(u"Saisissez ici une nombre d'inscrits maximal pour cet évènement")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)

        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)

        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_description, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_description, 0, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_horaires, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_horaires = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_horaires.Add(self.ctrl_heure_debut, 0, 0, 0)
        grid_sizer_horaires.Add(self.label_a, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaires.Add(self.ctrl_heure_fin, 0, 0, 0)
        grid_sizer_horaires.Add( (5, 5), 0, 0, 0)
        grid_sizer_horaires.Add(self.check_limitation_inscrits, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaires.Add(self.ctrl_limitation_inscrits, 0, 0, 0)

        grid_sizer_horaires.AddGrowableCol(3)
        grid_sizer_generalites.Add(grid_sizer_horaires, 1, wx.EXPAND, 0)


        grid_sizer_generalites.AddGrowableCol(1)
        grid_sizer_generalites.AddGrowableRow(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Tarification
        staticbox_tarification = wx.StaticBoxSizer(self.staticbox_tarification_staticbox, wx.VERTICAL)

        grid_sizer_tarification = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Aucune tarification
        grid_sizer_tarification.Add(self.radio_tarification_aucune, 0, 0, 0)

        # Tarification simple
        grid_sizer_tarification.Add(self.radio_tarification_montant, 0, 0, 0)

        grid_sizer_tarification_simple = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_tarification_simple.Add( (12, 12), 0, 0, 0)
        grid_sizer_tarification_simple.Add(self.label_montant, 0, 0, 0)
        grid_sizer_tarification_simple.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_tarification.Add(grid_sizer_tarification_simple, 0, 0, 0)

        # Tarification avancée
        grid_sizer_tarification.Add(self.radio_tarification_tarif, 0, 0, 0)

        grid_sizer_tarification_avancee = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_tarification_avancee.Add( (12, 12), 0, 0, 0)
        grid_sizer_tarification_avancee.Add(self.ctrl_tarifs, 0, wx.EXPAND, 0)
        grid_sizer_tarification_avancee_boutons = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_tarification_avancee_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_tarification_avancee_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_tarification_avancee_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_tarification_avancee.Add(grid_sizer_tarification_avancee_boutons, 0, 0, 0)
        grid_sizer_tarification_avancee.AddGrowableCol(1)
        grid_sizer_tarification_avancee.AddGrowableRow(0)
        grid_sizer_tarification.Add(grid_sizer_tarification_avancee, 0, wx.EXPAND, 0)

        grid_sizer_tarification.AddGrowableCol(0)
        grid_sizer_tarification.AddGrowableRow(4)

        staticbox_tarification.Add(grid_sizer_tarification, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_tarification, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Calendrier")

    def OnRadioTarification(self, event=None):
        self.label_montant.Enable(self.radio_tarification_montant.GetValue())
        self.ctrl_montant.Enable(self.radio_tarification_montant.GetValue())
        self.ctrl_tarifs.Activation(self.radio_tarification_tarif.GetValue())
        self.bouton_ajouter.Enable(self.radio_tarification_tarif.GetValue())
        self.bouton_modifier.Enable(self.radio_tarification_tarif.GetValue())
        self.bouton_supprimer.Enable(self.radio_tarification_tarif.GetValue())

    def OnCheckLimitationInscrits(self, event):
        self.ctrl_limitation_inscrits.Enable(self.check_limitation_inscrits.GetValue())

    def Importation(self):
        self.ctrl_nom.SetValue(self.track_evenement.nom)
        self.ctrl_description.SetValue(self.track_evenement.description)
        self.ctrl_heure_debut.SetHeure(self.track_evenement.heure_debut)
        self.ctrl_heure_fin.SetHeure(self.track_evenement.heure_fin)

        # Capacité max
        if self.track_evenement.capacite_max != None :
            self.check_limitation_inscrits.SetValue(True)
            self.ctrl_limitation_inscrits.SetValue(self.track_evenement.capacite_max)
            self.OnCheckLimitationInscrits(None)

        if self.track_evenement.montant != None :
            self.radio_tarification_montant.SetValue(True)
            self.ctrl_montant.SetMontant(self.track_evenement.montant)

        if len(self.ctrl_tarifs.GetTracksTarifs()) > 0 :
            self.radio_tarification_tarif.SetValue(True)

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour cet évènement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        description = self.ctrl_description.GetValue()
        heure_debut = self.ctrl_heure_debut.GetHeure()
        heure_fin = self.ctrl_heure_fin.GetHeure()

        if heure_debut != None and heure_fin != None and heure_debut > heure_fin :
            dlg = wx.MessageDialog(self, _(u"L'heure de début ne peut pas être supérieure à l'heure de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_debut.SetFocus()
            return False

        # Capacité max
        capacite_max = None
        if self.check_limitation_inscrits.GetValue() == True :
            capacite_max = self.ctrl_limitation_inscrits.GetValue()

        # Tarification simple
        montant = None
        if self.radio_tarification_montant.GetValue() == True :
            montant = self.ctrl_montant.GetMontant()

        # Tarification avancée
        liste_tarifs = []
        if self.radio_tarification_tarif.GetValue() == True :
            liste_tarifs = self.ctrl_tarifs.GetTracksTarifs()
            if len(liste_tarifs) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir au moins un tarif !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Mémorisation des valeurs
        self.track_evenement.nom = nom
        self.track_evenement.description = description
        self.track_evenement.heure_debut = heure_debut
        self.track_evenement.heure_fin = heure_fin
        self.track_evenement.capacite_max = capacite_max
        self.track_evenement.montant = montant
        self.track_evenement.dirty = True
        self.track_evenement.tarifs = liste_tarifs

        self.EndModal(wx.ID_OK)

    def GetTrackEvenement(self):
        return self.track_evenement



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
