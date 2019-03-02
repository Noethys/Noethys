#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime

import GestionDB
#from Ctrl import CTRL_Tarification_type
CTRL_Tarification_type = UTILS_Adaptations.Import("Ctrl.CTRL_Tarification_type")


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))



class ListBoxCombinaisons(wx.ListBox):
    def __init__(self, parent, IDactivite=None, IDtarif=None):
        wx.ListBox.__init__(self, parent, -1)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif
        self.listeAnciennesCombi = []
        self.listeAnciennesUnites = []
        self.dictUnites = self.ImportationUnites()
        self.listeDonnees = self.Importation()
        if self.listeDonnees == None : 
            self.listeDonnees = []
        self.MAJ() 
    
    def MAJ(self):
        self.Clear()
        if self.listeDonnees == None : return
        self.listeDonnees.sort()
        for IDcombi_tarif, quantite_max, listeUnites in self.listeDonnees :
            label = u""
            for IDcombi_tarif_unite, IDunite in listeUnites :
                label += self.dictUnites[IDunite]["nom"] + " + "
            if len(label) > 0 : label = label[:-2]
            if quantite_max != None :
                label += u" (%d max)" % quantite_max
            self.Insert(label, self.GetCount(), IDcombi_tarif) 
    
    def ImportationUnites(self):
        # Recherche des unités disponibles de l'activité
        db = GestionDB.DB()
        req = """SELECT IDunite, ordre, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        db.ExecuterReq(req)
        listeUnites = db.ResultatReq()
        db.Close()
        dictUnites = {}
        for IDunite, ordre, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin in listeUnites :
            dictUnites[IDunite] = {"ordre":ordre, "nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin, "date_debut":date_debut, "date_fin":date_fin}
        return dictUnites
    
    def Importation(self):
        if self.IDtarif == None : return None
        # Importation des combinaisons
        db = GestionDB.DB()
        req = """SELECT IDcombi_tarif, IDtarif, quantite_max
        FROM combi_tarifs
        WHERE IDtarif=%d AND type='CREDIT'
        ORDER BY IDcombi_tarif;""" % self.IDtarif
        db.ExecuterReq(req)
        listeCombinaisons = db.ResultatReq()
        db.Close()
        if len(listeCombinaisons) == 0 : return None
        for IDcombi_tarif, IDtarif, date in listeCombinaisons :
            self.listeAnciennesCombi.append(IDcombi_tarif)
        # Importation des unités des combinaisons
        db = GestionDB.DB()
        req = """SELECT IDcombi_tarif_unite, IDcombi_tarif, IDunite
        FROM combi_tarifs_unites
        WHERE IDtarif=%d;""" % self.IDtarif
        db.ExecuterReq(req)
        listeUnites = db.ResultatReq()
        db.Close()
        if len(listeUnites) == 0 : return None
        dictDonnees = {}
        for IDcombi_tarif_unite, IDcombi_tarif, IDunite in listeUnites :
            self.listeAnciennesUnites.append(IDcombi_tarif_unite)
            dictTemp = {"IDcombi_tarif_unite":IDcombi_tarif_unite, "IDunite":IDunite}
            if IDcombi_tarif in dictDonnees :
                dictDonnees[IDcombi_tarif].append(dictTemp)
            else:
                dictDonnees[IDcombi_tarif] = [dictTemp,]
        # Création de la liste des données
        listeDonnees = []
        for IDcombi_tarif, IDtarif, quantite_max in listeCombinaisons :
            if IDcombi_tarif in dictDonnees :
                listeValeurs = []
                for dictValeurs in dictDonnees[IDcombi_tarif] :
                    listeValeurs.append([dictValeurs["IDcombi_tarif_unite"], dictValeurs["IDunite"]])
                listeDonnees.append([IDcombi_tarif, quantite_max, listeValeurs])
        return listeDonnees
            
    def Sauvegarde(self):
        DB = GestionDB.DB()
        
        listeIDcombi = []
        listeIDunites = []
        
        for IDcombi_tarif, quantite_max, listeUnites in self.listeDonnees :
            # Sauvegarde des nouvelles combinaisons
            if IDcombi_tarif == None :
                listeDonnees = [ ("IDtarif", self.IDtarif ), ("type", "CREDIT" ), ("quantite_max", quantite_max),]
                IDcombi_tarif = DB.ReqInsert("combi_tarifs", listeDonnees)
            else:
                DB.ReqMAJ("combi_tarifs", [("quantite_max", quantite_max),], "IDcombi_tarif", IDcombi_tarif)
                listeIDcombi.append(IDcombi_tarif)
            
            # Sauvegarde des unités de combi
            for IDcombi_tarif_unite, IDunite in listeUnites :
                
                # Nouvelles unités
                if IDcombi_tarif_unite == None :
                    listeDonnees = [ ("IDcombi_tarif", IDcombi_tarif ), ("IDtarif", self.IDtarif ), ("IDunite", IDunite ), ]
                    IDcombi_tarif_unite = DB.ReqInsert("combi_tarifs_unites", listeDonnees)
                else:
                    listeIDunites.append(IDcombi_tarif_unite)
        
        # Suppression des combi supprimées
        for IDcombi_tarif in self.listeAnciennesCombi :
            if IDcombi_tarif not in listeIDcombi :
                DB.ReqDEL("combi_tarifs", "IDcombi_tarif", IDcombi_tarif)
            
        # Suppression des unités supprimées
        for IDcombi_tarif_unite in self.listeAnciennesUnites :
            if IDcombi_tarif_unite not in listeIDunites :
                DB.ReqDEL("combi_tarifs_unites", "IDcombi_tarif_unite", IDcombi_tarif_unite)
        
        DB.Close()
    
    def Ajouter(self):
        listeIDunites, quantite_max = self.Saisie() 
        if listeIDunites == None : return
        listeTmp = []
        for IDunite in listeIDunites :
            listeTmp.append((None, IDunite))
        self.listeDonnees.append([None, quantite_max, listeTmp])
        self.MAJ() 
    
    def Modifier(self):
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune combinaison à modifier dans la liste !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcombi_tarif = self.GetClientData(index)
        # Récupération des anciennes IDunites
        listeAnciennesIDunites = []
        IDcombi_tarifTmp, quantite_max, listeUnites = self.listeDonnees[index]
        for IDcombi_tarif_unite, IDunite in listeUnites :
            listeAnciennesIDunites.append(IDunite)
        listeAnciennesIDunites.sort()
        # Fenêtre de saisie
        listeIDunites, quantite_max = self.Saisie(listeAnciennesIDunites, quantite_max) 
        if listeIDunites == None : return
        # Modification de la liste de données
        listeValeurs = []
        listeTemp = []
        for IDunite in listeIDunites :
            found = False
            for IDcombi_tarif_uniteTmp, IDuniteTmp in self.listeDonnees[index][2] :
                if IDuniteTmp == IDunite :
                    listeTemp.append([IDcombi_tarif_uniteTmp, IDuniteTmp])
                    found = True
            if found == False :
                listeTemp.append([None, IDunite])
        self.listeDonnees[index][1] = quantite_max
        self.listeDonnees[index][2] = listeTemp
        self.MAJ() 
    
    def Supprimer(self):
        index = self.GetSelection()
        if index == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune combinaison à supprimer dans la liste !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcombi_tarif = self.GetClientData(index)
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette combinaison ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            # Suppression
            self.listeDonnees.pop(index)
            self.MAJ() 
        dlg.Destroy()

    def Saisie(self, listeAnciennesIDunites=None, ancienne_quantite_max=None):     
        # Recherche des unités disponibles de l'activité
        db = GestionDB.DB()
        req = """SELECT IDunite, nom, type, heure_debut, heure_fin, date_debut, date_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        db.ExecuterReq(req)
        listeUnites = db.ResultatReq()
        db.Close()
        if len(listeUnites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'existe aucune unité pour cette activité !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return None, None
        
        listeAnciennesSelections = []
        listeItems = []
        index = 0
        for valeurs in listeUnites :
            if listeAnciennesIDunites != None :
                if valeurs[0] in listeAnciennesIDunites :
                    listeAnciennesSelections.append(index)
            listeItems.append(valeurs[1])
            index += 1
            
        # Boîte de dialogue pour choisir les combinaisons
        from Dlg import DLG_Saisie_combi_credit
        dlg = DLG_Saisie_combi_credit.Dialog(self, self.IDactivite, listeItems)
        dlg.SetQuantiteMax(ancienne_quantite_max)
        if len(listeAnciennesSelections) > 0 :
            dlg.SetUnites(listeAnciennesSelections)
        if dlg.ShowModal() == wx.ID_OK :
            listeSelections = dlg.GetUnites()
            quantite_max = dlg.GetQuantiteMax()
            if len(listeSelections) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucune unité !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None, None

            # Vérifie que les unités sélectionnées sont compatibles entre elles
            db = GestionDB.DB()
            req = """SELECT IDunite_incompat, IDunite, IDunite_incompatible
            FROM unites_incompat;"""
            db.ExecuterReq(req)
            listeIncompatibilites = db.ResultatReq()
            db.Close()
            if len(listeIncompatibilites) > 0 :
                for indexSelection1 in listeSelections :
                    IDunite1 = listeUnites[indexSelection1][0]
                    nomUnite1 = listeUnites[indexSelection1][1]
                    for indexSelection2 in listeSelections : 
                        IDunite2 = listeUnites[indexSelection2][0]
                        nomUnite2 = listeUnites[indexSelection2][1]
                        if IDunite1 != IDunite2 :
                            for IDunite_incompat, IDunite, IDunite_incompatible in listeIncompatibilites :
                                if (IDunite == IDunite1 and IDunite_incompatible == IDunite2) or (IDunite == IDunite2 and IDunite_incompatible == IDunite1) :
                                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas créer cette combinaison car les\nunités '%s' et '%s' sont incompatibles entre elles !") % (nomUnite1, nomUnite2), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                                    dlg.ShowModal()
                                    dlg.Destroy()
                                    return None, None
            dlg.Destroy()
        else:
            dlg.Destroy()
            return None, None
        
        # Crée une liste des IDunités sélectionnés
        listeIDunites = []
        for selection in listeSelections :
            listeIDunites.append(listeUnites[selection][0])
        listeIDunites.sort()

        # Si c'est une modification, vérifie qu'une modification a été faite
        if listeAnciennesIDunites != None :
            if listeAnciennesIDunites == listeIDunites and ancienne_quantite_max == quantite_max :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez effectué aucune modification !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None, None
        
##        # Vérifie que la combinaison n'existe pas déjà
##        for IDcombi_tarifTmp, quantite_maxTemp, listeUnites in self.listeDonnees :
##            listeUnitesTmp = []
##            for IDcombi_tarif_uniteTmp, IDuniteTmp in listeUnites :
##                listeUnitesTmp.append(IDuniteTmp)
##            listeUnitesTmp.sort()
##            if listeUnitesTmp == listeIDunites  :
##                dlg = wx.MessageDialog(self, _(u"Cette combinaison existe déjà !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
##                dlg.ShowModal()
##                dlg.Destroy()
##                return None, None
        
        return listeIDunites, quantite_max
        
# -----------------------------------------------------------------------------------------------------------------------



class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None, nouveauTarif=True):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif
        self.nouveauTarif = nouveauTarif
        
        # Intro
        self.label_intro = wx.StaticText(self, -1, _(u"Saisissez les unités associables au forfait :"))
        
        # Combinaisons
        self.ctrl_combinaisons = ListBoxCombinaisons(self, IDactivite=IDactivite, IDtarif=IDtarif)
        self.bouton_ajouter_combi = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_combi = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_combi = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        # Durée
        self.label_duree_forfait = wx.StaticText(self, -1, _(u"Durée par défaut :"))
        self.ctrl_duree_forfait = wx.CheckBox(self, -1, _(u""))
        self.label_jours = wx.StaticText(self, -1, _(u"Jours :"))
        self.spin_jours = wx.SpinCtrl(self, -1, "", min=0, max=500)
        self.label_mois = wx.StaticText(self, -1, _(u"Mois :"))
        self.spin_mois = wx.SpinCtrl(self, -1, "", min=0, max=500)
        self.label_annees = wx.StaticText(self, -1, _(u"Années :"))
        self.spin_annees = wx.SpinCtrl(self, -1, "", min=0, max=500)

        # Blocage
        self.label_blocage_plafond = wx.StaticText(self, -1, _(u"Blocage plafond :"))
        self.ctrl_blocage_plafond = wx.CheckBox(self, -1, _(u"Bloquer si la quantité maximale de consommations est atteinte"))

        # Bénéficiaire
        self.label_type_forfait = wx.StaticText(self, -1, _(u"Type de forfait :"))
        self.ctrl_beneficiaire_individu = wx.RadioButton(self, -1, _(u"Forfait individuel"), style = wx.RB_GROUP)
        self.ctrl_beneficiaire_famille = wx.RadioButton(self, -1, _(u"Forfait familial"))
        
        # Date de facturation
        self.label_date_facturation = wx.StaticText(self, -1, _(u"Date de facturation :"))
        listeChoix = [
            ("date_debut_forfait", _(u"Date de début du forfait")),
            ("date_saisie", _(u"Date de la saisie du forfait")),
            ]
        self.ctrl_date_facturation = CTRL_Tarification_type.CTRL_Date_facturation(self, listeChoix=listeChoix)
        self.ctrl_date_facturation.SetCodeSelection("date_debut_forfait") 
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDuree, self.ctrl_duree_forfait)
        self.Bind(wx.EVT_BUTTON, self.OnAjouterCombi, self.bouton_ajouter_combi)
        self.Bind(wx.EVT_BUTTON, self.OnModifierCombi, self.bouton_modifier_combi)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerCombi, self.bouton_supprimer_combi)
        
        # Init
        if self.IDtarif != None :
            self.Importation() 
        self.OnCheckDuree() 

    def __set_properties(self):
        self.bouton_ajouter_combi.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une combinaison d'unités")))
        self.bouton_modifier_combi.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la combinaison d'unités selectionnée dans la liste")))
        self.bouton_supprimer_combi.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la combinaison d'unités selectionnée dans la liste")))
        self.ctrl_duree_forfait.SetToolTip(wx.ToolTip(_(u"Vous pouvez définir une durée de validité à partir de la date de début de forfait saisie par l'utilisateur")))
        self.ctrl_blocage_plafond.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour empêcher la saisie d'une consommation si la quantité maximale est atteinte")))
        self.spin_jours.SetMinSize((60, -1))
        self.spin_mois.SetMinSize((60, -1))
        self.spin_annees.SetMinSize((60, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=8, cols=1, vgap=5, hgap=5)
        
        grid_sizer_base.Add(self.label_intro, 0, 0, 0)
        
        # Liste Combinaisons
        grid_sizer_combinaisons = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_combinaisons.Add(self.ctrl_combinaisons, 0, wx.EXPAND, 0)
        
        grid_sizer_boutons_combi = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_combi.Add(self.bouton_ajouter_combi, 0, 0, 0)
        grid_sizer_boutons_combi.Add(self.bouton_modifier_combi, 0, 0, 0)
        grid_sizer_boutons_combi.Add(self.bouton_supprimer_combi, 0, 0, 0)
        grid_sizer_combinaisons.Add(grid_sizer_boutons_combi, 1, wx.EXPAND, 0)
        
        grid_sizer_combinaisons.AddGrowableRow(0)
        grid_sizer_combinaisons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_combinaisons, 1, wx.EXPAND, 0)

        grid_sizer_options = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        grid_sizer_options.Add(self.label_duree_forfait, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_duree = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_duree.Add(self.ctrl_duree_forfait, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_duree.Add(self.label_jours, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_duree.Add(self.spin_jours, 0, 0, 0)
        grid_sizer_duree.Add(self.label_mois, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree.Add(self.spin_mois, 0, 0, 0)
        grid_sizer_duree.Add(self.label_annees, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree.Add(self.spin_annees, 0, 0, 0)
        grid_sizer_options.Add(grid_sizer_duree, 0, 0, 0)

        grid_sizer_options.Add(self.label_blocage_plafond, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_blocage_plafond, 0, 0, 0)

        grid_sizer_options.Add(self.label_type_forfait, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_beneficiaire = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_beneficiaire.Add(self.ctrl_beneficiaire_individu, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_beneficiaire.Add(self.ctrl_beneficiaire_famille, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(grid_sizer_beneficiaire, 0, 0, 0)

        grid_sizer_options.Add(self.label_date_facturation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_date_facturation, 0, 0, 0)

        grid_sizer_options.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_options, 0, 0, 0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
    
    def OnCheckDuree(self, event=None):
        etat = self.ctrl_duree_forfait.GetValue()
        self.label_jours.Enable(etat)
        self.spin_jours.Enable(etat)
        self.label_mois.Enable(etat)
        self.spin_mois.Enable(etat)
        self.label_annees.Enable(etat)
        self.spin_annees.Enable(etat)
        
    def OnAjouterCombi(self, event): 
        self.ctrl_combinaisons.Ajouter()

    def OnModifierCombi(self, event): 
        self.ctrl_combinaisons.Modifier() 

    def OnSupprimerCombi(self, event):
        self.ctrl_combinaisons.Supprimer() 
    
    def SetDuree(self, duree=""):
        if duree == None :
            self.ctrl_duree_forfait.SetValue(False)
        else :
            self.ctrl_duree_forfait.SetValue(True)
            posM = duree.find("m")
            posA = duree.find("a")
            jours = int(duree[1:posM-1])
            mois = int(duree[posM+1:posA-1])
            annees = int(duree[posA+1:])
            self.spin_jours.SetValue(jours)
            self.spin_mois.SetValue(mois)
            self.spin_annees.SetValue(annees)
        self.OnCheckDuree(None)
        
    def GetDuree(self):
        if self.ctrl_duree_forfait.GetValue() == False :
            duree = None
        else:
            duree = "j%d-m%d-a%d" % (int(self.spin_jours.GetValue()), int(self.spin_mois.GetValue()), int(self.spin_annees.GetValue()),)
        return duree
    
    def SetBeneficiaire(self, beneficiaire="individu"):
        if beneficiaire == "individu" :
            self.ctrl_beneficiaire_individu.SetValue(True)
        else:
            self.ctrl_beneficiaire_famille.SetValue(True)
    
    def GetBeneficiaire(self):
        if self.ctrl_beneficiaire_individu.GetValue() == True :
            return "individu"
        else:
            return "famille"
    
    def SetDateFacturation(self, date_facturation):
        if date_facturation != None :
            self.ctrl_date_facturation.SetCodeSelection(date_facturation)
    
    def GetDateFacturation(self):
        return self.ctrl_date_facturation.GetCodeSelection() 
    
    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT forfait_duree, forfait_beneficiaire, date_facturation, options
        FROM tarifs
        WHERE IDtarif=%d;""" % self.IDtarif
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        forfait_duree, forfait_beneficiaire, date_facturation, options = listeDonnees[0]
        # Remplissage des contrôles
        self.SetDuree(forfait_duree)
        self.SetBeneficiaire(forfait_beneficiaire)
        self.SetDateFacturation(date_facturation)

        if options != None :
            # Blocage plafond
            if "blocage_plafond" in options :
                self.ctrl_blocage_plafond.SetValue(True)
            else :
                self.ctrl_blocage_plafond.SetValue(False)
    
    def Validation(self):
        if self.ctrl_duree_forfait.GetValue() == True :
            jours = int(self.spin_jours.GetValue())
            mois = int(self.spin_mois.GetValue())
            annees = int(self.spin_annees.GetValue())
            if jours == 0 and mois == 0 and annees == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous avez coché une durée limitée. \nVous devez donc saisir un nombre de jours et/ou de mois et/ou d'années."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.spin_jours.SetFocus()
                return False
        
        if self.ctrl_date_facturation.Validation() == False :
            return False
        
        return True
        
    def Sauvegarde(self):
        # Sauvegarde des combinaisons
        self.ctrl_combinaisons.Sauvegarde() 
        
        # Récupération des autres données
        forfait_duree = self.GetDuree()
        forfait_beneficiaire = self.GetBeneficiaire()
        date_facturation = self.GetDateFacturation()

        # Options
        if self.ctrl_blocage_plafond.GetValue() == True :
            options = "blocage_plafond"
        else :
            options = None
        
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
            ("forfait_duree", forfait_duree ),
            ("forfait_beneficiaire", forfait_beneficiaire ),
            ("date_facturation", date_facturation ),
            ("options", options),
            ]
        DB.ReqMAJ("tarifs", listeDonnees, "IDtarif", self.IDtarif)
        DB.Close() 



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDactivite=1, IDtarif=1)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()