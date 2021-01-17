#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.filebrowsebutton as filebrowse
import xlrd
import os
import datetime
import GestionDB
import time
import FonctionsPerso
from threading import Thread
from Ctrl import CTRL_Bandeau
from Utils import UTILS_Interface
from Utils import UTILS_Dates
from Utils import UTILS_Internet
from Ctrl.CTRL_ObjectListView import ObjectListView, FastObjectListView, ColumnDefn, Filter, CTRL_Outils
from Data import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()



class Track_modification(object):
    def __init__(self, action=None, label=None, IDfamille=None, track=None, ancienne_valeur=None, nouvelle_valeur=None, req=None, donnees=None):
        self.action = action
        self.label = label
        self.IDfamille = IDfamille
        self.track = track
        self.ancienne_valeur = ancienne_valeur
        self.nouvelle_valeur = nouvelle_valeur
        self.req = req
        self.donnees = donnees
        self.od_nom_complet = track.od_nom_complet



class Track_excel(object):
    def __init__(self, parent=None, ctrl_log=None, dict_champs={}, dict_ligne={}):
        self.parent = parent
        self.ctrl_log = ctrl_log
        self.liste_anomalies = []
        self.liste_ad = []

        # Valeur par défaut
        self.od_civilite = None
        self.od_nom_complet = None
        self.od_date_naiss = None
        self.od_rue = u""
        self.dict_ad = {}

        # Remplissage avec les valeurs
        for num_colonne, valeur in dict_ligne.items():

            # Récupère le nom de colonne original
            nom_colonne = dict_champs[num_colonne]

            # ------------------------------ OD -------------------------------------

            # OD Matricule
            if u"Matricule" in nom_colonne:
                self.od_matricule = valeur

            # OD Civilité
            if u"Libellé civilité" in nom_colonne:
                if u"Monsieur" in valeur:
                    self.od_civilite = 1
                if u"Mademoiselle" in valeur:
                    self.od_civilite = 2
                if u"Madame" in valeur:
                    self.od_civilite = 3

            # OD Nom et prénom
            if u"Nom+Prénom OD" in nom_colonne:
                valeur_temp = valeur.split("  ")
                if len(valeur_temp) >= 2:
                    self.od_nom = valeur_temp[0]
                    self.od_prenom = valeur_temp[1]
                    self.od_nom_complet = u"%s %s" % (self.od_nom, self.od_prenom)

            # OD Date de naissance
            if u"Date de naissance OD" in nom_colonne:
                self.od_date_naiss = valeur

            # OD Rue
            if u"Adresse domicile 1" in nom_colonne:
                if len(valeur) > 0:
                    self.od_rue += valeur
            if u"Adresse domicile 2" in nom_colonne:
                if len(valeur) > 0:
                    self.od_rue += u" - " + valeur
            if u"Adresse domicile 3" in nom_colonne:
                if len(valeur) > 0:
                    self.od_rue += u" - " + valeur
            self.od_rue = self.od_rue.replace('"', "")

            # OD Code postal
            if u"Code postal domicile" in nom_colonne:
                self.od_code_postal = valeur

            # OD Ville
            if u"Ville domicile" in nom_colonne:
                self.od_ville = valeur

            # OD Téléphone 1
            if nom_colonne == u"Téléphone personnel":
                valeur = valeur.replace(" ", "").replace(".", "")
                if len(valeur) == 10:
                    self.od_telephone_1 = "%s.%s.%s.%s.%s." % (valeur[0:2], valeur[2:4], valeur[4:6], valeur[6:8], valeur[8:10])

            # OD Téléphone 2
            if u"Téléphone personnel 2" in nom_colonne:
                valeur = valeur.replace(" ", "").replace(".", "")
                if len(valeur) == 10:
                    self.od_telephone_2 = "%s.%s.%s.%s.%s." % (valeur[0:2], valeur[2:4], valeur[4:6], valeur[6:8], valeur[8:10])

            # OD Mail personnel
            if u"E-Mail personnel" in nom_colonne:
                self.od_mail_perso = valeur

            # OD Mail interne
            if u"E-Mail interne" in nom_colonne:
                self.od_mail_travail = valeur

            # ------------------------------ AD -------------------------------------
            # AD Nom et prénom
            if u"Nom+Prénom AD" in nom_colonne:
                valeur_temp = valeur.split("  ")
                if len(valeur_temp) >= 2:
                    self.ad_nom = valeur_temp[0]
                    self.ad_prenom = valeur_temp[1]
                    self.ad_nom_complet = u"%s %s" % (self.ad_nom, self.ad_prenom)

            # AD Civilité
            if u"Sexe Ayant-droit" in nom_colonne or u"Sexe AD" in nom_colonne:
                if u"M" in valeur:
                    self.ad_civilite = 4
                if u"F" in valeur:
                    self.ad_civilite = 5

            # AD Date de naissance
            if u"Date de naissance AD" in nom_colonne:
                self.ad_date_naiss = valeur

        # Stocke les données de l'AD dans un dict
        self.dict_ad = {"nom": self.ad_nom, "prenom": self.ad_prenom, "nom_complet": self.ad_nom_complet, "date_naiss": self.ad_date_naiss, "IDcivilite": self.ad_civilite}
        self.liste_ad.append(self.dict_ad)


        # Recherche anomalies sur la ligne
        if self.od_civilite == None:
            self.liste_anomalies.append(u"La civilité de l'OD n'est pas valide")

        if self.od_nom_complet == None:
            self.liste_anomalies.append(u"Le nom complet de l'OD n'est pas valide")

        if self.od_date_naiss == None:
            self.liste_anomalies.append(u"La date de naissance de l'OD n'est pas valide")

        if self.ad_nom_complet == None:
            self.liste_anomalies.append(u"Le nom complet de l'AD n'est pas valide")

        if self.ad_civilite == None:
            self.liste_anomalies.append(u"La civilité de l'AD n'est pas valide")

        if self.ad_date_naiss == None:
            self.liste_anomalies.append(u"La date de naissance de l'AD n'est pas valide")

    def GetValeur(self, code=""):
        return getattr(self, code, None)


# ------------------------------------------------------------------------------------------------------------

class CTRL_Categories(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1, size=(-1, 80))
        self.parent = parent
        self.MAJ()

    def MAJ(self):
        """ items = (ID, label, checked) """
        liste_categories = [
            ("ajouter_famille", u"Ajouter une famille"),
            ("modifier_civilite",  u"Modifier la civilité"),
            ("modifier_rue",  u"Modifier la rue"),
            ("modifier_cp",  u"Modifier le code postal"),
            ("modifier_ville",  u"Modifier la ville"),
            ("modifier_tel_domicile", u"Modifier le tél domicile"),
            ("modifier_tel_portable",  u"Modifier le tél portable"),
            ("modifier_mail_perso",  u"Modifier le mail perso"),
            ("modifier_mail_travail",  u"Modifier le mail pro"),
            ("modifier_internet_identifiant", u"Modifier l'identifiant internet"),
            ("modifier_internet_mdp",  u"Modifier le mot de passe internet"),
            ("ajouter_individu",  u"Ajouter un individu AD"),
            ("modifier_enfant", u"Modifier un individu AD"),
        ]
        self.data = []
        index = 0
        for ID, label in liste_categories:
            self.data.append((ID, label))
            self.Append(label)
            self.Check(index)
            index += 1

    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches:
                self.Check(index)
            index += 1



# ------------------------------------------------------------------------------------------------------------

class CTRL_Donnees(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.donnees = []
        self.liste_categories = []
        self.ctrl_log = None
        self.nom_fichier = None
        FastObjectListView.__init__(self, *args, **kwds)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateValeur(valeur):
            if type(valeur) == datetime.date:
                return UTILS_Dates.DateEngFr(str(valeur))
            if valeur == None:
                return ""
            return valeur

        # Création des colonnes
        liste_colonnes = [
            ColumnDefn(_(u"Ouvrant-droit"), 'left', 200, "od_nom_complet", typeDonnee="texte"),
            ColumnDefn(_(u"Action"), 'left', 270, "label", typeDonnee="texte"),
            ColumnDefn(_(u"Ancienne valeur"), 'left', 180, "ancienne_valeur", typeDonnee="texte", stringConverter=FormateValeur),
            ColumnDefn(_(u"Nouvelle valeur"), 'left', 180, "nouvelle_valeur", typeDonnee="texte", stringConverter=FormateValeur),
            ]

        self.SetColumns(liste_colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune donnée"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)

    def SetTracks(self, tracks=[]):
        self.donnees = tracks
        self.MAJ()

    def MAJ(self):
        self.InitObjectListView()
        self._ResizeSpaceFillingColumns() 
        self.CocheTout()

    def OnCheck(self, event=None):
        texte = _(u"Sélection des modifications à appliquer (%d)") % len(self.GetTracksCoches())
        self.GetParent().box_donnees_staticbox.SetLabel(texte)

    def GetTracksCoches(self):
        listeCoches = []
        index = 0
        for track in self.donnees :
            if self.GetCheckState(track) == True :
                listeCoches.append(track)
            index += 1
        return listeCoches

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille correspondante"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)
        if len(self.Selection()) == 0:
            item.Enable(False)
        else:
            track = self.Selection()[0]
            if track.IDfamille == None:
                item.Enable(False)

        menuPop.AppendSeparator()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des modifications"))

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OuvrirFicheFamille(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, track.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

    def SetFichier(self, nom_fichier=""):
        self.nom_fichier = nom_fichier
        self.Analyse_fichier()

    def Analyse_fichier(self):
        self.SetTracks([])

        # Récupération des catégories
        self.liste_categories = self.GetParent().ctrl_categories.GetIDcoches()
        if len(self.liste_categories) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une catégorie !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Validation du fichier
        if self.nom_fichier == None or len(self.nom_fichier) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un fichier de données à importer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if os.path.isfile(self.nom_fichier) == False :
            dlg = wx.MessageDialog(self, _(u"L'emplacement fichier que vous avez saisi n'existe pas !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Ouverture du fichier Excel
        try:
            classeur = xlrd.open_workbook(self.nom_fichier)
            feuille = classeur.sheet_by_index(0)
        except:
            dlg = wx.MessageDialog(self, _(u"Impossible d'ouvrir ce fichier Excel !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        self.ctrl_log.Ecrit(u"Lecture du fichier %s..." % self.nom_fichier)

        # Lecture des noms de champs
        dict_champs = {}
        for num_colonne in range(feuille.ncols):
            dict_champs[num_colonne] = feuille.cell(rowx=0, colx=num_colonne).value

        # Vérifie que les champs essentiels sont là
        champs_obligatoires = [
            u"Matricule Ouvrant-droit", u"Libellé civilité", u"Nom+Prénom OD", u"Date de naissance OD", u"Adresse domicile 1",
            u"Adresse domicile 2", u"Adresse domicile 3", u"Code postal domicile", u"Ville domicile",
            u"Téléphone personnel", u"Téléphone personnel 2", u"E-Mail personnel", u"E-Mail interne",
            u"Nom+Prénom AD", u"Sexe AD", u"Date de naissance AD",
            ]
        champs_manquants = []
        for champ in champs_obligatoires:
            present = False
            for num_colonne, nom_colonne in dict_champs.items():
                if champ == nom_colonne :
                    present = True
            if present == False:
                champs_manquants.append(champ)

        if len(champs_manquants) > 0:
            self.ctrl_log.Ecrit(u"[ERREUR] Il manque les champs suivants dans le fichier Excel : %s." % u", ".join(champs_manquants))
            dlg = wx.MessageDialog(self, _(u"Il manque les champs suivants dans le fichier Excel :\n\n- %s") % u"\n- ".join(champs_manquants), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Lecture des lignes de données
        self.ctrl_log.Ecrit(u"%d lignes trouvées dans le fichier." % feuille.nrows)
        dict_tracks = {}
        for num_ligne in range(1, feuille.nrows):
            dict_ligne = {}
            for num_colonne in range(feuille.ncols):
                # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
                case = feuille.cell(rowx=num_ligne, colx=num_colonne)
                valeur = case.value

                # Date
                if case.ctype == 3:
                    dateTuple = xlrd.xldate_as_tuple(case.value, classeur.datemode)
                    valeur = datetime.date(*dateTuple[:3])

                dict_ligne[num_colonne] = valeur

            # Mémorisation dans un track
            track = Track_excel(self, self.ctrl_log, dict_champs, dict_ligne)
            if len(track.liste_anomalies) == 0:

                if track.od_matricule not in dict_tracks:
                    # Si le matricule n'est pas dans la liste, on mémorise le track
                    dict_tracks[track.od_matricule] = track
                else:
                    # Si le matricule existe déjà, on rajoute juste le dict_ad au track existant
                    dict_tracks[track.od_matricule].liste_ad.append(track.dict_ad)

            else:
                self.ctrl_log.Ecrit(u"%d anomalies sur la ligne %d : %s" % (len(track.liste_anomalies), num_ligne, u" / ".join(track.liste_anomalies)))

        # Importation des données de la base
        DB = GestionDB.DB()

        # Importation de tous les individus
        req = """SELECT IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid, tel_domicile, tel_mobile, mail, travail_tel, travail_mail
        FROM individus;"""
        DB.ExecuterReq(req)
        liste_individus = DB.ResultatReq()
        dict_individus = {}
        dict_date_naiss = {}
        for IDindividu, IDcivilite, nom, prenom, date_naiss, adresse_auto, rue_resid, cp_resid, ville_resid, tel_domicile, tel_mobile, mail, travail_tel, travail_mail in liste_individus:
            date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)
            nom_complet = nom
            if prenom != None: nom_complet += u" " + prenom
            # Mémorisation du dict individu
            dict_individus[IDindividu] = {
                "IDcivilite" : IDcivilite, "nom" : nom, "prenom" : prenom, "date_naiss" : date_naiss, "adresse_auto": adresse_auto,
                "rue_resid" : rue_resid, "cp_resid": cp_resid, "ville_resid" : ville_resid, "tel_domicile" : tel_domicile,
                "tel_mobile" : tel_mobile, "mail": mail, "travail_tel" : travail_tel, "travail_mail" : travail_mail, "nom_complet": nom_complet,
                "familles" : []
            }

            # Mémorisation par date de naissance
            if date_naiss not in dict_date_naiss:
                dict_date_naiss[date_naiss] = []
            dict_date_naiss[date_naiss].append(IDindividu)

        # Importation de toutes les familles
        req = """SELECT IDfamille, internet_identifiant, internet_mdp
        FROM familles;"""
        DB.ExecuterReq(req)
        liste_familles = DB.ResultatReq()
        dict_familles = {}
        for IDfamille, internet_identifiant, internet_mdp in liste_familles:
            dict_familles[IDfamille] = {"internet_identifiant": internet_identifiant, "internet_mdp": internet_mdp, "individus": []}

        # Importation de tous les rattachements
        req = """SELECT IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire
        FROM rattachements;"""
        DB.ExecuterReq(req)
        liste_rattachements = DB.ResultatReq()
        for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire in liste_rattachements:

            # Mémorise l'IDfamille dans le dict_individus
            if titulaire == 1:
                if IDindividu in dict_individus:
                    dict_individus[IDindividu]["familles"].append(IDfamille)

            # Mémorise les membres de la famille dans le dict_familles
            if IDfamille in dict_familles:
                dict_familles[IDfamille]["individus"].append(IDindividu)

        DB.Close()

        # Analyse des tracks du fichier Excel
        def Recherche_individu(nom=None, prenom=None, date_naiss=None):
            if date_naiss in dict_date_naiss:
                for IDindividu in dict_date_naiss[date_naiss]:
                    dict_individu = dict_individus[IDindividu]
                    if nom != None and dict_individu["nom"].lower() == nom.lower() and dict_individu["prenom"].lower() == prenom.lower():
                        return IDindividu
            return None

        IDfichier = FonctionsPerso.GetIDfichier()

        liste_modif = []
        liste_antidoublons = []

        def AjouterModification(track=None):
            antidoublon = (track.action, track.req, track.track.od_nom_complet)
            if antidoublon not in liste_antidoublons:
                liste_antidoublons.append(antidoublon)
                liste_modif.append(track)

        for track in dict_tracks.values():

            # Recherche si l'OD existe dans la base
            IDindividu_od = Recherche_individu(track.GetValeur("od_nom"), track.GetValeur("od_prenom"), track.GetValeur("od_date_naiss"))

            # Si l'OD n'existe pas, on propose de le créer
            if IDindividu_od == None:
                label = u"Création d'une nouvelle famille"
                if "ajouter_famille" in self.liste_categories:
                    AjouterModification(Track_modification(action="ajouter_famille", label=label, track=track))

            # Si l'OD existe déjà dans la base, on vérifie les données
            if IDindividu_od != None:
                dict_individu = dict_individus[IDindividu_od]

                # Recherche la famille de l'OD
                if len(dict_individu["familles"]) == 1:
                    IDfamille = dict_individu["familles"][0]
                    liste_individus = dict_familles[IDfamille]["individus"]
                else:
                    IDfamille = None
                    liste_individus = []
                    self.ctrl_log.Ecrit(u"[ERREUR] Aucune famille pour l'OD %s" % track.GetValeur("od_nom_complet"))

                # Vérification OD - Civilité
                if dict_individu["IDcivilite"] != track.GetValeur("od_civilite"):
                    IDcivilite = track.GetValeur("od_civilite")
                    if IDcivilite != None:

                        label = u"Changement de civilité"
                        if dict_individu["IDcivilite"] in DICT_CIVILITES:
                            ancienne_valeur = DICT_CIVILITES[dict_individu["IDcivilite"]]["civiliteAbrege"]
                        else:
                            ancienne_valeur = u""
                        if IDcivilite != None:
                            nouvelle_valeur = DICT_CIVILITES[IDcivilite]["civiliteAbrege"]
                        else:
                            nouvelle_valeur = 1
                        req = {"table": "individus", "nom_champ": "IDcivilite", "valeur": IDcivilite, "nom_key": "IDindividu", "valeur_key": IDindividu_od}
                        if "modifier_civilite" in self.liste_categories:
                            AjouterModification(Track_modification(action="modifier", label=label, track=track, IDfamille=IDfamille, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))

                # Vérification OD - Rue
                if dict_individu["adresse_auto"] == None and dict_individu["rue_resid"] != track.GetValeur("od_rue"):
                    label = u"Changement de rue"
                    ancienne_valeur = dict_individu["rue_resid"]
                    nouvelle_valeur = track.GetValeur("od_rue")
                    req = {"table": "individus", "nom_champ": "rue_resid", "valeur": nouvelle_valeur, "nom_key": "IDindividu", "valeur_key": IDindividu_od}
                    if "modifier_rue" in self.liste_categories:
                        AjouterModification(Track_modification(action="modifier", label=label, track=track, IDfamille=IDfamille, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))

                # Vérification OD - Code postal
                if dict_individu["adresse_auto"] == None and dict_individu["cp_resid"] != track.GetValeur("od_code_postal"):
                    label = u"Changement de code postal"
                    ancienne_valeur = dict_individu["cp_resid"]
                    nouvelle_valeur = track.GetValeur("od_code_postal")
                    req = {"table": "individus", "nom_champ": "cp_resid", "valeur": nouvelle_valeur, "nom_key": "IDindividu", "valeur_key": IDindividu_od}
                    if "modifier_cp" in self.liste_categories:
                        AjouterModification(Track_modification(action="modifier", label=label, track=track, IDfamille=IDfamille, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))

                # Vérification OD - Ville
                if dict_individu["adresse_auto"] == None and dict_individu["ville_resid"] != track.GetValeur("od_ville"):
                    label = u"Changement de ville"
                    ancienne_valeur = dict_individu["ville_resid"]
                    nouvelle_valeur = track.GetValeur("od_ville")
                    req = {"table": "individus", "nom_champ": "ville_resid", "valeur": nouvelle_valeur, "nom_key": "IDindividu", "valeur_key": IDindividu_od}
                    if "modifier_ville" in self.liste_categories:
                        AjouterModification(Track_modification(action="modifier", label=label, track=track, IDfamille=IDfamille, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))

                # Vérification OD - Téléphone 1
                if dict_individu["tel_domicile"] != track.GetValeur("od_telephone_1") and track.GetValeur("od_telephone_1") != "":
                    label = u"Changement de téléphone fixe"
                    ancienne_valeur = dict_individu["tel_domicile"]
                    nouvelle_valeur = track.GetValeur("od_telephone_1")
                    req = {"table": "individus", "nom_champ": "tel_domicile", "valeur": nouvelle_valeur, "nom_key": "IDindividu", "valeur_key": IDindividu_od}
                    if "modifier_tel_domicile" in self.liste_categories:
                        AjouterModification(Track_modification(action="modifier", label=label, track=track, IDfamille=IDfamille, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))

                # Vérification OD - Téléphone 2
                if dict_individu["tel_mobile"] != track.GetValeur("od_telephone_2") and track.GetValeur("od_telephone_2") != "":
                    label = u"Changement de téléphone mobile"
                    ancienne_valeur = dict_individu["tel_mobile"]
                    nouvelle_valeur = track.GetValeur("od_telephone_2")
                    req = {"table": "individus", "nom_champ": "tel_mobile", "valeur": nouvelle_valeur, "nom_key": "IDindividu", "valeur_key": IDindividu_od}
                    if "modifier_tel_portable" in self.liste_categories:
                        AjouterModification(Track_modification(action="modifier", label=label, track=track, IDfamille=IDfamille, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))

                # OD Mail personnel
                if dict_individu["mail"] != track.GetValeur("od_mail_perso") and track.GetValeur("od_mail_perso") != "":
                    label = u"Changement de mail personnel"
                    ancienne_valeur = dict_individu["mail"]
                    nouvelle_valeur = track.GetValeur("od_mail_perso")
                    req = {"table": "individus", "nom_champ": "mail", "valeur": nouvelle_valeur, "nom_key": "IDindividu", "valeur_key": IDindividu_od}
                    if "modifier_mail_perso" in self.liste_categories:
                        AjouterModification(Track_modification(action="modifier", label=label, track=track, IDfamille=IDfamille, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))

                # OD Mail interne
                if dict_individu["travail_mail"] != track.GetValeur("od_mail_travail") and track.GetValeur("od_mail_travail") != "":
                    label = u"Changement de mail professionnel"
                    ancienne_valeur = dict_individu["travail_mail"]
                    nouvelle_valeur = track.GetValeur("od_mail_travail")
                    req = {"table": "individus", "nom_champ": "travail_mail", "valeur": nouvelle_valeur, "nom_key": "IDindividu", "valeur_key": IDindividu_od}
                    if "modifier_mail_travail" in self.liste_categories:
                        AjouterModification(Track_modification(action="modifier", label=label, track=track, IDfamille=IDfamille, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))

                # Vérifie si l'identifiant internet est ok
                if IDfamille != None:
                    internet_identifiant = dict_familles[IDfamille]["internet_identifiant"]
                    if internet_identifiant != track.GetValeur("od_matricule"):
                        label = u"Changement d'identifiant internet"
                        ancienne_valeur = internet_identifiant
                        nouvelle_valeur = track.GetValeur("od_matricule")
                        req = {"table": "familles", "nom_champ": "internet_identifiant", "valeur": nouvelle_valeur, "nom_key": "IDfamille", "valeur_key": IDfamille}
                        if "modifier_internet_identifiant" in self.liste_categories:
                            AjouterModification(Track_modification(action="modifier", label=label, track=track, IDfamille=IDfamille, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))

                # Vérifie si le mot de passe internet est ok
                if IDfamille != None:
                    internet_mdp = dict_familles[IDfamille]["internet_mdp"]
                    if internet_mdp.startswith("#@#"):
                        internet_mdp = UTILS_Internet.DecrypteMDP(internet_mdp, IDfichier=IDfichier)
                    mdp_defaut = track.GetValeur("od_date_naiss").strftime("%d%m%Y")
                    if internet_mdp.startswith("custom") == False and internet_mdp != mdp_defaut:
                        label = u"Changement de mot de passe internet"
                        ancienne_valeur = internet_mdp
                        nouvelle_valeur = mdp_defaut
                        req = {"table": "familles", "nom_champ": "internet_mdp", "valeur": nouvelle_valeur, "nom_key": "IDfamille", "valeur_key": IDfamille}
                        if "modifier_internet_mdp" in self.liste_categories:
                            AjouterModification(Track_modification(action="modifier", label=label, track=track, IDfamille=IDfamille, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))

                # Recherche des modifications chez les Ayants-droits
                if IDfamille != None:
                    for dict_ad in track.liste_ad:

                        # Recherche si l'individu existe dans la base de données
                        IDindividu_ad = Recherche_individu(dict_ad["nom"], dict_ad["prenom"], dict_ad["date_naiss"])
                        if IDindividu_ad == None:
                            label = u"Création de l'individu %s" % dict_ad["nom_complet"]
                            donnees = {"IDfamille": IDfamille, "IDindividu_od": IDindividu_od, "dict_ad": dict_ad}
                            if "ajouter_individu" in self.liste_categories:
                                AjouterModification(Track_modification(action="ajouter_individu", label=label, IDfamille=IDfamille, track=track, donnees=donnees))

                        if IDindividu_ad != None and IDindividu_ad not in liste_individus:
                            pass
                            # self.ctrl_log.Ecrit(u"Bizarre, l'individu %s %s existe dans la base mais n'est pas rattaché à la famille" % (dict_ad["nom"], dict_ad["prenom"]))

                        if IDindividu_ad != None and IDindividu_ad in liste_individus:
                            # On vérifie si les données de l'ad sont exactes
                            dict_individu = dict_individus[IDindividu_ad]

                            # Civilité
                            if dict_individu["IDcivilite"] != dict_ad["IDcivilite"]:
                                IDcivilite = dict_ad["IDcivilite"]

                                label = u"Changement de civilité"
                                if dict_individu["IDcivilite"] in DICT_CIVILITES:
                                    ancienne_valeur = DICT_CIVILITES[dict_individu["IDcivilite"]]["civiliteAbrege"]
                                else:
                                    ancienne_valeur = u""
                                nouvelle_valeur = DICT_CIVILITES[IDcivilite]["civiliteAbrege"]
                                # req = "UPDATE individus SET IDcivilite=%d WHERE IDindividu=%s" % (IDcivilite, IDindividu_ad)
                                req = {"table": "individus", "nom_champ": "IDcivilite", "valeur": IDcivilite, "nom_key": "IDindividu", "valeur_key": IDindividu_ad}
                                if "modifier_enfant" in self.liste_categories:
                                    AjouterModification(Track_modification(action="modifier", label=label, IDfamille=IDfamille, track=track, ancienne_valeur=ancienne_valeur, nouvelle_valeur=nouvelle_valeur, req=req))


        # Envoi des modifications vers le listview
        self.SetTracks(liste_modif)



# ---------------------------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Sélection du fichier
        self.box_fichier_staticbox = wx.StaticBox(self, -1, _(u"Sélection du fichier"))
        self.label_fichier = wx.StaticText(self, -1, _(u"Cliquez sur le bouton 'Sélectionner' pour sélectionner le fichier de données :"))
        wildcard = _(u"Fichiers Excel (*.xls)|*.xls|Tous les fichiers (*.*)|*.*")
        sp = wx.StandardPaths.Get()
        self.ctrl_fichier = filebrowse.FileBrowseButton(self, -1, labelText=_(u"Fichier à importer :"), buttonText=_(u"Sélectionner"), toolTip=_(u"Cliquez ici pour sélectionner un fichier de données"), dialogTitle=_(u"Sélectionner un fichier"), fileMask=wildcard, startDirectory=sp.GetDocumentsDir(), changeCallback=self.OnSelectionFichier)

        # Catégories des modifications
        self.box_categories_staticbox = wx.StaticBox(self, -1, _(u"Catégories des modifications"))
        self.ctrl_categories = CTRL_Categories(self)
        self.ctrl_categories.SetMinSize((250, 20))
        self.ctrl_appliquer_categories = wx.Button(self, -1, u"Appliquer")

        # Liste de données
        self.box_donnees_staticbox = wx.StaticBox(self, -1, _(u"Sélection des modifications à appliquer"))
        self.label_donnees = wx.StaticText(self, -1, _(u"Cochez les données à modifier puis cliquez sur le bouton Appliquer :"))
        self.ctrl_donnees = CTRL_Donnees(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_recherche = CTRL_Outils(self, listview=self.ctrl_donnees, afficherCocher=True)

        # Log
        self.box_log_staticbox = wx.StaticBox(self, -1, _(u"Journal"))
        self.ctrl_log = CTRL_Log(self)
        self.ctrl_log.SetMinSize((100, 80))
        self.ctrl_donnees.ctrl_log = self.ctrl_log

        # Bind
        self.Bind(wx.EVT_BUTTON, self.OnAppliquerCategories, self.ctrl_appliquer_categories)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=10, cols=1, vgap=10, hgap=10)

        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        box_fichier = wx.StaticBoxSizer(self.box_fichier_staticbox, wx.VERTICAL)
        sizer_fichier = wx.BoxSizer(wx.VERTICAL)
        sizer_fichier.Add(self.label_fichier, 0, wx.EXPAND, 0)
        sizer_fichier.Add(self.ctrl_fichier, 0, wx.TOP|wx.EXPAND, 10)
        box_fichier.Add(sizer_fichier, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(box_fichier, 1, wx.EXPAND, 0)

        box_categories = wx.StaticBoxSizer(self.box_categories_staticbox, wx.VERTICAL)
        sizer_categories = wx.BoxSizer(wx.HORIZONTAL)
        sizer_categories.Add(self.ctrl_categories, 0, wx.EXPAND, 0)
        sizer_categories.Add(self.ctrl_appliquer_categories, 0, wx.LEFT|wx.EXPAND, 10)
        box_categories.Add(sizer_categories, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(box_categories, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)

        box_donnees = wx.StaticBoxSizer(self.box_donnees_staticbox, wx.VERTICAL)
        sizer_donnees = wx.BoxSizer(wx.VERTICAL)
        sizer_donnees.Add(self.label_donnees, 0, 0, 0)
        sizer_donnees.Add(self.ctrl_donnees, 1, wx.TOP|wx.EXPAND, 10)
        sizer_donnees.Add(self.ctrl_recherche, 0, wx.TOP | wx.EXPAND, 5)
        box_donnees.Add(sizer_donnees, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_donnees, 1, wx.EXPAND, 0)

        box_log = wx.StaticBoxSizer(self.box_log_staticbox, wx.VERTICAL)
        sizer_log = wx.BoxSizer(wx.VERTICAL)
        sizer_log.Add(self.ctrl_log, 1, wx.ALL|wx.EXPAND, 0)
        box_log.Add(sizer_log, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_log, 1, wx.EXPAND, 0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)

    def OnSelectionFichier(self, event=None):
        self.ctrl_donnees.SetFichier(event.GetString())

    def OnAppliquerCategories(self, event=None):
        self.ctrl_donnees.Analyse_fichier()


# ----------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Log(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, u"", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)

    def Ecrit(self, message=""):
        horodatage = time.strftime("%d/%m/%y %H:%M:%S", time.localtime())
        if len(self.GetValue()) >0 :
            texte = u"\n"
        else :
            texte = u""
        try :
            texte += u"[%s] %s " % (horodatage, message)
        except :
            texte += u"[%s] %s " % (horodatage, str(message).decode("iso-8859-15"))
        self.AppendText(texte)

        # Surlignage des erreurs
        if "[ERREUR]" in texte :
            self.SetStyle(self.GetInsertionPoint()-len(texte), self.GetInsertionPoint()-1, wx.TextAttr("RED", "YELLOW"))



# ----------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.dictDonnees = {}

        # Intro
        intro = _(u"Cet assistant permet d'importer des individus depuis un fichier Excel.")
        titre = _(u"Assistant d'importation d'individus")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Document_import.png")

        # Panel
        self.panel = Panel(self)
        self.ctrl_log = self.panel.ctrl_log

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Synchroniser"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
        self.__set_properties()
        self.__do_layout()
                
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez pour lancer la synchronisation")))
        self.SetMinSize((950, 800))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        # Contenu
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(self.panel, 1, wx.ALL|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        self.sizer_pages = sizer_pages
    
    def Onbouton_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        tracks = self.panel.ctrl_donnees.GetTracksCoches()

        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la synchronisation de %d informations ?\n\nAttention, il est conseillé de procéder à une sauvegarde des données auparavant.") % len(tracks), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Lancement de la synchro
        synchro = Synchronisation(self, tracks=tracks)
        synchro.start()
        return True


class Synchronisation(Thread):
    def __init__(self, parent, tracks=[]):
        Thread.__init__(self)
        self.parent = parent
        self.ctrl_log = self.parent.ctrl_log
        self.tracks = tracks

    def run(self):
        self.ctrl_log.Ecrit(u"Lancement de la synchronisation...")
        DB = GestionDB.DB()

        index = 0
        for track_modification in self.tracks:
            self.ctrl_log.Ecrit(u"%s pour %s..." % (track_modification.label, track_modification.od_nom_complet))

            def Creer_individu(IDfamille, ID_od, dict_ad):
                # self.ctrl_log.Ecrit(u"Création de l'individu %s %s..." % (dict_ad["nom"], dict_ad["prenom"]))
                ID_ad = DB.ReqInsert("individus", [("IDcivilite", dict_ad["IDcivilite"]), ("nom", dict_ad["nom"]),
                                                   ("prenom", dict_ad["prenom"]), ("date_naiss", dict_ad["date_naiss"]),
                                                   ("deces", 0), ("IDnationalite", 73), ("IDpays_naiss", 73),
                                                   ("adresse_auto", ID_od), ("date_creation", datetime.date.today()), ])
                # Rattachement
                DB.ReqInsert("rattachements", [("IDindividu", ID_ad), ("IDfamille", IDfamille), ("IDcategorie", 2), ("titulaire", 0)])

                # Liens
                if track_modification.track.od_civilite == 1:
                    DB.ReqInsert("liens", [("IDfamille", IDfamille), ("IDindividu_sujet", ID_ad), ("IDtype_lien", 2), ("IDindividu_objet", ID_od)])
                    DB.ReqInsert("liens", [("IDfamille", IDfamille), ("IDindividu_sujet", ID_od), ("IDtype_lien", 1), ("IDindividu_objet", ID_ad)])
                else:
                    DB.ReqInsert("liens", [("IDfamille", IDfamille), ("IDindividu_sujet", ID_ad), ("IDtype_lien", 2), ("IDindividu_objet", ID_od)])
                    DB.ReqInsert("liens", [("IDfamille", IDfamille), ("IDindividu_sujet", ID_od), ("IDtype_lien", 1), ("IDindividu_objet", ID_ad)])

                # Inscriptions
                # IDinscription = DB.ReqInsert("inscriptions",
                #                              [("IDindividu", IDenfant), ("IDfamille", IDfamille), ("IDactivite", 1),
                #                               ("IDgroupe", 1), ("IDcategorie_tarif", 1),
                #                               ("IDcompte_payeur", IDcompte_payeur),
                #                               ("date_inscription", datetime.date.today()), ("parti", 0)])

            # Modifier une donnée
            if track_modification.action == "modifier":
                DB.ReqMAJ(track_modification.req["table"], [(track_modification.req["nom_champ"], track_modification.req["valeur"]), ], track_modification.req["nom_key"], track_modification.req["valeur_key"])
                DB.Commit()

            # Ajouter un individu
            if track_modification.action == "ajouter_individu":
                Creer_individu(track_modification.donnees["IDfamille"], track_modification.donnees["IDindividu_od"], track_modification.donnees["dict_ad"])

            # Ajouter une famille
            if track_modification.action == "ajouter_famille":
                track_excel = track_modification.track
                # print "Famille", ("nom", track_excel.od_nom), ("prenom", track_excel.od_prenom)

                # Famille
                IDfamille = DB.ReqInsert("familles", [("date_creation", datetime.date.today()),
                                                      ("IDcompte_payeur", None),
                                                      ("internet_actif", 1),
                                                      ("internet_identifiant", track_excel.GetValeur("od_matricule")),
                                                      ("internet_mdp", track_excel.GetValeur("od_date_naiss").strftime("%d%m%Y")),
                                                      ])

                IDcompte_payeur = DB.ReqInsert("comptes_payeurs", [("IDfamille", IDfamille), ])
                DB.ReqMAJ("familles", [("IDcompte_payeur", IDcompte_payeur), ], "IDfamille", IDfamille)

                # Création de l'OD
                ID_od = DB.ReqInsert("individus", [("IDcivilite", track_excel.od_civilite),
                                                    ("nom", track_excel.od_nom),
                                                    ("prenom", track_excel.od_prenom),
                                                    ("date_naiss", track_excel.od_date_naiss),
                                                    ("rue_resid", track_excel.od_rue),
                                                    ("cp_resid", track_excel.od_code_postal),
                                                    ("ville_resid", track_excel.od_ville),
                                                    ("tel_domicile", getattr(track_excel, "od_telephone_1", None)),
                                                    ("tel_mobile", getattr(track_excel, "od_telephone_2", None)),
                                                    ("mail", getattr(track_excel, "od_mail_perso", None)),
                                                    ("travail_mail", getattr(track_excel, "od_mail_travail", None)),
                                                    ("deces", 0),
                                                    ("IDnationalite", 73),
                                                    ("IDpays_naiss", 73),
                                                    ("date_creation", datetime.date.today()),
                                                     ])

                DB.ReqInsert("rattachements", [("IDindividu", ID_od), ("IDfamille", IDfamille), ("IDcategorie", 1), ("titulaire", 1)])

                # Création des AD
                for dict_ad in track_excel.liste_ad:
                    Creer_individu(IDfamille, ID_od, dict_ad)

            index += 1

        DB.Close()
        self.ctrl_log.Ecrit(u"Synchronisation terminée.")




if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
