#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import sys
import datetime
import wx.propgrid as wxpg

import GestionDB
import UTILS_Dates
import UTILS_Parametres
import copy



class EditeurComboBoxAvecBoutons(wxpg.PyChoiceEditor):
    def __init__(self):
        wxpg.PyChoiceEditor.__init__(self)

    def CreateControls(self, propGrid, property, pos, sz):
        # Create and populate buttons-subwindow
        buttons = wxpg.PGMultiButton(propGrid, sz)

        # Add two regular buttons
        buttons.AddBitmapButton(wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_PNG))
        buttons.GetButton(0).SetToolTipString(_(u"Cliquez ici pour acc�der � la gestion des param�tres"))
        
        # Create the 'primary' editor control (textctrl in this case)
        wnd = self.CallSuperMethod("CreateControls", propGrid, property, pos, buttons.GetPrimarySize())
        buttons.Finalize(propGrid, pos);
        self.buttons = buttons
        return (wnd, buttons)

    def OnEvent(self, propGrid, prop, ctrl, event):
        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            buttons = self.buttons
            evtId = event.GetId()
            if evtId == buttons.GetButtonId(0):
                propGrid.GetPanel().OnBoutonParametres(prop)

        return self.CallSuperMethod("OnEvent", propGrid, prop, ctrl, event)




# ----------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wxpg.PropertyGrid) :
    def __init__(self, parent, style=wxpg.PG_SPLITTER_AUTO_CENTER):
        wxpg.PropertyGrid.__init__(self, parent, -1, style=style)
        self.parent = parent
        
        # D�finition des �diteurs personnalis�s
        if not getattr(sys, '_PropGridEditorsRegistered', False):
            self.RegisterEditor(EditeurComboBoxAvecBoutons)
            # ensure we only do it once
            sys._PropGridEditorsRegistered = True
        
        # Remplissage des valeurs               
##        for nom, listeProprietes in self.listeDonnees :
##            self.Append( wxpg.PropertyCategory(nom) )
##        
##            for dictTemp in listeProprietes :
##                propriete = wxpg.IntProperty(label=dictTemp["label"], name=dictTemp["code"], value=dictTemp["valeur"])
##                self.Append(propriete)
##                self.SetPropertyAttribute(propriete, "Min", 0)
##                self.SetPropertyAttribute(propriete, "Max", 800)
##                self.SetPropertyEditor(propriete, "EditeurAvecBoutons")
        
##        self.SetVerticalSpacing(3) 
        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        
        couleurFond = "#e5ecf3"
        self.SetCaptionBackgroundColour(couleurFond)
        self.SetMarginColour(couleurFond)

        self.Bind( wxpg.EVT_PG_CHANGED, self.OnPropGridChange )
        
        # Remplissage du contr�le
        self.Remplissage() 
        
        # M�morisation des valeurs par d�faut
        self.dictValeursDefaut = self.GetPropertyValues()
        
        # Importation des valeurs
        self.Importation() 
        
##        # Bordereau
##        self.Append( wxpg.PropertyCategory(_(u"Bordereau")) )
##        
##        propriete = wxpg.IntProperty(label=_(u"Exercice"), name="exercice", value=datetime.date.today().year)
##        propriete.SetHelpString(_(u"Saisissez l'ann�e de l'exercice")) 
##        self.Append(propriete)
##        self.SetPropertyEditor("exercice", "SpinCtrl")
##        
##        listeMois = [_(u"Janvier"), _(u"F�vrier"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Ao�t"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"D�cembre")]
##        propriete = wxpg.EnumProperty(label=_(u"Mois"), name="mois", labels=listeMois, values=range(1, 13) , value=datetime.date.today().month)
##        propriete.SetHelpString(_(u"S�lectionnez le mois")) 
##        self.Append(propriete)
##        
##        propriete = wxpg.StringProperty(label=_(u"Objet"), name="objet_dette", value=u"")
##        propriete.SetHelpString(_(u"Saisissez l'objet du bordereau (Ex : 'Centre de Loisirs')")) 
##        self.Append(propriete)
##
##        # Dates
##        self.Append( wxpg.PropertyCategory(_(u"Dates")) )
##        
##        propriete = wxpg.DateProperty(label=_(u"Date d'�mission"), name="date_emission", value=wx.DateTime_Now())
##        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
##        self.Append(propriete)
##        
##        propriete = wxpg.DateProperty(label=_(u"Date du pr�l�vement"), name="date_prelevement", value=wx.DateTime_Now())
##        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
##        self.Append(propriete)
##        
##        propriete = wxpg.DateProperty(label=_(u"Avis d'envoi"), name="date_envoi", value=wx.DateTime_Now())
##        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
##        self.Append(propriete)
##
##        # Collectivit�
##        self.Append( wxpg.PropertyCategory(_(u"Identification")) )
##        
##        propriete = wxpg.StringProperty(label=_(u"ID Bordereau"), name="id_bordereau", value=u"")
##        propriete.SetHelpString(_(u"Saisissez l'ID du bordereau")) 
##        self.Append(propriete)
####        propriete.SetAttribute("Hint", _(u"Coucou !"))
####        self.SetPropertyCell("id_bordereau", 0, bitmap = wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
##        
##        propriete = wxpg.StringProperty(label=_(u"ID Poste"), name="id_poste", value=u"")
##        propriete.SetHelpString(_(u"Saisissez l'ID du bordereau")) 
##        self.Append(propriete)
##        
##        propriete = wxpg.StringProperty(label=_(u"ID Collectivit�"), name="id_collectivite", value=u"")
##        propriete.SetHelpString(_(u"Saisissez l'ID de la collectivit�")) 
##        self.Append(propriete)
##        
##        propriete = wxpg.StringProperty(label=_(u"Code Collectivit�"), name="code_collectivite", value=u"")
##        propriete.SetHelpString(_(u"Saisissez le code Collectivit�")) 
##        self.Append(propriete)
##        
##        propriete = wxpg.StringProperty(label=_(u"Code Budget"), name="code_budget", value=u"")
##        propriete.SetHelpString(_(u"Saisissez le code Budget")) 
##        self.Append(propriete)
##        
##        propriete = wxpg.StringProperty(label=_(u"Code Produit Local"), name="code_prodloc", value=u"")
##        propriete.SetHelpString(_(u"Saisissez le code Produit Local")) 
##        self.Append(propriete)
##
##        # Libell�s
##        self.Append( wxpg.PropertyCategory(_(u"Libell�s")) )
##
##        propriete = wxpg.StringProperty(label=_(u"Objet de la pi�ce"), name="objet_piece", value=_(u"FACTURE_NUM{NUM_FACTURE}_{MOIS_LETTRES}_{ANNEE}"))
##        propriete.SetHelpString(_(u"Saisissez l'objet de la pi�ce (en majuscules et sans accents). Vous pouvez personnaliser ce libell� gr�ce aux mots-cl�s suivants : {NOM_ORGANISATEUR} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
##        self.Append(propriete)
##
##        propriete = wxpg.StringProperty(label=_(u"Libell� du pr�l�vement"), name="prelevement_libelle", value=u"{NOM_ORGANISATEUR} - {OBJET_PIECE}")
##        propriete.SetHelpString(_(u"Saisissez le libell� du pr�l�vement qui appara�tra sur le relev� de compte de la famille. Vous pouvez personnaliser ce libell� gr�ce aux mots-cl�s suivants : {NOM_ORGANISATEUR} {OBJET_PIECE} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
##        self.Append(propriete)
##
##        # R�glement automatique
##        self.Append( wxpg.PropertyCategory(_(u"R�glement automatique")) )
##        
##        propriete = wxpg.BoolProperty(label="R�gler automatiquement", name="reglement_auto", value=False)
##        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys cr�� un r�glement automatiquement pour les pr�l�vements")) 
##        propriete.SetAttribute("UseCheckbox", True)
##        self.Append(propriete)
##        
##        propriete = wxpg.EnumProperty(label=_(u"Compte � cr�diter"), name="IDcompte")
##        propriete.SetHelpString(_(u"S�lectionnez le compte bancaire � cr�diter dans le cadre du r�glement automatique"))
##        propriete.SetEditor("EditeurComboBoxAvecBoutons")
##        self.Append(propriete)
##        self.MAJ_comptes() 
##
##        propriete = wxpg.EnumProperty(label=_(u"Mode de r�glement"), name="IDmode")
##        propriete.SetHelpString(_(u"S�lectionnez le mode de r�glement � utiliser dans le cadre du r�glement automatique"))
##        propriete.SetEditor("EditeurComboBoxAvecBoutons")
##        self.Append(propriete)
####        self.MAJ_modes() 
##                            
##                            
##    def MAJ_comptes(self):
##        DB = GestionDB.DB()
##        req = """SELECT IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics
##        FROM comptes_bancaires
##        ORDER BY nom;"""
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close()
##        self.dictComptes = {}
##        choix = wxpg.PGChoices()
##        for IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics in listeDonnees :
##            self.dictComptes[IDcompte] = { 
##                "nom" : nom, "numero" : numero, "defaut" : defaut,
##                "raison" : raison, "code_etab" : code_etab, "code_guichet" : code_guichet, 
##                "code_nne" : code_nne, "cle_rib" : cle_rib, "cle_iban" : cle_iban,
##                "iban" : iban, "bic" : bic, "code_ics" : code_ics,
##                }
##            choix.Add(nom, IDcompte)
##        propriete = self.GetPropertyByName("IDcompte")
##        propriete.SetChoices(choix)
##
##    def MAJ_modes(self):
##        DB = GestionDB.DB()
##        req = """SELECT IDmode, label, numero_piece, nbre_chiffres, 
##        frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label, image
##        FROM modes_reglements
##        ORDER BY label;"""
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close()
##        self.dictModes = {}
##        choix = wxpg.PGChoices()
##        for IDmode, label, numero_piece, nbre_chiffres, frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label, image in listeDonnees :
##            self.dictModes[IDmode] = { 
##                "label" : label, "numero_piece" : numero_piece, "nbre_chiffres" : nbre_chiffres,
##                "frais_gestion" : frais_gestion, "frais_montant" : frais_montant, "frais_pourcentage" : frais_pourcentage, 
##                "frais_arrondi" : frais_arrondi, "frais_label" : frais_label, "image" : image,
##                }
##            bmp = OL_Modes_reglements.GetImage(image)
##            choix.Add(label, bmp, IDmode)
##        propriete = self.GetPropertyByName("IDmode")
##        propriete.SetChoices(choix)
##
##
##    def OnBoutonParametres(self, propriete=None):
##        ancienneValeur = propriete.GetValue() 
##        if propriete.GetName() == "compte" :
##            import DLG_Comptes_bancaires
##            dlg = DLG_Comptes_bancaires.Dialog(self)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.MAJ_comptes() 
##        if propriete.GetName() == "mode" :
##            import DLG_Modes_reglements
##            dlg = DLG_Modes_reglements.Dialog(self)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.MAJ_modes() 
##        
##        propriete.SetValue(ancienneValeur)

    def OnPropGridChange(self, event):
        event.Skip() 
##        propriete = event.GetProperty()
##        if propriete.GetName() == "reglement_auto" :
##            self.parent.ctrl_pieces.reglement_auto = propriete.GetValue()
    
    def Reinitialisation(self):
        dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment r�initialiser tous les param�tres ?"), _(u"Param�tres par d�faut"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse == wx.ID_YES :
            for nom, valeur in self.dictValeursDefaut.iteritems() :
                propriete = self.GetPropertyByName(nom)
                if self.GetPropertyAttribute(propriete, "reinitialisation_interdite") != True :
                    propriete.SetValue(valeur)
    
##    def Sauvegarde(self):
##        # R�cup�ration des noms et valeurs par d�faut du contr�le
##        dictValeurs = copy.deepcopy(self.GetPropertyValues())
##        # Sauvegarde des valeurs
##        UTILS_Parametres.ParametresCategorie(mode="set", categorie="impression_facture", dictParametres=dictValeurs)



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Bouton_reinitialisation(wx.BitmapButton):
    def __init__(self, parent, ctrl_parametres=None):
        wx.BitmapButton.__init__(self, parent, -1, wx.Bitmap(u"Images/16x16/Actualiser.png", wx.BITMAP_TYPE_ANY))
        self.ctrl_parametres = ctrl_parametres
        self.SetToolTipString(_(u"Cliquez ici pour r�initialiser tous les param�tres"))
        self.Bind(wx.EVT_BUTTON, self.OnBouton)
    
    def OnBouton(self, event):
        self.ctrl_parametres.Reinitialisation() 

class Bouton_sauvegarde(wx.BitmapButton):
    def __init__(self, parent, ctrl_parametres=None):
        wx.BitmapButton.__init__(self, parent, -1, wx.Bitmap(u"Images/16x16/Sauvegarder.png", wx.BITMAP_TYPE_ANY))
        self.ctrl_parametres = ctrl_parametres
        self.SetToolTipString(_(u"Cliquez ici pour m�moriser tous les param�tres"))
        self.Bind(wx.EVT_BUTTON, self.OnBouton)
    
    def OnBouton(self, event):
        self.ctrl_parametres.Sauvegarde(forcer=True) 


# --------------------------------------- TESTS ----------------------------------------------------------------------------------------


class CTRL_TEST(CTRL) :
    def __init__(self, parent):
        CTRL.__init__(self, parent)
    
    def Remplissage(self):
        # Cat�gorie 
        self.Append( wxpg.PropertyCategory(_(u"M�morisation")) )
        
        # M�morisation des param�tres
        propriete = wxpg.EnumProperty(label=_(u"M�moriser les param�tres"), name="memoriser_parametres", labels=[_(u"Non"), _(u"Uniquement sur cet ordinateur"), _(u"Pour tous les ordinateurs")], values=[0, 1, 3] , value=3)
        propriete.SetHelpString(_(u"M�moriser les param�tres")) 
        self.Append(propriete)

        # R�pertoire de sauvegarde
        propriete = wxpg.DirProperty(label=_(u"R�pertoire pour copie unique"), name="repertoire_copie", value="")
        propriete.SetHelpString(_(u"Enregistrer une copie unique de chaque document dans le r�pertoire s�lectionn�")) 
        self.Append(propriete)

        # Cat�gorie 
        self.Append( wxpg.PropertyCategory(_(u"El�ments � afficher")) )
        
        # Afficher les coupons-r�ponse
        propriete = wxpg.BoolProperty(label="Afficher le coupon-r�ponse", name="coupon_reponse", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher un coupon-r�ponse dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        # Afficher les messages
        propriete = wxpg.BoolProperty(label="Afficher les messages", name="messages", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher les messages dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher le rappel des impay�s
        propriete = wxpg.BoolProperty(label="Afficher le rappel des impay�s", name="impayes", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher le rappel des impay�s dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Afficher les codes-barres
        propriete = wxpg.BoolProperty(label="Afficher les codes-barres", name="codes_barres", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher les codes-barres dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        # Afficher les avis de pr�l�vements
        propriete = wxpg.BoolProperty(label="Afficher les avis de pr�l�vements", name="avis_prelevements", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher les avis de pr�l�vements dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        # Cat�gorie 
        self.Append( wxpg.PropertyCategory(_(u"Titre")) )

        # Afficher le titre
        propriete = wxpg.BoolProperty(label="Afficher le titre", name="afficher_titre", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher le titre du le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Titre du document"), name="titre_document", value=_(u"Facture"))
        propriete.SetHelpString(_(u"Saisissez le titre du document (Par d�faut 'Facture')")) 
        self.Append(propriete)

        propriete = wxpg.IntProperty(label=_(u"Taille de texte du titre"), name="taille_texte_titre", value=19)
        propriete.SetHelpString(_(u"Saisissez la taille de texte du titre (29 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_titre", "SpinCtrl")
        
        propriete = wxpg.BoolProperty(label="Afficher la p�riode de facturation", name="afficher_periode", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez afficher la p�riode de facturation dans le document")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de la p�riode"), name="taille_texte_periode", value=8)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de la p�riode (8 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_periode", "SpinCtrl")

        # Cat�gorie 
        self.Append( wxpg.PropertyCategory(_(u"Tableau des prestations")) )

        # Affichage condens� ou d�taill�
        propriete = wxpg.EnumProperty(label=_(u"Affichage des prestations"), name="affichage_prestations", labels=[_(u"D�taill�"), _(u"Condens�")], values=[0, 1] , value=0)
        propriete.SetHelpString(_(u"S�lectionnez un type d'affichage")) 
        self.Append(propriete)

        # Intitul�s des prestations
        labels = [_(u"Intitul� original"), _(u"Intitul� original + �tat 'Absence injustifi�e'"), _(u"Nom du tarif"), _(u"Nom de l'activit�")]
        propriete = wxpg.EnumProperty(label=_(u"Intitul�s des prestations"), name="intitules", labels=labels, values=[0, 1, 2, 3] , value=0)
        propriete.SetHelpString(_(u"S�lectionnez le type d'intitul� � afficher pour les prestations")) 
        self.Append(propriete)
        
        # Couleur 1
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond 1"), name="couleur_fond_1", value=wx.Colour(255, 0, 0) )
        propriete.SetHelpString(_(u"S�lectionnez la couleur 1")) 
        self.Append(propriete)
        
        # Couleur 2
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond 2"), name="couleur_fond_2", value=wx.Colour(255, 0, 0) )
        propriete.SetHelpString(_(u"S�lectionnez la couleur 2")) 
        self.Append(propriete)
        
        # Largeur colonne Date
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Date (ou Qt�)"), name="largeur_colonne_date", value=50)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Date (50 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_date", "SpinCtrl")
        
        # Largeur colonne Montant HT
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Montant HT"), name="largeur_colonne_montant_ht", value=50)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Montant HT (50 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_montant_ht", "SpinCtrl")

        # Largeur colonne Montant TVA
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Montant TVA"), name="largeur_colonne_montant_tva", value=50)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Montant TVA (50 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_montant_tva", "SpinCtrl")

        # Largeur colonne Montant TTC
        propriete = wxpg.IntProperty(label=_(u"Largeur de la colonne Montant TTC"), name="largeur_colonne_montant_ttc", value=70)
        propriete.SetHelpString(_(u"Saisissez la largeur de la colonne Montant TTC (70 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("largeur_colonne_montant_ttc", "SpinCtrl")
        
        # Taille de texte du nom de l'individu
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de l'individu"), name="taille_texte_individu", value=9)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de l'individu (9 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_individu", "SpinCtrl")

        # Taille de texte du nom de l'activit�
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de l'activit�"), name="taille_texte_activite", value=6)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de l'activit� (6 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_activite", "SpinCtrl")

        # Taille de texte des noms de colonnes
        propriete = wxpg.IntProperty(label=_(u"Taille de texte des noms de colonnes"), name="taille_texte_noms_colonnes", value=5)
        propriete.SetHelpString(_(u"Saisissez la taille de texte des noms de colonnes (5 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_noms_colonnes", "SpinCtrl")

        # Taille de texte des prestations
        propriete = wxpg.IntProperty(label=_(u"Taille de texte de des prestations"), name="taille_texte_prestation", value=7)
        propriete.SetHelpString(_(u"Saisissez la taille de texte des prestations (7 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_prestation", "SpinCtrl")
        
        # Cat�gorie 
        self.Append( wxpg.PropertyCategory(_(u"Autres textes")) )

        propriete = wxpg.LongStringProperty(label=_(u"Texte d'introduction"), name="texte_introduction", value=u"")
        propriete.SetHelpString(_(u"Saisissez un texte d'introduction (Aucun par d�faut)")) 
        self.Append(propriete)

        propriete = wxpg.IntProperty(label=_(u"Taille de texte d'introduction"), name="taille_texte_introduction", value=9)
        propriete.SetHelpString(_(u"Saisissez la taille de texte d'introduction (9 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_introduction", "SpinCtrl")

        propriete = wxpg.LongStringProperty(label=_(u"Texte de conclusion"), name="texte_conclusion", value=u"")
        propriete.SetHelpString(_(u"Saisissez un texte de conclusion (Aucun par d�faut)")) 
        self.Append(propriete)

        propriete = wxpg.IntProperty(label=_(u"Taille de texte de conclusion"), name="taille_texte_conclusion", value=9)
        propriete.SetHelpString(_(u"Saisissez la taille de texte de conclusion (9 par d�faut)")) 
        self.Append(propriete)
        self.SetPropertyEditor("taille_texte_conclusion", "SpinCtrl")
        
    def Importation(self):
        """ Importation des valeurs dans le contr�le """
        # R�cup�ration des noms et valeurs par d�faut du contr�le
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
##        for nom, valeur in dictValeurs.iteritems() :
##            print (nom, valeur, str(type(valeur)))
        # Recherche les param�tres m�moris�s
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="impression_facture", dictParametres=dictValeurs)
        # Envoie les param�tres dans le contr�le
        for nom, valeur in dictParametres.iteritems() :
            propriete = self.GetPropertyByName(nom)
            print propriete
            ancienneValeur = propriete.GetValue() 
            propriete.SetValue(valeur)
    
    def Sauvegarde(self):
        """ M�morisation des valeurs du contr�le """
        # R�cup�ration des noms et valeurs par d�faut du contr�le
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        # Sauvegarde des valeurs
        UTILS_Parametres.ParametresCategorie(mode="set", categorie="impression_facture", dictParametres=dictValeurs)
        
        
        
        
        
    def GetDictValeurs(self) :
        return self.GetPropertyValues()
        

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL_TEST(panel)
        self.boutonTest = wx.Button(panel, -1, _(u"Bouton de test"))
        self.bouton_reinit = Bouton_reinitialisation(panel, self.ctrl)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_reinit, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        self.ctrl.Sauvegarde() 


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 600))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

