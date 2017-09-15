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
from Utils.UTILS_Traduction import _
import wx
import datetime
import GestionDB
from Utils import UTILS_Interface
from Utils import UTILS_Questionnaires
from Utils import UTILS_Locations
from Utils import UTILS_Titulaires

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


class Track(object):
    def __init__(self, parent=None, donnees=None):
        self.IDproduit = donnees[0]
        self.nom = donnees[1]
        self.observations = donnees[2]
        self.nomCategorie = donnees[3]
        self.position = None

        # Recherche si le produit est en cours de location
        if parent.afficher_locations == True :
            if parent.dictLocations.has_key(self.IDproduit):
                self.statut = "indisponible"
                dictLocation = parent.dictLocations[self.IDproduit]
                self.IDfamille = dictLocation["IDfamille"]
                self.nomTitulaires = parent.dict_titulaires[self.IDfamille]["titulairesSansCivilite"]
                self.date_debut = dictLocation["date_debut"]
                self.date_fin = dictLocation["date_fin"]
            else :
                self.statut = "disponible"

        # Récupération des réponses des questionnaires
        for dictQuestion in parent.liste_questions :
            setattr(self, "question_%d" % dictQuestion["IDquestion"], parent.GetReponse(dictQuestion["IDquestion"], self.IDproduit))

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selection_multiple = kwds.pop("selection_multiple", False)
        self.afficher_locations = kwds.pop("afficher_locations", True)
        self.afficher_detail_location = kwds.pop("afficher_detail_location", True)
        self.on_double_click = kwds.pop("on_double_click", "modification")
        self.afficher_uniquement_disponibles = False
        self.coche_uniquement_disponibles = False
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.filtreListeID = None
        self.dictPositions = None

        # Importation des titulaires
        if self.afficher_locations == True :
            self.dict_titulaires = UTILS_Titulaires.GetTitulaires()

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        if self.on_double_click == "modification" :
            self.Modifier(None)
        elif self.on_double_click == "consultation" :
            self.Consulter(None)
        else :
            return

    def InitModel(self):
        # MAJ du listview
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None

        # Initialisation des questionnaires
        categorie = "produit"
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        self.liste_questions = self.UtilsQuestionnaires.GetQuestions(type=categorie)
        self.dict_questionnaires = self.UtilsQuestionnaires.GetReponses(type=categorie)

        DB = GestionDB.DB()

        # Importation des locations en cours
        if self.afficher_locations == True :
            self.dictLocations = UTILS_Locations.GetProduitsLoues(DB=DB)

        # Importation des produits
        if self.filtreListeID == None :
            condition = ""
        else :
            if len(self.filtreListeID) == 0: condition = "WHERE produits.IDproduit IN ()"
            elif len(self.filtreListeID) == 1: condition = "WHERE produits.IDproduit IN (%d)" % self.filtreListeID[0]
            else: condition = "WHERE produits.IDproduit IN %s" % str(tuple(self.filtreListeID))

        req = """SELECT IDproduit, produits.nom, produits.observations, produits_categories.nom
        FROM produits
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        %s;""" % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeListeView = []
        for item in listeDonnees :
            track = Track(parent=self, donnees=item)

            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False

            # Mémorisation position
            if self.dictPositions != None and self.dictPositions.has_key(track.IDproduit):
                track.position = self.dictPositions[track.IDproduit]

            # Coche afficher uniquement les disponibles
            if self.coche_uniquement_disponibles == True and track.statut != "disponible":
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
        self.AddNamedImages("indisponible", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("disponible", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok4.png"), wx.BITMAP_TYPE_PNG))

        def GetImageStatut(track):
            if track.statut == "disponible" :
                return "disponible"
            elif track.statut == "indisponible" :
                return "indisponible"
            else :
                return None

        def FormateDate(date):
            if date == None :
                return _(u"")
            else :
                return datetime.datetime.strftime(date, "%d/%m/%Y - %Hh%M")

        def FormatePosition(position):
            if position == None :
                return _(u"")
            elif position == 1 :
                return _(u"1er")
            else :
                return _(u"%dème") % position

        def FormateStatut(statut):
            if statut == "disponible" :
                return _(u"Disponible")
            if statut == "indisponible" :
                return _(u"Indisponible")


        dict_colonnes = {
            "IDproduit" : ColumnDefn(u"", "left", 0, "IDproduit", typeDonnee="entier"),
            "nom": ColumnDefn(_(u"Nom"), 'left', 170, "nom", typeDonnee="texte"),
            "nomCategorie": ColumnDefn(_(u"Catégorie"), 'left', 170, "nomCategorie", typeDonnee="texte"),
            "statut": ColumnDefn(_(u"Statut"), "left", 100, "statut", typeDonnee="texte", stringConverter=FormateStatut, imageGetter=GetImageStatut),
            "nomTitulaires": ColumnDefn(_(u"Loueur"), "left", 200, "nomTitulaires", typeDonnee="texte"),
            "date_debut": ColumnDefn(_(u"Début"), "left", 120, "date_debut", typeDonnee="texte", stringConverter=FormateDate),
            "date_fin": ColumnDefn(_(u"Fin"), "left", 120, "date_fin", typeDonnee="texte", stringConverter=FormateDate),
            "position": ColumnDefn(u"Position", "left", 80, "position", typeDonnee="entier", stringConverter=FormatePosition),
        }

        if self.afficher_locations == True:
            if self.afficher_detail_location == True :
                liste_temp = ["IDproduit", "nom", "nomCategorie", "statut", "nomTitulaires", "date_debut", "date_fin"]
            else :
                liste_temp = ["IDproduit", "nom", "nomCategorie", "statut"]
        else :
            liste_temp = ["IDproduit", "nom", "nomCategorie"]

        if self.dictPositions != None :
            liste_temp.append("position")

        liste_Colonnes = []
        for code in liste_temp :
            liste_Colonnes.append(dict_colonnes[code])

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
        if self.selection_multiple == True :
            self.CreateCheckStateColumn(0)

        self.SetEmptyListMsg(_(u"Aucun produit"))
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
        menuPop = wx.Menu()

        if self.on_double_click == "modification":

            # Item Ajouter
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
            if noSelection == True: item.Enable(False)

            # Item Supprimer
            item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
            if noSelection == True: item.Enable(False)

        if self.on_double_click == "consultation":
            # Item Consulter
            item = wx.MenuItem(menuPop, 70, _(u"Consulter la fiche produit"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Consulter, id=70)
            if noSelection == True: item.Enable(False)

        menuPop.AppendSeparator()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des produits"))

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event):
        from Dlg import DLG_Saisie_produit
        dlg = DLG_Saisie_produit.Dialog(self, IDproduit=None)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(dlg.GetIDproduit() )
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun produit à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        from Dlg import DLG_Saisie_produit
        dlg = DLG_Saisie_produit.Dialog(self, IDproduit=track.IDproduit)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(dlg.GetIDproduit() )
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun produit à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        
        # Vérifie que ce produit n'a pas déjà été attribué à une location
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDlocation)
        FROM locations 
        WHERE IDproduit=%d
        ;""" % track.IDproduit
        DB.ExecuterReq(req)
        nbreLocationsRattachees = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreLocationsRattachees > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce produit a déjà été attribué à %d location(s).\n\nVous ne pouvez donc pas le supprimer !") % nbreLocationsRattachees, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce produit ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("produits", "IDproduit", track.IDproduit)
            DB.ExecuterReq("DELETE FROM questionnaire_reponses WHERE type='produit' AND IDdonnee=%d;" % track.IDproduit)
            DB.Close()
            self.MAJ()
        dlg.Destroy()
    
    def GetID(self):
        if len(self.Selection()) > 0 :
            return self.Selection()[0].IDproduit
        else :
            return None

    def SetID(self, IDproduit=None):
        for track in self.donnees :
            if track.IDproduit == IDproduit :
                self.SelectObject(track, deselectOthers=True, ensureVisible=True)
                return True
        return False

    def GetListeProduits(self):
        liste_produits = []
        for track in self.GetCheckedObjects():
            liste_produits.append(track.IDproduit)
        return liste_produits

    def SetListeProduits(self, liste_produits=[]):
        if self.GetFilter() != None:
            listeObjets = self.GetFilteredObjects()
        else:
            listeObjets = self.GetObjects()
        for track in listeObjets:
            if track.IDproduit in liste_produits :
                self.Check(track)
                self.RefreshObject(track)

    def SetFiltreIDproduit(self, listeID=[]):
        self.filtreListeID = listeID
        self.MAJ()

    def SetDictPropositions(self, dictPropositions={}, IDdemande=False):
        listeID = []
        self.dictPositions = {}
        for IDdemandeTemp, liste_produits in dictPropositions.iteritems():
            if IDdemande == False or IDdemande == IDdemandeTemp :
                for dictProduit in liste_produits:
                    if dictProduit["disponible"] == True or self.afficher_uniquement_disponibles == False :
                        listeID.append(dictProduit["IDproduit"])
                        self.dictPositions[dictProduit["IDproduit"]] = dictProduit["position"]

        # Affiche meilleure position
        position = UTILS_Locations.GetMeilleurePosition(dictPropositions=dictPropositions, IDdemande=IDdemande)
        if position == 1 :
            texte_position = u"1er"
        elif position > 1 :
            texte_position = u"%dème" % position
        else :
            texte_position = u""

        # Met à jour la liste des propositions
        self.SetFiltreIDproduit(listeID)

        # Création d'un label
        if len(listeID) == 0 :
            texte = _(u"Aucun produit proposé.")
        elif len(listeID) == 1 :
            texte = _(u"1 produit proposé (meilleure position : %s) :") % texte_position
        else :
            texte = _(u"%d produits proposés (meilleure position : %s) :") % (len(listeID), texte_position)
        return texte


    def Consulter(self, event=None):
        """ Consulter la fiche produit """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun produit à consulter dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Ouverture de la fiche produit
        track = self.Selection()[0]
        from Dlg import DLG_Fiche_produit
        dlg = DLG_Fiche_produit.Dialog(self, IDproduit=track.IDproduit)
        dlg.ShowModal()
        dlg.Destroy()
        self.MAJ(track.IDproduit)

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, selection_multiple=True, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
