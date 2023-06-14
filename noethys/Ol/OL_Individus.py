#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _

import wx
import time
import datetime
import GestionDB
from Data import DATA_Civilites as Civilites
from Utils import UTILS_Titulaires
from Utils import UTILS_Dates


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils import UTILS_Utilisateurs

try :
    import smartcard
except :
    pass



def GetRattachements(IDindividu):
    # R�cup�ration des rattachements dans la base
    DB = GestionDB.DB()
    req = """SELECT IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire
    FROM rattachements
    WHERE IDindividu=%d
    ;""" % IDindividu
    DB.ExecuterReq(req)
    listeRattachements = DB.ResultatReq()
    DB.Close()

    # Recherche des rattachements
    dictTitulaires = {}
    if len(listeRattachements) == 0:
        rattachements = None
        dictTitulaires = {}
        txtTitulaires = _(u"Rattach� � aucune famille")
    elif len(listeRattachements) == 1:
        IDfamille = listeRattachements[0][2]
        IDcategorie = listeRattachements[0][3]
        titulaire = listeRattachements[0][4]
        rattachements = [(IDcategorie, IDfamille, titulaire)]
        dictTitulaires[IDfamille] = GetNomsTitulaires(IDfamille)
        txtTitulaires = dictTitulaires[IDfamille]
    else:
        rattachements = []
        txtTitulaires = ""
        for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire in listeRattachements:
            rattachements.append((IDcategorie, IDfamille, titulaire))
            nomsTitulaires = GetNomsTitulaires(IDfamille)
            dictTitulaires[IDfamille] = nomsTitulaires
            txtTitulaires += nomsTitulaires + u" | "
        if len(txtTitulaires) > 0:
            txtTitulaires = txtTitulaires[:-2]

    return rattachements, dictTitulaires, txtTitulaires


def GetNomsTitulaires(IDfamille=None):
    dictTitulaires = UTILS_Titulaires.GetTitulaires(listeIDfamille=[IDfamille, ])
    if IDfamille in dictTitulaires:
        noms = dictTitulaires[IDfamille]["titulairesSansCivilite"]
    else:
        noms = "?"
    return noms




class Track(object):
    def __init__(self, donnees, dictIndividus):
        self.IDindividu = donnees["individus.IDindividu"]
        self.IDcivilite = donnees["IDcivilite"]
        self.nom = donnees["nom"]
        self.prenom = donnees["prenom"]
        self.IDnationalite = donnees["IDnationalite"]
        self.date_naiss = donnees["date_naiss"]
        self.age = donnees["age"]
        self.IDpays_naiss = donnees["IDpays_naiss"]
        self.cp_naiss = donnees["cp_naiss"]
        self.ville_naiss = donnees["ville_naiss"]
        self.adresse_auto = donnees["adresse_auto"]
        
        # Adresse auto ou manuelle
        if self.adresse_auto != None and self.adresse_auto in dictIndividus :
            self.rue_resid = dictIndividus[self.adresse_auto]["rue_resid"]
            self.cp_resid = dictIndividus[self.adresse_auto]["cp_resid"]
            self.ville_resid = dictIndividus[self.adresse_auto]["ville_resid"]
        else:
            self.rue_resid = donnees["rue_resid"]
            self.cp_resid = donnees["cp_resid"]
            self.ville_resid = donnees["ville_resid"]
        
        self.profession = donnees["profession"]
        self.employeur = donnees["employeur"]
        self.travail_tel = donnees["travail_tel"]
        self.travail_fax = donnees["travail_fax"]
        self.travail_mail = donnees["travail_mail"]
        self.tel_domicile = donnees["tel_domicile"]
        self.tel_mobile = donnees["tel_mobile"]
        self.tel_fax = donnees["tel_fax"]
        self.mail = donnees["mail"]
        self.tel_fax = donnees["tel_fax"]
        self.genre = donnees["genre"]
        self.categorieCivilite = donnees["categorieCivilite"]
        self.civiliteLong = donnees["civiliteLong"]
        self.civiliteAbrege = donnees["civiliteAbrege"]
        self.nomImage = donnees["nomImage"]
        self.etat = donnees["etat"]
        
        # Champ pour filtre de recherche
        nom = self.nom
        if nom == None : nom = ""
        prenom = self.prenom
        if prenom == None : prenom = ""
        self.champ_recherche = u"%s %s %s" % (nom, prenom, nom)

    def GetRattachements(self):
        return GetRattachements(self.IDindividu)

    def GetNomsTitulaires(self, IDfamille=None):
        return GetNomsTitulaires(IDfamille)


    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.historique = []
        self.dictTracks = {}
        self.dictIndividus = {}
        self.donnees = []
        self.dictParametres = {
            "groupes_activites" : [],
            "activites" : [],
            "archives" : False,
            "effaces" : False,
        }
        self.forceActualisation = False
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        try :
            self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, faceName="Tekton"))
        except :
            self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetEmptyListMsg(_(u"Aucun individu"))
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def SetParametres(self, parametres=""):
        if parametres == None :
            parametres = ""

        dictParametres = {}
        listeParametres = parametres.split("###")
        for parametre in listeParametres :
            if "===" in parametre:
                nom, valeur = parametre.split("===")
                dictParametres[nom] = valeur

        # Groupes d'activit�s
        self.dictParametres["groupes_activites"] = []
        if "liste_groupes_activites" in dictParametres:
            listeID = [int(ID) for ID in dictParametres["liste_groupes_activites"].split(";")]
            self.dictParametres["groupes_activites"] = listeID

        # Activit�s
        self.dictParametres["activites"] = []
        if "liste_activites" in dictParametres:
            listeID = [int(ID) for ID in dictParametres["liste_activites"].split(";")]
            self.dictParametres["activites"] = listeID

        # Options
        if "archives" in dictParametres:
            self.dictParametres["archives"] = True
        else :
            self.dictParametres["archives"] = False

        if "effaces" in dictParametres:
            self.dictParametres["effaces"] = True
        else :
            self.dictParametres["effaces"] = False

        if "rfid" in dictParametres:
            if dictParametres["rfid"] == "oui":
                self.InitialisationRFID()
            else:
                self.StopRFID()

    def OnItemActivated(self,event):
        self.Modifier(None)
    
    def GetListeRattachements(self):
        global DICT_RATTACHEMENTS_INDIVIDUS, DICT_RATTACHEMENTS_FAMILLES
        db = GestionDB.DB()
        req = """SELECT IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire
        FROM rattachements;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        dictRattachementsIndividus = {}
        dictRattachementsFamilles = {}
        for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire in listeDonnees :
            # Ajout au dictionnaire INDIVIDUS
            if (IDindividu in dictRattachementsIndividus) == False :
                dictRattachementsIndividus[IDindividu] = [(IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire),]
            else:
                dictRattachementsIndividus[IDindividu].append((IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire))
            
    def GetTracks(self):
        """ R�cup�ration des donn�es """        
        # R�cup�ration des donn�es dans la base
        listeChamps = (
            "individus.IDindividu", "IDcivilite", "nom", "prenom", "num_secu","IDnationalite", 
            "date_naiss", "IDpays_naiss", "cp_naiss", "ville_naiss",
            "adresse_auto", "rue_resid", "cp_resid", "ville_resid", 
            "IDcategorie_travail", "profession", "employeur", "travail_tel", "travail_fax", "travail_mail", 
            "tel_domicile", "tel_mobile", "tel_fax", "mail", "etat"
            )

        conditions = "etat IS NULL"
        if "archives" in self.dictParametres and self.dictParametres["archives"] == True :
            conditions += " OR etat='archive'"
        if "effaces" in self.dictParametres and self.dictParametres["effaces"] == True :
            conditions += " OR etat='efface'"

        db = GestionDB.DB()
        req = """SELECT %s FROM individus WHERE %s;""" % (",".join(listeChamps), conditions)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        
        # R�cup�ration du dictionnaire des civilit�s
        dictCivilites = Civilites.GetDictCivilites()

        # Cr�ation du dictionnaire des donn�es
        dictIndividus = {}
        for valeurs in listeDonnees :
            IDindividu = valeurs[0]
            dictTemp = {}
            # Infos de la table Individus
            for index in range(0, len(listeChamps)) :
                nomChamp = listeChamps[index]
                dictTemp[nomChamp] = valeurs[index]
            # Infos sur la civilit�
            if dictTemp["IDcivilite"] != None and dictTemp["IDcivilite"] != "" :
                dictTemp["genre"] = dictCivilites[dictTemp["IDcivilite"]]["sexe"]
                dictTemp["categorieCivilite"] = dictCivilites[dictTemp["IDcivilite"]]["categorie"]
                dictTemp["civiliteLong"] = dictCivilites[dictTemp["IDcivilite"]]["civiliteLong"]
                dictTemp["civiliteAbrege"] = dictCivilites[dictTemp["IDcivilite"]]["civiliteAbrege"] 
                dictTemp["nomImage"] = dictCivilites[dictTemp["IDcivilite"]]["nomImage"] 
            else:
                dictTemp["genre"] = ""
                dictTemp["categorieCivilite"] = ""
                dictTemp["civiliteLong"] = ""
                dictTemp["civiliteAbrege"] = ""
                dictTemp["nomImage"] = None
            
            if dictTemp["date_naiss"] == None :
                dictTemp["age"] = None
            else:
                try : 
                    datenaissDD = UTILS_Dates.DateEngEnDateDD(dictTemp["date_naiss"])
                    datedujour = datetime.date.today()
                    age = (datedujour.year - datenaissDD.year) - int((datedujour.month, datedujour.day) < (datenaissDD.month, datenaissDD.day))
                    dictTemp["age"] = age
                    dictTemp["date_naiss"] = datenaissDD
                except :
                    dictTemp["age"] = None

            dictIndividus[IDindividu] = dictTemp
        
        # V�rifie si le dictIndividus est diff�rent du pr�c�dent pour emp�cher l'actualisation de la liste
        if dictIndividus == self.dictIndividus and self.forceActualisation == False :
            return None
        else :
            self.dictIndividus = dictIndividus
        
        filtre = None

        # Si filtre activit�s
        if len(self.dictParametres["activites"]) > 0 :
            conditionActivites = GestionDB.ConvertConditionChaine(self.dictParametres["activites"])
            db = GestionDB.DB()
            req = """SELECT individus.IDindividu, nom
            FROM individus
            LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
            WHERE inscriptions.statut='ok' AND inscriptions.IDactivite IN %s
            ;""" % conditionActivites
            db.ExecuterReq(req)
            listeDonnees = db.ResultatReq()
            db.Close()
            filtre = []
            for ID, nom in listeDonnees :
                filtre.append(ID)

        # Si filtre Groupes d'activit�s
        if len(self.dictParametres["groupes_activites"]) > 0 :
            conditionGroupesActivites = GestionDB.ConvertConditionChaine(self.dictParametres["groupes_activites"])
            db = GestionDB.DB()
            req = """SELECT individus.IDindividu, nom
            FROM individus
            LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
            LEFT JOIN groupes_activites ON groupes_activites.IDactivite = inscriptions.IDactivite
            WHERE inscriptions.statut='ok' AND groupes_activites.IDtype_groupe_activite IN %s
            ;""" % conditionGroupesActivites
            db.ExecuterReq(req)
            listeDonnees = db.ResultatReq()
            db.Close()
            filtre = []
            for ID, nom in listeDonnees :
                filtre.append(ID)

        # Cr�ation des Tracks
        listeListeView = []
        self.dictTracks = {}
        for IDindividu, dictTemp in dictIndividus.items() :
            if filtre == None or IDindividu in filtre :
                track = Track(dictTemp, dictIndividus)
                listeListeView.append(track)
                self.dictTracks[IDindividu] = track
        
        return listeListeView
      
    def InitObjectListView(self):
        # Cr�ation du imageList
        for categorie, civilites in Civilites.LISTE_CIVILITES :
            for IDcivilite, CiviliteLong, CiviliteAbrege, nomImage, genre in civilites :
                indexImg = self.AddNamedImages(nomImage, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % nomImage), wx.BITMAP_TYPE_PNG))
        imgSansRattachement = self.AddNamedImages("sansRattachement", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attention.png"), wx.BITMAP_TYPE_PNG))
        imgArchive = self.AddNamedImages("archive", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Archiver.png"), wx.BITMAP_TYPE_PNG))
        imgEfface = self.AddNamedImages("efface", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gomme.png"), wx.BITMAP_TYPE_PNG))

        def GetImageCivilite(track):
            if track.etat == "archive" :
                return "archive"
            if track.etat == "efface" :
                return "efface"
            return track.nomImage

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)
        
        def FormateAge(age):
            if age == None : return ""
            return _(u"%d ans") % age
        
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        liste_Colonnes = [
            ColumnDefn(u"", "left", 22, "IDindividu", typeDonnee="entier", imageGetter=GetImageCivilite),
            ColumnDefn(_(u"Nom"), 'left', 120, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Pr�nom"), "left", 110, "prenom", typeDonnee="texte"),
            ColumnDefn(_(u"Date naiss."), "left", 72, "date_naiss", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Age"), "left", 50, "age", typeDonnee="entier", stringConverter=FormateAge),
            ColumnDefn(_(u"Rue"), "left", 150, "rue_resid", typeDonnee="texte"),
            ColumnDefn(_(u"C.P."), "left", 50, "cp_resid", typeDonnee="texte"),
            ColumnDefn(_(u"Ville"), "left", 100, "ville_resid", typeDonnee="texte"),
            ColumnDefn(_(u"T�l. domicile"), "left", 100, "tel_domicile", typeDonnee="texte"),
            ColumnDefn(_(u"T�l. mobile"), "left", 100, "tel_mobile", typeDonnee="texte"),
            ColumnDefn(_(u"Email"), "left", 150, "mail", typeDonnee="texte"),
            ColumnDefn(_(u"Recherche"), "left", 0, "champ_recherche", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, IDindividu=None, forceActualisation=False):        
        # M�morise l'individu s�lectionn� avant la MAJ
        if IDindividu == None :
            selectionTrack = self.Selection()
            if len(selectionTrack) > 0 :        
                IDindividu = selectionTrack[0].IDindividu
        
        # MAJ
        self.forceActualisation = forceActualisation
        if not self.donnees or forceActualisation:
            self.donnees = self.GetTracks()
            self.GetParent().Freeze() 
            self.InitObjectListView()
            self.GetParent().Thaw() 
        self.Reselection(IDindividu)
    
    def Reselection(self, IDindividu=None):
        """ Re-s�lection apr�s MAJ de la liste """
        if IDindividu in self.dictTracks :
            track = self.dictTracks[IDindividu]
            self.SelectObject(track, deselectOthers=True, ensureVisible=True)
        
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Si on est dans le DLG Rattachement
        if self.GetParent().GetName() == "DLG_Rattachement" :
            return
        
        # Si on est dans le panel Recherche d'individus
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDindividu
                
        # Cr�ation du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter une fiche famille"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille_ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier la fiche famille"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille_modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer la fiche famille"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille_supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 60, _(u"Ouvrir la grille des consommations"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=60)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 70, _(u"Ouvrir la fiche individuelle"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Personnes.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=70)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()

        # G�n�ration automatique des fonctions standards
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des individus"), orientation=wx.LANDSCAPE)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "creer") == False : return
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille=None)
        if dlg.ShowModal() == wx.ID_OK:
            pass
        # MAJ du listView
##        self.MAJ()
        # MAJ du remplissage
        try :
            if self.GetGrandParent().GetName() == "general" :
                self.GetGrandParent().MAJ() 
##                self.GetGrandParent().ctrl_remplissage.MAJ() 
            else:
                self.MAJ() 
        except : pass

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        # Si on est dans le DLG Rattachement
        if self.GetParent().GetName() == "DLG_Rattachement" :
            self.GetParent().OnBoutonOk(None)
            return
        # Si on est dans le panel de recherche d'individus
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Ouvrir la fiche famille de l'individu
        track = self.Selection()[0]
        
        ouvrirGrille=False
        ouvrirFicheInd = False
        if event != None :
            # Ouverture grille de l'individu si touche CTRL enfonc�e
            if wx.GetKeyState(wx.WXK_CONTROL) == True or event.GetId() == 60 :
                ouvrirGrille=True
            
            # Ouverture fiche de l'individu si touche SHIFT enfonc�e
            if wx.GetKeyState(wx.WXK_SHIFT) == True or event.GetId() == 70 :
                ouvrirFicheInd = True
        
        # Ouverture de la fiche famille
        self.OuvrirFicheFamille(track, ouvrirGrille, ouvrirFicheInd)
    
    def OuvrirFicheFamille(self, track=None, ouvrirGrille=False, ouvrirFicheInd=False, IDfamille=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return

        IDindividu = None
        if IDfamille == None:

            IDindividu = track.IDindividu

            rattachements, dictTitulaires, txtTitulaires = track.GetRattachements()
            if rattachements != None :
                rattachements.sort()

            # Rattach� � aucune famille
            if rattachements == None :
                dlg = wx.MessageDialog(self, _(u"Cet individu n'est rattach� � aucune famille.\n\nSouhaitez-vous ouvrir sa fiche individuelle ?"), _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse !=  wx.ID_YES :
                    return False
                else:
                    # Ouverture de la fiche individuelle
                    from Dlg import DLG_Individu
                    dlg = DLG_Individu.Dialog(None, IDindividu=IDindividu)
                    if dlg.ShowModal() == wx.ID_OK:
                        pass
                    dlg.Destroy()
                    self.MAJ()
                    return

            # Rattach�e � une seule famille
            elif len(rattachements) == 1 :
                IDcategorie, IDfamille, titulaire = rattachements[0]
            # Rattach�e � plusieurs familles
            else:
                listeNoms = []
                for IDcategorie, IDfamille, titulaire in rattachements :
                    nomTitulaires = dictTitulaires[IDfamille]
                    if IDcategorie == 1 :
                        nomCategorie = _(u"repr�sentant")
                        if titulaire == 1 :
                            nomCategorie += _(u" titulaire")
                    elif IDcategorie == 2 : nomCategorie = _(u"enfant")
                    elif IDcategorie == 3 : nomCategorie = _(u"contact")
                    else: nomCategorie = _(u"Cat�gorie inconnue")
                    listeNoms.append(_(u"%s (en tant que %s)") % (nomTitulaires, nomCategorie))
                dlg = wx.SingleChoiceDialog(self, _(u"Cet individu est rattach� � %d familles.\nLa fiche de quelle famille souhaitez-vous ouvrir ?") % len(listeNoms), _(u"Rattachements multiples"), listeNoms, wx.CHOICEDLG_STYLE)
                IDfamilleSelection = None
                if dlg.ShowModal() == wx.ID_OK:
                    indexSelection = dlg.GetSelection()
                    IDcategorie, IDfamille, titulaire = rattachements[indexSelection]
                    dlg.Destroy()
                else:
                    dlg.Destroy()
                    return
            
        # Ouverture de la fiche famille
        if IDfamille != None and IDfamille != -1 :
            from Dlg import DLG_Famille
            if ouvrirGrille == True or ouvrirFicheInd == True :
                AfficherMessagesOuverture = False
            else :
                AfficherMessagesOuverture = True
            dlg = DLG_Famille.Dialog(self, IDfamille=IDfamille, AfficherMessagesOuverture=AfficherMessagesOuverture)
            # Ouverture grille de l'individ
            if ouvrirGrille == True :
                dlg.OuvrirGrilleIndividu(IDindividu)
            # Ouverture fiche de l'individu
            if ouvrirFicheInd == True :
                dlg.OuvrirFicheIndividu(IDindividu)
            if dlg.ShowModal() == wx.ID_OK:
                self.MAJ(IDindividu)
            try :
                dlg.Destroy()
            except :
                pass
            # MAJ du remplissage
            try :
                if self.GetGrandParent().GetName() == "general" :
                    self.GetGrandParent().MAJ() 
                else:
                    self.MAJ() 
            except :
                pass
            # M�morisation pour l'historique de la barre de recherche rapide
            try :
                if IDindividu not in self.historique :
                    self.historique.append(IDindividu)
                    if len(self.historique) > 30 :
                        self.historique.pop(0)
            except :
                pass

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun individu dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDindividu = self.Selection()[0].IDindividu
        
        DB = GestionDB.DB()
        
        # V�rifie si cet individu n'est pas rattach� � une famille
        req = """
        SELECT IDrattachement, IDfamille
        FROM rattachements
        WHERE IDindividu=%d
        """ % IDindividu
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer cette fiche car elle est rattach�e � au moins une famille.\n\nSi vous souhaitez vraiment la supprimer, veuillez effectuer cette action � partir de la fiche famille !"), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False
        
        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cet individu ?"), _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() != wx.ID_YES :
            DB.Close()
            dlg.Destroy()
            return False
        dlg.Destroy()
        
        # Suppression : liens
        req = "DELETE FROM liens WHERE IDindividu_sujet=%d;" % IDindividu
        DB.ExecuterReq(req)
        req = "DELETE FROM liens WHERE IDindividu_objet=%d;" % IDindividu
        DB.ExecuterReq(req)
        
        # Suppression : vaccins
        req = "DELETE FROM vaccins WHERE IDindividu=%d;" % IDindividu
        DB.ExecuterReq(req)
        
        # Suppression : problemes_sante
        req = "DELETE FROM problemes_sante WHERE IDindividu=%d;" % IDindividu
        DB.ExecuterReq(req)
        
        # Suppression : abonnements
        req = "DELETE FROM abonnements WHERE IDindividu=%d;" % IDindividu
        DB.ExecuterReq(req)
        
        # Suppression : individu
        req = "DELETE FROM individus WHERE IDindividu=%d;" % IDindividu
        DB.ExecuterReq(req)
        
        DB.Commit() 
        DB.Close()
                
        dlg = wx.MessageDialog(self, _(u"La fiche individuelle a �t� supprim�e avec succ�s."), _(u"Suppression"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        self.MAJ()

        # MAJ du listView
        # MAJ du remplissage
        try :
            if self.GetGrandParent().GetName() == "general" :
                self.GetGrandParent().MAJ() 
            else:
                self.MAJ() 

        except : pass


    def InitialisationRFID(self):
        self.connexion = None
        self.dernierRFID = None
        self.delai = 0

        # Connexion du lecteur RFID
        try :
            self.lecteurs = smartcard.System.readers()
            if len(self.lecteurs) > 0 :
                self.lecteur = self.lecteurs[0]
                self.connexion = self.lecteur.createConnection()
        except :
            pass

        # Pr�paration du timer
        self.timer_rfid = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnTimerRFID, self.timer_rfid)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        if not self.timer_rfid.IsRunning():
            self.timer_rfid.Start(500)

    def OnDestroy(self, event):
        self.StopRFID()

    def StopRFID(self):
        try:
            self.timer_rfid.Stop()
        except:
            pass

    def RechercherSiDlgOuverte(self, widget=None):
        if not widget:
            return False
        for child in widget.GetChildren():
            if "wxDialog" in child.__str__():
                return True
            if len(child.GetChildren()) > 0:
                tmp = self.RechercherSiDlgOuverte(child)
                if tmp != False: return tmp
        return False

    def OnTimerRFID(self, event):
        dlg_ouverte = self.RechercherSiDlgOuverte(wx.GetApp().GetTopWindow())
        if dlg_ouverte == True:
            return False

        self.delai += 0.5
        if self.delai > 8:
            self.delai = 0
            self.dernierRFID = None

        def ListToHex(data):
            string = ''
            for d in data:
                string += '%02X' % d
            return string

        if self.connexion != None:
            try:
                self.connexion.connect()
                apdu = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                data, sw1, sw2 = self.connexion.transmit(apdu)
                if sw1 == 144:
                    IDbadge = ListToHex(data)
                    self.connexion.disconnect()
                    if self.dernierRFID != IDbadge :
                        self.dernierRFID = IDbadge

                    # Recherche du badge RFID dans les questionnaires
                    DB = GestionDB.DB()
                    req = """SELECT IDindividu, IDfamille
                    FROM questionnaire_reponses
                    LEFT JOIN questionnaire_questions ON questionnaire_questions.IDquestion = questionnaire_reponses.IDquestion
                    WHERE controle='rfid' AND reponse='%s'
                    ;""" % IDbadge
                    DB.ExecuterReq(req)
                    listeDonnees = DB.ResultatReq()
                    DB.Close()
                    IDindividu, IDfamille = None, None
                    if len(listeDonnees) > 0 :
                        IDindividu, IDfamille = listeDonnees[0]

                    # On stoppe le timer de d�tection RFID
                    self.timer_rfid.Stop()

                    time.sleep(2)

                    # Ouverture de la fiche famille
                    if IDindividu != None:
                        track = self.dictTracks[IDindividu]
                        self.SelectObject(track)
                        self.OuvrirFicheFamille(track)

                    if IDfamille != None:
                        self.OuvrirFicheFamille(IDfamille=IDfamille)

                    # On relance le timer de d�tection RFID
                    self.timer_rfid.Start()

            except Exception as err:
                pass






# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, historique=False):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.historique = historique
        self.ouvrir_fiche = False
        
        self.SetDescriptiveText(_(u"Rechercher un individu..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        if self.historique == True :
            self.SetMenu(self.MakeMenu())
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchMenuBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe_et_menu.png"), wx.BITMAP_TYPE_PNG))

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Recherche, self.timer)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self.Bind(wx.EVT_TEXT, self.OnText)
        
        # HACK pour avoir le EVT_CHAR
        for child in self.GetChildren(): 
            if isinstance(child, wx.TextCtrl): 
                child.Bind(wx.EVT_CHAR, self.OnKeyDown) 
                break 

    def OnKeyDown(self, event):
        """ Efface tout si touche ECHAP """
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE :
            self.OnCancel(None) 
        event.Skip()

    def OnEnter(self, evt):
        if self.timer.IsRunning():
            self.ouvrir_fiche = True
        else :
            self.OuvrirFiche()

    def OuvrirFiche(self):
        listeObjets = self.listView.GetFilteredObjects()
        if len(listeObjets) == 0 : return
        track = listeObjets[0]
        self.listView.SelectObject(track)
        self.listView.OuvrirFicheFamille(track)
        self.ouvrir_fiche = False

    def OnSearch(self, evt):
        if self.historique == True :
            self.SetMenu(self.MakeMenu())

    def OnCancel(self, evt):
        self.SetValue("")

    def OnText(self, evt):
        txtSearch = self.GetValue()
        
        # Si code-barres individu saisi
        if len(txtSearch) > 6 and txtSearch.startswith("I") :
            txtSearch = txtSearch[1:]
            IDindividu = None
            try :
                IDindividu = int(txtSearch)
            except :
                IDfamille = None
            if IDindividu != None and IDindividu in self.listView.dictTracks :
                track = self.listView.dictTracks[IDindividu]
                self.listView.SelectObject(track)
                self.listView.OuvrirFicheFamille(track)
                self.OnCancel(None)
                return
                
        # Si code-barres famille saisi
        if len(txtSearch) > 6 and txtSearch.startswith("A") :
            txtSearch = txtSearch[1:]
            IDfamille = None
            try :
                IDfamille = int(txtSearch)
            except :
                IDfamille = None
            if IDfamille != None :
                DB = GestionDB.DB()
                req = """SELECT IDfamille FROM familles WHERE IDfamille=%d
                ;""" % IDfamille
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                DB.Close()
                if len(listeDonnees) > 0 :
                    from Dlg import DLG_Famille
                    dlg = DLG_Famille.Dialog(self, IDfamille)
                    dlg.ShowModal()
                    dlg.Destroy()
                    # MAJ du remplissage
                    if self.GetGrandParent().GetName() == "general" :
                        self.GetGrandParent().MAJ() 
                    else:
                        self.MAJ() 
                    self.OnCancel(None)
                    return

        if self.timer.IsRunning():
            self.timer.Stop()

        if len(self.listView.donnees) < 500 :
            duree = 10
        elif len(self.listView.donnees) < 1000 :
            duree = 200
        elif len(self.listView.donnees) < 5000 :
            duree = 500
        else :
            duree = 1000
        self.timer.Start(duree)

    def Recherche(self, event=None):
        if self.timer.IsRunning():
            self.timer.Stop()
        txtSearch = self.GetValue()

        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.listView.Refresh()

        if self.ouvrir_fiche == True :
            self.OuvrirFiche()
    
    def MakeMenu(self):
        menu = UTILS_Adaptations.Menu()
        if len(self.listView.historique) == 0 :
            label = _(u"L'historique des fiches ouvertes est vide")
        else:
            label = _(u"----- Historique des fiches ouvertes -----")
        item = menu.Append(-1, label)
        item.Enable(False)
        index = 0
        for IDindividu in self.listView.historique :
            if IDindividu in self.listView.dictTracks :
                track = self.listView.dictTracks[IDindividu]
                label = u"%s %s" % (track.nom, track.prenom)
                menu.Append(index, label)
                index += 1
        self.Bind(wx.EVT_MENU_RANGE, self.OnItemMenu, id=0, id2=len(self.listView.historique))
        return menu

    def OnItemMenu(self, event):
        index = event.GetId()
        IDindividu = self.listView.historique[index]
        track = self.listView.dictTracks[IDindividu]
        self.listView.SelectObject(track)
        self.listView.OuvrirFicheFamille(track)



# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.listview = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
##        self.listview.listeGroupesActivites = [1, 2]
        self.listview.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.listview, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

