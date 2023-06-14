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

from Utils import UTILS_Utilisateurs


class Track(object):
    def __init__(self, donnees):
        self.IDmedecin = donnees[0]
        self.nom = donnees[1]
        self.prenom = donnees[2]
        self.rue_resid = donnees[3]
        self.cp_resid = donnees[4]
        self.ville_resid = donnees[5]
        self.tel_cabinet = donnees[6]
        self.tel_mobile = donnees[7]


    
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
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
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
        db = GestionDB.DB()
        req = """SELECT IDmedecin, nom, prenom, rue_resid, cp_resid, ville_resid, tel_cabinet, tel_mobile
        FROM medecins ORDER BY nom, prenom; """ 
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
            ColumnDefn(_(u"ID"), "left", 0, "IDmedecin", typeDonnee="entier"),
            ColumnDefn(_(u"Nom"), 'left', 120, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Prénom"), "left", 120, "prenom", typeDonnee="texte"),
            ColumnDefn(_(u"Rue"), "left", 140, "rue_resid", typeDonnee="texte"),
            ColumnDefn(_(u"C.P."), "left", 45, "cp_resid", typeDonnee="texte"),
            ColumnDefn(_(u"Ville"), "left", 110, "ville_resid", typeDonnee="texte"),
            ColumnDefn(_(u"Tél. Cabinet"), "left", 100, "tel_cabinet", typeDonnee="texte"),
            ColumnDefn(_(u"Tél. Mobile"), "left", 100, "tel_mobile", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun médecin"))
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
            ID = self.Selection()[0].IDmedecin
                
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des médecins"), format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des médecins"), format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_medecins", "creer") == False : return
        from Dlg import DLG_Saisie_medecin
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
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_medecins", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun médecin dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        from Dlg import DLG_Saisie_medecin
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
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_medecins", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun médecin dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDmedecin = self.Selection()[0].IDmedecin
        
        # Vérifie que ce médecin n'a pas déjà attribué à un individu
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDindividu)
        FROM individus 
        WHERE IDmedecin=%d
        ;""" % IDmedecin
        DB.ExecuterReq(req)
        nbreIndividus = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreIndividus > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce médecin a déjà été attribué à %d individu(s).\n\nVous ne pouvez donc pas le supprimer !") % nbreIndividus, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce médecin ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("medecins", "IDmedecin", IDmedecin)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()


# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un médecin..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
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
