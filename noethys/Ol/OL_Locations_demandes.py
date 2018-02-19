#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
import copy
import GestionDB
from Utils import UTILS_Titulaires
from Utils import UTILS_Interface
from Utils import UTILS_Questionnaires
from Utils import UTILS_Texte
from Utils import UTILS_Locations
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter
import FonctionsPerso




class Track(object):
    def __init__(self, listview=None, donnees=None):
        self.IDdemande = donnees[0]
        self.date = donnees[1]
        self.IDfamille = donnees[2]
        self.observations = donnees[3]

        # Catégories
        self.categories = UTILS_Texte.ConvertStrToListe(donnees[4], siVide=[])
        liste_labels = []
        for IDcategorie in self.categories :
            if listview.dictCategories.has_key(IDcategorie) :
                liste_labels.append(listview.dictCategories[IDcategorie])
        self.texte_categories = ", ".join(liste_labels)

        # Produits
        self.produits = UTILS_Texte.ConvertStrToListe(donnees[5], siVide=[])
        liste_labels = []
        for IDproduit in self.produits :
            if listview.dictProduits.has_key(IDproduit) :
                liste_labels.append(listview.dictProduits[IDproduit])
        self.texte_produits = ", ".join(liste_labels)

        # Statut
        self.statut = donnees[6]

        # Position
        self.position = None

        # Vérifie s'il y a des propositions de produits
        if self.statut == "refusee" :
            self.texte_statut = _(u"Refusée")
        elif self.statut == "attribuee" :
            self.texte_statut = _(u"Demande satisfaite")
        elif self.statut == "attente" :
            if listview.dictPropositions.has_key(self.IDdemande) :

                # Recherche disponibilités
                listeProduitsProposes = listview.dictPropositions[self.IDdemande]
                if len(listeProduitsProposes) == 0 :
                    self.texte_statut = _(u"En attente")
                elif len(listeProduitsProposes) == 1 :
                    self.texte_statut = _(u"1 produit disponible")
                else :
                    self.texte_statut = _(u"%d produits disponibles") % len(listeProduitsProposes)
                self.statut = "disponibilite"

                # Recherche meilleure position
                self.position = UTILS_Locations.GetMeilleurePosition(dictPropositions=listview.dictPropositions, IDdemande=self.IDdemande)
            else :
                self.texte_statut = _(u"En attente")

        # Formatage date
        if isinstance(self.date, str) or isinstance(self.date, unicode) :
            self.date = datetime.datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S")

        # Récupération des réponses des questionnaires
        for dictQuestion in listview.liste_questions :
            setattr(self, "question_%d" % dictQuestion["IDquestion"], listview.GetReponse(dictQuestion["IDquestion"], self.IDdemande))
        
        # Famille
        if listview.IDfamille == None :
            self.nomTitulaires = listview.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
            self.rue = listview.dict_titulaires[self.IDfamille]["adresse"]["rue"]
            self.cp = listview.dict_titulaires[self.IDfamille]["adresse"]["cp"]
            self.ville = listview.dict_titulaires[self.IDfamille]["adresse"]["ville"]


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDfamille = kwds.pop("IDfamille", None)
        self.checkColonne = kwds.pop("checkColonne", False)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.liste_options = None
        self.regroupement = None
        self.afficher_uniquement_actives = False

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        # Initialisation des questionnaires
        categorie = "location_demande"
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        self.liste_questions = self.UtilsQuestionnaires.GetQuestions(type=categorie)
        self.dict_questionnaires = self.UtilsQuestionnaires.GetReponses(type=categorie)

        # Importation des titulaires de dossier
        if self.IDfamille == None:
            self.dict_titulaires = UTILS_Titulaires.GetTitulaires()

        # Importation des propositions de locations
        self.dictPropositions = UTILS_Locations.GetPropositionsLocations()

        # MAJ du listview
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        DB = GestionDB.DB()

        # Importation des catégories de produits
        req = """SELECT IDcategorie, nom
        FROM produits_categories;"""
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        self.dictCategories = {}
        for IDcategorie, nom in listeCategories :
            self.dictCategories[IDcategorie] = nom

        # Importation des produits
        req = """SELECT IDproduit, nom
        FROM produits;"""
        DB.ExecuterReq(req)
        listeProduits = DB.ResultatReq()
        self.dictProduits = {}
        for IDproduit, nom in listeProduits :
            self.dictProduits[IDproduit] = nom

        # Filtre famille
        conditions = []
        if self.IDfamille != None :
            conditions.append("IDfamille=%d" % self.IDfamille)

        # Filtres de liste
        if self.liste_options != None :
            liste_options = copy.deepcopy(self.liste_options)
            liste_options = ['attente' if statut == 'disponibilite' else statut for statut in liste_options]
            if len(liste_options) == 0 : option = "statut IN ('')"
            elif len(liste_options) == 1 : option = "statut in ('%s')" % liste_options[0]
            else : option = "statut IN %s" % str(tuple(liste_options))
            conditions.append(option)

        if self.afficher_uniquement_actives == True :
            conditions.append("statut IN ('attente', 'disponibilite')")

        if len(conditions) > 0 :
            conditions = "WHERE %s" % " AND ".join(conditions)
        else :
            conditions = ""

        req = """SELECT IDdemande, date, IDfamille, observations, categories, produits, statut
        FROM locations_demandes
        %s;""" % conditions
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeListeView = []
        for item in listeDonnees :
            track = Track(listview=self, donnees=item)

            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if self.liste_options != None :
                if track.statut not in self.liste_options :
                    valide = False
            if valide == True :
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        # Préparation de la listeImages
        self.AddNamedImages("attente", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("refusee", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer_2.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("attribuee", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok4.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("disponibilite", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok4_orange.png"), wx.BITMAP_TYPE_PNG))

        def GetImageStatut(track):
            if track.statut == "attente" :
                return "attente"
            elif track.statut == "refusee" :
                return "refusee"
            elif track.statut == "attribuee" :
                return "attribuee"
            elif track.statut == "disponibilite" :
                return "disponibilite"
            else :
                return None

        def FormateDate(date):
            if date == None :
                return _(u"Non définie")
            else :
                return datetime.datetime.strftime(date, "%d/%m/%Y - %Hh%M")

        def FormatePosition(position):
            if position == None :
                return _(u"")
            elif position == 1 :
                return _(u"1er")
            else :
                return _(u"%dème") % position

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDdemande", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), "left", 130, "date", typeDonnee="date", stringConverter=FormateDate),
            ]

        if self.IDfamille == None :
            liste_Colonnes.extend([
                ColumnDefn(_(u"Nom du demandeur"), 'left', 210, "nomTitulaires", typeDonnee="texte"),
                # ColumnDefn(_(u"Rue"), 'left', 200, "rue", typeDonnee="texte"),
                # ColumnDefn(_(u"C.P."), 'left', 70, "cp", typeDonnee="texte"),
                # ColumnDefn(_(u"Ville"), 'left', 150, "ville", typeDonnee="texte"),
                ])

        liste_Colonnes.extend([
            ColumnDefn(_(u"Statut de la demande"), 'left', 170, "texte_statut", typeDonnee="texte", imageGetter=GetImageStatut),
            ColumnDefn(_(u"Position"), 'left', 80, "position", typeDonnee="entier", stringConverter=FormatePosition),
            ColumnDefn(_(u"Catégories demandées"), 'left', 200, "texte_categories", typeDonnee="texte"),
            ColumnDefn(_(u"Produits demandés"), 'left', 200, "texte_produits", typeDonnee="texte"),
            ColumnDefn(_(u"Notes"), 'left', 200, "observations", typeDonnee="texte"),
            ])

        # Ajout des questions des questionnaires
        for dictQuestion in self.liste_questions :
            if dictQuestion["filtre"] == "texte" : typeDonnee = "texte"
            elif dictQuestion["filtre"] == "entier" : typeDonnee = "entier"
            elif dictQuestion["filtre"] == "montant" : typeDonnee = "montant"
            elif dictQuestion["filtre"] == "choix" : typeDonnee = "texte"
            elif dictQuestion["filtre"] == "coche" : typeDonnee = "texte"
            elif dictQuestion["filtre"] == "date" : typeDonnee = "date"
            else : typeDonnee = "texte"
            liste_Colonnes.append(ColumnDefn(dictQuestion["label"], "left", 150, "question_%d" % dictQuestion["IDquestion"], typeDonnee=typeDonnee))

        self.SetColumns(liste_Colonnes)

        if self.checkColonne == True :
            self.CreateCheckStateColumn(1)
            self.SetSortColumn(self.columns[2])
        else :
            self.SetSortColumn(self.columns[1])

        # Regroupement
        # if hasattr(self, "ctrl_regroupement") :
        #     self.ctrl_regroupement.MAJ(listview=self)
        # if self.regroupement != None:
        #     self.SetAlwaysGroupByColumn(self.regroupement)
        #     self.SetShowGroups(True)
        #     self.useExpansionColumn = False
        #     self.SetShowItemCounts(True)
        # else:
        #     self.SetShowGroups(False)
        #     self.useExpansionColumn = False

        self.SetEmptyListMsg(_(u"Aucune demande de location"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
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

    def GetReponse(self, IDquestion=None, ID=None):
        if self.dict_questionnaires.has_key(IDquestion) :
            if self.dict_questionnaires[IDquestion].has_key(ID) :
                return self.dict_questionnaires[IDquestion][ID]
        return u""

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()

        # Item Imprimer
        item = wx.MenuItem(menuPop, 100, _(u"Imprimer la demande"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ImprimerPDF, id=100)
        if noSelection == True : item.Enable(False)

        # Item Envoyer par Email
        item = wx.MenuItem(menuPop, 110, _(u"Envoyer la demande par Email"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EnvoyerEmail, id=110)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des demandes de locations"))

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event):
        from Dlg import DLG_Saisie_location_demande
        dlg = DLG_Saisie_location_demande.Dialog(self, IDdemande=None, IDfamille=self.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(dlg.GetIDdemande() )
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune demande à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        from Dlg import DLG_Saisie_location_demande
        dlg = DLG_Saisie_location_demande.Dialog(self, IDdemande=track.IDdemande, IDfamille=self.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(dlg.GetIDdemande() )
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune demande à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]

        # Suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette demande de location ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("locations_demandes", "IDdemande", track.IDdemande)
            DB.ExecuterReq("DELETE FROM questionnaire_reponses WHERE type='location_demande' AND IDdonnee=%d;" % track.IDdemande)
            DB.Close()
            self.MAJ()
        dlg.Destroy()
    
    def GetID(self):
        track = self.Selection()[0]
        return track.IDdemande

    def SetID(self, IDdemande=None):
        for track in self.donnees :
            if track.IDdemande == IDdemande :
                self.SelectObject(track, deselectOthers=True, ensureVisible=True)
                return True
        return False

    def SetOptions(self, liste_options=[]):
        self.liste_options = liste_options

    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def ImprimerPDF(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune demande à imprimer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdemande = self.Selection()[0].IDdemande
        from Utils import UTILS_Locations_demandes
        demande = UTILS_Locations_demandes.Demande()
        demande.Impression(listeDemandes=[IDdemande,])

    def EnvoyerEmail(self, event):
        """ Envoyer la location par Email """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune demande à envoyer par Email !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        # Envoi du mail
        from Utils import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=track.IDfamille, nomDoc=FonctionsPerso.GenerationNomDoc("DEMANDELOCATION", "pdf") , categorie="location_demande")

    def CreationPDF(self, nomDoc="", afficherDoc=True):
        """ Création du PDF pour Email """
        IDdemande = self.Selection()[0].IDdemande
        from Utils import UTILS_Locations_demandes
        demande = UTILS_Locations_demandes.Demande()
        resultat = demande.Impression(listeDemandes=[IDdemande,], nomDoc=nomDoc, afficherDoc=False)
        if resultat == False :
            return False
        dictChampsFusion, dictPieces = resultat
        return dictChampsFusion[IDdemande]


# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "date": {"mode": "nombre", "singulier": _(u"demande"), "pluriel": _(u"demandes"), "alignement": wx.ALIGN_CENTER},
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
        self.myOlv = ListView(panel, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ()
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 200))
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
