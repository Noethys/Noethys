#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image

import OL_Groupes
import GestionDB

try: import psyco; psyco.full()
except: pass

class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, nouvelleActivite=False):
        wx.Panel.__init__(self, parent, id=-1, name="panel_groupes", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        
        self.staticbox_groupes_staticbox = wx.StaticBox(self, -1, _(u"Groupes"))
        
        self.ctrl_groupes = OL_Groupes.ListView(self, IDactivite=self.IDactivite, id=-1, name="OL_groupes", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_groupes.MAJ() 

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_ANY))

        self.label_info = wx.StaticText(self, -1, _(u"Vous devez obligatoirement saisir un groupe. Si votre activité n'en possède pas, créez juste un groupe intitulé 'Groupe unique'."))
        self.label_info.SetFont(wx.Font(6, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.Monter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.Descendre, self.bouton_descendre)

        # Importation
        if self.IDactivite != None :
            self.Importation() 
        
        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un groupe"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier le groupe selectionné dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le groupe selectionné dans la liste"))
        self.bouton_monter.SetToolTipString(_(u"Cliquez ici pour monter le groupe sélectionné dans la liste"))
        self.bouton_descendre.SetToolTipString(_(u"Cliquez ici pour descendre le groupe sélectionné dans la liste"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=1, vgap=10, hgap=10)
        staticbox_groupes = wx.StaticBoxSizer(self.staticbox_groupes_staticbox, wx.VERTICAL)
        
        grid_sizer_groupes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_groupes.Add(self.ctrl_groupes, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_groupes.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        
        grid_sizer_groupes.AddGrowableRow(0)
        grid_sizer_groupes.AddGrowableCol(0)
                
        staticbox_groupes.Add(grid_sizer_groupes, 1, wx.ALL|wx.EXPAND, 5)
        
        staticbox_groupes.Add(self.label_info, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        grid_sizer_base.Add(staticbox_groupes, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnRadio(self, event): 
        if self.radio_sans.GetValue() == 1 :
            self.ctrl_groupes.Enable(False)
            self.bouton_ajouter.Enable(False)
            self.bouton_modifier.Enable(False)
            self.bouton_supprimer.Enable(False)
        if self.radio_avec.GetValue() == 1 :
            self.ctrl_groupes.Enable(True)
            self.bouton_ajouter.Enable(True)
            self.bouton_modifier.Enable(True)
            self.bouton_supprimer.Enable(True)

    def OnBoutonAjouter(self, event): 
        self.ctrl_groupes.Ajouter(None)

    def OnBoutonModifier(self, event): 
        self.ctrl_groupes.Modifier(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_groupes.Supprimer(None)

    def Monter(self, event):
        self.ctrl_groupes.Monter(None)
        
    def Descendre(self, event):
        self.ctrl_groupes.Descendre(None)

    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT IDgroupe, nom 
        FROM groupes WHERE IDactivite=%d;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()

    def Validation(self):
        nbreGroupes = len(self.ctrl_groupes.donnees)
        if nbreGroupes == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez créer au moins un groupe !\n\nSi vous n'avez aucun groupe, créez juste un groupe intitulé par exemple 'Groupe unique'."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        # Validation
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
        self.ctrl= Panel(panel, IDactivite=37)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()