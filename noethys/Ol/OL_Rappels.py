#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
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
import GestionDB
import datetime
import locale
import FonctionsPerso

from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal

from Utils import UTILS_Titulaires
from Utils import UTILS_Dates
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter




class Track(object):
    def __init__(self, donnees):
        self.IDrappel = donnees["IDrappel"]
        self.numero = donnees["numero"]
        if self.numero == None : self.numero = 0
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.date_edition = donnees["date_edition"]
        self.date_reference = donnees["date_reference"]
        self.IDutilisateur = donnees["IDutilisateur"]
        self.date_min = donnees["date_min"]
        self.date_max = donnees["date_max"]
        self.solde = donnees["solde"]
        if self.solde != 0.0 : 
            self.solde = -self.solde
        self.IDfamille = donnees["IDfamille"]
        self.nomsTitulaires =  donnees["titulaires"]
        self.nomLot =  donnees["nomLot"]
        self.IDtexte = donnees["IDtexte"]
        
        if self.date_edition == None or self.date_min == None :
            self.retard = None
        else :
            self.retard = _(u"%s jours") % (self.date_edition - self.date_max).days
                
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
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnActivated(self,event):
        self.Modifier(None)

    def InitModel(self):
        self.donnees = self.GetTracks()
    
    def SetFiltres(self, filtres=None):
        self.filtres = filtres

    def GetListeRappels(self):
        dictTitulaires = UTILS_Titulaires.GetTitulaires() 

        DB = GestionDB.DB()
        
        # Conditions
        listeConditions = []
        
        if self.IDcompte_payeur != None :
            listeConditions.append("rappels.IDcompte_payeur = %d" % self.IDcompte_payeur)
        
        # 1ère série de filtres
        if self.filtres != None :
            for filtre in self.filtres :
            
                # IDrappel_intervalle
                if filtre["type"] == "IDrappel_intervalle" :
                    listeConditions.append( "(rappels.IDrappel>=%d AND rappels.IDrappel<=%d)" % (filtre["IDrappel_min"], filtre["IDrappel_max"]) )

                # IDrappel_liste
                if filtre["type"] == "IDrappel_liste" :
                    if len(filtre["liste"]) == 0 : listeTemp = "()" 
                    elif len(filtre["liste"]) == 1 : listeTemp = "(%d)" % filtre["liste"][0]
                    else : listeTemp = str(tuple(filtre["liste"]))
                    listeConditions.append( "rappels.IDrappel IN %s" % listeTemp)

                # Lot de rappels
                if filtre["type"] == "lot" :
                    listeConditions.append( "rappels.IDlot=%d" % filtre["IDlot"] )
            
                # Date d'émission
                if filtre["type"] == "date_emission" :
                    listeConditions.append( "(rappels.date_edition>='%s' AND rappels.date_edition<='%s')" % (filtre["date_min"], filtre["date_max"]) )

                # Date de référence
                if filtre["type"] == "date_reference" :
                    listeConditions.append( "(rappels.date_reference>='%s' AND rappels.date_reference<='%s')" % (filtre["date_min"], filtre["date_max"]) )

                # numero_intervalle
                if filtre["type"] == "numero_intervalle" :
                    listeConditions.append( "(rappels.numero>=%d AND rappels.numero<=%d)" % (filtre["numero_min"], filtre["numero_max"]) )

                # numero_liste
                if filtre["type"] == "numero_liste" :
                    if len(filtre["liste"]) == 0 : listeTemp = "()" 
                    elif len(filtre["liste"]) == 1 : listeTemp = "(%d)" % filtre["liste"][0]
                    else : listeTemp = str(tuple(filtre["liste"]))
                    listeConditions.append( "rappels.numero IN %s" % listeTemp)

        if len(listeConditions) > 0 :
            conditions = "WHERE %s" % " AND ".join(listeConditions)
        else :
            conditions = ""


        # Récupération des rappels
        req = """
        SELECT rappels.IDrappel, rappels.numero, rappels.IDcompte_payeur, 
        rappels.date_edition, rappels.date_reference, rappels.IDutilisateur,
        rappels.date_min, rappels.date_max, rappels.solde,
        comptes_payeurs.IDfamille, rappels.IDlot, lots_rappels.nom,
        textes_rappels.IDtexte, textes_rappels.label
        FROM rappels
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = rappels.IDcompte_payeur
        LEFT JOIN lots_rappels ON lots_rappels.IDlot = rappels.IDlot
        LEFT JOIN textes_rappels ON textes_rappels.IDtexte = rappels.IDtexte
        %s
        ORDER BY rappels.date_edition
        ;""" % conditions
        DB.ExecuterReq(req)
        listeRappels = DB.ResultatReq()
                
        # Infos Prélèvement + Envoi par Email des factures
        if self.IDcompte_payeur != None :
            conditions = "WHERE comptes_payeurs.IDcompte_payeur = %d" % self.IDcompte_payeur
        else:
            conditions = ""
        req = """
        SELECT 
        prelevement_activation, prelevement_etab, prelevement_guichet, prelevement_numero, prelevement_cle, prelevement_banque,
        prelevement_individu, prelevement_nom, prelevement_rue, prelevement_cp, prelevement_ville, email_factures,
        comptes_payeurs.IDcompte_payeur
        FROM familles
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = familles.IDfamille
        %s
        ;""" % conditions
        DB.ExecuterReq(req)
        listeInfosFamilles = DB.ResultatReq()
        dictInfosFamilles = {}
        for prelevement_activation, prelevement_etab, prelevement_guichet, prelevement_numero, prelevement_cle, prelevement_banque, prelevement_individu, prelevement_nom, prelevement_rue, prelevement_cp, prelevement_ville, email_factures, IDcompte_payeur in listeInfosFamilles :
            dictInfosFamilles[IDcompte_payeur] = {
                    "prelevement_activation" : prelevement_activation, "prelevement_etab" : prelevement_etab, "prelevement_guichet" : prelevement_guichet, 
                    "prelevement_numero" : prelevement_numero, "prelevement_cle" : prelevement_cle, "prelevement_banque" : prelevement_banque, 
                    "prelevement_individu" : prelevement_individu, "prelevement_nom" : prelevement_nom, "prelevement_rue" : prelevement_rue, 
                    "prelevement_cp" : prelevement_cp, "prelevement_ville" : prelevement_ville, "email_factures" : email_factures, 
                    }
        
        DB.Close() 
                        
        listeResultats = []
        for IDrappel, numero, IDcompte_payeur, date_edition, date_reference, IDutilisateur, date_min, date_max, solde, IDfamille, IDlot, nomLot, IDtexte, labeltexte in listeRappels :
            
            if numero == None : numero = 0
            date_edition = UTILS_Dates.DateEngEnDateDD(date_edition) 
            date_min = UTILS_Dates.DateEngEnDateDD(date_min)
            date_max = UTILS_Dates.DateEngEnDateDD(date_max)
            date_reference = UTILS_Dates.DateEngEnDateDD(date_reference)
            if dictTitulaires.has_key(IDfamille):
                titulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
            else :
                titulaires = _(u"Titulaires inconnus")

            dictTemp = {
                "IDrappel" : IDrappel, "numero" : numero, "IDcompte_payeur" : IDcompte_payeur, "date_edition" : date_edition, "date_reference" : date_reference,
                "IDutilisateur" : IDutilisateur, "date_min" : date_min, "date_max" : date_max, "solde" : solde, "IDfamille" : IDfamille, "titulaires" : titulaires, 
                "IDlot" : IDlot, "nomLot" : nomLot, "IDtexte" : IDtexte, "labelTexte" : labeltexte,
                }
            
            if dictInfosFamilles.has_key(IDcompte_payeur) :
                dictTemp.update(dictInfosFamilles[IDcompte_payeur])

            valide = True
            
            # 2ème série de filtres
            if self.filtres != None :
                for filtre in self.filtres :
            
                    # IDrappel_intervalle
                    if filtre["type"] == "solde" :
                        if self.ComparateurFiltre(-solde, filtre["operateur"], filtre["montant"]) == False :
                            valide = False

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
        listeDonnees = self.GetListeRappels() 
    
        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item["IDrappel"] :
                    self.selectionTrack = track
        return listeListeView


    def InitObjectListView(self):
        
        # ImageList
        self.imgEmail = self.AddNamedImages("email", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG))

        def GetImageEmail(track):
            if track.email == True :
                return self.imgEmail
        
        def FormateNumero(numero):
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
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = "#FFFFFF" # Vert

        # Paramètres ListView
        self.useExpansionColumn = True
        
        dictColonnes = {
            "IDrappel" : ColumnDefn(u"", "left", 0, "IDrappel", typeDonnee="entier"),
            "date_edition" : ColumnDefn(_(u"Date d'édition"), "centre", 80, "date_edition", typeDonnee="date", stringConverter=FormateDate),
            "date_reference" : ColumnDefn(_(u"Date de référence"), "centre", 80, "date_reference", typeDonnee="date", stringConverter=FormateDate),
            "numero" : ColumnDefn(u"N°", "centre", 65, "numero", typeDonnee="entier", stringConverter=FormateNumero),
            "famille" : ColumnDefn(_(u"Famille"), "left", 180, "nomsTitulaires", typeDonnee="texte"),
            "date_min" : ColumnDefn(_(u"Date min"), "centre", 80, "date_min", typeDonnee="date", stringConverter=FormateDate),
            "date_max" : ColumnDefn(_(u"Date max"), "centre", 80, "date_max", typeDonnee="date", stringConverter=FormateDate),
            "solde" : ColumnDefn(_(u"Solde"), "right", 65, "solde", typeDonnee="montant", stringConverter=FormateMontant),
            "nom_lot" : ColumnDefn(_(u"Lot"), "left", 150, "nomLot", typeDonnee="texte"),
            "labelTexte" : ColumnDefn(_(u"Texte"), "left", 150, "labelTexte", typeDonnee="texte"),
            "email" : ColumnDefn(u"E", "left", 20, "", imageGetter=GetImageEmail),
            "retard" : ColumnDefn(_(u"Retard"), "left", 80, "retard", typeDonnee="texte"),
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

        self.SetEmptyListMsg(_(u"Aucune lettre de rappel"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
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
            ID = self.Selection()[0].IDrappel
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Rééditer la lettre
        item = wx.MenuItem(menuPop, 60, _(u"Aperçu PDF de la lettre de rappel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Reedition, id=60)

        # Item Envoyer la lettre par Email
        item = wx.MenuItem(menuPop, 90, _(u"Envoyer la lettre de rappel par Email"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EnvoyerEmail, id=90)
        
        menuPop.AppendSeparator()
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 : item.Enable(False)

        menuPop.AppendSeparator()
        
        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        intro, total = self.GetTextesImpression()
        dictParametres = {
            "titre" : _(u"Liste des lettres de rappel"),
            "intro" : intro,
            "total" : total,
            "orientation" : wx.PORTRAIT,
            }
        return dictParametres

    def Reedition(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune lettre à imprimer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDrappel = self.Selection()[0].IDrappel
        from Utils import UTILS_Rappels
        facturation = UTILS_Rappels.Facturation()
        facturation.Impression(listeRappels=[IDrappel,])
    
    def EnvoyerEmail(self, event):
        """ Envoyer la lettre par Email """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune lettre de rappel à envoyer par Email !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        # Envoi du mail
        from Utils import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=track.IDfamille, nomDoc=FonctionsPerso.GenerationNomDoc("RAPPEL", "pdf") , categorie="rappel")
    
    def CreationPDF(self, nomDoc="", afficherDoc=True):        
        """ Création du PDF pour Email """
        IDrappel = self.Selection()[0].IDrappel
        from Utils import UTILS_Rappels
        facturation = UTILS_Rappels.Facturation()
        resultat = facturation.Impression(listeRappels=[IDrappel,], nomDoc=nomDoc, afficherDoc=False)
        if resultat == False : 
            return False
        dictChampsFusion, dictPieces = resultat
        return dictChampsFusion[IDrappel]

    def GetTextesImpression(self):
        total = _(u"%d factures. ") % len(self.donnees)
        if self.filtres != None :
            from Dlg.DLG_Filtres_rappels import GetTexteFiltres 
            intro = total + _(u"Filtres de sélection : %s") % GetTexteFiltres(self.filtres)
        else :
            intro = None
        return intro, total

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
        if self.IDcompte_payeur == None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_rappels", "supprimer") == False : return
        
        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune lettre de rappel à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if len(self.GetTracksCoches()) > 0 :
            # Suppression multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer les %d lettres de rappel cochées ?") % len(listeSelections), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        else :
            # Suppression unique
            listeSelections = self.Selection()        
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer la lettre de rappel n°%d ?") % listeSelections[0].numero, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        # Suppression des lettres de rappel
        listeIDrappels = []
        for track in listeSelections :
            listeIDrappels.append(track.IDrappel)

        dlgAttente = wx.BusyInfo(_(u"Suppression des lettres de rappel en cours..."), None)
        wx.Yield() 
        DB = GestionDB.DB()
        for IDrappel in listeIDrappels :
            DB.ReqDEL("rappels", "IDrappel", IDrappel)
        DB.Close() 
        del dlgAttente
        
        # MAJ du listeView
        self.MAJ() 
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"%d lettres(s) de rappel supprimée(s) avec succès.") % len(listeSelections), _(u"Suppression"), wx.OK | wx.ICON_INFORMATION)
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
        IDrappel = self.Selection()[0].IDrappel
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDrappel)
        dlg.Destroy()


# -------------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, listview=None):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une lettre de rappel..."))
        self.ShowSearchButton(True)
        
        if listview != None :
            self.listView = listview
        else :
            self.listView = self.parent.ctrl_listview
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




class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nomsTitulaires" : {"mode" : "nombre", "singulier" : "rappel", "pluriel" : "rappels", "alignement" : wx.ALIGN_CENTER},
            "solde" : {"mode" : "total"},
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
        codesColonnes = ["IDrappel", "date_edition", "date_reference", "numero", "famille", "date_min", "date_max", "retard", "email", "solde", "nom_lot", "labelTexte"]
        checkColonne = True
        triColonne = "numero"

        self.myOlv = ListView(panel, -1, IDcompte_payeur=IDcompte_payeur, codesColonnes=codesColonnes, checkColonne=checkColonne, triColonne=triColonne, style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.myOlv.MAJ() 
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
