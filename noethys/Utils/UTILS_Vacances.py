#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-21 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import six
from six.moves.urllib.request import urlopen
import datetime, json, codecs
from Utils import UTILS_Dates


class Calendrier():
    def __init__(self, zone="A"):
        self.zone = zone
        try:
            # fichier = codecs.open(nom_fichier, "rb", encoding='utf-8')
            fichier = urlopen("https://www.data.gouv.fr/fr/datasets/r/000ae493-9fa8-4088-9f53-76d375204036", timeout=5)
            self.data = json.load(fichier)
            fichier.close()
        except:
            self.data = {}

    def GetVacances(self):
        """ Récupère les périodes de vacances """
        liste_items = []
        for item in self.data:
            if item["fields"]["zones"] == "Zone %s" % self.zone.upper() and "end_date" in item["fields"] and u"Enseignants" not in item["fields"].get("population", ""):
                description = item["fields"]["description"]
                date_debut = UTILS_Dates.DateEngEnDateDD(item["fields"]["start_date"])
                if date_debut.weekday() != 5:
                    date_debut += datetime.timedelta(days=1)
                date_fin = UTILS_Dates.DateEngEnDateDD(item["fields"]["end_date"]) - datetime.timedelta(days=1)
                annee = date_debut.year

                if u"Hiver" in description: nom = u"Février"
                elif u"Printemps" in description: nom = u"Pâques"
                elif u"Été" in description: nom = u"Eté"
                elif u"Toussaint" in description: nom = u"Toussaint"
                elif u"Noël" in description: nom = u"Noël"
                else: nom = None

                periode = {"annee": annee, "nom": nom, "date_debut": date_debut, "date_fin": date_fin}
                if nom and periode not in liste_items:
                    liste_items.append(periode)

        # Tri par date de début
        if six.PY2:
            liste_items.sort(lambda x, y: cmp(x["date_debut"], y["date_debut"]))
        else:
            liste_items.sort(key=lambda x: x["date_debut"])

        return liste_items


if __name__ == "__main__":
    cal = Calendrier(zone="B")
    for item in cal.GetVacances():
        print(item)
