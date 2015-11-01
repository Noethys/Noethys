#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import  wx.lib.colourselect as  csel
import CTRL_Etiquettes

import GestionDB



class Dialog(wx.Dialog):
    def __init__(self, parent, listeActivites=[], nomActivite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent      
        self.listeActivites = listeActivites
        
        self.SetTitle(_(u"Saisie d'une étiquette"))
        
        # Label
        self.staticbox_label_staticbox = wx.StaticBox(self, -1, _(u"Label de l'étiquette"))
        self.ctrl_label = wx.TextCtrl(self, -1, "")

        # Couleur
        self.staticbox_couleur_staticbox = wx.StaticBox(self, -1, _(u"Couleur"))
        self.ctrl_couleur = csel.ColourSelect(self, -1, "", (255, 255, 255), size = (40, 22))

        # Parent
        self.staticbox_parent_staticbox = wx.StaticBox(self, -1, _(u"Sélection du parent"))
        self.ctrl_parent = CTRL_Etiquettes.CTRL(self, listeActivites=listeActivites, nomActivite=nomActivite, activeMenu=False)
        self.ctrl_parent.MAJ() 
        self.ctrl_parent.SetID(None)
        
        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.ctrl_active = wx.CheckBox(self, -1, _(u"Etiquette active"))
        self.ctrl_active.SetValue(True)
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        wx.CallLater(1, self.ctrl_label.SetFocus)

    def __set_properties(self):
        self.ctrl_label.SetToolTipString(_(u"Saisissez un label pour cette étiquette"))
        self.ctrl_couleur.SetToolTipString(_(u"Cliquez ici pour sélectionner une couleur pour cette étiquette"))
        self.ctrl_active.SetToolTipString(_(u"Décochez cette case pour empêcher l'utilisateur de sélectionner cette étiquette. Cette option peut par exemple servir pour créer une étiquette de regroupement pour des sous-étiquettes ou pour désactiver une étiquette obsolète."))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((500, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Label
        staticbox_label = wx.StaticBoxSizer(self.staticbox_label_staticbox, wx.VERTICAL)
        staticbox_label.Add(self.ctrl_label, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_label, 1, wx.EXPAND, 0)
        
        # Couleur
        staticbox_couleur = wx.StaticBoxSizer(self.staticbox_couleur_staticbox, wx.VERTICAL)
        staticbox_couleur.Add(self.ctrl_couleur, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_couleur, 1, wx.EXPAND, 0)
        
        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.TOP | wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Parent
        staticbox_parent = wx.StaticBoxSizer(self.staticbox_parent_staticbox, wx.VERTICAL)
        staticbox_parent.Add(self.ctrl_parent, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_parent, 1, wx.EXPAND | wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        staticbox_options.Add(self.ctrl_active, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_options, 1, wx.EXPAND | wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
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
        

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event): 
        # Vérification des données
        if len(self.ctrl_label.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un label pour cette étiquette !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_label.SetFocus()
            return

##        if self.GetCouleur() == "(255, 255, 255)" :
##            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une couleur en cliquant sur le bouton couleur."), "Information", wx.OK | wx.ICON_INFORMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.ctrl_couleur.SetFocus()
##            return
                
        if self.GetIDparent() == (None, None) :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une étiquette parente !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_parent.SetFocus()
            return
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetLabel(self):
        return self.ctrl_label.GetValue()
    
    def GetCouleur(self):
        couleur = self.ctrl_couleur.GetValue()
        return "(%d, %d, %d)" % (couleur[0], couleur[1], couleur[2])
    
    def GetOptions(self):
        active = self.ctrl_active.GetValue()
        dictOptions = {
            "active" : active,
            }
        return dictOptions
        
    def GetIDparent(self):
        return self.ctrl_parent.GetID() 
    
    def SetLabel(self, texte=""):
        self.SetTitle(_(u"Modification d'une étiquette"))
        if texte != None :
            self.ctrl_label.SetValue(texte)
    
    def SetCouleur(self, texte=""):
        if texte != None :
            temp = texte[1:-1].split(",")
            self.ctrl_couleur.SetValue((int(temp[0]), int(temp[1]), int(temp[2]),))
    
    def SetIDparent(self, IDetiquette=None, IDactivite=None):
        self.ctrl_parent.SetID(IDetiquette, IDactivite)
        
    def SetOptions(self, dictOptions={}):
        if dictOptions.has_key("active") : 
            active = dictOptions["active"]
            if active == "" or active == None :
                active = 1
            self.ctrl_active.SetValue(active)
        
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
