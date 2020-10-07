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
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Synthese_conso
from Utils import UTILS_Questionnaires
from Dlg import DLG_Selection_activite



def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text



class CTRL_Groupes(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.listeGroupes = []
        self.dictGroupes = {}
        
    def SetActivite(self, IDactivite=None):
        self.IDactivite = IDactivite
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeGroupes, self.dictGroupes = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeGroupes = []
        dictGroupes = {}
        if self.IDactivite == None :
            return listeGroupes, dictGroupes 
        DB = GestionDB.DB()
        req = """SELECT IDgroupe, IDactivite, nom
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY nom;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDgroupe, IDactivite, nom in listeDonnees :
            dictTemp = { "nom" : nom, "IDactivite" : IDactivite}
            dictGroupes[IDgroupe] = dictTemp
            listeGroupes.append((nom, IDgroupe))
        listeGroupes.sort()
        return listeGroupes, dictGroupes

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDgroupe in self.listeGroupes :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeGroupes)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeGroupes[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeGroupes)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeGroupes)):
            ID = self.listeGroupes[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def GetListeGroupes(self):
        return self.GetIDcoches() 
    
    def GetDictGroupes(self):
        return self.dictGroupes
    
    def GetNomsGroupes(self):
        listeLabels = []
        for IDgroupe in self.GetIDcoches() :
            listeLabels.append(self.dictGroupes[IDgroupe]["nom"])
        return ", ".join(listeLabels)
    
# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Choix_valeurs(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        self.listeLabels = [_(u"Quantité"), _(u"Temps de présence"), _(u"Temps facturé")]
        self.SetItems(self.listeLabels)
        self.Select(0)

    def GetValeur(self):
        index = self.GetSelection()
        if index == 0 : return "quantite"
        if index == 1 : return "temps_presence"
        if index == 2 : return "temps_facture"


# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Choix_colonnes(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.MAJ()

    def MAJ(self):
        self.listeLabels = [_(u"Unités"), _(u"Unités + groupes"), _(u"Unités + événements")]
        self.SetItems(self.listeLabels)
        self.Select(0)

    def GetValeur(self):
        index = self.GetSelection()
        if index == 0: return "unites"
        if index == 1: return "unites_groupes"
        if index == 2: return "unites_evenements"


# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Choix_lignes(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeDonnees = [
            {"label" : _(u"Date"), "code" : "jour"},
            {"label" : _(u"Mois"), "code" : "mois"},
            {"label" : _(u"Année"), "code" : "annee"},
            {"label" : _(u"Activité"), "code" : "activite"},
            {"label" : _(u"Groupe"), "code" : "groupe"},
            {"label" : _(u"Evènement"), "code": "evenement"},
            {"label" : _(u"Evènement (avec date)"), "code": "evenement_date"},
            {"label" : _(u"Etiquette"), "code": "etiquette"},
            {"label" : _(u"Catégorie de tarif"), "code" : "categorie_tarif"},
            {"label" : _(u"Ville de résidence"), "code" : "ville_residence"},
            {"label" : _(u"Secteur géographique"), "code" : "secteur"},
            {"label" : _(u"Genre (M/F)"), "code" : "genre"},
            {"label" : _(u"Age"), "code" : "age"},
            {"label" : _(u"Ville de naissance"), "code" : "ville_naissance"},
            {"label" : _(u"Ecole"), "code" : "nom_ecole"},
            {"label" : _(u"Classe"), "code" : "nom_classe"},
            {"label" : _(u"Niveau scolaire"), "code" : "nom_niveau_scolaire"},
            {"label" : _(u"Famille"), "code" : "famille"},
            {"label" : _(u"Individu"), "code" : "individu"},
            {"label" : _(u"Régime social"), "code" : "regime"},
            {"label" : _(u"Caisse d'allocations"), "code" : "caisse"},
            {"label" : _(u"Quotient familial"), "code" : "qf"},
            {"label" : _(u"Catégorie de travail"), "code" : "categorie_travail"},
            {"label" : _(u"Catégorie de travail du père"), "code" : "categorie_travail_pere"},
            {"label" : _(u"Catégorie de travail de la mère"), "code" : "categorie_travail_mere"},
            ]
        
        # Intégration des questionnaires
        q = UTILS_Questionnaires.Questionnaires() 
        for public in ("famille", "individu") :
            for dictTemp in q.GetQuestions(public) :
                label = _(u"Question %s. : %s") % (public[:3], dictTemp["label"])
                if len(label) > 45: label = label[:45] + "..."
                code = "question_%s_%d" % (public, dictTemp["IDquestion"])
                self.listeDonnees.append({"label" : label, "code" : code})

        self.MAJ() 

    def MAJ(self):
        listeLabels = []
        for dictTemp in self.listeDonnees :
            listeLabels.append(dictTemp["label"])
        self.SetItems(listeLabels)
        self.Select(0)

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeDonnees[index]["code"]

# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Choix_mode(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        self.listeLabels = [_(u"Réservation"), _(u"Attente"), _(u"Refus")]
        self.SetItems(self.listeLabels)
        self.Select(0)

    def GetValeur(self):
        index = self.GetSelection()
        if index == 0 : return "reservation"
        if index == 1 : return "attente"
        if index == 2 : return "refus"
    
    def GetLabel(self):
        return self.GetStringSelection()

# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Choix_etat(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1) 
        self.parent = parent
        self.SetMinSize((-1, 80))
        self.MAJ() 
    
    def MAJ(self):
        self.listeLabels = [_(u"Pointage en attente"), _(u"Présent"), _(u"Absence justifiée"), _(u"Absence injustifiée")]
        self.SetItems(self.listeLabels)
        self.Check(0)
        self.Check(1)

    def GetValeur(self):
        listeSelections = []
        if self.IsChecked(0) : listeSelections.append("reservation")
        if self.IsChecked(1) : listeSelections.append("present")
        if self.IsChecked(2) : listeSelections.append("absentj")
        if self.IsChecked(3) : listeSelections.append("absenti")
        return listeSelections
    
    def GetLabels(self):
        listeLabels = []
        for code in self.GetValeur() :
            if code == "reservation" : listeLabels.append(_(u"Réservation"))
            if code == "present" : listeLabels.append(_(u"Présent"))
            if code == "absentj" : listeLabels.append(_(u"Absence justifiée"))
            if code == "absenti" : listeLabels.append(_(u"Absence injustifiée"))
        return ", ".join(listeLabels)

# ----------------------------------------------------------------------------------------------------------------------------------

class Parametres(wx.Panel):
    def __init__(self, parent, listview=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listview = listview

        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Période de référence"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.ctrl_date_debut.SetDate(datetime.date(datetime.date.today().year, 1, 1))
        self.ctrl_date_fin.SetDate(datetime.date(datetime.date.today().year, 12, 31))
        
        # Activité
        self.box_activite_staticbox = wx.StaticBox(self, -1, _(u"Activité"))
        self.ctrl_activite = DLG_Selection_activite.Panel_Activite(self, callback=self.OnSelectionActivite)
        self.ctrl_activite.SetMinSize((200, -1))
        
        # Groupes
        self.box_groupes_staticbox = wx.StaticBox(self, -1, _(u"Groupes"))
        self.ctrl_groupes = CTRL_Groupes(self)
        self.ctrl_groupes.SetMinSize((200, 50))

        # Affichage
        self.box_affichage_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_lignes = wx.StaticText(self, -1, _(u"Lignes :"))
        self.ctrl_lignes = CTRL_Choix_lignes(self)
        self.label_colonnes = wx.StaticText(self, -1, _(u"Colonnes :"))
        self.ctrl_colonnes = CTRL_Choix_colonnes(self)
        self.label_valeurs = wx.StaticText(self, -1, _(u"Valeurs :"))
        self.ctrl_valeurs = CTRL_Choix_valeurs(self)
        self.label_mode = wx.StaticText(self, -1, _(u"Mode :"))
        self.ctrl_mode = CTRL_Choix_mode(self)
        self.label_etat = wx.StaticText(self, -1, _(u"Etat :"))
        self.ctrl_etat = CTRL_Choix_etat(self)

        # Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKLISTBOX, self.Actualiser, self.ctrl_groupes)
        self.Bind(wx.EVT_CHOICE, self.Actualiser, self.ctrl_valeurs)
        self.Bind(wx.EVT_CHOICE, self.Actualiser, self.ctrl_lignes)
        self.Bind(wx.EVT_CHOICE, self.Actualiser, self.ctrl_colonnes)
        self.Bind(wx.EVT_CHOICE, self.OnChoixMode, self.ctrl_mode) 
        self.Bind(wx.EVT_CHECKLISTBOX, self.Actualiser, self.ctrl_etat)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de période")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de période")))
        self.ctrl_activite.SetToolTip(wx.ToolTip(_(u"Sélectionnez une activité")))
        self.ctrl_groupes.SetToolTip(wx.ToolTip(_(u"Cochez les groupes à prendre en compte")))
        self.ctrl_valeurs.SetToolTip(wx.ToolTip(_(u"Sélectionnez le type de données à afficher")))
        self.ctrl_lignes.SetToolTip(wx.ToolTip(_(u"Sélectionnez le type de données par ligne")))
        self.ctrl_colonnes.SetToolTip(wx.ToolTip(_(u"Sélectionnez le type de données par colonne")))
        self.bouton_actualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour actualiser la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)

        # Date de référence
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_periode, 1, wx.EXPAND, 0)

        # Activité
        box_activite = wx.StaticBoxSizer(self.box_activite_staticbox, wx.VERTICAL)
        box_activite.Add(self.ctrl_activite, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_activite, 1, wx.EXPAND, 0)
        
        # Groupes
        box_groupes = wx.StaticBoxSizer(self.box_groupes_staticbox, wx.VERTICAL)
        box_groupes.Add(self.ctrl_groupes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_groupes, 1, wx.EXPAND, 0)
        
        # affichage
        box_affichage = wx.StaticBoxSizer(self.box_affichage_staticbox, wx.VERTICAL)
        grid_sizer_affichage = wx.FlexGridSizer(rows=5, cols=2, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.label_lignes, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.ctrl_lignes, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.label_colonnes, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.ctrl_colonnes, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.label_valeurs, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.ctrl_valeurs, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.label_mode, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.ctrl_mode, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.label_etat, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_affichage.Add(self.ctrl_etat, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.AddGrowableCol(1)
        box_affichage.Add(grid_sizer_affichage, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_affichage, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.bouton_actualiser, 0, wx.EXPAND|wx.TOP, 5)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
    
    def OnChoixDate(self):
        self.Actualiser() 

    def OnSelectionActivite(self):
        IDactivite = self.ctrl_activite.GetID()
        self.ctrl_groupes.SetActivite(IDactivite)
        self.Actualiser() 
        
    def OnChoixMode(self, event):
        if self.ctrl_mode.GetValeur() == "reservation" :
            self.ctrl_etat.Enable(True)
        else :
            self.ctrl_etat.Enable(False)
        self.Actualiser() 
            
    def OnBoutonActualiser(self, event): 
        # Vérifications
        if self.ctrl_date_debut.GetDate()  == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune date de début !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.ctrl_date_fin.GetDate()  == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune date de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.ctrl_activite.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(self.ctrl_groupes.GetListeGroupes()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins un groupe !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(self.ctrl_etat.GetValeur()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un état !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # MAJ
        self.Actualiser() 

    def Actualiser(self, event=None):
        """ MAJ du tableau """
        date_debut = self.ctrl_date_debut.GetDate() 
        date_fin = self.ctrl_date_fin.GetDate() 
        IDactivite = self.ctrl_activite.GetID()
        listeGroupes = self.ctrl_groupes.GetListeGroupes()
        affichage_valeurs = self.ctrl_valeurs.GetValeur()
        affichage_lignes = self.ctrl_lignes.GetValeur()
        affichage_colonnes = self.ctrl_colonnes.GetValeur()
        affichage_mode = self.ctrl_mode.GetValeur() 
        affichage_etat = self.ctrl_etat.GetValeur()
        
        # Vérifications
        if date_debut == None :
            self.parent.ctrl_resultats.ResetGrid()
            return False

        if date_fin == None :
            self.parent.ctrl_resultats.ResetGrid()
            return False

        if IDactivite == None :
            self.parent.ctrl_resultats.ResetGrid()
            return False

        if len(listeGroupes) == 0 :
            self.parent.ctrl_resultats.ResetGrid()
            return False
        
        # Label Paramètres
        listeParametres = [ 
            _(u"Période du %s au %s") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin))),
            _(u"Activité : %s") % self.ctrl_activite.GetNomActivite(),
            _(u"Groupes : %s") % self.ctrl_groupes.GetNomsGroupes(),
            _(u"Mode : %s") % self.ctrl_mode.GetLabel(),
            _(u"Etats : %s") % self.ctrl_etat.GetLabels(),
            ]
        labelParametres = " | ".join(listeParametres)
        
        # MAJ
        self.parent.ctrl_resultats.MAJ(date_debut=date_debut, date_fin=date_fin, IDactivite=IDactivite, listeGroupes=listeGroupes,
                                                    affichage_valeurs=affichage_valeurs, affichage_lignes=affichage_lignes, affichage_colonnes=affichage_colonnes,
                                                    affichage_mode=affichage_mode, affichage_etat=affichage_etat, labelParametres=labelParametres)



# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici éditer une synthèse des consommations pour une période et une activité données. Commencez par sélectionner une date de début et de fin puis choisissez une activité. Vous pouvez affiner vos résultats et modifier l'affichage des données grâce aux options proposées.")
        titre = _(u"Synthèse des consommations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Diagramme.png")
        
        # Liste
        self.staticbox_resultats_staticbox = wx.StaticBox(self, -1, _(u"Résultats"))
        self.ctrl_resultats = CTRL_Synthese_conso.CTRL(self)
        self.ctrl_resultats.SetMinSize((50, 50)) 
        
        # Paramètres
        self.ctrl_parametres = Parametres(self, listview=self.ctrl_resultats)
        
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)


    def __set_properties(self):
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu de la liste (PDF)")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((980, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        box_resultats = wx.StaticBoxSizer(self.staticbox_resultats_staticbox, wx.HORIZONTAL)
        
        # Liste de resultats
        box_resultats.Add(self.ctrl_resultats, 1, wx.EXPAND|wx.ALL, 5)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_excel, 0, 0, 0)
        box_resultats.Add(grid_sizer_commandes, 0, wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 5)
        
        grid_sizer_droit.Add(box_resultats, 1, wx.EXPAND, 0)

        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)

        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def Apercu(self, event):
        self.ctrl_resultats.Apercu()

    def ExportTexte(self, event):
        self.ctrl_resultats.ExportTexte()

    def ExportExcel(self, event):
        self.ctrl_resultats.ExportExcel()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Synthsedesconsommations")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
