#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import six
import GestionDB
from Ctrl import CTRL_Editeur_email




class Dialog(wx.Dialog):
    def __init__(self, parent, IDelement=None, categorie=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        self.IDelement = IDelement
        self.categorie = categorie

        # Editeur
        self.ctrl_editeur = CTRL_Editeur_email.CTRL(self)

        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()


        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDelement != None or self.categorie != None :
            self.SetTitle(_(u"Modification d'un texte HTML"))
            self.Importation()
        else:
            self.SetTitle(_(u"Saisie d'un texte HTML"))
        

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((700, 580))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=10)

        # Editeur
        grid_sizer_base.Add(self.ctrl_editeur, 0, wx.EXPAND | wx.ALL, 10)

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
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def GetHTML(self):
        return self.ctrl_editeur.GetHTML_base64()

    def OnBoutonOk(self, event):
        # Récupération du texte
        texteStr = self.ctrl_editeur.GetValue()
        texteXML = self.ctrl_editeur.GetXML()
        texteHTML = self.ctrl_editeur.GetHTML_base64()
        if len(texteStr) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_editeur.SetFocus()
            return

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
                ("categorie", self.categorie),
                ("texte_xml", texteXML),
                ("texte_html", texteHTML),
                ]
        if self.IDelement == None :
            self.IDelement = DB.ReqInsert("portail_elements", listeDonnees)
        else:
            DB.ReqMAJ("portail_elements", listeDonnees, "IDelement", self.IDelement)
        DB.Close()

        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDelement(self):
        return self.IDelement

    def Importation(self):
        if self.IDelement != None :
            condition = "IDelement=%d" % self.IDelement
        if self.categorie != None :
            condition = "categorie='%s'" % self.categorie
        DB = GestionDB.DB()
        req = """SELECT IDelement, categorie, texte_xml
        FROM portail_elements
        WHERE %s;""" % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        self.IDelement, self.categorie, texte_xml = listeDonnees[0]
        if texte_xml != None :
            if six.PY3 and isinstance(texte_xml, str):
                texte_xml = texte_xml.encode("utf8")
            self.ctrl_editeur.SetXML(texte_xml)





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDtexte=None, code=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
