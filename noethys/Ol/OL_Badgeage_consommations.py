#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Utils import UTILS_Dates
import datetime
import time
import GestionDB

from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils



class Track(object):
    def __init__(self, donnees=None):
        self.IDconso = donnees[0]
        self.date = donnees[1]
        self.heure_debut = donnees[2]
        self.heure_fin = donnees[3]
        self.badgeage_debut = UTILS_Dates.DateEngEnDateDDT(donnees[4])
        self.badgeage_fin = UTILS_Dates.DateEngEnDateDDT(donnees[5])
        self.IDindividu = donnees[6]
        self.nom = donnees[7]
        self.prenom = donnees[8]
        self.nom_unite = donnees[9]

        if self.prenom == None : self.prenom = ""
        self.nom_individu = u"%s %s" % (self.nom, self.prenom)

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.date_debut = None
        self.date_fin = None
        self.donnees = []
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        self.InitObjectListView() 
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        if self.date_debut == None or self.date_fin == None :
            listeDonnees = []
        else :
            DB = GestionDB.DB()
            req = """SELECT IDconso, date, consommations.heure_debut, consommations.heure_fin, badgeage_debut, badgeage_fin,
            individus.IDindividu, individus.nom, individus.prenom,
            unites.nom
            FROM consommations 
            LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
            LEFT JOIN unites ON unites.IDunite = consommations.IDunite
            WHERE (badgeage_debut IS NOT NULL OR badgeage_fin IS NOT NULL) AND date>='%s' AND date<='%s';""" % (self.date_debut, self.date_fin)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()

        listeListeView = []
        for item in listeDonnees :
            track = Track(item)
            listeListeView.append(track)
        return listeListeView

    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateDate(dateDD):
            if dateDD == None : return u""
            return UTILS_Dates.DateEngFr(str(dateDD))

        def FormateHeure(heure):
            if not heure:
                return ""
            heure = heure.replace(":", "h")
            return heure

        def FormateHorodatage(horodatage):
            if horodatage != None:
                return horodatage.strftime("%d/%m/%Y  %H:%M:%S")
            else :
                return ""

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDconso", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'center', 80, "date", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Individu"), 'left', 180, "nom_individu", typeDonnee="date"),
            ColumnDefn(_(u"Unité"), 'left', 100, "nom_unite", typeDonnee="date"),
            ColumnDefn(_(u"Début"), 'center', 65, "heure_debut", typeDonnee="texte", stringConverter=FormateHeure),
            ColumnDefn(_(u"Badgeage début"), 'center', 125, "badgeage_debut", typeDonnee="dateheure", stringConverter=FormateHorodatage),
            ColumnDefn(_(u"Fin"), 'center', 65, "heure_fin", typeDonnee="texte", stringConverter=FormateHeure),
            ColumnDefn(_(u"Badgeage fin"), 'center', 125, "badgeage_fin", typeDonnee="dateheure", stringConverter=FormateHorodatage),
        ]

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune consommation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)

    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()

    def SetPeriode(self, date_debut=None, date_fin=None):
        self.date_debut = date_debut
        self.date_fin = date_fin

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        dictParametres = {
            "titre": _(u"Liste des consommations badgées"),
            "total": _(u"> %s consommations") % len(self.GetFilteredObjects()),
            "orientation": wx.PORTRAIT,
        }
        return dictParametres


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)

        # TEST
        self.myOlv.date_debut = datetime.date(2019, 1, 18)
        self.myOlv.date_fin = datetime.date(2019, 1, 25)
        self.myOlv.MAJ()

        # Layout
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
