#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
import wx.lib.agw.floatspin as FS

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros
from Ol import OL_Consommations
from Ol import OL_Deductions
from Ctrl import CTRL_Saisie_duree
from Utils import UTILS_Dates
from Utils import UTILS_Gestion


def DateEngEnDateDD(dateEng):
    if dateEng != None :
        return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
    else:
        return None

def DateDDenFr(dateDD):
    if dateDD == None : return None
    return dateDD.strftime("%d/%m/%Y")
    
def ConvertStrToListe(texte=None):
    """ Convertit un texte "1;2;3;4" en [1, 2, 3, 4] """
    if texte == None :
        return None
    listeResultats = []
    temp = texte.split(";")
    for ID in temp :
        listeResultats.append(int(ID))
    return listeResultats


class Choix_categorie(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        
        self.listeCategories = [
            ("consommation", _(u"Consommation")),
            ("cotisation", _(u"Cotisation")),
            ("location", _(u"Location")),
            ("autre", _(u"Autre")),
            ]

        self.listeNoms = []
        for code, label in self.listeCategories :
            self.listeNoms.append(label)
        self.SetItems(self.listeNoms)
        self.SetCategorie("autre")
    
    def SetCategorie(self, categorie=""):
        index = 0
        for code, label in self.listeCategories :
            if categorie == code :
                 self.SetSelection(index)
            index += 1

    def GetCategorie(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeCategories[index][0]

# ------------------------------------------------------------------------------------------------------------------------------------------

class Choix_individu(wx.Choice):
    def __init__(self, parent, IDfamille=None):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDfamille = IDfamille
        self.listeIndividus = []
        self.listeNoms = []
        self.dictIndividus = self.Importation_individus()
        self.SetListeDonnees(self.dictIndividus)

    def Importation_individus(self):
        DB = GestionDB.DB()
        # Recherche les individus de la famille
        dictIndividus = {}
        req = """SELECT individus.IDindividu, IDcivilite, nom, prenom, date_naiss, IDcategorie, titulaire
        FROM individus
        LEFT JOIN rattachements ON individus.IDindividu = rattachements.IDindividu
        WHERE rattachements.IDfamille = %d AND IDcategorie IN (1, 2)
        ORDER BY nom, prenom;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeIndividus = DB.ResultatReq()
        for IDindividu, IDcivilite, nom, prenom, date_naiss, IDcategorie, titulaire in listeIndividus:
            dictTemp = {
                "IDcivilite": IDcivilite, "nom": nom, "prenom": prenom,
                "IDcategorie": IDcategorie, "titulaire": titulaire,
                "inscriptions": [],
            }
            dictIndividus[IDindividu] = dictTemp

        # Recherche des inscriptions pour chaque membre de la famille
        req = """SELECT inscriptions.IDinscription, IDindividu, inscriptions.IDactivite, IDgroupe, inscriptions.IDcategorie_tarif, categories_tarifs.nom
        FROM inscriptions 
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
        WHERE inscriptions.statut='ok' AND IDfamille = %d ;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeInscriptions = DB.ResultatReq()
        for IDinscription, IDindividu, IDactivite, IDgroupe, IDcategorie_tarif, nomCategorie_tarif in listeInscriptions:
            dictTemp = {
                "IDinscription": IDinscription, "IDactivite": IDactivite, "IDgroupe": IDgroupe,
                "IDcategorie_tarif": IDcategorie_tarif, "nomCategorie_tarif": nomCategorie_tarif,
            }
            if IDindividu in dictIndividus:
                dictIndividus[IDindividu]["inscriptions"].append(dictTemp)

        # Cloture de la base de données
        DB.Close()

        return dictIndividus

    def SetListeDonnees(self, dictIndividus):
        self.listeIndividus = []
        self.listeNoms = []
        for IDindividu, dictIndividu in dictIndividus.items() :
            nomIndividu = u"%s %s" % (dictIndividu["nom"], dictIndividu["prenom"])
            self.listeIndividus.append((nomIndividu, IDindividu))
        self.listeIndividus.sort()
        for nomIndividu, IDindividu in self.listeIndividus :
            self.listeNoms.append(nomIndividu)
        self.SetItems(self.listeNoms)
    
    def SetID(self, ID=None):
        index = 0
        for nomIndividu, IDindividu in self.listeIndividus :
            if IDindividu == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeIndividus[index][1]

# ------------------------------------------------------------------------------------------------------------------------------------------

class Choix_activite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeActivites = []
    
    def SetListeDonnees(self, listeActivites=[]):
        self.listeNoms = []
        self.listeActivites = listeActivites
        for dictActivite in listeActivites :
            IDactivite = dictActivite["IDactivite"]
            nom = dictActivite["nom"]
            if nom == None : nom = "?"
            self.listeNoms.append(nom)
        self.SetItems(self.listeNoms)
    
    def SetID(self, ID=None):
        index = 0
        for dictActivite in self.listeActivites :
            IDactivite = dictActivite["IDactivite"]
            if IDactivite == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeActivites[index]["IDactivite"]

# ------------------------------------------------------------------------------------------------------------------------------------------

class Choix_categorie_tarif(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeCategoriesTarifs= []
    
    def SetListeDonnees(self, listeCategoriesTarifs=[]):
        self.listeNoms = []
        self.listeCategoriesTarifs = listeCategoriesTarifs
        for dictCategorieTarif in listeCategoriesTarifs :
            IDcategorie_tarif = dictCategorieTarif["IDcategorie_tarif"]
            nom = dictCategorieTarif["nom"]
            self.listeNoms.append(nom)
        self.SetItems(self.listeNoms)
    
    def SetID(self, ID=None):
        index = 0
        for dictCategorieTarif in self.listeCategoriesTarifs :
            IDcategorie_tarif = dictCategorieTarif["IDcategorie_tarif"]
            if IDcategorie_tarif == ID :
                self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeCategoriesTarifs[index]["IDcategorie_tarif"]

# ------------------------------------------------------------------------------------------------------------------------------------------

class Choix_tarif(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeNoms = []
        self.listeTarifs= []
    
    def SetListeDonnees(self, listeTarifs=[]):
        self.listeNoms = []
        self.listeTarifs = listeTarifs
        for dictTarif in listeTarifs :
            IDtarif = dictTarif["IDtarif"]
            nom = dictTarif["nomTarif"]
            date_debut = dictTarif["date_debut"]
            date_fin = dictTarif["date_fin"]
            if date_debut == None and date_fin == None : label = _(u"%s (Sans période de validité)") % nom
            if date_debut == None and date_fin != None : label = _(u"%s (Jusqu'au %s)") % (nom, DateDDenFr(date_fin))
            if date_debut != None and date_fin == None : label = _(u"%s (A partir du %s)") % (nom, DateDDenFr(date_debut))
            if date_debut != None and date_fin != None : label = _(u"%s (Du %s au %s)") % (nom, DateDDenFr(date_debut), DateDDenFr(date_fin))
            self.listeNoms.append(label)
        self.SetItems(self.listeNoms)
    
    def SetID(self, ID=None):
        index = 0
        for dictTarif in self.listeTarifs :
            IDtarif = dictTarif["IDtarif"]
            if IDtarif == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeTarifs[index]["IDtarif"]

# ------------------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDprestation=None, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_prestation", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDprestation = IDprestation
        self.IDfamille = IDfamille
        self.ancienMontant = 0.0
        self.IDfacture = None
        
        # Recherche du IDcompte_payeur
        DB = GestionDB.DB()
        req = """SELECT IDcompte_payeur
        FROM comptes_payeurs 
        WHERE IDfamille=%d;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.IDcompte_payeur = listeDonnees[0][0]
        
        if self.IDprestation == None :
            self.SetTitle(_(u"Saisie d'une prestation"))
            titre = _(u"Saisie d'une prestation")
        else:
            self.SetTitle(_(u"Modification d'une prestation"))
            titre = _(u"Modification d'une prestation")
        intro = _(u"Vous pouvez saisir ou modifier ici les caractéristiques d'une prestation. Cela peut être utile lorsque vous devez saisir une prestation exceptionnelle pour un individu ou une famille (ex.: frais de dossier, pénalité, report...) ou quand certains paramètres doivent être modifiés manuellement.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
        
        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralites"))
        self.label_date = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = Choix_categorie(self)
##        self.ctrl_categorie.Enable(False)
        self.label_label = wx.StaticText(self, -1, _(u"Intitulé :"))
        self.ctrl_label = wx.TextCtrl(self, -1, u"")
        self.label_type = wx.StaticText(self, -1, _(u"Type :"))
        self.radio_type_familiale = wx.RadioButton(self, -1, _(u"Prestation familiale"), style=wx.RB_GROUP)
        self.radio_type_individuelle = wx.RadioButton(self, -1, _(u"Prestation individuelle :"))
        self.ctrl_individu = Choix_individu(self, self.IDfamille)
        
        # Facturation
        self.staticbox_facturation_staticbox = wx.StaticBox(self, -1, _(u"Facturation"))
        self.label_activite = wx.StaticText(self, -1, _(u"Activité :"))
        self.ctrl_activite = Choix_activite(self)
        self.label_categorie_tarif = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie_tarif = Choix_categorie_tarif(self)
        self.label_tarif = wx.StaticText(self, -1, _(u"Tarif :"))
        self.ctrl_tarif = Choix_tarif(self)
        self.label_facture = wx.StaticText(self, -1, _(u"Facture :"))
        self.ctrl_facture = wx.StaticText(self, -1, _(u"Non facturé"))
        self.label_temps = wx.StaticText(self, -1, _(u"Temps facturé :"))
        self.ctrl_temps = CTRL_Saisie_duree.CTRL(self, size=(80, -1))

        # TVA
        self.label_tva = wx.StaticText(self, -1, _(u"Taux TVA (%) :"))
        self.ctrl_tva = FS.FloatSpin(self, -1, min_val=0, max_val=100, increment=0.1, agwStyle=FS.FS_RIGHT)
        self.ctrl_tva.SetFormat("%f")
        self.ctrl_tva.SetDigits(2)
        
        # Code comptable
        self.label_code_comptable = wx.StaticText(self, -1, _(u"Code compta :"))
        self.ctrl_code_comptable = wx.TextCtrl(self, -1, u"") 
        
        # Montants
        self.label_montant_avant_deduc = wx.StaticText(self, -1, _(u"Montant TTC (%s) :") % SYMBOLE)
        self.ctrl_montant_avant_deduc = CTRL_Saisie_euros.CTRL(self)
        self.ctrl_montant_avant_deduc.SetMinSize((100, -1))
        self.label_montant = wx.StaticText(self, -1, _(u"Montant final TTC (%s) :") % SYMBOLE)
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self, font=wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, u""))
        self.ctrl_montant.SetBackgroundColour("#F0FBED")
        self.ctrl_montant.SetEditable(False)
        self.ctrl_montant.SetMinSize((100, -1))
        
        # Déductions associées
        self.staticbox_deductions_staticbox = wx.StaticBox(self, -1, _(u"Déductions"))
        if self.IDprestation == None :
            IDprestationTemp = 0
        else :
            IDprestationTemp = self.IDprestation
        self.ctrl_deductions = OL_Deductions.ListView(self, id=-1, IDprestation=IDprestationTemp, IDcompte_payeur=self.IDcompte_payeur, modificationsVirtuelles=True, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_deductions.SetMinSize((20, 100))
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        # Consommations associées
        self.staticbox_consommations_staticbox = wx.StaticBox(self, -1, _(u"Consommations associées"))
        self.ctrl_consommations = OL_Consommations.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_consommations.SetMinSize((20, 100))
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixCategorie, self.ctrl_categorie)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioType, self.radio_type_familiale)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioType, self.radio_type_individuelle)
        self.Bind(wx.EVT_CHOICE, self.OnChoixActivite, self.ctrl_activite)
        self.Bind(wx.EVT_CHOICE, self.OnChoixCategorieTarif, self.ctrl_categorie_tarif)
        self.Bind(wx.EVT_CHOICE, self.OnChoixTarif, self.ctrl_tarif)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        self.ctrl_categorie_tarif.Enable(False)
        self.ctrl_tarif.Enable(False)
        
        # Remplissage des contrôles
        self.listeActivites = self.Importation_activites()
        self.ctrl_activite.SetListeDonnees(self.listeActivites)
        
        self.listeCategoriesTarifs = self.Importation_categories_tarifs(IDactivite=0) 
        self.ctrl_categorie_tarif.SetListeDonnees(self.listeCategoriesTarifs)
        
        self.listeTarifs = self.Importation_tarifs(IDcategorie_tarif=0)
        self.ctrl_tarif.SetListeDonnees(self.listeTarifs)
        
        # Importation lors d'une modification
        if self.IDprestation != None :
            self.Importation() 
        else:
            self.ctrl_consommations.SetIDprestation(IDprestation) 
            self.ctrl_date.SetDate(datetime.date.today())
        
        self.ctrl_deductions.MAJ() 
        
##        # Saisie du montant initial de la prestation
##        totalDeductions = self.ctrl_deductions.GetTotalDeductions()
##        montantInitial = self.ctrl_montant.GetMontant() + totalDeductions
##        self.ctrl_montant_avant_deduc.SetMontant(montantInitial)
        
        # MAJ des contrôles
        self.OnRadioType(None)
        
        self.Bind(wx.EVT_TEXT, self.OnTextMontant, self.ctrl_montant_avant_deduc)
        

    def __set_properties(self):
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de la prestation")))
        self.ctrl_categorie.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici la catégorie de la prestation")))
        self.ctrl_label.SetToolTip(wx.ToolTip(_(u"Saisissez un intitulé pour cette prestation")))
        self.radio_type_familiale.SetToolTip(wx.ToolTip(_(u"Selectionnez cette case si la prestation concerne toute la famille")))
        self.radio_type_individuelle.SetToolTip(wx.ToolTip(_(u"Selectionnez cette case si la prestation ne concerne qu'un individu")))
        self.ctrl_individu.SetToolTip(wx.ToolTip(_(u"Selectionnez l'individu associé à la prestation")))
        self.ctrl_activite.SetToolTip(wx.ToolTip(_(u"Selectionnez ici l'activité concernée par la prestation")))
        self.ctrl_categorie_tarif.SetToolTip(wx.ToolTip(_(u"Selectionnez ici la catégorie de tarif rattaché a cette prestation")))
        self.ctrl_tarif.SetToolTip(wx.ToolTip(_(u"Selectionnez un tarif parmi ceux proposés")))
        self.ctrl_montant_avant_deduc.SetToolTip(wx.ToolTip(_(u"Saisissez ici le montant avant déductions en Euros")))
        self.ctrl_montant.SetToolTip(wx.ToolTip(_(u"Montant après déductions en Euros")))
        self.ctrl_facture.SetToolTip(wx.ToolTip(_(u"Quand une prestation a été facturée, le numéro de facture apparait ici")))
        self.ctrl_temps.SetToolTip(wx.ToolTip(_(u"Vous pouvez modifier ici le temps facturé pour cette prestation (utile pour la CAF)")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une nouvelle déduction")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la déduction selectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la déduction selectionnée dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))
        self.ctrl_tva.SetToolTip(wx.ToolTip(_(u"Saisissez le taux de TVA inclus [Optionnel]")))
        self.ctrl_code_comptable.SetToolTip(wx.ToolTip(_(u"Saisissez le code comptable de cette prestation si vous souhaitez utiliser l'export vers les logiciels de comptabilité [Optionnel]")))

        self.ctrl_label.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, u""))
        
        self.SetMinSize((850, 700))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        staticbox_facturation = wx.StaticBoxSizer(self.staticbox_facturation_staticbox, wx.VERTICAL)
        grid_sizer_facturation = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)
        grid_sizer_type = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_generalites.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_type, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_type.Add(self.radio_type_familiale, 0, 0, 0)
        grid_sizer_type.Add(self.radio_type_individuelle, 0, 0, 0)
        grid_sizer_type.Add(self.ctrl_individu, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_type.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_type, 1, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_generalites, 1, wx.EXPAND, 0)
        grid_sizer_facturation.Add(self.label_activite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_facturation.Add(self.ctrl_activite, 0, wx.EXPAND, 0)
        grid_sizer_facturation.Add(self.label_categorie_tarif, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_facturation.Add(self.ctrl_categorie_tarif, 0, wx.EXPAND, 0)
        grid_sizer_facturation.Add(self.label_tarif, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_facturation.Add(self.ctrl_tarif, 0, wx.EXPAND, 0)
        
        # Temps facturé + numéro de facture
        grid_sizer_facturation.Add(self.label_temps, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_temps = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_temps.Add(self.ctrl_temps, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_temps.Add( (5, 5), 1, wx.EXPAND, 0)
        grid_sizer_temps.Add(self.label_facture, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_temps.Add( self.ctrl_facture, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_temps.AddGrowableCol(1)
        grid_sizer_facturation.Add(grid_sizer_temps, 1, wx.EXPAND, 0)

        # TVA + code comptable
        grid_sizer_facturation.Add(self.label_tva, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tva = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_tva.Add(self.ctrl_tva, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tva.Add( (5, 5), 1, wx.EXPAND, 0)
        grid_sizer_tva.Add(self.label_code_comptable, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tva.Add( self.ctrl_code_comptable, 0, 0, 0)
        grid_sizer_tva.AddGrowableCol(1)
        grid_sizer_facturation.Add(grid_sizer_tva, 1, wx.EXPAND, 0)

        # Montants
        grid_sizer_facturation.Add(self.label_montant_avant_deduc, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_montants = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_montants.Add(self.ctrl_montant_avant_deduc, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_montants.Add( (5, 5), 1, wx.EXPAND, 0)
        grid_sizer_montants.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_montants.Add( self.ctrl_montant, 0, 0, 0)
        grid_sizer_montants.AddGrowableCol(1)
        grid_sizer_facturation.Add(grid_sizer_montants, 1, wx.EXPAND, 0)
        
        grid_sizer_facturation.AddGrowableCol(1)
        staticbox_facturation.Add(grid_sizer_facturation, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_facturation, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Déductions
        staticbox_deductions = wx.StaticBoxSizer(self.staticbox_deductions_staticbox, wx.VERTICAL)
        grid_sizer_deductions = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_deductions.Add(self.ctrl_deductions, 1, wx.EXPAND, 0)
        grid_sizer_boutons_deduc = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_deduc.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_deduc.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_deduc.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_deductions.Add(grid_sizer_boutons_deduc, 1, wx.EXPAND, 0)
        grid_sizer_deductions.AddGrowableRow(0)
        grid_sizer_deductions.AddGrowableCol(0)
        staticbox_deductions.Add(grid_sizer_deductions, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_deductions, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Consommations
        staticbox_consommations = wx.StaticBoxSizer(self.staticbox_consommations_staticbox, wx.VERTICAL)
        grid_sizer_consommations = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_consommations.Add(self.ctrl_consommations, 1, wx.EXPAND, 0)
        grid_sizer_consommations.AddGrowableRow(0)
        grid_sizer_consommations.AddGrowableCol(0)
        staticbox_consommations.Add(grid_sizer_consommations, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_consommations, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnChoixCategorie(self, event): 
        pass

    def OnRadioType(self, event): 
        if self.radio_type_familiale.GetValue() == True :
            self.ctrl_individu.Enable(False)
        else:
            self.ctrl_individu.Enable(True)

    def OnChoixActivite(self, event): 
        # MAJ du contrôle des catégories de tarifs
        IDactivite = self.ctrl_activite.GetID()
        self.listeCategoriesTarifs = self.Importation_categories_tarifs(IDactivite) 
        if len(self.listeCategoriesTarifs) > 0 :
            self.ctrl_categorie_tarif.Enable(True)
        else:
            self.ctrl_categorie_tarif.Enable(False)
        self.ctrl_categorie_tarif.SetListeDonnees(self.listeCategoriesTarifs)
        self.OnChoixCategorieTarif(None)

    def OnChoixCategorieTarif(self, event): 
        # MAJ du contrôle des tarifs
        IDcategorie_tarif = self.ctrl_categorie_tarif.GetID()
        self.listeTarifs = self.Importation_tarifs(IDcategorie_tarif)
        if len(self.listeTarifs) > 0 :
            self.ctrl_tarif.Enable(True)
        else:
            self.ctrl_tarif.Enable(False)
        self.ctrl_tarif.SetListeDonnees(self.listeTarifs)

    def OnChoixTarif(self, event): 
        event.Skip()

    def OnBoutonAjouter(self, event): 
        self.ctrl_deductions.Ajouter(None)

    def OnBoutonModifier(self, event): 
        self.ctrl_deductions.Modifier(None)

    def OnBoutonSupprimer(self, event): 
        self.ctrl_deductions.Supprimer(None)

    def OnTextMontant(self, event):
        validation, message = self.ctrl_montant_avant_deduc.Validation() 
        if validation == True :
            montantInitial = self.ctrl_montant_avant_deduc.GetMontant() 
            totalDeductions = self.ctrl_deductions.GetTotalDeductions()
            self.ctrl_montant.SetMontant(montantInitial - totalDeductions)
                                    
    def Importation(self):
        """ Importation des données """
        DB = GestionDB.DB()
        req = """SELECT IDprestation, prestations.IDcompte_payeur, date, categorie, label, montant_initial, montant, prestations.IDactivite, 
        prestations.IDtarif, prestations.IDfacture, IDfamille, IDindividu, temps_facture, categories_tarifs, prestations.IDcategorie_tarif, prestations.code_compta, prestations.tva,
        factures.IDprefixe, factures_prefixes.prefixe, factures.numero
        FROM prestations 
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        LEFT JOIN factures_prefixes ON factures_prefixes.IDprefixe = factures.IDprefixe
        WHERE IDprestation=%d;""" % self.IDprestation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        prestation = listeDonnees[0]
        IDprestation, IDcompte_payeur, date, categorie, label, montant_initial, montant, IDactivite, IDtarif, IDfacture, IDfamille, IDindividu, temps_facture, categories_tarifs, IDcategorie_tarif, code_compta, tva, IDprefixe, prefixe, numFacture = prestation
        date = UTILS_Dates.DateEngEnDateDD(date)

        # Date
        self.ctrl_date.SetDate(date)
        # Label
        self.ctrl_label.SetValue(label)
        # Catégorie
        self.ctrl_categorie.SetCategorie(categorie)
        # Individu
        if IDindividu != None and IDindividu != 0 :
            self.radio_type_individuelle.SetValue(True)
            self.ctrl_individu.SetID(IDindividu)
        # Activité
        if IDactivite != None :
            self.ctrl_activite.SetID(IDactivite)
        if categorie == "cotisation" :
            self.ctrl_activite.Enable(False)
        # Catégorie de tarif
        self.OnChoixActivite(None)
        self.ctrl_categorie_tarif.SetID(IDcategorie_tarif)
        # Tarif
        self.OnChoixCategorieTarif(None)
        self.ctrl_tarif.SetID(IDtarif)
        # Code comptable
        if code_compta != None :
            self.ctrl_code_comptable.SetValue(code_compta)
        # TVA
        if tva != None :
            self.ctrl_tva.SetValue(tva)
        # Montant initial
        self.ctrl_montant_avant_deduc.SetMontant(montant_initial)
        # Montant final
        self.ctrl_montant.SetMontant(montant)
        self.ancienMontant = montant
        # Facture
        self.IDfacture = IDfacture

        verrouillage = False

        if numFacture != None :
            if IDprefixe != None :
                numFacture = u"%s-%06d" % (prefixe, numFacture)
            else :
                numFacture = u"%06d" % numFacture
            self.ctrl_facture.SetLabel(_(u"Facture n°%s") % numFacture)

            verrouillage = True

        # Périodes de gestion
        self.gestion = UTILS_Gestion.Gestion(None)
        if self.gestion.Verification("prestations", date, silencieux=True) == False:
            verrouillage = True

        if verrouillage == True :
            self.ctrl_deductions.Enable(False)
            self.bouton_ajouter.Enable(False)
            self.bouton_modifier.Enable(False)
            self.bouton_supprimer.Enable(False)
            
        # Liste des consommations
        self.ctrl_consommations.SetIDprestation(IDprestation) 
        # Temps facturé
        if temps_facture != None :
            self.ctrl_temps.SetDuree(temps_facture)
                

    def Importation_activites(self):
        DB = GestionDB.DB()
        # Recherche les activités
        dictIndividus = {}
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeActivites = []
        for IDactivite, nom, abrege in listeDonnees :
            dictTemp = {"IDactivite" : IDactivite, "nom" : nom, "abrege" : abrege}
            listeActivites.append(dictTemp)
        return listeActivites

    def Importation_categories_tarifs(self, IDactivite=0):
        if IDactivite == None : return []
        DB = GestionDB.DB()
        # Recherche les catégories de tarifs
        dictIndividus = {}
        req = """SELECT IDcategorie_tarif, IDactivite, nom
        FROM categories_tarifs
        WHERE IDactivite=%d
        ORDER BY nom;""" % IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeCategoriesTarifs = []
        for IDcategorie_tarif, IDactivite, nom in listeDonnees :
            dictTemp = {"IDcategorie_tarif" : IDcategorie_tarif, "IDactivite" : IDactivite, "nom" : nom}
            listeCategoriesTarifs.append(dictTemp)
        return listeCategoriesTarifs

    def Importation_tarifs(self, IDcategorie_tarif=0):
        if IDcategorie_tarif == None : return []
        DB = GestionDB.DB()
        # Recherche les tarifs
        dictIndividus = {}
        req = """SELECT IDtarif, tarifs.IDactivite, 
        tarifs.IDnom_tarif, noms_tarifs.nom, 
        date_debut, date_fin, methode, categories_tarifs, groupes
        FROM tarifs
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        ORDER BY noms_tarifs.nom, date_debut;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        listeTarifs = []
        for IDtarif, IDactivite, IDnom_tarif, nomTarif, date_debut, date_fin, methode, categories_tarifs, groupes in listeDonnees :
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            listeCategoriesTarifs = ConvertStrToListe(categories_tarifs)
            
            dictTemp = {
                    "IDtarif" : IDtarif, "IDactivite" : IDactivite, 
                    "IDnom_tarif" : IDnom_tarif, "nomTarif" : nomTarif, "date_debut" : date_debut,
                    "date_fin" : date_fin, "methode" : methode, "categories_tarifs":categories_tarifs, "groupes":groupes,
                    }
            
            if listeCategoriesTarifs != None :
                if IDcategorie_tarif in listeCategoriesTarifs :
                    listeTarifs.append(dictTemp)

        return listeTarifs


    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Prestations")

    def OnBoutonOk(self, event):
        # Récupération et vérification des données saisies
        if self.IDfacture != None :
            dlg = wx.MessageDialog(self, _(u"Cette prestation apparaît déjà sur une facture. Il est donc impossible de la modifier !\n\nVous devez obligatoirement cliquer sur le bouton ANNULER pour quitter."), _(u"Validation impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        date = self.ctrl_date.GetDate()
        if date == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return
        
        categorie = self.ctrl_categorie.GetCategorie() 
        
        label = self.ctrl_label.GetValue()
        if label == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un intitulé !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_label.SetFocus()
            return
        
        IDactivite = self.ctrl_activite.GetID()
        IDcategorie_tarif = self.ctrl_categorie_tarif.GetID() 
        IDtarif = self.ctrl_tarif.GetID()
        
        montant_initial = self.ctrl_montant_avant_deduc.GetMontant()
        montant = self.ctrl_montant.GetMontant()
        if montant == None :
            dlg = wx.MessageDialog(self, _(u"Le montant que vous avez saisi ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return
        
        IDfamille = self.IDfamille
        if self.radio_type_individuelle.GetValue() == True :
            IDindividu = self.ctrl_individu.GetID()
            if IDindividu == None :
                dlg = wx.MessageDialog(self, _(u"Etant donné que vous avez sélectionné le type 'prestation individuelle', vous devez obligatoirement sélectionner un individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_individu.SetFocus()
                return
        else:
            IDindividu = 0
        
        code_comptable = self.ctrl_code_comptable.GetValue() 
        if code_comptable == "" :
            code_comptable = None
        tva = self.ctrl_tva.GetValue()
        if tva == 0.0 :
            tva = None

        # Vérifie temps facturé
        temps_facture = UTILS_Dates.DeltaEnStr(self.ctrl_temps.GetDuree(), separateur=":")
        if temps_facture != None :
            if self.ctrl_temps.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Le temps facturé que vous avez saisi ne semble pas correct !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_temps.SetFocus()
                return

        # Périodes de gestion
        gestion = UTILS_Gestion.Gestion(None)
        if gestion.Verification("prestations", date) == False: return False

        # Récupération du IDcompte_payeur
        DB = GestionDB.DB()
        req = "SELECT IDcompte_payeur FROM familles WHERE IDfamille=%d" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        IDcompte_payeur = listeDonnees[0][0]
        
        DB = GestionDB.DB()
        
        # Recherche si cette prestation a déjà été ventilée sur un règlement
        if self.IDprestation != None :
            req = """SELECT IDventilation, ventilation.montant
            FROM ventilation
            LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
            WHERE IDprestation=%d
            ORDER BY reglements.date;""" % self.IDprestation
            DB.ExecuterReq(req)
            listeVentilations = DB.ResultatReq()
            montantVentilation = 0.0
            for IDventilation, montantTmp in listeVentilations :
                montantVentilation += montantTmp
            if montantVentilation > montant :
                # Si le montant total ventilé est supérieur au montant de la prestation :
                montantVentilationTmp = 0.0
                for IDventilation, montantTmp in listeVentilations :
                    montantVentilationTmp += montantTmp
                    if montantVentilationTmp > montant :
                        nouveauMontant = montantTmp - (montantVentilationTmp - montant)
                        if nouveauMontant > 0.0 :
                            DB.ReqMAJ("ventilation", [("montant", nouveauMontant),], "IDventilation", IDventilation)
                            montantVentilationTmp =  (montantVentilationTmp - montantTmp) + nouveauMontant
                        else:
                            DB.ReqDEL("ventilation", "IDventilation", IDventilation)

        # Sauvegarde de la prestation
        listeDonnees = [    
                ("IDcompte_payeur", IDcompte_payeur),
                ("date", date),
                ("categorie", categorie),
                ("label", label),
                ("montant_initial", montant_initial),
                ("montant", montant),
                ("IDactivite", IDactivite),
                ("IDtarif", IDtarif),
                ("IDfamille", IDfamille),
                ("IDindividu", IDindividu),
                ("temps_facture", temps_facture),
                ("IDcategorie_tarif", IDcategorie_tarif),
                ("code_compta", code_comptable),
                ("tva", tva),
            ]
        if self.IDprestation == None :
            listeDonnees.append(("date_valeur", str(datetime.date.today())))
            self.IDprestation = DB.ReqInsert("prestations", listeDonnees)
        else:
            DB.ReqMAJ("prestations", listeDonnees, "IDprestation", self.IDprestation)
        DB.Close()
        
        # Sauvegarde des déductions
        self.ctrl_deductions.Sauvegarde(IDprestation=self.IDprestation)        
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDprestation(self):
        return self.IDprestation


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDprestation=26675, IDfamille=399)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()

