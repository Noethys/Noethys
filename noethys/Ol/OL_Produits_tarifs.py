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
import GestionDB
from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils
from Ctrl.CTRL_Tarification_calcul import LISTE_METHODES
from Utils import UTILS_Dates

from Dlg.DLG_Ouvertures import Track_tarif




class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.donnees = []
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)

    def SetTarifs(self, tarifs=[]):
        self.donnees = tarifs
        self.MAJ()

    def InitModel(self):
        pass

    def GetTracks(self):
        """ Récupération des données """
        return self.track_evenement.tarifs

    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def GetMethode(code):
            for dictValeurs in LISTE_METHODES:
                if dictValeurs["code"] == code :
                    return dictValeurs["label"]
            return ""

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDtarif", typeDonnee="entier"),
            ColumnDefn(_(u"Du"), 'left', 80, "date_debut", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"au"), 'left', 80, "date_fin", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Description"), "left", 190, "description", typeDonnee="texte"),
            ColumnDefn(_(u"Méthode de calcul"), 'left', 190, "methode", typeDonnee="texte", stringConverter=GetMethode),
            ]

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun tarif"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, track=None):
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if track != None :
            self.SelectObject(track, deselectOthers=True, ensureVisible=True)

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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event):
        track_tarif = Track_tarif()
        nom_tarif = self.GetGrandParent().GetParent().ctrl_nom.GetValue()
        from Dlg import DLG_Saisie_tarification
        dlg = DLG_Saisie_tarification.Dialog(self, IDactivite=None, IDtarif=None, nom_tarif=nom_tarif,
                                             choix_pages=["generalites", "calcul"], track_tarif=track_tarif)
        dlg.toolbook.GetPage("calcul").SetFiltreTypeTarif("PRODUIT")
        dlg.toolbook.GetPage("generalites").MasqueCategories()
        dlg.SetMinSize((700, 450))
        dlg.SetSize((700, 450))

        if dlg.ShowModal() == wx.ID_OK:
            track_tarif = dlg.GetTrackTarif()
            self.donnees.append(track_tarif)
            self.MAJ(track_tarif)
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun tarif à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track_tarif = self.Selection()[0]
        nom_tarif = self.GetGrandParent().GetParent().ctrl_nom.GetValue()
        from Dlg import DLG_Saisie_tarification
        dlg = DLG_Saisie_tarification.Dialog(self, IDactivite=None, IDtarif=None, nom_tarif=nom_tarif, choix_pages=["generalites", "calcul"], track_tarif=track_tarif)
        dlg.toolbook.GetPage("calcul").SetFiltreTypeTarif("PRODUIT")
        dlg.toolbook.GetPage("generalites").MasqueCategories()
        dlg.SetMinSize((700, 450))
        dlg.SetSize((700, 450))

        if dlg.ShowModal() == wx.ID_OK:
            track_tarif.dirty = True
            self.MAJ(track_tarif)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun tarif à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track_tarif = self.Selection()[0]

        # Vérifie que ce tarif n'est pas déjà attribué à une prestation
        if track_tarif.IDtarif != None :
            DB = GestionDB.DB()
            req = """SELECT IDprestation FROM prestations WHERE IDtarif=%d;""" % track_tarif.IDtarif
            DB.ExecuterReq(req)
            listePrestations = DB.ResultatReq()
            DB.Close()
            nbrePrestations = len(listePrestations)
            if nbrePrestations > 0 :
                dlg = wx.MessageDialog(self, _(u"Ce tarif a déjà été attribué à %d prestations.\nIl est donc impossible de le supprimer !") % nbrePrestations, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce tarif ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            self.donnees.remove(track_tarif)
            self.MAJ()
        dlg.Destroy()

    def GetTracksTarifs(self):
        return self.donnees


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
