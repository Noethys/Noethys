#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Utils import UTILS_Dates
import datetime
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import BitmapComboBox
else :
    from wx.combo import BitmapComboBox
from Ctrl import CTRL_Bandeau

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import numpy as np
import matplotlib
matplotlib.interactive(False)
matplotlib.use('wxagg')
try :
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas
    from matplotlib.pyplot import setp
    import matplotlib.dates as mdates
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FormatStrFormatter
except Exception as err :
    print("Erreur d'import : ", Exception, err)



LISTE_MODELES = [
    {"code" : "repartition_categories_debit_tresorerie", "label" : _(u"Répartition des opérations de trésorerie au débit"), "image" : "Repartition.png"},
    {"code" : "repartition_categories_credit_tresorerie", "label" : _(u"Répartition des opérations de trésorerie au crédit"), "image" : "Repartition.png"},
    {"code" : "repartition_categories_debit_budgetaires", "label" : _(u"Répartition des opérations budgétaires au débit"), "image" : "Repartition.png"},
    {"code" : "repartition_categories_credit_budgetaires", "label" : _(u"Répartition des opérations budgétaires au crédit"), "image" : "Repartition.png"},
    {"code" : "repartition_categories_debit_tresorerie_budgetaires", "label" : _(u"Répartition des opérations de trésorerie + budgétaires au débit"), "image" : "Repartition.png"},
    {"code" : "repartition_categories_credit_tresorerie_budgetaires", "label" : _(u"Répartition des opérations de trésorerie + budgétaires au crédit"), "image" : "Repartition.png"},
    {"code" : "tiers_debit", "label" : _(u"Dépenses par tiers"), "image" : "Barres.png"},
    {"code" : "tiers_credit", "label" : _(u"Recettes par tiers"), "image" : "Barres.png"},
    #{"code" : "repartition_depenses", "label" : _(u"Graphique 3"), "image" : "Courbes2.png"},
    ]


class CTRL_Modele(BitmapComboBox):
    def __init__(self, parent, size=(-1,  -1)):
        BitmapComboBox.__init__(self, parent, size=size, style=wx.CB_READONLY)
        self.parent = parent
        self.MAJlisteDonnees() 
        if len(self.dictDonnees) > 0 :
            self.SetSelection(0)
    
    def MAJlisteDonnees(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        for label, bmp in listeItems :
            self.Append(label, bmp, label)
    
    def GetListeDonnees(self):
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for dictModele in LISTE_MODELES :
            self.dictDonnees[index] = { "ID" : dictModele["code"] }
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/%s" % dictModele["image"]), wx.BITMAP_TYPE_ANY)
            listeItems.append((dictModele["label"], bmp))
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetLabel(self):
        return self.GetStringSelection()

# -----------------------------------------------------------------------------------------------------------------------


class CTRL_Exercice(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDdefaut = None
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
        self.SetID(self.IDdefaut)
    
    def GetListeDonnees(self):
        listeItems = [_(u"Tous les exercices"),]
        self.dictDonnees = { 0 : {"ID":None, "date_debut":None, "date_fin":None}, }
        DB = GestionDB.DB()
        req = """SELECT IDexercice, nom, date_debut, date_fin, defaut
        FROM compta_exercices
        ORDER BY date_debut; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDexercice, nom, date_debut, date_fin, defaut in listeDonnees :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            self.dictDonnees[index] = { "ID" : IDexercice, "date_debut" : date_debut, "date_fin" : date_fin}
            label = nom
            listeItems.append(label)
            if defaut == 1 :
                self.IDdefaut = IDexercice
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetDictExercice(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Analytique(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDdefaut = None
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
        self.SetID(self.IDdefaut)
    
    def GetListeDonnees(self):
        listeItems = [_(u"Tous les postes analytiques"),]
        self.dictDonnees = { 0 : {"ID":None}, }
        DB = GestionDB.DB()
        req = """SELECT IDanalytique, nom, abrege, defaut
        FROM compta_analytiques
        ORDER BY nom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDanalytique, nom, abrege, defaut in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDanalytique }
            label = nom
            listeItems.append(label)
            if defaut == 1 :
                self.IDdefaut = IDanalytique
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Graphique(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        self.dictParametres = None
        self.afficher_valeurs = False
        
        # Init canvas
        self.figure = matplotlib.pyplot.figure()
        self.canvas = Canvas(self, -1, self.figure)
        self.canvas.SetMinSize((20, 20))
        self.SetColor( (255,255,255) )

        # Layout
        sizer_canvas = wx.BoxSizer(wx.VERTICAL)
        sizer_canvas.Add(self.canvas, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_canvas)
        self.Layout()

    def OnBoutonZoom(self, event):
        from Dlg import DLG_Zoom_graphe
        dlg = DLG_Zoom_graphe.Dialog(self, figure=self.figure)
        dlg.ShowModal() 
        dlg.Destroy()

    def OnBoutonOptions(self, event):
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        item = wx.MenuItem(menuPop, 10, _(u"Afficher les valeurs"), _(u"Afficher les valeurs"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_afficher_valeurs, id=10)
        if self.afficher_valeurs == True : item.Check(True)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def On_afficher_valeurs(self, event):
        self.afficher_valeurs = not self.afficher_valeurs
        self.MAJ() 

    def SetColor(self, rgbtuple=None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))
    
    def ConvertCouleur(self, couleur=None):
        return [c/255. for c in couleur]
    
    def SetParametres(self, dictParametres=None) :
        self.dictParametres = dictParametres
        
    def MAJ(self) :
        self.figure.clear()
        if self.dictParametres == None :
            wx.CallAfter(self.SendSizeEvent)
            return
        
        if self.dictParametres["IDmodele"] == "repartition_categories_debit_tresorerie" : self.Graphe_repartition_categories(typeCategorie="debit", typeDonnees="tresorerie")
        if self.dictParametres["IDmodele"] == "repartition_categories_credit_tresorerie" : self.Graphe_repartition_categories(typeCategorie="credit", typeDonnees="tresorerie")
        if self.dictParametres["IDmodele"] == "repartition_categories_debit_budgetaires" : self.Graphe_repartition_categories(typeCategorie="debit", typeDonnees="budgetaires")
        if self.dictParametres["IDmodele"] == "repartition_categories_credit_budgetaires" : self.Graphe_repartition_categories(typeCategorie="credit", typeDonnees="budgetaires")
        if self.dictParametres["IDmodele"] == "repartition_categories_debit_tresorerie_budgetaires" : self.Graphe_repartition_categories(typeCategorie="debit", typeDonnees="tresorerie+budgetaires")
        if self.dictParametres["IDmodele"] == "repartition_categories_credit_tresorerie_budgetaires" : self.Graphe_repartition_categories(typeCategorie="credit", typeDonnees="tresorerie+budgetaires")
        if self.dictParametres["IDmodele"] == "tiers_debit" : self.Graphe_tiers(typeCategorie="debit")
        if self.dictParametres["IDmodele"] == "tiers_credit" : self.Graphe_tiers(typeCategorie="credit")
        self.Layout()

    def Graphe_repartition_categories(self, typeCategorie="", typeDonnees="tresorerie+budgetaires"):
        # Récupération des données
        conditions = []
        if self.dictParametres["date_debut"] != None :
            conditions.append("date_budget>='%s'" % self.dictParametres["date_debut"])
            conditions.append("date_budget<='%s'" % self.dictParametres["date_fin"])
        if self.dictParametres["IDanalytique"] != None :
            conditions.append("IDanalytique=%d" % self.dictParametres["IDanalytique"])
        if len(conditions) > 0 :
            ConditionsStr = "AND " + " AND ".join(conditions)
        else :
            ConditionsStr = ""
            
        DB = GestionDB.DB()
        dictDonnees = {}
        
        if "budgetaires" in typeDonnees :
            req = """SELECT compta_operations_budgetaires.IDcategorie, compta_categories.nom, SUM(compta_operations_budgetaires.montant)
            FROM compta_operations_budgetaires
            LEFT JOIN compta_categories ON compta_categories.IDcategorie = compta_operations_budgetaires.IDcategorie
            WHERE compta_operations_budgetaires.type='%s' %s
            GROUP BY compta_operations_budgetaires.IDcategorie
            ;""" % (typeCategorie, ConditionsStr)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            for IDcategorie, nom, montant in listeDonnees :
                if (IDcategorie in dictDonnees) == False :
                    dictDonnees[IDcategorie] = {"nom" : nom, "montant" : 0.0}
                dictDonnees[IDcategorie]["montant"] += montant
        
        if "tresorerie" in typeDonnees :
            req = """SELECT compta_ventilation.IDcategorie, compta_categories.nom, SUM(compta_ventilation.montant)
            FROM compta_ventilation
            LEFT JOIN compta_categories ON compta_categories.IDcategorie = compta_ventilation.IDcategorie
            WHERE type='%s' %s
            GROUP BY compta_ventilation.IDcategorie
            ;""" % (typeCategorie, ConditionsStr)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            for IDcategorie, nom, montant in listeDonnees :
                if (IDcategorie in dictDonnees) == False :
                    dictDonnees[IDcategorie] = {"nom" : nom, "montant" : 0.0}
                dictDonnees[IDcategorie]["montant"] += montant

        DB.Close()
        if len(dictDonnees) == 0 :
            return

        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        
        montantTotal = 0.0
        for IDcategorie, dictTemp in dictDonnees.items() :
            montantTotal += dictTemp["montant"]
            
        index = 1
        for IDcategorie, dictTemp in dictDonnees.items() :
            listeValeurs.append(dictTemp["montant"])
            label = dictTemp["nom"]
            if self.afficher_valeurs == True :
                label += u"\n%.2f %s" % (float(montant), SYMBOLE)
            listeLabels.append(label)            
            
            couleur = 1.0 * montant / montantTotal
            couleur = matplotlib.cm.hsv(index * 0.1)
            listeCouleurs.append(couleur)
            
            index += 1
                
        # Création du graphique
        ax = self.figure.add_subplot(111)
        cam = ax.pie(listeValeurs, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
        title = ax.set_title(self.dictParametres["nom"], weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=11)
        ax.set_aspect(1)
        labels, labelsPourcent = cam[1], cam[2]
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=11) 
        matplotlib.pyplot.setp(labelsPourcent, rotation=0, fontsize=9) 

        # Finalisation
        ax.autoscale_view('tight')
        ax.figure.canvas.draw()
        wx.CallAfter(self.SendSizeEvent)


    def Graphe_tiers(self, typeCategorie=""):
        # Récupération des données
        conditions = []
        if self.dictParametres["date_debut"] != None :
            conditions.append("date_budget>='%s'" % self.dictParametres["date_debut"])
            conditions.append("date_budget<='%s'" % self.dictParametres["date_fin"])
        if self.dictParametres["IDanalytique"] != None :
            conditions.append("IDanalytique=%d" % self.dictParametres["IDanalytique"])
        if len(conditions) > 0 :
            ConditionsStr = "AND " + " AND ".join(conditions)
        else :
            ConditionsStr = ""
        
        DB = GestionDB.DB()
        req = """SELECT compta_tiers.IDtiers, compta_tiers.nom, SUM(compta_ventilation.montant)
        FROM compta_tiers
        LEFT JOIN compta_operations ON compta_operations.IDtiers = compta_tiers.IDtiers
        LEFT JOIN compta_ventilation ON compta_ventilation.IDoperation = compta_operations.IDoperation
        WHERE type='%s' %s
        GROUP BY compta_tiers.IDtiers
        ;""" % (typeCategorie, ConditionsStr)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 :
            return
        
        listeValeurs = []
        listeLabels = []
        listeCouleurs = []
        
        for IDtiers, nom, montant in listeDonnees :
            listeValeurs.append(montant)
            listeLabels.append(nom)

        listeIndex = np.arange(len(listeLabels))
        bar_height = 0.2
        opacity = 0.4
        
        ax = self.figure.add_subplot(111)
        barres = ax.barh(listeIndex, listeValeurs, height=bar_height, align='center', alpha=opacity)

        # Formatage des montants sur x
        majorFormatter = FormatStrFormatter(u"%d " + SYMBOLE)
        ax.xaxis.set_major_formatter(majorFormatter)
        
        # Affichage des labels x
        ax.set_yticks(listeIndex) 
        ax.set_yticklabels(listeLabels)

        def autolabel(rects):
            # attach some text labels
            for rect in rects:
                width = rect.get_width()
                ax.text(width + 10, rect.get_y()+rect.get_height()/2., u"%.2f %s" % (int(width), SYMBOLE), ha='left', va='center', fontsize=8, color="grey")
        
        if self.afficher_valeurs == True :
            autolabel(barres)

        # Recherche la largeur de texte max
        largeurMax = 0
        for label in listeLabels :
            if len(label) > largeurMax :
                largeurMax = len(label) 
        
        # Espaces autour du graph
        margeGauche = 0.1 + largeurMax * 0.008
        self.figure.subplots_adjust(left=margeGauche, right=None, wspace=None, hspace=None)

        # Finalisation
        ax.autoscale_view('tight')
##        ax.grid(True, linestyle=":")
        ax.figure.canvas.draw()
        wx.CallAfter(self.SendSizeEvent)
        return













        # Récupération des données
        from Ol import OL_Suivi_budget
        analyse = OL_Suivi_budget.Analyse(self.dictBudget)
        listeCategories = analyse.GetValeurs() 
                
        listeRealise = []
        listeBudgete = []
        listeLabels = []

        for dictCategorie in listeCategories :
            listeRealise.append(dictCategorie["realise"])
            listeBudgete.append(dictCategorie["plafond"])
            listeLabels.append(dictCategorie["nomCategorie"])
            
##            if dictCategorie["typeCategorie"] == "debit" : 
##                solde = plafond - realise
##            else :
##                solde = realise - plafond

##        # TEST
##        listeIndex = np.arange(len(listeLabels))
##        bar_width = 0.2
##        opacity = 0.4
##        
##        ax = self.figure.add_subplot(111)
##        barres = ax.bar(listeIndex, listeRealise, width=bar_width, alpha=opacity, color="g", label=_(u"Réel"))
##        barres = ax.bar(listeIndex + bar_width, listeBudgete, width=bar_width, alpha=opacity, color="b", label=_(u"Budgété"))
##
##        # Formatage des montants sur y
##        majorFormatter = FormatStrFormatter(SYMBOLE + u" %d")
##        ax.yaxis.set_major_formatter(majorFormatter)
##        
##        # Affichage des labels x
##        ax.set_xticks(listeIndex + bar_width) 
##        ax.set_xticklabels(listeLabels)
##        
##        labels = ax.get_xticklabels()
##        setp(labels, rotation=45) 
##        
##        # Légende
##        props = matplotlib.font_manager.FontProperties(size=10)
##        leg = ax.legend(loc='best', shadow=False, fancybox=True, prop=props)
##        leg.get_frame().set_alpha(0.5)
##
##        # Espaces autour du graph
##        self.figure.subplots_adjust(left=0.12, bottom=0.40, right=None, wspace=None, hspace=None)


        # TEST
        listeIndex = np.arange(len(listeLabels))
        bar_height = 0.2
        opacity = 0.4
        
        ax = self.figure.add_subplot(111)
        barresRealise = ax.barh(listeIndex, listeRealise, height=bar_height, alpha=opacity, color="g", label=_(u"Réel"))
        barresBudgete = ax.barh(listeIndex + bar_height, listeBudgete, height=bar_height, alpha=opacity, color="b", label=_(u"Budgété"))

        # Formatage des montants sur x
        majorFormatter = FormatStrFormatter(u"%d " + SYMBOLE)
        ax.xaxis.set_major_formatter(majorFormatter)
        
        # Affichage des labels x
        ax.set_yticks(listeIndex + bar_height) 
        ax.set_yticklabels(listeLabels)

        def autolabel(rects):
            # attach some text labels
            for rect in rects:
                width = rect.get_width()
                ax.text(width + 20, rect.get_y()+rect.get_height()/2., u"%.2f %s" % (int(width), SYMBOLE), ha='left', va='center', fontsize=8, color="grey")
        
        if self.afficher_valeurs == True :
            autolabel(barresRealise)
            autolabel(barresBudgete)

        # Recherche la largeur de texte max
        largeurMax = 0
        for label in listeLabels :
            if len(label) > largeurMax :
                largeurMax = len(label) 
        
        # Espaces autour du graph
        margeGauche = 0.1 + largeurMax * 0.008
        self.figure.subplots_adjust(left=margeGauche, right=None, wspace=None, hspace=None)

        # Légende
        props = matplotlib.font_manager.FontProperties(size=10)
        leg = ax.legend(loc='best', shadow=False, fancybox=True, prop=props)
        leg.get_frame().set_alpha(0.5)

        # Finalisation
        ax.autoscale_view('tight')
        ax.grid(True, linestyle=":")
        ax.figure.canvas.draw()
        wx.CallAfter(self.SendSizeEvent)
        return


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent 

        intro = _(u"Sélectionnez un modèle de graphique dans la liste proposée puis ajustez les paramètres si besoin.")
        titre = _(u"Graphiques")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Diagramme.png")

        # Modèle
        self.box_modele_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Modèle"))
        self.ctrl_modele = CTRL_Modele(self)
        self.ctrl_modele.SetMinSize((400, -1))
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Paramètres"))
        self.label_exercice = wx.StaticText(self, wx.ID_ANY, _(u"Exercice :"))
        self.ctrl_exercice = CTRL_Exercice(self)
        self.label_analytique = wx.StaticText(self, wx.ID_ANY, _(u"Analytique :"))
        self.ctrl_analytique = CTRL_Analytique(self)
        
        # Graphique
        self.box_graphique_staticbox = wx.StaticBox(self, wx.ID_ANY, "Graphique")
        self.ctrl_graphique = CTRL_Graphique(self)
        self.bouton_zoom = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_options = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_COMBOBOX, self.OnChoixModele, self.ctrl_modele)
        self.Bind(wx.EVT_CHOICE, self.OnChoixExercice, self.ctrl_exercice)
        self.Bind(wx.EVT_CHOICE, self.OnChoixAnalytique, self.ctrl_analytique)
        self.Bind(wx.EVT_BUTTON, self.ctrl_graphique.OnBoutonZoom, self.bouton_zoom)
        self.Bind(wx.EVT_BUTTON, self.ctrl_graphique.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_ok)
        
        # Init contrôles
        wx.CallLater(1, self.MAJgraphique)
        

    def __set_properties(self):
        self.ctrl_modele.SetToolTip(wx.ToolTip(_(u"Sélectionnez un modèle de graphique")))
        self.ctrl_exercice.SetToolTip(wx.ToolTip(_(u"Sélectionnez un exercice")))
        self.ctrl_analytique.SetToolTip(wx.ToolTip(_(u"Sélectionnez un poste analytique")))
        self.bouton_zoom.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux fonctions d'export et d'impression du graphique")))
        self.bouton_options.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux options du graphique")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((800, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)
        
        # Modèle
        box_modele = wx.StaticBoxSizer(self.box_modele_staticbox, wx.VERTICAL)
        box_modele.Add(self.ctrl_modele, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_modele, 1, wx.EXPAND, 0)
        
        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(2, 2, 5, 5)

        grid_sizer_parametres.Add(self.label_exercice, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_exercice, 0, wx.EXPAND, 0)
        grid_sizer_parametres.Add(self.label_analytique, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_analytique, 0, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableCol(1)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_haut.Add(box_parametres, 1, wx.EXPAND, 0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Graphique
        box_graphique = wx.StaticBoxSizer(self.box_graphique_staticbox, wx.VERTICAL)
        grid_sizer_graphique = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_graphique.Add(self.ctrl_graphique, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons_graphiques = wx.FlexGridSizer(3, 1, 5, 5)
        grid_sizer_boutons_graphiques.Add(self.bouton_zoom, 0, 0, 0)
        grid_sizer_boutons_graphiques.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_graphique.Add(grid_sizer_boutons_graphiques, 1, wx.EXPAND, 0)
        grid_sizer_graphique.AddGrowableRow(0)
        grid_sizer_graphique.AddGrowableCol(0)
        
        box_graphique.Add(grid_sizer_graphique, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_graphique, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 3, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnChoixModele(self, event):  
        self.MAJgraphique() 

    def OnChoixExercice(self, event): 
        self.MAJgraphique() 

    def OnChoixAnalytique(self, event): 
        self.MAJgraphique() 
    
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Graphiques")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def MAJgraphique(self, event=None):
        dictExercice = self.ctrl_exercice.GetDictExercice() 
        if dictExercice == None : return
        date_debut = dictExercice["date_debut"]
        date_fin = dictExercice["date_fin"]
        
        dictParametres = {
            "IDmodele" : self.ctrl_modele.GetID(),
            "nom" : self.ctrl_modele.GetLabel(),
            "date_debut" : date_debut,
            "date_fin" : date_fin,
            "IDanalytique" : self.ctrl_analytique.GetID(),
            }
        
        self.ctrl_graphique.SetParametres(dictParametres)
        self.ctrl_graphique.MAJ() 


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
