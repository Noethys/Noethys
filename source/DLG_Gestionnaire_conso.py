#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import wx.lib.agw.aui as aui
import wx.html as html
import wx.lib.agw.hyperlink as Hyperlink

import UTILS_Config
import UTILS_Utilisateurs
import GestionDB

import CTRL_Grille
import CTRL_Grille_calendrier
import CTRL_Grille_activite3 #CTRL_Grille_activite
import CTRL_Grille_totaux
import CTRL_Grille_forfaits2 as CTRL_Grille_forfaits
import OL_Legende_grille
import OL_Raccourcis_grille


ID_AFFICHAGE_PERSPECTIVE_DEFAUT = wx.NewId()
ID_PREMIERE_PERSPECTIVE = 500
ID_AFFICHAGE_PERSPECTIVE_SAVE = wx.NewId()
ID_AFFICHAGE_PERSPECTIVE_SUPPR = wx.NewId()
ID_AFFICHAGE_PANNEAUX = 600
ID_AFFICHAGE_LARGEUR_UNITE = wx.NewId()
ID_AFFICHAGE_PARAMETRES = wx.NewId()
ID_AFFICHE_COLONNE_MEMO = wx.NewId()
ID_AFFICHE_COLONNE_TRANSPORTS = wx.NewId()
ID_BLOCAGE_SI_COMPLET = wx.NewId()
ID_COCHER_ACTIVITES = wx.NewId()

ID_OUTILS_SAISIE_FORFAIT = wx.NewId()
ID_OUTILS_RECALCUL = wx.NewId()
ID_OUTILS_IMPRIMER_CONSO = wx.NewId()


def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (u"Lundi", u"Mardi", u"Mercredi", u"Jeudi", u"Vendredi", u"Samedi", u"Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def CalculeAge(dateReference, date_naiss):
    # Calcul de l'age de la personne
    age = (dateReference.year - date_naiss.year) - int((dateReference.month, dateReference.day) < (date_naiss.month, date_naiss.day))
    return age


class CTRL_Titre(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=30,  couleurFond=(255, 255, 255)):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(4)
        self.SetMinSize((-1, hauteur))
        self.couleurFond = couleurFond
            
    def SetTexte(self, texte=""):
        self.SetPage(u"<B><FONT SIZE=5 COLOR='WHITE'>%s</FONT></B>""" % texte)
        self.SetBackgroundColour(self.couleurFond)



class Commandes(wx.Panel):
    def __init__(self, parent):
        """ Boutons de commande en bas de la fenêtre """
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        # Boutons 
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_options = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Options.png", wx.BITMAP_TYPE_ANY))        
        self.bouton_outils = self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Outils.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        # Propriétés
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_options.SetToolTipString(u"Cliquez ici pour définir les paramètres d'affichage de la fenêtre")
        self.bouton_outils.SetToolTipString(u"Cliquez ici pour accéder aux outils")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour fermer")
        
        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=7, vgap=10, hgap=10)
        grid_sizer_base.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_outils, 0, wx.EXPAND, 0)
        grid_sizer_base.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_base.AddGrowableCol(3)
        sizer_base.Add(grid_sizer_base, 0, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer_base)
        self.SetMinSize((-1, 50))
        self.Layout()
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def OnBoutonOk(self, event):
        # Sauvegarde
        self.parent.panel_grille.grille.Sauvegarde()
        self.parent.panel_grille.grille.SauvegardeTransports()
        self.parent.MemoriseParametres()
        # Fermeture de la fenêtre
        self.parent.EndModal(wx.ID_OK)
        
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Gestionnairedesconsommations")
    
    def OnBoutonOutils(self, event):
        self.parent.MenuOutils()
    
    def OnBoutonAnnuler(self, event):
        etat = self.parent.Annuler() 
        if etat == False :
            return
        self.parent.EndModal(wx.ID_CANCEL)

    def OnBoutonOptions(self, event):
        self.parent.MenuOptions()


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
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
        if self.URL == "AJOUTER" :
            import DLG_Grille_ajouter_individu
            dlg = DLG_Grille_ajouter_individu.Dialog(self)
            if dlg.ShowModal() == wx.ID_OK:
                IDindividu = dlg.GetIDindividu()
                # Recherche si l'individu est déjà dans la grille
                if IDindividu in self.GetGrandParent().grille.listeSelectionIndividus :
                    dlg = wx.MessageDialog(self, u"L'individu que vous avez sélectionné est déjà dans la grille des présences !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                self.GetGrandParent().AjouterIndividu(IDindividu)
            dlg.Destroy()

        if self.URL == "INSCRITS" :
            self.GetGrandParent().AfficherTousInscrits()
        
        self.UpdateLink()
        

class CTRL_Options(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        
        # Ajouter individu
        self.hyper_ajouter_individu = Hyperlien(self, label=u"Ajouter un individu", infobulle=u"Cliquez ici pour ajouter un individu à la liste afichée", URL="AJOUTER")
        self.label_separation_1 = wx.StaticText(self, -1, u"|")
        self.hyper_tous_inscrits = Hyperlien(self, label=u"Afficher tous les inscrits", infobulle=u"Cliquez ici pour afficher tous les inscrits aux activités et groupes sélectionnés", URL="INSCRITS")
        # Mode de saisie
        self.label_mode = wx.StaticText(self, -1, u"Mode de saisie :")
        self.radio_reservation = wx.RadioButton(self, -1, u"Réservation", style = wx.RB_GROUP )
        self.radio_attente = wx.RadioButton(self, -1, u"Attente" )
        self.radio_refus = wx.RadioButton(self, -1, u"Refus" )
        self.radio_reservation.SetValue(True)
        
        self.radio_reservation.SetToolTipString(u"Le mode Réservation permet de saisir une réservation")
        self.radio_attente.SetToolTipString(u"Le mode Attente permet de saisir une place sur liste d'attente")
        self.radio_refus.SetToolTipString(u"Le mode de refus permet de saisir une place sur liste d'attente qui a été refusée par l'individu. Cette saisie est juste utilisée à titre statistique")
        
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_base.Add(self.hyper_ajouter_individu, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_separation_1, 0, 0, 0)
        grid_sizer_base.Add(self.hyper_tous_inscrits, 0, wx.EXPAND, 0)
        grid_sizer_base.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_mode, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_reservation, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_attente, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_refus, 0, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(3)
        self.SetSizer(grid_sizer_base)
        self.Layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_reservation)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_attente)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_refus)
    
    def OnRadioMode(self, event):
        pass
    
    def GetMode(self):
        if self.radio_reservation.GetValue() == True : return "reservation"
        if self.radio_attente.GetValue() == True : return "attente"
        if self.radio_refus.GetValue() == True : return "refus"


class PanelGrille(wx.Panel):
    def __init__(self, parent):
        """ Panel central """
        wx.Panel.__init__(self, parent, id=-1, name="panel_grille", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.date = None
        self.listeActivites = []
        self.listeGroupes = []
        self.dictIndividusAjoutes = {}
        
        # Paramètres de sélection
        self.listeSelectionActivites = [] #[1,]
        self.listeSelectionIndividus =  [] #[24,]
        
        # Création des contrôles
        self.ctrl_titre = CTRL_Titre(self, couleurFond="#316AC5")
        self.grille = CTRL_Grille.CTRL(self, "date")
        self.ctrl_options = CTRL_Options(self)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_titre, 0, wx.EXPAND,  0)
        grid_sizer_base.Add(self.grille, 0, wx.EXPAND,  0)
        grid_sizer_base.Add(self.ctrl_options, 0, wx.EXPAND|wx.ALL,  5)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        self.Layout()
    
    def Reinitialisation_grille(self):
        """ A utiliser après une sauvegarde de la grille """
        self.grille.InitDonnees() 
        self.MAJ_grille() 
        
    def MAJ_grille(self):
##        self.grille.OnChangementParametres()
        self.listeSelectionIndividus = self.GetListeIndividus()
        self.grille.SetModeDate(self.listeActivites, self.listeSelectionIndividus, self.date)
            
    def SetDate(self, date=None):
        self.date = date
        if self.date == None :
            dateStr = u""
        else:
            dateStr = DateComplete(self.date)
        self.ctrl_titre.SetTexte(dateStr)
    
    def SetActivites(self, listeActivites=[]):
        self.listeActivites = listeActivites
    
    def SetGroupes(self, listeGroupes=[]):
        self.listeGroupes = listeGroupes
    
    def GetListeIndividus(self):
        listeSelectionIndividus = []
        # Conditions Activités :
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        # Condition Groupes
        if len(self.listeGroupes) == 0 : conditionGroupes = ""
        elif len(self.listeGroupes) == 1 : conditionGroupes = " AND IDgroupe=%d" % self.listeGroupes[0]
        else : conditionGroupes = " AND IDgroupe IN %s" % str(tuple(self.listeGroupes))
        
        DB = GestionDB.DB()
        req = """SELECT IDindividu, COUNT(IDconso)
        FROM consommations
        WHERE date='%s' AND IDactivite IN %s %s
        GROUP BY IDindividu
        ORDER BY IDindividu;""" % (str(self.date), conditionActivites, conditionGroupes)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDindividu, nbreConsommations in listeDonnees :
            listeSelectionIndividus.append(IDindividu)
        
        # On ajoute les individus ajoutés manuellement :
        if self.dictIndividusAjoutes.has_key(self.date) :
            for IDindividu in self.dictIndividusAjoutes[self.date] :
                valide = False
                if self.grille.dictConsoIndividus.has_key(IDindividu) :
                    if self.grille.dictConsoIndividus[IDindividu].has_key(self.date) :
                        # Vérifie que l'individu a des conso pour la ou les groupes sélectionnés
                        for IDunite, listeConso in self.grille.dictConsoIndividus[IDindividu][self.date].iteritems() :
                            for conso in listeConso :
                                if conso.IDgroupe in self.listeGroupes :
                                    valide = True
                if valide == True and IDindividu not in listeSelectionIndividus : 
                    listeSelectionIndividus.append(IDindividu)
        
        return listeSelectionIndividus

    def AjouterIndividu(self, IDindividu=None):
        if IDindividu == None : return
        self.listeSelectionIndividus.append(IDindividu)
        self.grille.SetModeDate(self.listeActivites, self.listeSelectionIndividus, self.date)
        # Ajout de l'individu dans une liste pour le garder afficher lors d'une MAJ de l'affichage
        if self.dictIndividusAjoutes.has_key(self.date) == False :
            self.dictIndividusAjoutes[self.date] = []
        if IDindividu not in self.dictIndividusAjoutes[self.date] :
            self.dictIndividusAjoutes[self.date].append(IDindividu)


    def AfficherTousInscrits(self):
        """ Affiche tous les inscrits à l'activité """
        # Conditions Activités :
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        # Condition Groupes
        if len(self.listeGroupes) == 0 : conditionGroupes = ""
        elif len(self.listeGroupes) == 1 : conditionGroupes = " AND IDgroupe=%d" % self.listeGroupes[0]
        else : conditionGroupes = " AND IDgroupe IN %s" % str(tuple(self.listeGroupes))

        DB = GestionDB.DB()
        req = """SELECT IDinscription, IDindividu
        FROM inscriptions
        WHERE IDactivite IN %s %s and parti=0
        GROUP BY IDindividu
        ORDER BY IDindividu;""" % (conditionActivites, conditionGroupes)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        
        listeIndividus = []
        for IDinscription, IDindividu in listeDonnees :
            if IDindividu not in self.listeSelectionIndividus :
                self.listeSelectionIndividus.append(IDindividu)
                # Ajout de l'individu dans une liste pour le garder afficher lors d'une MAJ de l'affichage
                if self.dictIndividusAjoutes.has_key(self.date) == False :
                    self.dictIndividusAjoutes[self.date] = []
                if IDindividu not in self.dictIndividusAjoutes[self.date] :
                    self.dictIndividusAjoutes[self.date].append(IDindividu)
        # MAJ de l'affichage
        self.grille.SetModeDate(self.listeActivites, self.listeSelectionIndividus, self.date)
        
        
        
class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Gestionnaire_conso", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        
        # Détermine la taille de la fenêtre
        self.SetMinSize((700, 600))
        taille_fenetre = UTILS_Config.GetParametre("taille_fenetre_tableau_presences")
        if taille_fenetre == None :
            self.SetSize((900, 600))
        if taille_fenetre == (0, 0) :
            self.Maximize(True)
        else:
            self.SetSize(taille_fenetre)
        self.CenterOnScreen()

        # Récupère les perspectives
        cfg = UTILS_Config.FichierConfig("Data/Config.dat")
        self.userConfig = cfg.GetDictConfig()
        if self.userConfig.has_key("gestionnaire_perspectives") == True :
            self.perspectives = self.userConfig["gestionnaire_perspectives"]
        else:
            self.perspectives = []
        if self.userConfig.has_key("gestionnaire_perspective_active") == True :
            self.perspective_active = self.userConfig["gestionnaire_perspective_active"]
        else:
            self.perspective_active = None

        # Création du notebook
        self.panel_grille = PanelGrille(self)
        self.dictActivites = self.panel_grille.grille.dictActivites
        self.dictIndividus = self.panel_grille.grille.dictIndividus
        self.dictGroupes = self.panel_grille.grille.dictGroupes
        self.listeSelectionIndividus = self.panel_grille.grille.listeSelectionIndividus
                        
        # Création des panels amovibles
        self.panel_commandes = Commandes(self)
        self._mgr.AddPane(self.panel_commandes, aui.AuiPaneInfo().
                          Name("commandes").Caption(u"Commandes").
                          Bottom().Layer(0).Position(1).CaptionVisible(False).CloseButton(False).MaximizeButton(False).MinSize((-1, 50)))

        self.panel_totaux = CTRL_Grille_totaux.CTRL(self, grille=self.panel_grille.grille)
        self._mgr.AddPane(self.panel_totaux, aui.AuiPaneInfo().
                          Name("totaux").Caption(u"Totaux").
                          Bottom().Layer(0).Position(0).Row(1).CloseButton(False).MaximizeButton(False).MinSize((160, 100)))

        self.panel_calendrier = CTRL_Grille_calendrier.CTRL(self)
        self._mgr.AddPane(self.panel_calendrier, aui.AuiPaneInfo().
                          Name("calendrier").Caption(u"Sélection de la date").
                          Left().Layer(1).BestSize(wx.Size(195, 180)).Position(1).CloseButton(False).Fixed().MaximizeButton(False))
                                
        self.panel_activites = CTRL_Grille_activite3.CTRL(self)        
        self._mgr.AddPane(self.panel_activites, aui.AuiPaneInfo().
                          Name("activites").Caption(u"Sélection des activités").
                          Left().Layer(1).Position(1).CloseButton(False).MaximizeButton(False).BestSize(wx.Size(-1,50)))
        pi = self._mgr.GetPane("activites")
        pi.dock_proportion = 100000 # Proportion
        
        self.panel_legende = OL_Legende_grille.ListView(self, id=-1, name="OL_legende", style=wx.LC_REPORT|wx.LC_NO_HEADER | wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.panel_legende.SetSize((50, 50))
        self._mgr.AddPane(self.panel_legende, aui.AuiPaneInfo().
                          Name("legende").Caption(u"Légende").
                          Left().Layer(1).Position(2).CloseButton(False).MaximizeButton(False).MinSize((160, 100)).MaxSize((-1, 120)) )

        self.panel_raccourcis = OL_Raccourcis_grille.ListView(self, id=-1, name="OL_raccourcis", style=wx.LC_REPORT|wx.LC_NO_HEADER | wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.panel_raccourcis.SetSize((50, 50))
        self._mgr.AddPane(self.panel_raccourcis, aui.AuiPaneInfo().
                          Name("raccourcis").Caption(u"Touches raccourcis").
                          Left().Layer(1).Position(3).CloseButton(False).MaximizeButton(False).MinSize((160, 100)).MaxSize((-1, 120)) )
        self._mgr.GetPane("raccourcis").dock_proportion = 60000
        
        self.panel_forfaits = CTRL_Grille_forfaits.CTRL(self, grille=self.panel_grille.grille)
        self._mgr.AddPane(self.panel_forfaits, aui.AuiPaneInfo().
                          Name("forfaits").Caption(u"Forfaits crédits").
                          Right().Layer(0).BestSize(wx.Size(275,140)).Position(4).CloseButton(False).MaximizeButton(False).MinSize((275, 100)))
        self._mgr.GetPane("forfaits").Hide()
        
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
        
        # Affichage du panneau du panneau Forfait Credits
        if self.panel_grille.grille.tarifsForfaitsCreditsPresents == True :
            self._mgr.GetPane("forfaits").Show()
        else:
            self._mgr.GetPane("forfaits").Hide()

        self._mgr.Update()
        
        self.SetTitle(u"Gestionnaire des consommations")
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
                
        # Initialisation des contrôles
        date = self.panel_calendrier.GetDate()
        self.SetDate(date)
        
        # Init
        self.panel_activites.SetCocherParDefaut(UTILS_Config.GetParametre("gestionnaire_conso_cocher_activites", defaut=True))

        # Affichage du panneau du panneau Forfait Credits
##        if self.panel_grille.grille.tarifsForfaitsCreditsPresents == True :
##            self._mgr.GetPane("forfaits").Show()
##        else:
##            self._mgr.GetPane("forfaits").Hide()
##        self._mgr.Update()

        # Contre le bug de maximize
        wx.CallAfter(self._mgr.Update)


    def AffichePanneauForfaitsCredit(self):
        self._mgr.GetPane("forfaits").Show()

    def MAJ_totaux(self):
        self.panel_totaux.MAJ() 

    def MAJ_totaux_contenu(self):
        self.panel_totaux.MAJ_donnees()
        self.panel_totaux.MAJ_contenu() 
    
    def SetDate(self, date):
        self.panel_activites.SetDate(date)
        self.panel_grille.SetDate(date)
        listeActivites, listeGroupes = self.panel_activites.GetActivitesEtGroupes()
        self.panel_grille.SetActivites(listeActivites)
        self.panel_grille.SetGroupes(listeGroupes)
        self.panel_grille.MAJ_grille()
        self.panel_totaux.MAJ(date)
    
    def GetDate(self):
        return self.panel_calendrier.GetDate()
    
##    def SetActivites(self, listeActivites=[]):
##        self.panel_grille.SetActivites(self.panel_activites.GetListeActivites())
##        self.panel_grille.MAJ_grille()
##        self.panel_totaux.MAJ()

    def MAJactivites(self):
        listeActivites, listeGroupes = self.panel_activites.GetActivitesEtGroupes()
        self.panel_grille.SetActivites(listeActivites)
        self.panel_grille.SetGroupes(listeGroupes)
        self.panel_grille.MAJ_grille()
        self.panel_totaux.MAJ()
        
    def MAJ_grille(self):
        self.panel_grille.MAJ_grille()
        self.panel_totaux.MAJ()
    
    def OnClose(self, event):
        self.MemoriseParametres()
        etat = self.Annuler() 
        if etat == False :
            return
        event.Skip() 
        
    def MemoriseParametres(self):        
        # Mémorisation du paramètre de la taille d'écran
        if self.IsMaximized() == True :
            taille_fenetre = (0, 0)
        else:
            taille_fenetre = tuple(self.GetSize())
        UTILS_Config.SetParametre("taille_fenetre_tableau_presences", taille_fenetre)
        # Autres paramètres
        UTILS_Config.SetParametre("gestionnaire_perspectives", self.perspectives)
        UTILS_Config.SetParametre("gestionnaire_perspective_active", self.perspective_active)
        # Paramètres grille
        self.panel_grille.grille.MemoriseParametres() 

    def Annuler(self):
        if len(self.panel_grille.grille.listeHistorique) > 0 :
##            texteHistorique = self.panel_grille.grille.GetTexteHistorique() 
            dlg = wx.MessageDialog(self, u"Des modifications ont été effectuées dans la grille.\n\nSouhaitez-vous enregistrer ces modifications avant de fermer cette fenêtre ?", u"Sauvegarde des modifications", wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse == wx.ID_CANCEL :
                return False
            if reponse == wx.ID_YES :
                # Sauvegarde des données
                self.panel_grille.grille.Sauvegarde()
            return True
    
    def MenuOutils(self):
        # Création du menu Outils
        menuPop = wx.Menu()
            
##        item = wx.MenuItem(menuPop, ID_OUTILS_SAISIE_FORFAIT, u"Appliquer un forfait daté", u"Appliquer un forfait daté")
##        item.SetBitmap(wx.Bitmap("Images/16x16/Forfait.png", wx.BITMAP_TYPE_PNG))
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.On_outils_saisie_forfait, id=ID_OUTILS_SAISIE_FORFAIT)
##        
##        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, ID_OUTILS_IMPRIMER_CONSO, u"Imprimer la liste des consommations", u"Imprimer la liste des consommations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_outils_imprimer, id=ID_OUTILS_IMPRIMER_CONSO)
        
        item = wx.MenuItem(menuPop, ID_OUTILS_RECALCUL, u"Recalculer toutes les prestations", u"Recalculer toutes les prestations")
        item.SetBitmap(wx.Bitmap("Images/16x16/Euro.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_outils_recalculer, id=ID_OUTILS_RECALCUL)

        menuPop.AppendSeparator()

        sousMenuConvertirEtat = wx.Menu()
            
        ID = 1000
        self.dictTempConversionEtat = {}
        listeEtats = [("reservation", u"Réservation"), ("attente", u"Attente"), ("refus", u"Refus"), ("present", u"Présent"), ("absenti", u"Absence injustifiée"), ("absentj", u"Absence justifiée")]
        for codeEtat1, labelEtat1 in listeEtats :
            for codeEtat2, labelEtat2 in listeEtats : 
                if codeEtat1 != codeEtat2 :
                    labelCommande = u"Convertir les consommations '%s' en '%s'" % (labelEtat1, labelEtat2)
                    item = wx.MenuItem(sousMenuConvertirEtat, ID, labelCommande, labelCommande)
                    item.SetBitmap(wx.Bitmap("Images/16x16/Calendrier_modification.png", wx.BITMAP_TYPE_PNG))
                    sousMenuConvertirEtat.AppendItem(item)
                    self.Bind(wx.EVT_MENU, self.On_outils_convert_etat, id=ID)
                    self.dictTempConversionEtat[ID] = (codeEtat1, labelEtat1, codeEtat2, labelEtat2)
                    ID += 1
        
        item = menuPop.AppendMenu(500, u"Convertir l'état des consommations affichées", sousMenuConvertirEtat)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
        
    def On_outils_convert_etat(self, event):
        """ Convertit tous les refus en réservations """
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier") == False : return
        codeEtat1, labelEtat1, codeEtat2, labelEtat2 = self.dictTempConversionEtat[event.GetId()]
        nbre = self.panel_grille.grille.GetNbreDatesEtat(codeEtat1)
        if nbre == 0 :
            dlg = wx.MessageDialog(self, u"Il n'y a aucune consommation affichée ayant cet état !", u"Annulation", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, u"Confirmez-vous le changement d'état '%s' en '%s' pour %d consommations ?" % (labelEtat1, labelEtat2, nbre), u"Changement d'état", wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return 
        self.panel_grille.grille.ConvertirEtat(etatInitial=codeEtat1, etatFinal=codeEtat2)

        
    def On_outils_imprimer(self, event):
        if len(self.panel_grille.grille.listeHistorique) > 0 :
##            texteHistorique = self.panel_grille.grille.GetTexteHistorique() 
            dlg = wx.MessageDialog(self, u"Des modifications ont été effectuées dans la grille.\n\nSouhaitez-vous les enregistrer maintenant afin qu'elles apparaissent dans le document ?", u"Sauvegarde des modifications", wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return 
            
            # Sauvegarde des données
            self.panel_grille.grille.Sauvegarde()
            # Re-initialisation de la grille
            self.panel_grille.Reinitialisation_grille()
            
        # Impression PDF
        date = self.GetDate() 
        import DLG_Impression_conso
        dlg = DLG_Impression_conso.Dialog(self, date=date)
        dlg.ShowModal() 
        dlg.Destroy()

    def On_outils_recalculer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier") == False : return
        dlg = wx.MessageDialog(self, u"Confirmez-vous le recalcul des prestations de toutes les consommations affichées ?\n\n(Attention, la ventilation des règlements sera supprimée pour ces consommations)", u"Recalcul des prestations", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return 
        self.panel_grille.grille.RecalculerToutesPrestations() 

    def MenuOptions(self):
        # Création du menu Options
        menuPop = wx.Menu()
    
        item = wx.MenuItem(menuPop, ID_AFFICHAGE_PERSPECTIVE_DEFAUT, u"Disposition par défaut", u"Afficher la disposition par défaut", wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_affichage_perspective_defaut, id=ID_AFFICHAGE_PERSPECTIVE_DEFAUT)
        if self.perspective_active == None : item.Check(True)
        
        index = 0
        for dictPerspective in self.perspectives:
            label = dictPerspective["label"]
            item = wx.MenuItem(menuPop, ID_PREMIERE_PERSPECTIVE + index, label, u"Afficher la disposition '%s'" % label, wx.ITEM_CHECK)
            menuPop.AppendItem(item)
            if self.perspective_active == index : item.Check(True)
            index += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_perspective_perso, id=ID_PREMIERE_PERSPECTIVE, id2=ID_PREMIERE_PERSPECTIVE+99 )
        
        menuPop.AppendSeparator()
        
        item = wx.MenuItem(menuPop, ID_AFFICHAGE_PERSPECTIVE_SAVE, u"Sauvegarder la disposition actuelle", u"Sauvegarder la disposition actuelle de la page d'accueil")
        item.SetBitmap(wx.Bitmap("Images/16x16/Perspective_ajouter.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_affichage_perspective_save, id=ID_AFFICHAGE_PERSPECTIVE_SAVE)
        
        item = wx.MenuItem(menuPop, ID_AFFICHAGE_PERSPECTIVE_SUPPR, u"Supprimer des dispositions", u"Supprimer des dispositions de page d'accueil sauvegardée")
        item.SetBitmap(wx.Bitmap("Images/16x16/Perspective_supprimer.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_affichage_perspective_suppr, id=ID_AFFICHAGE_PERSPECTIVE_SUPPR)
        
        menuPop.AppendSeparator()
        
        self.listePanneaux = [
            { "label" : u"Sélection de la date", "code" : "calendrier", "IDmenu" : None },
            { "label" : u"Sélection des activités", "code" : "activites", "IDmenu" : None }, 
            { "label" : u"Légende", "code" : "legende", "IDmenu" : None },
            { "label" : u"Touches raccourcis", "code" : "raccourcis", "IDmenu" : None },
            { "label" : u"Totaux", "code" : "totaux", "IDmenu" : None },
            ]
        ID = ID_AFFICHAGE_PANNEAUX
        for dictPanneau in self.listePanneaux :
            dictPanneau["IDmenu"] = ID
            label = dictPanneau["label"]
            item = wx.MenuItem(menuPop, dictPanneau["IDmenu"], label, u"Afficher le panneau '%s'" % label, wx.ITEM_CHECK)
            menuPop.AppendItem(item)
            panneau = self._mgr.GetPane(dictPanneau["code"])
            if panneau.IsShown() == True :
                item.Check(True)
            ID += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_panneau_afficher, id=ID_AFFICHAGE_PANNEAUX, id2=ID_AFFICHAGE_PANNEAUX+len(self.listePanneaux) )
        
        menuPop.AppendSeparator()
        
        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, ID_AFFICHE_COLONNE_MEMO, u"Afficher la colonne Mémo journalier", u"Afficher la colonne Mémo journalier", wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        item.Check(self.panel_grille.grille.GetAfficheColonneMemo())
        self.Bind(wx.EVT_MENU, self.On_affiche_memo, id=ID_AFFICHE_COLONNE_MEMO)

        item = wx.MenuItem(menuPop, ID_AFFICHE_COLONNE_TRANSPORTS, u"Afficher la colonne Transports", u"Afficher la colonne Transports", wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        item.Check(self.panel_grille.grille.GetAfficheColonneTransports())
        self.Bind(wx.EVT_MENU, self.On_affiche_transports, id=ID_AFFICHE_COLONNE_TRANSPORTS)
        
        item = wx.MenuItem(menuPop, ID_AFFICHAGE_PARAMETRES, u"Définir hauteur et largeurs des cases", u"Définir la hauteur des lignes et la largeur des cases")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_affichage_parametres, id=ID_AFFICHAGE_PARAMETRES)

        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, ID_COCHER_ACTIVITES, u"Cocher les activités automatiquement", u"Cocher automatiquement toutes les activités automatiquement dans le cadre 'Selection des activités'", wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        item.Check(self.panel_activites.cocherParDefaut)
        self.Bind(wx.EVT_MENU, self.On_cocher_activites_defaut, id=ID_COCHER_ACTIVITES)

        item = wx.MenuItem(menuPop, ID_BLOCAGE_SI_COMPLET, u"Blocage si capacité maximale atteinte", u"Empêche l'utilisateur de saisir une consommation si la capacité maximale est atteinte (case rouge)", wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        item.Check(self.panel_grille.grille.blocageSiComplet)
        self.Bind(wx.EVT_MENU, self.On_blocage_si_complet, id=ID_BLOCAGE_SI_COMPLET)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def On_affichage_perspective_defaut(self, event):
        self._mgr.LoadPerspective(self.perspective_defaut)
        self.perspective_active = None

    def On_affichage_perspective_perso(self, event):
        index = event.GetId() - ID_PREMIERE_PERSPECTIVE
        self._mgr.LoadPerspective(self.perspectives[index]["perspective"])
        self.perspective_active = index

    def On_affichage_perspective_save(self, event):
        newIDperspective = len(self.perspectives)
        dlg = wx.TextEntryDialog(self, u"Veuillez saisir un intitulé pour cette disposition :", "Sauvegarde d'une disposition")
        dlg.SetValue(u"Disposition %d" % (newIDperspective + 1))
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
        dlg = wx.MultiChoiceDialog( self, u"Cochez les dispositions que vous souhaitez supprimer :", u"Supprimer des dispositions", listeLabels)
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
    
    def On_affichage_largeur_unite(self, event):
        """ Définit la largeur de la colonne unité """
        largeur = self.panel_grille.grille.GetLargeurColonneUnite()
        dlg = wx.TextEntryDialog(self, u"Veuillez saisir une largeur en pixels (50 par défaut) :", "Largeur d'une colonne unité")
        dlg.SetValue(str(largeur))
        reponse = dlg.ShowModal()
        if reponse == wx.ID_OK:
            newLargeur = dlg.GetValue()
            try :
                newLargeur = int(newLargeur)
            except :
                dlg2 = wx.MessageDialog(self, u"La valeur saisie semble incorrecte !", u"Erreur de saisie", wx.OK | wx.ICON_INFORMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
                dlg.Destroy() 
                return
            if newLargeur < 30 or newLargeur > 300 :
                dlg2 = wx.MessageDialog(self, u"La valeur doit être comprise entre 30 et 300 !", u"Erreur de saisie", wx.OK | wx.ICON_INFORMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
                return
            self.panel_grille.grille.SetLargeurColonneUnite(newLargeur)
        dlg.Destroy() 
        UTILS_Config.SetParametre("largeur_colonne_unite", newLargeur)

    def On_affichage_parametres(self, event):
        """ Définit la largeur de la colonne unité """
        self.panel_grille.grille.Parametres() 

    def On_affiche_memo(self, event):
        grille = self.panel_grille.grille
        grille.SetAfficheColonneMemo(not grille.GetAfficheColonneMemo())

    def On_affiche_transports(self, event):
        grille = self.panel_grille.grille
        grille.SetAfficheColonneTransports(not grille.GetAfficheColonneTransports())
    
    def On_cocher_activites_defaut(self, event):
        self.panel_activites.cocherParDefaut = not self.panel_activites.cocherParDefaut
        UTILS_Config.SetParametre("gestionnaire_conso_cocher_activites", self.panel_activites.cocherParDefaut)
        
    def On_blocage_si_complet(self, event):
        self.panel_grille.grille.blocageSiComplet = not self.panel_grille.grille.blocageSiComplet



if __name__ == "__main__":
    app = wx.App(0)
    import CTRL_Grille
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()    
