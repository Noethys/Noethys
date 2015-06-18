#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import datetime
import locale
import FonctionsPerso

from UTILS_Decimal import FloatToDecimal as FloatToDecimal

import UTILS_Titulaires
import UTILS_Dates
import UTILS_Utilisateurs
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter




class Track(object):
    def __init__(self, donnees):
        self.IDfacture = donnees["IDfacture"]
        self.numero = donnees["numero"]
        if self.numero == None : self.numero = 0
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.date_edition = donnees["date_edition"]
        self.date_echeance = donnees["date_echeance"]
        self.IDutilisateur = donnees["IDutilisateur"]
        self.date_debut = donnees["date_debut"]
        self.date_fin = donnees["date_fin"]
        self.total = donnees["total"]
        self.regle = donnees["regle"]
        self.solde = donnees["solde"]
        if self.solde != 0.0 : 
            self.solde = -self.solde
        self.totalPrestations = donnees["totalPrestations"]
        self.totalVentilation = donnees["totalVentilation"]
        if self.totalVentilation == None :
            self.totalVentilation = 0.0
        self.soldeActuel = self.totalVentilation - self.totalPrestations
        self.IDfamille = donnees["IDfamille"]
        self.nomsTitulaires =  donnees["titulaires"]
        self.IDlot =  donnees["IDlot"]
        self.nomLot =  donnees["nomLot"]
        self.adresse_famille = donnees["adresse_famille"]
        self.titulaire_helios = donnees["titulaire_helios"]
        
        # Prélèvement
        self.prelevement_activation =  donnees["prelevement_activation"]
        self.prelevement_etab =  donnees["prelevement_etab"]
        self.prelevement_guichet =  donnees["prelevement_guichet"]
        self.prelevement_numero =  donnees["prelevement_numero"]
        self.prelevement_cle =  donnees["prelevement_cle"]
        self.prelevement_banque =  donnees["prelevement_banque"]
        self.prelevement_individu =  donnees["prelevement_individu"]
        self.prelevement_nom =  donnees["prelevement_nom"]
        self.prelevement_rue =  donnees["prelevement_rue"]
        self.prelevement_cp =  donnees["prelevement_cp"]
        self.prelevement_ville =  donnees["prelevement_ville"]
        self.prelevement_cle_iban =  donnees["prelevement_cle_iban"]
        self.prelevement_iban =  donnees["prelevement_iban"]
        self.prelevement_bic =  donnees["prelevement_bic"]
        self.prelevement_reference_mandat =  donnees["prelevement_reference_mandat"]
        self.prelevement_date_mandat =  donnees["prelevement_date_mandat"]

        if self.prelevement_activation == 1 :
            self.prelevement = True
        else :
            self.prelevement = False
        
        self.nomPayeur = donnees["nomPayeur"]
        self.prenomPayeur = donnees["prenomPayeur"]
        if self.nomPayeur == None : self.nomPayeur = u""
        if self.prenomPayeur == None : self.prenomPayeur = u""
        if self.prelevement_individu == None :
            self.prelevement_payeur = self.prelevement_nom
        else :
            self.prelevement_payeur = u"%s %s" % (self.nomPayeur, self.prenomPayeur)
            
        
        # Envoi par Email
        self.email_factures =  donnees["email_factures"]
        
        if self.email_factures != None :
            self.email = True
        else :
            self.email = False
            


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.IDcompte_payeur = kwds.pop("IDcompte_payeur", None)
        self.codesColonnes = kwds.pop("codesColonnes", [])
        self.checkColonne = kwds.pop("checkColonne", False)
        self.triColonne = kwds.pop("triColonne", "numero")
        self.filtres = None
        self.selectionID = None
        self.selectionTrack = None
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnActivated(self,event):
        self.Reedition(None)

    def InitModel(self):
        self.donnees = self.GetTracks()
    
    def SetFiltres(self, filtres=None):
        """
        None ->                     filtre = None
        IDfacture_intervalle ->  filtre = {"type" : "IDfacture_intervalle", "IDfacture_min" : 22, "IDfacture_max" : 28}
        IDfacture_liste ->         filtre = {"type" : "IDfacture_liste", "liste" : [10, 300, 20] }
        Lot de factures ->        filtre = {"type" : "lot", "IDlot" : 22}
        Date d'émission ->      filtre = {"type" : "date_emission", "date_debut" : ___, "date_fin" : ___}
        Date d'échéance ->      filtre = {"type" : "date_echance", "date_debut" : ___, "date_fin" : ___}
        numero_intervalle ->    filtre = {"type" : "numero_intervalle", "numero_min" : 210, "numero_max" : 215}
        numero_liste ->           filtre = {"type" : "numero_liste", "liste" : [10, 300, 20] }
        """
        self.filtres = filtres

    def GetListeFactures(self):
        dictTitulaires = UTILS_Titulaires.GetTitulaires() 

        DB = GestionDB.DB()
        
        # Conditions
        listeConditions = []
        
        if self.IDcompte_payeur != None :
            listeConditions.append("prestations.IDcompte_payeur = %d" % self.IDcompte_payeur)
        
        # 1ère série de filtres
        if self.filtres != None :
            for filtre in self.filtres :
            
                # IDfacture_intervalle
                if filtre["type"] == "IDfacture_intervalle" :
                    listeConditions.append( "(factures.IDfacture>=%d AND factures.IDfacture<=%d)" % (filtre["IDfacture_min"], filtre["IDfacture_max"]) )

                # IDfacture_liste
                if filtre["type"] == "IDfacture_liste" :
                    if len(filtre["liste"]) == 0 : listeTemp = "()" 
                    elif len(filtre["liste"]) == 1 : listeTemp = "(%d)" % filtre["liste"][0]
                    else : listeTemp = str(tuple(filtre["liste"]))
                    listeConditions.append( "factures.IDfacture IN %s" % listeTemp)

                # Lot de factures
                if filtre["type"] == "lot" :
                    listeConditions.append( "factures.IDlot=%d" % filtre["IDlot"] )
            
                # Date d'émission
                if filtre["type"] == "date_emission" :
                    listeConditions.append( "(factures.date_edition>='%s' AND factures.date_edition<='%s')" % (filtre["date_min"], filtre["date_max"]) )

                # Date d'échéance
                if filtre["type"] == "date_echeance" :
                    listeConditions.append( "(factures.date_echeance>='%s' AND factures.date_echeance<='%s')" % (filtre["date_min"], filtre["date_max"]) )

                # numero_intervalle
                if filtre["type"] == "numero_intervalle" :
                    listeConditions.append( "(factures.numero>=%d AND factures.numero<=%d)" % (filtre["numero_min"], filtre["numero_max"]) )

                # numero_liste
                if filtre["type"] == "numero_liste" :
                    if len(filtre["liste"]) == 0 : listeTemp = "()" 
                    elif len(filtre["liste"]) == 1 : listeTemp = "(%d)" % filtre["liste"][0]
                    else : listeTemp = str(tuple(filtre["liste"]))
                    listeConditions.append( "factures.numero IN %s" % listeTemp)

        if len(listeConditions) > 0 :
            conditions = "WHERE %s" % " AND ".join(listeConditions)
        else :
            conditions = ""
        
        # Récupération des totaux des prestations pour chaque facture
        req = """
        SELECT 
        prestations.IDfacture, SUM(prestations.montant)
        FROM prestations
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        %s
        GROUP BY prestations.IDfacture
        ;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        dictPrestations = {}
        for IDfacture, totalPrestations in listeDonnees :
            if IDfacture != None :
                dictPrestations[IDfacture] = totalPrestations
        
        # Récupération des factures
        req = """
        SELECT factures.IDfacture, factures.numero, factures.IDcompte_payeur, 
        factures.date_edition, factures.date_echeance, factures.IDutilisateur,
        factures.date_debut, factures.date_fin, factures.total, factures.regle, factures.solde,
        comptes_payeurs.IDfamille, factures.IDlot, lots_factures.nom
        FROM factures
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = factures.IDcompte_payeur
        LEFT JOIN lots_factures ON lots_factures.IDlot = factures.IDlot
        %s
        ORDER BY factures.date_edition
        ;""" % conditions.replace("prestations.IDcompte_payeur", "comptes_payeurs.IDcompte_payeur")
        DB.ExecuterReq(req)
        listeFactures = DB.ResultatReq()
        
        # Récupération de la ventilation
        req = """
        SELECT prestations.IDfacture, SUM(ventilation.montant)
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = prestations.IDcompte_payeur
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        %s
        GROUP BY prestations.IDfacture
        ;""" % conditions
        DB.ExecuterReq(req)
        listeVentilation = DB.ResultatReq()
        dictVentilation = {}
        for IDfacture, montantVentilation in listeVentilation :
            if IDfacture != None :
                dictVentilation[IDfacture] = montantVentilation
        
        # Infos Prélèvement + Envoi par Email des factures
        if self.IDcompte_payeur != None :
            conditions = "WHERE comptes_payeurs.IDcompte_payeur = %d" % self.IDcompte_payeur
        else:
            conditions = ""

        req = """
        SELECT 
        prelevement_activation, prelevement_etab, prelevement_guichet, prelevement_numero, prelevement_cle, prelevement_banque,
        prelevement_individu, prelevement_nom, prelevement_rue, prelevement_cp, prelevement_ville, 
        prelevement_cle_iban, prelevement_iban, prelevement_bic, prelevement_reference_mandat, prelevement_date_mandat, 
        email_factures,
        comptes_payeurs.IDcompte_payeur,
        individus.nom, individus.prenom,
        titulaire_helios
        FROM familles
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = familles.IDfamille
        LEFT JOIN individus ON individus.IDindividu = prelevement_individu
        %s
        ;""" % conditions
        DB.ExecuterReq(req)
        listeInfosFamilles = DB.ResultatReq()
        dictInfosFamilles = {}
        for prelevement_activation, prelevement_etab, prelevement_guichet, prelevement_numero, prelevement_cle, prelevement_banque, prelevement_individu, prelevement_nom, prelevement_rue, prelevement_cp, prelevement_ville, prelevement_cle_iban, prelevement_iban, prelevement_bic, prelevement_reference_mandat, prelevement_date_mandat, email_factures, IDcompte_payeur, nomPayeur, prenomPayeur, titulaire_helios in listeInfosFamilles :
            prelevement_date_mandat = UTILS_Dates.DateEngEnDateDD(prelevement_date_mandat) 
            dictInfosFamilles[IDcompte_payeur] = {
                    "prelevement_activation" : prelevement_activation, "prelevement_etab" : prelevement_etab, "prelevement_guichet" : prelevement_guichet, 
                    "prelevement_numero" : prelevement_numero, "prelevement_cle" : prelevement_cle, "prelevement_banque" : prelevement_banque, 
                    "prelevement_individu" : prelevement_individu, "prelevement_nom" : prelevement_nom, "prelevement_rue" : prelevement_rue, 
                    "prelevement_cp" : prelevement_cp, "prelevement_ville" : prelevement_ville, 
                    "prelevement_cle_iban" : prelevement_cle_iban, "prelevement_iban" : prelevement_iban, "prelevement_bic" : prelevement_bic,
                    "prelevement_reference_mandat" : prelevement_reference_mandat, "prelevement_date_mandat" : prelevement_date_mandat,
                    "email_factures" : email_factures, "nomPayeur" : nomPayeur, "prenomPayeur" : prenomPayeur, "titulaire_helios" : titulaire_helios,
                    }
        
        DB.Close() 
                
        listeResultats = []
        for IDfacture, numero, IDcompte_payeur, date_edition, date_echeance, IDutilisateur, date_debut, date_fin, total, regle, solde, IDfamille, IDlot, nomLot in listeFactures :
            if numero == None : numero = 0
            date_edition = UTILS_Dates.DateEngEnDateDD(date_edition) 
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            date_echeance = UTILS_Dates.DateEngEnDateDD(date_echeance)       
            if dictVentilation.has_key(IDfacture) :
                totalVentilation = FloatToDecimal(dictVentilation[IDfacture])
            else :
                totalVentilation = FloatToDecimal(0.0)
            if dictPrestations.has_key(IDfacture) :
                totalPrestations = FloatToDecimal(dictPrestations[IDfacture])
            else :
                totalPrestations = FloatToDecimal(0.0)
            solde_actuel = totalPrestations - totalVentilation
            
            if dictTitulaires.has_key(IDfamille) == True :
                
                titulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
                adresse_famille = dictTitulaires[IDfamille]["adresse"]
                
                dictTemp = {
                    "IDfacture" : IDfacture, "numero" : numero, "IDcompte_payeur" : IDcompte_payeur, "date_edition" : date_edition, "date_echeance" : date_echeance,
                    "IDutilisateur" : IDutilisateur, "date_debut" : date_debut, "date_fin" : date_fin, "total" : total, "regle" : regle, "solde" : solde, 
                    "totalPrestations" : totalPrestations, "totalVentilation" : totalVentilation, "IDfamille" : IDfamille, "titulaires" : titulaires, "IDlot" : IDlot, "nomLot" : nomLot,
                    "adresse_famille" : adresse_famille,
                    }
                
                if dictInfosFamilles.has_key(IDcompte_payeur) :
                    dictTemp.update(dictInfosFamilles[IDcompte_payeur])

                valide = True
                
                # 2ème série de filtres
                if self.filtres != None :
                    for filtre in self.filtres :
                
                        # IDfacture_intervalle
                        if filtre["type"] == "solde_initial" :
                            if self.ComparateurFiltre(-solde, filtre["operateur"], filtre["montant"]) == False :
                                valide = False

                        if filtre["type"] == "solde_actuel" :
                            if self.ComparateurFiltre(-solde_actuel, filtre["operateur"], filtre["montant"]) == False :
                                valide = False

                        if filtre["type"] == "prelevement" :
                            if filtre["choix"] == True :
                                if dictTemp["prelevement_activation"] == None : valide = False
                            else :
                                if dictTemp["prelevement_activation"] != None : valide = False

                        if filtre["type"] == "email" :
                            if filtre["choix"] == True :
                                if dictTemp["email_factures"] == None : valide = False
                            else :
                                if dictTemp["email_factures"] != None : valide = False

                # Mémorisation des valeurs
                if valide == True :                    
                    listeResultats.append(dictTemp)
            
        return listeResultats
    
    def ComparateurFiltre(self, valeur1=12.00, operateur=">=", valeur2=0.0):
        if operateur == "=" : 
            if valeur1 == valeur2 : return True
        if operateur == "<>" : 
            if valeur1 != valeur2 : return True
        if operateur == ">" : 
            if valeur1 > valeur2 : return True
        if operateur == "<" : 
            if valeur1 < valeur2 : return True
        if operateur == ">=" : 
            if valeur1 >= valeur2 : return True
        if operateur == "<=" : 
            if valeur1 <= valeur2 : return True
        return False


    def GetTracks(self):
        # Récupération des données
        listeID = None
        listeDonnees = self.GetListeFactures() 
    
        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item["IDfacture"] :
                    self.selectionTrack = track
        return listeListeView


    def InitObjectListView(self):
        
        # ImageList
        self.imgVert = self.AddNamedImages("vert", wx.Bitmap("Images/16x16/Ventilation_vert.png", wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("rouge", wx.Bitmap("Images/16x16/Ventilation_rouge.png", wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("orange", wx.Bitmap("Images/16x16/Ventilation_orange.png", wx.BITMAP_TYPE_PNG))
        self.imgPrelevement = self.AddNamedImages("prelevement", wx.Bitmap("Images/16x16/Prelevement.png", wx.BITMAP_TYPE_PNG))
        self.imgEmail = self.AddNamedImages("email", wx.Bitmap("Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_PNG))

        def GetImageSoldeActuel(track):
            if track.soldeActuel == 0.0 :
                return self.imgVert
            if track.soldeActuel < 0.0 and track.soldeActuel != -track.total :
                return self.imgOrange
            return self.imgRouge
        
        def GetImagePrelevement(track):
            if track.prelevement == True :
                return self.imgPrelevement

        def GetImageEmail(track):
            if track.email == True :
                return self.imgEmail
        
        def FormateNumero(numero):
            if numero == None :
                return ""
            if type(numero) == str or type(numero) == unicode :
                numero = int(numero)
            return "%06d" % numero

        def FormateDate(dateDD):
            if dateDD == None : return u""
            return UTILS_Dates.DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None or montant == "" : return ""
            return u"%.2f %s" % (montant, SYMBOLE)
                   
        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour(wx.Colour(150, 150, 150))
                
        # Couleur en alternance des lignes
        self.oddRowsBackColor = wx.Colour(255, 255, 255) #"#EEF4FB" # Bleu
        self.evenRowsBackColor = "#F0FBED" # Vert

        # Paramètres ListView
        self.useExpansionColumn = True
        
        dictColonnes = {
            "IDfacture" : ColumnDefn(u"", "left", 0, "IDfacture", typeDonnee="entier"),
            "date" : ColumnDefn(_(u"Date"), "centre", 80, "date_edition", typeDonnee="date", stringConverter=FormateDate),
            "numero" : ColumnDefn(u"N°", "centre", 65, "numero", typeDonnee="entier", stringConverter=FormateNumero),
            "famille" : ColumnDefn(_(u"Famille"), "left", 180, "nomsTitulaires", typeDonnee="texte"),
            "date_debut" : ColumnDefn(_(u"Date début"), "centre", 80, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            "date_fin" : ColumnDefn(_(u"Date fin"), "centre", 80, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            "total" : ColumnDefn(_(u"Total"), "right", 65, "total", typeDonnee="montant", stringConverter=FormateMontant),
            "regle" : ColumnDefn(_(u"Réglé"), "right", 65, "regle", typeDonnee="montant", stringConverter=FormateMontant),
            "solde" : ColumnDefn(_(u"Solde"), "right", 65, "solde", typeDonnee="montant", stringConverter=FormateMontant),
            "solde_actuel" : ColumnDefn(_(u"Solde actuel"), "right", 90, "soldeActuel", typeDonnee="montant", stringConverter=FormateMontant, imageGetter=GetImageSoldeActuel),
            "date_echeance" : ColumnDefn(_(u"Echéance"), "centre", 80, "date_echeance", typeDonnee="date", stringConverter=FormateDate),
            "nom_lot" : ColumnDefn(_(u"Lot"), "left", 150, "nomLot", typeDonnee="texte"),
            "prelevement" : ColumnDefn(u"P", "left", 20, "", imageGetter=GetImagePrelevement),
            "email" : ColumnDefn(u"E", "left", 20, "", imageGetter=GetImageEmail),
            }
            
        listeColonnes = []
        tri = None
        index = 0
        for codeColonne in self.codesColonnes :
            listeColonnes.append(dictColonnes[codeColonne])
            # Checkbox 
            if codeColonne == self.triColonne :
                tri = index
            index += 1
        
        self.SetColumns(listeColonnes)
        if self.checkColonne == True :
            self.CreateCheckStateColumn(1)
        if tri != None :
            if self.checkColonne == True : tri += 1
            self.SetSortColumn(self.columns[tri])

        self.SetEmptyListMsg(_(u"Aucune facture"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
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
        # MAJ du total du panel
        try :
            if self.GetParent().GetName() == "panel_prestations" :
                self.GetParent().MAJtotal()
        except :
            pass
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def DefilePremier(self):
        if len(self.GetObjects()) > 0 :
            self.EnsureCellVisible(0, 0)

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) > 0 :
            ID = self.Selection()[0].IDfacture
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Rééditer la facture
        item = wx.MenuItem(menuPop, 60, _(u"Aperçu PDF de la facture"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Reedition, id=60)

        # Item Envoyer la facture par Email
        item = wx.MenuItem(menuPop, 90, _(u"Envoyer la facture par Email"))
        bmp = wx.Bitmap("Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EnvoyerEmail, id=90)
        
        menuPop.AppendSeparator()
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 : item.Enable(False)

        menuPop.AppendSeparator()
        
        if self.checkColonne == True :
            
            # Item Tout cocher
            item = wx.MenuItem(menuPop, 70, _(u"Tout cocher"))
            item.SetBitmap(wx.Bitmap("Images/16x16/Cocher.png", wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.CocheTout, id=70)

            # Item Tout décocher
            item = wx.MenuItem(menuPop, 80, _(u"Tout décocher"))
            item.SetBitmap(wx.Bitmap("Images/16x16/Decocher.png", wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.CocheRien, id=80)

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
    
    def Reedition(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune facture à imprimer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfacture = self.Selection()[0].IDfacture
        import UTILS_Facturation
        facturation = UTILS_Facturation.Facturation()
        facturation.Impression(listeFactures=[IDfacture,])
    
    def EnvoyerEmail(self, event):
        """ Envoyer la facture par Email """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune facture à envoyer par Email !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        # Envoi du mail
        import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=track.IDfamille, nomDoc="Temp/FACTURE%s.pdf" % FonctionsPerso.GenerationIDdoc(), categorie="facture")
    
    def CreationPDF(self, nomDoc="", afficherDoc=True):        
        """ Création du PDF pour Email """
        IDfacture = self.Selection()[0].IDfacture
        import UTILS_Facturation
        facturation = UTILS_Facturation.Facturation()
        resultat = facturation.Impression(listeFactures=[IDfacture,], nomDoc=nomDoc, afficherDoc=False)
        if resultat == False : 
            return False
        dictChampsFusion, dictPieces = resultat
        return dictChampsFusion[IDfacture]
    
    def GetTextesImpression(self):
        total = _(u"%d factures. ") % len(self.donnees)
        if self.filtres != None :
            from DLG_Filtres_factures import GetTexteFiltres 
            intro = total + _(u"Filtres de sélection : %s") % GetTexteFiltres(self.filtres)
        else :
            intro = None
        return intro, total

    def Apercu(self, event=None):
        import UTILS_Printer
        txtIntro, txtTotal = self.GetTextesImpression()
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des factures"), intro=txtIntro, total=txtTotal, format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event=None):
        import UTILS_Printer
        txtIntro, txtTotal = self.GetTextesImpression()
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des factures"), intro=txtIntro, total=txtTotal, format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des factures"))
        
    def ExportExcel(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des factures"))

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
    
    def GetTracksTous(self):
        return self.donnees
        
    def Supprimer(self, event):
        if self.IDcompte_payeur != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_factures", "supprimer") == False : return
        if self.IDcompte_payeur == None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_factures", "supprimer") == False : return
        
        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune facture à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if len(self.GetTracksCoches()) > 0 :
            # Suppression multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer les %d factures cochées ?") % len(listeSelections), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        else :
            # Suppression unique
            listeSelections = self.Selection()        
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer la facture n°%d ?") % listeSelections[0].numero, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        # Suppression de la facture
        import UTILS_Facturation
        listeIDfactures = []
        for track in listeSelections :
            listeIDfactures.append(track.IDfacture)
        UTILS_Facturation.SuppressionFacture(listeIDfactures)
        
        # MAJ du listeView
        self.MAJ() 
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"%d facture(s) supprimée(s) avec succès.") % len(listeSelections), _(u"Suppression"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = self.Selection()[0].IDfamille
        IDfacture = self.Selection()[0].IDfacture
        import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDfacture)
        dlg.Destroy()


# -------------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, listview=None):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une facture..."))
        self.ShowSearchButton(True)
        
        if listview != None :
            self.listView = listview
        else :
            self.listView = self.parent.ctrl_listview
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

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "date_edition" : {"mode" : "nombre", "singulier" : _(u"facture"), "pluriel" : _(u"factures"), "alignement" : wx.ALIGN_CENTER},
            "total" : {"mode" : "total"},
            "regle" : {"mode" : "total"},
            "solde" : {"mode" : "total"},
            "soldeActuel" : {"mode" : "total"},
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

        IDcompte_payeur = None
        codesColonnes = ["IDfacture", "date", "numero", "famille", "prelevement", "email", "date_debut", "date_fin", "total", "regle", "solde", "solde_actuel", "date_echeance", "nom_lot"]
        checkColonne = True
        triColonne = "numero"

##        listview = ListView(panel, -1, IDcompte_payeur=IDcompte_payeur, codesColonnes=codesColonnes, checkColonne=checkColonne, triColonne=triColonne, style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER)
##        listview.MAJ() 

        ctrl = ListviewAvecFooter(panel, kwargs={"IDcompte_payeur" : IDcompte_payeur, "codesColonnes" : codesColonnes, "checkColonne" : checkColonne, "triColonne" : triColonne}) 
        listview = ctrl.GetListview()
        listview.MAJ() 

        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(ctrl, 1, wx.ALL|wx.EXPAND, 4)
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
