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
import time
import wx.lib.agw.aui as aui
import wx.html as html
# import wx.lib.agw.hyperlink as Hyperlink

from Utils import UTILS_Config
from Utils import UTILS_Utilisateurs
import GestionDB

from Ctrl import CTRL_Grille
from Ctrl import CTRL_Grille_calendrier
from Ctrl import CTRL_Grille_activite3 #CTRL_Grille_activite
from Ctrl import CTRL_Grille_ecoles
from Ctrl import CTRL_Grille_totaux
from Ctrl import CTRL_Grille_forfaits2 as CTRL_Grille_forfaits
from Ctrl import CTRL_Etiquettes
from Ol import OL_Legende_grille
from Ol import OL_Raccourcis_grille



def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (
        _(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"),
        _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"),
    )
    listeMois = (
        _(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"),
        _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"),
        _(u"octobre"), _(u"novembre"), _(u"décembre"),
    )
    dateComplete = u"{0} {1} {2} {3}".format(
        listeJours[dateDD.weekday()], str(dateDD.day),
        listeMois[dateDD.month-1], str(dateDD.year),
    )
    return dateComplete


def DateEngEnDateDD(dateEng):
    return datetime.date(
        int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]),
    )


def CalculeAge(dateReference, date_naiss):
    # Calcul de l'age de la personne
    age = (dateReference.year - date_naiss.year) - int((dateReference.month, dateReference.day) < (date_naiss.month, date_naiss.day))
    return age


class CTRL_Titre(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=30,  couleurFond=(255, 255, 255)):
        html.HtmlWindow.__init__(self, parent, -1, style=(
            wx.html.HW_NO_SELECTION |
            wx.html.HW_SCROLLBAR_NEVER |
            wx.NO_FULL_REPAINT_ON_RESIZE
        ))
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
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Options"), cheminImage="Images/32x32/Configuration2.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        # Propriétés
        self.bouton_aide.SetToolTip(wx.ToolTip(
            _(u"Cliquez ici pour obtenir de l'aide")
        ))
        self.bouton_options.SetToolTip(wx.ToolTip(
            _(u"Cliquez ici pour définir les paramètres d'affichage de la fenêtre")
        ))
        self.bouton_outils.SetToolTip(wx.ToolTip(
            _(u"Cliquez ici pour accéder aux outils")
        ))
        self.bouton_annuler.SetToolTip(wx.ToolTip(
            _(u"Cliquez ici pour fermer")
        ))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=7, vgap=10, hgap=10)
        grid_sizer_base.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_base.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_base.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_base.AddGrowableCol(3)
        sizer_base.Add(grid_sizer_base, 0, wx.ALL | wx.EXPAND, 10)
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
        if 'phoenix' in wx.PlatformInfo:
            self.parent._mgr.UnInit()
        self.parent.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Gestionnairedesconsommations")

    def OnBoutonOutils(self, event):
        self.parent.MenuOutils()

    def OnBoutonAnnuler(self, event):
        etat = self.parent.Annuler()
        if etat is False:
            return
        if 'phoenix' in wx.PlatformInfo:
            self.parent._mgr.UnInit()
        self.parent.EndModal(wx.ID_CANCEL)

    def OnBoutonOptions(self, event):
        self.parent.MenuOptions()


##class Hyperlien(Hyperlink.HyperLinkCtrl):
##    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
##        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
##        self.parent = parent
##        self.URL = URL
##        self.AutoBrowse(False)
##        self.SetColours("BLUE", "BLUE", "BLUE")
##        self.SetUnderlines(False, False, True)
##        self.SetBold(False)
##        self.EnableRollover(True)
##        self.SetToolTip(wx.ToolTip(infobulle))
##        self.UpdateLink()
##        self.DoPopup(False)
##        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
##
##    def OnLeftLink(self, event):
##        if self.URL == "AJOUTER" :
##            import DLG_Grille_ajouter_individu
##            dlg = DLG_Grille_ajouter_individu.Dialog(self)
##            if dlg.ShowModal() == wx.ID_OK:
##                IDindividu = dlg.GetIDindividu()
##                # Recherche si l'individu est déjà dans la grille
##                if IDindividu in self.GetGrandParent().grille.listeSelectionIndividus :
##                    dlg = wx.MessageDialog(self, _(u"L'individu que vous avez sélectionné est déjà dans la grille des présences !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
##                    dlg.ShowModal()
##                    dlg.Destroy()
##                    return
##                self.GetGrandParent().AjouterIndividu(IDindividu)
##            dlg.Destroy()
##
##        if self.URL == "INSCRITS" :
##            self.GetGrandParent().AfficherTousInscrits()
##
##        self.UpdateLink()


##class CTRL_Options(wx.Panel):
##    def __init__(self, parent):
##        wx.Panel.__init__(self, parent, -1)
##        self.parent = parent
##
##        # Ajouter individu
##        self.hyper_ajouter_individu = Hyperlien(self, label=_(u"Ajouter un individu"), infobulle=_(u"Cliquez ici pour ajouter un individu à la liste afichée"), URL="AJOUTER")
##        self.label_separation_1 = wx.StaticText(self, -1, u"|")
##        self.hyper_tous_inscrits = Hyperlien(self, label=_(u"Afficher tous les inscrits"), infobulle=_(u"Cliquez ici pour afficher tous les inscrits aux activités et groupes sélectionnés"), URL="INSCRITS")
##        # Mode de saisie
##        self.label_mode = wx.StaticText(self, -1, _(u"Mode de saisie :"))
##        self.radio_reservation = wx.RadioButton(self, -1, _(u"Réservation"), style = wx.RB_GROUP )
##        self.radio_attente = wx.RadioButton(self, -1, _(u"Attente") )
##        self.radio_refus = wx.RadioButton(self, -1, _(u"Refus") )
##        self.radio_reservation.SetValue(True)
##
##        self.radio_reservation.SetToolTip(wx.ToolTip(_(u"Le mode Réservation permet de saisir une réservation")))
##        self.radio_attente.SetToolTip(wx.ToolTip(_(u"Le mode Attente permet de saisir une place sur liste d'attente")))
##        self.radio_refus.SetToolTip(wx.ToolTip(_(u"Le mode de refus permet de saisir une place sur liste d'attente qui a été refusée par l'individu. Cette saisie est juste utilisée à titre statistique")))
##
##        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
##        grid_sizer_base.Add(self.hyper_ajouter_individu, 0, wx.EXPAND, 0)
##        grid_sizer_base.Add(self.label_separation_1, 0, 0, 0)
##        grid_sizer_base.Add(self.hyper_tous_inscrits, 0, wx.EXPAND, 0)
##        grid_sizer_base.Add( (5, 5), 0, wx.EXPAND, 0)
##        grid_sizer_base.Add(self.label_mode, 0, wx.EXPAND, 0)
##        grid_sizer_base.Add(self.radio_reservation, 0, wx.EXPAND, 0)
##        grid_sizer_base.Add(self.radio_attente, 0, wx.EXPAND, 0)
##        grid_sizer_base.Add(self.radio_refus, 0, wx.EXPAND, 0)
##        grid_sizer_base.AddGrowableCol(3)
##        self.SetSizer(grid_sizer_base)
##        self.Layout()
##
##        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_reservation)
##        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_attente)
##        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_refus)
##
##    def OnRadioMode(self, event):
##        pass
##
##    def GetMode(self):
##        if self.radio_reservation.GetValue() == True : return "reservation"
##        if self.radio_attente.GetValue() == True : return "attente"
##        if self.radio_refus.GetValue() == True : return "refus"



def AddTool(barre=None, ID=None, bitmap=None, kind=wx.ITEM_NORMAL, label=""):
    if 'phoenix' in wx.PlatformInfo:
        item = barre.AddTool(toolId=ID, label=label, bitmap=bitmap, shortHelp=label, kind=kind)
    else :
        if kind == wx.ITEM_RADIO :
            item = barre.AddRadioLabelTool(id=ID, label=label, bitmap=bitmap, shortHelp=label, longHelp=label)
        else :
            item = barre.AddLabelTool(id=ID, label=label, bitmap=bitmap, shortHelp=label, longHelp=label)
    return item

class PanelGrille(wx.Panel):
    def __init__(self, parent):
        """ Panel central """
        wx.Panel.__init__(self, parent, id=-1, name="panel_grille", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.date = None
        self.listeActivites = []
        self.listeGroupes = []
        self.listeClasses = []
        self.filtrerClasses = False
        self.avecScolariteInconnue = True
        self.dictIndividusAjoutes = {}

        # Paramètres de sélection
        self.listeSelectionActivites = [] #[1,]
        self.listeSelectionIndividus =  [] #[24,]

        # Création des contrôles
        self.ctrl_titre = CTRL_Titre(self, couleurFond="#316AC5")
        self.grille = CTRL_Grille.CTRL(self, "date")

        # Barre d'outils
        self.barreOutils = wx.ToolBar(self, -1, style=(
            wx.TB_HORIZONTAL |
            wx.NO_BORDER |
            wx.TB_FLAT |
            wx.TB_TEXT |
            wx.TB_HORZ_LAYOUT |
            wx.TB_NODIVIDER
        ))
        self.ctrl_recherche = CTRL_Grille.BarreRecherche(self.barreOutils, ctrl_grille=self.grille)
        self.barreOutils.AddControl(self.ctrl_recherche)

        ID_AJOUTER_INDIVIDU = wx.Window.NewControlId()
        ID_AFFICHER_TOUS_INSCRITS = wx.Window.NewControlId()
        self.ID_MODE_RESERVATION = wx.Window.NewControlId()
        self.ID_MODE_ATTENTE = wx.Window.NewControlId()
        self.ID_MODE_REFUS = wx.Window.NewControlId()

        AddTool(self.barreOutils, ID_AJOUTER_INDIVIDU, label=_(u"Ajouter un individu"), bitmap=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Femme.png"), wx.BITMAP_TYPE_PNG))
        AddTool(self.barreOutils, ID_AFFICHER_TOUS_INSCRITS, label=_(u"Afficher tous les inscrits"), bitmap=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG))

        try:
            self.barreOutils.AddStretchableSpace()
        except:
            self.barreOutils.AddSeparator()

        AddTool(self.barreOutils, self.ID_MODE_RESERVATION, label=_(u"Réservation"), bitmap=CTRL_Grille.CreationImage(10, 20, CTRL_Grille.COULEUR_RESERVATION), kind=wx.ITEM_RADIO)
        AddTool(self.barreOutils, self.ID_MODE_ATTENTE, label=_(u"Attente"), bitmap=CTRL_Grille.CreationImage(10, 20, CTRL_Grille.COULEUR_ATTENTE), kind=wx.ITEM_RADIO)
        AddTool(self.barreOutils, self.ID_MODE_REFUS, label=_(u"Refus"), bitmap=CTRL_Grille.CreationImage(10, 20, CTRL_Grille.COULEUR_REFUS), kind=wx.ITEM_RADIO)

        self.Bind(wx.EVT_TOOL, self.AjouterIndividu, id=ID_AJOUTER_INDIVIDU)
        self.Bind(wx.EVT_TOOL, self.AfficherTousInscrits, id=ID_AFFICHER_TOUS_INSCRITS)
        self.barreOutils.Realize()

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_titre, 0, wx.EXPAND,  0)
        grid_sizer_base.Add(self.grille, 0, wx.EXPAND,  0)
        grid_sizer_base.Add(self.barreOutils, 0, wx.EXPAND | wx.ALL,  5)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        self.Layout()

    def Reinitialisation_grille(self):
        """ A utiliser après une sauvegarde de la grille """
        self.grille.InitDonnees()
        self.MAJ_grille()

    def MAJ_grille(self):
        self.listeSelectionIndividus = self.GetListeIndividus()
        self.grille.SetModeDate(self.listeActivites, self.listeSelectionIndividus, self.date)

    def SetDate(self, date=None):
        self.date = date
        if self.date is None:
            dateStr = u""
        else:
            dateStr = DateComplete(self.date)
        self.ctrl_titre.SetTexte(dateStr)

    def SetActivites(self, listeActivites=[]):
        self.listeActivites = listeActivites

    def SetGroupes(self, listeGroupes=[]):
        self.listeGroupes = listeGroupes

    def SetFiltrerClasses(self, etat):
        self.filtrerClasses = etat

    def SetClasses(self, listeClasses=[], scolariteInconnue=None):
        self.listeClasses = listeClasses
        if scolariteInconnue is not None:
            self.avecScolariteInconnue = scolariteInconnue

    def GetListeConditions(self, tableScolarite="scolarite"):
        conditions = []

        # Condition Activités
        conditionActivites = ""
        if len(self.listeActivites) > 0:
            conditionActivites = ", ".join(map(str, self.listeActivites))
        conditions.append("IDactivite IN ({0})".format(conditionActivites))

        # Condition Groupes
        if len(self.listeGroupes) > 0:
            if len(self.listeGroupes) == 1:
                conditions.append("IDgroupe={0}".format(self.listeGroupes[0]))
            else:
                conditions.append("IDgroupe IN ({0})".format(
                    ", ".join(map(str, self.listeGroupes))
                ))

        # Condition Classes
        if self.filtrerClasses:
            conditionsClasses = []
            if self.avecScolariteInconnue:
                conditionsClasses.append("{0}.IDclasse IS NULL".format(
                    tableScolarite
                ))
            if len(self.listeClasses) == 1:
                conditionsClasses.append("{0}.IDclasse={1}".format(
                    tableScolarite, self.listeClasses[0],
                ))
            else:
                conditionsClasses.append("{0}.IDclasse IN ({1})".format(
                    tableScolarite, ", ".join(map(str, self.listeClasses)),
                ))
            conditions.append("({0})".format(" OR ".join(conditionsClasses)))

        return conditions

    def GetListeIndividus(self):
        listeSelectionIndividus = []

        conditions = self.GetListeConditions()
        conditions.append("date='{0}'".format(self.date))

        DB = GestionDB.DB()
        req = """SELECT consommations.IDindividu, COUNT(IDconso)
        FROM consommations"""
        if self.filtrerClasses:
            req += """
        LEFT JOIN scolarite ON scolarite.IDindividu = consommations.IDindividu
                           AND scolarite.date_debut <= consommations.date
                           AND scolarite.date_fin >= consommations.date"""
        req += """
        WHERE {0}
        GROUP BY consommations.IDindividu
        ORDER BY consommations.IDindividu;""".format(" AND ".join(conditions))
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDindividu, nbreConsommations in listeDonnees:
            listeSelectionIndividus.append(IDindividu)

        # On ajoute les individus ajoutés manuellement :
        if self.date in self.dictIndividusAjoutes:
            for IDindividu in self.dictIndividusAjoutes[self.date]:
                valide = False
                if IDindividu in self.grille.dictConsoIndividus:
                    if self.date in self.grille.dictConsoIndividus[IDindividu]:
                        # Vérifie que l'individu a des conso pour la ou les groupes sélectionnés
                        for IDunite, listeConso in self.grille.dictConsoIndividus[IDindividu][self.date].items():
                            for conso in listeConso:
                                if conso.IDgroupe in self.listeGroupes:
                                    valide = True
                if valide is True and IDindividu not in listeSelectionIndividus:
                    listeSelectionIndividus.append(IDindividu)

        return listeSelectionIndividus

    def AjouterIndividu(self, event=None):
        IDindividu = None
        from Dlg import DLG_Grille_ajouter_individu
        dlg = DLG_Grille_ajouter_individu.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            IDindividu = dlg.GetIDindividu()
            # Recherche si l'individu est déjà dans la grille
            if IDindividu in self.grille.listeSelectionIndividus:
                dlg = wx.MessageDialog(self, _(u"L'individu que vous avez sélectionné est déjà dans la grille des présences !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        dlg.Destroy()
        if IDindividu is None:
            return
        self.listeSelectionIndividus.append(IDindividu)
        self.grille.SetModeDate(self.listeActivites, self.listeSelectionIndividus, self.date)
        # Ajout de l'individu dans une liste pour le garder afficher lors d'une MAJ de l'affichage
        if self.date not in self.dictIndividusAjoutes:
            self.dictIndividusAjoutes[self.date] = []
        if IDindividu not in self.dictIndividusAjoutes[self.date]:
            self.dictIndividusAjoutes[self.date].append(IDindividu)

    def AfficherTousInscrits(self, event=None):
        """ Affiche tous les inscrits à l'activité """
        conditions = self.GetListeConditions()
        conditions.append("(date_desinscription IS NULL OR"
                          " date_desinscription>='{0}')".format(self.date))

        DB = GestionDB.DB()
        req = """SELECT IDinscription, inscriptions.IDindividu
        FROM inscriptions"""
        if self.filtrerClasses:
            req += """
        LEFT JOIN scolarite ON scolarite.IDindividu = inscriptions.IDindividu
                           AND scolarite.date_debut <= '{0}'
                           AND scolarite.date_fin >= '{0}'""".format(self.date)
        req += """
        WHERE inscriptions.statut='ok' AND {0}
        GROUP BY inscriptions.IDindividu
        ORDER BY inscriptions.IDindividu;""".format(" AND ".join(conditions))
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        for IDinscription, IDindividu in listeDonnees:
            if IDindividu not in self.listeSelectionIndividus:
                self.listeSelectionIndividus.append(IDindividu)
                # Ajout de l'individu dans une liste pour le garder afficher lors d'une MAJ de l'affichage
                if self.date not in self.dictIndividusAjoutes:
                    self.dictIndividusAjoutes[self.date] = []
                if IDindividu not in self.dictIndividusAjoutes[self.date]:
                    self.dictIndividusAjoutes[self.date].append(IDindividu)
        # MAJ de l'affichage
        self.grille.SetModeDate(self.listeActivites, self.listeSelectionIndividus, self.date)

    def GetMode(self):
        if self.barreOutils.GetToolState(self.ID_MODE_RESERVATION) == True:
            return "reservation"
        if self.barreOutils.GetToolState(self.ID_MODE_ATTENTE) == True:
            return "attente"
        if self.barreOutils.GetToolState(self.ID_MODE_REFUS) == True:
            return "refus"


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Gestionnaire_conso", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        # Détermine la taille de la fenêtre
        self.SetMinSize((700, 600))
        taille_fenetre = UTILS_Config.GetParametre("taille_fenetre_tableau_presences")
        if taille_fenetre is None:
            self.SetSize((900, 600))
        if taille_fenetre == (0, 0) or taille_fenetre == [0, 0] or taille_fenetre == None:
            self.Maximize(True)
        else:
            self.SetSize(taille_fenetre)
        self.CenterOnScreen()

        # Récupère les perspectives
        cfg = UTILS_Config.FichierConfig()
        self.userConfig = cfg.GetDictConfig()
        if "gestionnaire_perspectives" in self.userConfig:
            self.perspectives = self.userConfig["gestionnaire_perspectives"]
        else:
            self.perspectives = []
        if "gestionnaire_perspective_active" in self.userConfig:
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
        self._mgr.AddPane(self.panel_commandes, (
            aui.AuiPaneInfo()
               .Name("commandes").Caption(_(u"Commandes"))
               .Bottom().Layer(0).Position(1)
               .CaptionVisible(False).CloseButton(False).MaximizeButton(False)
               .MinSize((-1, 50))
        ))

        self.panel_totaux = CTRL_Grille_totaux.CTRL(
            self, grille=self.panel_grille.grille,
        )
        self._mgr.AddPane(self.panel_totaux, (
            aui.AuiPaneInfo()
               .Name("totaux").Caption(_(u"Totaux"))
               .Bottom().Layer(0).Position(0).Row(1)
               .CloseButton(False).MaximizeButton(False)
               .MinSize((160, 100))
        ))

        self.panel_calendrier = CTRL_Grille_calendrier.CTRL(self)
        self._mgr.AddPane(self.panel_calendrier, (
            aui.AuiPaneInfo()
               .Name("calendrier").Caption(_(u"Sélection de la date"))
               .Left().Layer(1).Position(0)
               .CloseButton(False).MaximizeButton(False)
               .BestSize(wx.Size(195, 180)).Fixed()
        ))

        self.panel_activites = CTRL_Grille_activite3.CTRL(self)
        self._mgr.AddPane(self.panel_activites, (
            aui.AuiPaneInfo()
               .Name("activites").Caption(_(u"Sélection des activités"))
               .Left().Layer(1).Position(1)
               .CloseButton(False).MaximizeButton(False)
               .BestSize(wx.Size(-1, 50))
        ))
        self._mgr.GetPane("activites").dock_proportion = 100000

        self.panel_legende = OL_Legende_grille.ListView(
            self, id=-1, name="OL_legende", style=(
                wx.LC_REPORT | wx.LC_NO_HEADER |
                wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
            ),
        )
        self.panel_legende.SetSize((50, 50))
        self._mgr.AddPane(self.panel_legende, (
            aui.AuiPaneInfo()
               .Name("legende").Caption(_(u"Légende"))
               .Left().Layer(1).Position(2)
               .CloseButton(False).MaximizeButton(False)
               .MinSize((160, 100)).MaxSize((-1, 120))
        ))

        self.panel_raccourcis = OL_Raccourcis_grille.ListView(
            self, id=-1, name="OL_raccourcis", style=(
                wx.LC_REPORT | wx.LC_NO_HEADER |
                wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
            ),
        )
        self.panel_raccourcis.SetSize((50, 50))
        self._mgr.AddPane(self.panel_raccourcis, (
            aui.AuiPaneInfo()
               .Name("raccourcis").Caption(_(u"Touches raccourcis"))
               .Left().Layer(1).Position(3)
               .CloseButton(False).MaximizeButton(False)
               .MinSize((160, 100)).MaxSize((-1, 120))
        ))
        self._mgr.GetPane("raccourcis").dock_proportion = 60000

        self.panel_ecoles = CTRL_Grille_ecoles.CTRL(self)
        self._mgr.AddPane(self.panel_ecoles, (
            aui.AuiPaneInfo()
               .Name("ecoles").Caption(_(u"Écoles/classes"))
               .Right().Layer(0).Position(0)
               .CloseButton(False).MaximizeButton(False)
               .BestSize(wx.Size(275, -1))
        ))
        self._mgr.GetPane("etiquettes").Hide()

        self.panel_etiquettes = CTRL_Etiquettes.CTRL(self, activeMenu=False)
        self._mgr.AddPane(self.panel_etiquettes, (
            aui.AuiPaneInfo()
               .Name("etiquettes").Caption(_(u"Etiquettes"))
               .Right().Layer(0).Position(1)
               .CloseButton(False).MaximizeButton(False)
               .BestSize(wx.Size(275, 100)).MinSize((275, 100))
        ))
        self._mgr.GetPane("etiquettes").Hide()

        self.panel_forfaits = CTRL_Grille_forfaits.CTRL(
            self, grille=self.panel_grille.grille
        )
        self._mgr.AddPane(self.panel_forfaits, (
            aui.AuiPaneInfo()
               .Name("forfaits").Caption(_(u"Forfaits crédits"))
               .Right().Layer(0).Position(2)
               .CloseButton(False).MaximizeButton(False)
               .BestSize(wx.Size(275, 140)).MinSize((275, 100))
        ))
        self._mgr.GetPane("forfaits").Hide()

        # Création du panel central
        self._mgr.AddPane(self.panel_grille, aui.AuiPaneInfo().Name("grille").
                          CenterPane())
        self._mgr.GetPane("grille").Show()

        # Sauvegarde de la perspective par défaut
        self.perspective_defaut = self._mgr.SavePerspective()

        # Récupération de la perspective chargée
        if self.perspective_active is not None:
            self._mgr.LoadPerspective(self.perspectives[self.perspective_active]["perspective"])
        else:
            self._mgr.LoadPerspective(self.perspective_defaut)

        # Adapte la grille suivant l'état du panneau Ecoles
        self.panel_grille.SetFiltrerClasses(
            self._mgr.GetPane("ecoles").IsShown()
        )

        # Affichage du panneau du panneau Forfait Credits
        if self.panel_grille.grille.tarifsForfaitsCreditsPresents is True:
            self._mgr.GetPane("forfaits").Show()
        else:
            self._mgr.GetPane("forfaits").Hide()

        # Affichage du panneau du panneau Etiquettes
        if self.panel_grille.grille.afficherListeEtiquettes is True:
            self._mgr.GetPane("etiquettes").Show()
        else:
            self._mgr.GetPane("etiquettes").Hide()

        self._mgr.Update()

        self.SetTitle(_(u"Gestionnaire des consommations"))

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Initialisation des contrôles
#        date = self.panel_calendrier.GetDate()
#        self.SetDate(date)

        # Init
        self.panel_activites.SetCocherParDefaut(
            UTILS_Config.GetParametre("gestionnaire_conso_cocher_activites",
                                      defaut=True)
        )

        # Affichage du panneau du panneau Forfait Credits
#        if self.panel_grille.grille.tarifsForfaitsCreditsPresents == True :
#            self._mgr.GetPane("forfaits").Show()
#        else:
#            self._mgr.GetPane("forfaits").Hide()
#        self._mgr.Update()

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
        self.panel_ecoles.SetDate(date)
        listeActivites, listeGroupes = self.panel_activites.GetActivitesEtGroupes()
        self.panel_grille.SetActivites(listeActivites)
        self.panel_grille.SetClasses(
            self.panel_ecoles.GetListeClasses(),
            self.panel_ecoles.GetScolariteInconnue(),
        )
        self.panel_etiquettes.SetActivites(listeActivites)
        self.panel_grille.SetGroupes(listeGroupes)
        self.panel_grille.MAJ_grille()
        self.panel_totaux.MAJ(date)

    def GetDate(self):
        return self.panel_calendrier.GetDate()

#    def SetActivites(self, listeActivites=[]):
#        self.panel_grille.SetActivites(self.panel_activites.GetListeActivites())
#        self.panel_grille.MAJ_grille()
#        self.panel_totaux.MAJ()

    def MAJactivites(self):
        listeActivites, listeGroupes = self.panel_activites.GetActivitesEtGroupes()
        self.panel_grille.SetActivites(listeActivites)
        self.panel_etiquettes.SetActivites(listeActivites)
        self.panel_grille.SetGroupes(listeGroupes)
        self.panel_grille.MAJ_grille()
        self.panel_totaux.MAJ()

    def MAJecoles(self):
        self.panel_grille.SetClasses(
            self.panel_ecoles.GetListeClasses(),
            self.panel_ecoles.GetScolariteInconnue(),
        )
        self.MAJ_grille()

    def MAJ_grille(self):
        self.panel_grille.MAJ_grille()
        self.panel_totaux.MAJ()

    def OnClose(self, event):
        self.MemoriseParametres()
        etat = self.Annuler()
        if etat is False:
            return
        event.Skip()

    def MemoriseParametres(self):
        # Mémorisation du paramètre de la taille d'écran
        if self.IsMaximized() == True:
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
        if len(self.panel_grille.grille.listeHistorique) > 0:
            dlg = wx.MessageDialog(self, _(u"Des modifications ont été effectuées dans la grille.\n\nSouhaitez-vous enregistrer ces modifications avant de fermer cette fenêtre ?"), _(u"Sauvegarde des modifications"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_CANCEL:
                return False
            if reponse == wx.ID_YES:
                # Sauvegarde des données
                self.panel_grille.grille.Sauvegarde()
            return True

    def MenuOutils(self):
        # Création du menu Outils
        menuPop = UTILS_Adaptations.Menu()

        ID_OUTILS_SAISIE_FORFAIT = wx.Window.NewControlId()
        ID_OUTILS_RECALCUL = wx.Window.NewControlId()
        ID_OUTILS_IMPRIMER_CONSO = wx.Window.NewControlId()
        ID_OUTILS_CONVERTIR_ETAT = wx.Window.NewControlId()
        ID_OUTILS_RECOPIAGE = wx.Window.NewControlId()
        ID_OUTILS_TOUT_SELECTIONNER = wx.Window.NewControlId()
        ID_OUTILS_TOUT_DESELECTIONNER = wx.Window.NewControlId()

        #        item = wx.MenuItem(menuPop, ID_OUTILS_SAISIE_FORFAIT, _(u"Appliquer un forfait daté"), _(u"Appliquer un forfait daté"))
#        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Forfait.png"), wx.BITMAP_TYPE_PNG))
#        menuPop.AppendItem(item)
#        self.Bind(wx.EVT_MENU, self.On_outils_saisie_forfait, id=ID_OUTILS_SAISIE_FORFAIT)
#
#        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, ID_OUTILS_IMPRIMER_CONSO, _(u"Imprimer la liste des consommations"), _(u"Imprimer la liste des consommations"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_outils_imprimer, id=ID_OUTILS_IMPRIMER_CONSO)

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

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    # def On_outils_convert_etat(self, event):
    #     """ Convertit tous les refus en réservations """
    #     if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier") == False : return
    #     codeEtat1, labelEtat1, codeEtat2, labelEtat2 = self.dictTempConversionEtat[event.GetId()]
    #     nbre = self.panel_grille.grille.GetNbreDatesEtat(codeEtat1)
    #     if nbre == 0 :
    #         dlg = wx.MessageDialog(self, _(u"Il n'y a aucune consommation affichée ayant cet état !"), _(u"Annulation"), wx.OK | wx.ICON_EXCLAMATION)
    #         dlg.ShowModal()
    #         dlg.Destroy()
    #         return
    #     dlg = wx.MessageDialog(self, _(u"Confirmez-vous le changement d'état '%s' en '%s' pour %d consommations ?") % (labelEtat1, labelEtat2, nbre), _(u"Changement d'état"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
    #     reponse = dlg.ShowModal()
    #     dlg.Destroy()
    #     if reponse != wx.ID_YES :
    #         return
    #     self.panel_grille.grille.ConvertirEtat(etatInitial=codeEtat1, etatFinal=codeEtat2)


    def On_outils_imprimer(self, event):
        if len(self.panel_grille.grille.listeHistorique) > 0:
            dlg = wx.MessageDialog(self, _(u"Des modifications ont été effectuées dans la grille.\n\nSouhaitez-vous les enregistrer maintenant afin qu'elles apparaissent dans le document ?"), _(u"Sauvegarde des modifications"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES:
                return

            # Sauvegarde des données
            self.panel_grille.grille.Sauvegarde()
            # Re-initialisation de la grille
            self.panel_grille.Reinitialisation_grille()

        # Impression PDF
        date = self.GetDate()
        from Dlg import DLG_Impression_conso
        dlg = DLG_Impression_conso.Dialog(self, date=date)
        dlg.ShowModal()
        dlg.Destroy()

    def On_outils_recalculer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("consommations_conso", "modifier") is False:
            return
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous le recalcul des prestations de toutes les consommations affichées ?"), _(u"Recalcul des prestations"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES:
            return
        self.panel_grille.grille.RecalculerToutesPrestations()

    def MenuOptions(self):
        # Création du menu Options
        menuPop = UTILS_Adaptations.Menu()

        ID_AFFICHAGE_PERSPECTIVE_DEFAUT = wx.Window.NewControlId()
        self.ID_PREMIERE_PERSPECTIVE = 500
        ID_AFFICHAGE_PERSPECTIVE_SAVE = wx.Window.NewControlId()
        ID_AFFICHAGE_PERSPECTIVE_SUPPR = wx.Window.NewControlId()
        self.ID_AFFICHAGE_PANNEAUX = 600
        ID_AFFICHAGE_PARAMETRES = wx.Window.NewControlId()
        ID_AFFICHE_COLONNE_MEMO = wx.Window.NewControlId()
        ID_AFFICHE_COLONNE_TRANSPORTS = wx.Window.NewControlId()
        ID_BLOCAGE_SI_COMPLET = wx.Window.NewControlId()
        ID_AFFICHE_SANS_PRESTATION = wx.Window.NewControlId()
        ID_COCHER_ACTIVITES = wx.Window.NewControlId()
        ID_FORMAT_LABEL_LIGNE_MENU = wx.Window.NewControlId()
        self.ID_FORMAT_LABEL_LIGNE_1 = wx.Window.NewControlId()
        self.ID_FORMAT_LABEL_LIGNE_2 = wx.Window.NewControlId()
        self.ID_FORMAT_LABEL_LIGNE_3 = wx.Window.NewControlId()
        self.ID_FORMAT_LABEL_LIGNE_4 = wx.Window.NewControlId()

        item = wx.MenuItem(menuPop, ID_AFFICHAGE_PERSPECTIVE_DEFAUT, _(u"Disposition par défaut"), _(u"Afficher la disposition par défaut"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_affichage_perspective_defaut, id=ID_AFFICHAGE_PERSPECTIVE_DEFAUT)
        if self.perspective_active is None:
            item.Check(True)

        index = 0
        for dictPerspective in self.perspectives:
            label = dictPerspective["label"]
            item = wx.MenuItem(menuPop, self.ID_PREMIERE_PERSPECTIVE + index, label, _(u"Afficher la disposition '%s'") % label, wx.ITEM_CHECK)
            menuPop.AppendItem(item)
            if self.perspective_active == index:
                item.Check(True)
            index += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_perspective_perso, id=self.ID_PREMIERE_PERSPECTIVE, id2=self.ID_PREMIERE_PERSPECTIVE+99 )

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
            {"label": _(u"Sélection de la date"),
             "code": "calendrier", "IDmenu": None},
            {"label": _(u"Sélection des activités"),
             "code": "activites", "IDmenu": None},
            {"label": _(u"Légende"),
             "code": "legende", "IDmenu": None},
            {"label": _(u"Touches raccourcis"),
             "code": "raccourcis", "IDmenu": None},
            {"label": _(u"Totaux"),
             "code": "totaux", "IDmenu": None},
            {"label": _(u"Écoles"),
             "code": "ecoles", "IDmenu": None},
        ]
        ID = self.ID_AFFICHAGE_PANNEAUX
        for dictPanneau in self.listePanneaux:
            dictPanneau["IDmenu"] = ID
            label = dictPanneau["label"]
            item = wx.MenuItem(menuPop, dictPanneau["IDmenu"], label, _(u"Afficher le panneau '%s'") % label, wx.ITEM_CHECK)
            menuPop.AppendItem(item)
            panneau = self._mgr.GetPane(dictPanneau["code"])
            if panneau.IsShown() == True:
                item.Check(True)
            ID += 1
        self.Bind(wx.EVT_MENU_RANGE, self.On_affichage_panneau_afficher, id=self.ID_AFFICHAGE_PANNEAUX, id2=self.ID_AFFICHAGE_PANNEAUX+len(self.listePanneaux))

        menuPop.AppendSeparator()

        sousMenuLabelLigne = UTILS_Adaptations.Menu()

        item = wx.MenuItem(sousMenuLabelLigne, self.ID_FORMAT_LABEL_LIGNE_1, _(u"Nom Prénom"), _(u"Format du label : 'Nom Prénom'"), wx.ITEM_RADIO)
        sousMenuLabelLigne.AppendItem(item)
        item.Check(self.panel_grille.grille.GetFormatLabelLigne() == "nom_prenom")
        self.Bind(wx.EVT_MENU, self.On_format_label_ligne, id=self.ID_FORMAT_LABEL_LIGNE_1)

        item = wx.MenuItem(sousMenuLabelLigne, self.ID_FORMAT_LABEL_LIGNE_2, _(u"Prénom Nom"), _(u"Format du label : 'Prénom Nom'"), wx.ITEM_RADIO)
        sousMenuLabelLigne.AppendItem(item)
        item.Check(self.panel_grille.grille.GetFormatLabelLigne() == "prenom_nom")
        self.Bind(wx.EVT_MENU, self.On_format_label_ligne, id=self.ID_FORMAT_LABEL_LIGNE_2)

        item = wx.MenuItem(sousMenuLabelLigne, self.ID_FORMAT_LABEL_LIGNE_3, _(u"Nom Prénom (ID)"), _(u"Format du label : 'Nom Prénom (ID)'"), wx.ITEM_RADIO)
        sousMenuLabelLigne.AppendItem(item)
        item.Check(self.panel_grille.grille.GetFormatLabelLigne() == "nom_prenom_id")
        self.Bind(wx.EVT_MENU, self.On_format_label_ligne, id=self.ID_FORMAT_LABEL_LIGNE_3)

        item = wx.MenuItem(sousMenuLabelLigne, self.ID_FORMAT_LABEL_LIGNE_4, _(u"Prénom Nom (ID)"), _(u"Format du label : 'Prénom Nom (ID)'"), wx.ITEM_RADIO)
        sousMenuLabelLigne.AppendItem(item)
        item.Check(self.panel_grille.grille.GetFormatLabelLigne() == "prenom_nom_id")
        self.Bind(wx.EVT_MENU, self.On_format_label_ligne, id=self.ID_FORMAT_LABEL_LIGNE_4)

        item = menuPop.AppendMenu(ID_FORMAT_LABEL_LIGNE_MENU, _(u"Format du label de la ligne"), sousMenuLabelLigne)

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

        item = wx.MenuItem(menuPop, ID_COCHER_ACTIVITES, _(u"Cocher les activités automatiquement"), _(u"Cocher automatiquement toutes les activités automatiquement dans le cadre 'Selection des activités'"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        item.Check(self.panel_activites.cocherParDefaut)
        self.Bind(wx.EVT_MENU, self.On_cocher_activites_defaut, id=ID_COCHER_ACTIVITES)

        item = wx.MenuItem(menuPop, ID_BLOCAGE_SI_COMPLET, _(u"Blocage si capacité maximale atteinte"), _(u"Empêche l'utilisateur de saisir une consommation si la capacité maximale est atteinte (case rouge)"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        item.Check(self.panel_grille.grille.blocageSiComplet)
        self.Bind(wx.EVT_MENU, self.On_blocage_si_complet, id=ID_BLOCAGE_SI_COMPLET)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def On_affichage_perspective_defaut(self, event):
        self._mgr.LoadPerspective(self.perspective_defaut)
        self.perspective_active = None

    def On_affichage_perspective_perso(self, event):
        index = event.GetId() - self.ID_PREMIERE_PERSPECTIVE
        self._mgr.LoadPerspective(self.perspectives[index]["perspective"])
        self.perspective_active = index

    def On_affichage_perspective_save(self, event):
        newIDperspective = len(self.perspectives)
        dlg = wx.TextEntryDialog(self, _(u"Veuillez saisir un intitulé pour cette disposition :"), "Sauvegarde d'une disposition")
        dlg.SetValue(_(u"Disposition %d") % (newIDperspective + 1))
        reponse = dlg.ShowModal()
        if reponse != wx.ID_OK:
            dlg.Destroy()
            return

        label = dlg.GetValue()
        dlg.Destroy()

        # Sauvegarde de la perspective
        self.perspectives.append({"label": label, "perspective": self._mgr.SavePerspective()})
        self.perspective_active = newIDperspective

    def On_affichage_perspective_suppr(self, event):
        listeLabels = []
        for dictPerspective in self.perspectives:
            listeLabels.append(dictPerspective["label"])
        dlg = wx.MultiChoiceDialog( self, _(u"Cochez les dispositions que vous souhaitez supprimer :"), _(u"Supprimer des dispositions"), listeLabels)
        if dlg.ShowModal() == wx.ID_OK:
            selections = dlg.GetSelections()
            selections.sort(reverse=True)
            for index in selections:
                self.perspectives.pop(index)
            if self.perspective_active in selections:
                self._mgr.LoadPerspective(self.perspective_defaut)
            self.perspective_active = None
        dlg.Destroy()

    def On_affichage_panneau_afficher(self, event):
        index = event.GetId() - self.ID_AFFICHAGE_PANNEAUX
        code = self.listePanneaux[index]["code"]
        panneau = self._mgr.GetPane(code)
        if panneau.IsShown():
            panneau.Hide()
        else:
            panneau.Show()
        if code == "ecoles":
            self.panel_grille.SetFiltrerClasses(panneau.IsShown())
            self.MAJecoles()
        self._mgr.Update()

    def On_affichage_largeur_unite(self, event):
        """ Définit la largeur de la colonne unité """
        largeur = self.panel_grille.grille.GetLargeurColonneUnite()
        dlg = wx.TextEntryDialog(self, _(u"Veuillez saisir une largeur en pixels (50 par défaut) :"), "Largeur d'une colonne unité")
        dlg.SetValue(str(largeur))
        reponse = dlg.ShowModal()
        if reponse == wx.ID_OK:
            newLargeur = dlg.GetValue()
            try:
                newLargeur = int(newLargeur)
            except:
                dlg2 = wx.MessageDialog(self, _(u"La valeur saisie semble incorrecte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_INFORMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
                dlg.Destroy()
                return
            if newLargeur < 30 or newLargeur > 300:
                dlg2 = wx.MessageDialog(self, _(u"La valeur doit être comprise entre 30 et 300 !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_INFORMATION)
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

    def On_affiche_sans_prestation(self, event):
        self.panel_grille.grille.afficheSansPrestation = not self.panel_grille.grille.afficheSansPrestation
        self.panel_grille.grille.MAJ_affichage()

    def On_format_label_ligne(self, event):
        if event.GetId() == self.ID_FORMAT_LABEL_LIGNE_1:
            self.panel_grille.grille.SetFormatLabelLigne("nom_prenom")
        if event.GetId() == self.ID_FORMAT_LABEL_LIGNE_2:
            self.panel_grille.grille.SetFormatLabelLigne("prenom_nom")
        if event.GetId() == self.ID_FORMAT_LABEL_LIGNE_3:
            self.panel_grille.grille.SetFormatLabelLigne("nom_prenom_id")
        if event.GetId() == self.ID_FORMAT_LABEL_LIGNE_4:
            self.panel_grille.grille.SetFormatLabelLigne("prenom_nom_id")


if __name__ == "__main__":
    app = wx.App(0)
    heure_debut = time.time()
    dlg = Dialog(None)
    print(("Temps de chargement = {0}".format(time.time() - heure_debut)))
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
