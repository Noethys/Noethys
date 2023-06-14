#!/usr/bin/env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import GestionDB

if wx.VERSION < (2, 9, 0, 0) :
    from Outils import ultimatelistctrl as ULC
else :
    from wx.lib.agw import ultimatelistctrl as ULC


class CTRL(ULC.UltimateListCtrl):
    def __init__(self, parent, listePieces=[]):
        ULC.UltimateListCtrl.__init__(self, parent, -1, 
                                                #agwStyle=ULC.ULC_SINGLE_SEL | ULC.ULC_REPORT |  ULC.ULC_NO_HEADER | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT,
                                                agwStyle=wx.LC_LIST | ULC.ULC_SINGLE_SEL,
                                                )
        self.parent = parent
        self.listePieces = listePieces
        
        # Liste images
        self.dictImages = {}
        il = wx.ImageList(16, 16, True)
        listeExtensions = ["bmp", "doc", "docx", "gif", "jpeg", "jpg", "pdf", "png", "tous", "xls", "xlsx", "zip",]
        for extension in listeExtensions :
            self.dictImages[extension] = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fichier_%s.png" % extension), wx.BITMAP_TYPE_ANY))
        self.AssignImageList(il, wx.IMAGE_LIST_SMALL)
            
        self.Bind(ULC.EVT_LIST_ITEM_RIGHT_CLICK, self.OnContextMenu)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)

        self.MAJ()
    
    def MAJ(self):
        self.DeleteAllItems() 
        index = 0
        for dictFichier in self.listePieces :
            nomFichier = os.path.basename(dictFichier["nom"])
            extension = dictFichier["extension"]
            taille = dictFichier["taille"]
            obligatoire = dictFichier["obligatoire"]

            if taille != None :
                if taille >= 1000000 :
                    texteTaille = "%s Mo" % (taille/1000000)
                else :
                    texteTaille = "%s Ko" % (taille/1000)
                label = u"%s (%s)" % (nomFichier, texteTaille)
            else :
                label = nomFichier
                
            if extension in self.dictImages :
                bmp = self.dictImages[extension]
            else:
                bmp = self.dictImages["tous"]
                
            self.InsertImageStringItem(index, label, bmp)
            self.SetItemData(index, dictFichier)            
            
            if obligatoire == True :
                self.EnableItem(index, enable=False)
                self.SetItemTextColour(index, wx.Colour(150, 150, 150))
                
            index += 1
            
        try :
            if len(self.listePieces) > 0 :
                self.parent.box_pieces_staticbox.SetLabel(u"Pièces jointes communes (%d)" % len(self.listePieces))
            else:
                self.parent.box_pieces_staticbox.SetLabel(u"Pièces jointes communes")
        except :
            pass
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item, flags = self.HitTest((event.GetX(), event.GetY()))
        if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
            self.Select(item)
            noSelection = False
        else:
            noSelection = True
            self.ToutDeselectionner()
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def ToutDeselectionner(self):
        index = self.GetFirstSelected()
        while index != -1:
            self.Select(index, False)
            index = self.GetNextSelected(index)

    def Ajouter(self, event):
        # Demande l'emplacement du fichier à joindre
        standardPath = wx.StandardPaths.Get()
        rep = standardPath.GetDocumentsDir()
        dlg = wx.FileDialog(self, message=_(u"Veuillez sélectionner le ou les fichiers à joindre"), defaultDir=rep, defaultFile="", style=wx.FD_OPEN|wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            chemins = dlg.GetPaths()
        else:
            return
        dlg.Destroy()
        for fichier in chemins :
            valide = True
            
            for dictFichier in self.listePieces :
                if fichier == dictFichier["nom"] :
                    dlg = wx.MessageDialog(self, _(u"Le fichier '%s' est déjà dans la liste !") % os.path.basename(fichier), "Erreur", wx.OK| wx.ICON_EXCLAMATION)  
                    dlg.ShowModal()
                    dlg.Destroy()
                    valide = False
            
            if valide == True :
                extension = fichier.split('.')[-1].lower()
                taille = os.path.getsize(fichier)
                dictFichier = {"nom":fichier, "extension":extension, "taille":taille, "obligatoire":False}
                self.listePieces.append(dictFichier)
        self.MAJ()

    def Supprimer(self, event):
        if self.GetSelectedItemCount() == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune pièce jointe à enlever de la liste !"), "Erreur", wx.OK| wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        index = self.GetFirstSelected()
        if self.listePieces[index]["obligatoire"] == True :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas désélectionner cette pièce !"), "Erreur", wx.OK| wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.listePieces.pop(index)
        self.MAJ()
    
    def SetPieces(self, listePieces=[]):
        self.listePieces = listePieces
        self.MAJ() 
        

# ----------------------------------------------------------------------------------------------------------------------        

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        listePieces = []
        for x in range(0, 1) :
            listePieces.append(
                {"nom":_(u"Facture"), "extension":"pdf", "taille":None, "obligatoire":True},
                )

        self.ctrl = CTRL(panel, listePieces=listePieces)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()