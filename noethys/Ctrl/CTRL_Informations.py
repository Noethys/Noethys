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
##import wx.lib.agw.hypertreelist as HTL
import datetime
import calendar
from dateutil import relativedelta
import GestionDB
from Data import DATA_Renseignements as Renseignements
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Interface


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def FormatDuree(duree):
    posM = duree.find("m")
    posA = duree.find("a")
    jours = int(duree[1:posM-1])
    mois = int(duree[posM+1:posA-1])
    annees = int(duree[posA+1:])
    return jours, mois, annees

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


##class CTRL(HTL.HyperTreeList):
##    def __init__(self, parent, IDfamille=None, IDindividu=None, dictFamillesRattachees={}, size=(-1, -1) ): 
##        HTL.HyperTreeList.__init__(self, parent, -1, size=size)



class Track_message(object):
    def __init__(self, donnees):
        self.IDmessage = donnees[0]
        self.type = donnees[1]
        self.IDcategorie = donnees[2]
        self.date_saisie = DateEngEnDateDD(donnees[3])
        self.IDutilisateur = donnees[4]
        self.date_parution = DateEngEnDateDD(donnees[5])
        self.priorite = donnees[6]
        self.afficher_accueil = donnees[7]
        self.afficher_liste = donnees[8]
        self.IDfamille = donnees[9]
        self.IDindividu = donnees[10]
        self.texte = donnees[11]
        self.rappel_famille = donnees[12]



class CTRL(wx.TreeCtrl):
    def __init__(self, parent, IDfamille=None, IDindividu=None, dictFamillesRattachees={}, size=(-1, -1) ): 
        wx.TreeCtrl.__init__(self, parent, -1, size=size, style=wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS)
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees
        self.listeMessages = []
        
        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        couleur_fond = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.SetBackgroundColour(couleur_fond)
        
        self.listePiecesObligatoires = []
        self.dictItems = {}

        # Création des colonnes
##        self.AddColumn(_(u"Informations"))
##        self.SetColumnWidth(0, 270)
##        self.SetColumnAlignment(0, wx.ALIGN_LEFT)
                
        # ImageList
        il = wx.ImageList(16, 16)
        self.img_messages = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mail.png"), wx.BITMAP_TYPE_PNG))
        self.img_pieces = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_PNG))
        self.img_renseignements = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Identite.png"), wx.BITMAP_TYPE_PNG))
        self.img_vaccins = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Seringue.png"), wx.BITMAP_TYPE_PNG))
        self.img_attention = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attention.png"), wx.BITMAP_TYPE_PNG))
        self.img_pasok = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
                    
##        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | HTL.TR_NO_HEADER)
        
        # Binds
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnDoubleClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)

    def OnDoubleClick(self, event):
        self.Modifier()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item, flags = self.HitTest(event.GetPosition())
        noSelection = True
        if item :
            self.SelectItem(item)
            self.SetFocus()
            dataItem = self.GetPyData(self.GetSelection()) 
            if dataItem["type"] == "message" :
                noSelection = False

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        item = wx.MenuItem(menuPop, 10, _(u"Ajouter un message"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def Ajouter(self, event=None):
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_messages", "creer") == False : return
        if self.IDindividu != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_messages", "creer") == False : return
        if self.GetParent().GetName() == "panel_informations":
            self.GetParent().OnBoutonAjouter(event)
        
    def Modifier(self, event=None):
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_messages", "modifier") == False : return
        if self.IDindividu != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_messages", "modifier") == False : return
        dataItem = self.GetPyData(self.GetSelection()) 
        if dataItem["type"] == "message" and self.GetParent().GetName() == "panel_informations":
            self.GetParent().OnBoutonModifier(event)
        
    def Supprimer(self, event=None):
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_messages", "supprimer") == False : return
        if self.IDindividu != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_messages", "supprimer") == False : return
        dataItem = self.GetPyData(self.GetSelection()) 
        if dataItem["type"] == "message" and self.GetParent().GetName() == "panel_informations":
            self.GetParent().OnBoutonSupprimer(event)
        
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.Remplissage()

    def Remplissage(self):
        # Création de la racine
        self.root = self.AddRoot("Racine")
        
        self.DB = GestionDB.DB()
        
        # Création des branches Messages
        self.Branches_messages(self.root)
        
        # Création des branches Pièces
        self.Branches_pieces(self.root)
        
        # Création des branches Cotisations
        self.Branches_cotisations(self.root)
        
        # Création des branches Renseignements
        self.Branches_renseignements(self.root)
        
        # Création des branches Vaccinations
        self.Branches_vaccinations(self.root)
        
        self.DB.Close() 
        
        self.ExpandAllChildren(self.root)

    def Branches_messages(self, niveauParent=None):
        # Création des branches
        self.listeMessages = self.GetMessages()
        nbreMessages = len(self.listeMessages)
        if nbreMessages > 0 : 
            
            # Label de la catégorie d'info
            if nbreMessages == 1 :
                labelBranche = _(u"1 message")
            else:
                labelBranche = _(u"%d messages") % nbreMessages
            niveauCategorie = self.AppendItem(niveauParent, labelBranche)
            if 'phoenix' in wx.PlatformInfo:
                self.SetItemData(niveauCategorie, {"type":"categorie"})
            else :
                self.SetPyData(niveauCategorie, {"type":"categorie"})
            self.SetItemBold(niveauCategorie, True)
            self.SetItemImage(niveauCategorie, self.img_messages, which=wx.TreeItemIcon_Normal)
            niveauParent = niveauCategorie
            
            for track in self.listeMessages :
                niveau1 = self.AppendItem(niveauParent, track.texte)
                if track.priorite == "HAUTE" :
                    self.SetItemImage(niveau1, self.img_attention, which=wx.TreeItemIcon_Normal)
                if 'phoenix' in wx.PlatformInfo:
                    self.SetItemData(niveau1, {"type":"message", "IDmessage":track.IDmessage})
                else :
                    self.SetPyData(niveau1, {"type":"message", "IDmessage":track.IDmessage})


    def Branches_cotisations(self, niveauParent=None):
        # Création des branches
        dictCotisations, nbreCotisations, nbreFamilles = self.GetCotisations() 
        if nbreCotisations > 0 :
            
            # Label de la catégorie d'info
            if nbreCotisations == 1 :
                labelBranche = _(u"1 cotisation à faire")
            else:
                labelBranche = _(u"%d cotisations à faire") % nbreCotisations
            niveauCategorie = self.AppendItem(niveauParent, labelBranche)
            if 'phoenix' in wx.PlatformInfo:
                self.SetItemData(niveauCategorie, {"type":"categorie"} )
            else :
                self.SetPyData(niveauCategorie, {"type": "categorie"})
            self.SetItemBold(niveauCategorie, True)
            self.SetItemImage(niveauCategorie, self.img_pieces, which=wx.TreeItemIcon_Normal)
            niveauParent = niveauCategorie
                    
            for IDfamille, valeurs in dictCotisations.items() :
                
                # Niveau 1 : Titulaires des familles
                if nbreFamilles > 1 :
                    if IDfamille == None :
                        label = _(u"Cotisations indépendantes")
                    else:
                        if self.dictFamillesRattachees != None and len(self.dictFamillesRattachees) > 0 :
                            label = self.dictFamillesRattachees[IDfamille]["nomsTitulaires"]
                        else:
                            label = _(u"IDfamille=%d") % IDfamille
                    niveau1 = self.AppendItem(niveauParent, label)
                    self.SetPyData(niveau1, {"type":"famille", "IDfamille":IDfamille} )
                    self.SetItemBold(niveau1, True)
                else:
                    niveau1 = niveauParent
                
                # Niveau 2 : Nom des cotisations
                for IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide in valeurs :
                    if typeCotisation == "famille" or self.IDindividu != None :
                        label = nomCotisation
                    else:
                        label = _(u"%s de %s") % (nomCotisation, prenom)
                    niveau2 = self.AppendItem(niveau1, label)
                    data = {"type":"cotisation", "IDtype_cotisation":IDtype_cotisation, "IDindividu":IDindividu, "IDfamille":IDfamille, "valide":valide}
                    if 'phoenix' in wx.PlatformInfo:
                        self.SetItemData(niveau2, data)
                    else :
                        self.SetPyData(niveau2, data)
                    self.dictItems[(IDfamille, IDtype_cotisation, IDindividu)] = niveau2
                    if valide == "ok" : self.SetItemImage(niveau2, self.img_ok, which=wx.TreeItemIcon_Normal)
                    if valide == "attention" : self.SetItemImage(niveau2, self.img_attention, which=wx.TreeItemIcon_Normal)
                    if valide == "pasok" : self.SetItemImage(niveau2, self.img_pasok, which=wx.TreeItemIcon_Normal)



    def Branches_vaccinations(self, niveauParent=None):
        # Création des branches
        listeMaladies = self.GetVaccinations() 
        nbreMaladies = len(listeMaladies)
        if nbreMaladies > 0 : 
            
            # Label de la catégorie d'info
            if nbreMaladies == 1 :
                labelBranche = _(u"1 vaccination à réaliser")
            else:
                labelBranche = _(u"%d vaccinations à réaliser") % nbreMaladies
            niveauCategorie = self.AppendItem(niveauParent, labelBranche)
            if 'phoenix' in wx.PlatformInfo:
                self.SetItemData(niveauCategorie, {"type":"categorie"} )
            else:
                self.SetPyData(niveauCategorie, {"type":"categorie"} )
            self.SetItemBold(niveauCategorie, True)
            self.SetItemImage(niveauCategorie, self.img_vaccins, which=wx.TreeItemIcon_Normal)
            niveauParent = niveauCategorie
            
            for IDindividu, prenom, labelMaladie, IDtype_maladie, etat in listeMaladies :
                labelVaccination = labelMaladie
                if self.IDfamille != None :
                    labelVaccination = _(u"%s pour %s") % (labelMaladie, prenom)
                niveau1 = self.AppendItem(niveauParent, labelVaccination)
                if etat == "pasok" : self.SetItemImage(niveau1, self.img_pasok, which=wx.TreeItemIcon_Normal)
                if etat == "attention" : self.SetItemImage(niveau1, self.img_attention, which=wx.TreeItemIcon_Normal)
                if 'phoenix' in wx.PlatformInfo:
                    self.SetItemData(niveau1, {"type":"vaccination", "IDindividu":IDindividu, "IDtype_maladie":IDtype_maladie})
                else:
                    self.SetPyData(niveau1, {"type":"vaccination", "IDindividu":IDindividu, "IDtype_maladie":IDtype_maladie})

    def Branches_renseignements(self, niveauParent=None):
        # Création des branches
        try :
            listeRenseignementsManquants = self.GetRenseignements() 
        except Exception as err:
            listeRenseignementsManquants = []
            print("Erreur dans la recherche des renseignements à fournir : ", err)
            
        nbreRenseignementsManquants = len(listeRenseignementsManquants)
        if nbreRenseignementsManquants > 0 : 
            
            # Label de la catégorie d'info
            if nbreRenseignementsManquants == 1 :
                labelBranche = _(u"1 renseignement manquant")
            else:
                labelBranche = _(u"%d renseignements manquants") % nbreRenseignementsManquants
            niveauCategorie = self.AppendItem(niveauParent, labelBranche)
            data = {"type":"categorie"}
            if 'phoenix' in wx.PlatformInfo:
                self.SetItemData(niveauCategorie, data)
            else :
                self.SetPyData(niveauCategorie, data)
            self.SetItemBold(niveauCategorie, True)
            self.SetItemImage(niveauCategorie, self.img_renseignements, which=wx.TreeItemIcon_Normal)
            niveauParent = niveauCategorie
            
            for dictValeurs in listeRenseignementsManquants :
                IDtype_renseignement = dictValeurs["IDtype_renseignement"]
                IDfamille = dictValeurs["IDfamille"]
                IDindividu = dictValeurs["IDindividu"]
                prenom = dictValeurs["prenom"]
                label = u"?"
                for ID, label in Renseignements.LISTE_TYPES_RENSEIGNEMENTS :
                    if ID == IDtype_renseignement :
                        labelRenseignement = label
                if self.IDfamille != None :
                    labelRenseignement = _(u"%s de %s") % (labelRenseignement, prenom)
                niveau1 = self.AppendItem(niveauParent, labelRenseignement)
                self.SetItemImage(niveau1, self.img_pasok, which=wx.TreeItemIcon_Normal)
                data = {"type":"renseignement", "IDfamille":IDfamille, "IDindividu":IDindividu, "IDtype_renseignement":IDtype_renseignement}
                if 'phoenix' in wx.PlatformInfo:
                    self.SetItemData(niveau1, data)
                else :
                    self.SetPyData(niveau1, data)



    def Branches_pieces(self, niveauParent=None):
        # Création des branches
        dictPieces, nbrePieces, nbreFamilles = self.GetPieces() 
        
        if nbrePieces > 0 :
            
            # Label de la catégorie d'info
            if nbrePieces == 1 :
                labelBranche = _(u"1 pièce à fournir")
            else:
                labelBranche = _(u"%d pièces à fournir") % nbrePieces
            niveauCategorie = self.AppendItem(niveauParent, labelBranche)
            data = {"type":"categorie"}
            if 'phoenix' in wx.PlatformInfo:
                self.SetItemData(niveauCategorie, data)
            else :
                self.SetPyData(niveauCategorie, data)
            self.SetItemBold(niveauCategorie, True)
            self.SetItemImage(niveauCategorie, self.img_pieces, which=wx.TreeItemIcon_Normal)
            niveauParent = niveauCategorie
                    
            for IDfamille, valeurs in dictPieces.items() :
                
                # Niveau 1 : Titulaires des familles
                if nbreFamilles > 1 :
                    if IDfamille == None :
                        label = _(u"Pièces indépendantes")
                    else:
                        if self.dictFamillesRattachees != None and len(self.dictFamillesRattachees) > 0 :
                            if IDfamille in self.dictFamillesRattachees:
                                label = self.dictFamillesRattachees[IDfamille]["nomsTitulaires"]
                            else:
                                label = _(u"Titulaires inconnus")
                        else:
                            label = _(u"IDfamille=%d") % IDfamille
                    niveau1 = self.AppendItem(niveauParent, label)
                    self.SetPyData(niveau1, {"type":"famille", "IDfamille":IDfamille} )
                    self.SetItemBold(niveau1, True)
                else:
                    niveau1 = niveauParent
                
                # Niveau 2 : Nom des pièces
                for IDfamille, IDtype_piece, nomPiece, publicPiece, prenom, IDindividu, valide in valeurs :
                    if nomPiece == None :
                        nomPiece = "?"
                    if publicPiece == "famille" or self.IDindividu != None :
                        label = nomPiece
                    else:
                        label = _(u"%s de %s") % (nomPiece, prenom)
                    niveau2 = self.AppendItem(niveau1, label)
                    data = {"type":"piece", "IDtype_piece":IDtype_piece, "IDindividu":IDindividu, "IDfamille":IDfamille, "valide":valide}
                    if 'phoenix' in wx.PlatformInfo:
                        self.SetItemData(niveau2, data)
                    else :
                        self.SetPyData(niveau2, data)
                    self.dictItems[(IDfamille, IDtype_piece, IDindividu)] = niveau2
                    if valide == "ok" : self.SetItemImage(niveau2, self.img_ok, which=wx.TreeItemIcon_Normal)
                    if valide == "attention" : self.SetItemImage(niveau2, self.img_attention, which=wx.TreeItemIcon_Normal)
                    if valide == "pasok" : self.SetItemImage(niveau2, self.img_pasok, which=wx.TreeItemIcon_Normal)
            
        
        
        
    def GetMessages(self):
        # Récupération des données
        listeMessages = []
        
        # Création des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "WHERE IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "WHERE IDindividu=%d " % self.IDindividu
        
        # Récupération des pièces à fournir pour la famille ou l'individu
        req = """
        SELECT IDmessage, type, IDcategorie, date_saisie, IDutilisateur, date_parution, priorite,
        afficher_accueil, afficher_liste, IDfamille, IDindividu, texte, rappel_famille
        FROM messages
        %s
        """ % condition
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        
        for donnees in listeDonnees :
            listeMessages.append(Track_message(donnees))
        
        return listeMessages



    def GetPieces(self):
        # Récupération des données
        self.listePiecesObligatoires = []
        self.dictItems = {}
        
        # Création des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "AND inscriptions.IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "AND inscriptions.IDindividu=%d " % self.IDindividu
        
        # Récupération des pièces à fournir pour la famille ou l'individu
        req = """
        SELECT 
        inscriptions.IDfamille, pieces_activites.IDtype_piece, types_pieces.nom, types_pieces.public, types_pieces.valide_rattachement, individus.prenom, individus.IDindividu
        FROM pieces_activites 
        LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces_activites.IDtype_piece
        LEFT JOIN inscriptions ON inscriptions.IDactivite = pieces_activites.IDactivite
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        WHERE inscriptions.statut='ok' AND (inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s') %s AND activites.date_fin>='%s'
        GROUP BY inscriptions.IDfamille, pieces_activites.IDtype_piece, individus.IDindividu;
        """ % (datetime.date.today(), condition, datetime.date.today())
        self.DB.ExecuterReq(req)
        listePiecesObligatoires = self.DB.ResultatReq()
        
        # Récupération des pièces de la famille
        dateDuJour = datetime.date.today()
        
        if self.IDindividu != None :
            # Pour un individu
            if self.dictFamillesRattachees != None :
                listeIDfamille = []
                for IDfamille, dictFamille in self.dictFamillesRattachees.items() :
                    if dictFamille["IDcategorie"] in (1, 2) :
                        listeIDfamille.append(IDfamille)
                if len(listeIDfamille) == 0 : conditionIDfamille = "()"
                if len(listeIDfamille) == 1 : conditionIDfamille = "(%d)" % listeIDfamille[0]
                else : conditionIDfamille = str(tuple(listeIDfamille))
            else:
                conditionIDfamille = "()"
            req = """
            SELECT IDpiece, pieces.IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, public
            FROM pieces 
            LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
            WHERE date_debut <= '%s' AND date_fin >= '%s'
            AND (IDindividu=%d OR (IDfamille IN %s AND IDindividu IS NULL))
            ORDER BY date_fin
            ;""" % (str(dateDuJour), str(dateDuJour), self.IDindividu, conditionIDfamille)
        else:
            # Pour une famille
            req = """
            SELECT IDindividu, IDcategorie
            FROM rattachements 
            WHERE IDfamille=%d AND IDcategorie IN (1, 2);
            """ % self.IDfamille
            self.DB.ExecuterReq(req)
            listeDonnees = self.DB.ResultatReq()
            listeIDindividus = []
            for IDindividu, IDcategorie in listeDonnees :
                if IDindividu not in listeIDindividus :
                    listeIDindividus.append(IDindividu) 
            if len(listeIDindividus) == 0 : conditionIndividus = "()"
            if len(listeIDindividus) == 1 : conditionIndividus = "(%d)" % listeIDindividus[0]
            else : conditionIndividus = str(tuple(listeIDindividus))
            req = """
            SELECT IDpiece, pieces.IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, public
            FROM pieces 
            LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
            WHERE date_debut <= '%s' AND date_fin >= '%s'
            AND (IDfamille=%s OR (IDindividu IN %s AND IDfamille IS NULL))
            ORDER BY date_fin
            """ % (str(dateDuJour), str(dateDuJour), self.IDfamille, conditionIndividus)
        
        self.DB.ExecuterReq(req)
        listePiecesFournies = self.DB.ResultatReq()
        dictPiecesFournies = {}
        for IDpiece, IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, publicPiece in listePiecesFournies :
            # Pour les pièces familiales :
            if publicPiece == "famille" : IDindividu = None
            
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            dictPiecesFournies[ (IDfamille, IDtype_piece, IDindividu) ] = (date_debut, date_fin)
        
        # Comparaison de la liste des pièces à fournir et la liste des pièces fournies
        dictDonnees = {}
        for IDfamille, IDtype_piece, nomPiece, publicPiece, rattachementPiece, prenom, IDindividu in listePiecesObligatoires :
            
            # Pour les pièces familiales :
            if publicPiece == "famille" : IDindividu = None
            # Pour les pièces qui sont indépendantes de la famille
            if rattachementPiece == 1 :
                IDfamille = None
            
            # Mémorise pour la fenêtre de saisie d'une pièce
            self.listePiecesObligatoires.append((IDfamille, IDtype_piece, IDindividu))
            
            if (IDfamille, IDtype_piece, IDindividu) in dictPiecesFournies :
                date_debut, date_fin = dictPiecesFournies[(IDfamille, IDtype_piece, IDindividu)]
                nbreJoursRestants = (date_fin - datetime.date.today()).days
                if nbreJoursRestants > 15 :
                    valide = "ok"
                else:
                    valide = "attention"
            else:
                valide = "pasok"
                
            if valide == "attention" or valide == "pasok" :
                dictDonnees[(IDfamille, IDtype_piece, IDindividu)] = (IDfamille, IDtype_piece, nomPiece, publicPiece, prenom, IDindividu, valide)
        
        # Répartition par famille
        dictPieces = {}
        nbreFamilles = 0
        nbrePieces = len(dictDonnees)
        for key, valeurs in dictDonnees.items() :
            IDfamille = valeurs[0]
            if (IDfamille in dictPieces) == False :
                dictPieces[IDfamille] = []
                if IDfamille != None : 
                    nbreFamilles += 1
            dictPieces[IDfamille].append(valeurs)
            dictPieces[IDfamille].sort()
        
        return dictPieces, nbrePieces, nbreFamilles


    def GetRenseignements(self):
        """ Renseignements à fournir """
        # Création des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "AND inscriptions.IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "AND inscriptions.IDindividu=%d " % self.IDindividu

        # Récupération des renseignements à fournir pour la famille ou l'individu
        req = """
        SELECT 
        inscriptions.IDfamille, individus.IDindividu, IDtype_renseignement, individus.prenom
        FROM renseignements_activites 
        LEFT JOIN inscriptions ON inscriptions.IDactivite = renseignements_activites.IDactivite
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        WHERE inscriptions.statut='ok' AND (inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s') %s AND activites.date_fin>='%s'
        GROUP BY individus.IDindividu, renseignements_activites.IDtype_renseignement, inscriptions.IDfamille;
        """ % (datetime.date.today(), condition, datetime.date.today())
        self.DB.ExecuterReq(req)
        listeRenseignementsObligatoires = self.DB.ResultatReq()
    
        # Récupération des données de la famille
        if self.IDfamille != None :
            req = """SELECT IDcaisse, num_allocataire, allocataire, titulaire_helios, code_comptable
            FROM familles WHERE IDfamille=%d""" % self.IDfamille
            self.DB.ExecuterReq(req)
            IDcaisse, num_allocataire, allocataire, titulaire_helios, code_comptable = self.DB.ResultatReq()[0]
            dictDonneesFamille = {"IDcaisse":IDcaisse, "num_allocataire":num_allocataire, "allocataire":allocataire, "titulaire_helios":titulaire_helios, "code_comptable":code_comptable}

        # Récupère la liste des ID individus concernés
        listeIDindividus = []
        for valeurs in listeRenseignementsObligatoires :
            IDindividu = valeurs[1]
            if IDindividu not in listeIDindividus and IDindividu != None :
                listeIDindividus.append(IDindividu)
        
        # Récupère les données individus
        if len(listeIDindividus) == 0 : conditionIDindividu = "()"
        if len(listeIDindividus) == 1 : conditionIDindividu = "(%d)" % listeIDindividus[0]
        else : conditionIDindividu = str(tuple(listeIDindividus))
        req = """SELECT IDindividu, IDcivilite, nom, nom_jfille, prenom, num_secu, IDnationalite, adresse_auto, rue_resid,
        date_naiss, ville_naiss, IDmedecin
        FROM individus WHERE IDindividu IN %s;""" % conditionIDindividu
        self.DB.ExecuterReq(req)
        listeDonneesIndividu = self.DB.ResultatReq()
        
        dictDonneesIndividus = {}
        for IDindividu, IDcivilite, nom, nom_jfille, prenom, num_secu, IDnationalite, adresse_auto, rue_resid, date_naiss, ville_naiss, IDmedecin in listeDonneesIndividu :
            dictTemp = {
                "IDcivilite" : IDcivilite,
                "nom" : nom,
                "nom_jfille" : nom_jfille,
                "prenom" : prenom,
                "num_secu" : num_secu,
                "IDnationalite" : IDnationalite,
                "adresse_auto" : adresse_auto,
                "rue_resid" : rue_resid,
                "date_naiss" : date_naiss,
                "ville_naiss" : ville_naiss,
                "IDmedecin" : IDmedecin,
                }
            dictDonneesIndividus[IDindividu] = dictTemp
        
        # Recherche les renseignements manquants
        listeRenseignementsManquants = []
        listeRenseignementsTemp = []
        for IDfamille, IDindividu, IDtype_renseignement, prenom in listeRenseignementsObligatoires :
            dictTemp = {"IDfamille":IDfamille, "IDindividu":IDindividu, "IDtype_renseignement":IDtype_renseignement, "prenom" : prenom}
            
            # Date de naissance
            if IDtype_renseignement == 1 and IDindividu in dictDonneesIndividus :
                valeur = dictDonneesIndividus[IDindividu]["date_naiss"]
                if self.IDindividu != None and self.GetGrandParent().GetName() == "notebook_individu" :
                    panel = self.GetGrandParent().GetPageAvecCode("identite")
                    if panel.majEffectuee == True :
                        valeur = panel.ctrl_datenaiss.GetDate()
                if valeur == None :
                    listeRenseignementsManquants.append(dictTemp)
            
            # Lieu de naissance
            if IDtype_renseignement == 2 and IDindividu in dictDonneesIndividus :
                valeur = dictDonneesIndividus[IDindividu]["ville_naiss"]
                if self.IDindividu != None and self.GetGrandParent().GetName() == "notebook_individu" :
                    panel = self.GetGrandParent().GetPageAvecCode("identite")
                    if panel.majEffectuee == True :
                        valeur = panel.ctrl_adressenaiss.GetValueVille()
                if valeur == None :
                    listeRenseignementsManquants.append(dictTemp)
            
            # Numéro de sécu
            if IDtype_renseignement == 3 and IDindividu in dictDonneesIndividus :
                valeur = dictDonneesIndividus[IDindividu]["num_secu"]
                if self.IDindividu != None and self.GetGrandParent().GetName() == "notebook_individu" :
                    panel = self.GetGrandParent().GetPageAvecCode("identite")
                    if panel.majEffectuee == True :
                        valeur = panel.ctrl_numsecu.GetValue().strip() 
                if valeur == "" :
                    listeRenseignementsManquants.append(dictTemp)
            
##            # Adresse de résidence
##            if IDtype_renseignement == 5 :
##                adresse_auto = dictDonneesIndividus[IDindividu]["adresse_auto"]
##                if adresse_auto == None :
##                    
##                if self.IDindividu != None and self.GetGrandParent().GetName() == "notebook_individu" :
##                    panel = self.GetGrandParent().GetPageAvecCode("coords")
##                    if panel.majEffectuee == True :
##                        valeur = panel.ctrl_numsecu.GetValue().strip() 
##                if valeur == "" :
##                    listeRenseignementsManquants.append(dictTemp)

            # Médecin traitant
            if IDtype_renseignement == 6 and IDindividu in dictDonneesIndividus :
                valeur = dictDonneesIndividus[IDindividu]["IDmedecin"]
##                if self.IDindividu != None and self.GetGrandParent().GetName() == "notebook_individu" :
##                    panel = self.GetGrandParent().GetPageAvecCode("medical")
##                    if panel.majEffectuee == True :
##                        valeur = panel.ctrl_medecin.GetIDmedecin()
                if valeur == None :
                    listeRenseignementsManquants.append(dictTemp)
            
            # Caisse d'allocations
            if IDtype_renseignement == 7 and self.IDfamille != None and IDtype_renseignement not in listeRenseignementsTemp :
                if dictDonneesFamille["IDcaisse"] == None :
                    dictTemp["prenom"] = _(u"la famille")
                    listeRenseignementsManquants.append(dictTemp)
                    listeRenseignementsTemp.append(IDtype_renseignement)

            # Numéro d'allocataire
            if IDtype_renseignement == 8 and self.IDfamille != None and IDtype_renseignement not in listeRenseignementsTemp :
                if dictDonneesFamille["num_allocataire"] in (None, "") :
                    dictTemp["prenom"] = _(u"la famille")
                    listeRenseignementsManquants.append(dictTemp)
                    listeRenseignementsTemp.append(IDtype_renseignement)

            # Nom de l'allocataire
            if IDtype_renseignement == 9 and self.IDfamille != None and IDtype_renseignement not in listeRenseignementsTemp :
                if dictDonneesFamille["allocataire"] == None :
                    dictTemp["prenom"] = _(u"la famille")
                    listeRenseignementsManquants.append(dictTemp)
                    listeRenseignementsTemp.append(IDtype_renseignement)

            # Titulaire Hélios
            if IDtype_renseignement == 10 and self.IDfamille != None and IDtype_renseignement not in listeRenseignementsTemp :
                if dictDonneesFamille["titulaire_helios"] == None :
                    dictTemp["prenom"] = _(u"la famille")
                    listeRenseignementsManquants.append(dictTemp)
                    listeRenseignementsTemp.append(IDtype_renseignement)

            # Code comptable
            if IDtype_renseignement == 11 and self.IDfamille != None and IDtype_renseignement not in listeRenseignementsTemp :
                if dictDonneesFamille["code_comptable"] in (None, "") :
                    dictTemp["prenom"] = _(u"la famille")
                    listeRenseignementsManquants.append(dictTemp)
                    listeRenseignementsTemp.append(IDtype_renseignement)

            # Quotient familial
            if IDtype_renseignement == 12 and self.IDfamille != None and IDtype_renseignement not in listeRenseignementsTemp :
                dateDuJour = datetime.date.today()
                req = """SELECT IDquotient, date_debut, date_fin
                FROM quotients 
                WHERE IDfamille=%d AND date_debut<='%s' AND date_fin>='%s';""" % (self.IDfamille, dateDuJour, dateDuJour)
                self.DB.ExecuterReq(req)
                listeQuotients = self.DB.ResultatReq()
                if len(listeQuotients) == 0 :
                    dictTemp["prenom"] = _(u"la famille")
                    listeRenseignementsManquants.append(dictTemp)
                    listeRenseignementsTemp.append(IDtype_renseignement)

        return listeRenseignementsManquants

    def CalcValiditeVaccin(self, date_vaccin, duree_validite):
        jours, mois, annees = FormatDuree(duree_validite)
        date_jour = datetime.date.today()
        dateJour, dateMois, dateAnnee = date_vaccin.day, date_vaccin.month, date_vaccin.year
        
        if jours==0 and mois==0 and annees==0:
            # Si illimité
            dateFin = datetime.date(2999, 1, 1)
            return str(dateFin), None
        else:
            # Limité
            dateFin = date_vaccin
            if jours != 0 : dateFin = dateFin + relativedelta.relativedelta(days=+jours)
            if mois != 0 : dateFin = dateFin + relativedelta.relativedelta(months=+mois)
            if annees != 0 : dateFin = dateFin + relativedelta.relativedelta(years=+annees)
        
        # Calcule le nbre de jours restants
        nbreJours = (dateFin - date_jour).days
        
        return str(dateFin), nbreJours


    def GetVaccinations(self):
        
        # Création des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "AND inscriptions.IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "AND inscriptions.IDindividu=%d " % self.IDindividu
        
        # Récupère la liste des individus pour lesquels les vaccinations à jour sont obligatoires
        req = """
        SELECT inscriptions.IDindividu, prenom
        FROM activites
        LEFT JOIN inscriptions ON inscriptions.IDactivite = activites.IDactivite
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        WHERE inscriptions.statut='ok' AND (inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s') AND vaccins_obligatoires=1 %s AND activites.date_fin>='%s'
        GROUP BY inscriptions.IDindividu;
        """ % (datetime.date.today(), condition, datetime.date.today())
        self.DB.ExecuterReq(req)
        listeIndividus = self.DB.ResultatReq()
        
        if len(listeIndividus) == 0 :
            return []
        
        listeIDindividus = []
        dictPrenoms = {}
        for IDindividu, prenom in listeIndividus :
            listeIDindividus.append(IDindividu)
            dictPrenoms[IDindividu] = prenom
        
        if len(listeIDindividus) == 0 : conditionIDindividu = "()"
        if len(listeIDindividus) == 1 : conditionIDindividu = "(%d)" % listeIDindividus[0]
        else : conditionIDindividu = str(tuple(listeIDindividus))
        
        # Récupère la liste des maladies dont le vaccin est obligatoire
        req = """
        SELECT nom, IDtype_maladie
        FROM types_maladies
        WHERE vaccin_obligatoire=1
        ORDER BY nom;"""
        self.DB.ExecuterReq(req)
        listeMaladies = self.DB.ResultatReq()
        
        # Récupère la liste des vaccins de l'individu
        req = """
        SELECT 
        vaccins.IDindividu, vaccins.IDvaccin, vaccins.IDtype_vaccin, vaccins.date, vaccins_maladies.IDtype_maladie, 
        types_vaccins.nom, types_vaccins.duree_validite, types_maladies.nom
        FROM vaccins 
        LEFT JOIN vaccins_maladies ON vaccins.IDtype_vaccin = vaccins_maladies.IDtype_vaccin
        LEFT JOIN types_vaccins ON vaccins.IDtype_vaccin = types_vaccins.IDtype_vaccin
        LEFT JOIN types_maladies ON vaccins_maladies.IDtype_maladie = types_maladies.IDtype_maladie
        WHERE vaccins.IDindividu IN %s AND types_maladies.vaccin_obligatoire=1;
        """ % conditionIDindividu
        self.DB.ExecuterReq(req)
        listeVaccins = self.DB.ResultatReq()
    
        dictMaladiesIndividus = {}
        for IDindividu, IDvaccin, IDtype_vaccin, date, IDtype_maladie, nomVaccin, duree_validite, nomMaladie in listeVaccins :
            dateDD = datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10]))
            dateFinValidite, nbreJoursRestants = self.CalcValiditeVaccin(dateDD, duree_validite)
            if (IDindividu in dictMaladiesIndividus) == False :
                dictMaladiesIndividus[IDindividu] = {}
            if IDtype_maladie in dictMaladiesIndividus[IDindividu] :
                if dictMaladiesIndividus[IDindividu][IDtype_maladie] < nbreJoursRestants :
                    dictMaladiesIndividus[IDindividu][IDtype_maladie] = nbreJoursRestants
            else:
                dictMaladiesIndividus[IDindividu][IDtype_maladie] = nbreJoursRestants
        
        listeMaladiesFinal = []
        for labelMaladie, IDtype_maladie in listeMaladies :
            for IDindividu in listeIDindividus :
                prenom = dictPrenoms[IDindividu]
                etat = "pasok"
                if IDindividu in dictMaladiesIndividus :
                    if IDtype_maladie in dictMaladiesIndividus[IDindividu] :
                        if dictMaladiesIndividus[IDindividu][IDtype_maladie] <= 0 :
                            etat = "pasok"
                        elif dictMaladiesIndividus[IDindividu][IDtype_maladie] > 0 and dictMaladiesIndividus[IDindividu][IDtype_maladie] <= 15 :
                            etat = "attention"
                        else:
                            etat = "ok"
                # Ajout à la liste finale
                if etat != "ok" :
                    listeMaladiesFinal.append((IDindividu, prenom, labelMaladie, IDtype_maladie, etat))
        listeMaladiesFinal.sort() 
        
        return listeMaladiesFinal


    def GetCotisations(self):
        """ Vérifie si l'individu ou la famille doit fournir une ou plusieurs cotisations """
        # Récupération des données
        self.listeCotisationsObligatoires = []
        self.dictItems = {}
        
        # Création des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "AND inscriptions.IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "AND inscriptions.IDindividu=%d " % self.IDindividu
        
        
        # Récupération des cotisations à fournir pour la famille ou l'individu
        req = """
        SELECT 
        inscriptions.IDfamille, cotisations_activites.IDactivite, cotisations_activites.IDtype_cotisation, types_cotisations.nom, types_cotisations.type, individus.prenom, individus.IDindividu
        FROM cotisations_activites 
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations_activites.IDtype_cotisation
        LEFT JOIN inscriptions ON inscriptions.IDactivite = cotisations_activites.IDactivite
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        WHERE inscriptions.statut='ok' AND (inscriptions.date_desinscription IS NULL OR inscriptions.date_desinscription>='%s') AND types_cotisations.IDtype_cotisation IS NOT NULL %s AND activites.date_fin>='%s'
        GROUP BY inscriptions.IDfamille, cotisations_activites.IDtype_cotisation, individus.IDindividu, cotisations_activites.IDactivite;
        """ % (datetime.date.today(), condition, datetime.date.today())
        self.DB.ExecuterReq(req)
        listeCotisationsObligatoiresTemp = self.DB.ResultatReq()

        dictCotisationObligatoires = {}
        for IDfamille, IDactivite, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu in listeCotisationsObligatoiresTemp :
            if (IDactivite in dictCotisationObligatoires) == False :
                dictCotisationObligatoires[IDactivite] = []
            dictCotisationObligatoires[IDactivite].append((IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu))
        
        # Récupération des pièces de la famille
        dateDuJour = datetime.date.today()
        
        if self.IDindividu != None :
            # Pour un individu
            if self.dictFamillesRattachees != None :
                listeIDfamille = []
                for IDfamille, dictFamille in self.dictFamillesRattachees.items() :
                    if dictFamille["IDcategorie"] in (1, 2) :
                        listeIDfamille.append(IDfamille)
                if len(listeIDfamille) == 0 : conditionIDfamille = "()"
                if len(listeIDfamille) == 1 : conditionIDfamille = "(%d)" % listeIDfamille[0]
                else : conditionIDfamille = str(tuple(listeIDfamille))
            else:
                conditionIDfamille = "()"
            req = """
            SELECT IDcotisation, cotisations.IDtype_cotisation, IDindividu, IDfamille, date_debut, date_fin, type
            FROM cotisations 
            LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
            WHERE date_debut <= '%s' AND date_fin >= '%s'
            AND (IDindividu=%d OR (IDfamille IN %s AND IDindividu IS NULL))
            ORDER BY date_fin
            ;""" % (str(dateDuJour), str(dateDuJour), self.IDindividu, conditionIDfamille)
        else:
            # Pour une famille
            req = """
            SELECT IDindividu, IDcategorie
            FROM rattachements 
            WHERE IDfamille=%d AND IDcategorie IN (1, 2);
            """ % self.IDfamille
            self.DB.ExecuterReq(req)
            listeDonnees = self.DB.ResultatReq()
            listeIDindividus = []
            for IDindividu, IDcategorie in listeDonnees :
                if IDindividu not in listeIDindividus :
                    listeIDindividus.append(IDindividu) 
            if len(listeIDindividus) == 0 : conditionIndividus = "()"
            if len(listeIDindividus) == 1 : conditionIndividus = "(%d)" % listeIDindividus[0]
            else : conditionIndividus = str(tuple(listeIDindividus))
            req = """
            SELECT IDcotisation, cotisations.IDtype_cotisation, IDindividu, IDfamille, date_debut, date_fin, type
            FROM cotisations 
            LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
            WHERE date_debut <= '%s' AND date_fin >= '%s'
            AND (IDfamille=%s OR (IDindividu IN %s AND IDfamille IS NULL))
            ORDER BY date_fin
            """ % (str(dateDuJour), str(dateDuJour), self.IDfamille, conditionIndividus)
        
        self.DB.ExecuterReq(req)
        listeCotisationsFournies = self.DB.ResultatReq()
        
        dictCotisationsFournies = {}
        for IDcotisation, IDtype_cotisation, IDindividu, IDfamille, date_debut, date_fin, typeCotisation in listeCotisationsFournies :
            # Pour les cotisations familiales :
            if typeCotisation == "famille" : IDindividu = None
            
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            dictCotisationsFournies[ (IDfamille, IDtype_cotisation, IDindividu) ] = (date_debut, date_fin)
        
        # Comparaison de la liste des cotisations à fournir et la liste des cotisations fournies
        dictDonnees = {}
        for IDactivite, listeCotisationsActivite in dictCotisationObligatoires.items() :
            activiteValide = False
            
            listeTemp = []
            for IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu in listeCotisationsActivite :
                
                # Pour les cotisations familiales :
                if typeCotisation == "famille" : 
                    IDindividu = None
                else:
                    # Pour les cotisations qui sont indépendantes de la famille
                    IDfamille = None
                
                # Mémorise pour la fenêtre de saisie d'une cotisation
                self.listeCotisationsObligatoires.append((IDfamille, IDtype_cotisation, IDindividu))
                
                if (IDfamille, IDtype_cotisation, IDindividu) in dictCotisationsFournies :
                    date_debut, date_fin = dictCotisationsFournies[(IDfamille, IDtype_cotisation, IDindividu)]
                    nbreJoursRestants = (date_fin - datetime.date.today()).days
                    if nbreJoursRestants > 15 :
                        valide = "ok"
                    else:
                        valide = "attention"
                else:
                    valide = "pasok"
                
                if valide == "ok" :
                    activiteValide = True
                    
                if valide == "attention" or valide == "pasok" :
                    listeTemp.append((IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide))
                
            # Mémorisation
            if activiteValide == False :
                for IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide in listeTemp :
                    dictDonnees[(IDfamille, IDtype_cotisation, IDindividu)] = (IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide)
        
        # Répartition par famille
        dictCotisations = {}
        nbreFamilles = 0
        nbreCotisations = len(dictDonnees)
        for key, valeurs in dictDonnees.items() :
            IDfamille = valeurs[0]
            if (IDfamille in dictCotisations) == False :
                dictCotisations[IDfamille] = []
                if IDfamille != None : 
                    nbreFamilles += 1
            dictCotisations[IDfamille].append(valeurs)
            dictCotisations[IDfamille].sort()

        return dictCotisations, nbreCotisations, nbreFamilles

    def GetListeMessages(self):
        return self.listeMessages

# --------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, IDindividu=None, IDfamille=46)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    import time
    heure_debut = time.time()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    print("Temps de chargement CTRL_Informations =", time.time() - heure_debut)
    frame_1.Show()
    app.MainLoop()