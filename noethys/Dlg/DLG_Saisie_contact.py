#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Saisie_adresse
from Ctrl import CTRL_Saisie_tel
from Ctrl import CTRL_Saisie_mail


class Dialog(wx.Dialog):
    def __init__(self, parent, IDcontact=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDcontact = IDcontact
        
        self.staticbox_identite_staticbox = wx.StaticBox(self, -1, _(u"Identité"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")
        self.label_prenom = wx.StaticText(self, -1, _(u"Prénom :"))
        self.ctrl_prenom = wx.TextCtrl(self, -1, "")

        self.staticbox_coords_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées"))
        self.label_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_rue = wx.TextCtrl(self, -1, "")
        self.label_cp = wx.StaticText(self, -1, _(u"C.P. :"))
        self.ctrl_ville = CTRL_Saisie_adresse.Adresse(self)
        self.label_tel = wx.StaticText(self, -1, _(u"Tél. fixe :"))
        self.ctrl_tel = CTRL_Saisie_tel.Tel(self, intitule=_(u"domicile"))
        self.label_mobile = wx.StaticText(self, -1, _(u"Tél. portable :"))
        self.ctrl_mobile = CTRL_Saisie_tel.Tel(self, intitule=_(u"mobile"))
        self.label_mail = wx.StaticText(self, -1, _(u"Email :"))
        self.ctrl_mail = CTRL_Saisie_mail.Mail(self)
        self.label_site = wx.StaticText(self, -1, _(u"Site internet :"))
        self.ctrl_site = wx.TextCtrl(self, -1, "")

        self.staticbox_memo_staticbox = wx.StaticBox(self, -1, _(u"Mémo"))
        self.ctrl_memo = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.ctrl_memo.SetMinSize((300, 90))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Init
        if self.IDcontact:
            self.Importation()

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un contact"))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez le nom du contact")))
        self.ctrl_prenom.SetToolTip(wx.ToolTip(_(u"Saisissez le prénom du contact")))
        self.ctrl_rue.SetToolTip(wx.ToolTip(_(u"Saisissez la rue du contact")))
        self.ctrl_tel.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro de téléphone fixe du contact")))
        self.ctrl_mobile.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro de portable du contact")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Identité
        staticbox_identite = wx.StaticBoxSizer(self.staticbox_identite_staticbox, wx.VERTICAL)
        grid_sizer_identite = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_identite.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_identite.Add(self.label_prenom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_prenom, 0, wx.EXPAND, 0)
        grid_sizer_identite.AddGrowableCol(1)
        staticbox_identite.Add(grid_sizer_identite, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_identite, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Coordonnées
        staticbox_coords = wx.StaticBoxSizer(self.staticbox_coords_staticbox, wx.VERTICAL)
        grid_sizer_coords = wx.FlexGridSizer(rows=8, cols=2, vgap=10, hgap=10)
        grid_sizer_coords.Add(self.label_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_rue, 0, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.label_cp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_ville, 0, wx.EXPAND, 0)

        grid_sizer_coords.Add(self.label_tel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tel = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_tel.Add(self.ctrl_tel, 0, 0, 0)
        grid_sizer_tel.Add(self.label_mobile, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tel.Add(self.ctrl_mobile, 0, 0, 0)
        grid_sizer_coords.Add(grid_sizer_tel, 1, wx.ALL | wx.EXPAND, 0)

        grid_sizer_coords.Add(self.label_mail, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_mail, 0, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.label_site, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_site, 0, wx.EXPAND, 0)
        grid_sizer_coords.AddGrowableCol(1)
        staticbox_coords.Add(grid_sizer_coords, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_coords, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Mémo
        staticbox_memo = wx.StaticBoxSizer(self.staticbox_memo_staticbox, wx.VERTICAL)
        staticbox_memo.Add(self.ctrl_memo, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_memo, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDcontact, nom, prenom, rue_resid, cp_resid, ville_resid, tel_domicile, tel_mobile, mail, site, memo
        FROM contacts
        WHERE IDcontact=%d;""" % self.IDcontact
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if listeDonnees:
            IDcontact, nom, prenom, rue_resid, cp_resid, ville_resid, tel_domicile, tel_mobile, mail, site, memo = listeDonnees[0]
            self.ctrl_nom.SetValue(nom)
            self.ctrl_prenom.SetValue(prenom)
            self.ctrl_rue.SetValue(rue_resid)
            self.ctrl_ville.SetValueCP(cp_resid)
            self.ctrl_ville.SetValueVille(ville_resid)
            self.ctrl_tel.SetNumero(tel_domicile)
            self.ctrl_mobile.SetNumero(tel_mobile)
            self.ctrl_mail.SetMail(mail)
            self.ctrl_site.SetValue(site)
            self.ctrl_memo.SetValue(memo)

    def OnBoutonOk(self, event):
        if not self.ctrl_nom.GetValue():
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir au moins un nom !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        DB = GestionDB.DB()
        listeDonnees = [
            ("nom", self.ctrl_nom.GetValue()),
            ("prenom", self.ctrl_prenom.GetValue()),
            ("rue_resid", self.ctrl_rue.GetValue()),
            ("cp_resid", self.ctrl_ville.GetValueCP()),
            ("ville_resid", self.ctrl_ville.GetValueVille()),
            ("tel_domicile", self.ctrl_tel.GetNumero()),
            ("tel_mobile", self.ctrl_mobile.GetNumero()),
            ("mail", self.ctrl_mail.GetMail()),
            ("site", self.ctrl_site.GetValue()),
            ("memo", self.ctrl_memo.GetValue()),
        ]
        if self.IDcontact == None :
            self.IDcontact = DB.ReqInsert("contacts", listeDonnees)
        else:
            DB.ReqMAJ("contacts", listeDonnees, "IDcontact", self.IDcontact)
        DB.Close()

        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def GetIDcontact(self):
        return self.IDcontact



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
