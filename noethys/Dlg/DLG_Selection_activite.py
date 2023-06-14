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
from Ol import OL_Inscriptions_activite
from Utils import UTILS_Interface

import GestionDB




class CTRL_Activite(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.BORDER_THEME|wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = None
        couleur_fond = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.SetBackgroundColour(couleur_fond)

        self.ctrl_activite = wx.StaticText(self, -1, "")
        self.ctrl_activite.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_activite, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER, 0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()

    def MAJ(self, IDactivite=None, nomActivite=""):
        self.IDactivite = IDactivite
        self.ctrl_activite.SetLabel(nomActivite)
        self.Layout()

    def GetID(self):
        return self.IDactivite

    def GetNomActivite(self):
        return self.ctrl_activite.GetLabel()



class Panel_Activite(wx.Panel):
    def __init__(self, parent, callback=None):
        wx.Panel.__init__(self, parent, id=-1, name="CTRL_Activite", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.callback = callback

        self.ctrl_activite = CTRL_Activite(self)
        self.bouton_activites = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_activite.SetMinSize((-1, self.bouton_activites.GetSize()[1]))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonActivite, self.bouton_activites)

    def __set_properties(self):
        self.ctrl_activite.SetToolTip(wx.ToolTip(_(u"Activité sélectionnée")))
        self.bouton_activites.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner une activité")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_activite, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_activites, 1, wx.EXPAND, 0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnBoutonActivite(self, event):
        dlg = Dialog(self)
        dlg.SetIDactivite(self.ctrl_activite.GetID())
        if dlg.ShowModal() == wx.ID_OK:
            IDactivite = dlg.GetIDactivite()
            nomActivite = dlg.GetNomActivite()
            self.ctrl_activite.MAJ(IDactivite, nomActivite)
            if self.callback != None :
                self.callback()
        dlg.Destroy()

    def GetID(self):
        return self.ctrl_activite.GetID()

    def GetNomActivite(self):
        return self.ctrl_activite.GetNomActivite()


# ----------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent     

        self.ctrl_activites = OL_Inscriptions_activite.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_activites.SetMinSize((750, 500))
        self.ctrl_recherche = OL_Inscriptions_activite.CTRL_Outils(self, listview=self.ctrl_activites)

        self.ctrl_activites_valides = wx.CheckBox(self, -1, _(u"Afficher uniquement les activités ouvertes"))
        self.ctrl_activites_valides.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
        self.ctrl_activites_valides.SetValue(True)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        # self.ctrl_activites.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectionActivite)
        # self.ctrl_activites.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnSelectionActivite)
        self.ctrl_activites.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHECKBOX, self.OnCocheActivitesValides, self.ctrl_activites_valides)

        # Init contrôles
        self.ctrl_activites.MAJ()

        wx.CallLater(10, self.ctrl_recherche.SetFocus)

    def __set_properties(self):
        self.SetTitle(_(u"Sélection d'une activité"))
        self.ctrl_activites.SetToolTip(wx.ToolTip(_(u"Double-cliquez sur une ligne pour la sélectionner rapidement")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)

        grid_sizer_activite = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_activites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_outils = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=30)
        grid_sizer_outils.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)
        grid_sizer_outils.Add(self.ctrl_activites_valides, 0, wx.ALIGN_CENTER_VERTICAL, 0)
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

    def OnCocheActivitesValides(self, event):
        self.ctrl_activites.activites_recentes = self.ctrl_activites_valides.GetValue()
        self.ctrl_activites.MAJ()

    def OnItemActivated(self, event):
        self.OnBoutonOk()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Activits1")

    def OnBoutonOk(self, event=None):
        # Vérification des données saisies
        if self.ctrl_activites.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def SetIDactivite(self, IDactivite=None):
        self.ctrl_activites.SetID(IDactivite)
        self.ctrl_activites.SetFocus()

    def GetIDactivite(self):
        return self.ctrl_activites.GetID()

    def GetNomActivite(self):
        return self.ctrl_activites.GetNom()




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
