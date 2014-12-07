#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB
import datetime

from ObjectListView import FastObjectListView, ColumnDefn, Filter, ListCtrlPrinter

try: import psyco; psyco.full()
except: pass


def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (u"Lundi", u"Mardi", u"Mercredi", u"Jeudi", u"Vendredi", u"Samedi", u"Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))




class Track(object):
    def __init__(self, donnees):
        self.IDconso = donnees["IDconso"]
        self.date = donnees["date"]
        self.IDactivite = donnees["IDactivite"]
        self.nomActivite = donnees["nomActivite"]
        self.IDunite = donnees["IDunite"]
        self.nomUnite = donnees["nomUnite"]
        self.IDindividu = donnees["IDindividu"]
        self.nomIndividu = donnees["nomIndividu"]
        self.prenomIndividu = donnees["prenomIndividu"]
        self.individu = u"%s %s" % (self.nomIndividu, self.prenomIndividu)
            
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDprestation = kwds.pop("IDprestation", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
##        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        if self.GetParent().GetName() == "DLG_medecin" :
            if self.GetParent().mode == "selection" :
                self.GetParent().OnBouton_ok(None)
                return
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        # Recherche si des consommations y sont attachées
        DB = GestionDB.DB()
        req = """
        SELECT IDconso, date, consommations.IDactivite, activites.nom, etat, consommations.IDunite, 
        unites.nom, consommations.IDindividu, individus.nom, individus.prenom
        FROM consommations
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        LEFT JOIN unites ON unites.IDunite = consommations.IDunite
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        WHERE IDprestation=%d
        ORDER BY date
        ;""" % self.IDprestation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq() 
        DB.Close() 
        listeConsommations = []
        for IDconso, date, IDactivite, nomActivite, etat, IDunite, nomUnite, IDindividu, nomIndividu, prenomIndividu in listeDonnees :
            date = DateEngEnDateDD(date)
            dictTemp = {
            "IDconso" : IDconso, "date" : date, "IDactivite" : IDactivite, "nomActivite" : nomActivite, 
            "IDunite" : IDunite, "nomUnite" : nomUnite, 
            "IDindividu" : IDindividu, "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu
            }
            listeConsommations.append(dictTemp)
        listeListeView = []
        for item in listeConsommations :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item["IDconso"] :
                    self.selectionTrack = track
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateDate(dateDD):
            return DateComplete(dateDD)

        liste_Colonnes = [
            ColumnDefn(u"IDconso", "left", 0, "IDconso"),
            ColumnDefn(u"Date", 'left', 150, "date", stringConverter=FormateDate),
            ColumnDefn(u"Individu", "left", 130, "individu"),
            ColumnDefn(u"Activité", "left", 120, "nomActivite"),
            ColumnDefn(u"Unité", "left", 120, "nomUnite"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucune consommation")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
    
    def SetIDprestation(self, IDprestation=0):
        if IDprestation == None :
            IDprestation = 0
        self.IDprestation = IDprestation
        self.MAJ() 
       
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
        # Création du menu contextuel
        menuPop = wx.Menu()

##        # Item Modifier
##        item = wx.MenuItem(menuPop, 10, u"Ajouter")
##        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
##        
##        menuPop.AppendSeparator()
##
##        # Item Ajouter
##        item = wx.MenuItem(menuPop, 20, u"Modifier")
##        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
##        if noSelection == True : item.Enable(False)
##        
##        # Item Supprimer
##        item = wx.MenuItem(menuPop, 30, u"Supprimer")
##        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
##        if noSelection == True : item.Enable(False)
##                
##        menuPop.AppendSeparator()
    
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
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, u"Exporter au format Texte")
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, u"Exporter au format Excel")
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des consommations", format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des consommations", format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=u"Liste des consommations")
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=u"Liste des consommations")

    def Ajouter(self, event):
        import DLG_Saisie_medecin
        dlg = DLG_Saisie_medecin.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            prenom = dlg.GetPrenom()
            rue = dlg.GetRue()
            cp = dlg.GetCp()
            ville = dlg.GetVille()
            tel_cabinet = dlg.GetTel()
            tel_mobile = dlg.GetMobile()
            DB = GestionDB.DB()
            listeDonnees = [
                ("nom", nom ),
                ("prenom", prenom),
                ("rue_resid", rue),
                ("cp_resid", cp),
                ("ville_resid", ville),
                ("tel_cabinet", tel_cabinet),
                ("tel_mobile", tel_mobile),
                ]
            IDmedecin = DB.ReqInsert("medecins", listeDonnees)
            DB.Close()
            self.MAJ(IDmedecin)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun médecin dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        import DLG_Saisie_medecin
        IDmedecin = self.Selection()[0].IDmedecin
        dlg = DLG_Saisie_medecin.Dialog(self)
        dlg.SetNom(self.Selection()[0].nom)
        dlg.SetPrenom(self.Selection()[0].prenom)
        dlg.SetRue(self.Selection()[0].rue_resid)
        dlg.SetCp(self.Selection()[0].cp_resid)
        dlg.SetVille(self.Selection()[0].ville_resid)
        dlg.SetTel(self.Selection()[0].tel_cabinet)
        dlg.SetMobile(self.Selection()[0].tel_mobile)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetNom()
            prenom = dlg.GetPrenom()
            rue = dlg.GetRue()
            cp = dlg.GetCp()
            ville = dlg.GetVille()
            tel_cabinet = dlg.GetTel()
            tel_mobile = dlg.GetMobile()
            DB = GestionDB.DB()
            listeDonnees = [
                ("nom", nom ),
                ("prenom", prenom),
                ("rue_resid", rue),
                ("cp_resid", cp),
                ("ville_resid", ville),
                ("tel_cabinet", tel_cabinet),
                ("tel_mobile", tel_mobile),
                ]
            DB.ReqMAJ("medecins", listeDonnees, "IDmedecin", IDmedecin)
            DB.Close()
            self.MAJ(IDmedecin)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun médecin dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer ce médecin ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDmedecin = self.Selection()[0].IDmedecin
            DB = GestionDB.DB()
            DB.ReqDEL("medecins", "IDmedecin", IDmedecin)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()


# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher un médecin...")
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)
    
    def OnEnter(self, event):
        listeObjets = self.listView.GetFilteredObjects()
        if len(listeObjets) == 0 : return
        track = listeObjets[0]
        self.listView.SelectObject(track)
        if self.GetParent().GetName() == "DLG_medecin" :
            self.GetParent().OnBouton_ok(None)
        
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
        self.myOlv = ListView(panel, id=-1, IDprestation=102 ,name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
