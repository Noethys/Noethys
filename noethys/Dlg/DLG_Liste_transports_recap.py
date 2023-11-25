#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime

import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Calendrier
from Ctrl import CTRL_Filtres_transports
from Ctrl import CTRL_Liste_transports




class Parametres(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
                
        # Calendrier
        self.staticbox_calendrier_staticbox = wx.StaticBox(self, -1, _(u"Calendrier"))
        self.ctrl_calendrier = CTRL_Calendrier.CTRL(self, afficheBoutonAnnuel=False, multiSelections=True)
        
        # Filtres
        self.staticbox_filtres_staticbox = wx.StaticBox(self, -1, _(u"Filtres"))
        self.ctrl_filtres = CTRL_Filtres_transports.CTRL(self)
        self.ctrl_filtres.SetMinSize((250, -1))
        

        self.__set_properties()
        self.__do_layout()

        self.ctrl_calendrier.Bind(CTRL_Calendrier.EVT_SELECT_DATES, self.OnDateSelected)
        
    def __set_properties(self):
        pass

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
                        
        # Calendrier
        staticbox_calendrier = wx.StaticBoxSizer(self.staticbox_calendrier_staticbox, wx.VERTICAL)
        staticbox_calendrier.Add(self.ctrl_calendrier, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_calendrier, 1, wx.RIGHT|wx.EXPAND, 5)

        # Filtres
        staticbox_filtres = wx.StaticBoxSizer(self.staticbox_filtres_staticbox, wx.VERTICAL)
        staticbox_filtres.Add(self.ctrl_filtres, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_filtres, 1, wx.RIGHT|wx.EXPAND, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
    
    def MAJFiltres(self):
        self.ctrl_filtres.MAJ(listeDates=self.GetListeDates())
        
    def OnDateSelected(self, event):
        self.MAJFiltres()
        self.parent.MAJ()
    
    def OnCocheFiltres(self):
        self.parent.MAJ()
        
    def GetListeDates(self):
        return self.ctrl_calendrier.GetSelections() 
    
    def GetDictFiltres(self):
        return self.ctrl_filtres.GetCoches() 
    
    


# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Commencez par sélectionner une ou plusieurs dates dans le calendrier (Sélections multiples : conservez la touche CTRL pour des dates non continues, SHIFT pour des dates continues et ALT pour des dates continues sans les week-ends). Vous pouvez ensuite imprimer la liste au format PDF.")
        titre = _(u"Liste récapitulative des transports")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Transport.png")
        
        self.ctrl_parametres = Parametres(self)
        self.ctrl_transports = CTRL_Liste_transports.CTRL(self)
        
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.MAJ() 

    def __set_properties(self):
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu PDF de la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((950, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # Liste + Barre de recherche
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_transports, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        # Commandes
        grid_sizer_droit = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OuvrirFiche(self, event):
        self.ctrl_transports.OuvrirFicheFamille(None)

    def Apercu(self, event):
        self.ctrl_transports.Imprimer(None)
    
    def MAJ(self):
        listeDates = self.ctrl_parametres.GetListeDates()
        dictFiltres = self.ctrl_parametres.GetDictFiltres()
        self.ctrl_transports.MAJ(listeDates=listeDates, dictFiltres=dictFiltres) 
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedestransports")


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
