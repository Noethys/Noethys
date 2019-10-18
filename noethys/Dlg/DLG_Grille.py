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
import wx.lib.agw.aui as aui
import wx.html as html

from Utils import UTILS_Config
from Utils import UTILS_Utilisateurs
import GestionDB

from Ctrl import CTRL_Grille

from Ctrl import CTRL_Grille_periode
from Ctrl import CTRL_Grille_individus
from Ctrl import CTRL_Grille_activite2
from Ctrl import CTRL_Grille_facturation
from Ctrl import CTRL_Grille_forfaits2 as CTRL_Grille_forfaits
from Ol import OL_Legende_grille
from Ol import OL_Raccourcis_grille
from Ctrl import CTRL_Etiquettes


ID_AFFICHAGE_PERSPECTIVE_DEFAUT = wx.NewId()
ID_PREMIERE_PERSPECTIVE = 500
ID_AFFICHAGE_PERSPECTIVE_SAVE = wx.NewId()
ID_AFFICHAGE_PERSPECTIVE_SUPPR = wx.NewId()
ID_AFFICHAGE_PANNEAUX = 600
ID_AFFICHAGE_PARAMETRES = wx.NewId()
ID_AFFICHE_COLONNE_MEMO = wx.NewId()
ID_AFFICHE_COLONNE_TRANSPORTS = wx.NewId()
ID_BLOCAGE_SI_COMPLET = wx.NewId()
ID_AFFICHE_SANS_PRESTATION = wx.NewId()

ID_OUTILS_SAISIE_FORFAIT = wx.NewId()
ID_OUTILS_RECALCUL = wx.NewId()
ID_OUTILS_LOT = wx.NewId()
ID_OUTILS_LOT_SAISIE = wx.NewId()
ID_OUTILS_LOT_MODIF = wx.NewId()
ID_OUTILS_LOT_SUPPR = wx.NewId()
ID_OUTILS_IMPRIMER_CONSO = wx.NewId()
ID_OUTILS_ENVOYER_CONSO = wx.NewId()
ID_OUTILS_TOUT_SELECTIONNER = wx.NewId()
ID_OUTILS_TOUT_DESELECTIONNER = wx.NewId()
ID_OUTILS_CONVERTIR_ETAT = wx.NewId()
ID_OUTILS_RECOPIAGE = wx.NewId()

ID_MODE_RESERVATION = wx.NewId()
ID_MODE_ATTENTE = wx.NewId()
ID_MODE_REFUS = wx.NewId()






class Commandes(wx.Panel):
    def __init__(self, parent):
        """ Boutons de commande en bas de la fenêtre """
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Options"), cheminImage="Images/32x32/Configuration2.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_lot = CTRL_Bouton_image.CTRL(self, texte=_(u"Traitement par lot"), cheminImage="Images/32x32/Magique.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=7, vgap=10, hgap=10)
        grid_sizer_base.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_lot, 0, 0, 0)
        grid_sizer_base.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_base.AddGrowableCol(4)
        sizer_base.Add(grid_sizer_base, 0, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer_base)
        self.SetMinSize((-1, 50))
        self.Layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonLot, self.bouton_lot)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Infosbulles
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.bouton_options.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder au menu des options")))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder au menu des outils")))
        self.bouton_lot.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir, modifier ou supprimer un lot de consommations")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))

    def OnBoutonOk(self, event):
        # Sauvegarde
        self.parent.panel_grille.grille.Sauvegarde()
        self.parent.panel_grille.grille.SauvegardeTransports()
        self.parent.MemoriseParametres()
        # Fermeture de la fenêtre
        if 'phoenix' in wx.PlatformInfo:
            self.parent._mgr.UnInit()
        try :
            self.parent.EndModal(wx.ID_OK)
        except :
            pass

    def OnBoutonAnnuler(self, event):
        # Confirmation d'annulation
        listeHistorique = self.parent.panel_grille.grille.GetHistorique()
        if len(listeHistorique) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous avez effectué %d modification(s) dans la grille.\n\nSouhaitez-vous vraiment les annuler ?") % len(listeHistorique), _(u"Annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        # Fermeture de la fenêtre
        if 'phoenix' in wx.PlatformInfo:
            self.parent._mgr.UnInit()
        self.parent.EndModal(wx.ID_CANCEL)
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lagrilledesconsommations")
        
        # Test d'impression de la grid
##        import wx.lib.printout as  printout
##        grid = self.parent.panel_grille.grille
##        prt = printout.PrintGrid(self.GetGrandParent(), grid, total_col = 5, total_row = 2)
##        prt.SetAttributes()
##        prt.Preview()

    def OnBoutonOptions(self, event):
        self.parent.MenuOptions()

    def OnBoutonOutils(self, event):
        self.parent.MenuOutils()

    def OnBoutonLot(self, event):
        self.parent.TraitementLot()

        
class CTRL_titre(html.HtmlWindow):
    def __init__(self, parent, IDfamille, texte="", hauteur=18,  couleurFond=(255, 255, 255)):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(2)
        self.SetMinSize((-1, hauteur))
        self.couleurFond = couleurFond
        self.IDfamille = IDfamille
        
        texte = _(u"coucou") # _(u"Famille de %s") % self.GetNomsTitulaires()
        self.SetTexte(texte)
    
    def SetTexte(self, texte=""):
        self.SetPage(u"<B><FONT SIZE=2 COLOR='WHITE'>%s</FONT></B>""" % texte)
        self.SetBackgroundColour(self.couleurFond)
    
    def GetNomsTitulaires(self):
        listeTitulaires = []
        nbreTitulaires = 0
        for IDindividu, dictIndividu in self.dictIndividus.items():
            if dictIndividu["titulaire"] == 1 :
                nom = dictIndividu["nom"]
                prenom = dictIndividu["prenom"]
                listeTitulaires.append(u"%s %s" % (nom, prenom))
                nbreTitulaires += 1
        if nbreTitulaires == 1 : return listeTitulaires[0]
        if nbreTitulaires == 2 : return _(u"%s et %s") % (listeTitulaires[0], listeTitulaires[1])
        if nbreTitulaires > 2 :
            texteNoms = ""
            for nomTitulaire in listeTitulaires[:-2] :
                texteNoms += u"%s, " % nom
            texteNoms += listeTitulaires[-1]
            return texteNoms
        return u""


class PanelGrille(wx.Panel):
    def __init__(self, parent, mode="individu", IDfamille=None):
        """ Panel central """
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille
        
        # Paramètres de sélection
        self.mode = mode
        self.listeSelectionActivites = [] #[1,]
        self.listeSelectionIndividus =  [] #[24,]
        self.listePeriodes = [] # [(datetime.date(2010, 1, 1), datetime.date(2010, 12, 31)), (datetime.date(2011, 5, 1), datetime.date(2011, 12, 31)),]
        
        # Création des contrôles
##        self.ctrl_titre = CTRL_titre(self, IDfamille, couleurFond="#316AC5")
        self.grille = CTRL_Grille.CTRL(self, IDfamille=IDfamille)

        # Barre d'outils
        self.barreOutils = wx.ToolBar(self, -1, style = 
            wx.TB_HORIZONTAL 
            | wx.NO_BORDER
            | wx.TB_FLAT
            | wx.TB_TEXT
            | wx.TB_HORZ_LAYOUT
            | wx.TB_NODIVIDER
            )
        self.ctrl_recherche = CTRL_Grille.BarreRecherche(self.barreOutils, ctrl_grille=self.grille, size=(300, -1))
        self.barreOutils.AddControl(self.ctrl_recherche)
        try :
            self.barreOutils.AddStretchableSpace()
        except :
            self.barreOutils.AddSeparator()

        liste_tools = [
            (ID_MODE_RESERVATION, _(u"Réservation"), CTRL_Grille.COULEUR_RESERVATION, _(u"Mode de saisie 'Réservation'")),
            (ID_MODE_ATTENTE, _(u"Attente"), CTRL_Grille.COULEUR_ATTENTE, _(u"Mode de saisie 'Attente'")),
            (ID_MODE_REFUS, _(u"Refus"), CTRL_Grille.COULEUR_REFUS, _(u"Mode de saisie 'Refus'")),
        ]
        for ID, label, couleur, help in liste_tools :
            if 'phoenix' in wx.PlatformInfo:
                self.barreOutils.AddRadioTool(ID, label, CTRL_Grille.CreationImage(10, 20, couleur), wx.NullBitmap, help, help)
            else :
                self.barreOutils.AddRadioLabelTool(ID, label=label, bitmap=CTRL_Grille.CreationImage(10, 20, couleur), shortHelp=help, longHelp=help)
        self.barreOutils.Realize()

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
##        grid_sizer_base.Add(self.ctrl_titre, 0, wx.EXPAND,  0)
        grid_sizer_base.Add(self.grille, 0, wx.EXPAND,  0)
        grid_sizer_base.Add(self.barreOutils, 0, wx.EXPAND|wx.ALL,  5)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()
    
    def MAJ_titre(self):
        dictIndividus = self.grille.dictIndividus
        listeIndividus = []
        nbreIndividus = 0
        for IDindividu in self.listeSelectionIndividus :
            if dictIndividu["titulaire"] == 1 :
                nom = dictIndividu["nom"]
                prenom = dictIndividu["prenom"]
                listeTitulaires.append(u"%s %s" % (nom, prenom))
                nbreTitulaires += 1
        if nbreTitulaires == 1 : return listeTitulaires[0]
        if nbreTitulaires == 2 : return _(u"%s et %s") % (listeTitulaires[0], listeTitulaires[1])
        if nbreTitulaires > 2 :
            texteNoms = ""
            for nomTitulaire in listeTitulaires[:-2] :
                texteNoms += u"%s, " % nom
            texteNoms += listeTitulaires[-1]
            return texteNoms
        return u""
        
    def MAJ_grille(self):
        # Recherche des individus de la famille ayant des inscriptions
        self.listeIndividusFamille = []
        for IDindividu, dictIndividu in self.parent.dictIndividus.items() :
            if len(dictIndividu["inscriptions"]) > 0 :
                self.listeIndividusFamille.append(IDindividu)
        self.listeIndividusFamille.sort()

        self.grille.SetModeIndividu(self.listeSelectionActivites, self.listeSelectionIndividus, self.listeIndividusFamille, self.listePeriodes)    
        
    def SetListesPeriodes(self, listePeriodes=[]):
        self.listePeriodes = listePeriodes

    def SetListeSelectionIndividus(self, listeIndividus=[]):
        self.listeSelectionIndividus = listeIndividus
    
    def SetListeSelectionActivites(self, listeActivites=[]):
        self.listeSelectionActivites = listeActivites

    def GetMode(self):
        if self.barreOutils.GetToolState(ID_MODE_RESERVATION) == True : return "reservation"
        if self.barreOutils.GetToolState(ID_MODE_ATTENTE) == True : return "attente"
        if self.barreOutils.GetToolState(ID_MODE_REFUS) == True : return "refus"



class Notebook(aui.AuiNotebook):
    def __init__(self, parent):
        aui.AuiNotebook.__init__(self, parent, -1, style=aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_BOTTOM | wx.NO_BORDER)
        self.parent = parent
        
        self.pages = []
        
        # Paramètres de sélection
        self.mode = "individu"
        self.listeActivites = [1,]
        self.listeSelectionIndividus = [24,]
        self.listeIndividusFamille = [24, 25]
        self.listePeriodes = [] # [(datetime.date(2010, 1, 1), datetime.date(2010, 12, 31)), (datetime.date(2011, 5, 1), datetime.date(2011, 12, 31)),]
        
        # Création de la grille
        self.grille = CTRL_Grille.CTRL(self)
        
        # Création des pages de tests sur le notebook
        self.AddPage(self.grille, _(u"test1"))
        self.AddPage(wx.Panel(self, -1), _(u"test2"))
        self.AddPage(wx.Panel(self, -1), _(u"test3"))
        
##        self.nb.Split(2, wx.RIGHT)
##        self.nb.CalculateNewSplitSize() 

##        # Notebook
##        self.nb.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged) 
##        self.nb.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
    
    def MAJ_grille(self):
        self.grille.SetModeIndividu(self.listeActivites, self.listeSelectionIndividus, self.listeIndividusFamille, self.listePeriodes)    
        
    def SetListesPeriodes(self, listePeriodes=[]):
        self.listePeriodes = listePeriodes
        self.MAJ_grille()
        self.panel_facturation.RAZ()

    def SetListeSelectionIndividus(self, listeIndividus=[]):
        self.listeSelectionIndividus = listeIndividus
        self.MAJ_grille()
        self.panel_facturation.RAZ()

# ---------------------------------------------------------------------------------------------------------------------------
        
class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, selectionIndividus=[], selectionTous=False):
        wx.Dialog.__init__(self, parent, -1, name="grille", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDfamille = IDfamille
        
        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)
        
        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.SetTitle(_(u"Grille des consommations"))
        
        # Récupère les perspectives
        cfg = UTILS_Config.FichierConfig()
        self.userConfig = cfg.GetDictConfig()
        if ("grille_perspectives" in self.userConfig) == True :
            self.perspectives = self.userConfig["grille_perspectives"]
        else:
            self.perspectives = []
        if ("grille_perspective_active" in self.userConfig) == True :
            self.perspective_active = self.userConfig["grille_perspective_active"]
        else:
            self.perspective_active = None
                
        # Création du notebook
        self.panel_grille = PanelGrille(self, "individu", self.IDfamille)
        self.dictActivites = self.panel_grille.grille.dictActivites
        self.dictIndividus = self.panel_grille.grille.dictIndividus
        self.dictGroupes = self.panel_grille.grille.dictGroupes
        self.listeSelectionIndividus = self.panel_grille.grille.listeSelectionIndividus
                        
        # Création des panels amovibles
        self.panel_periode = CTRL_Grille_periode.CTRL(self)
        dictDonnees = UTILS_Config.GetParametre("dict_selection_periodes_activites")
        self.panel_periode.SetDictDonnees(dictDonnees)
        self._mgr.AddPane(self.panel_periode, aui.AuiPaneInfo().
                          Name("periode").Caption(_(u"Sélection de la période")).
                          Top().Layer(1).BestSize(wx.Size(230,144)).Position(1).CloseButton(False).Fixed().MaximizeButton(False))
        
        self.panel_individus = CTRL_Grille_individus.CTRL(self, self.IDfamille, self.dictIndividus, selectionIndividus, selectionTous)
        self._mgr.AddPane(self.panel_individus, aui.AuiPaneInfo().
                          Name("individus").Caption(_(u"Sélection des individus")).
                          Top().Layer(1).BestSize(wx.Size(180,140)).Position(2).CloseButton(False).MaximizeButton(False).MinSize((10, 100)))
                        
        self.panel_activites = CTRL_Grille_activite2.CTRL(self, self.dictIndividus, self.dictActivites, self.dictGroupes, self.listeSelectionIndividus)
        self._mgr.AddPane(self.panel_activites, aui.AuiPaneInfo().
                          Name("activites").Caption(_(u"Sélection des activités")).
                          Top().Layer(1).Position(3).CloseButton(False).MaximizeButton(False).MinSize((160, 100)))
        
        self.panel_facturation = CTRL_Grille_facturation.CTRL(self)
        self._mgr.AddPane(self.panel_facturation, aui.AuiPaneInfo().
                          Name("facturation").Caption(_(u"Facturation")).
                          Right().Layer(0).BestSize(wx.Size(275,140)).Position(3).CloseButton(False).MaximizeButton(False).MinSize((275, 100)))

        self.panel_etiquettes = CTRL_Etiquettes.CTRL(self, activeMenu=False, onCheck=self.panel_grille.grille.MAJ_affichage)
        self._mgr.AddPane(self.panel_etiquettes, aui.AuiPaneInfo().
                          Name("etiquettes").Caption(_(u"Etiquettes")).
                          Right().Layer(0).Position(3).CloseButton(False).BestSize(wx.Size(275, 100)).MaximizeButton(False).MinSize((275, 100)))    

        self.panel_forfaits = CTRL_Grille_forfaits.CTRL(self, grille=self.panel_grille.grille)
        self._mgr.AddPane(self.panel_forfaits, aui.AuiPaneInfo().
                          Name("forfaits").Caption(_(u"Forfaits crédits")).
                          Right().Layer(0).Position(4).BestSize(wx.Size(275,140)).CloseButton(False).MaximizeButton(False).MinSize((275, 100)))
        self._mgr.GetPane("forfaits").dock_proportion = 50000
        
        self.panel_commandes = Commandes(self)
        self._mgr.AddPane(self.panel_commandes, aui.AuiPaneInfo().
                          Name("commandes").Caption(_(u"Commandes")).
                          Bottom().Layer(0).CaptionVisible(False).CloseButton(False).MaximizeButton(False).MinSize((-1, 50)))

        self.panel_legende = OL_Legende_grille.ListView(self, id=-1, name="OL_legende", style=wx.LC_REPORT|wx.LC_NO_HEADER | wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self._mgr.AddPane(self.panel_legende, aui.AuiPaneInfo().
                          Name("legende").Caption(_(u"Légende")).
                          Left().Layer(0).Position(2).CloseButton(False).BestSize(wx.Size(170, 100)).MaximizeButton(False).MinSize((170, 100)))    
        self._mgr.GetPane("legende").dock_proportion = 60000
        
        self.panel_raccourcis = OL_Raccourcis_grille.ListView(self, id=-1, name="OL_raccourcis", style=wx.LC_REPORT|wx.LC_NO_HEADER | wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self._mgr.AddPane(self.panel_raccourcis, aui.AuiPaneInfo().
                          Name("raccourcis").Caption(_(u"Touches raccourcis")).
                          Left().Layer(0).Position(2).CloseButton(False).BestSize(wx.Size(170, 100)).MaximizeButton(False).MinSize((170, 100)))    
        self._mgr.GetPane("raccourcis").dock_proportion = 30000
        
        
        # Création du panel central
        self._mgr.AddPane(self.panel_grille, aui.AuiPaneInfo().Name("grille").
                          CenterPane())
                
        self._mgr.GetPane("grille").Show()

        # Sauvegarde de la perspective par défaut
        self.perspective_defaut = self._mgr.SavePerspective()

        # Récupération de la perspective chargée
        if self.perspective_active != None :
            self._mgr.LoadPerspective(self.perspectives[self.perspective_active]["perspective"])
        else:
            self._mgr.LoadPerspective(self.perspective_defaut)

        self._mgr.Update()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Détermine la taille de la fenêtre
        self.SetMinSize((600, 670))
        taille_fenetre = UTILS_Config.GetParametre("taille_fenetre_grille")
        if taille_fenetre == None :
            self.SetSize((900, 670))
        if taille_fenetre == (0, 0) or taille_fenetre == [0, 0] or taille_fenetre == None :
            self.Maximize(True)
        else:
            self.SetSize(taille_fenetre)
        self.CenterOnScreen()
        
        # Initialisation des contrôles
        self.panel_periode.SetVisibleSelection()
        self.SetListesPeriodes(self.panel_periode.GetDatesSelections())
        self.SetListeSelectionIndividus(self.panel_individus.GetSelections())
        self.SetListeSelectionActivites(self.panel_activites.ctrl_activites.GetIDcoches())
        self.MAJ_grille()
        
        # Affichage du panneau du panneau Forfait Credits
        if self.panel_grille.grille.tarifsForfaitsCreditsPresents == True :
            self._mgr.GetPane("forfaits").Show()
        else:
            self._mgr.GetPane("forfaits").Hide()
        
        # Affichage du panneau du panneau Etiquettes
        if self.panel_grille.grille.afficherListeEtiquettes == True :
            self._mgr.GetPane("etiquettes").Show()
        else:
            self._mgr.GetPane("etiquettes").Hide()
        
        # Contre le bug de maximize
        wx.CallAfter(self._mgr.Update)
        wx.CallAfter(self.panel_grille.grille.SetFocus)


    def SetListesPeriodes(self, listePeriodes=[]):
        self.panel_grille.SetListesPeriodes(listePeriodes)

    def SetListeSelectionIndividus(self, listeIndividus=[]):
        self.panel_activites.ctrl_activites.SetListeSelectionIndividus(listeIndividus)
        self.panel_grille.SetListeSelectionIndividus(listeIndividus)
    
    def SetListeSelectionActivites(self, listeActivites=[]):
        self.panel_grille.SetListeSelectionActivites(listeActivites)
        self.panel_periode.SetVisibleSelection()
        self.panel_etiquettes.SetActivites(listeActivites)

    def MAJ_grille(self, autoCocheActivites=True):
        if autoCocheActivites == True :
            date_min, date_max = self.panel_grille.grille.GetDatesExtremes(self.panel_grille.listePeriodes)
            listeIDactivites = self.panel_activites.ctrl_activites.CocheActivitesOuvertes(date_min, date_max)
            self.SetListeSelectionActivites(listeIDactivites)
        self.panel_grille.MAJ_grille()
    
    def OnClose(self, event):
        self.panel_commandes.OnBoutonAnnuler(None)
##        self.MemoriseTailleFenetre() 
##        self.MemorisePerspectives()
##        event.Skip() 

    def MemoriseParametres(self):
        # Mémorisation du paramètre de la taille d'écran
        if self.IsMaximized() == True :
            taille_fenetre = (0, 0)
        else:
            taille_fenetre = tuple(self.GetSize())
        UTILS_Config.SetParametre("taille_fenetre_grille", taille_fenetre)
        # Autres paramètres
        UTILS_Config.SetParametre("grille_perspectives", self.perspectives)
        UTILS_Config.SetParametre("grille_perspective_active", self.perspective_active)
        # Paramètres grille
        self.panel_grille.grille.MemoriseParametres() 

    def MenuOptions(self):
        # Création du menu Options
        menuPop = UTILS_Adaptations.Menu()
    
        item = wx.MenuItem(menuPop, ID_AFFICHAGE_PERSPECTIVE_DEFAUT, _(u"Disposition par défaut"), _(u"Afficher la disposition par défaut"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_affichage_perspective_defaut, id=ID_AFFICHAGE_PERSPECTIVE_DEFAUT)
        if self.perspective_active == None : item.Check(True)
        
        index = 0
        for dictPerspective in self.perspectives:
            label = dictPerspective["label"]
            item = wx.MenuItem(menuPop, ID_PREMIERE_PERSPECTIVE + index, label, _(u"Afficher la disposition '%s'") % label, wx.ITEM_CHECK)
            menuPop.AppendItem(item)
            if self.perspective_active == index : item.Check(True)
            index += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_perspective_perso, id=ID_PREMIERE_PERSPECTIVE, id2=ID_PREMIERE_PERSPECTIVE+99 )
        
        menuPop.AppendSeparator()
        
        item = wx.MenuItem(menuPop, ID_AFFICHAGE_PERSPECTIVE_SAVE, _(u"Sauvegarder la disposition actuelle"), _(u"Sauvegarder la disposition actuelle de la page d'accueil"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Perspective_ajouter.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_affichage_perspective_save, id=ID_AFFICHAGE_PERSPECTIVE_SAVE)
        
        item = wx.MenuItem(menuPop, ID_AFFICHAGE_PERSPECTIVE_SUPPR, _(u"Supprimer des dispositions"), _(u"Supprimer des dispositions de page d'accueil sauvegardée"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Perspective_supprimer.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_affichage_perspective_suppr, id=ID_AFFICHAGE_PERSPECTIVE_SUPPR)
        
        menuPop.AppendSeparator()
        
        self.listePanneaux = [
            { "label" : _(u"Sélection de la période"), "code" : "periode", "IDmenu" : None },
            { "label" : _(u"Sélection des individus"), "code" : "individus", "IDmenu" : None }, 
            { "label" : _(u"Options d'affichage et de saisie"), "code" : "activites", "IDmenu" : None },
            { "label" : _(u"Facturation"), "code" : "facturation", "IDmenu" : None },
            { "label" : _(u"Légende"), "code" : "legende", "IDmenu" : None },
            { "label" : _(u"Touches raccourcis"), "code" : "raccourcis", "IDmenu" : None },
            ]
        ID = ID_AFFICHAGE_PANNEAUX
        for dictPanneau in self.listePanneaux :
            dictPanneau["IDmenu"] = ID
            label = dictPanneau["label"]
            item = wx.MenuItem(menuPop, dictPanneau["IDmenu"], label, _(u"Afficher le panneau '%s'") % label, wx.ITEM_CHECK)
            menuPop.AppendItem(item)
            panneau = self._mgr.GetPane(dictPanneau["code"])
            if panneau.IsShown() == True :
                item.Check(True)
            ID += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_panneau_afficher, id=ID_AFFICHAGE_PANNEAUX, id2=ID_AFFICHAGE_PANNEAUX+len(self.listePanneaux) )
        
        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, ID_AFFICHE_COLONNE_MEMO, _(u"Afficher la colonne Mémo journalier"), _(u"Afficher la colonne Mémo journalier"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        item.Check(self.panel_grille.grille.GetAfficheColonneMemo())
        self.Bind(wx.EVT_MENU, self.On_affiche_memo, id=ID_AFFICHE_COLONNE_MEMO)

        item = wx.MenuItem(menuPop, ID_AFFICHE_COLONNE_TRANSPORTS, _(u"Afficher la colonne Transports"), _(u"Afficher la colonne Transports"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        item.Check(self.panel_grille.grille.GetAfficheColonneTransports())
        self.Bind(wx.EVT_MENU, self.On_affiche_transports, id=ID_AFFICHE_COLONNE_TRANSPORTS)
        
        item = wx.MenuItem(menuPop, ID_AFFICHAGE_PARAMETRES, _(u"Définir hauteur et largeurs des cases"), _(u"Définir la hauteur des lignes et la largeur des cases"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_affichage_parametres, id=ID_AFFICHAGE_PARAMETRES)

        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, ID_AFFICHE_SANS_PRESTATION, _(u"Afficher le symbole 'Sans prestation'"), _(u"Affiche le symbole 'Sans prestation' dans les cases si aucune prestation n'est rattachée"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        item.Check(self.panel_grille.grille.afficheSansPrestation)
        self.Bind(wx.EVT_MENU, self.On_affiche_sans_prestation, id=ID_AFFICHE_SANS_PRESTATION)

        item = wx.MenuItem(menuPop, ID_BLOCAGE_SI_COMPLET, _(u"Blocage si capacité maximale atteinte"), _(u"Empêche l'utilisateur de saisir une consommation si la capacité maximale est atteinte (case rouge)"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        item.Check(self.panel_grille.grille.blocageSiComplet)
        self.Bind(wx.EVT_MENU, self.On_blocage_si_complet, id=ID_BLOCAGE_SI_COMPLET)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def MenuOutils(self):
        # Création du menu Outils
        menuPop = UTILS_Adaptations.Menu()
            
        item = wx.MenuItem(menuPop, ID_OUTILS_SAISIE_FORFAIT, _(u"Appliquer des forfaits datés"), _(u"Appliquer des forfaits datés"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Forfait.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_outils_saisie_forfait, id=ID_OUTILS_SAISIE_FORFAIT)
        
        menuPop.AppendSeparator()
        
        item = wx.MenuItem(menuPop, ID_OUTILS_RECALCUL, _(u"Recalculer toutes les prestations"), _(u"Recalculer toutes les prestations"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Euro.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_outils_recalculer, id=ID_OUTILS_RECALCUL)

        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, ID_OUTILS_CONVERTIR_ETAT, _(u"Convertir l'état des consommations"), _(u"Convertir l'état des consommations"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier_modification.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.panel_grille.grille.ConvertirEtat, id=ID_OUTILS_CONVERTIR_ETAT)

        item = wx.MenuItem(menuPop, ID_OUTILS_RECOPIAGE, _(u"Recopier des consommations"), _(u"Recopier des consommations"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier_modification.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.panel_grille.grille.Recopier, id=ID_OUTILS_RECOPIAGE)

        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, ID_OUTILS_TOUT_SELECTIONNER, _(u"Sélectionner toutes les lignes"), _(u"Sélectionner toutes les lignes"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cocher.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.panel_grille.grille.SelectionnerLignes, id=ID_OUTILS_TOUT_SELECTIONNER)

        item = wx.MenuItem(menuPop, ID_OUTILS_TOUT_DESELECTIONNER, _(u"Désélectionner toutes les lignes"), _(u"Désélectionner toutes les lignes"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Decocher.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.panel_grille.grille.DeselectionnerLignes, id=ID_OUTILS_TOUT_DESELECTIONNER)

        menuPop.AppendSeparator()
        
        item = wx.MenuItem(menuPop, ID_OUTILS_IMPRIMER_CONSO, _(u"Imprimer la liste des réservations"), _(u"Imprimer la liste des réservations affichées"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_outils_imprimer_conso, id=ID_OUTILS_IMPRIMER_CONSO)

        item = wx.MenuItem(menuPop, ID_OUTILS_ENVOYER_CONSO, _(u"Envoyer la liste des réservations par Email"), _(u"Envoyer la liste des réservations affichées par Email"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_outils_envoyer_conso, id=ID_OUTILS_ENVOYER_CONSO)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
        
    def TraitementLot(self):
        """ Traitement par lot """
        self.panel_grille.grille.TraitementLot() 
        
    def On_affichage_perspective_defaut(self, event):
        self._mgr.LoadPerspective(self.perspective_defaut)
        self.perspective_active = None

    def On_affichage_perspective_perso(self, event):
        index = event.GetId() - ID_PREMIERE_PERSPECTIVE
        self._mgr.LoadPerspective(self.perspectives[index]["perspective"])
        self.perspective_active = index

    def On_affichage_perspective_save(self, event):
        newIDperspective = len(self.perspectives)
        dlg = wx.TextEntryDialog(self, _(u"Veuillez saisir un intitulé pour cette disposition :"), _(u"Sauvegarde d'une disposition"))
        dlg.SetValue(_(u"Disposition %d") % (newIDperspective + 1))
        reponse = dlg.ShowModal()
        if reponse != wx.ID_OK:
            dlg.Destroy() 
            return
        
        label = dlg.GetValue()
        dlg.Destroy() 
        
        # Sauvegarde de la perspective
        self.perspectives.append( {"label" : label, "perspective" : self._mgr.SavePerspective() } )
        self.perspective_active = newIDperspective
            
        
    def On_affichage_perspective_suppr(self, event):
        listeLabels = []
        for dictPerspective in self.perspectives :
            listeLabels.append(dictPerspective["label"])
        dlg = wx.MultiChoiceDialog( self, _(u"Cochez les dispositions que vous souhaitez supprimer :"), _(u"Supprimer des dispositions"), listeLabels)
        if dlg.ShowModal() == wx.ID_OK :
            selections = dlg.GetSelections()
            selections.sort(reverse=True)
            for index in selections :
                self.perspectives.pop(index)
            if self.perspective_active in selections :
                self._mgr.LoadPerspective(self.perspective_defaut)
            self.perspective_active = None
        dlg.Destroy()
        
    def On_affichage_panneau_afficher(self, event):
        index = event.GetId() - ID_AFFICHAGE_PANNEAUX
        panneau = self._mgr.GetPane(self.listePanneaux[index]["code"])
        if panneau.IsShown() :
            panneau.Hide()
        else:
            panneau.Show()
        self._mgr.Update()
    
    def On_affichage_parametres(self, event):
        """ Définit la largeur de la colonne unité """
        self.panel_grille.grille.Parametres() 

    def On_affiche_memo(self, event):
        grille = self.panel_grille.grille
        grille.SetAfficheColonneMemo(not grille.GetAfficheColonneMemo())

    def On_affiche_transports(self, event):
        grille = self.panel_grille.grille
        grille.SetAfficheColonneTransports(not grille.GetAfficheColonneTransports())

    def On_affiche_sans_prestation(self, event):
        self.panel_grille.grille.afficheSansPrestation = not self.panel_grille.grille.afficheSansPrestation
        self.panel_grille.grille.MAJ_affichage() 

    def On_blocage_si_complet(self, event):
        self.panel_grille.grille.blocageSiComplet = not self.panel_grille.grille.blocageSiComplet
        
    def On_outils_saisie_forfait(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "creer") == False : return
        listeActivites = self.panel_grille.listeSelectionActivites
        listeIndividus = self.panel_grille.listeSelectionIndividus
        
        if len(self.panel_grille.grille.listeHistorique) > 0 :
            dlg = wx.MessageDialog(self, _(u"Des modifications ont été effectuées dans la grille.\n\nVous devez d'abord les sauvegarder avant de saisir un forfait !"), _(u"Sauvegarde des modifications"), wx.YES_NO|wx.YES_DEFAULT|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return 
            
            # Sauvegarde des données
            self.panel_grille.grille.Sauvegarde()
            self.panel_grille.grille.InitDonnees()
            self.panel_grille.MAJ_grille() 
        
        from Dlg import DLG_Appliquer_forfait
        dlg = DLG_Appliquer_forfait.Dialog(self, IDfamille=self.IDfamille, listeActivites=listeActivites, listeIndividus=listeIndividus)
        dlg.ShowModal()
        dlg.Destroy()
        self.panel_grille.MAJ_grille()

    def On_outils_recalculer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier") == False : return
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous le recalcul des prestations de toutes les consommations affichées ?"), _(u"Recalcul des prestations"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return 
        self.panel_grille.grille.RecalculerToutesPrestations() 

    def On_outils_lot_saisie(self, event):
        dlg = wx.MessageDialog(self, _(u"Désolé, cette fonction n'est pas encore disponible !"), _(u"Fonction indisponible"), wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def On_outils_lot_modif(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier") == False : return
        # Récupération des données affichées
        periodes = self.panel_grille.listePeriodes
        listeActivites = self.panel_grille.listeSelectionActivites
        if len(listeActivites) == 1 :
            activites = listeActivites[0]
        else:
            activites = None
        listeIndividus = self.panel_grille.listeSelectionIndividus
        # Ouverture de la DLG
        from Dlg import DLG_Modification_lot_conso
        dlg = DLG_Modification_lot_conso.Dialog(self, 
                    IDfamille=self.IDfamille, 
                    selectionPeriode=periodes, 
                    selectionIndividus=listeIndividus, 
                    selectionActivite=activites,
                    )
        if dlg.ShowModal() != wx.ID_OK:
            dictResultats = dlg.GetDictResultats() 
            dlg.Destroy()
            return
        dlg.Destroy()
        self.panel_grille.Modification_lot(dictResultats)

    def On_outils_lot_suppr(self, event):
        dlg = wx.MessageDialog(self, _(u"Désolé, cette fonction n'est pas encore disponible !"), _(u"Fonction indisponible"), wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def On_outils_imprimer_conso(self, event):
        # Impression d'une liste de conso
        self.panel_grille.grille.Imprimer()

    def On_outils_envoyer_conso(self, event):
        # Envoyer la liste des consommations par Email
        self.panel_grille.grille.EnvoyerEmail() 



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    import time
    heure_debut = time.time()
    dialog_1 = Dialog(None, IDfamille=1, selectionIndividus=[3,])
    print("Temps de chargement DLG_Grille =", time.time() - heure_debut)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()    
