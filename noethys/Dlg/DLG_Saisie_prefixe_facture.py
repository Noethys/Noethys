#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB


class Dialog(wx.Dialog):
    def __init__(self, parent, IDprefixe=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent   
        self.IDprefixe = IDprefixe

        self.label_nom = wx.StaticText(self, wx.ID_ANY, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, wx.ID_ANY, u"")
        
        self.label_prefixe = wx.StaticText(self, wx.ID_ANY, _(u"Préfixe :"))
        self.ctrl_prefixe = wx.TextCtrl(self, wx.ID_ANY, u"")

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init contrôles
        if self.IDprefixe != None :
            self.SetTitle(_(u"Modification d'un préfixe de facture"))
            self.Importation() 
        else :
            self.SetTitle(_(u"Saisie d'un préfixe de facture"))

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez le nom du préfixe (interne au logiciel)")))
        self.ctrl_prefixe.SetToolTip(wx.ToolTip(_(u"Saisissez le préfixe (en majuscules uniquement)")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(3, 2, 10, 10)

        grid_sizer_haut.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_nom, 0, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_prefixe, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_prefixe, 0, 0, 0)
                
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Prefixesdefactures")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        if self.Sauvegarde()  == False :
            return
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def Sauvegarde(self):
        """ Sauvegarde des données """
        nom = self.ctrl_nom.GetValue() 
        prefixe = self.ctrl_prefixe.GetValue()
        
        # Validation des données saisies
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        if prefixe == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un préfixe !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_prefixe.SetFocus()
            return False

        for caract in prefixe :
            if caract not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" :
                dlg = wx.MessageDialog(self, _(u"Le préfixe ne peut comporter que des chiffres et des lettres majuscules !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_prefixe.SetFocus()
                return False

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [ 
            ("nom", nom),
            ("prefixe", prefixe),
            ]
        if self.IDprefixe == None :
            self.IDprefixe = DB.ReqInsert("factures_prefixes", listeDonnees)
        else :
            DB.ReqMAJ("factures_prefixes", listeDonnees, "IDprefixe", self.IDprefixe)
        DB.Close()

    def Importation(self):
        """ Importation des valeurs """
        DB = GestionDB.DB()
        req = """SELECT nom, prefixe, COUNT(factures.IDprefixe)
        FROM factures_prefixes
        LEFT JOIN factures ON factures.IDprefixe = factures_prefixes.IDprefixe
        WHERE factures_prefixes.IDprefixe=%d
        GROUP BY factures_prefixes.IDprefixe;""" % self.IDprefixe
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        nom, prefixe, nbre_factures = listeTemp[0]
        if nom == None : nom = ""
        if prefixe == None : prefixe = ""
        
        self.ctrl_nom.SetValue(nom)
        self.ctrl_prefixe.SetValue(prefixe)
        if nbre_factures > 0 :
            self.ctrl_prefixe.Enable(False)

    def GetIDprefixe(self):
        return self.IDprefixe



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
