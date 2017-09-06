#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
import GestionDB
import cStringIO
from Utils import UTILS_Images
from wx.lib.agw import ultimatelistctrl as ULC
from Ctrl import CTRL_Bouton_image



class CTRL(ULC.UltimateListCtrl):
    def __init__(self, parent):
        ULC.UltimateListCtrl.__init__(self, parent, -1, agwStyle=wx.LC_ICON | wx.LC_AUTOARRANGE)
        self.parent = parent
        self.EnableSelectionVista(True)
        self.taillePhoto = (100, 100)

    def SetTaillePhoto(self, taillePhoto=None):
        self.taillePhoto = taillePhoto
        self.MAJ()

    def MAJ(self):
        self.ClearAll()

        DB = GestionDB.DB()
        req = """SELECT IDmodele, documents_modeles.nom,
        produits_categories.IDcategorie, produits_categories.nom, produits_categories.image
        FROM documents_modeles
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = documents_modeles.IDdonnee
        WHERE documents_modeles.categorie='produits_categories'
        ORDER BY documents_modeles.nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        self.liste_images = []
        for IDmodele, nomModele, IDcategorie, nomCategorie, image in listeDonnees :

            # Conversion en bmp de l'image
            if image != None :
                io = cStringIO.StringIO(image)
                if 'phoenix' in wx.PlatformInfo:
                    img = wx.Image(io, wx.BITMAP_TYPE_PNG)
                else:
                    img = wx.ImageFromStream(io, wx.BITMAP_TYPE_PNG)
                img = UTILS_Images.RecadreImg(img, self.taillePhoto)
                bmp = img.ConvertToBitmap()
            else :
                bmp = None

            # Mémorisation
            dictTemp = {"IDmodele" : IDmodele, "nomModele" : nomModele, "IDcategorie" : IDcategorie,
                        "nomCategorie": nomCategorie, "bmp" : bmp}
            self.liste_images.append(dictTemp)

        # liste images
        dictPhotos = {}
        il = wx.ImageList(self.taillePhoto[0], self.taillePhoto[1], True)

        # Image par défaut
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Categorie_produits_nb.png"), wx.BITMAP_TYPE_PNG)
        img = bmp.ConvertToImage()
        img = UTILS_Images.RecadreImg(img, self.taillePhoto)
        bmp = img.ConvertToBitmap()
        il.Add(bmp)

        for dictImage in self.liste_images :
            if dictImage["bmp"] != None :
                dictPhotos[dictImage["IDmodele"]] = il.Add(dictImage["bmp"])
        self.AssignImageList(il, wx.IMAGE_LIST_NORMAL)

        # Création des items
        index = 0
        for dictImage in self.liste_images:
            label = dictImage["nomModele"]
            if dictPhotos.has_key(dictImage["IDmodele"]):
                indexPhoto = dictPhotos[dictImage["IDmodele"]]
            else :
                indexPhoto = 0
            self.InsertImageStringItem(index, label, indexPhoto)
            self.SetItemData(index, dictImage["IDmodele"])
            self.SetDisabledTextColour(wx.Colour(255, 0, 0))
            index += 1

        # Binds
        self.Bind(ULC.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)

    def OnActivated(self, event):
        dictImage = self.liste_images[event.m_itemIndex]
        from Dlg import DLG_Image_interactive
        dlg = DLG_Image_interactive.Dialog(None, IDmodele=dictImage["IDmodele"])
        dlg.ShowModal()
        dlg.Destroy()




# -----------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        self.parent = parent

        self.ctrl_image = CTRL(self)
        self.ctrl_image.SetMinSize((700, 500))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Logo
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Image_interactive.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle(_(u"Images interactives"))

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.ctrl_image, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 10)

        # Layout
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        sizer_base.Add(grid_sizer_boutons, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

        # Init
        self.ctrl_image.MAJ()


    def OnBoutonFermer(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()

