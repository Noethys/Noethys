#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import wx.grid as gridlib
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
import GestionDB
from Data import DATA_Civilites as Civilites
from Utils import UTILS_Dates
from Utils import UTILS_Historique
from Utils import UTILS_Identification
from Utils import UTILS_Titulaires
from Ctrl import CTRL_Choix_modele
from Utils import UTILS_Config
from Utils import UTILS_Questionnaires
import FonctionsPerso
from Ctrl import CTRL_Devis_options
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")
DICT_CIVILITES = Civilites.GetDictCivilites()
from Utils import UTILS_Infos_individus


LISTE_DONNEES = [
    { "nom" : _(u"Devis"), "champs" : [
        { "code" : "numero", "label" : _(u"Num�ro")}, 
        { "code" : "date", "label" : _(u"Date d'�dition")}, 
        { "code" : "lieu", "label" : _(u"Lieu d'�dition")},
        ] },
    { "nom" : _(u"Destinataire"), "champs" : [ 
        { "code" : "nom", "label" : _(u"Nom")}, 
        { "code" : "rue", "label" : _(u"Rue")}, 
        { "code" : "ville", "label" : _(u"CP + Ville")},
        ] },
    { "nom" : _(u"Organisme"), "champs" : [ 
        { "code" : "siret", "label" : _(u"Num�ro SIRET")}, 
        { "code" : "ape", "label" : _(u"Code APE")}, 
        ] },
    ]

DICT_DONNEES = {}


def RechercheAgrement(listeAgrements, IDactivite, date):
    for IDactiviteTmp, agrement, date_debut, date_fin in listeAgrements :
        if IDactivite == IDactiviteTmp and date >= date_debut and date <= date_fin :
            return agrement
    return None

# -------------------------------------------------------------------------------------------------------------------------

class CTRL_Individus(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.date_debut = None
        self.date_fin = None
        self.listeIndividus = []
        self.dictIndividus = {}
        # Binds
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def SetPeriode(self, date_debut=None, date_fin=None):
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeIndividus, self.dictIndividus = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeIndividus = [(_(u"Prestations familiales"), 0)]
        dictIndividus = {}
        if self.date_debut == None or self.date_fin == None :
            return listeIndividus, dictIndividus 
        # R�cup�ration des individus
        DB = GestionDB.DB()
        req = """SELECT individus.IDindividu, individus.nom, individus.prenom
        FROM individus
        LEFT JOIN prestations ON prestations.IDindividu = individus.IDindividu
        WHERE prestations.IDfamille=%d
        AND prestations.date>='%s' AND prestations.date<='%s'
        GROUP BY individus.IDindividu
        ;""" % (self.parent.IDfamille, self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        for IDindividu, nom, prenom in listeDonnees :
            dictTemp = {"IDindividu": IDindividu, "nom": nom, "prenom": prenom}
            dictIndividus[IDindividu] = dictTemp
            listeIndividus.append((prenom, IDindividu))
        listeIndividus.sort()
        return listeIndividus, dictIndividus

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDindividu in self.listeIndividus :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeIndividus)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeIndividus[index][1])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeIndividus)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeIndividus)):
            ID = self.listeActivites[index][1]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1

    def OnCheck(self, event):
        """ Quand une s�lection d'activit�s est effectu�e... """
        listeIndividus = self.GetIDcoches()
        self.parent.ctrl_activites.SetDonnees(listeIndividus, self.date_debut, self.date_fin)
        listeActivites = self.parent.ctrl_activites.GetListeActivites()
        self.parent.ctrl_unites.SetDonnees(listeIndividus, listeActivites, self.date_debut, self.date_fin)

    def GetListeIndividus(self):
        return self.GetIDcoches() 
    
    def GetDictIndividus(self):
        return self.dictIndividus
    
    def GetTexteNoms(self):
        """ R�cup�re les noms sous la forme David DUPOND et Maxime DURAND... """
        listeNoms = []
        listeIDIndividu = self.GetListeIndividus() 
        for IDindividu, dictIndividu in self.dictIndividus.items() :
            nom = dictIndividu["nom"]
            prenom = dictIndividu["prenom"]
            if IDindividu in listeIDIndividu :
                listeNoms.append(u"%s %s" % (prenom, nom))
        
        texteNoms = u""
        nbreIndividus = len(listeNoms)
        if nbreIndividus == 0 : texteNoms = u""
        if nbreIndividus == 1 : texteNoms = listeNoms[0]
        if nbreIndividus == 2 : texteNoms = _(u"%s et %s") % (listeNoms[0], listeNoms[1])
        if nbreIndividus > 2 :
            for texteNom in listeNoms[:-2] :
                texteNoms += u"%s, " % texteNom
            texteNoms += _(u"%s et %s") % (listeNoms[-2], listeNoms[-1])
        
        return texteNoms

# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Activites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.listeIndividus = []
        self.date_debut = None
        self.date_fin = None
        self.listeActivites = []
        self.dictActivites = {}
        # Binds
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def SetDonnees(self, listeIndividus=[], date_debut=None, date_fin=None):
        self.listeIndividus = listeIndividus
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeActivites, self.dictActivites = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeActivites = []
        dictActivites = {}
        if len(self.listeIndividus) == 0 or self.date_debut == None or self.date_fin == None :
            return listeActivites, dictActivites 
        # R�cup�ration des activit�s disponibles
        if len(self.listeIndividus) == 0 : conditionIndividus = "()"
        elif len(self.listeIndividus) == 1 : conditionIndividus = "(%d)" % self.listeIndividus[0]
        else : conditionIndividus = str(tuple(self.listeIndividus))
        DB = GestionDB.DB()
        req = """SELECT prestations.IDactivite, activites.nom, activites.abrege
        FROM prestations
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        WHERE prestations.IDindividu IN %s
        AND prestations.date>='%s' AND prestations.date<='%s'
        GROUP BY prestations.IDactivite
        ;""" % (conditionIndividus, self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        for IDactivite, nom, abrege in listeDonnees :
            if not IDactivite:
                IDactivite = 0
            dictTemp = {"nom": nom, "abrege": abrege}
            dictActivites[IDactivite] = dictTemp
            listeActivites.append((nom, IDactivite))
        listeActivites.sort()
        return listeActivites, dictActivites

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDactivite in self.listeActivites :
            if not nom:
                nom = _(u"Autre")
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
        for index in range(0, len(self.listeActivites)):
            self.Check(index)

    def SetIDcoches(self, listeIDcoches=[]):
        for index in range(0, len(self.listeActivites)):
            ID = self.listeActivites[index][1]
            if ID in listeIDcoches :
                self.Check(index)

    def OnCheck(self, event):
        """ Quand une s�lection d'activit�s est effectu�e... """
        listeSelections = self.GetIDcoches()
        self.parent.ctrl_unites.SetDonnees(self.listeIndividus, listeSelections, self.date_debut, self.date_fin)

    def GetListeActivites(self):
        return self.GetIDcoches() 
    
    def GetDictActivites(self):
        return self.dictActivites
    
# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Unites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.date = None
        self.listeIndividus = []
        self.date_debut = None
        self.date_fin = None
        self.listeActivites = []
        self.listeUnites = []
        # Binds
##        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)
        
    def SetDonnees(self, listeIndividus=[], listeActivites=[], date_debut=None, date_fin=None):
        self.listeIndividus = listeIndividus
        self.listeActivites = listeActivites
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.MAJ() 
        self.CocheTout()

    def MAJ(self):
        self.listeUnites = self.Importation()
        self.SetListeChoix()
    
    def Importation(self):
        listeUnites = []
        if len(self.listeIndividus) == 0 or len(self.listeActivites) == 0 or self.date_debut == None or self.date_fin == None :
            return listeUnites 
        # R�cup�ration des activit�s disponibles
        if len(self.listeIndividus) == 0 : conditionIndividus = "()"
        elif len(self.listeIndividus) == 1 : conditionIndividus = "(%d)" % self.listeIndividus[0]
        else : conditionIndividus = str(tuple(self.listeIndividus))
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))

        DB = GestionDB.DB()
        req = """SELECT prestations.label
        FROM prestations
        WHERE (IDindividu IN %s OR IDindividu IS NULL)
        AND (prestations.IDactivite IN %s OR prestations.IDactivite IS NULL)
        AND prestations.date>='%s' AND prestations.date<='%s'
        AND prestations.IDfamille=%d
        GROUP BY prestations.label
        ;""" % (conditionIndividus, conditionActivites, self.date_debut, self.date_fin, self.parent.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for label, in listeDonnees :
            listeUnites.append(label)
        listeUnites.sort()
        return listeUnites

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for label in self.listeUnites :
            self.Append(label)
            index += 1
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeUnites)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.listeUnites[index])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeUnites)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeUnites)):
            ID = self.listeUnites[index]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1

    def OnCheck(self, event):
        """ Quand une s�lection d'activit�s est effectu�e... """
        listeSelections = self.GetIDcoches()
        return
    
    def GetListeUnites(self):
        return self.GetIDcoches() 
    
    def GetDictUnites(self):
        return self.dictUnites


# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Donnees(gridlib.Grid): 
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, size=(200, 200), style=wx.WANTS_CHARS)
        self.moveTo = None
        self.parent = parent
        self.dictCodes = {}
        
        self.MAJ_CTRL_Donnees() 
        
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        
        # Calcul du nbre de lignes
        nbreLignes = 0
        for dictCategorie in LISTE_DONNEES :
            nbreLignes += 1
            for dictChamp in dictCategorie["champs"] :
                nbreLignes += 1
        
        # Cr�ation de la grille
        self.CreateGrid(nbreLignes, 2)
        self.SetColSize(0, 150)
        self.SetColSize(1, 300)
        self.SetColLabelValue(0, "")
        self.SetColLabelValue(1, "")
        self.SetRowLabelSize(1)
        self.SetColLabelSize(1)
        
        # Remplissage avec les donn�es
        key = 0
        for dictCategorie in LISTE_DONNEES :
            nomCategorie = dictCategorie["nom"]
            
            # Cr�ation d'une ligne CATEGORIE
            self.SetRowLabelValue(key, "")
            self.SetCellFont(key, 0, wx.Font(8, wx.DEFAULT , wx.NORMAL, wx.BOLD))
            self.SetCellBackgroundColour(key, 0, "#C5DDFA")
            self.SetReadOnly(key, 0, True)
            self.SetCellValue(key, 0, nomCategorie)
            self.SetCellAlignment(key, 0, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
            self.SetCellValue(key, 1, "")
            self.SetCellBackgroundColour(key, 1, "#C5DDFA")
            self.SetReadOnly(key, 1, True)
            self.SetCellSize(key, 0, 1, 2)
            
            key += 1
            
            # Cr�ation d'une ligne de donn�es
            for dictChamp in dictCategorie["champs"] :
                code = dictChamp["code"]
                label = dictChamp["label"]
                if code in DICT_DONNEES:
                    valeur = DICT_DONNEES[code]
                else:
                    valeur = u""
                
                # Entete de ligne
                self.SetRowLabelValue(key, "")
                
                # Cr�ation de la cellule LABEL
                self.SetCellValue(key, 0, label)
                self.SetCellBackgroundColour(key, 0, "#EEF4FB")
                self.SetReadOnly(key, 0, True)
                self.SetCellAlignment(key, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetCellValue(key, 1, valeur)
            
                # M�morisation dans le dictionnaire des donn�es
                self.dictCodes[key] = code
                key += 1
            
        # test all the events
        if 'phoenix' in wx.PlatformInfo:
            self.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.OnCellChange)
        else :
            self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        self.moveTo = (1, 1)

    def OnCellChange(self, evt):
        # Modification de la valeur dans le dict de donn�es
        numRow = evt.GetRow()
        valeur = self.GetCellValue(numRow, 1)
        code = self.dictCodes[numRow]
        self.SetValeur(code, valeur)
        
    def OnIdle(self, evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None
        evt.Skip()

    def GetValeur(self, code=""):
        if code in DICT_DONNEES :
            return DICT_DONNEES[code]
        else:
            return None

    def SetValeur(self, code="", valeur = u""):
        global DICT_DONNEES
        DICT_DONNEES[code] = valeur

    def MAJ_CTRL_Donnees(self):
        """ Importe les valeurs de base dans le GRID Donn�es """
        DB = GestionDB.DB()
        
        # R�cup�ration des infos sur le devis
        dateDuJour = str(datetime.date.today())
        self.SetValeur("date", UTILS_Dates.DateEngFr(dateDuJour))
        
        req = """SELECT MAX(numero)
        FROM devis
        ;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        numero = 1
        if len(listeDonnees) > 0 : 
            numero = listeDonnees[0][0]
            if numero == None:
                numero = 1
            else:
                numero += 1
        self.SetValeur("numero", u"%06d" % numero)
        
        # R�cup�ration des infos sur l'organisme
        self.SetValeur("siret", "")
        self.SetValeur("ape", "")
        self.SetValeur("lieu", "")
        req = """SELECT nom, num_siret, code_ape, ville
        FROM organisateur
        WHERE IDorganisateur=1;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        for nom, num_siret, code_ape, ville in listeDonnees :
            if num_siret != None : self.SetValeur("siret", num_siret)
            if code_ape != None : self.SetValeur("ape", code_ape)
            if ville != None : self.SetValeur("lieu", ville.capitalize() )
        
        DB.Close()

        dictInfosTitulaires = UTILS_Titulaires.GetTitulaires([self.parent.IDfamille,], mode_adresse_facturation=True)

        self.SetValeur("nom", dictInfosTitulaires[self.parent.IDfamille]["titulairesAvecCivilite"])
        self.SetValeur("rue", dictInfosTitulaires[self.parent.IDfamille]["adresse"]["rue"])
        self.SetValeur("ville", u"%s %s" % (dictInfosTitulaires[self.parent.IDfamille]["adresse"]["cp"], dictInfosTitulaires[self.parent.IDfamille]["adresse"]["ville"]))
        


# --------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, date_debut=None, date_fin=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Impression_devis", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.dictSave = {}
                
        # Bandeau
        intro = _(u"Vous pouvez ici �diter un devis au format PDF. Saisissez une p�riode, s�lectionnez les �l�ments de votre choix, puis cliquez sur 'Aper�u'.")
        titre = _(u"Edition d'un devis")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")
        
        # P�riode
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"P�riode"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        self.bouton_date_debut = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        self.bouton_date_fin = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))

        # Individus
        self.staticbox_individus_staticbox = wx.StaticBox(self, -1, _(u"S�lection des individus"))
        self.ctrl_individus = CTRL_Individus(self)
        self.ctrl_individus.SetMinSize((170, 60))

        # Activit�s
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"S�lection des activit�s"))
        self.ctrl_activites = CTRL_Activites(self)
        self.ctrl_activites.SetMinSize((-1, 80))
        
        # Unit�s
        self.staticbox_unites_staticbox = wx.StaticBox(self, -1, _(u"S�lection des prestations"))
        self.ctrl_unites = CTRL_Unites(self)
        self.ctrl_unites.SetMinSize((-1, 80))

        # Donn�es
        self.staticbox_donnees_staticbox = wx.StaticBox(self, -1, _(u"Donn�es"))
        self.ctrl_donnees = CTRL_Donnees(self)

        # Options
        self.ctrl_parametres = CTRL_Devis_options.CTRL(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer par Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aper�u"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.OnTextDateDebut, self.ctrl_date_debut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDateDebut, self.bouton_date_debut)
        self.Bind(wx.EVT_TEXT, self.OnTexteDateFin, self.ctrl_date_fin)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDateFin, self.bouton_date_fin)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        
        # Init contr�les
        if date_debut != None : 
            self.ctrl_date_debut.SetDate(date_debut)
        if date_fin != None : 
            self.ctrl_date_fin.SetDate(date_fin)
        if date_debut != None and date_fin != None :
            self.ctrl_individus.SetPeriode(date_debut, date_fin)
            listeIndividus = self.ctrl_individus.GetListeIndividus()
            self.ctrl_activites.SetDonnees(listeIndividus, date_debut, date_fin)
            listeActivites = self.ctrl_activites.GetListeActivites()
            self.ctrl_unites.SetDonnees(listeIndividus, listeActivites, date_debut, date_fin)
        
        

    def __set_properties(self):
        self.SetTitle(_(u"Edition d'un devis"))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de d�but")))
        self.bouton_date_debut.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour s�lectionner la date de d�but")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin")))
        self.bouton_date_fin.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour s�lectionner la date de fin")))
        self.ctrl_individus.SetToolTip(wx.ToolTip(_(u"Cochez les individus")))
        self.ctrl_activites.SetToolTip(wx.ToolTip(_(u"Cochez les activit�s")))
        self.ctrl_unites.SetToolTip(wx.ToolTip(_(u"Cochez les unites")))
        self.ctrl_donnees.SetToolTip(wx.ToolTip(_(u"Vous pouvez modifier ici les donn�es de base")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_email.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer ce document par Email")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher le PDF")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((760, 660))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # P�riode
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_periode.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.bouton_date_debut, 0, 0, 0)
        grid_sizer_periode.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add(self.bouton_date_fin, 0, 0, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_periode, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Individus
        staticbox_individus = wx.StaticBoxSizer(self.staticbox_individus_staticbox, wx.VERTICAL)
        staticbox_individus.Add(self.ctrl_individus, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_individus, 1, wx.EXPAND, 0)
        
        # Activit�s
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        staticbox_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_activites, 1, wx.EXPAND, 0)
        
        # unites
        staticbox_unites = wx.StaticBoxSizer(self.staticbox_unites_staticbox, wx.VERTICAL)
        staticbox_unites.Add(self.ctrl_unites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(staticbox_unites, 1, wx.EXPAND, 0)
        
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_gauche.AddGrowableRow(2)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # Donn�es
        staticbox_donnees = wx.StaticBoxSizer(self.staticbox_donnees_staticbox, wx.VERTICAL)
        staticbox_donnees.Add(self.ctrl_donnees, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_donnees, 1, wx.EXPAND, 0)
        
        # Options
        grid_sizer_droit.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_email, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def MAJlistes(self):
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        self.ctrl_individus.SetPeriode(date_debut, date_fin)
        listeIndividus = self.ctrl_individus.GetListeIndividus()
        self.ctrl_activites.SetDonnees(listeIndividus, date_debut, date_fin)
        listeActivites = self.ctrl_activites.GetListeActivites()
        self.ctrl_unites.SetDonnees(listeIndividus, listeActivites, date_debut, date_fin)

    def OnCheckAfficherConso(self, event):
        self.ctrl_unites.MAJ() 
        self.ctrl_unites.CocheTout()
        
    def OnTextDateDebut(self, event): 
        date = self.ctrl_date_debut.GetDate() 
        self.MAJlistes() 

    def OnBoutonDateDebut(self, event):
        from Dlg import DLG_calendrier_simple
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date_debut.SetDate(date)
        dlg.Destroy()

    def OnTexteDateFin(self, event): 
        date = self.ctrl_date_fin.GetDate() 
        self.MAJlistes() 

    def OnBoutonDateFin(self, event):
        from Dlg import DLG_calendrier_simple
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date_fin.SetDate(date)
        dlg.Destroy()        

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Genererundevis")

    def Sauvegarder(self):
        """ Sauvegarder la trace du devis """
        if len(self.dictSave) == 0 : 
            return
        
        # Demande la confirmation de sauvegarde
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous m�moriser le devis ?\n\n(Cliquez NON si c'�tait juste un test sinon cliquez OUI)"), _(u"Sauvegarde"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        
        # Sauvegarde du devis
        DB = GestionDB.DB()
        listeDonnees = [ 
            ("numero", self.dictSave["numero"] ), 
            ("IDfamille", self.dictSave["IDfamille"] ), 
            ("date_edition", self.dictSave["date_edition"] ), 
            ("activites", self.dictSave["activites"] ), 
            ("individus", self.dictSave["individus"] ), 
            ("IDutilisateur", self.dictSave["IDutilisateur"] ), 
            ("date_debut", self.dictSave["date_debut"] ), 
            ("date_fin", self.dictSave["date_fin"] ), 
            ("total", self.dictSave["total"] ), 
            ("regle", self.dictSave["regle"] ), 
            ("solde", self.dictSave["solde"] ), 
            ]
        IDdevis = DB.ReqInsert("devis", listeDonnees)
        DB.Close()
        
        # M�morisation de l'action dans l'historique
        UTILS_Historique.InsertActions([{
                "IDfamille" : self.IDfamille,
                "IDcategorie" : 36,
                "action" : _(u"Edition d'un devis pour la p�riode du %s au %s pour un total de %.02f � et un solde de %.02f �") % (UTILS_Dates.DateEngFr(self.dictSave["date_debut"]), UTILS_Dates.DateEngFr(self.dictSave["date_fin"]), self.dictSave["total"], self.dictSave["solde"] ),
                },])
        
        # M�morisation des param�tres
        self.ctrl_parametres.MemoriserParametres() 
        
    
    def OnBoutonAnnuler(self, event):
        self.Sauvegarder() 
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)

    def OnBoutonEmail(self, event): 
        """ Envoi par mail """
        from Utils import UTILS_Envoi_email
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=self.IDfamille, nomDoc=FonctionsPerso.GenerationNomDoc("DEVIS", "pdf"), categorie="devis")

    def OnBoutonOk(self, event): 
        self.CreationPDF() 

    def CreationPDF(self, nomDoc=FonctionsPerso.GenerationNomDoc("DEVIS", "pdf") , afficherDoc=True):
        # R�cup�ration du dictOptions
        dictOptions = self.ctrl_parametres.GetOptions() 
        if dictOptions == False :
            return False

        if dictOptions["IDmodele"] == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez s�lectionner un mod�le de document !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        dictChampsFusion = {}

        # R�cup�ration des valeurs
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        listeIndividus = self.ctrl_individus.GetListeIndividus()
        listeActivites = self.ctrl_activites.GetListeActivites()
        listeUnites = self.ctrl_unites.GetListeUnites()
        
        dictDonnees = DICT_DONNEES
        
        # R�cup�ration des pr�sences
        if len(listeIndividus) == 0 : conditionIndividus = "()"
        elif len(listeIndividus) == 1 : conditionIndividus = "(%d)" % listeIndividus[0]
        else : conditionIndividus = str(tuple(listeIndividus))
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))
        
        DB = GestionDB.DB()
        
        # R�cup�ration de tous les individus de la base
        req = """
        SELECT IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid
        FROM individus
        ;""" 
        DB.ExecuterReq(req)
        listeIndividus2 = DB.ResultatReq()  
        dictIndividus = {}
        for IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid in listeIndividus2 :
            dictIndividus[IDindividu] = {"IDcivilite":IDcivilite, "nom":nom, "prenom":prenom, "date_naiss":date_naiss, "adresse_auto":adresse_auto, "rue_resid":rue_resid, "cp_resid":cp_resid, "ville_resid":ville_resid}

        # Recherche des prestations
        req = u"""
        SELECT prestations.IDprestation, prestations.IDcompte_payeur, prestations.IDfamille, prestations.date, categorie, 
        label, prestations.montant_initial, prestations.montant, prestations.tva,
        prestations.IDactivite, activites.nom, activites.abrege,
        prestations.IDtarif, noms_tarifs.nom, categories_tarifs.nom, IDfacture, 
        prestations.IDindividu, 
        individus.IDcivilite, individus.nom, individus.prenom, individus.date_naiss, 
        SUM(ventilation.montant) AS montant_ventilation,
        forfait_date_debut, forfait_date_fin
        FROM prestations
        LEFT JOIN ventilation ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN individus ON prestations.IDindividu = individus.IDindividu
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON tarifs.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        WHERE (prestations.IDindividu IN %s OR prestations.IDindividu IS NULL)
        AND (prestations.IDactivite IN %s or prestations.IDactivite IS NULL)
        AND prestations.date>='%s' AND prestations.date<='%s'
        AND prestations.IDfamille=%d
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % (conditionIndividus, conditionActivites, date_debut, date_fin, self.IDfamille)
        DB.ExecuterReq(req)
        listePrestationsTemp = DB.ResultatReq()  
        
        # Filtre des noms de prestations
        listePrestations = []
        for donnees in listePrestationsTemp :
            if donnees[5] in listeUnites :
                listePrestations.append(donnees)
        
        if len(listePrestations) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'existe aucune prestation avec les param�tres donn�s !"), _(u"Annulation"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Recherche des d�ductions
        req = u"""
        SELECT IDdeduction, IDprestation, IDfamille, date, montant, label, IDaide
        FROM deductions
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = deductions.IDcompte_payeur
        AND comptes_payeurs.IDfamille=%d
        ;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDeductionsTemp = DB.ResultatReq()  
        dictDeductions = {}
        for IDdeduction, IDprestation, IDfamille, date, montant, label, IDaide in listeDeductionsTemp :
            if (IDprestation in dictDeductions) == False :
                dictDeductions[IDprestation] = []
            dictDeductions[IDprestation].append({"IDdeduction":IDdeduction, "date":date, "montant":montant, "label":label, "IDaide":IDaide})
            
        # Recherche des consommations (sert pour les forfaits)
        req = """
        SELECT IDconso, consommations.date, consommations.IDprestation
        FROM consommations
        LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
        WHERE (consommations.IDindividu IN %s OR consommations.IDindividu IS NULL)
        AND (prestations.IDactivite IN %s or prestations.IDactivite IS NULL)
        AND prestations.date>='%s' AND prestations.date<='%s'
        AND prestations.IDfamille=%d
        AND prestations.categorie='consommation'
        ;""" % (conditionIndividus, conditionActivites, date_debut, date_fin, self.IDfamille)
        DB.ExecuterReq(req)
        listeConsommations = DB.ResultatReq()  
        dictConsommations = {}
        for IDconso, date, IDprestation in listeConsommations :
            date = UTILS_Dates.DateEngEnDateDD(date)
            if (IDprestation in dictConsommations) == False :
                dictConsommations[IDprestation] = []
            if date not in dictConsommations[IDprestation] :
                dictConsommations[IDprestation].append(date)
        
        # Recherche des num�ros d'agr�ments
        req = """
        SELECT IDactivite, agrement, date_debut, date_fin
        FROM agrements
        WHERE IDactivite IN %s
        ORDER BY date_debut
        """ % conditionActivites
        DB.ExecuterReq(req)
        listeAgrements = DB.ResultatReq()  

        # R�cup�ration des infos sur l'organisme
        req = """SELECT nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape
        FROM organisateur
        WHERE IDorganisateur=1;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        dictOrganisme = {}
        for nom, rue, cp, ville, tel, fax, mail, site, num_agrement, num_siret, code_ape in listeDonnees :
            dictOrganisme["nom"] = nom
            dictOrganisme["rue"] = rue
            dictOrganisme["cp"] = cp
            if ville != None : ville = ville.capitalize()
            dictOrganisme["ville"] = ville
            dictOrganisme["tel"] = tel
            dictOrganisme["fax"] = fax
            dictOrganisme["mail"] = mail
            dictOrganisme["site"] = site
            dictOrganisme["num_agrement"] = num_agrement
            dictOrganisme["num_siret"] = num_siret
            dictOrganisme["code_ape"] = code_ape

        DB.Close() 

        # Get noms Titulaires
        dictNomsTitulaires = UTILS_Titulaires.GetTitulaires(mode_adresse_facturation=True)

        # R�cup�ration des questionnaires
        Questionnaires = UTILS_Questionnaires.ChampsEtReponses(type="famille")

        # R�cup�ration des infos de base individus et familles
        self.infosIndividus = UTILS_Infos_individus.Informations(mode_adresse_facturation=True)

        # ----------------------------------------------------------------------------------------------------
        # Analyse et regroupement des donn�es
        dictValeurs = {}
        listeActivitesUtilisees = []
        for IDprestation, IDcompte_payeur, IDfamille, date, categorie, label, montant_initial, montant, tva, IDactivite, nomActivite, abregeActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, IDindividu, IDcivilite, nomIndividu, prenomIndividu, dateNaiss, montant_ventilation, forfait_date_debut, forfait_date_fin in listePrestations :
            montant_initial = FloatToDecimal(montant_initial) 
            montant = FloatToDecimal(montant) 
            montant_ventilation = FloatToDecimal(montant_ventilation) 
            
            # Regroupement par compte payeur
            if (IDcompte_payeur in dictValeurs) == False :
                    
                # Recherche des titulaires
                dictInfosTitulaires = dictNomsTitulaires[IDfamille]
                nomsTitulairesAvecCivilite = dictInfosTitulaires["titulairesAvecCivilite"]
                nomsTitulairesSansCivilite = dictInfosTitulaires["titulairesSansCivilite"]
                rue_resid = dictInfosTitulaires["adresse"]["rue"]
                cp_resid = dictInfosTitulaires["adresse"]["cp"]
                ville_resid = dictInfosTitulaires["adresse"]["ville"]
                
                # M�morisation des infos                
                dictValeurs[IDcompte_payeur] = {
                    "nomSansCivilite" : nomsTitulairesSansCivilite,
                    "IDfamille" : IDfamille,
                    "{IDFAMILLE}" : str(IDfamille),
                    "individus" : {},
                    "listePrestations" : [],
                    "prestations_familiales" : [],
                    "total" : FloatToDecimal(0.0),
                    "ventilation" : FloatToDecimal(0.0),
                    "solde" : FloatToDecimal(0.0),
                    "num_devis" : dictDonnees["numero"],
                    "select" : True,
                    "date_debut" : date_debut,
                    "date_fin" : date_fin,

                    "{LIEU_EDITION}" : dictDonnees["lieu"],
                    "{DESTINATAIRE_NOM}" : dictDonnees["nom"],
                    "{DESTINATAIRE_RUE}" : dictDonnees["rue"],
                    "{DESTINATAIRE_VILLE}" : dictDonnees["ville"],
                    
                    "{NUM_DEVIS}" : dictDonnees["numero"],
                    "{DATE_EDITION}" : dictDonnees["date"],
                    "{DATE_DEBUT}" : UTILS_Dates.DateEngFr(str(date_debut)),
                    "{DATE_FIN}" : UTILS_Dates.DateEngFr(str(date_fin)),
                    "{NOMS_INDIVIDUS}" : self.ctrl_individus.GetTexteNoms(),

                    "{ORGANISATEUR_NOM}" : dictOrganisme["nom"],
                    "{ORGANISATEUR_RUE}" : dictOrganisme["rue"],
                    "{ORGANISATEUR_CP}" : dictOrganisme["cp"],
                    "{ORGANISATEUR_VILLE}" : dictOrganisme["ville"],
                    "{ORGANISATEUR_TEL}" : dictOrganisme["tel"],
                    "{ORGANISATEUR_FAX}" : dictOrganisme["fax"],
                    "{ORGANISATEUR_MAIL}" : dictOrganisme["mail"],
                    "{ORGANISATEUR_SITE}" : dictOrganisme["site"],
                    "{ORGANISATEUR_AGREMENT}" : dictOrganisme["num_agrement"],
                    "{ORGANISATEUR_SIRET}" : dictOrganisme["num_siret"],
                    "{ORGANISATEUR_APE}" : dictOrganisme["code_ape"],
                    }
                
                # Ajoute les infos de base familles
                dictValeurs[IDcompte_payeur].update(self.infosIndividus.GetDictValeurs(mode="famille", ID=IDfamille, formatChamp=True))
                
                # Ajoute les r�ponses des questionnaires
                for dictReponse in Questionnaires.GetDonnees(IDfamille) :
                    dictValeurs[IDcompte_payeur][dictReponse["champ"]] = dictReponse["reponse"]
                    if dictReponse["controle"] == "codebarres" :
                        dictValeurs[IDcompte_payeur]["{CODEBARRES_QUESTION_%d}" % dictReponse["IDquestion"]] = dictReponse["reponse"]

                # Fusion pour textes personnalis�s
                dictValeurs[IDcompte_payeur]["texte_titre"] = CTRL_Devis_options.RemplaceMotsCles(dictOptions["texte_titre"], dictValeurs[IDcompte_payeur])
                dictValeurs[IDcompte_payeur]["texte_introduction"] = CTRL_Devis_options.RemplaceMotsCles(dictOptions["texte_introduction"], dictValeurs[IDcompte_payeur])
                dictValeurs[IDcompte_payeur]["texte_conclusion"] = CTRL_Devis_options.RemplaceMotsCles(dictOptions["texte_conclusion"], dictValeurs[IDcompte_payeur])


            # Insert les montants pour le compte payeur
            if montant_ventilation == None : montant_ventilation = FloatToDecimal(0.0)
            dictValeurs[IDcompte_payeur]["total"] += montant
            dictValeurs[IDcompte_payeur]["ventilation"] += montant_ventilation
            dictValeurs[IDcompte_payeur]["solde"] = dictValeurs[IDcompte_payeur]["total"] - dictValeurs[IDcompte_payeur]["ventilation"]
            
            dictValeurs[IDcompte_payeur]["{TOTAL_PERIODE}"] = u"%.02f %s" % (dictValeurs[IDcompte_payeur]["total"], SYMBOLE)
            dictValeurs[IDcompte_payeur]["{TOTAL_REGLE}"] = u"%.02f %s" % (dictValeurs[IDcompte_payeur]["ventilation"], SYMBOLE)
            dictValeurs[IDcompte_payeur]["{SOLDE_DU}"] = u"%.02f %s" % (dictValeurs[IDcompte_payeur]["solde"], SYMBOLE)


            # Ajout d'une prestation familiale
            if IDindividu == None : 
                IDindividu = 0
            if IDactivite == None :
                IDactivite = 0
            
            # Ajout d'un individu
            if (IDindividu in dictValeurs[IDcompte_payeur]["individus"]) == False :
                if IDindividu in dictIndividus :
                    
                    # Si c'est bien un individu
                    IDcivilite = dictIndividus[IDindividu]["IDcivilite"]
                    nomIndividu = dictIndividus[IDindividu]["nom"]
                    prenomIndividu = dictIndividus[IDindividu]["prenom"]
                    dateNaiss = dictIndividus[IDindividu]["date_naiss"]
                    if dateNaiss != None : 
                        if DICT_CIVILITES[IDcivilite]["sexe"] == "M" :
                            texteDateNaiss = _(u", n� le %s") % UTILS_Dates.DateEngFr(str(dateNaiss))
                        else:
                            texteDateNaiss = _(u", n�e le %s") % UTILS_Dates.DateEngFr(str(dateNaiss))
                    else:
                        texteDateNaiss = u""
                    texteIndividu = _(u"<b>%s %s</b><font size=7>%s</font>") % (nomIndividu, prenomIndividu, texteDateNaiss)
                    nom = u"%s %s" % (nomIndividu, prenomIndividu)
                    
                else:
                    # Si c'est pour une prestation familiale on cr�� un individu ID 0 :
                    nom = _(u"Prestations diverses")
                    texteIndividu = u"<b>%s</b>" % nom
                    
                dictValeurs[IDcompte_payeur]["individus"][IDindividu] = { "texte" : texteIndividu, "activites" : {}, "total" : FloatToDecimal(0.0), "ventilation" : FloatToDecimal(0.0), "total_reports" : FloatToDecimal(0.0), "nom" : nom, "select" : True }
            
            # Ajout de l'activit�
            if (IDactivite in dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"]) == False :
                texteActivite = nomActivite
                agrement = RechercheAgrement(listeAgrements, IDactivite, date)
                if agrement != None :
                    texteActivite += _(u" - n� agr�ment : %s") % agrement
                dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite] = { "texte" : texteActivite, "presences" : {} }
            
            # Ajout de la pr�sence
            if (date in dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"]) == False :
                dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"][date] = { "texte" : UTILS_Dates.DateEngFr(str(date)), "unites" : [], "total" : FloatToDecimal(0.0) }
            
            # Recherche du nbre de dates pour cette prestation
            if IDprestation in dictConsommations :
                listeDates = dictConsommations[IDprestation]
            else:
                listeDates = []
            
            # Recherche des d�ductions
            if IDprestation in dictDeductions :
                deductions = dictDeductions[IDprestation]
            else :
                deductions = []
            
            # Adaptation du label
            if dictOptions["intitules"] == 2 and IDtarif != None :
                label = nomTarif
            if dictOptions["intitules"] == 3 and IDtarif != None :
                label = nomActivite
            
            # M�morisation de la prestation
            dictPrestation = {
                "IDprestation" : IDprestation, "date" : date, "categorie" : categorie, "label" : label,
                "montant_initial" : montant_initial, "montant" : montant, "tva" : tva, 
                "IDtarif" : IDtarif, "nomTarif" : nomTarif, "nomCategorieTarif" : nomCategorieTarif, 
                "montant_ventilation" : montant_ventilation, "listeDatesConso" : listeDates,
                "deductions" : deductions, "forfait_date_debut": UTILS_Dates.DateEngEnDateDD(forfait_date_debut), "forfait_date_fin": UTILS_Dates.DateEngEnDateDD(forfait_date_fin),
                }

            dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"][date]["unites"].append(dictPrestation)
            
            # Ajout des totaux
            if montant != None : 
                dictValeurs[IDcompte_payeur]["individus"][IDindividu]["total"] += montant
                dictValeurs[IDcompte_payeur]["individus"][IDindividu]["activites"][IDactivite]["presences"][date]["total"] += montant
            if montant_ventilation != None : 
                dictValeurs[IDcompte_payeur]["individus"][IDindividu]["ventilation"] += montant_ventilation
            
            # Stockage des IDprestation pour saisir le IDfacture apr�s cr�ation de la facture
            dictValeurs[IDcompte_payeur]["listePrestations"].append( (IDindividu, IDprestation) )
            
            # M�morisation des activit�s concern�es
            if IDactivite != None :
                listeActivitesUtilisees.append(IDactivite) 
        
        # --------------------------------------------------------------------------------------------------------------------
        
                
        # Pr�paration des donn�es pour une sauvegarde du devis
        self.dictSave = {}
        self.dictSave["numero"] = dictDonnees["numero"]
        self.dictSave["IDfamille"] = self.IDfamille
        self.dictSave["date_edition"] = UTILS_Dates.DateFrEng(dictDonnees["date"])
        self.dictSave["activites"] = ";".join([str(IDactivite) for IDactivite in listeActivitesUtilisees]) 
        self.dictSave["individus"] = ";".join([str(IDindividu) for IDindividu in listeIndividus]) 
        self.dictSave["IDutilisateur"] = UTILS_Identification.GetIDutilisateur()
        self.dictSave["date_debut"] = str(date_debut)
        self.dictSave["date_fin"] = str(date_fin)
        self.dictSave["total"] = float(dictValeurs[IDcompte_payeur]["total"])
        self.dictSave["regle"] = float(dictValeurs[IDcompte_payeur]["ventilation"])
        self.dictSave["solde"] = float(dictValeurs[IDcompte_payeur]["ventilation"] - dictValeurs[IDcompte_payeur]["total"])

        # DictOptions
        dictOptions["date_debut"] = date_debut
        dictOptions["date_fin"] = date_fin
        dictOptions["codeBarre"] = True

        # D�tail
        if dictOptions["affichage_prestations"] == 0 :
            detail = True
        else:
            detail = False
                
        # Champs pour fusion pour Emails
        dictChampsFusion["{NUMERO_DEVIS}"] = self.dictSave["numero"]
        dictChampsFusion["{DATE_DEBUT}"] = UTILS_Dates.DateEngFr(str(date_debut))
        dictChampsFusion["{DATE_FIN}"] = UTILS_Dates.DateEngFr(str(date_fin))
        dictChampsFusion["{DATE_EDITION_DEVIS}"] = UTILS_Dates.DateEngFr(str(self.dictSave["date_edition"]))
        dictChampsFusion["{INDIVIDUS_CONCERNES}"] = self.ctrl_individus.GetTexteNoms()
        dictChampsFusion["{SOLDE}"] = u"%.2f %s" % (self.dictSave["solde"], SYMBOLE)

        # Fabrication du PDF
        from Utils import UTILS_Impression_facture
        UTILS_Impression_facture.Impression(dictValeurs, dictOptions, dictOptions["IDmodele"], mode="devis", ouverture=afficherDoc, nomFichier=nomDoc)
        
        return dictChampsFusion


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=291, date_debut=datetime.date(2020, 11, 1), date_fin=datetime.date(2020, 11, 30))
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
