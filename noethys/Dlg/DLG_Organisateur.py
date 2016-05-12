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
import cStringIO
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_adresse
from Ctrl import CTRL_Saisie_tel
from Ctrl import CTRL_Saisie_mail
from Ctrl import CTRL_Logo
from Utils import UTILS_Gps
from Utils import UTILS_Utilisateurs

import GestionDB




class Dialog(wx.Dialog):
    def __init__(self, parent, empecheAnnulation=False):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.empecheAnnulation = empecheAnnulation
        
        self.logo = None
        
        intro = _(u"Saisissez ici les informations concernant l'organisateur. Ces données seront utilisées dans les différents documents édités par le logiciel.")
        titre = _(u"L'organisateur")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Organisateur.png")
        
        self.staticbox_nom_staticbox = wx.StaticBox(self, -1, _(u"Nom de l'organisateur"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        self.staticbox_coords_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées"))
        self.label_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_rue = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_adresse = wx.StaticText(self, -1, _(u"C.P. :"))
        self.ctrl_adresse = CTRL_Saisie_adresse.Adresse(self)
        self.label_tel = wx.StaticText(self, -1, _(u"Tél :"))
        self.ctrl_tel = CTRL_Saisie_tel.Tel(self, intitule=_(u"siège"))
        self.label_mail = wx.StaticText(self, -1, _(u"Email :"))
        self.ctrl_mail = CTRL_Saisie_mail.Mail(self)
        self.label_fax = wx.StaticText(self, -1, _(u"Fax :"))
        self.ctrl_fax = CTRL_Saisie_tel.Tel(self, intitule=_(u"fax"))
        self.label_site = wx.StaticText(self, -1, _(u"Site internet :"))
        self.ctrl_site = wx.TextCtrl(self, -1, u"")
        
        self.staticbox_numeros_staticbox = wx.StaticBox(self, -1, _(u"Numéros d'identification"))
        self.label_agrement = wx.StaticText(self, -1, _(u"Numéro agrément :"))
        self.ctrl_agrement = wx.TextCtrl(self, -1, u"")
        self.label_siret = wx.StaticText(self, -1, _(u"Numéro SIRET :"))
        self.ctrl_siret = wx.TextCtrl(self, -1, u"")
        self.label_ape = wx.StaticText(self, -1, _(u"Code APE :"))
        self.ctrl_ape = wx.TextCtrl(self, -1, u"")
        
        self.staticbox_logo_staticbox = wx.StaticBox(self, -1, _(u"Logo"))
        self.ctrl_logo = CTRL_Logo.CTRL(self, qualite=100, couleurFond=wx.Colour(255, 255, 255), size=(83, 83) )
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_visualiser = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        # Empêche l'annulation
        if self.empecheAnnulation == True :
            self.bouton_annuler.Show(False)
            self.EnableCloseButton(False)
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifierLogo, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimerLogo, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonVisualiserLogo, self.bouton_visualiser)

        self.Importation()

        
    def __set_properties(self):
        self.SetTitle(_(u"L'organisateur"))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici le nom de l'organisateur"))
        self.ctrl_rue.SetToolTipString(_(u"Saisissez ici la rue de l'adresse de l'organisateur"))
        self.ctrl_site.SetToolTipString(_(u"Saisissez ici l'adresse du site internet de l'organisateur"))
        self.ctrl_agrement.SetMinSize((200, -1))
        self.ctrl_agrement.SetToolTipString(_(u"Saisissez ici le numéro d'agrément de l'organisateur"))
        self.ctrl_siret.SetToolTipString(_(u"Saisissez ici le numéro SIRET de l'organisateur"))
        self.ctrl_ape.SetToolTipString(_(u"Saisissez ici le code APE de l'organisateur"))
        self.ctrl_logo.SetToolTipString(_(u"Logo de l'organisateur"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour ajouter ou modifier le logo de l'organisateur"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer le logo actuel"))
        self.bouton_visualiser.SetToolTipString(_(u"Cliquez ici pour visualiser le logo actuel en taille réelle"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider la saisie"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        staticbox_logo = wx.StaticBoxSizer(self.staticbox_logo_staticbox, wx.VERTICAL)
        grid_sizer_logo = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_logo_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        staticbox_numeros = wx.StaticBoxSizer(self.staticbox_numeros_staticbox, wx.VERTICAL)
        grid_sizer_numeros = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        staticbox_coords = wx.StaticBoxSizer(self.staticbox_coords_staticbox, wx.VERTICAL)
        grid_sizer_coords = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_fax = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_tel = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        staticbox_nom = wx.StaticBoxSizer(self.staticbox_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        staticbox_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_nom, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_coords.Add(self.label_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_rue, 0, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.label_adresse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_adresse, 0, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.label_tel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tel.Add(self.ctrl_tel, 0, 0, 0)
        grid_sizer_tel.Add(self.label_mail, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tel.Add(self.ctrl_mail, 0, wx.EXPAND, 0)
        grid_sizer_tel.AddGrowableCol(2)
        grid_sizer_coords.Add(grid_sizer_tel, 1, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.label_fax, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_fax.Add(self.ctrl_fax, 0, 0, 0)
        grid_sizer_fax.Add(self.label_site, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_fax.Add(self.ctrl_site, 0, wx.EXPAND, 0)
        grid_sizer_fax.AddGrowableCol(2)
        grid_sizer_coords.Add(grid_sizer_fax, 1, wx.EXPAND, 0)
        grid_sizer_coords.AddGrowableCol(1)
        staticbox_coords.Add(grid_sizer_coords, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_coords, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_numeros.Add(self.label_agrement, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_numeros.Add(self.ctrl_agrement, 0, wx.EXPAND, 0)
        grid_sizer_numeros.Add(self.label_siret, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_numeros.Add(self.ctrl_siret, 0, wx.EXPAND, 0)
        grid_sizer_numeros.Add(self.label_ape, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_numeros.Add(self.ctrl_ape, 0, wx.EXPAND, 0)
        grid_sizer_numeros.AddGrowableCol(1)
        staticbox_numeros.Add(grid_sizer_numeros, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_bas.Add(staticbox_numeros, 1, wx.EXPAND, 0)
        grid_sizer_logo.Add(self.ctrl_logo, 0, wx.EXPAND, 0)
        grid_sizer_logo_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_logo_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_logo_boutons.Add(self.bouton_visualiser, 0, 0, 0)
        grid_sizer_logo.Add(grid_sizer_logo_boutons, 1, wx.EXPAND, 0)
        grid_sizer_logo.AddGrowableRow(0)
        grid_sizer_logo.AddGrowableCol(0)
        staticbox_logo.Add(grid_sizer_logo, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_bas.Add(staticbox_logo, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lorganisateur")

    def GetGPSOrganisateur(self, cp="", ville=""):
        """ Récupère les coordonnées GPS de l'organisateur """
        if ville == "" or cp == "" : 
            return None
        # Recherche des coordonnées
        dictGPS = UTILS_Gps.GPS(cp=cp, ville=ville, pays="France")
        if dictGPS == None : 
            coords = None
        else :
            # Sauvegarde des coordonnées GPS dans la base
            lat, long = dictGPS["lat"], dictGPS["long"]
            coords = "%s;%s" % (str(lat), str(long))
        return coords

    def OnBoutonOk(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_organisateur", "modifier") == False : return
        
        nom = self.ctrl_nom.GetValue()
        rue = self.ctrl_rue.GetValue() 
        cp = self.ctrl_adresse.GetValueCP()
        ville = self.ctrl_adresse.GetValueVille()
        tel = self.ctrl_tel.GetNumero()
        fax = self.ctrl_fax.GetNumero()
        mail = self.ctrl_mail.GetMail()
        site = self.ctrl_site.GetValue()
        num_agrement = self.ctrl_agrement.GetValue()
        num_siret = self.ctrl_siret.GetValue()
        code_ape = self.ctrl_ape.GetValue()
        gps = self.GetGPSOrganisateur(cp, ville)
        
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("nom", nom),
                ("rue", rue),
                ("cp", cp),
                ("ville", ville),
                ("tel", tel),
                ("fax", fax),
                ("mail", mail),
                ("site", site),
                ("num_agrement", num_agrement),
                ("num_siret",  num_siret),
                ("code_ape", code_ape),
                ("gps", gps),
            ]
        req = """SELECT nom FROM organisateur WHERE IDorganisateur=1;"""
        DB.ExecuterReq(req)
        test = DB.ResultatReq()
        if len(test) == 0 :
            IDorganisateur = DB.ReqInsert("organisateur", listeDonnees)
        else:
            DB.ReqMAJ("organisateur", listeDonnees, "IDorganisateur", 1)
        
        # Sauvegarde du logo
        if self.ctrl_logo.estModifie == True :
            bmp = self.ctrl_logo.GetBuffer() 
            if bmp != None :
                DB.MAJimage(table="organisateur", key="IDorganisateur", IDkey=1, blobImage=bmp, nomChampBlob="logo")
            else:
                DB.ReqMAJ("organisateur", [("logo", None),], "IDorganisateur", 1)
        DB.Close()
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
        

    def Importation(self):
        """ Importation des données """
        db = GestionDB.DB()
        req = """SELECT nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape, logo
        FROM organisateur WHERE IDorganisateur=1;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        organisateur = listeDonnees[0]
        
        self.ctrl_nom.SetValue(organisateur[0])
        
        self.ctrl_rue.SetValue(organisateur[1])
        self.ctrl_adresse.SetValueCP(organisateur[2])
        self.ctrl_adresse.SetValueVille(organisateur[3])
        self.ctrl_tel.SetNumero(organisateur[4])
        self.ctrl_fax.SetNumero(organisateur[5])
        self.ctrl_mail.SetMail(organisateur[6])
        self.ctrl_site.SetValue(organisateur[7])
        
        # Numéros
        self.ctrl_agrement.SetValue(organisateur[8])
        self.ctrl_siret.SetValue(organisateur[9])
        self.ctrl_ape.SetValue(organisateur[10])
        
        # Logo
        img = organisateur[11]
        if img != None :
            self.ctrl_logo.ChargeFromBuffer(img)

    def OnBoutonModifierLogo(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_organisateur", "modifier") == False : return
        self.ctrl_logo.Ajouter()
    
    def OnBoutonSupprimerLogo(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_organisateur", "modifier") == False : return
        self.ctrl_logo.Supprimer()
    
    def OnBoutonVisualiserLogo(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_organisateur", "modifier") == False : return
        self.ctrl_logo.Visualiser()


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, empecheAnnulation=False)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()


