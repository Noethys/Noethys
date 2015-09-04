#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import OL_Quotients 
import GestionDB
import UTILS_Utilisateurs


class Panel(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_quotients", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.staticbox_quotients = wx.StaticBox(self, -1, _(u"Quotients familiaux"))
        
        # OL Quotients
        self.ctrl_quotients = OL_Quotients.ListView(self, id=-1, IDfamille=self.IDfamille, name="OL_quotients", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_recherche = OL_Quotients.CTRL_Outils(self, listview=self.ctrl_quotients)
        self.ctrl_recherche.SetBackgroundColour((255, 255, 255))

        # Commandes boutons
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        
        # Propriétés
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour saisir un quotient familial"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le quotient familial sélectionné"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le quotient familial sélectionné"))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        staticbox_quotients = wx.StaticBoxSizer(self.staticbox_quotients, wx.VERTICAL)
        grid_sizer_quotients = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_quotients.Add(self.ctrl_quotients, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, wx.ALL, 0)
        grid_sizer_quotients.Add(grid_sizer_boutons, 1, wx.ALL, 0)

        grid_sizer_quotients.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)

        grid_sizer_quotients.AddGrowableCol(0)
        grid_sizer_quotients.AddGrowableRow(0)
        staticbox_quotients.Add(grid_sizer_quotients, 1, wx.EXPAND|wx.ALL, 5)
        
        grid_sizer_base.Add(staticbox_quotients, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
    
    def OnBoutonAjouter(self, event):
        self.ctrl_quotients.Ajouter(None)
 
    def OnBoutonModifier(self, event):
        self.ctrl_quotients.Modifier(None)

    def OnBoutonSupprimer(self, event):
        self.ctrl_quotients.Supprimer(None)

    def IsLectureAutorisee(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_quotients", "consulter", afficheMessage=False) == False : 
            return False
        return True

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        self.ctrl_quotients.MAJ() 
                
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        return True
    
    def Sauvegarde(self):
        pass
        
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDfamille=3)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()