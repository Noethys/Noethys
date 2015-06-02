#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import sys
import CTRL_Newsticker
import wx.lib.analogclock as clock
import GestionDB

import datetime
import random
import threading

from DATA_Celebrations import DICT_FETES
from DATA_Celebrations import DICT_CELEBRATIONS
from DATA_Citations import LISTE_CITATIONS

try :
    from UTILS_Astral import City
except Exception, err :
    print err
    
import UTILS_Meteo


def DateDDEnDateFR(dateDD):
    """ Transforme une datetime.date en date complète FR """
    listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    return listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def Concatenation(listeTextes=[]):
    if len(listeTextes) == 0 : 
        return ""
    elif len(listeTextes) == 1 :
        return listeTextes[0]
    elif len(listeTextes) == 2 :
        return _(u"%s et %s") % (listeTextes[0], listeTextes[1])
    else :
        premiers = ", ".join(listeTextes[:-1])
        return _(u"%s et %s") % (premiers, listeTextes[-1])

def GetAge(date_naiss=None):
    if date_naiss == None : return None
    datedujour = datetime.date.today()
    age = (datedujour.year - date_naiss.year) - int((datedujour.month, datedujour.day) < (date_naiss.month, date_naiss.day))
    return age

    

class CTRL(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.dateJour = datetime.date.today()
        self.dictOrganisateur = None
        
        # Horloge
        self.ctrl_horloge = clock.AnalogClock(self, size=(80, 80), 
                            hoursStyle=clock.TICKS_SQUARE,
                            minutesStyle=clock.TICKS_CIRCLE,
                            clockStyle=clock.SHOW_HOURS_TICKS| \
                                       clock.SHOW_MINUTES_TICKS|
                                       clock.SHOW_HOURS_HAND| \
                                       clock.SHOW_MINUTES_HAND| \
                                       clock.SHOW_SECONDS_HAND)
        self.ctrl_horloge.SetTickSize(12, target=clock.HOUR)
        
        # Date du jour
        self.ctrl_date = wx.StaticText(self, -1, DateDDEnDateFR(self.dateJour))
        
        # Newsticker
        self.ctrl_ticker = CTRL_Newsticker.Newsticker(self, pauseTime=10000, start=False, size=(-1, 100))   
        self.ctrl_ticker.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        
        # Adaptation pour Linux : Couleur de l'horloge
        if  "linux" in sys.platform :
            couleur = self.ctrl_date.GetBackgroundColour()
            self.ctrl_horloge.SetBackgroundColour(couleur)
            self.ctrl_horloge.SetFaceFillColour(couleur)
            self.ctrl_horloge.SetFaceBorderColour(couleur)
        
        self.__set_properties()
        self.__do_layout()
        
        self.ctrl_ticker.Start()

    def __set_properties(self):
        self.ctrl_date.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_droite = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_horloge, 0, wx.LEFT|wx.ALL, 10)
        grid_sizer_droite.Add(self.ctrl_date, 0, wx.EXPAND|wx.TOP, 5)
        grid_sizer_droite.Add(self.ctrl_ticker, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.TOP, 5)
        grid_sizer_droite.AddGrowableRow(1)
        grid_sizer_droite.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_droite, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
    
    def Initialisation(self):
        timerInit = threading.Thread(None, self.InitListes)
        timerInit.start()
        
    def InitListes(self):
        try :
            listePages = []
            
            # Infos Organisateur
            self.dictOrganisateur = self.GetOrganisateur() 
            
            # Ajout des célébrations
            texte = self.GetCelebrations()
            if texte != None :
                listePages.append(texte)

            # Ajout des anniversaires
            texte = self.GetAnniversaires()
            if texte != None :
                listePages.append(texte)

            # Ajout de la citation
            texte = self.GetCitation()
            if texte != None :
                listePages.append(texte)

            # Ajout des heures de soleil
            texte = self.GetSoleil()
            if texte != None :
                listePages.append(texte)
            
            # Ajout de la météo
##            texte = self.GetMeteo()
##            if texte != None :
##                listePages.append(texte)
            
            # Envoi des textes au ticker
            self.ctrl_ticker.SetPages(listePages, restart=True)
        
        except :
            pass
        
    def StartTicker(self):
        self.ctrl_ticker.Start()
    
    def StopTicker(self):
        self.ctrl_ticker.Stop()

    def GetOrganisateur(self):
        """ Récupère les infos sur l'organisateur """
        DB = GestionDB.DB()
        req = """SELECT cp, ville, gps
        FROM organisateur WHERE IDorganisateur=1;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return None
        cp, ville, gps = listeDonnees[0]
        if cp == None : cp = ""
        if ville == None : ville = ""
        if gps == None : gps = ""
        if len(gps) > 0 :
            lat, long = gps.split(";") 
        else :
            lat, long = self.GetGPSOrganisateur(cp, ville) 
        dictOrganisateur = {"cp":cp, "ville":ville, "lat":lat, "long":long}
        return dictOrganisateur
    
    def GetGPSOrganisateur(self, cp="", ville=""):
        """ Récupère les coordonnées GPS de l'organisateur """
        if ville == "" or cp == "" : 
            return None, None
        # Recherche des coordonnées
        import UTILS_Gps
        dictGPS = UTILS_Gps.GPS(cp=cp, ville=ville, pays="France")
        if dictGPS == None : 
            lat, long = None, None
        else :
            # Sauvegarde des coordonnées GPS dans la base
            lat, long = dictGPS["lat"], dictGPS["long"]
            DB = GestionDB.DB()
            DB.ReqMAJ("organisateur", [("gps", u"%s;%s" % (str(lat), str(long)) ),], "IDorganisateur", 1)
            DB.Close()
        return lat, long
        
    def GetCelebrations(self):
        """ Récupère les célébrations du jour """
        try :
            # Fêtes
            texteFetes = ""
            if DICT_FETES.has_key((self.dateJour.day, self.dateJour.month)) :
                noms = DICT_FETES[(self.dateJour.day, self.dateJour.month)]
                listeNoms = noms.split(";")
                texteFetes = Concatenation(listeNoms)
                
            # Fêtes
            texteCelebrations = ""
            if DICT_CELEBRATIONS.has_key((self.dateJour.day, self.dateJour.month)) :
                texteCelebrations = DICT_CELEBRATIONS[(self.dateJour.day, self.dateJour.month)]
                
            # Mix des fêtes et des célébrations
            texte = u""
            intro = _(u"<t>LES CELEBRATIONS DU JOUR</t>")
            if len(texteFetes) > 0 and len(texteCelebrations) > 0 : texte = _(u"%sNous fêtons aujourd'hui les %s et célébrons %s.") % (intro, texteFetes, texteCelebrations)
            if len(texteFetes) > 0 and len(texteCelebrations) == 0 : texte = _(u"%sNous fêtons aujourd'hui les %s.") % (intro, texteFetes)
            if len(texteFetes) == 0 and len(texteCelebrations) > 0 : texte = _(u"%sNous célébrons aujourd'hui %s.") % (intro, texteCelebrations)
            if texte == "" : 
                return None
            return texte
        
        except :
            return None

    def GetAnniversaires(self):
        """ Récupère les anniversaires """
        try :
            conditionJour = "%02d-%02d" % (self.dateJour.month, self.dateJour.day) 
            DB = GestionDB.DB()
            req = """SELECT individus.IDindividu, nom, prenom, date_naiss
            FROM individus 
            LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
            WHERE  date_naiss LIKE '%%%s' AND IDinscription IS NOT NULL
            GROUP BY individus.IDindividu
            ORDER BY date_naiss DESC
            ;""" % conditionJour
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 : return None
            listeTextes = []
            for IDindividu, nom, prenom, date_naiss in listeDonnees :
                date_naiss = DateEngEnDateDD(date_naiss)
                age = GetAge(date_naiss)
                listeTextes.append(_(u"%s %s (%d ans)") % (prenom, nom, age))
            texte = _(u"<t>LES ANNIVERSAIRES DU JOUR</t>Joyeux anniversaire à %s.") % Concatenation(listeTextes)
            return texte
        
        except :
            return None

    def GetCitation(self):
        """ Récupère la citation du jour """
        texte = ""
        index = random.randint(0, len(LISTE_CITATIONS) - 1)
        citation, auteur = LISTE_CITATIONS[index]
        texte = _(u"<t>LA CITATION DU JOUR</t>%s (%s)") % (citation, auteur)
        return texte

    def GetSoleil(self):
        """ Récupère les heures de lever et de coucher du soleil """
        try :
            # Récupère les coordonnées GPS de l'organisateur
            if self.dictOrganisateur == None : 
                return None
            ville = self.dictOrganisateur["ville"]
            lat = self.dictOrganisateur["lat"]
            long = self.dictOrganisateur["long"]
            if ville == "" or ville == None or lat == None or long == None : 
                return None
            
            # Récupère les heures de lever et de coucher du soleil
            c = City((ville, "France", float(lat), float(long), "Europe/Paris"))
            heureLever = c.sunrise()
            heureCoucher = c.sunset()
            texte = _(u"<t>HORAIRES DU SOLEIL</t>Aujourd'hui à %s, le soleil se lève à %dh%02d et se couche à %dh%02d.") % (ville.capitalize(), heureLever.hour, heureLever.minute, heureCoucher.hour, heureCoucher.minute)
            return texte
        
        except :
            return None
    
    def GetMeteo(self):
        """ Récupère la météo """
        try :
            # Récupère les coordonnées GPS de l'organisateur
            if self.dictOrganisateur == None : 
                return None
            ville = self.dictOrganisateur["ville"]
            cp = self.dictOrganisateur["cp"]
            if ville == "" or cp == "" :
                return None
            
            # Récupère la météo
            dictMeteo = UTILS_Meteo.Meteo(ville, cp)
            if dictMeteo == None :
                return None
            texte = _(u"<t>METEO</t>Actuellement sur %s, c'est %s (%s°c - %s, %s). Prévision pour demain : %s.") % (
                    ville.capitalize(), 
                    dictMeteo["jour"]["condition"].decode("iso-8859-15").replace(u"&#39;", "'").lower(), 
                    dictMeteo["jour"]["temp"].decode("iso-8859-15"),
                    dictMeteo["jour"]["vent"].decode("iso-8859-15"), 
                    dictMeteo["jour"]["humidite"].decode("iso-8859-15"),
                    dictMeteo["previsions"][1]["condition"].decode("iso-8859-15").replace(u"&#39;", "'").lower(),
                    )
            return texte
        
        except :
            return None


# Pour astral :
# Pour récupérer la liste de tous les timezones :
# import pytz
# from pytz import all_timezones
# print all_timezones







class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(self)
        self.ctrl.Initialisation() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 0)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 200))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()