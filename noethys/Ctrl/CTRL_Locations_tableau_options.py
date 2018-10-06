#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import copy
import GestionDB
from Utils import UTILS_Texte
from Utils import UTILS_Config
from Utils import UTILS_Dates
from Utils import UTILS_Parametres
from Ctrl import CTRL_Selection_periode_simple
from Ctrl import CTRL_Saisie_heure
from Ctrl import CTRL_Propertygrid

import wx.propgrid as wxpg


class CTRL_Categories(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.SetMinSize((80, 80))
        self.MAJ()

    def MAJ(self):
        self.Importation()

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, nom
        FROM produits_categories
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictCategories = {}
        index = 0
        for IDcategorie, nom in listeDonnees:
            self.Append(nom)
            self.dictCategories[index] = IDcategorie
            self.Check(index)
            index += 1

    def GetIDcoches(self):
        listeIDcoches = []
        for index, IDcategorie in self.dictCategories.iteritems():
            if self.IsChecked(index):
                listeIDcoches.append(IDcategorie)
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        if type(listeIDcoches) == str :
            listeIDcoches = UTILS_Texte.ConvertStrToListe(listeIDcoches)
        for index, IDcategorie in self.dictCategories.iteritems():
            if IDcategorie in listeIDcoches:
                self.Check(index)



# -------------------------------------------------------------------------------------



class CTRL_Parametres(CTRL_Propertygrid.CTRL):
    def __init__(self, parent):
        self.parent = parent
        CTRL_Propertygrid.CTRL.__init__(self, parent)
        self.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)

    def Remplissage(self):
        # Heure min affichée
        propriete = wxpg.StringProperty(label=_(u"Heure minimale affichée"), name="heure_min", value="08:30")
        propriete.SetHelpString(_(u"Saisissez une heure"))
        propriete.SetEditor("EditeurHeure")
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Heure max affichée
        propriete = wxpg.StringProperty(label=_(u"Heure maximale affichée"), name="heure_max", value="22:30")
        propriete.SetHelpString(_(u"Saisissez une heure"))
        propriete.SetEditor("EditeurHeure")
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Intervalle souris
        propriete = wxpg.StringProperty(label=_(u"Pas de la souris"), name="temps_arrondi", value="00:30")
        propriete.SetHelpString(_(u"Saisissez un temps"))
        propriete.SetEditor("EditeurHeure")
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Durée minimale barre
        propriete = wxpg.StringProperty(label=_(u"Durée minimale location"), name="barre_duree_minimale", value="00:30")
        propriete.SetHelpString(_(u"Saisissez une durée"))
        propriete.SetEditor("EditeurHeure")
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Hauteur de ligne
        propriete = wxpg.IntProperty(label=_(u"Hauteur de ligne"), name="case_hauteur", value=50)
        propriete.SetHelpString(_(u"Saisissez une hauteur de ligne (50 par défaut)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("case_hauteur", "SpinCtrl")

        # Autoriser changement de ligne
        propriete = wxpg.BoolProperty(label=_(u"Autoriser le changement de ligne"), name="autoriser_changement_ligne", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez pouvoir changer de ligne"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

    def OnPropGridChange(self, event):
        self.AppliquerParametres()
        event.Skip()

    def AppliquerParametres(self):
        for code, valeur in self.GetParametres().iteritems():
            self.parent.ctrl_tableau.SetOption(code, valeur)
        self.parent.ctrl_tableau.MAJ(reinit_scroll_h=True, reinit_scroll_v=True)

    def Validation(self):
        """ Validation des données saisies """
        # Vérifie que les données obligatoires ont été saisies
        for nom, valeur in self.GetPropertyValues().iteritems():
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "obligatoire") == True:
                if valeur == "" or valeur == None:
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le paramètre '%s' !") % self.GetPropertyLabel(nom), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        self.Sauvegarde()

        return True

    def Importation(self):
        """ Importation des valeurs dans le contrôle """
        # Récupération des noms et valeurs par défaut du contrôle
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        # Recherche les paramètres mémorisés
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="dlg_locations_tableau", dictParametres=dictValeurs)
        # Envoie les paramètres dans le contrôle
        for nom, valeur in dictParametres.iteritems():
            if valeur not in ("", None):
                propriete = self.GetPropertyByName(nom)
                ancienneValeur = propriete.GetValue()
                propriete.SetValue(valeur)

    def Sauvegarde(self, forcer=False):
        """ Mémorisation des valeurs du contrôle """
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        UTILS_Parametres.ParametresCategorie(mode="set", categorie="dlg_locations_tableau", dictParametres=dictValeurs)

    def GetParametres(self):
        return copy.deepcopy(self.GetPropertyValues())



# ---------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, ctrl_tableau=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.ctrl_tableau = ctrl_tableau

        # Période
        self.staticBox_periode = wx.StaticBox(self, -1, _(u"Sélection de la période"))
        self.ctrl_periode = CTRL_Selection_periode_simple.CTRL(self, callback=self.OnChangePeriode)

        # Catégories de produits
        self.staticBox_categories = wx.StaticBox(self, -1, _(u"Catégories de produits"))
        self.ctrl_categories = CTRL_Categories(self)

        # Options
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_parametres = CTRL_Parametres(self)
        self.ctrl_parametres.SetMinSize((400, 80))
        self.bouton_reinitialisation = CTRL_Propertygrid.Bouton_reinitialisation(self, self.ctrl_parametres)
        self.bouton_sauvegarde = CTRL_Propertygrid.Bouton_sauvegarde(self, self.ctrl_parametres)

        # Binds
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheckCategories, self.ctrl_categories)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(1, 4, 10, 10)

        # Période
        staticBox_periode = wx.StaticBoxSizer(self.staticBox_periode, wx.HORIZONTAL)
        staticBox_periode.Add(self.ctrl_periode, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_base.Add(staticBox_periode, 1, wx.EXPAND, 0)

        # Catégories
        staticBox_categories = wx.StaticBoxSizer(self.staticBox_categories, wx.HORIZONTAL)
        staticBox_categories.Add(self.ctrl_categories, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_base.Add(staticBox_categories, 1, wx.EXPAND, 0)

        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_parametres.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_reinitialisation, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_sauvegarde, 0, 0, 0)

        grid_sizer_parametres.Add(grid_sizer_boutons, 0, 0, 0)
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(0)
        box_parametres.Add(grid_sizer_parametres, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_base.Add(box_parametres, 1, wx.EXPAND|wx.ALL, 0)

        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        self.Layout()

        # Configuration
        dict_parametres = UTILS_Config.GetParametre("dlg_locations_tableau", {})
        if dict_parametres.has_key("periode") :
            self.ctrl_periode.SetModePeriode(dict_parametres["periode"])
        if dict_parametres.has_key("case_largeur") :
            self.ctrl_tableau.slider_largeur.SetValue(dict_parametres["case_largeur"])
            self.ctrl_tableau.OnSliderLargeur()

    def AppliquerParametres(self):
        self.OnChangePeriode()
        self.ctrl_parametres.AppliquerParametres()

    def MemoriseConfig(self):
        dictParametres = {
            "periode" : self.ctrl_periode.GetModePeriode(),
            "case_largeur": self.ctrl_tableau.slider_largeur.GetValue(),
            }
        UTILS_Config.SetParametre("dlg_locations_tableau", dictParametres)

    def OnChangePeriode(self):
        self.ctrl_tableau.SetOption("date_debut", self.ctrl_periode.GetDateDebut())
        self.ctrl_tableau.SetOption("date_fin", self.ctrl_periode.GetDateFin())
        self.ctrl_tableau.MAJ(reinit_scroll_h=True)

    def OnCheckCategories(self, event):
        self.ctrl_tableau.SetOption("categories", self.ctrl_categories.GetIDcoches())
        self.ctrl_tableau.MAJ(reinit_scroll_v=True)

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        # Contrôles
        self.ctrl_options = CTRL(panel)

        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_options, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((1200, 500))
        self.Layout()
        self.CenterOnScreen()




if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
