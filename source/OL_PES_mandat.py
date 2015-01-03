#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import decimal
import GestionDB
import UTILS_Dates
import UTILS_Identification
import UTILS_Mandats
import wx.lib.dialogs as dialogs

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Titulaires
DICT_INDIVIDUS = UTILS_Titulaires.GetIndividus()



class Track(object):
    def __init__(self, donnees, dictTitulaires):
        self.dictTitulaires = dictTitulaires
        self.IDpiece = donnees["IDpiece"]
        self.IDlot = donnees["IDlot"]
        self.IDfamille = donnees["IDfamille"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]

        self.prelevement = donnees["prelevement"]
        self.prelevement_iban =  donnees["prelevement_iban"]
        self.prelevement_bic =  donnees["prelevement_bic"]
        self.prelevement_rum =  donnees["prelevement_rum"]
        self.prelevement_date_mandat =  donnees["prelevement_date_mandat"]
        self.prelevement_IDmandat =  donnees["prelevement_IDmandat"]
        self.prelevement_sequence =  donnees["prelevement_sequence"]
        self.prelevement_titulaire =  donnees["prelevement_titulaire"]
        self.prelevement_statut =  donnees["prelevement_statut"]
        
        self.type = donnees["type"]
        self.IDfacture = donnees["IDfacture"]
        self.libelle = donnees["libelle"]
        self.montant = donnees["montant"]
        
        self.titulaires = ""
        self.InitNomsTitulaires() 
        
        self.IDreglement = donnees["IDreglement"]
        if self.IDreglement == None :
            self.reglement = False
        else :
            self.reglement = True
        self.dateReglement = donnees["dateReglement"]
        self.IDdepot = donnees["IDdepot"]
        
        self.titulaire_helios = donnees["titulaire_helios"]
        self.InitTitulaireHelios()
        
        self.nomLot = donnees["nomLot"]
        self.datePrelevement = donnees["datePrelevement"]
        
    def InitTitulaireHelios(self):
        if DICT_INDIVIDUS.has_key(self.titulaire_helios) :
            self.titulaireCivilite = DICT_INDIVIDUS[self.titulaire_helios]["civiliteAbrege"] 
            self.titulaireNom = DICT_INDIVIDUS[self.titulaire_helios]["nom"]
            self.titulairePrenom = DICT_INDIVIDUS[self.titulaire_helios]["prenom"]
            self.titulaireNomComplet = u"%s %s %s" % (self.titulaireCivilite, self.titulaireNom, self.titulairePrenom)
            self.titulaireRue = DICT_INDIVIDUS[self.titulaire_helios]["rue"]
            self.titulaireCP = DICT_INDIVIDUS[self.titulaire_helios]["cp"]
            self.titulaireVille = DICT_INDIVIDUS[self.titulaire_helios]["ville"]
            self.titulaireAdresse = u"%s %s %s" % (self.titulaireRue, self.titulaireCP, self.titulaireVille)
        else :
            self.titulaireCivilite = ""
            self.titulaireNom = ""
            self.titulairePrenom = ""
            self.titulaireNomComplet = ""
            self.titulaireRue = ""
            self.titulaireCP = ""
            self.titulaireVille = ""
            self.titulaireAdresse = ""
            
    def InitNomsTitulaires(self):
        if self.IDfamille != None :
            self.titulaires = self.dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
    




    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDfamille = kwds.pop("IDfamille", None)
        self.IDmandat = kwds.pop("IDmandat", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.tracks = []
        self.numColonneTri = 1
        self.ordreAscendant = True
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        criteres = ""
        if self.IDfamille != None :
            criteres = "WHERE pes_pieces.IDfamille=%d" % self.IDfamille
        if self.IDmandat != None :
            criteres = "WHERE pes_pieces.prelevement_IDmandat=%d" % self.IDmandat
        DB = GestionDB.DB()
        req = """SELECT 
        pes_pieces.IDpiece, pes_pieces.IDlot, pes_pieces.IDfamille, 
        prelevement, prelevement_iban, prelevement_bic, 
        prelevement_IDmandat, prelevement_rum, prelevement_date_mandat,
        prelevement_sequence, prelevement_titulaire, prelevement_statut,
        type, IDfacture, libelle, pes_pieces.montant, 
        reglements.IDreglement, reglements.date, reglements.IDdepot,
        comptes_payeurs.IDcompte_payeur,
        pes_pieces.titulaire_helios,
        pes_lots.nom, pes_lots.date_prelevement
        FROM pes_pieces
        LEFT JOIN reglements ON reglements.IDpiece = pes_pieces.IDpiece
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = pes_pieces.IDfamille
        LEFT JOIN pes_lots ON pes_lots.IDlot = pes_pieces.IDlot
        %s
        ;""" % criteres
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeListeView = []
        for IDpiece, IDlot, IDfamille, prelevement, prelevement_iban, prelevement_bic, prelevement_IDmandat, prelevement_rum, prelevement_date_mandat, prelevement_sequence, prelevement_titulaire, prelevement_statut, type_piece, IDfacture, libelle, montant, IDreglement, dateReglement, IDdepot, IDcompte_payeur, titulaire_helios, nomLot, datePrelevement in listeDonnees :
            dictTemp = {
                "IDpiece" : IDpiece, "IDlot" : IDlot, "IDfamille" : IDfamille, 
                "prelevement" : prelevement, "prelevement_iban" : prelevement_iban, "prelevement_bic" : prelevement_bic, 
                "prelevement_IDmandat" : prelevement_IDmandat, "prelevement_rum" : prelevement_rum, "prelevement_date_mandat" : prelevement_date_mandat,
                "prelevement_sequence" : prelevement_sequence, "prelevement_titulaire" : prelevement_titulaire, "prelevement_statut" : prelevement_statut, 
                "IDfacture" : IDfacture, "libelle" : libelle, "montant" : montant, "statut" : prelevement_statut, "IDlot" : IDlot, "etat" : None, "type" : type_piece,
                "IDreglement" : IDreglement, "dateReglement" : dateReglement, "IDdepot" : IDdepot, "IDcompte_payeur" : IDcompte_payeur,
                "titulaire_helios" : titulaire_helios, "nomLot" : nomLot, "datePrelevement" : datePrelevement,
                }
            track = Track(dictTemp, dictTitulaires)
            listeListeView.append(track)
        return listeListeView
        
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        # Image list
        self.imgValide = self.AddNamedImages("valide", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        self.imgRefus = self.AddNamedImages("refus", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.imgAttente = self.AddNamedImages("attente", wx.Bitmap("Images/16x16/Attente.png", wx.BITMAP_TYPE_PNG))
        self.imgPrelevement = self.AddNamedImages("prelevement", wx.Bitmap("Images/16x16/Prelevement.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageStatut(track):
            if track.prelevement_statut == "valide" : return self.imgValide
            if track.prelevement_statut == "refus" : return self.imgRefus
            if track.prelevement_statut == "attente" : return self.imgAttente

        def GetImageReglement(track):
            if track.reglement == False :
                return self.imgRefus
            else :
                return self.imgValide

        def FormateDateCourt(dateDD):
            if dateDD == None or dateDD == "" :
                return ""
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateType(statut):
            if statut == "manuel" : return u"Manuel"
            if statut == "facture" : return u"Facture"
            return ""

        def FormateStatut(statut):
            if statut == "valide" : return u"Valide"
            if statut == "refus" : return u"Refus"
            if statut == "attente" : return u"Attente"

        def FormateReglement(reglement):
            if reglement == True :
                return u"Oui"
            else:
                return u""

        def FormatePrelevement(prelevement):
            if prelevement == 1 :
                return u"Oui"
            else:
                return u""

        def GetImagePrelevement(track):
            if track.prelevement == 1 : 
                return self.imgPrelevement
            else :
                return self.imgRefus
            
        liste_Colonnes = [
            ColumnDefn(u"ID", "left", 0, "IDprelevement", typeDonnee="entier"),
            ColumnDefn(u"Date Prélèv.", 'left', 80, "datePrelevement", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(u"Nom bordereau", 'left', 150, "nomLot", typeDonnee="texte"),
##            ColumnDefn(u"Famille", 'left', 230, "titulaires"),
##            ColumnDefn(u"Type", 'left', 70, "type", stringConverter=FormateType),
            ColumnDefn(u"Libellé", 'left', 110, "libelle", typeDonnee="texte"),
            ColumnDefn(u"Montant", 'right', 70, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(u"Statut", 'left', 80, "prelevement_statut", typeDonnee="texte", stringConverter=FormateStatut, imageGetter=GetImageStatut),
            ColumnDefn(u"Règlement", 'left', 70, "reglement", typeDonnee="montant", stringConverter=FormateReglement, imageGetter=GetImageReglement),
            ColumnDefn(u"Séquence", 'left', 70, "prelevement_sequence", typeDonnee="texte"),
            ColumnDefn(u"IBAN", 'left', 190, "prelevement_iban", typeDonnee="texte"),
            ColumnDefn(u"BIC", 'left', 100, "prelevement_bic", typeDonnee="texte"),
            ColumnDefn(u"Titulaire compte bancaire", 'left', 160, "prelevement_titulaire", typeDonnee="texte"),
            ColumnDefn(u"Ref. mandat", 'left', 90, "prelevement_rum", typeDonnee="texte"),
            ColumnDefn(u"Date mandat", 'left', 80, "prelevement_date_mandat", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(u"Titulaire Hélios", 'left', 150, "titulaireNomComplet", typeDonnee="texte"),
            ColumnDefn(u"Adresse", 'left', 220, "titulaireAdresse", typeDonnee="texte"),
            ]
            
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucun prélèvement")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
##        self.SetSortColumn(self.columns[self.numColonneTri])
        self.SortBy(self.numColonneTri, ascending=self.ordreAscendant)
        self.SetObjects(self.donnees)
       
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = wx.Menu()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, u"Aperçu avant impression")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, u"Imprimer")
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, u"Exporter au format Texte")
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, u"Exporter au format Excel")
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self):
        # Récupère l'intitulé du compte
        txtIntro = u"Liste des prélèvements"
        # Récupère le total
        total = 0.0
        for track in self.donnees :
            total += track.montant
        txtTotal = self.GetTexteTotaux().replace("<B>", "").replace("</B>", "")
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des prélèvements", intro=txtIntro, total=txtTotal, format="A", orientation=wx.LANDSCAPE)
        return prt
        
    def Apercu(self, event=None):
        self.Impression().Preview()

    def Imprimer(self, event=None):
        self.Impression().Print()

    def ExportTexte(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=u"Liste des prélèvements PES ORMC")
        
    def ExportExcel(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=u"Liste des prélèvements PES ORMC")
        




# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher...")
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_reglements
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh() 


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
        
        self.bouton_test = wx.Button(panel, -1, u"Bouton test")
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 400))
        self.CenterOnScreen()
        
    def OnBoutonTest(self, event):
        print "Test de la sauvegarde des reglements :"
        self.myOlv.SauvegardeReglements(date=datetime.date.today(), IDcompte=99)
        
        
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
