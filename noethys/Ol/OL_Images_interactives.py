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
import os
import GestionDB
from Utils import UTILS_Export_documents
from Utils import UTILS_Utilisateurs

try :
    from Dlg.DLG_Images_interactives import LISTE_CATEGORIES
except :
    LISTE_CATEGORIES = []
    pass

from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils



class Track(object):
    def __init__(self, parent, donnees):
        self.IDmodele = donnees[0]
        self.nom = donnees[1]
        self.categorie = donnees[2]
        self.supprimable = donnees[3]
        self.observations = donnees[4]
        self.IDdonnee = donnees[5]

        # Récupération du nom de la donnée associée
        if parent.dictNomsDonnees.has_key(self.IDdonnee) :
            self.nomDonnee = parent.dictNomsDonnees[self.IDdonnee]
        else:
            self.nomDonnee = ""
        

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.categorie = kwds.pop("categorie", "")
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        DB = GestionDB.DB()

        # Importation des documents
        req = """SELECT IDmodele, documents_modeles.nom, categorie, supprimable, observations, IDdonnee
        FROM documents_modeles
        WHERE categorie='%s'
        ORDER BY nom;""" % self.categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()

        # Recherche du nom de la donnée associée
        self.dictNomsDonnees = {}
        self.champs_interactifs = {}

        if self.categorie == "produits_categories" :
            # Importation des catégories
            req = """SELECT IDcategorie, nom
            FROM produits_categories;"""
            DB.ExecuterReq(req)
            listeCategories = DB.ResultatReq()
            for IDcategorie, nom in listeCategories:
                self.dictNomsDonnees[IDcategorie] = nom

            # Importation des produits
            req = """SELECT IDproduit, IDcategorie, nom
            FROM produits;"""
            DB.ExecuterReq(req)
            listeProduits = DB.ResultatReq()
            for IDproduit, IDcategorie, nom in listeProduits:
                if self.champs_interactifs.has_key(IDcategorie) == False :
                    self.champs_interactifs[IDcategorie] = {}
                self.champs_interactifs[IDcategorie][IDproduit] = nom

        DB.Close()

        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(self, item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDmodele", typeDonnee="entier"),
            ColumnDefn(_(u"Nom"), "left", 200, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Donnée associée"), "left", 200, "nomDonnee", typeDonnee="texte"),
            ColumnDefn(_(u"Observations"), "left", 120, "observations", typeDonnee="texte", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune image"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None, categorie=None):
        if categorie != None :
            self.categorie = categorie
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
        self._ResizeSpaceFillingColumns()
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def SelectionModele(self, IDmodele=None):
        for track in self.donnees :
            if track.IDmodele == IDmodele :
                self.SelectObject(track, deselectOthers=True, ensureVisible=True)

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Modifier
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

        # Item Visualiser
        item = wx.MenuItem(menuPop, 32, _(u"Visualiser"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Visualiser, id=32)
        if noSelection == True: item.Enable(False)

        menuPop.AppendSeparator()

        # Item Dupliquer
        item = wx.MenuItem(menuPop, 60, _(u"Dupliquer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Dupliquer, id=60)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()

        # Item Importer
        item = wx.MenuItem(menuPop, 80, _(u"Importer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_import.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Importer, id=80)

        # Item Exporter
        item = wx.MenuItem(menuPop, 90, _(u"Exporter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_export.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Exporter, id=90)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des images interactives"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des images interactives"), format="A", orientation=wx.PORTRAIT)
        prt.Print()
            
    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_images_interactives", "creer") == False : return

        # Demande le nom et la donnée associée
        from Dlg import DLG_Saisie_nom_image_interactive
        dlg = DLG_Saisie_nom_image_interactive.Dialog(self, categorie=self.categorie)
        if dlg.ShowModal() == wx.ID_OK:
            dictResultats = dlg.GetResultats()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return False

        # Ouvre l'éditeur d'images interactives
        if self.champs_interactifs.has_key(dictResultats["IDdonnee"]) :
            champs_interactifs = self.champs_interactifs[dictResultats["IDdonnee"]]
        else :
            champs_interactifs = {}
        from Dlg import DLG_Saisie_image_interactive
        dlg = DLG_Saisie_image_interactive.Dialog(self, IDmodele=None, nom=dictResultats["nom"], categorie=self.categorie,
                                                  IDdonnee=dictResultats["IDdonnee"], champs_interactifs=champs_interactifs)
        if dlg.ShowModal() == wx.ID_OK:
            IDmodele = dlg.GetIDmodele()
            self.MAJ(IDmodele)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_images_interactives", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune image à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        IDmodele = track.IDmodele
        IDdonnee = track.IDdonnee
        if self.champs_interactifs.has_key(IDdonnee):
            champs_interactifs = self.champs_interactifs[IDdonnee]
        else :
            champs_interactifs = {}
        from Dlg import DLG_Saisie_image_interactive
        dlg = DLG_Saisie_image_interactive.Dialog(self, IDmodele=IDmodele, nom=track.nom, observations=track.observations,
                                                  categorie=self.categorie, IDdonnee=IDdonnee, champs_interactifs=champs_interactifs)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDmodele)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_images_interactives", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune image à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDmodele = self.Selection()[0].IDmodele

        # Vérifie qu'il est autorisé de supprimer ce modèle
        if self.Selection()[0].supprimable == 0 :
            dlg = wx.MessageDialog(self, _(u"Cette image ne peut pas être supprimé !"), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette image ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("documents_modeles", "IDmodele", IDmodele)
            DB.ReqDEL("documents_objets", "IDmodele", IDmodele)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()
    
    def Dupliquer(self, event):
        """ Dupliquer un modèle """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_images_interactives", "creer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune image à dupliquer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDmodele = self.Selection()[0].IDmodele
        nom = self.Selection()[0].nom
        
        DB = GestionDB.DB()
        
        # Duplication du modèle
        conditions = "IDmodele=%d" % IDmodele
        dictModifications = {"nom" : _(u"Copie de %s") % nom, "defaut" : 0}
        newIDmodele = DB.Dupliquer("documents_modeles", "IDmodele", conditions, dictModifications)
        
        # Duplication des objets
        conditions = "IDmodele=%d" % IDmodele
        dictModifications = {"IDmodele" : newIDmodele}
        newIDobjet = DB.Dupliquer("documents_objets", "IDobjet", conditions, dictModifications)

        DB.Close() 
        self.MAJ(newIDmodele)

    def Importer(self, event):
        """ Importer un modèle """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_images_interactives", "creer") == False : return
        # Ouverture de la fenêtre de dialogue
        wildcard = u"Image interactive Noethys (*.ndi)|*.ndi|Tous les fichiers (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez un modèle à importer"),
            defaultDir=sp.GetDocumentsDir(), 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN
            )
        if dlg.ShowModal() == wx.ID_OK:
            nomFichierCourt = dlg.GetFilename()
            nomFichierLong = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Demande confirmation
        dictInfos = UTILS_Export_documents.InfosFichier(nomFichierLong)
        nom = dictInfos["nom"]
        categorie = dictInfos["categorie"]
        labelCategorie = categorie
        for code, label in LISTE_CATEGORIES :
            if code == categorie :
                labelCategorie = label
        
        message = _(u"Confirmez-vous l'importation de l'image suivante ?\n\nNom : %s\nCatégorie : %s\n") % (nom , labelCategorie)
        dlg = wx.MessageDialog(self, message, _(u"Importer une image interactive"), wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES : 
            return
        
        # Importation
        IDmodele = UTILS_Export_documents.Importer(nomFichierLong)
        self.GetParent().SelectCategorie(categorie)
        self.SelectionModele(IDmodele)
        
        # Confirmation
        dlg = wx.MessageDialog(self, _(u"L'image interactive a été importée avec succès dans la catégorie '%s' !") % labelCategorie, _(u"Importation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def Exporter(self, event):
        """ Exporter le modèle sélectionné """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_images_interactives", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune image dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        IDmodele = track.IDmodele

        # Demande le chemin pour la sauvegarde du fichier
        standardPath = wx.StandardPaths.Get()
        dlg = wx.FileDialog(self, message=_(u"Enregistrer l'image interactive sous..."),
                            defaultDir = standardPath.GetDocumentsDir(), defaultFile="image.ndi",
                            wildcard=u"Image interactive Noethys (*.ndi)|*.ndi", style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        else :
            path = None
        dlg.Destroy()
        if path == None :
            return

        # Le fichier de destination existe déjà :
        if os.path.isfile(path) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Exportation
        UTILS_Export_documents.Exporter(IDmodele, path)

        # Confirmation
        dlg = wx.MessageDialog(self, _(u"L'image interactive a été exportée avec succès !"), _(u"Exportation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def Visualiser(self, event=None):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune image à visualiser dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        from Dlg import DLG_Image_interactive
        dlg = DLG_Image_interactive.Dialog(None, IDmodele=track.IDmodele)
        dlg.ShowModal()
        dlg.Destroy()


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, categorie="produits_categories", id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
