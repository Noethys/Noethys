#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import UTILS_Prelevements


class Dialog(wx.Dialog):
    def __init__(self, parent, IDcompte=None, defaut=0):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDcompte = IDcompte
        self.defaut = defaut
        
        # G�n�ralit�s
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"G�n�ralit�s"))
        self.label_nom = wx.StaticText(self, -1, _(u"Intitul� :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_numero = wx.StaticText(self, -1, _(u"Num�ro :"))
        self.ctrl_numero = wx.TextCtrl(self, -1, u"")
        
        # Infos compl�mentaires
        self.box_infos_staticbox = wx.StaticBox(self, -1, _(u"Infos compl�mentaires"))
        self.label_info = wx.StaticText(self, -1, _(u"(Ces informations sont uniquement n�cessaires pour les pr�l�vements automatiques)"))
        self.label_raison = wx.StaticText(self, -1, _(u"Raison sociale :"))
        self.ctrl_raison = wx.TextCtrl(self, -1, u"")
        
        self.label_etab = wx.StaticText(self, -1, _(u"N� Etab. :"))
        self.ctrl_etab = wx.TextCtrl(self, -1, u"")
        self.label_guichet = wx.StaticText(self, -1, _(u"N� Guichet :"))
        self.ctrl_guichet = wx.TextCtrl(self, -1, u"")
        
        self.label_cle_rib = wx.StaticText(self, -1, _(u"Cl� RIB :"))
        self.ctrl_cle_rib = wx.TextCtrl(self, -1, u"")
        self.label_cle_iban = wx.StaticText(self, -1, _(u"Cl� IBAN :"))
        self.ctrl_cle_iban = wx.TextCtrl(self, -1, _(u"FR76"))
                
        self.label_iban = wx.StaticText(self, -1, _(u"N� IBAN :"))
        self.ctrl_iban = wx.TextCtrl(self, -1, u"")
        self.ctrl_iban.Enable(False) 

        self.image_valide = wx.Bitmap(u"Images/16x16/Ok4.png", wx.BITMAP_TYPE_ANY)
        self.image_nonvalide = wx.Bitmap(u"Images/16x16/Interdit2.png", wx.BITMAP_TYPE_ANY)
        self.ctrl_controle_iban = wx.StaticBitmap(self, -1, self.image_nonvalide)

        self.label_bic = wx.StaticText(self, -1, _(u"N� BIC :"))
        self.ctrl_bic = wx.TextCtrl(self, -1, u"")
        
        self.label_nne = wx.StaticText(self, -1, _(u"N� NNE :"))
        self.ctrl_nne = wx.TextCtrl(self, -1, u"")
        self.label_ics = wx.StaticText(self, -1, _(u"N� ICS :"))
        self.ctrl_ics = wx.TextCtrl(self, -1, u"")
        
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
        
        # Init contr�les
        if self.IDcompte != None :
            self.Importation() 
            
        self.MAJ_IBAN() 
        
    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un compte bancaire"))
        
        self.ctrl_numero.SetMinSize((200, -1))
        self.label_info.SetForegroundColour(wx.Colour(180, 180, 180))
        self.label_info.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, u""))
        
        self.ctrl_nom.SetToolTipString(_(u"Saisissez un intitul� pour ce compte (Ex : 'Compte cr�che')"))
        self.ctrl_numero.SetToolTipString(_(u"Saisissez le num�ro de compte"))
        self.ctrl_raison.SetToolTipString(_(u"Saisissez la raison sociale de l'organisme (Ex : 'Centre social'"))
        self.ctrl_etab.SetToolTipString(_(u"Saisissez le code �tablissement du compte"))
        self.ctrl_guichet.SetToolTipString(_(u"Saisissez le code guichet du compte"))
        self.ctrl_cle_rib.SetToolTipString(_(u"Saisissez la cl� RIB du compte"))
        self.ctrl_cle_iban.SetToolTipString(_(u"Saisissez la cl� IBAN du compte (FR76 pour la France)"))
        self.ctrl_bic.SetToolTipString(_(u"Saisissez le num�ro BIC du compte"))
        self.ctrl_iban.SetToolTipString(_(u"Saisissez le num�ro IBAN du compte"))
        self.ctrl_controle_iban.SetToolTipString(_(u"Une coche verte appara�t si les coordonn�es bancaires sont valides"))
        self.ctrl_nne.SetToolTipString(_(u"Saisissez le code NNE de l'organisme (pour les pr�l�vements automatiques NATIONAUX)"))
        self.ctrl_ics.SetToolTipString(_(u"Saisissez le code ICS de l'organisme (pour les pr�l�vements automatiques SEPA)"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_numero, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_numero, 0, 0, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        box_infos = wx.StaticBoxSizer(self.box_infos_staticbox, wx.VERTICAL)
        grid_sizer_infos = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)
        
        box_infos.Add(self.label_info, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)
        grid_sizer_infos.Add(self.label_raison, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infos.Add(self.ctrl_raison, 0, wx.EXPAND, 0)
        
        grid_sizer_infos.Add(self.label_etab, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_etab = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_etab.Add(self.ctrl_etab, 0, 0, 0)
        grid_sizer_etab.Add(self.label_guichet, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_etab.Add(self.ctrl_guichet, 0, 0, 0)
        grid_sizer_infos.Add(grid_sizer_etab, 1, wx.EXPAND, 0)

        grid_sizer_infos.Add(self.label_cle_rib, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_cle_iban = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_cle_iban.Add(self.ctrl_cle_rib, 0, 0, 0)
        grid_sizer_cle_iban.Add(self.label_cle_iban, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_cle_iban.Add(self.ctrl_cle_iban, 0, wx.EXPAND, 0)
        grid_sizer_cle_iban.AddGrowableCol(2)
        grid_sizer_infos.Add(grid_sizer_cle_iban, 1, wx.EXPAND, 0)

        grid_sizer_infos.Add(self.label_iban, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_iban = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_iban.Add(self.ctrl_iban, 0, wx.EXPAND, 0)
        grid_sizer_iban.Add(self.ctrl_controle_iban, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_iban.AddGrowableCol(0)
        grid_sizer_infos.Add(grid_sizer_iban, 1, wx.EXPAND, 0)

        grid_sizer_infos.Add(self.label_bic, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infos.Add(self.ctrl_bic, 0, wx.EXPAND, 0)
        
        grid_sizer_infos.Add(self.label_ics, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_ics = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_ics.Add(self.ctrl_ics, 0, 0, 0)
        grid_sizer_ics.Add(self.label_nne, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ics.Add(self.ctrl_nne, 0, wx.EXPAND, 0)
        grid_sizer_ics.AddGrowableCol(2)
        grid_sizer_infos.Add(grid_sizer_ics, 1, wx.EXPAND, 0)

        grid_sizer_infos.AddGrowableCol(1)
        box_infos.Add(grid_sizer_infos, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_infos, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
    
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Comptesbancaires")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        if self.Sauvegarde()  == False :
            return
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)
    
    def Sauvegarde(self):
        """ Sauvegarde des donn�es """
        nom = self.ctrl_nom.GetValue() 
        numero = self.ctrl_numero.GetValue() 
        raison = self.ctrl_raison.GetValue() 
        etab = self.ctrl_etab.GetValue() 
        guichet = self.ctrl_guichet.GetValue() 
        nne = self.ctrl_nne.GetValue() 
        cle_rib = self.ctrl_cle_rib.GetValue() 
        cle_iban = self.ctrl_cle_iban.GetValue() 
        iban = self.ctrl_iban.GetValue() 
        bic = self.ctrl_bic.GetValue() 
        code_ics = self.ctrl_ics.GetValue() 
        
        # Validation des donn�es saisies
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce compte !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        if numero == "" :
            dlg = wx.MessageDialog(self, _(u"Etes-vous s�r de ne pas saisir de num�ro de compte ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
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
            ("code_nne", nne),
            ("cle_rib", cle_rib),
            ("cle_iban", cle_iban),
            ("iban", iban),
            ("bic", bic),
            ("code_ics", code_ics),
            ]
        if self.IDcompte == None :
            self.IDcompte = DB.ReqInsert("comptes_bancaires", listeDonnees)
        else :
            DB.ReqMAJ("comptes_bancaires", listeDonnees, "IDcompte", self.IDcompte)
        DB.Close()

    def Importation(self):
        """ Importation des valeurs """
        DB = GestionDB.DB()
        req = """SELECT nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics
        FROM comptes_bancaires WHERE IDcompte=%d;""" % self.IDcompte
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        nom, numero, self.defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics = listeTemp[0]

        if nom == None : nom = ""
        if numero == None : numero = ""
        if raison == None : raison = ""
        if code_etab == None : code_etab = ""
        if code_guichet == None : code_guichet = ""
        if code_nne == None : code_nne = ""
        if cle_rib == None : cle_rib = ""
        if cle_iban == None : cle_iban = ""
        if iban == None : iban = ""
        if bic == None : bic = ""
        if code_ics == None : code_ics = ""
        
        self.ctrl_nom.SetValue(nom) 
        self.ctrl_numero.SetValue(numero) 
        self.ctrl_raison.SetValue(raison) 
        self.ctrl_etab.SetValue(code_etab) 
        self.ctrl_guichet.SetValue(code_guichet) 
        self.ctrl_nne.SetValue(code_nne) 
        self.ctrl_cle_rib.SetValue(cle_rib) 
        if cle_iban == "" :
            cle_iban = "FR76"
        self.ctrl_cle_iban.SetValue(cle_iban) 
        self.ctrl_iban.SetValue(iban) 
        self.ctrl_bic.SetValue(bic) 
        self.ctrl_ics.SetValue(code_ics) 
        
        self.MAJ_IBAN() 
        
    def GetIDcompte(self):
        return self.IDcompte
    

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDcompte=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
