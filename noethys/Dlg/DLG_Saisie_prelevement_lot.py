#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.html as html
import os
import GestionDB
import datetime
import six
from Ctrl import CTRL_Saisie_date
from Utils import UTILS_Dates
from Utils import UTILS_Historique
from Dlg import DLG_Messagebox
from Ol import OL_Prelevements_national
from Ol import OL_Prelevements_sepa
from Ol import OL_Modes_reglements
from Utils import UTILS_Prelevements
import FonctionsPerso
import wx.lib.agw.hyperlink as Hyperlink
import wx.propgrid as wxpg
from Ctrl import CTRL_Propertygrid
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal



def Supprime_accent(texte):
    liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"),]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte


class CTRL_Parametres(CTRL_Propertygrid.CTRL):
    def __init__(self, parent, IDlot=None):
        self.parent = parent
        self.IDlot = IDlot
        CTRL_Propertygrid.CTRL.__init__(self, parent)

        self.SetExtraStyle(wxpg.PG_EX_HELP_AS_TOOLTIPS)
        couleurFond = "#dcf7d4"
        self.SetCaptionBackgroundColour(couleurFond)
        self.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)

    def Remplissage(self):
        # Généralités
        self.Append(wxpg.PropertyCategory(_(u"Généralités")))

        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Format"), name="format", liste_choix=[("prive", _(u"Secteur privé")), ("public_dft", _(u"Secteur public DFT"))], valeur="prive")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez le format"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        propriete = wxpg.EnumProperty(label=_(u"Compte à créditer"), name="IDcompte")
        propriete.SetHelpString(_(u"Sélectionnez le compte bancaire à créditer dans le cadre du règlement automatique"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_comptes()

        propriete = wxpg.EnumProperty(label=_(u"Perception"), name="perception")
        propriete.SetHelpString(_(u"Sélectionnez une perception (uniquement pour le secteur public)"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_perceptions()

        propriete = wxpg.StringProperty(label=_(u"Motif du prélèvement"), name="motif", value=u"")
        propriete.SetHelpString(_(u"Saisissez le motif du prélèvement. Ex : 'Garderie Novembre 2019' (uniquement pour le secteur public)"))
        self.Append(propriete)

        # Règlement auto
        self.Append(wxpg.PropertyCategory(_(u"Règlement automatique")))

        propriete = wxpg.BoolProperty(label=_(u"Régler automatiquement"), name="reglement_auto", value=False)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys enregistre un règlement dans Noethys pour chaque prélèvement valide"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        propriete = wxpg.EnumProperty(label=_(u"Mode de règlement"), name="IDmode")
        propriete.SetHelpString(_(u"Sélectionnez le mode de règlement à utiliser dans le cadre du règlement automatique"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_modes()

        # Options
        self.Append(wxpg.PropertyCategory(_(u"Options")))

        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Encodage"), name="encodage", liste_choix=[("utf-8", _(u"utf-8")), ("iso-8859-15", _(u"iso-8859-15"))], valeur="utf-8")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez l'encodage du fichier"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


    def Importation(self):
        """ Importation des données """
        pass

    def MAJ_comptes(self):
        DB = GestionDB.DB()
        req = """SELECT IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics, dft_titulaire, dft_iban
        FROM comptes_bancaires
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictComptes = {}
        choix = wxpg.PGChoices()
        for IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics, dft_titulaire, dft_iban in listeDonnees:
            self.dictComptes[IDcompte] = {
                "nom": nom, "numero": numero, "defaut": defaut, "raison": raison, "code_etab": code_etab, "code_guichet": code_guichet, "code_nne": code_nne,
                "cle_rib": cle_rib, "cle_iban": cle_iban, "iban": iban, "bic": bic, "code_ics": code_ics, "dft_titulaire": dft_titulaire, "dft_iban": dft_iban,
                }
            choix.Add(label=nom, value=IDcompte)
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
        for IDmode, label, numero_piece, nbre_chiffres, frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label, image in listeDonnees:
            self.dictModes[
                IDmode] = {"label": label, "numero_piece": numero_piece, "nbre_chiffres": nbre_chiffres, "frais_gestion": frais_gestion, "frais_montant": frais_montant, "frais_pourcentage": frais_pourcentage, "frais_arrondi": frais_arrondi, "frais_label": frais_label, "image": image, }
            bmp = OL_Modes_reglements.GetImage(image)
            choix.Add(label=label, bitmap=bmp, value=IDmode)
        propriete = self.GetPropertyByName("IDmode")
        propriete.SetChoices(choix)
        self.RefreshProperty(propriete)

    def MAJ_comptes(self):
        DB = GestionDB.DB()
        req = """SELECT IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics, dft_titulaire, dft_iban
        FROM comptes_bancaires
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictComptes = {}
        choix = wxpg.PGChoices()
        for IDcompte, nom, numero, defaut, raison, code_etab, code_guichet, code_nne, cle_rib, cle_iban, iban, bic, code_ics, dft_titulaire, dft_iban in listeDonnees:
            self.dictComptes[IDcompte] = {
                "nom": nom, "numero": numero, "defaut": defaut, "raison": raison, "code_etab": code_etab, "code_guichet": code_guichet, "code_nne": code_nne,
                "cle_rib": cle_rib, "cle_iban": cle_iban, "iban": iban, "bic": bic, "code_ics": code_ics, "dft_titulaire": dft_titulaire, "dft_iban": dft_iban,
                }
            choix.Add(label=nom, value=IDcompte)
        propriete = self.GetPropertyByName("IDcompte")
        propriete.SetChoices(choix)
        self.RefreshProperty(propriete)

    def MAJ_perceptions(self):
        DB = GestionDB.DB()
        req = """SELECT IDperception, nom, rue_resid, cp_resid, ville_resid
        FROM perceptions
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictPerceptions = {}
        choix = wxpg.PGChoices()
        for IDperception, nom, rue_resid, cp_resid, ville_resid in listeDonnees:
            self.dictPerceptions[IDperception] = {"IDperception" : IDperception, "nom" : nom, "rue_resid" : rue_resid, "cp_resid" : cp_resid, "ville_resid" : ville_resid}
            choix.Add(label=nom, value=IDperception)
        propriete = self.GetPropertyByName("perception")
        propriete.SetChoices(choix)
        self.RefreshProperty(propriete)

    def OnBoutonParametres(self, propriete=None):
        ancienneValeur = propriete.GetValue()
        if propriete.GetName() == "IDcompte":
            from Dlg import DLG_Comptes_bancaires
            dlg = DLG_Comptes_bancaires.Dialog(self)
            dlg.ShowModal()
            dlg.Destroy()
            self.MAJ_comptes()
        if propriete.GetName() == "IDmode":
            from Dlg import DLG_Modes_reglements
            dlg = DLG_Modes_reglements.Dialog(self)
            dlg.ShowModal()
            dlg.Destroy()
            self.MAJ_modes()
        if propriete.GetName() == "perception":
            from Dlg import DLG_Perceptions
            dlg = DLG_Perceptions.Dialog(self)
            dlg.ShowModal()
            dlg.Destroy()
            self.MAJ_perceptions()

        try:
            propriete.SetValue(ancienneValeur)
        except:
            pass

    def OnPropGridChange(self, event):
        propriete = event.GetProperty()
        if propriete.GetName() == "reglement_auto":
            self.parent.ctrl_prelevements.reglement_auto = propriete.GetValue()




# ------------------------------------------------------------------------------------------------------------------------


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
            self.parent.ctrl_prelevements.CocheTout() 
        if self.URL == "selection_rien" :
            self.parent.ctrl_prelevements.CocheRien() 
        if self.URL == "etat_valide" :
            self.parent.ctrl_prelevements.SetStatut("valide")
        if self.URL == "etat_attente" :
            self.parent.ctrl_prelevements.SetStatut("attente")
        if self.URL == "etat_refus" :
            self.parent.ctrl_prelevements.SetStatut("refus")
        if self.URL == "reglements_tout" :
            self.parent.ctrl_prelevements.SetRegle(True)
        if self.URL == "reglements_rien" :
            self.parent.ctrl_prelevements.SetRegle(False)
        self.UpdateLink()
            
        

# ---------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDlot=None, typePrelevement="national"):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_prelevement_lot", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent  
        self.IDlot = IDlot 
        self.typePrelevement = typePrelevement
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"Caractéristiques"))
        
        self.label_nom = wx.StaticText(self, -1, _(u"Nom du lot :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.ctrl_nom.SetMinSize((230, -1))
        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.ctrl_observations.SetMinSize((-1, 50))

        self.label_date = wx.StaticText(self, -1, _(u"Date du prélèv. :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.ctrl_date.SetDate(datetime.date.today())
        self.label_verrouillage = wx.StaticText(self, -1, _(u"Verrouillage :"))
        self.ctrl_verrouillage = wx.CheckBox(self, -1, u"")

        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_parametres = CTRL_Parametres(self, IDlot=self.IDlot)

        # Prélèvements
        self.box_prelevements_staticbox = wx.StaticBox(self, -1, _(u"Prélèvements"))
        
        if self.typePrelevement == "sepa" :
            MODULE = OL_Prelevements_sepa
        else :
            MODULE = OL_Prelevements_national
        self.ctrl_prelevements = MODULE.ListView(self, id=-1, typePrelevement=self.typePrelevement, name="OL_prelevements", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_prelevements.SetMinSize((50, 50)) 
        
        self.ctrl_recherche = MODULE.CTRL_Outils(self, listview=self.ctrl_prelevements, afficherCocher=False)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        
        
        self.label_actions = wx.StaticText(self, -1, _(u"Actions sur prélèvements cochés :"))

        self.hyper_etat_attente = Hyperlien(self, label=_(u"Attente"), infobulle=_(u"Cliquez ici pour mettre en attente les prélèvements cochés"), URL="etat_attente")
        self.label_separation_1 = wx.StaticText(self, -1, u"|")
        self.hyper_etat_valide = Hyperlien(self, label=_(u"Valide"), infobulle=_(u"Cliquez ici pour valider les prélèvements cochés"), URL="etat_valide")
        self.label_separation_2 = wx.StaticText(self, -1, u"|")
        self.hyper_etat_refus = Hyperlien(self, label=_(u"Refus"), infobulle=_(u"Cliquez ici pour refuser les prélèvements cochés"), URL="etat_refus")

        self.hyper_reglements_tout = Hyperlien(self, label=_(u"Régler"), infobulle=_(u"Cliquez ici pour régler les prélèvements cochés"), URL="reglements_tout")
        self.label_separation_3 = wx.StaticText(self, -1, u"|")
        self.hyper_reglements_rien = Hyperlien(self, label=_(u"Ne pas régler"), infobulle=_(u"Cliquez ici pour ne pas régler les prélèvements cochés"), URL="reglements_rien")


        self.hyper_selection_tout = Hyperlien(self, label=_(u"Tout cocher"), infobulle=_(u"Cliquez ici pour tout cocher la sélection"), URL="selection_tout")
        self.label_separation_4 = wx.StaticText(self, -1, u"|")
        self.hyper_selection_rien = Hyperlien(self, label=_(u"Tout décocher"), infobulle=_(u"Cliquez ici pour tout décocher la sélection"), URL="selection_rien")

        self.ctrl_totaux = CTRL_Infos(self, hauteur=40, couleurFond="#F0FBED" , style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.SUNKEN_BORDER)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fichier_national = CTRL_Bouton_image.CTRL(self, texte=_(u"Générer un fichier AFB-CFONB"), cheminImage="Images/32x32/Disk.png")
        self.bouton_fichier_SEPA = CTRL_Bouton_image.CTRL(self, texte=_(u"Générer un fichier SEPA"), cheminImage="Images/32x32/Disk.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        if self.typePrelevement == "sepa" : self.bouton_fichier_national.Show(False)
        if self.typePrelevement == "national" : self.bouton_fichier_SEPA.Show(False)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFichierNational, self.bouton_fichier_national)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFichierSEPA, self.bouton_fichier_SEPA)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init contrôles
        self.Importation() 
        
        self.tracks = MODULE.GetTracks(self.IDlot)
        self.ctrl_prelevements.MAJ(tracks=self.tracks) 
        self.ctrl_prelevements.MAJtotaux() 

    def __set_properties(self):
        if self.typePrelevement == "sepa" :
            self.SetTitle(_(u"Saisie d'un lot de prélèvements - format SEPA"))
        else :
            self.SetTitle(_(u"Saisie d'un lot de prélèvements - format National"))
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez un nom pour ce lot (Ex : 'Janvier 2013', etc...)")))
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Saisissez la date prévue du prélèvement")))
        self.ctrl_verrouillage.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour verrouiller le lot lorsqu'il a été communiqué à la banque")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez ici des observations sur ce lot de prélèvements")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un prélèvement")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le prélèvement sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour retirer le prélèvement sélectionné dans la liste")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste des prélèvements")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste des prélèvements de ce lot")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fichier_national.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour générer un fichier normalisé AFB-CFONB destiné à votre banque")))
        self.bouton_fichier_SEPA.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour générer un fichier normalisé SEPA destiné à votre banque")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider les données")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((900, 780))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
                
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        
        grid_sizer_generalites = wx.FlexGridSizer(rows=5, cols=2, vgap=5, hgap=5)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_generalites.Add(self.label_verrouillage, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_verrouillage, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_generalites.AddGrowableRow(2)        
        grid_sizer_haut.Add(box_generalites, 1, wx.EXPAND, 0)
        
        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        box_parametres.Add(self.ctrl_parametres, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_parametres, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        # Prélèvements
        box_prelevements = wx.StaticBoxSizer(self.box_prelevements_staticbox, wx.VERTICAL)
        grid_sizer_prelevements = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_prelevements.Add(self.ctrl_prelevements, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons_liste = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_liste.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_liste.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_liste.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons_liste.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_boutons_liste.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons_liste.Add(self.bouton_imprimer, 0, 0, 0)
        
        grid_sizer_prelevements.Add(grid_sizer_boutons_liste, 1, wx.EXPAND, 0)

        # CTRL Outils
        grid_sizer_prelevements.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)
        grid_sizer_prelevements.Add((10, 10), 0, wx.EXPAND, 0)

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
        
        grid_sizer_prelevements.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_prelevements.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_prelevements.Add(self.ctrl_totaux, 0, wx.EXPAND, 0)
        grid_sizer_prelevements.AddGrowableRow(0)
        grid_sizer_prelevements.AddGrowableCol(0)
        box_prelevements.Add(grid_sizer_prelevements, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_prelevements, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fichier_national, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fichier_SEPA, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(3)
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
##        self.ctrl_prelevements.Saisie_factures()
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        item = wx.MenuItem(menuPop, 20, _(u"Ajouter une ou plusieurs factures"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_prelevements.Saisie_factures, id=20)

        item = wx.MenuItem(menuPop, 10, _(u"Ajouter un prélèvement manuel"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_prelevements.Saisie_manuelle, id=10)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OnBoutonModifier(self, event): 
        self.ctrl_prelevements.Modifier()

    def OnBoutonSupprimer(self, event): 
        self.ctrl_prelevements.Supprimer()

    def OnBoutonApercu(self, event): 
        self.ctrl_prelevements.Apercu()

    def OnBoutonImprimer(self, event): 
        self.ctrl_prelevements.Imprimer()

    def OnBoutonAide(self, event=None): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Prlvementautomatique1")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonFichierNational(self, event):
        """ Génération d'un fichier normalisé format NATIONAL """
        # Validation des données
        if self.ValidationDonnees() == False :
            return

        listeLignes = []

        # Ligne 1 : Emetteur
        date_prelevement = self.ctrl_date.GetDate()
        dictCompte = self.ctrl_compte.GetInfos()
        numero_emetteur = dictCompte["code_nne"]
        raison_sociale = dictCompte["raison"]
        numero_guichet = dictCompte["code_guichet"]
        numero_compte = dictCompte["numero"]
        numero_etablissement = dictCompte["code_etab"]

        dictDonnees = {
            "type_prelevement" : u"0308",
            "numero_emetteur" : numero_emetteur,
            "date" : date_prelevement,
            "raison_sociale" : raison_sociale,
            "reference_virement" : u"",
            "monnaie" : u"E",
            "numero_guichet" : numero_guichet,
            "numero_compte" : numero_compte,
            "numero_etablissement" : numero_etablissement,
            }
        ligne = UTILS_Prelevements.GetLigneEmetteur(dictDonnees)
        listeLignes.append(ligne)

        # Lignes des prélèvements
        index = 0
        total = 0
        for track in self.ctrl_prelevements.GetObjects() :
            montant = int(str(FloatToDecimal(track.montant)).replace(".", ""))
            dictDonnees = {
                "type_prelevement" : u"0608",
                "numero_emetteur" : numero_emetteur,
                "reference_ligne" : str(index+1),
                "nom_destinataire" : track.titulaire,
                "nom_banque" : track.nomBanque,
                "numero_guichet" : track.prelevement_guichet,
                "numero_compte" : track.prelevement_numero,
                "montant" : str(montant),
                "libelle" : track.libelle,
                "numero_etablissement" : track.prelevement_etab,
                }
            ligne = UTILS_Prelevements.GetLigneDestinataire(dictDonnees)
            listeLignes.append(ligne)
            total += montant

            index += 1

        # Ligne de total
        dictDonnees = {
            "type_prelevement" : u"0808",
            "numero_emetteur" : numero_emetteur,
            "total" : str(total),
            }
        ligne = UTILS_Prelevements.GetLigneTotal(dictDonnees)
        listeLignes.append(ligne)

        # Finalisation du texte
        texte = "".join(listeLignes)

        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "Prelevements.txt"
        wildcard = "Fichier texte (*.txt)|*.txt|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut,
            defaultFile = nomFichier,
            wildcard = wildcard,
            style = wx.FD_SAVE
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
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Création du fichier texte
        f = open(cheminFichier, "w")
        f.write(texte.encode("iso-8859-15"))
        f.close()

        # Confirmation de création du fichier et demande d'ouverture directe
        txtMessage = _(u"Le fichier a été créé avec succès.\n\nSouhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)

    def OnBoutonFichierSEPA(self, event): 
        """ Génération d'un fichier normalisé format SEPA """
        # Validation des données
        if self.ValidationDonnees() == False :
            return

        # Récupération des infos sur la remise
        remise_nom = Supprime_accent(self.ctrl_nom.GetValue())
        paiement_date = self.ctrl_date.GetDate() 

        # Récupération des infos sur l'organisme
        DB = GestionDB.DB()
        req = """SELECT rue, cp, ville, num_siret
        FROM organisateur
        WHERE IDorganisateur=1;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        creancier_rue, creancier_cp, creancier_ville, creancier_siret = listeDonnees[0]

        # Récupération des infos sur le compte créditeur
        parametres = self.ctrl_parametres.GetParametres()
        IDcompte = parametres["IDcompte"]
        motif = parametres["motif"]
        dictCompte = self.ctrl_parametres.dictComptes[IDcompte]
        paiement_ics = dictCompte["code_ics"]
        creancier_nom = dictCompte["raison"]
        paiement_iban = dictCompte["iban"]
        paiement_bic = dictCompte["bic"]
        dft_titulaire = dictCompte["dft_titulaire"]
        dft_iban = dictCompte["dft_iban"]
        perception = self.ctrl_parametres.dictPerceptions.get(parametres["perception"], None)
        
        # Création des lots
        listeSequences = ["OOFF", "FRST", "RCUR", "FNAL"]        
        
        # Récupération des transactions à effectuer
        montantTotal = FloatToDecimal(0.0)
        nbreTotal = 0
        listeAnomalies = []
        listeLots = []
        
        # Vérifie que seul les tracks filtrés sont souhaités
        tracks = self.ctrl_prelevements.GetFilteredObjects()
        if len(self.ctrl_prelevements.GetObjects()) != len(tracks) :
            txtMessage = u"Souhaitez-vous vraiment prendre uniquement compte les lignes filtrées (%d/%d lignes) ?\n\nSi vous répondez Non, toutes les lignes seront intégrées dans le fichier." % (len(tracks), len(self.ctrl_prelevements.GetObjects()))
            dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.CANCEL|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_CANCEL :
                return
            if reponse == wx.ID_NO :
                tracks = self.ctrl_prelevements.GetObjects()
        
        for sequence in listeSequences :
            
            lot_montant = FloatToDecimal(0.0)
            listeTransactions = []
            for track in tracks :
                if sequence == track.sequence :
                    
                    montant = FloatToDecimal(track.montant)
                    
                    if track.prelevement_reference_mandat in ("", None) : listeAnomalies.append(_(u"%s : Référence Unique du Mandat manquant") % track.titulaires)
                    if track.prelevement_date_mandat in ("", None) : listeAnomalies.append(_(u"%s : Date du Mandat manquante") % track.titulaires)
                    if track.prelevement_iban in ("", None) : listeAnomalies.append(_(u"%s : Numéro IBAN du compte bancaire manquant") % track.titulaires)
                    if track.prelevement_bic in ("", None) : listeAnomalies.append(_(u"%s : Numéro BIC du compte bancaire manquant") % track.titulaires)
                    if track.titulaire in ("", None) : listeAnomalies.append(_(u"%s : Nom du titulaire du compte bancaire manquant") % track.titulaires)

                    dictTransaction = {
                        "transaction_id" : track.libelle,
                        "transaction_montant" : str(montant),
                        "transaction_mandat_id" : track.prelevement_reference_mandat,
                        "transaction_mandat_date" : str(track.prelevement_date_mandat),
                        "transaction_bic" : track.prelevement_bic,
                        "transaction_debiteur" : track.titulaire,
                        "transaction_iban" : track.prelevement_iban,
                        }        
                    listeTransactions.append(dictTransaction)
                    montantTotal += montant
                    lot_montant += montant
                    nbreTotal += 1
            
            # Mémorisation du lot
            if len(listeTransactions) > 0 :
                
                dictLot = {
                    "lot_nom" : u"%s %s" % (remise_nom, sequence),
                    "lot_nbre" : str(len(listeTransactions)),
                    "lot_montant" : str(lot_montant),
                    "lot_date" : str(paiement_date),
                    "lot_iban" : paiement_iban,
                    "lot_bic" : paiement_bic,
                    "lot_ics" : paiement_ics,
                    "dft_titulaire": dft_titulaire,
                    "dft_iban" : dft_iban,
                    "motif": motif,
                    "lot_sequence" : sequence,
                    "transactions" : listeTransactions,
                    }
                
                listeLots.append(dictLot)
            
        
        if len(listeAnomalies) > 0 :
            intro = _(u"Le fichier SEPA ne peut être généré en raison des anomalies suivantes :")
            detail = "\n".join(listeAnomalies)
            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Génération impossible"), introduction=intro, detail=detail, icone=wx.ICON_ERROR, boutons=[_(u"Ok"), ], defaut=0)
            dlg.ShowModal()
            dlg.Destroy() 
            return
            
        # Mémorisation de tous les données
        dictDonnees = {
            "remise_nom" : remise_nom,
            "remise_date_heure" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "remise_nbre" : str(nbreTotal),
            "remise_montant" : str(montantTotal),
            
            "creancier_nom" : creancier_nom,
            "creancier_rue" : creancier_rue,
            "creancier_cp" : creancier_cp,
            "creancier_ville" : creancier_ville,
            "creancier_pays" : _(u"FR"),
            "creancier_siret" : creancier_siret,

            "type_remise": parametres["format"],
            "perception": perception,
            
            "lots" : listeLots,
            }
        
        # Génération du fichier XML
        doc = UTILS_Prelevements.GetXMLSepa(dictDonnees)
        xml = doc.toprettyxml(encoding=parametres["encodage"])
        
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = u"%s.xml" % remise_nom # "Prelevements.xml"
        wildcard = "Fichier XML (*.xml)|*.xml| All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
            wildcard = wildcard, 
            style = wx.FD_SAVE
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
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà.\n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy()
                return False
            else:
                dlg.Destroy()

        # Création du fichier texte
        if six.PY2:
            flag = "w"
        else:
            flag = "wb"
        f = open(cheminFichier, flag)
        try:
            f.write(xml)
        finally:
            f.close()

        # Mémorisation dans historique
        UTILS_Historique.InsertActions([{
            "IDcategorie" : 35, 
            "action" : _(u"Génération du fichier XML SEPA '%s'") % remise_nom,
            },])

        # Confirmation de création du fichier et demande d'ouverture directe
        txtMessage = _(u"Le fichier SEPA a été créé avec succès.\n\nSouhaitez-vous visualiser son contenu maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)
        

    def GetLabelParametres(self):
        """ Renvoie les paramètres pour impression """
        nom = self.ctrl_nom.GetValue()
        if self.ctrl_date.GetDate() != None :
            date = UTILS_Dates.DateEngFr(str(self.ctrl_date.GetDate()))
        texte = _(u"Prélèvement : '%s' (%s)") % (nom, date)
        return texte
    
    def Importation(self):
        """ Importation des données """
        if self.IDlot == None :
            # Données du dernier lot
            DB = GestionDB.DB()
            req = """SELECT nom, date, verrouillage, IDcompte, observations, IDmode, reglement_auto, format, encodage, IDperception, motif
            FROM lots_prelevements
            ORDER BY IDlot;"""
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 :
                return
            nom, date, verrouillage, IDcompte, observations, IDmode, reglement_auto, format_lot, encodage, IDperception, motif = listeDonnees[-1]
            nom = u""
            date = datetime.date.today() 
            verrouillage = False
            observations = u""

        else :
            # Importation
            DB = GestionDB.DB()
            req = """SELECT nom, date, verrouillage, IDcompte, observations, IDmode, reglement_auto, format, encodage, IDperception, motif
            FROM lots_prelevements
            WHERE IDlot=%d
            ;""" % self.IDlot
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 :
                return
            nom, date, verrouillage, IDcompte, observations, IDmode, reglement_auto, format_lot, encodage, IDperception, motif = listeDonnees[0]
        
        # Attribution des données aux contrôles
        self.ctrl_nom.SetValue(nom)
        self.ctrl_date.SetDate(date)
        self.ctrl_verrouillage.SetValue(verrouillage)
        self.ctrl_observations.SetValue(observations)

        listeValeurs = [
            ("IDcompte", IDcompte),
            ("IDmode", IDmode),
            ("reglement_auto", reglement_auto),
            ("format", format_lot),
            ("encodage", encodage),
            ("perception", IDperception),
            ("motif", motif),
            ]
        for code, valeur in listeValeurs:
            propriete = self.ctrl_parametres.GetPropertyByName(code)
            propriete.SetValue(valeur)


    def ValidationDonnees(self):
        """ Vérifie que les données saisies sont exactes """
        parametres = self.ctrl_parametres.GetParametres()

        # Généralités
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de lot (Ex : 'Janvier 2013'...) !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
 
        for caract in nom :
            if caract in ("_",) :
                dlg = wx.MessageDialog(self, _(u"Le caractère '%s' n'est pas autorisé dans le nom du lot de prélèvements !") % caract, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
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
        FROM lots_prelevements
        WHERE nom='%s' AND IDlot!=%d;""" % (nom, IDlotTemp)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce nom de lot a déjà été attribué à un autre lot de prélèvements.\n\nChaque lot doit avoir un nom unique. Changez le nom."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False

        date = self.ctrl_date.GetDate()
        if date == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de prélèvement !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus() 
            return False
        
        observations = self.ctrl_observations.GetValue()
        if self.ctrl_verrouillage.GetValue() == True :
            verrouillage = 1
        else :
            verrouillage = 0
        
        # Vérification du compte créditeur
        IDcompte = parametres["IDcompte"]
        if IDcompte == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un compte à créditer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        type_remise = parametres["format"]
        dictCompte = self.ctrl_parametres.dictComptes[IDcompte]
        nomCompte = dictCompte["nom"]
        numero = dictCompte["numero"]
        raison = dictCompte["raison"]
        code_etab = dictCompte["code_etab"]
        code_guichet = dictCompte["code_guichet"]
        code_nne = dictCompte["code_nne"]
        code_ics = dictCompte["code_ics"]
        iban = dictCompte["iban"]
        bic = dictCompte["bic"]
        dft_titulaire = dictCompte["dft_titulaire"]
        dft_iban = dictCompte["dft_iban"]

        if raison == "" or raison == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné la raison sociale du compte créditeur !\n\nModifiez les paramètres du compte bancaire."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.typePrelevement == "sepa" :

            if iban == "" or iban == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le IBAN du compte créditeur !\n\nModifiez les paramètres du compte bancaire."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            if bic == "" or bic == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le BIC du compte créditeur !\n\nModifiez les paramètres du compte bancaire."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            if code_ics == "" or code_ics == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le ICS du compte créditeur !\n\nModifiez les paramètres du compte bancaire."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        if self.typePrelevement == "national" :

            if numero == "" or numero == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le numéro du compte créditeur !\n\nModifiez les paramètres du compte bancaire."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if code_etab == "" or code_etab == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le code Etablissement créditeur !\n\nModifiez les paramètres du compte bancaire."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if code_guichet == "" or code_guichet == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le code Guichet du compte créditeur !\n\nModifiez les paramètres du compte bancaire."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if code_nne == "" or code_nne == None :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le code NNE du compte créditeur !\n\nModifiez les paramètres du compte bancaire."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Si remise de type publique DFT
        if type_remise == "public_dft":

            if not dft_titulaire:
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le nom du titulaire du compte DFT !\n\nModifiez les paramètres du compte bancaire."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if not dft_iban:
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le nom du titulaire du compte DFT !\n\nModifiez les paramètres du compte bancaire."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if not parametres["motif"]:
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le motif du prélèvement !\n\nModifiez les paramètres du lot."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if not parametres["perception"]:
                dlg = wx.MessageDialog(self, _(u"Vous n'avez pas sélectionné de perception !\n\nModifiez les paramètres du lot."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False


        IDmode = parametres["IDmode"]
        reglement_auto = int(parametres["reglement_auto"])

        # Vérification des prélèvements
        listeErreurs = []
        listeTemp1 = []
        for track in self.ctrl_prelevements.GetObjects() :
            
            # Vérifie qu'un OOFF ou un FRST n'est pas attribué 2 fois à un seul mandat
            if self.typePrelevement == "sepa" :
                if track.sequence in ("OOFF", "FRST") :
                    key = (track.IDmandat, track.sequence)
                    if key in listeTemp1 :
                        if track.sequence == "OOFF" :
                            listeErreurs.append(_(u"- Prélèvement '%s' de %s : Le mandat '%s' de type ponctuel a déjà été utilisé une fois !") % (track.libelle, track.titulaires, track.prelevement_reference_mandat))
                        if track.sequence == "FRST" : 
                            listeErreurs.append(_(u"- Prélèvement '%s' de %s : Mandat '%s' déjà initialisé. La séquence doit être définie sur 'RCUR' !") % (track.libelle, track.titulaires, track.prelevement_reference_mandat))
                    listeTemp1.append(key)
            
        if len(listeErreurs) > 0 :
            message1 = _(u"Le lot de prélèvements ne peut être validé en raison des erreurs suivantes :")
            detail = "\n".join(listeErreurs)
            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Erreur"), introduction=message1, detail=detail, icone=wx.ICON_EXCLAMATION, boutons=[_(u"Ok"), ], defaut=0)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        return True
    
    
    def OnBoutonOk(self, event): 
        # Validation des données
        if self.ValidationDonnees() == False :
            return

        if self.ctrl_verrouillage.GetValue() == False :
            dlg = wx.MessageDialog(self, _(u"Pour clôturer le traitement d'un lot de prélèvements, vous devez valider ou refuser les prélèvements puis verrouiller le lot.\n\nSouhaitez-vous le faire maintenant ?!"), _(u"Information"), wx.YES_NO|wx.CANCEL|wx.NO_DEFAULT|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_NO :
                return

        # Récupération des données
        parametres = self.ctrl_parametres.GetParametres()
        nom = self.ctrl_nom.GetValue()
        date = self.ctrl_date.GetDate()
        observations = self.ctrl_observations.GetValue()
        verrouillage = int(self.ctrl_verrouillage.GetValue())

        # Sauvegarde du lot
        listeDonnees = [
            ("nom", nom ),
            ("date", date),
            ("verrouillage", verrouillage),
            ("IDcompte", parametres["IDcompte"]),
            ("observations", observations),
            ("IDmode", parametres["IDmode"]),
            ("reglement_auto", int(parametres["reglement_auto"])),
            ("type", self.typePrelevement),
            ("format", parametres["format"]),
            ("encodage", parametres["encodage"]),
            ("IDperception", parametres["perception"]),
            ("motif", parametres["motif"]),
        ]

        DB = GestionDB.DB()
        if self.IDlot == None :
            # Ajout
            self.IDlot = DB.ReqInsert("lots_prelevements", listeDonnees)
        else :
            # Modification
            DB.ReqMAJ("lots_prelevements", listeDonnees, "IDlot", self.IDlot)
        DB.Close() 
        
        # Sauvegarde des prélèvements du lot
        self.ctrl_prelevements.Sauvegarde(IDlot=self.IDlot, datePrelevement=date, IDcompte=parametres["IDcompte"], IDmode=parametres["IDmode"])
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetIDlot(self):
        return self.IDlot

    def Assistant(self, filtres=[], nomLot=None):
        # Saisie du titre du lot
        if nomLot != None :
            self.ctrl_nom.SetValue(nomLot)       

        # Saisie des factures
        from Ctrl import CTRL_Liste_factures
        ctrl_factures = CTRL_Liste_factures.CTRL(self, filtres=filtres)
        ctrl_factures.ctrl_factures.CocheTout()
        tracksFactures = ctrl_factures.GetTracksCoches()
        self.ctrl_prelevements.AjoutFactures(tracksFactures)

        # Coche tous les prélèvements
        self.ctrl_prelevements.CocheTout()

        # Ferme ctrl_factures (utilise CallAfter pour éviter bug)
        wx.CallAfter(self.FermeAssistant, ctrl_factures)

    def FermeAssistant(self, ctrl_factures=None):
        ctrl_factures.Destroy()
        del ctrl_factures

        
if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDlot=1, typePrelevement="sepa")
    filtres = [
        #{"type": "numero_intervalle", "numero_min": 6862, "numero_max": 7022},
        {"type": "solde_actuel", "operateur": "<", "montant": 0.0},
        {"type": "prelevement", "choix": True},
    ]
    dlg.Assistant(filtres=filtres, nomLot="Nom de lot exemple")
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
