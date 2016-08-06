#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import datetime
from Ctrl import CTRL_Saisie_heure
from Ol import OL_Portail_periodes
from Ol import OL_Portail_unites
from Ctrl import CTRL_Saisie_date
import GestionDB



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

        # Réservations
        self.box_reservations_staticbox = wx.StaticBox(self, -1, _(u"Réservations sur le portail"))
        self.radio_reservations_non = wx.RadioButton(self, -1, _(u"Ne pas autoriser"), style=wx.RB_GROUP)
        self.radio_reservations_oui = wx.RadioButton(self, -1, _(u"Autoriser"))

        # Périodes de réservations
        self.staticbox_periodes_staticbox = wx.StaticBox(self, -1, _(u"Périodes de réservations"))
        self.ctrl_periodes = OL_Portail_periodes.ListView(self, IDactivite=self.IDactivite, id=-1, name="OL_portail_periodes", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_periodes.MAJ()
        self.bouton_periodes_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_periodes_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_periodes_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Unités de réservations
        self.staticbox_unites_staticbox = wx.StaticBox(self, -1, _(u"Unités de réservations"))
        self.ctrl_unites = OL_Portail_unites.ListView(self, IDactivite=self.IDactivite, id=-1, name="OL_portail_unites", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_unites.MAJ()
        self.bouton_unites_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_unites_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_unites_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_unites_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_unites_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))

        self.check_unites_multiples = wx.CheckBox(self, -1, _(u"Sélection multiple d'unités de réservations autorisée"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioInscriptions, self.radio_inscriptions_oui)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioInscriptions, self.radio_inscriptions_dates)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioInscriptions, self.radio_inscriptions_non)
        self.Bind(wx.EVT_BUTTON, self.ctrl_periodes.Ajouter, self.bouton_periodes_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_periodes.Modifier, self.bouton_periodes_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_periodes.Supprimer, self.bouton_periodes_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Ajouter, self.bouton_unites_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Modifier, self.bouton_unites_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Supprimer, self.bouton_unites_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Monter, self.bouton_unites_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_unites.Descendre, self.bouton_unites_descendre)

        # Importation
        if nouvelleActivite == False :
            self.Importation()

        # Init
        self.OnRadioInscriptions()

    def __set_properties(self):
        self.radio_inscriptions_oui.SetToolTipString(_(u"Sélectionnez cette option pour autoriser l'inscription à cette activité sur le portail"))
        self.radio_inscriptions_dates.SetToolTipString(_(u"Sélectionnez cette option pour autoriser l'inscription à cette activité sur le portail uniquement entre les dates souhaitées"))
        self.radio_inscriptions_non.SetToolTipString(_(u"Sélectionnez cette option pour ne pas autoriser l'inscription à cette activité sur le portail"))
        self.radio_reservations_oui.SetToolTipString(_(u"Sélectionnez cette option pour autoriser les réservations à cette activité sur le portail"))
        self.radio_reservations_non.SetToolTipString(_(u"Sélectionnez cette option pour ne pas autoriser les réservations à cette activité sur le portail"))
        self.bouton_periodes_ajouter.SetToolTipString(_(u"Cliquez ici pour créer une période de réservations"))
        self.bouton_periodes_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la période de réservations sélectionnée dans la liste"))
        self.bouton_periodes_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la période de réservations selectionnée dans la liste"))
        self.bouton_unites_ajouter.SetToolTipString(_(u"Cliquez ici pour créer une unité de réservation"))
        self.bouton_unites_modifier.SetToolTipString(_(u"Cliquez ici pour modifier l'unité de réservation sélectionnée dans la liste"))
        self.bouton_unites_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer l'unité de réservation sélectionnée dans la liste"))
        self.bouton_unites_monter.SetToolTipString(_(u"Cliquez ici pour monter l'unité de réservation dans la liste"))
        self.bouton_unites_descendre.SetToolTipString(_(u"Cliquez ici pour descendre l'unité de réservation dans la liste"))
        self.check_unites_multiples.SetToolTipString(_(u"Cochez cette case pour autoriser l'internaute à cocher plusieurs unités à la fois"))

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

        # Réservations
        staticbox_reservations = wx.StaticBoxSizer(self.box_reservations_staticbox, wx.VERTICAL)
        grid_sizer_affichage = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.radio_reservations_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.radio_reservations_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_reservations.Add(grid_sizer_affichage, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_reservations, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Périodes
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
        grid_sizer_base.Add(staticbox_periodes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Unités
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
        grid_sizer_base.Add(staticbox_unites, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)

    def OnRadioInscriptions(self, event=None):
        etat = self.radio_inscriptions_dates.GetValue()
        self.ctrl_inscriptions_date_debut.Enable(etat)
        self.ctrl_inscriptions_date_fin.Enable(etat)
        self.ctrl_inscriptions_heure_debut.Enable(etat)
        self.ctrl_inscriptions_heure_fin.Enable(etat)

    def Importation(self):
        """ Importation des données """
        db = GestionDB.DB()
        req = """SELECT portail_inscriptions_affichage, portail_inscriptions_date_debut,
        portail_inscriptions_date_fin, portail_reservations_affichage, portail_unites_multiples
        FROM activites
        WHERE IDactivite=%d;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        portail_inscriptions_affichage, portail_inscriptions_date_debut, portail_inscriptions_date_fin, portail_reservations_affichage, portail_unites_multiples = listeDonnees[0]

        # Inscriptions
        if portail_inscriptions_affichage == 1 :
            if portail_inscriptions_date_debut != None :
                self.radio_inscriptions_dates.SetValue(True)
                self.ctrl_inscriptions_date_debut.SetDate(portail_inscriptions_date_debut.strftime("%Y-%m-%d"))
                self.ctrl_inscriptions_heure_debut.SetHeure(portail_inscriptions_date_debut.strftime("%H:%M"))
                self.ctrl_inscriptions_date_fin.SetDate(portail_inscriptions_date_fin.strftime("%Y-%m-%d"))
                self.ctrl_inscriptions_heure_fin.SetHeure(portail_inscriptions_date_fin.strftime("%H:%M"))
            else :
                self.radio_inscriptions_oui.SetValue(True)
        else :
            self.radio_inscriptions_non.SetValue(True)

        # Réservations
        if portail_reservations_affichage == 1 :
            self.radio_reservations_oui.SetValue(True)
        else :
            self.radio_reservations_non.SetValue(True)

        if portail_unites_multiples != None :
            self.check_unites_multiples.SetValue(portail_unites_multiples)

    def Validation(self):
        if self.radio_inscriptions_dates.GetValue() == True :

            affichage_date_debut = self.ctrl_inscriptions_date_debut.GetDate()
            if affichage_date_debut == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_inscriptions_date_debut.SetFocus()
                return False

            affichage_heure_debut = self.ctrl_inscriptions_heure_debut.GetHeure()
            if affichage_heure_debut == None or self.ctrl_inscriptions_heure_debut.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de début valide pour l'affichage !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
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
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin supérieure à la date de début !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_inscriptions_date_fin.SetFocus()
                return False

        # Sauvegarde
        self.Sauvegarde()

        return True
        
    def Sauvegarde(self):
        # Données Inscriptions
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

        # Données réservations
        if self.radio_reservations_oui.GetValue() == True : portail_reservations_affichage = True
        if self.radio_reservations_non.GetValue() == True : portail_reservations_affichage = False

        # Unités de réservations
        portail_unites_multiples = self.check_unites_multiples.GetValue()

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
            ("portail_inscriptions_affichage", int(portail_inscriptions_affichage)),
            ("portail_inscriptions_date_debut", portail_inscriptions_date_debut),
            ("portail_inscriptions_date_fin", portail_inscriptions_date_fin),
            ("portail_reservations_affichage", int(portail_reservations_affichage)),
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