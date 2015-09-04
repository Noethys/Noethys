#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import CTRL_Grille_periode

import FonctionsPerso
import sys
import operator

import CTRL_Photo
import CTRL_Bandeau

import GestionDB
import UTILS_Config
import UTILS_Organisateur
import DATA_Civilites as Civilites

from DLG_Saisie_pb_sante import LISTE_TYPES

DICT_TYPES_INFOS = {}
for IDtype, nom, img in LISTE_TYPES :
    DICT_TYPES_INFOS[IDtype] = { "nom" : nom, "img" : img }



try: import psyco; psyco.full()
except: pass

DICT_CIVILITES = Civilites.GetDictCivilites()


def DateComplete(dateDD):
    """ Transforme une date DD en date compl�te : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"f�vrier"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"ao�t"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"d�cembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def GetSQLdates(listePeriodes=[]):
    texteSQL = ""
    for date_debut, date_fin in listePeriodes :
        texteSQL += "(date>='%s' AND date<='%s') OR " % (date_debut, date_fin)
    if len(texteSQL) > 0 :
        texteSQL = "(" + texteSQL[:-4] + ")"
    else:
        texteSQL = "date=0"
    return texteSQL


class CTRL_Activites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.listePeriodes = []
        self.SetToolTipString(_(u"Cochez les activit�s � afficher"))
        self.listeActivites = []
        self.dictActivites = {}
        self.SetMinSize((-1, 100))
        # Binds
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def SetPeriodes(self, listePeriodes=[]):
        self.listePeriodes = listePeriodes
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeActivites, self.dictActivites = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeActivites = []
        dictActivites = {}
        if len(self.listePeriodes) == 0 :
            return listeActivites, dictActivites 
        # Condition P�riodes
        conditionsPeriodes = GetSQLdates(self.listePeriodes)
        
        # R�cup�ration des activit�s disponibles la p�riode s�lectionn�e
        DB = GestionDB.DB()
        req = """SELECT activites.IDactivite, nom, abrege, date_debut, date_fin
        FROM activites
        LEFT JOIN ouvertures ON ouvertures.IDactivite = activites.IDactivite
        WHERE %s
        GROUP BY activites.IDactivite
        ORDER BY date_fin DESC;""" % conditionsPeriodes
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDactivite, nom, abrege, date_debut, date_fin in listeDonnees :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            dictTemp = { "nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin, "tarifs" : {} }
            dictActivites[IDactivite] = dictTemp
            listeActivites.append((nom, IDactivite))
        listeActivites.sort()
        return listeActivites, dictActivites

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDactivite in self.listeActivites :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeActivites)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeActivites[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeActivites)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeActivites)):
            ID = self.listeActivites[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1

    def OnCheck(self, event):
        """ Quand une s�lection d'activit�s est effectu�e... """
        listeSelections = self.GetIDcoches()
        try :
            self.parent.SetGroupes(listeSelections)
        except :
            print listeSelections
    
    def GetListeActivites(self):
        return self.GetIDcoches() 
    
    def GetDictActivites(self):
        return self.dictActivites
    
# ----------------------------------------------------------------------------------------------------------------------------------


class CTRL_Groupes(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.SetToolTipString(_(u"Cochez les groupes � afficher"))
        self.listeGroupes = []
        self.dictGroupes = {}
        self.SetMinSize((-1, 100))
        # Binds
##        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def SetActivites(self, listeActivites=[]):
        self.listeActivites = listeActivites
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeGroupes, self.dictGroupes = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeGroupes = []
        dictGroupes = {}
        if len(self.listeActivites) == 0 :
            return listeGroupes, dictGroupes 
        # R�cup�ration des groupes des activit�s s�lectionn�es
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))
        DB = GestionDB.DB()
        req = """SELECT IDgroupe, IDactivite, nom
        FROM groupes
        WHERE IDactivite IN %s
        ORDER BY nom;""" % conditionActivites
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDgroupe, IDactivite, nom in listeDonnees :
            dictTemp = { "nom" : nom, "IDactivite" : IDactivite}
            dictGroupes[IDgroupe] = dictTemp
            listeGroupes.append((nom, IDgroupe))
        listeGroupes.sort()
        return listeGroupes, dictGroupes

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDgroupe in self.listeGroupes :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeGroupes)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeGroupes[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeGroupes)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeGroupes)):
            ID = self.listeGroupes[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1

##    def OnCheck(self, event):
##        """ Quand une s�lection de groupes est effectu�e... """
##        listeSelections = self.GetIDcoches()
##        try :
##            self.parent.SetActivites(listeSelections)
##        except :
##            print listeSelections
    
    def GetListeGroupes(self):
        return self.GetIDcoches() 
    
    def GetDictGroupes(self):
        return self.dictGroupes
    
# ----------------------------------------------------------------------------------------------------------------------------------




class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Impression_infos_medicales", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici imprimer une liste au format PDF des informations m�dicales des individus pr�sents sur la p�riode de votre choix. Pour une liste standard, s�lectionnez simplement une p�riode puis cliquez sur 'Aper�u'.")
        titre = _(u"Impression de la liste des informations m�dicales")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")
        
        # Calendrier
        self.staticbox_date_staticbox = wx.StaticBox(self, -1, _(u"P�riode"))
        self.ctrl_calendrier = CTRL_Grille_periode.CTRL(self)
        self.ctrl_calendrier.SetMinSize((200, 150))
        
        # Activit�s
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activit�s"))
        self.ctrl_activites = CTRL_Activites(self)
        self.ctrl_activites.SetMinSize((10, 50))
        
        # Groupes
        self.staticbox_groupes_staticbox = wx.StaticBox(self, -1, _(u"Groupes"))
        self.ctrl_groupes = CTRL_Groupes(self)
        
        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_modele = wx.StaticText(self, -1, _(u"Mod�le :"))
        self.ctrl_modele = wx.Choice(self, -1, choices=[_(u"Mod�le par d�faut"),])
        self.ctrl_modele.Select(0)
        self.label_tri = wx.StaticText(self, -1, _(u"Tri :"))
        self.ctrl_tri = wx.Choice(self, -1, choices=["Nom", _(u"Pr�nom"), _(u"Age")])
        self.ctrl_tri.Select(0)
        self.ctrl_ordre = wx.Choice(self, -1, choices=["Croissant", _(u"D�croissant")])
        self.ctrl_ordre.Select(0)
        self.checkbox_lignes_vierges = wx.CheckBox(self, -1, _(u"Afficher des lignes vierges :"))
        self.checkbox_lignes_vierges.SetValue(True)
        self.ctrl_nbre_lignes = wx.Choice(self, -1, choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"])
        self.ctrl_nbre_lignes.Select(2)
        self.checkbox_page_groupe = wx.CheckBox(self, -1, _(u"Ins�rer un saut de page apr�s chaque groupe"))
        self.checkbox_page_groupe.SetValue(True)
        self.checkbox_nonvides = wx.CheckBox(self, -1, _(u"Afficher uniquement les individus avec infos"))
        self.checkbox_nonvides.SetValue(False)
        self.checkbox_age = wx.CheckBox(self, -1, _(u"Afficher l'�ge des individus"))
        self.checkbox_age.SetValue(True)
        self.checkbox_photos = wx.CheckBox(self, -1, _(u"Afficher les photos :"))
        self.checkbox_photos.SetValue(False)
        self.ctrl_taille_photos = wx.Choice(self, -1, choices=[_(u"Petite taille"), _(u"Moyenne taille"), _(u"Grande taille")])
        self.ctrl_taille_photos.SetSelection(1)
        
        # M�morisation des param�tres
        self.ctrl_memoriser = wx.CheckBox(self, -1, _(u"M�moriser les param�tres"))
        font = self.GetFont() 
        font.SetPointSize(7)
        self.ctrl_memoriser.SetFont(font)
        self.ctrl_memoriser.SetValue(True) 
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aper�u"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckLignesVierges, self.checkbox_lignes_vierges)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckPhotos, self.checkbox_photos)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # R�cup�ration des param�tres dans le CONFIG
        param_tri = UTILS_Config.GetParametre("impression_infos_med_tri", defaut=0)
        self.ctrl_tri.Select(param_tri)
        
        param_ordre = UTILS_Config.GetParametre("impression_infos_med_ordre", defaut=0)
        self.ctrl_ordre.Select(param_ordre)
        
        param_lignes_vierges = UTILS_Config.GetParametre("impression_infos_med_lignes_vierges", defaut=1)
        self.checkbox_lignes_vierges.SetValue(param_lignes_vierges)
        
        if param_lignes_vierges == 1 :
            param_nbre_lignes_vierges = UTILS_Config.GetParametre("impression_infos_med_nbre_lignes_vierges", defaut=2)
            self.ctrl_nbre_lignes.Select(param_nbre_lignes_vierges)
        
        param_page_groupe = UTILS_Config.GetParametre("impression_infos_med_page_groupe", defaut=1)
        self.checkbox_page_groupe.SetValue(param_page_groupe)
        
        param_nonvides = UTILS_Config.GetParametre("impression_infos_med_nonvides", defaut=0)
        self.checkbox_nonvides.SetValue(param_nonvides)
        
        param_age = UTILS_Config.GetParametre("impression_infos_med_age", defaut=1)
        self.checkbox_age.SetValue(param_age)
        
        param_photos = UTILS_Config.GetParametre("impression_infos_med_photos", defaut=1)
        self.checkbox_photos.SetValue(param_photos)
        
        param_taille_photos = UTILS_Config.GetParametre("impression_infos_med_taille_photos", defaut=1)
        self.ctrl_taille_photos.SetSelection(param_taille_photos)
        
        param_memoriser = UTILS_Config.GetParametre("impression_infos_med_memoriser", defaut=1)
        self.ctrl_memoriser.SetValue(param_memoriser)
        
        # Init Contr�les
        self.OnCheckLignesVierges(None)
        self.OnCheckPhotos(None) 
        self.bouton_ok.SetFocus() 
        
        self.ctrl_calendrier.SetVisibleSelection()
        self.SetListesPeriodes(self.ctrl_calendrier.GetDatesSelections())
        
        self.grid_sizer_base.Fit(self)
        

    def __set_properties(self):
        self.SetTitle(_(u"Impression de la liste des informations m�dicales"))
        self.checkbox_lignes_vierges.SetToolTipString(_(u"Cochez cette case pour afficher des lignes vierges � la fin de la liste"))
        self.checkbox_page_groupe.SetToolTipString(_(u"Cochez cette case pour afficher une page par groupe"))
        self.checkbox_age.SetToolTipString(_(u"Cochez cette case pour afficher l'�ge des individus dans la liste"))
        self.checkbox_photos.SetToolTipString(_(u"Cochez cette case pour afficher les photos individuelles"))
        self.ctrl_nbre_lignes.SetToolTipString(_(u"S�lectionnez le nombre de lignes � afficher"))
        self.checkbox_nonvides.SetToolTipString(_(u"Cochez cette case pour afficher uniquement les individus qui ont au moins une information m�dicale"))
        self.ctrl_memoriser.SetToolTipString(_(u"Cochez cette case pour m�moriser les param�tres pour la prochaine �dition"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options_lignes = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=10)
        grid_sizer_lignes_vierges = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_options_grille = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=10)
        staticbox_groupes = wx.StaticBoxSizer(self.staticbox_groupes_staticbox, wx.VERTICAL)
        grid_sizer_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        staticbox_date = wx.StaticBoxSizer(self.staticbox_date_staticbox, wx.VERTICAL)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        staticbox_date.Add(self.ctrl_calendrier, 0, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(staticbox_date, 1, wx.EXPAND, 0)
        staticbox_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(staticbox_activites, 1, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        staticbox_groupes.Add(self.ctrl_groupes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droit.Add(staticbox_groupes, 1, wx.EXPAND, 0)
        grid_sizer_options_grille.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_grille.Add(self.ctrl_modele, 0, wx.EXPAND, 0)
        grid_sizer_options_grille.Add(self.label_tri, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        # Tri
        grid_sizer_tri = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_tri.Add(self.ctrl_tri, 0, wx.EXPAND, 0)
        grid_sizer_tri.Add(self.ctrl_ordre, 0, wx.EXPAND, 0)
        grid_sizer_options_grille.Add(grid_sizer_tri, 0, wx.EXPAND, 0)
        
        grid_sizer_options_grille.AddGrowableCol(1)
        grid_sizer_options_lignes.Add(grid_sizer_options_grille, 1, wx.EXPAND, 0)
        grid_sizer_lignes_vierges.Add(self.checkbox_lignes_vierges, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_lignes_vierges.Add(self.ctrl_nbre_lignes, 0, 0, 0)
        grid_sizer_options_lignes.Add(grid_sizer_lignes_vierges, 1, wx.EXPAND, 0)
        grid_sizer_options_lignes.Add(self.checkbox_page_groupe, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_lignes.Add(self.checkbox_nonvides, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options_lignes.Add(self.checkbox_age, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_photos = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_photos.Add(self.checkbox_photos, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_photos.Add(self.ctrl_taille_photos, 0, 0, 0)
        grid_sizer_options_lignes.Add(grid_sizer_photos, 1, wx.EXPAND, 0)
        
        grid_sizer_options_lignes.AddGrowableCol(0)
        staticbox_options.Add(grid_sizer_options_lignes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droit.Add(staticbox_options, 1, wx.EXPAND, 0)
        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_base.Add(self.ctrl_memoriser, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        
        self.grid_sizer_base = grid_sizer_base

    def OnCheckLignesVierges(self, event): 
        if self.checkbox_lignes_vierges.GetValue() == True :
            self.ctrl_nbre_lignes.Enable(True)
        else:
            self.ctrl_nbre_lignes.Enable(False)

    def OnCheckPhotos(self, event): 
        if self.checkbox_photos.GetValue() == True :
            self.ctrl_taille_photos.Enable(True)
        else:
            self.ctrl_taille_photos.Enable(False)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Listedesinformationsmdicales")
    
    def SetListesPeriodes(self, listePeriodes=[]):
        self.ctrl_activites.SetPeriodes(listePeriodes)
        self.SetGroupes(self.ctrl_activites.GetListeActivites())

    def SetGroupes(self, listeActivites=[]):
        self.ctrl_groupes.SetActivites(self.ctrl_activites.GetListeActivites())

    def GetAge(self, date_naiss=None):
        if date_naiss == None : return None
        datedujour = datetime.date.today()
        age = (datedujour.year - date_naiss.year) - int((datedujour.month, datedujour.day) < (date_naiss.month, date_naiss.day))
        return age

    def OnBoutonOk(self, event):
        # R�cup�ration et v�rification des donn�es
        listePeriodes = self.ctrl_calendrier.GetDatesSelections() 
        
        listeActivites = self.ctrl_activites.GetListeActivites() 
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une activit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        listeGroupes = self.ctrl_groupes.GetListeGroupes() 
        if len(listeGroupes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un groupe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Cr�ation du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch, cm
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        self.taille_page = A4
        self.orientation = "PAYSAGE"
        if self.orientation == "PORTRAIT" :
            self.hauteur_page = self.taille_page[1]
            self.largeur_page = self.taille_page[0]
        else:
            self.hauteur_page = self.taille_page[0]
            self.largeur_page = self.taille_page[1]
        
        # Cr�ation des conditions pour les requ�tes SQL
        conditionsPeriodes = GetSQLdates(listePeriodes)
        
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))
        
        if len(listeGroupes) == 0 : conditionGroupes = "()"
        elif len(listeGroupes) == 1 : conditionGroupes = "(%d)" % listeGroupes[0]
        else : conditionGroupes = str(tuple(listeGroupes))
                
        # R�cup�ration des noms des groupes
        dictGroupes = self.ctrl_groupes.GetDictGroupes()
        
        # R�cup�ration des noms d'activit�s
        dictActivites = self.ctrl_activites.GetDictActivites()
        
        # R�cup�ration de la liste des groupes ouverts sur cette p�riode
        DB = GestionDB.DB()
        req = """SELECT IDouverture, IDactivite, IDunite, IDgroupe
        FROM ouvertures 
        WHERE ouvertures.IDactivite IN %s AND %s
        AND IDgroupe IN %s
        ; """ % (conditionActivites, conditionsPeriodes, conditionGroupes)
        DB.ExecuterReq(req)
        listeOuvertures = DB.ResultatReq()
        dictOuvertures = {}
        for IDouverture, IDactivite, IDunite, IDgroupe in listeOuvertures :
            if dictOuvertures.has_key(IDactivite) == False : 
                dictOuvertures[IDactivite] = []
            if IDgroupe not in dictOuvertures[IDactivite] :
                dictOuvertures[IDactivite].append(IDgroupe)
    
        # R�cup�ration des individus gr�ce � leurs consommations
        DB = GestionDB.DB() 
        req = """SELECT individus.IDindividu, IDactivite, IDgroupe, etat,
        IDcivilite, nom, prenom, date_naiss
        FROM consommations 
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        WHERE etat IN ("reservation", "present")
        AND IDactivite IN %s AND %s
        GROUP BY individus.IDindividu
        ORDER BY nom, prenom
        ;""" % (conditionActivites, conditionsPeriodes)
        DB.ExecuterReq(req)
        listeIndividus = DB.ResultatReq()
        dictIndividus = {}
        listeIDindividus = []
        
        for IDindividu, IDactivite, IDgroupe, etat, IDcivilite, nom, prenom, date_naiss in listeIndividus :
            if date_naiss != None : date_naiss = DateEngEnDateDD(date_naiss)
            age = self.GetAge(date_naiss)
            
            # M�morisation de l'individu
            dictIndividus[IDindividu] = { 
                "IDcivilite" : IDcivilite, "nom" : nom, "prenom" : prenom, 
                "age" : age, "date_naiss" : date_naiss, "IDgroupe" : IDgroupe, "IDactivite" : IDactivite,
                }
            
            # M�morisation du IDindividu
            if IDindividu not in listeIDindividus :
                listeIDindividus.append(IDindividu) 
            
        # Dict Informations m�dicales
        req = """SELECT IDprobleme, IDindividu, IDtype, intitule, date_debut, date_fin, description, traitement_medical,
        description_traitement, date_debut_traitement, date_fin_traitement, eviction, date_debut_eviction, date_fin_eviction
        FROM problemes_sante 
        WHERE diffusion_listing_enfants=1
        ;"""
        DB.ExecuterReq(req)
        listeInformations = DB.ResultatReq()
        DB.Close()
        dictInfosMedicales = {}
        for IDprobleme, IDindividu, IDtype, intitule, date_debut, date_fin, description, traitement_medical, description_traitement, date_debut_traitement, date_fin_traitement, eviction, date_debut_eviction, date_fin_eviction in listeInformations :
            if dictInfosMedicales.has_key(IDindividu) == False :
                dictInfosMedicales[IDindividu] = []
            dictTemp = {
                "IDprobleme" : IDprobleme, "IDtype" : IDtype, "intitule" : intitule, "date_debut" : date_debut, 
                "date_fin" : date_fin, "description" : description, "traitement_medical" : traitement_medical, "description_traitement" : description_traitement, 
                "date_debut_traitement" : date_debut_traitement, "date_fin_traitement" : date_fin_traitement, "eviction" : eviction, 
                "date_debut_eviction" : date_debut_eviction, "date_fin_eviction" : date_fin_eviction, 
                }
            dictInfosMedicales[IDindividu].append(dictTemp)
        
        # R�cup�ration des photos individuelles
        dictPhotos = {}
        taillePhoto = 128
        if self.ctrl_taille_photos.GetSelection() == 0 : tailleImageFinal = 16
        if self.ctrl_taille_photos.GetSelection() == 1 : tailleImageFinal = 32
        if self.ctrl_taille_photos.GetSelection() == 2 : tailleImageFinal = 64
        if self.checkbox_photos.GetValue() == True :
            for IDindividu in listeIDindividus :
                IDcivilite = dictIndividus[IDindividu]["IDcivilite"]
                nomFichier = "Images/128x128/%s" % DICT_CIVILITES[IDcivilite]["nomImage"]
                IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDindividu, nomFichier=nomFichier, taillePhoto=(taillePhoto, taillePhoto), qualite=100)
                
                # Cr�ation de la photo dans le r�pertoire Temp
                nomFichier = "Temp/photoTmp" + str(IDindividu) + ".jpg"
                bmp.SaveFile(nomFichier, type=wx.BITMAP_TYPE_JPEG)
                img = Image(nomFichier, width=tailleImageFinal, height=tailleImageFinal)
                dictPhotos[IDindividu] = img
            
        # ---------------- Cr�ation du PDF -------------------
        
        # Initialisation du PDF
        nomDoc = "Temp/liste_informations_medicales_%s.pdf" % FonctionsPerso.GenerationIDdoc() 
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(self.largeur_page, self.hauteur_page), topMargin=30, bottomMargin=30)
        story = []
        
        largeurContenu = self.largeur_page - 75 #520
        
        # Cr�ation du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (largeurContenu-100, 100) )
            dateDuJour = DateEngFr(str(datetime.date.today()))
            dataTableau.append( (_(u"Informations m�dicales"), _(u"%s\nEdit� le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
            style = TableStyle([
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                    ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                    ('ALIGN', (0,0), (0,0), 'LEFT'), 
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                    ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                    ('FONT',(1,0),(1,0), "Helvetica", 6), 
                    ])
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)
            story.append(Spacer(0,20))       
        
        # Ins�re un header
        Header() 
        
        # Activit�s
        for IDactivite in listeActivites :
            nomActivite = dictActivites[IDactivite]["nom"]
            # Groupes
            if dictOuvertures.has_key(IDactivite) :
                nbreGroupes = len(dictOuvertures[IDactivite])
                indexGroupe = 1
                for IDgroupe in dictOuvertures[IDactivite] :
                    nomGroupe = dictGroupes[IDgroupe]["nom"]
                    
                    # Initialisation du tableau
                    dataTableau = []
                    largeursColonnes = []
                    labelsColonnes = []
                                        
                    # Recherche des ent�tes de colonnes :
                    if self.checkbox_photos.GetValue() == True :
                        labelsColonnes.append(_(u"Photo"))
                        largeursColonnes.append(tailleImageFinal+6)
                        
                    labelsColonnes.append(_(u"Nom - pr�nom"))
                    largeursColonnes.append(120)
                    
                    if self.checkbox_age.GetValue() == True :
                        labelsColonnes.append(_(u"�ge"))
                        largeursColonnes.append(20)
                    
                    # Calcule la largeur restante
                    largeurRestante = largeurContenu - sum(largeursColonnes)
                                        
                    labelsColonnes.append(_(u"Informations alimentaires"))
                    largeursColonnes.append(largeurRestante/2.0)
                    
                    labelsColonnes.append(_(u"Informations diverses"))
                    largeursColonnes.append(largeurRestante/2.0)
                    
                    # Cr�ation de l'entete de groupe
                    ligne = [nomGroupe,]
                    for x in range(0, len(labelsColonnes)-1):
                        ligne.append("")
                    dataTableau.append(ligne)
        
                    # Cr�ation des ent�tes
                    ligne = []
                    for label in labelsColonnes :
                        ligne.append(label)
                    dataTableau.append(ligne)
                    
                    # --------- Cr�ation des lignes -----------
                            
                    # Cr�ation d'une liste temporaire pour le tri
                    listeIndividus = []
                    if dictOuvertures.has_key(IDactivite) :
                        if IDgroupe in dictOuvertures[IDactivite] :
                            for IDindividu in listeIDindividus :
                                dictIndividu = dictIndividus[IDindividu]
                                if dictIndividu["IDgroupe"] == IDgroupe :
                                    valeursTri = (IDindividu, dictIndividu["nom"], dictIndividu["prenom"], dictIndividu["age"])
                                    
                                    # + S�lection uniquement des individus avec infos
                                    if self.checkbox_nonvides.GetValue() == False or (self.checkbox_nonvides.GetValue() == True and dictInfosMedicales.has_key(IDindividu) ) :
                                        listeIndividus.append(valeursTri)
                    
                    if self.ctrl_tri.GetSelection() == 0 : paramTri = 1 # Nom
                    if self.ctrl_tri.GetSelection() == 1 : paramTri = 2 # Pr�nom
                    if self.ctrl_tri.GetSelection() == 2 : paramTri = 3 # Age
                    if self.ctrl_ordre.GetSelection() == 0 :
                        ordreDecroissant = False
                    else:
                        ordreDecroissant = True
                    listeIndividus = sorted(listeIndividus, key=operator.itemgetter(paramTri), reverse=ordreDecroissant)
                    
                    # R�cup�ration des lignes individus
                    for IDindividu, nom, prenom, age in listeIndividus :
                        dictIndividu = dictIndividus[IDindividu]
                        
                        ligne = []
                        
                        # Photo
                        if self.checkbox_photos.GetValue() == True and IDindividu in dictPhotos :
                            img = dictPhotos[IDindividu]
                            ligne.append(img)
                        
                        # Nom
                        ligne.append(u"%s %s" % (nom, prenom))
                        
                        # Age
                        if self.checkbox_age.GetValue() == True :
                            if age != None :
                                ligne.append(age)
                            else:
                                ligne.append("")
                        
                        # Informations m�dicales
                        paraStyle = ParagraphStyle(name="infos",
                                  fontName="Helvetica",
                                  fontSize=7,
                                  leading=8,
                                  spaceAfter=2,
                                )
                                
                        listeInfosAlim = []
                        listeInfosDivers = []
                        if dictInfosMedicales.has_key(IDindividu) :
                            for infoMedicale in dictInfosMedicales[IDindividu] :
                                intitule = infoMedicale["intitule"]
                                description = infoMedicale["description"]
                                traitement = infoMedicale["traitement_medical"]
                                description_traitement = infoMedicale["description_traitement"]
                                date_debut_traitement = infoMedicale["date_debut_traitement"]
                                date_fin_traitement = infoMedicale["date_fin_traitement"]
                                IDtype = infoMedicale["IDtype"]
                                # Intitul� et description
                                if description != None and description != "" :
                                    texteInfos = u"<b>%s</b> : %s" % (intitule, description)
                                else:
                                    texteInfos = u"%s" % intitule
                                if len(texteInfos) > 0 and texteInfos[-1] != "." : texteInfos += u"."
                                # Traitement m�dical
                                if traitement == 1 and description_traitement != None and description_traitement != "" :
                                    texteDatesTraitement = u""
                                    if date_debut_traitement != None and date_fin_traitement != None : 
                                        texteDatesTraitement = _(u" du %s au %s") % (DateEngFr(date_debut_traitement), DateEngFr(date_fin_traitement))
                                    if date_debut_traitement != None and date_fin_traitement == None : 
                                        texteDatesTraitement = _(u" � partir du %s") % DateEngFr(date_debut_traitement)
                                    if date_debut_traitement == None and date_fin_traitement != None : 
                                        texteDatesTraitement = _(u" jusqu'au %s") % DateEngFr(date_fin_traitement)
                                    texteInfos += _(u"Traitement%s : %s.") % (texteDatesTraitement, description_traitement)
                                
                                # Cr�ation du paragraphe
                                img = DICT_TYPES_INFOS[IDtype]["img"]
                                p = ParagraphAndImage(Paragraph(texteInfos, paraStyle), Image("Images/16x16/%s" % img,width=8, height=8), xpad=1, ypad=0, side="left")
                                if infoMedicale["IDtype"] == 2 :
                                    listeInfosAlim.append(p)
                                else:
                                    listeInfosDivers.append(p)
                            
                            ligne.append(listeInfosAlim)
                            ligne.append(listeInfosDivers)
                            
                        
                        # Ajout de la ligne individuelle dans le tableau
                        dataTableau.append(ligne)
                    
                    # Cr�ation des lignes vierges
                    if self.checkbox_lignes_vierges.GetValue() == True :
                        for x in range(0, self.ctrl_nbre_lignes.GetSelection()+1):
                            ligne = []
                            for col in labelsColonnes :
                                ligne.append("") 
                            dataTableau.append(ligne)
                                                
                    # Style du tableau
                    colPremiere = 1
                    if self.checkbox_photos.GetValue() == True :
                        colPremiere += 1
                    if self.checkbox_age.GetValue() == True :
                        colPremiere += 1
                    
                    couleurFond = (0.8, 0.8, 1) # Vert -> (0.5, 1, 0.2)
                    
                    style = TableStyle([
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                            
                            ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Cr�e la bordure noire pour tout le tableau
                            ('ALIGN', (0,1), (-2,-1), 'CENTRE'), # Centre les cases
                            
                            ('ALIGN', (0,1), (-1,1), 'CENTRE'), # Ligne de labels colonne align�e au centre
                            ('FONT',(0,1),(-1,1), "Helvetica", 6), # Donne la police de caract. + taille de police des labels
                            
                            ('SPAN',(0,0),(-1,0)), # Fusionne les lignes du haut pour faire le titre du groupe
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", 10), # Donne la police de caract. + taille de police du titre de groupe
                            ('BACKGROUND', (0,0), (-1,0), couleurFond), # Donne la couleur de fond du titre de groupe
                            
                            ])
                        
                       
                    # Cr�ation du tableau
                    tableau = Table(dataTableau, largeursColonnes)
                    tableau.setStyle(style)
                    story.append(tableau)
                    story.append(Spacer(0,20))
                    
                    # Saut de page apr�s un groupe
                    if self.checkbox_page_groupe.GetValue() == True :
                        story.append(PageBreak())
                        # Ins�re un header
                        if indexGroupe < nbreGroupes :
                            Header() 
                    
                    indexGroupe += 1
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
        
        self.MemoriserParametres() 
        

    def MemoriserParametres(self):
        if self.ctrl_memoriser.GetValue() == True :
            UTILS_Config.SetParametre("impression_infos_med_tri", self.ctrl_tri.GetSelection())
            UTILS_Config.SetParametre("impression_infos_med_ordre", self.ctrl_ordre.GetSelection())
            UTILS_Config.SetParametre("impression_infos_med_lignes_vierges", int(self.checkbox_lignes_vierges.GetValue()))
            UTILS_Config.SetParametre("impression_infos_med_nbre_lignes_vierges", self.ctrl_nbre_lignes.GetSelection())
            UTILS_Config.SetParametre("impression_infos_med_page_groupe", int(self.checkbox_page_groupe.GetValue()))
            UTILS_Config.SetParametre("impression_infos_med_age", int(self.checkbox_age.GetValue()))
            UTILS_Config.SetParametre("impression_infos_med_nonvides", int(self.checkbox_nonvides.GetValue()))
            UTILS_Config.SetParametre("impression_infos_med_photos", int(self.checkbox_photos.GetValue()))
            UTILS_Config.SetParametre("impression_infos_med_taille_photos", int(self.ctrl_taille_photos.GetSelection()))   
        
        UTILS_Config.SetParametre("impression_infos_med_memoriser", int(self.ctrl_memoriser.GetValue()))
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
