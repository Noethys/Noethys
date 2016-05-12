#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import FonctionsPerso
import webbrowser


class DLG_Financement(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.CAPTION)
        self.parent = parent
        self.image_fond = wx.Bitmap(Chemins.GetStaticPath(u"Images/Special/Financement.png"), wx.BITMAP_TYPE_ANY)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"En savoir plus"), cheminImage="Images/32x32/Aide.png")
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Bon de commande"), cheminImage="Images/32x32/Imprimante.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
        
        # Propriétés
        self.SetTitle(_(u"Programme de financement de Noethys"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour en savoir plus sur le programme de financement"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer le bon de commande et les conditions générales de vente"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        
        # Calcule les espaces du sizer
        largeurImage, hauteurImage = self.image_fond.GetSize() 
        hauteurBouton = self.bouton_imprimer.GetSize()[1]
        hauteurEspaceBas = 40
        hauteurEspaceHaut = hauteurImage - hauteurBouton - hauteurEspaceBas
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        grid_sizer_base.Add( (largeurImage, hauteurEspaceHaut), 0, 0, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add( (10, 10), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.RIGHT|wx.EXPAND, 30)
        
        grid_sizer_base.Add( (largeurImage, hauteurEspaceBas), 0, 0, 0)

        self.SetSizer(grid_sizer_base)
        
        # Calcule taille de la fenêtre
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        
        # Init
        self.bouton_fermer.SetFocus() 

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.image_fond, 0, 0)

    def OnBoutonFermer(self, event):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBoutonAide(self, event):
        url = "http://www.noethys.com/index.php/presentation/2013-09-08-15-48-17/programme-de-financement"
        webbrowser.open(url)

    def OnBoutonImprimer(self, event):
        try :
            FonctionsPerso.LanceFichierExterne(Chemins.GetStaticPath("Images/Special/Bon_commande.pdf"))
        except :
            dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas ouvrir le PDF !\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()






    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = DLG_Financement(None)
    dlg.ShowModal() 
    dlg.Destroy()
    app.MainLoop()
