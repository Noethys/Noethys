#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import time
import sys
from Ctrl import CTRL_Informations
from Ol import OL_Etat_compte

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal

import GestionDB
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Linux


class CTRL_Solde(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_solde", style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Solde du compte
        self.ctrl_solde = wx.StaticText(self, -1, u"0.00 %s" % SYMBOLE)
        font = wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.ctrl_solde.SetFont(font)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_solde, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL|wx.ALL, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        
        self.SetToolTip(wx.ToolTip(_(u"Solde final du compte")))
        self.ctrl_solde.SetToolTip(wx.ToolTip(_(u"Solde final du compte")))
    
    def SetSolde(self, montant=FloatToDecimal(0.0)):
        """ MAJ integrale du controle avec MAJ des donnees """
        if montant > FloatToDecimal(0.0) :
            label = u"+ %.2f %s" % (montant, SYMBOLE)
            self.SetBackgroundColour("#C4BCFC") # Bleu
        elif montant == FloatToDecimal(0.0) :
            label = u"0.00 %s" % SYMBOLE
            self.SetBackgroundColour("#5DF020") # Vert
        else:
            label = u"- %.2f %s" % (-montant, SYMBOLE)
            self.SetBackgroundColour("#F81515") # Rouge
        self.ctrl_solde.SetLabel(label)
        self.Layout() 
        self.Refresh() 


# -------------------------------------------------------------------------------------------------------------------
        
class Panel(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_informations", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille
        
        # Informations
        self.staticbox_infos = wx.StaticBox(self, -1, _(u"Messages"))
        self.ctrl_infos = CTRL_Informations.CTRL(self, IDfamille=self.IDfamille)
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        # Etat de la facturation
        self.staticbox_facturation = wx.StaticBox(self, -1, _(u"Etat du compte"))
        self.ctrl_facturation = OL_Etat_compte.ListView(self, id=-1, IDfamille=self.IDfamille, name="OL_Etat_compte", style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_facturation.SetMinSize((220, 20))
        
        if "linux" in sys.platform :
            UTILS_Linux.AdaptePolice(self.ctrl_facturation)
        
        # Solde du compte
        self.staticbox_solde = wx.StaticBox(self, -1, _(u"Solde du compte"))
        self.ctrl_solde = CTRL_Solde(self)
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        
        # Propriétés
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir un mémo familial")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le mémo familial sélectionné")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le mémo familial sélectionné")))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Infos
        staticbox_infos = wx.StaticBoxSizer(self.staticbox_infos, wx.VERTICAL)
        grid_sizer_infos = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_infos.Add(self.ctrl_infos, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, wx.ALL, 0)
        grid_sizer_infos.Add(grid_sizer_boutons, 1, wx.ALL, 0)
        
        grid_sizer_infos.AddGrowableCol(0)
        grid_sizer_infos.AddGrowableRow(0)
        staticbox_infos.Add(grid_sizer_infos, 1, wx.EXPAND|wx.ALL, 5)
        
        grid_sizer_base.Add(staticbox_infos, 1, wx.EXPAND|wx.ALL, 5)
        
        grid_sizer_compte = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        
        # Facturation
        staticbox_facturation = wx.StaticBoxSizer(self.staticbox_facturation, wx.VERTICAL)
        grid_sizer_facturation = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_facturation.Add(self.ctrl_facturation, 1, wx.EXPAND, 0)
        grid_sizer_facturation.AddGrowableCol(0)
        grid_sizer_facturation.AddGrowableRow(0)
        staticbox_facturation.Add(grid_sizer_facturation, 1, wx.EXPAND|wx.ALL, 5)
        
        grid_sizer_compte.Add(staticbox_facturation, 1, wx.EXPAND|wx.ALL, 5)
        
        # Solde
        staticbox_solde = wx.StaticBoxSizer(self.staticbox_solde, wx.VERTICAL)
        grid_sizer_solde = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_solde.Add(self.ctrl_solde, 1, wx.EXPAND, 0)
        grid_sizer_solde.AddGrowableCol(0)
        grid_sizer_solde.AddGrowableRow(0)
        staticbox_solde.Add(grid_sizer_solde, 1, wx.EXPAND|wx.ALL, 5)
        
        grid_sizer_compte.Add(staticbox_solde, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_compte.AddGrowableCol(0)
        grid_sizer_compte.AddGrowableRow(0)
        
        grid_sizer_base.Add(grid_sizer_compte, 1, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
    
    def OnBoutonAjouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_messages", "creer") == False : return
        import DLG_Saisie_message
        dlg = DLG_Saisie_message.Dialog(self, IDmessage=None, IDfamille=self.IDfamille, mode="famille")
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ()
        dlg.Destroy()
 
    def OnBoutonModifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_messages", "modifier") == False : return
        item = self.ctrl_infos.GetSelection()
        if not item or self.ctrl_infos.GetPyData(item)  == None or self.ctrl_infos.GetPyData(item)["type"] != "message":
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun message à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDmessage = self.ctrl_infos.GetPyData(item)["IDmessage"]
        import DLG_Saisie_message
        dlg = DLG_Saisie_message.Dialog(self, IDmessage=IDmessage, mode="famille")
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ()
        dlg.Destroy()

    def OnBoutonSupprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_messages", "supprimer") == False : return
        item = self.ctrl_infos.GetSelection()
        if not item or self.ctrl_infos.GetPyData(item)  == None or self.ctrl_infos.GetPyData(item)["type"] != "message":
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun message à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce message ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDmessage = self.ctrl_infos.GetPyData(item)["IDmessage"]
            DB = GestionDB.DB()
            DB.ReqDEL("messages", "IDmessage", IDmessage)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()

    def IsLectureAutorisee(self):
        return True

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        self.ctrl_infos.MAJ() 
        self.ctrl_facturation.MAJ() 
        # Remplit le contrôle solde
        solde = self.ctrl_facturation.GetSolde()
        self.ctrl_solde.SetSolde(solde)
                
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        return True
    
    def Sauvegarde(self):
        pass

    def GetListeMessages(self):
        return self.ctrl_infos.GetListeMessages()



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel, IDfamille=14)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    import time
    heure_debut = time.time()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    print "Temps de chargement DLG_Famille_informations =", time.time() - heure_debut
    frame_1.Show()
    app.MainLoop()