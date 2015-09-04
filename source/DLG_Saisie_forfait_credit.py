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
import GestionDB
import datetime
import wx.lib.agw.hypertreelist as HTL
import calendar

import CTRL_Saisie_date
import CTRL_Saisie_euros
import UTILS_Titulaires
import UTILS_Dates
from dateutil import relativedelta

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


class CTRL_Forfaits(HTL.HyperTreeList):
    def __init__(self, parent, grille=None): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.SetAGWWindowStyleFlag(wx.TR_COLUMN_LINES | HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.parent = parent
        self.grille = grille
        self.IDfamille = None
        self.date = None
        self.dictBranches = {}
        
        self.SetBackgroundColour(wx.WHITE)
        
        # Adapte taille Police pour Linux
        import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)
        
        # Binds
##        self.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnContextMenu)
            
    def Initialisation(self):      
        self.dictBranches = {}
                 
        # Création des colonnes
        self.AddColumn(_(u"Individu/Forfait"))
        self.SetMainColumn(0)
        self.SetColumnWidth(0, 230)
        self.AddColumn(_(u"Activité"))
        self.SetColumnWidth(1, 60)
        self.AddColumn(_(u"Tarif"))
        self.SetColumnWidth(2, 60)
        self.SetColumnAlignment(2, wx.ALIGN_RIGHT)

        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        
        if self.IDfamille == None or self.date == None:
            return
        
        # Recherche des données
        self.dictDonnees = self.grille.GetTarifsForfaitsCreditDisponibles(self.date)
        
        # Recherche du nom des titulaires
        dictTitulaires = UTILS_Titulaires.GetTitulaires([self.IDfamille,])
                    
        # Création des branches
        for IDfamille, dictFamille in self.dictDonnees.iteritems() :
            
            if IDfamille == self.IDfamille :
                
                # Forfait familial
                listeTemp = []
                for dictTarif in dictFamille["forfaits"] :
                    listeTemp.append((dictTarif["resultat"]["nomActivite"], dictTarif["resultat"]["nom_tarif"], dictTarif))
                listeTemp.sort()
                for nomActivite, label, dictTarif in listeTemp :
                    item = self.CreationBrancheTarif(self.root, dictTarif)
                    self.dictBranches[(None, dictTarif["IDtarif"])] = item
                    
                # Forfaits individuels
                for IDindividu, dictIndividu in dictFamille["individus"].iteritems() :
                    
                    if len(dictIndividu["forfaits"]) > 0 :
                        label = u"%s %s" % (dictIndividu["nom"], dictIndividu["prenom"])
                        brancheIndividu = self.AppendItem(self.root, label)
                        self.SetPyData(brancheIndividu, {"type":"individu", "donnees":IDindividu})
                        self.SetItemBold(brancheIndividu, True)

                        listeTemp = []
                        for dictTarif in dictIndividu["forfaits"] :
                            listeTemp.append((dictTarif["resultat"]["nomActivite"], dictTarif["resultat"]["nom_tarif"], dictTarif))
                        listeTemp.sort()
                        for nomActivite, label, dictTarif in listeTemp :
                            item = self.CreationBrancheTarif(brancheIndividu, dictTarif)
                            self.dictBranches[(IDindividu, dictTarif["IDtarif"])] = item
                            
        self.ExpandAllChildren(self.root)
                
    def CreationBrancheTarif(self, brancheParente, dictTarif):
        label = dictTarif["resultat"]["nom_tarif"]
        branche = self.AppendItem(brancheParente, label)
        self.SetPyData(branche, {"type":"tarif", "donnees":dictTarif})
        nomActivite = dictTarif["resultat"]["nomActivite"]
        self.SetItemText(branche, nomActivite, 1)
        montant = dictTarif["resultat"]["montant_tarif"]
        self.SetItemText(branche, u"%.2f %s " % (montant, SYMBOLE), 2)
        return branche
                                                
    def MAJ(self, IDfamille=None, date=None):
        self.IDfamille = IDfamille
        self.date = date
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()
    
    def GetForfait(self):
        """ Retourne la sélection """
        item = self.GetSelection() 
        if item == -1 :
            return None
        data = self.GetPyData(item)
        if data == None :
            return None
        if data["type"] == "tarif" :
            dictTarif = data["donnees"]
            return dictTarif
        return None
    
    def SetForfait(self, IDindividu=None, IDtarif=None):
        if self.dictBranches.has_key((IDindividu, IDtarif)) :
            item = self.dictBranches[(IDindividu, IDtarif)]
            self.SelectItem(item)
    
    def Activation(self, etat=False):
        self.EnableChildren(self.root, etat)
        self.Enable(etat)

# -------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Famille(wx.Choice):
    def __init__(self, parent, listeFamilles=[]):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeFamilles = listeFamilles
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires(self.listeFamilles)
        self.MAJ() 
    
    def MAJ(self):
        listeItems = []
        for IDfamille in self.listeFamilles :
            listeItems.append(self.dictTitulaires[IDfamille]["titulairesSansCivilite"])
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.SetItems(listeItems)
        if len(listeItems) == 1 :
            self.Select(0)
            self.Enable(False)
                                        
    def SetIDfamille(self, IDfamille=None):
        index = 0
        for IDfamilleTmp in self.listeFamilles :
            if IDfamilleTmp == IDfamille :
                self.SetSelection(index)
            index += 1

    def GetIDfamille(self):
        index = self.GetSelection()
        if index == -1 :
            return None
        else :
            return self.listeFamilles[index]
    
    def GetIDcompte_payeur(self):
        IDfamille = self.GetIDfamille()
        if IDfamille == None :
            return None
        else:
            return self.dictTitulaires[IDfamille]["IDcompte_payeur"]
        
# -------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, grille=None, listeFamilles=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        self.grille = grille
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))

        self.label_famille = wx.StaticText(self, -1, _(u"Famille :"))
        self.ctrl_famille = CTRL_Famille(self, listeFamilles)

        self.label_dates = wx.StaticText(self, -1, _(u"Validité du :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self, activeCallback=False)

        # Forfaits
        self.box_forfaits_staticbox = wx.StaticBox(self, -1, _(u"Forfaits disponibles"))
        self.ctrl_forfaits = CTRL_Forfaits(self, grille=self.grille)

        # Prestation
        self.box_prestation_staticbox = wx.StaticBox(self, -1, _(u"Prestation"))

        self.label_label = wx.StaticText(self, -1, _(u"Label :"))
        self.ctrl_label = wx.TextCtrl(self, -1, "")

        self.label_date_prestation = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date_prestation = CTRL_Saisie_date.Date2(self, activeCallback=False)
        
        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_CHOICE, self.OnChoixFamille, self.ctrl_famille)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.ctrl_forfaits.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnChoixForfait)
        self.ctrl_forfaits.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDoubleClicForfait)

        # Init contrôles
        self.OnChoixFamille() 
        self.ctrl_date_debut.SetFocus()
        

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un forfait crédit"))
        self.ctrl_forfaits.SetToolTipString(_(u"Sélectionnez un forfait à créer"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((-1, 640))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
##        # Famille
##        grid_sizer_famille = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
##        grid_sizer_famille.Add(self.label_famille, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_famille.Add(self.ctrl_famille, 0, wx.EXPAND, 0)
##        grid_sizer_famille.AddGrowableCol(1)
##        grid_sizer_base.Add(grid_sizer_famille, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        grid_sizer_parametres.Add(self.label_famille, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_famille, 0, wx.EXPAND, 0)
        
        grid_sizer_parametres.Add(self.label_dates, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_parametres.Add(grid_sizer_dates, 1, wx.EXPAND, 0)

        grid_sizer_parametres.AddGrowableCol(1)
        box_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_parametres, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Forfaits
        box_forfaits = wx.StaticBoxSizer(self.box_forfaits_staticbox, wx.VERTICAL)
        box_forfaits.Add(self.ctrl_forfaits, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_forfaits, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Prestation
        box_prestation = wx.StaticBoxSizer(self.box_prestation_staticbox, wx.VERTICAL)
        grid_sizer_prestation = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        grid_sizer_prestation.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        
        grid_sizer_prestation.Add(self.label_date_prestation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_prestation_2 = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_prestation_2.Add(self.ctrl_date_prestation, 0, 0, 0)
        grid_sizer_prestation_2.Add( (40, 5), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation_2.Add(self.label_montant, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation_2.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_prestation.Add(grid_sizer_prestation_2, 1, wx.EXPAND, 0)

        grid_sizer_prestation.AddGrowableCol(1)
        box_prestation.Add(grid_sizer_prestation, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_prestation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnChoixFamille(self, event=None):
        IDfamille = self.ctrl_famille.GetIDfamille()
        self.ctrl_forfaits.MAJ(IDfamille, self.GetDateDebut() )
    
    def OnChoixDate(self):
        IDfamille = self.ctrl_famille.GetIDfamille()
        date_debut = self.GetDateDebut() 
        self.ctrl_forfaits.MAJ(IDfamille, date_debut)
    
    def OnChoixForfait(self, event=None):
        item = event.GetItem()
        data = self.ctrl_forfaits.GetPyData(item)
        date_debut_forfait = self.GetDateDebut() 
        if data == None :
            return
        if data["type"] == "tarif" :
            dictTarif = data["donnees"]
            
            # Définit les données par défaut
            self.SetDuree(dictTarif["forfait_duree"])
            self.ctrl_label.SetValue(dictTarif["resultat"]["nom_tarif"])
            self.ctrl_montant.SetMontant(dictTarif["resultat"]["montant_tarif"])
            
            # Recherche date de facturation du forfait
            date_facturation_tarif = dictTarif["date_facturation"]
            if date_facturation_tarif == "date_debut_forfait" : 
                date_facturation = date_debut_forfait
            elif date_facturation_tarif == "date_saisie" : 
                date_facturation = datetime.date.today()
            elif date_facturation_tarif != None and date_facturation_tarif.startswith("date:") : 
                date_facturation = UTILS_Dates.DateEngEnDateDD(date_facturation_tarif[5:])
            else :
                date_facturation = date_debut_forfait
            self.ctrl_date_prestation.SetDate(date_facturation)
            
    def GetLabel(self):
        return self.ctrl_label.GetValue()
    
    def GetDatePrestation(self):
        return self.ctrl_date_prestation.GetDate() 
    
    def GetMontant(self):
        return self.ctrl_montant.GetMontant() 
    
    def SetDuree(self, duree=None):
        dateDebut = self.GetDateDebut() 
        if duree != None and dateDebut != None :
            posM = duree.find("m")
            posA = duree.find("a")
            jours = int(duree[1:posM-1])-1
            mois = int(duree[posM+1:posA-1])
            annees = int(duree[posA+1:])
            
            dateFin = dateDebut
            if jours != 0 : dateFin = dateFin + relativedelta.relativedelta(days=+jours)
            if mois != 0 : dateFin = dateFin + relativedelta.relativedelta(months=+mois)
            if annees != 0 : dateFin = dateFin + relativedelta.relativedelta(years=+annees)

##            # Calcul des jours
##            if jours != 0:
##                dateFin = dateDebut + (datetime.timedelta(days = jours))
##                dateJour = dateFin.day
##                dateMois = dateFin.month
##                dateAnnee = dateFin.year
##
##            # Calcul des mois
##            if mois != 0:
##                dateMois = dateMois + mois
##                if dateMois > 12:
##                    division = divmod(dateMois, 12)
##                    dateAnnee = dateAnnee + division[0]
##                    dateMois = division[1]
##                nbreJoursMois = calendar.monthrange(dateAnnee, dateMois)[1]
##                if dateJour > nbreJoursMois :
##                    dateJour = nbreJoursMois
##                dateFin = datetime.date(dateAnnee, dateMois, dateJour)
##                dateJour = dateFin.day
##                dateMois = dateFin.month
##                dateAnnee = dateFin.year
##
##            # Calcul des années
##            if annees != 0:
##                dateAnnee = dateAnnee + annees
##                dateFin = datetime.date(dateAnnee, dateMois, dateJour)
            
            self.ctrl_date_fin.SetDate(dateFin)

    def OnDoubleClicForfait(self, event=None):
        self.OnBoutonOk()
        
    def OnBoutonAide(self, event=None):
        import UTILS_Aide
        UTILS_Aide.Aide("Utiliserdesforfaitcrdits")
    
    def SetFamille(self, IDfamille=None):
        self.ctrl_famille.SetIDfamille(IDfamille)
        self.OnChoixFamille()
    
    def SetDateDebut(self, date=None):
        self.ctrl_date_debut.SetDate(date)
        self.OnChoixDate() 
        
    def SetDateFin(self, date=None):
        self.ctrl_date_fin.SetDate(date)
    
    def SetLabel(self, label=u""):
        self.ctrl_label.SetValue(label)
        
    def SetDatePrestation(self, date=None):
        self.ctrl_date_prestation.SetDate(date) 
    
    def SetMontant(self, montant):
        self.ctrl_montant.SetMontant(montant)
    
    def SetForfait(self, IDindividu=None, IDtarif=None):
        if IDindividu == 0 :
            IDindividu = None
        self.ctrl_forfaits.SetFocus()
        self.ctrl_forfaits.SetForfait(IDindividu, IDtarif)
        
    def GetFamille(self):
        return self.ctrl_famille.GetIDfamille()
    
    def GetComptePayeur(self):
        return self.ctrl_famille.GetIDcompte_payeur()
    
    def GetDateDebut(self):
        return self.ctrl_date_debut.GetDate()

    def GetDateFin(self):
        return self.ctrl_date_fin.GetDate()

    def GetForfait(self):
        return self.ctrl_forfaits.GetForfait() 
    
    def OnBoutonOk(self, event=None):
        # validation : Famille
        if self.ctrl_famille.GetIDfamille() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une famille !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_famille.SetFocus()
            return False

        # validation des dates
        if self.ctrl_date_debut.Validation() == False or self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de début valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        if self.ctrl_date_fin.Validation() == False or self.ctrl_date_fin.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        if self.ctrl_date_debut.GetDate() > self.ctrl_date_fin.GetDate() :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas saisir une date de début supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False
        
        # Validation Forfait
        dictTarif = self.ctrl_forfaits.GetForfait() 
        if dictTarif == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un tarif dans la liste proposée !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_forfaits.SetFocus()
            return False

        # Validation Prestation
        if len(self.ctrl_label.GetValue()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un label pour cette prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_label.SetFocus()
            return False

        if self.ctrl_date_prestation.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date pour cette prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_prestation.SetFocus()
            return False

        if self.ctrl_montant.GetMontant() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un montant pour cette prestation !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return False

        # Ferme la fenêtre
        self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event=None): 
        self.EndModal(wx.ID_CANCEL)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
