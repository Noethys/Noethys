#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB


LISTE_PERIODES = [
    ( "1jour", _(u"1 journ�e")),
    ( "1semaine", _(u"1 semaine")),
    ( "1mois", _(u"1 mois")),
    ( "1annee", _(u"1 ann�e")),
    ( "perso", _(u"Personnalis�e")),
]


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
        # Recherche des unit�s disponibles de l'activit�
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
        # Importation des unit�s des combinaisons
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
            if dictDonnees.has_key(IDcombi_tarif) :
                dictDonnees[IDcombi_tarif].append(dictTemp)
            else:
                dictDonnees[IDcombi_tarif] = [dictTemp,]
        # Cr�ation de la liste des donn�es
        listeDonnees = []
        for IDcombi_tarif, IDtarif in listeCombinaisons :
            if dictDonnees.has_key(IDcombi_tarif) :
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
            
            # Sauvegarde des unit�s de combi
            for IDcombi_tarif_unite, IDunite in listeUnites :
                
                # Nouvelles unit�s
                if IDcombi_tarif_unite == None :
                    listeDonnees = [ ("IDcombi_tarif", IDcombi_tarif ), ("IDtarif", self.IDtarif ), ("IDunite", IDunite ), ]
                    IDcombi_tarif_unite = DB.ReqInsert("combi_tarifs_unites", listeDonnees)
                else:
                    listeIDunites.append(IDcombi_tarif_unite)
        
        # Suppression des combi supprim�es
        for IDcombi_tarif in self.listeAnciennesCombi :
            if IDcombi_tarif not in listeIDcombi :
                DB.ReqDEL("combi_tarifs", "IDcombi_tarif", IDcombi_tarif)
            
        # Suppression des unit�s supprim�es
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
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune combinaison � modifier dans la liste !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDcombi_tarif = self.GetClientData(index)
        # R�cup�ration des anciennes IDunites
        listeAnciennesIDunites = []
        IDcombi_tarifTmp, listeUnites = self.listeDonnees[index]
        for IDcombi_tarif_unite, IDunite in listeUnites :
            listeAnciennesIDunites.append(IDunite)
        listeAnciennesIDunites.sort()
        # Fen�tre de saisie
        listeIDunites = self.Saisie(listeAnciennesIDunites) 
        if listeIDunites == None : return
        # Modification de la liste de donn�es
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
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune combinaison � supprimer dans la liste !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
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
        # Recherche des unit�s disponibles de l'activit�
        db = GestionDB.DB()
        req = """SELECT IDunite, nom, type, heure_debut, heure_fin, date_debut, date_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        db.ExecuterReq(req)
        listeUnites = db.ResultatReq()
        db.Close()
        if len(listeUnites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'existe aucune unit� pour cette activit� !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
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
            
        # Bo�te de dialogue pour choisir les combinaisons
        dlg = wx.MultiChoiceDialog(self, _(u"Cochez les unit�s � combiner :"), _(u"Combinaisons d'unit�s"), listeItems)
        if len(listeAnciennesSelections) > 0 :
            dlg.SetSelections(listeAnciennesSelections)
        if dlg.ShowModal() == wx.ID_OK :
            listeSelections = dlg.GetSelections()
            if len(listeSelections) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez coch� aucune unit� !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None
            # V�rifie que les unit�s s�lectionn�es sont compatibles entre elles
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
                                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas cr�er cette combinaison car les\nunit�s '%s' et '%s' sont incompatibles entre elles !") % (nomUnite1, nomUnite2), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                                    dlg.ShowModal()
                                    dlg.Destroy()
                                    return None
            dlg.Destroy()
        else:
            dlg.Destroy()
            return None
        
        # Cr�e une liste des IDunit�s s�lectionn�s
        listeIDunites = []
        for selection in listeSelections :
            listeIDunites.append(listeUnites[selection][0])
        listeIDunites.sort()
        
        # Si c'est une modification, v�rifie qu'une modification a �t� faite
        if listeAnciennesIDunites != None :
            if listeAnciennesIDunites == listeIDunites :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez effectu� aucune modification !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None
        
        # V�rifie que la combinaison n'existe pas d�j�
        for IDcombi_tarifTmp, listeUnites in self.listeDonnees :
            listeUnitesTmp = []
            for IDcombi_tarif_uniteTmp, IDuniteTmp in listeUnites :
                listeUnitesTmp.append(IDuniteTmp)
            listeUnitesTmp.sort()
            if (listeUnitesTmp == listeIDunites)  :
                dlg = wx.MessageDialog(self, _(u"Cette combinaison existe d�j� !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return None
        
        return listeIDunites
        
# -----------------------------------------------------------------------------------------------------------------------



class Panel(wx.Panel):
    def __init__(self, parent, IDactivite=None, IDtarif=None, nouveauTarif=True):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif
        self.nouveauTarif = nouveauTarif
        
        self.label_intro = wx.StaticText(self, -1, _(u"Saisissez les combinaisons conditionnelles :"))
        self.ctrl_nbre = wx.SpinCtrl(self, -1, u"1", min=1, max=100)
        self.label_ctrl = wx.StaticText(self, -1, _(u"des combinaisons d'unit�s suivantes :"))
        self.ctrl_combinaisons = ListBoxCombinaisons(self, IDactivite=IDactivite, IDtarif=IDtarif)
        self.bouton_ajouter_combi = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_combi = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_combi = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.ctrl_non_facturees = wx.CheckBox(self, -1, _(u"Les consommations peuvent d�j� avoir �t� factur�es"))
        self.label_periode = wx.StaticText(self, -1, _(u"Sur la p�riode suivante :"))
        periodes = []
        for code, label in LISTE_PERIODES :
            periodes.append(label)
        self.ctrl_periode = wx.Choice(self, -1, choices=periodes)
        self.ctrl_jours = wx.SpinCtrl(self, -1, u"", min=0, max=365)
        self.label_jours = wx.StaticText(self, -1, _(u"jours"))
        self.ctrl_dates_continues = wx.CheckBox(self, -1, _(u"Les dates doivent �tre continues"))
        
        # D�sactive temporairement les contr�els inutilis�es
        self.ctrl_nbre.Show(False)
        self.label_ctrl.Show(False)
        self.ctrl_non_facturees.Show(False)
        self.label_periode.Show(False)
        self.ctrl_periode.Show(False)
        self.ctrl_jours.Show(False)
        self.label_jours.Show(False)
        self.ctrl_dates_continues.Show(False)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnAjouterCombi, self.bouton_ajouter_combi)
        self.Bind(wx.EVT_BUTTON, self.OnModifierCombi, self.bouton_modifier_combi)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerCombi, self.bouton_supprimer_combi)
        self.Bind(wx.EVT_CHOICE, self.OnChoixPeriode, self.ctrl_periode)
        
        if self.IDtarif != None :
            self.Importation() 
            
        self.OnChoixPeriode(None)

    def __set_properties(self):
##        self.label_intro.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, 1, ""))
        self.label_periode.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, 1, ""))
        self.ctrl_nbre.SetMinSize((55, -1))
        self.bouton_ajouter_combi.SetToolTipString(_(u"Cliquez ici pour ajouter une combinaison d'unit�s"))
        self.bouton_modifier_combi.SetToolTipString(_(u"Cliquez ici pour modifier la combinaison d'unit�s selectionn�e dans la liste"))
        self.bouton_supprimer_combi.SetToolTipString(_(u"Cliquez ici pour supprimer la combinaison d'unit�s selectionn�e dans la liste"))
        self.ctrl_periode.SetSelection(0)
        self.ctrl_jours.SetMinSize((55, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=9, cols=1, vgap=5, hgap=5)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_combinaisons = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_combi = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_nbre = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_intro, 0, 0, 0)
        grid_sizer_nbre.Add(self.ctrl_nbre, 0, 0, 0)
        grid_sizer_nbre.Add(self.label_ctrl, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_nbre, 1, wx.EXPAND, 0)
        grid_sizer_combinaisons.Add(self.ctrl_combinaisons, 1, wx.EXPAND, 0)
        grid_sizer_boutons_combi.Add(self.bouton_ajouter_combi, 0, 0, 0)
        grid_sizer_boutons_combi.Add(self.bouton_modifier_combi, 0, 0, 0)
        grid_sizer_boutons_combi.Add(self.bouton_supprimer_combi, 0, 0, 0)
        grid_sizer_combinaisons.Add(grid_sizer_boutons_combi, 1, wx.EXPAND, 0)
        grid_sizer_combinaisons.AddGrowableRow(0)
        grid_sizer_combinaisons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_combinaisons, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_non_facturees, 0, 0, 0)
        grid_sizer_base.Add(self.label_periode, 0, 0, 0)
        grid_sizer_periode.Add(self.ctrl_periode, 0, 0, 0)
        grid_sizer_periode.Add(self.ctrl_jours, 0, 0, 0)
        grid_sizer_periode.Add(self.label_jours, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_periode, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_dates_continues, 0, 0, 0)
        grid_sizer_base.AddGrowableRow(2)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)

    def OnAjouterCombi(self, event): 
        self.ctrl_combinaisons.Ajouter()

    def OnModifierCombi(self, event): 
        self.ctrl_combinaisons.Modifier() 

    def OnSupprimerCombi(self, event):
        self.ctrl_combinaisons.Supprimer() 

    def OnChoixPeriode(self, event):
        if self.ctrl_periode.GetStringSelection() == _(u"Personnalis�e") :
            self.ctrl_jours.Enable(True)
            self.label_jours.Enable(True)
            self.ctrl_combinaisons.Sauvegarde()
        else:
            self.ctrl_jours.Enable(False)
            self.label_jours.Enable(False)

    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT condition_nbre_combi, condition_periode, condition_nbre_jours, condition_conso_facturees, condition_dates_continues, date_facturation
        FROM tarifs
        WHERE IDtarif=%d;""" % self.IDtarif
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        condition_nbre_combi, condition_periode, condition_nbre_jours, condition_conso_facturees, condition_dates_continues, date_facturation = listeDonnees[0]
        # Remplissage des contr�les
        if condition_nbre_combi != None : self.ctrl_nbre.SetValue(condition_nbre_combi)
        index = 0
        for code, label in LISTE_PERIODES :
            if code == condition_periode :
                self.ctrl_periode.SetSelection(index)
            index += 1
        if condition_nbre_jours != None : self.ctrl_jours.SetValue(condition_nbre_jours)
        if condition_conso_facturees != None : self.ctrl_non_facturees.SetValue(condition_conso_facturees)
        if condition_dates_continues != None : self.ctrl_dates_continues.SetValue(condition_dates_continues)
        
    def Validation(self):
        return True
        
    def Sauvegarde(self):
        # Sauvegarde des combinaisons
        self.ctrl_combinaisons.Sauvegarde() 
        
        # R�cup�ration des autres donn�es
        condition_nbre_combi = int(self.ctrl_nbre.GetValue())
        condition_periode = LISTE_PERIODES[self.ctrl_periode.GetSelection()][0]
        if condition_periode == "perso" :
            condition_nbre_jours = int(self.ctrl_jours.GetValue())
        else:
            condition_nbre_jours = 0
        condition_conso_facturees = int(self.ctrl_non_facturees.GetValue())
        condition_dates_continues = int(self.ctrl_dates_continues.GetValue())
        
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
            ("condition_nbre_combi", condition_nbre_combi ),
            ("condition_periode", condition_periode ), 
            ("condition_nbre_jours", condition_nbre_jours ), 
            ("condition_conso_facturees", condition_conso_facturees ), 
            ("condition_dates_continues", condition_dates_continues ), 
            ("date_facturation", None ),
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