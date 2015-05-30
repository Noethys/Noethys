#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import string

import CTRL_Saisie_adresse
import CTRL_Saisie_euros
import GestionDB
import UTILS_Titulaires
import UTILS_Prelevements

from UTILS_Mandats import CTRL_Sequence



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

class CTRL_Titulaire_helios(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDfamille = None
        self.dictDonnees = {}
        self.SetMinSize((100, -1))
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self, IDfamille=None):
        self.IDfamille = IDfamille
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        if self.IDfamille == None : return []
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
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDindividu, nom, prenom in listeDonnees :
            if prenom == None : prenom = ""
            nomIndividu = u"%s %s" % (nom, prenom)
            self.dictDonnees[index] = { "IDindividu" : IDindividu, "nomIndividu " : nomIndividu}
            listeItems.append(nomIndividu)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["IDindividu"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["IDindividu"]
    
            

# -----------------------------------------------------------------------------------------------------------------------



class Dialog(wx.Dialog):
    def __init__(self, parent, track=None, activeMontant=True):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.track = track
        
        self.SetTitle(_(u"Saisie d'une pièce"))
        
        # Famille
        self.box_famille_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_famille = wx.StaticText(self, -1, _(u"Famille :"))
        self.ctrl_famille = CTRL_Famille(self)
        
        self.label_titulaire_helios = wx.StaticText(self, -1, _(u"Titulaire Hélios :"))
        self.ctrl_titulaire_helios = CTRL_Titulaire_helios(self)

        # Pièce
        self.box_piece_staticbox = wx.StaticBox(self, -1, _(u"Pièce"))
        
        self.label_type = wx.StaticText(self, -1, _(u"Type :"))
        self.ctrl_type = wx.StaticText(self, -1, _(u"Saisie manuelle"))
        
        self.label_libelle = wx.StaticText(self, -1, _(u"Libellé :"))
        self.ctrl_libelle = wx.TextCtrl(self, -1, u"")

        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        if activeMontant == False :
            self.ctrl_montant.Enable(False) 

        # Prélèvement
        self.box_prelevement_staticbox = wx.StaticBox(self, -1, _(u"Prélèvement"))

        self.label_prelevement_actif = wx.StaticText(self, -1, _(u"Activé :"))
        self.ctrl_prelevement_actif = wx.CheckBox(self, -1, u"")

        self.label_sequence = wx.StaticText(self, -1, _(u"Séquence :"))
        self.ctrl_sequence = CTRL_Sequence(self, afficherAutomatique=False)
            
        self.label_etat = wx.StaticText(self, -1, _(u"Statut :"))
        self.radio_etat_attente = wx.RadioButton(self, -1, _(u"Attente"), style=wx.RB_GROUP)
        self.radio_etat_valide = wx.RadioButton(self, -1, _(u"Valide"))
        self.radio_etat_refus= wx.RadioButton(self, -1, _(u"Refus"))
        
        self.radio_etat_attente.Enable(False) 
        self.radio_etat_valide.Enable(False) 
        self.radio_etat_refus.Enable(False) 

        self.label_reglement = wx.StaticText(self, -1, _(u"Règlement :"))
        self.ctrl_reglement = wx.StaticText(self, -1, _(u"Non"))

        # IBAN
        self.box_rib_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées bancaires"))
        
        self.label_iban = wx.StaticText(self, -1, _(u"IBAN"))
        self.label_bic = wx.StaticText(self, -1, _(u"BIC"))
        self.ctrl_iban = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE)

        self.image_valide = wx.Bitmap(u"Images/16x16/Ok4.png", wx.BITMAP_TYPE_ANY)
        self.image_nonvalide = wx.Bitmap(u"Images/16x16/Interdit2.png", wx.BITMAP_TYPE_ANY)
        self.ctrl_controle = wx.StaticBitmap(self, -1, self.image_nonvalide)
        
        self.ctrl_bic = wx.TextCtrl(self, -1, u"", style=wx.TE_CENTRE)

        self.label_titulaire = wx.StaticText(self, -1, _(u"Titulaire du compte"))
        self.ctrl_titulaire = wx.TextCtrl(self, -1, u"")

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHOICE, self.OnChoixFamille, self.ctrl_famille)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_TEXT, self.OnSaisieIBAN, self.ctrl_iban)
        self.Bind(wx.EVT_TEXT, self.OnSaisieIBAN, self.ctrl_bic)

        # Init contrôles
        self.Importation() 
        self.OnSaisieIBAN(None)

    def __set_properties(self):
        self.ctrl_iban.SetMinSize((200, -1))
        self.ctrl_bic.SetMinSize((120, -1))
        self.ctrl_iban.SetToolTipString(_(u"Saisissez ici le numéro IBAN"))
        self.ctrl_bic.SetToolTipString(_(u"Saisissez ici le numéro BIC"))

        self.ctrl_type.SetForegroundColour(wx.Colour(150, 150, 150))
        self.ctrl_reglement.SetForegroundColour(wx.Colour(150, 150, 150))

        self.ctrl_famille.SetToolTipString(_(u"Sélectionnez ici la famille à débiter"))
        self.ctrl_titulaire_helios.SetToolTipString(_(u"Sélectionnez ici le titulaire Hélios de la famille"))
        self.ctrl_controle.SetToolTipString(_(u"Une coche verte apparaît si les coordonnées bancaires sont valides"))
        self.ctrl_prelevement_actif.SetToolTipString(_(u"Cochez cette case pour activer le prélèvement automatique sur cette recette"))
        
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        
        self.ctrl_sequence.SetToolTipString(_(u"Sélectionnez la séquence de l'opération (Si vous n'êtes pas sûr, laissez ce que Noethys a sélectionné automatiquement)"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)

        # Famille
        box_famille = wx.StaticBoxSizer(self.box_famille_staticbox, wx.VERTICAL)
        grid_sizer_famille = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_famille.Add(self.label_famille, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_famille.Add(self.ctrl_famille, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
        grid_sizer_famille.Add(self.label_titulaire_helios, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_famille.Add(self.ctrl_titulaire_helios, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
        grid_sizer_famille.AddGrowableCol(1)
        box_famille.Add(grid_sizer_famille, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_famille, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Pièce
        box_piece = wx.StaticBoxSizer(self.box_piece_staticbox, wx.VERTICAL)
        grid_sizer_piece = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_piece.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_piece.Add(self.ctrl_type, 0, wx.EXPAND, 0)
        grid_sizer_piece.Add(self.label_libelle, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_piece.Add(self.ctrl_libelle, 0, wx.EXPAND, 0)
        grid_sizer_piece.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_piece.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_piece.AddGrowableCol(1)
        box_piece.Add(grid_sizer_piece, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_piece, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Prélèvement
        box_prelevement = wx.StaticBoxSizer(self.box_prelevement_staticbox, wx.VERTICAL)
        grid_sizer_prelevement = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)

        grid_sizer_prelevement.Add(self.label_prelevement_actif, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prelevement.Add(self.ctrl_prelevement_actif, 0, wx.EXPAND, 0)

        grid_sizer_prelevement.Add(self.label_sequence, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prelevement.Add(self.ctrl_sequence, 0, wx.EXPAND, 0)

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

        # IBAN + BIC
        box_rib = wx.StaticBoxSizer(self.box_rib_staticbox, wx.VERTICAL)
        grid_sizer_rib = wx.FlexGridSizer(rows=2, cols=5, vgap=5, hgap=5)
        
        grid_sizer_iban = wx.FlexGridSizer(rows=2, cols=3, vgap=5, hgap=5)
        grid_sizer_iban.Add(self.label_iban, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_iban.Add(self.label_bic, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_iban.Add( (2, 2), 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_iban.Add(self.ctrl_iban, 0, wx.EXPAND, 0)
        grid_sizer_iban.Add(self.ctrl_bic, 0, wx.EXPAND, 0)
        grid_sizer_iban.Add(self.ctrl_controle, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_iban.AddGrowableCol(0)
        box_rib.Add(grid_sizer_iban, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_label_titulaire = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_label_titulaire.Add(self.label_titulaire, 0, wx.EXPAND|wx.LEFT|wx.BOTTOM, 8)
        box_rib.Add(grid_sizer_label_titulaire, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        box_rib.Add(self.ctrl_titulaire, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_base.Add(box_rib, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
                
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
        print "A CODER"
        return
##        IDfamille = self.ctrl_famille.GetIDfamille() 
##        if IDfamille == None :
##            return
##        DB = GestionDB.DB()
##        req = """SELECT 
##        prelevement_activation, prelevement_etab, prelevement_guichet, prelevement_numero, prelevement_cle, 
##        prelevement_banque, prelevement_individu, prelevement_nom, individus.nom, individus.prenom
##        FROM familles
##        LEFT JOIN individus ON individus.IDindividu = familles.prelevement_individu
##        WHERE IDfamille=%d;""" % IDfamille
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close()
##        if len(listeDonnees) == 0 :
##            return
##        activation, etab, guichet, numero, cle, banque, IDindividu, nomIndividu, nomMembre, prenomMembre = listeDonnees[0]
##        
##        if etab != None : self.ctrl_code_etab.SetValue(etab)
##        if guichet != None : self.ctrl_code_guichet.SetValue(guichet)
##        if numero != None : self.ctrl_numero.SetValue(numero)
##        if cle != None : self.ctrl_cle.SetValue(cle)
##        if nomIndividu == None : nomIndividu = u""
##        
##        self.ctrl_banque.SetID(banque) 
##        
##        if IDindividu != None :
##            titulaireCompte = u"%s %s" % (nomMembre, prenomMembre)
##        else :
##            titulaireCompte = nomIndividu
##        self.ctrl_titulaire.SetValue(titulaireCompte)
        

    def OnSaisieIBAN(self, event):
        self.ControleIBAN() 
        if event != None : event.Skip() 
    
    def ControleIBAN(self):
        iban = self.ctrl_iban.GetValue() 
        bic = self.ctrl_bic.GetValue() 
        if UTILS_Prelevements.ControleIBAN(iban) == True and UTILS_Prelevements.ControleBIC(bic) == True :
            self.ctrl_controle.SetBitmap(self.image_valide)
            return True
        else :
            self.ctrl_controle.SetBitmap(self.image_nonvalide)
            return False

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def Importation(self):
        """ Importation des données """
        if self.track == None :
            return
        
        self.ctrl_famille.SetIDfamille(self.track.IDfamille)
        self.ctrl_famille.Enable(False) 
        self.ctrl_titulaire_helios.MAJ(self.track.IDfamille)
        self.ctrl_titulaire_helios.SetID(self.track.titulaire_helios)
        
        self.ctrl_prelevement_actif.SetValue(self.track.prelevement)
        if self.track.prelevement_iban != None : self.ctrl_iban.SetValue(self.track.prelevement_iban)
        if self.track.prelevement_bic != None : self.ctrl_bic.SetValue(self.track.prelevement_bic)
        
        self.ctrl_titulaire.SetValue(self.track.prelevement_titulaire)
        
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
        
        if self.track.prelevement_statut == "valide" : self.radio_etat_valide.SetValue(True)
        elif self.track.prelevement_statut == "refus" : self.radio_etat_refus.SetValue(True)
        else : self.radio_etat_attente.SetValue(True)
        
        self.ctrl_sequence.SetCode(self.track.prelevement_sequence) 
        

    def OnBoutonOk(self, event):
        # Récupération des données
        track = self.GetTrack() 
        if track == False :
            return

        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetTrack(self):
        IDfamille = self.ctrl_famille.GetIDfamille()
        titulaire_helios = self.ctrl_titulaire_helios.GetID()
        IDcompte_payeur = self.ctrl_famille.GetIDcompte_payeur()
        iban = self.ctrl_iban.GetValue()
        bic = self.ctrl_bic.GetValue()
        titulaire = self.ctrl_titulaire.GetValue()
        libelle = self.ctrl_libelle.GetValue() 
        montant = self.ctrl_montant.GetMontant()
        sequence = self.ctrl_sequence.GetCode() 
        prelevement_actif = self.ctrl_prelevement_actif.GetValue() 
        
        # Validation des données
        if IDfamille == None :
            dlg = wx.MessageDialog(self, _(u"Vous avez oublié de sélectionner une famille dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_famille.SetFocus()
            return False
        
        if libelle == "" :
            dlg = wx.MessageDialog(self, _(u"Vous avez oublié de saisir un libellé pour cette opération !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_libelle.SetFocus()
            return False

        if montant == None :
            dlg = wx.MessageDialog(self, _(u"Vous avez oublié de saisir un montant pour cette opération !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return False

        if prelevement_actif in (True, 1) :
            
            if self.ControleIBAN() == False :
                dlg = wx.MessageDialog(self, _(u"Il est impossible d'activer le prélèvement :\nLes coordonnées bancaires ne sont pas valides !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_iban.SetFocus()
                return False

            if titulaire == "" :
                dlg = wx.MessageDialog(self, _(u"Vous avez oublié de saisir un nom de titulaire pour le compte bancaire !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_titulaire.SetFocus()
                return False


        # MAJ du track
        track = self.track
        track.IDfamille = IDfamille
        track.InitNomsTitulaires() 
        
        track.titulaire_helios = titulaire_helios
        track.InitTitulaireHelios()
        
        track.IDcompte_payeur = IDcompte_payeur
        
        track.prelevement = int(prelevement_actif)
        track.prelevement_iban = iban
        track.prelevement_bic = bic
        track.prelevement_titulaire = titulaire
        track.libelle = libelle
        track.montant = montant
        track.prelevement_sequence = sequence
        
        if self.ctrl_type.GetLabel() == _(u"Saisie manuelle") : track.type = "manuel"
        if self.ctrl_type.GetLabel() == _(u"Facture") : track.type = "facture"
        
        if self.radio_etat_attente.GetValue() == True : track.prelevement_statut = "attente"
        if self.radio_etat_valide.GetValue() == True : track.prelevement_statut = "valide"
        if self.radio_etat_refus.GetValue() == True : track.prelevement_statut = "refus"
        
        track.AnalysePiece() 
        
        return track
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
