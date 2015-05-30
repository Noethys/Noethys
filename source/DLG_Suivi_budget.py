#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import UTILS_Dates
import datetime

import OL_Suivi_budget
import CTRL_Bandeau
import CTRL_Saisie_date

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import copy
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
except Exception, err :
    print "Erreur d'import : ", Exception, err




class CTRL_Budget(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.defaut = None
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.SetSelection(0)
        if self.defaut != None :
            self.SetID(self.defaut)

    def GetListeDonnees(self):
        listeItems = []
        self.dictDonnees = {}
        DB = GestionDB.DB()
        req = """SELECT IDbudget, nom, observations, analytiques, date_debut, date_fin
        FROM compta_budgets
        ORDER BY date_debut; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dateJour = datetime.date.today() 
        index = 0
        for IDbudget, nom, observations, analytiques, date_debut, date_fin in listeDonnees :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            
            if date_debut <= dateJour and date_fin >= dateJour :
                self.defaut = IDbudget
            
            analytiques = analytiques.split(";")
            listeTemp = []
            if len(analytiques) > 0 :
                for IDanalytique in analytiques :
                    listeTemp.append(int(IDanalytique))
            analytiques = listeTemp
            
            dictTemp = {
                "IDbudget" : IDbudget, "nom" : nom, "observations" : observations, 
                "analytiques" : analytiques, "date_debut" : date_debut, "date_fin" : date_fin, 
                }
            self.dictDonnees[index] = dictTemp
            label = nom
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["IDbudget"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["IDbudget"]
    
    def GetDictBudget(self):
        index = self.GetSelection()
        if index == -1 : return None
        dictBudget = self.dictDonnees[index]
        return dictBudget
        
# ----------------------------------------------------------------------------------------------------------------------------

class Panel_Donnees(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        
##        self.listviewAvecFooter = OL_Suivi_budget.ListviewAvecFooter(self) 
##        self.ctrl = self.listviewAvecFooter.GetListview()
        self.ctrl = OL_Suivi_budget.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)

        self.ctrl.MAJ() 
        
        # Boutons
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Texte2.png", wx.BITMAP_TYPE_ANY))
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.ctrl.ExportTexte, self.bouton_texte)
        
        # Properties
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour afficher un aperçu avant impression des données"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer les données"))
        self.bouton_excel.SetToolTipString(_(u"Cliquez ici pour exporter au format Excel les données"))
        self.bouton_texte.SetToolTipString(_(u"Cliquez ici pour exporter au format texte les données"))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(1, 2, 5, 5)
        
##        grid_sizer_base.Add(self.listviewAvecFooter, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, 10)
        grid_sizer_base.Add(self.ctrl, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(5, 1, 5, 5)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, 10)

        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)

        self.SetSizer(grid_sizer_base)
        self.Layout()
    
    def SetDictBudget(self, dictBudget=None):
        self.ctrl.SetDictBudget(dictBudget)
        self.ctrl.MAJ() 

# ----------------------------------------------------------------------------------------------------------------------------

class Panel_Graphe(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        self.afficher_valeurs = False
        
        self.panel = wx.Panel(self, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        
        self.figure = matplotlib.pyplot.figure()
        self.canvas = Canvas(self.panel, -1, self.figure)
        self.canvas.SetMinSize((20, 20))
        self.SetColor( (255,255,255) )

        # Boutons
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_options = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.Options, self.bouton_options)

        # Properties
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour ouvrir le visualiseur de graphe pour accéder aux fonctions d'export et d'impression"))
        self.bouton_options.SetToolTipString(_(u"Cliquez ici pour accéder aux options du graphe"))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(1, 2, 5, 5)
        
        sizer_canvas = wx.BoxSizer(wx.VERTICAL)
        sizer_canvas.Add(self.canvas, 1, wx.EXPAND, 0)
        self.panel.SetSizer(sizer_canvas)

        grid_sizer_base.Add(self.panel, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, 10)

        grid_sizer_boutons = wx.FlexGridSizer(5, 1, 5, 5)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, 10)

        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)

        self.SetSizer(grid_sizer_base)
        self.Layout()

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
        
    def Apercu(self, event):
        import DLG_Zoom_graphe
        dlg = DLG_Zoom_graphe.Dialog(self, figure=self.figure)
        dlg.ShowModal() 
        dlg.Destroy()
    
    def Options(self, event):
        # Création du menu contextuel
        menuPop = wx.Menu()
        
        item = wx.MenuItem(menuPop, 10, _(u"Afficher les valeurs"), _(u"Afficher les valeurs"), wx.ITEM_CHECK)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.On_afficher_valeurs, id=10)
        if self.afficher_valeurs == True : item.Check(True)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def On_afficher_valeurs(self, event):
        self.afficher_valeurs = not self.afficher_valeurs
        self.MAJ() 
        
    def SetDictBudget(self, dictBudget=None):
        self.dictBudget = dictBudget
        self.MAJ() 

    def MAJ(self) :
        self.figure.clear()
        if self.dictBudget == None :
            wx.CallAfter(self.SendSizeEvent)
            return
        
        # Récupération des données
        import OL_Suivi_budget
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
##        ax.grid(True)
        ax.figure.canvas.draw()
        wx.CallAfter(self.SendSizeEvent)
        return

# ----------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent 

        intro = _(u"Sélectionnez un budget dans la liste déroulante pour afficher les données correspondantes.")
        titre = _(u"Suivi du budget")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Tresorerie.png")

        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Paramètres"))
        self.label_budget = wx.StaticText(self, wx.ID_ANY, _(u"Budget :"))
        self.ctrl_budget = CTRL_Budget(self)
        self.bouton_budget = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        self.check_periode = wx.CheckBox(self, -1, _(u"Période personnalisée :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, wx.ID_ANY, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.bouton_valider_periode = wx.Button(self, -1, _(u"Valider")) 
        
        self.check_inclure = wx.CheckBox(self, -1, _(u"Inclure les catégories non budgétées"))
        
        # Situation
        self.box_situation_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Situation"))
        self.notebook = wx.Notebook(self, -1, style=wx.BK_BOTTOM)
        
        self.ctrl_donnees = Panel_Donnees(self.notebook)
        self.notebook.AddPage(self.ctrl_donnees, _(u"Données"))

        self.ctrl_graphe = Panel_Graphe(self.notebook)
        self.notebook.AddPage(self.ctrl_graphe, _(u"Graphique"))

        # Images des pages
        il = wx.ImageList(16, 16)
        self.image_donnees = il.Add(wx.Bitmap("Images/16x16/Tableau.png", wx.BITMAP_TYPE_PNG))
        self.image_graphique = il.Add(wx.Bitmap("Images/16x16/Barres.png", wx.BITMAP_TYPE_PNG))
        self.notebook.AssignImageList(il)
        
        self.notebook.SetPageImage(0, self.image_donnees)
        self.notebook.SetPageImage(1, self.image_graphique)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHOICE, self.OnChoixBudget, self.ctrl_budget)
        self.Bind(wx.EVT_CHECKBOX, self.OnChoixBudget, self.check_inclure)
        self.Bind(wx.EVT_CHECKBOX, self.OnChoixBudget, self.check_periode)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonBudget, self.bouton_budget)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_BUTTON, self.OnChoixBudget, self.bouton_valider_periode)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
        # Init
        self.OnChoixBudget(None) 
        

    def __set_properties(self):
        self.ctrl_budget.SetToolTipString(_(u"Sélectionnez une budget dans la liste"))
        self.check_periode.SetToolTipString(_(u"Cochez cette case pour saisir une autre date que celle définie dans le budget"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de début de période"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez la date de fin de période"))
        self.bouton_valider_periode.SetToolTipString(_(u"Cliquez ici pour valider les dates saisies"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((770, 680))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(3, 2, 10, 10)
                
        grid_sizer_generalites.Add(self.label_budget, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_budget = wx.FlexGridSizer(1, 5, 5, 5)
        grid_sizer_budget.Add(self.ctrl_budget, 0, wx.EXPAND, 0)
        grid_sizer_budget.Add(self.bouton_budget, 0, 0, 0)
        grid_sizer_budget.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_budget, 1, wx.EXPAND, 0)
        
        grid_sizer_generalites.Add( (5, 5), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_periode = wx.FlexGridSizer(1, 5, 5, 5)
        grid_sizer_periode.Add(self.check_periode, 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add(self.bouton_valider_periode, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_periode, 1, wx.EXPAND, 0)

        grid_sizer_generalites.Add( (50, 5), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.check_inclure, 1, wx.EXPAND, 0)

        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Situation
        box_situation = wx.StaticBoxSizer(self.box_situation_staticbox, wx.VERTICAL)
        box_situation.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_situation, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide(u"")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonBudget(self, event):  
        IDbudget = self.ctrl_budget.GetID()
        import DLG_Budgets
        dlg = DLG_Budgets.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_budget.MAJ()
        self.ctrl_budget.SetID(IDbudget)
        self.OnChoixBudget(None)
    
    def OnChoixBudget(self, event):
        # Activation de la période personnalisée
        self.ctrl_date_debut.Enable(self.check_periode.GetValue())
        self.label_au.Enable(self.check_periode.GetValue())
        self.ctrl_date_fin.Enable(self.check_periode.GetValue())
        self.bouton_valider_periode.Enable(self.check_periode.GetValue())
        # Récupération des données
        dictBudget = copy.copy(self.ctrl_budget.GetDictBudget())
        if dictBudget != None :
            dictBudget["inclure_toutes_categories"] = self.check_inclure.GetValue() 
            if self.check_periode.GetValue() == True :
                if self.ctrl_date_debut.GetDate() != None and self.ctrl_date_fin.GetDate() != None :
                    dictBudget["date_debut"] = self.ctrl_date_debut.GetDate()
                    dictBudget["date_fin"] = self.ctrl_date_fin.GetDate()
                else :
                    dictBudget = None
        # Envoi des données vers le ctrl de suivi
        page = self.notebook.GetPage(self.notebook.GetSelection())
        page.SetDictBudget(dictBudget)

    def OnPageChanged(self, event):
        """ Quand une page du notebook est sélectionnée """
        old = event.GetOldSelection()
        self.OnChoixBudget(None)
        event.Skip()
    
        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
