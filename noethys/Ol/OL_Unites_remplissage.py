#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import GestionDB


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text



class Track(object):
    def __init__(self, donnees):
        self.IDunite_remplissage = donnees[0]
        self.nom = donnees[1]
        self.abrege = donnees[2]
        self.seuil_alerte = donnees[3]
        self.date_debut = donnees[4]
        self.date_fin = donnees[5]
        self.ordre = donnees[6]
        self.heure_min = donnees[7]
        self.heure_max = donnees[8]
        
        if self.heure_min != None and self.heure_max != None :
            self.tranche_horaire = u"%s-%s" % (self.heure_min.replace(":", "h"), self.heure_max.replace(":", "h"))
        else :
            self.tranche_horaire = u""
        
        if self.date_debut == "1977-01-01" and self.date_fin == "2999-01-01" :
            self.periode_validite = _(u"Illimitée")
        else:
            self.periode_validite = _(u"Du %s au %s") % (DateEngFr(self.date_debut), DateEngFr(self.date_fin))
        
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDactivite = kwds.pop("IDactivite", None)
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
        db = GestionDB.DB()
        req = """SELECT IDunite_remplissage, nom, abrege, seuil_alerte, date_debut, date_fin, ordre, heure_min, heure_max
        FROM unites_remplissage 
        WHERE IDactivite=%d
        ORDER BY ordre; """ % self.IDactivite
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
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDunite", typeDonnee="entier"),
            ColumnDefn(_(u"Ordre"), "left", 70, "ordre", typeDonnee="entier"),
            ColumnDefn(_(u"Nom"), 'left', 190, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Abrégé"), "left", 60, "abrege", typeDonnee="texte"), 
            ColumnDefn(_(u"Seuil alerte"), "left", 70, "seuil_alerte", typeDonnee="texte"), 
            ColumnDefn(_(u"Plage horaire"), "left", 90, "tranche_horaire", typeDonnee="texte"), 
            ColumnDefn(_(u"Période de validité"), "left", 170, "periode_validite", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune unité de remplissage"))
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
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDunite_remplissage
                
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
        
        # Item Deplacer vers le haut
        item = wx.MenuItem(menuPop, 40, _(u"Déplacer vers le haut"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Monter, id=40)

        # Item Déplacer vers le bas
        item = wx.MenuItem(menuPop, 50, _(u"Déplacer vers le bas"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Descendre, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 60, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=60)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop,70, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=70)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des unités de remplissage"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des unités de remplissage"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        from Dlg import DLG_Saisie_unite_remplissage
        dlg = DLG_Saisie_unite_remplissage.Dialog(self, IDactivite=self.IDactivite, IDunite_remplissage=None)
        if dlg.ShowModal() == wx.ID_OK:
            IDunite_remplissage = dlg.GetIDunite_remplissage()
            self.MAJ(IDunite_remplissage)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune unité à modifier dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDunite_remplissage = self.Selection()[0].IDunite_remplissage
        from Dlg import DLG_Saisie_unite_remplissage
        dlg = DLG_Saisie_unite_remplissage.Dialog(self, IDactivite=self.IDactivite, IDunite_remplissage=IDunite_remplissage)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDunite_remplissage)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune unité à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDunite_remplissage = self.Selection()[0].IDunite_remplissage
        
        # Vérifie que l'unité n'est pas déjà attribuée à un remplissage
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDremplissage)
        FROM remplissage
        WHERE IDunite_remplissage=%d
        ;""" % IDunite_remplissage
        DB.ExecuterReq(req)
        nbreRemplissages = int(DB.ResultatReq()[0][0])
        DB.Close()
##        if nbreRemplissages > 0 :
##            dlg = wx.MessageDialog(self, _(u"Cette unité de remplissage a déjà été attribuée à %d remplissage(s).\n\nVous ne pouvez donc pas la supprimer !") % nbreRemplissages, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return

        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette unité de remplissage ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("unites_remplissage", "IDunite_remplissage", IDunite_remplissage)
            DB.ReqDEL("unites_remplissage_unites", "IDunite_remplissage", IDunite_remplissage)
            DB.Close() 
            self.MAJordre(IDunite_remplissage)
            self.MAJ()
        dlg.Destroy()
    
    def MAJordre(self, IDunite_remplissage=None):
        DB = GestionDB.DB()
        ordre = 1
        for index in range(0, len(self.donnees)) :
            objet = self.GetObjectAt(index)
            if objet.IDunite_remplissage != IDunite_remplissage :
                DB.ReqMAJ("unites_remplissage", [("ordre", ordre),], "IDunite_remplissage", objet.IDunite_remplissage)
                ordre += 1
        DB.Close()

    def Monter(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune unité dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDunite_remplissage = self.Selection()[0].IDunite_remplissage
        ordre = self.Selection()[0].ordre
        if ordre == 1 : return
        DB = GestionDB.DB()
        # Modifie unite actuelle
        DB.ReqMAJ("unites_remplissage", [("ordre", ordre-1),], "IDunite_remplissage", IDunite_remplissage)
        self.Selection()[0].ordre = ordre-1
        # Modifie unite a remplacer
        index = self.GetIndexOf(self.Selection()[0])
        unite_remplissage2 = self.GetObjectAt(index-1)
        IDunite_remplissage2 = unite_remplissage2.IDunite_remplissage
        DB.ReqMAJ("unites_remplissage", [("ordre", ordre),], "IDunite_remplissage", IDunite_remplissage2)
        DB.Close()
        self.MAJ(IDunite_remplissage)
    
    def Descendre(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune unité dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDunite_remplissage = self.Selection()[0].IDunite_remplissage
        ordre = self.Selection()[0].ordre
        if ordre == len(self.donnees) : return
        DB = GestionDB.DB()
        # Modifie unite actuelle
        DB.ReqMAJ("unites_remplissage", [("ordre", ordre+1),], "IDunite_remplissage", IDunite_remplissage)
        self.Selection()[0].ordre = ordre+1
        # Modifie unite a remplacer
        index = self.GetIndexOf(self.Selection()[0])
        unite_remplissage2 = self.GetObjectAt(index+1)
        IDunite_remplissage2 = unite_remplissage2.IDunite_remplissage
        DB.ReqMAJ("unites_remplissage", [("ordre", ordre),], "IDunite_remplissage", IDunite_remplissage2)
        DB.Close()
        self.MAJ(IDunite_remplissage)











# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une unité de remplissage..."))
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
        self.myOlv = ListView(panel, IDactivite=1, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
