#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB

import CTRL_Editeur_email



class Dialog(wx.Dialog):
    def __init__(self, parent, donnees=[], texte_xml=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent  
        self.donnees = donnees 
        self.texte_xml = texte_xml
        
        listeAdresses = []
        for dictTemp in self.donnees :
            listeAdresses.append(dictTemp["adresse"])
        
        # Navigation
        self.bouton_premier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Premier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_reculer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Reculer.png", wx.BITMAP_TYPE_ANY))
        self.ctrl_adresse = wx.ComboBox(self, -1, choices=listeAdresses, style=wx.CB_DROPDOWN )
        self.ctrl_adresse.SetEditable(False)
        if len(listeAdresses) > 0 :
            self.ctrl_adresse.Select(0)
        self.bouton_avancer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Avancer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_dernier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Dernier.png", wx.BITMAP_TYPE_ANY))
        
        # Aperçu
        self.ctrl_editeur = CTRL_Editeur_email.Editeur(self)
        self.ctrl_editeur.SetEditable(False) 
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonPremier, self.bouton_premier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReculer, self.bouton_reculer)
        self.Bind(wx.EVT_CHOICE, self.OnChoixAdresse, self.ctrl_adresse)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAvancer, self.bouton_avancer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDernier, self.bouton_dernier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        
        # Init contrôles
        self.bouton_fermer.SetFocus() 
        self.MAJ_apercu()

    def __set_properties(self):
        self.SetTitle(_(u"Aperçu de la fusion"))
        self.bouton_premier.SetToolTipString(_(u"Cliquez ici pour atteindre le premier"))
        self.bouton_reculer.SetMinSize((50, -1))
        self.bouton_reculer.SetToolTipString(_(u"Cliquez ici pour atteindre le précédent"))
        self.bouton_avancer.SetMinSize((50, -1))
        self.bouton_avancer.SetToolTipString(_(u"Cliquez ici pour atteindre le suivant"))
        self.bouton_dernier.SetToolTipString(_(u"Cliquez ici pour atteindre le dernier"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((600, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        # Navigation
        grid_sizer_navigation = wx.FlexGridSizer(rows=1, cols=7, vgap=0, hgap=0)
        grid_sizer_navigation.Add(self.bouton_premier, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_reculer, 0, 0, 0)
        grid_sizer_navigation.Add( (10, 5), 0, 0, 0)
        grid_sizer_navigation.Add(self.ctrl_adresse, 1, wx.EXPAND, 0)
        grid_sizer_navigation.Add( (10, 5), 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_avancer, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_dernier, 0, 0, 0)
        grid_sizer_navigation.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_navigation, 1, wx.ALL|wx.EXPAND, 10)
        
        # Ctrl Aperçu
        grid_sizer_base.Add(self.ctrl_editeur, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonPremier(self, event): 
        self.ctrl_adresse.Select(0)
        self.MAJ_apercu()

    def OnBoutonReculer(self, event): 
        index = self.ctrl_adresse.GetSelection()
        if index > 0 :
            self.Navigation(-1)

    def OnChoixAdresse(self, event): 
        self.MAJ_apercu()

    def OnBoutonAvancer(self, event): 
        index = self.ctrl_adresse.GetSelection()
        if index < len(self.donnees) :
            self.Navigation(+1)

    def OnBoutonDernier(self, event): 
        self.ctrl_adresse.Select(len(self.donnees)-1)
        self.MAJ_apercu()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("EditeurdEmails")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def Navigation(self, sens=1):
        index = self.ctrl_adresse.GetSelection()
        if index != -1 :
            self.ctrl_adresse.Select(index+sens)
            self.MAJ_apercu()
    
    def MAJ_apercu(self):
        index = self.ctrl_adresse.GetSelection()
        if index == -1 :
            return
        xml = self.texte_xml
        if xml == None :
            return
        # Remplacement des champs standards
        for motcle, valeur in CTRL_Editeur_email.GetChampsStandards().iteritems() :
            xml = xml.replace(motcle, valeur)
        # Remplacement des champs spécifiques
        dictDonnee = self.donnees[index]
        for motcle, valeur in dictDonnee["champs"].iteritems() :
            if valeur == None or valeur == "//None" :
                valeur = ""
            xml = xml.replace(motcle, valeur)
        # MAJ éditeur
        self.ctrl_editeur.SetXML(xml)
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()

    DB = GestionDB.DB()
    req = """SELECT categorie, nom, description, objet, texte_xml, IDadresse, defaut
    FROM modeles_emails
    WHERE IDmodele=1;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    categorie, nom, description, objet, texte_xml, IDadresse, defaut = listeDonnees[0]

    donnees = [
        {"adresse" : "monadresse1@gmail.com", "pieces" : [], "champs" : {} },
        {"adresse" : "monadresse2@gmail.com", "pieces" : [], "champs" : {} },
        {"adresse" : "monadresse3@gmail.com", "pieces" : [], "champs" : {} },
        ]
    
    dialog_1 = Dialog(None, donnees=donnees, texte_xml=texte_xml)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
