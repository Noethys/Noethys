#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
import os
import FonctionsPerso


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

LISTE_EXTENSIONS = ["bmp", "doc", "docx", "gif", "jpeg", "jpg", "pdf", "png", "tous", "xls", "xlsx", "zip", "plusieurs",]


class Track(object):
    def __init__(self, fichier=""):
        self.fichier = fichier

        self.nomFichier = os.path.basename(fichier)
        self.extension = fichier.split('.')[-1].lower()
        if self.extension not in LISTE_EXTENSIONS :
            self.extension = "tous"
        self.taille = os.path.getsize(fichier)
        if self.taille != None :
            if self.taille >= 1000000 :
                texteTaille = "%s Mo" % (self.taille/1000000)
            else :
                texteTaille = "%s Ko" % (self.taille/1000)
            self.label = u"%s (%s)" % (self.nomFichier, texteTaille)
        else :
            self.label = self.nomFichier
            

        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.listeDonnees = kwds.pop("listeDonnees", [])
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
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        listeListeView = []
        for item in self.listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == track.fichier :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Préparation de la listeImages
        self.dictImages = {}
        for extension in LISTE_EXTENSIONS :
            self.AddNamedImages(extension, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fichier_%s.png" % extension), wx.BITMAP_TYPE_PNG))
        
        # Formatage des données
        def GetImagePiece(track):
            return track.extension

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, None),
            ColumnDefn(_(u"Pièce"), 'left', 180, "label", imageGetter=GetImagePiece, isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune pièce"))
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
##        self._ResizeSpaceFillingColumns() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            selection = None
        else:
            selection = self.Selection()[0]

        # Création du menu contextuel
        menuPop = wx.Menu()
        
        # Ajouter pièce jointe
        item = wx.MenuItem(menuPop, 20, _(u"Ajouter"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=20)
        
        # Retirer pièce jointe
        item = wx.MenuItem(menuPop, 30, _(u"Retirer"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Retirer, id=30)
        if selection == None :
            item.Enable(False)

        menuPop.AppendSeparator()

        # Ouvrir pièce jointe
        item = wx.MenuItem(menuPop, 60, _(u"Ouvrir la pièce"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ouvrir, id=60)
        if selection == None :
            item.Enable(False)

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

    def SetFichiers(self, listeFichiers=[]):
        """ Pour une saisie manuelle directe """
        for cheminFichier in listeFichiers :
            self.listeDonnees.append(cheminFichier)
        self.MAJ()

    def Ajouter(self, event):
        """ Demande l'emplacement du fichier à joindre """
        standardPath = wx.StandardPaths.Get()
        rep = standardPath.GetDocumentsDir()
        dlg = wx.FileDialog(self, message=_(u"Veuillez sélectionner le ou les fichiers à joindre"), defaultDir=rep, defaultFile="", style=wx.OPEN|wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            chemins = dlg.GetPaths()
        else:
            return
        dlg.Destroy()
        listeTemp = []
        for fichier in chemins :
            valide = True
            if fichier in self.listeDonnees :
                dlg = wx.MessageDialog(self, _(u"Le fichier '%s' est déjà dans la liste !") % os.path.basename(fichier), "Erreur", wx.OK| wx.ICON_EXCLAMATION)  
                dlg.ShowModal()
                dlg.Destroy()
                valide = False
            if valide == True :
                self.listeDonnees.append(fichier)
        self.MAJ()
        
    def Retirer(self, event):
        """ Retirer pièces """
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une pièce à retirer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        self.listeDonnees.remove(track.fichier)
        self.MAJ() 

    def Ouvrir(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une pièce à ouvrir dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        FonctionsPerso.LanceFichierExterne(track.fichier)

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des pièces jointes"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des pièces jointes"), format="A", orientation=wx.PORTRAIT)
        prt.Print()
    
    def GetDonnees(self):
        return self.listeDonnees
    

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        listeDonnees = []
        
        self.myOlv = ListView(panel, id=-1, listeDonnees=listeDonnees, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
