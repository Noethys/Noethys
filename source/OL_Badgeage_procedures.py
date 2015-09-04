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
import GestionDB
import UTILS_Export_tables
import UTILS_Utilisateurs

from DLG_Badgeage_interface import LISTE_STYLES, LISTE_THEMES

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


class Exporter(UTILS_Export_tables.Exporter):
    """ Adaptation de l'exportation """
    def __init__(self, categorie="badgeage"):
        UTILS_Export_tables.Exporter.__init__(self, categorie)
        
    def Exporter(self, ID=None):
        # G�n�ralit�s
        self.ExporterTable("badgeage_procedures", "IDprocedure=%d" % ID, remplacement=("defaut", 0))
        self.ExporterTable("badgeage_actions", "IDprocedure=%d" % ID)
        self.ExporterTable("badgeage_messages", "IDprocedure=%d" % ID)



class Track(object):
    def __init__(self, donnees):
        self.IDprocedure = donnees[0]
        self.nom = donnees[1]
        self.defaut = donnees[2]
        self.style = donnees[3]
        self.theme = donnees[4]        
        
        nomStyle = u""
        for dictStyle in LISTE_STYLES :
            if dictStyle["code"] == self.style :
                nomStyle = dictStyle["label"] 
        nomTheme = u""
        for dictTheme in LISTE_THEMES :
            if dictTheme["code"] == self.theme :
                nomTheme += dictTheme["label"] 
        self.interface = u"%s - %s" % (nomStyle, nomTheme) 
        
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
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
        """ R�cup�ration des donn�es """
        listeID = None
        db = GestionDB.DB()
        req = """
        SELECT IDprocedure, nom, defaut, style, theme
        FROM badgeage_procedures
        ORDER BY nom;
        """
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
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Pr�paration de la listeImages
        imgDefaut = self.AddNamedImages("defaut", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageDefaut(track):
            if track.defaut == 1 : return "defaut"
            else: return None 

        liste_Colonnes = [
            ColumnDefn(u"", "left", 22, "IDprocedure", typeDonnee="entier", imageGetter=GetImageDefaut),
            ColumnDefn(_(u"Nom"), 'left', 300, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Interface"), 'left', 200, "interface", typeDonnee="texte", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune proc�dure"))
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
        # S�lection d'un item
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
            ID = self.Selection()[0].IDprocedure
                
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()

        # Item Dupliquer
        item = wx.MenuItem(menuPop, 70, _(u"Dupliquer"))
        bmp = wx.Bitmap("Images/16x16/Dupliquer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Dupliquer, id=70)
        if noSelection == True : item.Enable(False)

        # Item Par d�faut
        item = wx.MenuItem(menuPop, 60, _(u"D�finir comme proc�dure par d�faut"))
        if noSelection == False :
            if self.Selection()[0].defaut == 1 :
                bmp = wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.SetDefaut, id=60)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des proc�dures de badgeage"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des proc�dures de badgeage"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_procedures_badgeage", "creer") == False : return
        if len(self.donnees) == 0 :
            defaut = 1
        else:
            defaut = 0
        import DLG_Badgeage_saisie_procedure
        dlg = DLG_Badgeage_saisie_procedure.Dialog(self, IDprocedure=None, defaut=defaut)
        if dlg.ShowModal() == wx.ID_OK:
            IDprocedure = dlg.GetIDprocedure()
            self.MAJ(IDprocedure)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_procedures_badgeage", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun type de cotisation � modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDprocedure = self.Selection()[0].IDprocedure
        import DLG_Badgeage_saisie_procedure
        dlg = DLG_Badgeage_saisie_procedure.Dialog(self, IDprocedure=IDprocedure, defaut=self.Selection()[0].defaut)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDprocedure)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_procedures_badgeage", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune proc�dure � supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDprocedure = self.Selection()[0].IDprocedure
        
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette proc�dure ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("badgeage_actions", "IDprocedure", IDprocedure)
            DB.ReqDEL("badgeage_messages", "IDprocedure", IDprocedure)
            DB.ReqDEL("badgeage_procedures", "IDprocedure", IDprocedure)
            # Attribue le D�faut � un autre type de cotisation
            if self.Selection()[0].defaut == 1 :
                req = """SELECT IDprocedure, defaut
                FROM badgeage_procedures
                ORDER BY nom
                ; """
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) > 0 :
                    DB.ReqMAJ("badgeage_procedures", [("defaut", 1 ),], "IDprocedure", listeDonnees[0][0])
            DB.Close() 
            self.MAJ()
        dlg.Destroy()

    def Dupliquer(self, event):
        """ Dupliquer un mod�le """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_procedures_badgeage", "creer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune proc�dure � dupliquer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDprocedure = self.Selection()[0].IDprocedure
        nom = self.Selection()[0].nom

        dlg = wx.MessageDialog(None, _(u"Confirmez-vous la duplication de la proc�dure '%s' ?") % nom, _(u"Duplication"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Exportation
        exportation = Exporter(categorie="badgeage")
        exportation.Ajouter(ID=IDprocedure, nom=nom)
        contenu = exportation.GetContenu()
        # Importation
        importation = UTILS_Export_tables.Importer(contenu=contenu)
        importation.Ajouter(index=0)
        newIDprocedure = importation.GetNewID("IDprocedure", IDprocedure)
        # MAJ listView
        self.MAJ(newIDprocedure)

    def SetDefaut(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_procedures_badgeage", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune proc�dure dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDprocedureDefaut = self.Selection()[0].IDprocedure
        DB = GestionDB.DB()
        req = """SELECT IDprocedure, defaut
        FROM badgeage_procedures
        ; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDprocedure, defaut in listeDonnees :
            if IDprocedure == IDprocedureDefaut :
                DB.ReqMAJ("badgeage_procedures", [("defaut", 1 ),], "IDprocedure", IDprocedure)
            else:
                DB.ReqMAJ("badgeage_procedures", [("defaut", 0 ),], "IDprocedure", IDprocedure)
        DB.Close()
        self.MAJ()



# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une proc�dure..."))
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
