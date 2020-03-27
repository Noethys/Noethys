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
from Ol import OL_Categories_produits


class Dialog(wx.Dialog):
    def __init__(self, parent, IDcategorie=None, liste_categories=[], selection_multiple=False, selection_obligatoire=True):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.selection_multiple = selection_multiple
        self.selection_obligatoire = selection_obligatoire

        self.ctrl_categories = OL_Categories_produits.ListView(self, id=-1, selection_multiple=selection_multiple, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_categories.SetMinSize((750, 500))
        self.ctrl_recherche = OL_Categories_produits.CTRL_Outils(self, listview=self.ctrl_categories, afficherCocher=selection_multiple)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.ctrl_categories.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init contrôles
        self.ctrl_categories.MAJ()

        if IDcategorie == None and len(liste_categories) == 0 :
            wx.CallLater(10, self.ctrl_recherche.SetFocus)
        else :
            if self.selection_multiple == False :
                self.ctrl_categories.SetID(IDcategorie)
            else :
                self.ctrl_categories.SetListeCategories(liste_categories)
            wx.CallLater(10, self.ctrl_categories.SetFocus)

    def __set_properties(self):
        self.SetTitle(_(u"Sélection d'une catégorie de produits"))
        self.ctrl_categories.SetToolTip(wx.ToolTip(_(u"Double-cliquez sur une ligne pour la sélectionner rapidement")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)

        grid_sizer_base.Add(self.ctrl_categories, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_outils = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=30)
        grid_sizer_outils.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)
        grid_sizer_outils.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_outils, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
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
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen() 

    def OnItemActivated(self, event):
        self.OnBoutonOk()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Categoriesdeproduits")

    def OnBoutonOk(self, event=None):
        # Vérification des données saisies
        if self.selection_obligatoire == True :

            if self.selection_multiple == False:
                if self.ctrl_categories.GetID() == None :
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une catégorie !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            else :
                if len(self.ctrl_categories.GetListeCategories()) == 0 :
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une catégorie !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetIDcategorie(self):
        return self.ctrl_categories.GetID()

    def SetIDcategorie(self, IDcategorie=None):
        return self.ctrl_categories.SetID(IDcategorie)

    def GetListeCategories(self):
        return self.ctrl_categories.GetListeCategories()

    def SetListeCategories(self, liste_categories=[]):
        return self.ctrl_categories.SetListeCategories(liste_categories)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None, selection_multiple=True)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
