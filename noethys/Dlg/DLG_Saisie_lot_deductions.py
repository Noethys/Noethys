#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import decimal
import wx.lib.agw.floatspin as FS

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros

import GestionDB
from Ol import OL_Saisie_lot_deductions
from Utils import UTILS_Identification
from Dlg import DLG_Messagebox

from Utils import UTILS_Gestion
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")




class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   

        # Bandeau
        titre = _(u"Saisir un lot de déductions")
        intro = _(u"Vous pouvez saisir ici un lot de déductions pour les prestations sélectionnées. Commencez par définir les caractéristiques de la déduction puis sélectionnez les prestations concernées.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Impayes.png")

        # Déduction
        self.box_deduction_staticbox = wx.StaticBox(self, -1, _(u"Paramètres de la déduction"))
        self.label_label = wx.StaticText(self, -1, _(u"Label :"))
        self.ctrl_label = wx.TextCtrl(self, -1, "")

        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.radio_montant_fixe = wx.RadioButton(self, -1, _(u"Montant fixe :"), style=wx.RB_GROUP)
        self.ctrl_montant_fixe = CTRL_Saisie_euros.CTRL(self)
        self.radio_montant_pourcent = wx.RadioButton(self, -1, _(u"Pourcentage :"))
        self.ctrl_montant_pourcent = FS.FloatSpin(self, -1, min_val=0, max_val=100, increment=0.1, agwStyle=FS.FS_RIGHT)
        self.ctrl_montant_pourcent.SetFormat("%f")
        self.ctrl_montant_pourcent.SetDigits(2)
        
        # Prestations
        self.box_prestations_staticbox = wx.StaticBox(self, -1, _(u"Sélection des prestations"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, "au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.bouton_actualiser = wx.Button(self, -1, _(u"Actualiser la liste"))

        self.listviewAvecFooter = OL_Saisie_lot_deductions.ListviewAvecFooter(self, kwargs={}) 
        self.ctrl_prestations = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Saisie_lot_deductions.CTRL_Outils(self, listview=self.ctrl_prestations, afficherCocher=True)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMontant, self.radio_montant_fixe)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMontant, self.radio_montant_pourcent)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        self.OnRadioMontant(None)
        self.ctrl_prestations.MAJ() 
        wx.CallLater(0, self.Layout)

    def __set_properties(self):
        self.ctrl_label.SetToolTip(wx.ToolTip(_(u"Saisissez le label de la déduction")))
        self.radio_montant_fixe.SetToolTip(wx.ToolTip(_(u"Saisie d'un montant pour chaque déduction")))
        self.radio_montant_pourcent.SetToolTip(wx.ToolTip(_(u"Saisie d'un pourcentage du montant de la prestation")))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez une date de début")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez une date de fin")))
        self.bouton_actualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour actualiser la liste")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((690, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Déduction
        box_deduction = wx.StaticBoxSizer(self.box_deduction_staticbox, wx.VERTICAL)
        grid_sizer_deduction = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_deduction.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_deduction.Add(self.ctrl_label, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_deduction.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_montant = wx.BoxSizer(wx.HORIZONTAL)
        
        g = wx.BoxSizer(wx.HORIZONTAL)
        g.Add(self.radio_montant_fixe, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        g.Add(self.ctrl_montant_fixe, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_montant.Add(g, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        
        g = wx.BoxSizer(wx.HORIZONTAL)
        g.Add(self.radio_montant_pourcent, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        g.Add(self.ctrl_montant_pourcent, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_montant.Add(g, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 15)

        grid_sizer_deduction.Add(grid_sizer_montant, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_deduction.AddGrowableCol(1)
        box_deduction.Add(grid_sizer_deduction, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_deduction, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Prestations
        box_prestations = wx.StaticBoxSizer(self.box_prestations_staticbox, wx.VERTICAL)
        grid_sizer_prestations = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add((20, 20), 0, 0, 0)
        grid_sizer_periode.Add(self.bouton_actualiser, 1, wx.EXPAND, 0)
        grid_sizer_periode.AddGrowableCol(5)
        grid_sizer_prestations.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_prestations.Add(self.listviewAvecFooter, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_options.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableCol(0)
        grid_sizer_prestations.Add(grid_sizer_options, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_prestations.AddGrowableRow(1)
        grid_sizer_prestations.AddGrowableCol(0)
        box_prestations.Add(grid_sizer_prestations, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(box_prestations, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnRadioMontant(self, event):
        self.ctrl_montant_fixe.Enable(self.radio_montant_fixe.GetValue())
        self.ctrl_montant_pourcent.Enable(self.radio_montant_pourcent.GetValue())
        
    def OnBoutonActualiser(self, event): 
        date_debut = self.ctrl_date_debut.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus() 
            return False

        date_fin = self.ctrl_date_fin.GetDate()
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus() 
            return False
        
        self.ctrl_prestations.SetPeriode(date_debut, date_fin)
        self.ctrl_prestations.MAJ() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Saisirunlotdedeductions")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)        
        
    def OnBoutonOk(self, event): 
        # Déduction
        label = self.ctrl_label.GetValue()
        if len(label) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un label pour la déduction !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_label.SetFocus() 
            return False
        
        if self.radio_montant_fixe.GetValue() == True :
            montant = self.ctrl_montant_fixe.GetMontant()
            typeValeur = "montant"
            if montant == 0.0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_montant_fixe.SetFocus()
                return False
        else :
            pourcent = self.ctrl_montant_pourcent.GetValue() 
            typeValeur = "pourcent"
            if pourcent == 0.0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un pourcentage !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_montant_pourcent.SetFocus()
                return False

        # Tracks
        tracks = self.ctrl_prestations.GetTracksCoches() 
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une ligne dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Périodes de gestion
        gestion = UTILS_Gestion.Gestion(None)
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        if gestion.IsPeriodeinPeriodes("prestations", date_debut, date_fin) == False: return False

        listePrestations = self.ctrl_prestations.GetListePrestations() 
        
        # Demande les prestations concernées
        listeLabelsPrestations = []
        for dictPrestation in listePrestations :
            if dictPrestation["label"] not in listeLabelsPrestations :
                listeLabelsPrestations.append(dictPrestation["label"]) 
        listeLabelsPrestations.sort() 
        
        dlg = wx.MultiChoiceDialog( self, _(u"Cochez les prestations auxquelles vous souhaitez appliquer les déductions :"), _(u"Sélection des prestations"), listeLabelsPrestations)
        dlg.SetSelections(range(0, len(listeLabelsPrestations)))
        reponse = dlg.ShowModal() 
        selections = dlg.GetSelections()
        listeSelectionPrestations = [listeLabelsPrestations[x] for x in selections]
        dlg.Destroy()
        if reponse != wx.ID_OK :
            return False
        
        # Confirmation
        nbrePrestations = 0
        for dictPrestation in listePrestations :
            if dictPrestation["label"] in listeSelectionPrestations :
                nbrePrestations += 1

        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la création automatique de %d déductions ?") % nbrePrestations, _(u"Demande de confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False
        
        
        
        # ----------------------------- Création des déductions -----------------------------------------------------------
        DB = GestionDB.DB()
        
        listeAjouts = []
        listeModifications = []
        listeSupprVentilations = []
        listeAnomalies = []
        for dictPrestation in listePrestations :
            
            # Vérifie si label sélectionné :
            if dictPrestation["label"] in listeSelectionPrestations :
                
                # Calcul du montant de la déduction
                montantPrestation = float(dictPrestation["montant"])
                montantVentilation = float(dictPrestation["paye"])
                
                if typeValeur == "montant" :
                    montantDeduction = montant
                if typeValeur == "pourcent" :
                    montantDeduction = float(decimal.Decimal(montantPrestation * pourcent / 100.0))
                
                nouveauMontantPrestation = montantPrestation - montantDeduction
                
                # Détection anomalie
                valide = True
                labelPrestation = _(u"Famille ID%d - Prestation ID%d '%s' : ") % (dictPrestation["IDfamille"], dictPrestation["IDprestation"], dictPrestation["label"])
                
                if nouveauMontantPrestation < 0.0 :
                    listeAnomalies.append(labelPrestation + _(u"La déduction est plus élevée que le montant de la prestation !"))
                    valide = False

                if nouveauMontantPrestation < montantVentilation :
                    listeAnomalies.append(labelPrestation + _(u"La ventilation est plus élevée que le nouveau montant de la prestation !"))
                    valide = False

                if dictPrestation["IDfacture"] != None :
                    listeAnomalies.append(labelPrestation + _(u"La prestation ne peut être modifiée car elle apparaît sur une facture !"))
                    valide = False

                # Mémorisation
                if valide == True :
                    listeAjouts.append((dictPrestation["IDprestation"], dictPrestation["IDcompte_payeur"], str(datetime.date.today()), montantDeduction, label))
                    listeModifications.append((nouveauMontantPrestation, dictPrestation["IDprestation"]))
                    listeSupprVentilations.append(dictPrestation["IDprestation"]) 
                    
        # Affichages anomalies
        if len(listeAnomalies) > 0 :
            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Anomalies"), introduction=_(u"Les %d anomalies suivantes ont été détectées :") % len(listeAnomalies), detail=u"\n".join(listeAnomalies), conclusion=_(u"Souhaitez-vous continuer pour les %d déductions valides ?") % len(listeAjouts), icone=wx.ICON_EXCLAMATION, boutons=[_(u"Oui"), _(u"Non"), _(u"Annuler")])
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            if reponse in (1, 2) :
                return False
    
        # Sauvegarde
        DB = GestionDB.DB()
        if len(listeAjouts) > 0 :
            DB.Executermany(u"INSERT INTO deductions (IDprestation, IDcompte_payeur, date, montant, label) VALUES (?, ?, ?, ?, ?)", listeAjouts, commit=False)
        if len(listeModifications) > 0 :
            DB.Executermany(_(u"UPDATE prestations SET montant=? WHERE IDprestation=?"), listeModifications, commit=False)
        if len(listeSupprVentilations) > 0 :
            if len(listeSupprVentilations) == 1 : conditionSuppressions = "(%d)" % listeSupprVentilations[0]
            else : conditionSuppressions = str(tuple(listeSupprVentilations))
            DB.ExecuterReq("DELETE FROM ventilation WHERE IDprestation IN %s" % conditionSuppressions)
        DB.Commit()
        DB.Close() 
        
        # Confirmation
        dlg = wx.MessageDialog(self, _(u"%d déductions ont été créées avec succès.") % len(listeAjouts), _(u"Confirmation"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
        if len(listeAjouts) == 0 :
            return False
        
        # Fermeture
        self.EndModal(wx.ID_OK)
        
        
        

if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ctrl_date_debut.SetDate(datetime.date(2013, 1, 1))
    dlg.ctrl_date_fin.SetDate(datetime.date(2013, 12, 31))
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
