#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import datetime
import time
import wx
import six
from six.moves import range

LISTE_JOURS = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
LISTE_MOIS = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
LISTE_JOURS_ABREGES = (_(u"Lun."), _(u"Mar."), _(u"Mer."), _(u"Jeu."), _(u"Ven."), _(u"Sam."), _(u"Dim."))
LISTE_MOIS_ABREGES = (_(u"janv."), _(u"fév."), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juil."), _(u"août"), _(u"sept."), _(u"oct"), _(u"nov."), _(u"déc."))


def DateEngFr(textDate):
    if textDate in (None, "") : return ""
    if type(textDate) == datetime.date : return DateDDEnFr(textDate)
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateDDEnFr(date):
    if date == None : return ""
    return DateEngFr(str(date))
    
def DateComplete(dateDD, abrege=False):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    if dateDD == None : return u""
    if abrege == False :
        listeJours, listeMois = LISTE_JOURS, LISTE_MOIS
    else :
        listeJours, listeMois = LISTE_JOURS_ABREGES, LISTE_MOIS_ABREGES
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng in (None, "", "None") : return None
    if type(dateEng) == datetime.date : return dateEng
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngEnDateDDT(dateEng):
    if dateEng in (None, "", "None") : return None
    if type(dateEng) == datetime.datetime : return dateEng
    if len(dateEng) == 19 :
        return datetime.datetime.strptime(dateEng, "%Y-%m-%d %H:%M:%S")
    else :
        return datetime.datetime.strptime(dateEng, "%Y-%m-%d %H:%M:%S.%f")

def PeriodeComplete(mois, annee):
    listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete

def CalculeAge(dateReference=None, date_naiss=None):
    """ Calcul de l'age de la personne """
    if dateReference == None :
        dateReference = datetime.date.today()
    if date_naiss in (None, "") :
        return None
    age = (dateReference.year - date_naiss.year) - int((dateReference.month, dateReference.day) < (date_naiss.month, date_naiss.day))
    return age

def HeuresEnDecimal(texteHeure="07:00"):
    """ Transforme une heure string ou datetime.time en entier de type 2075"""
    if texteHeure == None :
        return 0
    if type(texteHeure) == datetime.time :
        heures = str(texteHeure.hour)
        minutes = int(texteHeure.minute)
    if type(texteHeure) in (str, six.text_type) :
        posTemp = texteHeure.index(":")
        heures = str(texteHeure[0:posTemp])
        minutes = int(texteHeure[posTemp+1:5])
    minutes = str(minutes * 100 //60)
    if len(minutes) == 1 : minutes = "0" + minutes
    heure = str(heures + minutes)
    return int(heure)

def FloatEnDelta(valeur=10.50):
    """ Convertit une valeur décimale en timedelta """
    return datetime.timedelta(hours=valeur)

def DeltaEnFloat(valeur=datetime.timedelta(0)):
    """ Convertit une valeur décimale en timedelta """
    return (valeur.days*24) + (valeur.seconds/3600.0)

def DeltaEnHeures(valeur=datetime.timedelta(0)):
    """ Convertit une durée timedelta en nombre d'heures"""
    return (valeur.days*24) + (valeur.seconds/3600.0)

def SoustractionHeures(heure_max, heure_min):
    """ Effectue l'opération heure_max - heure_min. Renvoi un timedelta """
    if type(heure_max) != datetime.timedelta : heure_max = datetime.timedelta(hours=heure_max.hour, minutes=heure_max.minute)
    if type(heure_min) != datetime.timedelta : heure_min =  datetime.timedelta(hours=heure_min.hour, minutes=heure_min.minute)
    return heure_max - heure_min

def AdditionHeures(heure1, heure2):
    """ Effectue l'opération heure_max - heure_min. Renvoi un timedelta """
    if type(heure1) != datetime.timedelta : heure1 = datetime.timedelta(hours=heure1.hour, minutes=heure1.minute)
    if type(heure2) != datetime.timedelta : heure2 =  datetime.timedelta(hours=heure2.hour, minutes=heure2.minute)
    return heure1 + heure2

def Additionne_intervalles_temps(intervals=[]):
    def tparse(timestring):
        return datetime.datetime.strptime(timestring, '%H:%M')

    START, END = range(2)
    times = []
    for interval in intervals:
        times.append((tparse(interval[START]), START))
        times.append((tparse(interval[END]), END))
    times.sort()

    started = 0
    result = datetime.timedelta()
    for t, categorie in times:
        if categorie == START:
            if not started:
                start_time = t
            started += 1
        elif categorie == END:
            started -= 1
            if not started:
               result += (t - start_time)
    return result

def DeltaEnTime(varTimedelta) :
    """ Transforme une variable TIMEDELTA en heure datetime.time """
    heureStr = time.strftime("%H:%M", time.gmtime(varTimedelta.seconds))
    heure = HeureStrEnTime(heureStr)
    return heure

def DeltaEnStr(heureDelta, separateur="h"):
    if heureDelta < datetime.timedelta(0):
        signe = "-"
        heureDelta = -heureDelta
    else :
        signe = ""

    heures = (heureDelta.days*24) + (heureDelta.seconds//3600)
    minutes = heureDelta.seconds%3600//60
    valeur = "{}{}{}{:0>2}".format(signe, heures, separateur, minutes)
    return valeur

    # heures = (heureDelta.days*24) + (heureDelta.seconds/3600)
    # minutes = heureDelta.seconds%3600/60
    # return "%d%s%02d" % (heures, separateur, minutes)

    # texte = time.strftime("%Hh%M", time.gmtime(heureDelta.seconds))
    # texte = texte.replace("h", separateur)
    # return texte

def TimeEnDelta(heureTime):
    if heureTime == None :
        return datetime.timedelta(0)
    hr = heureTime.hour
    mn = heureTime.minute
    return datetime.timedelta(hours=hr, minutes=mn)

def HeureStrEnDelta(heureStr):
    if heureStr == None or heureStr == "" : return datetime.timedelta(hours=0, minutes=0)
    if "h" in heureStr :
        heureStr = heureStr.replace("h", ":")
    if ":" not in heureStr :
        heureStr += u":"
    if len(heureStr.split(":")) == 2 :
        heures, minutes = heureStr.split(":")
    if len(heureStr.split(":")) == 3 :
        heures, minutes, secondes = heureStr.split(":")
    if heures == "" : heures = 0
    if minutes == "" : minutes = 0
    return datetime.timedelta(hours=int(heures), minutes=int(minutes))

def HeureStrEnTime(heureStr):
    if heureStr == None or heureStr == "" : return datetime.time(0, 0)
    if len(heureStr.split(":")) == 2 : heures, minutes = heureStr.split(":")
    if len(heureStr.split(":")) == 3 : heures, minutes, secondes = heureStr.split(":")
    try :
        return datetime.time(int(heures), int(minutes))
    except :
        return datetime.time(0, 0)

def DatetimeTimeEnStr(heure, separateur="h"):
    if heure == None : 
        return None
    else :
        return u"%02d%s%02d" % (heure.hour, separateur, heure.minute)

def HorodatageEnDatetime(horodatage, separation=None):
    if separation == None :
        annee = int(horodatage[0:4])
        mois = int(horodatage[4:6])
        jour = int(horodatage[6:8])
        heures = int(horodatage[8:10])
        minutes = int(horodatage[10:12])
        secondes = int(horodatage[12:14])
        horodatage = datetime.datetime(annee, mois, jour, heures, minutes, secondes)
    else :
        annee, mois, jour, heures, minutes, secondes = horodatage.split(separation)
        horodatage = datetime.datetime(int(annee), int(mois), int(jour), int(heures), int(minutes), int(secondes))
    return horodatage

def ArrondirTime(heure=datetime.time(hour=10, minute=25), delta_minutes=15, sens="inf"):
    """ sens = 'sup' ou 'inf' """
    dt = datetime.datetime(year=2015, month=1, day=1, hour=heure.hour, minute=heure.minute)
    if dt.minute % delta_minutes :
        if sens == "sup" :
            resultat = dt + datetime.timedelta(minutes = delta_minutes - dt.minute % delta_minutes)
        if sens == "inf" :
            resultat = dt - datetime.timedelta(minutes = dt.minute % delta_minutes)
    else:
        resultat = dt
    return datetime.time(hour=resultat.hour, minute=resultat.minute)

def ArrondirDelta(duree=datetime.timedelta(hours=1, minutes=25), delta_minutes=15, sens="sup"):
    duree_minutes = duree.seconds // 60
    if duree_minutes % delta_minutes :
        if sens == "sup" :
            resultat = duree + datetime.timedelta(minutes = delta_minutes - duree_minutes % delta_minutes)
        if sens == "inf" :
            resultat = duree - datetime.timedelta(minutes = duree_minutes % delta_minutes)
    else :
        resultat = duree
    return resultat

def CalculerArrondi(arrondi_type="duree", arrondi_delta=15, heure_debut=None, heure_fin=None):
    """
    :param arrondi_type: None ou duree ou tranche_horaire
    :param arrondi_delta: minutes
    :param heure_debut: heure_debut en time
    :param heure_fin: heure_fin en time
    :return: datetime.time
    """
    duree_reelle = SoustractionHeures(heure_fin, heure_debut)

    if arrondi_type == None :
        duree_arrondie = duree_reelle

    if arrondi_type == "tranche_horaire" :
        heure_debut_temp = ArrondirTime(heure=heure_debut, delta_minutes=arrondi_delta, sens="inf")
        heure_fin_temp = ArrondirTime(heure=heure_fin, delta_minutes=arrondi_delta, sens="sup")
        duree_arrondie = SoustractionHeures(heure_fin_temp, heure_debut_temp)

    if arrondi_type == "duree" :
        duree_arrondie = ArrondirDelta(duree=duree_reelle, delta_minutes=arrondi_delta, sens="sup")

    return duree_arrondie

def ArrondirDT(dt=None, dateDelta=datetime.timedelta(minutes=1)):
    """ Arrondir un datetime.datetime """
    roundTo = dateDelta.total_seconds()
    if dt == None : dt = datetime.datetime.now()
    seconds = (dt - dt.min).seconds
    rounding = (seconds+roundTo//2) // roundTo * roundTo
    return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

def FormateMois(donnee):
    if donnee in ("", None):
        return ""
    else:
        annee, mois = donnee
        return u"%s %d" % (LISTE_MOIS[mois-1].capitalize(), annee)

def ConvertDateWXenDT(datewx=None):
    """ Convertit une date WX.datetime en datetime """
    if datewx == None :
        return None
    jour = datewx.GetDay()
    mois = datewx.GetMonth()+1
    annee = datewx.GetYear()
    heures = datewx.GetHour()
    minutes = datewx.GetMinute()
    dt = datetime.datetime(annee, mois, jour, heures, minutes)
    return dt

def ConvertDateDTenWX(date=None):
    """ Convertit une date datetime en WX.datetime """
    if date == None :
        return None
    datewx = wx.DateTime()
    datewx.Set(date.day, month=date.month-1, year=date.year)
    return datewx

def DatetimeEnFr(date=None):
    if type(date) == str :
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return date.strftime("%d/%m/%Y %H:%M:%S")

def FormatDelta(delta, fmt="auto"):
    """ fmt = 'auto' ou par exemple : '{jours} jours {heures}:{minutes}:{secondes}' """
    # Recherche des valeurs
    d = {"jours": delta.days}
    d["heures"], rem = divmod(delta.seconds, 3600)
    d["minutes"], d["secondes"] = divmod(rem, 60)
    # Formatage des valeurs
    if fmt == "auto" :
        temp = []
        if d["jours"] == 1 : temp.append("{jours} jour")
        if d["jours"] > 1 : temp.append("{jours} jours")
        if d["heures"] == 1 : temp.append("{heures} heure")
        if d["heures"] > 1: temp.append("{heures} heures")
        if d["minutes"] == 1 : temp.append("{minutes} minute")
        if d["minutes"] > 1: temp.append("{minutes} minutes")
        fmt = " ".join(temp)
    return fmt.format(**d)



if __name__ == "__main__":
    # Tests
    #print CalculerArrondi(arrondi_type="tranche_horaire", arrondi_delta=15, heure_debut=datetime.time(9, 25), heure_fin=datetime.time(9, 35))
    #print ArrondirDT(datetime.datetime.now(), datetime.timedelta(minutes=5))
    print(FormatDelta(datetime.timedelta(hours=48, minutes=30)))

