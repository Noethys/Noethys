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
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils
from Ctrl.CTRL_Tarification_calcul import LISTE_METHODES
from Utils import UTILS_Texte
from Dlg.DLG_Ouvertures import Track_tarif



class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.track_evenement = kwds.pop("track_evenement", None)
        self.dictCategories = self.GetCategoriesTarifs()
        self.donnees = self.track_evenement.tarifs
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        pass
        #self.donnees = self.GetTracks()

    def GetCategoriesTarifs(self):
        DB = GestionDB.DB()
        req = """SELECT IDcategorie_tarif, nom
        FROM categories_tarifs 
        WHERE IDactivite=%d;""" % self.track_evenement.IDactivite
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        dictCategories = {}
        for IDcategorie_tarif, nom in listeCategories:
            dictCategories[IDcategorie_tarif] = nom
        DB.Close()
        return dictCategories

    def GetTracks(self):
        """ Récupération des données """
        return self.track_evenement.tarifs

        # listeID = None
        # DB = GestionDB.DB()
        # req = """SELECT IDtarif, methode, categories_tarifs, description
        # FROM tarifs
        # WHERE IDevenement=%d
        # ;""" % self.IDevenement
        # DB.ExecuterReq(req)
        # listeDonnees = DB.ResultatReq()
        # DB.Close()
        # listeListeView = []
        # for item in listeDonnees :
        #     valide = True
        #     if listeID != None :
        #         if item[0] not in listeID :
        #             valide = False
        #     if valide == True :
        #         track = Track(item)
        #         listeListeView.append(track)
        #         if self.selectionID == item[0] :
        #             self.selectionTrack = track
        # return listeListeView
      
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

        def GetCategories(categories_tarifs):
            listeTemp = []
            for IDcategorie in UTILS_Texte.ConvertStrToListe(categories_tarifs) :
                if self.dictCategories.has_key(IDcategorie) :
                    listeTemp.append(self.dictCategories[IDcategorie])
            return ", ".join(listeTemp)

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDtarif", typeDonnee="entier"),
            ColumnDefn(_(u"Description"), "left", 140, "description", typeDonnee="texte"),
            ColumnDefn(_(u"Méthode de calcul"), 'left', 140, "methode", typeDonnee="texte", stringConverter=GetMethode),
            ColumnDefn(_(u"Catégories de tarifs"), "left", 140, "categories_tarifs", typeDonnee="texte", stringConverter=GetCategories),
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
        menuPop = wx.Menu()

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
        track_tarif = Track_tarif(dictDonnees={"IDactivite":self.track_evenement.IDactivite, "date_debut":self.track_evenement.date, "date_fin":self.track_evenement.date})
        nom_evenement = self.GetParent().ctrl_nom.GetValue()
        from Dlg import DLG_Saisie_tarification
        dlg = DLG_Saisie_tarification.Dialog(self, IDactivite=self.track_evenement.IDactivite, IDtarif=None, nom_tarif=nom_evenement,
                                             choix_pages=["generalites", "conditions", "calcul"], cacher_dates=True, track_tarif=track_tarif)
        dlg.toolbook.GetPage("calcul").SetFiltreTypeTarif("JOURN")
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
        nom_evenement = self.GetParent().ctrl_nom.GetValue()
        from Dlg import DLG_Saisie_tarification
        dlg = DLG_Saisie_tarification.Dialog(self, IDactivite=self.track_evenement.IDactivite, IDtarif=None, nom_tarif=nom_evenement, choix_pages=["generalites", "conditions", "calcul"], cacher_dates=True, track_tarif=track_tarif)
        dlg.toolbook.GetPage("calcul").SetFiltreTypeTarif("JOURN")
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
            # DB = GestionDB.DB()
            # DB.ReqDEL("tarifs", "IDtarif", IDtarif)
            # DB.ReqDEL("combi_tarifs", "IDtarif", IDtarif)
            # DB.ReqDEL("combi_tarifs_unites", "IDtarif", IDtarif)
            # DB.ReqDEL("tarifs_lignes", "IDtarif", IDtarif)
            # DB.Close()
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
