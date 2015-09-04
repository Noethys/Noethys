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
import GestionDB


try: import psyco; psyco.full()
except: pass



class CTRL_Unites(wx.CheckListBox):
    def __init__(self, parent, listeUnites=[]):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.date = None
        self.listeUnites = listeUnites
        
        # Remplissage
        for label in self.listeUnites :
            self.Append(label)
                            
    def GetCoches(self):
        listeCoches = []
        NbreItems = len(self.listeUnites)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeCoches.append(index)
        return listeCoches
    
    def SetCoches(self, listeCoches=[]):
        for index in listeCoches :
            self.Check(index)

# ------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, listeUnites=[], afficheOptions=True):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_combi_credit", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDactivite = IDactivite
        self.listeUnites = listeUnites

        # Unites
        self.staticbox_unites = wx.StaticBox(self, -1, _(u"Unit�s � combiner"))
        self.ctrl_unites = CTRL_Unites(self, self.listeUnites)
        
        # Options
        self.staticbox_options = wx.StaticBox(self, -1, _(u"Options"))
        self.check_quantite = wx.CheckBox(self, -1, _(u"Quantit� max. :"))
        self.ctrl_quantite = wx.SpinCtrl(self, -1, "", min=0, max=500)
        
        if afficheOptions == False :
            self.staticbox_options.Show(False)
            self.check_quantite.Show(False)
            self.ctrl_quantite.Show(False)

        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckQuantite, self.check_quantite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Init
        self.OnCheckQuantite() 
        
    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une combinaison"))
        self.check_quantite.SetToolTipString(_(u"Vous pouvez d�finir ici un plafond maximal"))
        self.ctrl_unites.SetToolTipString(_(u"Cochez les unit�s � combiner"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((350, 420))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Unit�s
        staticbox_unites = wx.StaticBoxSizer(self.staticbox_unites, wx.VERTICAL)
        staticbox_unites.Add(self.ctrl_unites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_unites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_options.Add(self.check_quantite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_quantite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnCheckQuantite(self, event=None):
        self.ctrl_quantite.Enable(self.check_quantite.GetValue())

    def GetUnites(self):
        return self.ctrl_unites.GetCoches()
    
    def SetUnites(self, listeCoches=[]):
        return self.ctrl_unites.SetCoches(listeCoches)
    
    def GetQuantiteMax(self):
        if self.check_quantite.GetValue() == True :
            return self.ctrl_quantite.GetValue()
        else :
            return None
    
    def SetQuantiteMax(self, quantite=None):
        if quantite != None :
            self.check_quantite.SetValue(True)
            self.ctrl_quantite.SetValue(quantite)
        self.OnCheckQuantite() 
        
    def OnBoutonOk(self, event): 
        # Quantit�
        if self.check_quantite.GetValue() == True :
            quantite = self.ctrl_quantite.GetValue()
            if quantite == 0 or quantite == "" or quantite == None :
                dlg = wx.MessageDialog(self, _(u"La quantit� max. que vous avez saisi ne semble pas valide !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_quantite.SetFocus()
                return
        
        # Unit�s
        listeUnites = self.GetUnites()
        if len(listeUnites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une unit� !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
                
        # Fermeture fen�tre
        self.EndModal(wx.ID_OK)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()