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
import sys
import datetime
import os
import io
import json

import wx.lib.agw.labelbook as LB
import wx.lib.agw.flatnotebook as FNB
import wx.lib.agw.hyperlink as Hyperlink

import wx.html as  html
import wx.lib.wxpTag 

##for item in sorted(sys.modules.keys()):
##    if "STATS" in item :
##        print 'delete ' + str(sys.modules[item])
##        del(sys.modules[item])


from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Stats_objets
from Dlg import DLG_Stats_parametres
from Utils import UTILS_Stats_modeles as MODELES
from Utils import UTILS_Stats_individus as INDIVIDUS
from Utils import UTILS_Stats_familles as FAMILLES
from Utils import UTILS_Stats_rapports as RAPPORTS
from Utils import UTILS_Stats_croise as CROISE



def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", ID=None, size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.ID = ID
        self.URL = URL
        
        # Construit l'hyperlink
        self.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
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
        if self.URL == "selectionner" : self.parent.Coche(True)
        if self.URL == "deselectionner" : self.parent.Coche(False)
        if self.URL == "parametres" : self.parent.ModificationParametres()
        if self.URL == "gestion_onglets" : self.parent.OnGestionOnglets()
        if self.URL == "rapport_supprimer" : self.parent.OnSupprimerRapport()
        if self.URL == "rapport_exporter" : self.parent.OnExporterRapport()
        if self.URL == "rapport_importer" : self.parent.OnImporterRapport()
        self.UpdateLink()
        


class HtmlPrintout(wx.html.HtmlPrintout):
    def __init__(self, html=""):
        wx.html.HtmlPrintout.__init__(self)
        self.SetHtmlText(html)
        self.SetMargins(10, 10, 10, 10, spaces=0)



class CTRL_Parametres(wx.html.HtmlWindow):
    def __init__(self, parent):
        wx.html.HtmlWindow.__init__(self, parent, id=-1, style=wx.SUNKEN_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetMinSize((-1, 120))
        self.periode = None
        self.dictParametres = {}
    
    def SetParametres(self, dictParametres={}):
        self.dictParametres = dictParametres

    def MAJ(self):
        """ Création de la source HTML """
        html = ""
        
        if ("mode" in self.dictParametres) == False or len(self.dictParametres["listeActivites"]) == 0 :
            return
        
        # Période
        if self.dictParametres["mode"] == "inscrits" :
            html += _(u"<U><B>Période :</B></U> Aucune")
        else:
            html += _(u"<U><B>Période :</B></U> %s") % self.dictParametres["periode"]["label"]
        html += u"<BR><BR>"
        
        # Activités
        listeActivites = self.dictParametres["listeActivites"]
        if len(listeActivites) == 0 :
            html += _(u"<U><B>Activités :</B></U> Aucune")
        else :
            html += _(u"<U><B>Activités : </B></U><UL>")
            for IDactivite in listeActivites :
                nomActivite = self.dictParametres["dictActivites"][IDactivite]
                html += u"<LI>%s</LI>" % nomActivite
            html += u"</UL>"

        # Options
        if self.dictParametres.get("exclure_archives", False) == True :
            html += _(u"<U><B>Options :</B></U> Individus archivés ou effacés exclus")

        # Finalisation du html
        html = _(u"<html><head><title>Paramètres</title></head><body><FONT SIZE=-1>%s</FONT></body></html>") % html
        self.SetPage(html)



class MyHtml(html.HtmlWindow):
    def __init__(self, parent):
        html.HtmlWindow.__init__(self, parent, id=-1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, linkinfo):
        code = linkinfo.GetHref()
        parentDlg = self.parent
        while parentDlg and not isinstance(parentDlg, Dialog):
            parentDlg = parentDlg.GetParent()

        if code.startswith("custom_tab:"):
            codeObjet = code.split("custom_tab:")[1]
            if parentDlg:
                parentDlg.PersonnaliserTableau(codeObjet)
            return

        if code.startswith("monter_tab:"):
            codeObjet = code.split("monter_tab:")[1]
            if parentDlg:
                parentDlg.DeplacerTableau(codeObjet, direction="monter")
            return

        if code.startswith("descendre_tab:"):
            codeObjet = code.split("descendre_tab:")[1]
            if parentDlg:
                parentDlg.DeplacerTableau(codeObjet, direction="descendre")
            return

        if code.startswith("masquer_tab:"):
            codeObjet = code.split("masquer_tab:")[1]
            if parentDlg:
                parentDlg.MasquerTableau(codeObjet)
            return

        if code.startswith("nouveau_tab:"):
            parts = code.split("nouveau_tab:")[1].split(":")
            codeRubrique = parts[0]
            codePage = parts[1] if len(parts) > 1 else ""
            if parentDlg:
                parentDlg.CreerNouveauTableau(codeRubrique, codePage)
            return

        if code.startswith("organiser_page:"):
            parts = code.split("organiser_page:")[1].split(":")
            codeRubrique = parts[0]
            codePage = parts[1] if len(parts) > 1 else ""
            if parentDlg:
                parentDlg.OrganiserPage(codeRubrique, codePage)
            return

        if code.startswith("suppr_tab:"):
            codeObjet = code.split("suppr_tab:")[1]
            if parentDlg:
                parentDlg.SupprimerTableau(codeObjet)
            return

        if code.startswith("gestion_onglets"):
            if parentDlg:
                parentDlg.OnGestionOnglets()
            return

        figure = self.parent.GetGrandParent().baseHTML.GetFigure(code)
        if figure:
            from Dlg import DLG_Zoom_graphe
            dlg = DLG_Zoom_graphe.Dialog(self, figure=figure)
            dlg.ShowModal() 
            dlg.Destroy()
        


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Stats", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.couleurFond = wx.SystemSettings.GetColour(30)

        self.dictParametres = {}

####Liste d'objets ici
        self.listeObjets = [

            {"nom" : _(u"Individus"), "code" : "individus", "image" : None, "ctrl_notebook" : None, "visible" : True, "pages" : [
            
                    {"nom" : _(u"Nombre"), "code" : "individus_nombre", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Texte_nombre_individus(),
                            INDIVIDUS.Tableau_nombre_individus(),
                            INDIVIDUS.Tableau_evolution_inscriptions(),
                            INDIVIDUS.Graphe_nombre_individus(),
                            ]},

                    {"nom" : _(u"Ancienneté"), "code" : "individus_anciennete", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_nouveaux_individus(),
                            INDIVIDUS.Graphe_nouveaux_individus(),
                            INDIVIDUS.Graphe_arrivee_individus(),
                            INDIVIDUS.Tableau_anciens_individus(),
                            INDIVIDUS.Tableau_mouvements_individus(),
                            INDIVIDUS.Tableau_taux_rotation(),
                            ]},

                    {"nom" : _(u"Genre"), "code" : "individus_genre", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_repartition_genre(),
                            INDIVIDUS.Graphe_repartition_genre(),
                            ]},

                    {"nom" : _(u"Âge"), "code" : "individus_age", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_repartition_ages(),
                            INDIVIDUS.Graphe_repartition_ages(),
                            INDIVIDUS.Tableau_repartition_annees_naiss(),
                            INDIVIDUS.Graphe_repartition_annees_naiss(),
                            INDIVIDUS.Tableau_repartition_tranches_ages(),
                            ]},

                    {"nom" : _(u"Coordonnées"), "code" : "individus_coordonnees", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_repartition_villes(),
                            INDIVIDUS.Graphe_repartition_villes(),
                            ]},

                    {"nom" : _(u"Scolarité"), "code" : "individus_scolarite", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_repartition_ecoles(),
                            INDIVIDUS.Graphe_repartition_ecoles(),
                            INDIVIDUS.Tableau_repartition_niveaux_scolaires(),
                            INDIVIDUS.Graphe_repartition_niveaux_scolaires(),
                            ]},

                    {"nom" : _(u"Profession"), "code" : "individus_profession", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            INDIVIDUS.Tableau_activites_professionnelles(),
                            INDIVIDUS.Graphe_activites_professionnelles(),
                            ]},

                    ]},

            {"nom" : _(u"Familles"), "code" : "familles", "image" : None, "ctrl_notebook" : None, "visible" : True, "pages" : [

                    {"nom" : _(u"Nombre"), "code" : "familles_nombre", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            FAMILLES.Texte_nombre_familles(),
                            FAMILLES.Tableau_nombre_familles(),
                            FAMILLES.Graphe_nombre_familles(),
                            ]},

                    {"nom" : _(u"Caisse"), "code" : "familles_caisse", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            FAMILLES.Tableau_repartition_caisses(),
                            FAMILLES.Graphe_repartition_caisses(),
                            ]},

                    {"nom" : _(u"Composition"), "code" : "familles_composition", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            FAMILLES.Tableau_nombre_membres(),
                            FAMILLES.Graphe_nombre_membres(),
                            ]},

                    {"nom" : _(u"Quotient familial"), "code" : "familles_qf", "image" : None, "ctrl_html" : None, "visible" : True, "objets" : [
                            FAMILLES.Tableau_qf_tarifs(),
                            FAMILLES.Graphe_qf_tarifs(),
                            FAMILLES.Tableau_qf_defaut(),
                            FAMILLES.Graphe_qf_defaut(),
                            ]},

                    ]},

            ]


        # Bandeau
        intro = _(u"Vous pouvez ici consulter des statistiques complètes sur les activités et la période de votre choix. Ces informations sont présentées sous forme de rubrique, de pages et d'items que vous pouvez choisir d'afficher ou non. Vous pouvez ensuite imprimer ces informations sous forme de rapport hierarchisé. Cliquez sur les graphes pour accéder aux outils spécifiques.")
        titre = _(u"Statistiques")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Barres.png")
        
        # Labelbook
        self.box_informations_staticbox = wx.StaticBox(self, -1, _(u"Informations"))
        self.ctrl_labelbook = LB.LabelBook(self, -1, agwStyle=LB.INB_DRAW_SHADOW | LB.INB_LEFT)

        MODELES.ViderCache()
        self.baseHTML = MODELES.HTML(liste_objets=self.listeObjets)
        self.ChargerOngletsPersoSauvegardes()
        self.InitLabelbook() 
        if self.ctrl_labelbook.GetPageCount() > 0:
            self.ctrl_labelbook.SetSelection(0) 

        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_parametres = CTRL_Parametres(self)
        self.ctrl_parametres.MAJ() 
        self.hyper_parametres = Hyperlien(self, label=_(u"Modifier les paramètres"), infobulle=_(u"Modifier les paramètres"), URL="parametres")
        self.label_sep_onglets = wx.StaticText(self, -1, u"|")
        self.hyper_onglets = Hyperlien(self, label=_(u"Gérer les onglets"), infobulle=_(u"Afficher ou masquer des rubriques et des onglets"), URL="gestion_onglets")

        # Rapports personnalisés
        self.box_rapports_staticbox = wx.StaticBox(self, -1, _(u"Rapports personnalisés"))
        self.combo_rapports = wx.Choice(self, -1, choices=[])
        self.bouton_charger_rapport = wx.Button(self, -1, _(u"Charger"), size=(-1, 24))
        self.bouton_sauver_rapport = wx.Button(self, -1, _(u"Enregistrer..."), size=(-1, 24))
        self.hyper_supprimer_rapport = Hyperlien(self, label=_(u"Supprimer"), infobulle=_(u"Supprimer ce modèle de rapport"), URL="rapport_supprimer")
        self.label_sep_rapport1 = wx.StaticText(self, -1, u"|")
        self.hyper_exporter_rapport = Hyperlien(self, label=_(u"Exporter"), infobulle=_(u"Exporter le modèle au format JSON"), URL="rapport_exporter")
        self.label_sep_rapport2 = wx.StaticText(self, -1, u"|")
        self.hyper_importer_rapport = Hyperlien(self, label=_(u"Importer"), infobulle=_(u"Importer un modèle JSON"), URL="rapport_importer")

        # Charger les tableaux personnalisés enregistrés
        self.ChargerTableauxCroisesSauvegardes()

        # impression
        self.box_impression_staticbox = wx.StaticBox(self, -1, _(u"Impression"))
        self.ctrl_impression = CTRL_Stats_objets.CTRL_Objets(self, liste_objets=self.listeObjets)
        self.ctrl_impression.MAJ() 
        
        self.hyper_selectionner = Hyperlien(self, label=_(u"Tout sélectionner"), infobulle=_(u"Tout sélectionner"), URL="selectionner")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_deselectionner = Hyperlien(self, label=_(u"Tout dé-sélectionner"), infobulle=_(u"Tout dé-sélectionner"), URL="deselectionner")
        
        self.bouton_imprimer = CTRL_Bouton_image.CTRL(self, texte=_(u"Imprimer"), cheminImage="Images/32x32/Imprimante.png")
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        self.MAJRapportsCombo()
        
        # Binds
        self.Bind(LB.EVT_IMAGENOTEBOOK_PAGE_CHANGED, self.OnChangeLabelbook, self.ctrl_labelbook)
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_BUTTON, self.OnChargerRapport, self.bouton_charger_rapport)
        self.Bind(wx.EVT_BUTTON, self.OnSauverRapport, self.bouton_sauver_rapport)
                

    def __set_properties(self):
        self.ctrl_impression.SetMinSize((250, -1))
        self.bouton_charger_rapport.SetToolTip(wx.ToolTip(_(u"Charger les paramètres et personnalisations du rapport sélectionné")))
        self.bouton_sauver_rapport.SetToolTip(wx.ToolTip(_(u"Enregistrer la configuration actuelle comme modèle de rapport")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((950, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Labelbook
        box_informations = wx.StaticBoxSizer(self.box_informations_staticbox, wx.VERTICAL)
        box_informations.Add(self.ctrl_labelbook, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(box_informations, 0, wx.EXPAND, 0)
        
        grid_sizer_droite = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=2, cols=1, vgap=2, hgap=2)
        grid_sizer_parametres.Add(self.ctrl_parametres, 0, wx.EXPAND, 0)
        
        grid_sizer_liens_parametres = wx.FlexGridSizer(rows=1, cols=3, vgap=2, hgap=4)
        grid_sizer_liens_parametres.Add(self.hyper_onglets, 0, 0, 0)
        grid_sizer_liens_parametres.Add(self.label_sep_onglets, 0, 0, 0)
        grid_sizer_liens_parametres.Add(self.hyper_parametres, 0, 0, 0)
        grid_sizer_parametres.Add(grid_sizer_liens_parametres, 0, wx.ALIGN_RIGHT, 0)
        
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(0)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droite.Add(box_parametres, 0, wx.EXPAND, 0)

        # Rapports personnalisés
        box_rapports = wx.StaticBoxSizer(self.box_rapports_staticbox, wx.VERTICAL)
        grid_sizer_rapports = wx.FlexGridSizer(rows=3, cols=1, vgap=3, hgap=2)
        grid_sizer_rapports.Add(self.combo_rapports, 0, wx.EXPAND, 0)

        grid_sizer_boutons_rapports = wx.FlexGridSizer(rows=1, cols=2, vgap=2, hgap=4)
        grid_sizer_boutons_rapports.Add(self.bouton_charger_rapport, 1, wx.EXPAND, 0)
        grid_sizer_boutons_rapports.Add(self.bouton_sauver_rapport, 1, wx.EXPAND, 0)
        grid_sizer_boutons_rapports.AddGrowableCol(0)
        grid_sizer_boutons_rapports.AddGrowableCol(1)
        grid_sizer_rapports.Add(grid_sizer_boutons_rapports, 0, wx.EXPAND, 0)

        grid_sizer_liens_rapports = wx.FlexGridSizer(rows=1, cols=5, vgap=2, hgap=4)
        grid_sizer_liens_rapports.Add(self.hyper_supprimer_rapport, 0, 0, 0)
        grid_sizer_liens_rapports.Add(self.label_sep_rapport1, 0, 0, 0)
        grid_sizer_liens_rapports.Add(self.hyper_exporter_rapport, 0, 0, 0)
        grid_sizer_liens_rapports.Add(self.label_sep_rapport2, 0, 0, 0)
        grid_sizer_liens_rapports.Add(self.hyper_importer_rapport, 0, 0, 0)
        grid_sizer_rapports.Add(grid_sizer_liens_rapports, 0, wx.ALIGN_RIGHT, 0)

        grid_sizer_rapports.AddGrowableCol(0)
        box_rapports.Add(grid_sizer_rapports, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droite.Add(box_rapports, 0, wx.EXPAND, 0)
        
        # Impression
        box_impression = wx.StaticBoxSizer(self.box_impression_staticbox, wx.VERTICAL)
        grid_sizer_impression = wx.FlexGridSizer(rows=3, cols=1, vgap=2, hgap=2)
        grid_sizer_impression.Add(self.ctrl_impression, 0, wx.EXPAND, 0)
        
        grid_sizer_hyperliens = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_hyperliens.Add( (2, 2), 0, 0, 0)
        grid_sizer_hyperliens.Add(self.hyper_selectionner, 0, 0, 0)
        grid_sizer_hyperliens.Add(self.label_separation, 0, 0, 0)
        grid_sizer_hyperliens.Add(self.hyper_deselectionner, 0, 0, 0)
        grid_sizer_hyperliens.AddGrowableCol(0)
        grid_sizer_impression.Add(grid_sizer_hyperliens, 0, wx.EXPAND, 0)
        
        grid_sizer_impression.Add(self.bouton_imprimer, 0, wx.EXPAND|wx.TOP, 5)
        grid_sizer_impression.AddGrowableRow(0)
        grid_sizer_impression.AddGrowableCol(0)
        box_impression.Add(grid_sizer_impression, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droite.Add(box_impression, 1, wx.EXPAND, 0)
        
        grid_sizer_droite.AddGrowableRow(2)
        grid_sizer_droite.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_droite, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
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
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Statistiques")

    def OnBoutonImprimer(self, event): 
        # Demande le type d'impression
        menuPop = UTILS_Adaptations.Menu()

        item = wx.MenuItem(menuPop, 10, _(u"Tout"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=10)
        
        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, 20, _(u"La rubrique affichée"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=20)

        item = wx.MenuItem(menuPop, 30, _(u"La page affichée"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=30)
            
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Imprimer(self, event=None):
        ID = event.GetId() 
        listeCodes = self.ctrl_impression.GetCoches() 
        
        # Imprimer tout
        dlgAttente = wx.BusyInfo(_(u"Création du rapport..."), None)
        if 'phoenix' not in wx.PlatformInfo:
            wx.Yield()
        
        if ID == 10 : 
            html = self.baseHTML.GetHTML(mode="impression", selectionsCodes=listeCodes)
        # Imprimer la rubrique affichée
        if ID == 20 : 
            indexRubrique = self.ctrl_labelbook.GetSelection()
            codeRubrique = self.RechercherElement(indexRubrique=indexRubrique)[0]
            html = self.baseHTML.GetHTML(mode="impression", rubrique=codeRubrique, selectionsCodes=listeCodes)
        # Imprimer la page affichée
        if ID == 30 : 
            codeRubrique, codePage = self.RecherchePageAffichee() 
            html = self.baseHTML.GetHTML(mode="impression", rubrique=codeRubrique, page=codePage, selectionsCodes=listeCodes)
        
        if len(listeCodes) == 0 or len(html) <= 50 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune information à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        del dlgAttente
        
        # Impression
        printout = HtmlPrintout(html)
        printout2 = HtmlPrintout(html)
        preview = wx.PrintPreview(printout, printout2)
        
##        from Utils import UTILS_Printer
##        preview_window = UTILS_Printer.PreviewFrame(preview, None, _(u"Aperçu avant impression"))
##        preview_window.Initialize()
##        preview_window.MakeModal(False)
##        preview_window.Show(True)

        preview.SetZoom(100)
        frame = wx.GetApp().GetTopWindow() 
        preview_window = wx.PreviewFrame(preview, None, _(u"Aperçu avant impression"))
        preview_window.Initialize()
        # preview_window.Show(False)
        preview_window.SetPosition(frame.GetPosition())
        preview_window.SetSize(frame.GetSize())
        preview_window.Show(True)


    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def InitLabelbook(self):
        self.ctrl_labelbook.SetColour(LB.INB_TAB_AREA_BACKGROUND_COLOUR, self.couleurFond)
        self.ctrl_labelbook.SetColour(LB.INB_ACTIVE_TAB_COLOUR, (255, 255, 255) )

        # Création de l'ImageList
        self.dictImages = {
            "individus" : {"img" : wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Personnes.png'), wx.BITMAP_TYPE_PNG), "index" : None},
            "familles" : {"img" : wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Famille.png'), wx.BITMAP_TYPE_PNG), "index" : None},
            }
        
        il = wx.ImageList(16, 16)
        index = 0
        for code, dictImage in self.dictImages.items() :
            il.Add(dictImage["img"])
            dictImage["index"] = index
            index += 1
        self.ctrl_labelbook.AssignImageList(il)

        self.listeContenu = []
        for dictRubrique in self.listeObjets :
            if dictRubrique.get("visible", True) == True :
                self.AjouterRubrique(dictRubrique["code"])
    
    def AjouterRubrique(self, code=""):
        # Recherche du dictRubrique
        targetRubrique = None
        for dictRubrique in self.listeObjets :
            if dictRubrique["code"] == code :
                targetRubrique = dictRubrique
                break

        if not targetRubrique:
            return

        # Création du notebook
        flatNoteBook = FNB.FlatNotebook(self.ctrl_labelbook, -1, agwStyle=FNB.FNB_BOTTOM 
                                                                        | FNB.FNB_NO_TAB_FOCUS
                                                                        | FNB.FNB_NO_X_BUTTON
                                                                        )
        flatNoteBook.SetTabAreaColour(self.couleurFond)
        
        # Mémorise le ctrl flatNoteBook
        targetRubrique["ctrl_notebook"] = flatNoteBook
        
        # Création des pages
        listePages = []
        for dictPage in targetRubrique.get("pages", []) :
            if dictPage.get("visible", True) == True :
                ctrl_html = MyHtml(flatNoteBook)
                flatNoteBook.AddPage(ctrl_html, dictPage["nom"])
                dictPage["ctrl_html"] = ctrl_html
                listePages.append(dictPage["code"])
            else:
                dictPage["ctrl_html"] = None
        
        # Si aucune page visible, on n'affiche pas la rubrique
        if len(listePages) == 0:
            targetRubrique["visible"] = False
            return

        # Ajoute le notebook au labelbook
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnChangeNotebook, flatNoteBook)
        if targetRubrique["code"] in self.dictImages:
            indexImage = self.dictImages[targetRubrique["code"]]["index"]
        else:
            indexImage = -1
        self.ctrl_labelbook.AddPage(flatNoteBook, targetRubrique["nom"], imageId=indexImage)
        
        self.listeContenu.append((targetRubrique["code"], listePages))

    def MAJpageAffichee(self):
        indexRubrique = self.ctrl_labelbook.GetSelection()
        if indexRubrique == wx.NOT_FOUND or indexRubrique < 0:
            return
        # Recherche la page à MAJ
        indexR = 0
        for dictRubrique in self.listeObjets :
            if dictRubrique.get("visible", True) == True :
                if indexR == indexRubrique :
                    ctrl_notebook = dictRubrique.get("ctrl_notebook", None)
                    if ctrl_notebook and ctrl_notebook.GetPageCount() > 0:
                        indexPage = ctrl_notebook.GetSelection() 
                        if indexPage != wx.NOT_FOUND and indexPage >= 0:
                            self.MAJpage(indexRubrique, indexPage)
                    break
                indexR += 1

    def MAJpage(self, indexRubrique=None, indexPage=None):
        """ Met à jour le contenu d'une page """
        if indexRubrique is None or indexRubrique < 0:
            return None
        if indexPage is None or indexPage < 0:
            return None

        dlgAttente = wx.BusyInfo(_(u"Actualisation des données..."), None)
        if 'phoenix' not in wx.PlatformInfo:
            wx.Yield()
        
        codeRubrique = None
        codePage = None
        ctrl_html = None
        indexR = 0
        # Recherche de la rubrique
        for dictRubrique in self.listeObjets :
            if dictRubrique.get("visible", True) == True :
                if indexR == indexRubrique :
                    codeRubrique = dictRubrique["code"]
                    ctrl_notebook = dictRubrique.get("ctrl_notebook", None)
                    # Recherche de la page
                    indexP = 0
                    for dictPage in dictRubrique.get("pages", []) :
                        if dictPage.get("visible", True) == True :
                            if indexP == indexPage :
                                codePage = dictPage["code"]
                                ctrl_html = dictPage.get("ctrl_html", None)
                                break
                            indexP += 1
                    break
                indexR += 1
        
        if codeRubrique == None or codePage == None or ctrl_html == None :
            del dlgAttente
            return None
        
        # MAJ du contrôles HTML
        self.baseHTML.MAJ(page=codePage)
        pageHTML = self.baseHTML.GetHTML(page=codePage) 
        ctrl_html.SetPage(pageHTML)
        
        del dlgAttente
    
    def RechercherElement(self, indexRubrique=None, indexPage=None):
        """ retourne le codeRubrique et codePage par rapport aux index """
        codeRubrique = None
        codePage = None
        indexR = 0
        for dictRubrique in self.listeObjets :
            if dictRubrique.get("visible", True) == True :
                if indexR == indexRubrique or indexRubrique == None :
                    codeRubrique = dictRubrique["code"]
                    ctrl_notebook = dictRubrique.get("ctrl_notebook", None)
                    # Recherche de la page
                    indexP = 0
                    for dictPage in dictRubrique.get("pages", []) :
                        if dictPage.get("visible", True) == True :
                            if indexP == indexPage :
                                codePage = dictPage["code"]
                                ctrl_html = dictPage.get("ctrl_html", None)
                                break
                            indexP += 1
                    break
                indexR += 1
        return codeRubrique, codePage
    
    def RecherchePageAffichee(self):
        indexRubrique = self.ctrl_labelbook.GetSelection()
        codeRubrique = None
        codePage = None
        if indexRubrique == wx.NOT_FOUND or indexRubrique < 0:
            return codeRubrique, codePage
        # Recherche la page à MAJ
        indexR = 0
        for dictRubrique in self.listeObjets :
            if dictRubrique.get("visible", True) == True :
                if indexR == indexRubrique :
                    ctrl_notebook = dictRubrique.get("ctrl_notebook", None)
                    if ctrl_notebook and ctrl_notebook.GetPageCount() > 0:
                        indexPage = ctrl_notebook.GetSelection() 
                        indexP = 0
                        for dictPage in dictRubrique.get("pages", []) :
                            if dictPage.get("visible", True) == True :
                                if indexP == indexPage :
                                    codeRubrique = dictRubrique["code"]
                                    codePage = dictPage["code"]
                                    ctrl_html = dictPage.get("ctrl_html", None)
                                    return codeRubrique, codePage
                indexR += 1
        return codeRubrique, codePage
        
    def OnChangeLabelbook(self, event):
        self.MAJpageAffichee() 
##        indexRubrique = self.ctrl_labelbook.GetSelection()
##        # Recherche la page à MAJ
##        indexR = 0
##        for dictRubrique in self.listeObjets :
##            if dictRubrique["visible"] == True :
##                if indexR == indexRubrique :
##                    ctrl_notebook = dictRubrique["ctrl_notebook"]
##                    indexPage = ctrl_notebook.GetSelection() 
##                    self.MAJpage(indexRubrique, indexPage)
##                indexR += 1
        
    def OnChangeNotebook(self, event):
        indexRubrique = self.ctrl_labelbook.GetSelection()
        indexPage = event.GetSelection()
        self.MAJpage(indexRubrique, indexPage)
    
    def AjouterElement(self, code="", afficher=True):
        """ Ajoute une rubrique, une page ou un objet """
        indexR = 0
        for dictRubrique in self.listeObjets :
            if dictRubrique["code"] == code :
                # Affiche la rubrique
                if etat == True and dictRubrique["visible"] == False :
                    pass
    
    def Coche(self, etat=True):
        self.ctrl_impression.Coche(etat)
    
    def ModificationParametres(self, premiere=False):
        if premiere == True :
            dateJour = datetime.date.today() 
            annee = dateJour.year
            self.dictParametres = {"mode":"presents", "periode":{"type":"annee", "annee":annee, "date_debut":datetime.date(annee, 1, 1), "date_fin":datetime.date(annee, 12, 31)}, "listeActivites":[], "dictActivites":{} }
        
        # Demande les paramètres à l'utilisateur
        dlg = DLG_Stats_parametres.Dialog(self)
        dlg.SetParametres(self.dictParametres)
        if dlg.ShowModal() == wx.ID_OK:
            self.dictParametres = dlg.GetDictParametres()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        # Envoi des paramètres à l'afficheur HTML
        self.ctrl_parametres.SetParametres(self.dictParametres)
        self.ctrl_parametres.MAJ() 
        
        # Envoi des paramètres à la baseHTML
        self.baseHTML.SetParametres(self.dictParametres)
        
        # Actualisation de la page affichée actuellement
        self.MAJpageAffichee()
        return True

    def ChargerTableauxCroisesSauvegardes(self):
        """ Charge et insère les tableaux personnalisés enregistrés localement """
        listeDefs = CROISE.GetTableauxPersonnalisesSauvegardes()
        for def_tab in listeDefs:
            self.AjouterTableauCroise(def_tab, maj_ui=False)

    def AjouterTableauCroise(self, definition, maj_ui=True):
        """ Instancie et ajoute un tableau croisé dynamique à la page cible """
        tab = CROISE.TableauCroiseDynamique(definition)
        codeRub = definition.get("rubrique", "individus")
        codePg = definition.get("page", "individus_nombre")

        for dictRubrique in self.listeObjets:
            if dictRubrique["code"] == codeRub:
                for dictPage in dictRubrique["pages"]:
                    if dictPage["code"] == codePg:
                        objExistant = False
                        for idxObj, obj in enumerate(dictPage["objets"]):
                            if getattr(obj, "code", None) == tab.code:
                                dictPage["objets"][idxObj] = tab
                                objExistant = True
                                break
                        if not objExistant:
                            dictPage["objets"].append(tab)
                        break
                break

        if maj_ui:
            if hasattr(self, "ctrl_impression") and self.ctrl_impression:
                self.ctrl_impression.MAJ()
            self.MAJpageAffichee()

    def CreerNouveauTableau(self, codeRubrique, codePage):
        """ Ouvre l'assistant de création d'un tableau croisé """
        from Dlg import DLG_Nouveau_tableau
        dlg = DLG_Nouveau_tableau.Dialog(self, rubrique=codeRubrique, page=codePage)
        if dlg.ShowModal() == wx.ID_OK:
            definition = dlg.GetDefinition()
            if definition:
                self.AjouterTableauCroise(definition, maj_ui=True)
        dlg.Destroy()

    def SupprimerTableau(self, codeObjet):
        """ Supprime un tableau personnalisé """
        dlg = wx.MessageDialog(self, _(u"Voulez-vous vraiment supprimer ce tableau personnalisé ?"), _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            for dictRubrique in self.listeObjets:
                for dictPage in dictRubrique["pages"]:
                    dictPage["objets"] = [obj for obj in dictPage["objets"] if getattr(obj, "code", None) != codeObjet]
            CROISE.SupprimerTableauPerso(codeObjet)
            if hasattr(self, "ctrl_impression") and self.ctrl_impression:
                self.ctrl_impression.MAJ()
            self.MAJpageAffichee()
        dlg.Destroy()

    def DeplacerTableau(self, codeObjet, direction="monter"):
        """ Déplace un tableau ou graphique vers le haut ou vers le bas sur sa page """
        for dictRubrique in self.listeObjets:
            for dictPage in dictRubrique["pages"]:
                objets = dictPage["objets"]
                indices = [i for i, obj in enumerate(objets) if getattr(obj, "code", None) == codeObjet]
                if indices:
                    idx = indices[0]
                    if direction == "monter" and idx > 0:
                        objets[idx - 1], objets[idx] = objets[idx], objets[idx - 1]
                        if hasattr(self, "ctrl_impression") and self.ctrl_impression:
                            self.ctrl_impression.MAJ()
                        self.MAJpageAffichee()
                    elif direction == "descendre" and idx < len(objets) - 1:
                        objets[idx + 1], objets[idx] = objets[idx], objets[idx + 1]
                        if hasattr(self, "ctrl_impression") and self.ctrl_impression:
                            self.ctrl_impression.MAJ()
                        self.MAJpageAffichee()
                    return

    def MasquerTableau(self, codeObjet):
        """ Masque un tableau ou graphique sur sa page """
        for dictRubrique in self.listeObjets:
            for dictPage in dictRubrique["pages"]:
                for obj in dictPage["objets"]:
                    if getattr(obj, "code", None) == codeObjet:
                        obj.visible = False
                        if hasattr(self, "ctrl_impression") and self.ctrl_impression:
                            if hasattr(self.ctrl_impression, "DecocherCode"):
                                self.ctrl_impression.DecocherCode(codeObjet)
                            self.ctrl_impression.MAJ()
                        self.MAJpageAffichee()
                        return

    def OrganiserPage(self, codeRubrique, codePage):
        """ Ouvre la boîte de dialogue d'organisation de la page (ordre et visibilité) """
        page_dict = None
        for dictRubrique in self.listeObjets:
            if dictRubrique["code"] == codeRubrique:
                for dictP in dictRubrique["pages"]:
                    if dictP["code"] == codePage:
                        page_dict = dictP
                        break
                break
        if not page_dict:
            return
        from Dlg import DLG_Organiser_page
        dlg = DLG_Organiser_page.Dialog(self, page_dict=page_dict)
        if dlg.ShowModal() == wx.ID_OK:
            if hasattr(self, "ctrl_impression") and self.ctrl_impression:
                self.ctrl_impression.MAJ()
            self.MAJpageAffichee()
        dlg.Destroy()

    def PersonnaliserTableau(self, codeObjet):
        """ Ouvre la boîte de dialogue de personnalisation du tableau sélectionné """
        objet = self.baseHTML.GetObjet(codeObjet)
        if not objet:
            return
        from Dlg import DLG_Personnalisation_tableau
        dlg = DLG_Personnalisation_tableau.Dialog(self, objet=objet)
        if dlg.ShowModal() == wx.ID_OK:
            # Actualisation de la page affichée actuellement
            self.MAJpageAffichee()
        dlg.Destroy()

    def MAJRapportsCombo(self, selectionNom=None):
        """ Met à jour la liste des rapports dans le contrôle Choice """
        liste = RAPPORTS.GetListeRapports()
        self.combo_rapports.Clear()
        for nom in liste:
            self.combo_rapports.Append(nom)
        if selectionNom and selectionNom in liste:
            self.combo_rapports.SetStringSelection(selectionNom)
        elif len(liste) > 0:
            self.combo_rapports.SetSelection(0)
        self.bouton_charger_rapport.Enable(len(liste) > 0)
        self.hyper_supprimer_rapport.Enable(len(liste) > 0)
        self.hyper_exporter_rapport.Enable(len(liste) > 0)

    def OnChargerRapport(self, event=None):
        """ Charge la configuration d'un rapport enregistré """
        nom = self.combo_rapports.GetStringSelection()
        if not nom:
            dlg = wx.MessageDialog(self, _(u"Veuillez sélectionner un rapport dans la liste."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        rapport = RAPPORTS.ChargerRapport(nom)
        if not rapport:
            dlg = wx.MessageDialog(self, _(u"Impossible de charger le modèle de rapport '%s'.") % nom, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Application des paramètres
        self.dictParametres = rapport.get("dictParametres", {})
        dictPersonnalisations = rapport.get("dictPersonnalisations", {})
        selectionsCodes = rapport.get("selectionsCodes", [])
        
        # Charger les tableaux personnalisés sauvegardés dans ce rapport
        tableauxPersonnalises = rapport.get("tableauxPersonnalises", [])
        for def_tab in tableauxPersonnalises:
            self.AjouterTableauCroise(def_tab, maj_ui=False)

        # Restaurer l'ordre et la visibilité des pages
        organisationsPages = rapport.get("organisationsPages", {})
        if organisationsPages:
            for dictR in self.listeObjets:
                for dictP in dictR["pages"]:
                    p_code = dictP["code"]
                    if p_code in organisationsPages:
                        ordre_vis = organisationsPages[p_code]
                        dict_ord = {item["code"]: (idx, item.get("visible", True)) for idx, item in enumerate(ordre_vis)}
                        def tri_obj(o):
                            if getattr(o, "code", None) in dict_ord:
                                return dict_ord[o.code][0]
                            return 999
                        dictP["objets"].sort(key=tri_obj)
                        for o in dictP["objets"]:
                            if getattr(o, "code", None) in dict_ord:
                                o.visible = dict_ord[o.code][1]

        # Restaurer la visibilité des onglets
        ongletsVisibles = rapport.get("ongletsVisibles", {})
        if ongletsVisibles:
            self.AppliquerVisibiliteOnglets(ongletsVisibles)
            self.ReconstruireOnglets()

        self.ctrl_parametres.SetParametres(self.dictParametres)
        self.ctrl_parametres.MAJ()
        self.baseHTML.SetParametres(self.dictParametres)
        self.baseHTML.SetPersonnalisations(dictPersonnalisations)
        if hasattr(self, "ctrl_impression") and self.ctrl_impression:
            self.ctrl_impression.MAJ()
            if selectionsCodes:
                self.ctrl_impression.SetCoches(selectionsCodes)
        
        # Actualisation de l'affichage
        self.MAJpageAffichee()
        
        dlg = wx.MessageDialog(self, _(u"Le modèle de rapport '%s' a été chargé avec succès.") % nom, _(u"Succès"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnSauverRapport(self, event=None):
        """ Enregistre les paramètres et personnalisations sous un nom """
        nomDefaut = self.combo_rapports.GetStringSelection() if self.combo_rapports.GetCount() > 0 else u""
        dlg = wx.TextEntryDialog(self, _(u"Veuillez saisir un nom pour ce modèle de rapport :"), _(u"Enregistrer un rapport"), nomDefaut)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue().strip()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        if not nom:
            return
        
        selectionsCodes = self.ctrl_impression.GetCoches()
        dictPersonnalisations = self.baseHTML.GetPersonnalisations()
        tableauxPersonnalises = [getattr(obj, "definition", {}) for dictR in self.listeObjets for dictP in dictR["pages"] for obj in dictP["objets"] if getattr(obj, "is_custom", False)]
        organisationsPages = {dictP["code"]: [{"code": obj.code, "visible": getattr(obj, "visible", True)} for obj in dictP["objets"]] for dictR in self.listeObjets for dictP in dictR["pages"]}
        ongletsVisibles = {}
        for dictR in self.listeObjets:
            ongletsVisibles[dictR["code"]] = {
                "visible": dictR.get("visible", True),
                "pages": {p["code"]: p.get("visible", True) for p in dictR.get("pages", [])}
            }
        
        succes, chemin = RAPPORTS.SauvegarderRapport(
            nom=nom, 
            dictParametres=self.dictParametres, 
            dictPersonnalisations=dictPersonnalisations, 
            selectionsCodes=selectionsCodes,
            tableauxPersonnalises=tableauxPersonnalises,
            organisationsPages=organisationsPages,
            ongletsVisibles=ongletsVisibles
        )
        if succes:
            self.MAJRapportsCombo(selectionNom=nom)
            dlg = wx.MessageDialog(self, _(u"Le modèle de rapport '%s' a été enregistré avec succès.") % nom, _(u"Succès"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self, _(u"Erreur lors de l'enregistrement du rapport."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def OnGestionOnglets(self, event=None):
        """ Ouvre la boîte de dialogue pour afficher / masquer les onglets et rubriques """
        from Dlg import DLG_Gestion_onglets
        dlg = DLG_Gestion_onglets.Dialog(self, liste_objets=self.listeObjets)
        if dlg.ShowModal() == wx.ID_OK:
            self.SauvegarderOngletsPerso()
            self.ReconstruireOnglets()
        dlg.Destroy()

    def ReconstruireOnglets(self):
        """ Reconstruit l'affichage du LabelBook et des sous-onglets selon la visibilité configurée """
        try:
            self.ctrl_labelbook.DeleteAllPages()
        except Exception:
            while self.ctrl_labelbook.GetPageCount() > 0:
                self.ctrl_labelbook.DeletePage(0)
        
        self.listeContenu = []
        for dictRubrique in self.listeObjets:
            dictRubrique["ctrl_notebook"] = None
            for dictPage in dictRubrique.get("pages", []):
                dictPage["ctrl_html"] = None
            if dictRubrique.get("visible", True) == True:
                has_page = any(p.get("visible", True) for p in dictRubrique.get("pages", []))
                if has_page:
                    self.AjouterRubrique(dictRubrique["code"])
                else:
                    dictRubrique["visible"] = False

        if self.ctrl_labelbook.GetPageCount() > 0:
            self.ctrl_labelbook.SetSelection(0)
        
        if hasattr(self, "ctrl_impression") and self.ctrl_impression:
            self.ctrl_impression.MAJ()

        self.MAJpageAffichee()

    def AppliquerVisibiliteOnglets(self, dictOnglets):
        """ Applique un dictionnaire de visibilité sur self.listeObjets """
        if not dictOnglets:
            return
        for dictRubrique in self.listeObjets:
            codeRub = dictRubrique["code"]
            if codeRub in dictOnglets:
                infoRub = dictOnglets[codeRub]
                dictRubrique["visible"] = infoRub.get("visible", True)
                pagesDict = infoRub.get("pages", {})
                for p in dictRubrique.get("pages", []):
                    if p["code"] in pagesDict:
                        p["visible"] = pagesDict[p["code"]]

    def SauvegarderOngletsPerso(self):
        """ Enregistre la visibilité des onglets dans la configuration locale """
        rep = RAPPORTS.GetRepertoireRapports()
        chemin = os.path.join(rep, "onglets_visibles.json")
        dictOnglets = {}
        for dictRubrique in self.listeObjets:
            codeRub = dictRubrique["code"]
            dictOnglets[codeRub] = {
                "visible": dictRubrique.get("visible", True),
                "pages": {p["code"]: p.get("visible", True) for p in dictRubrique.get("pages", [])}
            }
        try:
            with io.open(chemin, "w", encoding="utf-8") as f:
                f.write(json.dumps(dictOnglets, indent=2, ensure_ascii=False))
        except Exception:
            pass

    def ChargerOngletsPersoSauvegardes(self):
        """ Charge la visibilité des onglets depuis la configuration locale """
        rep = RAPPORTS.GetRepertoireRapports()
        chemin = os.path.join(rep, "onglets_visibles.json")
        if not os.path.exists(chemin):
            return
        try:
            with io.open(chemin, "r", encoding="utf-8") as f:
                dictOnglets = json.loads(f.read())
            self.AppliquerVisibiliteOnglets(dictOnglets)
        except Exception:
            pass

    def OnSupprimerRapport(self):
        """ Supprime le rapport sélectionné """
        nom = self.combo_rapports.GetStringSelection()
        if not nom:
            return
        dlg = wx.MessageDialog(self, _(u"Voulez-vous vraiment supprimer le modèle de rapport '%s' ?") % nom, _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            RAPPORTS.SupprimerRapport(nom)
            self.MAJRapportsCombo()
        dlg.Destroy()

    def OnExporterRapport(self):
        """ Exporte le rapport au format JSON """
        nom = self.combo_rapports.GetStringSelection()
        if not nom:
            return
        RAPPORTS.ExporterRapport(self, nom)

    def OnImporterRapport(self):
        """ Importe un rapport depuis un fichier JSON """
        nom = RAPPORTS.ImporterRapport(self)
        if nom:
            self.MAJRapportsCombo(selectionNom=nom)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    
    dialog_1.ModificationParametres(premiere=True) 
    
    dialog_1.ShowModal()
    app.MainLoop()
