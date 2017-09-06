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
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Questionnaire
from Ctrl import CTRL_Logo
import GestionDB


class CTRL_Categorie(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.MAJ()
        if len(self.dictDonnees) > 0:
            self.SetSelection(0)

    def MAJ(self):
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)

    def GetListeDonnees(self):
        # Importation des catégories
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, nom
        FROM produits_categories
        ORDER BY nom
        ;"""
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()
        listeItems = []
        self.dictDonnees = {}
        self.dictCategories = {}
        index = 0
        for IDcategorie, nom in listeCategories:
            dictTemp = {"IDcategorie": IDcategorie, "nom": nom}
            self.dictDonnees[index] = dictTemp
            self.dictCategories[IDcategorie] = dictTemp
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["IDcategorie"] == ID:
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1: return None
        return self.dictDonnees[index]["IDcategorie"]




class Dialog(wx.Dialog):
    def __init__(self, parent, IDproduit=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDproduit = IDproduit
        self.logo = None

        if self.IDproduit == None :
            self.SetTitle(_(u"Saisie d'un produit"))
        else :
            self.SetTitle(_(u"Modification d'un produit"))

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = CTRL_Categorie(self)
        self.bouton_categories = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        self.label_observations = wx.StaticText(self, -1, _(u"Notes :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)

        # Logo
        self.staticbox_logo_staticbox = wx.StaticBox(self, -1, _(u"Image"))
        self.ctrl_logo = CTRL_Logo.CTRL(self, qualite=100, couleurFond=wx.Colour(255, 255, 255), size=(110, 110) )
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_visualiser = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))

        # Questionnaire
        self.staticbox_questionnaire_staticbox = wx.StaticBox(self, -1, _(u"Questionnaire"))
        self.ctrl_questionnaire = CTRL_Questionnaire.CTRL(self, type="produit", IDdonnee=self.IDproduit)
        self.ctrl_questionnaire.SetMinSize((620, 250))

        # Options
        # self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        # self.label_image_interactive = wx.StaticText(self, -1, _(u"Image interactive :"))
        # self.ctrl_image_interactive = wx.TextCtrl(self, -1, u"Non fonctionnelle")

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.ctrl_logo.Ajouter, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_logo.MAJ, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_logo.Visualiser, self.bouton_visualiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCategories, self.bouton_categories)

        if self.IDproduit != None :
            self.Importation()
        else :
            self.ImportationDernierProduit()

        self.ctrl_questionnaire.MAJ()
        self.ctrl_nom.SetFocus()

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom du produit")))
        self.ctrl_categorie.SetToolTip(wx.ToolTip(_(u"Sélectionnez la catégorie associée au produit")))
        self.bouton_categories.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des catégories de produits")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez ici des observations éventuelles")))
        self.ctrl_logo.SetToolTip(wx.ToolTip(_(u"Image du produit")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter ou modifier l'image")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'image actuelle")))
        self.bouton_visualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour visualiser l'image actuelle en taille réelle")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider la saisie")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_categorie, 0, wx.ALIGN_RIGHT, 0)

        grid_sizer_categorie = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_categorie.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_categorie.Add(self.bouton_categories, 0, 0, 0)
        grid_sizer_categorie.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_categorie, 1, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        grid_sizer_generalites.AddGrowableRow(2)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_generalites, 1, wx.EXPAND, 10)

        # Logo
        staticbox_logo = wx.StaticBoxSizer(self.staticbox_logo_staticbox, wx.VERTICAL)
        grid_sizer_logo = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_logo_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_logo.Add(self.ctrl_logo, 0, wx.EXPAND, 0)
        grid_sizer_logo_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_logo_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_logo_boutons.Add(self.bouton_visualiser, 0, 0, 0)
        grid_sizer_logo.Add(grid_sizer_logo_boutons, 1, wx.EXPAND, 0)
        grid_sizer_logo.AddGrowableRow(0)
        grid_sizer_logo.AddGrowableCol(0)
        staticbox_logo.Add(grid_sizer_logo, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_logo, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Questionnaire
        staticbox_questionnaire = wx.StaticBoxSizer(self.staticbox_questionnaire_staticbox, wx.VERTICAL)
        staticbox_questionnaire.Add(self.ctrl_questionnaire, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_questionnaire, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Options
        # staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        #
        # grid_sizer_options = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        # grid_sizer_options.Add(self.label_image_interactive, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        # grid_sizer_options.Add(self.ctrl_image_interactive, 0, wx.EXPAND, 0)
        # grid_sizer_options.AddGrowableCol(1)
        # staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        # grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonCategories(self, event):
        IDcategorie = self.ctrl_categorie.GetID()
        import DLG_Categories_produits
        dlg = DLG_Categories_produits.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_categorie.MAJ()
        self.ctrl_categorie.SetID(IDcategorie)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        observations = self.ctrl_observations.GetValue()
        IDcategorie = self.ctrl_categorie.GetID()

        if len(nom) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce produit !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        if IDcategorie == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une catégorie pour ce produit !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_categorie.SetFocus()
            return

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
            ("nom", nom),
            ("IDcategorie", IDcategorie),
            ("observations", observations),
            ]

        if self.IDproduit == None :
            self.IDproduit = DB.ReqInsert("produits", listeDonnees)
        else:
            DB.ReqMAJ("produits", listeDonnees, "IDproduit", self.IDproduit)
        
        # Sauvegarde du logo
        if self.ctrl_logo.estModifie == True :
            bmp = self.ctrl_logo.GetBuffer() 
            if bmp != None :
                DB.MAJimage(table="produits", key="IDproduit", IDkey=self.IDproduit, blobImage=bmp, nomChampBlob="image")
            else:
                DB.ReqMAJ("produits", [("image", None),], "IDproduit", self.IDproduit)

        # Sauvegarde du questionnaire
        self.ctrl_questionnaire.Sauvegarde(DB=DB, IDdonnee=self.IDproduit)

        DB.Close()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetIDproduit(self):
        return self.IDproduit

    def Importation(self):
        """ Importation des données """
        db = GestionDB.DB()
        req = """SELECT nom, observations, image, IDcategorie
        FROM produits WHERE IDproduit=%d;""" % self.IDproduit
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        nom, observations, image, IDcategorie = listeDonnees[0]

        # Généralités
        self.ctrl_nom.SetValue(nom)
        self.ctrl_categorie.SetID(IDcategorie)
        self.ctrl_observations.SetValue(observations)

        # Logo
        if image != None :
            self.ctrl_logo.ChargeFromBuffer(image)

    def ImportationDernierProduit(self):
        DB = GestionDB.DB()
        req = """SELECT IDproduit, IDcategorie
        FROM produits
        ORDER BY IDproduit DESC
        LIMIT 1
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDproduit, IDcategorie = listeDonnees[0]
        self.ctrl_categorie.SetID(IDcategorie)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDproduit=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()


