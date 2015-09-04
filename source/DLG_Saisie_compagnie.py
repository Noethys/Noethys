#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image

import GestionDB

import CTRL_Saisie_adresse
import CTRL_Saisie_tel
import CTRL_Saisie_mail


class Dialog(wx.Dialog):
    def __init__(self, parent, titre=_(u"Saisie d'une compagnie")):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        self.titre = titre
        
        # Nom
        self.staticbox_nom_staticbox = wx.StaticBox(self, -1, _(u"Nom de la compagnie"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        # Coords
        self.staticbox_coords_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées"))
        self.label_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_rue = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_ville = wx.StaticText(self, -1, _(u"C.P. :"))
        self.ctrl_ville = CTRL_Saisie_adresse.Adresse(self)
        self.label_tel = wx.StaticText(self, -1, _(u"Tél. :"))
        self.ctrl_tel = CTRL_Saisie_tel.Tel(self, intitule=_(u"restaurateur"))
        self.label_fax = wx.StaticText(self, -1, _(u"Fax. :"))
        self.ctrl_fax = CTRL_Saisie_tel.Tel(self, intitule=_(u"fax"))
        self.label_mail = wx.StaticText(self, -1, _(u"Email :"))
        self.ctrl_mail = CTRL_Saisie_mail.Mail(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.SetTitle(self.titre)
        self.ctrl_nom.SetToolTipString(_(u"Saisissez le nom de la compagnie"))
        self.ctrl_rue.SetToolTipString(_(u"Saisissez la rue"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((375, 305))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_coords = wx.StaticBoxSizer(self.staticbox_coords_staticbox, wx.VERTICAL)
        grid_sizer_coords = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_tel = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        staticbox_nom = wx.StaticBoxSizer(self.staticbox_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        staticbox_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_coords.Add(self.label_rue, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_coords.Add(self.ctrl_rue, 0, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.label_ville, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_ville, 0, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.label_tel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tel.Add(self.ctrl_tel, 0, 0, 0)
        grid_sizer_tel.Add(self.label_fax, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tel.Add(self.ctrl_fax, 0, 0, 0)
        grid_sizer_coords.Add(grid_sizer_tel, 1, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.label_mail, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_mail, 0, wx.EXPAND, 0)
        grid_sizer_coords.AddGrowableCol(1)
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
        
    def GetNom(self):
        return self.ctrl_nom.GetValue()

    def GetRue(self):
        return self.ctrl_rue.GetValue()   
    
    def GetCp(self):
        return self.ctrl_ville.GetValueCP()

    def GetVille(self):
        return self.ctrl_ville.GetValueVille()
    
    def GetTel(self):
        return self.ctrl_tel.GetNumero()

    def GetFax(self):
        return self.ctrl_fax.GetNumero()

    def GetMail(self):
        return self.ctrl_mail.GetMail()

    def SetNom(self, nom=""):
        self.ctrl_nom.SetValue(nom)

    def SetRue(self, rue=""):
        self.ctrl_rue.SetValue(rue)   
    
    def SetCp(self, cp=""):
        self.ctrl_ville.SetValueCP(cp)

    def SetVille(self, ville=""):
        self.ctrl_ville.SetValueVille(ville)
    
    def SetTel(self, numero=""):
        self.ctrl_tel.SetNumero(numero)

    def SetFax(self, numero=""):
        self.ctrl_fax.SetNumero(numero)

    def SetMail(self, mail=""):
        return self.ctrl_mail.SetMail(mail)
    
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
        UTILS_Aide.Aide("Compagnies")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
