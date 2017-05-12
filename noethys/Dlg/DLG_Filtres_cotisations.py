#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import wx.html as html

import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros
from DLG_Factures_generation_parametres import CTRL_Lot_factures

from Utils import UTILS_Dates
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")



def GetTexteFiltres(filtres):
    """ Transforme la liste de filtres en texte pour le contrôle HTML """
    if filtres == None :
        filtres = []
    
    listeTextes = []
    for filtre in filtres :

        # Type de cotisation
         if filtre["type"] == "type" :
            DB = GestionDB.DB()
            req = """SELECT IDtype_cotisation, nom FROM types_cotisations WHERE IDtype_cotisation=%d;""" % filtre["IDtype_cotisation"]
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                listeTextes.append(_(u"Type de cotisation '%s'") % listeDonnees[0][1])

        # Unité de cotisation
         if filtre["type"] == "unite" :
            DB = GestionDB.DB()
            req = """SELECT IDunite_cotisation, nom FROM unites_cotisations WHERE IDunite_cotisation=%d;""" % filtre["IDunite_cotisation"]
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                listeTextes.append(_(u"Unité de cotisation '%s'") % listeDonnees[0][1])

##        # Date d'échéance
##         if filtre["type"] == "date_echeance" :
##            listeTextes.append(_(u"Date d'échéance de %s à %s") % (UTILS_Dates.DateEngFr(str(filtre["date_min"])), UTILS_Dates.DateEngFr(str(filtre["date_max"]))))

        # Numéros Intervalle
         if filtre["type"] == "numero_intervalle" :
            listeTextes.append(_(u"Numéros de cotisations de %d à %d") % (filtre["numero_min"], filtre["numero_max"]))

        # Numéros Liste
         if filtre["type"] == "numero_liste" :
            listeTextes.append(_(u"Numéros de cotisations suivants : %s") % ";".join([str(x) for x in filtre["liste"]]))

        # Montant
         if filtre["type"] == "montant" :
            operateur = filtre["operateur"]
            if operateur == u"<>" : operateur = u"&#60;&#62;"
            if operateur == u"<" : operateur = u"&#60;"
            if operateur == u">" : operateur = u"&#62;"
            listeTextes.append(_(u"Montant facturé %s %.2f %s") % (operateur, filtre["montant"], SYMBOLE))

        # Solde actuel
         if filtre["type"] == "solde_actuel" :
            operateur = filtre["operateur"]
            if operateur == u"<>" : operateur = u"&#60;&#62;"
            if operateur == u"<" : operateur = u"&#60;"
            if operateur == u">" : operateur = u"&#62;"
            listeTextes.append(_(u"Montant réglé %s %.2f %s") % (operateur, filtre["montant"], SYMBOLE))

        # Carte
         if filtre["type"] == "carte" :
            if filtre["choix"] == True :
                listeTextes.append(_(u"Cotisations pour lesquelles une carte a été créée"))
            else :
                listeTextes.append(_(u"Cotisations pour lesquelles aucune carte n'a été créée"))

        # Facturée
         if filtre["type"] == "facturee" :
            if filtre["choix"] == True :
                listeTextes.append(_(u"Cotisations facturées"))
            else :
                listeTextes.append(_(u"Cotisations non facturées"))

        # Dépôt
         if filtre["type"] == "depot" :
            DB = GestionDB.DB()
            req = """SELECT IDdepot_cotisation, nom FROM depots_cotisations WHERE IDdepot_cotisation=%d;""" % filtre["IDdepot_cotisation"]
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                listeTextes.append(_(u"Dépôt de cotisations '%s'") % listeDonnees[0][1])

    if len(listeTextes) > 0 :
        texte = u" | ".join(listeTextes) + u"."
    else :
        texte = _(u"Aucun.")
    return texte


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Types_cotisations(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self):
        DB = GestionDB.DB()
        req = """SELECT IDtype_cotisation, nom
        FROM types_cotisations
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeItems = [_(u"Aucun type de cotisation"),]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnu")}
        index = 1
        for IDtype_cotisation, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDtype_cotisation, "nom" : nom}
            listeItems.append(nom)
            index += 1
        self.SetItems(listeItems)
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetNom(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["nom"]

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Unites_cotisations(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self):
        DB = GestionDB.DB()
        req = """SELECT IDunite_cotisation, nom
        FROM unites_cotisations
        ORDER BY date_debut;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeItems = [_(u"Aucune unité de cotisation"),]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnu")}
        index = 1
        for ID, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : ID, "nom" : nom}
            listeItems.append(nom)
            index += 1
        self.SetItems(listeItems)
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetNom(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["nom"]

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Depots_cotisations(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self):
        DB = GestionDB.DB()
        req = """SELECT IDdepot_cotisation, nom
        FROM depots_cotisations
        ORDER BY date;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeItems = [_(u"Aucun dépôt de cotisations"),]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnu")}
        index = 1
        for ID, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : ID, "nom" : nom}
            listeItems.append(nom)
            index += 1
        self.SetItems(listeItems)
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetNom(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["nom"]

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------


class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25, couleurFond=(255, 255, 255)):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        self.couleurFond = couleurFond
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        self.SetTexte(texte)
    
    def SetTexte(self, texte=u""):
        self.SetPage(texte)
        self.SetBackgroundColour(self.couleurFond)
        

class CTRL_Filtres(wx.Panel):
    def __init__(self, parent, filtres=[], ctrl_cotisations=None):
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.filtres = filtres
        self.parent = parent
        self.ctrl_cotisations = ctrl_cotisations
        
        couleurFond=wx.Colour(255, 255, 255)
        self.SetBackgroundColour(couleurFond)
        
        self.ctrl_html = MyHtml(self, texte=_(u"Aucun filtre de sélection."), couleurFond=couleurFond, hauteur=25)
        self.bouton_parametres = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Filtre.png"), wx.BITMAP_TYPE_ANY))#wx.Bitmap("Images/32x32/Configuration2.png", wx.BITMAP_TYPE_ANY))
        self.bouton_parametres.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier les filtres de sélection des cotisations")))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonParametres, self.bouton_parametres)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.ctrl_html, 1, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, 5)
        sizer.Add(self.bouton_parametres, 0, wx.ALL, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
        # Init contrôles
        self.MAJ() 
    
##    def SetTexte(self, texte=u""):
##        self.ctrl_html.SetTexte(texte)
    
    def OnBoutonParametres(self, event):
        dlg = Dialog(self)
        dlg.SetFiltres(self.filtres)
        if dlg.ShowModal() == wx.ID_OK:
            self.filtres = dlg.GetFiltres()
            self.MAJ() 
        dlg.Destroy()
        
    def MAJ(self):
        # MAJ du HTML
        texte = _(u"<FONT SIZE=-1><B>Filtres de sélection :</B> %s</FONT>") % GetTexteFiltres(self.filtres)
        self.ctrl_html.SetTexte(texte)
        # MAJ du CTRL_Cotisations
        if self.ctrl_cotisations != None :
            self.ctrl_cotisations.SetFiltres(self.filtres)
            self.ctrl_cotisations.MAJ()


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Sélectionnez ici les filtres de sélection de votre choix à appliquer sur la liste des cotisations")
        titre = _(u"Filtres de sélection des cotisations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Filtre.png")
        
        # Filtres
        self.check_type = wx.CheckBox(self, -1, _(u"Type de cotisation :"))
        self.check_type.SetToolTip(wx.ToolTip(_(u"Filtre type de cotisation")))
        self.ctrl_type = CTRL_Types_cotisations(self)
        self.ctrl_type.SetToolTip(wx.ToolTip(_(u"Sélectionnez un type de cotisation dans la liste")))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_type)

        self.check_unite = wx.CheckBox(self, -1, _(u"Unité de cotisation :"))
        self.check_unite.SetToolTip(wx.ToolTip(_(u"Filtre unité de cotisation")))
        self.ctrl_unite = CTRL_Unites_cotisations(self)
        self.ctrl_unite.SetToolTip(wx.ToolTip(_(u"Sélectionnez une unité de cotisation dans la liste")))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_unite)
        
##        self.check_echeance = wx.CheckBox(self, -1, _(u"Date d'échéance de"))
##        self.ctrl_echeance_min = CTRL_Saisie_date.Date2(self)
##        self.label_echeance_a = wx.StaticText(self, -1, u"à")
##        self.ctrl_echeance_max = CTRL_Saisie_date.Date2(self)
        
        self.check_numeros_intervalle = wx.CheckBox(self, -1, _(u"Numéros de cotisations de"))
        self.check_numeros_intervalle.SetToolTip(wx.ToolTip(_(u"Filtre Intervalle de numéros de cotisation")))
        self.ctrl_numeros_intervalle_min = wx.SpinCtrl(self, -1, u"", min=0, max=1000000)
        self.ctrl_numeros_intervalle_min.SetMinSize((70, -1))
        self.label_numeros_intervalle_a = wx.StaticText(self, -1, u"à")
        self.ctrl_numeros_intervalle_max = wx.SpinCtrl(self, -1, u"", min=0, max=1000000)
        self.ctrl_numeros_intervalle_max.SetMinSize((70, -1))
        self.ctrl_numeros_intervalle_min.SetToolTip(wx.ToolTip(_(u"Saisissez un numéro de cotisation min")))
        self.ctrl_numeros_intervalle_max.SetToolTip(wx.ToolTip(_(u"Saisissez un numéro de cotisation max")))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_numeros_intervalle)
        
        self.check_numeros_liste = wx.CheckBox(self, -1, _(u"Numéros de cotisations suivants :"))
        self.check_numeros_liste.SetToolTip(wx.ToolTip(_(u"Filtre Liste de numéros de cotisations")))
        self.ctrl_numeros_liste = wx.TextCtrl(self, -1, u"")
        self.ctrl_numeros_liste.SetToolTip(wx.ToolTip(_(u"Saisissez les numéros de cotisations souhaités en les séparant par un point-virgule (;)")))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_numeros_liste)
        
        listeOperateurs = (u"=", u"<>", u">", u"<", u">=", u"<=")
        
        self.check_montant = wx.CheckBox(self, -1, _(u"Montant facturé"))
        self.check_montant.SetToolTip(wx.ToolTip(_(u"Filtre montant facturé")))
        self.ctrl_montant_operateur = wx.Choice(self, -1, choices=listeOperateurs)
        self.ctrl_montant_operateur.SetSelection(0)
        self.ctrl_montant_operateur.SetToolTip(wx.ToolTip(_(u"Sélectionnez un opérateur de comparaison")))
        self.ctrl_montant_montant = CTRL_Saisie_euros.CTRL(self)
        self.ctrl_montant_montant.SetToolTip(wx.ToolTip(_(u"Saisissez un montant")))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_montant)
        
        self.check_solde_actuel = wx.CheckBox(self, -1, _(u"Solde actuel"))
        self.check_solde_actuel.SetToolTip(wx.ToolTip(_(u"Filtre Solde actuel")))
        self.ctrl_solde_actuel_operateur = wx.Choice(self, -1, choices=listeOperateurs)
        self.ctrl_solde_actuel_operateur.SetSelection(0)
        self.ctrl_solde_actuel_operateur.SetToolTip(wx.ToolTip(_(u"Sélectionnez un opérateur de comparaison")))
        self.ctrl_solde_actuel_montant = CTRL_Saisie_euros.CTRL(self)
        self.ctrl_solde_actuel_montant.SetToolTip(wx.ToolTip(_(u"Saisissez un montant")))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_solde_actuel)
        
        self.check_carte = wx.CheckBox(self, -1, _(u"Carte créée"))
        self.check_carte.SetToolTip(wx.ToolTip(_(u"Filtre carte créée")))
        self.ctrl_carte = wx.Choice(self, -1, choices=["Oui", _(u"Non")])
        self.ctrl_carte.SetSelection(0)
        self.ctrl_carte.SetToolTip(wx.ToolTip(_(u"Oui/Non")))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_carte)
        
        self.check_facturee = wx.CheckBox(self, -1, _(u"Cotisation facturée"))
        self.check_facturee.SetToolTip(wx.ToolTip(_(u"Filtre cotisation facturée")))
        self.ctrl_facturee = wx.Choice(self, -1, choices=["Oui", _(u"Non")])
        self.ctrl_facturee.SetSelection(0)
        self.ctrl_facturee.SetToolTip(wx.ToolTip(_(u"Oui/Non")))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_facturee)
        
        self.check_depot = wx.CheckBox(self, -1, _(u"Dépôt de cotisations :"))
        self.check_depot.SetToolTip(wx.ToolTip(_(u"Filtre dépôt de cotisations")))
        self.ctrl_depot = CTRL_Depots_cotisations(self)
        self.ctrl_depot.SetToolTip(wx.ToolTip(_(u"Sélectionnez un dépôt de cotisations dans la liste")))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_depot)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        self.OnCheck(None)
        

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=20, hgap=20)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Filtres
        grid_sizer_contenu = wx.FlexGridSizer(rows=10, cols=1, vgap=10, hgap=10)
                
        grid_sizer_type = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_type.Add(self.check_type, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_type.Add(self.ctrl_type, 0, wx.EXPAND, 0)
        grid_sizer_type.AddGrowableCol(1)
        grid_sizer_contenu.Add(grid_sizer_type, 1, wx.EXPAND, 0)

        grid_sizer_unite = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_unite.Add(self.check_unite, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_unite.Add(self.ctrl_unite, 0, wx.EXPAND, 0)
        grid_sizer_unite.AddGrowableCol(1)
        grid_sizer_contenu.Add(grid_sizer_unite, 1, wx.EXPAND, 0)

##        grid_sizer_emission = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
##        grid_sizer_emission.Add(self.check_emission, 0, wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_emission.Add(self.ctrl_emission_min, 0, 0, 0)
##        grid_sizer_emission.Add(self.label_emission_a, 0, wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_emission.Add(self.ctrl_emission_max, 0, 0, 0)
##        grid_sizer_contenu.Add(grid_sizer_emission, 1, wx.EXPAND, 0)
                
        grid_sizer_numeros_intervalle = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_numeros_intervalle.Add(self.check_numeros_intervalle, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_numeros_intervalle.Add(self.ctrl_numeros_intervalle_min, 0, 0, 0)
        grid_sizer_numeros_intervalle.Add(self.label_numeros_intervalle_a, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_numeros_intervalle.Add(self.ctrl_numeros_intervalle_max, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_numeros_intervalle, 1, wx.EXPAND, 0)
        
        grid_sizer_numeros_liste = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_numeros_liste.Add(self.check_numeros_liste, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_numeros_liste.Add(self.ctrl_numeros_liste, 0, wx.EXPAND, 0)
        grid_sizer_numeros_liste.AddGrowableCol(1)
        grid_sizer_contenu.Add(grid_sizer_numeros_liste, 1, wx.EXPAND, 0)
        
        grid_sizer_montant = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_montant.Add(self.check_montant, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_montant.Add(self.ctrl_montant_operateur, 0, 0, 0)
        grid_sizer_montant.Add(self.ctrl_montant_montant, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_montant, 1, wx.EXPAND, 0)
        
        grid_sizer_solde_actuel = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_solde_actuel.Add(self.check_solde_actuel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_solde_actuel.Add(self.ctrl_solde_actuel_operateur, 0, 0, 0)
        grid_sizer_solde_actuel.Add(self.ctrl_solde_actuel_montant, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_solde_actuel, 1, wx.EXPAND, 0)
        
        grid_sizer_carte = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_carte.Add(self.check_carte, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_carte.Add(self.ctrl_carte, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_carte, 1, wx.EXPAND, 0)

        grid_sizer_facturee = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_facturee.Add(self.check_facturee, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_facturee.Add(self.ctrl_facturee, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_facturee, 1, wx.EXPAND, 0)

        grid_sizer_depot = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_depot.Add(self.check_depot, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_depot.Add(self.ctrl_depot, 0, wx.EXPAND, 0)
        grid_sizer_depot.AddGrowableCol(1)
        grid_sizer_contenu.Add(grid_sizer_depot, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Imprimer")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnCheck(self, event): 
        self.ctrl_type.Enable(self.check_type.GetValue())
        
        self.ctrl_unite.Enable(self.check_unite.GetValue())

##        self.ctrl_echeance_min.Enable(self.check_echeance.GetValue())
##        self.ctrl_echeance_max.Enable(self.check_echeance.GetValue())
        
        self.ctrl_numeros_intervalle_min.Enable(self.check_numeros_intervalle.GetValue())
        self.ctrl_numeros_intervalle_max.Enable(self.check_numeros_intervalle.GetValue())

        self.ctrl_numeros_liste.Enable(self.check_numeros_liste.GetValue())

        self.ctrl_montant_operateur.Enable(self.check_montant.GetValue())
        self.ctrl_montant_montant.Enable(self.check_montant.GetValue())

        self.ctrl_solde_actuel_operateur.Enable(self.check_solde_actuel.GetValue())
        self.ctrl_solde_actuel_montant.Enable(self.check_solde_actuel.GetValue())

        self.ctrl_carte.Enable(self.check_carte.GetValue())

        self.ctrl_facturee.Enable(self.check_facturee.GetValue())
        
        self.ctrl_depot.Enable(self.check_depot.GetValue())
    
    def GetFiltres(self):
        filtres = []
        
        # Types de cotisations
        if self.check_type.GetValue() == True :
            IDtype_cotisation = self.ctrl_type.GetID()
            if IDtype_cotisation == None :
                dlg = wx.MessageDialog(self, _(u"Filtre Type de cotisation : Vous n'avez sélectionné aucun type dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            filtres.append({"type" : "type", "IDtype_cotisation" : IDtype_cotisation})
        
        # Unités de cotisations
        if self.check_unite.GetValue() == True :
            IDunite_cotisation = self.ctrl_unite.GetID()
            if IDunite_cotisation == None :
                dlg = wx.MessageDialog(self, _(u"Filtre Unité de cotisation : Vous n'avez sélectionné aucune unité dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            filtres.append({"type" : "unite", "IDunite_cotisation" : IDunite_cotisation})
        
##        # Date d'échéance
##        if self.check_echeance.GetValue() == True :
##            date_min = self.ctrl_echeance_min.GetDate()
##            date_max = self.ctrl_echeance_max.GetDate()
##            if date_min == None or date_max == None :
##                dlg = wx.MessageDialog(self, _(u"Filtre Date d'échéance : Les dates saisies ne sont pas valides !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
##                dlg.ShowModal()
##                dlg.Destroy()
##                return False
##        
##            filtres.append({"type" : "date_echeance", "date_min" : date_min, "date_max" : date_max})

        # Numéros Intervalle
        if self.check_numeros_intervalle.GetValue() == True :
            numero_min = int(self.ctrl_numeros_intervalle_min.GetValue())
            numero_max = int(self.ctrl_numeros_intervalle_max.GetValue())
        
            filtres.append({"type" : "numero_intervalle", "numero_min" : numero_min, "numero_max" : numero_max})

        # Numéros Liste
        if self.check_numeros_liste.GetValue() == True :
            listeTemp = self.ctrl_numeros_liste.GetValue()
            if listeTemp == "" :
                dlg = wx.MessageDialog(self, _(u"Filtre Liste de numéros : Vous n'avez saisi aucun numéro de facture dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            try :
                listeNumeros = []
                for numero in listeTemp.split(";") :
                    listeNumeros.append(int(numero))
            except :
                dlg = wx.MessageDialog(self, _(u"Filtre Liste de numéros : Les numéros de factures saisis ne sont pas valides !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
            filtres.append({"type" : "numero_liste", "liste" : listeNumeros})

        # Montant
        if self.check_montant.GetValue() == True :
            operateur = self.ctrl_montant_operateur.GetStringSelection()
            montant = self.ctrl_montant_montant.GetMontant()
            if montant == None :
                dlg = wx.MessageDialog(self, _(u"Filtre Montant facturé : Le montant saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
            filtres.append({"type" : "montant", "operateur" : operateur, "montant" : montant})

        # Solde actuel
        if self.check_solde_actuel.GetValue() == True :
            operateur = self.ctrl_solde_actuel_operateur.GetStringSelection()
            montant = self.ctrl_solde_actuel_montant.GetMontant()
            if montant == None :
                dlg = wx.MessageDialog(self, _(u"Filtre Solde actuel : Le montant saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
            filtres.append({"type" : "solde_actuel", "operateur" : operateur, "montant" : montant})

        # Carte créée
        if self.check_carte.GetValue() == True :
            if self.ctrl_carte.GetSelection() == 0 :
                choix = True
            else :
                choix = False
                
            filtres.append({"type" : "carte", "choix" : choix})

        # Facturée
        if self.check_facturee.GetValue() == True :
            if self.ctrl_facturee.GetSelection() == 0 :
                choix = True
            else :
                choix = False
                
            filtres.append({"type" : "facturee", "choix" : choix})

        # Dépôt de cotisations
        if self.check_depot.GetValue() == True :
            IDdepot_cotisation = self.ctrl_depot.GetID()
            if IDdepot_cotisation == None :
                dlg = wx.MessageDialog(self, _(u"Filtre Dépôt de cotisations : Vous n'avez sélectionné aucun dépôt dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            filtres.append({"type" : "depot", "IDdepot_cotisation" : IDdepot_cotisation})

        return filtres
    
    def OnBoutonOk(self, event): 
        # Validation
        filtres = self.GetFiltres() 
        if filtres == False :
            return
    
        # Fermeture
        self.EndModal(wx.ID_OK)

    def SetFiltres(self, filtres=[]):
        if filtres == None :
            filtres = []
        
        for filtre in filtres :
            
            # Type de cotisation
            if filtre["type"] == "type" :
                self.check_type.SetValue(True)
                self.ctrl_type.SetID(filtre["IDtype_cotisation"])
    
            # Unité de cotisation
            if filtre["type"] == "unite" :
                self.check_unite.SetValue(True)
                self.ctrl_unite.SetID(filtre["IDunite_cotisation"])
    
##            # Date d'échéance
##            if filtre["type"] == "date_echeance" :
##                self.check_echeance.SetValue(True)
##                self.ctrl_echeance_min.SetDate(filtre["date_min"])
##                self.ctrl_echeance_max.SetDate(filtre["date_max"])

            # numero_intervalle
            if filtre["type"] == "numero_intervalle" :
                self.check_numeros_intervalle.SetValue(True)
                self.ctrl_numeros_intervalle_min.SetValue(filtre["numero_min"])
                self.ctrl_numeros_intervalle_max.SetValue(filtre["numero_max"])

            # numero_liste
            if filtre["type"] == "numero_liste" :
                self.check_numeros_liste.SetValue(True)
                self.ctrl_numeros_liste.SetValue(";".join([str(x) for x in filtre["liste"]]))

            # Montant
            if filtre["type"] == "montant" :
                self.check_montant.SetValue(True)
                self.ctrl_montant_operateur.SetStringSelection(filtre["operateur"])
                self.ctrl_montant_montant.SetMontant(filtre["montant"])

            # Solde actuel
            if filtre["type"] == "solde_actuel" :
                self.check_solde_actuel.SetValue(True)
                self.ctrl_solde_actuel_operateur.SetStringSelection(filtre["operateur"])
                self.ctrl_solde_actuel_montant.SetMontant(filtre["montant"])
                            
            # Carte
            if filtre["type"] == "carte" :
                self.check_carte.SetValue(True)
                self.ctrl_carte.SetSelection(not int(filtre["choix"]))
            
            # Facturée
            if filtre["type"] == "facturee" :
                self.check_facturee.SetValue(True)
                self.ctrl_facturee.SetSelection(not int(filtre["choix"]))

            # Dépôt de cotisations
            if filtre["type"] == "depot" :
                self.check_depot.SetValue(True)
                self.ctrl_depot.SetID(filtre["IDdepot_cotisation"])

        self.OnCheck(None)
        
    


# -------------------- POUR TESTER CTRL_Filtres -----------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL_Filtres(panel)
        self.boutonTest = wx.Button(panel, -1, _(u"Bouton de test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        pass

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

# -------------------- POUR TESTER DIALOG -----------------------------------------------------------------------------------
        
##if __name__ == u"__main__":
##    app = wx.App(0)
##    #wx.InitAllImageHandlers()
##    dlg = Dialog(None)
##    
##    # Test d'importation de filtres
##    dlg.SetFiltres([
##        {"type" : "numero_intervalle", "numero_min" : 210, "numero_max" : 215},
##        {"type" : "montant", "operateur" : ">=", "montant" : 2.15},
##        ])
##    
##    app.SetTopWindow(dlg)
##    dlg.ShowModal()
##    app.MainLoop()
