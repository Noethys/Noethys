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
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Questionnaire
from Ctrl import CTRL_Logo
import GestionDB


class Dialog(wx.Dialog):
    def __init__(self, parent, IDcategorie=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDcategorie = IDcategorie
        self.logo = None

        if self.IDcategorie == None :
            self.SetTitle(_(u"Saisie d'une catégorie de produits"))
        else :
            self.SetTitle(_(u"Modification d'une catégorie de produits"))

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_observations = wx.StaticText(self, -1, _(u"Notes :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)

        # Logo
        self.staticbox_logo_staticbox = wx.StaticBox(self, -1, _(u"Image"))
        self.ctrl_logo = CTRL_Logo.CTRL(self, qualite=100, couleurFond=wx.Colour(255, 255, 255), size=(83, 83) )
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_visualiser = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))

        # Questionnaire
        self.staticbox_questionnaire_staticbox = wx.StaticBox(self, -1, _(u"Questionnaire"))
        self.ctrl_questionnaire = CTRL_Questionnaire.CTRL(self, type="categorie_produit", IDdonnee=self.IDcategorie)
        self.ctrl_questionnaire.SetMinSize((620, 270))

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

        if self.IDcategorie != None :
            self.Importation()

        self.ctrl_questionnaire.MAJ()
        self.ctrl_nom.SetFocus()

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom de la catégorie de produits")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez ici des observations éventuelles")))
        self.ctrl_logo.SetToolTip(wx.ToolTip(_(u"Image de la catégorie de produits")))
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
        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        grid_sizer_generalites.AddGrowableRow(1)
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

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Categoriesdeproduits")

    def OnBoutonOk(self, event):
        nom = self.ctrl_nom.GetValue()
        observations = self.ctrl_observations.GetValue()

        if len(nom) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour cette catégorie de produits !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
            ("nom", nom),
            ("observations", observations),
            ]

        if self.IDcategorie == None :
            self.IDcategorie = DB.ReqInsert("produits_categories", listeDonnees)
        else:
            DB.ReqMAJ("produits_categories", listeDonnees, "IDcategorie", self.IDcategorie)
        
        # Sauvegarde du logo
        if self.ctrl_logo.estModifie == True :
            bmp = self.ctrl_logo.GetBuffer() 
            if bmp != None :
                DB.MAJimage(table="produits_categories", key="IDcategorie", IDkey=self.IDcategorie, blobImage=bmp, nomChampBlob="image")
            else:
                DB.ReqMAJ("produits_categories", [("image", None),], "IDcategorie", self.IDcategorie)

        # Sauvegarde du questionnaire
        self.ctrl_questionnaire.Sauvegarde(DB=DB, IDdonnee=self.IDcategorie)

        DB.Close()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetIDcategorie(self):
        return self.IDcategorie

    def Importation(self):
        """ Importation des données """
        db = GestionDB.DB()
        req = """SELECT nom, observations, image
        FROM produits_categories WHERE IDcategorie=%d;""" % self.IDcategorie
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        nom, observations, image = listeDonnees[0]

        # Généralités
        self.ctrl_nom.SetValue(nom)
        self.ctrl_observations.SetValue(observations)

        # Logo
        if image != None :
            self.ctrl_logo.ChargeFromBuffer(image)





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDcategorie=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()


