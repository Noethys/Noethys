#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-21 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Synthese_deductions
from Utils import UTILS_Questionnaires
from Utils import UTILS_Dates
from Ctrl import CTRL_Selection_activites



class CTRL_Choix_regroupement(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeDonnees = [
            {"label" : _(u"Jour"), "code" : "jour"},
            {"label" : _(u"Mois"), "code" : "mois"},
            {"label" : _(u"Année"), "code" : "annee"},
            {"label" : _(u"Ville de résidence"), "code" : "ville_residence"},
            {"label" : _(u"Secteur géographique"), "code" : "secteur"},
            {"label" : _(u"Famille"), "code" : "famille"},
            {"label" : _(u"Individu"), "code": "individu"},
            {"label" : _(u"Régime social"), "code" : "regime"},
            {"label" : _(u"Caisse d'allocations"), "code" : "caisse"},
            {"label" : _(u"Quotient familial"), "code" : "qf"},
            {"label" : _(u"Montant de la déduction"), "code": "montant_deduction"},
            {"label" : _(u"Label de la déduction"), "code": "nom_deduction"},
            {"label" : _(u"Label de l'aide"), "code": "nom_aide"},
            ]
        
        # Intégration des questionnaires
        q = UTILS_Questionnaires.Questionnaires() 
        for public in ("famille",) :
            for dictTemp in q.GetQuestions(public) :
                label = _(u"Question %s. : %s") % (public[:3], dictTemp["label"])
                code = "question_%s_%d" % (public, dictTemp["IDquestion"])
                self.listeDonnees.append({"label" : label, "code" : code})

        self.MAJ() 

    def MAJ(self):
        listeLabels = []
        for dictTemp in self.listeDonnees :
            listeLabels.append(dictTemp["label"])
        self.SetItems(listeLabels)
        self.Select(6)

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeDonnees[index]["code"]


# ----------------------------------------------------------------------------------------------------------------------------------


class CTRL_Choix_caisse(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        DB = GestionDB.DB()
        req = """SELECT IDcaisse, nom
        FROM caisses
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.listeDonnees = [{"label": _(u"Toutes les caisses"), "ID": None}]
        for IDcaisse, nom in listeDonnees:
            self.listeDonnees.append({"label": nom, "ID": IDcaisse})
        self.MAJ()

    def MAJ(self):
        listeLabels = []
        for dictTemp in self.listeDonnees:
            listeLabels.append(dictTemp["label"])
        self.SetItems(listeLabels)
        self.Select(0)

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeDonnees[index]["ID"]


# ----------------------------------------------------------------------------------------------------------------------------------



class Parametres(wx.Panel):
    def __init__(self, parent, listview=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.listview = listview

        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Période de référence"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.ctrl_date_debut.SetDate(datetime.date(datetime.date.today().year, 1, 1))
        self.ctrl_date_fin.SetDate(datetime.date(datetime.date.today().year, 12, 31))

        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        self.ctrl_activites.SetMinSize((-1, 90))

        # Affichage
        self.box_affichage_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_regroupement = wx.StaticText(self, -1, _(u"Regroup. :"))
        self.ctrl_regroupement = CTRL_Choix_regroupement(self)
        self.label_caisse = wx.StaticText(self, -1, _(u"Caisse :"))
        self.ctrl_caisse = CTRL_Choix_caisse(self)

        # Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.Actualiser, self.ctrl_caisse)
        self.Bind(wx.EVT_CHOICE, self.Actualiser, self.ctrl_regroupement) 
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)

        self.Actualiser()

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de période")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de période")))
        self.ctrl_regroupement.SetToolTip(wx.ToolTip(_(u"Sélectionnez le niveau de regroupement")))
        self.ctrl_caisse.SetToolTip(wx.ToolTip(_(u"Sélectionnez un filtre pour la caisse associée à l'aide")))
        self.bouton_actualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour actualiser la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)

        # Date de référence
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_periode, 1, wx.EXPAND, 0)

        # Activités
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        staticbox_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_activites, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # affichage
        box_affichage = wx.StaticBoxSizer(self.box_affichage_staticbox, wx.VERTICAL)
        grid_sizer_affichage = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.label_regroupement, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.ctrl_regroupement, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.label_caisse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.ctrl_caisse, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.AddGrowableCol(1)
        box_affichage.Add(grid_sizer_affichage, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_affichage, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.bouton_actualiser, 0, wx.EXPAND|wx.TOP, 5)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
    
    def OnChoixDate(self):
        self.Actualiser() 

    def OnBoutonActualiser(self, event): 
        # Vérifications
        if self.ctrl_date_debut.GetDate()  == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune date de début !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.ctrl_date_fin.GetDate()  == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune date de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # MAJ
        self.Actualiser()

    def OnCheckActivites(self):
        self.Actualiser()

    def Actualiser(self, event=None):
        """ MAJ du tableau """
        date_debut = self.ctrl_date_debut.GetDate() 
        date_fin = self.ctrl_date_fin.GetDate() 
        listeActivites = self.ctrl_activites.GetActivites()
        affichage_caisse = self.ctrl_caisse.GetValeur()
        affichage_regroupement = self.ctrl_regroupement.GetValeur()

        # Vérifications
        if date_debut == None :
            self.parent.ctrl_resultats.ResetGrid()
            return False

        if date_fin == None :
            self.parent.ctrl_resultats.ResetGrid()
            return False

        # Label Paramètres
        activites = ", ".join(self.ctrl_activites.GetLabelActivites())
        if activites == "":
            activites = _(u"Aucune")

        listeParametres = [ 
            _(u"Période du %s au %s") % (UTILS_Dates.DateEngFr(str(date_debut)), UTILS_Dates.DateEngFr(str(date_fin))),
            _(u"Activités : %s") % activites,
            ]
        labelParametres = " | ".join(listeParametres)
        
        # MAJ
        self.parent.ctrl_resultats.MAJ(date_debut=date_debut, date_fin=date_fin, listeActivites=listeActivites,
                                        affichage_regroupement=affichage_regroupement, affichage_caisse=affichage_caisse,
                                        labelParametres=labelParametres)



# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici éditer une synthèse des déductions pour une période donnée. Commencez par sélectionner une date de début et de fin et cliquer sur le bouton Actualiser. Vous pouvez affiner vos résultats et modifier l'affichage des données grâce aux options proposées.")
        titre = _(u"Synthèse des déductions")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Diagramme.png")
        
        # Liste
        self.staticbox_resultats_staticbox = wx.StaticBox(self, -1, _(u"Résultats"))
        self.ctrl_resultats = CTRL_Synthese_deductions.CTRL(self)
        self.ctrl_resultats.SetMinSize((50, 50)) 
        
        # Paramètres
        self.ctrl_parametres = Parametres(self, listview=self.ctrl_resultats)
        
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)


    def __set_properties(self):
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu de la liste (PDF)")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((980, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        box_resultats = wx.StaticBoxSizer(self.staticbox_resultats_staticbox, wx.HORIZONTAL)
        
        # Liste de resultats
        box_resultats.Add(self.ctrl_resultats, 1, wx.EXPAND|wx.ALL, 5)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_commandes.Add( (5, 5), 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_excel, 0, 0, 0)
        box_resultats.Add(grid_sizer_commandes, 0, wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 5)
        
        grid_sizer_droit.Add(box_resultats, 1, wx.EXPAND, 0)

        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)

        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
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

    def Apercu(self, event):
        self.ctrl_resultats.Apercu()

    def ExportTexte(self, event):
        self.ctrl_resultats.ExportTexte()

    def ExportExcel(self, event):
        self.ctrl_resultats.ExportExcel()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    dialog_1.ctrl_parametres.ctrl_date_debut.SetDate("2011-01-01")
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
