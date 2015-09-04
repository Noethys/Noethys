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
import wx.html as html
import os
import sys
import GestionDB
import datetime
import Image
import cStringIO
import wx.propgrid as wxpg

import CTRL_Saisie_date
import UTILS_Dates
import OL_Modes_reglements
import OL_PES_pieces
import UTILS_Pes
import FonctionsPerso
import wx.lib.dialogs as dialogs
import wx.lib.agw.hyperlink as Hyperlink

import UTILS_Organisateur
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

from UTILS_Decimal import FloatToDecimal as FloatToDecimal


def Supprime_accent(texte):
    liste = [ (u"�", u"e"), (u"�", u"e"), (u"�", u"e"), (u"�", u"e"), (u"�", u"a"), (u"�", u"u"), (u"�", u"o"), (u"�", u"c"), (u"�", u"i"), (u"�", u"i"),]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte

def GetMoisStr(numMois, majuscules=False, sansAccents=False) :
    listeMois = (u"_", _(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
    nom = listeMois[numMois]
    if sansAccents == True : 
        nom = Supprime_accent(nom)
    if majuscules == True :
        nom = nom.upper() 
    return nom    


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



class CTRL_Parametres(wxpg.PropertyGrid) :
    def __init__(self, parent):
        wxpg.PropertyGrid.__init__(self, parent, -1, style=wxpg.PG_SPLITTER_AUTO_CENTER )
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
        couleurFond = "#dcf7d4"
        self.SetCaptionBackgroundColour(couleurFond)
##        self.SetMarginColour(couleurFond)
        self.Bind( wxpg.EVT_PG_CHANGED, self.OnPropGridChange )
        
        # Bordereau
        self.Append( wxpg.PropertyCategory(_(u"Bordereau")) )
        
        propriete = wxpg.IntProperty(label=_(u"Exercice"), name="exercice", value=datetime.date.today().year)
        propriete.SetHelpString(_(u"Saisissez l'ann�e de l'exercice")) 
        self.Append(propriete)
        self.SetPropertyEditor("exercice", "SpinCtrl")
        
        listeMois = [u"_", _(u"Janvier"), _(u"F�vrier"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Ao�t"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"D�cembre")]
        propriete = wxpg.EnumProperty(label=_(u"Mois"), name="mois", labels=listeMois, values=range(0, 13) , value=datetime.date.today().month)
        propriete.SetHelpString(_(u"S�lectionnez le mois")) 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"Objet"), name="objet_dette", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'objet du bordereau (Ex : 'Centre de Loisirs')")) 
        self.Append(propriete)

        # Dates
        self.Append( wxpg.PropertyCategory(_(u"Dates")) )
        
        propriete = wxpg.DateProperty(label=_(u"Date d'�mission"), name="date_emission", value=wx.DateTime_Now())
        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
        self.Append(propriete)
        
        propriete = wxpg.DateProperty(label=_(u"Date du pr�l�vement"), name="date_prelevement", value=wx.DateTime_Now())
        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
        self.Append(propriete)
        
        propriete = wxpg.DateProperty(label=_(u"Avis d'envoi"), name="date_envoi", value=wx.DateTime_Now())
        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
        self.Append(propriete)

        # Collectivit�
        self.Append( wxpg.PropertyCategory(_(u"Identification")) )
        
        propriete = wxpg.StringProperty(label=_(u"ID Bordereau"), name="id_bordereau", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'ID du bordereau")) 
        self.Append(propriete)
##        propriete.SetAttribute("Hint", _(u"Coucou !"))
##        self.SetPropertyCell("id_bordereau", 0, bitmap = wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        propriete = wxpg.StringProperty(label=_(u"ID Poste"), name="id_poste", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'ID du bordereau")) 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"ID Collectivit�"), name="id_collectivite", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'ID de la collectivit�")) 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"Code Collectivit�"), name="code_collectivite", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code Collectivit�")) 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"Code Budget"), name="code_budget", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code Budget")) 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"Code Produit Local"), name="code_prodloc", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code Produit Local")) 
        self.Append(propriete)

        # Libell�s
        self.Append( wxpg.PropertyCategory(_(u"Libell�s")) )

        propriete = wxpg.StringProperty(label=_(u"Objet de la pi�ce"), name="objet_piece", value=_(u"FACTURE_NUM{NUM_FACTURE}_{MOIS_LETTRES}_{ANNEE}"))
        propriete.SetHelpString(_(u"Saisissez l'objet de la pi�ce (en majuscules et sans accents). Vous pouvez personnaliser ce libell� gr�ce aux mots-cl�s suivants : {NOM_ORGANISATEUR} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Libell� du pr�l�vement"), name="prelevement_libelle", value=u"{NOM_ORGANISATEUR} - {OBJET_PIECE}")
        propriete.SetHelpString(_(u"Saisissez le libell� du pr�l�vement qui appara�tra sur le relev� de compte de la famille. Vous pouvez personnaliser ce libell� gr�ce aux mots-cl�s suivants : {NOM_ORGANISATEUR} {OBJET_PIECE} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
        self.Append(propriete)

        # R�glement automatique
        self.Append( wxpg.PropertyCategory(_(u"R�glement automatique")) )
        
        propriete = wxpg.BoolProperty(label="R�gler automatiquement", name="reglement_auto", value=False)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys cr�� un r�glement automatiquement pour les pr�l�vements")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        propriete = wxpg.EnumProperty(label=_(u"Compte � cr�diter"), name="IDcompte")
        propriete.SetHelpString(_(u"S�lectionnez le compte bancaire � cr�diter dans le cadre du r�glement automatique"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_comptes() 

        propriete = wxpg.EnumProperty(label=_(u"Mode de r�glement"), name="IDmode")
        propriete.SetHelpString(_(u"S�lectionnez le mode de r�glement � utiliser dans le cadre du r�glement automatique"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_modes() 
                            
                            
    def MAJ_comptes(self):
        DB = GestionDB.DB()
        req = """SELECT IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics
        FROM comptes_bancaires
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictComptes = {}
        choix = wxpg.PGChoices()
        for IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics in listeDonnees :
            self.dictComptes[IDcompte] = { 
                "nom" : nom, "numero" : numero, "defaut" : defaut,
                "raison" : raison, "code_etab" : code_etab, "code_guichet" : code_guichet, 
                "code_nne" : code_nne, "cle_rib" : cle_rib, "cle_iban" : cle_iban,
                "iban" : iban, "bic" : bic, "code_ics" : code_ics,
                }
            choix.Add(nom, IDcompte)
        propriete = self.GetPropertyByName("IDcompte")
        propriete.SetChoices(choix)
        self.RefreshProperty(propriete) 

    def MAJ_modes(self):
        DB = GestionDB.DB()
        req = """SELECT IDmode, label, numero_piece, nbre_chiffres, 
        frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label, image
        FROM modes_reglements
        ORDER BY label;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictModes = {}
        choix = wxpg.PGChoices()
        for IDmode, label, numero_piece, nbre_chiffres, frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label, image in listeDonnees :
            self.dictModes[IDmode] = { 
                "label" : label, "numero_piece" : numero_piece, "nbre_chiffres" : nbre_chiffres,
                "frais_gestion" : frais_gestion, "frais_montant" : frais_montant, "frais_pourcentage" : frais_pourcentage, 
                "frais_arrondi" : frais_arrondi, "frais_label" : frais_label, "image" : image,
                }
            bmp = OL_Modes_reglements.GetImage(image)
            choix.Add(label, bmp, IDmode)
        propriete = self.GetPropertyByName("IDmode")
        propriete.SetChoices(choix)
        self.RefreshProperty(propriete) 


    def OnBoutonParametres(self, propriete=None):
        ancienneValeur = propriete.GetValue() 
        if propriete.GetName() == "IDcompte" :
            import DLG_Comptes_bancaires
            dlg = DLG_Comptes_bancaires.Dialog(self)
            dlg.ShowModal()
            dlg.Destroy()
            self.MAJ_comptes() 
        if propriete.GetName() == "IDmode" :
            import DLG_Modes_reglements
            dlg = DLG_Modes_reglements.Dialog(self)
            dlg.ShowModal()
            dlg.Destroy()
            self.MAJ_modes() 
        try :
            propriete.SetValue(ancienneValeur)
        except :
            pass

    def OnPropGridChange(self, event):
        propriete = event.GetProperty()
        if propriete.GetName() == "reglement_auto" :
            self.parent.ctrl_pieces.reglement_auto = propriete.GetValue()

    
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Infos(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=32,  couleurFond=(255, 255, 255), style=0):
        html.HtmlWindow.__init__(self, parent, -1, style=style)#, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(3)
        self.SetMinSize((-1, hauteur))
        self.couleurFond = couleurFond
        font = self.parent.GetFont()
        self.SetFont(font)
        self.SetLabel(texte)
    
    def SetLabel(self, texte=""):
        self.SetPage(u"""<BODY><FONT SIZE=2 COLOR='#000000'>%s</FONT></BODY>""" % texte)
        self.SetBackgroundColour(self.couleurFond)
    

# ---------------------------------------------------------------------------------------------------------------------------------------

class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        
    def OnLeftLink(self, event):
        if self.URL == "selection_tout" :
            self.parent.ctrl_pieces.CocheTout() 
        if self.URL == "selection_rien" :
            self.parent.ctrl_pieces.CocheRien() 
        if self.URL == "etat_valide" :
            self.parent.ctrl_pieces.SetStatut("valide")
        if self.URL == "etat_attente" :
            self.parent.ctrl_pieces.SetStatut("attente")
        if self.URL == "etat_refus" :
            self.parent.ctrl_pieces.SetStatut("refus")
        if self.URL == "reglements_tout" :
            self.parent.ctrl_pieces.SetRegle(True)
        if self.URL == "reglements_rien" :
            self.parent.ctrl_pieces.SetRegle(False)
        if self.URL == "creer_mode" :
            self.parent.CreerMode()
        self.UpdateLink()
            
        

# ---------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDlot=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_pes_lot", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent  
        self.IDlot = IDlot 
        
        # G�n�ralit�s
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"Caract�ristiques"))
        
        self.label_nom = wx.StaticText(self, -1, _(u"Nom du lot :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.ctrl_nom.SetMinSize((230, -1))
        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_verrouillage = wx.StaticText(self, -1, _(u"Verrouillage :"))
        self.ctrl_verrouillage = wx.CheckBox(self, -1, u"")
        
        # Param�tres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Param�tres"))
        self.ctrl_parametres = CTRL_Parametres(self)

        # Pi�ces
        self.box_pieces_staticbox = wx.StaticBox(self, -1, _(u"Pi�ces"))
        
        self.ctrl_pieces = OL_PES_pieces.ListView(self, id=-1, IDlot=self.IDlot, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_pieces.SetMinSize((50, 50)) 
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        
        
        self.label_actions = wx.StaticText(self, -1, _(u"Actions sur pr�l�vements coch�s :"))

        self.hyper_etat_attente = Hyperlien(self, label=_(u"Attente"), infobulle=_(u"Cliquez ici pour mettre en attente les pr�l�vements coch�s"), URL="etat_attente")
        self.label_separation_1 = wx.StaticText(self, -1, u"|")
        self.hyper_etat_valide = Hyperlien(self, label=_(u"Valide"), infobulle=_(u"Cliquez ici pour valider les pr�l�vements coch�s"), URL="etat_valide")
        self.label_separation_2 = wx.StaticText(self, -1, u"|")
        self.hyper_etat_refus = Hyperlien(self, label=_(u"Refus"), infobulle=_(u"Cliquez ici pour refuser les pr�l�vements coch�s"), URL="etat_refus")

        self.hyper_reglements_tout = Hyperlien(self, label=_(u"R�gler"), infobulle=_(u"Cliquez ici pour r�gler les pr�l�vements coch�s"), URL="reglements_tout")
        self.label_separation_3 = wx.StaticText(self, -1, u"|")
        self.hyper_reglements_rien = Hyperlien(self, label=_(u"Ne pas r�gler"), infobulle=_(u"Cliquez ici pour ne pas r�gler les pr�l�vements coch�s"), URL="reglements_rien")


        self.hyper_selection_tout = Hyperlien(self, label=_(u"Tout cocher"), infobulle=_(u"Cliquez ici pour tout cocher la s�lection"), URL="selection_tout")
        self.label_separation_4 = wx.StaticText(self, -1, u"|")
        self.hyper_selection_rien = Hyperlien(self, label=_(u"Tout d�cocher"), infobulle=_(u"Cliquez ici pour tout d�cocher la s�lection"), URL="selection_rien")

        self.ctrl_totaux = CTRL_Infos(self, hauteur=40, couleurFond="#F0FBED" , style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.SUNKEN_BORDER)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fichier = CTRL_Bouton_image.CTRL(self, texte=_(u"G�n�rer un fichier PES Recette ORMC"), cheminImage="Images/32x32/Disk.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFichier, self.bouton_fichier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contr�les
        self.Importation() 
        
        self.tracks = OL_PES_pieces.GetTracks(self.IDlot)
        self.ctrl_pieces.MAJ(tracks=self.tracks) 
        self.ctrl_pieces.MAJtotaux() 

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un bordereau PES ORMC"))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez un nom pour ce bordereau (Ex : 'Janvier 2013', etc...). Nom interne � Noethys."))
        self.ctrl_verrouillage.SetToolTipString(_(u"Cochez cette case pour verrouiller le bordereau lorsqu'il a �t� communiqu� � la Tr�sorerie"))
        self.ctrl_observations.SetToolTipString(_(u"Saisissez ici des observations sur ce bordereau"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter une pi�ce"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la pi�ce s�lectionn�e dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour retirer la pi�ce s�lectionn�e dans la liste"))
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour afficher un aper�u avant impression de la liste des pi�ces"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste des pi�ces de ce bordereau"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fichier.SetToolTipString(_(u"Cliquez ici pour g�n�rer un fichier normalis� xml PES Recette ORMC destin� � votre tr�sorerie"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider les donn�es"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((900, 780))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
                
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # G�n�ralit�s
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        
        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_date = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_verrouillage, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_verrouillage, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_generalites.AddGrowableRow(1)        
        grid_sizer_haut.Add(box_generalites, 1, wx.EXPAND, 0)
        
        # Param�tres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        box_parametres.Add(self.ctrl_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(box_parametres, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Pi�ces
        box_pieces = wx.StaticBoxSizer(self.box_pieces_staticbox, wx.VERTICAL)
        grid_sizer_pieces = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_pieces.Add(self.ctrl_pieces, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons_liste = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_liste.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_liste.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_liste.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons_liste.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_boutons_liste.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons_liste.Add(self.bouton_imprimer, 0, 0, 0)
        
        grid_sizer_pieces.Add(grid_sizer_boutons_liste, 1, wx.EXPAND, 0)
        
        # Commandes
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=16, vgap=5, hgap=5)
        
        grid_sizer_commandes.Add(self.label_actions, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_commandes.Add((10, 10), 0, wx.EXPAND, 0)
        
        grid_sizer_commandes.Add(self.hyper_etat_attente, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.label_separation_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_etat_valide, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.label_separation_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_etat_refus, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_commandes.Add((10, 10), 0, wx.EXPAND, 0)
        
        grid_sizer_commandes.Add(self.hyper_reglements_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.label_separation_3, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_reglements_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_commandes.Add((10, 10), 0, wx.EXPAND, 0)
        
        grid_sizer_commandes.Add(self.hyper_selection_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.label_separation_4, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_selection_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_commandes.AddGrowableCol(10)
        
        grid_sizer_pieces.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_pieces.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_pieces.Add(self.ctrl_totaux, 0, wx.EXPAND, 0)
        grid_sizer_pieces.AddGrowableRow(0)
        grid_sizer_pieces.AddGrowableCol(0)
        box_pieces.Add(grid_sizer_pieces, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_pieces, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fichier, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
        
        wx.CallLater(0, self.Layout) # Contre pb d'affichage du wx.Choice
    
    def GetVerrouillage(self):
        return self.ctrl_verrouillage.GetValue() 
        
    def OnBoutonAjouter(self, event): 
        self.ctrl_pieces.Saisie_factures()
        
        # Cr�ation du menu contextuel
##        menuPop = wx.Menu()
##
##        # Item Ajouter
##        item = wx.MenuItem(menuPop, 10, _(u"Ajouter un pr�l�vement manuel"))
##        item.SetBitmap(wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG))
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.ctrl_pieces.Saisie_manuelle, id=10)
##
##        # Item Modifier
##        item = wx.MenuItem(menuPop, 20, _(u"Ajouter une ou plusieurs factures"))
##        item.SetBitmap(wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG))
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.ctrl_pieces.Saisie_factures, id=20)
##                
##        self.PopupMenu(menuPop)
##        menuPop.Destroy()

    def OnBoutonModifier(self, event): 
        self.ctrl_pieces.Modifier()

    def OnBoutonSupprimer(self, event): 
        self.ctrl_pieces.Supprimer()

    def OnBoutonApercu(self, event): 
        self.ctrl_pieces.Apercu()

    def OnBoutonImprimer(self, event): 
        self.ctrl_pieces.Imprimer()

    def OnBoutonAide(self, event=None): 
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def OnBoutonFichier(self, event): 
        """ G�n�ration d'un fichier normalis� """
        # Validation des donn�es
        if self.ValidationDonnees() == False :
            return

        # R�cup�ration des infos sur la remise
        remise_nom = Supprime_accent(self.ctrl_nom.GetValue())
        nom_fichier = remise_nom
        
        nomOrganisateur = UTILS_Organisateur.GetNom() 
        
        # R�cup�ration des transactions � effectuer
        montantTotal = FloatToDecimal(0.0)
        nbreTotal = 0
        listeAnomalies = []
        listePieces = []
        for track in self.ctrl_pieces.GetObjects() :
            montant = FloatToDecimal(track.montant)
            
            if track.analysePiece == False :
                listeAnomalies.append(u"%s : " % (track.libelle, track.analysePieceTexte))

            # Objet de la pi�ce
            objet_piece = self.ctrl_parametres.GetPropertyValue("objet_piece")
            objet_piece = Supprime_accent(objet_piece).upper() 
            objet_piece = objet_piece.replace("{NOM_ORGANISATEUR}", nomOrganisateur)
            objet_piece = objet_piece.replace("{NUM_FACTURE}", str(track.numero))
            objet_piece = objet_piece.replace("{LIBELLE_FACTURE}", track.libelle)
            objet_piece = objet_piece.replace("{MOIS}", str(self.ctrl_parametres.GetPropertyValue("mois")))
            objet_piece = objet_piece.replace("{MOIS_LETTRES}", GetMoisStr(self.ctrl_parametres.GetPropertyValue("mois"), majuscules=True, sansAccents=True))
            objet_piece = objet_piece.replace("{ANNEE}", str(self.ctrl_parametres.GetPropertyValue("exercice")))

            # Cr�ation du libell� du pr�l�vement
            prelevement_libelle = self.ctrl_parametres.GetPropertyValue("prelevement_libelle")
            prelevement_libelle = prelevement_libelle.replace("{NOM_ORGANISATEUR}", nomOrganisateur)
            prelevement_libelle = prelevement_libelle.replace("{LIBELLE_FACTURE}", track.libelle)
            prelevement_libelle = prelevement_libelle.replace("{NUM_FACTURE}", str(track.numero))
            prelevement_libelle = prelevement_libelle.replace("{MOIS}", str(self.ctrl_parametres.GetPropertyValue("mois")))
            prelevement_libelle = prelevement_libelle.replace("{MOIS_LETTRES}", GetMoisStr(self.ctrl_parametres.GetPropertyValue("mois"), majuscules=True, sansAccents=True))
            prelevement_libelle = prelevement_libelle.replace("{ANNEE}", str(self.ctrl_parametres.GetPropertyValue("exercice")))
            
            dictPiece = {
                "id_piece" : str(track.IDfacture),
                "objet_piece" : objet_piece,
                "num_dette" : str(track.numero),
                "montant" : str(montant),
                "sequence" : track.prelevement_sequence,
                "prelevement" : track.prelevement,
                "prelevement_date_mandat" : str(track.prelevement_date_mandat),
                "prelevement_rum" : track.prelevement_rum,
                "prelevement_bic" : track.prelevement_bic,
                "prelevement_iban" : track.prelevement_iban,
                "prelevement_titulaire" : track.prelevement_titulaire,
                "prelevement_libelle" : prelevement_libelle,
                "titulaire_civilite" : track.titulaireCivilite,
                "titulaire_nom" : track.titulaireNom,
                "titulaire_prenom" : track.titulairePrenom,
                "titulaire_rue" : track.titulaireRue,
                "titulaire_cp" : track.titulaireCP,
                "titulaire_ville" : track.titulaireVille,
                "idtiers_helios" : track.idtiers_helios,
                "natidtiers_helios" : track.natidtiers_helios,
                "reftiers_helios" : track.reftiers_helios,
                "cattiers_helios" : track.cattiers_helios,
                "natjur_helios" : track.natjur_helios,
                }        
            listePieces.append(dictPiece)
            montantTotal += montant
            nbreTotal += 1

        # M�morisation de tous les donn�es
        dictDonnees = {
            "nom_fichier" : nom_fichier,
            "date_emission" : self.ctrl_parametres.GetPropertyValue("date_emission").strftime("%Y-%m-%d"),
            "date_envoi" : self.ctrl_parametres.GetPropertyValue("date_envoi").strftime("%Y-%m-%d"),
            "date_prelevement" : self.ctrl_parametres.GetPropertyValue("date_prelevement").strftime("%Y-%m-%d"),
            "id_poste" : self.ctrl_parametres.GetPropertyValue("id_poste"),
            "id_collectivite" : self.ctrl_parametres.GetPropertyValue("id_collectivite"),
            "code_collectivite" : self.ctrl_parametres.GetPropertyValue("code_collectivite"),
            "code_budget" : self.ctrl_parametres.GetPropertyValue("code_budget"),
            "exercice" : str(self.ctrl_parametres.GetPropertyValue("exercice")),
            "mois" : str(self.ctrl_parametres.GetPropertyValue("mois")),
            "id_bordereau" : self.ctrl_parametres.GetPropertyValue("id_bordereau"),
            "montant_total" : str(montantTotal),
            "objet_dette" : self.ctrl_parametres.GetPropertyValue("objet_dette"),
            "code_prodloc" : self.ctrl_parametres.GetPropertyValue("code_prodloc"),
            "pieces" : listePieces,
            }
    
        if len(listeAnomalies) > 0 :
            import wx.lib.dialogs as dialogs
            message = "\n".join(listeAnomalies)
            dlg = dialogs.MultiMessageDialog(self, _(u"Le fichier XML PES Recette ORMC ne peut �tre g�n�r� en raison des anomalies suivantes :"), caption = _(u"G�n�ration impossible"), msg2=message, style = wx.ICON_ERROR | wx.OK, icon=None, btnLabels={wx.ID_OK : _(u"Fermer")})
            dlg.ShowModal() 
            dlg.Destroy() 
            return

        # G�n�ration du fichier XML
        doc = UTILS_Pes.GetXML(dictDonnees)
        xml = doc.toprettyxml(encoding="utf-8")
        
        # Demande � l'utilisateur le nom de fichier et le r�pertoire de destination
        wildcard = "Fichier XML (*.xml)|*.xml| All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez s�lectionner le r�pertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nom_fichier, 
            wildcard = wildcard, 
            style = wx.SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Le fichier de destination existe d�j� :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe d�j�. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Cr�ation du fichier texte
        f = open(cheminFichier, "w")
        try:
            f.write(doc.toxml(encoding="ISO-8859-1"))
        finally:
            f.close()

        # Confirmation de cr�ation du fichier et demande d'ouverture directe
        txtMessage = _(u"Le fichier xml PES Recette ORMC a �t� cr�� avec succ�s.\n\nSouhaitez-vous visualiser son contenu maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)
        
    def GetLabelParametres(self):
        """ Renvoie les param�tres pour impression """
        nom = self.ctrl_nom.GetValue()
        texte = _(u"Pr�l�vement : '%s'") % nom
        return texte
    
    def Importation(self):
        """ Importation des donn�es """
        if self.IDlot == None :
            # Donn�es du dernier lot
            DB = GestionDB.DB()
            req = """SELECT reglement_auto, IDcompte, IDmode, exercice, mois, objet_dette, date_emission, date_prelevement, date_envoi, id_bordereau, id_poste, id_collectivite, code_collectivite, code_budget, code_prodloc, prelevement_libelle, objet_piece
            FROM pes_lots
            ORDER BY IDlot;"""
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 :
                return
            reglement_auto, IDcompte, IDmode, exercice, mois, objet_dette, date_emission, date_prelevement, date_envoi, id_bordereau, id_poste, id_collectivite, code_collectivite, code_budget, code_prodloc, prelevement_libelle, objet_piece  = listeDonnees[-1]
            nom = u""
            verrouillage = False
            observations = u""

        else :
            # Importation
            DB = GestionDB.DB()
            req = """SELECT nom, verrouillage, observations, reglement_auto, IDcompte, IDmode, exercice, mois, objet_dette, date_emission, date_prelevement, date_envoi, id_bordereau, id_poste, id_collectivite, code_collectivite, code_budget, code_prodloc, prelevement_libelle, objet_piece 
            FROM pes_lots
            WHERE IDlot=%d
            ;""" % self.IDlot
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 :
                return
            nom, verrouillage, observations, reglement_auto, IDcompte, IDmode, exercice, mois, objet_dette, date_emission, date_prelevement, date_envoi, id_bordereau, id_poste, id_collectivite, code_collectivite, code_budget, code_prodloc, prelevement_libelle, objet_piece = listeDonnees[0]
        
        # Attribution des donn�es aux contr�les
        self.ctrl_nom.SetValue(nom)
        self.ctrl_verrouillage.SetValue(verrouillage)
        self.ctrl_observations.SetValue(observations)
        if reglement_auto == 1 :
            self.ctrl_pieces.reglement_auto = True
        if prelevement_libelle in ("", None):
            prelevement_libelle = u"{NOM_ORGANISATEUR} - {LIBELLE_FACTURE}"
        if objet_piece in ("", None):
            objet_piece = _(u"FACTURE_NUM{NUM_FACTURE}_{MOIS_LETTRES}_{ANNEE}")
            
            
        listeValeurs = [
            ("exercice", exercice),
            ("mois", mois),
            ("objet_dette", objet_dette),
            ("date_emission", UTILS_Dates.DateEngEnDateDD(date_emission)),
            ("date_prelevement", UTILS_Dates.DateEngEnDateDD(date_prelevement)),
            ("date_envoi", UTILS_Dates.DateEngEnDateDD(date_envoi)),
            ("id_bordereau", id_bordereau),
            ("id_poste", id_poste),
            ("id_collectivite", id_collectivite),
            ("code_collectivite", code_collectivite),
            ("code_budget", code_budget),
            ("code_prodloc", code_prodloc),
            ("reglement_auto", reglement_auto),
            ("IDcompte", IDcompte),
            ("IDmode", IDmode),
            ("prelevement_libelle", prelevement_libelle),
            ("objet_piece", objet_piece),
            ]
            
        for code, valeur in listeValeurs :
            self.ctrl_parametres.SetPropertyValue(code, valeur)
        
    
    def ValidationDonnees(self):
        """ V�rifie que les donn�es saisies sont exactes """
        # G�n�ralit�s
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de lot (Ex : 'Janvier 2013'...) !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
 
        for caract in nom :
            if caract in ("_",) :
                dlg = wx.MessageDialog(self, _(u"Le caract�re '%s' n'est pas autoris� dans le nom du bordereau !") % caract, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_nom.SetFocus() 
                return False
       
        # V�rifie que le nom n'est pas d�j� attribu�
        if self.IDlot == None :
            IDlotTemp = 0
        else :
            IDlotTemp = self.IDlot
        DB = GestionDB.DB()
        req = """SELECT IDlot, nom
        FROM pes_lots
        WHERE nom='%s' AND IDlot!=%d;""" % (nom, IDlotTemp)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce nom de bordereau a d�j� �t� attribu� � un autre bordereau.\n\nChaque bordereau doit avoir un nom unique. Changez le nom."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
        
        observations = self.ctrl_observations.GetValue()
        
        if self.ctrl_verrouillage.GetValue() == True :
            verrouillage = 1
        else :
            verrouillage = 0
        
##        if len(self.ctrl_pieces.GetObjects()) == 0 :
##            dlg = wx.MessageDialog(self, _(u"Vous devez inclure au moins une pi�ce dans ce bordereau.\n\nCliquez sur le bouton AJOUTER � droite de la liste des pi�ces..."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return False
            
        # R�cup�ration des donn�es du CTRL Param�tres
        exercice = self.ctrl_parametres.GetPropertyValue("exercice")
        mois = self.ctrl_parametres.GetPropertyValue("mois")
        objet_dette = self.ctrl_parametres.GetPropertyValue("objet_dette")
        date_emission = self.ctrl_parametres.GetPropertyValue("date_emission")
        date_prelevement = self.ctrl_parametres.GetPropertyValue("date_prelevement")
        date_envoi = self.ctrl_parametres.GetPropertyValue("date_envoi")
        id_bordereau = self.ctrl_parametres.GetPropertyValue("id_bordereau")
        id_poste = self.ctrl_parametres.GetPropertyValue("id_poste")
        id_collectivite = self.ctrl_parametres.GetPropertyValue("id_collectivite")
        code_collectivite = self.ctrl_parametres.GetPropertyValue("code_collectivite")
        code_budget = self.ctrl_parametres.GetPropertyValue("code_budget")
        code_prodloc = self.ctrl_parametres.GetPropertyValue("code_prodloc")
        reglement_auto = int(self.ctrl_parametres.GetPropertyValue("reglement_auto"))
        IDcompte = self.ctrl_parametres.GetPropertyValue("IDcompte")
        IDmode = self.ctrl_parametres.GetPropertyValue("IDmode")
        
        # V�rification du compte � cr�diter
        if reglement_auto == 1 :
            if IDcompte == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un compte � cr�diter !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if IDmode == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un mode de r�glement pour le r�glement automatique !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # V�rification des param�tres du bordereau
        listeVerifications = [
            (exercice, "exercice", _(u"l'ann�e de l'exercice")),
            (mois, "mois", _(u"le mois")),
            (objet_dette, "objet_dette", _(u"l'objet de la dette")),
            (date_emission, "date_emission", _(u"la date d'�mission")),
            (date_prelevement, "date_prelevement", _(u"la date souhait�e du pr�l�vement")),
            (date_envoi, "date_envoi", _(u"la date d'envoi")),
            (id_bordereau, "id_bordereau", _(u"l'ID bordereau")),
            (id_poste, "id_poste", _(u"l'ID poste")),
            (id_collectivite, "id_collectivite", _(u"l'ID collectivit�")),
            (code_collectivite, "code_collectivite", _(u"le Code Collectivit�")),
            (code_budget, "code_budget", _(u"le Code Bugdet")),
            (code_prodloc, "code_prodloc", _(u"le code Produit Local")),
            ]
            
        for donnee, code, label in listeVerifications :
            if donnee == None or donnee == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir %s dans les param�tres du bordereau !") % label, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if code == "id_bordereau" :
                try :
                    test = int(donnee) 
                except :
                    dlg = wx.MessageDialog(self, _(u"Vous devez saisir une valeur num�rique valide pour le param�tre de bordereau 'ID Bordereau' !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

            if code == "id_collectivite" :
                try :
                    test = int(donnee) 
                except :
                    dlg = wx.MessageDialog(self, _(u"Vous devez saisir une valeur num�rique valide pour le param�tre de bordereau 'ID Collectivit�' !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False



        # V�rification des pi�ces
        listeErreurs = []
        listeTemp1 = []
        for track in self.ctrl_pieces.GetObjects() :

            if track.analysePiece == False :
                listeErreurs.append(_(u"- Facture n�%s : %s") % (track.IDfacture, track.analysePieceTexte))
                
            # V�rifie qu'un OOFF ou un FRST n'est pas attribu� 2 fois � un seul mandat
            if track.prelevement == 1 :
                if track.prelevement_sequence in ("OOFF", "FRST") :
                    key = (track.prelevement_IDmandat, track.prelevement_sequence)
                    if key in listeTemp1 :
                        if track.prelevement_sequence == "OOFF" : 
                            listeErreurs.append(_(u"- Facture n�%s : Le mandat n�%s de type ponctuel a d�j� �t� utilis� une fois !") % (track.IDfacture, track.prelevement_IDmandat))
                        if track.prelevement_sequence == "FRST" : 
                            listeErreurs.append(_(u"- Facture n�%s : Mandat n�%s d�j� initialis�. La s�quence doit �tre d�finie sur 'RCUR' !") % (track.IDfacture, track.prelevement_IDmandat))
                    listeTemp1.append(key)
            
        if len(listeErreurs) > 0 :
            message1 = _(u"Le bordereau ne peut �tre valid� en raison des erreurs suivantes :")
            message2 = "\n".join(listeErreurs)
            dlg = dialogs.MultiMessageDialog(self, message1, caption=_(u"Erreur"), msg2=message2, style = wx.ICON_EXCLAMATION |wx.OK, icon=None, btnLabels={wx.ID_OK : _(u"Ok")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            return False

        return True
    
    
    def OnBoutonOk(self, event): 
        # Validation des donn�es
        if self.ValidationDonnees() == False :
            return
        
        if self.ctrl_verrouillage.GetValue() == False :
            dlg = wx.MessageDialog(self, _(u"Pour cl�turer le traitement d'un bordereau, vous devez valider ou refuser les pi�ces puis verrouiller le bordereau.\n\nSouhaitez-vous le faire maintenant ?"), _(u"Information"), wx.YES_NO|wx.CANCEL|wx.NO_DEFAULT|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_NO :
                return
            
        # R�cup�ration des donn�es
        nom = self.ctrl_nom.GetValue()
        observations = self.ctrl_observations.GetValue()
        if self.ctrl_verrouillage.GetValue() == True :
            verrouillage = 1
        else :
            verrouillage = 0
        
        exercice = self.ctrl_parametres.GetPropertyValue("exercice")
        mois = self.ctrl_parametres.GetPropertyValue("mois")
        objet_dette = self.ctrl_parametres.GetPropertyValue("objet_dette")
        date_emission = self.ctrl_parametres.GetPropertyValue("date_emission").strftime("%Y-%m-%d")
        date_prelevement = self.ctrl_parametres.GetPropertyValue("date_prelevement").strftime("%Y-%m-%d")
        date_envoi = self.ctrl_parametres.GetPropertyValue("date_envoi").strftime("%Y-%m-%d")
        id_bordereau = self.ctrl_parametres.GetPropertyValue("id_bordereau")
        id_poste = self.ctrl_parametres.GetPropertyValue("id_poste")
        id_collectivite = self.ctrl_parametres.GetPropertyValue("id_collectivite")
        code_collectivite = self.ctrl_parametres.GetPropertyValue("code_collectivite")
        code_budget = self.ctrl_parametres.GetPropertyValue("code_budget")
        code_prodloc = self.ctrl_parametres.GetPropertyValue("code_prodloc")
        reglement_auto = int(self.ctrl_parametres.GetPropertyValue("reglement_auto"))
        IDcompte = self.ctrl_parametres.GetPropertyValue("IDcompte")
        IDmode = self.ctrl_parametres.GetPropertyValue("IDmode")
        prelevement_libelle = self.ctrl_parametres.GetPropertyValue("prelevement_libelle")
        objet_piece = self.ctrl_parametres.GetPropertyValue("objet_piece")

        # Sauvegarde du lot
        listeDonnees = [
            ("nom", nom ),
            ("verrouillage", verrouillage),
            ("observations", observations),
            ("reglement_auto", reglement_auto),
            ("IDcompte", IDcompte),
            ("IDmode", IDmode),
            ("exercice", exercice),
            ("mois", mois),
            ("objet_dette", objet_dette),
            ("date_emission", date_emission),
            ("date_prelevement", date_prelevement),
            ("date_envoi", date_envoi),
            ("id_bordereau", id_bordereau),
            ("id_poste", id_poste),
            ("id_collectivite", id_collectivite),
            ("code_collectivite", code_collectivite),
            ("code_budget", code_budget),
            ("code_prodloc", code_prodloc),
            ("prelevement_libelle", prelevement_libelle),
            ("objet_piece", objet_piece),
            ]

        DB = GestionDB.DB()
        if self.IDlot == None :
            # Ajout
            self.IDlot = DB.ReqInsert("pes_lots", listeDonnees)
        else :
            # Modification
            DB.ReqMAJ("pes_lots", listeDonnees, "IDlot", self.IDlot)
        DB.Close() 
        
        # Sauvegarde des pr�l�vements du lot
        self.ctrl_pieces.Sauvegarde(IDlot=self.IDlot, datePrelevement=date_prelevement, IDcompte=IDcompte, IDmode=IDmode) 
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetIDlot(self):
        return self.IDlot

    def Assistant(self, filtres=[], nomLot=None):
        # Saisie du titre du lot
        if nomLot != None :
            self.ctrl_nom.SetValue(nomLot)       
        
        # Saisie des factures
        import CTRL_Liste_factures
        ctrl_factures = CTRL_Liste_factures.CTRL(self, filtres=filtres)
        ctrl_factures.ctrl_factures.CocheTout()
        tracksFactures = ctrl_factures.GetTracksCoches()
        ctrl_factures.Destroy()
        del ctrl_factures
        self.ctrl_pieces.AjoutFactures(tracksFactures)
        
        # Coche tous les pr�l�vements
        self.ctrl_pieces.CocheTout()
        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDlot=3)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
