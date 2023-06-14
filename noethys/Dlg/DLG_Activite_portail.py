#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
from Ctrl import CTRL_Saisie_heure
from Ol import OL_Portail_periodes
from Ol import OL_Portail_unites
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_heure
from Utils import UTILS_Dates
import GestionDB




class Page_periodes(wx.Panel):
    def __init__(self, parent, IDactivite=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite

        # P�riodes de r�servations
        self.staticbox_periodes_staticbox = wx.StaticBox(self, -1, _(u"P�riodes de r�servations"))
        self.ctrl_periodes = OL_Portail_periodes.ListView(self, IDactivite=IDactivite, id=-1, name="OL_portail_periodes", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_periodes.MAJ()
        self.bouton_periodes_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_periodes_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_periodes_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_periodes.Ajouter, self.bouton_periodes_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_periodes.Modifier, self.bouton_periodes_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_periodes.Supprimer, self.bouton_periodes_supprimer)

        # Properties
        self.bouton_periodes_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour cr�er une p�riode de r�servations")))
        self.bouton_periodes_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la p�riode de r�servations s�lectionn�e dans la liste")))
        self.bouton_periodes_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la p�riode de r�servations selectionn�e dans la liste")))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        staticbox_periodes = wx.StaticBoxSizer(self.staticbox_periodes_staticbox, wx.VERTICAL)
        grid_sizer_periodes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_periodes = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_periodes.Add(self.ctrl_periodes, 1, wx.EXPAND, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_periodes_ajouter, 0, 0, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_periodes_modifier, 0, 0, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_periodes_supprimer, 0, 0, 0)
        grid_sizer_periodes.Add(grid_sizer_boutons_periodes, 1, wx.EXPAND, 0)
        grid_sizer_periodes.AddGrowableRow(0)
        grid_sizer_periodes.AddGrowableCol(0)
        staticbox_periodes.Add(grid_sizer_periodes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_periodes, 1, wx.ALL|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)



class Page_unites(wx.Panel):
    def __init__(self, parent, IDactivite=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite

        # Unit�s de r�servations
        self.staticbox_unites_staticbox = wx.StaticBox(self, -1, _(u"Unit�s de r�servations"))
        self.ctrl_unites = OL_Portail_unites.ListView(self, IDactivite=self.IDactivite, id=-1, name="OL_portail_unites", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_unites.MAJ()
        self.bouton_unites_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_unites_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_unites_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_unites_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_unites_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))

        self.check_unites_multiples = wx.CheckBox(self, -1, _(u"S�lection multiple d'unit�s de r�servations autoris�e"))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Ajouter, self.bouton_unites_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Modifier, self.bouton_unites_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Supprimer, self.bouton_unites_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Monter, self.bouton_unites_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Descendre, self.bouton_unites_descendre)

        # Properties
        self.bouton_unites_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour cr�er une unit� de r�servation")))
        self.bouton_unites_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'unit� de r�servation s�lectionn�e dans la liste")))
        self.bouton_unites_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'unit� de r�servation s�lectionn�e dans la liste")))
        self.bouton_unites_monter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour monter l'unit� de r�servation dans la liste")))
        self.bouton_unites_descendre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour descendre l'unit� de r�servation dans la liste")))
        self.check_unites_multiples.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour autoriser l'internaute � cocher plusieurs unit�s � la fois")))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        staticbox_unites = wx.StaticBoxSizer(self.staticbox_unites_staticbox, wx.VERTICAL)
        grid_sizer_unites = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_unites = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_unites.Add(self.ctrl_unites, 1, wx.EXPAND, 0)
        grid_sizer_boutons_unites.Add(self.bouton_unites_ajouter, 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_unites_modifier, 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_unites_supprimer, 0, 0, 0)
        #grid_sizer_boutons_unites.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_unites_monter, 0, 0, 0)
        grid_sizer_boutons_unites.Add(self.bouton_unites_descendre, 0, 0, 0)
        grid_sizer_unites.Add(grid_sizer_boutons_unites, 1, wx.EXPAND, 0)
        grid_sizer_unites.Add(self.check_unites_multiples, 1, wx.EXPAND, 0)
        grid_sizer_unites.AddGrowableRow(0)
        grid_sizer_unites.AddGrowableCol(0)
        staticbox_unites.Add(grid_sizer_unites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_unites, 1, wx.ALL|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)


class CTRL_Date_limite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1))
        self.parent = parent
        self.MAJ()

    def MAJ(self):
        self.liste_donnees = [
            (1000, _(u"Lundi pr�c�dent")),
            (1001, _(u"Mardi pr�c�dent")),
            (1002, _(u"Mercredi pr�c�dent")),
            (1003, _(u"Jeudi pr�c�dent")),
            (1004, _(u"Vendredi pr�c�dent")),
            (1005, _(u"Samedi pr�c�dent")),
            (1006, _(u"Dimanche pr�c�dent")),
            (2000, _(u"Lundi de la semaine pr�c�dente")),
            (2001, _(u"Mardi de la semaine pr�c�dente")),
            (2002, _(u"Mercredi de la semaine pr�c�dente")),
            (2003, _(u"Jeudi de la semaine pr�c�dente")),
            (2004, _(u"Vendredi de la semaine pr�c�dente")),
            (2005, _(u"Samedi de la semaine pr�c�dente")),
            (2006, _(u"Dimanche de la semaine pr�c�dente")),
            (0, _(u"Jour J")),
        ]
        for x in range(1, 31):
            self.liste_donnees.append((x, _(u"Jour J-%d") % x))

        listeItems = []
        for code, label in self.liste_donnees:
            listeItems.append(label)
        self.SetItems(listeItems)
        self.SetValeur(0)

    def SetValeur(self, valeur=None):
        for index, (code, label) in enumerate(self.liste_donnees):
            if code == valeur:
                self.SetSelection(index)

    def GetValeur(self):
        index = self.GetSelection()
        return self.liste_donnees[index][0]



class Page_options(wx.Panel):
    def __init__(self, parent, IDactivite=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite

        # Pr�paration de la liste des jours
        liste_jours = [_(u"Jour J"),]
        for x in range(1, 31):
            liste_jours.append(liste_jours[0] + str(-x))

        # Date limite de modification
        self.staticbox_date_limite = wx.StaticBox(self, -1, _(u"Limite de modification"))
        self.check_date_limite = wx.CheckBox(self, -1, _(u"Une r�servation peut �tre ajout�e, modifi�e ou supprim�e jusqu'�"))
        self.ctrl_date_limite = CTRL_Date_limite(self)
        self.ctrl_heure_limite = CTRL_Saisie_heure.Heure(self)
        self.check_limite_weekends = wx.CheckBox(self, -1, _(u"Exclure les week-ends"))
        self.check_limite_feries = wx.CheckBox(self, -1, _(u"Exclure les jours f�ri�s"))

        # Absence injustifi�e
        self.staticbox_absenti = wx.StaticBox(self, -1, _(u"Absence injustifi�e"))
        self.check_absenti = wx.CheckBox(self, -1, _(u"L'�tat 'Absence injustifi�e' est attribu� aux r�servations modifi�es ou supprim�es apr�s"))
        self.ctrl_date_absenti = wx.Choice(self, -1, choices=liste_jours)
        self.ctrl_heure_absenti = CTRL_Saisie_heure.Heure(self)

        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDateLimite, self.check_date_limite)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAbsenti, self.check_absenti)

        # Properties

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        staticbox_date_limite = wx.StaticBoxSizer(self.staticbox_date_limite, wx.VERTICAL)

        grid_sizer_limite = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)

        grid_sizer_date_limite = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_date_limite.Add(self.check_date_limite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date_limite.Add(self.ctrl_date_limite, 0, 0, 0)
        grid_sizer_date_limite.Add(self.ctrl_heure_limite, 0, 0, 0)
        grid_sizer_limite.Add(grid_sizer_date_limite, 1, wx.EXPAND, 0)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_options.Add(self.check_limite_weekends, 1, wx.LEFT, 0)
        grid_sizer_options.Add(self.check_limite_feries, 1, wx.LEFT, 0)
        grid_sizer_limite.Add(grid_sizer_options, 1, wx.LEFT, 23)

        staticbox_date_limite.Add(grid_sizer_limite, 1, wx.ALL | wx.EXPAND, 5)

        grid_sizer_base.Add(staticbox_date_limite, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        staticbox_absenti = wx.StaticBoxSizer(self.staticbox_absenti, wx.VERTICAL)
        grid_sizer_absenti = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_absenti.Add(self.check_absenti, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_absenti.Add(self.ctrl_date_absenti, 0, 0, 0)
        grid_sizer_absenti.Add(self.ctrl_heure_absenti, 0, 0, 0)
        staticbox_absenti.Add(grid_sizer_absenti, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_absenti, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)

        # Init
        self.ctrl_date_limite.SetValeur(0)
        self.ctrl_heure_limite.SetHeure("09:00")
        self.OnCheckDateLimite()

        self.ctrl_date_absenti.SetSelection(3)
        self.ctrl_heure_absenti.SetHeure("23:59")
        self.OnCheckAbsenti()

    def OnCheckDateLimite(self, event=None):
        self.ctrl_date_limite.Enable(self.check_date_limite.GetValue())
        self.ctrl_heure_limite.Enable(self.check_date_limite.GetValue())
        self.check_limite_feries.Enable(self.check_date_limite.GetValue())
        self.check_limite_weekends.Enable(self.check_date_limite.GetValue())

    def SetDateLimite(self, valeur=""):
        if valeur in (None, ""):
            return
        limite = valeur.split("#")
        date = limite[0]
        heure = limite[1]
        if len(limite) > 2 :
            options = limite[2]
        else :
            options = ""
        self.ctrl_date_limite.SetValeur(int(date))
        self.ctrl_heure_limite.SetHeure(heure)
        self.check_date_limite.SetValue(True)
        if "weekends" in options :
            self.check_limite_weekends.SetValue(True)
        if "feries" in options :
            self.check_limite_feries.SetValue(True)
        self.OnCheckDateLimite()

    def GetDateLimite(self):
        if self.check_date_limite.GetValue() == True :
            liste_options = []
            if self.check_limite_weekends.GetValue() == True :
                liste_options.append("weekends")
            if self.check_limite_feries.GetValue() == True :
                liste_options.append("feries")
            return "%d#%s#%s" % (self.ctrl_date_limite.GetValeur(), self.ctrl_heure_limite.GetHeure(), ",".join(liste_options))
        else :
            return None

    def OnCheckAbsenti(self, event=None):
        self.ctrl_date_absenti.Enable(self.check_absenti.GetValue())
        self.ctrl_heure_absenti.Enable(self.check_absenti.GetValue())

    def SetAbsenti(self, valeur=""):
        if valeur in (None, ""):
            return
        date, heure = valeur.split("#")
        self.ctrl_date_absenti.SetSelection(int(date))
        self.ctrl_heure_absenti.SetHeure(heure)
        self.check_absenti.SetValue(True)
        self.OnCheckAbsenti()

    def GetAbsenti(self):
        if self.check_absenti.GetValue() == True :
            return "%d#%s" % (self.ctrl_date_absenti.GetSelection(), self.ctrl_heure_absenti.GetHeure())
        else :
            return None

    def Validation(self):
        if self.check_date_limite.GetValue() == True :
            if self.ctrl_heure_limite.GetHeure() == None or self.ctrl_heure_limite.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure limite valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_heure_limite.SetFocus()
                return False

        if self.check_absenti.GetValue() == True :
            if self.ctrl_heure_absenti.GetHeure() == None or self.ctrl_heure_absenti.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_heure_absenti.SetFocus()
                return False

        return True





class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, nouvelleActivite=False):
        wx.Panel.__init__(self, parent, id=-1, name="panelportail", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite

        # Inscriptions
        self.box_inscriptions_staticbox = wx.StaticBox(self, -1, _(u"Inscriptions sur le portail"))
        self.radio_inscriptions_non = wx.RadioButton(self, -1, _(u"Ne pas autoriser"), style=wx.RB_GROUP)
        self.radio_inscriptions_oui = wx.RadioButton(self, -1, _(u"Autoriser"))
        self.radio_inscriptions_dates = wx.RadioButton(self, -1, _(u"Autoriser uniquement du"))
        self.ctrl_inscriptions_date_debut = CTRL_Saisie_date.Date2(self)
        self.ctrl_inscriptions_heure_debut = CTRL_Saisie_heure.Heure(self)
        self.label_inscriptions_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_inscriptions_date_fin = CTRL_Saisie_date.Date2(self)
        self.ctrl_inscriptions_heure_fin = CTRL_Saisie_heure.Heure(self)

        # R�servations
        self.box_reservations_staticbox = wx.StaticBox(self, -1, _(u"R�servations sur le portail"))
        self.radio_reservations_non = wx.RadioButton(self, -1, _(u"Ne pas autoriser"), style=wx.RB_GROUP)
        self.radio_reservations_oui = wx.RadioButton(self, -1, _(u"Autoriser"))

        # Notebook
        self.notebook_reservations = wx.Notebook(self, -1, style=wx.BK_TOP)

        self.page_periodes = Page_periodes(self.notebook_reservations, IDactivite=IDactivite)
        self.page_unites = Page_unites(self.notebook_reservations, IDactivite=IDactivite)
        self.page_options = Page_options(self.notebook_reservations, IDactivite=IDactivite)

        self.notebook_reservations.AddPage(self.page_periodes, _(u"P�riodes"))
        self.notebook_reservations.AddPage(self.page_unites, _(u"Unit�s"))
        self.notebook_reservations.AddPage(self.page_options, _(u"Options"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioInscriptions, self.radio_inscriptions_oui)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioInscriptions, self.radio_inscriptions_dates)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioInscriptions, self.radio_inscriptions_non)

        # Importation
        if nouvelleActivite == False :
            self.Importation()

        # Init
        self.OnRadioInscriptions()

    def __set_properties(self):
        self.radio_inscriptions_oui.SetToolTip(wx.ToolTip(_(u"S�lectionnez cette option pour autoriser l'inscription � cette activit� sur le portail")))
        self.radio_inscriptions_dates.SetToolTip(wx.ToolTip(_(u"S�lectionnez cette option pour autoriser l'inscription � cette activit� sur le portail uniquement entre les dates souhait�es")))
        self.radio_inscriptions_non.SetToolTip(wx.ToolTip(_(u"S�lectionnez cette option pour ne pas autoriser l'inscription � cette activit� sur le portail")))
        self.radio_reservations_oui.SetToolTip(wx.ToolTip(_(u"S�lectionnez cette option pour autoriser les r�servations � cette activit� sur le portail")))
        self.radio_reservations_non.SetToolTip(wx.ToolTip(_(u"S�lectionnez cette option pour ne pas autoriser les r�servations � cette activit� sur le portail")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        # Inscriptions
        staticbox_inscriptions = wx.StaticBoxSizer(self.box_inscriptions_staticbox, wx.VERTICAL)

        grid_sizer_affichage = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.radio_inscriptions_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.radio_inscriptions_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_affichage_periode = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_affichage_periode.Add(self.radio_inscriptions_dates, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage_periode.Add(self.ctrl_inscriptions_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage_periode.Add(self.ctrl_inscriptions_heure_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage_periode.Add(self.label_inscriptions_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage_periode.Add(self.ctrl_inscriptions_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage_periode.Add(self.ctrl_inscriptions_heure_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(grid_sizer_affichage_periode, 0, wx.EXPAND, 0)

        staticbox_inscriptions.Add(grid_sizer_affichage, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_inscriptions, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # R�servations
        staticbox_reservations = wx.StaticBoxSizer(self.box_reservations_staticbox, wx.VERTICAL)

        grid_sizer_reservations = wx.FlexGridSizer(rows=2, cols=1, vgap=20, hgap=10)

        grid_sizer_affichage = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.radio_reservations_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.radio_reservations_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reservations.Add(grid_sizer_affichage, 1, wx.EXPAND, 0)

        grid_sizer_reservations.Add(self.notebook_reservations, 1, wx.EXPAND, 0)

        grid_sizer_reservations.AddGrowableRow(1)
        grid_sizer_reservations.AddGrowableCol(0)
        staticbox_reservations.Add(grid_sizer_reservations, 1, wx.ALL|wx.EXPAND, 5)

        grid_sizer_base.Add(staticbox_reservations, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def OnRadioInscriptions(self, event=None):
        etat = self.radio_inscriptions_dates.GetValue()
        self.ctrl_inscriptions_date_debut.Enable(etat)
        self.ctrl_inscriptions_date_fin.Enable(etat)
        self.ctrl_inscriptions_heure_debut.Enable(etat)
        self.ctrl_inscriptions_heure_fin.Enable(etat)

    def Importation(self):
        """ Importation des donn�es """
        db = GestionDB.DB()
        req = """SELECT portail_inscriptions_affichage, portail_inscriptions_date_debut,
        portail_inscriptions_date_fin, portail_reservations_affichage, portail_unites_multiples,
        portail_reservations_limite, portail_reservations_absenti
        FROM activites
        WHERE IDactivite=%d;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        portail_inscriptions_affichage, portail_inscriptions_date_debut, portail_inscriptions_date_fin, portail_reservations_affichage, portail_unites_multiples, portail_reservations_limite, portail_reservations_absenti = listeDonnees[0]

        # Inscriptions
        if portail_inscriptions_affichage == 1 :
            if portail_inscriptions_date_debut != None :
                self.radio_inscriptions_dates.SetValue(True)
                self.ctrl_inscriptions_date_debut.SetDate(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(portail_inscriptions_date_debut),"%Y-%m-%d"))
                self.ctrl_inscriptions_heure_debut.SetHeure(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(portail_inscriptions_date_debut),"%H:%M"))
                self.ctrl_inscriptions_date_fin.SetDate(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(portail_inscriptions_date_fin),"%Y-%m-%d"))
                self.ctrl_inscriptions_heure_fin.SetHeure(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(portail_inscriptions_date_fin),"%H:%M"))
            else :
                self.radio_inscriptions_oui.SetValue(True)
        else :
            self.radio_inscriptions_non.SetValue(True)

        # R�servations
        if portail_reservations_affichage == 1 :
            self.radio_reservations_oui.SetValue(True)
        else :
            self.radio_reservations_non.SetValue(True)

        if portail_unites_multiples != None :
            self.page_unites.check_unites_multiples.SetValue(portail_unites_multiples)

        # Options
        self.page_options.SetDateLimite(portail_reservations_limite)
        self.page_options.SetAbsenti(portail_reservations_absenti)


    def Validation(self):
        if self.radio_inscriptions_dates.GetValue() == True :

            affichage_date_debut = self.ctrl_inscriptions_date_debut.GetDate()
            if affichage_date_debut == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de d�but !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_inscriptions_date_debut.SetFocus()
                return False

            affichage_heure_debut = self.ctrl_inscriptions_heure_debut.GetHeure()
            if affichage_heure_debut == None or self.ctrl_inscriptions_heure_debut.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de d�but valide pour l'affichage !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_inscriptions_heure_debut.SetFocus()
                return False

            affichage_date_fin = self.ctrl_inscriptions_date_fin.GetDate()
            if affichage_date_fin == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_inscriptions_date_fin.SetFocus()
                return False

            affichage_heure_fin = self.ctrl_inscriptions_heure_fin.GetHeure()
            if affichage_heure_fin == None or self.ctrl_inscriptions_heure_fin.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de fin valide pour l'affichage !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_inscriptions_heure_fin.SetFocus()
                return False

            if affichage_date_debut > affichage_date_fin :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin sup�rieure � la date de d�but !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_inscriptions_date_fin.SetFocus()
                return False

        if self.page_options.Validation() == False :
            return False

        # Sauvegarde
        self.Sauvegarde()

        return True
        
    def Sauvegarde(self):
        # Donn�es Inscriptions
        portail_inscriptions_date_debut = None
        portail_inscriptions_date_fin = None

        if self.radio_inscriptions_non.GetValue() == True :
            portail_inscriptions_affichage = False
        if self.radio_inscriptions_oui.GetValue() == True :
            portail_inscriptions_affichage = True
        if self.radio_inscriptions_dates.GetValue() == True :
            portail_inscriptions_affichage = True
            affichage_date_debut = self.ctrl_inscriptions_date_debut.GetDate()
            affichage_heure_debut = self.ctrl_inscriptions_heure_debut.GetHeure()
            portail_inscriptions_date_debut = datetime.datetime(year=affichage_date_debut.year, month=affichage_date_debut.month, day=affichage_date_debut.day, hour=int(affichage_heure_debut[:2]), minute=int(affichage_heure_debut[3:]))

            affichage_date_fin = self.ctrl_inscriptions_date_fin.GetDate()
            affichage_heure_fin = self.ctrl_inscriptions_heure_fin.GetHeure()
            portail_inscriptions_date_fin = datetime.datetime(year=affichage_date_fin.year, month=affichage_date_fin.month, day=affichage_date_fin.day, hour=int(affichage_heure_fin[:2]), minute=int(affichage_heure_fin[3:]))

        # Donn�es r�servations
        if self.radio_reservations_oui.GetValue() == True : portail_reservations_affichage = True
        if self.radio_reservations_non.GetValue() == True : portail_reservations_affichage = False

        # Unit�s de r�servations
        portail_unites_multiples = self.page_unites.check_unites_multiples.GetValue()

        # Options r�servations
        portail_reservations_limite = self.page_options.GetDateLimite()
        portail_reservations_absenti = self.page_options.GetAbsenti()

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
            ("portail_inscriptions_affichage", int(portail_inscriptions_affichage)),
            ("portail_inscriptions_date_debut", portail_inscriptions_date_debut),
            ("portail_inscriptions_date_fin", portail_inscriptions_date_fin),
            ("portail_reservations_affichage", int(portail_reservations_affichage)),
            ("portail_reservations_limite", portail_reservations_limite),
            ("portail_reservations_absenti", portail_reservations_absenti),
            ("portail_unites_multiples", int(portail_unites_multiples)),
            ]
        DB.ReqMAJ("activites", listeDonnees, "IDactivite", self.IDactivite)
        DB.Close()
        

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDactivite=1)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()