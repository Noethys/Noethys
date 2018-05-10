#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations, UTILS_Prestations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import datetime
import locale

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Gestion
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import GroupListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter

def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


# ---------------------------------------- LISTVIEW DATES -----------------------------------------------------------------------

class Track(object):
    def __init__(self, donnees):
        self.IDprestation = donnees["IDprestation"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.date = donnees["date"]
        self.categorie = donnees["categorie"]
        self.label = donnees["label"]
        self.montant = donnees["montant"]
        self.IDactivite = donnees["IDactivite"]
        self.nomActivite = donnees["nomActivite"]
        self.nomAbregeActivite = donnees["nomAbregeActivite"]
        self.IDtarif = donnees["IDtarif"]
        self.nomTarif = donnees["nomTarif"]
        self.nomCategorieTarif = donnees["nomCategorieTarif"]
        self.IDfacture = donnees["IDfacture"]
        if self.IDfacture == None :
            self.label_facture = u""
        else:
            IDprefixe = donnees["IDprefixe"]
            prefixe = donnees["prefixe"]
            num_facture = donnees["num_facture"]
            date_facture = donnees["date_facture"]
            if num_facture == None :
                self.label_facture = u""
            else :
                if IDprefixe != None :
                    num_facture = u"%s-%06d" % (prefixe, num_facture)
                else :
                    num_facture = u"%06d" % num_facture
                self.label_facture = u"n°%s" % num_facture

        self.IDfamille = donnees["IDfamille"]
        self.IDindividu = donnees["IDindividu"]
        self.nomIndividu = donnees["nomIndividu"]
        self.prenomIndividu = donnees["prenomIndividu"]
        if self.prenomIndividu != None :
            self.nomCompletIndividu = u"%s %s" % (self.nomIndividu, self.prenomIndividu)
        else :
            self.nomCompletIndividu = self.nomIndividu
        self.montant_ventilation = donnees["montant_ventilation"]
        self.montant_deduction = donnees["montant_deduction"]
        self.nbre_deductions = donnees["nbre_deductions"]
        self.forfait = donnees["forfait"]
        self.reglement_frais = donnees["reglement_frais"]
        
                                
class ListView(GroupListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.IDfamille = kwds.pop("IDfamille", None)
        self.selectionID = None
        self.selectionTrack = None
##        locale.setlocale(locale.LC_ALL, 'FR')
        GroupListView.__init__(self, *args, **kwds)
        self.listePeriodes = []
        self.listeIndividus = []
        self.listeActivites = []
        self.listeFactures = []
        self.titre = _(u"Liste des prestations")
        self.total = 0.0
        self.dictFiltres = {}
##        self.InitModel()
##        self.InitObjectListView()
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
        self.SetShowGroups(False)

        # Périodes de gestion
        self.gestion = UTILS_Gestion.Gestion(None)

        
    def OnActivated(self,event):
        self.Modifier(None)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetSQLdates(self, listePeriodes=[]):
        texteSQL = ""
        for date_debut, date_fin in listePeriodes :
            texteSQL += "(prestations.date>='%s' AND prestations.date<='%s') OR " % (date_debut, date_fin)
        if len(texteSQL) > 0 :
            texteSQL = "  (" + texteSQL[:-4] + ")"
        else:
            texteSQL = ""
        return texteSQL

    def GetListePrestations(self, IDfamille=None, listeComptesPayeurs=[]):
        DB = GestionDB.DB()
        
        # Condition Famille
        if IDfamille == None or IDfamille == 0 :
            conditionFamille = "IDfamille>0"
        else:
            conditionFamille = "IDfamille=%d" % IDfamille
        
        # Condition PERIODES
        conditions = self.GetSQLdates(self.listePeriodes)
        if len(conditions) > 0 :
            conditionDates = " AND %s" % conditions
        else:
            conditionDates = ""
        
        # Condition COMPTES PAYEURS
        if len(listeComptesPayeurs) == 0 : conditionComptes = "AND prestations.IDcompte_payeur > 0"
        elif len(listeComptesPayeurs) == 1 : conditionComptes = "AND prestations.IDcompte_payeur IN (%d)" % listeComptesPayeurs[0]
        else : conditionComptes = "AND prestations.IDcompte_payeur IN %s" % str(tuple(listeComptesPayeurs))
        
        # Filtres de l'utilisateur
        filtreSQL = self.GetFiltres() 

        req = """
        SELECT prestations.IDprestation, prestations.IDcompte_payeur, prestations.date, categorie, 
        prestations.label, prestations.montant, 
        prestations.IDactivite, activites.nom, activites.abrege,
        prestations.IDtarif, noms_tarifs.nom, categories_tarifs.nom,
        prestations.IDfacture, factures.IDprefixe, factures_prefixes.prefixe, factures.numero, factures.date_edition,
        prestations.forfait, prestations.IDcategorie_tarif,
        IDfamille, prestations.IDindividu, 
        individus.nom, individus.prenom,
        SUM(deductions.montant) AS montant_deduction,
        COUNT(deductions.IDdeduction) AS nbre_deductions,
        reglement_frais
        FROM prestations
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN individus ON prestations.IDindividu = individus.IDindividu
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON prestations.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        LEFT JOIN deductions ON deductions.IDprestation = prestations.IDprestation
        LEFT JOIN factures ON prestations.IDfacture = factures.IDfacture
        LEFT JOIN factures_prefixes ON factures_prefixes.IDprefixe = factures.IDprefixe
        WHERE %s %s %s %s
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % (conditionFamille, conditionComptes, conditionDates, filtreSQL)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq() 

        req = """
        SELECT ventilation.IDprestation, SUM(ventilation.montant) AS montant_ventilation
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN individus ON prestations.IDindividu = individus.IDindividu
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON prestations.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        LEFT JOIN factures ON prestations.IDfacture = factures.IDfacture
        WHERE %s %s %s %s
        GROUP BY ventilation.IDprestation
        ;""" % (conditionFamille, conditionComptes, conditionDates, filtreSQL)
        DB.ExecuterReq(req)
        listeVentilation = DB.ResultatReq() 
        dictVentilation = {}
        for IDprestation, montantVentilation in listeVentilation :
            dictVentilation[IDprestation] = montantVentilation
        DB.Close() 

        listePrestations = []
        listeIndividus = []
        listeActivites = []
        listeFactures = []
        total = 0.0
        for IDprestation, IDcompte_payeur, date, categorie, label, montant, IDactivite, nomActivite, nomAbregeActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, IDprefixe, prefixe, num_facture, date_facture, forfait, IDcategorie_tarif, IDfamille, IDindividu, nomIndividu, prenomIndividu, montant_deduction, nbre_deductions, reglement_frais in listeDonnees :
            date = DateEngEnDateDD(date)  
            if dictVentilation.has_key(IDprestation) :
                montant_ventilation = FloatToDecimal(dictVentilation[IDprestation])
            else :
                montant_ventilation = FloatToDecimal(0.0)
            if montant == None :
                montant = 0.0 
                
            dictTemp = {
                "IDprestation" : IDprestation, "IDcompte_payeur" : IDcompte_payeur, "date" : date, "categorie" : categorie,
                "label" : label, "montant" : FloatToDecimal(montant), "IDactivite" : IDactivite, "nomActivite" : nomActivite, "nomAbregeActivite" : nomAbregeActivite, "IDtarif" : IDtarif, "nomTarif" : nomTarif, 
                "nomCategorieTarif" : nomCategorieTarif, "IDfacture" : IDfacture, "IDprefixe" : IDprefixe, "prefixe" : prefixe, "num_facture" : num_facture, "date_facture" : date_facture, "forfait" : forfait,
                "IDfamille" : IDfamille, "IDindividu" : IDindividu, "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu,
                "montant_ventilation" : FloatToDecimal(montant_ventilation), "montant_deduction" : FloatToDecimal(montant_deduction), 
                "nbre_deductions" : nbre_deductions, "reglement_frais" : reglement_frais,
                }
            listePrestations.append(dictTemp)
            
            # Mémorisation des individus
            if IDindividu != None and prenomIndividu != None and (prenomIndividu, IDindividu) not in listeIndividus :
                listeIndividus.append((prenomIndividu, IDindividu))
            
            # Mémorisation des activités
            if IDactivite != None and nomActivite != None and (nomActivite, IDactivite) not in listeActivites :
                listeActivites.append((nomActivite, IDactivite))
                
            # Mémorisation des factures
            if IDfacture != None and (u"N° %d" % IDfacture, IDfacture) not in listeFactures :
                listeFactures.append((u"N° %d" % IDfacture, IDfacture))
            
            # Mémorisation du total des prestations affichées
            total += montant

        return listePrestations, listeIndividus, listeActivites, listeFactures, total


    def GetTracks(self):
        # Récupération des données
        listeID = None
        listeDonnees, self.listeIndividus, self.listeActivites, self.listeFactures, self.total = self.GetListePrestations(IDfamille=self.IDfamille) 
    
        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False            
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item["IDprestation"] :
                    self.selectionTrack = track
        return listeListeView


    def InitObjectListView(self):
        # ImageList
        self.imgVert = self.AddNamedImages("vert", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_vert.png"), wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("rouge", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_rouge.png"), wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("orange", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_orange.png"), wx.BITMAP_TYPE_PNG))

        def GetImageVentilation(track):
            if track.montant == track.montant_ventilation :
                return self.imgVert
            if track.montant_ventilation == FloatToDecimal(0.0) or track.montant_ventilation == None :
                return self.imgRouge
            if track.montant_ventilation < track.montant :
                return self.imgOrange
            return self.imgRouge

        def FormateDate(dateDD):
            return DateComplete(dateDD)

        def FormateMontant(montant):
            if montant == None or montant == "" : return ""
            return u"%.2f %s" % (montant, SYMBOLE)
                   
        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour(wx.Colour(150, 150, 150))
                
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = "#FFFFFF" # Vert
        
        # Paramètres ListView
        self.useExpansionColumn = True
        
        if self.IDfamille != None :
            listeColonnes = ["IDprestation", "date", "prenom_individu", "nom_activite", "label", "montant", "regle", "deductions", "categorie_tarif", "num_facture"]
        else :
            listeColonnes = ["IDprestation", "date", "nom_complet_individu", "nom_activite", "label", "montant", "regle", "deductions", "categorie_tarif", "num_facture"]
        
        dictColonnes = {
            "IDprestation" : ColumnDefn(u"", "left", 0, "IDprestation", typeDonnee="entier"),
            "date" : ColumnDefn(_(u"Date"), "left", 160, "date", typeDonnee="date", stringConverter=FormateDate),
            "categorie_prestation" : ColumnDefn(_(u"Catégorie"), "left", 100, "categorie", typeDonnee="texte"),
            "prenom_individu" : ColumnDefn(_(u"Individu"), "left", 75, "prenomIndividu", typeDonnee="texte"),
            "nom_complet_individu" : ColumnDefn(_(u"Individu"), "left", 150, "nomCompletIndividu", typeDonnee="texte"),
            "nom_activite" : ColumnDefn(_(u"Activité"), "left", 55, "nomAbregeActivite", typeDonnee="texte"),
            "label" : ColumnDefn(_(u"Label"), "left", 155, "label", typeDonnee="texte"),
            "montant" : ColumnDefn(_(u"Montant"), "right", 65, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            "regle" : ColumnDefn(_(u"Réglé"), "right", 72, "montant_ventilation", typeDonnee="montant", stringConverter=FormateMontant, imageGetter=GetImageVentilation),
            "deductions" : ColumnDefn(_(u"Déduc."), "right", 55, "montant_deduction", typeDonnee="montant", stringConverter=FormateMontant),
            "nom_tarif" : ColumnDefn(_(u"Tarif"), "left", 140, "nomTarif", typeDonnee="texte"),
            "categorie_tarif" : ColumnDefn(_(u"Catégorie de tarif"), "left", 100, "nomCategorieTarif", typeDonnee="texte"),
            "num_facture" : ColumnDefn(_(u"N° Facture"), "left", 70, "label_facture", typeDonnee="texte"),
        }
        
        self.SetColumns([dictColonnes[code] for code in listeColonnes])
        
##        self.SetShowGroups(False)
        self.CreateCheckStateColumn(0)
        self.SetShowItemCounts(False)
        self.SetSortColumn(self.columns[2])
        self.SetEmptyListMsg(_(u"Aucune prestation"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
##        self.rowFormatter = rowFormatter
        self.SetObjects(self.donnees)
    
    def GetListeIndividus(self):
        return self.listeIndividus
    
    def GetListeActivites(self):
        return self.listeActivites
    
    def GetListeFactures(self):
        return self.listeFactures
    
    def GetTotal(self):
        return self.total 
    
    def GetTitresColonnes(self):
        listeColonnes = []
        for index in range(0, self.GetColumnCount()) :
            listeColonnes.append(self.columns[index].title)
        return listeColonnes
    
    def SetColonneTri(self, indexColonne=1):
##        self.SetAlwaysGroupByColumn(indexColonne)
        self.MAJ()
        self.SetAlwaysGroupByColumn(indexColonne+1)
##        self.SetSortColumn(self.columns[indexColonne-1], resortNow=True)
    
    def GetFiltres(self):
        filtreSQL = ""
        for champFiltre, valeur in self.dictFiltres.iteritems() :
            if "COMPLEXE" in champFiltre and valeur != None :
                filtreSQL += " AND %s" % valeur
            else :
                if valeur != None :
                    filtreSQL += " AND %s = %s" % (champFiltre, valeur)
        return filtreSQL
        
    def SetFiltre(self, champFiltre, valeur):
        self.dictFiltres[champFiltre] = valeur
        self.MAJ() 
        
    def SetListePeriodes(self, listePeriodes=[]):
        if listePeriodes == None :
            self.listePeriodes = []
        else:
            self.listePeriodes = listePeriodes
        self.MAJ() 
        
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
        # MAJ du total du panel
        try :
            if self.GetParent().GetName() == "panel_prestations" :
                self.GetParent().MAJtotal()
        except :
            pass
        self.Refresh()
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) > 0 :
            ID = self.Selection()[0].IDprestation
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        if self.IDfamille != None :
            item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if len(self.Selection()) == 0 : item.Enable(False)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if len(self.Selection()) == 0 : item.Enable(False)


        # Item Appliquer modèle de prestation
        if self.IDfamille != None :
            menuPop.AppendSeparator()
            item = wx.MenuItem(menuPop, 11, _(u"Ajouter une prestation selon un modèle"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Magique.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Appliquer_modele, id=11)

        menuPop.AppendSeparator()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des prestations"))

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_prestations", "creer") == False : return
        from Dlg import DLG_Saisie_prestation
        dlg = DLG_Saisie_prestation.Dialog(self, IDprestation=None, IDfamille=self.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            IDprestation = dlg.GetIDprestation()
            self.MAJ(IDprestation)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_prestations", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune prestation dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        
        if track.IDfacture != None :
            dlg = wx.MessageDialog(self, _(u"Cette prestation apparaît déjà sur la facture %s. Il est donc impossible de la modifier. \n\nSouhaitez-vous tout de même consulter le détail de cette prestation en mode lecture seule ?") % track.label_facture, _(u"Modification impossible"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        else :
            if self.gestion.Verification("prestations", track.date, silencieux=True) == False:
                dlg = wx.MessageDialog(self, _(u"Cette prestation est dans une période de gestion verrouillée. Il est donc impossible de la modifier. \n\nSouhaitez-vous tout de même consulter le détail de cette prestation en mode lecture seule ?"), _(u"Modification impossible"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse != wx.ID_YES :
                    return

        if track.categorie == "cotisation" :
            dlg = wx.MessageDialog(self, _(u"Pour modifier la prestation d'une cotisation, allez directement dans la liste des cotisations !"), _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        from Dlg import DLG_Saisie_prestation
        dlg = DLG_Saisie_prestation.Dialog(self, IDprestation=track.IDprestation, IDfamille=track.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(track.IDprestation)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_prestations", "supprimer") == False : return
        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune prestation à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.GetTracksCoches()) > 0 :
            # Suppression multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer les %d prestations cochées ?") % len(listeSelections), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        else :
            # Suppression unique
            listeSelections = self.Selection()        
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer la prestation n°%d ?") % listeSelections[0].IDprestation, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        nePlusDemanderConfirmation = False
        listeSuppressions = []
        DB = GestionDB.DB()
        for track in listeSelections :
            
            valide = True

            if self.gestion.Verification("prestations", track.date) == False: return False
            
            # Vérifie si ce n'est pas un forfait non supprimable
            if track.forfait == 2 :
                dlg = wx.MessageDialog(self, _(u"La prestation n°%d est un forfait non supprimable !\n\n(Pour le supprimer, vous devez obligatoirement désinscrire l'individu de l'activité)") % track.IDprestation, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                valide = False
            
            # Vérifie qu'aucune facture n'y est rattachée
            if valide == True and track.IDfacture != None :
                dlg = wx.MessageDialog(self, _(u"La prestation n°%d apparaît déjà sur la facture %s.\n\nVous ne pouvez donc pas la supprimer !") % (track.IDprestation, track.label_facture), _(u"Suppression impossible"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                valide = False

            # Recherche si des consommations y sont attachées
            req = """
            SELECT IDconso, date, etat, consommations.IDunite, unites.nom, 
            consommations.IDindividu, individus.nom, individus.prenom
            FROM consommations
            LEFT JOIN unites ON unites.IDunite = consommations.IDunite
            LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
            WHERE IDprestation=%d
            ORDER BY date
            ;""" % track.IDprestation
            DB.ExecuterReq(req)
            listeConsommations = DB.ResultatReq() 
            listeIDconso = []
            nbreVerrouillees = 0
            
            if len(listeConsommations) > 0 and valide == True :
##                message = _(u"Attention, la prestation n°%d est rattachée aux %d consommation(s) suivantes :\n\n") % (track.IDprestation, len(listeConsommations))
##                lignesConso = []
##                for IDconso, date, etat, IDunite, nomUnite, IDindividu, nomIndividu, prenomIndividu in listeConsommations :
##                    listeIDconso.append(IDconso)
##                    if etat == "present" :
##                        nbreVerrouillees += 1
##                    dateDD = DateEngEnDateDD(date)
##                    dateFr = DateComplete(dateDD)
##                    if IDindividu == 0 or IDindividu == None :
##                        individu = u""
##                    else:
##                        individu = _(u"pour %s %s") % (nomIndividu, prenomIndividu)
##                    ligneTexte = _(u"   - Le %s : %s %s\n") % (dateFr, nomUnite, individu)
##                    #message += ligneTexte
##                    lignesConso.append(ligneTexte)
##                
##                maxAffichage = 20
##                if len(lignesConso) > maxAffichage :
##                    message += "".join(lignesConso[:maxAffichage]) + _(u"   - Et %d autres consommations...\n") % (len(lignesConso) - maxAffichage)
##                else :
##                    message += "".join(lignesConso)
##                    
##                message += _(u"\nSouhaitez-vous supprimer également ces consommations (conseillé) ?\n\n(Si vous répondez non, les consommations seront conservées dans le calendrier mais seront considérées comme gratuites)")


                lignesConso = []
                for IDconso, date, etat, IDunite, nomUnite, IDindividu, nomIndividu, prenomIndividu in listeConsommations :
                    listeIDconso.append(IDconso)
                    if etat == "present" :
                        nbreVerrouillees += 1
                    dateDD = DateEngEnDateDD(date)
                    dateFr = DateComplete(dateDD)
                    if IDindividu == 0 or IDindividu == None :
                        individu = u""
                    else:
                        individu = _(u"pour %s %s") % (nomIndividu, prenomIndividu)
                    ligneTexte = _(u"   - Le %s : %s %s\n") % (dateFr, nomUnite, individu)
                    #message += ligneTexte
                    lignesConso.append(ligneTexte)

                    if self.gestion.Verification("consommations", dateDD) == False: return False

                detail = ""
                maxAffichage = 20
                if len(lignesConso) > maxAffichage :
                    detail += "".join(lignesConso[:maxAffichage]) + _(u"   - Et %d autres consommations...\n") % (len(lignesConso) - maxAffichage)
                else :
                    detail += "".join(lignesConso)

                introduction = _(u"Attention, la prestation n°%d est rattachée aux %d consommation(s) suivantes :") % (track.IDprestation, len(listeConsommations))
                conclusion = _(u"Souhaitez-vous supprimer également ces consommations (conseillé) ?\n\n(Si vous répondez non, les consommations seront conservées dans le calendrier mais seront considérées comme gratuites)")

                # Demande confirmation pour supprimer les consommations associées
                if nePlusDemanderConfirmation == False :
                    from Dlg import DLG_Messagebox
                    dlg = DLG_Messagebox.Dialog(self, titre=_(u"Avertissement"), introduction=introduction, detail=detail, conclusion=conclusion, icone=wx.ICON_EXCLAMATION, boutons=[_(u"Oui"), _(u"Oui pour tout"), _(u"Non"), _(u"Annuler")], defaut=0)
                    reponse = dlg.ShowModal() 
                    dlg.Destroy() 
                else :
                    reponse = 0
                    
                if reponse == 0 or reponse == 1 or nePlusDemanderConfirmation == True :
                    if nbreVerrouillees > 0 :
                        # Annule la procédure d'annulation si des consommations sont déjà pointées sur 'présent' :
                        dlg = wx.MessageDialog(self, _(u"La prestation %d est rattachée à %d consommation(s) déjà pointées.\nIl vous est donc impossible de le(s) supprimer !\n\nProcédure de suppression annulée.") % (track.IDprestation, nbreVerrouillees), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        valide = False
                    else :
                        # Suppression des consommations associées
                        for IDconso in listeIDconso :
                            DB.ReqDEL("consommations", "IDconso", IDconso)
                            
                    if reponse == 1 :
                        nePlusDemanderConfirmation = True

                if reponse == 2 :
                    # Supprime la référence à la prestation des consommations
                    for IDconso in listeIDconso :
                        listeDonnees = [("IDprestation", None),]
                        DB.ReqMAJ("consommations", listeDonnees, "IDconso", IDconso)

                if reponse == 3 :
                    return

            
            # Recherche s'il s'agit d'une prestation de frais de gestion pour un règlement
            if track.reglement_frais != None :
                dlg = wx.MessageDialog(self, _(u"La prestation n°%d est rattachée au règlement n°%d en tant que frais de gestion de règlement.\n\nSouhaitez-vous vraiment supprimer cette prestation ?") % (track.IDprestation, track.reglement_frais), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
                reponse = dlg.ShowModal() 
                dlg.Destroy()
                if reponse != wx.ID_YES :
                    valide = False
                    
            # Annuler la prestation
            if valide:
                # Avertir l'utilisateur qu'il s'agit d'une annulation, et demander son accord
                msg = u"Pour préserver l'intégrité des états comptables, " \
                      u"cette modification engendrerait une nouvelle prestation d'annulation. " \
                      u"La prestation d'origine reste intacte.\n" \
                      u"Voulez-vous continuer ?"
                dlg = wx.MessageDialog(self, _(msg), _(u"Confirmation"), wx.YES_NO | wx.ICON_QUESTION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse == wx.ID_YES:
                    UTILS_Prestations.annuler(track.IDprestation, DB)
                    DB.ReqDEL("ventilation", "IDprestation", track.IDprestation)
                    DB.ReqDEL("deductions", "IDprestation", track.IDprestation)
                    listeSuppressions.append(track)

            # MAJ du listeView
            self.MAJ() 
            
        DB.Close() 
        
##        # Confirmation de suppression
##        dlg = wx.MessageDialog(self, _(u"%d prestation(s) ont été supprimée(s) avec succès.") % len(listeSuppressions), _(u"Suppression"), wx.OK | wx.ICON_INFORMATION)
##        dlg.ShowModal()
##        dlg.Destroy()
        
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

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, track.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(track.IDfacture)
        dlg.Destroy()

    def Appliquer_modele(self, event=None):
        from Dlg import DLG_Appliquer_modele_prestation
        dlg = DLG_Appliquer_modele_prestation.Dialog(self, IDfamille=self.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            IDprestation = dlg.GetIDprestation()
            self.MAJ(IDprestation)
        dlg.Destroy()








# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "date" : {"mode" : "nombre", "singulier" : _(u"prestation"), "pluriel" : _(u"prestations"), "alignement" : wx.ALIGN_CENTER},
            "montant" : {"mode" : "total"},
            "montant_ventilation" : {"mode" : "total"},
            "montant_deduction" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


# ----------------- FRAME DE TEST ----------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, -1, IDfamille=None, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        import time
        t = time.time()
        self.myOlv.MAJ() 
        print time.time() - t
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((800, 400))
        self.Layout()


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "GroupListView")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
