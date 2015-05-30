#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import icalendar
import urllib2
import datetime


class Calendrier():
    def __init__(self, nomFichier=None, url=None):
        try :
            # Ouverture du calendrier
            if url != None :
                fichier = urllib2.urlopen(url, timeout=5)
            if nomFichier != None :
                fichier = open(nomFichier, "rb")
            # Lecture du fichier
            self.cal = icalendar.Calendar.from_ical(fichier.read())
            fichier.close()
        except :
            self.cal = None

    def GetEvents(self):
        """ Parcours les Events """
        listeEvents = []
        for component in self.cal.walk():
            if component.name == "VEVENT" :
                description = self.RechercheElement(component, "DESCRIPTION", "texte")
                date_debut = self.RechercheElement(component, "DTSTART", "date")
                date_fin = self.RechercheElement(component, "DTEND", "date")
                listeEvents.append({"description" : description, "date_debut" : date_debut, "date_fin" : date_fin})
        return listeEvents
    
    def RechercheElement(self, component=None, nom="DTSTART", type="date"):
        """ Recherche un élément dans un Event """
        if component.has_key(nom) :
            if type == "date" : return component.decoded(nom)
            if type == "texte" : return u"%s" % component[nom]
        else :
            return None
    
    def GetTitre(self):
        """ Récupère le titre du calendrier """
        try :
            titre = self.cal["X-WR-CALNAME"]
        except :
            titre = None
        return titre
    
    def GetVacances(self):
        """ Récupère les périodes de vacances """
        listeEvents = self.GetEvents() 
        listeResultats = []
        listeCorrespondances = [
            (_(u"hiver"), _(u"Février")),
            (_(u"printemps"), _(u"Pâques")),
            (u"été", _(u"Eté")),
            (_(u"Toussaint"), _(u"Toussaint")),
            (_(u"Noël"), _(u"Noël")),
            ]
            
        for nomOriginal, nomFinal in listeCorrespondances :
            for dictEvent in listeEvents :
                if nomOriginal in dictEvent["description"] :
                    if dictEvent["date_debut"] != None and dictEvent["date_fin"] != None :
                        annee = dictEvent["date_debut"].year
                        date_debut = dictEvent["date_debut"]
                        date_fin = dictEvent["date_fin"] - datetime.timedelta(days=1)
                        listeResultats.append({"annee" : annee, "nom" : nomFinal, "date_debut" : date_debut, "date_fin" : date_fin})
        
        # Tri par date de début
        listeResultats.sort(lambda x,y: cmp(x["date_debut"], y["date_debut"]))
        
        return listeResultats
        
        
        
        


if __name__ == "__main__":
    cal = Calendrier(url="http://media.education.gouv.fr/ics/Calendrier_Scolaire_Zone_A.ics")
    print ">>", cal.GetTitre()
##    for event in cal.GetEvents() :
##        print event
    for x in cal.GetVacances() :
        print x
        