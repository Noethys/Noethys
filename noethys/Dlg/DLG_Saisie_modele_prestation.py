#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
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
from Ctrl import CTRL_Tarification_calcul
from Ctrl import CTRL_Saisie_euros
from Ctrl import CTRL_Saisie_duree
from Utils import UTILS_Dates
from Utils import UTILS_Texte

from Dlg.DLG_Ouvertures import Track_tarif
from Ctrl.CTRL_Tarification_calcul import CHAMPS_TABLE_LIGNES


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
            if nom == None :
                nom = _(u"Sans nom")
            date_debut = dictTarif["date_debut"]
            date_fin = dictTarif["date_fin"]
            if date_debut == None and date_fin == None : label = _(u"%s (Sans période de validité)") % nom
            if date_debut == None and date_fin != None : label = _(u"%s (Jusqu'au %s)") % (nom, UTILS_Dates.DateDDEnFr(date_fin))
            if date_debut != None and date_fin == None : label = _(u"%s (A partir du %s)") % (nom, UTILS_Dates.DateDDEnFr(date_debut))
            if date_debut != None and date_fin != None : label = _(u"%s (Du %s au %s)") % (nom, UTILS_Dates.DateDDEnFr(date_debut), UTILS_Dates.DateDDEnFr(date_fin))
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
    def __init__(self, parent, IDmodele=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_modele_prestation", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDmodele = IDmodele
        self.track_tarif = None
        self.listeInitialeIDlignes = []

        if self.IDmodele == None :
            titre = _(u"Saisie d'un modèle de prestation")
        else:
            titre = _(u"Modification d'un modèle de prestation")
        self.SetTitle(titre)
        intro = _(u"Vous pouvez saisir ou modifier ici les caractéristiques d'un modèle de prestation. Un modèle permet une saisie rapide de plusieurs prestations aux caractéristiques identiques.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
        
        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralites"))
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = Choix_categorie(self)
        self.label_label = wx.StaticText(self, -1, _(u"Intitulé :"))
        self.ctrl_label = wx.TextCtrl(self, -1, u"")
        self.ctrl_label.SetMinSize((200, -1))
        self.label_type = wx.StaticText(self, -1, _(u"Type :"))
        self.radio_type_familiale = wx.RadioButton(self, -1, _(u"Prestation familiale"), style=wx.RB_GROUP)
        self.radio_type_individuelle = wx.RadioButton(self, -1, _(u"Prestation individuelle"))

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_activite = wx.StaticText(self, -1, _(u"Activité :"))
        self.ctrl_activite = Choix_activite(self)
        self.label_categorie_tarif = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie_tarif = Choix_categorie_tarif(self)
        self.label_tarif = wx.StaticText(self, -1, _(u"Tarif :"))
        self.ctrl_tarif = Choix_tarif(self)

        # TVA
        self.label_tva = wx.StaticText(self, -1, _(u"Taux TVA (%) :"))
        self.ctrl_tva = FS.FloatSpin(self, -1, min_val=0, max_val=100, increment=0.1, agwStyle=FS.FS_RIGHT)
        self.ctrl_tva.SetFormat("%f")
        self.ctrl_tva.SetDigits(2)
        
        # Code comptable
        self.label_code_comptable = wx.StaticText(self, -1, _(u"Code compta :"))
        self.ctrl_code_comptable = wx.TextCtrl(self, -1, u"")
        self.ctrl_code_comptable.SetMinSize((80, -1))

        # Tarification
        self.staticbox_tarification_staticbox = wx.StaticBox(self, -1, _(u"Tarification"))
        self.track_tarif = Track_tarif(dictDonnees={"lignes" : self.Importation_lignes()})
        filtre_methodes = ("montant_unique", "qf")
        self.ctrl_tarification = CTRL_Tarification_calcul.Panel(self, IDactivite=None, IDtarif=None, track_tarif=self.track_tarif, filtre_methodes=filtre_methodes)

        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixCategorie, self.ctrl_categorie)
        self.Bind(wx.EVT_CHOICE, self.OnChoixActivite, self.ctrl_activite)
        self.Bind(wx.EVT_CHOICE, self.OnChoixCategorieTarif, self.ctrl_categorie_tarif)
        self.Bind(wx.EVT_CHOICE, self.OnChoixTarif, self.ctrl_tarif)
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
        if self.IDmodele != None :
            self.Importation() 

    def __set_properties(self):
        self.ctrl_categorie.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici la catégorie de la prestation")))
        self.ctrl_label.SetToolTip(wx.ToolTip(_(u"Saisissez un intitulé pour cette prestation")))
        self.radio_type_familiale.SetToolTip(wx.ToolTip(_(u"Selectionnez cette case si la prestation concerne toute la famille")))
        self.radio_type_individuelle.SetToolTip(wx.ToolTip(_(u"Selectionnez cette case si la prestation ne concerne qu'un individu")))
        self.ctrl_activite.SetToolTip(wx.ToolTip(_(u"Selectionnez ici l'activité concernée par la prestation")))
        self.ctrl_categorie_tarif.SetToolTip(wx.ToolTip(_(u"Selectionnez ici la catégorie de tarif rattaché a cette prestation")))
        self.ctrl_tarif.SetToolTip(wx.ToolTip(_(u"Selectionnez un tarif parmi ceux proposés")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))
        self.ctrl_tva.SetToolTip(wx.ToolTip(_(u"Saisissez le taux de TVA inclus [Optionnel]")))
        self.ctrl_code_comptable.SetToolTip(wx.ToolTip(_(u"Saisissez le code comptable de cette prestation si vous souhaitez utiliser l'export vers les logiciels de comptabilité [Optionnel]")))
        self.ctrl_label.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, u""))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=6, cols=2, vgap=10, hgap=10)
        grid_sizer_type = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_type, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_type.Add(self.radio_type_familiale, 0, 0, 0)
        grid_sizer_type.Add(self.radio_type_individuelle, 0, 0, 0)
        grid_sizer_type.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_type, 1, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_generalites, 1, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_activite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_activite, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_categorie_tarif, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_categorie_tarif, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_tarif, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_tarif, 0, wx.EXPAND, 0)

        # TVA + code comptable
        grid_sizer_options.Add(self.label_tva, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tva = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_tva.Add(self.ctrl_tva, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tva.Add( (5, 5), 1, wx.EXPAND, 0)
        grid_sizer_tva.Add(self.label_code_comptable, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tva.Add( self.ctrl_code_comptable, 0, 0, 0)
        grid_sizer_tva.AddGrowableCol(1)
        grid_sizer_options.Add(grid_sizer_tva, 1, wx.EXPAND, 0)

        grid_sizer_options.AddGrowableCol(1)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_options, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Déductions
        staticbox_tarification = wx.StaticBoxSizer(self.staticbox_tarification_staticbox, wx.VERTICAL)
        grid_sizer_tarification = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_tarification.Add(self.ctrl_tarification, 1, wx.EXPAND, 0)
        grid_sizer_tarification.AddGrowableRow(0)
        grid_sizer_tarification.AddGrowableCol(0)
        staticbox_tarification.Add(grid_sizer_tarification, 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.Add(staticbox_tarification, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnChoixCategorie(self, event): 
        pass

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
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            listeCategoriesTarifs = UTILS_Texte.ConvertStrToListe(categories_tarifs)
            
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

    def Importation_lignes(self):
        if self.IDmodele == None :
            return []

        DB = GestionDB.DB()
        req = """SELECT %s FROM tarifs_lignes WHERE IDmodele=%d ORDER BY num_ligne;""" % (", ".join(CHAMPS_TABLE_LIGNES), self.IDmodele)
        DB.ExecuterReq(req)
        listeDonneesLignes = DB.ResultatReq()
        DB.Close()

        # Importation des lignes de tarifs
        liste_lignes = []
        for ligne in listeDonneesLignes:
            dictLigne = {}
            index = 0
            for valeur in ligne:
                dictLigne[CHAMPS_TABLE_LIGNES[index]] = valeur
                index += 1
            liste_lignes.append(dictLigne)
            self.listeInitialeIDlignes.append(dictLigne["IDligne"])
        return liste_lignes

    def Importation(self):
        """ Importation des données """
        DB = GestionDB.DB()
        req = """SELECT categorie, label, IDactivite, IDtarif, IDcategorie_tarif, code_compta, tva, public, IDtype_quotient
        FROM modeles_prestations 
        WHERE IDmodele=%d;""" % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0: return
        categorie, label, IDactivite, IDtarif, IDcategorie_tarif, code_compta, tva, public, IDtype_quotient = listeDonnees[0]

        # Label
        self.ctrl_label.SetValue(label)
        # Catégorie
        self.ctrl_categorie.SetCategorie(categorie)
        # Activité
        if IDactivite != None:
            self.ctrl_activite.SetID(IDactivite)
        if categorie == "cotisation":
            self.ctrl_activite.Enable(False)
        # Catégorie de tarif
        self.OnChoixActivite(None)
        self.ctrl_categorie_tarif.SetID(IDcategorie_tarif)
        # Tarif
        self.OnChoixCategorieTarif(None)
        self.ctrl_tarif.SetID(IDtarif)
        # Code comptable
        if code_compta != None:
            self.ctrl_code_comptable.SetValue(code_compta)
        # TVA
        if tva != None:
            self.ctrl_tva.SetValue(tva)
        # Public
        if public == "famille" :
            self.radio_type_familiale.SetValue(True)
        else :
            self.radio_type_individuelle.SetValue(True)
        # Tarification
        self.ctrl_tarification.SetTypeQuotient(IDtype_quotient)

    def OnBoutonOk(self, event):
        # Récupération et vérification des données saisies
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

        code_comptable = self.ctrl_code_comptable.GetValue() 
        if code_comptable == "" :
            code_comptable = None
        tva = self.ctrl_tva.GetValue()
        if tva == 0.0 :
            tva = None

        if self.radio_type_familiale.GetValue() == True :
            public = "famille"
        else :
            public = "individu"

        # Tarification
        IDtype_quotient = self.ctrl_tarification.GetTypeQuotient()

        # Validation de la tarification
        if self.ctrl_tarification.Validation() == False :
            return False

        # Sauvegarde de la prestation
        listeDonnees = [    
                ("categorie", categorie),
                ("label", label),
                ("IDactivite", IDactivite),
                ("IDtarif", IDtarif),
                ("IDcategorie_tarif", IDcategorie_tarif),
                ("code_compta", code_comptable),
                ("tva", tva),
                ("public", public),
                ("IDtype_quotient", IDtype_quotient),
                ]
        DB = GestionDB.DB()
        if self.IDmodele == None :
            self.IDmodele = DB.ReqInsert("modeles_prestations", listeDonnees)
        else:
            DB.ReqMAJ("modeles_prestations", listeDonnees, "IDmodele", self.IDmodele)

        # Sauvegarde des lignes de tarifs
        self.ctrl_tarification.Sauvegarde()

        listeFinaleID = []
        for track_ligne in self.track_tarif.lignes:
            track_ligne.IDmodele = self.IDmodele
            listeDonnees = track_ligne.Get_listedonnees_pour_db()

            if track_ligne.IDligne == None:
                # Ci-dessous pour parer bug de Last_row_id de Sqlite
                if DB.isNetwork == False:
                    req = """SELECT max(IDligne) FROM tarifs_lignes;"""
                    DB.ExecuterReq(req)
                    listeTemp = DB.ResultatReq()
                    if listeTemp[0][0] == None:
                        newID = 1
                    else:
                        newID = listeTemp[0][0] + 1
                    listeDonnees.append(("IDligne", newID))
                    DB.ReqInsert("tarifs_lignes", listeDonnees)
                else:
                    # Version MySQL
                    DB.ReqInsert("tarifs_lignes", listeDonnees)
            else:
                # Modification
                DB.ReqMAJ("tarifs_lignes", listeDonnees, "IDligne", track_ligne.IDligne)
                listeFinaleID.append(track_ligne.IDligne)

        # Suppression des lignes supprimées
        for IDligne in self.listeInitialeIDlignes:
            if IDligne not in listeFinaleID:
                DB.ReqDEL("tarifs_lignes", "IDligne", IDligne)

        DB.Close()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDmodele(self):
        return self.IDmodele




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmodele=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()

