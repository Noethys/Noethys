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
import datetime
import os
import cStringIO

import GestionDB

import DLG_Saisie_emetteur

from ObjectListView import FastObjectListView, ColumnDefn, Filter

import UTILS_Utilisateurs


TAILLE_IMAGE = (132/2.0, 72/2.0)
IMAGE_DEFAUT = "Images/Special/Image_non_disponible.png"



class Track(object):
    def __init__(self, donnees):
        self.IDemetteur = donnees[0]
        self.IDmode = donnees[1]
        self.nom = donnees[2]
        self.bufferImage = donnees[3]
        self.label_mode = donnees[4]
        self.bmp = self.GetImage()

    def GetImage(self):
        """ Récupère une image """            
        # Recherche de l'image
        if self.bufferImage != None :
            io = cStringIO.StringIO(self.bufferImage)
            img = wx.ImageFromStream(io, wx.BITMAP_TYPE_JPEG)
            bmp = img.Rescale(width=TAILLE_IMAGE[0], height=TAILLE_IMAGE[1], quality=wx.IMAGE_QUALITY_HIGH) 
            bmp = bmp.ConvertToBitmap()
            return bmp
        else:
            # Si aucune image est trouvée, on prend l'image par défaut
            bmp = self.GetImageDefaut() 
            return bmp
    
    def GetImageDefaut(self):
        if os.path.isfile(IMAGE_DEFAUT):
            bmp = wx.Bitmap(IMAGE_DEFAUT, wx.BITMAP_TYPE_ANY) 
            bmp = bmp.ConvertToImage()
            bmp = bmp.Rescale(width=TAILLE_IMAGE[0], height=TAILLE_IMAGE[1], quality=wx.IMAGE_QUALITY_HIGH) 
            bmp = bmp.ConvertToBitmap()
            return bmp
        return None



class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.IDmode = None
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
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
        db = GestionDB.DB()
        req = """SELECT IDemetteur, emetteurs.IDmode, nom, emetteurs.image, modes_reglements.label
        FROM emetteurs
        LEFT JOIN modes_reglements ON emetteurs.IDmode = modes_reglements.IDmode
        %s
        """ % self.criteres
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
        
        # Création du imageList avec une taille personnalisée
        dictImages = {}
        imageList = wx.ImageList(TAILLE_IMAGE[0], TAILLE_IMAGE[1])
        for track in self.donnees :
            indexImg = imageList.Add(track.bmp)            
            dictImages[track.IDemetteur] = indexImg
        self.SetImageLists(imageList, imageList)
                    
        def GetImage(track):
            return dictImages[track.IDemetteur]
                    
        liste_Colonnes = [
            ColumnDefn(u"IDemetteur", "left", 0, "IDemetteur"),
            ColumnDefn(u"Image", 'left', TAILLE_IMAGE[0]+1, "", imageGetter=GetImage),
            ColumnDefn(u"Mode de règlement", 'left', 0, "label_mode"),
            ColumnDefn(u"Nom de l'émetteur", 'left', 410, "nom"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucun émetteur")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None, IDmode=None):
        if IDmode != None :
            self.IDmode = IDmode
        if self.IDmode != None :
            self.criteres = "WHERE emetteurs.IDmode=%d" % self.IDmode

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
            ID = self.Selection()[0].IDemetteur
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, u"Ajouter")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des émetteurs", format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des émetteurs", format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_emetteurs", "creer") == False : return
        if self.IDmode == None :
            dlg = wx.MessageDialog(self, u"Vous devez d'abord sélectionner un mode de règlement !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        dlg = DLG_Saisie_emetteur.Dialog(self, IDmode=self.IDmode, IDemetteur=None)
        if dlg.ShowModal() == wx.ID_OK:
            IDemetteur = dlg.GetIDemetteur()
            self.MAJ(IDemetteur)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_emetteurs", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun émetteur à modifier dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDemetteur = self.Selection()[0].IDemetteur
        dlg = DLG_Saisie_emetteur.Dialog(self, IDmode=self.IDmode, IDemetteur=IDemetteur)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDemetteur)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_emetteurs", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun émetteur à supprimer dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDemetteur = self.Selection()[0].IDemetteur
        
        # Vérifie que l'émetteur n'a pas déjà été attribué à un règlement
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDreglement)
        FROM reglements 
        WHERE IDemetteur=%d
        ;""" % IDemetteur
        DB.ExecuterReq(req)
        nbreReglements = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbreReglements > 0 :
            dlg = wx.MessageDialog(self, u"Cet émetteur a déjà été attribué à %d règlement(s).\n\nVous ne pouvez donc pas le supprimer !" % nbreReglements, u"Suppression impossible", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Suppression
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer cet émetteur ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("emetteurs", "IDemetteur", IDemetteur)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()



# -----------------------------------------------------------------------------------------------------------------

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
