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

import GestionDB
import CTRL_Image_mode
import CTRL_Bandeau
import OL_Emetteurs

import Image
import os
import cStringIO
import wx.combo


TAILLE_IMAGE = (132/2.0, 72/2.0)
IMAGE_DEFAUT = "Images/Special/Image_non_disponible.png"


class CTRL_Mode(wx.combo.BitmapComboBox):
    def __init__(self, parent, size=(-1,  -1)):
        wx.combo.BitmapComboBox.__init__(self, parent, size=size, style=wx.CB_READONLY)
        self.parent = parent
        self.MAJlisteDonnees() 
        if len(self.dictDonnees) > 0 :
            self.SetSelection(0)
    
    def MAJlisteDonnees(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        for label, bmp in listeItems :
            self.Append(label, bmp, label)
    
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDmode, label, image
        FROM modes_reglements
        ORDER BY label;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDmode, label, bufferImage in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDmode }
            bmp = self.GetImage(bufferImage)
            listeItems.append((label, bmp))
            index += 1
        return listeItems

    def GetImage(self, bufferImage=None):
        """ Récupère une image """         
        qualite = wx.IMAGE_QUALITY_HIGH 

        # Recherche de l'image
        if bufferImage != None :
            io = cStringIO.StringIO(bufferImage)
            img = wx.ImageFromStream(io, wx.BITMAP_TYPE_JPEG)
            bmp = img.Rescale(width=TAILLE_IMAGE[0], height=TAILLE_IMAGE[1], quality=qualite) 
            bmp = bmp.ConvertToBitmap()
            return bmp
        else:
            # Si aucune image est trouvée, on prend l'image par défaut
            bmp = self.GetImageDefaut() 
            return bmp
    
    def GetImageDefaut(self):
        # Adaptation pour wxPython >= 2.9
        if wx.VERSION > (2, 9, 0, 0) :
            qualite = wx.IMAGE_QUALITY_BICUBIC
        else :
            qualite = 100 

        if os.path.isfile(IMAGE_DEFAUT):
            bmp = wx.Bitmap(IMAGE_DEFAUT, wx.BITMAP_TYPE_ANY) 
            bmp = bmp.ConvertToImage()
            bmp = bmp.Rescale(width=TAILLE_IMAGE[0], height=TAILLE_IMAGE[1], quality=qualite) 
            bmp = bmp.ConvertToBitmap()
            return bmp
        return None

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Mode_archive(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJlisteDonnees() 
        if len(self.dictDonnees) > 0 :
            self.SetSelection(0)
    
    def MAJlisteDonnees(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDmode, label, image
        FROM modes_reglements
        ORDER BY label;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDmode, label, image in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDmode }
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


# -------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Emetteurs", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Vous pouvez ici saisir, modifier ou supprimer des émetteurs de règlements. Commencez toujours par sélectionner un mode de règlement dans la liste déroulante puis utilisez les boutons de commande de la liste des émetteurs.")
        titre = _(u"Gestion des émetteurs de règlements")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Mode_reglement.png")
        
        # Mode
        self.staticbox_mode_staticbox = wx.StaticBox(self, -1, _(u"Mode de règlement"))
        self.label_mode = wx.StaticText(self, -1, _(u"Mode de règlement :"))
        self.ctrl_mode = CTRL_Mode(self)
        
        # Emetteurs
        self.staticbox_emetteurs_staticbox = wx.StaticBox(self, -1, _(u"Emetteurs"))
        self.ctrl_emetteurs = OL_Emetteurs.ListView(self, id=-1, name="OL_Emetteurs", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        self.boutons_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_COMBOBOX, self.OnChoixMode, self.ctrl_mode)
        self.Bind(wx.EVT_BUTTON, self.OnAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.boutons_aide)
        
        # Initialisation des contrôles
        self.OnChoixMode(None)
        

    def __set_properties(self):
        self.ctrl_mode.SetToolTipString(_(u"Sélectionnez ici un mode de règlement"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un émetteur à ce mode de règlement"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier l'émetteur sélectionné dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer l'émetteur sélectionné dans la liste"))
        self.boutons_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer la fenetre"))
        self.SetMinSize((600, 640))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_emetteurs = wx.StaticBoxSizer(self.staticbox_emetteurs_staticbox, wx.VERTICAL)
        grid_sizer_emetteurs = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_boutons_emetteurs = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        staticbox_mode = wx.StaticBoxSizer(self.staticbox_mode_staticbox, wx.VERTICAL)
        grid_sizer_mode = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_mode.Add(self.label_mode, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mode.Add(self.ctrl_mode, 0, wx.EXPAND, 0)
        grid_sizer_mode.AddGrowableCol(1)
        staticbox_mode.Add(grid_sizer_mode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_mode, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_emetteurs.Add(self.ctrl_emetteurs, 1, wx.EXPAND, 0)
        grid_sizer_boutons_emetteurs.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_emetteurs.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_emetteurs.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_emetteurs.Add(grid_sizer_boutons_emetteurs, 1, wx.EXPAND, 0)
        grid_sizer_emetteurs.AddGrowableRow(0)
        grid_sizer_emetteurs.AddGrowableCol(0)
        staticbox_emetteurs.Add(grid_sizer_emetteurs, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_emetteurs, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.boutons_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnChoixMode(self, event): 
        IDmode = self.ctrl_mode.GetID()
        if IDmode != None :
            self.ctrl_emetteurs.MAJ(IDmode=IDmode)

    def OnAjouter(self, event): 
        self.ctrl_emetteurs.Ajouter(None)

    def OnModifier(self, event): 
        self.ctrl_emetteurs.Modifier(None)

    def OnSupprimer(self, event): 
        self.ctrl_emetteurs.Supprimer(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Emetteursderglements")
    
    def SelectMode(self, IDmode=None):
        if IDmode != None :
            self.ctrl_mode.SetID(IDmode)
            self.OnChoixMode(None)
    


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
