#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
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


from Ctrl import CTRL_Ultrachoice
from Ctrl import CTRL_Saisie_adresse
from Ctrl import CTRL_Saisie_euros
import GestionDB
from Utils import UTILS_Titulaires
from Utils import UTILS_Prelevements




class MyValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
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

        if not wx.Validator_IsSilent():
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
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection2(index)

    def GetID(self):
        index = self.GetSelection2()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]



# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Famille(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.SetMinSize((100, -1))
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        titulaires = UTILS_Titulaires.GetTitulaires() 
        listeFamilles = []
        for IDfamille, dictTemp in titulaires.iteritems() :
            listeFamilles.append((dictTemp["titulairesSansCivilite"], IDfamille, dictTemp["IDcompte_payeur"]))
        listeFamilles.sort()
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "IDfamille" : 0, "nom" : _(u"Inconnue"), "IDcompte_payeur" : 0 }
        index = 1
        for nom, IDfamille, IDcompte_payeur in listeFamilles :
            self.dictDonnees[index] = { "IDfamille" : IDfamille, "nom " : nom, "IDcompte_payeur" : IDcompte_payeur}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetIDfamille(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["IDfamille"] == ID :
                 self.SetSelection(index)

    def GetIDfamille(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["IDfamille"]
    
    def GetIDcompte_payeur(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["IDcompte_payeur"]
            

# -----------------------------------------------------------------------------------------------------------------------



class Dialog(wx.Dialog):
    def __init__(self, parent, track=None, activeMontant=True):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.track = track
        
        self.SetTitle(_(u"Saisie d'un prélèvement"))
        
        # Famille
        self.box_famille_staticbox = wx.StaticBox(self, -1, _(u"Destinataire"))
        self.label_famille = wx.StaticText(self, -1, _(u"Famille :"))
        self.ctrl_famille = CTRL_Famille(self)
        
        # RIB
        self.box_rib_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées bancaires"))
        
        self.label_etab = wx.StaticText(self, -1, _(u"Etab."))
        self.label_guichet = wx.StaticText(self, -1, _(u"Guichet"))
        self.label_numero = wx.StaticText(self, -1, _(u"Numéro"))
        self.label_cle = wx.StaticText(self, -1, _(u"Clé"))
        self.ctrl_code_etab = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE, validator = MyValidator())
        self.ctrl_code_guichet = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE, validator = MyValidator())
        self.ctrl_numero = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE, validator = MyValidator())
        self.ctrl_cle = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE, validator = MyValidator())
        
        self.image_valide = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ok4.png"), wx.BITMAP_TYPE_ANY)
        self.image_nonvalide = wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Interdit2.png"), wx.BITMAP_TYPE_ANY)
        self.ctrl_controle = wx.StaticBitmap(self, -1, self.image_nonvalide)
        
        self.label_banque = wx.StaticText(self, -1, _(u"Etablissement"))
        self.ctrl_banque = CTRL_Banque(self)
        self.bouton_banques = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.label_titulaire = wx.StaticText(self, -1, _(u"Titulaire du compte"))
        self.ctrl_titulaire = wx.TextCtrl(self, -1, u"")

        # Prélèvement
        self.box_prelevement_staticbox = wx.StaticBox(self, -1, _(u"Prélèvement"))

        self.label_type = wx.StaticText(self, -1, _(u"Type :"))
        self.ctrl_type = wx.StaticText(self, -1, _(u"Saisie manuelle"))

        self.label_libelle = wx.StaticText(self, -1, _(u"Libellé :"))
        self.ctrl_libelle = wx.TextCtrl(self, -1, u"")

        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        if activeMontant == False :
            self.ctrl_montant.Enable(False) 
            
        self.label_etat = wx.StaticText(self, -1, _(u"Statut :"))
        self.radio_etat_attente = wx.RadioButton(self, -1, _(u"Attente"), style=wx.RB_GROUP)
        self.radio_etat_valide = wx.RadioButton(self, -1, _(u"Valide"))
        self.radio_etat_refus= wx.RadioButton(self, -1, _(u"Refus"))
        
        self.radio_etat_attente.Enable(False) 
        self.radio_etat_valide.Enable(False) 
        self.radio_etat_refus.Enable(False) 

        self.label_reglement = wx.StaticText(self, -1, _(u"Règlement :"))
        self.ctrl_reglement = wx.StaticText(self, -1, _(u"Non"))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHOICE, self.OnChoixFamille, self.ctrl_famille)
        self.Bind(wx.EVT_TEXT, self.OnSaisieRIB, self.ctrl_code_etab)
        self.Bind(wx.EVT_TEXT, self.OnSaisieRIB, self.ctrl_code_guichet)
        self.Bind(wx.EVT_TEXT, self.OnSaisieRIB, self.ctrl_numero)
        self.Bind(wx.EVT_TEXT, self.OnSaisieRIB, self.ctrl_cle)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonBanques, self.bouton_banques)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        self.Importation() 
        self.OnSaisieRIB(None)

    def __set_properties(self):
        self.ctrl_code_etab.SetMinSize((70, -1))
        self.ctrl_code_guichet.SetMinSize((70, -1))
        self.ctrl_numero.SetMinSize((150, -1))
        self.ctrl_cle.SetMinSize((50, -1))
        
        self.ctrl_type.SetForegroundColour(wx.Colour(150, 150, 150))
        self.ctrl_reglement.SetForegroundColour(wx.Colour(150, 150, 150))

        self.ctrl_famille.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici la famille à débiter")))
        self.ctrl_code_etab.SetToolTip(wx.ToolTip(_(u"Saisissez ici le code Etablissement")))
        self.ctrl_code_guichet.SetToolTip(wx.ToolTip(_(u"Saisissez ici le code Guichet")))
        self.ctrl_numero.SetToolTip(wx.ToolTip(_(u"Saisissez ici le numéro de compte")))
        self.ctrl_cle.SetToolTip(wx.ToolTip(_(u"Saisissez ici la clé du RIB")))
        self.ctrl_controle.SetToolTip(wx.ToolTip(_(u"Une coche verte apparaît si les coordonnées bancaires sont valides")))
        self.ctrl_banque.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici l'établissement du compte")))
        self.bouton_banques.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des établissements bancaires")))
        
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)

        # Activation
        box_famille = wx.StaticBoxSizer(self.box_famille_staticbox, wx.VERTICAL)
        grid_sizer_famille = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_famille.Add(self.label_famille, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_famille.Add(self.ctrl_famille, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
        grid_sizer_famille.AddGrowableCol(1)
        box_famille.Add(grid_sizer_famille, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_famille, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # RIB
        box_rib = wx.StaticBoxSizer(self.box_rib_staticbox, wx.VERTICAL)
        grid_sizer_rib = wx.FlexGridSizer(rows=2, cols=5, vgap=5, hgap=5)
        
        grid_sizer_rib.Add(self.label_etab, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rib.Add(self.label_guichet, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rib.Add(self.label_numero, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rib.Add(self.label_cle, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rib.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_rib.Add(self.ctrl_code_etab, 0, 0, 0)
        grid_sizer_rib.Add(self.ctrl_code_guichet, 0, 0, 0)
        grid_sizer_rib.Add(self.ctrl_numero, 0, 0, 0)
        grid_sizer_rib.Add(self.ctrl_cle, 0, 0, 0)
        grid_sizer_rib.Add(self.ctrl_controle, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        box_rib.Add(grid_sizer_rib, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        grid_sizer_label_banque = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_label_banque.Add(self.label_banque, 0, wx.EXPAND|wx.LEFT|wx.BOTTOM, 8)
        box_rib.Add(grid_sizer_label_banque, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
    
        grid_sizer_banque = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_banque.Add(self.ctrl_banque, 0, wx.EXPAND, 0)
        grid_sizer_banque.Add(self.bouton_banques, 0, wx.EXPAND, 0)
        grid_sizer_banque.AddGrowableCol(0)
        box_rib.Add(grid_sizer_banque, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_label_titulaire = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_label_titulaire.Add(self.label_titulaire, 0, wx.EXPAND|wx.LEFT|wx.BOTTOM, 8)
        box_rib.Add(grid_sizer_label_titulaire, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        box_rib.Add(self.ctrl_titulaire, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_base.Add(box_rib, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Prélèvement
        box_prelevement = wx.StaticBoxSizer(self.box_prelevement_staticbox, wx.VERTICAL)
        grid_sizer_prelevement = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        grid_sizer_prelevement.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prelevement.Add(self.ctrl_type, 0, wx.EXPAND, 0)

        grid_sizer_prelevement.Add(self.label_libelle, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prelevement.Add(self.ctrl_libelle, 0, wx.EXPAND, 0)

        grid_sizer_prelevement.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prelevement.Add(self.ctrl_montant, 0, 0, 0)

        grid_sizer_prelevement.Add(self.label_etat, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_etat = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_etat.Add(self.radio_etat_attente, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_etat.Add(self.radio_etat_valide, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_etat.Add(self.radio_etat_refus, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prelevement.Add(grid_sizer_etat, 1, wx.EXPAND, 0)

        grid_sizer_prelevement.Add(self.label_reglement, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prelevement.Add(self.ctrl_reglement, 0, 0, 0)

        grid_sizer_prelevement.AddGrowableCol(1)
        box_prelevement.Add(grid_sizer_prelevement, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_prelevement, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
    
    def OnChoixFamille(self, event):
        IDfamille = self.ctrl_famille.GetIDfamille() 
        if IDfamille == None :
            return
        DB = GestionDB.DB()
        req = """SELECT 
        prelevement_activation, prelevement_etab, prelevement_guichet, prelevement_numero, prelevement_cle, 
        prelevement_banque, prelevement_individu, prelevement_nom, individus.nom, individus.prenom
        FROM familles
        LEFT JOIN individus ON individus.IDindividu = familles.prelevement_individu
        WHERE IDfamille=%d;""" % IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 :
            return
        activation, etab, guichet, numero, cle, banque, IDindividu, nomIndividu, nomMembre, prenomMembre = listeDonnees[0]
        
        if etab != None : self.ctrl_code_etab.SetValue(etab)
        if guichet != None : self.ctrl_code_guichet.SetValue(guichet)
        if numero != None : self.ctrl_numero.SetValue(numero)
        if cle != None : self.ctrl_cle.SetValue(cle)
        if nomIndividu == None : nomIndividu = u""
        
        self.ctrl_banque.SetID(banque) 
        
        if IDindividu != None :
            titulaireCompte = u"%s %s" % (nomMembre, prenomMembre)
        else :
            titulaireCompte = nomIndividu
        self.ctrl_titulaire.SetValue(titulaireCompte)
        

    def OnSaisieRIB(self, event):
        if self.ControleRIB() == True :
            self.ctrl_controle.SetBitmap(self.image_valide)
        else :
            self.ctrl_controle.SetBitmap(self.image_nonvalide)
    
    def ControleRIB(self):
        etab = self.ctrl_code_etab.GetValue()
        guichet = self.ctrl_code_guichet.GetValue()
        numero = self.ctrl_numero.GetValue()
        cle = self.ctrl_cle.GetValue()
        bic = u"%s%s%s%s" % (etab, guichet, numero, cle)
        return UTILS_Prelevements.AlgoControleRIB(bic)
    
    def OnBoutonBanques(self, event):
        IDbanque = self.ctrl_banque.GetID()
        import DLG_Banques
        dlg = DLG_Banques.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_banque.MAJ() 
        self.ctrl_banque.SetID(IDbanque)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Prlvementautomatique1")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def Importation(self):
        """ Importation des données """
        if self.track == None :
            return
        
        self.ctrl_famille.SetIDfamille(self.track.IDfamille)

        if self.track.prelevement_etab != None : self.ctrl_code_etab.SetValue(self.track.prelevement_etab)
        if self.track.prelevement_guichet != None : self.ctrl_code_guichet.SetValue(self.track.prelevement_guichet)
        if self.track.prelevement_numero != None : self.ctrl_numero.SetValue(self.track.prelevement_numero)
        if self.track.prelevement_cle != None : self.ctrl_cle.SetValue(self.track.prelevement_cle)
        if self.track.prelevement_banque != None : self.ctrl_banque.SetID(self.track.prelevement_banque)
        
        self.ctrl_titulaire.SetValue(self.track.titulaire)
        
        if self.track.type == "manuel" : labelType = _(u"Saisie manuelle")
        elif self.track.type == "facture" : labelType = _(u"Facture")
        else : labelType = u""
        self.ctrl_type.SetLabel(labelType)
        
        self.ctrl_libelle.SetValue(self.track.libelle) 
        self.ctrl_montant.SetMontant(self.track.montant)
        
        if self.track.reglement == True :
            self.ctrl_reglement.SetLabel(_(u"Oui"))
        else :
            self.ctrl_reglement.SetLabel(_(u"Non"))
        
        if self.track.statut == "valide" : self.radio_etat_valide.SetValue(True)
        elif self.track.statut == "refus" : self.radio_etat_refus.SetValue(True)
        else : self.radio_etat_attente.SetValue(True)


    def OnBoutonOk(self, event):
        # Récupération des données
        track = self.GetTrack() 
        if track == False :
            return

        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetTrack(self):
        IDfamille = self.ctrl_famille.GetIDfamille()
        IDcompte_payeur = self.ctrl_famille.GetIDcompte_payeur()
        etab = self.ctrl_code_etab.GetValue()
        guichet = self.ctrl_code_guichet.GetValue()
        numero = self.ctrl_numero.GetValue()
        cle = self.ctrl_cle.GetValue()
        IDbanque = self.ctrl_banque.GetID()
        titulaire = self.ctrl_titulaire.GetValue()
        libelle = self.ctrl_libelle.GetValue() 
        montant = self.ctrl_montant.GetMontant()
        
        # Validation des données
        if IDfamille == None :
            dlg = wx.MessageDialog(self, _(u"Vous avez oublié de sélectionner une famille dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_famille.SetFocus()
            return False

        if self.ControleRIB() == False :
            dlg = wx.MessageDialog(self, _(u"Il est impossible d'activer le prélèvement :\nLes coordonnées bancaires ne sont pas valides !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_code_etab.SetFocus()
            return False

        if IDbanque == None :
            dlg = wx.MessageDialog(self, _(u"Il est impossible d'activer le prélèvement :\nVous n'avez sélectionné aucun établissement bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_banque.SetFocus()
            return False

        if titulaire == "" :
            dlg = wx.MessageDialog(self, _(u"Vous avez oublié de saisir un nom de titulaire pour le compte bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_titulaire.SetFocus()
            return False

        if libelle == "" :
            dlg = wx.MessageDialog(self, _(u"Vous avez oublié de saisir un libellé pour cette opération !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_libelle.SetFocus()
            return False

        if montant == None or montant == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Vous avez oublié de saisir un montant pour cette opération !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return False

        # MAJ du track
        track = self.track
        track.IDfamille = IDfamille
        track.InitNomsTitulaires() 
        track.IDcompte_payeur = IDcompte_payeur
        
        track.prelevement_etab = etab
        track.prelevement_guichet = guichet
        track.prelevement_numero = numero
        track.prelevement_cle = cle
        track.prelevement_banque = IDbanque
        track.titulaire = titulaire
        track.libelle = libelle
        track.montant = montant
        track.nomBanque = self.ctrl_banque.GetStringSelection()
        
        if self.ctrl_type.GetLabel() == _(u"Saisie manuelle") : track.type = "manuel"
        if self.ctrl_type.GetLabel() == _(u"Facture") : track.type = "facture"
        
        if self.radio_etat_attente.GetValue() == True : track.statut = "attente"
        if self.radio_etat_valide.GetValue() == True : track.statut = "valide"
        if self.radio_etat_refus.GetValue() == True : track.statut = "refus"
        
        return track
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
