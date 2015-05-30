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
import GestionDB

import CTRL_Saisie_adresse
import CTRL_Saisie_tel


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent      
        
        self.staticbox_adresse_staticbox = wx.StaticBox(self, -1, _(u"Adresse"))
        self.staticbox_coords_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées"))
        self.staticbox_identite_staticbox = wx.StaticBox(self, -1, _(u"Identité"))
        
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        self.label_prenom = wx.StaticText(self, -1, _(u"Prénom :"))
        self.ctrl_prenom = wx.TextCtrl(self, -1, "")
        self.label_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_rue = wx.TextCtrl(self, -1, "")
        self.label_cp = wx.StaticText(self, -1, _(u"C.P. :"))
        self.ctrl_ville = CTRL_Saisie_adresse.Adresse(self)
        self.label_tel = wx.StaticText(self, -1, _(u"Tél. Cabinet :"))
        self.ctrl_tel = CTRL_Saisie_tel.Tel(self, intitule=_(u"cabinet"))
        self.label_mobile = wx.StaticText(self, -1, _(u"Tél. Mobile :"))
        self.ctrl_mobile = CTRL_Saisie_tel.Tel(self, intitule=_(u"mobile"))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.ctrl_nom.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusNom)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un médecin"))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez le nom de famille du médecin"))
        self.ctrl_prenom.SetToolTipString(_(u"Saisissez le prénom du médecin"))
        self.ctrl_rue.SetToolTipString(_(u"Saisissez la rue du cabinet du médecin"))
        self.ctrl_tel.SetToolTipString(_(u"Saisissez le numéro de téléphone du cabinet"))
        self.ctrl_mobile.SetToolTipString(_(u"Saisissez le numéro de mobile du médecin"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider et fermer"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_coords = wx.StaticBoxSizer(self.staticbox_coords_staticbox, wx.VERTICAL)
        grid_sizer_coords = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=0)
        staticbox_adresse = wx.StaticBoxSizer(self.staticbox_adresse_staticbox, wx.VERTICAL)
        grid_sizer_adresse = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        staticbox_identite = wx.StaticBoxSizer(self.staticbox_identite_staticbox, wx.VERTICAL)
        grid_sizer_identite = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_identite.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_identite.Add(self.label_prenom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_prenom, 0, wx.EXPAND, 0)
        grid_sizer_identite.AddGrowableCol(1)
        staticbox_identite.Add(grid_sizer_identite, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_identite, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_adresse.Add(self.label_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_rue, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_cp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_ville, 0, wx.EXPAND, 0)
        grid_sizer_adresse.AddGrowableCol(1)
        staticbox_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_adresse, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_coords.Add(self.label_tel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_tel, 0, 0, 0)
        grid_sizer_coords.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.label_mobile, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_mobile, 0, wx.EXPAND, 0)
        staticbox_coords.Add(grid_sizer_coords, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_coords, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
    
    def OnKillFocusNom(self, event):
        self.ctrl_nom.SetValue(self.GetNom().upper())
        
    def GetNom(self):
        return self.ctrl_nom.GetValue()

    def GetPrenom(self):
        return self.ctrl_prenom.GetValue()    

    def GetRue(self):
        return self.ctrl_rue.GetValue()   
    
    def GetCp(self):
        return self.ctrl_ville.GetValueCP()

    def GetVille(self):
        return self.ctrl_ville.GetValueVille()
    
    def GetTel(self):
        return self.ctrl_tel.GetNumero()

    def GetMobile(self):
        return self.ctrl_mobile.GetNumero()


    def SetNom(self, nom=""):
        self.ctrl_nom.SetValue(nom)

    def SetPrenom(self, prenom=""):
        self.ctrl_prenom.SetValue(prenom)    

    def SetRue(self, rue=""):
        self.ctrl_rue.SetValue(rue)   
    
    def SetCp(self, cp=""):
        self.ctrl_ville.SetValueCP(cp)

    def SetVille(self, ville=""):
        self.ctrl_ville.SetValueVille(ville)
    
    def SetTel(self, numero=""):
        self.ctrl_tel.SetNumero(numero)

    def SetMobile(self, numero=""):
        self.ctrl_mobile.SetNumero(numero)

    def OnBoutonOk(self, event):
        if self.GetNom() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun nom !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Mdecins")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
