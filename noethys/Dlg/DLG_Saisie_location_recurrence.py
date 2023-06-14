#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_heure
import wx.lib.agw.hyperlink as Hyperlink



class CTRL_Semaines(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.listeEtats = [
            (1, _(u"Toutes les semaines")),
            (2, _(u"Une semaine sur deux")),
            (3, _(u"Une semaine sur trois")),
            (4, _(u"Une semaine sur quatre")),
            (5, _(u"Les semaines paires")),
            (6, _(u"Les semaines impaires")),
        ]
        self.MAJ()

    def MAJ(self):
        listeLabels = []
        for code, label in self.listeEtats:
            listeLabels.append(label)
        self.SetItems(listeLabels)
        self.Select(0)

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeEtats[index][0]

    def GetLabel(self):
        return self.GetStringSelection()

    def SetValeur(self, valeur=1):
        index = 0
        for code, label in self.listeEtats:
            if code == valeur:
                self.Select(index)
            index += 1


# ----------------------------------------------------------------------------------------------------------------------------------

class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent

        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)

    def OnLeftLink(self, event):
        if self.URL == "tout": self.parent.CocherTout()
        if self.URL == "rien": self.parent.CocherRien()
        self.UpdateLink()


class CTRL_Jours(wx.Panel):
    def __init__(self, parent, periode="scolaire"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.periode = periode
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        
        for jour in self.liste_jours :
            setattr(self, "check_%s" % jour, wx.CheckBox(self, -1, jour[0].upper()))
            getattr(self, "check_%s" % jour).SetToolTip(wx.ToolTip(jour.capitalize()))

        self.hyper_tout = Hyperlien(self, label=_(u"Tout"), infobulle=_(u"Cliquez ici pour tout cocher"), URL="tout")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=_(u"Rien"), infobulle=_(u"Cliquez ici pour tout décocher"), URL="rien")

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=10, vgap=0, hgap=0)
        for jour in self.liste_jours :
            grid_sizer_base.Add(getattr(self, "check_%s" % jour), 0, 0, 0)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=3)
        grid_sizer_options.Add(self.hyper_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.hyper_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_options, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

        # Init
        # self.SetJours("0;1;2;3;4;5;6")

    def GetJours(self):
        listeTemp = []
        index = 0
        for jour in self.liste_jours :
            etat = getattr(self, "check_%s" % jour).GetValue()
            if etat == True :
                listeTemp.append(index)
            index += 1
        return listeTemp
    
    def SetJours(self, texteJours=""):
        if texteJours == None :
            return

        if isinstance(texteJours, list) or isinstance(texteJours, tuple):
            listeJours = texteJours
        else:
            listeJoursTemp = texteJours.split(";")
            listeJours = []
            for jour in listeJoursTemp :
                if len(jour) > 0 :
                    listeJours.append(int(jour))
        index = 0
        for jour in self.liste_jours :
            if index in listeJours :
                etat = True
            else :
                etat = False
            getattr(self, "check_%s" % jour).SetValue(etat)
            index += 1

    def CocherTout(self):
        self.SetJours("0;1;2;3;4;5;6")

    def CocherRien(self):
        self.SetJours("")


# ---------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, donnees=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.dictDonnees = {}

        # Période
        self.box_periode_staticbox = wx.StaticBox(self, -1, _(u"Période d'application"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.ctrl_feries = wx.CheckBox(self, -1, _(u"Inclure les fériés"))

        # Heures
        self.box_heures_staticbox = wx.StaticBox(self, -1, _(u"Horaires"))
        self.label_heure_debut = wx.StaticText(self, -1, u"De")
        self.ctrl_heure_debut = CTRL_Saisie_heure.Heure(self)
        self.label_heure_fin = wx.StaticText(self, -1, _(u"à"))
        self.ctrl_heure_fin = CTRL_Saisie_heure.Heure(self)

        # Jours
        self.box_jours_staticbox = wx.StaticBox(self, -1, _(u"Jours"))
        self.label_scolaires = wx.StaticText(self, -1, _(u"Scolaires :"))
        self.ctrl_scolaires = CTRL_Jours(self, "scolaire")
        self.label_vacances = wx.StaticText(self, -1, _(u"Vacances :"))
        self.ctrl_vacances = CTRL_Jours(self, "vacances")
        self.label_semaines = wx.StaticText(self, -1, _(u"Fréquence :"))
        self.ctrl_semaines = CTRL_Semaines(self)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init
        if donnees:
            self.SetDonnees(donnees)

    def __set_properties(self):
        self.SetTitle(_(u"Appliquer une récurrence"))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date de début de période cible")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date de fin de période cible")))
        self.ctrl_semaines.SetToolTip(wx.ToolTip(_(u"Sélectionnez une fréquence")))
        self.ctrl_feries.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour inclure également les jours fériés")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Périodes
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=8, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add( (5, 5), 0, 0, 0)
        grid_sizer_periode.Add(self.ctrl_feries, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_periode, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Heures
        box_heures = wx.StaticBoxSizer(self.box_heures_staticbox, wx.VERTICAL)
        grid_sizer_heures = wx.FlexGridSizer(rows=2, cols=8, vgap=5, hgap=5)
        grid_sizer_heures.Add(self.label_heure_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heures.Add(self.ctrl_heure_debut, 0, 0, 0)
        grid_sizer_heures.Add(self.label_heure_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heures.Add(self.ctrl_heure_fin, 0, 0, 0)
        box_heures.Add(grid_sizer_heures, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_heures, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Jours
        box_jours = wx.StaticBoxSizer(self.box_jours_staticbox, wx.VERTICAL)
        grid_sizer_jours = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_jours.Add(self.label_scolaires, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_scolaires, 0, wx.EXPAND, 0)
        grid_sizer_jours.Add(self.label_vacances, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_vacances, 0, wx.EXPAND, 0)
        grid_sizer_jours.Add(self.label_semaines, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_semaines, 0, wx.EXPAND, 0)
        grid_sizer_jours.AddGrowableCol(1)
        box_jours.Add(grid_sizer_jours, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(box_jours, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedeslocations")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        # Période
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de début de période !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin de période !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False
        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"La date de début ne peut pas être supérieure à la date de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        # Heures
        heure_debut = self.ctrl_heure_debut.GetHeure()
        if heure_debut == None or self.ctrl_heure_debut.Validation() == False:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de début valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_debut.SetFocus()
            return

        heure_fin = self.ctrl_heure_fin.GetHeure()
        if heure_fin == None or self.ctrl_heure_fin.Validation() == False:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de fin valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_fin.SetFocus()
            return

        if date_debut > date_fin:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de fin supérieure à l'heure de début !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_fin.SetFocus()
            return

        # Jours
        jours_scolaires = self.ctrl_scolaires.GetJours()
        jours_vacances = self.ctrl_vacances.GetJours()
        if len(jours_scolaires) == 0 and len(jours_vacances) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un jour scolaire ou de vacances !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        feries = self.ctrl_feries.GetValue()
        semaines = self.ctrl_semaines.GetValeur()

        # Mémorisation des données
        self.dictDonnees = {
            "date_debut": date_debut,
            "date_fin": date_fin,
            "heure_debut": heure_debut,
            "heure_fin": heure_fin,
            "jours_scolaires": jours_scolaires,
            "jours_vacances": jours_vacances,
            "semaines": semaines,
            "feries": feries,
            }

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetDonnees(self):
        return self.dictDonnees

    def SetDonnees(self, dict_donnees=None):
        # Période
        if "date_debut" in dict_donnees:
            self.ctrl_date_debut.SetDate(dict_donnees["date_debut"])
        if "date_fin" in dict_donnees:
            self.ctrl_date_fin.SetDate(dict_donnees["date_fin"])
        if "feries" in dict_donnees:
            self.ctrl_feries.SetValue(dict_donnees["feries"])

        # Heures
        if "heure_debut" in dict_donnees:
            self.ctrl_heure_debut.SetHeure(dict_donnees["heure_debut"])
        if "heure_fin" in dict_donnees:
            self.ctrl_heure_fin.SetHeure(dict_donnees["heure_fin"])

        # Jours
        if "jours_scolaires" in dict_donnees:
            self.ctrl_scolaires.SetJours(dict_donnees["jours_scolaires"])
        if "jours_vacances" in dict_donnees:
            self.ctrl_vacances.SetJours(dict_donnees["jours_vacances"])
        if "semaines" in dict_donnees:
            self.ctrl_semaines.SetValeur(dict_donnees["semaines"])



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
