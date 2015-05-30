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



class Dialog(wx.Dialog):
    def __init__(self, parent, IDmode=None, IDemetteur=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_emetteur", style=wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDmode = IDmode
        self.IDemetteur = IDemetteur
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, u"")
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        self.label_image = wx.StaticText(self, -1, _(u"Image :"))
        self.ctrl_image = CTRL_Image_mode.CTRL(self, table="emetteurs", key="IDemetteur", IDkey=self.IDemetteur, imageDefaut="Images/Special/Image_non_disponible.png", style=wx.BORDER_SUNKEN)
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDemetteur == None :
            self.SetTitle(_(u"Création d'un émetteur"))
        else:
            self.Importation()
            self.SetTitle(_(u"Modification d'un émetteur"))
        
        
        

    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici un nom pour cet émetteur"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour importer une image"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer l'image active"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_image = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_image = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_image, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_image.Add(self.ctrl_image, 0, wx.EXPAND, 0)
        grid_sizer_boutons_image.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_image.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_image.Add(grid_sizer_boutons_image, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(grid_sizer_image, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        staticbox.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAjouter(self, event): 
        self.ctrl_image.Ajouter(sauvegarder=False)
    
    def OnBoutonSupprimer(self, event): 
        self.ctrl_image.Supprimer(sauvegarder=False)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Emetteursderglements")

    def OnBoutonOk(self, event): 
        # Récupération et vérification des données saisies
        nom = self.ctrl_nom.GetValue()
        if nom == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
                
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("nom", nom),
                ("image", None),
                ("IDmode", self.IDmode),
            ]
        if self.IDemetteur == None :
            self.IDemetteur = DB.ReqInsert("emetteurs", listeDonnees)
        else:
            DB.ReqMAJ("emetteurs", listeDonnees, "IDemetteur", self.IDemetteur)
        DB.Close()
        
        # Sauvegarde de l'image
        self.ctrl_image.IDkey = self.IDemetteur
        self.ctrl_image.Sauvegarder() 
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDemetteur(self):
        return self.IDemetteur

    def Importation(self):
        """ Importation des données """
        DB = GestionDB.DB()
        req = """SELECT nom, IDmode
        FROM emetteurs 
        WHERE IDemetteur=%d;""" % self.IDemetteur
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        emetteur = listeDonnees[0]
        nom, IDmode = emetteur
        
        # label
        self.ctrl_nom.SetLabel(nom)
        



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmode=1, IDemetteur=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
