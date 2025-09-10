#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import wx.html as html

import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros
from Dlg.DLG_Rappels_generation_parametres import CTRL_Lot_rappels

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text



# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

def GetTexteFiltres(filtres):
    """ Transforme la liste de filtres en texte pour le contrôle HTML """
    if filtres == None :
        filtres = []
    
    listeTextes = []
    for filtre in filtres :

        # Lots de lettres
         if filtre["type"] == "lot" :
            DB = GestionDB.DB()
            req = """SELECT IDlot, nom FROM lots_rappels WHERE IDlot=%d;""" % filtre["IDlot"]
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                listeTextes.append(_(u"Lot de lettres '%s'") % listeDonnees[0][1])
        
        # Date d'émission
         if filtre["type"] == "date_emission" :
            listeTextes.append(_(u"Date d'émission de %s à %s") % (DateEngFr(str(filtre["date_min"])), DateEngFr(str(filtre["date_max"]))))

        # Date de référence
         if filtre["type"] == "date_reference" :
            listeTextes.append(_(u"Date de référence de %s à %s") % (DateEngFr(str(filtre["date_min"])), DateEngFr(str(filtre["date_max"]))))

        # Numéros Intervalle
         if filtre["type"] == "numero_intervalle" :
            listeTextes.append(_(u"Numéros de lettres de %s à %s") % (filtre["numero_min"], filtre["numero_max"]))

        # Numéros Liste
         if filtre["type"] == "numero_liste" :
            listeTextes.append(_(u"Numéros de lettres suivants : %s") % ";".join(filtre["listeNumeros"]))

        # Solde
         if filtre["type"] == "solde" :
            operateur = filtre["operateur"]
            if operateur == u"<>" : operateur = u"&#60;&#62;"
            if operateur == u"<" : operateur = u"&#60"
            if operateur == u">" : operateur = u"&#62;"
            listeTextes.append(_(u"Solde %s %.2f %s") % (operateur, filtre["montant"], SYMBOLE))

        # Email
         if filtre["type"] == "email" :
            if filtre["choix"] == True :
                listeTextes.append(_(u"Lettres nécessitant un envoi par Email"))
            else :
                listeTextes.append(_(u"Lettres ne nécessitant pas un envoi par Email"))
    
    if len(listeTextes) > 0 :
        texte = u" | ".join(listeTextes) + u"."
    else :
        texte = _(u"Aucun.")
    return texte


# -------------------------------------------------------------------------------------------------------------------------------

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
    def __init__(self, parent, filtres=[], ctrl_rappels=None):
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)
        self.filtres = filtres
        self.parent = parent
        self.ctrl_rappels = ctrl_rappels
        
        couleurFond=wx.Colour(255, 255, 255)
        self.SetBackgroundColour(couleurFond)
        
        self.ctrl_html = MyHtml(self, texte=_(u"Aucun filtre de sélection."), couleurFond=couleurFond, hauteur=25)
        self.bouton_parametres = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))#wx.Bitmap("Images/32x32/Configuration2.png", wx.BITMAP_TYPE_ANY))
        self.bouton_parametres.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier les filtres de sélection des lettres de rappel")))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonParametres, self.bouton_parametres)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.ctrl_html, 1, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, 5)
        sizer.Add(self.bouton_parametres, 0, wx.ALL, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
        # Init contrôles
        self.MAJ() 
    
    def SetTexte(self, texte=u""):
        self.ctrl_html.SetTexte(texte)
    
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
        self.SetTexte(texte) 
        # MAJ du ctrl_rappels
        if self.ctrl_rappels != None :
            self.ctrl_rappels.SetFiltres(self.filtres)
            self.ctrl_rappels.MAJ()


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Sélectionnez ici les filtres de sélection de votre choix à appliquer sur la liste des lettres de rappel.")
        titre = _(u"Filtres de sélection des lettres de rappel")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Filtre.png")
        
        # Filtres
        self.check_lot = wx.CheckBox(self, -1, _(u"Lot de rappels :"))
        self.ctrl_lot = CTRL_Lot_rappels(self)
        
        self.check_emission = wx.CheckBox(self, -1, _(u"Date d'émission de"))
        self.ctrl_emission_min = CTRL_Saisie_date.Date2(self)
        self.label_emission_a = wx.StaticText(self, -1, u"à")
        self.ctrl_emission_max = CTRL_Saisie_date.Date2(self)
        
        self.check_reference = wx.CheckBox(self, -1, _(u"Date de référence de"))
        self.ctrl_reference_min = CTRL_Saisie_date.Date2(self)
        self.label_reference_a = wx.StaticText(self, -1, u"à")
        self.ctrl_reference_max = CTRL_Saisie_date.Date2(self)
        
        self.check_numeros_intervalle = wx.CheckBox(self, -1, _(u"Numéros de lettres de"))
        self.ctrl_numeros_intervalle_min = wx.SpinCtrl(self, -1, u"", min=0, max=1000000)
        self.ctrl_numeros_intervalle_min.SetMinSize((70, -1))
        self.label_numeros_intervalle_a = wx.StaticText(self, -1, u"à")
        self.ctrl_numeros_intervalle_max = wx.SpinCtrl(self, -1, u"", min=0, max=1000000)
        self.ctrl_numeros_intervalle_max.SetMinSize((70, -1))

        self.check_numeros_liste = wx.CheckBox(self, -1, _(u"Numéros de lettres suivants :"))
        self.ctrl_numeros_liste = wx.TextCtrl(self, -1, u"")
        
        listeOperateurs = (u"=", u"<>", u">", u"<", u">=", u"<=")
        
        self.check_solde = wx.CheckBox(self, -1, _(u"Solde"))
        self.ctrl_solde_operateur = wx.Choice(self, -1, choices=listeOperateurs)
        self.ctrl_solde_operateur.SetSelection(0)
        self.ctrl_solde_montant = CTRL_Saisie_euros.CTRL(self)

        self.check_email = wx.CheckBox(self, -1, _(u"Envoi par Email demandé"))
        self.ctrl_email = wx.Choice(self, -1, choices=["Oui", _(u"Non")])
        self.ctrl_email.SetSelection(0)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_lot)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_emission)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_reference)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_numeros_intervalle)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_numeros_liste)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_solde)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        self.OnCheck(None)
        

    def __set_properties(self):
        self.check_lot.SetToolTip(wx.ToolTip(_(u"Filtre Lot de lettres de rappel")))
        self.ctrl_lot.SetToolTip(wx.ToolTip(_(u"Sélectionnez un lot de lettres dans la liste")))
        self.check_emission.SetToolTip(wx.ToolTip(_(u"Filtre Date d'émission")))
        self.ctrl_emission_min.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date min")))
        self.ctrl_emission_max.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date max")))
        self.check_reference.SetToolTip(wx.ToolTip(_(u"Filtre Date d'échéance")))
        self.ctrl_reference_min.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date min")))
        self.ctrl_reference_max.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date max")))
        self.check_numeros_intervalle.SetToolTip(wx.ToolTip(_(u"Filtre Intervalle de numéros de lettres")))
        self.ctrl_numeros_intervalle_min.SetToolTip(wx.ToolTip(_(u"Saisissez un numéro de lettre min")))
        self.ctrl_numeros_intervalle_max.SetToolTip(wx.ToolTip(_(u"Saisissez un numéro de lettre max")))
        self.check_numeros_liste.SetToolTip(wx.ToolTip(_(u"Filtre Liste de numéros de lettres")))
        self.ctrl_numeros_liste.SetToolTip(wx.ToolTip(_(u"Saisissez les numéros de lettres souhaités en les séparant par un point-virgule (;)")))
        self.check_solde.SetToolTip(wx.ToolTip(_(u"Filtre Solde")))
        self.ctrl_solde_operateur.SetToolTip(wx.ToolTip(_(u"Sélectionnez un opération de comparaison")))
        self.ctrl_solde_montant.SetToolTip(wx.ToolTip(_(u"Saisissez un montant")))
        self.check_email.SetToolTip(wx.ToolTip(_(u"Filtre Envoi par Email")))
        self.ctrl_email.SetToolTip(wx.ToolTip(_(u"Oui/Non")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=20, hgap=20)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Filtres
        grid_sizer_contenu = wx.FlexGridSizer(rows=10, cols=1, vgap=10, hgap=10)
                
        grid_sizer_lot = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_lot.Add(self.check_lot, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_lot.Add(self.ctrl_lot, 0, wx.EXPAND, 0)
        grid_sizer_lot.AddGrowableCol(1)
        grid_sizer_contenu.Add(grid_sizer_lot, 1, wx.EXPAND, 0)
        
        grid_sizer_emission = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_emission.Add(self.check_emission, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_emission.Add(self.ctrl_emission_min, 0, 0, 0)
        grid_sizer_emission.Add(self.label_emission_a, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_emission.Add(self.ctrl_emission_max, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_emission, 1, wx.EXPAND, 0)
        
        grid_sizer_reference = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_reference.Add(self.check_reference, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reference.Add(self.ctrl_reference_min, 0, 0, 0)
        grid_sizer_reference.Add(self.label_reference_a, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reference.Add(self.ctrl_reference_max, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_reference, 1, wx.EXPAND, 0)
        
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
        
        grid_sizer_solde = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_solde.Add(self.check_solde, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_solde.Add(self.ctrl_solde_operateur, 0, 0, 0)
        grid_sizer_solde.Add(self.ctrl_solde_montant, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_solde, 1, wx.EXPAND, 0)
        
        grid_sizer_email = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_email.Add(self.check_email, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_email.Add(self.ctrl_email, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_email, 1, wx.EXPAND, 0)

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
        UTILS_Aide.Aide("Imprimer1")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnCheck(self, event): 
        self.ctrl_lot.Enable(self.check_lot.GetValue())

        self.ctrl_emission_min.Enable(self.check_emission.GetValue())
        self.ctrl_emission_max.Enable(self.check_emission.GetValue())

        self.ctrl_reference_min.Enable(self.check_reference.GetValue())
        self.ctrl_reference_max.Enable(self.check_reference.GetValue())
        
        self.ctrl_numeros_intervalle_min.Enable(self.check_numeros_intervalle.GetValue())
        self.ctrl_numeros_intervalle_max.Enable(self.check_numeros_intervalle.GetValue())

        self.ctrl_numeros_liste.Enable(self.check_numeros_liste.GetValue())

        self.ctrl_solde_operateur.Enable(self.check_solde.GetValue())
        self.ctrl_solde_montant.Enable(self.check_solde.GetValue())

        self.ctrl_email.Enable(self.check_email.GetValue())
    
    def GetFiltres(self):
        filtres = []
        
        # Lots de lettres
        if self.check_lot.GetValue() == True :
            IDlot = self.ctrl_lot.GetID()
            if IDlot == None :
                dlg = wx.MessageDialog(self, _(u"Filtre Lot de lettres : Vous n'avez sélectionné aucun lot dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            filtres.append({"type" : "lot", "IDlot" : IDlot})
        
        # Date d'émission
        if self.check_emission.GetValue() == True :
            date_min = self.ctrl_emission_min.GetDate()
            date_max = self.ctrl_emission_max.GetDate()
            if date_min == None or date_max == None :
                dlg = wx.MessageDialog(self, _(u"Filtre Date d'émission : Les dates saisies ne sont pas valides !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
            filtres.append({"type" : "date_emission", "date_min" : date_min, "date_max" : date_max})

        # Date de référence
        if self.check_reference.GetValue() == True :
            date_min = self.ctrl_reference_min.GetDate()
            date_max = self.ctrl_reference_max.GetDate()
            if date_min == None or date_max == None :
                dlg = wx.MessageDialog(self, _(u"Filtre Date de référence : Les dates saisies ne sont pas valides !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
            filtres.append({"type" : "date_reference", "date_min" : date_min, "date_max" : date_max})

        # Numéros Intervalle
        if self.check_numeros_intervalle.GetValue() == True :
            numero_min = int(self.ctrl_numeros_intervalle_min.GetValue())
            numero_max = int(self.ctrl_numeros_intervalle_max.GetValue())
        
            filtres.append({"type" : "numero_intervalle", "numero_min" : numero_min, "numero_max" : numero_max})

        # Numéros Liste
        if self.check_numeros_liste.GetValue() == True :
            listeTemp = self.ctrl_numeros_liste.GetValue()
            if listeTemp == "" :
                dlg = wx.MessageDialog(self, _(u"Filtre Liste de numéros : Vous n'avez saisi aucun numéro de lettre dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            try :
                listeNumeros = []
                for numero in listeTemp.split(";") :
                    listeNumeros.append(int(numero))
            except :
                dlg = wx.MessageDialog(self, _(u"Filtre Liste de numéros : Les numéros de lettres saisis ne sont pas valides !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
            filtres.append({"type" : "numero_liste", "liste" : listeNumeros})

        # Solde
        if self.check_solde.GetValue() == True :
            operateur = self.ctrl_solde_operateur.GetStringSelection()
            montant = self.ctrl_solde_montant.GetMontant()
            if montant == None :
                dlg = wx.MessageDialog(self, _(u"Filtre Solde : Le montant saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
            filtres.append({"type" : "solde", "operateur" : operateur, "montant" : montant})

        # Email
        if self.check_email.GetValue() == True :
            if self.ctrl_email.GetSelection() == 0 :
                choix = True
            else :
                choix = False
                
            filtres.append({"type" : "email", "choix" : choix})

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
            
            # Lot de lettres
            if filtre["type"] == "lot" :
                self.check_lot.SetValue(True)
                self.ctrl_lot.SetID(filtre["IDlot"])
        
            # Date d'émission
            if filtre["type"] == "date_emission" :
                self.check_emission.SetValue(True)
                self.ctrl_emission_min.SetDate(filtre["date_min"])
                self.ctrl_emission_max.SetDate(filtre["date_max"])

            # Date de référence
            if filtre["type"] == "date_reference" :
                self.check_reference.SetValue(True)
                self.ctrl_reference_min.SetDate(filtre["date_min"])
                self.ctrl_reference_max.SetDate(filtre["date_max"])

            # numero_intervalle
            if filtre["type"] == "numero_intervalle" :
                self.check_numeros_intervalle.SetValue(True)
                self.ctrl_numeros_intervalle_min.SetValue(filtre["numero_min"])
                self.ctrl_numeros_intervalle_max.SetValue(filtre["numero_max"])

            # numero_liste
            if filtre["type"] == "numero_liste" :
                self.check_numeros_liste.SetValue(True)
                self.ctrl_numeros_liste.SetValue(";".join(filtre["liste"]))

            # Solde
            if filtre["type"] == "solde" :
                self.check_solde.SetValue(True)
                self.ctrl_solde_operateur.SetStringSelection(filtre["operateur"])
                self.ctrl_solde_montant.SetMontant(filtre["montant"])
            
            # Email
            if filtre["type"] == "email" :
                self.check_email.SetValue(True)
                self.ctrl_email.SetSelection(not int(filtre["choix"]))

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

##if __name__ == '__main__':
##    app = wx.App(0)
##    #wx.InitAllImageHandlers()
##    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
##    app.SetTopWindow(frame_1)
##    frame_1.Show()
##    app.MainLoop()

# -------------------- POUR TESTER DIALOG -----------------------------------------------------------------------------------
        
if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    
    # Test d'importation de filtres
    dlg.SetFiltres([
        {"type" : "numero_intervalle", "numero_min" : 210, "numero_max" : 215},
        {"type" : "solde", "operateur" : ">=", "montant" : 2.15},
        ])
    
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
