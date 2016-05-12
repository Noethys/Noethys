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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import cStringIO
import datetime
import GestionDB
from Utils import UTILS_Historique


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, ListCtrlPrinter

from Utils import UTILS_Utilisateurs


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text




class Track(object):
    def __init__(self, parent, donnees):
        self.IDscolarite = donnees[0]
        self.IDindividu = donnees[1]
        self.date_debut = donnees[2]
        self.date_fin = donnees[3]
        
        self.IDecole = donnees[4]
        self.nomEcole = donnees[5]
        if self.nomEcole == None :
            self.nomEcole = u""
        
        self.IDclasse = donnees[6]
        self.nomClasse = donnees[7]
        if self.nomClasse == None :
            self.nomClasse = u""
            
        self.IDniveau = donnees[8]
        self.nomNiveau = donnees[9]
        if self.nomNiveau == None :
            self.nomNiveau = u""
            
        self.abregeNiveau = donnees[10]
        
        self.dateDebutDD = DateEngEnDateDD(self.date_debut)
        self.dateFinDD = DateEngEnDateDD(self.date_fin)
        dateDuJour = datetime.date.today() 
        if self.dateDebutDD <= dateDuJour and self.dateFinDD >= dateDuJour :
            self.valide = True
        else:
            self.valide = False
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDindividu = kwds.pop("IDindividu", None)
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
        req = """SELECT IDscolarite, scolarite.IDindividu, scolarite.date_debut, scolarite.date_fin, scolarite.IDecole, ecoles.nom, scolarite.IDclasse, classes.nom, scolarite.IDniveau, niveaux_scolaires.nom, niveaux_scolaires.abrege
        FROM scolarite 
        LEFT JOIN ecoles ON ecoles.IDecole = scolarite.IDecole
        LEFT JOIN classes ON classes.IDclasse = scolarite.IDclasse
        LEFT JOIN niveaux_scolaires ON niveaux_scolaires.IDniveau = scolarite.IDniveau
        WHERE scolarite.IDindividu=%d
        ORDER BY scolarite.date_debut; """ % self.IDindividu
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
        
        def DateEngFr(textDate):
            if textDate != None :
                text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
            else:
                text = ""
            return text

        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour((180, 180, 180))

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDscolarite", typeDonnee="entier"),
            ColumnDefn(u"Du", 'left', 70, "date_debut", typeDonnee="date", stringConverter=DateEngFr),
            ColumnDefn(_(u"Au"), 'left', 70, "date_fin", typeDonnee="date", stringConverter=DateEngFr),
            ColumnDefn(_(u"Ecole"), 'left', 160, "nomEcole", typeDonnee="texte"),
            ColumnDefn(_(u"Classe"), 'left', 100, "nomClasse", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Niveau"), 'left', 60, "abregeNiveau", typeDonnee="texte"),
            ]

        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune classe"))
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
            ID = self.Selection()[0].IDscolarite
                
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
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Scolarité"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Scolarité"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Scolarité"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Scolarité"))

    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_scolarite", "creer") == False : return
        
        # Recherches des dernières dates saisies
        DB = GestionDB.DB()
        req = """SELECT date_debut, date_fin
        FROM scolarite 
        ORDER BY IDscolarite DESC LIMIT 1;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            date_debut = DateEngEnDateDD(listeDonnees[0][0])
            date_fin = DateEngEnDateDD(listeDonnees[0][1])
        else:
            date_debut = None
            date_fin = None
            
        # Ouverture de la DLG de saisie
        from Dlg import DLG_Saisie_scolarite
        dlg = DLG_Saisie_scolarite.Dialog(self, IDscolarite=None, donneesScolarite=self.donnees)
        dlg.SetDateDebut(date_debut)
        dlg.SetDateFin(date_fin)
        if dlg.ShowModal() == wx.ID_OK:
            date_debut = dlg.GetDateDebut()
            date_fin = dlg.GetDateFin()
            IDecole = dlg.GetEcole()
            IDclasse = dlg.GetClasse()
            IDniveau = dlg.GetNiveau()
            nomEcole = dlg.GetNomEcole()
            nomClasse = dlg.GetNomClasse()
            nomNiveau = dlg.GetNomNiveau()
            
            # Sauvegarde
            DB = GestionDB.DB()
            listeDonnees = [
                ("IDindividu", self.IDindividu ),
                ("date_debut", date_debut ),
                ("date_fin", date_fin ),
                ("IDecole", IDecole),
                ("IDclasse", IDclasse),
                ("IDniveau", IDniveau),
                ]
            IDscolarite = DB.ReqInsert("scolarite", listeDonnees)
            DB.Close()
            
            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDindividu" : self.IDindividu,
                "IDfamille" : None,
                "IDcategorie" : 30, 
                "action" : _(u"Inscription scolaire du %s au %s. Ecole : '%s'. Classe : '%s'. Niveau : '%s'") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)), nomEcole, nomClasse, nomNiveau)
                },])
            
            # Actualise l'affichage
            self.MAJ(IDscolarite)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_scolarite", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune étape de scolarité à modifier dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDscolarite = self.Selection()[0].IDscolarite
        date_debut = self.Selection()[0].dateDebutDD
        date_fin = self.Selection()[0].dateFinDD
        IDecole = self.Selection()[0].IDecole
        IDclasse = self.Selection()[0].IDclasse
        IDniveau = self.Selection()[0].IDniveau
        
        from Dlg import DLG_Saisie_scolarite
        dlg = DLG_Saisie_scolarite.Dialog(self, IDscolarite=IDscolarite, donneesScolarite=self.donnees)
        dlg.SetTitle(_(u"Modification d'une étape de la scolarité"))
        dlg.SetDateDebut(date_debut)
        dlg.SetDateFin(date_fin)
        dlg.SetEcole(IDecole)
        dlg.SetClasse(IDclasse)
        dlg.SetNiveau(IDniveau)
        if dlg.ShowModal() == wx.ID_OK:
            date_debut = dlg.GetDateDebut()
            date_fin = dlg.GetDateFin()
            IDecole = dlg.GetEcole()
            IDclasse = dlg.GetClasse()
            IDniveau = dlg.GetNiveau()
            nomEcole = dlg.GetNomEcole()
            nomClasse = dlg.GetNomClasse()
            nomNiveau = dlg.GetNomNiveau()

            # Sauvegarde
            DB = GestionDB.DB()
            listeDonnees = [
                ("date_debut", date_debut ),
                ("date_fin", date_fin ),
                ("IDecole", IDecole),
                ("IDclasse", IDclasse),
                ("IDniveau", IDniveau),
                ]
            DB.ReqMAJ("scolarite", listeDonnees, "IDscolarite", IDscolarite)
            DB.Close()
            
            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDindividu" : self.IDindividu,
                "IDfamille" : None,
                "IDcategorie" : 31, 
                "action" : _(u"Inscription scolaire du %s au %s. Ecole : '%s'. Classe : '%s'. Niveau : '%s'") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)), nomEcole, nomClasse, nomNiveau)
                },])

            # Actualise l'affichage
            self.MAJ(IDscolarite)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_scolarite", "supprimer") == False : return

        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune étape de scolarité à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDscolarite = self.Selection()[0].IDscolarite
        date_debut = self.Selection()[0].dateDebutDD
        date_fin = self.Selection()[0].dateFinDD
        nomEcole = self.Selection()[0].nomEcole
        nomClasse = self.Selection()[0].nomClasse
        nomNiveau = self.Selection()[0].nomNiveau
        
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette étape de scolarité ?\n\nPériode : Du %s au %s\nEcole : %s\nClasse : %s\nNiveau : %s") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)), nomEcole, nomClasse, nomNiveau), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("scolarite", "IDscolarite", IDscolarite)
            DB.Close() 
            
            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDindividu" : self.IDindividu,
                "IDfamille" : None,
                "IDcategorie" : 32, 
                "action" : _(u"Inscription scolaire du %s au %s. Ecole : '%s'. Classe : '%s'. Niveau : '%s'") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)), nomEcole, nomClasse, nomNiveau)
                },])
                
            # Actualise l'affichage
            self.MAJ()
        dlg.Destroy()

# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une étape de la scolarité..."))
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
        self.myOlv = ListView(panel, id=-1, IDindividu=3, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
