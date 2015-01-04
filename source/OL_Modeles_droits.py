#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import GestionDB
import UTILS_Export_tables
import UTILS_Utilisateurs

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


class Exporter(UTILS_Export_tables.Exporter):
    """ Adaptation de l'exportation """
    def __init__(self, categorie="modeles_droits"):
        UTILS_Export_tables.Exporter.__init__(self, categorie)
        
    def Exporter(self, ID=None):
        # Généralités
        self.ExporterTable("modeles_droits", "IDmodele=%d" % ID, remplacement=("defaut", 0))
        self.ExporterTable("droits", "IDmodele=%d" % ID)



class Track(object):
    def __init__(self, donnees, dictDroits):
        self.IDmodele = donnees[0]
        self.nom = donnees[1]
        self.observations = donnees[2]
        self.defaut = donnees[3]
        
        # Détail
        nbreAutorisations = 0
        nbreInterdictions = 0
        nbreRestrictions = 0
        if dictDroits.has_key(self.IDmodele) :
            for etat in dictDroits[self.IDmodele] : 
                if etat == "autorisation" : nbreAutorisations += 1
                if etat == "interdiction" : nbreInterdictions += 1
                if etat.startswith("restriction") : nbreRestrictions += 1
        
        listeTemp = []
        if nbreAutorisations > 0 : listeTemp.append(u"%d autorisations" % nbreAutorisations)
        if nbreInterdictions > 0 : listeTemp.append(u"%d interdictions" % nbreInterdictions)
        if nbreRestrictions > 0 : listeTemp.append(u"%d restrictions" % nbreRestrictions)
        
        if len(listeTemp) > 0 :
            self.details = u" - ".join(listeTemp)
        else :
            self.details = u"Aucune information"
        
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
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
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        DB = GestionDB.DB()
        
        # Lecture des droits
        req = """SELECT IDdroit, IDmodele, categorie, action , etat
        FROM droits
        WHERE IDmodele IS NOT NULL;"""
        DB.ExecuterReq(req)
        listeDroits = DB.ResultatReq()
        self.dictDroits = {}
        for IDdroit, IDmodele, categorie, action, etat in listeDroits :
            if self.dictDroits.has_key(IDmodele) == False :
                self.dictDroits[IDmodele] = []
            self.dictDroits[IDmodele].append(etat)
        
        # Lecture des modèles
        req = """SELECT IDmodele, nom, observations, defaut
        FROM modeles_droits
        ORDER BY nom;
        """
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
                track = Track(item, self.dictDroits)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Préparation de la listeImages
        imgDefaut = self.AddNamedImages("defaut", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageDefaut(track):
            if track.defaut == 1 : return "defaut"
            else: return None 

        liste_Colonnes = [
            ColumnDefn(u"", "left", 22, "IDmodele", typeDonnee="entier", imageGetter=GetImageDefaut),
            ColumnDefn(u"Nom", 'left', 200, "nom", typeDonnee="texte"),
            ColumnDefn(u"Détails", 'left', 250, "details", typeDonnee="texte"),
            ColumnDefn(u"Observations", 'left', 200, "observations", typeDonnee="texte", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucun modèle de droits")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
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
        self._ResizeSpaceFillingColumns() 
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDmodele
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, u"Ajouter")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, u"Modifier")
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, u"Supprimer")
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()

        # Item Dupliquer
        item = wx.MenuItem(menuPop, 70, u"Dupliquer")
        bmp = wx.Bitmap("Images/16x16/Dupliquer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Dupliquer, id=70)
        if noSelection == True : item.Enable(False)

        # Item Par défaut
        item = wx.MenuItem(menuPop, 60, u"Définir comme modèle par défaut")
        if noSelection == False :
            if self.Selection()[0].defaut == 1 :
                bmp = wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.SetDefaut, id=60)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, u"Aperçu avant impression")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, u"Imprimer")
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des modèle de droits", format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des modèles de droits", format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_droits", "creer") == False : return
        if len(self.donnees) == 0 :
            defaut = 1
        else:
            defaut = 0
        import DLG_Saisie_modele_droits
        dlg = DLG_Saisie_modele_droits.Dialog(self, IDmodele=None, defaut=defaut)
        if dlg.ShowModal() == wx.ID_OK:
            IDmodele = dlg.GetIDmodele()
            self.MAJ(IDmodele)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun modèle à modifier dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_droits", "modifier") == False : return
        IDmodele = self.Selection()[0].IDmodele
        import DLG_Saisie_modele_droits
        dlg = DLG_Saisie_modele_droits.Dialog(self, IDmodele=IDmodele)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDmodele)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun modèle à supprimer dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_droits", "supprimer") == False : return
        IDmodele = self.Selection()[0].IDmodele
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer ce modèle ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("modeles_droits", "IDmodele", IDmodele)
            DB.ReqDEL("droits", "IDmodele", IDmodele)
            # Attribue le Défaut à un autre type de cotisation
            if self.Selection()[0].defaut == 1 :
                req = """SELECT IDmodele, defaut
                FROM modeles_droits
                ORDER BY nom
                ; """
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) > 0 :
                    DB.ReqMAJ("modeles_droits", [("defaut", 1 ),], "IDmodele", listeDonnees[0][0])
            DB.Close() 
            self.MAJ()
        dlg.Destroy()

    def Dupliquer(self, event):
        """ Dupliquer un modèle """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun modèle à dupliquer dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_droits", "creer") == False : return
        IDmodele = self.Selection()[0].IDmodele
        nom = self.Selection()[0].nom

        dlg = wx.MessageDialog(None, u"Confirmez-vous la duplication du modèle '%s' ?" % nom, u"Duplication", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Exportation
        exportation = Exporter(categorie="modele")
        exportation.Ajouter(ID=IDmodele, nom=nom)
        contenu = exportation.GetContenu()
        # Importation
        importation = UTILS_Export_tables.Importer(contenu=contenu)
        importation.Ajouter(index=0)
        newIDmodele = importation.GetNewID("IDmodele", IDmodele)
        # MAJ listView
        self.MAJ(newIDmodele)

    def SetDefaut(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun modèle dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_droits", "modifier") == False : return
        IDmodeleDefaut = self.Selection()[0].IDmodele
        DB = GestionDB.DB()
        req = """SELECT IDmodele, defaut
        FROM modeles_droits
        ; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDmodele, defaut in listeDonnees :
            if IDmodele == IDmodeleDefaut :
                DB.ReqMAJ("modeles_droits", [("defaut", 1 ),], "IDmodele", IDmodele)
            else:
                DB.ReqMAJ("modeles_droits", [("defaut", 0 ),], "IDmodele", IDmodele)
        DB.Close()
        self.MAJ()



# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher un modèle...")
        self.ShowSearchButton(True)
        
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



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
