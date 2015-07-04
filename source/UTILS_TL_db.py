#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# Copyright (C) 2009  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


"""
Implementation of Timeline with flat file storage.

The class FileTimeline implements the Timeline interface.
"""
from UTILS_Traduction import _

import wx
import CTRL_Bouton_image

import re
import codecs
import shutil
import os.path
from os.path import abspath
import datetime

from UTILS_TL_data import TimelineIOError
from UTILS_TL_data import Timeline
from UTILS_TL_data import TimePeriod
from UTILS_TL_data import Event
from UTILS_TL_data import Category
from UTILS_TL_data import time_period_center
from UTILS_TL_data import get_event_data_plugins
from UTILS_TL_data import get_event_data_plugin


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def CalculeAge(dateReference, date_naiss):
    # Calcul de l'age de la personne
    age = (dateReference.year - date_naiss.year) - int((dateReference.month, dateReference.day) < (date_naiss.month, date_naiss.day))
    return age

def HeureStrEnTime(heureStr):
    if heureStr == None or heureStr == "" : return datetime.time(0, 0, 0)
    if len(heureStr) > 5 :
        heures, minutes, secondes = heureStr.split(":")
    else:
        heures, minutes = heureStr.split(":")
        secondes = 0
    return datetime.time(int(heures), int(minutes), int(secondes))



class ParseException(Exception):
    """Thrown if parsing of data read from file fails."""
    pass


class TimelinePerso(Timeline):
    # Errors caused by loading and saving timeline data to file
    ERROR_NONE    = 0
    ERROR_READ    = 1 # Unable to read from file
    ERROR_CORRUPT = 2 # Able to read from file but content corrupt
    ERROR_WRITE   = 3 # Unable to write to file

    def __init__(self):
        Timeline.__init__(self)
        self._load_data()

    def get_events(self, time_period):
        def include_event(event):
            if not event.inside_period(time_period):
                return False
            if event.category != None and event.category.visible == False:
                return False
            return True
        return [event for event in self.events if include_event(event)]

    def add_event(self, event):
        self.events.append(event)
        self._save_data()

    def event_edited(self, event):
        self._save_data()

    def select_event(self, event, selected=True):
        event.selected = selected
        self._notify(Timeline.STATE_CHANGE_ANY)

    def delete_selected_events(self):
        self.events = [event for event in self.events if not event.selected]
        self._save_data()

    def reset_selected_events(self):
        for event in self.events:
            event.selected = False
        self._notify(Timeline.STATE_CHANGE_ANY)

    def get_categories(self):
        # Make sure the original list can't be modified
        return tuple(self.categories)

    def add_category(self, category):
        self.categories.append(category)
        self._save_data()
        self._notify(Timeline.STATE_CHANGE_CATEGORY)

    def category_edited(self, category):
        self._save_data()
        self._notify(Timeline.STATE_CHANGE_CATEGORY)

    def delete_category(self, category):
        if category in self.categories:
            self.categories.remove(category)
        for event in self.events:
            if event.category == category:
                event.category = None
        self._save_data()
        self._notify(Timeline.STATE_CHANGE_CATEGORY)

    def get_preferred_period(self):
        if self.preferred_period != None:
            return self.preferred_period
        return time_period_center(datetime.datetime.now(), datetime.timedelta(days=30))

    def set_preferred_period(self, period):
        if not period.is_period():
            raise TimelineIOError("Preferred period must be > 0.")
        self.preferred_period = period
        self._save_data()


# ----------------------------------------------------------------------------------------------------------------------------------------

    def _load_data(self):
        """ Importation des données """
        self.preferred_period = None
        self.categories = []
        self.events = []
        self.error_flag = TimelinePerso.ERROR_NONE
        
        ################### TEST AVEC VRAIES DONNEES  ####################
        
##        # Période préférée
##        dateDebut = datetime.datetime(2011, 1, 1, 9, 52, 0)
##        dateFin = datetime.datetime(2011, 12, 31, 18, 52, 0)
##        self.preferred_period = TimePeriod(dateDebut, dateFin)

        import GestionDB
        from UTILS_Historique import CATEGORIES as dictCategories
        
##        # Récupération des catégories
##        dictCategorieTemp = {}
##        for IDcategorie, nomCategorie in dictCategories.iteritems() :
##            categorie = Category(nomCategorie, (0, 255, 0), True)
##            self.categories.append(categorie)
##            dictCategorieTemp[IDcategorie] = categorie
##        
##        # Récupération des events
##        DB = GestionDB.DB()
##        req = """SELECT IDaction, date, heure, IDcategorie, action
##        FROM historique
##        WHERE IDfamille=7
##        ORDER BY date, heure;"""
##        DB.ExecuterReq(req)
##        listeActions = DB.ResultatReq()
##        DB.Close()
##        
##        for IDaction, date, heure, IDcategorie, action in listeActions :
##            date = DateEngEnDateDD(date)
##            heure = HeureStrEnTime(heure)
##            dateDebut = datetime.datetime(date.year, date.month, date.day, heure.hour, heure.minute, heure.second)
##            nomCategorie = dictCategories[IDcategorie]
##            texte = nomCategorie
##            categorie = dictCategorieTemp[IDcategorie]
##            description = action
##            icon = None
##            
##            evt = Event(dateDebut, dateDebut, texte, categorie)
##            if description != None : evt.set_data("description", description)
##            if icon != None : evt.set_data("icon", icon)
##            self.events.append(evt)
##
##        ################### TEsT AVEC CONSOMMATIONS ####################
##                
##        
##        # Récupération des events
##        DB = GestionDB.DB()
##        req = """SELECT IDconso, IDindividu, IDactivite, date, heure_debut, heure_fin, IDunite, IDgroupe, etat
##        FROM consommations
##        WHERE IDunite=1 AND IDcompte_payeur=6
##        ORDER BY date;"""
##        DB.ExecuterReq(req)
##        listeConso = DB.ResultatReq()
##        DB.Close()
##        
##        for IDconso, IDindividu, IDactivite, date, heure_debut, heure_fin, IDunite, IDgroupe, etat in listeConso :
##            date = DateEngEnDateDD(date)
##            heure_debut = HeureStrEnTime(heure_debut)
##            heure_fin = HeureStrEnTime(heure_fin)
##            dateDebut = datetime.datetime(date.year, date.month, date.day, heure_debut.hour, heure_debut.minute, heure_debut.second)
##            dateFin = datetime.datetime(date.year, date.month, date.day, heure_fin.hour, heure_fin.minute, heure_fin.second)
##            texte = _(u"IDindividu %d") % IDindividu
##            categorie = None
##            description = _(u"IDunite%d - IDgroupe%d") % (IDunite, IDgroupe)
##            icon = None
##            
##            evt = Event(dateDebut, dateFin, texte, categorie)
##            if description != None : evt.set_data("description", description)
##            if icon != None : evt.set_data("icon", icon)
##            self.events.append(evt)


        
        ################### TEST AVEC ANNIVERSAIRES ####################
        
        
        # Période préférée
        dateDuJour = datetime.datetime.today()
        dateDebut = dateDuJour - datetime.timedelta(1)
        dateFin = dateDuJour + datetime.timedelta(3)
        self.preferred_period = TimePeriod(dateDebut, dateFin)
        
        # Récupération des events
        DB = GestionDB.DB()
        req = """SELECT IDindividu, nom, prenom, date_naiss
        FROM individus
        ORDER BY date_naiss;"""
        DB.ExecuterReq(req)
        listeIndividus = DB.ResultatReq()
        DB.Close()
        
        for IDindividu, nom, prenom, date_naiss in listeIndividus :
            if date_naiss != None :
                
                date_naiss = DateEngEnDateDD(date_naiss)
                for numAnnee in range(date_naiss.year, date_naiss.year+70) : # Boucle sur 100 ans
                    date = datetime.date(numAnnee, date_naiss.month, date_naiss.day)
                    age = CalculeAge(date, date_naiss)

                    dateDebut = datetime.datetime(date.year, date.month, date.day, 9, 0, 0)
                    texte = u"%s %s" % (prenom, nom)
                    categorie = None
                    description = _(u"%s a %d ans") % (prenom, age)
                    icon = None
                    
                    evt = Event(dateDebut, dateDebut, texte, categorie)
                    if description != None : evt.set_data("description", description)
                    if icon != None : evt.set_data("icon", icon)
                    self.events.append(evt)



            ################### TEST AVEC DONNEES FICTIVES ####################
            
##        # Importation de la période préférée
##        dateDebut = datetime.datetime(2011, 8, 11, 9, 52, 0)
##        dateFin = datetime.datetime(2011, 8, 13, 18, 52, 0)
##        self.preferred_period = TimePeriod(dateDebut, dateFin)
##        
##        # Importation d'une catégorie
##        catExemple = Category(_(u"Catégorie Exemple"), (0, 255, 0), True)
##        self.categories.append(catExemple)
##        
##        # Importation d'un Event
##        dateDebut = datetime.datetime(2011, 8, 12, 9, 52, 0)
##        dateFin = datetime.datetime(2011, 8, 12, 9, 52, 0)
##        texte = _(u"Evènement 1")
##        categorie = catExemple
##        description = _(u"Ceci est la description de l'event 1")
##        icon = wx.Bitmap("Images/32x32/Anniversaire.png", wx.BITMAP_TYPE_ANY)
##        
##        # Mémorisation de l'event
##        evt = Event(dateDebut, dateFin, texte, categorie)
##        if description != None : evt.set_data("description", description)
##        if icon != None : evt.set_data("icon", icon)
##        self.events.append(evt)

    def _save_data(self):
        print "--------- Sauvegarde fictive : ----------"
        
        # Sauvegarde de la période préférée
        print "Periode preferee :"
        print (self.preferred_period.start_time, self.preferred_period.end_time)
        
        # Sauvegarde des catégories
        print "Categories :"
        for categorie in self.categories:
            print (categorie.name, categorie.color, categorie.visible)
        
        # Sauvegarde des events
        print "Events :"
        for event in self.events :
            dateDebut = event.time_period.start_time
            dateFin = event.time_period.end_time
            texte = event.text
            if event.category != None :
                nomCategorie = event.category.name
            else:
                nomCategorie = u""
            description = event.get_data("description")
            icon = event.get_data("icon")
            
            print ">>>>>> EVENT  >>>>>>>>>>>"
            print (dateDebut, dateFin) # time.year, time.month, time.day, time.hour, time.minute, time.second
            print (texte,)
            print (nomCategorie,)
            print (description,)
            print (icon,)
            print "-------------------------------------------------"
            
        # Indique que tout a été sauvegardé
        self._notify(Timeline.STATE_CHANGE_ANY)
        
        print "Fin sauvegarde."
