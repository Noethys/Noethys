#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
import GestionDB
import six
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils
from Utils import UTILS_Locations
from Utils import UTILS_Dates


def Verif_dispo_produit(track, IDlocation_exception=None, IDlocation_portail_exception=None):
    # Vérifie que la quantité demandée est disponible
    dictPeriodes = UTILS_Locations.GetStockDisponible(IDproduit=track.IDproduit, date_debut=track.date_debut, date_fin=track.date_fin, IDlocation_exception=IDlocation_exception, IDlocation_portail_exception=IDlocation_portail_exception)
    liste_periode_non_dispo = []
    for periode, valeurs in dictPeriodes.items():
        if valeurs["disponible"] < track.quantite:
            debut = datetime.datetime.strftime(periode[0], "%d/%m/%Y-%Hh%M")
            if periode[1].year == 2999:
                fin = _(u"Illimité")
            else:
                fin = datetime.datetime.strftime(periode[1], "%d/%m/%Y-%Hh%M")
            liste_periode_non_dispo.append(_(u"Stock disponible du %s au %s : %d produits") % (debut, fin, valeurs["disponible"]))
    return liste_periode_non_dispo


class Track(object):
    def __init__(self, parent, donnees):
        self.IDreservation = donnees[0]
        self.date_debut = UTILS_Dates.DateEngEnDateDDT(donnees[1])
        self.date_fin = UTILS_Dates.DateEngEnDateDDT(donnees[2])
        self.partage = donnees[3]
        self.IDlocation = donnees[4]
        self.IDproduit = donnees[5]
        self.etat = donnees[6]
        self.resultat = donnees[7]
        self.nom_produit = donnees[8]
        self.description = donnees[9]
        self.quantite = 1
        self.action_possible = False
        self.date_debut_txt = self.date_debut.strftime("%d/%m/%Y-%H:%M")

        # Formate état
        if self.etat == "ajouter":
            self.action = u"Ajouter %s de %s à %s" % (self.nom_produit, self.date_debut.strftime("%d/%m/%Y-%H:%M"), self.date_fin.strftime("%d/%m/%Y-%H:%M"))
            liste_periodes_non_dispo = Verif_dispo_produit(self)
            if len(liste_periodes_non_dispo) > 0:
                self.action_possible = False
                self.statut = _(u"Produit non disponible sur la période demandée")
            else:
                self.action_possible = True
                self.statut = _(u"Ajout possible")

        if self.etat == "modifier":
            if self.IDlocation in parent.dict_locations_existantes:
                # Recherche la location à modifier
                temp = parent.dict_locations_existantes[self.IDlocation]
                self.action = u"Modifier %s de %s à %s > %s de %s à %s" % (
                    temp["nom_produit"], temp["date_debut"].strftime("%d/%m/%Y-%H:%M"), temp["date_fin"].strftime("%d/%m/%Y-%H:%M"),
                    self.nom_produit, self.date_debut.strftime("%d/%m/%Y-%H:%M"), self.date_fin.strftime("%d/%m/%Y-%H:%M")
                    )
                self.action_possible = True
                self.statut = _(u"Modification possible")
                # Vérifie disponibilité produit
                if "-" in self.IDlocation:
                    liste_periodes_non_dispo = Verif_dispo_produit(self, IDlocation_portail_exception=self.IDlocation)
                else:
                    liste_periodes_non_dispo = Verif_dispo_produit(self, IDlocation_exception=int(self.IDlocation))
                if len(liste_periodes_non_dispo) > 0:
                    self.action_possible = False
                    self.statut = _(u"Produit non disponible sur la période demandée")
            else:
                self.action_possible = False
                self.statut = _(u"La location à modifier est inexistante")
                self.action = _(u"Modifier : Location initiale inexistante !")

        if self.etat == "supprimer":
            self.action = u"Supprimer %s de %s à %s" % (self.nom_produit, self.date_debut.strftime("%d/%m/%Y-%H:%M"), self.date_fin.strftime("%d/%m/%Y-%H:%M"))
            # Recherche la location à supprimer
            if self.IDlocation in parent.dict_locations_existantes:
                self.action_possible = True
                self.statut = _(u"Suppression possible")
            else:
                self.action_possible = False
                self.statut = _(u"La location à supprimer est inexistante")

        if self.partage:
            self.action += u" (Partage autorisé)"

        if self.resultat == "ok":
            self.action_possible = False
            if self.etat == "ajouter": self.statut = _(u"Ajout effectué")
            if self.etat == "modifier": self.statut = _(u"Modification effectuée")
            if self.etat == "supprimer": self.statut = _(u"Suppression effectuée")

        if self.resultat == "refus":
            self.action_possible = True
            if self.etat == "ajouter": self.statut = _(u"Ajout refusé")
            if self.etat == "modifier": self.statut = _(u"Modification refusée")
            if self.etat == "supprimer": self.statut = _(u"Suppression refusée")



class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.track_demande = None
        self.donnees = []
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        DB = GestionDB.DB()
        req = """SELECT IDreservation, date_debut, date_fin, partage, IDlocation, portail_reservations_locations.IDproduit, etat, resultat, produits.nom, description
        FROM portail_reservations_locations
        LEFT JOIN produits ON produits.IDproduit = portail_reservations_locations.IDproduit
        WHERE IDaction=%d ORDER BY date_debut;""" % self.track_demande.IDaction
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()

        # Importe locations existantes
        liste_IDlocation = []
        for item in listeDonnees:
            if "-" not in item[4]:
                liste_IDlocation.append(int(item[4]))
            else:
                liste_IDlocation.append(item[4])

        if len(liste_IDlocation) == 0:
            condition = "()"
        elif len(liste_IDlocation) == 1:
            if type(liste_IDlocation[0]) == int :
                condition = "(%d)" % liste_IDlocation[0]
            else:
                condition = "('%s')" % liste_IDlocation[0]
        else:
            condition = str(tuple(liste_IDlocation))

        req = """SELECT IDlocation, date_debut, date_fin, locations.IDproduit, produits.nom, IDlocation_portail
        FROM locations
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        WHERE IDlocation IN %s OR IDlocation_portail IN %s;""" % (condition, condition)
        DB.ExecuterReq(req)
        listeExistantes = DB.ResultatReq()
        DB.Close()

        self.dict_locations_existantes = {}
        for IDlocation, date_debut, date_fin, IDproduit, nom_produit, IDlocation_portail in listeExistantes:
            date_debut = UTILS_Dates.DateEngEnDateDDT(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDDT(date_fin)
            dict_temp = {"IDlocation": IDlocation, "date_debut": date_debut, "date_fin": date_fin, "IDproduit": IDproduit, "nom_produit": nom_produit}
            self.dict_locations_existantes[six.text_type(IDlocation)] = dict_temp
            if IDlocation_portail:
                self.dict_locations_existantes[IDlocation_portail] = dict_temp

        # Mémorisation des tracks
        listeListeView = []
        for item in listeDonnees:
            listeListeView.append(Track(self, item))
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Préparation de la liste Images
        self.AddNamedImages("ajouter", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Plus.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("modifier", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Crayon.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("supprimer", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Moins.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("ok", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok4.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("pasok", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit2.png"), wx.BITMAP_TYPE_PNG))

        # Formatage des données
        def GetImageEtat(track):
            return track.etat

        def GetImageStatut(track):
            if track.resultat == "ok":
                return "ok"
            if track.resultat == "refus":
                return "pasok"
            return None

        def FormateEtat(etat):
            if etat == "ajouter":
                return _(u"Ajout")
            elif etat == "modifier":
                return _(u"Modification")
            else:
                return _(u"Suppression")

        def FormateDateDT(date):
            if date == None :
                return ""
            else:
                return date.strftime("%d/%m/%Y-%H:%M")

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDreservation", typeDonnee="entier"),
            ColumnDefn(_(u"Action"), 'left', 500, "action", typeDonnee="texte", imageGetter=GetImageEtat),
            # ColumnDefn(_(u"Action"), 'left', 100, "etat", typeDonnee="texte", stringConverter=FormateEtat, imageGetter=GetImageEtat),
            # ColumnDefn(_(u"Produit"), 'left', 150, "nom_produit", typeDonnee="texte"),
            # ColumnDefn(_(u"Début"), 'centre', 110, "date_debut", typeDonnee="date", stringConverter=FormateDateDT),
            # ColumnDefn(_(u"Fin"), 'centre', 110, "date_fin", typeDonnee="date", stringConverter=FormateDateDT),
            ColumnDefn(_(u"Statut"), 'left', 280, "statut", typeDonnee="texte", imageGetter=GetImageStatut),
            ]

        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune action"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)

    def MAJ(self, track_demande=None):
        if track_demande:
            self.track_demande = track_demande
        self.InitModel()
        self.InitObjectListView()
        self.CocheTout()

    def Selection(self):
        return self.GetSelectedObjects()

    def CocheTout(self, event=None):
        for track in self.donnees:
            self.Check(track)
            self.RefreshObject(track)

    def CocheRien(self, event=None):
        for track in self.donnees:
            self.Uncheck(track)
            self.RefreshObject(track)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        menuPop = UTILS_Adaptations.Menu()
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des actions"))
        self.PopupMenu(menuPop)
        menuPop.Destroy()




class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
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
