#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import time
import sys
import wx.lib.agw.hyperlink as hl

import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Selection_activites
from Ctrl import CTRL_Saisie_date
from Dlg import DLG_calendrier_simple
from Ctrl import CTRL_Synthese_prestations
from Utils import UTILS_Questionnaires
from Utils import UTILS_Parametres
from Utils import UTILS_Dialogs



def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


class CTRL_Regroupement(wx.Choice):
    def __init__(self, parent, option_aucun=False):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.listeDonnees = [
            {"label": _(u"Jour"), "code": "jour"},
            {"label": _(u"Mois"), "code": "mois"},
            {"label": _(u"Année"), "code": "annee"},
            {"label": _(u"Label de la prestation"), "code": "label_prestation"},
            {"label": _(u"Activité"), "code": "activite"},
            {"label": _(u"Catégorie de tarif"), "code": "categorie_tarif"},
            {"label": _(u"Famille"), "code": "famille"},
            {"label": _(u"Individu"), "code": "individu"},
            {"label": _(u"Ville de résidence"), "code": "ville_residence"},
            {"label": _(u"Secteur géographique"), "code": "secteur"},
            {"label": _(u"Age"), "code": "age"},
            {"label": _(u"Ville de naissance"), "code": "ville_naissance"},
            {"label": _(u"Ecole"), "code": "nom_ecole"},
            {"label": _(u"Classe"), "code": "nom_classe"},
            {"label": _(u"Niveau scolaire"), "code": "nom_niveau_scolaire"},
            {"label": _(u"Régime social"), "code": "regime"},
            {"label": _(u"Caisse d'allocations"), "code": "caisse"},
            {"label": _(u"Quotient familial - Tranches tarifs"), "code": "qf_tarifs"},
            {"label": _(u"Quotient familial - Tranches de 100"), "code": "qf_100"},
            {"label": _(u"Numéro de facture"), "code": "num_facture"},
            {"label": _(u"Numéro de facture + famille"), "code": "num_facture_famille"},
        ]

        if option_aucun == True :
            self.listeDonnees.insert(0, {"label": _(u"Aucun"), "code": ""})

        # Intégration des questionnaires
        q = UTILS_Questionnaires.Questionnaires()
        for public in ("famille", "individu"):
            for dictTemp in q.GetQuestions(public):
                label = _(u"Question %s. : %s") % (public[:3], dictTemp["label"])
                code = "question_%s_%d" % (public, dictTemp["IDquestion"])
                self.listeDonnees.append({"label": label, "code": code})

        self.MAJ()

    def MAJ(self):
        listeLabels = []
        for dictTemp in self.listeDonnees:
            listeLabels.append(dictTemp["label"])
        self.SetItems(listeLabels)
        self.Select(0)

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeDonnees[index]["code"]

    def SetValeur(self, code=""):
        index = 0
        for dictTemp in self.listeDonnees :
            if dictTemp["code"] == code :
                self.Select(index)
            index += 1

# ----------------------------------------------------------------------------------------------------------------------------------


class CTRL_Mode(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeDonnees = [
            (_(u"Nombre de prestations"), "nbre"),
            (_(u"Montant des prestations"), "facture"),
            (_(u"Montant des prestations réglées"), "regle"),
            (_(u"Montant des prestations impayées"), "impaye"),
            (u"---------------------------------------------", None),
            (_(u"Nombre de prestations facturées"), "nbre_facturees"),
            (_(u"Montant des prestations facturées"), "facture_facturees"),
            (_(u"Montant des prestations réglées et facturées"), "regle_facturees"),
            (_(u"Montant des prestations impayées et facturées"), "impaye_facturees"),
            (u"---------------------------------------------", None),
            (_(u"Nombre de prestations non facturées"), "nbre_nonfacturees"),
            (_(u"Montant des prestations non facturées"), "facture_nonfacturees"),
            (_(u"Montant des prestations réglées et non facturées"), "regle_nonfacturees"),
            (_(u"Montant des prestations impayées et non facturées"), "impaye_nonfacturees"),
            ]
        self.Remplissage() 
    
    def Remplissage(self):
        listeLabels = []
        for label, code in self.listeDonnees :
            listeLabels.append(label)
        self.SetItems(listeLabels)
    
    def SetID(self, ID=""):
        index = 0
        for label, code in self.listeDonnees :
            if code == ID :
                self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index][1]

    def GetLabel(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index][0]



class ChoixPeriode(wx.Panel):
    def __init__(self, parent, type="", label=u"", infobulle=u""):
        wx.Panel.__init__(self, parent, id=-1, name="panel_choix_periode", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.type = type

        self.check = wx.CheckBox(self, -1, label)
        self.label_du = wx.StaticText(self, -1, u"du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        self.label_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        
        # Propriétés
        self.check.SetToolTip(wx.ToolTip(infobulle))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin")))
        self.ctrl_date_debut.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.ctrl_date_debut.SetMinSize((70, 18))
        self.ctrl_date_fin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.ctrl_date_fin.SetMinSize((70, 18))
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check)
        
        # Layout
        grid_sizer = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer.Add(self.check, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_dates.Add(self.label_du, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer.Add(grid_sizer_dates, 0, wx.LEFT|wx.EXPAND, 18)
        self.SetSizer(grid_sizer)

        # Init contrôles
        self.ActiveControles() 
    
    def ActiveControles(self):
        self.ctrl_date_debut.Enable(self.check.GetValue())
        self.ctrl_date_fin.Enable(self.check.GetValue())
        self.label_du.Enable(self.check.GetValue())
        self.label_au.Enable(self.check.GetValue())
        
    def OnCheck(self, event):
        self.ActiveControles() 
        self.ctrl_date_debut.SetFocus() 
        self.GetParent().parent.MAJ()
    
    def GetEtat(self):
        return self.check.GetValue() 
    
    def GetDateDebut(self):
        return self.ctrl_date_debut.GetDate()

    def GetDateFin(self):
        return self.ctrl_date_fin.GetDate()



class Parametres(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Période de référence"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        self.bouton_date_debut = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        self.bouton_date_fin = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))
        
        # Filtres
        self.staticbox_affichage_staticbox = wx.StaticBox(self, -1, _(u"Types de prestations"))
        self.radio_cotisations = wx.CheckBox(self, -1, _(u"Cotisations"))
        self.radio_consommations = wx.CheckBox(self, -1, _(u"Consommations"))
        self.radio_locations = wx.CheckBox(self, -1, _(u"Locations"))
        self.radio_autres = wx.CheckBox(self, -1, _(u"Autres"))
        self.radio_cotisations.SetValue(True)
        self.radio_consommations.SetValue(True)
        self.radio_locations.SetValue(True)
        self.radio_autres.SetValue(True)
        
        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        self.ctrl_activites.SetMinSize((-1, 90))
        
        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
##        self.options_cotisations = ChoixPeriode(self, type="cotisations", label=_(u"Uniquement les cotisations déposées"))
        self.options_reglements = ChoixPeriode(self, type="reglements", label=_(u"Uniquement les règlements saisis"), infobulle=_(u"Ne seront considérés dans le calcul que les règlements saisis sur la période indiquée"))
        self.options_depots = ChoixPeriode(self, type="depots", label=_(u"Uniquement les règlements déposés"), infobulle=_(u"Ne seront considérés dans le calcul que les règlements qui ont été déposés en banque sur la période indiquée"))
        
        # Boutons Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")
        self.bouton_actualiser.SetMinSize((-1, 50)) 

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDateDebut, self.bouton_date_debut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDateFin, self.bouton_date_fin)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCotisations, self.radio_cotisations)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckConsommations, self.radio_consommations)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckLocations, self.radio_locations)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAutres, self.radio_autres)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        
    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de période")))
        self.bouton_date_debut.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner la date de début dans un calendrier")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de période")))
        self.bouton_date_fin.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner la date de fin dans un calendrier")))
        self.radio_cotisations.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les cotisations dans la synthèse")))
        self.radio_consommations.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les consommations dans la synthèse")))
        self.radio_locations.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les locations dans la synthèse")))
        self.radio_autres.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les autres types de prestations dans la synthèse")))
        self.bouton_actualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour actualiser les résultats en fonction des paramètres sélectionnés")))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Date de référence
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=3, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.bouton_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.bouton_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_periode, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Filtres 
        staticbox_affichage = wx.StaticBoxSizer(self.staticbox_affichage_staticbox, wx.VERTICAL)
        grid_sizer_affichage = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.radio_cotisations, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 18)
        grid_sizer_affichage.Add(self.radio_consommations, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.radio_locations, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 18)
        grid_sizer_affichage.Add(self.radio_autres, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_affichage.Add(grid_sizer_affichage, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_affichage, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Activités
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        staticbox_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_activites, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        
##        grid_sizer_options.Add(self.options_cotisations, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.options_reglements, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.options_depots, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_options, 1, wx.RIGHT|wx.EXPAND, 5)

        # Bouton Actualiser
        grid_sizer_base.Add(self.bouton_actualiser, 1, wx.RIGHT|wx.EXPAND, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
            
    def OnBoutonDateDebut(self, event): 
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date_debut.SetDate(date)
            self.parent.MAJ()
        dlg.Destroy()

    def OnBoutonDateFin(self, event): 
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date_fin.SetDate(date)
            self.parent.MAJ()
        dlg.Destroy()
        
    def OnCheckCotisations(self, event):
        self.parent.MAJ()
        
    def OnCheckConsommations(self, event):
        self.parent.MAJ()

    def OnCheckLocations(self, event):
        self.parent.MAJ()

    def OnCheckAutres(self, event):
        self.parent.MAJ()

    def OnBoutonActualiser(self, event):
        """ Validation des données saisies """
        # Vérifie date de référence
        date_debut = self.ctrl_date_debut.GetDate()
        if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
            dlg = wx.MessageDialog(self, _(u"La date de début de période ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        date_fin = self.ctrl_date_fin.GetDate()
        if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
            dlg = wx.MessageDialog(self, _(u"La date de fin de période ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False
        
        # Envoi des données
        self.parent.MAJ()
        
        return True
    
    def OnCheckActivites(self):
        self.parent.MAJ()
    
    def GetActivites(self):
        return self.ctrl_activites.GetActivites() 
    

# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Cette fonction vous permet de quantifier précisément les prestations facturées sur une période donnée. Commencez par saisir une période puis sélectionnez un groupe d'activités.")
        titre = _(u"Synthèse des prestations")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Diagramme.png")
        self.SetTitle(titre)
        
        # Panel Paramètres
        self.ctrl_parametres = Parametres(self)
        
        # CTRL résultats
        self.staticbox_stats_staticbox = wx.StaticBox(self, -1, _(u"Résultats"))

        self.label_lignes_1 = wx.StaticText(self, -1, _(u"Ligne :"))
        self.ctrl_lignes_1 = CTRL_Regroupement(self)
        self.ctrl_lignes_1.SetMinSize((50, -1))

        self.label_lignes_2 = wx.StaticText(self, -1, _(u"Détail :"))
        self.ctrl_lignes_2 = CTRL_Regroupement(self, option_aucun=True)
        self.ctrl_lignes_2.SetMinSize((50, -1))

        self.label_colonnes = wx.StaticText(self, -1, _(u"Colonnes :"))
        self.ctrl_colonnes = CTRL_Regroupement(self)
        self.ctrl_colonnes.SetMinSize((50, -1))

        self.label_mode_affichage = wx.StaticText(self, -1, _(u"Données :"))
        self.ctrl_mode = CTRL_Mode(self)
        self.ctrl_mode.SetMinSize((50, -1))

        self.ctrl_stats = CTRL_Synthese_prestations.CTRL(self)
        self.ctrl_stats.SetMinSize((100, 100))

        # Commandes de liste
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))

        # Commandes de résultats
        self.check_details_total = wx.CheckBox(self, -1, _(u"Afficher le détail de la ligne total"))
        self.check_details_total.SetValue(True)

        self.hyper_developper = self.Build_Hyperlink_developper()
        self.label_barre = wx.StaticText(self, -1, u"|")
        self.hyper_reduire = self.Build_Hyperlink_reduire()
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_colonnes)
        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_lignes_1)
        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_lignes_2)
        self.Bind(wx.EVT_CHOICE, self.MAJ, self.ctrl_mode)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDetailsTotal, self.check_details_total)

        self.__set_properties()
        self.__do_layout()
                
        # Initialisation des contrôles
        anneeActuelle = datetime.date.today().year
        self.ctrl_parametres.ctrl_date_debut.SetDate(datetime.date(anneeActuelle, 1, 1))
        self.ctrl_parametres.ctrl_date_fin.SetDate(datetime.date(anneeActuelle, 12, 31))

        # Récupération des paramètres
        dictParametres = {"ligne" : "activite", "detail" : "label_prestation", "colonnes" : "mois", "donnees" : "facture", "detail_total" : False}
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="dlg_synthese_prestations", dictParametres=dictParametres)

        self.ctrl_colonnes.SetValeur(dictParametres["colonnes"])
        self.ctrl_lignes_1.SetValeur(dictParametres["ligne"])
        self.ctrl_lignes_2.SetValeur(dictParametres["detail"])
        self.ctrl_mode.SetID(dictParametres["donnees"])
        self.check_details_total.SetValue(dictParametres["detail_total"])
        self.ctrl_stats.SetAffichageDetailsTotal(dictParametres["detail_total"])

        self.MAJ() 

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu avant impression des résultats (PDF)")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter les résultats au format MS Excel")))
        self.ctrl_mode.SetToolTip(wx.ToolTip(_(u"Sélectionnez le mode d'affichage souhaité")))
        self.check_details_total.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher les détails de la ligne total")))
        self.SetMinSize((990, 730))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # Résultats
        staticbox_stats= wx.StaticBoxSizer(self.staticbox_stats_staticbox, wx.VERTICAL)
        grid_sizer_contenu2 = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)

        grid_sizer_affichage = wx.FlexGridSizer(rows=2, cols=5, vgap=5, hgap=5)

        grid_sizer_affichage.Add(self.label_lignes_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.ctrl_lignes_1, 0, wx.EXPAND, 0)
        grid_sizer_affichage.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_affichage.Add(self.label_colonnes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.ctrl_colonnes, 0, wx.EXPAND, 0)

        grid_sizer_affichage.Add(self.label_lignes_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.ctrl_lignes_2, 0, wx.EXPAND, 0)
        grid_sizer_affichage.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_affichage.Add(self.label_mode_affichage, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.ctrl_mode, 0, wx.EXPAND, 0)

        grid_sizer_affichage.AddGrowableCol(1)
        grid_sizer_affichage.AddGrowableCol(4)

        grid_sizer_contenu2.Add(grid_sizer_affichage, 1, wx.EXPAND, 0)
        grid_sizer_contenu2.Add( (5, 5), 1, wx.EXPAND, 0)

        grid_sizer_contenu2.Add(self.ctrl_stats, 1, wx.EXPAND, 0)
        
        # Boutons de liste
        grid_sizer_commandes = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_excel, 0, wx.EXPAND, 0)
        grid_sizer_contenu2.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        # Commandes de liste
        grid_sizer_commandes2 = wx.FlexGridSizer(rows=1, cols=11, vgap=5, hgap=5)
        grid_sizer_commandes2.Add( (30, 5), 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add(self.check_details_total, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes2.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add(self.hyper_developper, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes2.Add(self.label_barre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes2.Add(self.hyper_reduire, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes2.AddGrowableCol(0)
        grid_sizer_contenu2.Add(grid_sizer_commandes2, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu2.AddGrowableRow(1)
        grid_sizer_contenu2.AddGrowableCol(0)
        
        staticbox_stats.Add(grid_sizer_contenu2, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(staticbox_stats, 1, wx.RIGHT|wx.EXPAND, 5)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
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
        self.SetMinSize(self.GetSize())
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()

    def Build_Hyperlink_developper(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, _(u"Tout développer"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_developper)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Tout développer")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_developper(self, event):
        self.ctrl_stats.DevelopperTout()

    def Build_Hyperlink_reduire(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, _(u"Tout réduire"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_reduire)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Tout réduire")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_reduire(self, event):
        self.ctrl_stats.ReduireTout()

    def OnCheckDetailsTotal(self, event):
        etat = self.check_details_total.GetValue()
        self.ctrl_stats.SetAffichageDetailsTotal(etat)
        self.MAJ()

    def MAJ(self, event=None):
        self.ctrl_stats.date_debut = self.ctrl_parametres.ctrl_date_debut.GetDate()
        self.ctrl_stats.date_fin = self.ctrl_parametres.ctrl_date_fin.GetDate()
        self.ctrl_stats.afficher_consommations = self.ctrl_parametres.radio_consommations.GetValue()
        self.ctrl_stats.afficher_cotisations = self.ctrl_parametres.radio_cotisations.GetValue()
        self.ctrl_stats.afficher_locations = self.ctrl_parametres.radio_locations.GetValue()
        self.ctrl_stats.afficher_autres = self.ctrl_parametres.radio_autres.GetValue()
        self.ctrl_stats.listeActivites = self.ctrl_parametres.ctrl_activites.GetActivites() 
        self.ctrl_stats.key_colonne = self.ctrl_colonnes.GetValeur()
        self.ctrl_stats.key_ligne1 = self.ctrl_lignes_1.GetValeur()
        self.ctrl_stats.key_ligne2 = self.ctrl_lignes_2.GetValeur()
        if self.ctrl_mode.GetID():
            self.ctrl_stats.mode_affichage = self.ctrl_mode.GetID()

        # Options
        if self.ctrl_parametres.options_reglements.GetEtat() == True :
            self.ctrl_stats.filtreReglements = True
            self.ctrl_stats.filtreReglements_dateDebut = self.ctrl_parametres.options_reglements.GetDateDebut()
            self.ctrl_stats.filtreReglements_dateFin = self.ctrl_parametres.options_reglements.GetDateFin()
        else:
            self.ctrl_stats.filtreReglements = False
        if self.ctrl_parametres.options_depots.GetEtat() == True :
            self.ctrl_stats.filtreDepots = True
            self.ctrl_stats.filtreDepots_dateDebut = self.ctrl_parametres.options_depots.GetDateDebut()
            self.ctrl_stats.filtreDepots_dateFin = self.ctrl_parametres.options_depots.GetDateFin()
        else:
            self.ctrl_stats.filtreDepots = False

        self.ctrl_stats.labelParametres = self.GetLabelParametres() 
        
        self.ctrl_stats.MAJ() 
    
    def GetLabelParametres(self):
        listeParametres = []
        
        # Dates
        date_debut = self.ctrl_parametres.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_parametres.ctrl_date_fin.GetDate()
        if date_debut == None : date_debut = "---"
        if date_fin == None : date_fin= "---"
        listeParametres.append(_(u"Période du %s au %s") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin))))
        
        # Affichage
        listeAffichage = []
        if self.ctrl_parametres.radio_consommations.GetValue() : listeAffichage.append("Consommations")
        if self.ctrl_parametres.radio_cotisations.GetValue() : listeAffichage.append("Cotisations")
        if self.ctrl_parametres.radio_locations.GetValue(): listeAffichage.append("Locations")
        if self.ctrl_parametres.radio_autres.GetValue() : listeAffichage.append("Autres")
        affichage = ", ".join(listeAffichage)
        listeParametres.append(_(u"Eléments affichés : %s") % affichage)
        
        # Activités
        activites = ", ".join(self.ctrl_parametres.ctrl_activites.GetLabelActivites())
        if activites == "" : 
            activites = _(u"Aucune")
        listeParametres.append(_(u"Activités : %s") % activites)
        
        # Règlements
        if self.ctrl_parametres.options_reglements.GetEtat() == True :
            date_debut_reglement = self.ctrl_parametres.options_reglements.GetDateDebut()
            if date_debut_reglement == None : date_debut_reglement = "---"
            date_fin_reglement = self.ctrl_parametres.options_reglements.GetDateFin()
            if date_fin_reglement == None : date_fin_reglement = "---"
            listeParametres.append(_(u"Uniquement les règlements saisis du %s au %s") % (date_debut_reglement, date_fin_reglement))
        
        # Dépôts
        if self.ctrl_parametres.options_depots.GetEtat() == True :
            date_debut_depot = self.ctrl_parametres.options_depots.GetDateDebut()
            if date_debut_depot == None : date_debut_depot = "---"
            date_fin_depot = self.ctrl_parametres.options_depots.GetDateFin()
            if date_fin_depot == None : date_fin_depot = "---"
            listeParametres.append(_(u"Uniquement les règlements déposés du %s au %s") % (date_debut_depot, date_fin_depot))
        
        # Mode d'affichage
        mode = self.ctrl_mode.GetLabel()
        listeParametres.append(_(u"Mode d'affichage : %s") % mode)
        
        labelParametres = " | ".join(listeParametres)
        return labelParametres
    
    def OnBoutonImprimer(self, event):
        self.ctrl_stats.Imprimer() 

    def OnBoutonExcel(self, event):
        self.ctrl_stats.ExportExcel() 
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Synthsedesprestations")

    def MemoriserParametres(self):
        dictParametres = {
            "ligne" : self.ctrl_lignes_1.GetValeur(),
            "detail" : self.ctrl_lignes_2.GetValeur(),
            "colonnes" : self.ctrl_colonnes.GetValeur(),
            "donnees" : self.ctrl_mode.GetID(),
            "detail_total" : self.check_details_total.GetValue(),
        }
        UTILS_Parametres.ParametresCategorie(mode="set", categorie="dlg_synthese_prestations", dictParametres=dictParametres)

    def OnBoutonFermer(self, event):
        self.MemoriserParametres()
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        event.Skip()

    def OnClose(self, event):
        self.MemoriserParametres()
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        event.Skip()

# -------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
