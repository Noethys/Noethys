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
import FonctionsPerso

import CTRL_Saisie_adresse
import CTRL_Saisie_tel
import CTRL_Saisie_mail

import UTILS_Utilisateurs




class Adresse_auto(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.SetToolTipString(_(u"Sélectionnez ici un représentant de la famille.\n(Les individus sans adresse n'apparaissent pas)"))
    
    def MAJ(self, DB=None):
        if self.parent.IDindividu != None :
            listeItems = self.GetListeDonnees(DB)
            self.SetItems(listeItems)
        if len(listeItems) > 0 :
            self.Select(0)
    
    def GetNbreItems(self):
        return self.GetCount()
    
    def GetListeDonnees(self, DB=None):
        # Recherche des familles rattachées de l'individu
        req = """SELECT IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire
        FROM rattachements
        WHERE IDindividu=%d;""" % self.parent.IDindividu
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeFamilles = []
        for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire in listeDonnees :
            listeFamilles.append(IDfamille)
        if len(listeFamilles) == 0 :
            self.dictDonnees = {}
            return []
        elif len(listeFamilles) == 1 :
            condition = "(%s)" % listeFamilles[0]
        else :
            condition = str(tuple(listeFamilles))
        # Recherche des représentants des familles rattachées
        req = """SELECT individus.IDindividu, individus.nom, individus.prenom, rue_resid, cp_resid, ville_resid, tel_domicile
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE IDfamille IN %s;""" % condition # J'ai enlevé ici "IDcategorie=1 AND " pour afficher également les contacts
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictDonnees = {}
        listeNoms = []
        index = 0
        for IDindividu, nom, prenom, rue, cp, ville, tel_domicile in listeDonnees :
            if IDindividu != self.parent.IDindividu :
                if rue != "" and cp != "" and ville != "" :
                    nomComplet = u"%s %s" % (nom, prenom)
                    listeNoms.append(nomComplet)
                    self.dictDonnees[index] =  {"ID" : IDindividu, "rue" : rue, "cp" : cp, "ville" : ville, "tel_domicile" : tel_domicile }
                    index += 1
        return listeNoms

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetDonnee(self):
        """ return l'IDindividu sélectionné SI radio_adresse_auto est TRUE sinon renvoie None """
        if self.parent.radio_adresse_auto.GetValue() == True :
            return self.GetID()
        else:
            return None


class Categorie(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.SetToolTipString(_(u"Sélectionnez la catégorie socio-professionnelle de l'individu"))
    
    def MAJ(self, DB=None):
        choices = self.GetListeDonnees(DB)
        self.SetItems(choices)
        
    def GetListeDonnees(self, DB=None):
        req = """SELECT IDcategorie, nom FROM categories_travail ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictDonnees = {}
        listeNoms = []
        index = 0
        for IDcategorie, nom in listeDonnees :
            listeNoms.append(nom)
            self.dictDonnees[index] = (IDcategorie, nom)
            index += 1
        return listeNoms

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values[0] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index][0]
    
# ---------------------------------------------------------------------------------------------------------------------------

class Secteur(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, choices=[]) 
        self.parent = parent
        self.SetToolTipString(_(u"Sélectionnez le secteur géographique du lieu de résidence de l'individu"))
    
    def MAJ(self, DB=None):
        listeItems = self.GetListeDonnees(DB)
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)

    def GetListeDonnees(self, DB=None):
        req = """SELECT IDsecteur, nom FROM secteurs ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictDonnees = { 0 : (None, _(u"--- Aucun secteur géographique ---")) }
        listeNoms = [ _(u"------ Aucun secteur géographique ------")]
        index = 1
        for IDsecteur, nom in listeDonnees :
            listeNoms.append(nom)
            self.dictDonnees[index] = (IDsecteur, nom)
            index += 1
        return listeNoms

    def SetID(self, ID=0):
        if ID == None : return
        for index, values in self.dictDonnees.iteritems():
            if values[0] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        if index == 0 : return None
        return self.dictDonnees[index][0]

# -------------------------------------------------------------------------------------------------------------------------

class CTRL_diff(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.SetToolTipString(_(u"Cochez les listes de diffusion souhaitées"))
        self.listeDiff = []
        self.dictDiff = {}
        
    def MAJ(self, DB=None):
        self.listeDiff, self.dictDiff = self.Importation(DB)
        self.SetListeChoix()
    
    def Importation(self, DB=None):
        listeDiff = []
        dictDiff = {}
        # Recherche les listes de diffusion
        req = """SELECT IDliste, nom
        FROM listes_diffusion
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeListes = DB.ResultatReq()   
        for IDliste, nom in listeListes :
            dictDiff[IDliste] = nom
            listeDiff.append((nom, IDliste))
        listeDiff.sort()
        
        return listeDiff, dictDiff

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
    
# -------------------------------------------------------------------------------------------------------------------------------------------


class Panel_coords(wx.Panel):
    def __init__(self, parent, IDindividu=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_coords", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDindividu = IDindividu
        
        self.cp = None
        self.ville = None
        
        self.majEffectuee = False
                
        # Adresse
        self.staticbox_adresse = wx.StaticBox(self, -1, _(u"Adresse de résidence"))
        self.radio_adresse_auto = wx.RadioButton(self, -1, "", style=wx.RB_GROUP)
        self.label_adresse_auto = wx.StaticText(self, -1, _(u"L'adresse de :"))
        self.ctrl_adresse_auto = Adresse_auto(self)
        self.radio_adresse_manuelle = wx.RadioButton(self, -1, "")
        self.label_adresse_manuelle = wx.StaticText(self, -1, _(u"L'adresse suivante :"))
        self.label_rue = wx.StaticText(self, -1, _(u"Rue :"))
        self.ctrl_rue = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.label_cp = wx.StaticText(self, -1, _(u"CP :"))
        self.ctrl_ville = CTRL_Saisie_adresse.Adresse(self)
        self.label_secteur = wx.StaticText(self, -1, _(u"Secteur :"))
        self.ctrl_secteur = Secteur(self)
        self.bouton_secteurs = wx.Button(self, -1, "...", size=(20, 20))

        # Coordonnées
        self.staticbox_coords = wx.StaticBox(self, -1, _(u"Coordonnées"))
        self.label_tel_domicile = wx.StaticText(self, -1, _(u"Domicile :"))
        self.ctrl_tel_domicile = CTRL_Saisie_tel.Tel(self, intitule=_(u"Domicile"))
        self.label_tel_mobile = wx.StaticText(self, -1, _(u"Mobile :"))
        self.ctrl_tel_mobile = CTRL_Saisie_tel.Tel(self, intitule=_(u"mobile"))
        self.label_tel_fax = wx.StaticText(self, -1, _(u"Fax :"))
        self.ctrl_tel_fax = CTRL_Saisie_tel.Tel(self, intitule=_(u"fax"))
        self.label_mail = wx.StaticText(self, -1, _(u"Email :"))
        self.ctrl_mail = CTRL_Saisie_mail.Mail(self)
        self.bouton_mail_perso = wx.BitmapButton(self, 900, wx.Bitmap("Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_ANY))

        # Activité professionnelle
        self.staticbox_travail = wx.StaticBox(self, -1, _(u"Activité professionnelle"))
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = Categorie(self)
        self.label_travail_tel = wx.StaticText(self, -1, _(u"Tél :"))
        self.ctrl_travail_tel = CTRL_Saisie_tel.Tel(self, intitule=_(u"travail"))
        self.label_profession = wx.StaticText(self, -1, _(u"Profession :"))
        self.ctrl_profession = wx.TextCtrl(self, -1, "")
        self.label_travail_fax = wx.StaticText(self, -1, _(u"Fax :"))
        self.ctrl_travail_fax = CTRL_Saisie_tel.Tel(self, intitule=_(u"fax"))
        self.label_employeur = wx.StaticText(self, -1, _(u"Employeur :"))
        self.ctrl_employeur = wx.TextCtrl(self, -1, "")
        self.label_travail_mail = wx.StaticText(self, -1, _(u"Mail :"))
        self.ctrl_travail_mail = CTRL_Saisie_mail.Mail(self)
        self.bouton_mail_travail = wx.BitmapButton(self, 800, wx.Bitmap("Images/16x16/Emails_exp.png", wx.BITMAP_TYPE_ANY))
                
        # Listes de diffusion
        self.staticbox_listesdiff = wx.StaticBox(self, -1, _(u"Listes de diffusion"))
        self.label_listesdiff = wx.StaticText(self, -1, _(u"Inscrire aux listes suivantes :"))
        self.ctrl_listesdiff = CTRL_diff(self)

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAdresse, self.radio_adresse_auto )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAdresse, self.radio_adresse_manuelle )
        self.Bind(wx.EVT_BUTTON, self.OnGestionSecteurs, self.bouton_secteurs)
        self.Bind(wx.EVT_BUTTON, self.OnEnvoiEmail, self.bouton_mail_travail)
        self.Bind(wx.EVT_BUTTON, self.OnEnvoiEmail, self.bouton_mail_perso)
        
        self.ctrl_adresse_auto.Bind(wx.EVT_CHOICE, self.OnTextAdresse)
        self.ctrl_rue.Bind(wx.EVT_TEXT, self.OnTextAdresse)
        self.ctrl_ville.ctrl_cp.Bind(wx.EVT_TEXT, self.OnTextAdresse)
        self.ctrl_ville.ctrl_ville.Bind(wx.EVT_TEXT, self.OnTextAdresse)
        
        if self.ctrl_adresse_auto.GetNbreItems() == 0 :
            self.ctrl_adresse_auto.Enable(False)
            self.radio_adresse_auto.Enable(False)
            self.radio_adresse_manuelle.SetValue(True)
        
        self.OnRadioAdresse(None)
        
                

    def __set_properties(self):
        self.radio_adresse_auto.SetToolTipString(_(u"Cliquez ici pour utiliser l'adresse d'un autre membre de la famille"))
        self.radio_adresse_manuelle.SetToolTipString(_(u"Cliquez ici pour saisir manuellement une adresse"))
        self.ctrl_rue.SetToolTipString(_(u"Saisissez la rue de l'adresse"))
        self.ctrl_profession.SetToolTipString(_(u"Saisissez la profession de l'individu"))
        self.ctrl_employeur.SetToolTipString(_(u"Saisissez le nom de l'employeur de l'individu"))
        self.bouton_secteurs.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des secteurs"))
        self.bouton_mail_travail.SetToolTipString(_(u"Cliquez ici pour envoyer un email à cette adresse internet"))
        self.bouton_mail_perso.SetToolTipString(_(u"Cliquez ici pour envoyer un email à cette adresse internet"))

    def __do_layout(self):
        grid_sizer_base0 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        staticbox_listesdiff = wx.StaticBoxSizer(self.staticbox_listesdiff, wx.VERTICAL)
        grid_sizer_listesdiff = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        staticbox_coords = wx.StaticBoxSizer(self.staticbox_coords, wx.VERTICAL)
        grid_sizer_coords = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        staticbox_travail = wx.StaticBoxSizer(self.staticbox_travail, wx.VERTICAL)
        grid_sizer_travail = wx.FlexGridSizer(rows=3, cols=4, vgap=5, hgap=5)
        staticbox_adresse = wx.StaticBoxSizer(self.staticbox_adresse, wx.VERTICAL)
        grid_sizer_adresse = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_adresse_manuelle = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_adresse_manuelle_2 = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        grid_sizer_adresse_auto = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_adresse.Add(self.radio_adresse_auto, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse_auto.Add(self.label_adresse_auto, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse_auto.Add(self.ctrl_adresse_auto, 0, wx.EXPAND, 0)
        grid_sizer_adresse_auto.AddGrowableCol(1)
        grid_sizer_adresse.Add(grid_sizer_adresse_auto, 1, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.radio_adresse_manuelle, 0, 0, 0)
        grid_sizer_adresse_manuelle.Add(self.label_adresse_manuelle, 0, 0, 0)
        grid_sizer_adresse_manuelle_2.Add(self.label_rue, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse_manuelle_2.Add(self.ctrl_rue, 0, wx.EXPAND, 0)
        grid_sizer_adresse_manuelle_2.Add(self.label_cp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse_manuelle_2.Add(self.ctrl_ville, 0, wx.EXPAND, 0)
        grid_sizer_adresse_manuelle_2.Add(self.label_secteur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_secteur = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_secteur.Add(self.ctrl_secteur, 0, wx.EXPAND, 0)
        grid_sizer_secteur.Add(self.bouton_secteurs, 0, wx.EXPAND, 0)
        grid_sizer_secteur.AddGrowableCol(0)
        grid_sizer_adresse_manuelle_2.Add(grid_sizer_secteur, 0, wx.EXPAND, 0)
        
        grid_sizer_adresse_manuelle_2.AddGrowableCol(1)
        grid_sizer_adresse_manuelle.Add(grid_sizer_adresse_manuelle_2, 1, wx.EXPAND, 0)
        grid_sizer_adresse_manuelle.AddGrowableCol(0)
        grid_sizer_adresse.Add(grid_sizer_adresse_manuelle, 1, wx.EXPAND, 0)
        grid_sizer_adresse.AddGrowableCol(1)
        staticbox_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_adresse, 1, wx.EXPAND, 0)
        grid_sizer_travail.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_travail.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_travail.Add(self.label_travail_tel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_travail.Add(self.ctrl_travail_tel, 0, 0, 0)
        grid_sizer_travail.Add(self.label_profession, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_travail.Add(self.ctrl_profession, 0, wx.EXPAND, 0)
        grid_sizer_travail.Add(self.label_travail_fax, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_travail.Add(self.ctrl_travail_fax, 0, 0, 0)
        grid_sizer_travail.Add(self.label_employeur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_travail.Add(self.ctrl_employeur, 0, wx.EXPAND, 0)
        grid_sizer_travail.Add(self.label_travail_mail, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        # GridSizer Email Travail
        grid_sizer_mail_travail = wx.FlexGridSizer(rows=1, cols=2, vgap=2, hgap=2)
        grid_sizer_mail_travail.Add(self.ctrl_travail_mail, 0, wx.EXPAND, 0)
        grid_sizer_mail_travail.Add(self.bouton_mail_travail, 0, wx.EXPAND, 0)
        grid_sizer_travail.Add(grid_sizer_mail_travail, 0, wx.EXPAND, 0)

        grid_sizer_travail.AddGrowableCol(1)
        staticbox_travail.Add(grid_sizer_travail, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_travail, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.label_tel_domicile, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_tel_domicile, 0, 0, 0)
        grid_sizer_coords.Add(self.label_tel_mobile, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_tel_mobile, 0, 0, 0)
        grid_sizer_coords.Add(self.label_tel_fax, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_coords.Add(self.ctrl_tel_fax, 0, 0, 0)
        grid_sizer_coords.Add(self.label_mail, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        # GridSizer Email perso
        grid_sizer_mail_perso = wx.FlexGridSizer(rows=1, cols=2, vgap=2, hgap=2)
        grid_sizer_mail_perso.Add(self.ctrl_mail, 0, wx.EXPAND, 0)
        grid_sizer_mail_perso.Add(self.bouton_mail_perso, 0, wx.EXPAND, 0)
        grid_sizer_coords.Add(grid_sizer_mail_perso, 0, wx.EXPAND, 0)
        
        staticbox_coords.Add(grid_sizer_coords, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_coords, 1, wx.EXPAND, 0)
        grid_sizer_listesdiff.Add(self.label_listesdiff, 0, 0, 0)
        grid_sizer_listesdiff.Add(self.ctrl_listesdiff, 0, wx.EXPAND, 0)
        grid_sizer_listesdiff.AddGrowableRow(1)
        grid_sizer_listesdiff.AddGrowableCol(0)
        staticbox_listesdiff.Add(grid_sizer_listesdiff, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_listesdiff, 1, wx.EXPAND, 0)
        grid_sizer_droit.AddGrowableRow(1)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_base.AddGrowableCol(0)
        
        grid_sizer_base0.Add(grid_sizer_base, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(grid_sizer_base0)
        grid_sizer_base0.Fit(self)
        grid_sizer_base0.AddGrowableCol(0)
    
    def GetAdresseIndividu(self):
        """ Retourne le cp et la ville actuels de l'individu """
        dictTemp = {"cp":self.cp, "ville":self.ville}
        return dictTemp
        
    def OnRadioAdresse(self, event):
        if self.radio_adresse_auto.GetValue() == True :
            self.ctrl_adresse_auto.Enable(True)
            self.label_rue.Enable(False)
            self.ctrl_rue.Enable(False)
            self.label_cp.Enable(False)
            self.ctrl_ville.Enable(False)
            self.label_secteur.Enable(False)
            self.ctrl_secteur.Enable(False)
            self.bouton_secteurs.Enable(False)
        else:
            self.ctrl_adresse_auto.Enable(False)
            self.label_rue.Enable(True)
            self.ctrl_rue.Enable(True)
            self.label_cp.Enable(True)
            self.ctrl_ville.Enable(True)
            self.label_secteur.Enable(True)
            self.ctrl_secteur.Enable(True)
            self.bouton_secteurs.Enable(True)
        self.OnTextAdresse(None)
    
    def Set_Header(self, nomLigne, texte):
        try :
            self.ficheIndividu = self.Parent.GetParent()
            if self.ficheIndividu.GetName() != "fiche_individu" :
                self.ficheIndividu = None
        except : 
            self.ficheIndividu = None
        if self.ficheIndividu != None :
            self.ficheIndividu.Set_Header(nomLigne, texte)
    
    def OnTextAdresse(self, event):
        texte = ""
        rue = ""
        cp = ""
        ville = ""
        if self.radio_adresse_auto.GetValue() == True :
            # Adresse auto
            indexSelection = self.ctrl_adresse_auto.GetSelection()
            if indexSelection != - 1 and self.ctrl_adresse_auto.dictDonnees.has_key(indexSelection) :
                rue = self.ctrl_adresse_auto.dictDonnees[indexSelection]["rue"]
                cp = self.ctrl_adresse_auto.dictDonnees[indexSelection]["cp"]
                ville = self.ctrl_adresse_auto.dictDonnees[indexSelection]["ville"]
                tel_domicile = self.ctrl_adresse_auto.dictDonnees[indexSelection]["tel_domicile"]
                if rue == "" or rue == None : 
                    texte = _(u"Rue inconnue ")
                else:
                    texte = rue + " "
                if cp != "" and cp != None :
                    texte += cp + " "
                if ville != "" and ville != None :
                    texte +=  ville
                if rue == "" and cp == None and ville == None :
                    texte = _(u"Adresse inconnue")
                # Envoie le numéro de téléphone de domicile vers le CTRL tel_domicile
##                if tel_domicile != None and self.ctrl_tel_domicile.GetNumero() == None :
##                    self.ctrl_tel_domicile.SetNumero(tel_domicile)
            else:
                texte = _(u"Adresse inconnue")
        else:
            # Adresse manuelle
            rue = self.ctrl_rue.GetValue()
            cp = self.ctrl_ville.GetValueCP()
            ville = self.ctrl_ville.GetValueVille()
            if rue == "" or rue == None : 
                texte = _(u"Rue inconnue ")
            else:
                texte = rue + " "
            if cp != "" and cp != None :
                texte += cp + " "
            if ville != "" and ville != None :
                texte +=  ville
            if rue == "" and cp == None and ville == None :
                texte = _(u"Adresse inconnue")
        
        self.cp = cp
        self.ville = ville
        
        # Envoie les infos vers l'Header
        self.Set_Header(nomLigne="adresse", texte=texte)
        if event != None :
            event.Skip()
    
    def OnGestionSecteurs(self, event):
        IDsecteur = self.ctrl_secteur.GetID()
        import DLG_Secteurs
        dlg = DLG_Secteurs.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_secteur.MAJ() 
        self.ctrl_secteur.SetID(IDsecteur)
    
    def OnEnvoiEmail(self, event):
        # Création du menu contextuel
        menuPop = wx.Menu()
        
        item = wx.MenuItem(menuPop, event.GetId()+1, _(u"Depuis l'éditeur d'Emails de Noethys"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Editeur_email.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EnvoyerEmail, id=event.GetId()+1)
        
        item = wx.MenuItem(menuPop, event.GetId()+2, _(u"Depuis le client de messagerie par défaut"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Terminal.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EnvoyerEmail, id=event.GetId()+2)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def EnvoyerEmail(self, event):
        # Récupère l'adresse
        if event.GetId() in (801, 802) :
            ctrl = self.ctrl_travail_mail
        if event.GetId() in (901, 902) :
            ctrl = self.ctrl_mail
        adresse = ctrl.GetValue()
        valide, erreur = ctrl.Validation()

        # Vérifie l'adresse
        if adresse == "" or  valide == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord saisir une adresse internet valide !"), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            ctrl.SetFocus()
            return
        
        # Depuis l'éditeur d'Emails de Noethys
        if event.GetId() in (801, 901) :
            import DLG_Mailer
            dlg = DLG_Mailer.Dialog(self)
            listeDonnees = [{"adresse" : adresse, "pieces" : [], "champs" : {},},]
            dlg.SetDonnees(listeDonnees, modificationAutorisee=False)
            dlg.ShowModal() 
            dlg.Destroy()
        
        # Depuis le client de messagerie par défaut
        if event.GetId() in (802, 902) :
            FonctionsPerso.EnvoyerMail(adresses=[adresse,], sujet="", message="")
        
    def MAJ(self):
        """ Importation des données """
        if self.majEffectuee == True :
            return
        self.IDindividu = self.GetGrandParent().IDindividu
        if self.IDindividu == None :
            return
        if self.GetGrandParent().nouvelleFiche == True :
            return

        DB = GestionDB.DB()
        
        # Adresse auto
        self.ctrl_adresse_auto.MAJ(DB=DB) 
        
        # Secteur
        self.ctrl_secteur.MAJ(DB=DB) 
        
        # Catégorie
        self.ctrl_categorie.MAJ(DB=DB) 

        # Listes de diffusion
        self.listesDiffusionInitiale = []
        self.dictDiffusionInitiale = {}
        self.ctrl_listesdiff.MAJ(DB=DB) 
        req = """SELECT IDabonnement, IDliste
        FROM abonnements WHERE IDindividu=%d;""" % self.IDindividu
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeIDliste = []
        for IDabonnement, IDliste in listeDonnees :
            listeIDliste.append(IDliste)
            self.listesDiffusionInitiale.append(IDliste)
            self.dictDiffusionInitiale[IDliste] = IDabonnement
        self.ctrl_listesdiff.SetIDcoches(listeIDliste)

        # Adresse
        req = """SELECT adresse_auto, rue_resid, cp_resid, ville_resid, IDcategorie_travail, profession, employeur, 
        travail_tel, travail_fax, travail_mail, tel_domicile, tel_mobile, tel_fax, mail, IDsecteur FROM individus WHERE IDindividu=%d;""" % self.IDindividu
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 : 
            individu = listeDonnees[0]
            
            if individu[0] != None :
                self.radio_adresse_auto.SetValue(True)
                self.ctrl_adresse_auto.SetID(individu[0])
            else:
                self.radio_adresse_manuelle.SetValue(True)
                try : self.ctrl_rue.SetValue(individu[1])
                except : pass
                self.ctrl_ville.SetValueCP(individu[2])
                self.ctrl_ville.SetValueVille(individu[3])
                self.ctrl_secteur.SetID(individu[14])
            
            # Activité professionnelle
            self.ctrl_categorie.SetID(individu[4])
            try : self.ctrl_profession.SetValue(individu[5])
            except : pass
            try : self.ctrl_employeur.SetValue(individu[6])
            except : pass
            self.ctrl_travail_tel.SetNumero(individu[7])
            self.ctrl_travail_fax.SetNumero(individu[8])
            self.ctrl_travail_mail.SetMail(individu[9])
            
            # Coords
            self.ctrl_tel_domicile.SetNumero(individu[10])
            self.ctrl_tel_mobile.SetNumero(individu[11])
            self.ctrl_tel_fax.SetNumero(individu[12])
            self.ctrl_mail.SetMail(individu[13])
                
        # MAJ controles
        self.OnRadioAdresse(None)

        # Verrouillage utilisateurs
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_coordonnees", "modifier", afficheMessage=False) == False : 
            for ctrl in self.GetChildren() :
                ctrl.Enable(False)
        
        DB.Close()
        
        self.majEffectuee = True
    
    def ValidationData(self):
        """ Validation des données avant Sauvegarde """
        dictDonnees = self.GetData()
        
        # Vérification des adresses mails
        valide, messageErreur = self.ctrl_mail.Validation()
        if valide == False :
            dlg = wx.MessageDialog(self, _(u"L'adresse email personnelle n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        valide, messageErreur = self.ctrl_travail_mail.Validation()
        if valide == False :
            dlg = wx.MessageDialog(self, _(u"L'adresse email professionnelle n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        return True

    def GetData(self):
        dictDonnees = {
            "adresse_auto" : self.ctrl_adresse_auto.GetDonnee(),
            "rue" : self.ctrl_rue.GetValue(),
            "cp" : self.ctrl_ville.GetValueCP(),
            "ville" : self.ctrl_ville.GetValueVille(),
            "IDsecteur" : self.ctrl_secteur.GetID(),
            
            "travail_categorie" : self.ctrl_categorie.GetID(),
            "profession" : self.ctrl_profession.GetValue(),
            "employeur" : self.ctrl_employeur.GetValue(),
            "travail_tel" : self.ctrl_travail_tel.GetNumero(),
            "travail_fax" : self.ctrl_travail_fax.GetNumero(),
            "travail_mail" : self.ctrl_travail_mail.GetMail(),

            "tel_domicile" : self.ctrl_tel_domicile.GetNumero(),
            "tel_mobile" : self.ctrl_tel_mobile.GetNumero(),
            "tel_fax" : self.ctrl_tel_fax.GetNumero(),
            "mail" : self.ctrl_mail.GetMail(),
            }

        return dictDonnees

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base """
        dictDonnees = self.GetData()
        DB = GestionDB.DB()
        listeDonnees = [    
                            ("adresse_auto", dictDonnees["adresse_auto"]),
                            ("rue_resid", dictDonnees["rue"]),
                            ("cp_resid", dictDonnees["cp"]),
                            ("ville_resid", dictDonnees["ville"]),
                            ("IDsecteur", dictDonnees["IDsecteur"]),
                            ("IDcategorie_travail", dictDonnees["travail_categorie"]),
                            ("profession", dictDonnees["profession"]),
                            ("employeur", dictDonnees["employeur"]),
                            ("travail_tel", dictDonnees["travail_tel"]),
                            ("travail_fax", dictDonnees["travail_fax"]),
                            ("travail_mail",  dictDonnees["travail_mail"]),
                            ("tel_domicile", dictDonnees["tel_domicile"]),
                            ("tel_mobile", dictDonnees["tel_mobile"]),
                            ("tel_fax", dictDonnees["tel_fax"]),
                            ("mail", dictDonnees["mail"]),
                        ]
        DB.ReqMAJ("individus", listeDonnees, "IDindividu", self.IDindividu)
        
        # Listes de diffusion ------------
        nouvellesListes = self.ctrl_listesdiff.GetIDcoches() 
        # Ajout
        for IDliste in nouvellesListes :
            if IDliste not in self.listesDiffusionInitiale :
                listeDonnees = [ ("IDliste", IDliste), ("IDindividu", self.IDindividu) ]
                IDlisteNew = DB.ReqInsert("abonnements", listeDonnees)
        # Suppression
        for IDliste in self.listesDiffusionInitiale :
            if IDliste not in nouvellesListes :
                IDabonnement = self.dictDiffusionInitiale[IDliste] 
                DB.ReqDEL("abonnements", "IDabonnement", IDabonnement)
                
        DB.Close()

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.nouvelleFiche = False
        self.IDindividu = 1
        self.ctrl = Panel_coords(panel, IDindividu=self.IDindividu)
        self.ctrl.MAJ()
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()