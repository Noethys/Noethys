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
import UTILS_Titulaires
import UTILS_Utilisateurs
from UTILS_Decimal import FloatToDecimal as FloatToDecimal

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

# ----------------------------------------------------------------------------------------------------------------------------------------

def Importation(onlyNonVentiles=True, IDcompte_payeur=None):
    DB = GestionDB.DB()
    
    if IDcompte_payeur != None :
        conditionCompte = "WHERE IDcompte_payeur=%d" % IDcompte_payeur
    else:
        conditionCompte = ""
    
    # R�cup�re les comptes payeurs
    req = """SELECT IDcompte_payeur, IDfamille
    FROM comptes_payeurs
    %s
    ORDER BY IDcompte_payeur
    ;""" % conditionCompte
    DB.ExecuterReq(req)
    listeComptes = DB.ResultatReq()
    
    # R�cup�re la ventilation
    req = """SELECT IDcompte_payeur, SUM(montant) AS total_ventilations
    FROM ventilation
    %s
    GROUP BY IDcompte_payeur
    ORDER BY IDcompte_payeur
    ;""" % conditionCompte
    DB.ExecuterReq(req)
    listeVentilations = DB.ResultatReq()
    dictVentilations = {}
    for IDcompte_payeur, total_ventilations in listeVentilations :
        dictVentilations[IDcompte_payeur] = total_ventilations
    
    # R�cup�re les prestations
    req = """SELECT IDcompte_payeur, SUM(montant) AS total_prestations
    FROM prestations
    %s
    GROUP BY IDcompte_payeur
    ORDER BY IDcompte_payeur
    ;""" % conditionCompte
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq()
    dictPrestations = {}
    for IDcompte_payeur, total_prestations in listePrestations :
        dictPrestations[IDcompte_payeur] = total_prestations
        
    # R�cup�re les r�glements
    req = """SELECT IDcompte_payeur, SUM(montant) AS total_reglements
    FROM reglements
    %s
    GROUP BY IDcompte_payeur
    ORDER BY IDcompte_payeur
    ;""" % conditionCompte
    DB.ExecuterReq(req)
    listeReglements = DB.ResultatReq()
    dictReglements = {}
    for IDcompte_payeur, total_reglements in listeReglements :
        dictReglements[IDcompte_payeur] = total_reglements
    
    DB.Close()
    
    # R�cup�ration des titulaires de familles
    dictTitulaires = UTILS_Titulaires.GetTitulaires() 
    
    # Traitement des donn�es
    listeListeView = []
    for IDcompte_payeur, IDfamille in listeComptes :
        if dictVentilations.has_key(IDcompte_payeur) :
            total_ventilations = FloatToDecimal(dictVentilations[IDcompte_payeur])
        else:
            total_ventilations = FloatToDecimal(0.0)
        if dictPrestations.has_key(IDcompte_payeur) :
            total_prestations = FloatToDecimal(dictPrestations[IDcompte_payeur])
        else:
            total_prestations = FloatToDecimal(0.0)
        if dictReglements.has_key(IDcompte_payeur) :
            total_reglements = FloatToDecimal(dictReglements[IDcompte_payeur])
        else:
            total_reglements = FloatToDecimal(0.0)
        item = (IDcompte_payeur, IDfamille, total_ventilations, total_reglements, total_prestations)
        track = Track(dictTitulaires, item)
        
        if onlyNonVentiles == True :
            # Afficher seulement ceux qui sont mal ventil�s
            if track.reste_a_ventiler > FloatToDecimal(0.0) :
                listeListeView.append(track)
        else:
            # Afficher toute la liste
            listeListeView.append(track)

    return listeListeView
                
                
class Track(object):
    def __init__(self, dictTitulaires, donnees):
        self.IDcompte_payeur = donnees[0]
        self.IDfamille = donnees[1]
        self.total_ventilations = donnees[2]
        self.total_reglements = donnees[3]
        self.total_prestations = donnees[4]
        if dictTitulaires.has_key(self.IDfamille) :
            self.nomsTitulaires =  dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
        else:
            self.nomsTitulaires = _(u"Sans titulaires")
        
        self.solde = self.total_reglements - self.total_prestations
        self.total_a_ventiler = min(self.total_reglements, self.total_prestations)
        self.reste_a_ventiler = self.total_a_ventiler - self.total_ventilations

# ----------------------------------------------------------------------------------------------------------------------------------------

def VentilationAuto(IDcompte_payeur=None, IDreglement=None):
    """ Ventilation auto de tous les r�glements d'un compte payeur ou d'un r�glement sp�cifique """
    DB = GestionDB.DB()

    if IDreglement != None :
        conditionReglement = "AND IDreglement=%d" % IDreglement
    else :
        conditionReglement = ""

    # R�cup�re la ventilation
    req = """SELECT IDventilation, IDreglement, IDprestation, montant
    FROM ventilation
    WHERE IDcompte_payeur=%d;""" % IDcompte_payeur
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictVentilations = {}
    dictVentilationsReglement = {}
    dictVentilationsPrestation = {}
    for IDventilation, IDreglement, IDprestation, montant in listeDonnees :
        dictVentilations[IDventilation] = {"IDreglement" : IDreglement, "IDprestation" : IDprestation, "montant" : FloatToDecimal(montant)}
        
        if dictVentilationsReglement.has_key(IDreglement) == False :
            dictVentilationsReglement[IDreglement] = []
        dictVentilationsReglement[IDreglement].append(IDventilation)

        if dictVentilationsPrestation.has_key(IDprestation) == False :
            dictVentilationsPrestation[IDprestation] = []
        dictVentilationsPrestation[IDprestation].append(IDventilation)
    
    # R�cup�re les prestations
    req = """SELECT IDprestation, date, montant
    FROM prestations
    WHERE IDcompte_payeur=%d
    ORDER BY date;""" % IDcompte_payeur
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    listePrestations = []
    for IDprestation, date, montant in listeDonnees :
        listePrestations.append({"IDprestation" : IDprestation, "date" : date, "montant" : FloatToDecimal(montant)})

    # V�rifie qu'il n'y a pas de prestations n�gatives
    for dictPrestation in listePrestations : 
        IDprestation = dictPrestation["IDprestation"]
                        
        montantVentilation = FloatToDecimal(0.0)
        if dictVentilationsPrestation.has_key(IDprestation) :
            for IDventilation in dictVentilationsPrestation[IDprestation] :
                montantVentilation += dictVentilations[IDventilation]["montant"]
        
        ResteAVentiler = dictPrestation["montant"] - montantVentilation
        if ResteAVentiler < FloatToDecimal(0.0) :
            dlg = wx.MessageDialog(None, _(u"Ventilation automatique impossible !\n\nLa ventilation automatique n'est pas compatible avec les prestations comportant un montant n�gatif ! Vous devez donc effectuer une ventilation manuelle."), _(u"Information"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

    # R�cup�re les r�glements
    req = """SELECT IDreglement, date, montant
    FROM reglements
    WHERE IDcompte_payeur=%d %s
    ORDER BY date;""" % (IDcompte_payeur, conditionReglement)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    listeReglements = []
    for IDreglement, date, montant in listeDonnees :
        listeReglements.append({"IDreglement" : IDreglement, "date" : date, "montant" : FloatToDecimal(montant)})
    
    # V�rification de la ventilation de chaque r�glement
    listeReglementsAVentiler = []
    for dictReglement in listeReglements :
        IDreglement = dictReglement["IDreglement"]
        
        # Recherche s'il reste du cr�dit � ventiler dans ce r�glement
        montantVentilation = FloatToDecimal(0.0)
        if dictVentilationsReglement.has_key(IDreglement) :
            for IDventilation in dictVentilationsReglement[IDreglement] :
                montantVentilation += dictVentilations[IDventilation]["montant"]
                
        credit = dictReglement["montant"] - montantVentilation
        
        if credit > FloatToDecimal(0.0) :
    
            # Recherche s'il reste des prestations � ventiler pour cette famille
            listePrestationsAVentiler = []
            for dictPrestation in listePrestations : 
                IDprestation = dictPrestation["IDprestation"]
                                
                montantVentilation = FloatToDecimal(0.0)
                if dictVentilationsPrestation.has_key(IDprestation) :
                    for IDventilation in dictVentilationsPrestation[IDprestation] :
                        montantVentilation += dictVentilations[IDventilation]["montant"]
                
                ResteAVentiler = dictPrestation["montant"] - montantVentilation
                if ResteAVentiler > FloatToDecimal(0.0) :
                    
                    # Calcul du montant qui peut �tre ventil�
                    montant = ResteAVentiler
                    if credit < montant :
                        montant = credit
                    
                    if montant > FloatToDecimal(0.0) :
                        
                        # Modification d'une ventilation existante
                        ventilationTrouvee = False
                        if dictVentilationsPrestation.has_key(IDprestation) :
                            for IDventilation in dictVentilationsPrestation[IDprestation] :
                                if dictVentilations[IDventilation]["IDreglement"] == IDreglement :
                                    nouveauMontant = montant + montantVentilation
                                    
                                    DB.ReqMAJ("ventilation", [("montant", float(nouveauMontant)),], "IDventilation", IDventilation)
                                    
                                    # M�morisation du nouveau montant
                                    dictVentilations[IDventilation]["montant"] = nouveauMontant
                                    ResteAVentiler -= montant
                                    credit -= montant
                                    ventilationTrouvee = True
                                    
                        
                        # Cr�ation d'une ventilation
                        if ventilationTrouvee == False :
                            listeDonnees = [    
                                    ("IDreglement", IDreglement),
                                    ("IDcompte_payeur", IDcompte_payeur),
                                    ("IDprestation", IDprestation),
                                    ("montant", float(montant)),
                                ]
                            IDventilation = DB.ReqInsert("ventilation", listeDonnees)
                            
                            # M�morisation de la nouvelle ventilation
                            dictVentilations[IDventilation] = {"IDreglement" : IDreglement, "IDprestation" : IDprestation, "montant" : montant}
                            if dictVentilationsReglement.has_key(IDreglement) == False :
                                dictVentilationsReglement[IDreglement] = []
                            dictVentilationsReglement[IDreglement].append(IDventilation)
                            if dictVentilationsPrestation.has_key(IDprestation) == False :
                                dictVentilationsPrestation[IDprestation] = []
                            dictVentilationsPrestation[IDprestation].append(IDventilation)
                            ResteAVentiler -= montant
                            credit -= montant
    
    DB.Close()
    return True
    

# ----------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.onlyNonVentiles = kwds.pop("onlyNonVentiles", False)
        self.IDcompte_payeur = kwds.pop("IDcompte_payeur", None)
        self.tracks = kwds.pop("tracks", None)
        self.colonneTri = kwds.pop("colonneTri", None)
        self.sensTri = kwds.pop("sensTri", True)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.OuvrirFicheFamille(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        listeID = None
        
        if self.tracks == None :
            listeListeView = Importation(self.onlyNonVentiles, self.IDcompte_payeur)
        else:
            listeListeView = self.tracks
        
##        for item in listeDonnees :
##            valide = True
##            if listeID != None :
##                if item[0] not in listeID :
##                    valide = False
##            if valide == True :
##                track = Track(item)
##                listeListeView.append(track)
##                if self.selectionID == item[0] :
##                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        self.imgVentilation = self.AddNamedImages("ventilation", wx.Bitmap("Images/16x16/Attention.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageVentilation(track):
            if track.reste_a_ventiler > FloatToDecimal(0.0) :
                return self.imgVentilation

        def FormateMontant(montant):
            if montant == None or montant == 0.0 or montant == FloatToDecimal(0.0) : 
                return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateSolde(montant):
            if montant == None or montant == 0.0 or montant == FloatToDecimal(0.0) : 
                return u""
            if montant >= decimal.Decimal(str("0.0")) :
                return u"+ %.2f %s" % (montant, SYMBOLE)
            else:
                return u"- %.2f %s" % (-montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(_(u"IDfamille"), "left", 0, "IDfamille", typeDonnee="entier"),
            ColumnDefn(_(u"Famille"), 'left', 250, "nomsTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Solde"), 'right', 80, "solde", typeDonnee="montant", stringConverter=FormateSolde),
            ColumnDefn(_(u"Prestations"), 'right', 80, "total_prestations", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"R�glements"), 'right', 80, "total_reglements", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Total ventil�"), 'right', 80, "total_ventilations", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"A ventiler"), 'right', 80, "reste_a_ventiler", typeDonnee="montant", stringConverter=FormateMontant, imageGetter=GetImageVentilation),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucun probl�me de ventilation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        if self.colonneTri == None :
            self.SortBy(1, self.sensTri)
        else:
            self.SortBy(self.colonneTri, self.sensTri)
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
        # S�lection d'un item
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

        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Ouverture fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)
        
        menuPop.AppendSeparator()
        
        # Item Ventilation Automatique
        sousMenuVentilation = wx.Menu()
        
        item = wx.MenuItem(sousMenuVentilation, 201, _(u"Uniquement la ligne s�lectionn�e"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Magique.png", wx.BITMAP_TYPE_PNG))
        sousMenuVentilation.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.VentilationAuto, id=201)
        if noSelection == True : item.Enable(False)

        item = wx.MenuItem(sousMenuVentilation, 202, _(u"Uniquement les lignes coch�es"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Magique.png", wx.BITMAP_TYPE_PNG))
        sousMenuVentilation.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.VentilationAuto, id=202)
        if len(self.GetTracksCoches()) == 0 : item.Enable(False)

        item = wx.MenuItem(sousMenuVentilation, 203, _(u"Toutes les lignes"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Magique.png", wx.BITMAP_TYPE_PNG))
        sousMenuVentilation.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.VentilationAuto, id=203)

        menuPop.AppendMenu(wx.NewId(), _(u"Ventilation automatique"), sousMenuVentilation)
        
        menuPop.AppendSeparator()

        # Item Tout cocher
        item = wx.MenuItem(menuPop, 70, _(u"Tout cocher"))
        bmp = wx.Bitmap("Images/16x16/Cocher.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheTout, id=70)

        # Item Tout d�cocher
        item = wx.MenuItem(menuPop, 80, _(u"Tout d�cocher"))
        bmp = wx.Bitmap("Images/16x16/Decocher.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheRien, id=80)

        menuPop.AppendSeparator()

        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des soldes"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des soldes"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune fiche famille � ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = self.Selection()[0].IDfamille
        import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            pass
        dlg.Destroy()
        self.MAJ(IDfamille)

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des soldes"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des soldes"), autoriseSelections=False)

    def CocheTout(self, event=None):
        if self.GetFilter() != None :
            listeObjets = self.GetFilteredObjects()
        else :
            listeObjets = self.GetObjects()
        for track in listeObjets :
            self.Check(track)
            self.RefreshObject(track)
        
    def CocheRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def VentilationAuto(self, event):
        ID = event.GetId() 
        if ID == 201 :
            # Uniquement la ligne s�lectionn�e
            if len(self.Selection()) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune ligne !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            track = self.Selection()[0]
            VentilationAuto(IDcompte_payeur=track.IDcompte_payeur)
            self.MAJ(track.IDfamille)
        if ID == 202 :
            # Uniquement les lignes coch�es
            listeTracks = self.GetTracksCoches()
            if len(listeTracks) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coch� aucune ligne !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            for track in listeTracks :
                VentilationAuto(IDcompte_payeur=track.IDcompte_payeur)
            self.MAJ()
        # Toutes les lignes
        if ID == 203 :
            if len(self.donnees) == 0 :
                dlg = wx.MessageDialog(self, _(u"La liste est vide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            for track in self.donnees :
                VentilationAuto(IDcompte_payeur=track.IDcompte_payeur)
            self.MAJ()

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une famille..."))
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



class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nomsTitulaires" : {"mode" : "nombre", "singulier" : "famille", "pluriel" : "familles", "alignement" : wx.ALIGN_CENTER},
            "solde" : {"mode" : "total"},
            "total_prestations" : {"mode" : "total"},
            "total_reglements" : {"mode" : "total"},
            "total_ventilations" : {"mode" : "total"},
            "reste_a_ventiler" : {"mode" : "total"},
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
        self.myOlv = ListView(panel, tracks=None, onlyNonVentiles=True, IDcompte_payeur=None, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 400))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
