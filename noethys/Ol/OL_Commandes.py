#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Utils import UTILS_Interface
from Utils import UTILS_Dates
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


class Track(object):
    def __init__(self, donnees):
        self.IDcommande = donnees["IDcommande"]
        self.nom = donnees["nom"]
        self.date_debut = donnees["date_debut"]
        self.date_fin = donnees["date_fin"]


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.IDmodele = 0
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def SetIDmodele(self, IDmodele=None):
        self.IDmodele = IDmodele

    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        if self.IDmodele == None :
            IDmodele = 0
        else :
            IDmodele = self.IDmodele
        DB = GestionDB.DB()
        req = """SELECT IDcommande, nom, date_debut, date_fin
        FROM commandes 
        WHERE IDmodele=%d
        ORDER BY date_debut;""" % IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeModeles = []
        for IDcommande, nom, date_debut, date_fin in listeDonnees :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            listeModeles.append({"IDcommande" : IDcommande, "nom" : nom, "date_debut" : date_debut, "date_fin" : date_fin})

        listeListeView = []
        for item in listeModeles :
            track = Track(item)
            listeListeView.append(track)
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDcommande", typeDonnee="entier"),
            ColumnDefn(u"Du", 'left', 80, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(u"Au", 'left', 80, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Nom"), 'left', 200, "nom", typeDonnee="texte", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune commande"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        self.InitModel()
        self.InitObjectListView()

        # Sélection d'un item
        if ID != None :
            for track in self.donnees :
                if track.IDcommande == ID :
                    self.SelectObject(track, deselectOthers=True, ensureVisible=True)
                    break
        else :
            self.DefileDernier()
        self._ResizeSpaceFillingColumns()

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des commandes de repas"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des commandes de repas"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        from Dlg import DLG_Saisie_commande
        dlg = DLG_Saisie_commande.Dialog(self, IDmodele=self.IDmodele, IDcommande=None)
        if dlg.ShowModal() == wx.ID_OK:
            IDcommande = dlg.GetIDcommande()
            self.MAJ(IDcommande)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune commande à modifier dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcommande = self.Selection()[0].IDcommande
        from Dlg import DLG_Saisie_commande
        dlg = DLG_Saisie_commande.Dialog(self, IDmodele=self.IDmodele, IDcommande=IDcommande)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDcommande)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune commande à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        # Confirmation de suppression
        message = _(u"Souhaitez-vous vraiment supprimer cette commande de repas ?")
        dlg = wx.MessageDialog(self, message, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            if track.IDcommande != None :
                DB = GestionDB.DB()
                DB.ReqDEL("commandes", "IDcommande", track.IDcommande)
                DB.ReqDEL("commandes_valeurs", "IDcommande", track.IDcommande)
                #DB.ExecuterReq("DELETE FROM commandes_valeurs WHERE date>='%s' AND date<='%s'" % (track.date_debut, track.date_fin))
                #DB.Commit()
                DB.Close()
            self.MAJ()
        dlg.Destroy()


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
