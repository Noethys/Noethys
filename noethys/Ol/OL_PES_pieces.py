#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
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
from Utils import UTILS_Dates
from Dlg import DLG_Saisie_pes_piece
from Utils import UTILS_Identification
from Utils import UTILS_Prelevements
from Utils import UTILS_Mandats
import wx.lib.dialogs as dialogs

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils import UTILS_Titulaires



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
        self.tiers_solidaire = donnees["tiers_solidaire"]
        self.InitTitulaireHelios()

        # Autres donn�es H�lios
        if "idtiers_helios" in donnees["dictAutresDonnees"] :
            self.idtiers_helios = donnees["dictAutresDonnees"]["idtiers_helios"]
            if self.idtiers_helios == None :
                self.idtiers_helios = ""
        else :
            self.idtiers_helios = ""
        if "natidtiers_helios" in donnees["dictAutresDonnees"] :
            self.natidtiers_helios = donnees["dictAutresDonnees"]["natidtiers_helios"]
            if self.natidtiers_helios in (9999, None) :
                self.natidtiers_helios = ""
            else:
                self.natidtiers_helios = "0%d" % self.natidtiers_helios
        else :
            self.natidtiers_helios = ""
        if "reftiers_helios" in donnees["dictAutresDonnees"] :
            self.reftiers_helios = donnees["dictAutresDonnees"]["reftiers_helios"]
            if self.reftiers_helios == None :
                self.reftiers_helios = ""
        else :
            self.reftiers_helios = ""
        if "cattiers_helios" in donnees["dictAutresDonnees"] :
            self.cattiers_helios = donnees["dictAutresDonnees"]["cattiers_helios"]
            if self.cattiers_helios == None :
                self.cattiers_helios = "01"
            else :
                self.cattiers_helios = "%02d" % self.cattiers_helios
        else :
            self.cattiers_helios = "01"
        if "natjur_helios" in donnees["dictAutresDonnees"] :
            self.natjur_helios = donnees["dictAutresDonnees"]["natjur_helios"]
            if self.natjur_helios == None :
                self.natjur_helios = "01"
            else :
                self.natjur_helios = "%02d" % self.natjur_helios
        else :
            self.natjur_helios = "01"

        # Code tiers de la famille
        self.code_tiers = u"FAM%06d" % self.IDfamille

        # Code compta de la famille
        self.code_compta = ""
        if "code_compta" in donnees["dictAutresDonnees"] and donnees["dictAutresDonnees"]["code_compta"]:
            self.code_compta = donnees["dictAutresDonnees"]["code_compta"]

        # Etat de la pi�ce
        self.etat = donnees["etat"] # "ajout", "modif"
        self.AnalysePiece()
        
    def InitTitulaireHelios(self):
        if self.titulaire_helios in self.dictIndividus :
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

        if self.tiers_solidaire in self.dictIndividus :
            self.tiersSolidaireCivilite = self.dictIndividus[self.tiers_solidaire]["civiliteAbrege"]
            self.tiersSolidaireNom = self.dictIndividus[self.tiers_solidaire]["nom"]
            self.tiersSolidairePrenom = self.dictIndividus[self.tiers_solidaire]["prenom"]
            if self.tiersSolidaireCivilite == None :
                self.tiersSolidaireNomComplet = u"%s %s" % (self.tiersSolidaireNom, self.tiersSolidairePrenom)
            else :
                self.tiersSolidaireNomComplet = u"%s %s %s" % (self.tiersSolidaireCivilite, self.tiersSolidaireNom, self.tiersSolidairePrenom)
            self.tiersSolidaireNomPrenom = u"%s %s" % (self.tiersSolidaireNom, self.tiersSolidairePrenom)
            self.tiersSolidaireRue = self.dictIndividus[self.tiers_solidaire]["rue"]
            self.tiersSolidaireCP = self.dictIndividus[self.tiers_solidaire]["cp"]
            self.tiersSolidaireVille = self.dictIndividus[self.tiers_solidaire]["ville"]
            self.tiersSolidaireAdresse = u"%s %s %s" % (self.tiersSolidaireRue, self.tiersSolidaireCP, self.tiersSolidaireVille)
        else :
            self.tiersSolidaireCivilite = ""
            self.tiersSolidaireNom = ""
            self.tiersSolidairePrenom = ""
            self.tiersSolidaireNomComplet = ""
            self.tiersSolidaireNomPrenom = ""
            self.tiersSolidaireRue = ""
            self.tiersSolidaireCP = ""
            self.tiersSolidaireVille = ""
            self.tiersSolidaireAdresse = ""

    def InitNomsTitulaires(self):
        if self.IDfamille != None :
            self.titulaires = self.dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
    
    def AnalysePiece(self):
        listeProblemes = []
        
        if self.titulaire_helios in (None, "") : 
            listeProblemes.append(_(u"Titulaire H�lios manquant"))
        else :
            if self.titulaireRue in (None, "") or self.titulaireCP in (None, "") or self.titulaireVille in (None, "") : 
                listeProblemes.append(_(u"Adresse du titulaire H�lios incompl�te"))
        
        if self.prelevement == 1 :
            if self.prelevement_iban in (None, "") or self.prelevement_bic in (None, "") or self.prelevement_titulaire in (None, "") :
                listeProblemes.append(_(u"Coordonn�es bancaires incompl�tes"))
            if self.prelevement_rum in (None, "") or self.prelevement_IDmandat in (None, "") or self.prelevement_date_mandat in (None, "") :
                listeProblemes.append(_(u"Mandat SEPA manquant"))
            if self.prelevement_sequence in (None, "") :
                listeProblemes.append(_(u"S�quence SEPA non renseign�e"))
        
        if len(listeProblemes) > 0 :
            self.analysePiece = False
            self.analysePieceTexte = u", ".join(listeProblemes)
        else :
            self.analysePiece = True
            self.analysePieceTexte = _(u"Pi�ce valide")

def GetDictAutresDonnees():
    DB = GestionDB.DB()
    req = """SELECT IDfamille, idtiers_helios, natidtiers_helios, reftiers_helios, cattiers_helios, natjur_helios, code_comptable
    FROM familles;"""
    DB.ExecuterReq(req)
    listeAutresDonnees = DB.ResultatReq()
    dictAutresDonnees = {}
    for IDfamille, idtiers_helios, natidtiers_helios, reftiers_helios, cattiers_helios, natjur_helios, code_compta in listeAutresDonnees :
        dictAutresDonnees[IDfamille] = {
            "idtiers_helios": idtiers_helios, "natidtiers_helios": natidtiers_helios, "reftiers_helios": reftiers_helios,
            "cattiers_helios": cattiers_helios, "natjur_helios": natjur_helios, "code_compta": code_compta
        }
    DB.Close() 
    return dictAutresDonnees

def GetTracks(IDlot=None, IDmandat=None):
    """ R�cup�ration des donn�es """
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
    pes_pieces.titulaire_helios, pes_pieces.tiers_solidaire, pes_pieces.numero
    FROM pes_pieces
    LEFT JOIN reglements ON reglements.IDpiece = pes_pieces.IDpiece
    LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = pes_pieces.IDfamille
    %s
    ;""" % criteres
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    listeListeView = []
    for IDpiece, IDlot, IDfamille, prelevement, prelevement_iban, prelevement_bic, prelevement_IDmandat, prelevement_rum, prelevement_date_mandat, prelevement_sequence, prelevement_titulaire, prelevement_statut, type_piece, IDfacture, libelle, montant, IDreglement, dateReglement, IDdepot, IDcompte_payeur, titulaire_helios, tiers_solidaire, numero in listeDonnees :
        if IDfamille in dictAutresDonnees :
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
            "titulaire_helios" : titulaire_helios, "tiers_solidaire": tiers_solidaire, "numero" : numero, "dictAutresDonnees" : dictTempAutresDonnees,
            }
        track = Track(dictTemp, dictTitulaires, dictIndividus)
        listeListeView.append(track)
    return listeListeView



    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
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
        self.nom_fichier_liste = __file__
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
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        # Image list
        self.imgValide = self.AddNamedImages("valide", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        self.imgRefus = self.AddNamedImages("refus", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.imgAttente = self.AddNamedImages("attente", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attente.png"), wx.BITMAP_TYPE_PNG))
        self.imgPrelevement = self.AddNamedImages("prelevement", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Prelevement.png"), wx.BITMAP_TYPE_PNG))
        
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
            ColumnDefn(_(u"Analyse pi�ce"), 'left', 120, "analysePieceTexte", typeDonnee="texte", imageGetter=GetImageAnalysePiece),
            ColumnDefn(_(u"Famille"), 'left', 230, "titulaires", typeDonnee="texte"),
##            ColumnDefn(_(u"Type"), 'left', 70, "type", stringConverter=FormateType),
            ColumnDefn(_(u"Libell�"), 'left', 110, "libelle", typeDonnee="texte"),
            ColumnDefn(_(u"Montant"), 'right', 70, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Statut"), 'left', 80, "prelevement_statut", typeDonnee="texte", stringConverter=FormateStatut, imageGetter=GetImageStatut),
            ColumnDefn(_(u"R�glement"), 'left', 70, "reglement", typeDonnee="bool", stringConverter=FormateReglement, imageGetter=GetImageReglement),
            ColumnDefn(_(u"Pr�l�vt"), 'left', 55, "prelevement", typeDonnee="bool", stringConverter=FormatePrelevement, imageGetter=GetImagePrelevement),
            ColumnDefn(_(u"S�quence"), 'left', 70, "prelevement_sequence", typeDonnee="texte"),
            ColumnDefn(_(u"IBAN"), 'left', 190, "prelevement_iban", typeDonnee="texte"),
            ColumnDefn(_(u"BIC"), 'left', 100, "prelevement_bic", typeDonnee="texte"),
            ColumnDefn(_(u"Titulaire compte bancaire"), 'left', 160, "prelevement_titulaire", typeDonnee="texte"),
            ColumnDefn(_(u"Ref. mandat"), 'left', 90, "prelevement_rum", typeDonnee="texte"),
            ColumnDefn(_(u"Date mandat"), 'left', 80, "prelevement_date_mandat", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Titulaire H�lios"), 'left', 150, "titulaireNomComplet", typeDonnee="texte"),
            ColumnDefn(_(u"Adresse"), 'left', 220, "titulaireAdresse", typeDonnee="texte"),
            ColumnDefn(_(u"ID Tiers"), 'left', 70, "idtiers_helios", typeDonnee="texte"),
            ColumnDefn(_(u"Type IDTiers"), 'left', 70, "natidtiers_helios", typeDonnee="texte"),
            ColumnDefn(_(u"Ref. Tiers"), 'left', 70, "reftiers_helios", typeDonnee="texte"),
            ColumnDefn(_(u"Cat. Tiers"), 'left', 70, "cattiers_helios", typeDonnee="texte"),
            ColumnDefn(_(u"Nat. Jur."), 'left', 70, "natjur_helios", typeDonnee="texte"),
            ColumnDefn(_(u"Code compta."), 'left', 95, "code_compta", typeDonnee="texte"),
            ]
        

        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune pi�ce"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
##        self.SetSortColumn(self.columns[self.numColonneTri])
        self.SortBy(self.numColonneTri, ascending=self.ordreAscendant)
        self.SetObjects(self.donnees)
       
    def MAJ(self, tracks=None, ID=None, selectionTrack=None, nextTrack=None, IDcompte=None, IDmode=None):
        self.InitModel(tracks, IDcompte, IDmode)
        self.InitObjectListView()
        # S�lection d'un item
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
                
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Saisie manuelle
##        item = wx.MenuItem(menuPop, 10, _(u"Ajouter un pr�l�vement manuel"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Saisie_manuelle, id=10)

        # Item Saisie de factures
        item = wx.MenuItem(menuPop, 11, _(u"Ajouter une ou plusieurs factures"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Saisie_factures, id=11)

        menuPop.AppendSeparator()

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
                
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Retirer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)

        menuPop.AppendSeparator()

        # Item Activer le pr�l�vement
        item = wx.MenuItem(menuPop, 800, _(u"Activer le pr�l�vement"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Prelevement.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ActiverPrelevement, id=800)

        # Item Activer le pr�l�vement
        item = wx.MenuItem(menuPop, 801, _(u"D�sactiver le pr�l�vement"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Prelevement.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ActiverPrelevement, id=801)

        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self):
        # R�cup�re l'intitul� du compte
        txtIntro = self.GetParent().GetLabelParametres()
        # R�cup�re le total
        total = 0.0
        for track in self.donnees :
            total += track.montant
        txtTotal = self.GetTexteTotaux().replace("<B>", "").replace("</B>", "")
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des pi�ces du bordereau"), intro=txtIntro, total=txtTotal, format="A", orientation=wx.LANDSCAPE)
        return prt
        
    def Apercu(self, event=None):
        self.Impression().Preview()

    def Imprimer(self, event=None):
        self.Impression().Print()

    def ExportTexte(self, event=None):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des pi�ces du bordereau"))
        
    def ExportExcel(self, event=None):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des pi�ces du bordereau"))
        
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
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette action car le lot est verrouill� !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        from Dlg import DLG_Pes_factures
        dlg = DLG_Pes_factures.Dialog(self, IDlot=self.IDlot)
        reponse = dlg.ShowModal()
        tracks = dlg.GetTracks()
        dlg.Destroy()
        if reponse != wx.ID_OK :
            return
        self.AjoutFactures(tracks)
    
    def AjoutFactures(self, tracks=[]):
        # V�rifie que cette facture n'est pas d�j� pr�sente dans le lot
        listeFacturesPresentes = []
        for track in self.GetObjects() :
            if track.IDfacture != None :
                listeFacturesPresentes.append(track.IDfacture)
        
        mandats = UTILS_Mandats.Mandats() 
        dictAutresDonnees = GetDictAutresDonnees()
        
        # MAJ de la liste affich�e
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
                if track.IDfamille in dictTitulaires :
                    nomTitulaires = dictTitulaires[track.IDfamille]["titulairesSansCivilite"]
                else :
                    nomTitulaires = _(u"Titulaires inconnus")
                listeMandatsNonValides.append(_(u"Facture n�%s de la famille %s") % (track.numero, nomTitulaires))

                prelevement = 0
                prelevement_iban = ""
                prelevement_bic = ""
                prelevement_IDmandat = ""
                prelevement_rum = ""
                prelevement_mandat_date = ""
                prelevement_titulaire = ""
                prelevement_sequence = ""

            else :
                # R�cup�re les donn�es du mandat
                dictMandat = mandats.GetDictMandat(IDmandat) 
                prelevement = 1
                prelevement_iban = dictMandat["iban"]
                prelevement_bic = dictMandat["bic"]
                prelevement_IDmandat = dictMandat["IDmandat"]
                prelevement_rum = dictMandat["rum"]
                prelevement_mandat_date = dictMandat["date"]
                prelevement_titulaire = dictMandat["titulaire"]
                
                # Recherche de la s�quence
                analyse = mandats.AnalyseMandat(prelevement_IDmandat)
                prelevement_sequence = analyse["prochaineSequence"]
                
            if track.IDfamille in dictAutresDonnees :
                dictTempAutresDonnees = dictAutresDonnees[track.IDfamille]
            else :
                dictTempAutresDonnees = {}

            # M�morisation du track
            if track.solde < 0.0 :
                montant = -track.solde
            else :
                montant = track.solde
            dictTemp = {
                "IDpiece" : None, "IDfamille" : track.IDfamille, 
                "prelevement" : prelevement, "prelevement_iban" : prelevement_iban, "prelevement_bic" : prelevement_bic, 
                "prelevement_IDmandat" : prelevement_IDmandat, "prelevement_rum" : prelevement_rum, "prelevement_date_mandat" : prelevement_mandat_date,
                "prelevement_titulaire" : prelevement_titulaire, "type" : "facture", "IDfacture" : track.IDfacture, "prelevement_sequence" : prelevement_sequence,
                "libelle" : _(u"FACT%s") % track.numero, "montant" : montant, "prelevement_statut" : "attente", "IDlot" : self.IDlot, "etat" : "ajout", "IDreglement" : None, "dateReglement" : None,
                "IDdepot" : None, "IDcompte_payeur" : track.IDcompte_payeur, "titulaire_helios" : track.titulaire_helios, "tiers_solidaire": track.tiers_solidaire, "numero" : track.numero, "dictAutresDonnees" : dictTempAutresDonnees,
                }
            
            if track.IDfacture not in listeFacturesPresentes :
                listeNewTracks.append(Track(dictTemp, dictTitulaires, self.dictIndividus))
        
##        if len(listeMandatsNonValides) > 0 :
##            message1 = _(u"Les factures suivantes n'ont pas �t� int�gr�es car les mandats des familles sont indisponibles ou non valides :")
##            message2 = "\n".join(listeMandatsNonValides)
##            dlg = dialogs.MultiMessageDialog(self, message1, caption=_(u"Avertissement"), msg2=message2, style = wx.ICON_EXCLAMATION |wx.OK, icon=None, btnLabels={wx.ID_OK : _(u"Ok")})
##            reponse = dlg.ShowModal() 
##            dlg.Destroy() 

        self.AddObjects(listeNewTracks)
        self.MAJtotaux() 

    def Modifier(self, event=None):
        if self.GetParent().GetVerrouillage() == True :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette action car le lot est verrouill� !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune pi�ce � modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
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
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette action car le lot est verrouill� !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune pi�ce � retirer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if len(self.GetTracksCoches()) > 0 :
            # Suppression multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment retirer les %d pi�ces coch�es ?") % len(listeSelections), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        else :
            # Suppression unique
            listeSelections = self.Selection()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment retirer la pi�ce s�lectionn�e ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        # V�rifie que la pi�ce n'est pas d�j� d�pos� en banque
        listeDepots = []
        for track in listeSelections :
            if track.IDdepot != None :
                listeDepots.append(track)
        if len(listeDepots) > 0 :
            dlg = wx.MessageDialog(self, _(u"Suppression interdite car %d pi�ce(s) de la s�lection ont d�j� un r�glement attribu� � un d�p�t de r�glement !") % len(listeDepots), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Suppression
        for track in listeSelections :
            if track.etat in (None, "modif") :
                self.listeSuppressions.append(track)
            self.RemoveObject(track)
        self.MAJtotaux() 
        
    def ActiverPrelevement(self, event):
        if event.GetId() == 800 :
            prelevement = 1
        else :
            prelevement = 0

        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune pi�ce dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.GetTracksCoches()) > 0 :
            # S�lection multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment modifier le pr�l�vement des %d pi�ces coch�es ?") % len(listeSelections), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        else :
            # S�lection unique
            listeSelections = self.Selection()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment modifier le pr�l�vement de la pi�ce s�lectionn�e ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        # Activation/D�sactivation du pr�l�vement des pi�ces
        for track in listeSelections :
            if prelevement == 0 :
                track.prelevement = 0
                if track.etat != "ajout":
                    track.etat = "modif"
            if prelevement == 1 and track.prelevement_iban != "" :
                track.prelevement = 1
                if track.etat != "ajout":
                    track.etat = "modif"
        self.RefreshObjects(listeSelections)


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
                
                # R�glement automatique
                if self.reglement_auto == True and statut == "valide" :
                    track.reglement = True   
                
                # Annulation du r�glement si statut = refus
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
            dlg = wx.MessageDialog(self, _(u"Notez que Noethys n'a pas proc�d� changement de statut de %d pi�ce(s) car le r�glement correspondant appartient d�j� � un d�p�t de r�glement !") % len(listeDepots), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return


    def SetRegle(self, etat=False) :
        listeAnomalies = []
        listeDepots = []
        for track in self.GetObjects() :                
            if self.IsChecked(track) :
    
                if etat == True :
                    # Si on veut r�gler
                    if track.prelevement_statut in ("valide", "attente") :
                        track.reglement = True
                        if track.etat != "ajout" :
                            track.etat = "modif"
                        self.RefreshObject(track)
                    else :
                        listeAnomalies.append(track)
                
                if etat == False :
                    # Si on veut annuler le r�glement
                    if track.IDdepot != None :
                        listeDepots.append(track)
                    else :
                        track.reglement = False
                        if track.etat != "ajout" :
                            track.etat = "modif"
                        self.RefreshObject(track)

        if len(listeAnomalies) > 0 :
            dlg = wx.MessageDialog(self, _(u"Notez que Noethys n'a pas proc�d� au r�glement de %d pi�ce(s) en raison de leur statut 'Refus'.") % len(listeAnomalies), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(listeDepots) > 0 :
            dlg = wx.MessageDialog(self, _(u"Notez que Noethys n'a pas proc�d� � la suppression de %d pi�ce(s) car le r�glement correspondant appartient d�j� � un d�p�t de r�glement !") % len(listeDepots), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.MAJtotaux() 

    def GetLabelListe(self):
        """ R�cup�re le nombre de pi�ces et le montant total de la liste """
        nbre = 0
        montant = 0.0
        for track in self.GetObjects() :
            nbre += 1
            montant += track.montant
        # Label de staticbox
        if nbre > 1 :
            texte = _(u"pi�ces")
        else :
            texte = _(u"pi�ce")
        label = u"%d %s (%.2f %s)" % (nbre, texte, montant, SYMBOLE)
        return label          

    def MAJtotaux(self):
        """ Cr�� le texte infos avec les stats du lot """
        if self.GetParent().GetName() != "DLG_Saisie_lot_tresor_public" :
            return
        # Label de staticbox
        texte = self.GetTexteTotaux()
        self.GetParent().ctrl_totaux.SetLabel(texte)
        self.GetParent().box_pieces_staticbox.SetLabel(self.GetLabelListe())

    def GetTexteTotaux(self):
        # R�cup�ration des chiffres
        nbreTotal = 0
        montantTotal = 0.0
        dictDetails = {}
        for track in self.GetObjects() :
            nbreTotal += 1
            montantTotal += track.montant
            # Regroupement par statut
            if (track.prelevement_statut in dictDetails) == False :
                dictDetails[track.prelevement_statut] = {"nbre" : 0, "montant" : 0.0}
            dictDetails[track.prelevement_statut]["nbre"] += 1
            dictDetails[track.prelevement_statut]["montant"] += track.montant
            # Regroupement par r�glemennt
            if track.reglement == True :
                reglement = "regle"
            else :
                reglement = "pasregle"
            if (reglement in dictDetails) == False :
                dictDetails[reglement] = {"nbre" : 0, "montant" : 0.0}
            dictDetails[reglement]["nbre"] += 1
            dictDetails[reglement]["montant"] += track.montant
            
        # Cr�ation du texte
        if nbreTotal == 0 :
            texte = _(u"<B>Aucune pi�ce   </B>")
        elif nbreTotal == 1 :
            texte = _(u"<B>%d pi�ce (%.2f %s) : </B>") % (nbreTotal, montantTotal, SYMBOLE)
        else :
            texte = _(u"<B>%d pi�ces (%.2f %s) : </B>") % (nbreTotal, montantTotal, SYMBOLE)
        
        for key in ("attente", "valide", "refus", "regle", "pasregle") :
            if key in dictDetails :
                dictDetail = dictDetails[key]
                if dictDetail["nbre"] == 1 :
                    if key == "attente" : label = _(u"en attente")
                    if key == "valide" : label = _(u"valid�")
                    if key == "refus" : label = _(u"refus�")
                    if key == "regle" : label = _(u"r�gl�")
                    if key == "pasregle" : label = _(u"non r�gl�")
                else :
                    if key == "attente" : label = _(u"en attente")
                    if key == "valide" : label = _(u"valid�s")
                    if key == "refus" : label = _(u"refus�s")
                    if key == "regle" : label = _(u"r�gl�s")
                    if key == "pasregle" : label = _(u"non r�gl�s")
                texteDetail = u"%d %s (%.2f %s), " % (dictDetail["nbre"], label, dictDetail["montant"], SYMBOLE)
                texte += texteDetail
        if len(dictDetails) > 0 :
            texte = texte[:-2] + u"."
        else:
            texte = texte[:-7] + u"</B>"
        return texte

    def Sauvegarde(self, IDlot=None, datePrelevement=None, IDcompte=None, IDmode=None):
        """ Sauvegarde des donn�es """
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
                ("tiers_solidaire", track.tiers_solidaire),
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
        
        # Sauvegarde des r�glements
        self.SauvegardeReglements(date=datePrelevement, IDcompte=IDcompte, IDmode=IDmode)


    def SauvegardeReglements(self, date=None, IDcompte=None, IDmode=None):
        """ A effectuer apr�s la sauvegarde des pr�l�vements """
        DB = GestionDB.DB()
        
        # Recherche des payeurs
        req = """SELECT IDpayeur, IDcompte_payeur, nom
        FROM payeurs;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictPayeurs = {}
        for IDpayeur, IDcompte_payeur, nom in listeDonnees :
            if (IDcompte_payeur in dictPayeurs) == False :
                dictPayeurs[IDcompte_payeur] = []
            dictPayeurs[IDcompte_payeur].append({"nom" : nom, "IDpayeur" : IDpayeur})

        
        # R�cup�ration des prestations � ventiler pour chaque facture
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
        dictAventiler = {}
        for IDprestation, IDcompte_payeur, montant, IDfacture, ventilation in listeDonnees :
            if ventilation == None : 
                ventilation = 0.0
            montant = decimal.Decimal(montant)
            ventilation = decimal.Decimal(ventilation)
            aventiler = montant - ventilation
            if aventiler > decimal.Decimal(0.0) :

                # M�morisation des prestations � ventiler
                if (IDfacture in dictFactures) == False :
                    dictFactures[IDfacture] = []
                dictFactures[IDfacture].append({"IDprestation" : IDprestation, "IDcompte_payeur" : IDcompte_payeur, "montant" : montant, "ventilation" : ventilation, "aventiler" : aventiler})

                # M�morisation des montants � ventiler pour chaque facture
                if (IDfacture in dictAventiler) == False :
                    dictAventiler[IDfacture] = decimal.Decimal(0.0)
                dictAventiler[IDfacture] += aventiler
                        
        # Sauvegarde des r�glements + ventilation
        listeSuppressionReglements = []
        for track in self.GetObjects() :

            # Ajouts et modifications
            if track.reglement == True :

                if track.IDfacture in dictAventiler :

                    # Recherche du payeur
                    IDpayeur = None
                    if track.IDcompte_payeur in dictPayeurs :
                        for dictPayeur in dictPayeurs[track.IDcompte_payeur] :
                            if dictPayeur["nom"] == track.prelevement_titulaire :
                                IDpayeur = dictPayeur["IDpayeur"]

                    # Si pas de payeur correspond au titulaire du compte trouv� :
                    if IDpayeur == None :
                        IDpayeur = DB.ReqInsert("payeurs", [("IDcompte_payeur", track.IDcompte_payeur), ("nom", track.prelevement_titulaire)])

                    # Recherche du montant du r�glement
                    montant = dictAventiler[track.IDfacture] # track.montant

                    # Cr�ation des donn�es � sauvegarder
                    listeDonnees = [
                        ("IDcompte_payeur", track.IDcompte_payeur),
                        ("date", date),
                        ("IDmode", IDmode),
                        ("IDemetteur", None),
                        ("numero_piece", None),
                        ("montant", float(montant)),
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
                    if track.IDfacture in dictFactures :
                        for dictFacture in dictFactures[track.IDfacture] :
                            listeDonnees = [
                                    ("IDreglement", track.IDreglement),
                                    ("IDcompte_payeur", track.IDcompte_payeur),
                                    ("IDprestation", dictFacture["IDprestation"]),
                                    ("montant", float(dictFacture["aventiler"])),
                                ]
                            IDventilation = DB.ReqInsert("ventilation", listeDonnees)
            
            # Suppression de r�glements et ventilation
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
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
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
        print("Test de la sauvegarde des reglements :")
        self.myOlv.SauvegardeReglements(date=datetime.date.today(), IDcompte=99)
        
        
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
