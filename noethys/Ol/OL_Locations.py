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
import FonctionsPerso
from Utils import UTILS_Titulaires
from Utils import UTILS_Interface
from Utils import UTILS_Questionnaires
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter

def Supprimer_location(parent, IDlocation=None):
    # Vérifie si les prestations de cette location sont déjà facturées
    DB = GestionDB.DB()
    req = """SELECT
    IDprestation, IDfacture
    FROM prestations 
    WHERE categorie="location" and IDdonnee=%d AND IDfacture IS NOT NULL;""" % IDlocation
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq()
    DB.Close()
    listeIDprestations = []
    for IDprestation, IDfacture in listePrestations:
        listeIDprestations.append(IDprestation)
    if len(listePrestations) > 0:
        dlg = wx.MessageDialog(parent, _(u"Vous ne pouvez pas supprimer cette location car elle est déjà associée à %d prestations facturées !") % len(listePrestations), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return False

    # Suppression
    dlg = wx.MessageDialog(parent, _(u"Souhaitez-vous vraiment supprimer cette location ?"), _(u"Suppression"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION)
    if dlg.ShowModal() == wx.ID_YES:
        DB = GestionDB.DB()
        DB.ReqDEL("locations", "IDlocation", IDlocation)
        DB.ExecuterReq("DELETE FROM questionnaire_reponses WHERE type='location' AND IDdonnee=%d;" % IDlocation)
        DB.ReqMAJ("locations_demandes", [("statut", "attente"), ], "IDlocation", IDlocation)
        DB.ReqMAJ("locations_demandes", [("IDlocation", None), ], "IDlocation", IDlocation)
        DB.ExecuterReq("DELETE FROM prestations WHERE categorie='location' AND IDdonnee=%d;" % IDlocation)
        for IDprestation in listeIDprestations:
            DB.ReqDEL("ventilation", "IDprestation", IDprestation)
        DB.Close()
    dlg.Destroy()

    return True



class Track(object):
    def __init__(self, listview=None, donnees=None):
        self.IDlocation = donnees[0]
        self.IDfamille = donnees[1]
        self.IDproduit = donnees[2]
        self.observations = donnees[3]
        self.date_debut = donnees[4]
        self.date_fin = donnees[5]
        self.quantite = donnees[6]
        self.nomProduit = donnees[7]
        self.nomCategorie = donnees[8]

        if self.quantite == None :
            self.quantite = 1

        # Période
        if isinstance(self.date_debut, str) or isinstance(self.date_debut, unicode) :
            self.date_debut = datetime.datetime.strptime(self.date_debut, "%Y-%m-%d %H:%M:%S")

        if isinstance(self.date_fin, str) or isinstance(self.date_fin, unicode) :
            self.date_fin = datetime.datetime.strptime(self.date_fin, "%Y-%m-%d %H:%M:%S")

        # Récupération des réponses des questionnaires
        for dictQuestion in listview.liste_questions :
            setattr(self, "question_%d" % dictQuestion["IDquestion"], listview.GetReponse(dictQuestion["IDquestion"], self.IDproduit))

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
        self.IDproduit = kwds.pop("IDproduit", None)
        self.checkColonne = kwds.pop("checkColonne", False)
        self.afficher_uniquement_actives = kwds.pop("afficher_uniquement_actives", False)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.dirty = False

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
        categorie = "location"
        self.UtilsQuestionnaires = UTILS_Questionnaires.Questionnaires()
        self.liste_questions = self.UtilsQuestionnaires.GetQuestions(type=categorie)
        self.dict_questionnaires = self.UtilsQuestionnaires.GetReponses(type=categorie)

        # MAJ du listview
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        liste_conditions = []

        if self.IDfamille != None :
            liste_conditions.append("IDfamille=%d" % self.IDfamille)
        if self.IDproduit != None :
            liste_conditions.append("locations.IDproduit=%d" % self.IDproduit)
        if self.afficher_uniquement_actives == True :
            today = datetime.datetime.now()
            liste_conditions.append("locations.date_debut<='%s' AND (locations.date_fin IS NULL OR locations.date_fin>='%s')" % (today, today))

        if len(liste_conditions) > 0 :
            conditions = "WHERE %s" % " AND ".join(liste_conditions)
        else :
            conditions = ""

        listeID = None
        db = GestionDB.DB()
        req = """SELECT locations.IDlocation, locations.IDfamille, locations.IDproduit, 
        locations.observations, locations.date_debut, locations.date_fin, locations.quantite,
        produits.nom, 
        produits_categories.nom
        FROM locations
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        %s;""" % conditions
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(listview=self, donnees=item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateDate(date):
            if date == None :
                return _(u"Non définie")
            else :
                return datetime.datetime.strftime(date, "%d/%m/%Y - %Hh%M")

        dict_colonnes = {
            "IDlocation" : ColumnDefn(u"", "left", 0, "IDlocation", typeDonnee="entier"),
            "date_debut" : ColumnDefn(_(u"Début"), "left", 130, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            "date_fin" : ColumnDefn(_(u"Fin"), "left", 130, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            "nomProduit" : ColumnDefn(_(u"Nom du produit"), 'left', 200, "nomProduit", typeDonnee="texte"),
            "nomCategorie" : ColumnDefn(_(u"Catégorie du produit"), 'left', 200, "nomCategorie", typeDonnee="texte"),
            "quantite": ColumnDefn(u"Qté", "left", 60, "quantite", typeDonnee="entier"),
            "nomTitulaires" : ColumnDefn(_(u"Nom"), 'left', 270, "nomTitulaires", typeDonnee="texte"),
            "rue" : ColumnDefn(_(u"Rue"), 'left', 200, "rue", typeDonnee="texte"),
            "cp" : ColumnDefn(_(u"C.P."), 'left', 70, "cp", typeDonnee="texte"),
            "ville" : ColumnDefn(_(u"Ville"), 'left', 150, "ville", typeDonnee="texte"),
            }

        liste_temp = ["IDlocation", "date_debut", "date_fin", "nomProduit", "nomCategorie", "quantite", "nomTitulaires", "rue", "cp", "ville"]

        if self.IDfamille != None :
            liste_temp = ["IDlocation", "date_debut", "date_fin", "nomProduit", "nomCategorie", "quantite"]

        if self.IDproduit != None :
            liste_temp = ["IDlocation", "date_debut", "date_fin", "quantite", "nomTitulaires", "rue", "cp", "ville"]

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
        if self.checkColonne == True :
            self.CreateCheckStateColumn(1)
            self.SetSortColumn(self.columns[2])
        else :
            self.SetSortColumn(self.columns[1])

        self.SetEmptyListMsg(_(u"Aucune location"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))

        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        if self.IDfamille == None:
            self.dict_titulaires = UTILS_Titulaires.GetTitulaires()
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
        item = wx.MenuItem(menuPop, 100, _(u"Imprimer la location"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ImprimerPDF, id=100)
        if noSelection == True : item.Enable(False)

        # Item Envoyer par Email
        item = wx.MenuItem(menuPop, 110, _(u"Envoyer la location par Email"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EnvoyerEmail, id=110)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des locations"))

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event):
        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self, IDlocation=None, IDfamille=self.IDfamille, IDproduit=self.IDproduit)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(dlg.GetIDlocation())
            self.dirty = True
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune location à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        from Dlg import DLG_Saisie_location
        dlg = DLG_Saisie_location.Dialog(self, IDlocation=track.IDlocation, IDfamille=self.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(dlg.GetIDlocation())
            self.dirty = True
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune location à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        resultat = Supprimer_location(self, IDlocation=track.IDlocation)
        if resultat == True :
            self.MAJ()
            self.dirty = True

    def ImprimerPDF(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune location à imprimer !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDlocation = self.Selection()[0].IDlocation
        from Utils import UTILS_Locations
        location = UTILS_Locations.Location()
        location.Impression(listeLocations=[IDlocation,])

    def EnvoyerEmail(self, event):
        """ Envoyer la location par Email """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune location à envoyer par Email !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        # Envoi du mail
        from Utils import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=track.IDfamille, nomDoc=FonctionsPerso.GenerationNomDoc("LOCATION", "pdf") , categorie="location")

    def CreationPDF(self, nomDoc="", afficherDoc=True):
        """ Création du PDF pour Email """
        IDlocation = self.Selection()[0].IDlocation
        from Utils import UTILS_Locations
        location = UTILS_Locations.Location()
        resultat = location.Impression(listeLocations=[IDlocation,], nomDoc=nomDoc, afficherDoc=False)
        if resultat == False :
            return False
        dictChampsFusion, dictPieces = resultat
        return dictChampsFusion[IDlocation]

    def GetID(self):
        track = self.Selection()[0]
        return track.IDlocation

    def SetID(self, IDlocation=None):
        for track in self.donnees :
            if track.IDlocation == IDlocation :
                self.SelectObject(track, deselectOthers=True, ensureVisible=True)
                return True
        return False

    def GetTracksCoches(self):
        return self.GetCheckedObjects()


# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "date_debut": {"mode": "nombre", "singulier": _(u"location"), "pluriel": _(u"locations"), "alignement": wx.ALIGN_CENTER},
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
        self.myOlv = ListView(panel, id=-1, afficher_uniquement_actives=True, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
