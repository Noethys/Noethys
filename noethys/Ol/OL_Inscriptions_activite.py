#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Utils import UTILS_Dates
import datetime

from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils



class Track(object):
    def __init__(self, donnees=[], dictGroupes={}, dictInscriptions={}):
        self.IDactivite = donnees[0]
        self.nom = donnees[1]
        self.abrege = donnees[2]
        self.date_debut = donnees[3]
        self.date_fin = donnees[4]
        self.nbre_inscrits_max = donnees[5]

        # Recherche les inscrits
        if dictInscriptions.has_key(self.IDactivite) :
            self.dict_inscrits_groupes = dictInscriptions[self.IDactivite]
        else :
            self.dict_inscrits_groupes = {}

        # Recherche le nombre d'inscrits total de l'activité
        self.nbre_inscrits = 0
        for IDgroupe, nbre_inscrits in self.dict_inscrits_groupes.iteritems() :
            self.nbre_inscrits += nbre_inscrits

        # Recherche du nombre de places disponibles
        if self.nbre_inscrits_max not in (None, 0) :
            self.nbre_places_disponibles = self.nbre_inscrits_max - self.nbre_inscrits
        else :
            self.nbre_places_disponibles = None

        # Recherche les groupes
        if dictGroupes.has_key(self.IDactivite) :
            self.liste_groupes = dictGroupes[self.IDactivite]
        else :
            self.liste_groupes = []

        # Formatage du texte Places disponibles
        self.label_places = u""
        liste_labels_groupes = []

        # Recherche les places disponibles sur la totalité de l'activité
        if self.nbre_places_disponibles != None :
            liste_labels_groupes.append(u"Total : %d/%d " % (self.nbre_inscrits, self.nbre_inscrits_max))

        # Recherche les places disponibles sur chaque groupe
        for dictGroupe in self.liste_groupes :
            if dictGroupe["nbre_inscrits_max"] not in (None, 0) :

                # Recherche le nombre d'inscrits sur chaque groupe qui a une limite de places
                if self.dict_inscrits_groupes.has_key(dictGroupe["IDgroupe"]) :
                    nbre_inscrits_groupes = self.dict_inscrits_groupes[dictGroupe["IDgroupe"]]
                else :
                    nbre_inscrits_groupes = 0

                label = _(u"%s : %d/%d" % (dictGroupe["nom"], nbre_inscrits_groupes, dictGroupe["nbre_inscrits_max"]))
                liste_labels_groupes.append(label)

        self.label_places = u", ".join(liste_labels_groupes)

        if len(self.label_places) == 0 :
            self.label_places = _(u"Places illimitées")


        # Période
        if self.date_debut == "1977-01-01" and self.date_fin == "2999-01-01" :
            self.periode = "illimitee"
            #self.labelPeriode = _(u"Illimitée")
        else:
            if self.date_debut != None and self.date_fin != None :
                self.periode = u"%s;%s" % (self.date_fin, self.date_debut)
                #self.labelPeriode = _(u"Du %s au %s") % (UTILS_Dates.DateEngFr(self.date_debut), UTILS_Dates.DateEngFr(self.date_fin))
            else:
                self.periode = None
                #self.labelPeriode = _(u"Pas de période")

        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.activites_recentes = True
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        DB = GestionDB.DB()

        if self.activites_recentes == True :
            conditionDate = "WHERE date_fin >= '%s' " % str(datetime.date.today())
        else :
            conditionDate = ""

        # Recherche des activités
        req = """SELECT IDactivite, nom, abrege, date_debut, date_fin, nbre_inscrits_max
        FROM activites
        %s;""" % conditionDate
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()

        # Recherche des groupes
        req = """SELECT IDactivite, IDgroupe, nom, nbre_inscrits_max
        FROM groupes
        ORDER BY IDactivite, ordre;"""
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()
        dictGroupes = {}
        for IDactivite, IDgroupe, nom, nbre_inscrits_max in listeGroupes :
            if dictGroupes.has_key(IDactivite) == False :
                dictGroupes[IDactivite] = []
            dictGroupes[IDactivite].append({"IDgroupe" : IDgroupe, "nom" : nom, "nbre_inscrits_max" : nbre_inscrits_max})

        # Recherche des inscriptions existantes
        req = """SELECT IDactivite, IDgroupe, COUNT(IDinscription)
        FROM inscriptions
        GROUP BY IDactivite, IDgroupe;"""
        DB.ExecuterReq(req)
        listeInscriptions = DB.ResultatReq()
        dictInscriptions = {}
        for IDactivite, IDgroupe, nbre_inscrits in listeInscriptions :
            if dictInscriptions.has_key(IDactivite) == False :
                dictInscriptions[IDactivite] = {}
            dictInscriptions[IDactivite][IDgroupe] = nbre_inscrits

        DB.Close()

        listeListeView = []
        for item in listeActivites :
            track = Track(item, dictGroupes, dictInscriptions)
            listeListeView.append(track)
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormatePeriode(periode):
            if periode == None :
                return _(u"Pas de période")
            if periode == "illimitee" :
                return _(u"Illimitée")
            else:
                date_fin, date_debut = periode.split(";")
            return _(u"Du %s au %s") % (UTILS_Dates.DateEngFr(date_debut), UTILS_Dates.DateEngFr(date_fin))

        liste_Colonnes = [
            ColumnDefn(_(u"IDactivite"), "left", 0, "IDactivite", typeDonnee="entier"),
            ColumnDefn(_(u"Nom de l'activité"), 'left', 220, "nom", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Période de validité"), 'left', 180, "periode", typeDonnee="texte", stringConverter=FormatePeriode),
            ColumnDefn(_(u"Etat des places"), 'left', 250, "label_places", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune activité"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SortBy(2, False)
        self.SetObjects(self.donnees)
       
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        # if self.selectionTrack != None :
        #     self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self._ResizeSpaceFillingColumns()
    
    def Selection(self):
        selections = self.GetSelectedObjects()
        if len(selections) > 0 :
            return selections[0]
        else :
            return None

    def SelectID(self, ID=None):
        index = 0
        for track in self.donnees :
            if track.IDactivite == ID :
                self.SelectObject(track, ensureVisible=True)
                return True
            index += 1
        return False

    def SetID(self, ID=None):
        if ID == None :
            return
        if self.SelectID(ID) == False :
            self.activites_recentes = False
            self.GetParent().ctrl_activites_valides.SetValue(False)
            self.MAJ()
            self.SelectID(ID)

    def GetID(self):
        track = self.Selection()
        if track != None :
            return track.IDactivite
        else :
            return None

    def GetNom(self):
        track = self.Selection()
        if track != None :
            return track.nom
        else :
            return ""

    def GetTrack(self):
        return self.Selection()

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
