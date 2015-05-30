#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.html as html
import datetime
import GestionDB

import CTRL_Badgeage_conditions
import CTRL_Badgeage_action



class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        self.SetTexte(texte)

    def SetTexte(self, texte=u""):
        self.SetPage(texte)
        couleurFond = wx.SystemSettings.GetColour(30)
        self.SetBackgroundColour(couleurFond)


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDaction = None
        
        # Conditions
        self.box_conditions_staticbox = wx.StaticBox(self, -1, _(u"Conditions"))
        self.ctrl_conditions = CTRL_Badgeage_conditions.Panel(self)
        
        # Mémo des mots-clés
        self.box_motscles_staticbox = wx.StaticBox(self, -1, _(u"Mots-clés disponibles pour les messages"))
        texte = u"""
        <FONT SIZE=-2>
        {NOM} -> Nom, {PRENOM} -> Prénom, 
        <BR>{DATE} -> Date, {HEURE} -> Heure, 
        <BR>{FEMININ} -> Ajoute un 'e' si l'individu est de sexe féminin.
        </FONT>"""
        self.ctrl_motscles = MyHtml(self, texte=texte, hauteur=50)
        
        # Action
        self.box_action_staticbox = wx.StaticBox(self, -1, _(u"Action"))
        self.ctrl_action = CTRL_Badgeage_action.Panel(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une action"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.ctrl_conditions.SetMinSize((400, -1))
        self.SetMinSize((-1, 580))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Conditions
        box_conditions = wx.StaticBoxSizer(self.box_conditions_staticbox, wx.VERTICAL)
        box_conditions.Add(self.ctrl_conditions, 1, wx.EXPAND|wx.ALL, 10)
        
        # Mots-clés
        box_motscles = wx.StaticBoxSizer(self.box_motscles_staticbox, wx.VERTICAL)
        box_motscles.Add(self.ctrl_motscles, 1, wx.EXPAND|wx.ALL, 10)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box_conditions, 1, wx.EXPAND, 0)
        sizer.Add(box_motscles, 0, wx.EXPAND|wx.TOP, 10)
        grid_sizer_contenu.Add(sizer, 1, wx.EXPAND, 0)
        
        # Action
        box_action = wx.StaticBoxSizer(self.box_action_staticbox, wx.VERTICAL)
        box_action.Add(self.ctrl_action, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_contenu.Add(box_action, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
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
        import UTILS_Aide
        UTILS_Aide.Aide("Paramtreruneaction")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        # Validation des données
        if self.ctrl_conditions.Validation() == False :
            return False
        
        if self.ctrl_action.Validation() == False :
            return False
        
        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetDonnees(self):
        dictDonnees = {}
        dictDonnees["IDaction"] = self.IDaction
        dictDonnees.update(self.ctrl_conditions.GetDonnees())
        dictDonnees.update(self.ctrl_action.GetDonnees())
        return dictDonnees
    
    def SetDonnees(self, dictDonnees={}):
        # IDaction
        self.IDaction = dictDonnees["IDaction"]
        # Conditions
        dictTemp = {}
        for code, valeur in dictDonnees.iteritems() :
            if code.startswith("condition_") :
                dictTemp[code[10:]] = valeur
        self.ctrl_conditions.SetDonnees(dictTemp)
        # Action
        dictTemp = {}
        for code, valeur in dictDonnees.iteritems() :
            if code.startswith("action_") :
                dictTemp[code[7:]] = valeur
        self.ctrl_action.SetDonnees(dictDonnees["action"], dictTemp)
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()