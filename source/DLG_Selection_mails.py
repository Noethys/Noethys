#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import GestionDB
import UTILS_Titulaires
import wx.lib.agw.hyperlink as Hyperlink

try: import psyco; psyco.full()
except: pass


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
# -------------------------------------------------------------------------------------------------------------------------------------------

class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def OnLeftLink(self, event):        
        self.UpdateLink()
        
        if self.URL == "familles_tout" : self.parent.ctrl_familles.CocheTout()
        if self.URL == "familles_rien" : self.parent.ctrl_familles.DecocheTout()
        if self.URL == "individus_tout" : self.parent.ctrl_individus.CocheTout()
        if self.URL == "individus_rien" : self.parent.ctrl_individus.DecocheTout()
        
        # Coche les présents
        if self.URL == "familles_presents" or self.URL == "individus_presents" :
            
            # Demande les périodes et les activités à sélectionner
            import DLG_Parametres_remplissage
            dictDonnees = {
                "page" : 2,
                "listeSelections" : [],
                "annee" : datetime.date.today().year,
                "dateDebut" : None,
                "dateFin" : None,
                "listePeriodes" : [],
                "listeActivites" : [],
                }
            dlg = DLG_Parametres_remplissage.Dialog(self, dictDonnees=dictDonnees, afficheLargeurColonneUnite=False, afficheAbregeGroupes=False)
            dlg.SetTitle(u"Sélection de la période et des activités")
            if dlg.ShowModal() != wx.ID_OK:
                return
            listeActivites = dlg.GetListeActivites()
            listePeriodes = dlg.GetListePeriodes()
            dlg.Destroy()
            
            # Recherche les individus présents sur cette période et ces activités
            listeIndividus = []
            listeFamilles = []
            
            conditions = self.GetSQLdates(listePeriodes)
            if len(conditions) > 0 :
                conditionDates = " AND %s" % conditions
            else:
                conditionDates = ""
                
            if len(listeActivites) == 0 : conditionActivites = "()"
            elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
            else : conditionActivites = str(tuple(listeActivites))
            
            db = GestionDB.DB()
            req = """SELECT IDconso, consommations.IDindividu, IDactivite, IDinscription, date, IDunite, IDgroupe, heure_debut, heure_fin, etat, verrouillage, date_saisie, IDutilisateur, IDcategorie_tarif, consommations.IDcompte_payeur, IDprestation, comptes_payeurs.IDfamille
            FROM consommations 
            LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
            WHERE IDactivite IN %s %s
            ORDER BY date; """ % (conditionActivites, conditionDates)
            db.ExecuterReq(req)
            listeConso = db.ResultatReq()
            for IDconso, IDindividu, IDactivite, IDinscription, date, IDunite, IDgroupe, heure_debut, heure_fin, etat, verrouillage, date_saisie, IDutilisateur, IDcategorie_tarif, IDcompte_payeur, IDprestation, IDfamille in listeConso :
                dateDD = DateEngEnDateDD(date)
                if IDindividu not in listeIndividus :
                    listeIndividus.append(IDindividu)
                if IDfamille not in listeFamilles :
                    listeFamilles.append(IDfamille)
            
            # Recherche des familles présentes
            if self.URL == "familles_presents" :
                if len(listeFamilles) == 0 :
                    dlg = wx.MessageDialog(self, u"Aucun présent n'a été trouvé !", "Erreur", wx.OK| wx.ICON_EXCLAMATION)  
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                self.parent.ctrl_familles.SetIDcoches(listeFamilles)
                listeCtrl = self.parent.ctrl_familles.GetDictInfos().keys()
                listeFamillesSansMail = []
                dictTitulaires = UTILS_Titulaires.GetTitulaires() 
                for IDfamille in listeFamilles :
                    if IDfamille not in listeCtrl :
                        nomTitulaires = dictTitulaires[IDfamille]["titulairesSansCivilite"]
                        listeFamillesSansMail.append(nomTitulaires)
                if len(listeFamillesSansMail) > 0 :
                    listeFamillesSansMail.sort()
                    txt = u"%s présents ont été trouvés mais les %d familles suivantes ne possèdent pas d'adresse mail :\n\n> " % (len(listeFamilles), len(listeFamillesSansMail))
                    txt += ", ".join(listeFamillesSansMail) + u"."
                    dlg = wx.MessageDialog(self, txt, "Remarque", wx.OK| wx.ICON_INFORMATION)  
                    dlg.ShowModal()
                    dlg.Destroy()
            
            if self.URL == "individus_presents" :
                self.parent.ctrl_individus.SetIDcoches(listeIndividus)
        
        
        
    def GetSQLdates(self, listePeriodes=[]):
        """ Avec date """
        texteSQL = ""
        for date_debut, date_fin in listePeriodes :
            texteSQL += "(date>='%s' AND date<='%s') OR " % (date_debut, date_fin)
        if len(texteSQL) > 0 :
            texteSQL = "(" + texteSQL[:-4] + ")"
        else:
            texteSQL = "date='3000-01-01'"
        return texteSQL


# ----------------------------------------------------------------------------------------------------------------------


class CTRL_diff(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.SetToolTipString(u"Cochez les listes de diffusion souhaitées")
        self.listeDiff = []
        self.dictDiff = {}
        self.dictAbonnements = {}
        
    def MAJ(self):
        self.listeDiff, self.dictDiff, self.dictAbonnements = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeDiff = []
        dictDiff = {}
        dictAbonnements = {}
        DB = GestionDB.DB()
        # Recherche les individus abonnés
        req = """SELECT IDabonnement, IDliste, abonnements.IDindividu, individus.mail
        FROM abonnements
        LEFT JOIN individus ON individus.IDindividu = abonnements.IDindividu
        WHERE individus.mail IS NOT NULL and individus.mail != ""
        ;"""
        DB.ExecuterReq(req)
        listeAbonnes = DB.ResultatReq()   
        for IDabonnement, IDliste, IDindividu, mail in listeAbonnes :
            if dictAbonnements.has_key(IDliste) == False :
                dictAbonnements[IDliste] = []
            dictAbonnements[IDliste].append(mail)
        # Recherche les listes de diffusion
        req = """SELECT IDliste, nom
        FROM listes_diffusion
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeListes = DB.ResultatReq()   
        DB.Close() 
        for IDliste, nom in listeListes :
            dictDiff[IDliste] = nom
            if dictAbonnements.has_key(IDliste) :
                txtAbonnements = u"(%d abonnés)" % len(dictAbonnements[IDliste])
            else:
                txtAbonnements = u"(Aucun abonné)"
            label = u"%s %s" % (nom, txtAbonnements)
            listeDiff.append((label, IDliste))
        listeDiff.sort()
        
        return listeDiff, dictDiff, dictAbonnements

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDliste in self.listeDiff :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeDiff)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeDiff[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeDiff)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeDiff)):
            ID = self.listeDiff[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
        
    def GetDictDiff(self):
        return self.dictDiff
    
    def GetDictAbonnements(self):
        return self.dictAbonnements

# -------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Individus(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.SetToolTipString(u"Cochez les individus souhaités")
        self.liste = []
        self.dictInfos = {}
        
    def MAJ(self):
        self.liste, self.dictInfos = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeTemp = []
        dictTemp = {}
        DB = GestionDB.DB()
        req = """SELECT IDindividu, nom, prenom, mail
        FROM individus
        WHERE mail<>"" and mail IS NOT NULL
        ORDER BY nom, prenom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDindividu, nom, prenom, mail in listeDonnees :
            dictTemp[IDindividu] = {"nom":nom, "prenom":prenom, "mail":mail}
            label = u"%s %s -> %s" % (nom, prenom, mail)
            listeTemp.append((label, IDindividu))
        listeTemp.sort()
        return listeTemp, dictTemp

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for label, IDindividu in self.liste :
            self.Append(label)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.liste)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.liste[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.liste)):
            self.Check(index)
            index += 1

    def DecocheTout(self):
        index = 0
        for index in range(0, len(self.liste)):
            self.Check(index, False)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.liste)):
            ID = self.liste[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
        
    def GetDictInfos(self):
        return self.dictInfos
    
# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Familles(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.SetToolTipString(u"Cochez les familles souhaitées")
        self.liste = []
        self.dictInfos = {}
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        
    def MAJ(self):
        self.liste, self.dictInfos = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeTemp = []
        dictTemp = {}
        DB = GestionDB.DB()
        req = """SELECT IDfamille, IDcompte_payeur
        FROM familles
        ORDER BY IDfamille;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDfamille, IDcompte_payeur in listeDonnees :
            # Recherche des noms des titulaires
            nomsTitulaires = self.dictTitulaires[IDfamille]["titulairesSansCivilite"]
            
            # Recherche de l'adresse mail principale
            listeTitulaires = self.dictTitulaires[IDfamille]["listeTitulaires"]
            listeMails = []
            for dictIndividu in listeTitulaires :
                mail = dictIndividu["mail"]
                if mail != "" and mail != None : 
                    listeMails.append(mail)
            if len(listeMails) > 0 :
                mail = listeMails[0]
            else :
                mail = u""
                
            # On ne conserve que les familles qui ont une adresse mail
            if mail != u"" :
                dictTemp[IDfamille] = {"nomsTitulaires":nomsTitulaires, "mail":mail}
                label = u"%s -> %s" % (nomsTitulaires, mail)
                listeTemp.append((label, IDfamille))
                
        listeTemp.sort()
        return listeTemp, dictTemp

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for label, IDfamille in self.liste :
            self.Append(label)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.liste)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.liste[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.liste)):
            self.Check(index)
            index += 1
            
    def DecocheTout(self):
        index = 0
        for index in range(0, len(self.liste)):
            self.Check(index, False)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.liste)):
            ID = self.liste[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
        
    def GetDictInfos(self):
        return self.dictInfos
    
    
# ----------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, 
            valeurs_manuel = u"",
            valeurs_diff = [],
            valeurs_familles = [],
            valeurs_individus = []):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        
        self.valeurs_manuel = valeurs_manuel
        self.valeurs_diff = valeurs_diff
        self.valeurs_familles = valeurs_familles
        self.valeurs_individus = valeurs_individus
        self.listeMails = []
        
        # Manuel
        self.checkbox_manuel = wx.CheckBox(self, -1, u"")
        self.label_manuel = wx.StaticText(self, -1, u"Les adresses mails suivantes :")
        self.ctrl_manuel = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        # Listes de diffusion
        self.checkbox_diff = wx.CheckBox(self, -1, u"")
        self.label_diff = wx.StaticText(self, -1, u"Les abonnés aux listes de diffusion sélectionnées :")
        self.ctrl_diff = CTRL_diff(self)
        self.ctrl_diff.MAJ() 
        
        # Familles
        self.checkbox_familles = wx.CheckBox(self, -1, u"")
        self.label_familles = wx.StaticText(self, -1, u"Les familles sélectionnées :")
        self.ctrl_familles = CTRL_Familles(self)
        self.ctrl_familles.MAJ() 
        self.ctrl_familles_presents = Hyperlien(self, label=u"Sélectionner les présents", infobulle=u"Cliquez ici pour sélectionner les familles dont les membres sont présents sur une période donnée", URL="familles_presents")
        self.label_barre_1 = wx.StaticText(self, -1, u" | ")
        self.ctrl_familles_tout = Hyperlien(self, label=u"Tout sélectionner", infobulle=u"Cliquez ici pour tout sélectionner", URL="familles_tout")
        self.label_barre_2 = wx.StaticText(self, -1, u" | ")
        self.ctrl_familles_rien = Hyperlien(self, label=u"Tout désélectionner", infobulle=u"Cliquez ici pour tout désélectionner", URL="familles_rien")
        
        # Individus
        self.checkbox_individus = wx.CheckBox(self, -1, u"")
        self.label_individus = wx.StaticText(self, -1, u"Les individus sélectionnés :")
        self.ctrl_individus = CTRL_Individus(self)
        self.ctrl_individus.MAJ() 
        self.ctrl_individus_presents = Hyperlien(self, label=u"Sélectionner les présents", infobulle=u"Cliquez ici pour sélectionner les individus présents sur une période donnée", URL="individus_presents")
        self.label_barre_3 = wx.StaticText(self, -1, u" | ")
        self.ctrl_individus_tout = Hyperlien(self, label=u"Tout sélectionner", infobulle=u"Cliquez ici pour tout sélectionner", URL="individus_tout")
        self.label_barre_4 = wx.StaticText(self, -1, u" | ")
        self.ctrl_individus_rien = Hyperlien(self, label=u"Tout désélectionner", infobulle=u"Cliquez ici pour tout désélectionner", URL="individus_rien")
        
        # Commandes
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckManuel, self.checkbox_manuel)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDiff, self.checkbox_diff)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckFamilles, self.checkbox_familles)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckIndividus, self.checkbox_individus)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Init Contrôles
        if len(self.valeurs_manuel) > 0 :
            self.ctrl_manuel.SetValue(self.valeurs_manuel)
            self.checkbox_manuel.SetValue(True)
        if len(self.valeurs_diff) > 0 :
            self.ctrl_diff.SetIDcoches(self.valeurs_diff)
            self.checkbox_diff.SetValue(True)
        if len(self.valeurs_familles) > 0 :
            self.ctrl_familles.SetIDcoches(self.valeurs_familles) 
            self.checkbox_familles.SetValue(True)
        if len(self.valeurs_individus) > 0 :
            self.ctrl_individus.SetIDcoches(self.valeurs_individus)
            self.checkbox_individus.SetValue(True)

        self.OnCheckManuel(None) 
        self.OnCheckDiff(None) 
        self.OnCheckFamilles(None) 
        self.OnCheckIndividus(None) 
        
    def __set_properties(self):
        self.SetTitle(u"Sélection des destinataires")
        self.ctrl_manuel.SetToolTipString(u"Vous pouvez saisir les adresses mails ici en les séparant d'un point-virgule")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((850, 670))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=5, cols=4, vgap=0, hgap=0)
        grid_sizer_contenu.Add(self.checkbox_manuel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_contenu.Add(self.label_manuel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.checkbox_diff, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_contenu.Add(self.label_diff, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_manuel, 0, wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_contenu.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_diff, 0, wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_contenu.Add(self.checkbox_familles, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_contenu.Add(self.label_familles, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.checkbox_individus, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_contenu.Add(self.label_individus, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_familles, 0, wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_contenu.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_individus, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add((10, 10), 0, wx.EXPAND, 0)
        
        grid_sizer_familles_options = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        grid_sizer_familles_options.Add(self.ctrl_familles_presents, 0, wx.EXPAND, 0)
        grid_sizer_familles_options.Add(self.label_barre_1, 0, wx.EXPAND, 0)
        grid_sizer_familles_options.Add(self.ctrl_familles_tout, 0, wx.EXPAND, 0)
        grid_sizer_familles_options.Add(self.label_barre_2, 0, wx.EXPAND, 0)
        grid_sizer_familles_options.Add(self.ctrl_familles_rien, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(grid_sizer_familles_options, 0, wx.RIGHT|wx.ALIGN_RIGHT, 8)
        
        grid_sizer_contenu.Add((10, 10), 0, wx.EXPAND, 0)
        
        grid_sizer_individus_options = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        grid_sizer_individus_options.Add(self.ctrl_individus_presents, 0, wx.EXPAND, 0)
        grid_sizer_individus_options.Add(self.label_barre_3, 0, wx.EXPAND, 0)
        grid_sizer_individus_options.Add(self.ctrl_individus_tout, 0, wx.EXPAND, 0)
        grid_sizer_individus_options.Add(self.label_barre_4, 0, wx.EXPAND, 0)
        grid_sizer_individus_options.Add(self.ctrl_individus_rien, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(grid_sizer_individus_options, 0, wx.RIGHT|wx.ALIGN_RIGHT, 8)

        grid_sizer_contenu.AddGrowableRow(3)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_contenu.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base
        self.CenterOnScreen() 

    def OnCheckManuel(self, event): 
        if self.checkbox_manuel.GetValue() == True :
            self.ctrl_manuel.Enable(True)
        else:
            self.ctrl_manuel.Enable(False)

    def OnCheckDiff(self, event): 
        if self.checkbox_diff.GetValue() == True :
            self.ctrl_diff.Enable(True)
        else:
            self.ctrl_diff.Enable(False)

    def OnCheckFamilles(self, event): 
        if self.checkbox_familles.GetValue() == True :
            self.ctrl_familles.Enable(True)
            self.ctrl_familles_presents.Enable(True)
            self.ctrl_familles_tout.Enable(True)
            self.ctrl_familles_rien.Enable(True)
            self.label_barre_1.Enable(True)
            self.label_barre_2.Enable(True)
        else:
            self.ctrl_familles.Enable(False)
            self.ctrl_familles_presents.Enable(False)
            self.ctrl_familles_tout.Enable(False)
            self.ctrl_familles_rien.Enable(False)
            self.label_barre_1.Enable(False)
            self.label_barre_2.Enable(False)

    def OnCheckIndividus(self, event): 
        if self.checkbox_individus.GetValue() == True :
            self.ctrl_individus.Enable(True)
            self.ctrl_individus_presents.Enable(True)
            self.ctrl_individus_tout.Enable(True)
            self.ctrl_individus_rien.Enable(True)
            self.label_barre_3.Enable(True)
            self.label_barre_4.Enable(True)
        else:
            self.ctrl_individus.Enable(False)
            self.ctrl_individus_presents.Enable(False)
            self.ctrl_individus_tout.Enable(False)
            self.ctrl_individus_rien.Enable(False)
            self.label_barre_3.Enable(False)
            self.label_barre_4.Enable(False)
            
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("EditeurdEmails")

    def OnBoutonOk(self, event): 
        listeMails = []
        
        def AjouterListe(liste=[]):
            for ID in liste :
                if ID not in listeMails :
                    listeMails.append(ID)
            
        # Récupération de la liste manuelle
        if self.checkbox_manuel.GetValue() == True :
            valeurs_manuel = self.ctrl_manuel.GetValue()
            if len(valeurs_manuel) > 0 :
                listeTemp = valeurs_manuel.split(";")
                AjouterListe(listeTemp)
        else:
            valeurs_manuel = u""
        
        # Récupération de la liste des abonnés aux listes de diffusion
        if self.checkbox_diff.GetValue() == True :
            valeurs_diff = self.ctrl_diff.GetIDcoches()
            dictAbonnements = self.ctrl_diff.GetDictAbonnements()
            for IDliste in valeurs_diff :
                if dictAbonnements.has_key(IDliste):
                    listeAbonnes = dictAbonnements[IDliste]
                    AjouterListe(listeAbonnes)
        else:
            valeurs_diff = []
        
        # Récupération de la liste des familles
        if self.checkbox_familles.GetValue() == True :
            valeurs_familles = self.ctrl_familles.GetIDcoches()
            dictInfos = self.ctrl_familles.GetDictInfos()
            listeTemp = []
            for IDfamille in valeurs_familles :
                mail = dictInfos[IDfamille]["mail"]
                listeTemp.append(mail)
            AjouterListe(listeTemp)
        else:
            valeurs_familles = []

        # Récupération de la liste des individus
        if self.checkbox_individus.GetValue() == True :
            valeurs_individus = self.ctrl_individus.GetIDcoches()
            dictInfos = self.ctrl_individus.GetDictInfos()
            listeTemp = []
            for IDindividu in valeurs_individus :
                mail = dictInfos[IDindividu]["mail"]
                listeTemp.append(mail)
            AjouterListe(listeTemp)
        else:
            valeurs_individus = []
            
        # Prépare la liste finale des mails retenus
        self.valeurs_manuel = valeurs_manuel
        self.valeurs_diff = valeurs_diff
        self.valeurs_familles = valeurs_familles
        self.valeurs_individus = valeurs_individus
        
        listeMails.sort()
        self.listeMails = listeMails
        
        # Ferme la fenêtre
        self.EndModal(wx.ID_OK)

    def GetValeurs(self):
        return self.valeurs_manuel, self.valeurs_diff, self.valeurs_familles, self.valeurs_individus
    
    def GetListeMails(self):
        return self.listeMails
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
