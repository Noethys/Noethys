#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import GestionDB



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
        for IDcombi_tarif, listeUnites in self.listeDonnees :
            label = u""
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
        req = """SELECT IDcombi_tarif, IDtarif
        FROM combi_tarifs
        WHERE IDtarif=%d and type='JOURN'
        ORDER BY IDcombi_tarif;""" % self.IDtarif
        db.ExecuterReq(req)
        listeCombinaisons = db.ResultatReq()
        db.Close()
        if len(listeCombinaisons) == 0 : return None
        for IDcombi_tarif, IDtarif in listeCombinaisons :
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
        for IDcombi_tarif, IDtarif in listeCombinaisons :
            if IDcombi_tarif in dictDonnees :
                listeValeurs = []
                for dictValeurs in dictDonnees[IDcombi_tarif] :
                    listeValeurs.append([dictValeurs["IDcombi_tarif_unite"], dictValeurs["IDunite"]])
                listeDonnees.append([IDcombi_tarif, listeValeurs])
        return listeDonnees
            
    def Sauvegarde(self):
        DB = GestionDB.DB()

        listeIDcombi = []
        listeIDunites = []

        for IDcombi_tarif, listeUnites in self.listeDonnees :
            # Sauvegarde des nouvelles combinaisons
            if IDcombi_tarif == None :
                listeDonnees = [ ("IDtarif", self.IDtarif ), ("type", "JOURN" ), ]
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
        listeIDunites = self.Saisie() 
        if listeIDunites == None : return
        listeTmp = []
        for IDunite in listeIDunites :
            listeTmp.append((None, IDunite))
        self.listeDonnees.append((None, listeTmp))
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
        IDcombi_tarifTmp, listeUnites = self.listeDonnees[index]
        for IDcombi_tarif_unite, IDunite in listeUnites :
            listeAnciennesIDunites.append(IDunite)
        listeAnciennesIDunites.sort()
        # Fenêtre de saisie
        listeIDunites = self.Saisie(listeAnciennesIDunites) 
        if listeIDunites == None : return
        # Modification de la liste de données
        listeValeurs = []
        listeTemp = []
        for IDunite in listeIDunites :
            found = False
            for IDcombi_tarif_uniteTmp, IDuniteTmp in self.listeDonnees[index][1] :
                if IDuniteTmp == IDunite :
                    listeTemp.append([IDcombi_tarif_uniteTmp, IDuniteTmp])
                    found = True
            if found == False :
                listeTemp.append([None, IDunite])
        self.listeDonnees[index][1] = listeTemp
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

    def Saisie(self, listeAnciennesIDunites=None):                
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
            return None
        
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
        dlg = wx.MultiChoiceDialog(self, _(u"Cochez les unités à combiner :"), _(u"Combinaisons d'unités"), listeItems)
        if len(listeAnciennesSelections) > 0 :
            dlg.SetSelections(listeAnciennesSelections)
        if dlg.ShowModal() == wx.ID_OK :
            listeSelections = dlg.GetSelections()
            if len(listeSelections) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucune unité !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None
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
                                    return None
            dlg.Destroy()
        else:
            dlg.Destroy()
            return None
        
        # Crée une liste des IDunités sélectionnés
        listeIDunites = []
        for selection in listeSelections :
            listeIDunites.append(listeUnites[selection][0])
        listeIDunites.sort()
        
        # Si c'est une modification, vérifie qu'une modification a été faite
        if listeAnciennesIDunites != None :
            if listeAnciennesIDunites == listeIDunites :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez effectué aucune modification !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None
        
        # Vérifie que la combinaison n'existe pas déjà
        for IDcombi_tarifTmp, listeUnites in self.listeDonnees :
            listeUnitesTmp = []
            for IDcombi_tarif_uniteTmp, IDuniteTmp in listeUnites :
                listeUnitesTmp.append(IDuniteTmp)
            listeUnitesTmp.sort()
            if (listeUnitesTmp == listeIDunites)  :
                dlg = wx.MessageDialog(self, _(u"Cette combinaison existe déjà !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None
        
        return listeIDunites
        
# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Etats(wx.CheckListBox):
    def __init__(self, parent, IDactivite=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.IDactivite = IDactivite
        self.data = []
        self.Importation() 
    
    def Importation(self):
        listeEtats = [
            ("reservation", _(u"Réservation")),
            ("present", _(u"Présent")),
            ("absenti", _(u"Absence injustifiée")),
            ("absentj", _(u"Absence justifiée")),
            ("attente", _(u"Attente")),
            ("refus", _(u"Refus")),
            ]
        listeValeurs = []
        for code, label in listeEtats :
            listeValeurs.append((code, label, False)) 
        self.SetData(listeValeurs)
        
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.data = []
        index = 0
        for code, label, checked in listeValeurs:
            self.data.append((code, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches
    
    def GetTexteCoches(self):
        listeIDcoches = []
        listeTemp = self.GetIDcoches() 
        if len(listeTemp) == 0 : return ""
        for code in listeTemp :
            listeIDcoches.append(code)
        texte = ";".join(listeIDcoches)
        return texte

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index, True)
            else :
                self.Check(index, False)
            index += 1


# ----------------------------------------------------------------------------------------------------------------------------------------------------


class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None, nouveauTarif=True):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif
        self.nouveauTarif = nouveauTarif
        
        self.label_combinaisons = wx.StaticText(self, -1, _(u"Saisissez les combinaisons conditionnelles :"))
        self.ctrl_combinaisons = ListBoxCombinaisons(self, IDactivite=IDactivite, IDtarif=IDtarif)
        self.bouton_ajouter_combi = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_combi = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_combi = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))

        # Etats
        self.label_etats = wx.StaticText(self, -1, _(u"Cochez les états conditionnels :"))
        self.ctrl_etats = CTRL_Etats(self, IDactivite)
        self.ctrl_etats.SetIDcoches(("reservation", "present", "absenti"))
        self.ctrl_etats.SetMinSize((150, 120))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnAjouterCombi, self.bouton_ajouter_combi)
        self.Bind(wx.EVT_BUTTON, self.OnModifierCombi, self.bouton_modifier_combi)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerCombi, self.bouton_supprimer_combi)
        
        if self.IDtarif != None :
            self.Importation() 

    def __set_properties(self):
        self.ctrl_etats.SetToolTip(wx.ToolTip(_(u"Cochez les états de consommation associées à ce tarif")))
        self.bouton_ajouter_combi.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une combinaison d'unités")))
        self.bouton_modifier_combi.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la combinaison d'unités selectionnée dans la liste")))
        self.bouton_supprimer_combi.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la combinaison d'unités selectionnée dans la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=9, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_combinaisons, 0, 0, 0)
        
        grid_sizer_combinaisons = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_combinaisons.Add(self.ctrl_combinaisons, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons_combi = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_combi.Add(self.bouton_ajouter_combi, 0, 0, 0)
        grid_sizer_boutons_combi.Add(self.bouton_modifier_combi, 0, 0, 0)
        grid_sizer_boutons_combi.Add(self.bouton_supprimer_combi, 0, 0, 0)
        grid_sizer_combinaisons.Add(grid_sizer_boutons_combi, 1, wx.EXPAND, 0)
        
        grid_sizer_combinaisons.AddGrowableRow(0)
        grid_sizer_combinaisons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_combinaisons, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(self.label_etats, 0, 0, 0)
        grid_sizer_base.Add(self.ctrl_etats, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableRow(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)

    def OnAjouterCombi(self, event): 
        self.ctrl_combinaisons.Ajouter()

    def OnModifierCombi(self, event): 
        self.ctrl_combinaisons.Modifier() 

    def OnSupprimerCombi(self, event):
        self.ctrl_combinaisons.Supprimer() 

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT condition_nbre_combi, condition_periode, condition_nbre_jours, condition_conso_facturees, condition_dates_continues, date_facturation, etats
        FROM tarifs
        WHERE IDtarif=%d;""" % self.IDtarif
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        condition_nbre_combi, condition_periode, condition_nbre_jours, condition_conso_facturees, condition_dates_continues, date_facturation, etats = listeDonnees[0]
        if etats != None :
            self.ctrl_etats.SetIDcoches(etats)
        
    def Validation(self):
        if len(self.ctrl_combinaisons.listeDonnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Aucune combinaison conditionnelle n'a été indiquée, confirmez-vous ?"), _(u"Information"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION)
            if dlg.ShowModal() != wx.ID_YES:
                dlg.Destroy()
                return False
            else:
                dlg.Destroy()
        return True
        
    def Sauvegarde(self):
        # Sauvegarde des combinaisons
        self.ctrl_combinaisons.Sauvegarde() 
        
        # Récupération des autres données
        etats = self.ctrl_etats.GetTexteCoches() 

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
            ("date_facturation", None ),
            ("etats", etats ),
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