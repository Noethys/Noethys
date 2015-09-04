#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import OL_Pays

try: import psyco; psyco.full()
except: pass

    
class Dialog_pays(wx.Dialog):
    def __init__(self, parent, typeSelection="pays"):
        """ typeSelection = "pays" | "nationalite" """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.typeSelection = typeSelection
        if self.typeSelection == "pays" :
            intro = _(u"Vous pouvez s�lectionner ici un pays en double-cliquant sur sa ligne. La barre de recherche peut vous permettre de retrouver rapidement un �l�ment de la liste.")
            titre = _(u"S�lection d'un pays")
        else:
            intro = _(u"Vous pouvez s�lectionner ici une nationalit� en double-cliquant sur sa ligne. La barre de recherche peut vous permettre de retrouver rapidement un �l�ment de la liste.")
            titre = _(u"S�lection d'une nationalit�")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Monde.png")
        self.ctrl_pays = OL_Pays.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_pays.MAJ()
        self.ctrl_barreRecherche = OL_Pays.CTRL_Outils(self, listview=self.ctrl_pays)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        if self.typeSelection == "pays" :
            self.SetTitle(_(u"S�lection d'un pays"))
        else:
            self.SetTitle(_(u"S�lection d'une nationalit�"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider et fermer"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))
        self.SetMinSize((500, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_pays, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_barreRecherche, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
    
    def GetIDpays(self):
        return self.ctrl_pays.Selection()[0].IDpays
        
    def OnBoutonOk(self, event):
        selection = self.ctrl_pays.Selection()
        if len(selection) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun �l�ment dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog_pays(None, typeSelection="pays")
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
