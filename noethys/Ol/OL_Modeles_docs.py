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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import GestionDB
from Utils import UTILS_Export_documents
from Utils import UTILS_Utilisateurs

try :
    from Dlg.DLG_Modeles_docs import LISTE_CATEGORIES
except :
    LISTE_CATEGORIES = []
    pass


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils



DICT_FONDS = {} 


class Track(object):
    def __init__(self, donnees):
        self.IDmodele = donnees[0]
        self.nom = donnees[1]
        self.categorie = donnees[2]
        self.supprimable = donnees[3]
        self.largeur = donnees[4]
        self.hauteur = donnees[5]
        self.taille = (self.largeur, self.hauteur) 
        self.tailleStr = _(u"%d mm x %d mm") % (self.largeur, self.hauteur) 
        self.observations = donnees[6]
        self.IDfond = donnees[7]
        self.defaut = donnees[8]
        
        if self.IDfond != None :
            if self.IDfond in DICT_FONDS:
                self.nomFond = DICT_FONDS[self.IDfond]
        else:
            self.nomFond = u""
    
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
        global DICT_FONDS
        DICT_FONDS = self.GetFonds()
        self.donnees = self.GetTracks()
    
    def GetFonds(self):
        dictFonds = {}
        DB = GestionDB.DB()
        req = """SELECT IDmodele, nom
        FROM documents_modeles
        WHERE categorie='fond'
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDmodele, nom in listeDonnees :
            dictFonds[IDmodele] = nom
        return dictFonds

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        DB = GestionDB.DB()
        req = """SELECT IDmodele, nom, categorie, supprimable, largeur, hauteur, observations, IDfond, defaut
        FROM documents_modeles
        WHERE categorie='%s'
        ORDER BY nom;""" % self.categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
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
        imgDefaut = self.AddNamedImages("defaut", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        
        def GetImageDefaut(track):
            if track.defaut == 1 : return "defaut"
            else: return None 

        if self.categorie == "fond" :
            # Si ce sont des fonds de page
            liste_Colonnes = [
                ColumnDefn(u"", "left", 0, "IDmodele", typeDonnee="entier"),
                ColumnDefn(_(u"Nom"), "left", 200, "nom", typeDonnee="texte"), 
                ColumnDefn(_(u"Dimensions"), "left", 110, "tailleStr", typeDonnee="texte"), 
                ColumnDefn(_(u"Observations"), "left", 120, "observations", typeDonnee="texte", isSpaceFilling=True), 
                ]
        else:
            # Si ce sont des modèles de documents
            liste_Colonnes = [
                ColumnDefn(u"", "left", 22, "IDmodele", typeDonnee="entier", imageGetter=GetImageDefaut),
                ColumnDefn(_(u"Nom"), "left", 200, "nom", typeDonnee="texte"), 
                ColumnDefn(_(u"Dimensions"), "left", 110, "tailleStr", typeDonnee="texte"), 
                ColumnDefn(_(u"Fond de page"), "left", 120, "nomFond", typeDonnee="texte"), 
                ColumnDefn(_(u"Observations"), "left", 120, "observations", typeDonnee="texte", isSpaceFilling=True), 
                ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun modèle"))
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
            ID = self.Selection()[0].IDmodele
                
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

        # Item Dupliquer
        item = wx.MenuItem(menuPop, 60, _(u"Dupliquer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Dupliquer, id=60)
        if noSelection == True : item.Enable(False)

        # Item Par défaut
        if self.categorie != "fond" :
            item = wx.MenuItem(menuPop, 70, _(u"Définir comme modèle par défaut"))
            if noSelection == False :
                if self.Selection()[0].defaut == 1 :
                    bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG)
                    item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.SetDefaut, id=70)
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des modèles"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des modèles"), format="A", orientation=wx.PORTRAIT)
        prt.Print()
            
    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_docs", "creer") == False : return
        from Dlg import DLG_Noedoc
        dlg = DLG_Noedoc.Dialog(self, IDmodele=None,
                nom=u"", observations=u"", IDfond=None,
                categorie=self.categorie, taille_page=(210, 297),
                )
        if dlg.ShowModal() == wx.ID_OK:
            IDmodele = dlg.GetIDmodele()
            self.MAJ(IDmodele)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_docs", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun modèle à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        IDmodele = track.IDmodele
        from Dlg import DLG_Noedoc
        dlg = DLG_Noedoc.Dialog(self, IDmodele=IDmodele,
                nom=track.nom, observations=track.observations, IDfond=track.IDfond,
                categorie=self.categorie, taille_page=track.taille,
                )
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDmodele)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_docs", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun modèle à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDmodele = self.Selection()[0].IDmodele
        categorie = self.Selection()[0].categorie
        # Si c'est un fond, vérifie qu'il n'est pas utilisé dans un modèle
        if categorie == "fond" :
            DB = GestionDB.DB()
            req = """SELECT IDmodele, nom
            FROM documents_modeles
            WHERE IDfond=%d;""" % IDmodele
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                dlg = wx.MessageDialog(self, _(u"Ce fond de page ne peut pas être supprimé car il est déjà utilisé dans %d modèle(s) !") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        # Vérifie qu'il est autorisé de supprimer ce modèle
        if self.Selection()[0].supprimable == 0 :
            dlg = wx.MessageDialog(self, _(u"Ce modèle ne peut pas être supprimé !"), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce modèle ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("documents_modeles", "IDmodele", IDmodele)
            DB.ReqDEL("documents_objets", "IDmodele", IDmodele)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()
    
    def Dupliquer(self, event):
        """ Dupliquer un modèle """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_docs", "creer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun modèle à dupliquer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
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
    
    def SetDefaut(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_docs", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun modèle dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDmodele = self.Selection()[0].IDmodele
        DB = GestionDB.DB()
        for track in self.donnees :
            if track.defaut == 1 :
                DB.ReqMAJ("documents_modeles", [("defaut", 0),], "IDmodele", track.IDmodele)
        DB.ReqMAJ("documents_modeles", [("defaut", 1),], "IDmodele", IDmodele)
        DB.Close() 
        self.MAJ()
    
    def Importer(self, event):
        """ Importer un modèle """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_docs", "creer") == False : return
        # Ouverture de la fenêtre de dialogue
        wildcard = u"Modèle Noedoc (*.ndc)|*.ndc|Tous les fichiers (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez un modèle à importer"),
            defaultDir=sp.GetDocumentsDir(), 
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN
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
        
        message = _(u"Confirmez-vous l'importation du modèle suivant ?\n\nNom : %s\nCatégorie : %s\n") % (nom , labelCategorie)
        dlg = wx.MessageDialog(self, message, _(u"Importer un modèle"), wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES : 
            return
        
        # Importation
        IDmodele = UTILS_Export_documents.Importer(nomFichierLong)
        self.GetParent().SelectCategorie(categorie)
        self.SelectionModele(IDmodele)
        
        # Confirmation
        dlg = wx.MessageDialog(self, _(u"Le modèle a été importé avec succès dans la catégorie '%s' !") % labelCategorie, _(u"Importation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def Exporter(self, event):
        """ Exporter le modèle sélectionné """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_docs", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun modèle dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        IDmodele = track.IDmodele
        IDfond = track.IDfond
        
        # Vérifie s'il y a un fond
        if IDfond != None :
            dlg = wx.MessageDialog(None, _(u"Ce modèle dispose d'un fond. Notez que celui-ci ne sera pas intégré lors de l'exportation. \n\nVoulez-vous quand même continuer ?"), _(u"Remarque"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Demande le chemin pour la sauvegarde du fichier
        standardPath = wx.StandardPaths.Get()
        dlg = wx.FileDialog(self, message=_(u"Enregistrer le modèle sous..."),
                            defaultDir = standardPath.GetDocumentsDir(), defaultFile="modele.ndc",
                            wildcard=u"Modèle Noedoc (*.ndc)|*.ndc", style=wx.FD_SAVE)

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
        dlg = wx.MessageDialog(self, _(u"Le modèle a été exporté avec succès !"), _(u"Exportation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un modèle..."))
        self.ShowSearchButton(True)
        
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


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, categorie="facture", id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
