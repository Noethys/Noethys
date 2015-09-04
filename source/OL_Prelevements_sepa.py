#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import decimal
import GestionDB
import UTILS_Dates
import DLG_Saisie_prelevement
import DLG_Saisie_prelevement_sepa
import UTILS_Identification
import UTILS_Prelevements
import UTILS_Mandats
import UTILS_Historique
import wx.lib.dialogs as dialogs

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Titulaires

DICT_BANQUES = {}


class TrackManuelle():
    """ Simulation de track facture pour saisie manuelle de pr�l�vement """
    def __init__(self, IDfamille=None, libelle=u"", montant=0.0):
        self.IDfamille = IDfamille
        self.IDfacture = None
        self.numero = 0
        self.solde = -montant
        self.IDcompte_payeur = IDfamille
        self.libelle = libelle


class Track(object):
    def __init__(self, donnees, dictTitulaires):
        self.dictTitulaires = dictTitulaires
        self.IDprelevement = donnees["IDprelevement"]
        self.IDlot = donnees["IDlot"]
        self.IDfamille = donnees["IDfamille"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]

        self.prelevement_banque = donnees["prelevement_banque"]
        self.prelevement_iban =  donnees["prelevement_iban"]
        self.prelevement_bic =  donnees["prelevement_bic"]
        
        self.IDmandat = donnees["IDmandat"]
        self.prelevement_reference_mandat =  donnees["prelevement_reference_mandat"]
        self.prelevement_date_mandat =  donnees["prelevement_date_mandat"]
        self.sequence = donnees["sequence"]
        
        self.titulaire = donnees["titulaire"]
        self.type = donnees["type"]
        self.IDfacture = donnees["IDfacture"]
        self.libelle = donnees["libelle"]
        self.montant = donnees["montant"]
        self.statut = donnees["statut"]
        
##        self.MAJnomBanque()
        
        self.titulaires = ""
        self.InitNomsTitulaires() 
        
        self.IDreglement = donnees["IDreglement"]
        if self.IDreglement == None :
            self.reglement = False
        else :
            self.reglement = True
        self.dateReglement = donnees["dateReglement"]
        self.IDdepot = donnees["IDdepot"]

        self.etat = donnees["etat"] # "ajout", "modif"
    
    def InitNomsTitulaires(self):
        if self.IDfamille != None :
            self.titulaires = self.dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
    
##    def MAJnomBanque(self):
##        if DICT_BANQUES.has_key(self.prelevement_banque) :
##            self.nomBanque = DICT_BANQUES[self.prelevement_banque]
##        else :
##            self.nomBanque = u""




def GetTracks(IDlot=None):
    """ R�cup�ration des donn�es """
    dictTitulaires = UTILS_Titulaires.GetTitulaires() 
    if IDlot == None :
        return []
    DB = GestionDB.DB()
    req = """SELECT 
    prelevements.IDprelevement, IDlot, prelevements.IDfamille, 
    prelevement_banque, prelevement_iban, prelevement_bic, 
    prelevements.IDmandat, prelevement_reference_mandat, prelevement_date_mandat,
    prelevements.sequence,
    titulaire, type, IDfacture, libelle, prelevements.montant, statut,
    banques.nom,
    reglements.IDreglement, reglements.date, reglements.IDdepot,
    comptes_payeurs.IDcompte_payeur
    FROM prelevements
    LEFT JOIN banques ON banques.IDbanque = prelevements.prelevement_banque
    LEFT JOIN reglements ON reglements.IDprelevement = prelevements.IDprelevement
    LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = prelevements.IDfamille
    WHERE IDlot=%d
    ;""" % IDlot
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    listeListeView = []
    for IDprelevement, IDlot, IDfamille, prelevement_banque, prelevement_iban, prelevement_bic, IDmandat, prelevement_reference_mandat, prelevement_date_mandat, sequence, titulaire, type_prelevement, IDfacture, libelle, montant, statut, nomBanque, IDreglement, dateReglement, IDdepot, IDcompte_payeur in listeDonnees :
        dictTemp = {
            "IDprelevement" : IDprelevement, "IDlot" : IDlot, "IDfamille" : IDfamille, 
            "prelevement_banque" : prelevement_banque, "prelevement_iban" : prelevement_iban, "prelevement_bic" : prelevement_bic, 
            "IDmandat" : IDmandat, "prelevement_reference_mandat" : prelevement_reference_mandat, "prelevement_date_mandat" : prelevement_date_mandat,
            "sequence" : sequence, "titulaire" : titulaire, "type" : type_prelevement, "IDfacture" : IDfacture, 
            "libelle" : libelle, "montant" : montant, "statut" : statut, "IDlot" : IDlot, "IDmandat" : IDmandat, "nomBanque" : nomBanque, "etat" : None,
            "IDreglement" : IDreglement, "dateReglement" : dateReglement, "IDdepot" : IDdepot, "IDcompte_payeur" : IDcompte_payeur,
            }
        track = Track(dictTemp, dictTitulaires)
        listeListeView.append(track)
    return listeListeView



##def GetMandats():
##    """ R�cup�ration des mandats """
##    DB = GestionDB.DB()
##    req = """SELECT IDmandat, IDfamille, rum, type, date, IDbanque, mandats.IDindividu, individu_nom, iban, bic, sequence, individus.nom, individus.prenom
##    FROM mandats
##    LEFT JOIN individus ON individus.IDindividu = mandats.IDindividu
##    ORDER BY date;"""
##    DB.ExecuterReq(req)
##    listeDonnees = DB.ResultatReq()
##    DB.Close()
##    dictMandats = {}
##    for IDmandat, IDfamille, rum, type, date, IDbanque, IDindividu, individu_nom, iban, bic, sequence, nomIndividu, prenomIndividu in listeDonnees :
##        if dictMandats.has_key(IDfamille) == False :
##            dictMandats[IDfamille] = []
##        dictMandats[IDfamille].append({
##            "IDmandat" : IDmandat, "IDfamille" : IDfamille, "rum" : rum, "type" : type, "date" : date, "IDbanque" : IDbanque, 
##            "IDindividu" : IDindividu, "individu_nom" : individu_nom, "iban" : iban, "bic" : bic, "sequence" : sequence, 
##            "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu,       
##            })
##    return dictMandats




    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.IDlot = kwds.pop("IDlot", None)
        self.typePrelevement = kwds.pop("typePrelevement", "sepa")
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.tracks = []
        self.numColonneTri = 2
        self.ordreAscendant = True
        self.listeSuppressions = []
        self.dictBanques = {}
        self.reglement_auto = False
        # Initialisation du listCtrl
##        self.InitBanques() 
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier()

    def InitModel(self, tracks=None, IDcompte=None, IDmode=None):
##        self.InitBanques() 
        if tracks != None :
            self.tracks = tracks
        self.donnees = self.tracks
        
##    def InitBanques(self):
##        global DICT_BANQUES
##        DICT_BANQUES = self.GetNomsBanques()
    
##    def GetNomsBanques(self):
##        DB = GestionDB.DB()
##        req = """SELECT IDbanque, nom
##        FROM banques;"""
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close()
##        dictBanques = {}
##        for IDbanque, nom in listeDonnees :
##            dictBanques[IDbanque] = nom
##        return dictBanques
    
##    def MAJnomsBanquesTracks(self):
##        self.InitBanques() 
##        for track in self.GetObjects() :
##            track.MAJnomBanque()
##            self.RefreshObject(track)
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        # Image list
        self.imgValide = self.AddNamedImages("valide", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        self.imgRefus = self.AddNamedImages("refus", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.imgAttente = self.AddNamedImages("attente", wx.Bitmap("Images/16x16/Attente.png", wx.BITMAP_TYPE_PNG))
        self.imgInterdit = self.AddNamedImages("interdit", wx.Bitmap("Images/16x16/Interdit2.png", wx.BITMAP_TYPE_PNG))

        def GetImageStatut(track):
            if track.statut == "valide" : return self.imgValide
            if track.statut == "refus" : return self.imgRefus
            if track.statut == "attente" : return self.imgAttente

        def GetImageReglement(track):
            if track.reglement == False :
                return self.imgRefus
            else :
                return self.imgValide

        def FormateDateCourt(dateDD):
            if dateDD == None :
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

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDprelevement", typeDonnee="entier"),
            ColumnDefn(_(u"Famille"), 'left', 230, "titulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Type"), 'left', 70, "type", typeDonnee="texte", stringConverter=FormateType),
            ColumnDefn(_(u"Libell�"), 'left', 110, "libelle", typeDonnee="texte"),
##            ColumnDefn(_(u"Banque"), 'left', 120, "nomBanque"),
            ColumnDefn(_(u"Montant"), 'right', 70, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Statut"), 'left', 80, "statut", typeDonnee="texte", stringConverter=FormateStatut, imageGetter=GetImageStatut),
            ColumnDefn(_(u"R�glement"), 'left', 70, "reglement", typeDonnee="texte", stringConverter=FormateReglement, imageGetter=GetImageReglement),
            ColumnDefn(_(u"S�quence"), 'left', 70, "sequence", typeDonnee="texte"),
            ColumnDefn(_(u"IBAN"), 'left', 190, "prelevement_iban", typeDonnee="texte"),
            ColumnDefn(_(u"BIC"), 'left', 100, "prelevement_bic", typeDonnee="texte"),
##            ColumnDefn(_(u"Etab."), 'left', 50, "prelevement_etab"),
##            ColumnDefn(_(u"Guich."), 'left', 50, "prelevement_guichet"),
##            ColumnDefn(_(u"Compte"), 'left', 90, "prelevement_numero"),
##            ColumnDefn(_(u"Cl�"), 'left', 30, "prelevement_cle"),
##            ColumnDefn(_(u"Banque"), 'left', 130, "nomBanque"),
            ColumnDefn(_(u"Titulaire du compte"), 'left', 160, "titulaire", typeDonnee="texte"),
            ColumnDefn(_(u"Ref. mandat"), 'left', 90, "prelevement_reference_mandat", typeDonnee="texte"),
            ColumnDefn(_(u"Date mandat"), 'left', 100, "prelevement_date_mandat", typeDonnee="date", stringConverter=FormateDateCourt),
            ]
        

        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(1)
        self.SetEmptyListMsg(_(u"Aucun pr�l�vement"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
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
            ID = self.Selection()[0].IDprelevement
                
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Saisie de factures
        item = wx.MenuItem(menuPop, 11, _(u"Ajouter une ou plusieurs factures"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Saisie_factures, id=11)

        # Item Saisie manuelle
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter un pr�l�vement manuel"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Saisie_manuelle, id=10)

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
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
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
        # R�cup�re l'intitul� du compte
        txtIntro = self.GetParent().GetLabelParametres()
        # R�cup�re le total
        total = 0.0
        for track in self.donnees :
            total += track.montant
        txtTotal = self.GetTexteTotaux().replace("<B>", "").replace("</B>", "")
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des pr�l�vements"), intro=txtIntro, total=txtTotal, format="A", orientation=wx.LANDSCAPE)
        return prt
        
    def Apercu(self, event=None):
        self.Impression().Preview()

    def Imprimer(self, event=None):
        self.Impression().Print()

    def ExportTexte(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des pr�l�vements"))
        
    def ExportExcel(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des pr�l�vements"))
        
    def Saisie_factures(self, event=None):
        """ Saisie de factures """
        if self.GetParent().GetVerrouillage() == True :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette action car le lot de pr�l�vement est verrouill� !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        import DLG_Prelevements_factures
        dlg = DLG_Prelevements_factures.Dialog(self, IDlot=self.IDlot)
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
        
        # MAJ de la liste affich�e
        dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        listeNewTracks = []
        listeMandatsNonValides = []
        for track in tracks :
            
            # Recherche un mandat valide pour la famille
            IDmandat = mandats.RechercheMandatFamille(track.IDfamille) 
            
            if IDmandat == None :
                if dictTitulaires.has_key(track.IDfamille) :
                    nomTitulaires = dictTitulaires[track.IDfamille]["titulairesSansCivilite"]
                else :
                    nomTitulaires = _(u"Titulaires inconnus")
                listeMandatsNonValides.append(_(u"Famille %s (ID%d)") % (nomTitulaires, track.IDfamille))
                    
            else :
                # R�cup�re les donn�es du mandat
                dictMandat = mandats.GetDictMandat(IDmandat) 
                
                IDbanque = dictMandat["IDbanque"]
                iban = dictMandat["iban"]
                bic = dictMandat["bic"]
                IDmandat = dictMandat["IDmandat"]
                mandat_rum = dictMandat["rum"]
                mandat_date = dictMandat["date"]
                titulaire = dictMandat["titulaire"]
                
                # Recherche de la s�quence
                analyse = mandats.AnalyseMandat(IDmandat)
                sequence = analyse["prochaineSequence"]
                
                # M�morisation du track
                if track.IDfacture != None :
                    typeTrack = "facture"
                    libelle = _(u"FACT%06d") % track.numero
                else :
                    typeTrack = "manuel"
                    libelle = track.libelle
                    
                dictTemp = {
                    "IDprelevement" : None, "IDfamille" : track.IDfamille, 
                    "prelevement_banque" : IDbanque, "prelevement_iban" : iban, "prelevement_bic" : bic, 
                    "IDmandat" : IDmandat, "prelevement_reference_mandat" : mandat_rum, "prelevement_date_mandat" : mandat_date,
                    "titulaire" : titulaire, "type" : typeTrack, "IDfacture" : track.IDfacture, "sequence" : sequence,
                    "libelle" : libelle, "montant" : -track.solde, "statut" : "attente", "IDlot" : self.IDlot, "nomBanque" : "", "etat" : "ajout", "IDreglement" : None, "dateReglement" : None, 
                    "IDdepot" : None, "IDcompte_payeur" : track.IDcompte_payeur, 
                    }
                
                if track.IDfacture not in listeFacturesPresentes :
                    listeNewTracks.append(Track(dictTemp, dictTitulaires))
        
        if len(listeMandatsNonValides) > 0 :
            message1 = _(u"Les pr�l�vements suivants n'ont pas �t� int�gr�s car les mandats SEPA des familles sont indisponibles ou non valides :")
            message2 = "\n".join(listeMandatsNonValides)
            dlg = dialogs.MultiMessageDialog(self, message1, caption=_(u"Avertissement"), msg2=message2, style = wx.ICON_EXCLAMATION |wx.OK, icon=None, btnLabels={wx.ID_OK : _(u"Ok")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 

        self.AddObjects(listeNewTracks)
        self.MAJtotaux()         
        
    def Saisie_manuelle(self, event=None):
        """ Saisie manuelle """
##        dictTitulaires = UTILS_Titulaires.GetTitulaires() 
##        dictTemp = {
##            "IDprelevement" : None, "IDfamille" : None, "prelevement_etab" : "", "prelevement_guichet" : "", "prelevement_numero" : "", 
##            "prelevement_banque" : "", "prelevement_cle" : "", "prelevement_iban" : "", "prelevement_bic" : "", 
##            "prelevement_reference_mandat" : "", "prelevement_date_mandat" : None,
##            "titulaire" : "", "type" : "manuel", "IDfacture" : None, 
##            "libelle" : "", "montant" : 0.00, "statut" : "attente", "IDlot" : self.IDlot, "nomBanque" : "", "etat" : "ajout",
##            "IDreglement" : None, "dateReglement" : None, "IDdepot" : None, "IDcompte_payeur" : None,
##            }
##        track = Track(dictTemp, dictTitulaires)
##        dlg = DLG_Saisie_prelevement.Dialog(self, track=track)      
##        if dlg.ShowModal() == wx.ID_OK:
##            track = dlg.GetTrack()
##            self.AddObject(track)
##            self.MAJtotaux() 
##        dlg.Destroy() 

        if self.GetParent().GetVerrouillage() == True :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette action car le lot de pr�l�vement est verrouill� !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande les caract�ristiques du pr�l�vement manuel
        import DLG_Saisie_prelevement_manuel
        dlg = DLG_Saisie_prelevement_manuel.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            IDfamille = dlg.GetIDfamille() 
            libelle = dlg.GetLibelle()
            montant = dlg.GetMontant()  
            dlg.Destroy()
        else :
            dlg.Destroy()
            return
        
        # Simule un track de facture pour cr�er plus facilement le track pr�l�vement
        track = TrackManuelle(IDfamille, libelle, montant)
        self.AjoutFactures([track,])
        
    def Modifier(self, event=None):
        if self.GetParent().GetVerrouillage() == True :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette action car le lot de pr�l�vement est verrouill� !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun pr�l�vement � modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        if self.typePrelevement == "sepa" :
            MODULE = DLG_Saisie_prelevement_sepa
        else :
            MODULE = DLG_Saisie_prelevement
        dlg = MODULE.Dialog(self, track=track, activeMontant=True)      
        if dlg.ShowModal() == wx.ID_OK:
            if track.etat != "ajout" :
                track.etat = "modif"
            self.RefreshObject(track)
            self.MAJtotaux() 
        dlg.Destroy() 
##        self.MAJnomsBanquesTracks()

    def Supprimer(self, event=None):
        if self.GetParent().GetVerrouillage() == True :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas effectuer cette action car le lot de pr�l�vement est verrouill� !"), _(u"Verrouillage"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun pr�l�vement � retirer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if len(self.GetTracksCoches()) > 0 :
            # Suppression multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment retirer les %d pr�l�vements coch�s ?") % len(listeSelections), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        else :
            # Suppression unique
            listeSelections = self.Selection()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment retirer le pr�l�vement s�lectionn� ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        # V�rifie que le r�glement n'est pas d�j� d�pos� en banque
        listeDepots = []
        for track in listeSelections :
            if track.IDdepot != None :
                listeDepots.append(track)
        if len(listeDepots) > 0 :
            dlg = wx.MessageDialog(self, _(u"Suppression interdite car %d pr�l�vement(s) de la s�lection ont d�j� un r�glement attribu� � un d�p�t de r�glement !") % len(listeDepots), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
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
                track.statut = statut
                
                # R�glement automatique
                if self.reglement_auto == True and statut == "valide" : #and track.type != "manuel" :
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
            dlg = wx.MessageDialog(self, _(u"Notez que Noethys n'a pas proc�d� changement de statut de %d pr�l�vement(s) car le r�glement correspondant appartient d�j� � un d�p�t de r�glement !") % len(listeDepots), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return


    def SetRegle(self, etat=False) :
        listeAnomalies = []
        listeDepots = []
        for track in self.GetObjects() :                
            if self.IsChecked(track) : #and track.type != "manuel" :
    
                if etat == True :
                    # Si on veut r�gler
                    if track.statut in ("valide", "attente") :
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
            dlg = wx.MessageDialog(self, _(u"Notez que Noethys n'a pas proc�d� au r�glement de %d pr�l�vement(s) en raison de leur statut 'Refus'.") % len(listeAnomalies), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(listeDepots) > 0 :
            dlg = wx.MessageDialog(self, _(u"Notez que Noethys n'a pas proc�d� � la suppression de %d pr�l�vement(s) car le r�glement correspondant appartient d�j� � un d�p�t de r�glement !") % len(listeDepots), _(u"Remarque"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.MAJtotaux() 

    def GetLabelListe(self):
        """ R�cup�re le nombre de pr�l�vements et le montant total de la liste """
        nbre = 0
        montant = 0.0
        for track in self.GetObjects() :
            nbre += 1
            montant += track.montant
        # Label de staticbox
        if nbre > 1 :
            texte = _(u"pr�l�vements")
        else :
            texte = _(u"pr�l�vement")
        label = u"%d %s (%.2f %s)" % (nbre, texte, montant, SYMBOLE)
        return label          

    def MAJtotaux(self):
        """ Cr�� le texte infos avec les stats du lot """
        if self.GetParent().GetName() != "DLG_Saisie_prelevement_lot" :
            return
        # Label de staticbox
        texte = self.GetTexteTotaux()
        self.GetParent().ctrl_totaux.SetLabel(texte)
        self.GetParent().box_prelevements_staticbox.SetLabel(self.GetLabelListe())

    def GetTexteTotaux(self):
        # R�cup�ration des chiffres
        nbreTotal = 0
        montantTotal = 0.0
        dictDetails = {}
        for track in self.GetObjects() :
            nbreTotal += 1
            montantTotal += track.montant
            # Regroupement par statut
            if dictDetails.has_key(track.statut) == False :
                dictDetails[track.statut] = {"nbre" : 0, "montant" : 0.0}
            dictDetails[track.statut]["nbre"] += 1
            dictDetails[track.statut]["montant"] += track.montant
            # Regroupement par r�glemennt
            if track.reglement == True :
                reglement = "regle"
            else :
                reglement = "pasregle"
            if dictDetails.has_key(reglement) == False :
                dictDetails[reglement] = {"nbre" : 0, "montant" : 0.0}
            dictDetails[reglement]["nbre"] += 1
            dictDetails[reglement]["montant"] += track.montant
            
        # Cr�ation du texte
        if nbreTotal == 0 :
            texte = _(u"<B>Aucun pr�l�vement.   </B>")
        elif nbreTotal == 1 :
            texte = _(u"<B>%d pr�l�vement (%.2f %s) : </B>") % (nbreTotal, montantTotal, SYMBOLE)
        else :
            texte = _(u"<B>%d pr�l�vements (%.2f %s) : </B>") % (nbreTotal, montantTotal, SYMBOLE)
        
        for key in ("attente", "valide", "refus", "regle", "pasregle") :
            if dictDetails.has_key(key) :
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
                ("prelevement_banque", track.prelevement_banque),
                ("prelevement_iban", track.prelevement_iban),
                ("prelevement_bic", track.prelevement_bic),
                ("prelevement_reference_mandat", track.prelevement_reference_mandat),
                ("prelevement_date_mandat", track.prelevement_date_mandat),
                ("titulaire", track.titulaire),
                ("type", track.type),
                ("IDfacture", track.IDfacture),
                ("libelle", track.libelle),
                ("montant", track.montant),
                ("statut", track.statut),
                ("IDmandat", track.IDmandat),
                ("sequence", track.sequence),
                ]

            # Ajout
            if track.etat == "ajout" :
                track.IDprelevement = DB.ReqInsert("prelevements", listeDonnees)
                self.RefreshObject(track)
            
            # Modification
            if track.etat == "modif" :
                DB.ReqMAJ("prelevements", listeDonnees, "IDprelevement", track.IDprelevement)
        
        # Suppressions
        for track in self.listeSuppressions :
            if track.IDprelevement != None :
                DB.ReqDEL("prelevements", "IDprelevement", track.IDprelevement)
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
            if dictPayeurs.has_key(IDcompte_payeur) == False :
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
                        
        # Sauvegarde des r�glements + ventilation
        listeSuppressionReglements = []
        listeHistoriqueAjouts = []
        for track in self.GetObjects() :

            # Ajouts et modifications
            if track.reglement == True :
                
                # Recherche du payeur
                IDpayeur = None
                if dictPayeurs.has_key(track.IDcompte_payeur) :
                    for dictPayeur in dictPayeurs[track.IDcompte_payeur] :
                        if dictPayeur["nom"] == track.titulaire :
                            IDpayeur = dictPayeur["IDpayeur"]
                
                # Si pas de payeur correspond au titulaire du compte trouv� :
                if IDpayeur == None :
                    IDpayeur = DB.ReqInsert("payeurs", [("IDcompte_payeur", track.IDcompte_payeur), ("nom", track.titulaire)])
                    
                # Cr�ation des donn�es � sauvegarder
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
                    ("IDprelevement", track.IDprelevement),
                    ]
                

                # Ajout
                if track.IDreglement == None :
                    track.IDreglement = DB.ReqInsert("reglements", listeDonnees)
                    listeHistoriqueAjouts.append(self.MemoriseReglementHistorique(mode="saisie", IDfamille=track.IDfamille, IDreglement=track.IDreglement, montant=track.montant))
                    
                # Modification
                else:
                    DB.ReqMAJ("reglements", listeDonnees, "IDreglement", track.IDreglement)
                    #listeHistoriqueAjouts.append(self.MemoriseReglementHistorique(mode="modification", IDfamille=track.IDfamille, IDreglement=track.IDreglement, montant=track.montant))
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
            
            # Suppression de r�glements et ventilation
            else :

                if track.IDreglement != None :
                    DB.ReqDEL("reglements", "IDreglement", track.IDreglement)
                    DB.ReqDEL("ventilation", "IDreglement", track.IDreglement)
                    listeHistoriqueAjouts.append(self.MemoriseReglementHistorique(mode="suppression", IDfamille=track.IDfamille, IDreglement=track.IDreglement, montant=track.montant))
            
            # MAJ du track
            self.RefreshObject(track)
            
            # Sauvegarde dans historique
            
        DB.Close() 

        # Sauvegarde dans historique
        UTILS_Historique.InsertActions(listeHistoriqueAjouts)
    
    def MemoriseReglementHistorique(self, mode="saisie", IDfamille=None, IDreglement=None, montant=0.0):
        """ M�morisation d'un r�glement dans l'historique """
        # Choix du mode
        if mode == "saisie" :
            IDcategorie = 6
            categorie = _(u"Saisie")
        if mode == "modification" :
            IDcategorie = 7
            categorie = "Modification"
        if mode == "suppression" : 
            IDcategorie = 8
            categorie = "Suppression"
            
        montantStr = u"%.2f %s" % (montant, SYMBOLE)
        dictAction = {
            "IDfamille" : IDfamille,
            "IDcategorie" : IDcategorie, 
            "action" : _(u"%s du r�glement ID%d : %s pay�s par pr�l�vement automatique SEPA") % (categorie, IDreglement, montantStr),
            }
        return dictAction

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un pr�l�vement..."))
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
        tracks = GetTracks(IDlot=1)
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
