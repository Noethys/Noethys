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
    def __init__(self, parent, donnees=[], liste_ventilation=[]):
        self.parent = parent
        self.IDreglement = donnees[0]
        self.date_saisie = donnees[1]
        if self.date_saisie != None :
            self.date_saisie = UTILS_Dates.DateEngEnDateDD(self.date_saisie)
        self.IDcompte_payeur = donnees[2]
        self.date = UTILS_Dates.DateEngEnDateDD(donnees[3])
        self.encaissement_attente = donnees[4]
        self.IDmode = donnees[5]
        self.nom_mode = donnees[6]
        self.nom_emetteur = donnees[7]
        self.numero_piece = donnees[8]
        self.montant = donnees[9]
        self.nom_payeur = donnees[10]
        self.IDdepot = donnees[11]
        self.date_depot = donnees[12]
        if self.date_depot != None :
            self.date_depot = UTILS_Dates.DateEngEnDateDD(self.date_depot)
        self.nom_depot = donnees[13]
        self.IDfamille = donnees[14]
        self.inclus = True

        # Récupération du nom des titulaires
        self.nomTitulaires = _(" ")
        try :
            self.nomTitulaires = self.parent.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
        except :
            pass

        # Ventilation
        self.liste_ventilation = liste_ventilation

        # Analyse ventilation
        self.montant_ventilation = 0.0
        dict_factures = {}
        dict_prestations = {}
        for dict_ventilation in self.liste_ventilation:
            self.montant_ventilation += dict_ventilation["montant"]

            # Mémorisation des factures associées
            if dict_ventilation["IDfacture"] != None:

                IDprefixe = dict_ventilation["IDprefixe"]
                prefixe = dict_ventilation["prefixe"]
                num_facture = dict_ventilation["num_facture"]
                if IDprefixe != None:
                    numeroStr = u"%s-%06d" % (prefixe, num_facture)
                else:
                    numeroStr = num_facture

                key = (dict_ventilation["IDfacture"], numeroStr)
                if key not in dict_factures:
                    dict_factures[key] = 0.0
                dict_factures[key] += dict_ventilation["montant"]

            # Mémorisation des prestations associées
            if dict_ventilation["label"] not in dict_prestations:
                dict_prestations[dict_ventilation["label"]] = 0.0
            dict_prestations[dict_ventilation["label"]] += dict_ventilation["montant"]

        # Analyse des factures associées
        self.texte_factures = ""
        if len(dict_factures) > 0:
            liste_temp = []
            for (IDfacture, num_facture), montant in dict_factures.items():
                liste_temp.append(u" n°%s (%.2f %s)" % (num_facture, montant, SYMBOLE))
            self.texte_factures = u", ".join(liste_temp)

        # Analyse des factures associées
        self.texte_prestations = ""
        if len(dict_prestations) > 0:
            liste_temp = []
            for label, montant in dict_prestations.items():
                liste_temp.append(u"%s (%.2f %s)" % (label, montant, SYMBOLE))
            self.texte_prestations = u", ".join(liste_temp)




class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.criteres = ""
        self.listeFiltres = []
        self.numColonneTri = 1
        self.ordreAscendant = True

        # Importation des titulaires
        self.dict_titulaires = UTILS_Titulaires.GetTitulaires()

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        # Filtres
        criteres = ""
        if len(self.listeFiltres) > 0 :
            filtreStr = " AND ".join(self.listeFiltres)
            criteres = "WHERE " + " AND ".join(self.listeFiltres)

        DB = GestionDB.DB()

        req = """SELECT IDventilation, ventilation.IDreglement, ventilation.IDprestation, ventilation.montant,
        prestations.IDfacture, prestations.label, factures.numero,
        factures.IDprefixe, factures_prefixes.prefixe
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation 
        LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        LEFT JOIN factures_prefixes ON factures_prefixes.IDprefixe = factures.IDprefixe

        %s;""" % criteres
        DB.ExecuterReq(req)
        listeVentilation = DB.ResultatReq()
        dict_ventilation = {}
        for IDventilation, IDreglement, IDprestation, montant, IDfacture, label, num_facture, IDprefixe, prefixe in listeVentilation:
            if IDreglement not in dict_ventilation:
                dict_ventilation[IDreglement] = []
            dict_ventilation[IDreglement].append({"IDprestation": IDprestation, "label": label, "montant": montant, "IDfacture": IDfacture, "num_facture": num_facture,
                                                  "IDprefixe": IDprefixe, "prefixe": prefixe})

        req = """SELECT 
        reglements.IDreglement, date_saisie, reglements.IDcompte_payeur, reglements.date, reglements.encaissement_attente,
        reglements.IDmode, modes_reglements.label, emetteurs.nom, reglements.numero_piece, reglements.montant, 
        payeurs.nom, reglements.IDdepot, depots.date, depots.nom, comptes_payeurs.IDfamille
        FROM reglements
        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
        LEFT JOIN emetteurs ON reglements.IDemetteur=emetteurs.IDemetteur
        LEFT JOIN payeurs ON reglements.IDpayeur=payeurs.IDpayeur
        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
        %s
        GROUP BY reglements.IDreglement
        ;""" % criteres
        DB.ExecuterReq(req)
        listeReglements = DB.ResultatReq()
        DB.Close()
        
        listeListeView = []
        for item in listeReglements :
            # Recherche de la ventilation
            IDreglement = item[0]
            if IDreglement in dict_ventilation:
                liste_ventilation = dict_ventilation[IDreglement]
            else:
                liste_ventilation = []

            # Mémorisation du track règlement
            track = Track(self, item, liste_ventilation)
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
        
        def GetImageVentilation(track):
            if track.montant < FloatToDecimal(0.0) :
                return None
            if track.montant_ventilation == None :
                return self.imgRouge
            resteAVentiler = FloatToDecimal(track.montant) - FloatToDecimal(track.montant_ventilation)
            if resteAVentiler == FloatToDecimal(0.0) :
                return self.imgVert
            if resteAVentiler > FloatToDecimal(0.0) :
                return self.imgOrange
            if resteAVentiler < FloatToDecimal(0.0) :
                return self.imgRouge
        
        def GetImageDepot(track):
            if track.IDdepot == None :
                if track.encaissement_attente == 1 :
                    return self.imgAttente
                else:
                    return self.imgNon
            else:
                return self.imgOk

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDreglement", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 75, "date", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Mode"), 'left', 90, "nom_mode", typeDonnee="texte"),
            ColumnDefn(_(u"Emetteur"), 'left', 110, "nom_emetteur", typeDonnee="texte"),
            ColumnDefn(_(u"Numéro"), 'left', 60, "numero_piece", typeDonnee="texte"),
            ColumnDefn(_(u"Famille"), 'left', 130, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Payeur"), 'left', 130, "nom_payeur", typeDonnee="texte"),
            ColumnDefn(_(u"Montant"), 'right', 60, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Ventilé"), 'right', 80, "montant_ventilation", typeDonnee="montant", stringConverter=FormateMontant, imageGetter=GetImageVentilation),
            ColumnDefn(_(u"Date dépôt"), 'left', 75, "date_depot", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Nom dépôt"), 'left', 110, "nom_depot", typeDonnee="texte"),
            ColumnDefn(_(u"Factures associées"), 'left', 130, "texte_factures", typeDonnee="texte"),
            ColumnDefn(_(u"Prestations associées"), 'left', 250, "texte_prestations", typeDonnee="texte"),
            ]

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun règlement"))
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
            ID = self.Selection()[0].IDreglement
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        intro = u""
        total = 0.0
        for track in self.donnees :
            total += track.montant
        total = self.GetDetailReglements()

        dictParametres = {
            "titre" : _(u"Liste des règlements"),
            "intro" : intro,
            "total" : total,
            "orientation" : wx.LANDSCAPE,
            }
        return dictParametres

    def GetDetailReglements(self):
        # Récupération des chiffres
        nbreTotal = 0
        montantTotal = 0.0
        dictDetails = {}
        for track in self.donnees :
            if track.inclus == True :
                # Montant total
                nbreTotal += 1
                # Nbre total
                montantTotal += track.montant
                # Détail
                if (track.IDmode in dictDetails) == False :
                    dictDetails[track.IDmode] = { "label" : track.nom_mode, "nbre" : 0, "montant" : 0.0}
                dictDetails[track.IDmode]["nbre"] += 1
                dictDetails[track.IDmode]["montant"] += track.montant
        # Création du texte
        texte = _(u"%d règlements (%.2f €) : ") % (nbreTotal, montantTotal)
        for IDmode, dictDetail in dictDetails.items() :
            texteDetail = u"%d %s (%.2f €), " % (dictDetail["nbre"], dictDetail["label"], dictDetail["montant"])
            texte += texteDetail
        if len(dictDetails) > 0 :
            texte = texte[:-2] + u"."
        else:
            texte = texte[:-7] 
        return texte



# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nom_mode" : {"mode" : "nombre", "singulier" : _(u"règlement"), "pluriel" : _(u"règlements"), "alignement" : wx.ALIGN_CENTER},
            "montant" : {"mode" : "total"},
            "montant_ventilation" : {"mode" : "total"},
            }
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
