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
##import wx.lib.agw.hypertreelist as HTL
import datetime
import calendar
from dateutil import relativedelta
import GestionDB
import DATA_Renseignements as Renseignements
import UTILS_Utilisateurs


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


class CTRL(wx.TreeCtrl):
    def __init__(self, parent, IDfamille=None, IDindividu=None, dictFamillesRattachees={}, size=(-1, -1) ): 
        wx.TreeCtrl.__init__(self, parent, -1, size=size, style=wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS)
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees
        
        # Adapte taille Police pour Linux
        import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        self.SetBackgroundColour("#F0FBED")
        
        self.listePiecesObligatoires = []
        self.dictItems = {}

        # Cr�ation des colonnes
##        self.AddColumn(_(u"Informations"))
##        self.SetColumnWidth(0, 270)
##        self.SetColumnAlignment(0, wx.ALIGN_LEFT)
                
        # ImageList
        il = wx.ImageList(16, 16)
        self.img_messages = il.Add(wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG))
        self.img_pieces = il.Add(wx.Bitmap("Images/16x16/Dupliquer.png", wx.BITMAP_TYPE_PNG))
        self.img_renseignements = il.Add(wx.Bitmap("Images/16x16/Identite.png", wx.BITMAP_TYPE_PNG))
        self.img_vaccins = il.Add(wx.Bitmap("Images/16x16/Seringue.png", wx.BITMAP_TYPE_PNG))
        self.img_attention = il.Add(wx.Bitmap("Images/16x16/Attention.png", wx.BITMAP_TYPE_PNG))
        self.img_pasok = il.Add(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
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

        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        item = wx.MenuItem(menuPop, 10, _(u"Ajouter un message"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        item.SetBitmap(wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG))
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
        """ Met � jour (redessine) tout le contr�le """
        self.DeleteAllItems()
        self.Remplissage()

    def Remplissage(self):
        # Cr�ation de la racine
        self.root = self.AddRoot(_(u"Racine"))
        
        # Cr�ation des branches Messages
        self.Branches_messages(self.root)
        
        # Cr�ation des branches Pi�ces
        self.Branches_pieces(self.root)
        
        # Cr�ation des branches Cotisations
        self.Branches_cotisations(self.root)
        
        # Cr�ation des branches Renseignements
        self.Branches_renseignements(self.root)
        
        # Cr�ation des branches Vaccinations
        self.Branches_vaccinations(self.root)
        
        self.ExpandAllChildren(self.root)

    def Branches_messages(self, niveauParent=None):
        # Cr�ation des branches
        listeMessages = self.GetMessages() 
        nbreMessages = len(listeMessages)
        if nbreMessages > 0 : 
            
            # Label de la cat�gorie d'info
            if nbreMessages == 1 :
                labelBranche = _(u"1 message")
            else:
                labelBranche = _(u"%d messages") % nbreMessages
            niveauCategorie = self.AppendItem(niveauParent, labelBranche)
            self.SetPyData(niveauCategorie, {"type":"categorie"} )
            self.SetItemBold(niveauCategorie, True)
            self.SetItemImage(niveauCategorie, self.img_messages, which=wx.TreeItemIcon_Normal)
            niveauParent = niveauCategorie
            
            for IDmessage, date_parution, priorite, texte in listeMessages :
                niveau1 = self.AppendItem(niveauParent, texte)
                if priorite == "HAUTE" : self.SetItemImage(niveau1, self.img_attention, which=wx.TreeItemIcon_Normal)
                self.SetPyData(niveau1, {"type":"message", "IDmessage":IDmessage} )


    def Branches_cotisations(self, niveauParent=None):
        # Cr�ation des branches
        dictCotisations, nbreCotisations, nbreFamilles = self.GetCotisations() 
        if nbreCotisations > 0 :
            
            # Label de la cat�gorie d'info
            if nbreCotisations == 1 :
                labelBranche = _(u"1 cotisation � faire")
            else:
                labelBranche = _(u"%d cotisations � faire") % nbreCotisations
            niveauCategorie = self.AppendItem(niveauParent, labelBranche)
            self.SetPyData(niveauCategorie, {"type":"categorie"} )
            self.SetItemBold(niveauCategorie, True)
            self.SetItemImage(niveauCategorie, self.img_pieces, which=wx.TreeItemIcon_Normal)
            niveauParent = niveauCategorie
                    
            for IDfamille, valeurs in dictCotisations.iteritems() :
                
                # Niveau 1 : Titulaires des familles
                if nbreFamilles > 1 :
                    if IDfamille == None :
                        label = _(u"Cotisations ind�pendantes")
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
                    self.SetPyData(niveau2, {"type":"cotisation", "IDtype_cotisation":IDtype_cotisation, "IDindividu":IDindividu, "IDfamille":IDfamille, "valide":valide} )
                    self.dictItems[(IDfamille, IDtype_cotisation, IDindividu)] = niveau2
                    if valide == "ok" : self.SetItemImage(niveau2, self.img_ok, which=wx.TreeItemIcon_Normal)
                    if valide == "attention" : self.SetItemImage(niveau2, self.img_attention, which=wx.TreeItemIcon_Normal)
                    if valide == "pasok" : self.SetItemImage(niveau2, self.img_pasok, which=wx.TreeItemIcon_Normal)



    def Branches_vaccinations(self, niveauParent=None):
        # Cr�ation des branches
        listeMaladies = self.GetVaccinations() 
        nbreMaladies = len(listeMaladies)
        if nbreMaladies > 0 : 
            
            # Label de la cat�gorie d'info
            if nbreMaladies == 1 :
                labelBranche = _(u"1 vaccination � r�aliser")
            else:
                labelBranche = _(u"%d vaccinations � r�aliser") % nbreMaladies
            niveauCategorie = self.AppendItem(niveauParent, labelBranche)
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
                self.SetPyData(niveau1, {"type":"vaccination", "IDindividu":IDindividu, "IDtype_maladie":IDtype_maladie} )


    def Branches_renseignements(self, niveauParent=None):
        # Cr�ation des branches
        try :
            listeRenseignementsManquants = self.GetRenseignements() 
        except Exception, err:
            listeRenseignementsManquants = []
            print "Erreur dans la recherche des renseignements � fournir : ", err
            
        nbreRenseignementsManquants = len(listeRenseignementsManquants)
        if nbreRenseignementsManquants > 0 : 
            
            # Label de la cat�gorie d'info
            if nbreRenseignementsManquants == 1 :
                labelBranche = _(u"1 renseignement manquant")
            else:
                labelBranche = _(u"%d renseignements manquants") % nbreRenseignementsManquants
            niveauCategorie = self.AppendItem(niveauParent, labelBranche)
            self.SetPyData(niveauCategorie, {"type":"categorie"} )
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
                self.SetPyData(niveau1, {"type":"renseignement", "IDfamille":IDfamille, "IDindividu":IDindividu, "IDtype_renseignement":IDtype_renseignement} )
                



    def Branches_pieces(self, niveauParent=None):
        # Cr�ation des branches
        dictPieces, nbrePieces, nbreFamilles = self.GetPieces() 
        
        if nbrePieces > 0 :
            
            # Label de la cat�gorie d'info
            if nbrePieces == 1 :
                labelBranche = _(u"1 pi�ce � fournir")
            else:
                labelBranche = _(u"%d pi�ces � fournir") % nbrePieces
            niveauCategorie = self.AppendItem(niveauParent, labelBranche)
            self.SetPyData(niveauCategorie, {"type":"categorie"} )
            self.SetItemBold(niveauCategorie, True)
            self.SetItemImage(niveauCategorie, self.img_pieces, which=wx.TreeItemIcon_Normal)
            niveauParent = niveauCategorie
                    
            for IDfamille, valeurs in dictPieces.iteritems() :
                
                # Niveau 1 : Titulaires des familles
                if nbreFamilles > 1 :
                    if IDfamille == None :
                        label = _(u"Pi�ces ind�pendantes")
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
                
                # Niveau 2 : Nom des pi�ces
                for IDfamille, IDtype_piece, nomPiece, publicPiece, prenom, IDindividu, valide in valeurs :
                    if publicPiece == "famille" or self.IDindividu != None :
                        label = nomPiece
                    else:
                        label = _(u"%s de %s") % (nomPiece, prenom)
                    niveau2 = self.AppendItem(niveau1, label)
                    self.SetPyData(niveau2, {"type":"piece", "IDtype_piece":IDtype_piece, "IDindividu":IDindividu, "IDfamille":IDfamille, "valide":valide} )
                    self.dictItems[(IDfamille, IDtype_piece, IDindividu)] = niveau2
                    if valide == "ok" : self.SetItemImage(niveau2, self.img_ok, which=wx.TreeItemIcon_Normal)
                    if valide == "attention" : self.SetItemImage(niveau2, self.img_attention, which=wx.TreeItemIcon_Normal)
                    if valide == "pasok" : self.SetItemImage(niveau2, self.img_pasok, which=wx.TreeItemIcon_Normal)
            
        
    def GetMessages(self):
        # R�cup�ration des donn�es
        listeMessages = []
        
        # Cr�ation des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "WHERE IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "WHERE IDindividu=%d " % self.IDindividu
        
        DB = GestionDB.DB()
        
        # R�cup�ration des pi�ces � fournir pour la famille ou l'individu
        req = """
        SELECT IDmessage, type, IDcategorie, date_saisie, IDutilisateur, date_parution, priorite,
        afficher_accueil, afficher_liste, IDfamille, IDindividu, texte
        FROM messages
        %s
        """ % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        for IDmessage, type, IDcategorie, date_saisie, IDutilisateur, date_parution, priorite, afficher_accueil, afficher_liste, IDfamille, IDindividu, texte in listeDonnees :
            listeMessages.append((IDmessage, date_parution, priorite, texte))
        
        return listeMessages



    def GetPieces(self):
        # R�cup�ration des donn�es
        self.listePiecesObligatoires = []
        self.dictItems = {}
        
        # Cr�ation des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "AND inscriptions.IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "AND inscriptions.IDindividu=%d " % self.IDindividu
        
        DB = GestionDB.DB()
        
        # R�cup�ration des pi�ces � fournir pour la famille ou l'individu
        req = """
        SELECT 
        inscriptions.IDfamille, pieces_activites.IDtype_piece, types_pieces.nom, types_pieces.public, types_pieces.valide_rattachement, individus.prenom, individus.IDindividu
        FROM pieces_activites 
        LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces_activites.IDtype_piece
        LEFT JOIN inscriptions ON inscriptions.IDactivite = pieces_activites.IDactivite
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        WHERE inscriptions.parti=0 %s
        GROUP BY inscriptions.IDfamille, pieces_activites.IDtype_piece, individus.IDindividu;
        """ % condition
        DB.ExecuterReq(req)
        listePiecesObligatoires = DB.ResultatReq()
        
        # R�cup�ration des pi�ces de la famille
        dateDuJour = datetime.date.today()
        
        if self.IDindividu != None :
            # Pour un individu
            if self.dictFamillesRattachees != None :
                listeIDfamille = []
                for IDfamille, dictFamille in self.dictFamillesRattachees.iteritems() :
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
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
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
        
        DB.ExecuterReq(req)
        listePiecesFournies = DB.ResultatReq()
        DB.Close()
        dictPiecesFournies = {}
        for IDpiece, IDtype_piece, IDindividu, IDfamille, date_debut, date_fin, publicPiece in listePiecesFournies :
            # Pour les pi�ces familiales :
            if publicPiece == "famille" : IDindividu = None
            
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            dictPiecesFournies[ (IDfamille, IDtype_piece, IDindividu) ] = (date_debut, date_fin)
        
        # Comparaison de la liste des pi�ces � fournir et la liste des pi�ces fournies
        dictDonnees = {}
        for IDfamille, IDtype_piece, nomPiece, publicPiece, rattachementPiece, prenom, IDindividu in listePiecesObligatoires :
            
            # Pour les pi�ces familiales :
            if publicPiece == "famille" : IDindividu = None
            # Pour les pi�ces qui sont ind�pendantes de la famille
            if rattachementPiece == 1 :
                IDfamille = None
            
            # M�morise pour la fen�tre de saisie d'une pi�ce
            self.listePiecesObligatoires.append((IDfamille, IDtype_piece, IDindividu))
            
            if dictPiecesFournies.has_key( (IDfamille, IDtype_piece, IDindividu) ) :
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
        
        # R�partition par famille
        dictPieces = {}
        nbreFamilles = 0
        nbrePieces = len(dictDonnees)
        for key, valeurs in dictDonnees.iteritems() :
            IDfamille = valeurs[0]
            if dictPieces.has_key(IDfamille) == False :
                dictPieces[IDfamille] = []
                if IDfamille != None : 
                    nbreFamilles += 1
            dictPieces[IDfamille].append(valeurs)
            dictPieces[IDfamille].sort()
        
        return dictPieces, nbrePieces, nbreFamilles


    def GetRenseignements(self):
        """ Renseignements � fournir """
        # Cr�ation des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "AND inscriptions.IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "AND inscriptions.IDindividu=%d " % self.IDindividu

        DB = GestionDB.DB()
        # R�cup�ration des renseignements � fournir pour la famille ou l'individu
        req = """
        SELECT 
        inscriptions.IDfamille, individus.IDindividu, IDtype_renseignement, individus.prenom
        FROM renseignements_activites 
        LEFT JOIN inscriptions ON inscriptions.IDactivite = renseignements_activites.IDactivite
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        WHERE inscriptions.parti=0 %s
        GROUP BY individus.IDindividu, renseignements_activites.IDtype_renseignement;
        """ % condition
        DB.ExecuterReq(req)
        listeRenseignementsObligatoires = DB.ResultatReq()
    
        # R�cup�ration des donn�es de la famille
        if self.IDfamille != None :
            req = """SELECT IDcaisse, num_allocataire, allocataire, titulaire_helios, code_comptable
            FROM familles WHERE IDfamille=%d""" % self.IDfamille
            DB.ExecuterReq(req)
            IDcaisse, num_allocataire, allocataire, titulaire_helios, code_comptable = DB.ResultatReq()[0]
            dictDonneesFamille = {"IDcaisse":IDcaisse, "num_allocataire":num_allocataire, "allocataire":allocataire, "titulaire_helios":titulaire_helios, "code_comptable":code_comptable}

        # R�cup�re la liste des ID individus concern�s
        listeIDindividus = []
        for valeurs in listeRenseignementsObligatoires :
            IDindividu = valeurs[1]
            if IDindividu not in listeIDindividus and IDindividu != None :
                listeIDindividus.append(IDindividu)
        
        # R�cup�re les donn�es individus
        if len(listeIDindividus) == 0 : conditionIDindividu = "()"
        if len(listeIDindividus) == 1 : conditionIDindividu = "(%d)" % listeIDindividus[0]
        else : conditionIDindividu = str(tuple(listeIDindividus))
        req = """SELECT IDindividu, IDcivilite, nom, nom_jfille, prenom, num_secu, IDnationalite, adresse_auto, rue_resid,
        date_naiss, ville_naiss, IDmedecin
        FROM individus WHERE IDindividu IN %s;""" % conditionIDindividu
        DB.ExecuterReq(req)
        listeDonneesIndividu = DB.ResultatReq()
        DB.Close()
        
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
            if IDtype_renseignement == 1 and dictDonneesIndividus.has_key(IDindividu) :
                valeur = dictDonneesIndividus[IDindividu]["date_naiss"]
                if self.IDindividu != None and self.GetGrandParent().GetName() == "notebook_individu" :
                    panel = self.GetGrandParent().GetPageAvecCode("identite")
                    if panel.majEffectuee == True :
                        valeur = panel.ctrl_datenaiss.GetDate()
                if valeur == None :
                    listeRenseignementsManquants.append(dictTemp)
            
            # Lieu de naissance
            if IDtype_renseignement == 2 and dictDonneesIndividus.has_key(IDindividu) :
                valeur = dictDonneesIndividus[IDindividu]["ville_naiss"]
                if self.IDindividu != None and self.GetGrandParent().GetName() == "notebook_individu" :
                    panel = self.GetGrandParent().GetPageAvecCode("identite")
                    if panel.majEffectuee == True :
                        valeur = panel.ctrl_adressenaiss.GetValueVille()
                if valeur == None :
                    listeRenseignementsManquants.append(dictTemp)
            
            # Num�ro de s�cu
            if IDtype_renseignement == 3 and dictDonneesIndividus.has_key(IDindividu) :
                valeur = dictDonneesIndividus[IDindividu]["num_secu"]
                if self.IDindividu != None and self.GetGrandParent().GetName() == "notebook_individu" :
                    panel = self.GetGrandParent().GetPageAvecCode("identite")
                    if panel.majEffectuee == True :
                        valeur = panel.ctrl_numsecu.GetValue().strip() 
                if valeur == "" :
                    listeRenseignementsManquants.append(dictTemp)
            
##            # Adresse de r�sidence
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

            # M�decin traitant
            if IDtype_renseignement == 6 and dictDonneesIndividus.has_key(IDindividu) :
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

            # Num�ro d'allocataire
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

            # Titulaire H�lios
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
                DB = GestionDB.DB()
                req = """SELECT IDquotient, date_debut, date_fin
                FROM quotients 
                WHERE IDfamille=%d AND date_debut<='%s' AND date_fin>='%s';""" % (self.IDfamille, dateDuJour, dateDuJour)
                DB.ExecuterReq(req)
                listeQuotients = DB.ResultatReq()
                DB.Close()
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
            # Si illimit�
            dateFin = datetime.date(2999, 1, 1)
            return str(dateFin), None
        else:
            # Limit�
            dateFin = date_vaccin
            if jours != 0 : dateFin = dateFin + relativedelta.relativedelta(days=+jours)
            if mois != 0 : dateFin = dateFin + relativedelta.relativedelta(months=+mois)
            if annees != 0 : dateFin = dateFin + relativedelta.relativedelta(years=+annees)

##            # Calcul des jours
##            if jours != 0:
##                dateFin = date_vaccin + (datetime.timedelta(days = jours))
##                dateJour, dateMois, dateAnnee = dateFin.day, dateFin.month, dateFin.year
##
##            # Calcul des mois
##            if mois != 0:
##                if dateMois + mois > 12:
##                    for temp in range(0, mois):
##                        dateMois += 1
##                        if dateMois > 12 :
##                            dateAnnee += 1
##                            dateMois = 1
##                else:
##                    dateMois = dateMois + mois
##                nbreJoursMois = calendar.monthrange(dateAnnee, dateMois)[1]
##                if dateJour > nbreJoursMois :
##                    dateJour = nbreJoursMois
##                dateFin = datetime.date(dateAnnee, dateMois, dateJour)
##                dateJour, dateMois, dateAnnee = dateFin.day, dateFin.month, dateFin.year
##
##            # Calcul des ann�es
##            if annees != 0:
##                dateAnnee = dateAnnee + annees
##                nbreJoursMois = calendar.monthrange(dateAnnee, dateMois)[1]
##                if dateJour > nbreJoursMois :
##                    dateJour = nbreJoursMois
##                dateFin = datetime.date(dateAnnee, dateMois, dateJour)
        
        # Calcule le nbre de jours restants
        nbreJours = (dateFin - date_jour).days
        
        return str(dateFin), nbreJours


    def GetVaccinations(self):
        
        # Cr�ation des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "AND inscriptions.IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "AND inscriptions.IDindividu=%d " % self.IDindividu
        
        # R�cup�re la liste des individus pour lesquels les vaccinations � jour sont obligatoires
        DB = GestionDB.DB()
        req = """
        SELECT inscriptions.IDindividu, prenom
        FROM activites
        LEFT JOIN inscriptions ON inscriptions.IDactivite = activites.IDactivite
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        WHERE inscriptions.parti=0 AND vaccins_obligatoires=1 %s
        GROUP BY inscriptions.IDindividu;
        """ % condition
        DB.ExecuterReq(req)
        listeIndividus = DB.ResultatReq()
        
        if len(listeIndividus) == 0 :
            DB.Close()
            return []
        
        listeIDindividus = []
        dictPrenoms = {}
        for IDindividu, prenom in listeIndividus :
            listeIDindividus.append(IDindividu)
            dictPrenoms[IDindividu] = prenom
        
        if len(listeIDindividus) == 0 : conditionIDindividu = "()"
        if len(listeIDindividus) == 1 : conditionIDindividu = "(%d)" % listeIDindividus[0]
        else : conditionIDindividu = str(tuple(listeIDindividus))
        
        # R�cup�re la liste des maladies dont le vaccin est obligatoire
        req = """
        SELECT nom, IDtype_maladie
        FROM types_maladies
        WHERE vaccin_obligatoire=1
        ORDER BY nom;"""
        DB.ExecuterReq(req)
        listeMaladies = DB.ResultatReq()
        
        # R�cup�re la liste des vaccins de l'individu
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
        DB.ExecuterReq(req)
        listeVaccins = DB.ResultatReq()
        DB.Close()
    
        dictMaladiesIndividus = {}
        for IDindividu, IDvaccin, IDtype_vaccin, date, IDtype_maladie, nomVaccin, duree_validite, nomMaladie in listeVaccins :
            dateDD = datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10]))
            dateFinValidite, nbreJoursRestants = self.CalcValiditeVaccin(dateDD, duree_validite)
            if dictMaladiesIndividus.has_key(IDindividu) == False :
                dictMaladiesIndividus[IDindividu] = {}
            if dictMaladiesIndividus[IDindividu].has_key(IDtype_maladie) :
                if dictMaladiesIndividus[IDindividu][IDtype_maladie] < nbreJoursRestants :
                    dictMaladiesIndividus[IDindividu][IDtype_maladie] = nbreJoursRestants
            else:
                dictMaladiesIndividus[IDindividu][IDtype_maladie] = nbreJoursRestants
        
        listeMaladiesFinal = []
        for labelMaladie, IDtype_maladie in listeMaladies :
            for IDindividu in listeIDindividus :
                prenom = dictPrenoms[IDindividu]
                etat = "pasok"
                if dictMaladiesIndividus.has_key(IDindividu) :
                    if dictMaladiesIndividus[IDindividu].has_key(IDtype_maladie) :
                        if dictMaladiesIndividus[IDindividu][IDtype_maladie] <= 0 :
                            etat = "pasok"
                        elif dictMaladiesIndividus[IDindividu][IDtype_maladie] > 0 and dictMaladiesIndividus[IDindividu][IDtype_maladie] <= 15 :
                            etat = "attention"
                        else:
                            etat = "ok"
                # Ajout � la liste finale
                if etat != "ok" :
                    listeMaladiesFinal.append((IDindividu, prenom, labelMaladie, IDtype_maladie, etat))
        listeMaladiesFinal.sort() 
        
        return listeMaladiesFinal


    def GetCotisations(self):
        """ V�rifie si l'individu ou la famille doit fournir une ou plusieurs cotisations """
        # R�cup�ration des donn�es
        self.listeCotisationsObligatoires = []
        self.dictItems = {}
        
        # Cr�ation des conditions
        condition = ""
        # Si pour fiche FAMILLE :
        if self.IDfamille != None :
            condition = "AND inscriptions.IDfamille=%d " % self.IDfamille
        # Si pour fiche INDIVIDU
        if self.IDindividu != None :
            condition = "AND inscriptions.IDindividu=%d " % self.IDindividu
        
        DB = GestionDB.DB()
        
        # R�cup�ration des cotisations � fournir pour la famille ou l'individu
        req = """
        SELECT 
        inscriptions.IDfamille, cotisations_activites.IDactivite, cotisations_activites.IDtype_cotisation, types_cotisations.nom, types_cotisations.type, individus.prenom, individus.IDindividu
        FROM cotisations_activites 
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations_activites.IDtype_cotisation
        LEFT JOIN inscriptions ON inscriptions.IDactivite = cotisations_activites.IDactivite
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        WHERE inscriptions.parti=0 AND types_cotisations.IDtype_cotisation IS NOT NULL %s
        GROUP BY inscriptions.IDfamille, cotisations_activites.IDtype_cotisation, individus.IDindividu;
        """ % condition
        DB.ExecuterReq(req)
        listeCotisationsObligatoiresTemp = DB.ResultatReq()
        
        dictCotisationObligatoires = {}
        for IDfamille, IDactivite, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu in listeCotisationsObligatoiresTemp :
            if dictCotisationObligatoires.has_key(IDactivite) == False :
                dictCotisationObligatoires[IDactivite] = []
            dictCotisationObligatoires[IDactivite].append((IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu))
        
        # R�cup�ration des pi�ces de la famille
        dateDuJour = datetime.date.today()
        
        if self.IDindividu != None :
            # Pour un individu
            if self.dictFamillesRattachees != None :
                listeIDfamille = []
                for IDfamille, dictFamille in self.dictFamillesRattachees.iteritems() :
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
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
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
        
        DB.ExecuterReq(req)
        listeCotisationsFournies = DB.ResultatReq()
        DB.Close()
        
        dictCotisationsFournies = {}
        for IDcotisation, IDtype_cotisation, IDindividu, IDfamille, date_debut, date_fin, typeCotisation in listeCotisationsFournies :
            # Pour les cotisations familiales :
            if typeCotisation == "famille" : IDindividu = None
            
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            dictCotisationsFournies[ (IDfamille, IDtype_cotisation, IDindividu) ] = (date_debut, date_fin)
        
        # Comparaison de la liste des cotisations � fournir et la liste des cotisations fournies
        dictDonnees = {}
        for IDactivite, listeCotisationsActivite in dictCotisationObligatoires.iteritems() :
            activiteValide = False
            
            listeTemp = []
            for IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu in listeCotisationsActivite :
                
                # Pour les cotisations familiales :
                if typeCotisation == "famille" : 
                    IDindividu = None
                else:
                    # Pour les cotisations qui sont ind�pendantes de la famille
                    IDfamille = None
                
                # M�morise pour la fen�tre de saisie d'une cotisation
                self.listeCotisationsObligatoires.append((IDfamille, IDtype_cotisation, IDindividu))
                
                if dictCotisationsFournies.has_key( (IDfamille, IDtype_cotisation, IDindividu) ) :
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
                
            # M�morisation
            if activiteValide == False :
                for IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide in listeTemp :
                    dictDonnees[(IDfamille, IDtype_cotisation, IDindividu)] = (IDfamille, IDtype_cotisation, nomCotisation, typeCotisation, prenom, IDindividu, valide)
        
        # R�partition par famille
        dictCotisations = {}
        nbreFamilles = 0
        nbreCotisations = len(dictDonnees)
        for key, valeurs in dictDonnees.iteritems() :
            IDfamille = valeurs[0]
            if dictCotisations.has_key(IDfamille) == False :
                dictCotisations[IDfamille] = []
                if IDfamille != None : 
                    nbreFamilles += 1
            dictCotisations[IDfamille].append(valeurs)
            dictCotisations[IDfamille].sort()

        return dictCotisations, nbreCotisations, nbreFamilles


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
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()