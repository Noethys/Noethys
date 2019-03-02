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
from Ctrl import CTRL_Dates_forfait_date
#from Ctrl import CTRL_Tarification_type
CTRL_Tarification_type = UTILS_Adaptations.Import("Ctrl.CTRL_Tarification_type")



class ListBoxCombinaisons_ARCHIVE(wx.ListBox):
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
        for date, IDcombi_tarif, listeUnites in self.listeDonnees :
            if date != None :
                label = u"%s : " % DateComplete(date)
            else:
                label = u"? : "
            for IDcombi_tarif_unite, IDunite in listeUnites :
                label += self.dictUnites[IDunite]["nom"] + " + "
            if len(label) > 0 : label = label[:-2]
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
        req = """SELECT IDcombi_tarif, IDtarif, date
        FROM combi_tarifs
        WHERE IDtarif=%d AND type='FORFAIT'
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
        for IDcombi_tarif, IDtarif, date in listeCombinaisons :
            if date != None : date = DateEngEnDateDD(date)
            if IDcombi_tarif in dictDonnees :
                listeValeurs = []
                for dictValeurs in dictDonnees[IDcombi_tarif] :
                    listeValeurs.append([dictValeurs["IDcombi_tarif_unite"], dictValeurs["IDunite"]])
                listeDonnees.append([date, IDcombi_tarif,  listeValeurs])
        return listeDonnees
            
    def Sauvegarde(self):
        DB = GestionDB.DB()
        
        listeIDcombi = []
        listeIDunites = []
        
        for date, IDcombi_tarif, listeUnites in self.listeDonnees :
            # Sauvegarde des nouvelles combinaisons
            if IDcombi_tarif == None :
                listeDonnees = [ ("IDtarif", self.IDtarif ), ("type", "FORFAIT" ), ("date", str(date) ),]
                IDcombi_tarif = DB.ReqInsert("combi_tarifs", listeDonnees)
            else:
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
        date, listeIDunites = self.Saisie() 
        if listeIDunites == None : return
        listeTmp = []
        for IDunite in listeIDunites :
            listeTmp.append((None, IDunite))
        self.listeDonnees.append([date, None, listeTmp])
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
        date, IDcombi_tarifTmp, listeUnites = self.listeDonnees[index]
        for IDcombi_tarif_unite, IDunite in listeUnites :
            listeAnciennesIDunites.append(IDunite)
        listeAnciennesIDunites.sort()
        # Fenêtre de saisie
        date, listeIDunites = self.Saisie(date, listeAnciennesIDunites) 
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
        
    def ToutSupprimer(self):
        self.listeDonnees = []

    def Saisie(self, date=None, listeAnciennesIDunites=None):     
        ancienneDate = date           
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
        from Dlg import DLG_Saisie_combi_forfait
        dlg = DLG_Saisie_combi_forfait.Dialog(self, self.IDactivite, listeItems)
        dlg.SetDate(date)
        if len(listeAnciennesSelections) > 0 :
            dlg.SetUnites(listeAnciennesSelections)
        if dlg.ShowModal() == wx.ID_OK :
            listeSelections = dlg.GetUnites()
            date = dlg.GetDate()
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

        # Vérifie que les unités choises sont ouvertes à la date sélectionnée
        DB = GestionDB.DB()
        for IDunite in listeIDunites :
            req = """SELECT IDouverture, IDactivite, IDunite, IDgroupe, date
            FROM ouvertures
            WHERE IDactivite=%d AND IDunite=%d AND date='%s'
            ;""" % (self.IDactivite, IDunite, str(date))
            DB.ExecuterReq(req)
            listeOuvertures = DB.ResultatReq()
            if len(listeOuvertures) == 0 :
                dlg = wx.MessageDialog(self, _(u"Une des unités de cette combinaison n'est pas ouverte à la date sélectionnée.\nVous ne pouvez donc pas valider cette combinaison."), "Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                DB.Close()
                return None, None
        DB.Close()

        # Si c'est une modification, vérifie qu'une modification a été faite
        if listeAnciennesIDunites != None :
            if listeAnciennesIDunites == listeIDunites and ancienneDate == date :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez effectué aucune modification !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None, None
        
##        # Vérifie que la combinaison n'existe pas déjà
##        for dateTmp, IDcombi_tarifTmp, listeUnites in self.listeDonnees :
##            listeUnitesTmp = []
##            for IDcombi_tarif_uniteTmp, IDuniteTmp in listeUnites :
##                listeUnitesTmp.append(IDuniteTmp)
##            listeUnitesTmp.sort()
##            if listeUnitesTmp == listeIDunites and dateTmp == date  :
##                dlg = wx.MessageDialog(self, _(u"Cette combinaison existe déjà !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
##                dlg.ShowModal()
##                dlg.Destroy()
##                return None, None
        
        return date, listeIDunites
        
### -----------------------------------------------------------------------------------------------------------------------



class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None, nouveauTarif=True):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif
        self.nouveauTarif = nouveauTarif
        
        # Intro
        self.radio_conso_sans = wx.RadioButton(self, -1, _(u"Sans consommations"), style=wx.RB_GROUP)
        self.radio_conso_ouvertures = wx.RadioButton(self, -1, _(u"Créer les consommations selon le calendrier des ouvertures"))
        self.radio_conso_perso = wx.RadioButton(self, -1, _(u"Créer les consommations suivantes :"))
        
        # Combinaisons
        self.ctrl_combinaisons = CTRL_Dates_forfait_date.CTRL(self, IDactivite=IDactivite, IDtarif=IDtarif)
        self.bouton_modifier_combi = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_combi = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Autres paramètres
        self.ctrl_saisie_manuelle = wx.CheckBox(self, -1, _(u"Ce forfait peut être saisi manuellement depuis la grille des consommations"))
        self.ctrl_saisie_auto = wx.CheckBox(self, -1, _(u"Ce forfait est automatiquement créé lors de l'inscription à l'activité"))
        self.ctrl_suppression_auto = wx.CheckBox(self, -1, _(u"Ce forfait ne peut être supprimé que lors de la désinscription à l'activité"))

        # Date de facturation
        self.label_date_facturation = wx.StaticText(self, -1, _(u"Date de facturation :"))
        listeChoix = [
            ("date_debut_forfait", _(u"Date de début du forfait")),
            ("date_saisie", _(u"Date de la saisie du forfait")),
            ("date_debut_activite", _(u"Date de début de l'activité")),
            ]
        self.ctrl_date_facturation = CTRL_Tarification_type.CTRL_Date_facturation(self, listeChoix=listeChoix)
        self.ctrl_date_facturation.SetCodeSelection("date_debut_forfait") 


        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioCalendrier, self.radio_conso_sans)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioCalendrier, self.radio_conso_ouvertures)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioCalendrier, self.radio_conso_perso)
        self.Bind(wx.EVT_BUTTON, self.OnModifierCombi, self.bouton_modifier_combi)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerCombi, self.bouton_supprimer_combi)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckOptions, self.ctrl_saisie_manuelle)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckOptions, self.ctrl_saisie_auto)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckOptions, self.ctrl_suppression_auto)
        
        # Init
        if self.IDtarif != None :
            self.Importation() 
        if self.nouveauTarif == True :
            self.radio_conso_sans.SetValue(True)
        self.OnRadioCalendrier(None) 
        self.OnCheckOptions(None)

    def __set_properties(self):
        self.radio_conso_ouvertures.SetToolTip(wx.ToolTip(_(u"Cochez ce choix pour qu'aucune consommation ne soit créée")))
        self.radio_conso_ouvertures.SetToolTip(wx.ToolTip(_(u"Cochez ce choix pour que le forfait soit associé au calendrier des ouvertures")))
        self.radio_conso_perso.SetToolTip(wx.ToolTip(_(u"Cochez ce choix pour que le forfait soit basé sur les dates et unités saisies")))
        self.bouton_modifier_combi.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir ou modifier des combinaisons d'unités pour ce forfait")))
        self.bouton_supprimer_combi.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer en un clic TOUTES les combinaisons d'unités de cette liste")))
        self.ctrl_saisie_manuelle.SetToolTip(wx.ToolTip(_(u"Ce forfait peut être saisi manuellement dans la grille des consommations grâce à la commande dédiée")))
        self.ctrl_saisie_auto.SetToolTip(wx.ToolTip(_(u"Ce forfait est automatiquement saisi lorsqu'un individu s'inscrit à l'activité")))
        self.ctrl_suppression_auto.SetToolTip(wx.ToolTip(_(u"La suppression manuelle est impossible. Le forfait peut être uniquement supprimé lors d'un désincription à l'activité")))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=8, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.radio_conso_sans, 0, 0, 0)
        grid_sizer_base.Add(self.radio_conso_ouvertures, 0, 0, 0)
        grid_sizer_base.Add(self.radio_conso_perso, 0, 0, 0)
        
        # Liste Combinaisons
        grid_sizer_combinaisons = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_combinaisons.Add(self.ctrl_combinaisons, 0, wx.EXPAND|wx.LEFT, 20)
        
        grid_sizer_boutons_combi = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_combi.Add(self.bouton_modifier_combi, 0, 0, 0)
        grid_sizer_boutons_combi.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons_combi.Add(self.bouton_supprimer_combi, 0, 0, 0)
        grid_sizer_combinaisons.Add(grid_sizer_boutons_combi, 1, wx.EXPAND, 0)
        
        grid_sizer_combinaisons.AddGrowableRow(0)
        grid_sizer_combinaisons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_combinaisons, 1, wx.EXPAND, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_options.Add(self.ctrl_saisie_manuelle, 0, 0, 0)
        grid_sizer_options.Add(self.ctrl_saisie_auto, 0, 0, 0)
        grid_sizer_options.Add(self.ctrl_suppression_auto, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_options, 0, 0, 0)

        grid_sizer_date = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_date.Add(self.label_date_facturation, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date.Add(self.ctrl_date_facturation, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(grid_sizer_date, 0, wx.EXPAND, 0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)
    
    def OnRadioCalendrier(self, event):
        etat = self.radio_conso_perso.GetValue() 
        self.ctrl_combinaisons.Enable(etat)
        self.bouton_modifier_combi.Enable(etat)
        self.bouton_supprimer_combi.Enable(etat)
    
    def OnCheckOptions(self, event):
        if self.ctrl_saisie_manuelle.GetValue() == True :
            self.ctrl_saisie_auto.Enable(False)
            self.ctrl_saisie_auto.SetValue(False)
            self.ctrl_suppression_auto.Enable(False)
            self.ctrl_suppression_auto.SetValue(False)
        else :
            self.ctrl_saisie_auto.Enable(True)
        if self.ctrl_saisie_auto.GetValue() == True :
            self.ctrl_saisie_manuelle.Enable(False)
            self.ctrl_saisie_manuelle.SetValue(False)
            self.ctrl_suppression_auto.Enable(True)
        else :
            self.ctrl_saisie_manuelle.Enable(True)

    def OnModifierCombi(self, event): 
        self.ctrl_combinaisons.Modifier() 

    def OnSupprimerCombi(self, event): 
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer TOUTES les combinaisons de cette liste ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES :
            self.ctrl_combinaisons.ToutSupprimer() 
        dlg.Destroy()

    def SetDateFacturation(self, date_facturation):
        if date_facturation != None :
            self.ctrl_date_facturation.SetCodeSelection(date_facturation)
    
    def GetDateFacturation(self):
        return self.ctrl_date_facturation.GetCodeSelection() 

    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT forfait_saisie_manuelle, forfait_saisie_auto, forfait_suppression_auto, options, date_facturation
        FROM tarifs
        WHERE IDtarif=%d;""" % self.IDtarif
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        forfait_saisie_manuelle, forfait_saisie_auto, forfait_suppression_auto, options, date_facturation = listeDonnees[0]
        # Remplissage des contrôles
        if forfait_saisie_manuelle != None : self.ctrl_saisie_manuelle.SetValue(forfait_saisie_manuelle)
        if forfait_saisie_auto != None : self.ctrl_saisie_auto.SetValue(forfait_saisie_auto)
        if forfait_suppression_auto != None : self.ctrl_suppression_auto.SetValue(forfait_suppression_auto)
        
        if len(self.ctrl_combinaisons.listeDonnees) == 0 :
            self.radio_conso_sans.SetValue(True)
        else :
            self.radio_conso_perso.SetValue(True)
        if options != None and "calendrier" in options :
            self.radio_conso_ouvertures.SetValue(True)
        
        self.SetDateFacturation(date_facturation)
    
    def Validation(self):
        if self.radio_conso_perso.GetValue() == True and len(self.ctrl_combinaisons.listeDonnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune consommation pour ce forfait daté !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.ctrl_date_facturation.Validation() == False :
            return False

        return True
        
    def Sauvegarde(self):
        # Sauvegarde des combinaisons
        if self.radio_conso_sans.GetValue() == True :
            options = None
            self.ctrl_combinaisons.ToutSupprimer()
        if self.radio_conso_ouvertures.GetValue() == True :
            options = None
            self.ctrl_combinaisons.ToutSupprimer()
            options = "calendrier"   
        if self.radio_conso_perso.GetValue() == True :
            options = None
        self.ctrl_combinaisons.Sauvegarde() 
        
        # Récupération des autres données
        forfait_saisie_manuelle = int(self.ctrl_saisie_manuelle.GetValue())
        forfait_saisie_auto = int(self.ctrl_saisie_auto.GetValue())
        forfait_suppression_auto = int(self.ctrl_suppression_auto.GetValue())
        date_facturation = self.GetDateFacturation()
        
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
            ("forfait_saisie_manuelle", forfait_saisie_manuelle),
            ("forfait_saisie_auto", forfait_saisie_auto), 
            ("forfait_suppression_auto", forfait_suppression_auto), 
            ("options", options), 
            ("date_facturation", date_facturation ),
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