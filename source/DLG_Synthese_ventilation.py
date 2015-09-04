#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import time
import sys
import wx.lib.hyperlink as hl

import GestionDB
import CTRL_Bandeau
import CTRL_Selection_depots
import CTRL_Selection_activites
import CTRL_Saisie_date
import CTRL_Synthese_ventilation

try: import psyco; psyco.full()
except: pass


def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


class Parametres(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))
        
        self.radio_depots = wx.RadioButton(self, -1, "")
        self.label_depots = wx.StaticText(self, -1, _(u"Affiche les dépôts sélectionnés :"))
        self.ctrl_depots = CTRL_Selection_depots.CTRL(self)
        self.ctrl_depots.MAJ() 
        
        self.radio_prestations = wx.RadioButton(self, -1, "")
        self.label_prestations = wx.StaticText(self, -1, _(u"Affiche les prestations ventilées sur la période :"))
        
        self.label_date_debut = wx.StaticText(self, -1, "Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        self.label_date_fin = wx.StaticText(self, -1, " au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        
        self.check_activites = wx.CheckBox(self, -1, _(u"Uniquement rattachées aux activités :"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        
        # Boutons Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")
        self.bouton_actualiser.SetMinSize((-1, 50)) 

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_depots)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_prestations)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckActiveActivites, self.check_activites)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        
        self.radio_depots.SetValue(True)
        self.ActiveControles() 

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de début"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez la date de fin"))
##        self.ctrl_date_debut.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
##        self.ctrl_date_debut.SetMinSize((70, 18))
##        self.ctrl_date_fin.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
##        self.ctrl_date_fin.SetMinSize((70, 18))
        self.radio_depots.SetToolTipString(_(u"Cliquez ici pour sélectionner des dépôts"))
        self.radio_prestations.SetToolTipString(_(u"Cliquez ici pour sélectionner une periode"))
        self.bouton_actualiser.SetToolTipString(_(u"Cliquez ici pour actualiser les résultats"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=7, cols=2, vgap=5, hgap=5)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_contenu.Add(self.radio_depots, 0, 0, 0)
        grid_sizer_contenu.Add(self.label_depots, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add((15, 10), 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_depots, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add((15, 5), 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add((15, 5), 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.radio_prestations, 0, 0, 0)
        grid_sizer_contenu.Add(self.label_prestations, 0, 0, 0)
        grid_sizer_contenu.Add((15, 10), 0, wx.EXPAND, 0)
        
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_periode, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.Add((15, 10), 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.check_activites, 0, wx.EXPAND|wx.TOP, 8)
        grid_sizer_contenu.Add((15, 10), 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_activites, 0, wx.EXPAND|wx.LEFT, 15)
        
        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_contenu.AddGrowableCol(1)
        staticbox.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_actualiser, 0, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

    def OnBoutonActualiser(self, event):
        """ Validation des données saisies """
        if self.radio_depots.GetValue() == True :
            # DEPOTS
            listeDepots = self.ctrl_depots.GetDepots() 
##            if len(listeDepots) == 0 :
##                dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun dépôt !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
##                dlg.ShowModal()
##                dlg.Destroy()
            
            self.parent.SetTypeDepots(listeDepots) 
            
        else:
            # PRESTATIONS D'UNE PERIODE
            date_debut = self.ctrl_date_debut.GetDate()
            if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
                dlg = wx.MessageDialog(self, _(u"La date de début de période ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_debut.SetFocus()
                return False

            date_fin = self.ctrl_date_fin.GetDate()
            if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
                dlg = wx.MessageDialog(self, _(u"La date de fin de période ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False
            
            if self.check_activites.GetValue() == True :
                listeActivites = self.GetActivites() 
                if len(listeActivites) == 0 :
                    dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
            else:
                listeActivites = []

            self.parent.SetTypePrestations(date_debut, date_fin, listeActivites)

    def OnRadio(self, event): 
        self.ActiveControles() 
        
    def ActiveControles(self):
        if self.radio_depots.GetValue() == True :
            self.ctrl_depots.Enable(True)
            self.ctrl_date_debut.Enable(False)
            self.ctrl_date_fin.Enable(False)
            self.label_date_debut.Enable(False)
            self.label_date_fin.Enable(False)
            self.check_activites.Enable(False)
        else:
            self.ctrl_depots.Enable(False)
            self.ctrl_date_debut.Enable(True)
            self.ctrl_date_fin.Enable(True)
            self.label_date_debut.Enable(True)
            self.label_date_fin.Enable(True)
            self.ctrl_date_debut.SetFocus() 
            self.check_activites.Enable(True)
        self.OnCheckActiveActivites(None)
    
    def OnCheckActiveActivites(self, event):
        if self.radio_prestations.GetValue() == True and self.check_activites.GetValue() == True :
            self.ctrl_activites.Enable(True)
        else:
            self.ctrl_activites.Enable(False)
        
    def OnCheckActivites(self):
        pass
    
    def GetActivites(self):
        return self.ctrl_activites.GetActivites() 

# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Ceci est un tableau d'analyse croisée Ventilation/Dépôts qui vous permet d'afficher deux types de données : 1) Les prestations, regroupées par période, que les règlements des dépôts sélectionnés ont servi à payer, et 2) les dépôts dont les règlements ont servi à payer les prestations d'une période donnée. Ces résultats vous permettront donc de mettre en corrélation les dépôts et les prestations à la fin d'un exercice comptable.")
        titre = _(u"Tableau d'analyse croisée ventilation/dépôts")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Diagramme.png")
        self.SetTitle(titre)
        
        # Panel Paramètres
        self.ctrl_parametres = Parametres(self)
        
        # CTRL Coefficients
        self.staticbox_stats_staticbox = wx.StaticBox(self, -1, _(u"Résultats"))
        self.ctrl_stats = CTRL_Synthese_ventilation.CTRL(self)
        
        # Commandes de liste
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))

        # Commandes de résultats
        self.label_mode_affichage = wx.StaticText(self, -1, _(u"Mode d'affichage :"))
        self.radio_mois = wx.RadioButton(self, -1, _(u"Mois"), style=wx.RB_GROUP)
        self.radio_annee = wx.RadioButton(self, -1, _(u"Année"))
        
        self.check_details = wx.CheckBox(self, -1, _(u"Afficher détails"))
        self.check_details.SetValue(True) 
        
        self.hyper_developper = self.Build_Hyperlink_developper()
        self.label_barre = wx.StaticText(self, -1, u"|")
        self.hyper_reduire = self.Build_Hyperlink_reduire()
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMois, self.radio_mois)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAnnee, self.radio_annee)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDetails, self.check_details)
        
        self.__set_properties()
        self.__do_layout()
                
        # Initialisation des contrôles
        self.MAJ() 

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour créer un aperçu avant impression des résultats (PDF)"))
        self.bouton_excel.SetToolTipString(_(u"Cliquez ici pour exporter les résultats au format MS Excel"))
        self.radio_mois.SetToolTipString(_(u"Cliquez ici pour afficher les résultats par mois"))
        self.radio_annee.SetToolTipString(_(u"Cliquez ici pour afficher les résultats par années"))
        self.check_details.SetToolTipString(_(u"Cliquez ici pour afficher les détails dans les résultats"))
        self.SetMinSize((980, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # STATS
        staticbox_stats= wx.StaticBoxSizer(self.staticbox_stats_staticbox, wx.VERTICAL)
        grid_sizer_contenu2 = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_contenu2.Add(self.ctrl_stats, 1, wx.EXPAND, 0)
        
        # Boutons de liste
        grid_sizer_commandes = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_excel, 0, wx.EXPAND, 0)
        grid_sizer_contenu2.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        # Commandes de liste
        grid_sizer_commandes2 = wx.FlexGridSizer(rows=1, cols=9, vgap=5, hgap=5)
        grid_sizer_commandes2.Add(self.label_mode_affichage, 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add(self.radio_mois, 0, wx.EXPAND, 0) 
        grid_sizer_commandes2.Add(self.radio_annee, 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add( (30, 5), 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add(self.check_details, 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add(self.hyper_developper, 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add(self.label_barre, 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add(self.hyper_reduire, 0, wx.EXPAND, 0)
        grid_sizer_commandes2.AddGrowableCol(5)
        grid_sizer_contenu2.Add(grid_sizer_commandes2, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu2.AddGrowableRow(0)
        grid_sizer_contenu2.AddGrowableCol(0)
        
        staticbox_stats.Add(grid_sizer_contenu2, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(staticbox_stats, 1, wx.RIGHT|wx.EXPAND, 5)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
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

    def Build_Hyperlink_developper(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, _(u"Tout développer"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_developper)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Tout développer")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_developper(self, event):
        self.ctrl_stats.DevelopperTout()

    def Build_Hyperlink_reduire(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, _(u"Tout réduire"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_reduire)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Tout réduire")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_reduire(self, event):
        self.ctrl_stats.ReduireTout()
    
    def OnRadioMois(self, event):
        self.ctrl_stats.SetModeAffichage("mois")
        self.MAJ() 
    
    def OnRadioAnnee(self, event):
        self.ctrl_stats.SetModeAffichage("annee")
        self.MAJ() 
    
    def OnCheckDetails(self, event):
        etat = self.check_details.GetValue()
        self.ctrl_stats.SetAffichageDetails(etat)
        self.MAJ() 
        self.hyper_developper.Enable(-etat)
        self.label_barre.Enable(-etat)
        self.hyper_reduire.Enable(-etat)
        
    def SetTypeDepots(self, listeDepots=[]):
        self.ctrl_stats.SetTypeDepots(listeDepots) 
        self.ctrl_stats.MAJ() 
        
    def SetTypePrestations(self, date_debut=None, date_fin=None, listeActivites=[]):
        self.ctrl_stats.SetTypePrestations(date_debut, date_fin, listeActivites)
        self.ctrl_stats.MAJ() 
    
    def MAJ(self):
        self.ctrl_stats.MAJ() 
        
    def OnBoutonImprimer(self, event):
        self.ctrl_stats.Imprimer() 

    def OnBoutonExcel(self, event):
        self.ctrl_stats.ExportExcel() 
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Tableaudanalysecroiseventilation")


        

# -------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
