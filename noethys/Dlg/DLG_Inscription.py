#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx

import datetime
import GestionDB
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Questionnaire
from Utils import UTILS_Interface
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Historique
from Utils import UTILS_Titulaires
from Utils import UTILS_Dates
from Dlg import DLG_Selection_activite
from Dlg import DLG_Inscription_desinscription
from Dlg import DLG_Appliquer_forfait
from Dlg import DLG_Messagebox
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import BitmapComboBox
else :
    from wx.combo import BitmapComboBox


STATUTS = [
    {"code": "ok", "label_long": _(u"Inscription valid�e"), "label_court": _(u"Valide"), "image" : "Ok4.png"},
    {"code": "attente", "label_long": _(u"Inscription en attente"), "label_court": _(u"Attente"), "image" : "Attente.png"},
    {"code": "refus", "label_long": _(u"Inscription refus�e"), "label_court": _(u"Refus"), "image" : "Interdit.png"},
]



class Choix_famille(wx.Choice):
    def __init__(self, parent, IDindividu=None, verrouillage=False):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDindividu = IDindividu
        self.verrouillage = verrouillage
        self.listeNoms = []
        self.listeDonnees = []
        self.MAJ()

    def MAJ(self):
        if self.IDindividu != None :
            dictFamillesRattachees = UTILS_Titulaires.GetFamillesRattachees(self.IDindividu)

            self.listeNoms = []
            self.listeDonnees = []
            for IDfamille, dictFamille in dictFamillesRattachees.items() :
                nom = _(u"Famille de %s") % dictFamille["nomsTitulaires"]
                self.listeNoms.append(nom)
                self.listeDonnees.append({"IDfamille" : IDfamille, "nom" : nom})
            self.SetItems(self.listeNoms)

            if len(self.listeDonnees) < 2 or self.verrouillage == True :
                self.Enable(False)

    def SetID(self, ID=None):
        index = 0
        for dictTemp in self.listeDonnees :
            IDfamille = dictTemp["IDfamille"]
            if IDfamille == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index]["IDfamille"]

# ------------------------------------------------------------------------------------------------------------------------------------------

class Choix_statut(BitmapComboBox):
    def __init__(self, parent):
        BitmapComboBox.__init__(self, parent, id=-1, size=(170, -1), style=wx.CB_READONLY)
        self.parent = parent
        self.listeLabels = []
        self.listeDonnees = []
        self.MAJ()
        self.Select(0)

    def MAJ(self):
        for dictStatut in STATUTS:
            self.listeLabels.append(dictStatut["label_long"])
            self.listeDonnees.append(dictStatut["code"])
            self.Append(dictStatut["label_long"], wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % dictStatut["image"]), wx.BITMAP_TYPE_PNG), dictStatut["code"])

    def SetID(self, ID=None):
        index = 0
        for code in self.listeDonnees :
            if code == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index]


# -------------------------------------------------------------------------------------------------------------


class ListBox(wx.ListBox):
    def __init__(self, parent, type="groupes"):
        wx.ListBox.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.listeDonnees = []
        self.type = type

    def MAJ(self):
        selection_actuelle = self.GetID()
        self.listeDonnees = []
        if self.type == "groupes" : self.Importation_groupes()
        if self.type == "categories" : self.Importation_categories() 
        listeItems = []
        if len(self.listeDonnees) > 0 :
            for dictValeurs in self.listeDonnees :
                label = dictValeurs["label"]
                if label == None :
                    label = "Inconnu (ID%d)" % dictValeurs["ID"]
                listeItems.append(label)
        self.Set(listeItems)
        # Si un seul item dans la liste, le s�lectionne...
        if len(self.listeDonnees) == 1 :
            self.Select(0)
        if selection_actuelle != None :
            self.SetID(selection_actuelle)

    def Importation_groupes(self):
        for dictGroupe in self.parent.dictActivite["groupes"] :
            ID = dictGroupe["IDgroupe"]
            label = dictGroupe["nom"]
            self.listeDonnees.append({"ID" : ID, "label" : label})

    def Importation_categories(self):
        for dictCategorie in self.parent.dictActivite["categories_tarifs"] :
            self.listeDonnees.append({"ID" : dictCategorie["IDcategorie_tarif"], "label" : dictCategorie["nom"], "listeVilles" : dictCategorie["listeVilles"]})
            
    def SetID(self, ID=None):
        index = 0
        for dictValeurs in self.listeDonnees :
            if ID == dictValeurs["ID"] :
                self.SetSelection(index)
                return
            index += 1
        
    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        ID = self.listeDonnees[index]["ID"]
        return ID
    
    def GetInfosSelection(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index]
    
    def SelectCategorieSelonVille(self, cp=None, ville=None):
        if cp == None or ville == None :
            return False
        for dictTemp in self.listeDonnees :
            IDcategorie_tarif = dictTemp["ID"]
            for cpTemp, villeTemp in dictTemp["listeVilles"] :
                if cp == cpTemp and ville == villeTemp :
                    self.SetID(IDcategorie_tarif)
                    return True
        return False



        
class CTRL_Activite(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.BORDER_THEME|wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDactivite = None
        couleur_fond = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.SetBackgroundColour(couleur_fond)

        self.ctrl_activite = wx.StaticText(self, -1, "")
        self.ctrl_activite.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_activite, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER, 0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()

    def MAJ(self):
        self.IDactivite = self.parent.dictActivite["IDactivite"]
        label = self.parent.dictActivite["nom"]
        self.ctrl_activite.SetLabel(label)
        self.Layout()

    def GetID(self):
        return self.IDactivite

    def GetNomActivite(self):
        return self.ctrl_activite.GetLabel()

# -----------------------------------------------------------------------------------------------------------------------------------------------


class CTRL_Parametres(wx.Notebook):
    def __init__(self, parent, mode="saisie", IDindividu=None, IDinscription=None, IDfamille=None, cp=None, ville=None):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT | wx.NB_MULTILINE)
        self.parent = parent
        self.dictPages = {}
        self.IDinscription = IDinscription
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille
        self.cp = cp
        self.ville = ville
        self.mode = mode

        self.listePages = [
            {"code": "activite", "ctrl": Page_Activite(self, self.IDinscription), "label": _(u"Param�tres"), "image": "Mecanisme.png"},
            {"code": "questionnaire", "ctrl": Page_Questionnaire(self, self.IDinscription), "label": _(u"Questionnaire"), "image": "Questionnaire.png"},
        ]

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        for dictPage in self.listePages:
            self.dictImages[dictPage["code"]] = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % dictPage["image"]), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Cr�ation des pages
        self.dictPages = {}
        index = 0
        for dictPage in self.listePages:
            self.AddPage(dictPage["ctrl"], dictPage["label"])
            self.SetPageImage(index, self.dictImages[dictPage["code"]])
            self.dictPages[dictPage["code"]] = dictPage["ctrl"]
            index += 1

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]

    def AffichePage(self, codePage=""):
        index = 0
        for dictPage in self.listePages:
            if dictPage["code"] == codePage:
                self.SetSelection(index)
            index += 1

    def OnPageChanged(self, event):
        """ Quand une page du notebook est s�lectionn�e """
        if event.GetOldSelection() == -1: return
        indexPage = event.GetSelection()
        page = self.GetPage(indexPage)
        self.Freeze()
        wx.CallLater(1, page.Refresh)
        self.Thaw()
        event.Skip()

    def Validation(self):
        for dictPage in self.listePages :
            if dictPage["ctrl"].Validation() == False :
                return False
        return True

    def Sauvegarde(self):
        for dictPage in self.listePages :
            if dictPage["ctrl"].Sauvegarde() == False :
                return False
        return True

    def SetTexteOnglet(self, code, texte=""):
        index = 0
        for dictPage in self.listePages :
            if dictPage["code"] == code :
                self.SetPageText(index, texte)
            index += 1



# -----------------------------------------------------------------------------------------------------------------------------------------------------------


class Page_Questionnaire(wx.Panel):
    def __init__(self, parent, IDinscription=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDinscription = IDinscription
        self.ctrl_questionnaire = CTRL_Questionnaire.CTRL(self, type="inscription", IDdonnee=self.IDinscription)
        self.ctrl_questionnaire.MAJ()

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.ctrl_questionnaire, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def Validation(self):
        return True



class Page_Activite(wx.Panel):
    def __init__(self, parent, IDinscription=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDinscription = IDinscription

        self.dictActivite = None
        self.IDgroupe = None
        self.date_inscription = datetime.date.today()
        self.dict_remboursement = None
        self.action_consommation = None
        self.ancien_statut = None

        # Activit�
        self.staticbox_activite_staticbox = wx.StaticBox(self, -1, _(u"Activit�"))
        self.ctrl_activite = CTRL_Activite(self)
        self.bouton_activites = CTRL_Bouton_image.CTRL(self, texte=_(u"Rechercher"), cheminImage="Images/32x32/Loupe.png")
        self.ctrl_activite.SetMinSize((-1, self.bouton_activites.GetSize()[1]))

        # Groupe
        self.staticbox_groupe_staticbox = wx.StaticBox(self, -1, _(u"Groupe"))
        self.ctrl_groupes = ListBox(self, type="groupes")
        self.ctrl_groupes.SetMinSize((-1, 50))

        # Cat�gorie
        self.staticbox_categorie_staticbox = wx.StaticBox(self, -1, _(u"Cat�gorie de tarif"))
        self.ctrl_categories = ListBox(self, type="categories")
        self.ctrl_categories.SetMinSize((-1, 50))

        # D�part
        self.staticbox_depart_staticbox = wx.StaticBox(self, -1, _(u"D�part de l'activit�"))
        self.ctrl_check_depart = wx.CheckBox(self, -1, _(u"L'individu ne fr�quente plus l'activit� depuis le"))
        self.ctrl_date_depart = CTRL_Saisie_date.Date2(self)
        self.ctrl_date_depart.SetDate(datetime.date.today())
        self.bouton_remboursement = wx.Button(self, -1, _(u"Remboursement"))

        # Properties
        self.ctrl_activite.SetToolTip(wx.ToolTip(_(u"Activit� s�lectionn�e")))
        self.bouton_activites.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour s�lectionner une activit�")))
        self.ctrl_groupes.SetToolTip(wx.ToolTip(_(u"S�lectionnez un groupe")))
        self.ctrl_check_depart.SetToolTip(wx.ToolTip(_(u"Cochez cette case si l'individu ne fr�quente plus cette activit�")))
        self.ctrl_date_depart.SetToolTip(wx.ToolTip(_(u"Saisissez la date de d�part de l'activit� (le dernier jour)")))
        self.bouton_remboursement.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour g�n�rer un remboursement li� au d�part de l'activit�")))
        self.ctrl_categories.SetToolTip(wx.ToolTip(_(u"S�lectionnez une cat�gorie de tarif")))

        # Bind
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActivites, self.bouton_activites)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDepart, self.ctrl_check_depart)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRemboursement, self.bouton_remboursement)

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)

        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)

        # Activit�s
        staticbox_activite = wx.StaticBoxSizer(self.staticbox_activite_staticbox, wx.VERTICAL)
        grid_sizer_activite = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_activite.Add(self.ctrl_activite, 1, wx.EXPAND, 0)
        grid_sizer_activite.Add(self.bouton_activites, 1, wx.EXPAND, 0)
        grid_sizer_activite.AddGrowableCol(0)
        staticbox_activite.Add(grid_sizer_activite, 1, wx.ALL | wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_activite, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 0)
        self.grid_sizer_activite = grid_sizer_activite

        # Groupes
        staticbox_groupe = wx.StaticBoxSizer(self.staticbox_groupe_staticbox, wx.VERTICAL)
        staticbox_groupe.Add(self.ctrl_groupes, 1, wx.ALL | wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_groupe, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 0)

        # Cat�gories de tarifs
        staticbox_categorie = wx.StaticBoxSizer(self.staticbox_categorie_staticbox, wx.VERTICAL)
        staticbox_categorie.Add(self.ctrl_categories, 1, wx.ALL | wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_categorie, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 0)

        # D�part
        staticbox_depart = wx.StaticBoxSizer(self.staticbox_depart_staticbox, wx.VERTICAL)
        grid_sizer_depart = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_depart.Add(self.ctrl_check_depart, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_depart.Add(self.ctrl_date_depart, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_depart.Add(self.bouton_remboursement, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_depart.Add(grid_sizer_depart, 1, wx.ALL | wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_depart, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)

        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

        # Init
        if self.parent.mode != "saisie" :
            self.bouton_activites.Show(False)
            self.Importation()

        if self.parent.mode == "saisie" :
            if self.parent.cp == None :
                # Recherche cp et ville
                dict_coords = UTILS_Titulaires.GetCoordsIndividu(self.parent.IDindividu)
                if dict_coords != None :
                    self.cp = dict_coords["cp_resid"]
                    self.ville = dict_coords["ville_resid"]

        self.OnCheckDepart()

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDactivite, IDgroupe, IDcategorie_tarif, date_inscription, date_desinscription, statut
        FROM inscriptions
        WHERE IDinscription=%d;""" % self.IDinscription
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            IDactivite, IDgroupe, IDcategorie_tarif, date_inscription, date_desinscription, statut = listeDonnees[0]
            self.SetIDactivite(IDactivite)
            self.ctrl_groupes.SetID(IDgroupe)
            self.IDgroupe = IDgroupe
            self.ctrl_categories.SetID(IDcategorie_tarif)
            self.date_inscription = UTILS_Dates.DateEngEnDateDD(date_inscription)
            if date_desinscription != None :
                date_desinscription = UTILS_Dates.DateEngEnDateDD(date_desinscription)
                self.ctrl_check_depart.SetValue(True)
                self.ctrl_date_depart.SetDate(date_desinscription)
            if statut != None :
                self.parent.parent.ctrl_statut.SetID(statut)
                self.ancien_statut = statut

    def Validation(self):
        IDactivite = self.GetIDactivite()
        if IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner une activit� !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        IDgroupe = self.ctrl_groupes.GetID()
        if IDgroupe == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un groupe !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        IDcategorie_tarif = self.ctrl_categories.GetID()
        if IDcategorie_tarif == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner une cat�gorie de tarifs !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        IDfamille = self.GetGrandParent().ctrl_famille.GetID()
        if IDfamille == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner une famille !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        nomActivite = self.ctrl_activite.GetNomActivite()

        statut = self.parent.parent.ctrl_statut.GetID()

        DB = GestionDB.DB()

        self.action_consommation = None

        # Date d�part
        if self.ctrl_check_depart.IsChecked():
            if self.ctrl_date_depart.GetDate() == None or self.ctrl_date_depart.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de d�part valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                DB.Close()
                return False

            if self.date_inscription != None and self.ctrl_date_depart.GetDate() < self.date_inscription :
                DB.Close()
                dlg = wx.MessageDialog(self, _(u"La date de d�part doit �tre sup�rieure ou �gale � la date d'inscription !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            date_desinscription = str(self.ctrl_date_depart.GetDate())

            # V�rifie que il n'existe pas des conso apr�s cette date
            if self.IDinscription != None :
                req = """SELECT IDconso, date
                FROM consommations
                WHERE IDinscription=%d AND date>'%s';""" % (self.IDinscription, date_desinscription)
                DB.ExecuterReq(req)
                listeConso = DB.ResultatReq()
                titre = _(u"Consommations existantes")
                introduction = _(u"Il existe %d consommations enregistr�es apr�s la date de d�part. ") % len(listeConso)
                introduction += _(u"Si vous les conservez elles seront consid�r�es comme gratuites. ")
                introduction += _(u"Voulez-vous les supprimer d�finitivement.")
                conclusion = _(u"Oui pour les supprimer.\n")
                conclusion += _(u"Non pour les conserver.")
                if len(listeConso) > 0 :
                    dlg = DLG_Messagebox.Dialog(
                        self,
                        titre=titre,
                        introduction=introduction,
                        conclusion=conclusion,
                        icone=wx.ICON_QUESTION,
                        boutons=[_(u"Oui"), _(u"Non"), _(u"Annuler")])
                    reponse = dlg.ShowModal()
                    dlg.Destroy()
                    if reponse == 0:
                        # Il faudra supprimer les consommations existantes
                        self.action_consommation = self.SupprimerConsommations
                    elif reponse == 1:
                        # Il faudra garder les consommations existantes
                        self.action_consommation = self.PreserverConsommations
                    else:
                        DB.Close()
                        return False


        # Verrouillage utilisateurs
        if self.parent.mode == "saisie" :
            action = "creer"
        else :
            action = "modifier"
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_inscriptions", action, IDactivite=IDactivite) == False :
            DB.Close()
            return False

        # V�rifie que l'individu n'est pas d�j� inscrit � cette activite
        if self.parent.mode == "saisie" and self.dictActivite["inscriptions_multiples"] != 1:
            req = """SELECT IDinscription, IDindividu, IDfamille
            FROM inscriptions
            WHERE IDindividu=%d AND IDfamille=%d AND IDactivite=%d;""" % (self.parent.IDindividu, IDfamille, IDactivite)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                DB.Close()
                dlg = wx.MessageDialog(self, _(u"Cet individu est d�j� inscrit � l'activit� '%s' !") % nomActivite, _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # V�rification du nombre d'inscrits max de l'activit�
        if (statut == "ok" and self.ancien_statut != "ok") or (IDgroupe != self.IDgroupe) :
            reponse = None

            if self.dictActivite["nbre_places_disponibles"] != None :
                if self.dictActivite["nbre_places_disponibles"] <= 0 :
                    intro = _(u"Le nombre maximal d'inscrits autoris� pour cette activit� (%d places max) a �t� atteint !\n\nQue souhaitez-vous faire ?") % self.dictActivite["nbre_inscrits_max"]
                    dlg = DLG_Messagebox.Dialog(self, titre=_(u"Nbre d'inscrit maximal atteint"), introduction=intro, detail=None, icone=wx.ICON_EXCLAMATION, boutons=[_(u"Valider quand m�me"), _(u"Mettre en attente"), _(u"Refuser"), _(u"Annuler")], defaut=1)
                    reponse = dlg.ShowModal()
                    dlg.Destroy()

            # V�rification du nombre d'inscrits max du groupe
            if reponse == None:
                for dictGroupe in self.dictActivite["groupes"] :
                    if dictGroupe["IDgroupe"] == IDgroupe and dictGroupe["nbre_places_disponibles"] != None :
                        if dictGroupe["nbre_places_disponibles"] <= 0 :
                            intro = _(u"Le nombre maximal d'inscrits autoris� sur ce groupe (%d places max) a �t� atteint !\n\nQue souhaitez-vous faire ?") % dictGroupe["nbre_inscrits_max"]
                            dlg = DLG_Messagebox.Dialog(self, titre=_(u"Nbre d'inscrit maximal atteint"), introduction=intro, detail=None, icone=wx.ICON_EXCLAMATION, boutons=[_(u"Valider quand m�me"), _(u"Mettre en attente"), _(u"Refuser"), _(u"Annuler")], defaut=1)
                            reponse = dlg.ShowModal()
                            dlg.Destroy()

            # Applique un statut � l'inscription
            if reponse != None :
                if reponse == 0:
                    self.parent.parent.ctrl_statut.SetID("ok")
                elif reponse == 1:
                    self.parent.parent.ctrl_statut.SetID("attente")
                elif reponse == 2:
                    self.parent.parent.ctrl_statut.SetID("refus")
                else:
                    DB.Close()
                    return False

        # Si changement de statut : V�rifie si l'individu n'a pas d�j� des prestations
        if self.IDinscription != None and statut != "ok" and self.ancien_statut == "ok" :
            req = """SELECT IDprestation, prestations.date, prestations.forfait
            FROM prestations
            WHERE IDactivite=%d AND IDindividu=%d
            ;""" % (IDactivite, self.parent.parent.IDindividu)
            DB.ExecuterReq(req)
            listePrestations = DB.ResultatReq()
            if len(listePrestations) > 0 :
                DB.Close()
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas modifier le statut de cette inscription car des prestations y ont d�j� �t� associ�es !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        DB.Close()
        return True

    def Sauvegarde(self):
        # R�cup�ration des donn�es � sauvegarder
        IDactivite = self.GetIDactivite()
        IDgroupe = self.ctrl_groupes.GetID()
        IDcategorie_tarif = self.ctrl_categories.GetID()
        nomGroupe = self.ctrl_groupes.GetStringSelection()
        nomCategorie = self.ctrl_categories.GetStringSelection()
        IDfamille = self.GetGrandParent().ctrl_famille.GetID()
        IDcompte_payeur = self.GetCompteFamille(IDfamille)
        nomActivite = self.ctrl_activite.GetNomActivite()
        if self.ctrl_check_depart.IsChecked():
            date_desinscription = str(self.ctrl_date_depart.GetDate())
        else :
            date_desinscription = None
        statut = self.parent.parent.ctrl_statut.GetID()

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDindividu", self.parent.IDindividu),
            ("IDfamille", IDfamille),
            ("IDactivite", IDactivite),
            ("IDgroupe", IDgroupe),
            ("IDcategorie_tarif", IDcategorie_tarif),
            ("IDcompte_payeur", IDcompte_payeur),
            ("date_desinscription", date_desinscription),
            ("statut", statut),
            ]
        if self.parent.mode == "saisie" :
            listeDonnees.append(("date_inscription", str(datetime.date.today())))
            self.IDinscription = DB.ReqInsert("inscriptions", listeDonnees)
        else :
            DB.ReqMAJ("inscriptions", listeDonnees, "IDinscription", self.IDinscription)

        # Cr�ation d'une prestation n�gative pour la famille correspondant au remboursement
        if self.dict_remboursement != None:
            listeDonnees = [
                ("IDcompte_payeur", IDcompte_payeur),
                ("date", str(datetime.date.today())),
                ("label", self.dict_remboursement["motif"]),
                ("montant_initial", -self.dict_remboursement["montant"]),
                ("montant", -self.dict_remboursement["montant"]),
                ("IDactivite", IDactivite),
                ("IDcategorie_tarif", IDcategorie_tarif),
                ("IDfamille", IDfamille),
                ("IDindividu", self.parent.IDindividu),
                ("categorie", "autre"),
                ("date_valeur", str(datetime.date.today())),
            ]
            DB.ReqInsert("prestations", listeDonnees)

        # Si une action consommation est n�cessaire, on l'ex�cute
        if self.action_consommation != None:
            self.action_consommation(DB, date_desinscription)

        DB.Commit()
        DB.Close()

        # M�morise l'action dans l'historique
        if self.parent.mode == "saisie" :
            IDcategorie_historique = 18
            texte_historique = _(u"Inscription � l'activit� '%s' sur le groupe '%s' avec la tarification '%s'") % (nomActivite, nomGroupe, nomCategorie)
        else :
            IDcategorie_historique = 20
            texte_historique = _(u"Modification de l'inscription � l'activit� '%s' sur le groupe '%s' avec la tarification '%s'") % (nomActivite, nomGroupe, nomCategorie)

        UTILS_Historique.InsertActions([{
            "IDindividu" : self.parent.IDindividu,
            "IDfamille" : IDfamille,
            "IDcategorie" : IDcategorie_historique,
            "action" : texte_historique,
            },])

        # Saisie de forfaits auto
        #if self.parent.mode == "saisie" :
        if statut == "ok" and self.ancien_statut != "ok" :
            f = DLG_Appliquer_forfait.Forfaits(IDfamille=IDfamille, listeActivites=[IDactivite,], listeIndividus=[self.parent.IDindividu,], saisieManuelle=False, saisieAuto=True)
            resultat = f.Applique_forfait(selectionIDcategorie_tarif=IDcategorie_tarif, inscription=True, selectionIDactivite=IDactivite, selectionIDinscription=self.IDinscription)
            if resultat == False :
                dlg = wx.MessageDialog(self, _(u"Cet individu a bien �t� inscrit mais le forfait associ� n'a pas �t� cr�� !"), _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()

        return self.IDinscription

    def GetCompteFamille(self, IDfamille=None):
        """ R�cup�re le compte_payeur par d�faut de la famille """
        DB = GestionDB.DB()
        req = """SELECT IDfamille, IDcompte_payeur
        FROM familles
        WHERE IDfamille=%d;""" % IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return None
        IDcompte_payeur = listeDonnees[0][1]
        return IDcompte_payeur

    def SupprimerConsommations(self, db, date_desinscription):
        req = "DELETE FROM consommations WHERE IDinscription=%d AND date>'%s';" % (self.IDinscription, date_desinscription)
        db.ExecuterReq(req)

    def PreserverConsommations(self, db, date_desinscription):
        req = "UPDATE consommations SET IDinscription=NULL WHERE IDinscription=%d AND date>'%s';" % (self.IDinscription, date_desinscription)
        db.ExecuterReq(req)

    def OnCheckDepart(self, event=None):
        """Sur check demande informations complementaires, sur uncheck reinscription."""
        self.ctrl_date_depart.Enable(self.ctrl_check_depart.IsChecked())
        self.bouton_remboursement.Enable(self.ctrl_check_depart.IsChecked())

    def OnBoutonRemboursement(self, event=None):
        """ G�n�rer un remboursement """
        dlg = DLG_Inscription_desinscription.Dialog(self)
        dlg.SetDonnees(self.dict_remboursement)
        if dlg.ShowModal() == wx.ID_OK :
            self.dict_remboursement = dlg.GetDonnees()
        dlg.Destroy()

    def OnBoutonActivites(self, event):
        dlg = DLG_Selection_activite.Dialog(self)
        dlg.SetIDactivite(self.GetIDactivite())
        if dlg.ShowModal() == wx.ID_OK:
            IDactivite = dlg.GetIDactivite()
            self.SetIDactivite(IDactivite)
        dlg.Destroy()

    def SetIDactivite(self, IDactivite=None):
        self.dictActivite = self.GetDictActivite(IDactivite)
        self.ctrl_activite.MAJ()
        self.ctrl_groupes.MAJ()
        self.ctrl_categories.MAJ()
        if self.parent.mode == "saisie" :
            self.ctrl_categories.SelectCategorieSelonVille(self.parent.cp, self.parent.ville)

    def CacheBoutonActivite(self):
        self.bouton_activites.Show(False)
        self.grid_sizer_activite.Layout()

    def SetIDgroupe(self, IDgroupe=None):
        self.ctrl_groupes.SetID(IDgroupe)

    def GetDictActivite(self, IDactivite=None):
        dictActivite = {}

        DB = GestionDB.DB()

        # Recherche des activit�s
        req = """SELECT nom, abrege, date_debut, date_fin, nbre_inscrits_max, inscriptions_multiples
        FROM activites
        WHERE IDactivite=%d;""" % IDactivite
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()

        nom, abrege, date_debut, date_fin, nbre_inscrits_max, inscriptions_multiples = listeActivites[0]
        dictActivite = {"IDactivite" : IDactivite, "nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin,
                        "nbre_inscrits_max" : nbre_inscrits_max, "inscriptions_multiples": inscriptions_multiples}

        # Recherche des inscriptions existantes
        req = """SELECT IDgroupe, COUNT(IDinscription)
        FROM inscriptions
        WHERE IDactivite=%d AND inscriptions.statut='ok'
        GROUP BY IDgroupe;""" % IDactivite
        DB.ExecuterReq(req)
        listeInscriptions = DB.ResultatReq()
        dictActivite["inscriptions"] = {}
        for IDgroupe, nbre_inscrits in listeInscriptions :
            dictActivite["inscriptions"][IDgroupe] = nbre_inscrits

        # Recherche des groupes
        req = """SELECT IDgroupe, nom, nbre_inscrits_max
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY ordre;""" % IDactivite
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()
        dictActivite["groupes"] = []
        for IDgroupe, nom, nbre_inscrits_max in listeGroupes :

            # Recherche le nombre d'inscrits sur chaque groupe
            if IDgroupe in dictActivite["inscriptions"] :
                nbre_inscrits = dictActivite["inscriptions"][IDgroupe]
            else :
                nbre_inscrits = 0

            # Recherche du nombre de places disponibles sur le groupe
            if nbre_inscrits_max not in (None, 0) :
                nbre_places_disponibles = nbre_inscrits_max - nbre_inscrits
            else :
                nbre_places_disponibles = None

            # M�morise le groupe
            dictActivite["groupes"].append({"IDgroupe" : IDgroupe, "nom" : nom, "nbre_places_disponibles" : nbre_places_disponibles, "nbre_inscrits" : nbre_inscrits, "nbre_inscrits_max" : nbre_inscrits_max})

        # Recherche le nombre d'inscrits total de l'activit�
        dictActivite["nbre_inscrits"] = 0
        for IDgroupe, nbre_inscrits in dictActivite["inscriptions"].items() :
            dictActivite["nbre_inscrits"] += nbre_inscrits

        # Recherche du nombre de places disponibles sur l'activit�
        if dictActivite["nbre_inscrits_max"] not in (None, 0) :
            dictActivite["nbre_places_disponibles"] = dictActivite["nbre_inscrits_max"] - dictActivite["nbre_inscrits"]
        else :
            dictActivite["nbre_places_disponibles"] = None

        # Recherche des cat�gories de tarifs
        req = """SELECT IDcategorie_tarif, nom
        FROM categories_tarifs
        WHERE IDactivite=%d
        ORDER BY nom; """ % IDactivite
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()

        # Recherche des villes rattach�es � la cat�gorie de tarif
        req = """SELECT IDville, IDcategorie_tarif, cp, nom
        FROM categories_tarifs_villes; """
        DB.ExecuterReq(req)
        listeVilles = DB.ResultatReq()

        dictVilles = {}
        for IDville, IDcategorie_tarif, cp, nom in listeVilles :
            if (IDcategorie_tarif in dictVilles) == False :
                dictVilles[IDcategorie_tarif] = []
            dictVilles[IDcategorie_tarif].append((cp, nom))

        dictActivite["categories_tarifs"] = []
        for IDcategorie_tarif, nom in listeCategories :
            if IDcategorie_tarif in dictVilles :
                listeVilles = dictVilles[IDcategorie_tarif]
            else:
                listeVilles = []
            dictActivite["categories_tarifs"].append({"IDcategorie_tarif" : IDcategorie_tarif, "nom" : nom, "listeVilles" : listeVilles})

        DB.Close()

        return dictActivite

    def GetIDactivite(self):
        if self.dictActivite != None :
            return self.dictActivite["IDactivite"]
        else :
            return None


# -----------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, mode="saisie", IDindividu=None, IDinscription=None, IDfamille=None, cp=None, ville=None, intro=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDindividu = IDindividu
        self.IDinscription = IDinscription
        self.IDfamille = IDfamille
        self.cp = cp
        self.ville = ville
        self.mode = mode

        if intro == None :
            intro = _(u"Pour inscrire un individu � une activit�, vous devez s�lectionner une activit�, un groupe et une cat�gorie de tarifs. Utilisez la case D�part pour indiquer que l'individu ne fr�quente plus l'activit�. Le questionnaire permet une saisie d'informations li�es � l'inscription.")
        if self.mode == "saisie" :
            titre = _(u"Saisie d'une inscription")
        else :
            titre = _(u"Modification d'une inscription")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")

        # Famille
        self.staticbox_famille = wx.StaticBox(self, -1, _(u"Famille rattach�e"))
        self.ctrl_famille = Choix_famille(self, IDindividu=self.IDindividu, verrouillage=self.mode!="saisie")

        # Famille
        self.staticbox_statut = wx.StaticBox(self, -1, _(u"Statut"))
        self.ctrl_statut = Choix_statut(self)

        # Param�tres
        self.ctrl_parametres = CTRL_Parametres(self, mode=mode, IDindividu=IDindividu, IDinscription=IDinscription, IDfamille=IDfamille, cp=cp, ville=ville)
        self.ctrl_parametres.SetMinSize((650, 460))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init contr�les
        self.ctrl_famille.SetID(self.IDfamille)

    def __set_properties(self):
        self.SetTitle(_(u"Inscription � une activit�"))
        self.ctrl_famille.SetToolTip(wx.ToolTip(_(u"S�lectionnez une famille")))
        self.ctrl_statut.SetToolTip(wx.ToolTip(_(u"S�lectionnez un statut")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Famille
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=10)

        staticbox_famille = wx.StaticBoxSizer(self.staticbox_famille, wx.VERTICAL)
        staticbox_famille.Add(self.ctrl_famille, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_options.Add(staticbox_famille, 1, wx.EXPAND, 0)

        staticbox_statut = wx.StaticBoxSizer(self.staticbox_statut, wx.VERTICAL)
        staticbox_statut.Add(self.ctrl_statut, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_options.Add(staticbox_statut, 1, wx.EXPAND, 0)

        grid_sizer_options.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Notebook
        grid_sizer_base.Add(self.ctrl_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
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
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()
    
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Activits1")

    def OnBoutonOk(self, event):
        # V�rification des donn�es saisies
        if self.ctrl_parametres.Validation() == False :
            return False

        # Sauvegarde
        DB = GestionDB.DB()
        self.IDinscription = self.ctrl_parametres.GetPageAvecCode("activite").Sauvegarde()
        self.ctrl_parametres.GetPageAvecCode("questionnaire").ctrl_questionnaire.Sauvegarde(DB=DB, IDdonnee=self.IDinscription)
        DB.Close()

        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)

    def GetPageActivite(self):
        return self.ctrl_parametres.GetPageAvecCode("activite")

    def GetIDinscription(self):
        return self.IDinscription

    def GetStatut(self):
        return self.ctrl_statut.GetID()




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
