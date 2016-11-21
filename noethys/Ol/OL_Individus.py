#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _

import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Data import DATA_Civilites as Civilites
from Utils import UTILS_Titulaires
from Utils import UTILS_Dates


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils import UTILS_Utilisateurs



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
        if self.adresse_auto != None and dictIndividus.has_key(self.adresse_auto) :
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
        
        # Champ pour filtre de recherche
        nom = self.nom
        if nom == None : nom = ""
        prenom = self.prenom
        if prenom == None : prenom = ""
        self.champ_recherche = u"%s %s %s" % (nom, prenom, nom)
    
    
    def GetRattachements(self):
        # Récupération des rattachements dans la base
        DB = GestionDB.DB()
        req = """SELECT IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire
        FROM rattachements
        WHERE IDindividu=%d
        ;""" % self.IDindividu
        DB.ExecuterReq(req)
        listeRattachements = DB.ResultatReq()
        DB.Close()
    
        # Recherche des rattachements
        dictTitulaires = {}
        if len(listeRattachements) == 0 :
            rattachements = None
            dictTitulaires = {}
            txtTitulaires = _(u"Rattaché à aucune famille")
        elif len(listeRattachements) == 1 :
            IDfamille = listeRattachements[0][2]
            IDcategorie = listeRattachements[0][3]
            titulaire = listeRattachements[0][4]
            rattachements = [(IDcategorie, IDfamille, titulaire)]
            dictTitulaires[IDfamille] = self.GetNomsTitulaires(IDfamille)
            txtTitulaires = dictTitulaires[IDfamille]
        else:
            rattachements = []
            txtTitulaires = ""
            for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire in listeRattachements :
                rattachements.append((IDcategorie, IDfamille, titulaire))
                nomsTitulaires =  self.GetNomsTitulaires(IDfamille)
                dictTitulaires[IDfamille] = nomsTitulaires
                txtTitulaires += nomsTitulaires + u" | "
            if len(txtTitulaires) > 0 :
                txtTitulaires = txtTitulaires[:-2]
        
        return rattachements, dictTitulaires, txtTitulaires
                    
    def GetNomsTitulaires(self, IDfamille=None):
        dictTitulaires = UTILS_Titulaires.GetTitulaires(listeIDfamille=[IDfamille,])
        if dictTitulaires.has_key(IDfamille) :
            noms = dictTitulaires[IDfamille]["titulairesSansCivilite"]
        else :
            noms = "?"
        return noms


    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.historique = []
        self.dictTracks = {}
        self.dictIndividus = {}
        self.donnees = []
        self.listeActivites = []
        self.listeGroupesActivites = []
        self.forceActualisation = False
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetEmptyListMsg(_(u"Aucun individu"))
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
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
            if dictRattachementsIndividus.has_key(IDindividu) == False :
                dictRattachementsIndividus[IDindividu] = [(IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire),]
            else:
                dictRattachementsIndividus[IDindividu].append((IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire))
            
    def GetTracks(self):
        """ Récupération des données """        
        # Récupération des données dans la base
        listeChamps = (
            "individus.IDindividu", "IDcivilite", "nom", "prenom", "num_secu","IDnationalite", 
            "date_naiss", "IDpays_naiss", "cp_naiss", "ville_naiss",
            "adresse_auto", "rue_resid", "cp_resid", "ville_resid", 
            "IDcategorie_travail", "profession", "employeur", "travail_tel", "travail_fax", "travail_mail", 
            "tel_domicile", "tel_mobile", "tel_fax", "mail"
            )
        db = GestionDB.DB()
        req = """SELECT %s FROM individus;""" % ",".join(listeChamps)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        
        # Récupération du dictionnaire des civilités
        dictCivilites = Civilites.GetDictCivilites()

        # Création du dictionnaire des données
        dictIndividus = {}
        for valeurs in listeDonnees :
            IDindividu = valeurs[0]
            dictTemp = {}
            # Infos de la table Individus
            for index in range(0, len(listeChamps)) :
                nomChamp = listeChamps[index]
                dictTemp[nomChamp] = valeurs[index]
            # Infos sur la civilité
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
        
        # Vérifie si le dictIndividus est différent du précédent pour empêcher l'actualisation de la liste
        if dictIndividus == self.dictIndividus and len(self.listeActivites) == 0 and len(self.listeGroupesActivites) == 0 and self.forceActualisation == False :
            return None
        else :
            self.dictIndividus = dictIndividus
        
        filtre = None
        
        # Si filtre activités
        if len(self.listeActivites) > 0 :
            if len(self.listeActivites) == 0 : conditionActivites = "()"
            elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
            else : conditionActivites = str(tuple(self.listeActivites))
            db = GestionDB.DB()
            req = """SELECT individus.IDindividu, nom
            FROM individus
            LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
            WHERE inscriptions.IDactivite IN %s
            ;""" % conditionActivites
            db.ExecuterReq(req)
            listeDonnees = db.ResultatReq()
            db.Close()
            filtre = []
            for ID, nom in listeDonnees :
                filtre.append(ID)

        # Si filtre Groupes d'activités
        if len(self.listeGroupesActivites) > 0 :
            if len(self.listeGroupesActivites) == 0 : conditionGroupesActivites = "()"
            elif len(self.listeGroupesActivites) == 1 : conditionGroupesActivites = "(%d)" % self.listeGroupesActivites[0]
            else : conditionGroupesActivites = str(tuple(self.listeGroupesActivites))
            db = GestionDB.DB()
            req = """SELECT individus.IDindividu, nom
            FROM individus
            LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
            LEFT JOIN groupes_activites ON groupes_activites.IDactivite = inscriptions.IDactivite
            WHERE groupes_activites.IDtype_groupe_activite IN %s
            ;""" % conditionGroupesActivites
            db.ExecuterReq(req)
            listeDonnees = db.ResultatReq()
            db.Close()
            filtre = []
            for ID, nom in listeDonnees :
                filtre.append(ID)

        # Création des Tracks
        listeListeView = []
        self.dictTracks = {}
        for IDindividu, dictTemp in dictIndividus.iteritems() :
            if filtre == None or IDindividu in filtre :
                track = Track(dictTemp, dictIndividus)
                listeListeView.append(track)
                self.dictTracks[IDindividu] = track
        
        return listeListeView
      
    def InitObjectListView(self):
        # Création du imageList
        for categorie, civilites in Civilites.LISTE_CIVILITES :
            for IDcivilite, CiviliteLong, CiviliteAbrege, nomImage, genre in civilites :
                indexImg = self.AddNamedImages(nomImage, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % nomImage), wx.BITMAP_TYPE_PNG))
        imgSansRattachement = self.AddNamedImages("sansRattachement", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attention.png"), wx.BITMAP_TYPE_PNG))
        
        def GetImageCivilite(track):
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
            ColumnDefn(_(u"Nom"), 'left', 100, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Prénom"), "left", 100, "prenom", typeDonnee="texte"),
            ColumnDefn(_(u"Date naiss."), "left", 72, "date_naiss", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Age"), "left", 50, "age", typeDonnee="entier", stringConverter=FormateAge),
            ColumnDefn(_(u"Rue"), "left", 150, "rue_resid", typeDonnee="texte"),
            ColumnDefn(_(u"C.P."), "left", 50, "cp_resid", typeDonnee="texte"),
            ColumnDefn(_(u"Ville"), "left", 100, "ville_resid", typeDonnee="texte"),
            ColumnDefn(_(u"Tél. domicile"), "left", 100, "tel_domicile", typeDonnee="texte"),
            ColumnDefn(_(u"Tél. mobile"), "left", 100, "tel_mobile", typeDonnee="texte"),
            ColumnDefn(_(u"Email"), "left", 150, "mail", typeDonnee="texte"),
            ColumnDefn(_(u"Recherche"), "left", 0, "champ_recherche", typeDonnee="texte"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, IDindividu=None, forceActualisation=False):        
        # Mémorise l'individu sélectionné avant la MAJ
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
        """ Re-sélection après MAJ de la liste """
        if self.dictTracks.has_key(IDindividu) :
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
                
        # Création du menu contextuel
        menuPop = wx.Menu()

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

        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des individus"), format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des individus"), format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des individus"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des individus"))

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
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Ouvrir la fiche famille de l'individu
        track = self.Selection()[0]
        
        ouvrirGrille=False
        ouvrirFicheInd = False
        if event != None :
            # Ouverture grille de l'individu si touche CTRL enfoncée
            if wx.GetKeyState(wx.WXK_CONTROL) == True or event.GetId() == 60 :
                ouvrirGrille=True
            
            # Ouverture fiche de l'individu si touche SHIFT enfoncée
            if wx.GetKeyState(wx.WXK_SHIFT) == True or event.GetId() == 70 :
                ouvrirFicheInd = True
        
        # Ouverture de la fiche famille
        self.OuvrirFicheFamille(track, ouvrirGrille, ouvrirFicheInd)
    
    def OuvrirFicheFamille(self, track=None, ouvrirGrille=False, ouvrirFicheInd=False):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        
        IDindividu = track.IDindividu
        
        rattachements, dictTitulaires, txtTitulaires = track.GetRattachements() 
        if rattachements != None :
            rattachements.sort()
            
        # Rattaché à aucune famille
        if rattachements == None :
            dlg = wx.MessageDialog(self, _(u"Cet individu n'est rattaché à aucune famille.\n\nSouhaitez-vous ouvrir sa fiche individuelle ?"), _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
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
                
        # Rattachée à une seule famille
        elif len(rattachements) == 1 :
            IDcategorie, IDfamille, titulaire = rattachements[0]
        # Rattachée à plusieurs familles
        else:
            listeNoms = []
            for IDcategorie, IDfamille, titulaire in rattachements :
                nomTitulaires = dictTitulaires[IDfamille]
                if IDcategorie == 1 : 
                    nomCategorie = _(u"représentant")
                    if titulaire == 1 : 
                        nomCategorie += _(u" titulaire")
                if IDcategorie == 2 : nomCategorie = _(u"enfant")
                if IDcategorie == 3 : nomCategorie = _(u"contact")
                listeNoms.append(_(u"%s (en tant que %s)") % (nomTitulaires, nomCategorie))
            dlg = wx.SingleChoiceDialog(self, _(u"Cet individu est rattaché à %d familles.\nLa fiche de quelle famille souhaitez-vous ouvrir ?") % len(listeNoms), _(u"Rattachements multiples"), listeNoms, wx.CHOICEDLG_STYLE)
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
            dlg = DLG_Famille.Dialog(self, IDfamille)
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
            # Mémorisation pour l'historique de la barre de recherche rapide
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
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun individu dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDindividu = self.Selection()[0].IDindividu
        
        DB = GestionDB.DB()
        
        # Vérifie si cet individu n'est pas rattaché à une famille
        req = """
        SELECT IDrattachement, IDfamille
        FROM rattachements
        WHERE IDindividu=%d
        """ % IDindividu
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer cette fiche car elle est rattachée à au moins une famille.\n\nSi vous souhaitez vraiment la supprimer, veuillez effectuer cette action à partir de la fiche famille !"), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
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
                
        dlg = wx.MessageDialog(self, _(u"La fiche individuelle a été supprimée avec succès."), _(u"Suppression"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        self.MAJ()

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
        
# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, historique=False):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.historique = historique
        
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
        listeObjets = self.listView.GetFilteredObjects()
        if len(listeObjets) == 0 : return
        track = listeObjets[0]
        self.listView.SelectObject(track)
        self.listView.OuvrirFicheFamille(track)
        
    def OnSearch(self, evt):
        if self.historique == True :
            self.SetMenu(self.MakeMenu())
        #self.Recherche(self.GetValue())
            
    def OnCancel(self, evt):
        self.SetValue("")
        #self.Recherche(self.GetValue())

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
            if IDindividu != None and self.listView.dictTracks.has_key(IDindividu) :
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
                       
        # Filtre la liste normalement
        self.Recherche(self.GetValue())
        
    def Recherche(self, txtSearch):
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.listView.Refresh() 
    
    def MakeMenu(self):
        menu = wx.Menu()
        if len(self.listView.historique) == 0 :
            label = _(u"L'historique des fiches ouvertes est vide")
        else:
            label = _(u"----- Historique des fiches ouvertes -----")
        item = menu.Append(-1, label)
        item.Enable(False)
        index = 0
        for IDindividu in self.listView.historique :
            if self.listView.dictTracks.has_key(IDindividu) :
                track = self.listView.dictTracks[IDindividu]
                label = u"%s %s" % (track.nom, track.prenom)
                menu.Append(index, label)
                index += 1
        self.Bind(wx.EVT_MENU_RANGE, self.OnItemMenu, id=0, id2=len(self.listView.historique))
        return menu

    def OnItemMenu(self, event):
##        self.OnCancel(None)
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

