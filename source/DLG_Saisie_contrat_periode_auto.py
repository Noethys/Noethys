#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Saisie_date
import CTRL_Saisie_euros
import GestionDB
import UTILS_Dates

import datetime
from dateutil import relativedelta
from dateutil import rrule


LISTE_MOIS = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))


class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, dictValeurs={}, listeTracks=[]):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_contrat_periode_auto", style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDactivite = IDactivite
        self.listeTracks = listeTracks
        self.listeResultats = []

        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        self.label_dates = wx.StaticText(self, wx.ID_ANY, _(u"Dates :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, wx.ID_ANY, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Prestation
        self.box_prestation_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Prestation"))
        self.label_periodicite = wx.StaticText(self, wx.ID_ANY, _(u"Périodicité :"))
        self.ctrl_periodicite = wx.Choice(self, -1, choices=[_(u"Annuelle"), _(u"Mensuelle"), _(u"Hebdomadaire")])
        self.ctrl_periodicite.SetSelection(1) 
        self.label_date_prestation = wx.StaticText(self, wx.ID_ANY, _(u"Date :"))
        self.ctrl_date_prestation = wx.Choice(self, -1, choices=[_(u"Début de période"), _(u"Fin de période")])
        self.ctrl_date_prestation.SetSelection(0)
        self.label_label_prestation = wx.StaticText(self, wx.ID_ANY, _(u"Label :"))
        self.ctrl_label_prestation = wx.TextCtrl(self, wx.ID_ANY, u"{LABEL_AUTO}")
        self.label_montant_prestation = wx.StaticText(self, wx.ID_ANY, _(u"Montant :"))
        self.ctrl_montant_prestation = CTRL_Saisie_euros.CTRL(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        self.Importation(dictValeurs)

    def __set_properties(self):
        self.SetTitle(_(u"Génération automatique de périodes"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de début de la période"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez la date de fin de la période"))
        self.ctrl_periodicite.SetToolTipString(_(u"Sélectionnez la périodicité à appliquer"))
        self.ctrl_label_prestation.SetToolTipString(_(u"Saisissez le label de la prestation. Le mot-clé {LABEL_AUTO} permet d'insérer un label automatiquement (Ex : 'Janvier 2014'). Les mots-clés suivants sont également disponibles : {ANNEE} {NUM_MOIS} {NOM_MOIS} {NUM_SEMAINE}."))
        self.ctrl_date_prestation.SetToolTipString(_(u"Sélectionnez la date de la prestation"))
        self.ctrl_montant_prestation.SetToolTipString(_(u"Saisissez le montant de la prestation"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(2, 2, 10, 10)
        grid_sizer_dates = wx.FlexGridSizer(1, 4, 5, 5)
        grid_sizer_generalites.Add(self.label_dates, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_dates, 1, wx.EXPAND, 0)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        
        # Prestation
        box_prestation = wx.StaticBoxSizer(self.box_prestation_staticbox, wx.VERTICAL)
        grid_sizer_prestation = wx.FlexGridSizer(4, 2, 5, 10)
        grid_sizer_prestation.Add(self.label_periodicite, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_periodicite, 1, wx.EXPAND, 0)
        grid_sizer_prestation.Add(self.label_date_prestation, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_date_prestation, 0, wx.EXPAND, 0)
        grid_sizer_prestation.Add(self.label_label_prestation, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_label_prestation, 0, wx.EXPAND, 0)
        grid_sizer_prestation.Add(self.label_montant_prestation, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_montant_prestation, 0, 0, 0)
        grid_sizer_prestation.AddGrowableCol(1)
        box_prestation.Add(grid_sizer_prestation, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_prestation, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def Importation(self, dictValeurs={}):
        if dictValeurs.has_key("date_debut") :
            self.ctrl_date_debut.SetDate(dictValeurs["date_debut"])
        if dictValeurs.has_key("date_fin") :
            self.ctrl_date_fin.SetDate(dictValeurs["date_fin"])
    
    def GetParametres(self):
        dictValeurs = {
            "date_debut" : self.ctrl_date_debut.GetDate(),
            "date_fin" : self.ctrl_date_fin.GetDate(),
            "periodicite" : self.ctrl_periodicite.GetSelection(),
            "label_prestation" : self.ctrl_label_prestation.GetValue(),
            "date_prestation" : self.ctrl_date_prestation.GetSelection(),
            "montant_prestation" : self.ctrl_montant_prestation.GetMontant(),
            }   
        return dictValeurs
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide(u"")

    def OnBoutonAnnuler(self, event):  
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):  
        if self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner la date de début !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if self.ctrl_date_fin.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if self.ctrl_date_fin.GetDate() < self.ctrl_date_debut.GetDate() :
            dlg = wx.MessageDialog(self, _(u"La date de début ne doit pas être supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if self.ctrl_label_prestation.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le label de la prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if self.ctrl_montant_prestation.GetMontant() == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment appliquer un montant de 0.00 ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            if reponse != wx.ID_YES :
                return
        
        # Génération des périodes
        if self.Generation() == False :
            return
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def Generation(self):
        dictParametres = self.GetParametres() 
        
        def ConvertDateToDatetime(date):
            return datetime.datetime(date.year, date.month, date.day)
            
        # Génération des dates
        date_debut = ConvertDateToDatetime(dictParametres["date_debut"])
        date_fin = ConvertDateToDatetime(dictParametres["date_fin"])
        if dictParametres["periodicite"] == 0 :
            listeDates = list(rrule.rrule(rrule.YEARLY, byyearday=(1, -1), dtstart=date_debut, until=date_fin))
        if dictParametres["periodicite"] == 1 :
            listeDates = list(rrule.rrule(rrule.MONTHLY, bymonthday=(1, -1), dtstart=date_debut, until=date_fin))
        if dictParametres["periodicite"] == 2 :
            listeDates = list(rrule.rrule(rrule.WEEKLY, byweekday=(rrule.MO, rrule.SU), dtstart=date_debut, until=date_fin))
        
        # Traitement des dates pour obtenir [(date1, date2), ...]
        index = 0
        if listeDates[0] == date_debut :
            listeDates2 = []
            indexDebut = 0
        else :
            listeDates2 = [(date_debut, listeDates[0]),]
            indexDebut = 1
        for index in range(indexDebut, len(listeDates), 2) :
            date1 = listeDates[index]
            if index+1 > len(listeDates)-1 :
                date2 = date_fin
            else :
                date2 = listeDates[index+1]
            listeDates2.append((date1, date2))
        
        # Création des périodes
        listePeriodes = []
        for date1, date2 in listeDates2 :
            label_prestation = dictParametres["label_prestation"]
            
            # Création du label de la prestation
            if dictParametres["periodicite"] == 0 :
                nom_auto = str(date1.year)
            if dictParametres["periodicite"] == 1 :
                nom_auto = u"%s %d" % (LISTE_MOIS[date1.month-1].capitalize(), date1.year)
            if dictParametres["periodicite"] == 2 :
                nom_auto = _(u"Semaine %d") % date1.isocalendar()[1]
            
            label_prestation = label_prestation.replace("{LABEL_AUTO}", nom_auto)
            label_prestation = label_prestation.replace("{ANNEE}", str(date1.year))
            label_prestation = label_prestation.replace("{NUM_MOIS}", str(date1.month))
            label_prestation = label_prestation.replace("{NOM_MOIS}", LISTE_MOIS[date1.month-1].capitalize())
            label_prestation = label_prestation.replace("{NUM_SEMAINE}", str(date1.isocalendar()[1]))
            label_prestation = label_prestation.replace("{DATE_DEBUT}", UTILS_Dates.DateDDEnFr(date1))
            label_prestation = label_prestation.replace("{DATE_FIN}", UTILS_Dates.DateDDEnFr(date2))
            
            # Date de la prestation
            if dictParametres["date_prestation"] == 0 :
                date_prestation = date1.date() 
            else :
                date_prestation = date2.date() 
            
            # Mémorisation
            dictPeriode = {
                "IDprestation" : None, 
                "date_debut" : date1.date(), 
                "date_fin" : date2.date(),
                "montant_prestation" : dictParametres["montant_prestation"],
                "label_prestation" : label_prestation,
                "date_prestation" : date_prestation,
                "IDfacture" : None,
                "listeConso" : [],
                }
            listePeriodes.append(dictPeriode)
    
        # Vérifie que les périodes générées ne chevauchent pas des périodes existantes
        for dictPeriode in listePeriodes :
            for track in self.listeTracks :
                if dictPeriode["date_fin"] >= track.date_debut and dictPeriode["date_debut"] <= track.date_fin :
                    dlg = wx.MessageDialog(self, _(u"Génération impossible !\n\nLa période '%s' chevauche la période existante '%s' (du %s au %s).") % (dictPeriode["label_prestation"], track.label_prestation, UTILS_Dates.DateDDEnFr(track.date_debut), UTILS_Dates.DateDDEnFr(track.date_fin)), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        self.listeResultats = listePeriodes
        return True
    
    def GetResultats(self):
        return self.listeResultats
    
    
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDactivite=1)
    dlg.ctrl_date_debut.SetDate("2014-01-01")
    dlg.ctrl_date_fin.SetDate("2014-12-31")
    dlg.ctrl_label_prestation.SetLabel(_(u"Centre de Loisirs - {LABEL_AUTO}"))
    dlg.ctrl_montant_prestation.SetMontant(50.0)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    for x in dlg.GetResultats() :
        print x
    app.MainLoop()
