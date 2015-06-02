#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import decimal
import GestionDB
import UTILS_Dates
import DLG_Saisie_pes_piece
import UTILS_Identification
import UTILS_Prelevements
import UTILS_Mandats
import wx.lib.dialogs as dialogs

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Titulaires



class Track(object):
    def __init__(self, donnees, dictTitulaires={}, dictIndividus={}):
        self.dictTitulaires = dictTitulaires
        self.dictIndividus = dictIndividus
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
        if self.prelevement_IDmandat == "" :
            self.prelevement_IDmandat = None
        self.prelevement_sequence =  donnees["prelevement_sequence"]
        self.prelevement_titulaire =  donnees["prelevement_titulaire"]
        self.prelevement_statut =  donnees["prelevement_statut"]
        
        self.type = donnees["type"]
        self.IDfacture = donnees["IDfacture"]
        self.numero = donnees["numero"]
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
        
        # Autres données Hélios
        if donnees["dictAutresDonnees"].has_key("idtiers_helios") :
            self.idtiers_helios = donnees["dictAutresDonnees"]["idtiers_helios"]
            if self.idtiers_helios == None :
                self.idtiers_helios = ""
        else :
            self.idtiers_helios = ""
        if donnees["dictAutresDonnees"].has_key("natidtiers_helios") :
            self.natidtiers_helios = donnees["dictAutresDonnees"]["natidtiers_helios"]
            if self.natidtiers_helios in (9999, None) :
                self.natidtiers_helios = ""
        else :
            self.natidtiers_helios = ""
        if donnees["dictAutresDonnees"].has_key("reftiers_helios") :
            self.reftiers_helios = donnees["dictAutresDonnees"]["reftiers_helios"]
            if self.reftiers_helios == None :
                self.reftiers_helios = ""
        else :
            self.reftiers_helios = ""
        if donnees["dictAutresDonnees"].has_key("cattiers_helios") :
            self.cattiers_helios = donnees["dictAutresDonnees"]["cattiers_helios"]
            if self.cattiers_helios == None :
                self.cattiers_helios = "01"
            else :
                self.cattiers_helios = "%02d" % self.cattiers_helios
        else :
            self.cattiers_helios = "01"
        if donnees["dictAutresDonnees"].has_key("natjur_helios") :
            self.natjur_helios = donnees["dictAutresDonnees"]["natjur_helios"]
            if self.natjur_helios == None :
                self.natjur_helios = "01"
            else :
                self.natjur_helios = "%02d" % self.natjur_helios
        else :
            self.natjur_helios = "01"
        
        # Etat de la pièce
        self.etat = donnees["etat"] # "ajout", "modif"
        self.AnalysePiece() 
        
    def InitTitulaireHelios(self):
        if self.dictIndividus.has_key(self.titulaire_helios) :
            self.titulaireCivilite = self.dictIndividus[self.titulaire_helios]["civiliteAbrege"] 
            self.titulaireNom = self.dictIndividus[self.titulaire_helios]["nom"]
            self.titulairePrenom = self.dictIndividus[self.titulaire_helios]["prenom"]
            if self.titulaireCivilite == None :
                self.titulaireNomComplet = u"%s %s" % (self.titulaireNom, self.titulairePrenom)
            else :
                self.titulaireNomComplet = u"%s %s %s" % (self.titulaireCivilite, self.titulaireNom, self.titulairePrenom)
            self.titulaireNomPrenom = u"%s %s" % (self.titulaireNom, self.titulairePrenom)
            self.titulaireRue = self.dictIndividus[self.titulaire_helios]["rue"]
            self.titulaireCP = self.dictIndividus[self.titulaire_helios]["cp"]
            self.titulaireVille = self.dictIndividus[self.titulaire_helios]["ville"]
            self.titulaireAdresse = u"%s %s %s" % (self.titulaireRue, self.titulaireCP, self.titulaireVille)
        else :
            self.titulaireCivilite = ""
            self.titulaireNom = ""
            self.titulairePrenom = ""
            self.titulaireNomComplet = ""
            self.titulaireNomPrenom = ""
            self.titulaireRue = ""
            self.titulaireCP = ""
            self.titulaireVille = ""
            self.titulaireAdresse = ""
        
    def InitNomsTitulaires(self):
        if self.IDfamille != None :
            self.titulaires = self.dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
    
    def AnalysePiece(self):
        listeProblemes = []
        
        if self.titulaire_helios in (None, "") : 
            listeProblemes.append(_(u"Titulaire Hélios manquant"))
        else :
            if self.titulaireRue in (None, "") or self.titulaireCP in (None, "") or self.titulaireVille in (None, "") : 
                listeProblemes.append(_(u"Adresse du titulaire Hélios incomplète"))
        
        if self.prelevement == 1 :
            if self.prelevement_iban in (None, "") or self.prelevement_bic in (None, "") or self.prelevement_titulaire in (None, "") :
                listeProblemes.append(_(u"Coordonnées bancaires incomplètes"))
            if self.prelevement_rum in (None, "") or self.prelevement_IDmandat in (None, "") or self.prelevement_date_mandat in (None, "") :
                listeProblemes.append(_(u"Mandat SEPA manquant"))
            if self.prelevement_sequence in (None, "") :
                listeProblemes.append(_(u"Séquence SEPA non renseignée"))
        
        if len(listeProblemes) > 0 :
            self.analysePiece = False
            self.analysePieceTexte = u", ".join(listeProblemes)
        else :
            self.analysePiece = True
            self.analysePieceTexte = _(u"Pièce valide")

def GetDictAutresDonnees():
    DB = GestionDB.DB()
    req = """SELECT IDfamille, idtiers_helios, natidtiers_helios, reftiers_helios, cattiers_helios, natjur_helios
    FROM familles;"""
    DB.ExecuterReq(req)
    listeAutresDonnees = DB.ResultatReq()
    dictAutresDonnees = {}
    for IDfamille, idtiers_helios, natidtiers_helios, reftiers_helios, cattiers_helios, natjur_helios in listeAutresDonnees :
        dictAutresDonnees[IDfamille] = {"idtiers_helios":idtiers_helios, "natidtiers_helios":natidtiers_helios, "reftiers_helios":reftiers_helios, "cattiers_helios":cattiers_helios, "natjur_helios":natjur_helios}
    DB.Close() 
    return dictAutresDonnees

def GetTracks(IDlot=None, IDmandat=None):
    """ Récupération des données """
    dictTitulaires = UTILS_Titulaires.GetTitulaires() 
    dictIndividus = UTILS_Titulaires.GetIndividus() 
    if IDlot != None :
        criteres = "WHERE IDlot=%d" % IDlot
    if IDmandat != None :
        criteres = "WHERE prelevement_IDmandat=%d" % IDmandat
    if IDlot == None and IDmandat == None :
        return []
    
    dictAutresDonnees = GetDictAutresDonnees()
    
    DB = GestionDB.DB()
    req = """SELECT 
    pes_pieces.IDpiece, IDlot, pes_pieces.IDfamille, 
    prelevement, prelevement_iban, prelevement_bic, 
    prelevement_IDmandat, prelevement_rum, prelevement_date_mandat,
    prelevement_sequence, prelevement_titulaire, prelevement_statut,
    type, IDfacture, libelle, pes_pieces.montant, 
    reglements.IDreglement, reglements.date, reglements.IDdepot,
    comptes_payeurs.IDcompte_payeur,
    pes_pieces.titulaire_helios, pes_pieces.numero
    FROM pes_pieces
    LEFT JOIN reglements ON reglements.IDpiece = pes_pieces.IDpiece
    LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = pes_pieces.IDfamille
    %s
    ;""" % criteres
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    listeListeView = []
    for IDpiece, IDlot, IDfamille, prelevement, prelevement_iban, prelevement_bic, prelevement_IDmandat, prelevement_rum, prelevement_date_mandat, prelevement_sequence, prelevement_titulaire, prelevement_statut, type_piece, IDfacture, libelle, montant, IDreglement, dateReglement, IDdepot, IDcompte_payeur, titulaire_helios, numero in listeDonnees :
        if dictAutresDonnees.has_key(IDfamille) :
            dictTempAutresDonnees = dictAutresDonnees[IDfamille]
        else :
            dictTempAutresDonnees = {}
        dictTemp = {
            "IDpiece" : IDpiece, "IDlot" : IDlot, "IDfamille" : IDfamille, 
            "prelevement" : prelevement, "prelevement_iban" : prelevement_iban, "prelevement_bic" : prelevement_bic, 
            "prelevement_IDmandat" : prelevement_IDmandat, "prelevement_rum" : prelevement_rum, "prelevement_date_mandat" : prelevement_date_mandat,
            "prelevement_sequence" : prelevement_sequence, "prelevement_titulaire" : prelevement_titulaire, "prelevement_statut" : prelevement_statut, 
            "IDfacture" : IDfacture, "libelle" : libelle, "montant" : montant, "statut" : prelevement_statut, "IDlot" : IDlot, "etat" : None, "type" : type_piece,
            "IDreglement" : IDreglement, "dateReglement" : dateReglement, "IDdepot" : IDdepot, "IDcompte_payeur" : IDcompte_payeur,
            "titulaire_helios" : titulaire_helios, "numero" : numero, "dictAutresDonnees" : dictTempAutresDonnees,
            }
        track = Track(dictTemp, dictTitulaires, dictIndividus)
        listeListeView.append(track)
    return listeListeView



    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDlot = kwds.pop("IDlot", None)
        self.IDmandat = kwds.pop("IDmandat", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.tracks = []
        self.numColonneTri = 3
        self.ordreAscendant = True
        self.listeSuppressions = []
        self.reglement_auto = False
        self.dictIndividus = UTILS_Titulaires.GetIndividus()
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier()

    def InitModel(self, tracks=None, IDcompte=None, IDmode=None):
        if tracks != None :
            self.tracks = tracks
        self.donnees = self.tracks
                    
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
            if statut == "manuel" : return _(u"Manuel")
            if statut == "facture" : return _(u"Facture")
            return ""

        def FormateStatut(statut):
            if statut == "valide" : return _(u"Valide")
            if statut == "refus" : return _(u"Refus")
            if statut == "attente" : return _(u"Attente")

        def FormateReglement(reglement):
            if reglement == True :
                return _(u"Oui")
            else:
                return u""

        def FormatePrelevement(prelevement):
            if prelevement == 1 :
                return _(u"Oui")
            else:
                return u""

        def GetImagePrelevement(track):
            if track.prelevement == 1 : 
                return self.imgPrelevement
            else :
                return self.imgRefus
        
        def GetImageAnalysePiece(track):
            if track.analysePiece == True : 
                return self.imgValide
            else :
                return self.imgRefus
            
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDprelevement", typeDonnee="entier"),
            ColumnDefn(_(u"Analyse pièce"), 'left', 120, "analysePieceTexte", typeDonnee="texte", imageGetter=GetImageAnalysePiece),
            ColumnDefn(_(u"Famille"), 'left', 230, "titulaires", typeDonnee="texte"),
##            ColumnDefn(_(u"Type"), 'left', 70, "type", stringConverter=FormateType),
            ColumnDefn(_(u"Libellé"), 'left', 110, "libelle", typeDonnee="texte"),
            ColumnDefn(_(u"Montant"), 'right', 70, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Statut"), 'left', 80, "prelevement_statut", typeDonnee="texte", stringConverter=FormateStatut, imageGetter=GetImageStatut),
            ColumnDefn(_(u"Règlement"), 'left', 70, "reglement", typeDonnee="texte", stringConverter=FormateReglement, imageGetter=GetImageReglement),
            ColumnDefn(_(u"Prélèvt"), 'left', 55, "prelevement", typeDonnee="texte", stringConverter=FormatePrelevement, imageGetter=GetImagePrelevement),
            ColumnDefn(_(u"Séquence"), 'left', 70, "prelevement_sequence", typeDonnee="texte"),
            ColumnDefn(_(u"IBAN"), 'left', 190, "prelevement_iban", typeDonnee="texte"),
            ColumnDefn(_(u"BIC"), 'left', 100, "prelevement_bic", typeDonnee="texte"),
            ColumnDefn(_(u"Titulaire compte bancaire"), 'left', 160, "prelevement_titulaire", typeDonnee="texte"),
            ColumnDefn(_(u"Ref. mandat"), 'left', 90, "prelevement_rum", typeDonnee="texte"),
            ColumnDefn(_(u"Date mandat"), 'left', 80, "prelevement_date_mandat", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Titulaire Hélios"), 'left', 150, "titulaireNomComplet", typeDonnee="texte"),
            ColumnDefn(_(u"Adresse"), 'left', 220, "titulaireAdresse", typeDonnee="texte"),
            ColumnDefn(_(u"ID Tiers"), 'left', 70, "idtiers_helios", typeDonnee="texte"),
            ColumnDefn(_(u"Type IDTiers"), 'left', 70, "natidtiers_helios", typeDonnee="texte"),
            ColumnDefn(_(u"Ref. Tiers"), 'left', 70, "reftiers_helios", typeDonnee="texte"),
            ColumnDefn(_(u"Cat. Tiers"), 'left', 70, "cattiers_helios", typeDonnee="texte"),
            ColumnDefn(_(u"Nat. Jur."), 'left', 70, "natjur_helios", typeDonnee="texte"),
            ]
        

        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune pièce"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
##        self.SetSortColumn(self.columns[self.numColonneTri])
        self.SortBy(self.numColonneTri, ascending=self.ordreAscendant)
        self.SetObjects(self.donnees)
       
    def MAJ(self, tracks=None, ID=None, selectionTrack=None, nextTrack=None, IDcompte=None, IDmode=None):
        self.InitModel(tracks, IDcompte, IDmode)
        self.InitObjectListView()
        # Sélection d'un item
        if selectionTrack != None :
            self.SelectObject(selectionTrack, deselectOthers=True, ensureVisible=True)
            if self.GetSelectedObject() == None :
                self.SelectObject(nextTrack, deselectOthers=True, ensureVisible=True)

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDpiece
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Saisie manuelle
##        item = wx.MenuItem(menuPop, 10, _(u"Ajouter un prélèvement manuel"))
##        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Saisie_manuelle, id=10)

        # Item Saisie de factures
        item = wx.MenuItem(menuPop, 11, _(u"Ajouter une ou plusieurs factures"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Saisie_factures, id=11)

        menuPop.AppendSeparator()

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
                
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Retirer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
                
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self):
        # Récupère l'intitulé du compte
        txtIntro = self.GetParent().GetLabelParametres()
        # Récupère le total
        total = 0.0
        for track in self.donnees :
            total += track.montant
        txtTotal = self.GetTexteTotaux().replace("<B>", "").replace("</B>", "")
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des pièces du bordereau"), intro=txtIntro, total=txtTotal, format="A", orientation=wx.LANDSCAPE)
        return prt
        
    def Apercu(self, event=None):
        self.Impression().Preview()

    def Imprimer(self, event=None):
        self.Impression().Print()

    def ExportTexte(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des pièces du bordereau"))
        
    def ExportExcel(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des pièces du bordereau"))
        
    def Saisie_manuelle(self, event=None):
        """ Saisie manuelle """
        dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        dictTemp = {
            "IDprelevement" : None, "IDfamille" : None, "prelevement" : 0, "prelevement_iban" : "", "prelevement_bic" : "", 
            "prelevement_rum" : "", "prelevement_date_mandat" : None,
            "prelevement_titulaire" : "", "prelevement_statut" : "attente", "type" : "manuel", "IDfacture" : None, 
            "libelle" : "", "montant" : 0.00, "IDlot" : self.IDlot, "etat" : "ajout",
            "IDreglement" : None, "dateReglement" : None, "IDdepot" : None, "IDcompte_payeur" : None,
            }
        track = Track(dictTemp, dictTitulaires, self.dictIndividus)
        dlg = DLG_Saisie_prelevement.Dialog(self, track=track)      
        if dlg.ShowModal() == wx.ID_OK:
            track = dlg.GetTrack()
            self.AddObject(track)
            self.MAJtotaux() 
        dlg.Destroy() 
        
    def Saisie_factures(self, event=None):
        """ Saisie de factures """
        if self.GetParent().GetVerrouillage() == True :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette action car le lot est verrouillé !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        import DLG_Pes_factures
        dlg = DLG_Pes_factures.Dialog(self, IDlot=self.IDlot)
        reponse = dlg.ShowModal()
        tracks = dlg.GetTracks()
        dlg.Destroy()
        if reponse != wx.ID_OK :
            return
        self.AjoutFactures(tracks)
    
    def AjoutFactures(self, tracks=[]):
        # Vérifie que cette facture n'est pas déjà présente dans le lot
        listeFacturesPresentes = []
        for track in self.GetObjects() :
            if track.IDfacture != None :
                listeFacturesPresentes.append(track.IDfacture)
        
        mandats = UTILS_Mandats.Mandats() 
        dictAutresDonnees = GetDictAutresDonnees()
        
        # MAJ de la liste affichée
        dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        listeNewTracks = []
        listeMandatsNonValides = []
        for track in tracks :
            
            # Recherche un mandat valide pour la famille
            if track.prelevement in (True, 1) :
                IDmandat = mandats.RechercheMandatFamille(track.IDfamille) 
            else :
                IDmandat = None
            
            if IDmandat == None :
                if dictTitulaires.has_key(track.IDfamille) :
                    nomTitulaires = dictTitulaires[track.IDfamille]["titulairesSansCivilite"]
                else :
                    nomTitulaires = _(u"Titulaires inconnus")
                listeMandatsNonValides.append(_(u"Facture n°%s de la famille %s") % (track.numero, nomTitulaires))

                prelevement = 0
                prelevement_iban = ""
                prelevement_bic = ""
                prelevement_IDmandat = ""
                prelevement_rum = ""
                prelevement_mandat_date = ""
                prelevement_titulaire = ""
                prelevement_sequence = ""

            else :
                # Récupère les données du mandat
                dictMandat = mandats.GetDictMandat(IDmandat) 
                prelevement = 1
                prelevement_iban = dictMandat["iban"]
                prelevement_bic = dictMandat["bic"]
                prelevement_IDmandat = dictMandat["IDmandat"]
                prelevement_rum = dictMandat["rum"]
                prelevement_mandat_date = dictMandat["date"]
                prelevement_titulaire = dictMandat["titulaire"]
                
                # Recherche de la séquence
                analyse = mandats.AnalyseMandat(prelevement_IDmandat)
                prelevement_sequence = analyse["prochaineSequence"]
                
            if dictAutresDonnees.has_key(track.IDfamille) :
                dictTempAutresDonnees = dictAutresDonnees[track.IDfamille]
            else :
                dictTempAutresDonnees = {}

            # Mémorisation du track
            if track.solde < 0.0 :
                montant = -track.solde
            else :
                montant = track.solde
            dictTemp = {
                "IDpiece" : None, "IDfamille" : track.IDfamille, 
                "prelevement" : prelevement, "prelevement_iban" : prelevement_iban, "prelevement_bic" : prelevement_bic, 
                "prelevement_IDmandat" : prelevement_IDmandat, "prelevement_rum" : prelevement_rum, "prelevement_date_mandat" : prelevement_mandat_date,
                "prelevement_titulaire" : prelevement_titulaire, "type" : "facture", "IDfacture" : track.IDfacture, "prelevement_sequence" : prelevement_sequence,
                "libelle" : _(u"FACT%06d") % track.numero, "montant" : montant, "prelevement_statut" : "attente", "IDlot" : self.IDlot, "etat" : "ajout", "IDreglement" : None, "dateReglement" : None, 
                "IDdepot" : None, "IDcompte_payeur" : track.IDcompte_payeur, "titulaire_helios" : track.titulaire_helios, "numero" : track.numero, "dictAutresDonnees" : dictTempAutresDonnees,
                }
            
            if track.IDfacture not in listeFacturesPresentes :
                listeNewTracks.append(Track(dictTemp, dictTitulaires, self.dictIndividus))
        
##        if len(listeMandatsNonValides) > 0 :
##            message1 = _(u"Les factures suivantes n'ont pas été intégrées car les mandats des familles sont indisponibles ou non valides :")
##            message2 = "\n".join(listeMandatsNonValides)
##            dlg = dialogs.MultiMessageDialog(self, message1, caption=_(u"Avertissement"), msg2=message2, style = wx.ICON_EXCLAMATION |wx.OK, icon=None, btnLabels={wx.ID_OK : _(u"Ok")})
##            reponse = dlg.ShowModal() 
##            dlg.Destroy() 

        self.AddObjects(listeNewTracks)
        self.MAJtotaux() 

    def Modifier(self, event=None):
        if self.GetParent().GetVerrouillage() == True :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette action car le lot est verrouillé !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune pièce à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = DLG_Saisie_pes_piece.Dialog(self, track=track, activeMontant=False)      
        if dlg.ShowModal() == wx.ID_OK:
            if track.etat != "ajout" :
                track.etat = "modif"
            self.RefreshObject(track)
            self.MAJtotaux() 
        dlg.Destroy() 

    def Supprimer(self, event=None):
        if self.GetParent().GetVerrouillage() == True :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette action car le lot est verrouillé !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune pièce à retirer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if len(self.GetTracksCoches()) > 0 :
            # Suppression multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment retirer les %d pièces cochées ?") % len(listeSelections), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        else :
            # Suppression unique
            listeSelections = self.Selection()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment retirer la pièce sélectionnée ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        # Vérifie que la pièce n'est pas déjà déposé en banque
        listeDepots = []
        for track in listeSelections :
            if track.IDdepot != None :
                listeDepots.append(track)
        if len(listeDepots) > 0 :
            dlg = wx.MessageDialog(self, _(u"Suppression interdite car %d pièce(s) de la sélection ont déjà un règlement attribué à un dépôt de règlement !") % len(listeDepots), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Suppression
        for track in listeSelections :
            if track.etat in (None, "modif") :
                self.listeSuppressions.append(track)
            self.RemoveObject(track)
        self.MAJtotaux() 
        

    def CocheTout(self, event=None):
        if self.GetFilter() != None :
            listeObjets = self.GetFilteredObjects()
        else :
            listeObjets = self.GetObjects()
        for track in listeObjets :
            self.Check(track)
            self.RefreshObject(track)
        
    def CocheRien(self, event=None):
        if self.GetFilter() != None :
            listeObjets = self.GetFilteredObjects()
        else :
            listeObjets = self.GetObjects()
        for track in listeObjets :
            self.Uncheck(track)
            self.RefreshObject(track)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()
    
    def SetStatut(self, statut="attente") :
        listeDepots = []
        for track in self.GetObjects() :
            if self.IsChecked(track) :
                # Changement de statut
                track.prelevement_statut = statut
                
                # Règlement automatique
                if self.reglement_auto == True and statut == "valide" :
                    track.reglement = True   
                
                # Annulation du règlement si statut = refus
                if statut == "refus" :
                    if track.IDdepot != None :
                        listeDepots.append(track)
                    else :
                        track.reglement = False
                             
                if track.etat != "ajout" :
                    track.etat = "modif"
                self.RefreshObject(track)
                
        self.MAJtotaux() 
        
        if len(listeDepots) > 0 :
            dlg = wx.MessageDialog(self, _(u"Notez que Noethys n'a pas procédé changement de statut de %d pièce(s) car le règlement correspondant appartient déjà à un dépôt de règlement !") % len(listeDepots), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return


    def SetRegle(self, etat=False) :
        listeAnomalies = []
        listeDepots = []
        for track in self.GetObjects() :                
            if self.IsChecked(track) :
    
                if etat == True :
                    # Si on veut régler
                    if track.prelevement_statut in ("valide", "attente") :
                        track.reglement = True
                        if track.etat != "ajout" :
                            track.etat = "modif"
                        self.RefreshObject(track)
                    else :
                        listeAnomalies.append(track)
                
                if etat == False :
                    # Si on veut annuler le règlement
                    if track.IDdepot != None :
                        listeDepots.append(track)
                    else :
                        track.reglement = False
                        if track.etat != "ajout" :
                            track.etat = "modif"
                        self.RefreshObject(track)

        if len(listeAnomalies) > 0 :
            dlg = wx.MessageDialog(self, _(u"Notez que Noethys n'a pas procédé au règlement de %d pièce(s) en raison de leur statut 'Refus'.") % len(listeAnomalies), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(listeDepots) > 0 :
            dlg = wx.MessageDialog(self, _(u"Notez que Noethys n'a pas procédé à la suppression de %d pièce(s) car le règlement correspondant appartient déjà à un dépôt de règlement !") % len(listeDepots), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.MAJtotaux() 

    def GetLabelListe(self):
        """ Récupère le nombre de pièces et le montant total de la liste """
        nbre = 0
        montant = 0.0
        for track in self.GetObjects() :
            nbre += 1
            montant += track.montant
        # Label de staticbox
        if nbre > 1 :
            texte = _(u"pièces")
        else :
            texte = _(u"pièce")
        label = u"%d %s (%.2f %s)" % (nbre, texte, montant, SYMBOLE)
        return label          

    def MAJtotaux(self):
        """ Créé le texte infos avec les stats du lot """
        if self.GetParent().GetName() != "DLG_Saisie_pes_lot" :
            return
        # Label de staticbox
        texte = self.GetTexteTotaux()
        self.GetParent().ctrl_totaux.SetLabel(texte)
        self.GetParent().box_pieces_staticbox.SetLabel(self.GetLabelListe())

    def GetTexteTotaux(self):
        # Récupération des chiffres
        nbreTotal = 0
        montantTotal = 0.0
        dictDetails = {}
        for track in self.GetObjects() :
            nbreTotal += 1
            montantTotal += track.montant
            # Regroupement par statut
            if dictDetails.has_key(track.prelevement_statut) == False :
                dictDetails[track.prelevement_statut] = {"nbre" : 0, "montant" : 0.0}
            dictDetails[track.prelevement_statut]["nbre"] += 1
            dictDetails[track.prelevement_statut]["montant"] += track.montant
            # Regroupement par règlemennt
            if track.reglement == True :
                reglement = "regle"
            else :
                reglement = "pasregle"
            if dictDetails.has_key(reglement) == False :
                dictDetails[reglement] = {"nbre" : 0, "montant" : 0.0}
            dictDetails[reglement]["nbre"] += 1
            dictDetails[reglement]["montant"] += track.montant
            
        # Création du texte
        if nbreTotal == 0 :
            texte = _(u"<B>Aucune pièce   </B>")
        elif nbreTotal == 1 :
            texte = _(u"<B>%d pièce (%.2f %s) : </B>") % (nbreTotal, montantTotal, SYMBOLE)
        else :
            texte = _(u"<B>%d pièces (%.2f %s) : </B>") % (nbreTotal, montantTotal, SYMBOLE)
        
        for key in ("attente", "valide", "refus", "regle", "pasregle") :
            if dictDetails.has_key(key) :
                dictDetail = dictDetails[key]
                if dictDetail["nbre"] == 1 :
                    if key == "attente" : label = _(u"en attente")
                    if key == "valide" : label = _(u"validé")
                    if key == "refus" : label = _(u"refusé")
                    if key == "regle" : label = _(u"réglé")
                    if key == "pasregle" : label = _(u"non réglé")
                else :
                    if key == "attente" : label = _(u"en attente")
                    if key == "valide" : label = _(u"validés")
                    if key == "refus" : label = _(u"refusés")
                    if key == "regle" : label = _(u"réglés")
                    if key == "pasregle" : label = _(u"non réglés")
                texteDetail = u"%d %s (%.2f %s), " % (dictDetail["nbre"], label, dictDetail["montant"], SYMBOLE)
                texte += texteDetail
        if len(dictDetails) > 0 :
            texte = texte[:-2] + u"."
        else:
            texte = texte[:-7] + u"</B>"
        return texte

    def Sauvegarde(self, IDlot=None, datePrelevement=None, IDcompte=None, IDmode=None):
        """ Sauvegarde des données """
        DB = GestionDB.DB()
        
        # Ajouts et suppressions
        for track in self.GetObjects() :
            
            listeDonnees = [
                ("IDlot", IDlot ),
                ("IDfamille", track.IDfamille),
                ("prelevement", track.prelevement),
                ("prelevement_iban", track.prelevement_iban),
                ("prelevement_bic", track.prelevement_bic),
                ("prelevement_rum", track.prelevement_rum),
                ("prelevement_date_mandat", track.prelevement_date_mandat),
                ("prelevement_IDmandat", track.prelevement_IDmandat),
                ("prelevement_sequence", track.prelevement_sequence),
                ("prelevement_titulaire", track.prelevement_titulaire),
                ("prelevement_statut", track.prelevement_statut),
                ("titulaire_helios", track.titulaire_helios),
                ("type", track.type),
                ("IDfacture", track.IDfacture),
                ("numero", track.numero),
                ("libelle", track.libelle),
                ("montant", track.montant),
                ]

            # Ajout
            if track.etat == "ajout" :
                track.IDpiece = DB.ReqInsert("pes_pieces", listeDonnees)
                self.RefreshObject(track)
            
            # Modification
            if track.etat == "modif" :
                DB.ReqMAJ("pes_pieces", listeDonnees, "IDpiece", track.IDpiece)
        
        # Suppressions
        for track in self.listeSuppressions :
            if track.IDpiece != None :
                DB.ReqDEL("pes_pieces", "IDpiece", track.IDpiece)
            if track.IDreglement != None :
                DB.ReqDEL("reglements", "IDreglement", track.IDreglement)
                DB.ReqDEL("ventilation", "IDreglement", track.IDreglement)

        DB.Close() 
        
        # Sauvegarde des règlements
        self.SauvegardeReglements(date=datePrelevement, IDcompte=IDcompte, IDmode=IDmode)


    def SauvegardeReglements(self, date=None, IDcompte=None, IDmode=None):
        """ A effectuer après la sauvegarde des prélèvements """
        DB = GestionDB.DB()
        
        # Recherche des payeurs
        req = """SELECT IDpayeur, IDcompte_payeur, nom
        FROM payeurs;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictPayeurs = {}
        for IDpayeur, IDcompte_payeur, nom in listeDonnees :
            if dictPayeurs.has_key(IDcompte_payeur) == False :
                dictPayeurs[IDcompte_payeur] = []
            dictPayeurs[IDcompte_payeur].append({"nom" : nom, "IDpayeur" : IDpayeur})

        
        # Récupération des prestations à ventiler pour chaque facture
        listeIDfactures = []
        for track in self.GetObjects() :
            if track.IDfacture != None :
                listeIDfactures.append(track.IDfacture)
        
        if len(listeIDfactures) == 0 : conditionFactures = "()"
        elif len(listeIDfactures) == 1 : conditionFactures = "(%d)" % listeIDfactures[0]
        else : conditionFactures = str(tuple(listeIDfactures))
            
        req = """SELECT 
        prestations.IDprestation, prestations.IDcompte_payeur, prestations.montant, 
        prestations.IDfacture, SUM(ventilation.montant) AS montant_ventilation
        FROM prestations
        LEFT JOIN ventilation ON prestations.IDprestation = ventilation.IDprestation
        WHERE prestations.IDfacture IN %s
        GROUP BY prestations.IDprestation
        ;""" % conditionFactures
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        dictFactures = {}
        for IDprestation, IDcompte_payeur, montant, IDfacture, ventilation in listeDonnees :
            if ventilation == None : 
                ventilation = 0.0
            montant = decimal.Decimal(montant)
            ventilation = decimal.Decimal(ventilation)
            aventiler = montant - ventilation
            if aventiler > decimal.Decimal(0.0) :
                if dictFactures.has_key(IDfacture) == False :
                    dictFactures[IDfacture] = []
                dictFactures[IDfacture].append({"IDprestation" : IDprestation, "IDcompte_payeur" : IDcompte_payeur, "montant" : montant, "ventilation" : ventilation, "aventiler" : aventiler})
                        
        # Sauvegarde des règlements + ventilation
        listeSuppressionReglements = []
        for track in self.GetObjects() :

            # Ajouts et modifications
            if track.reglement == True :
                
                # Recherche du payeur
                IDpayeur = None
                if dictPayeurs.has_key(track.IDcompte_payeur) :
                    for dictPayeur in dictPayeurs[track.IDcompte_payeur] :
                        if dictPayeur["nom"] == track.prelevement_titulaire :
                            IDpayeur = dictPayeur["IDpayeur"]
                
                # Si pas de payeur correspond au titulaire du compte trouvé :
                if IDpayeur == None :
                    IDpayeur = DB.ReqInsert("payeurs", [("IDcompte_payeur", track.IDcompte_payeur), ("nom", track.prelevement_titulaire)])
                    
                # Création des données à sauvegarder
                listeDonnees = [
                    ("IDcompte_payeur", track.IDcompte_payeur),
                    ("date", date),
                    ("IDmode", IDmode),
                    ("IDemetteur", None),
                    ("numero_piece", None),
                    ("montant", track.montant),
                    ("IDpayeur", IDpayeur),
                    ("observations", None),
                    ("numero_quittancier", None),
                    ("IDcompte", IDcompte),
                    ("date_differe", None),
                    ("encaissement_attente", 0),
                    ("date_saisie", datetime.date.today()),
                    ("IDutilisateur", UTILS_Identification.GetIDutilisateur() ),
                    ("IDpiece", track.IDpiece),
                    ]
                

                # Ajout
                if track.IDreglement == None :
                    track.IDreglement = DB.ReqInsert("reglements", listeDonnees)
                    
                # Modification
                else:
                    DB.ReqMAJ("reglements", listeDonnees, "IDreglement", track.IDreglement)
                track.dateReglement = date
                
                # ----------- Sauvegarde de la ventilation ---------
                if dictFactures.has_key(track.IDfacture) :
                    for dictFacture in dictFactures[track.IDfacture] :
                        listeDonnees = [    
                                ("IDreglement", track.IDreglement),
                                ("IDcompte_payeur", track.IDcompte_payeur),
                                ("IDprestation", dictFacture["IDprestation"]),
                                ("montant", float(dictFacture["aventiler"])),
                            ]
                        IDventilation = DB.ReqInsert("ventilation", listeDonnees)        
            
            # Suppression de règlements et ventilation
            else :

                if track.IDreglement != None :
                    DB.ReqDEL("reglements", "IDreglement", track.IDreglement)
                    DB.ReqDEL("ventilation", "IDreglement", track.IDreglement)
            
            # MAJ du track
            self.RefreshObject(track)
        
        DB.Close() 





# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
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

class PanelTest(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)
        
    def GetVerrouillage(self):
        return False
        
class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = PanelTest(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.myOlv = ListView(panel, id=-1, IDlot=1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
##        tracks = GetTracks(IDlot=3)
        tracks = GetTracks(IDmandat=6)
        self.myOlv.MAJ(tracks=tracks) 
        
        self.bouton_test = wx.Button(panel, -1, _(u"Bouton test"))
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
