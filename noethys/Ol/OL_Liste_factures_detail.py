#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from Ctrl import CTRL_Bouton_image
import datetime
import decimal
import GestionDB
from Utils import UTILS_Historique
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Gestion
from Utils import UTILS_Config
from Utils import UTILS_Titulaires
from Utils import UTILS_Dates
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal


class Track(object):
    def __init__(self, parent, donnees=[], liste_prestations=[]):
        self.parent = parent
        self.IDfacture = donnees[0]
        self.IDfamille = donnees[1]
        self.date_edition = UTILS_Dates.DateEngEnDateDD(donnees[2])
        self.date_debut = UTILS_Dates.DateEngEnDateDD(donnees[3])
        self.date_fin = UTILS_Dates.DateEngEnDateDD(donnees[4])
        self.total = donnees[5]
        self.regle = donnees[6]
        self.solde = donnees[7]
        self.numero = donnees[8]
        self.IDprefixe = donnees[9]
        self.prefixe = donnees[10]

        # Récupération du nom des titulaires
        self.nomTitulaires = _(" ")
        try :
            self.nomTitulaires = self.parent.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
        except :
            pass

        # Prestations
        self.liste_prestations = liste_prestations

        self.montant_prestations = 0.0
        dict_prestations = {}
        for dict_prestation in self.liste_prestations:
            self.montant_prestations += dict_prestation["montant"]
            if dict_prestation[self.parent.detail] not in dict_prestations:
                dict_prestations[dict_prestation[self.parent.detail]] = 0.0
            dict_prestations[dict_prestation[self.parent.detail]] += dict_prestation["montant"]

        # Détail
        for key, montant in dict_prestations.items():
            if not key:
                key = 0
            if self.parent.detail == "label":
                label_key = "detail_%d" % self.parent.dict_labels_detail[key]
            if self.parent.detail == "IDactivite":
                label_key = "activite_%d" % key
            if label_key not in self.parent.colonnes_detail:
                self.parent.colonnes_detail.append(label_key)
            setattr(self, label_key, montant)


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.criteres = ""
        self.listeFiltres = []
        self.numColonneTri = 1
        self.ordreAscendant = True
        self.detail = "label"

        # Importation des titulaires
        self.dict_titulaires = UTILS_Titulaires.GetTitulaires()

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        self.colonnes_detail = []
        self.dict_labels_detail = {}
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        # Filtres
        criteres = ""
        if len(self.listeFiltres) > 0 :
            filtreStr = " AND ".join(self.listeFiltres)
            criteres = "WHERE " + " AND ".join(self.listeFiltres)

        DB = GestionDB.DB()

        req = """SELECT IDprestation, prestations.IDfacture, montant, label, activites.IDactivite, activites.nom
        FROM prestations
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        %s;""" % criteres
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        dict_prestations = {}
        index_temp = 0
        for IDprestation, IDfacture, montant, label, IDactivite, nom_activite in listePrestations:
            dict_prestations.setdefault(IDfacture, [])
            dict_prestations[IDfacture].append({"IDprestation": IDprestation, "label": label, "montant": montant, "IDfacture": IDfacture, "IDactivite": IDactivite, "nom_activite": nom_activite})
            if self.detail == "label":
                if label not in self.dict_labels_detail:
                    self.dict_labels_detail[label] = index_temp
                    index_temp += 1
            if self.detail == "IDactivite":
                self.dict_labels_detail[IDactivite] = nom_activite

        req = """SELECT 
        factures.IDfacture, comptes_payeurs.IDfamille, date_edition, date_debut, date_fin, 
        total, regle, solde, numero,
        factures_prefixes.IDprefixe, factures_prefixes.prefixe
        FROM factures
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = factures.IDcompte_payeur
        LEFT JOIN factures_prefixes ON factures_prefixes.IDprefixe = factures.IDprefixe
        %s
        ;""" % criteres
        DB.ExecuterReq(req)
        listeFactures = DB.ResultatReq()
        DB.Close()

        listeListeView = []
        for item in listeFactures:
            IDfacture = item[0]
            track = Track(self, item, liste_prestations=dict_prestations.get(IDfacture, []))
            listeListeView.append(track)
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Image list
        self.imgVert = self.AddNamedImages("ok", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_vert.png"), wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("erreur", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_rouge.png"), wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("addition", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_orange.png"), wx.BITMAP_TYPE_PNG))
        
        self.imgAttente = self.AddNamedImages("attente", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attente.png"), wx.BITMAP_TYPE_PNG))
        self.imgOk = self.AddNamedImages("ok", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        self.imgNon = self.AddNamedImages("erreur", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDfacture", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 90, "date_edition", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Du"), 'left', 80, "date_debut", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Au"), 'left', 80, "date_fin", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Numéro"), 'left', 60, "numero", typeDonnee="texte"),
            ColumnDefn(_(u"Famille"), 'left', 140, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Montant"), 'right', 80, "total", typeDonnee="montant", stringConverter=FormateMontant),
            ]

        for key_label in self.colonnes_detail:
            if self.detail == "label":
                key = int(key_label.split("_")[1])
                label_colonne = u"Autre"
                for label, key_detail in self.dict_labels_detail.items():
                    if key == key_detail:
                        label_colonne = label
            if self.detail == "IDactivite":
                key = int(key_label.split("_")[1])
                label_colonne = self.dict_labels_detail.get(key, "Autre")
            liste_Colonnes.append(ColumnDefn(label_colonne, "right", 100, key_label, typeDonnee="montant", stringConverter=FormateMontant))

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune facture"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SortBy(self.numColonneTri, ascending=self.ordreAscendant)
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        if ID != None :
            self.selectionID = ID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
        if ID == None :
            self.DefileDernier() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDfacture
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        dictParametres = {
            "titre" : _(u"Liste des factures"),
            "orientation" : wx.LANDSCAPE,
            }
        return dictParametres


# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "date_edition" : {"mode" : "nombre", "singulier" : _(u"facture"), "pluriel" : _(u"factures"), "alignement" : wx.ALIGN_CENTER},
            "total" : {"mode" : "total"},
        }
        for index in range(0, 1000):
            dictColonnes["activite_%d" % index] = {"mode": "total"}
            dictColonnes["detail_%d" % index] = {"mode": "total"}

        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


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
        self.Layout()
        self.SetSize((800, 200))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
