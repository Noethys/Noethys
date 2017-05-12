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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import time

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_heure

import GestionDB




class Dialog(wx.Dialog):
    def __init__(self, parent, nouveau=False, heure_min=None, heure_max=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.heure_min = heure_min
        self.heure_max = heure_max
        
        if nouveau == True :
            intro = _(u"Vous pouvez saisir ici une consommation horaire. Cliquez sur le bouton Horloge pour insérer l'heure actuelle.")
            titre = _(u"Saisie d'un horaire")
        else:
            intro = _(u"Vous pouvez modifier ici une consommation horaire. Cliquez sur le bouton Horloge pour insérer l'heure actuelle.")
            titre = _(u"Modification d'un horaire")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Horloge2.png")

        fontLabel = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial')
        fontHeure = wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial')
        
        self.label_heure_debut = wx.StaticText(self, -1, _(u"De"))
        self.label_heure_debut.SetFont(fontLabel)
        self.ctrl_heure_debut = CTRL_Saisie_heure.Heure(self, style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
        self.ctrl_heure_debut.SetFont(fontHeure)
        self.ctrl_heure_debut.SetMinSize((100, 40))
        self.bouton_heure_debut_now = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Horloge3.png"), wx.BITMAP_TYPE_ANY))
        
        self.label_heure_fin = wx.StaticText(self, -1, u"à")
        self.label_heure_fin.SetFont(fontLabel)
        self.ctrl_heure_fin = CTRL_Saisie_heure.Heure(self, style=wx.TE_PROCESS_ENTER|wx.TE_CENTER)
        self.ctrl_heure_fin.SetFont(fontHeure)
        self.ctrl_heure_fin.SetMinSize((100, 40))
        self.bouton_heure_fin_now = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Horloge3.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        if nouveau == True :
            self.bouton_supprimer.Enable(False)
            
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHeureDebutNow, self.bouton_heure_debut_now)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonHeureFinNow, self.bouton_heure_fin_now)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
##        self.ctrl_heure_debut.Bind(wx.EVT_TEXT_ENTER, self.OnBoutonOk)
##        self.ctrl_heure_fin.Bind(wx.EVT_TEXT_ENTER, self.OnBoutonOk)
        self.ctrl_heure_debut.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        self.ctrl_heure_fin.Bind(wx.EVT_KEY_DOWN, self.OnKey)

    def __set_properties(self):
        self.bouton_heure_debut_now.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour appliquer l'heure actuelle à l'heure de début")))
        self.bouton_heure_fin_now.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour appliquer l'heure actuelle à l'heure de fin")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer cette consommation")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((350, 110))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=10, vgap=5, hgap=5)
        grid_sizer_contenu.Add( (20, 5), 0, 0, 0)
        grid_sizer_contenu.Add(self.label_heure_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_heure_debut, 0, 0, 0) 
        grid_sizer_contenu.Add(self.bouton_heure_debut_now, 0, wx.EXPAND, 0) 
        grid_sizer_contenu.Add( (5, 5), 0, 0, 0)
        grid_sizer_contenu.Add(self.label_heure_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_heure_fin, 0, 0, 0)
        grid_sizer_contenu.Add(self.bouton_heure_fin_now, 0, wx.EXPAND, 0) 
        grid_sizer_contenu.Add( (5, 5), 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 20)
        
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnKey(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER: 
            self.OnBoutonOk() 
        event.Skip() 
        
    def OnBoutonHeureDebutNow(self, event):
        heureActuelle = time.strftime('%H:%M', time.localtime()) 
        self.ctrl_heure_debut.SetHeure(heureActuelle)
        
    def OnBoutonHeureFinNow(self, event):
        heureActuelle = time.strftime('%H:%M', time.localtime()) 
        self.ctrl_heure_fin.SetHeure(heureActuelle)

    def OnBoutonSupprimer(self, event):
        self.EndModal(3)

    def OnBoutonOk(self, event=None):
        # Vérification des données saisies
        if self.ctrl_heure_debut.GetHeure() == None or self.ctrl_heure_debut.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de début valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_debut.SetFocus()
            return
        if self.ctrl_heure_fin.GetHeure() == None or self.ctrl_heure_fin.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de fin valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_fin.SetFocus()
            return
        if self.ctrl_heure_debut.GetHeure() > self.ctrl_heure_fin.GetHeure() :
            dlg = wx.MessageDialog(self, _(u"L'heure de début ne peut pas être supérieure à l'heure de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.ctrl_heure_debut.GetHeure() == self.ctrl_heure_fin.GetHeure() :
            dlg = wx.MessageDialog(self, _(u"L'heure de début ne peut pas être égale à l'heure de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
##        if self.heure_min != None and self.ctrl_heure_debut.GetHeure() < self.heure_min :
##            dlg = wx.MessageDialog(self, _(u"L'heure de début ne peut pas être inférieure à %s !") % self.heure_min, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.ctrl_heure_debut.SetFocus()
##            return
##        if self.heure_max != None and self.ctrl_heure_fin.GetHeure() < self.heure_max :
##            dlg = wx.MessageDialog(self, _(u"L'heure de fin ne peut pas être supérieure à %s !") % self.heure_max, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.ctrl_heure_fin.SetFocus()
##            return
        
                    
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def SetHeureDebut(self, heure, fixe=False):
        self.ctrl_heure_debut.SetHeure(heure)
        if fixe == 1 :
            self.ctrl_heure_debut.Enable(False)
            self.bouton_heure_debut_now.Enable(False)
        wx.CallAfter(self.SetFocusHeure)

    def SetHeureFin(self, heure, fixe=False):
        self.ctrl_heure_fin.SetHeure(heure)
        if fixe == 1 :
            self.ctrl_heure_fin.Enable(False)
            self.bouton_heure_fin_now.Enable(False)
        wx.CallAfter(self.SetFocusHeure)
    
    def SetFocusHeure(self):
        if self.ctrl_heure_fin.IsEnabled() == True :
            self.ctrl_heure_fin.SetFocus() 
            self.ctrl_heure_fin.SetInsertionPoint(0)
        if self.ctrl_heure_debut.IsEnabled() == True :
            self.ctrl_heure_debut.SetFocus() 
            self.ctrl_heure_debut.SetInsertionPoint(0)
        
    def GetHeureDebut(self):
        return self.ctrl_heure_debut.GetHeure()

    def GetHeureFin(self):
        return self.ctrl_heure_fin.GetHeure()



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
