#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
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
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from UTILS_Decimal import FloatToDecimal as FloatToDecimal


def Supprime_accent(texte):
    liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"),]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte

def GetMoisStr(numMois, majuscules=False, sansAccents=False) :
    listeMois = (u"_", u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
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
        buttons.GetButton(0).SetToolTipString(u"Cliquez ici pour accéder à la gestion des paramètres")
        
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
        
        # Définition des éditeurs personnalisés
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
        self.Append( wxpg.PropertyCategory(u"Bordereau") )
        
        propriete = wxpg.IntProperty(label=u"Exercice", name="exercice", value=datetime.date.today().year)
        propriete.SetHelpString(u"Saisissez l'année de l'exercice") 
        self.Append(propriete)
        self.SetPropertyEditor("exercice", "SpinCtrl")
        
        listeMois = [u"_", u"Janvier", u"Février", u"Mars", u"Avril", u"Mai", u"Juin", u"Juillet", u"Août", u"Septembre", u"Octobre", u"Novembre", u"Décembre"]
        propriete = wxpg.EnumProperty(label=u"Mois", name="mois", labels=listeMois, values=range(0, 13) , value=datetime.date.today().month)
        propriete.SetHelpString(u"Sélectionnez le mois") 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=u"Objet", name="objet_dette", value=u"")
        propriete.SetHelpString(u"Saisissez l'objet du bordereau (Ex : 'Centre de Loisirs')") 
        self.Append(propriete)

        # Dates
        self.Append( wxpg.PropertyCategory(u"Dates") )
        
        propriete = wxpg.DateProperty(label=u"Date d'émission", name="date_emission", value=wx.DateTime_Now())
        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
        self.Append(propriete)
        
        propriete = wxpg.DateProperty(label=u"Date du prélèvement", name="date_prelevement", value=wx.DateTime_Now())
        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
        self.Append(propriete)
        
        propriete = wxpg.DateProperty(label=u"Avis d'envoi", name="date_envoi", value=wx.DateTime_Now())
        propriete.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN|wx.DP_SHOWCENTURY )
        self.Append(propriete)

        # Collectivité
        self.Append( wxpg.PropertyCategory(u"Identification") )
        
        propriete = wxpg.StringProperty(label=u"ID Bordereau", name="id_bordereau", value=u"")
        propriete.SetHelpString(u"Saisissez l'ID du bordereau") 
        self.Append(propriete)
##        propriete.SetAttribute("Hint", u"Coucou !")
##        self.SetPropertyCell("id_bordereau", 0, bitmap = wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        propriete = wxpg.StringProperty(label=u"ID Poste", name="id_poste", value=u"")
        propriete.SetHelpString(u"Saisissez l'ID du bordereau") 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=u"ID Collectivité", name="id_collectivite", value=u"")
        propriete.SetHelpString(u"Saisissez l'ID de la collectivité") 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=u"Code Collectivité", name="code_collectivite", value=u"")
        propriete.SetHelpString(u"Saisissez le code Collectivité") 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=u"Code Budget", name="code_budget", value=u"")
        propriete.SetHelpString(u"Saisissez le code Budget") 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=u"Code Produit Local", name="code_prodloc", value=u"")
        propriete.SetHelpString(u"Saisissez le code Produit Local") 
        self.Append(propriete)

        # Libellés
        self.Append( wxpg.PropertyCategory(u"Libellés") )

        propriete = wxpg.StringProperty(label=u"Objet de la pièce", name="objet_piece", value=u"FACTURE_NUM{NUM_FACTURE}_{MOIS_LETTRES}_{ANNEE}")
        propriete.SetHelpString(u"Saisissez l'objet de la pièce (en majuscules et sans accents). Vous pouvez personnaliser ce libellé grâce aux mots-clés suivants : {NOM_ORGANISATEUR} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.") 
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=u"Libellé du prélèvement", name="prelevement_libelle", value=u"{NOM_ORGANISATEUR} - {OBJET_PIECE}")
        propriete.SetHelpString(u"Saisissez le libellé du prélèvement qui apparaîtra sur le relevé de compte de la famille. Vous pouvez personnaliser ce libellé grâce aux mots-clés suivants : {NOM_ORGANISATEUR} {OBJET_PIECE} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.") 
        self.Append(propriete)

        # Règlement automatique
        self.Append( wxpg.PropertyCategory(u"Règlement automatique") )
        
        propriete = wxpg.BoolProperty(label="Régler automatiquement", name="reglement_auto", value=False)
        propriete.SetHelpString(u"Cochez cette case si vous souhaitez que Noethys créé un règlement automatiquement pour les prélèvements") 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        propriete = wxpg.EnumProperty(label=u"Compte à créditer", name="IDcompte")
        propriete.SetHelpString(u"Sélectionnez le compte bancaire à créditer dans le cadre du règlement automatique")
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_comptes() 

        propriete = wxpg.EnumProperty(label=u"Mode de règlement", name="IDmode")
        propriete.SetHelpString(u"Sélectionnez le mode de règlement à utiliser dans le cadre du règlement automatique")
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
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, -1, u"Caractéristiques")
        
        self.label_nom = wx.StaticText(self, -1, u"Nom du lot :")
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.ctrl_nom.SetMinSize((230, -1))
        self.label_observations = wx.StaticText(self, -1, u"Observations :")
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_verrouillage = wx.StaticText(self, -1, u"Verrouillage :")
        self.ctrl_verrouillage = wx.CheckBox(self, -1, u"")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, u"Paramètres")
        self.ctrl_parametres = CTRL_Parametres(self)

        # Pièces
        self.box_pieces_staticbox = wx.StaticBox(self, -1, u"Pièces")
        
        self.ctrl_pieces = OL_PES_pieces.ListView(self, id=-1, IDlot=self.IDlot, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_pieces.SetMinSize((50, 50)) 
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        
        
        self.label_actions = wx.StaticText(self, -1, u"Actions sur prélèvements cochés :")

        self.hyper_etat_attente = Hyperlien(self, label=u"Attente", infobulle=u"Cliquez ici pour mettre en attente les prélèvements cochés", URL="etat_attente")
        self.label_separation_1 = wx.StaticText(self, -1, u"|")
        self.hyper_etat_valide = Hyperlien(self, label=u"Valide", infobulle=u"Cliquez ici pour valider les prélèvements cochés", URL="etat_valide")
        self.label_separation_2 = wx.StaticText(self, -1, u"|")
        self.hyper_etat_refus = Hyperlien(self, label=u"Refus", infobulle=u"Cliquez ici pour refuser les prélèvements cochés", URL="etat_refus")

        self.hyper_reglements_tout = Hyperlien(self, label=u"Régler", infobulle=u"Cliquez ici pour régler les prélèvements cochés", URL="reglements_tout")
        self.label_separation_3 = wx.StaticText(self, -1, u"|")
        self.hyper_reglements_rien = Hyperlien(self, label=u"Ne pas régler", infobulle=u"Cliquez ici pour ne pas régler les prélèvements cochés", URL="reglements_rien")


        self.hyper_selection_tout = Hyperlien(self, label=u"Tout cocher", infobulle=u"Cliquez ici pour tout cocher la sélection", URL="selection_tout")
        self.label_separation_4 = wx.StaticText(self, -1, u"|")
        self.hyper_selection_rien = Hyperlien(self, label=u"Tout décocher", infobulle=u"Cliquez ici pour tout décocher la sélection", URL="selection_rien")

        self.ctrl_totaux = CTRL_Infos(self, hauteur=40, couleurFond="#F0FBED" , style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.SUNKEN_BORDER)

        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fichier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Fichier_pes_ormc.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

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
        
        # Init contrôles
        self.Importation() 
        
        self.tracks = OL_PES_pieces.GetTracks(self.IDlot)
        self.ctrl_pieces.MAJ(tracks=self.tracks) 
        self.ctrl_pieces.MAJtotaux() 

    def __set_properties(self):
        self.SetTitle(u"Saisie d'un bordereau PES ORMC")
        self.ctrl_nom.SetToolTipString(u"Saisissez un nom pour ce bordereau (Ex : 'Janvier 2013', etc...). Nom interne à Noethys.")
        self.ctrl_verrouillage.SetToolTipString(u"Cochez cette case pour verrouiller le bordereau lorsqu'il a été communiqué à la Trésorerie")
        self.ctrl_observations.SetToolTipString(u"Saisissez ici des observations sur ce bordereau")
        self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour ajouter une pièce")
        self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier la pièce sélectionnée dans la liste")
        self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour retirer la pièce sélectionnée dans la liste")
        self.bouton_apercu.SetToolTipString(u"Cliquez ici pour afficher un aperçu avant impression de la liste des pièces")
        self.bouton_imprimer.SetToolTipString(u"Cliquez ici pour imprimer la liste des pièces de ce bordereau")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_fichier.SetToolTipString(u"Cliquez ici pour générer un fichier normalisé xml PES Recette ORMC destiné à votre trésorerie")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider les données")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((900, 780))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
                
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Généralités
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
        
        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        box_parametres.Add(self.ctrl_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(box_parametres, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Pièces
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
        
        # Création du menu contextuel
##        menuPop = wx.Menu()
##
##        # Item Ajouter
##        item = wx.MenuItem(menuPop, 10, u"Ajouter un prélèvement manuel")
##        item.SetBitmap(wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG))
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.ctrl_pieces.Saisie_manuelle, id=10)
##
##        # Item Modifier
##        item = wx.MenuItem(menuPop, 20, u"Ajouter une ou plusieurs factures")
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
        """ Génération d'un fichier normalisé """
        # Validation des données
        if self.ValidationDonnees() == False :
            return

        # Récupération des infos sur la remise
        remise_nom = Supprime_accent(self.ctrl_nom.GetValue())
        nom_fichier = remise_nom
        
        nomOrganisateur = UTILS_Organisateur.GetNom() 
        
        # Récupération des transactions à effectuer
        montantTotal = FloatToDecimal(0.0)
        nbreTotal = 0
        listeAnomalies = []
        listePieces = []
        for track in self.ctrl_pieces.GetObjects() :
            montant = FloatToDecimal(track.montant)
            
            if track.analysePiece == False :
                listeAnomalies.append(u"%s : " % (track.libelle, track.analysePieceTexte))

            # Objet de la pièce
            objet_piece = self.ctrl_parametres.GetPropertyValue("objet_piece")
            objet_piece = Supprime_accent(objet_piece).upper() 
            objet_piece = objet_piece.replace("{NOM_ORGANISATEUR}", nomOrganisateur)
            objet_piece = objet_piece.replace("{NUM_FACTURE}", str(track.numero))
            objet_piece = objet_piece.replace("{LIBELLE_FACTURE}", track.libelle)
            objet_piece = objet_piece.replace("{MOIS}", str(self.ctrl_parametres.GetPropertyValue("mois")))
            objet_piece = objet_piece.replace("{MOIS_LETTRES}", GetMoisStr(self.ctrl_parametres.GetPropertyValue("mois"), majuscules=True, sansAccents=True))
            objet_piece = objet_piece.replace("{ANNEE}", str(self.ctrl_parametres.GetPropertyValue("exercice")))

            # Création du libellé du prélèvement
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
                }        
            listePieces.append(dictPiece)
            montantTotal += montant
            nbreTotal += 1

        # Mémorisation de tous les données
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
            dlg = dialogs.MultiMessageDialog(self, u"Le fichier XML PES Recette ORMC ne peut être généré en raison des anomalies suivantes :", caption = u"Génération impossible", msg2=message, style = wx.ICON_ERROR | wx.OK, icon=None, btnLabels={wx.ID_OK : u"Fermer"})
            dlg.ShowModal() 
            dlg.Destroy() 
            return

        # Génération du fichier XML
        doc = UTILS_Pes.GetXML(dictDonnees)
        xml = doc.toprettyxml(encoding="utf-8")
        
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        wildcard = "Fichier XML (*.xml)|*.xml| All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = u"Veuillez sélectionner le répertoire de destination et le nom du fichier", defaultDir=cheminDefaut, 
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
        
        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?", "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Création du fichier texte
        f = open(cheminFichier, "w")
        try:
            f.write(doc.toxml(encoding="ISO-8859-1"))
        finally:
            f.close()

        # Confirmation de création du fichier et demande d'ouverture directe
        txtMessage = u"Le fichier xml PES Recette ORMC a été créé avec succès.\n\nSouhaitez-vous visualiser son contenu maintenant ?"
        dlgConfirm = wx.MessageDialog(None, txtMessage, u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)
        
    def GetLabelParametres(self):
        """ Renvoie les paramètres pour impression """
        nom = self.ctrl_nom.GetValue()
        texte = u"Prélèvement : '%s'" % nom
        return texte
    
    def Importation(self):
        """ Importation des données """
        if self.IDlot == None :
            # Données du dernier lot
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
        
        # Attribution des données aux contrôles
        self.ctrl_nom.SetValue(nom)
        self.ctrl_verrouillage.SetValue(verrouillage)
        self.ctrl_observations.SetValue(observations)
        if reglement_auto == 1 :
            self.ctrl_pieces.reglement_auto = True
        if prelevement_libelle in ("", None):
            prelevement_libelle = u"{NOM_ORGANISATEUR} - {LIBELLE_FACTURE}"
        if objet_piece in ("", None):
            objet_piece = u"FACTURE_NUM{NUM_FACTURE}_{MOIS_LETTRES}_{ANNEE}"
            
            
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
        """ Vérifie que les données saisies sont exactes """
        # Généralités
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom de lot (Ex : 'Janvier 2013'...) !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
 
        for caract in nom :
            if caract in ("_",) :
                dlg = wx.MessageDialog(self, u"Le caractère '%s' n'est pas autorisé dans le nom du bordereau !" % caract, u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_nom.SetFocus() 
                return False
       
        # Vérifie que le nom n'est pas déjà attribué
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
            dlg = wx.MessageDialog(self, u"Ce nom de bordereau a déjà été attribué à un autre bordereau.\n\nChaque bordereau doit avoir un nom unique. Changez le nom.", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
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
##            dlg = wx.MessageDialog(self, u"Vous devez inclure au moins une pièce dans ce bordereau.\n\nCliquez sur le bouton AJOUTER à droite de la liste des pièces...", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return False
            
        # Récupération des données du CTRL Paramètres
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
        
        # Vérification du compte à créditer
        if reglement_auto == 1 :
            if IDcompte == None :
                dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un compte à créditer !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if IDmode == None :
                dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un mode de règlement pour le règlement automatique !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Vérification des paramètres du bordereau
        listeVerifications = [
            (exercice, "exercice", u"l'année de l'exercice"),
            (mois, "mois", u"le mois"),
            (objet_dette, "objet_dette", u"l'objet de la dette"),
            (date_emission, "date_emission", u"la date d'émission"),
            (date_prelevement, "date_prelevement", u"la date souhaitée du prélèvement"),
            (date_envoi, "date_envoi", u"la date d'envoi"),
            (id_bordereau, "id_bordereau", u"l'ID bordereau"),
            (id_poste, "id_poste", u"l'ID poste"),
            (id_collectivite, "id_collectivite", u"l'ID collectivité"),
            (code_collectivite, "code_collectivite", u"le Code Collectivité"),
            (code_budget, "code_budget", u"le Code Bugdet"),
            (code_prodloc, "code_prodloc", u"le code Produit Local"),
            ]
            
        for donnee, code, label in listeVerifications :
            if donnee == None or donnee == "" :
                dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir %s dans les paramètres du bordereau !" % label, u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if code == "id_bordereau" :
                try :
                    test = int(donnee) 
                except :
                    dlg = wx.MessageDialog(self, u"Vous devez saisir une valeur numérique valide pour le paramètre de bordereau 'ID Bordereau' !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

            if code == "id_collectivite" :
                try :
                    test = int(donnee) 
                except :
                    dlg = wx.MessageDialog(self, u"Vous devez saisir une valeur numérique valide pour le paramètre de bordereau 'ID Collectivité' !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False



        # Vérification des pièces
        listeErreurs = []
        listeTemp1 = []
        for track in self.ctrl_pieces.GetObjects() :

            if track.analysePiece == False :
                listeErreurs.append(u"- Facture n°%s : %s" % (track.IDfacture, track.analysePieceTexte))
                
            # Vérifie qu'un OOFF ou un FRST n'est pas attribué 2 fois à un seul mandat
            if track.prelevement == 1 :
                if track.prelevement_sequence in ("OOFF", "FRST") :
                    key = (track.prelevement_IDmandat, track.prelevement_sequence)
                    if key in listeTemp1 :
                        if track.prelevement_sequence == "OOFF" : 
                            listeErreurs.append(u"- Facture n°%s : Le mandat n°%s de type ponctuel a déjà été utilisé une fois !" % (track.IDfacture, track.prelevement_IDmandat))
                        if track.prelevement_sequence == "FRST" : 
                            listeErreurs.append(u"- Facture n°%s : Mandat n°%s déjà initialisé. La séquence doit être définie sur 'RCUR' !" % (track.IDfacture, track.prelevement_IDmandat))
                    listeTemp1.append(key)
            
        if len(listeErreurs) > 0 :
            message1 = u"Le bordereau ne peut être validé en raison des erreurs suivantes :"
            message2 = "\n".join(listeErreurs)
            dlg = dialogs.MultiMessageDialog(self, message1, caption=u"Erreur", msg2=message2, style = wx.ICON_EXCLAMATION |wx.OK, icon=None, btnLabels={wx.ID_OK : u"Ok"})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            return False

        return True
    
    
    def OnBoutonOk(self, event): 
        # Validation des données
        if self.ValidationDonnees() == False :
            return
        
        if self.ctrl_verrouillage.GetValue() == False :
            dlg = wx.MessageDialog(self, u"Pour clôturer le traitement d'un bordereau, vous devez valider ou refuser les pièces puis verrouiller le bordereau.\n\nSouhaitez-vous le faire maintenant ?", u"Information", wx.YES_NO|wx.CANCEL|wx.NO_DEFAULT|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_NO :
                return
            
        # Récupération des données
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
        
        # Sauvegarde des prélèvements du lot
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
        
        # Coche tous les prélèvements
        self.ctrl_pieces.CocheTout()
        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDlot=3)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
