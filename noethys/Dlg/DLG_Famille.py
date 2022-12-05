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
import wx.lib.agw.toasterbox as Toaster

from Utils import UTILS_Config
from Utils import UTILS_Historique
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Parametres
import GestionDB
import FonctionsPerso

from Ctrl import CTRL_Composition
from Dlg import DLG_Famille_informations
from Dlg import DLG_Famille_prestations
from Dlg import DLG_Famille_reglements
from Dlg import DLG_Famille_quotients
from Dlg import DLG_Famille_caisse
from Dlg import DLG_Famille_pieces
from Dlg import DLG_Famille_cotisations
from Dlg import DLG_Famille_divers
from Dlg import DLG_Famille_factures
from Dlg import DLG_Famille_questionnaire
from Dlg import DLG_Famille_locations




def CreateIDfamille(DB):
    """ Crée la fiche famille dans la base de données afin d'obtenir un IDfamille et un IDcompte_payeur """
    from Utils import UTILS_Internet
    date_creation = str(datetime.date.today())
    IDfamille = DB.ReqInsert("familles", [("date_creation", date_creation),])
    # Création du compte payeur
    IDcompte_payeur = DB.ReqInsert("comptes_payeurs", [("IDfamille", IDfamille),])
    # Création des codes internet
    internet_identifiant= UTILS_Internet.CreationIdentifiant(IDfamille=IDfamille)
    taille = UTILS_Parametres.Parametres(mode="get", categorie="comptes_internet", nom="taille_passwords", valeur=8)
    internet_mdp = UTILS_Internet.CreationMDP(nbreCaract=taille)
    # Sauvegarde des données
    listeDonnees = [
        ("IDcompte_payeur", IDcompte_payeur),
        ("internet_actif", 1),
        ("internet_identifiant", internet_identifiant),
        ("internet_mdp", internet_mdp),
        ]
    DB.ReqMAJ("familles", listeDonnees, "IDfamille", IDfamille)
    return IDfamille


class Notebook(wx.Notebook):
    def __init__(self, parent, id=-1, IDfamille=None):
        wx.Notebook.__init__(self, parent, id, style= wx.BK_DEFAULT) # | wx.NB_MULTILINE
        self.parent = parent
        self.IDfamille = IDfamille
        self.dictPages = {}
        
        self.listePages = [
            ("informations", _(u"Informations"), u"DLG_Famille_informations.Panel(self, IDfamille=IDfamille)", "Information.png"),
            ("questionnaire", _(u"Questionnaire"), u"DLG_Famille_questionnaire.Panel(self, IDfamille=IDfamille)", "Questionnaire.png"),
            ("pieces", _(u"Pièces"), u"DLG_Famille_pieces.Panel(self, IDfamille=IDfamille)", "Dupliquer.png"),
            ("locations", _(u"Locations"), u"DLG_Famille_locations.Panel(self, IDfamille=IDfamille)", "Location.png"),
            ("cotisations", _(u"Cotisations"), u"DLG_Famille_cotisations.Panel(self, IDfamille=IDfamille)", "Cotisation.png"),
            ("caisse", _(u"Caisse"), u"DLG_Famille_caisse.Panel(self, IDfamille=IDfamille)", "Mecanisme.png"),
            ("quotients", _(u"QF/Revenus"), u"DLG_Famille_quotients.Panel(self, IDfamille=IDfamille)", "Calculatrice.png"),
            ("prestations", _(u"Prestations"), u"DLG_Famille_prestations.Panel(self, IDfamille=IDfamille)", "Etiquette.png"),
            ("factures", _(u"Factures"), u"DLG_Famille_factures.Panel(self, IDfamille=IDfamille)", "Facture.png"),
            ("reglements", _(u"Règlements"), u"DLG_Famille_reglements.Panel(self, IDfamille=IDfamille)", "Reglement.png"),
            ("divers", _(u"Divers"), u"DLG_Famille_divers.Panel(self, IDfamille=IDfamille)", "Planete.png"),
            ]

        # Pages à afficher obligatoirement
        self.pagesObligatoires = ["informations",]

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            setattr(self, "img%d" % index, il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/%s') % imgPage, wx.BITMAP_TYPE_PNG)))
            index += 1
        self.AssignImageList(il)

        # Création des pages
        dictParametres = self.GetParametres()

        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            if dictParametres[codePage] == True :
                setattr(self, "page%s" % index, eval(ctrlPage))
                self.AddPage(getattr(self, "page%s" % index), labelPage)
                self.SetPageImage(index, getattr(self, "img%d" % index))
                self.dictPages[codePage] = {'ctrl': getattr(self, "page%d" % index), 'index': index}
                index += 1

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
    def GetPageAvecCode(self, codePage=""):
        if codePage in self.dictPages:
            return self.dictPages[codePage]["ctrl"]
        else:
            return None
    
    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)

    def OnPageChanged(self, event):
        """ Quand une page du notebook est sélectionnée """
        indexAnciennePage = event.GetOldSelection()
        codePage = self.listePages[indexAnciennePage][0]
        # Sauvegarde ancienne page si besoin
        if indexAnciennePage!=wx.NOT_FOUND:
            if codePage in ("caisse", "divers") :
                page = self.GetPage(indexAnciennePage)
                page.Sauvegarde()
            anciennePage = self.GetPage(indexAnciennePage)
        indexPage = event.GetSelection()
        page = self.GetPage(indexPage)
        if page.IsLectureAutorisee() == False :
            self.AffichePage("informations")
            UTILS_Utilisateurs.AfficheDLGInterdiction() 
            return
        self.Freeze()
        wx.CallLater(1, page.MAJ)
        self.Thaw()
        event.Skip()
        
    def MAJpageActive(self):
        """ MAJ la page active du notebook """
        indexPage = self.GetSelection()
        page = self.GetPage(indexPage)
        wx.CallLater(1, page.MAJ)
    
    def MAJpage(self, codePage=""):
        if codePage in self.dictPages:
            page = self.dictPages[codePage]["ctrl"]
            wx.CallLater(1, page.MAJ)

    def GetParametres(self):
        parametres = UTILS_Config.GetParametre("fiche_famille_pages", defaut={})
        dictParametres = {}
        for codePage, labelPage, ctrlPage, imgPage in self.listePages:
            if codePage in parametres:
                afficher = parametres[codePage]
            else :
                afficher = True
            dictParametres[codePage] = afficher
        return dictParametres

    def SelectionParametresPages(self):
        # Préparation de l'affichage des pages
        dictParametres = self.GetParametres()
        listeLabels = []
        listeSelections = []
        listeCodes = []
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages:
            if codePage not in self.pagesObligatoires :
                listeLabels.append(labelPage)
                if codePage in dictParametres:
                    if dictParametres[codePage] == True :
                        listeSelections.append(index)
                listeCodes.append(codePage)
                index += 1

        # Demande la sélection des pages
        dlg = wx.MultiChoiceDialog( self, _(u"Cochez ou décochez les onglets à afficher ou à masquer :"), _(u"Afficher/masquer des onglets"), listeLabels)
        dlg.SetSelections(listeSelections)
        dlg.SetSize((300, 350))
        dlg.CenterOnScreen()
        reponse = dlg.ShowModal()
        selections = dlg.GetSelections()
        dlg.Destroy()
        if reponse != wx.ID_OK :
            return False

        # Mémorisation des pages cochées
        dictParametres = {}
        index = 0
        for codePage in listeCodes:
            if index in selections :
                dictParametres[codePage] = True
            else :
                dictParametres[codePage] = False
            index += 1
        UTILS_Config.SetParametre("fiche_famille_pages", dictParametres)

        # Info
        dlg = wx.MessageDialog(self, _(u"Fermez cette fiche pour appliquer les modifications demandées !"), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()




class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, AfficherMessagesOuverture=True):
        wx.Dialog.__init__(self, parent, id=-1, name="fiche_famille", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.nouvelleFiche = False
        if IDfamille == None :
            self.CreateIDfamille()
            self.nouvelleFiche = True

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        # Composition
        self.sizer_composition_staticbox = wx.StaticBox(self, -1, _(u"Composition de la famille"))
        self.ctrl_composition = CTRL_Composition.Notebook(self, IDfamille=self.IDfamille)
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_calendrier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_liens_famille = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Composition.png"), wx.BITMAP_TYPE_ANY))
        
        # Notebook
        self.notebook = Notebook(self, IDfamille=self.IDfamille)
        
        # Boutons de commande
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Options"), cheminImage="Images/32x32/Configuration2.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_consommations = CTRL_Bouton_image.CTRL(self, texte=_(u"Consommations"), cheminImage="Images/32x32/Calendrier.png")
        self.bouton_saisie_reglement = CTRL_Bouton_image.CTRL(self, texte=_(u"Saisir un règlement"), cheminImage="Images/32x32/Reglement.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouterIndividu, self.bouton_ajouter)

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonLiens, self.bouton_liens_famille)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCalendrier, self.bouton_calendrier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonConsommations, self.bouton_consommations)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSaisieReglement, self.bouton_saisie_reglement)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        
        self.notebook.SetFocus() 
        
        # Si c'est une nouvelle fiche, on propose immédiatement la création d'un individu
        if self.nouvelleFiche == True :
            wx.CallAfter(self.CreerPremierIndividu)

        # Cache le bouton de saisie d'un règlement si l'onglet Règlements est caché
        if ("reglements" in self.notebook.dictPages) == False :
            self.bouton_saisie_reglement.Show(False)

        # MAJ de l'onglet Informations
        self.notebook.GetPageAvecCode("informations").MAJ() 
        
        # MAJ CTRL composition
        code = UTILS_Config.GetParametre("affichage_composition_famille", defaut="graphique")
        self.ctrl_composition.AffichePage(code)
        self.ctrl_composition.MAJ()

        # Affiche les messages à l'ouverture de la fiche famille
        if AfficherMessagesOuverture == True :
            self.AfficheMessagesOuverture()
        

    def __set_properties(self):
        self.SetTitle(_(u"Fiche familiale n°%d") % self.IDfamille)
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter ou créer un nouvel individu")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'individu sélectionné")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer ou détacher l'individu sélectionné")))
        self.bouton_liens_famille.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour visualiser l'ensemble des liens de la famille")))
        self.bouton_calendrier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir la grille des consommations de l'individu sélectionné")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_options.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux options")))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux outils")))
        self.bouton_consommations.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour consulter ou modifier les consommations d'un membre de la famille")))
        self.bouton_saisie_reglement.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir rapidement un règlement")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
        self.bouton_calendrier.SetSize(self.bouton_calendrier.GetBestSize())
        self.bouton_liens_famille.SetSize(self.bouton_liens_famille.GetBestSize())
        
        self.ctrl_composition.SetMinSize((-1, 300))
        self.notebook.SetMinSize((-1, 260))
        self.SetMinSize((960, 710))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        sizer_composition = wx.StaticBoxSizer(self.sizer_composition_staticbox, wx.VERTICAL)
        grid_sizer_composition = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_composition.Add(self.ctrl_composition, 0, wx.EXPAND, 0)
        
        grid_sizer_boutons_composition = wx.FlexGridSizer(rows=8, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_composition.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_composition.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_composition.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons_composition.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_boutons_composition.Add(self.bouton_calendrier, 0, 0, 0)
        grid_sizer_boutons_composition.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_boutons_composition.Add(self.bouton_liens_famille, 0, 0, 0)
        grid_sizer_composition.Add(grid_sizer_boutons_composition, 1, wx.EXPAND, 0)
        grid_sizer_composition.AddGrowableRow(0)
        grid_sizer_composition.AddGrowableCol(0)
        sizer_composition.Add(grid_sizer_composition, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizer_composition, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        grid_sizer_base.Add(self.notebook, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=9, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_consommations, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_saisie_reglement, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(5)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
##        grid_sizer_base.Fit(self)
        self.Layout()
        
        # Détermine la taille de la fenêtre
        taille_fenetre = UTILS_Config.GetParametre("taille_fenetre_famille")
        if taille_fenetre == None :
            self.SetSize((840, 700))
        elif taille_fenetre == (0, 0) or taille_fenetre == [0, 0]:
            self.Maximize(True)
        else:
            self.SetSize(taille_fenetre)        
        self.CenterOnScreen() 
    
    def CreerPremierIndividu(self):
        IDindividu = self.ctrl_composition.Ajouter()
        # Renseigne le premier individu comme titulaire Hélios
        if IDindividu != None :
            try :
                self.notebook.GetPageAvecCode("divers").ctrl_parametres.SetPropertyValue("titulaire_helios", IDindividu)
            except :
                pass
                
    def MAJpageActive(self):
        self.notebook.MAJpageActive() 
    
    def MAJpage(self, codePage=""):
        self.notebook.MAJpage(codePage) 

    def OnBoutonAjouter(self, event):
        self.ctrl_composition.Ajouter()
        
    def OnBoutonModifier(self, event):
        self.ctrl_composition.Modifier_selection()
        
    def OnBoutonSupprimer(self, event):
        self.ctrl_composition.Supprimer_selection()
    
    def OnBoutonLiens(self, event):
        from Dlg import DLG_Individu_liens
        dlg = DLG_Individu_liens.Dialog_liens(self, IDfamille=self.IDfamille)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_composition.MAJ() 
    
    def OnBoutonCalendrier(self, event):
        self.ctrl_composition.Calendrier_selection()
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lafichefamiliale")

    def OnBoutonOptions(self, event):
        self.notebook.SelectionParametresPages()

    def OnBoutonOutils(self, event):
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        # Item Régler une facture
        item = wx.MenuItem(menuPop, 40, _(u"Régler une facture"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Codebarre.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuReglerFacture, id=40)
        
        menuPop.AppendSeparator() 

        # Item Editer un revelé de compte
        item = wx.MenuItem(menuPop, 90, _(u"Editer un relevé des prestations"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Euro.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuImprimerReleve, id=90)
        
        menuPop.AppendSeparator() 

        # Item Editer Attestation de présence
        item = wx.MenuItem(menuPop, 10, _(u"Générer une attestation de présence"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Generation.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuGenererAttestation, id=10)
        
        # Item Liste Attestation de présence
        item = wx.MenuItem(menuPop, 12, _(u"Liste des attestations de présences générées"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Facture.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuListeAttestations, id=12)

        menuPop.AppendSeparator()

        # Item Editer Devis
        item = wx.MenuItem(menuPop, 15, _(u"Générer un devis"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Generation.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuGenererDevis, id=15)

        # Item Liste Devis
        item = wx.MenuItem(menuPop, 20, _(u"Liste des devis générés"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Facture.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuListeDevis, id=20)

        menuPop.AppendSeparator()

        # Item Editer Lettre de rappel
        item = wx.MenuItem(menuPop, 110, _(u"Générer une lettre de rappel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Generation.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuGenererRappel, id=110)
        
        # Item Liste Lettres de rappel
        item = wx.MenuItem(menuPop, 120, _(u"Liste des lettres de rappel générées"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Facture.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuListeRappels, id=120)

        menuPop.AppendSeparator() 

        # Item Liste des reçus édités
        item = wx.MenuItem(menuPop, 300, _(u"Liste des reçus de règlements édités"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Note.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuListeRecus, id=300)

        item = wx.MenuItem(menuPop, 301, _(u"Répartition de la ventilation par règlement"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Repartition.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuRepartitionVentilation, id=301)

        menuPop.AppendSeparator() 
        
        # Item Edition d'étiquettes et de badges
        item = wx.MenuItem(menuPop, 80, _(u"Edition d'étiquettes et de badges"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Etiquette2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuEditionEtiquettes, id=80)
        
        menuPop.AppendSeparator() 
        
        # Item Historique
        item = wx.MenuItem(menuPop, 30, _(u"Historique"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Historique.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuHistorique, id=30)
        
        item = wx.MenuItem(menuPop, 70, _(u"Chronologie"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Timeline.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuChronologie, id=70)
        
        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, 85, _(u"Exporter les données de la famille au format XML"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document_export.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuExporter, id=85)

        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, 200, _(u"Envoyer un Email avec l'éditeur d'Emails de Noethys"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Editeur_email.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuEnvoyerMail, id=200)
        
        item = wx.MenuItem(menuPop, 210, _(u"Envoyer un Email avec le client de messagerie par défaut"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Editeur_email.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuEnvoyerMail, id=210)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

##    def OnBoutonDocuments(self, event):
##        # Création du menu contextuel
##        menuPop = UTILS_Adaptations.Menu()
##        
##        # Item Apercu avant impression
##        item = wx.MenuItem(menuPop, 10, _(u"Editer une Attestation de présence"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.ImprimerAttestation, id=10)
##                
##        self.PopupMenu(menuPop)
##        menuPop.Destroy()
    
    def MenuReglerFacture(self, event):
        from Ctrl import CTRL_Numfacture
        dlg = CTRL_Numfacture.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal() 
        dlg.Destroy()
    
    def GetIDcomptePayeur(self):
        DB = GestionDB.DB()
        req = """SELECT IDcompte_payeur
        FROM familles
        WHERE IDfamille=%d
        """ % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        IDcompte_payeur = listeDonnees[0][0]
        return IDcompte_payeur

    def MenuImprimerReleve(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_releve_prestations", "creer") == False : return
        # Récupération du IDcompte_payeur
        IDcompte_payeur = self.GetIDcomptePayeur()
        # Vérification de la ventilation
        from Dlg import DLG_Verification_ventilation
        tracks = DLG_Verification_ventilation.Verification(IDcompte_payeur)
        if len(tracks) > 0 :
            dlg = wx.MessageDialog(self, _(u"Un ou plusieurs règlements sont encore à ventiler.\n\nVous devez obligatoirement effectuer cela avant d'éditer un relevé des prestations..."), _(u"Ventilation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Ouverture de la facturation
        from Dlg import DLG_Releve_prestations
        dlg = DLG_Releve_prestations.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

    def MenuGenererAttestation(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_attestation_presence", "creer") == False : return
        # Récupération du IDcompte_payeur
        IDcompte_payeur = self.GetIDcomptePayeur()
        # Vérification de la ventilation
        from Dlg import DLG_Verification_ventilation
        tracks = DLG_Verification_ventilation.Verification(IDcompte_payeur)
        if len(tracks) > 0 :
            dlg = wx.MessageDialog(self, _(u"Un ou plusieurs règlements sont encore à ventiler.\n\nVous devez obligatoirement effectuer cela avant d'éditer une attestation..."), _(u"Ventilation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Ouverture de la facturation
        from Dlg import DLG_Impression_attestation
        dlg = DLG_Impression_attestation.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

    def MenuListeAttestations(self, event):
        from Dlg import DLG_Liste_attestations
        dlg = DLG_Liste_attestations.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal() 
        dlg.Destroy()

    def MenuGenererDevis(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_devis", "creer") == False : return
        # Récupération du IDcompte_payeur
        IDcompte_payeur = self.GetIDcomptePayeur()
        # Vérification de la ventilation
        from Dlg import DLG_Verification_ventilation
        tracks = DLG_Verification_ventilation.Verification(IDcompte_payeur)
        if len(tracks) > 0 :
            dlg = wx.MessageDialog(self, _(u"Un ou plusieurs règlements sont encore à ventiler.\n\nVous devez obligatoirement effectuer cela avant d'éditer un devis..."), _(u"Ventilation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Ouverture de la facturation
        from Dlg import DLG_Impression_devis
        dlg = DLG_Impression_devis.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

    def MenuListeDevis(self, event):
        from Dlg import DLG_Liste_devis
        dlg = DLG_Liste_devis.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

    def MenuGenererRappel(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_lettre_rappel", "creer") == False : return
        # Récupération du IDcompte_payeur
        IDcompte_payeur = self.GetIDcomptePayeur()
        # Vérification de la ventilation
        from Dlg import DLG_Verification_ventilation
        tracks = DLG_Verification_ventilation.Verification(IDcompte_payeur)
        if len(tracks) > 0 :
            dlg = wx.MessageDialog(self, _(u"Un ou plusieurs règlements sont encore à ventiler.\n\nVous devez obligatoirement effectuer cela avant d'éditer une attestation..."), _(u"Ventilation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Ouverture de la facturation
        from Dlg import DLG_Rappels_generation
        dlg = DLG_Rappels_generation.Dialog(self)
        dlg.SetFamille(self.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

    def MenuListeRappels(self, event):
        from Dlg import DLG_Liste_rappels
        dlg = DLG_Liste_rappels.Dialog(self, IDcompte_payeur=self.GetIDcomptePayeur())
        dlg.ShowModal() 
        dlg.Destroy()

    def MenuListeRecus(self, event):
        from Dlg import DLG_Liste_recus
        dlg = DLG_Liste_recus.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal() 
        dlg.Destroy()

    def MenuRepartitionVentilation(self, event):
        from Dlg import DLG_Repartition
        dlg = DLG_Repartition.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonConsommations(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "consulter") == False : return
        self.Sauvegarde()
        from Dlg import DLG_Grille
        dlg = DLG_Grille.Dialog(self, IDfamille=self.IDfamille, selectionTous=True)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJpageActive() 
        try :
            dlg.Destroy()
        except :
            pass
    
    def OuvrirGrilleIndividu(self, IDindividu=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "consulter") == False : return
        self.Sauvegarde()
        from Dlg import DLG_Grille
        dlg = DLG_Grille.Dialog(self, IDfamille=self.IDfamille, selectionIndividus=[IDindividu,])
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJpageActive() 
        try :
            dlg.Destroy()
        except :
            pass
    
    def OuvrirFicheIndividu(self, IDindividu=None):
        self.ctrl_composition.Modifier_individu(IDindividu)
        
    def OnBoutonSaisieReglement(self, event):
        self.notebook.AffichePage("reglements")
        pageReglements = self.notebook.GetPageAvecCode("reglements")
        pageReglements.MAJ()
        pageReglements.OnBoutonAjouter(None)
    
    def ReglerFacture(self, IDfacture=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_reglements", "creer") == False : return
        self.notebook.AffichePage("reglements")
        pageReglements = self.notebook.GetPageAvecCode("reglements")
        pageReglements.MAJ()
        pageReglements.ReglerFacture(IDfacture)
        
    def OnBoutonAnnuler(self, event):
        self.Annuler()
    
    def OnClose(self, event):
        self.MemoriseParametres()
        self.Annuler()
        
    def MemoriseParametres(self):
        # Mémorisation du paramètre de la taille d'écran
        if self.IsMaximized() == True :
            taille_fenetre = (0, 0)
        else:
            taille_fenetre = tuple(self.GetSize())
        UTILS_Config.SetParametre("taille_fenetre_famille", taille_fenetre)

        # Mémorisation du type d'affichage de la composition
        code = self.ctrl_composition.GetCodePage()
        UTILS_Config.SetParametre("affichage_composition_famille", code)

    def Sauvegarde(self):
        # Validation des données avant sauvegarde
        listePages = ("questionnaire", "caisse", "divers")
        for codePage in listePages :
            page = self.notebook.GetPageAvecCode(codePage)
            if page != None and page.majEffectuee == True and page.ValidationData() == False :
                self.notebook.AffichePage(codePage)
                return False
        # Sauvegarde des données
        for codePage in listePages :
            page = self.notebook.GetPageAvecCode(codePage)
            if page != None and page.majEffectuee == True :
                page.Sauvegarde()
        return True

    def OnBoutonOk(self, event):
        # Sauvegarde
        etat = self.Sauvegarde() 
        if etat == False :
            return
        # Mémorise taille fenêtre
        self.MemoriseParametres()
        # Fermeture de la fenêtre
        try :
            self.EndModal(wx.ID_OK)
        except :
            pass
    
    def CreateIDfamille(self):
        """ Crée la fiche famille dans la base de données afin d'obtenir un IDfamille et un IDcompte_payeur """
        DB = GestionDB.DB()
        self.IDfamille = CreateIDfamille(DB)
        DB.Close()
        # Mémorise l'action dans l'historique
        UTILS_Historique.InsertActions([{
                "IDfamille" : self.IDfamille,
                "IDcategorie" : 4, 
                "action" : _(u"Création de la famille ID%d") % self.IDfamille,
                },])
    
    def SupprimerFamille(self):
        """ Suppression de la fiche famille """
        DB = GestionDB.DB()
        # Récupération du IDcompte_payeur
        req = """SELECT IDcompte_payeur FROM comptes_payeurs WHERE IDfamille=%d""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        try :
            IDcompte_payeur = listeDonnees[0][0]
        except :
            IDcompte_payeur = None
        # Suppression des tables rattachées
        if IDcompte_payeur != None :
            DB.ReqDEL("payeurs", "IDcompte_payeur", IDcompte_payeur)
            DB.ReqDEL("deductions", "IDcompte_payeur", IDcompte_payeur)
            DB.ReqDEL("rappels", "IDcompte_payeur", IDcompte_payeur)
            DB.ReqDEL("factures", "IDcompte_payeur", IDcompte_payeur)
            DB.ReqDEL("prestations", "IDcompte_payeur", IDcompte_payeur)

        DB.ReqDEL("quotients", "IDfamille", self.IDfamille)
        DB.ReqDEL("attestations", "IDfamille", self.IDfamille)
        DB.ReqDEL("messages", "IDfamille", self.IDfamille)
        DB.ReqDEL("pieces", "IDfamille", self.IDfamille)
        DB.ReqDEL("locations", "IDfamille", self.IDfamille)
        DB.ReqDEL("locations_demandes", "IDfamille", self.IDfamille)
        DB.ReqDEL("historique", "IDfamille", self.IDfamille)
        DB.ReqDEL("comptes_payeurs", "IDfamille", self.IDfamille)
        DB.ReqDEL("familles", "IDfamille", self.IDfamille)
        DB.ReqDEL("mandats", "IDfamille", self.IDfamille)
        DB.Commit() 
        DB.Close()
    
    def SupprimerFicheFamille(self):
        self.SupprimerFamille()
        self.Destroy()
        
        dlg = wx.MessageDialog(self, _(u"La fiche famille a été supprimée."), _(u"Suppression"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return
    
    def Annuler(self):
        """ Annulation des modifications """
        if self.nouvelleFiche == True :
            dlg = wx.MessageDialog(self, _(u"Par mesure de sécurité, vous ne pouvez pas annuler la création d'une fiche famille !\n\nSi vous voulez vraiment supprimer cette fiche famille, détachez ou supprimez chacun des membres de la famille..."), "Suppression", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        else:
            # Sauvegarde
            self.Sauvegarde() 
            # Fermeture
            try :
                self.Destroy() 
            except :
                pass
            
##            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment annuler la création de cette nouvelle fiche ?"), _(u"Annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
##            if dlg.ShowModal() == wx.ID_YES :
##                # Efface de la base la fiche individu 
##                self.SupprimerFamille()
##                dlg.Destroy()
##                # Ferme la fenêtre
##                self.Destroy()
##            else:
##                # annulation de la fermeture
##                dlg.Destroy()
##                return
##        else:
##            # Ferme la fenêtre
##            self.Destroy()
    
    def OnBoutonAjouterIndividu(self, event):
        """ Créer ou rattacher un individu """
        IDindividu = 5
        IDcategorie = 2
        titulaire = 0
        # Enregistrement du rattachement
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDindividu", IDindividu),
            ("IDfamille", self.IDfamille),
            ("IDcategorie", IDcategorie),
            ("titulaire", titulaire),
            ]
        IDrattachement = DB.ReqInsert("rattachements", listeDonnees)
        DB.Close()

    def MenuEditionEtiquettes(self, event):
        from Dlg import DLG_Impression_etiquettes
        dlg = DLG_Impression_etiquettes.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal() 
        dlg.Destroy()        
        
    def MenuHistorique(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_historique", "consulter") == False : return
        from Dlg import DLG_Historique
        dlg = DLG_Historique.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal() 
        dlg.Destroy()

    def MenuChronologie(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_chronologie", "consulter") == False : return
        from Dlg import DLG_Chronologie
        dlg = DLG_Chronologie.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal() 
        dlg.Destroy()

    def MenuExporter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_export", "creer") == False: return
        from Dlg import DLG_Export_familles
        dlg = DLG_Export_familles.Dialog(self, IDfamille=self.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

    def MenuEnvoyerMail(self, event):
        """ Envoyer un Email """
        from Utils import UTILS_Envoi_email
        listeAdresses = UTILS_Envoi_email.GetAdresseFamille(self.IDfamille)
        if listeAdresses == False or len(listeAdresses) == 0 :
            return
        
        # Depuis l'éditeur d'Emails de Noethys
        if event.GetId() == 200 :
            from Dlg import DLG_Mailer
            dlg = DLG_Mailer.Dialog(self)
            listeDonnees = []
            for adresse in listeAdresses :
                listeDonnees.append({"adresse" : adresse, "pieces" : [], "champs" : {},})
            dlg.SetDonnees(listeDonnees, modificationAutorisee=False)
            dlg.ShowModal() 
            dlg.Destroy()
        
        # Depuis le client de messagerie par défaut
        if event.GetId() == 210 :
            FonctionsPerso.EnvoyerMail(adresses=listeAdresses, sujet="", message="")


    def AfficheMessagesOuverture(self):
        """ Affiche les messages à l'ouverture de la fiche famille """
        listeMessages = self.notebook.GetPageAvecCode("informations").GetListeMessages()
        for track in listeMessages :
            if track.rappel_famille == 1 :
                texteToaster = track.texte
                if track.priorite == "HAUTE" :
                    couleurFond="#FFA5A5"
                else:
                    couleurFond="#FDF095"
                self.AfficheToaster(titre=_(u"Message"), texte=texteToaster, couleurFond=couleurFond)

    def AfficheToaster(self, titre=u"", texte=u"", taille=(200, 100), couleurFond="#F0FBED"):
        """ Affiche une boîte de dialogue temporaire """
        largeur, hauteur = taille
        tb = Toaster.ToasterBox(wx.GetApp().GetTopWindow(), Toaster.TB_SIMPLE, Toaster.TB_DEFAULT_STYLE, Toaster.TB_ONTIME)  # TB_CAPTION
        tb.SetTitle(titre)
        tb.SetPopupSize((largeur, hauteur))
        if 'phoenix' not in wx.PlatformInfo:
            largeurEcran, hauteurEcran = wx.ScreenDC().GetSizeTuple()
        else :
            largeurEcran, hauteurEcran = wx.ScreenDC().GetSize()
        tb.SetPopupPosition((largeurEcran - largeur - 10, hauteurEcran - hauteur - 50))
        tb.SetPopupPauseTime(3000)
        tb.SetPopupScrollSpeed(8)
        tb.SetPopupBackgroundColour(couleurFond)
        tb.SetPopupTextColour("#000000")
        tb.SetPopupText(texte)
        tb.Play()





if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    import time
    heure_debut = time.time()
    dialog_1 = Dialog(None, IDfamille=1)
    print("Temps de chargement fiche famille =", time.time() - heure_debut)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
