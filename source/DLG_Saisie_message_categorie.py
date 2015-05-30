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

import GestionDB
import CTRL_Saisie_date


class Dialog(wx.Dialog):
    def __init__(self, parent, IDcategorie=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent      
        self.IDcategorie = IDcategorie
        
        # Nom
        self.staticbox_nom_staticbox = wx.StaticBox(self, -1, _(u"Nom"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options par défaut"))
        
        self.ctrl_afficher_accueil = wx.CheckBox(self, -1, _(u"Afficher sur la page d'accueil"))
        self.ctrl_afficher_liste = wx.CheckBox(self, -1, _(u"Afficher sur la liste des consommations"))
        
        self.label_priorite = wx.StaticText(self, -1, _(u"Priorité :"))
        self.ctrl_priorite = wx.Choice(self, -1, choices=[_(u"Normale"), _(u"Haute")])
        self.ctrl_priorite.SetSelection(0)
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDcategorie == None :
            self.SetTitle(_(u"Saisie d'une catégorie de message"))
        else:
            self.Importation()
            self.SetTitle(_(u"Modification d'une catégorie de message"))

    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez un nom pour cette catégorie"))
        self.ctrl_afficher_accueil.SetToolTipString(_(u"Cochez cette case pour afficher ce message sur la page d'accueil"))
        self.ctrl_afficher_liste.SetToolTipString(_(u"Cochez cette case pour afficher ce message sur la liste des consommations"))
        self.ctrl_priorite.SetToolTipString(_(u"Sélectionnez ici la priorité du message"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((460, 220))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
                
        # Texte
        staticbox_nom = wx.StaticBoxSizer(self.staticbox_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        staticbox_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=2, cols=3, vgap=5, hgap=5)
        grid_sizer_options.Add(self.ctrl_afficher_accueil, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.label_priorite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_priorite, 0, 0, 0)
        grid_sizer_options.Add(self.ctrl_afficher_liste, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.AddGrowableCol(0)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        self.Layout()
        self.CenterOnScreen() 
    
    def Importation(self):
        """ Importation des donnees de la base """
        DB = GestionDB.DB()
        req = """SELECT nom, priorite, afficher_accueil, afficher_liste
        FROM messages_categories 
        WHERE IDcategorie=%d;""" % self.IDcategorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        
        nom, priorite, afficher_accueil, afficher_liste = listeDonnees[0]
        
        self.ctrl_nom.SetValue(nom)
        if priorite == "HAUTE" : self.ctrl_priorite.Select(1)
        if afficher_accueil == 1 : self.ctrl_afficher_accueil.SetValue(True)
        if afficher_liste == 1 : self.ctrl_afficher_liste.SetValue(True)
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Catgoriesdemessages")

    def OnBoutonOk(self, event): 
        # Vérification des données
        if len(self.ctrl_nom.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour cette catégorie !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        
        # Sauvegarde
        self.Sauvegarde()
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDcategorie(self):
        return self.IDcategorie

    def Sauvegarde(self):
        """ Sauvegarde """
        # Récupération des données
        nom = self.ctrl_nom.GetValue()
        if self.ctrl_priorite.GetSelection() == 1 :
            priorite = "HAUTE"
        else:
            priorite = "NORMALE"
        afficher_accueil = int(self.ctrl_afficher_accueil.GetValue())
        afficher_liste = int(self.ctrl_afficher_liste.GetValue())
                
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("nom", nom),
                ("priorite", priorite),
                ("afficher_accueil", afficher_accueil),
                ("afficher_liste", afficher_liste),
            ]
        if self.IDcategorie == None :
            self.IDcategorie = DB.ReqInsert("messages_categories", listeDonnees)
        else:
            DB.ReqMAJ("messages_categories", listeDonnees, "IDcategorie", self.IDcategorie)
        DB.Close()
        



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDcategorie=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
