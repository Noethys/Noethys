#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.html as html
import os
import six
import GestionDB
import datetime
import gzip
import shutil
import base64
import os.path
import wx.propgrid as wxpg
from Ctrl import CTRL_Propertygrid
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Dates
from Ol import OL_Modes_reglements
from Ol import OL_PES_pieces
import FonctionsPerso
import wx.lib.dialogs as dialogs
import wx.lib.agw.hyperlink as Hyperlink
from Utils import UTILS_Facturation
from Utils import UTILS_Parametres
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

if 'phoenix' in wx.PlatformInfo:
    from wx.adv import CommandLinkButton
else :
    from wx import CommandLinkButton

FORMATS = [
    {"code": "pes", "label": _(u"PES v2 ORMC Recette"), "description": _(u"Export vers le logiciel Hélios du Trésor Public diffusé par la DGFIP.")},
    {"code": "magnus", "label": _(u"Magnus Berger-Levrault"), "description": _(u"Export vers le logiciel Magnus de la société Berger-Levrault.")},
    {"code": "jvs", "label": _(u"Millesime Online JVS"), "description": _(u"Export vers le logiciel Millesime Online de la société JVS-MAIRISTEM.")},
    {"code": "corail", "label": _(u"Corail Cosoluce"), "description": _(u"Export vers le logiciel Corail de la société Cosoluce.")},
]

def GetFormatByCode(code=""):
    for dict_format in FORMATS:
        if dict_format["code"] == code:
            return dict_format
    return FORMATS[0]

def Supprime_accent(texte):
    liste = [ (u"é", u"e"), (u"è", u"e"), (u"ê", u"e"), (u"ë", u"e"), (u"à", u"a"), (u"û", u"u"), (u"ô", u"o"), (u"ç", u"c"), (u"î", u"i"), (u"ï", u"i"),]
    for a, b in liste :
        texte = texte.replace(a, b)
        texte = texte.replace(a.upper(), b.upper())
    return texte

def GetMoisStr(numMois, majuscules=False, sansAccents=False) :
    listeMois = (u"_", _(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    nom = listeMois[numMois]
    if sansAccents == True : 
        nom = Supprime_accent(nom)
    if majuscules == True :
        nom = nom.upper() 
    return nom    



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
        pass

    def Importation(self):
        """ Importation des données """
        pass

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
            if 'phoenix' in wx.PlatformInfo:
                choix.Add(label=nom, value=IDcompte)
            else:
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
            if 'phoenix' in wx.PlatformInfo:
                choix.Add(label=label, bitmap=bmp, value=IDmode)
            else:
                choix.Add(label, bmp, IDmode)
        propriete = self.GetPropertyByName("IDmode")
        propriete.SetChoices(choix)
        self.RefreshProperty(propriete) 


    def OnBoutonParametres(self, propriete=None):
        ancienneValeur = propriete.GetValue() 
        if propriete.GetName() == "IDcompte" :
            from Dlg import DLG_Comptes_bancaires
            dlg = DLG_Comptes_bancaires.Dialog(self)
            dlg.ShowModal()
            dlg.Destroy()
            self.MAJ_comptes() 
        if propriete.GetName() == "IDmode" :
            from Dlg import DLG_Modes_reglements
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
        html.HtmlWindow.__init__(self, parent, -1, style=style)
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





class DLG_Choix_format(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Choix_format", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        self.parent = parent
        self.format = None

        # Bandeau
        titre = _(u"Sélection du format")
        intro = _(u"Cliquez sur le format d'export souhaité.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Helios.png")

        self.liste_boutons = []
        for dict_format in FORMATS:
            ctrl = CommandLinkButton(self, -1, dict_format["label"], dict_format["description"], size=(200, -1))
            ctrl.SetMinSize((500, -1))
            self.Bind(wx.EVT_BUTTON, self.OnBoutonChoix, ctrl)
            self.liste_boutons.append({"id": ctrl.GetId(), "ctrl": ctrl, "dict_format": dict_format})

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(rows=10, cols=1, vgap=10, hgap=10)
        for dict_ctrl in self.liste_boutons:
            grid_sizer_contenu.Add(dict_ctrl["ctrl"], 0, wx.EXPAND, 10)

        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonChoix(self, event):
        for dict_ctrl in self.liste_boutons:
            if dict_ctrl["id"] == event.GetId():
                self.format = dict_ctrl["dict_format"]["code"]
                self.EndModal(wx.ID_OK)

    def GetFormat(self):
        return self.format

# ---------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDlot=None, format=None, ctrl_parametres=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_lot_tresor_public", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent  
        self.IDlot = IDlot
        self.format = format

        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"Caractéristiques"))

        self.label_format = wx.StaticText(self, -1, _(u"Format :"))
        self.ctrl_format = wx.TextCtrl(self, -1, GetFormatByCode(self.format)["label"])
        self.ctrl_format.Enable(False)

        self.label_nom = wx.StaticText(self, -1, _(u"Nom du lot :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.ctrl_nom.SetMinSize((230, -1))
        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_verrouillage = wx.StaticText(self, -1, _(u"Verrouillage :"))
        self.ctrl_verrouillage = wx.CheckBox(self, -1, u"")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_parametres = ctrl_parametres(self, IDlot=self.IDlot)

        # Pièces
        self.box_pieces_staticbox = wx.StaticBox(self, -1, _(u"Pièces"))
        
        self.ctrl_pieces = OL_PES_pieces.ListView(self, id=-1, IDlot=self.IDlot, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_pieces.SetMinSize((50, 50)) 
        
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
        self.bouton_fichier = CTRL_Bouton_image.CTRL(self, texte=_(u"Générer le fichier d'export %s") % GetFormatByCode(self.format)["label"], cheminImage="Images/32x32/Disk.png")
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
        
        # Init contrôles
        self.Importation() 
        
        self.tracks = OL_PES_pieces.GetTracks(self.IDlot)
        self.ctrl_pieces.MAJ(tracks=self.tracks) 
        self.ctrl_pieces.MAJtotaux() 

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un lot %s") % GetFormatByCode(self.format)["label"])
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez un nom pour ce lot (Ex : 'Janvier 2013', etc...). Nom interne à Noethys.")))
        self.ctrl_verrouillage.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour verrouiller le lot lorsque vous considérez qu'il est finalisé")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez ici des observations sur ce lot")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une pièce")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la pièce sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour retirer la pièce sélectionnée dans la liste")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher un aperçu avant impression de la liste des pièces")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste des pièces de ce lot")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fichier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour générer un fichier au format %s") % GetFormatByCode(self.format)["label"]))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider les données")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((900, 780))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
                
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        
        grid_sizer_generalites = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_format, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_format, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_verrouillage, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_verrouillage, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_generalites.AddGrowableRow(2)
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

    def OnBoutonModifier(self, event): 
        self.ctrl_pieces.Modifier()

    def OnBoutonSupprimer(self, event): 
        self.ctrl_pieces.Supprimer()

    def OnBoutonApercu(self, event): 
        self.ctrl_pieces.Apercu()

    def OnBoutonImprimer(self, event): 
        self.ctrl_pieces.Imprimer()

    def OnBoutonAide(self, event=None): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("ExportversHelios")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def GetLabelParametres(self):
        """ Renvoie les paramètres pour impression """
        nom = self.ctrl_nom.GetValue()
        texte = _(u"Lot : '%s'") % nom
        return texte
    
    def Importation(self):
        """ Importation des données """
        if self.IDlot == None :
            # Données du dernier lot
            DB = GestionDB.DB()
            req = """SELECT reglement_auto, IDcompte, IDmode, exercice, mois, objet_dette, date_emission, date_prelevement, date_envoi, id_bordereau, id_poste, id_collectivite, code_collectivite, code_budget, code_prodloc, code_etab, prelevement_libelle, objet_piece, format, options
            FROM pes_lots
            WHERE format='%s'
            ORDER BY IDlot;""" % self.format
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 :
                return
            reglement_auto, IDcompte, IDmode, exercice, mois, objet_dette, date_emission, date_prelevement, date_envoi, id_bordereau, id_poste, id_collectivite, code_collectivite, code_budget, code_prodloc, code_etab, prelevement_libelle, objet_piece, format, options = listeDonnees[-1]
            nom = u""
            verrouillage = False
            observations = u""

        else :
            # Importation
            DB = GestionDB.DB()
            req = """SELECT nom, verrouillage, observations, reglement_auto, IDcompte, IDmode, exercice, mois, objet_dette, date_emission, date_prelevement, date_envoi, id_bordereau, id_poste, id_collectivite, code_collectivite, code_budget, code_prodloc, code_etab, prelevement_libelle, objet_piece, format, options 
            FROM pes_lots
            WHERE IDlot=%d
            ;""" % self.IDlot
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 :
                return
            nom, verrouillage, observations, reglement_auto, IDcompte, IDmode, exercice, mois, objet_dette, date_emission, date_prelevement, date_envoi, id_bordereau, id_poste, id_collectivite, code_collectivite, code_budget, code_prodloc, code_etab, prelevement_libelle, objet_piece, format, options = listeDonnees[0]

        # Attribution des données aux contrôles
        self.ctrl_nom.SetValue(nom)
        self.ctrl_verrouillage.SetValue(verrouillage)
        self.ctrl_observations.SetValue(observations)
        if reglement_auto == 1 :
            self.ctrl_pieces.reglement_auto = True
        if prelevement_libelle in ("", None):
            prelevement_libelle = u"{NOM_ORGANISATEUR} - {LIBELLE_FACTURE}"
        if objet_piece in ("", None):
            objet_piece = _(u"FACTURE NUM{NUM_FACTURE} {MOIS_LETTRES} {ANNEE}")

        if self.IDlot == None:
            date_emission = datetime.date.today()
            date_prelevement = datetime.date.today()
            date_envoi = datetime.date.today()

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
            ("code_etab", code_etab),
            ("reglement_auto", reglement_auto),
            ("IDcompte", IDcompte),
            ("IDmode", IDmode),
            ("prelevement_libelle", prelevement_libelle),
            ("objet_piece", objet_piece),
            ]

        for code, valeur in listeValeurs:
            try:
                self.ctrl_parametres.SetPropertyValue(code, valeur)
            except:
                pass

    def ValidationDonnees(self):
        """ Vérifie que les données saisies sont exactes """
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
                dlg = wx.MessageDialog(self, _(u"Le caractère '%s' n'est pas autorisé dans le nom du lot !") % caract, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
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
            dlg = wx.MessageDialog(self, _(u"Ce nom de lot a déjà été attribué à un autre lot.\n\nChaque lot doit avoir un nom unique. Changez le nom."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
        
        observations = self.ctrl_observations.GetValue()
        
        if self.ctrl_verrouillage.GetValue() == True :
            verrouillage = 1
        else :
            verrouillage = 0

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
        code_etab = self.ctrl_parametres.GetPropertyValue("code_etab")
        reglement_auto = int(self.ctrl_parametres.GetPropertyValue("reglement_auto"))
        IDcompte = self.ctrl_parametres.GetPropertyValue("IDcompte")
        IDmode = self.ctrl_parametres.GetPropertyValue("IDmode")
        
        # Vérification du compte à créditer
        if reglement_auto == 1 :
            if IDcompte == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un compte à créditer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if IDmode == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un mode de règlement pour le règlement automatique !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Vérification des paramètres du bordereau
        listeVerifications = [
            (exercice, "exercice", _(u"l'année de l'exercice")),
            (mois, "mois", _(u"le mois")),
            (objet_dette, "objet_dette", _(u"l'objet de la dette")),
            (date_emission, "date_emission", _(u"la date d'émission")),
            (date_prelevement, "date_prelevement", _(u"la date souhaitée du prélèvement")),
            (date_envoi, "date_envoi", _(u"la date d'envoi")),
            (id_bordereau, "id_bordereau", _(u"l'ID bordereau")),
            (id_poste, "id_poste", _(u"l'ID poste")),
            (id_collectivite, "id_collectivite", _(u"l'ID collectivité")),
            (code_collectivite, "code_collectivite", _(u"le Code Collectivité")),
            (code_budget, "code_budget", _(u"le Code Bugdet")),
            (code_prodloc, "code_prodloc", _(u"le code Produit Local")),
            (code_etab, "code_etab", _(u"le code Etablissement")),
            ]
            
        for donnee, code, label in listeVerifications :
            if donnee == None or donnee == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir %s dans les paramètres du lot !") % label, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if code == "id_bordereau" :
                try :
                    test = int(donnee) 
                except :
                    dlg = wx.MessageDialog(self, _(u"Vous devez saisir une valeur numérique valide pour le paramètre de bordereau 'ID Bordereau' !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

            if code == "id_collectivite" :
                try :
                    test = int(donnee) 
                except :
                    dlg = wx.MessageDialog(self, _(u"Vous devez saisir une valeur numérique valide pour le paramètre de bordereau 'ID Collectivité' !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False



        # Vérification des pièces
        listeErreurs = []
        listeTemp1 = []
        for track in self.ctrl_pieces.GetObjects() :

            if track.analysePiece == False :
                listeErreurs.append(_(u"- Facture n°%s : %s") % (track.IDfacture, track.analysePieceTexte))
                
            # Vérifie qu'un OOFF ou un FRST n'est pas attribué 2 fois à un seul mandat
            if track.prelevement == 1 :
                if track.prelevement_sequence in ("OOFF", "FRST") :
                    key = (track.prelevement_IDmandat, track.prelevement_sequence)
                    if key in listeTemp1 :
                        if track.prelevement_sequence == "OOFF" : 
                            listeErreurs.append(_(u"- Facture n°%s : Le mandat n°%s de type ponctuel a déjà été utilisé une fois !") % (track.IDfacture, track.prelevement_IDmandat))
                        if track.prelevement_sequence == "FRST" : 
                            listeErreurs.append(_(u"- Facture n°%s : Mandat n°%s déjà initialisé. La séquence doit être définie sur 'RCUR' !") % (track.IDfacture, track.prelevement_IDmandat))
                    listeTemp1.append(key)
            
        if len(listeErreurs) > 0 :
            message1 = _(u"Le bordereau ne peut être validé en raison des erreurs suivantes :")
            message2 = "\n".join(listeErreurs)
            dlg = dialogs.MultiMessageDialog(self, message1, caption=_(u"Erreur"), msg2=message2, style = wx.ICON_EXCLAMATION |wx.OK, icon=None, btnLabels={wx.ID_OK : _(u"Ok")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            return False

        return True
    
    def Memorisation_parametres(self):
        """ Est surchargée """
        pass

    def OnBoutonOk(self, event): 
        # Validation des données
        if self.ValidationDonnees() == False :
            return
        
        if self.ctrl_verrouillage.GetValue() == False :
            dlg = wx.MessageDialog(self, _(u"Pour clôturer le traitement d'un lot, vous devez valider ou refuser les pièces puis verrouiller le lot.\n\nSouhaitez-vous le faire maintenant ?"), _(u"Information"), wx.YES_NO|wx.CANCEL|wx.NO_DEFAULT|wx.ICON_INFORMATION)
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
        if 'phoenix' in wx.PlatformInfo:
            date_emission = self.ctrl_parametres.GetPropertyValue("date_emission").FormatISODate()
            date_prelevement = self.ctrl_parametres.GetPropertyValue("date_prelevement").FormatISODate()
            try:
                date_envoi = self.ctrl_parametres.GetPropertyValue("date_envoi").FormatISODate()
            except:
                date_envoi = None
        else:
            date_emission = self.ctrl_parametres.GetPropertyValue("date_emission").strftime("%Y-%m-%d")
            date_prelevement = self.ctrl_parametres.GetPropertyValue("date_prelevement").strftime("%Y-%m-%d")
            try:
                date_envoi = self.ctrl_parametres.GetPropertyValue("date_envoi").strftime("%Y-%m-%d")
            except:
                date_envoi = None
        try:
            id_bordereau = self.ctrl_parametres.GetPropertyValue("id_bordereau")
        except:
            id_bordereau = None
        id_poste = self.ctrl_parametres.GetPropertyValue("id_poste")
        try:
            id_collectivite = self.ctrl_parametres.GetPropertyValue("id_collectivite")
        except:
            id_collectivite = None
        try:
            code_collectivite = self.ctrl_parametres.GetPropertyValue("code_collectivite")
        except:
            code_collectivite = None
        try:
            code_budget = self.ctrl_parametres.GetPropertyValue("code_budget")
        except:
            code_budget = None
        code_prodloc = self.ctrl_parametres.GetPropertyValue("code_prodloc")
        try:
            code_etab = self.ctrl_parametres.GetPropertyValue("code_etab")
        except:
            code_etab = None
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
            ("code_etab", code_etab),
            ("prelevement_libelle", prelevement_libelle),
            ("objet_piece", objet_piece),
            ("format", self.format),
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

        # Mémorisation des préférences
        self.Memorisation_parametres()

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
        self.ctrl_pieces.AjoutFactures(tracksFactures)
        
        # Coche tous les prélèvements
        self.ctrl_pieces.CocheTout()

        # Ferme ctrl_factures (utilise CallAfter pour éviter bug)
        wx.CallAfter(self.FermeAssistant, ctrl_factures)

    def FermeAssistant(self, ctrl_factures=None):
        ctrl_factures.Destroy()
        del ctrl_factures

    def OnBoutonFichier(self, event):
        """ Génération d'un fichier normalisé """
        pass






if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDlot=1)
    filtres = [
        {"type": "numero_intervalle", "numero_min": 1983, "numero_max": 2051},
    ]
    dlg.Assistant(filtres=filtres, nomLot="Nom de lot exemple")
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
