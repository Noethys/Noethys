#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ol import OL_Prestations 
import wx.lib.agw.hyperlink as Hyperlink
from Utils import UTILS_Utilisateurs

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


class Hyperlien_regroupement(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", listeChoix=[], indexChoixDefaut=None, size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.listeChoix = listeChoix
        self.indexChoixDefaut = indexChoixDefaut

        if self.GetGrandParent().GetName() == "notebook" :
            self.SetBackgroundColour(self.GetGrandParent().GetThemeBackgroundColour())

        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def SetListeChoix(self, listeChoix=[]):
        self.listeChoix = listeChoix
        
    def OnLeftLink(self, event):
        dlg = wx.SingleChoiceDialog(self, _(u"Choisissez un item dans la liste :"), _(u"Choix"), self.listeChoix, wx.CHOICEDLG_STYLE)
        if self.indexChoixDefaut != None and self.indexChoixDefaut < len(self.listeChoix) :
            dlg.SetSelection(self.indexChoixDefaut)
        if dlg.ShowModal() == wx.ID_OK:
            indexChoix = dlg.GetSelection()
            # Modification du label de l'hyperlien
            self.SetLabel(self.listeChoix[indexChoix])
            self.indexChoixDefaut = indexChoix
            # MAJ du listView
            self.parent.ctrl_prestations.SetColonneTri(indexChoix+1)
##            self.parent.MAJtotal()
            self.parent.grid_sizer_options.Layout() 
            self.parent.Refresh() 
        dlg.Destroy()
        self.UpdateLink()

# -----------------------------------------------------------------------------------------------------------------------


class Hyperlien_periodes(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent

        if self.GetGrandParent().GetName() == "notebook" :
            self.SetBackgroundColour(self.GetGrandParent().GetThemeBackgroundColour())

        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        
    def OnLeftLink(self, event):
        from Dlg import DLG_Choix_periodes
        dlg = DLG_Choix_periodes.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            listePeriodes = dlg.GetListePeriodes()
            # Label
            if listePeriodes == None :
                self.SetLabel(_(u"Toutes les périodes"))
            else:
                self.SetLabel(_(u"Sélection"))
            # MAJ
            self.parent.ctrl_prestations.SetListePeriodes(listePeriodes)
##            self.parent.MAJtotal()
            self.parent.grid_sizer_options.Layout() 
            self.parent.Refresh() 
        dlg.Destroy()
        self.UpdateLink()
        
        

# -----------------------------------------------------------------------------------------------------------------------



class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", listeChoix=[], indexChoixDefaut=None, champFiltre="", labelDefaut="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.listeChoix = listeChoix
        self.indexChoixDefaut = indexChoixDefaut
        self.champFiltre = champFiltre
        self.labelDefaut = labelDefaut

        if self.GetGrandParent().GetName() == "notebook" :
            self.SetBackgroundColour(self.GetGrandParent().GetThemeBackgroundColour())

        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def SetListeChoix(self, listeChoix=[]):
        self.listeChoix = listeChoix
        
    def OnLeftLink(self, event):
        self.listeChoix.sort()
        listeItems = [self.labelDefaut,]
        for label, ID in self.listeChoix :
            listeItems.append(label)
        dlg = wx.SingleChoiceDialog(self, _(u"Choisissez un filtre dans la liste suivante :"), _(u"Filtrer la liste"), listeItems, wx.CHOICEDLG_STYLE)
        if self.indexChoixDefaut != None and self.indexChoixDefaut < len(self.listeChoix) :
            dlg.SetSelection(self.indexChoixDefaut)
        if dlg.ShowModal() == wx.ID_OK:
            indexChoix = dlg.GetSelection() - 1
            # Modification du label de l'hyperlien
            if indexChoix == -1 :
                self.SetLabel(self.labelDefaut)
                self.indexChoixDefaut = None
                ID = None
            else:
                self.SetLabel(self.listeChoix[indexChoix][0])
                self.indexChoixDefaut = self.listeChoix[indexChoix][1]
                ID = self.listeChoix[indexChoix][1]
            # MAJ
            self.parent.ctrl_prestations.SetFiltre(self.champFiltre, ID)
##            self.parent.MAJtotal()
            self.parent.grid_sizer_options.Layout() 
            self.parent.Refresh() 
        dlg.Destroy()
        self.UpdateLink()
        

# -----------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_prestations", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.staticbox_prestations = wx.StaticBox(self, -1, _(u"Prestations"))
        
        # OL Prestations
        self.listviewAvecFooter = OL_Prestations.ListviewAvecFooter(self, kwargs={"IDfamille" : IDfamille}) 
        self.ctrl_prestations = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Prestations.CTRL_Outils(self, listview=self.ctrl_prestations, afficherCocher=True)
        self.ctrl_recherche.SetBackgroundColour((255, 255, 255))

        # Commandes boutons
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modele = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Magique.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_prestations.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_prestations.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_prestations.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_prestations.Appliquer_modele, self.bouton_modele)

        # Propriétés
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une prestation")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la prestation sélectionnée")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la prestation sélectionnée")))
        self.bouton_modele.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une prestation à partir d'un modèle de prestation")))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        staticbox_prestations = wx.StaticBoxSizer(self.staticbox_prestations, wx.VERTICAL)
        grid_sizer_prestations = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_prestations.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, wx.ALL, 0)
        grid_sizer_boutons.Add( (10, 10), 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modele, 0, wx.ALL, 0)
        grid_sizer_prestations.Add(grid_sizer_boutons, 1, wx.ALL, 0)
        
        grid_sizer_prestations.Add(self.ctrl_recherche, 0, wx.EXPAND|wx.ALL, 0)

        grid_sizer_prestations.AddGrowableCol(0)
        grid_sizer_prestations.AddGrowableRow(0)
        staticbox_prestations.Add(grid_sizer_prestations, 1, wx.EXPAND|wx.ALL, 5)
        
        grid_sizer_base.Add(staticbox_prestations, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)

    def IsLectureAutorisee(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_prestations", "consulter", afficheMessage=False) == False : 
            return False
        return True

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        self.ctrl_prestations.MAJ() 
        self.Refresh()
        
    def MAJtotal(self):
        self.ctrl_total.SetLabel(_(u"Total : %.2f %s") % (self.ctrl_prestations.GetTotal(), SYMBOLE))
            
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
        self.ctrl= Panel(panel, IDfamille=2)
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