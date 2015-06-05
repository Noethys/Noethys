#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Bandeau
import CTRL_Graph_tresorerie
import CTRL_Saisie_compte
import CTRL_Saisie_date




class Dialog(wx.Dialog):
    def __init__(self, parent, IDcompte_bancaire=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = _(u"Sélectionnez un compte et une période pour afficher le suivi de la trésorerie correspondante.")
        titre = _(u"Trésorerie")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Tresorerie.png")
        
        # Options
        self.label_compte = wx.StaticText(self, wx.ID_ANY, _(u"Compte :"))
        self.ctrl_compte = CTRL_Saisie_compte.CTRL(self, IDcompte_bancaire=IDcompte_bancaire)
        
        self.label_periode = wx.StaticText(self, wx.ID_ANY, _(u"Période :"))
        self.ctrl_periode = CTRL_Graph_tresorerie.CTRL_Affichage(self)
        
        self.label_date_debut = wx.StaticText(self, wx.ID_ANY, u"du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, wx.ID_ANY, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.bouton_actualiser = wx.Button(self, -1, _(u"Actualiser"))

        # Graphe
        self.ctrl_graphique = CTRL_Graph_tresorerie.CTRL(self, style=wx.SUNKEN_BORDER)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_CHOICE, self.Actualiser, self.ctrl_compte)
        self.Bind(wx.EVT_CHOICE, self.OnChoix, self.ctrl_periode)
        self.Bind(wx.EVT_BUTTON, self.Actualiser, self.bouton_actualiser)
        
        # Binds
        wx.CallLater(1, self.OnChoix)
        

    def __set_properties(self):
        self.bouton_actualiser.SetToolTipString(_(u"Cliquez ici pour actualiser l'affichage"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((850, 690))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=9, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_compte, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_compte, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_periode, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_periode, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_date_debut, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_date_fin, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.bouton_actualiser, 0, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableCol(1)

        grid_sizer_base.Add(grid_sizer_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_base.Add(self.ctrl_graphique, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
                
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnChoix(self, event=None):
        code = self.ctrl_periode.GetCode() 
        if code == "personnalise" :
            etat = True
        else :
            etat = False
        self.label_date_debut.Enable(etat)
        self.ctrl_date_debut.Enable(etat)
        self.label_date_fin.Enable(etat)
        self.ctrl_date_fin.Enable(etat)
        self.bouton_actualiser.Enable(etat)
        self.Actualiser()
        
    def Actualiser(self, event=None):
        code = self.ctrl_periode.GetCode() 
        date_debut = self.ctrl_date_debut.GetDate() 
        date_fin = self.ctrl_date_fin.GetDate() 
        self.ctrl_graphique.SetPeriode(code, date_debut, date_fin)
        IDcompte = self.ctrl_compte.GetID() 
        self.ctrl_graphique.SetCompte(IDcompte)
        self.ctrl_graphique.MAJ() 
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDcompte_bancaire=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
