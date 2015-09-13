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
import OL_Scolarite



class Panel(wx.Panel):
    def __init__(self, parent, IDindividu=None, dictFamillesRattachees={}):
        wx.Panel.__init__(self, parent, id=-1, name="panel_scolarite", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees
        
        # scolarite
        self.staticbox_scolarite = wx.StaticBox(self, -1, _(u"Scolarité"))
        self.ctrl_scolarite = OL_Scolarite.ListView(self, IDindividu=IDindividu, id=-1, name="OL_scolarite", style=wx.LC_HRULES|wx.LC_VRULES|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl_scolarite.SetMinSize((20, 20)) 
        self.ctrl_recherche = OL_Scolarite.CTRL_Outils(self, listview=self.ctrl_scolarite)
        self.ctrl_recherche.SetBackgroundColour((255, 255, 255))

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        
        # Propriétés
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour inscrire l'individu dans une classe"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier l'inscription sélectionnée"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer l'inscription sélectionnée"))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        
        # scolarite
        staticbox_scolarite = wx.StaticBoxSizer(self.staticbox_scolarite, wx.VERTICAL)
        grid_sizer_scolarite = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_scolarite.Add(self.ctrl_scolarite, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, wx.ALL, 0)
        grid_sizer_scolarite.Add(grid_sizer_boutons, 1, wx.ALL, 0)

        grid_sizer_scolarite.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)

        grid_sizer_scolarite.AddGrowableCol(0)
        grid_sizer_scolarite.AddGrowableRow(0)
        staticbox_scolarite.Add(grid_sizer_scolarite, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticbox_scolarite, 1, wx.EXPAND|wx.ALL, 5)
                
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
    
    def OnBoutonAjouter(self, event):
        self.ctrl_scolarite.Ajouter(None)

    def OnBoutonModifier(self, event):
        self.ctrl_scolarite.Modifier(None)

    def OnBoutonSupprimer(self, event):
        self.ctrl_scolarite.Supprimer(None)


##    def Set_Header(self, nomLigne, texte):
##        try :
##            self.ficheIndividu = self.Parent.GetParent()
##            if self.ficheIndividu.GetName() != "fiche_liens" :
##                self.ficheIndividu = None
##        except : 
##            self.ficheIndividu = None
##        if self.ficheIndividu != None :
##            self.ficheIndividu.Set_Header(nomLigne, texte)
    
    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        self.IDindividu = self.GetGrandParent().IDindividu
        if self.IDindividu == None :
            print "pas de IDindividu !"
            return
        self.ctrl_scolarite.MAJ() 
        
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
        self.IDindividu = 3
        self.ctrl = Panel(panel, IDindividu=self.IDindividu)
##        self.ctrl.MAJ() 
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