#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import datetime
from Utils import UTILS_Dates
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Editeur_email
from Ctrl.CTRL_Portail_pages import CTRL_Couleur
from Ol import OL_Portail_bloc_onglets
from Ol import OL_Portail_bloc_blog
from Ol import OL_Portail_bloc_calendrier
from Ol import OL_Portail_bloc_trombi

import wx.lib.agw.labelbook as LB



class CTRL_Page(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.MAJ()
        self.Select(0)

    def MAJ(self):
        DB = GestionDB.DB()
        req = """SELECT IDpage, titre
        FROM portail_pages
        ORDER BY ordre;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDpage, titre in listeDonnees:
            self.dictDonnees[index] = {"ID": IDpage, "titre": titre}
            listeItems.append(titre)
            index += 1
        self.SetItems(listeItems)

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID:
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]



# -----------------------------------------------------------------------------------

class PAGE_Texte(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDelement = None

        # Contrôles
        self.ctrl_editeur = CTRL_Editeur_email.CTRL(self)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_editeur, 0, wx.EXPAND | wx.LEFT, 10)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()

    def GetParametres(self):
        dictElement = {
            "IDelement" : self.IDelement,
            "titre" : "",
            "date_debut" : None,
            "date_fin" : None,
            "texte_xml" : self.ctrl_editeur.GetXML(),
            "texte_html" : self.ctrl_editeur.GetHTML_base64(),
        }
        return {"elements" : [dictElement,]}

    def SetParametres(self, dictParametres={}):
        if len(dictParametres["elements"]) > 0 :
            dictElement = dictParametres["elements"][0]
            self.IDelement = dictElement["IDelement"]
            self.ctrl_editeur.SetXML(dictElement["texte_xml"])

    def Validation(self):
        if len(self.ctrl_editeur.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_editeur.SetFocus()
            return False
        return True



# ----------------------------------------------------------------------------------------------------------

class PAGE_Onglets(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_elements = OL_Portail_bloc_onglets.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_elements.SetMinSize((150, 100))
        self.ctrl_elements.MAJ()

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Monter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Descendre, self.bouton_descendre)

        # Propriétés
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un onglet")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'onglet sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'onglet sélectionné dans la liste")))
        self.bouton_monter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour monter l'onglet sélectionné dans la liste")))
        self.bouton_descendre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour descendre l'onglet sélectionné dans la liste")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.ctrl_elements, 1, wx.EXPAND, 0)

        grid_sizer_droit = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.LEFT, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def GetParametres(self):
        return {"elements" : self.ctrl_elements.GetDonnees()}

    def SetParametres(self, dictParametres={}):
        self.ctrl_elements.SetDonnees(dictParametres["elements"])

    def Validation(self):
        if len(self.GetParametres()["elements"]) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez créer au moins un onglet pour ce modèle !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True





# ----------------------------------------------------------------------------------------------------------

class PAGE_Blog(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_elements = OL_Portail_bloc_blog.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_elements.SetMinSize((150, 100))
        self.ctrl_elements.MAJ()

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Supprimer, self.bouton_supprimer)

        # Propriétés
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un article")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'article sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'article sélectionné dans la liste")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.ctrl_elements, 1, wx.EXPAND, 0)

        grid_sizer_droit = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.LEFT, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def GetParametres(self):
        return {"elements" : self.ctrl_elements.GetDonnees()}

    def SetParametres(self, dictParametres={}):
        self.ctrl_elements.SetDonnees(dictParametres["elements"])

    def Validation(self):
        return True


# ----------------------------------------------------------------------------------------------------------


class PAGE_Calendrier(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_elements = OL_Portail_bloc_calendrier.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_elements.SetMinSize((150, 100))
        self.ctrl_elements.MAJ()

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Supprimer, self.bouton_supprimer)

        # Propriétés
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un évènement")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'évènement sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'évènement sélectionné dans la liste")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.ctrl_elements, 1, wx.EXPAND, 0)

        grid_sizer_droit = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.LEFT, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def GetParametres(self):
        return {"elements" : self.ctrl_elements.GetDonnees()}

    def SetParametres(self, dictParametres={}):
        self.ctrl_elements.SetDonnees(dictParametres["elements"])

    def Validation(self):
        return True


# ----------------------------------------------------------------------------------------------------------



class PAGE_Trombi(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_elements = OL_Portail_bloc_trombi.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_elements.SetMinSize((150, 100))
        self.ctrl_elements.MAJ()

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Monter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_elements.Descendre, self.bouton_descendre)

        # Propriétés
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un individu")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'individu sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'individu sélectionné dans la liste")))
        self.bouton_monter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour monter l'individu sélectionné dans la liste")))
        self.bouton_descendre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour descendre l'individu sélectionné dans la liste")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.ctrl_elements, 1, wx.EXPAND, 0)

        grid_sizer_droit = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.LEFT, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def GetParametres(self):
        return {"elements" : self.ctrl_elements.GetDonnees()}

    def SetParametres(self, dictParametres={}):
        self.ctrl_elements.SetDonnees(dictParametres["elements"])

    def Validation(self):
        if len(self.GetParametres()["elements"]) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez créer au moins un individu pour ce trombinoscope !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True


# -------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(LB.FlatImageBook):
    def __init__(self, parent):
        LB.FlatImageBook.__init__(self, parent, id=-1, agwStyle=LB.INB_BORDER | LB.INB_LEFT)
        self.parent = parent

        self.listePages = [
            (_("bloc_texte"), _(u"Texte"), PAGE_Texte(self), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Texte_bloc.png'), wx.BITMAP_TYPE_PNG)),
            (_("bloc_onglets"), _(u"Onglets"), PAGE_Onglets(self), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Onglets.png'), wx.BITMAP_TYPE_PNG)),
            (_("bloc_blog"), _(u"Blog"), PAGE_Blog(self), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Blog.png'), wx.BITMAP_TYPE_PNG)),
            (_("bloc_calendrier"), _(u"Calendrier"), PAGE_Calendrier(self), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Calendrier.png'), wx.BITMAP_TYPE_PNG)),
            (_("bloc_trombi"), _(u"Portraits"), PAGE_Trombi(self), wx.Bitmap(Chemins.GetStaticPath('Images/32x32/Trombi.png'), wx.BITMAP_TYPE_PNG)),
        ]

        # Images
        il = wx.ImageList(32, 32)
        index = 0
        for code, label, ctrl, image in self.listePages:
            il.Add(image)
            index += 1
        self.AssignImageList(il)

        # Création des pages
        index = 0
        for code, label, ctrl, image in self.listePages:
            self.AddPage(ctrl, label, imageId=index)
            index += 1

        # Sélection par défaut
        self.SetSelection(0)

    def GetPageByCode(self, code=""):
        index = 0
        for codetemp, label, ctrl, image in self.listePages:
            if code == codetemp:
                return ctrl
            index += 1
        return None

    def SetPageByCode(self, code=""):
        index = 0
        for codetemp, label, ctrl, image in self.listePages:
            if code == codetemp:
                self.SetSelection(index)
            index += 1

    def GetPageActive(self):
        return self.listePages[self.GetSelection()][2]

    def GetCodePageActive(self):
        return self.listePages[self.GetSelection()][0]

    def Validation(self):
        return self.GetPageActive().Validation()

    def GetParametres(self):
        dictParametres = self.GetPageActive().GetParametres()
        dictParametres["categorie"] = self.GetCodePageActive()
        return dictParametres

    def SetParametres(self, dictParametres={}):
        self.SetPageByCode(dictParametres["categorie"])
        self.GetPageActive().SetParametres(dictParametres)



# -----------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDbloc=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDbloc = IDbloc
        self.IDpage_initial = None
        self.listeIDelementsImportes = []

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))

        self.label_titre = wx.StaticText(self, -1, _(u"Titre :"))
        self.ctrl_titre = wx.TextCtrl(self, -1, "")

        self.label_page = wx.StaticText(self, -1, _(u"Page :"))
        self.ctrl_page = CTRL_Page(self)

        self.label_couleur = wx.StaticText(self, -1, _(u"Couleur :"))
        self.ctrl_couleur = CTRL_Couleur(self)

        # Paramètres
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.ctrl_parametres = CTRL_Parametres(self)
        self.ctrl_parametres.SetMinSize((550, 350))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Init
        if self.IDbloc == None :
            self.SetTitle(_(u"Saisie d'un bloc"))
        else :
            self.SetTitle(_(u"Modification d'un bloc"))
            self.Importation()
        self.ctrl_titre.SetFocus()

    def __set_properties(self):
        self.ctrl_titre.SetToolTip(wx.ToolTip(_(u"Saisissez ici le titre du bloc")))
        self.ctrl_page.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici la page dans laquelle vous souhaitez insérer ce bloc")))
        self.ctrl_couleur.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici la couleur du bloc")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)

        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_generalites.Add(self.label_titre, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_titre, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_page, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_page = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_page.Add(self.ctrl_page, 0, wx.EXPAND, 0)
        grid_sizer_page.Add( (5, 5), 0, 0, 0)
        grid_sizer_page.Add(self.label_couleur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_page.Add(self.ctrl_couleur, 0, 0, 0)
        grid_sizer_page.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_page, 0, wx.EXPAND, 0)

        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Paramètres
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        staticbox_parametres.Add(self.ctrl_parametres, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(staticbox_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def Importation(self):
        """ Importation des données """
        dictParametres = {}

        DB = GestionDB.DB()

        # Bloc
        req = """SELECT IDpage, titre, couleur, categorie, ordre, parametres
        FROM portail_blocs WHERE IDbloc=%d;""" % self.IDbloc
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0:
            IDpage, titre, couleur, categorie, ordre, parametres = listeDonnees[0]
            self.ctrl_titre.SetValue(titre)
            self.ctrl_couleur.SetID(couleur)
            self.ctrl_page.SetID(IDpage)
            self.IDpage_initial = IDpage
            dictParametres["categorie"] = categorie
            dictParametres["parametres"] = parametres

        # Eléments
        req = """SELECT IDelement, ordre, titre, categorie, date_debut, date_fin, parametres, texte_xml, texte_html
        FROM portail_elements
        WHERE IDbloc=%d
        ORDER BY ordre;""" % self.IDbloc
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeElements = []
        if len(listeDonnees) > 0:
            for IDelement, ordre, titre, categorie, date_debut, date_fin, parametres, texte_xml, texte_html in listeDonnees :
                dictElement = {"IDelement": IDelement, "ordre": ordre, "titre": titre, "categorie" : categorie, "date_debut": date_debut, "date_fin": date_fin, "parametres": parametres, "texte_xml": texte_xml, "texte_html" : texte_html}
                listeElements.append(dictElement)
                self.listeIDelementsImportes.append(IDelement)
        dictParametres["elements"] = listeElements

        # Envoie des paramètres
        self.ctrl_parametres.SetParametres(dictParametres)
        DB.Close()

    def GetParametre(self, dictTemp={}, code=""):
        if dictTemp.has_key(code):
            return dictTemp[code]
        else:
            return None

    def OnBoutonOk(self, event):
        titre = self.ctrl_titre.GetValue()
        if titre == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un titre pour ce bloc !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_titre.SetFocus()
            return False

        # Validation des paramètres
        if self.ctrl_parametres.Validation() == False :
            return False

        # Récupération des données
        IDpage = self.ctrl_page.GetID()
        couleur = self.ctrl_couleur.GetID()
        dictParametres = self.ctrl_parametres.GetParametres()

        # Sauvegarde
        DB = GestionDB.DB()

        # Sauvegarde du modèle
        listeDonnees = [
            ("IDpage", IDpage),
            ("titre", titre),
            ("couleur", couleur),
            ("categorie", dictParametres["categorie"]),
            ]

        # Recherche l'ordre du bloc
        if self.IDpage_initial == None or self.IDpage_initial != IDpage :
            req = """SELECT MAX(ordre) FROM portail_blocs WHERE IDpage=%d;""" % IDpage
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            if len(listeTemp) == 0 or listeTemp[0][0] == None :
                ordre = 1
            else :
                ordre = listeTemp[0][0] + 1
            listeDonnees.append(("ordre", ordre))

        if self.IDbloc == None :
            self.IDbloc = DB.ReqInsert("portail_blocs", listeDonnees)
        else:
            DB.ReqMAJ("portail_blocs", listeDonnees, "IDbloc", self.IDbloc)

        # Sauvegarde des éléments
        index = 1
        listeIDelement = []
        for dictElement in dictParametres["elements"] :
            IDelement = dictElement["IDelement"]
            listeDonnees = [
                ("IDbloc", self.IDbloc),
                ("ordre", index),
                ("titre", self.GetParametre(dictElement, "titre")),
                ("categorie", dictParametres["categorie"]),
                ("date_debut", self.GetParametre(dictElement, "date_debut")),
                ("date_fin", self.GetParametre(dictElement, "date_fin")),
                ("parametres", self.GetParametre(dictElement, "parametres")),
                ("texte_xml", self.GetParametre(dictElement, "texte_xml")),
                ("texte_html", self.GetParametre(dictElement, "texte_html")),
                ]
            if IDelement == None or IDelement < 0 :
                newIDelement = DB.ReqInsert("portail_elements", listeDonnees)
                dictElement["IDelement"] = newIDelement
            else:
                DB.ReqMAJ("portail_elements", listeDonnees, "IDelement", IDelement)
                listeIDelement.append(IDelement)
            index += 1

        # Suppression des colonnes obsolètes
        for IDelement in self.listeIDelementsImportes :
            if IDelement not in listeIDelement :
                DB.ReqDEL("portail_elements", "IDelement", IDelement)

        # Clôture de la base
        DB.Close()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetID(self):
        return self.IDbloc




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
