#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Utils import UTILS_Prelevements


class Dialog(wx.Dialog):
    def __init__(self, parent, IDcompte=None, defaut=0):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDcompte = IDcompte
        self.defaut = defaut
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_nom = wx.StaticText(self, -1, _(u"Intitulé :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_numero = wx.StaticText(self, -1, _(u"Numéro :"))
        self.ctrl_numero = wx.TextCtrl(self, -1, u"")
        
        # Coordonnées bancaires
        self.box_infos_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées bancaires"))
        self.label_etab = wx.StaticText(self, -1, _(u"N° Etab. :"))
        self.ctrl_etab = wx.TextCtrl(self, -1, u"")
        self.label_guichet = wx.StaticText(self, -1, _(u"N° Guichet :"))
        self.ctrl_guichet = wx.TextCtrl(self, -1, u"")
        
        self.label_cle_rib = wx.StaticText(self, -1, _(u"Clé RIB :"))
        self.ctrl_cle_rib = wx.TextCtrl(self, -1, u"")
        self.label_cle_iban = wx.StaticText(self, -1, _(u"Clé IBAN :"))
        self.ctrl_cle_iban = wx.TextCtrl(self, -1, _(u"FR76"))
                
        self.label_iban = wx.StaticText(self, -1, _(u"N° IBAN :"))
        self.ctrl_iban = wx.TextCtrl(self, -1, u"")
        self.ctrl_iban.Enable(False) 

        self.image_valide = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ok4.png"), wx.BITMAP_TYPE_ANY)
        self.image_nonvalide = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Interdit2.png"), wx.BITMAP_TYPE_ANY)
        self.ctrl_controle_iban = wx.StaticBitmap(self, -1, self.image_nonvalide)

        self.label_bic = wx.StaticText(self, -1, _(u"N° BIC :"))
        self.ctrl_bic = wx.TextCtrl(self, -1, u"")

        # Créancier
        self.staticbox_creancier_staticbox = wx.StaticBox(self, -1, _(u"Identification du créancier pour les prélèvements"))
        self.label_ics = wx.StaticText(self, -1, _(u"N° ICS :"))
        self.ctrl_ics = wx.TextCtrl(self, -1, u"")
        self.label_raison = wx.StaticText(self, -1, _(u"Raison sociale :"))
        self.ctrl_raison = wx.TextCtrl(self, -1, u"")
        self.label_service = wx.StaticText(self, -1, _(u"Service :"))
        self.ctrl_service = wx.TextCtrl(self, -1, "")
        self.label_adresse_numero = wx.StaticText(self, -1, _(u"Numéro :"))
        self.ctrl_adresse_numero = wx.TextCtrl(self, -1, "")
        self.label_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_rue = wx.TextCtrl(self, -1, "")
        self.label_batiment = wx.StaticText(self, -1, _(u"Bâtiment :"))
        self.ctrl_batiment = wx.TextCtrl(self, -1, "")
        self.label_etage = wx.StaticText(self, -1, _(u"Etage :"))
        self.ctrl_etage = wx.TextCtrl(self, -1, "")
        self.label_boite = wx.StaticText(self, -1, _(u"Boîte :"))
        self.ctrl_boite = wx.TextCtrl(self, -1, "")
        self.label_cp = wx.StaticText(self, -1, _(u"CP :"))
        self.ctrl_cp = wx.TextCtrl(self, -1, "")
        self.label_ville = wx.StaticText(self, -1, _(u"Ville :"))
        self.ctrl_ville = wx.TextCtrl(self, -1, "")
        self.label_pays = wx.StaticText(self, -1, _(u"Code pays :"))
        self.ctrl_pays = wx.TextCtrl(self, -1, "")
        self.label_dft_titulaire = wx.StaticText(self, -1, _(u"Titulaire du compte :"))
        self.ctrl_dft_titulaire = wx.TextCtrl(self, -1, u"")
        self.label_dft_iban = wx.StaticText(self, -1, _(u"N° IBAN DFT :"))
        self.ctrl_dft_iban = wx.TextCtrl(self, -1, u"")
        self.dft_image_valide = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ok4.png"), wx.BITMAP_TYPE_ANY)
        self.dft_image_nonvalide = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Interdit2.png"), wx.BITMAP_TYPE_ANY)
        self.ctrl_controle_dft_iban = wx.StaticBitmap(self, -1, self.dft_image_nonvalide)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_TEXT, self.MAJ_IBAN, self.ctrl_etab)
        self.Bind(wx.EVT_TEXT, self.MAJ_IBAN, self.ctrl_guichet)
        self.Bind(wx.EVT_TEXT, self.MAJ_IBAN, self.ctrl_cle_rib)
        self.Bind(wx.EVT_TEXT, self.MAJ_IBAN, self.ctrl_cle_iban)
        self.Bind(wx.EVT_TEXT, self.MAJ_DFT_IBAN, self.ctrl_dft_iban)

        # Init contrôles
        if self.IDcompte != None :
            self.Importation() 
            
        self.MAJ_IBAN()
        self.MAJ_DFT_IBAN()
        
    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un compte bancaire"))
        self.ctrl_numero.SetMinSize((250, -1))
        self.ctrl_raison.SetMinSize((250, -1))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez un intitulé pour ce compte (Ex : 'Compte crèche')")))
        self.ctrl_numero.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro de compte")))
        self.ctrl_raison.SetToolTip(wx.ToolTip(_(u"Saisissez la raison sociale de l'organisme (Ex : 'Centre social'")))
        self.ctrl_etab.SetToolTip(wx.ToolTip(_(u"Saisissez le code établissement du compte")))
        self.ctrl_guichet.SetToolTip(wx.ToolTip(_(u"Saisissez le code guichet du compte")))
        self.ctrl_cle_rib.SetToolTip(wx.ToolTip(_(u"Saisissez la clé RIB du compte")))
        self.ctrl_cle_iban.SetToolTip(wx.ToolTip(_(u"Saisissez la clé IBAN du compte (FR76 pour la France)")))
        self.ctrl_bic.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro BIC du compte")))
        self.ctrl_iban.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro IBAN du compte")))
        self.ctrl_controle_iban.SetToolTip(wx.ToolTip(_(u"Une coche verte apparaît si les coordonnées bancaires sont valides")))
        self.ctrl_ics.SetToolTip(wx.ToolTip(_(u"Saisissez le code ICS de l'organisme (pour les prélèvements automatiques SEPA)")))
        self.ctrl_dft_titulaire.SetToolTip(wx.ToolTip(_(u"Saisissez le nom du titulaire du compte DFT")))
        self.ctrl_dft_iban.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro IBAN du compte DFT")))
        self.ctrl_service.SetToolTip(wx.ToolTip(_(u"Identité du destinataire ou du service. Exemple : Service comptabilité.")))
        self.ctrl_adresse_numero.SetToolTip(wx.ToolTip(_(u"Numéro de la voie. Exemple : 14.")))
        self.ctrl_rue.SetToolTip(wx.ToolTip(_(u"Libellé de la voie sans le numéro. Exemple : Rue des alouettes.")))
        self.ctrl_batiment.SetToolTip(wx.ToolTip(_(u"Nom de l'immeuble, du bâtiment ou de la résidence, etc... Exemple : Résidence les acacias.")))
        self.ctrl_etage.SetToolTip(wx.ToolTip(_(u"Numéro de l'étage, de l'annexe, etc... Exemple : Etage 4.")))
        self.ctrl_boite.SetToolTip(wx.ToolTip(_(u"Boîte postale, tri service arrivée, etc... Exemple : BP64.")))
        self.ctrl_cp.SetToolTip(wx.ToolTip(_(u"Code postal. Exemple : 29200.")))
        self.ctrl_ville.SetToolTip(wx.ToolTip(_(u"Nom de la ville. Exemple : BREST.")))
        self.ctrl_pays.SetToolTip(wx.ToolTip(_(u"Code du pays. Exemple : FR.")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_colonnes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_colonne_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)

        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_numero, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_numero, 0, 0, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_colonne_gauche.Add(box_generalites, 1, wx.EXPAND, 0)

        box_infos = wx.StaticBoxSizer(self.box_infos_staticbox, wx.VERTICAL)
        grid_sizer_infos = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)

        grid_sizer_infos.Add(self.label_etab, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_infos = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)
        grid_sizer_infos.Add(self.label_etab, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infos.Add(self.ctrl_etab, 0, wx.EXPAND, 0)
        grid_sizer_infos.Add(self.label_guichet, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infos.Add(self.ctrl_guichet, 0, wx.EXPAND, 0)
        grid_sizer_infos.Add(self.label_cle_rib, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infos.Add(self.ctrl_cle_rib, 0, wx.EXPAND, 0)
        grid_sizer_infos.Add(self.label_cle_iban, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infos.Add(self.ctrl_cle_iban, 0, wx.EXPAND, 0)
        grid_sizer_infos.Add(self.label_iban, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_iban = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_iban.Add(self.ctrl_iban, 0, wx.EXPAND, 0)
        grid_sizer_iban.Add(self.ctrl_controle_iban, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_iban.AddGrowableCol(0)
        grid_sizer_infos.Add(grid_sizer_iban, 1, wx.EXPAND, 0)

        grid_sizer_infos.Add(self.label_bic, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infos.Add(self.ctrl_bic, 0, wx.EXPAND, 0)

        grid_sizer_infos.AddGrowableCol(1)
        box_infos.Add(grid_sizer_infos, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_colonne_gauche.Add(box_infos, 1, wx.EXPAND, 0)

        grid_sizer_colonnes.Add(grid_sizer_colonne_gauche, 1, wx.EXPAND, 0)

        # Créancier
        staticbox_creancier = wx.StaticBoxSizer(self.staticbox_creancier_staticbox, wx.VERTICAL)
        grid_sizer_creancier = wx.FlexGridSizer(rows=14, cols=2, vgap=5, hgap=5)
        grid_sizer_creancier.Add(self.label_raison, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_raison, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_ics, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_ics, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_service, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_service, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_adresse_numero, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_adresse_numero, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_rue, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_batiment, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_batiment, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_etage, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_etage, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_boite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_boite, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_cp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_cp, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_ville, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_ville, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_pays, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_pays, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_dft_titulaire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_creancier.Add(self.ctrl_dft_titulaire, 0, wx.EXPAND, 0)
        grid_sizer_creancier.Add(self.label_dft_iban, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dft_iban = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_dft_iban.Add(self.ctrl_dft_iban, 0, wx.EXPAND, 0)
        grid_sizer_dft_iban.Add(self.ctrl_controle_dft_iban, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dft_iban.AddGrowableCol(0)
        grid_sizer_creancier.Add(grid_sizer_dft_iban, 1, wx.EXPAND, 0)
        grid_sizer_creancier.AddGrowableCol(1)
        staticbox_creancier.Add(grid_sizer_creancier, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_colonnes.Add(staticbox_creancier, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_base.Add(grid_sizer_colonnes, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)

        grid_sizer_colonnes.AddGrowableRow(0)
        grid_sizer_colonnes.AddGrowableCol(0)
        grid_sizer_colonnes.AddGrowableCol(1)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
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
    
    def MAJ_IBAN(self, event=None):
        """ Actualise le code IBAN """
        cle_iban = self.ctrl_cle_iban.GetValue() 
        etab = self.ctrl_etab.GetValue() 
        guichet = self.ctrl_guichet.GetValue() 
        compte = self.ctrl_numero.GetValue() 
        cle_rib = self.ctrl_cle_rib.GetValue() 
        
        iban = ""
        if cle_iban != "" and etab != "" and guichet != "" and compte != "" and cle_rib != "" :
            iban = cle_iban + etab + guichet + compte + cle_rib
            if UTILS_Prelevements.ControleIBAN(iban) == False :
                iban = ""
        self.ctrl_iban.SetValue(iban)
        if iban != "" :
            self.ctrl_controle_iban.SetBitmap(self.image_valide)
        else :
            self.ctrl_controle_iban.SetBitmap(self.image_nonvalide)
        if event != None : event.Skip()

    def MAJ_DFT_IBAN(self, event=None):
        """ Actualise le code IBAN du comte DFT """
        iban = self.ctrl_dft_iban.GetValue()
        if UTILS_Prelevements.ControleIBAN(iban) == False:
            self.ctrl_controle_dft_iban.SetBitmap(self.dft_image_nonvalide)
        else:
            self.ctrl_controle_dft_iban.SetBitmap(self.dft_image_valide)
        if event != None: event.Skip()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Comptesbancaires")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        if self.Sauvegarde()  == False :
            return
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def Sauvegarde(self):
        """ Sauvegarde des données """
        nom = self.ctrl_nom.GetValue() 
        numero = self.ctrl_numero.GetValue() 
        raison = self.ctrl_raison.GetValue() 
        etab = self.ctrl_etab.GetValue() 
        guichet = self.ctrl_guichet.GetValue()
        cle_rib = self.ctrl_cle_rib.GetValue() 
        cle_iban = self.ctrl_cle_iban.GetValue() 
        iban = self.ctrl_iban.GetValue() 
        bic = self.ctrl_bic.GetValue() 
        code_ics = self.ctrl_ics.GetValue()
        dft_titulaire = self.ctrl_dft_titulaire.GetValue()
        dft_iban = self.ctrl_dft_iban.GetValue()
        
        # Validation des données saisies
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce compte !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        if numero == "" :
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas saisir de numéro de compte ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse !=  wx.ID_YES :
                return
        
        # Sauvegarde
        DB = GestionDB.DB()

        listeDonnees = [ 
            ("nom", nom ),
            ("numero", numero ),
            ("defaut", self.defaut),
            ("raison", raison),
            ("code_etab", etab),
            ("code_guichet", guichet),
            ("cle_rib", cle_rib),
            ("cle_iban", cle_iban),
            ("iban", iban),
            ("bic", bic),
            ("code_ics", code_ics),
            ("dft_titulaire", dft_titulaire),
            ("dft_iban", dft_iban),
            ("adresse_service", self.ctrl_service.GetValue()),
            ("adresse_numero", self.ctrl_adresse_numero.GetValue()),
            ("adresse_rue", self.ctrl_rue.GetValue()),
            ("adresse_batiment", self.ctrl_batiment.GetValue()),
            ("adresse_etage", self.ctrl_etage.GetValue()),
            ("adresse_boite", self.ctrl_boite.GetValue()),
            ("adresse_cp", self.ctrl_cp.GetValue()),
            ("adresse_ville", self.ctrl_ville.GetValue()),
            ("adresse_pays", self.ctrl_pays.GetValue()),
            ]
        if self.IDcompte == None :
            self.IDcompte = DB.ReqInsert("comptes_bancaires", listeDonnees)
        else :
            DB.ReqMAJ("comptes_bancaires", listeDonnees, "IDcompte", self.IDcompte)
        DB.Close()

    def Importation(self):
        """ Importation des valeurs """
        DB = GestionDB.DB()
        req = """SELECT nom, numero, defaut, raison, code_etab, code_guichet, cle_rib, cle_iban, iban, bic, code_ics, dft_titulaire, dft_iban, 
        adresse_service, adresse_numero, adresse_rue, adresse_batiment, adresse_etage, adresse_boite, adresse_cp, adresse_ville, adresse_pays
        FROM comptes_bancaires WHERE IDcompte=%d;""" % self.IDcompte
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        nom, numero, self.defaut, raison, code_etab, code_guichet, cle_rib, cle_iban, iban, bic, code_ics, dft_titulaire, dft_iban, adresse_service, adresse_numero, adresse_rue, adresse_batiment, adresse_etage, adresse_boite, adresse_cp, adresse_ville, adresse_pays = listeTemp[0]

        if nom == None : nom = ""
        if numero == None : numero = ""
        if raison == None : raison = ""
        if code_etab == None : code_etab = ""
        if code_guichet == None : code_guichet = ""
        if cle_rib == None : cle_rib = ""
        if cle_iban == None : cle_iban = ""
        if iban == None : iban = ""
        if bic == None : bic = ""
        if code_ics == None : code_ics = ""
        if dft_titulaire == None : dft_titulaire = ""
        if dft_iban == None : dft_iban = ""

        self.ctrl_nom.SetValue(nom) 
        self.ctrl_numero.SetValue(numero) 
        self.ctrl_raison.SetValue(raison) 
        self.ctrl_etab.SetValue(code_etab) 
        self.ctrl_guichet.SetValue(code_guichet)
        self.ctrl_cle_rib.SetValue(cle_rib) 
        if cle_iban == "" :
            cle_iban = "FR76"
        self.ctrl_cle_iban.SetValue(cle_iban) 
        self.ctrl_iban.SetValue(iban) 
        self.ctrl_bic.SetValue(bic) 
        self.ctrl_ics.SetValue(code_ics)
        self.ctrl_dft_titulaire.SetValue(dft_titulaire)
        self.ctrl_dft_iban.SetValue(dft_iban)

        if adresse_service: self.ctrl_service.SetValue(adresse_service)
        if adresse_numero: self.ctrl_adresse_numero.SetValue(adresse_numero)
        if adresse_rue: self.ctrl_rue.SetValue(adresse_rue)
        if adresse_batiment: self.ctrl_batiment.SetValue(adresse_batiment)
        if adresse_etage: self.ctrl_etage.SetValue(adresse_etage)
        if adresse_boite: self.ctrl_boite.SetValue(adresse_boite)
        if adresse_cp: self.ctrl_cp.SetValue(adresse_cp)
        if adresse_ville: self.ctrl_ville.SetValue(adresse_ville)
        if adresse_pays: self.ctrl_pays.SetValue(adresse_pays)
        
        self.MAJ_IBAN()
        self.MAJ_DFT_IBAN()
        
    def GetIDcompte(self):
        return self.IDcompte
    

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDcompte=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
