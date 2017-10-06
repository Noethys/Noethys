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
import datetime
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date
from Utils import UTILS_Dates
from Dlg.DLG_Ouvertures import Calendrier
import wx.lib.agw.hyperlink as Hyperlink
from Ol import OL_Evenements
import GestionDB



class CTRL_Unite(wx.Choice):
    def __init__(self, parent, IDactivite=None):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1))
        self.parent = parent
        self.IDactivite = IDactivite
        self.MAJ()

    def MAJ(self):
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
            self.Select(0)

    def GetListeDonnees(self):
        listeItems = []
        if self.IDactivite == None :
            return listeItems
        db = GestionDB.DB()
        req = """SELECT IDunite, nom, type
        FROM unites
        WHERE IDactivite=%d AND type='Evenement'
        ORDER BY ordre;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        self.dictDonnees = {}
        index = 0
        for IDunite, nom, type in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDunite, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


# --------------------------------------------------------------------------

class CTRL_Groupe(wx.Choice):
    def __init__(self, parent, IDactivite=0):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.IDactivite = IDactivite
        self.MAJlisteDonnees()

    def MAJlisteDonnees(self):
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
        if len(listeItems) == 0:
            self.Enable(False)
        else :
            self.Enable(True)
            self.Select(0)

    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDgroupe, nom
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDgroupe, nom in listeDonnees:
            self.dictDonnees[index] = {"ID": IDgroupe}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID:
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1: return None
        return self.dictDonnees[index]["ID"]



# --------------------------------------------------------------------------------

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
            exec("self.check_%s = wx.CheckBox(self, -1, u'%s')" % (jour, jour[0].upper()) )
            exec("self.check_%s.SetToolTip(wx.ToolTip(u'%s'))" % (jour, jour.capitalize()) )

        self.hyper_tout = Hyperlien(self, label=_(u"Tout"), infobulle=_(u"Cliquez ici pour tout cocher"), URL="tout")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=_(u"Rien"), infobulle=_(u"Cliquez ici pour tout décocher"), URL="rien")

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=10, vgap=0, hgap=0)
        for jour in self.liste_jours :
            exec("grid_sizer_base.Add(self.check_%s, 0, 0, 0)" % jour)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=3)
        grid_sizer_options.Add(self.hyper_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.hyper_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_options, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

        # Init
        self.SetJours("0;1;2;3;4;5;6")

    def GetJours(self):
        listeTemp = []
        index = 0
        for jour in self.liste_jours :
            exec("etat = self.check_%s.GetValue()" % jour)
            if etat == True :
                listeTemp.append(index)
            index += 1
        return listeTemp
    
    def SetJours(self, texteJours=""):
        if texteJours == None :
            return

        listeJoursTemp = texteJours.split(";")
        listeJours = []
        for jour in listeJoursTemp :
            if len(jour) > 0 :
                listeJours.append(int(jour))
        index = 0
        for jour in self.liste_jours :
            if index in listeJours :
                etat = "True"
            else :
                etat = "False"
            exec("self.check_%s.SetValue(%s)" % (jour, etat))
            index += 1

    def CocherTout(self):
        self.SetJours("0;1;2;3;4;5;6")

    def CocherRien(self):
        self.SetJours("")


# ---------------------------------------------------------------------------------------------------------------------------------------

class Page_dates(wx.Panel):
    def __init__(self, parent, afficheElements=True, IDactivite=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.dictDonnees = {}

        self.radio_date = wx.RadioButton(self, -1, _(u"Copier le schéma de la date suivante :"), style=wx.RB_GROUP)
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.check_ouvertures = wx.CheckBox(self, -1, _(u"Ouvertures"))
        self.check_places = wx.CheckBox(self, -1, _(u"Nbre de places max."))
        self.check_evenements = wx.CheckBox(self, -1, _(u"Evènements"))

        self.radio_calendrier = wx.RadioButton(self, -1, _(u"Copier le schéma suivant :"))
        self.ctrl_calendrier = Calendrier(self, IDactivite=IDactivite)
        self.ctrl_calendrier.SetMinSize((20, 20))

        self.radio_renitialisation = wx.RadioButton(self, -1, _(u"Réinitialiser la date"))

        if afficheElements == False:
            self.check_ouvertures.Show(False)
            self.check_places.Show(False)
            self.check_evenements.Show(False)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_calendrier)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_date)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_renitialisation)

        # Init
        self.check_ouvertures.SetValue(True)
        self.check_places.SetValue(True)
        self.check_evenements.SetValue(True)
        self.ctrl_date.SetFocus()
        self.OnRadioAction(None)

        self.ctrl_calendrier.MAJ(modele=True)

    def __set_properties(self):
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date modèle. Les éléments de cette date seront copiés vers les dates cibles")))
        self.radio_date.SetToolTip(wx.ToolTip(_(u"Sélectionnez ce mode pour copier les éléments d'une date donnée")))
        self.radio_renitialisation.SetToolTip(wx.ToolTip(_(u"Sélectionnez ce mode pour supprimer les ouvertures, évènements et remplissages des dates")))
        self.check_ouvertures.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour modifier les ouvertures")))
        self.check_places.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour modifier les nbres de places max. (remplissage)")))
        self.check_evenements.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour modifier les évènements (uniquement pour les unités de type évènementielles")))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(6, 1, 10, 10)

        # Date
        grid_sizer_base.Add(self.radio_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_date.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_elements = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_elements.Add(self.check_ouvertures, 0, 0, 0)
        grid_sizer_elements.Add(self.check_places, 0, 0, 0)
        grid_sizer_elements.Add(self.check_evenements, 0, 0, 0)
        grid_sizer_date.Add(grid_sizer_elements, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 17)
        grid_sizer_base.Add(grid_sizer_date, 1, wx.EXPAND | wx.LEFT, 17)

        # Calendrier
        grid_sizer_base.Add(self.radio_calendrier, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_calendrier, 0, wx.EXPAND | wx.LEFT, 17)

        # Réinit
        grid_sizer_base.Add(self.radio_renitialisation, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(3)

        sizer_base.Add(grid_sizer_base, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadioAction(self, event):
        self.ctrl_calendrier.Enable(self.radio_calendrier.GetValue())
        self.ctrl_date.Enable(self.radio_date.GetValue())
        self.check_ouvertures.Enable(self.radio_date.GetValue())
        self.check_evenements.Enable(self.radio_date.GetValue())
        self.check_places.Enable(self.radio_date.GetValue())

    def Validation(self, dictDonnees={}):
        self.dictDonnees = dictDonnees

        # Vérification des données saisies
        if self.radio_date.GetValue() == True:
            self.dictDonnees["action"] = "date"

            # Vérification de la date
            date = self.ctrl_date.GetDate()
            self.dictDonnees["date"] = date
            if date == None:
                dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une date modèle !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date.SetFocus()
                return False

            # Elements
            elements = []
            if self.check_ouvertures.GetValue() == True: elements.append("ouvertures")
            if self.check_places.GetValue() == True: elements.append("places")
            if self.check_evenements.GetValue() == True: elements.append("evenements")
            self.dictDonnees["elements"] = elements
            if len(elements) == 0:
                dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un élément à modifier (ouvertures/places) !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        if self.radio_calendrier.GetValue() == True :
            self.dictDonnees["action"] = "schema"
            self.dictDonnees["dictOuvertures"] = {}
            self.dictDonnees["dictRemplissage"] = {}
            if len(self.ctrl_calendrier.dictOuvertures.keys()) > 0 :
                date = self.ctrl_calendrier.dictOuvertures.keys()[0]
                if self.ctrl_calendrier.dictOuvertures.has_key(date) :
                    self.dictDonnees["dictOuvertures"] = self.ctrl_calendrier.dictOuvertures[date]
                if self.ctrl_calendrier.dictRemplissage.has_key(date) :
                    self.dictDonnees["dictRemplissage"] = self.ctrl_calendrier.dictRemplissage[date]

        if self.radio_renitialisation.GetValue() == True :
            self.dictDonnees["action"] = "reinit"

        return True

    def GetDonnees(self):
        return self.dictDonnees

# ---------------------------------------------------------------------------------------------------------------------------------------

class Page_evenements(wx.Panel):
    def __init__(self, parent, IDactivite=None, ctrl_calendrier=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.dictDonnees = {}
        self.ctrl_calendrier = ctrl_calendrier

        # Ajouter
        self.radio_ajouter = wx.RadioButton(self, -1, _(u"Ajouter les évènements suivants :"), style=wx.RB_GROUP)

        liste_colonnes = ["ID", "nom", "heure_debut", "heure_fin", "montant", "capacite_max"]
        self.ctrl_evenements = OL_Evenements.ListView(self, id=-1, IDactivite=IDactivite, liste_colonnes=liste_colonnes, style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.ctrl_evenements.SetMinSize((50, 50))
        self.ctrl_evenements.MAJ()

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        self.label_unite = wx.StaticText(self, -1, _(u"Unité :"))
        self.ctrl_unite = CTRL_Unite(self, IDactivite=IDactivite)
        self.ctrl_unite.SetMinSize((50, -1))

        self.label_groupe = wx.StaticText(self, -1, _(u"Groupe :"))
        self.ctrl_groupe = CTRL_Groupe(self, IDactivite=IDactivite)
        self.ctrl_groupe.SetMinSize((50, -1))

        # Supprimer
        self.radio_supprimer_expression = wx.RadioButton(self, -1, _(u"Supprimer les évènements dont le nom contient l'expression suivante :"))
        self.ctrl_expression = wx.TextCtrl(self, -1, "")

        self.radio_supprimer_tout = wx.RadioButton(self, -1, _(u"Supprimer tous les évènements:"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_ajouter)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_supprimer_expression)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAction, self.radio_supprimer_tout)
        self.Bind(wx.EVT_BUTTON, self.ctrl_evenements.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_evenements.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_evenements.Supprimer, self.bouton_supprimer)

        # Init
        self.OnRadioAction(None)

    def __set_properties(self):
        self.radio_ajouter.SetToolTip(wx.ToolTip(_(u"Sélectionnez ce mode pour ajouter un ou plusieurs évènements")))
        self.radio_supprimer_expression.SetToolTip(wx.ToolTip(_(u"Sélectionnez ce mode pour supprimer un ou plusieurs évènements")))
        self.radio_supprimer_tout.SetToolTip(wx.ToolTip(_(u"Sélectionnez ce mode pour supprimer tous les évènements")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'évènement sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'évènement sélectionné dans la liste")))
        self.ctrl_unite.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'unité de consommations de type évènementiel qui sera associée aux évènements à créer")))
        self.ctrl_groupe.SetToolTip(wx.ToolTip(_(u"Sélectionnez le groupe qui sera associé aux évènements à créer")))
        self.ctrl_expression.SetToolTip(wx.ToolTip(_(u"Saisissez un mot ou une expression qui se trouve dans le ou les évènements à supprimer (Exemples : Patinoire, piscine...")))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(6, 1, 10, 10)

        # Ajouter
        grid_sizer_base.Add(self.radio_ajouter, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_evenements = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_evenements.Add(self.ctrl_evenements, 0, wx.EXPAND, 0)

        grid_sizer_droit = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_evenements.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_unites = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_unites.Add(self.label_unite, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unites.Add(self.ctrl_unite, 1, wx.EXPAND, 0)
        grid_sizer_unites.Add(self.label_groupe, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unites.Add(self.ctrl_groupe, 1, wx.EXPAND, 0)
        grid_sizer_unites.AddGrowableCol(1)
        grid_sizer_unites.AddGrowableCol(3)
        grid_sizer_evenements.Add(grid_sizer_unites, 1, wx.EXPAND, 0)

        grid_sizer_evenements.AddGrowableRow(0)
        grid_sizer_evenements.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_evenements, 1, wx.LEFT|wx.EXPAND, 17)

        # Supprimer
        grid_sizer_base.Add(self.radio_supprimer_expression, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_expression, 0, wx.EXPAND | wx.LEFT, 17)
        grid_sizer_base.Add(self.radio_supprimer_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)

        sizer_base.Add(grid_sizer_base, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadioAction(self, event):
        self.ctrl_evenements.Activation(self.radio_ajouter.GetValue())
        self.bouton_ajouter.Enable(self.radio_ajouter.GetValue())
        self.bouton_modifier.Enable(self.radio_ajouter.GetValue())
        self.bouton_supprimer.Enable(self.radio_ajouter.GetValue())
        self.label_groupe.Enable(self.radio_ajouter.GetValue())
        self.ctrl_groupe.Enable(self.radio_ajouter.GetValue())
        self.label_unite.Enable(self.radio_ajouter.GetValue())
        self.ctrl_unite.Enable(self.radio_ajouter.GetValue())
        self.ctrl_expression.Enable(self.radio_supprimer_expression.GetValue())

    def Validation(self, dictDonnees={}):
        self.dictDonnees = dictDonnees

        # Vérification des données saisies
        if self.radio_ajouter.GetValue() == True:
            self.dictDonnees["action"] = "ajouter"

            # Vérification de la date
            liste_evenements = self.ctrl_evenements.GetListeEvenements()
            self.dictDonnees["liste_evenements"] = liste_evenements
            if len(liste_evenements) == 0:
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir au moins un évènement à créer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            # Unité
            IDunite = self.ctrl_unite.GetID()
            self.dictDonnees["IDunite"] = IDunite
            if IDunite == None:
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une unité de consommations à associer à ces évènements !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_unite.SetFocus()
                return False

            # Groupe
            IDgroupe = self.ctrl_groupe.GetID()
            self.dictDonnees["IDgroupe"] = IDgroupe
            if IDgroupe == None:
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un groupe à associer à ces évènements !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_groupe.SetFocus()
                return False

        if self.radio_supprimer_expression.GetValue() == True or self.radio_supprimer_tout.GetValue() == True :
            self.dictDonnees["action"] = "supprimer"

            if self.radio_supprimer_expression.GetValue() == True :
                expression = self.ctrl_expression.GetValue()
                self.dictDonnees["expression"] = expression
                if len(expression) == 0:
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une expression valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    self.ctrl_expression.SetFocus()
                    return False

            if self.radio_supprimer_tout.GetValue() == True :
                expression = None

            # Recherche les évènements à supprimer
            DB = GestionDB.DB()
            self.ctrl_calendrier.GetDictOuvertures(DB, dictDonnees["date_debut"], dictDonnees["date_fin"])
            self.ctrl_calendrier.GetDictRemplissage(DB, dictDonnees["date_debut"], dictDonnees["date_fin"])
            self.ctrl_calendrier.GetDictConso(DB, dictDonnees["date_debut"], dictDonnees["date_fin"])
            DB.Close()

            liste_tracks_trouves = []
            listeID = []
            for dateDD, dictGroupes in self.ctrl_calendrier.dictOuvertures.iteritems():
                for IDgroupe, dictUnites in dictGroupes.iteritems():
                    for IDunite, dictValeurs in dictUnites.iteritems():
                        liste_evenements = dictValeurs["liste_evenements"]
                        for track_evenement in liste_evenements :
                            if expression == None or expression.lower() in track_evenement.nom.lower() :
                                liste_tracks_trouves.append(track_evenement)
                                if track_evenement.IDevenement != None:
                                    listeID.append(track_evenement.IDevenement)

            dictNbreConso = {}
            if len(listeID) > 0 :
                if len(listeID) == 1 :
                    condition = "(%d)" % listeID[0]
                else :
                    condition = str(tuple(listeID))
                DB = GestionDB.DB()
                req = """SELECT IDconso, IDevenement
                FROM consommations 
                WHERE IDevenement IN %s
                ;""" % condition
                DB.ExecuterReq(req)
                listeConso = DB.ResultatReq()
                DB.Close()
                for IDconso, IDevenement in listeConso :
                    if dictNbreConso.has_key(IDevenement) == False :
                        dictNbreConso[IDevenement] = 0
                    dictNbreConso[IDevenement] += 1

            # Demande les évènements à supprimer
            listeTemp = [(track.date, track.nom, track) for track in liste_tracks_trouves]
            listeTemp.sort()
            listeLabelsEvenements = []
            listeID = []
            for date, nom, track in listeTemp :
                if dictNbreConso.has_key(track.IDevenement) == False :
                    listeLabelsEvenements.append(u"%s : %s" % (UTILS_Dates.DateDDEnFr(date), nom))
                    if track.IDevenement != None :
                        listeID.append(track.IDevenement)
            listeLabelsEvenements.sort()

            if len(listeLabelsEvenements) == 0:
                dlg = wx.MessageDialog(self, _(u"Aucun évènement supprimable dont le nom contient cette expression n'a été trouvé !"), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            dlg = wx.MultiChoiceDialog(self, _(u"Voici la liste des évènements supprimables. Cochez ceux que vous souhaitez supprimer :"), _(u"Sélection des évènements"), listeLabelsEvenements)
            dlg.SetSelections(range(0, len(listeLabelsEvenements)))
            reponse = dlg.ShowModal()
            selections = dlg.GetSelections()
            listeSelections = [listeTemp[x] for x in selections]
            dlg.Destroy()
            if reponse != wx.ID_OK:
                return False

            self.dictDonnees["tracks_a_supprimer"] = [track for date, nom, track in listeSelections]

        return True

    def GetDonnees(self):
        return self.dictDonnees




# ---------------------------------------------------------------------------------------------------------------------------------------

class Notebook(wx.Notebook):
    def __init__(self, parent, afficheElements=True, IDactivite=None, ctrl_calendrier=None):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT)
        self.dictPages = {}

        self.listePages = [
            (_(u"dates"), _(u"Dates"), _(u"Page_dates(self, afficheElements=afficheElements, IDactivite=IDactivite)"), "Calendrier_jour.png"),
            (_(u"evenements"), _(u"Evènements"), _(u"Page_evenements(self, IDactivite=IDactivite, ctrl_calendrier=ctrl_calendrier)"), "Evenement.png"),
        ]

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages:
            exec ("self.img%d = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/%s'), wx.BITMAP_TYPE_PNG))" % (index, imgPage))
            index += 1
        self.AssignImageList(il)

        # Création des pages
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages:
            exec ("self.page%d = %s" % (index, ctrlPage))
            exec ("self.AddPage(self.page%d, u'%s')" % (index, labelPage))
            exec ("self.SetPageImage(%d, self.img%d)" % (index, index))
            exec ("self.dictPages['%s'] = {'ctrl' : self.page%d, 'index' : %d}" % (codePage, index, index))
            index += 1

    def GetCodePageActive(self):
        index = self.GetSelection()
        return self.listePages[index][0]

    def GetPageActive(self):
        codePage = self.GetCodePageActive()
        return self.GetPage(codePage)

    def GetPage(self, codePage=""):
        return self.dictPages[codePage]["ctrl"]

    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)


# ----------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, afficheElements=True, IDactivite=None, ctrl_calendrier=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.afficheElements = afficheElements
        self.IDactivite = IDactivite
        self.ctrl_calendrier = ctrl_calendrier
        self.dictDonnees = {}

        # Action
        self.box_action_staticbox = wx.StaticBox(self, -1, _(u"Action"))
        self.notebook = Notebook(self, afficheElements=afficheElements, IDactivite=IDactivite, ctrl_calendrier=ctrl_calendrier)

        # Période
        self.box_periode_staticbox = wx.StaticBox(self, -1, _(u"Période d'application"))
        
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.ctrl_feries = wx.CheckBox(self, -1, _(u"Inclure les fériés"))

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
        

    def __set_properties(self):
        self.SetTitle(_(u"Saisie et suppression par lot"))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date de début de période cible")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date de fin de période cible")))
        self.ctrl_semaines.SetToolTip(wx.ToolTip(_(u"Sélectionnez une fréquence")))
        self.ctrl_feries.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour modifier également les jours fériés")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Action
        box_action = wx.StaticBoxSizer(self.box_action_staticbox, wx.VERTICAL)
        box_action.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_action, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Périodes
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add( (5, 5), 0, 0, 0)
        grid_sizer_periode.Add(self.ctrl_feries, 0, 0, 0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_bas.Add(box_periode, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)
        
        # Jours
        box_jours = wx.StaticBoxSizer(self.box_jours_staticbox, wx.VERTICAL)
        grid_sizer_jours = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_jours.Add(self.label_scolaires, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_scolaires, 0, wx.EXPAND, 0)
        grid_sizer_jours.Add(self.label_vacances, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_vacances, 0, wx.EXPAND, 0)
        grid_sizer_jours.Add(self.label_semaines, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_semaines, 0, wx.EXPAND, 0)
        #grid_sizer_jours.Add(self.label_feries, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        #grid_sizer_jours.Add(self.ctrl_feries, 0, wx.EXPAND, 0)
        grid_sizer_jours.AddGrowableCol(1)
        box_jours.Add(grid_sizer_jours, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_bas.Add(box_jours, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)

        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        self.SetMinSize((self.GetSize()[0], 590))
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Calendrier")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def SetDate(self, date=None):
        self.notebook.GetPage("dates").ctrl_date.SetDate(date)

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
            "mode": self.notebook.GetCodePageActive(),
            "date_debut": date_debut,
            "date_fin": date_fin,
            "jours_scolaires": jours_scolaires,
            "jours_vacances": jours_vacances,
            "semaines": semaines,
            "feries": feries,
            }

        # Validation des données
        page = self.notebook.GetPageActive()
        if page.Validation(dictDonnees=self.dictDonnees) == False :
            return False
        self.dictDonnees = page.GetDonnees()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetDonnees(self):
        return self.dictDonnees




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, afficheElements=True, IDactivite=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
