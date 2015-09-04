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
import datetime
import FonctionsPerso
import sys
import operator

import CTRL_Bandeau
import CTRL_Refus

try: import psyco; psyco.full()
except: pass


class Dialog(wx.Dialog):
    def __init__(self, parent, dictDonnees={}, dictEtatPlaces={}, dictUnitesRemplissage={}):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici consulter la liste des individus qui avaient r�serv� des places sur liste d'attente et qui apr�s lib�ration de places, les avaient finalement refus�. Cette liste vous permet donc de d�terminer avec pr�cision le nombre de places qui auraient �t� n�cessaires afin d'accueillir tout le monde...")
        titre = _(u"Liste des places refus�es")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Places_refus.png")
        
        self.ctrl_refus = CTRL_Refus.CTRL(self, dictDonnees=dictDonnees, dictEtatPlaces=dictEtatPlaces, dictUnitesRemplissage=dictUnitesRemplissage)
        
        self.bouton_ouvrir_fiche = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OuvrirFiche, self.bouton_ouvrir_fiche)
        self.Bind(wx.EVT_BUTTON, self.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.SetTitle(_(u"Liste des places refus�es"))
        self.bouton_ouvrir_fiche.SetToolTipString(_(u"Cliquez ici pour ouvrir la fiche famille de l'individu s�lectionn� dans la liste"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer cette liste (PDF)"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((780, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_droit = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_refus, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        grid_sizer_droit.Add(self.bouton_ouvrir_fiche, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (10, 10), 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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
        self.ctrl_refus.OuvrirFicheFamille(None)

    def Imprimer(self, event):
        self.ctrl_refus.Imprimer(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Listedesplacesrefuses")


# --------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    
    dictDonnees = {
        "page" : 0,
        "listeSelections" : [2, 3, 5],
        "annee" : 2009,
        "dateDebut" : None,
        "dateFin" : None,
        "listePeriodes" : [ (datetime.date(2010, 1, 1), datetime.date(2010, 12, 31)), ],
        "listeActivites" : [1,],
        }
        
    dialog_1 = Dialog(None, dictDonnees=dictDonnees)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
