#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import CTRL_Saisie_date
import GestionDB

import DLG_Saisie_pb_sante


import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Utilisateurs


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


class Track(object):
    def __init__(self, donnees):
        self.IDprobleme = donnees[0]
        self.IDtype = donnees[1]
        self.intitule = donnees[2]
        self.date_debut = donnees[3]
        self.date_fin = donnees[4]
        self.description = donnees[5]
        self.traitement_medical = donnees[6]
        self.description_traitement = donnees[7]
        self.date_debut_traitement = donnees[8]
        self.date_fin_traitement = donnees[9]
        self.eviction = donnees[10]
        self.date_debut_eviction = donnees[11]
        self.date_fin_eviction = donnees[12]
        self.diffusion_listing_enfants = donnees[13]
        self.diffusion_listing_conso = donnees[14]
        self.diffusion_listing_repas = donnees[15]
        
        self.texteComplet = self.intitule
        if self.description != "" and self.description != None :
            self.texteComplet += u" : " + self.description
        
        if self.date_fin != None and self.date_fin != "2999-01-01" :
            dateDD_fin = datetime.date(int(self.date_fin[:4]), int(self.date_fin[5:7]), int(self.date_fin[8:10]))
            date_jour = datetime.date.today()
            self.nbreJoursRestants = (dateDD_fin - date_jour).days
            if self.nbreJoursRestants > 0 :
                self.valide = True
            else:
                self.valide = False
        else:
            self.nbreJoursRestants = 99999
            self.valide = True

    
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
        listeChamps = [
        "IDprobleme", "IDtype", "intitule", "date_debut", "date_fin", "description",
        "traitement_medical", "description_traitement", "date_debut_traitement", "date_fin_traitement",
        "eviction", "date_debut_eviction", "date_fin_eviction", 
        "diffusion_listing_enfants", "diffusion_listing_conso", "diffusion_listing_repas"]
        db = GestionDB.DB()
        req = """
        SELECT %s
        FROM problemes_sante
        WHERE IDindividu=%d
        """ % (", ".join(listeChamps), self.IDindividu)
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

        # ListImages
        for IDtype, nom, nomImage in DLG_Saisie_pb_sante.LISTE_TYPES :
            self.AddNamedImages(str(IDtype), wx.Bitmap("Images/16x16/%s" % nomImage, wx.BITMAP_TYPE_PNG))
            
        def GetImage(track):
            return str(track.IDtype)
        
        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour((180, 180, 180))
            
        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDprobleme", typeDonnee="entier"),
            ColumnDefn(_(u"Intitulé"), 'left', 360, "texteComplet", typeDonnee="texte", imageGetter=GetImage, isSpaceFilling=True),
##            ColumnDefn(_(u"Nbre de jours restants"), 'left', 0, "nbreJoursRestants"),
            ]
        
        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune information médicale"))
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
            ID = self.Selection()[0].IDprobleme
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

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
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des informations médicales"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des informations médicales"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_pb_sante", "creer") == False : return
        dlg = DLG_Saisie_pb_sante.Dialog(self, IDindividu=self.IDindividu, IDprobleme=None)
        if dlg.ShowModal() == wx.ID_OK:
            IDprobleme = dlg.GetIDprobleme()
            self.MAJ(IDprobleme)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_pb_sante", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune information médicale à modifier dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDprobleme = self.Selection()[0].IDprobleme
        dlg = DLG_Saisie_pb_sante.Dialog(self, IDindividu=self.IDindividu, IDprobleme=IDprobleme)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDprobleme)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_pb_sante", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune information médicale à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette information médicale ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDprobleme = self.Selection()[0].IDprobleme
            DB = GestionDB.DB()
            DB.ReqDEL("problemes_sante", "IDprobleme", IDprobleme)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()





class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, IDindividu=27, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
