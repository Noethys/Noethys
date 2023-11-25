#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import string
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Ultrachoice
from Ctrl import CTRL_Saisie_adresse
from Ctrl import CTRL_Saisie_date
import GestionDB
from Utils import UTILS_Prelevements

if 'phoenix' in wx.PlatformInfo:
    validator = wx.Validator
    IsSilent = wx.Validator.IsSilent
else :
    validator = wx.PyValidator
    IsSilent = wx.Validator_IsSilent




class MyValidator(validator):
    def __init__(self):
        validator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return MyValidator()

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        for x in val:
            if x not in string.digits:
                return False
        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in string.digits or chr(key) in string.letters :
            event.Skip()
            return

        if not IsSilent():
            wx.Bell()

        return

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

# -----------------------------------------------------------------------------------------------------------------------


class CTRL_Banque(CTRL_Ultrachoice.CTRL):
    def __init__(self, parent, donnees=[]):
        CTRL_Ultrachoice.CTRL.__init__(self, parent, donnees) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeDonnees = self.GetListeDonnees()
        if len(listeDonnees) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetDonnees(listeDonnees)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDbanque, nom, rue_resid, cp_resid, ville_resid
        FROM banques
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDbanque, nom, rue_resid, cp_resid, ville_resid in listeDonnees :
            if rue_resid == None : rue_resid = ""
            if cp_resid == None : cp_resid = ""
            if ville_resid == None : ville_resid = ""
            self.dictDonnees[index] = { "ID" : IDbanque, "nom " : nom}
            listeItems.append({"label" : nom, "description" : u"%s %s %s" % (rue_resid, cp_resid, ville_resid)})
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection2(index)

    def GetID(self):
        index = self.GetSelection2()
        if index == -1 or (index in self.dictDonnees) == False : 
            return None
        return self.dictDonnees[index]["ID"]



# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Titulaire(wx.Choice):
    def __init__(self, parent, IDfamille=None):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDfamille = IDfamille
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        if self.IDfamille == None :
            return []
        # Récupération de la liste des représentants de la famille
        DB = GestionDB.DB()
        req = """SELECT individus.IDindividu, nom, prenom
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE IDfamille=%d AND IDcategorie=1
        GROUP BY individus.IDindividu
        ORDER BY nom, prenom;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        listeRepresentants = []
        for IDindividu, nom, prenom in listeDonnees :
            listeRepresentants.append({"IDindividu":IDindividu, "nom":nom, "prenom":prenom})
        
        # Remplissage du contrôle
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for donnees in listeRepresentants :
            label = u"%s %s" % (donnees["prenom"], donnees["nom"])
            self.dictDonnees[index] = { "ID" : donnees["IDindividu"], "nom " : label}
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]
            

# -----------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.SetTitle(_(u"Saisie du RIB"))
                                
        # RIB
        self.box_rib_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées bancaires"))
        
        self.label_cle_iban = wx.StaticText(self, -1, _(u"Clé IBAN"))
        self.label_etab = wx.StaticText(self, -1, _(u"Etab."))
        self.label_guichet = wx.StaticText(self, -1, _(u"Guichet"))
        self.label_numero = wx.StaticText(self, -1, _(u"Compte"))
        self.label_cle_rib = wx.StaticText(self, -1, _(u"Clé RIB"))
        
        self.ctrl_cle_iban = wx.TextCtrl(self, -1, _(u"FR76"), style=wx.TE_CENTRE)
        self.ctrl_code_etab = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE, validator = MyValidator())
        self.ctrl_code_guichet = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE, validator = MyValidator())
        self.ctrl_numero = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE, validator = MyValidator())
        self.ctrl_cle_rib = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE, validator = MyValidator())
        
        self.image_valide = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ok4.png"), wx.BITMAP_TYPE_ANY)
        self.image_nonvalide = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Interdit2.png"), wx.BITMAP_TYPE_ANY)
        self.ctrl_controle = wx.StaticBitmap(self, -1, self.image_nonvalide)
        
        # Etablissement
        self.label_banque = wx.StaticText(self, -1, _(u"Etablissement"))
        self.ctrl_banque = CTRL_Banque(self)
        self.bouton_banques = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        # Titulaire
        self.box_titulaire_staticbox = wx.StaticBox(self, -1, _(u"Titulaire du compte bancaire"))
        
        self.radio_membre = wx.RadioButton(self, -1, _(u"Le membre :"), style=wx.RB_GROUP)
        self.ctrl_membre = CTRL_Titulaire(self, IDfamille=IDfamille)
        
        self.radio_individu = wx.RadioButton(self, -1, _(u"Le titulaire suivant :"))
        self.label_individu_nom = wx.StaticText(self, -1, _(u"Nom :"))
        self.ctrl_individu_nom = wx.TextCtrl(self, -1, u"")
        self.label_individu_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_individu_rue = wx.TextCtrl(self, -1, u"")
        self.label_individu_ville = wx.StaticText(self, -1, _(u"C.P. :"))
        self.ctrl_individu_ville = CTRL_Saisie_adresse.Adresse(self)

        # Mémo
        self.box_memo_staticbox = wx.StaticBox(self, -1, _(u"Observations"))
        self.ctrl_memo = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_TEXT, self.OnSaisieRIB, self.ctrl_cle_iban)
        self.Bind(wx.EVT_TEXT, self.OnSaisieRIB, self.ctrl_code_etab)
        self.Bind(wx.EVT_TEXT, self.OnSaisieRIB, self.ctrl_code_guichet)
        self.Bind(wx.EVT_TEXT, self.OnSaisieRIB, self.ctrl_numero)
        self.Bind(wx.EVT_TEXT, self.OnSaisieRIB, self.ctrl_cle_rib)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonBanques, self.bouton_banques)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTitulaire, self.radio_membre)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTitulaire, self.radio_individu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        self.Importation() 
        self.OnSaisieRIB(None)
        self.OnRadioTitulaire(None)

    def __set_properties(self):
        self.ctrl_cle_iban.SetMinSize((55, -1))
        self.ctrl_code_etab.SetMinSize((50, -1))
        self.ctrl_code_guichet.SetMinSize((50, -1))
        self.ctrl_numero.SetMinSize((90, -1))
        self.ctrl_cle_rib.SetMinSize((40, -1))
        self.ctrl_code_etab.SetToolTip(wx.ToolTip(_(u"Saisissez ici le code Etablissement")))
        self.ctrl_code_guichet.SetToolTip(wx.ToolTip(_(u"Saisissez ici le code Guichet")))
        self.ctrl_numero.SetToolTip(wx.ToolTip(_(u"Saisissez ici le numéro de compte")))
        self.ctrl_cle_rib.SetToolTip(wx.ToolTip(_(u"Saisissez ici la clé RIB")))
        self.ctrl_controle.SetToolTip(wx.ToolTip(_(u"Une coche verte apparaît si les coordonnées bancaires sont valides")))
        self.ctrl_banque.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici l'établissement du compte")))
        self.bouton_banques.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des établissements bancaires")))
        self.radio_membre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner un membre de la famille")))
        self.ctrl_membre.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici un membre de la famille en tant que titulaire du compte bancaire")))
        self.radio_individu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir manuellement un titulaire de compte bancaire")))
        self.ctrl_individu_nom.SetToolTip(wx.ToolTip(_(u"Saisissez un nom de titulaire pour ce compte bancaire")))
        self.ctrl_individu_rue.SetToolTip(wx.ToolTip(_(u"Saisissez la rue de l'individu")))
        self.ctrl_memo.SetToolTip(wx.ToolTip(_(u"Saisissez des observations")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)
                
        # RIB
        box_rib = wx.StaticBoxSizer(self.box_rib_staticbox, wx.VERTICAL)
        
        grid_sizer_rib = wx.FlexGridSizer(rows=2, cols=6, vgap=5, hgap=5)
        grid_sizer_rib.Add(self.label_cle_iban, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rib.Add(self.label_etab, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rib.Add(self.label_guichet, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rib.Add(self.label_numero, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rib.Add(self.label_cle_rib, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rib.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_rib.Add(self.ctrl_cle_iban, 0, 0, 0)
        grid_sizer_rib.Add(self.ctrl_code_etab, 0, 0, 0)
        grid_sizer_rib.Add(self.ctrl_code_guichet, 0, 0, 0)
        grid_sizer_rib.Add(self.ctrl_numero, 0, 0, 0)
        grid_sizer_rib.Add(self.ctrl_cle_rib, 0, 0, 0)
        grid_sizer_rib.Add(self.ctrl_controle, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        box_rib.Add(grid_sizer_rib, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_label_banque = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_label_banque.Add(self.label_banque, 0, wx.EXPAND|wx.LEFT|wx.BOTTOM, 8)
        
        box_rib.Add(grid_sizer_label_banque, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
    
        grid_sizer_banque = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        
        grid_sizer_banque.Add(self.ctrl_banque, 0, wx.EXPAND, 0)
        grid_sizer_banque.Add(self.bouton_banques, 0, wx.EXPAND, 0)
        grid_sizer_banque.AddGrowableCol(0)
        box_rib.Add(grid_sizer_banque, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
                
        # Titulaire
        box_titulaire = wx.StaticBoxSizer(self.box_titulaire_staticbox, wx.VERTICAL)
        grid_sizer_titulaire = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)

        grid_sizer_membre = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_membre.Add(self.radio_membre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_membre.Add(self.ctrl_membre, 0, wx.EXPAND, 0)
        grid_sizer_membre.AddGrowableCol(1)
        grid_sizer_titulaire.Add(grid_sizer_membre, 1, wx.EXPAND, 0)
        
        grid_sizer_titulaire.Add(self.radio_individu, 0, 0, 0)
        
        grid_sizer_individu = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_individu.Add(self.label_individu_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_individu.Add(self.ctrl_individu_nom, 0, wx.EXPAND, 0)
        grid_sizer_individu.Add(self.label_individu_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_individu.Add(self.ctrl_individu_rue, 0, wx.EXPAND, 0)
        grid_sizer_individu.Add(self.label_individu_ville, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_individu.Add(self.ctrl_individu_ville, 0, wx.EXPAND, 0)
        grid_sizer_individu.AddGrowableCol(1)
        grid_sizer_titulaire.Add(grid_sizer_individu, 1, wx.LEFT|wx.EXPAND, 47)
        grid_sizer_titulaire.AddGrowableCol(0)
        box_titulaire.Add(grid_sizer_titulaire, 1, wx.ALL|wx.EXPAND, 10)
        
        
        # Mémo
        box_memo = wx.StaticBoxSizer(self.box_memo_staticbox, wx.VERTICAL)
        box_memo.Add(self.ctrl_memo, 1, wx.ALL|wx.EXPAND, 10)
        
        # Placement de tous les box
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_contenu.Add(box_rib, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(box_titulaire, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(box_memo, 1, wx.EXPAND, 0)
                
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnSaisieRIB(self, event):
        self.ControleRIB() 
        if event != None : event.Skip() 
    
    def ControleRIB(self):
        # Calcul du RIB
        cle_iban = self.ctrl_cle_iban.GetValue() 
        etab = self.ctrl_code_etab.GetValue()
        guichet = self.ctrl_code_guichet.GetValue()
        numero = self.ctrl_numero.GetValue()
        cle = self.ctrl_cle_rib.GetValue()
        rib = u"%s%s%s%s" % (etab, guichet, numero, cle)
        validationRIB = UTILS_Prelevements.AlgoControleRIB(rib)
        # Calcul du IBAN
        iban = ""
        if cle_iban != "" and rib != "" :
            iban = cle_iban + rib
            if UTILS_Prelevements.ControleIBAN(iban) == False :
                iban = ""
        if iban != "" :
            self.ctrl_controle.SetBitmap(self.image_valide)
            return True
        else :
            self.ctrl_controle.SetBitmap(self.image_nonvalide)
            return False
    
    def OnBoutonBanques(self, event):
        IDbanque = self.ctrl_banque.GetID()
        from Dlg import DLG_Banques
        dlg = DLG_Banques.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_banque.MAJ() 
        self.ctrl_banque.SetID(IDbanque)

    def OnRadioTitulaire(self, event):
        etat = self.radio_membre.GetValue()
        self.ctrl_membre.Enable(etat)
        self.ctrl_individu_nom.Enable(not etat)
        self.ctrl_individu_rue.Enable(not etat)
        self.ctrl_individu_ville.Enable(not etat)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Rglements1")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def Importation(self):
        """ Importation des données """
        if self.IDfamille == None :
            return
        DB = GestionDB.DB()
        req = """SELECT
        prelevement_etab, prelevement_guichet, prelevement_numero, prelevement_cle, prelevement_banque,
        prelevement_individu, prelevement_nom, prelevement_rue, prelevement_cp, prelevement_ville,
        prelevement_cle_iban, prelevement_iban, prelevement_bic, 
        prelevement_reference_mandat, prelevement_date_mandat, prelevement_memo
        FROM familles 
        WHERE IDfamille=%d;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        etab, guichet, numero, cle, IDbanque, IDindividu, nom, rue, cp, ville, cle_iban, iban, bic, reference_mandat, date_mandat, memo = listeDonnees[0]

        if etab == None : etab = ""
        if guichet == None : guichet = ""
        if numero == None : numero = ""
        if cle == None : cle = ""
        if nom == None : nom = ""
        if rue == None : rue = ""
        if cp == None : cp = ""
        if ville == None : ville = ""
        if cle_iban == None : 
            cle_iban = "FR76"
        if iban == None : iban = ""
        if bic == None : bic = ""
        if reference_mandat == None : 
            reference_mandat = str(self.IDfamille) 
        if memo == None : memo = ""

        # RIB
        self.ctrl_code_etab.SetValue(etab)
        self.ctrl_code_guichet.SetValue(guichet)
        self.ctrl_numero.SetValue(numero)
        self.ctrl_cle_rib.SetValue(cle)
        self.ctrl_banque.SetID(IDbanque)
        self.ctrl_cle_iban.SetValue(cle_iban) 
        
        self.ControleRIB() 
        
        # Titulaire
        if IDindividu != None :
            self.radio_membre.SetValue(True)
            self.ctrl_membre.SetID(IDindividu)
        else :
            self.radio_individu.SetValue(True)
            self.ctrl_individu_nom.SetValue(nom)
            self.ctrl_individu_rue.SetValue(rue)
            self.ctrl_individu_ville.SetValueCP(cp)
            self.ctrl_individu_ville.SetValueVille(ville)
        
        # Mémo
        self.ctrl_memo.SetValue(memo) 

    def OnBoutonOk(self, event):
        # Récupération des données
        etab = self.ctrl_code_etab.GetValue()
        guichet = self.ctrl_code_guichet.GetValue()
        numero = self.ctrl_numero.GetValue()
        cle = self.ctrl_cle_rib.GetValue()
        IDbanque = self.ctrl_banque.GetID()
        IDindividu = self.ctrl_membre.GetID()
        nom = self.ctrl_individu_nom.GetValue()
        rue = self.ctrl_individu_rue.GetValue()
        cp = self.ctrl_individu_ville.GetValueCP()
        ville = self.ctrl_individu_ville.GetValueVille()
        cle_iban = self.ctrl_cle_iban.GetValue() 
        memo = self.ctrl_memo.GetValue() 

        if self.radio_membre.GetValue() == True :
            nom = None
            rue = None
            cp = None
            ville = None
        else :
            IDindividu = None

        # Vérification des données saisies
        if self.ControleRIB() == False :
            dlg = wx.MessageDialog(self, _(u"Il est impossible d'activer le prélèvement :\nLes coordonnées bancaires ne sont pas valides !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_code_etab.SetFocus()
            return

        if IDbanque == None :
            dlg = wx.MessageDialog(self, _(u"Il est impossible d'activer le prélèvement :\nVous n'avez sélectionné aucun établissement bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_banque.SetFocus()
            return
        
        if self.radio_membre.GetValue() == True :
            if IDindividu == None :
                dlg = wx.MessageDialog(self, _(u"Il est impossible d'activer le prélèvement :\nVous n'avez pas sélectionné de titulaire du compte bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_membre.SetFocus()
                return
        else :
            if nom == "" or rue == "" or cp == "" or ville == "" or cp == None or ville == None :
                dlg = wx.MessageDialog(self, _(u"Il est impossible d'activer le prélèvement :\nVous n'avez pas renseigné le titulaire du compte bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_individu_nom.SetFocus()
                return

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("prelevement_etab", etab),
                ("prelevement_guichet", guichet),
                ("prelevement_numero", numero),
                ("prelevement_cle", cle),
                ("prelevement_banque", IDbanque),
                ("prelevement_individu", IDindividu),
                ("prelevement_nom", nom),
                ("prelevement_rue", rue),
                ("prelevement_cp", cp),
                ("prelevement_ville", ville),
                ("prelevement_cle_iban", cle_iban),
                ("prelevement_memo", memo),
            ]
        DB.ReqMAJ("familles", listeDonnees, "IDfamille", self.IDfamille)
        DB.Close()

        # Fermeture
        self.EndModal(wx.ID_OK)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=14)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
