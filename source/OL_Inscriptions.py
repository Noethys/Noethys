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
import os
import cStringIO
import datetime
import GestionDB
import UTILS_Historique

from ObjectListView import FastObjectListView, ColumnDefn, Filter, ListCtrlPrinter

import UTILS_Utilisateurs

TAILLE_IMAGE = (40, 40)
LOGO_ORGANISATEUR = None


def RecadreImg(img=None):
    # Recadre l'image en fonction de la taille du staticBitmap
    tailleMaxi = max(TAILLE_IMAGE)
    largeur, hauteur = img.GetSize()
    if max(largeur, hauteur) > tailleMaxi :
        if largeur > hauteur :
            hauteur = hauteur * tailleMaxi / largeur
            largeur = tailleMaxi
        else:
            largeur = largeur * tailleMaxi / hauteur
            hauteur = tailleMaxi
    img.Rescale(width=largeur, height=hauteur, quality=wx.IMAGE_QUALITY_HIGH)
    position = (((TAILLE_IMAGE[0]/2.0) - (largeur/2.0)), ((TAILLE_IMAGE[1]/2.0) - (hauteur/2.0)))
    img.Resize(TAILLE_IMAGE, position, 255, 255, 255)
    return img


class Track(object):
    def __init__(self, parent, donnees):
        self.IDinscription = donnees[0]
        self.IDindividu = donnees[1]
        self.IDfamille = donnees[2]
        self.IDactivite = donnees[3]
        self.IDgroupe = donnees[4]
        self.IDcategorie_tarif = donnees[5]
        self.date_inscription = donnees[6]
        self.nom_activite = donnees[7]
        self.nom_groupe = donnees[8]
        self.nom_categorie = donnees[9]
        self.parti = donnees[10]
        self.date_debut = donnees[11]
        self.date_fin = donnees[12]
        self.logo_activite = donnees[13]
        self.bmp = self.GetImage()

        # Nom des titulaires de famille
        self.nomTitulaires = u"IDfamille n°%d" % self.IDfamille
        if parent.dictFamillesRattachees != None :
            if parent.dictFamillesRattachees.has_key(self.IDfamille) : 
                self.nomTitulaires = parent.dictFamillesRattachees[self.IDfamille]["nomsTitulaires"]

        # Validité de la pièce
        if str(datetime.date.today()) <= self.date_fin and self.parti != 1 :
            self.valide = True
        else:
            self.valide = False
            
    def GetImage(self):
        """ Récupère une image """            
        # Recherche de l'image
        if self.logo_activite != None :
            io = cStringIO.StringIO(self.logo_activite)
            img = wx.ImageFromStream(io, wx.BITMAP_TYPE_ANY)
            img = RecadreImg(img)
            bmp = img.ConvertToBitmap()
            return bmp
        else:
            # Si aucune image est trouvée, on prend l'image de l'organisateur
            return LOGO_ORGANISATEUR

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDindividu = kwds.pop("IDindividu", None)
        self.dictFamillesRattachees = kwds.pop("dictFamillesRattachees", {} )
        self.nbreFamilles = 0
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.GetLogoOrganisateur()
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
    
    def GetLogoOrganisateur(self):
        global LOGO_ORGANISATEUR
        DB = GestionDB.DB()
        req = "SELECT nom, logo FROM organisateur WHERE IDorganisateur=1;"
        DB.ExecuterReq(req)
        nom, logo = DB.ResultatReq()[0]
        DB.Close()
        if logo != None :
            io = cStringIO.StringIO(logo)
            img = wx.ImageFromStream(io, wx.BITMAP_TYPE_ANY)
            img = RecadreImg(img)
            bmp = img.ConvertToBitmap()
        else:
            # Création d'une image vide si l'organisateur n'a pas de logo
            img = wx.EmptyImage(TAILLE_IMAGE[0], TAILLE_IMAGE[1])
            img.SetRGBRect((0, 0, TAILLE_IMAGE[0], TAILLE_IMAGE[1]), 255, 255, 255)
            bmp = img.ConvertToBitmap()
        LOGO_ORGANISATEUR = bmp
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        DB = GestionDB.DB()
        req = """SELECT IDinscription, IDindividu, IDfamille, 
        inscriptions.IDactivite, inscriptions.IDgroupe, inscriptions.IDcategorie_tarif, date_inscription, 
        activites.nom, groupes.nom, categories_tarifs.nom,
        inscriptions.parti, activites.date_debut, activites.date_fin, activites.logo
        FROM inscriptions 
        LEFT JOIN activites ON inscriptions.IDactivite=activites.IDactivite
        LEFT JOIN groupes ON inscriptions.IDgroupe=groupes.IDgroupe
        LEFT JOIN categories_tarifs ON inscriptions.IDcategorie_tarif=categories_tarifs.IDcategorie_tarif
        WHERE IDindividu=%d
        ORDER BY activites.nom; """ % self.IDindividu
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        listeListeView = []
        listeIDfamilles = []
        for item in listeDonnees :
            IDfamille = item[2]
            if IDfamille not in listeIDfamilles :
                listeIDfamilles.append(IDfamille)
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(self, item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track

        self.nbreFamilles = len(listeIDfamilles)
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Création du imageList avec une taille personnalisée
        dictImages = {}
        imageList = wx.ImageList(TAILLE_IMAGE[0], TAILLE_IMAGE[1])
        for track in self.donnees :
            indexImg = imageList.Add(track.bmp)            
            dictImages[track.IDactivite] = indexImg
        self.SetImageLists(imageList, imageList)
                    
        def GetLogo(track):
            if dictImages.has_key(track.IDactivite) :
                return dictImages[track.IDactivite]
            else :
                return None

        def DateEngFr(textDate):
            if textDate != None :
                text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
            else:
                text = ""
            return text

        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour((180, 180, 180))

        if self.nbreFamilles > 1 :
            liste_Colonnes = [
                ColumnDefn(u"ID", "left", 0, "IDinscription"),
                ColumnDefn(u"", 'left', TAILLE_IMAGE[0]+1, "", imageGetter=GetLogo),
                ColumnDefn(u"Date", 'center', 70, "date_inscription", stringConverter=DateEngFr),
                ColumnDefn(u"Nom de l'activité", 'left', 110, "nom_activite", isSpaceFilling=True),
                ColumnDefn(u"Groupe", 'left', 80, "nom_groupe"),
                ColumnDefn(u"Catégorie de tarifs", 'left', 110, "nom_categorie"),
                ColumnDefn(u"Famille", 'left', 110, "nomTitulaires"),
                ]
        else:
            liste_Colonnes = [
                ColumnDefn(u"ID", "left", 0, "IDinscription"),
                ColumnDefn(u"", 'left', TAILLE_IMAGE[0]+1, "", imageGetter=GetLogo),
                ColumnDefn(u"Date", 'center', 70, "date_inscription", stringConverter=DateEngFr),
                ColumnDefn(u"Nom de l'activité", 'left', 160, "nom_activite", isSpaceFilling=True),
                ColumnDefn(u"Groupe", 'left', 100, "nom_groupe"),
                ColumnDefn(u"Catégorie de tarifs", 'left', 140, "nom_categorie"),
                ]

        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucune activité")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        if ID != None :
            self.selectionID = ID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
        self._ResizeSpaceFillingColumns() 
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDinscription
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, u"Ajouter")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, u"Modifier")
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, u"Supprimer")
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()

        # Item Editer Confirmation d'inscription
        item = wx.MenuItem(menuPop, 60, u"Editer une confirmation d'inscription (PDF)")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EditerConfirmation, id=60)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()

        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, u"Aperçu avant impression")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, u"Imprimer")
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, u"Exporter au format Texte")
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, u"Exporter au format Excel")
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des inscriptions", format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des inscriptions", format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=u"Liste des inscriptions")
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=u"Liste des inscriptions")

    def Ajouter(self, event):
        # Recherche si l'individu est rattaché à d'autres familles
        listeNoms = []
        listeFamille = []
        # Vérifie que l'individu est rattaché comme REPRESENTANT ou ENFANT à une famille
        if self.dictFamillesRattachees != None :
            valide = False
            for IDfamille, dictFamille in self.dictFamillesRattachees.iteritems() :
                if dictFamille["IDcategorie"] in (1, 2) :
                    valide = True
            if valide == False :
                dlg = wx.MessageDialog(self, u"Pour être inscrit à une activité, un individu doit obligatoirement être\nrattaché comme représentant ou enfant à une fiche famille !", u"Inscription impossible", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        if len(self.dictFamillesRattachees) == 1 :
            IDfamille = self.dictFamillesRattachees.keys()[0]
            listeFamille.append(IDfamille)
            listeNoms.append(self.dictFamillesRattachees[IDfamille]["nomsTitulaires"])
        else:
            # Si rattachée à plusieurs familles
            for IDfamille, dictFamille in self.dictFamillesRattachees.iteritems() :
                IDcategorie = dictFamille["IDcategorie"]
                if IDcategorie in (1, 2) :
                    listeFamille.append(IDfamille)
                    listeNoms.append(dictFamille["nomsTitulaires"])
                
            if len(listeFamille) == 1 :
                IDfamille = listeFamille[0]
            else:
                # On demande à quelle famille rattacher cette inscription
                dlg = wx.SingleChoiceDialog(self, u"Cet individu est rattaché à %d familles.\nA quelle famille souhaitez-vous rattacher cette inscription ?" % len(listeNoms), u"Rattachements multiples", listeNoms, wx.CHOICEDLG_STYLE)
                if dlg.ShowModal() == wx.ID_OK:
                    indexSelection = dlg.GetSelection()
                    IDfamille = listeFamille[indexSelection]
                    dlg.Destroy()
                else:
                    dlg.Destroy()
                    return
        
        # Recherche de la ville de l'individu pour sélection auto de la catégorie de tarif
        cp, ville = None, None
        try :
            dictAdresse = self.GetGrandParent().GetPageAvecCode("coords").GetAdresseIndividu()
            cp = dictAdresse["cp"]
            ville = dictAdresse["ville"]
        except :
            pass
            
        # Ouverture de la fenêtre d'inscription
        import DLG_Inscription
        dlg = DLG_Inscription.Dialog(self, cp=cp, ville=ville)
        dlg.SetFamille(listeNoms, listeFamille, IDfamille, False)
        if dlg.ShowModal() == wx.ID_OK:
            IDfamille = dlg.GetIDfamille()
            IDactivite = dlg.GetIDactivite()
            IDgroupe = dlg.GetIDgroupe()
            IDcategorie_tarif = dlg.GetIDcategorie()
            nomActivite = dlg.GetNomActivite()
            nomGroupe = dlg.GetNomGroupe() 
            nomCategorie = dlg.GetNomCategorie() 
            IDcompte_payeur = self.GetCompteFamille(IDfamille)
            parti = dlg.GetParti() 
            
            # Verrouillage utilisateurs
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_inscriptions", "creer", IDactivite=IDactivite) == False : 
                return
            
            # Vérifie que l'individu n'est pas déjà inscrit à cette activite
            for inscription in self.donnees :
                if inscription.IDactivite == IDactivite and inscription.IDfamille == IDfamille :
                    dlg2 = wx.MessageDialog(self, u"Cet individu est déjà inscrit à l'activité '%s' !" % inscription.nom_activite, u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
                    dlg2.ShowModal()
                    dlg2.Destroy()
                    dlg.Destroy()
                    return
            
            # Sauvegarde
            DB = GestionDB.DB()
            listeDonnees = [
                ("IDindividu", self.IDindividu ),
                ("IDfamille", IDfamille ),
                ("IDactivite", IDactivite ),
                ("IDgroupe", IDgroupe),
                ("IDcategorie_tarif", IDcategorie_tarif),
                ("IDcompte_payeur", IDcompte_payeur),
                ("date_inscription", str(datetime.date.today()) ),
                ("parti", parti),
                ]
            IDinscription = DB.ReqInsert("inscriptions", listeDonnees)
            DB.Close()
            
            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDindividu" : self.IDindividu,
                "IDfamille" : IDfamille,
                "IDcategorie" : 18, 
                "action" : u"Inscription à l'activité '%s' sur le groupe '%s' avec la tarification '%s'" % (nomActivite, nomGroupe, nomCategorie)
                },])
            
            # Actualise l'affichage
            self.MAJ(IDinscription)
            
            # Saisie de forfaits auto
            import DLG_Appliquer_forfait
            f = DLG_Appliquer_forfait.Forfaits(IDfamille=IDfamille, listeActivites=[IDactivite,], listeIndividus=[self.IDindividu,], saisieManuelle=False, saisieAuto=True)
            f.Applique_forfait(selectionIDcategorie_tarif=IDcategorie_tarif, inscription=True, selectionIDactivite=IDactivite) 
    
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune inscription à modifier dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Recherche si l'individu est rattaché à d'autres familles
        listeNoms = []
        listeFamille = []
        for IDfamille, dictFamille in self.dictFamillesRattachees.iteritems() :
            listeFamille.append(IDfamille)
            listeNoms.append(dictFamille["nomsTitulaires"])

        import DLG_Inscription
        IDinscription = self.Selection()[0].IDinscription
        IDfamille = self.Selection()[0].IDfamille
        dlg = DLG_Inscription.Dialog(self)
        dlg.SetFamille(listeNoms, listeFamille, self.Selection()[0].IDfamille, True)
        dlg.SetIDactivite(self.Selection()[0].IDactivite)
        dlg.ctrl_activites.Enable(False)
        dlg.SetIDgroupe(self.Selection()[0].IDgroupe)
        dlg.SetIDcategorie(self.Selection()[0].IDcategorie_tarif)
        dlg.SetParti(self.Selection()[0].parti)
        if dlg.ShowModal() == wx.ID_OK:
            IDactivite = dlg.GetIDactivite()
            IDgroupe = dlg.GetIDgroupe()
            IDcategorie_tarif = dlg.GetIDcategorie()
            nomActivite = dlg.GetNomActivite()
            nomGroupe = dlg.GetNomGroupe() 
            nomCategorie = dlg.GetNomCategorie() 
            parti = dlg.GetParti() 

            # Verrouillage utilisateurs
            if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_inscriptions", "modifier", IDactivite=IDactivite) == False : 
                return

            # Sauvegarde
            DB = GestionDB.DB()
            listeDonnees = [
                ("IDindividu", self.IDindividu ),
                ("IDactivite", IDactivite ),
                ("IDgroupe", IDgroupe),
                ("IDcategorie_tarif", IDcategorie_tarif),
                ("parti", parti),
                ]
            DB.ReqMAJ("inscriptions", listeDonnees, "IDinscription", IDinscription)
            DB.Close()
            
            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDindividu" : self.IDindividu,
                "IDfamille" : IDfamille,
                "IDcategorie" : 20, 
                "action" : u"Modification de l'inscription à l'activité '%s' sur le groupe '%s' avec la tarification '%s'" % (nomActivite, nomGroupe, nomCategorie)
                },])

            # Actualise l'affichage
            self.MAJ(IDinscription)
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune inscription à supprimer dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDinscription = self.Selection()[0].IDinscription
        IDfamille = self.Selection()[0].IDfamille
        IDindividu = self.Selection()[0].IDindividu
        nomActivite = self.Selection()[0].nom_activite
        IDactivite = self.Selection()[0].IDactivite

        # Verrouillage utilisateurs
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_inscriptions", "supprimer", IDactivite=IDactivite) == False : 
            return

        DB = GestionDB.DB()
        
        # Recherche si des consommations existent
        req = """SELECT IDconso, forfait
        FROM consommations
        WHERE IDinscription=%d AND (forfait IS NULL OR forfait=1);""" % IDinscription
        DB.ExecuterReq(req)
        listeConso = DB.ResultatReq()     
        if len(listeConso) > 0 :
            dlg = wx.MessageDialog(self, u"Il existe déjà %d consommations enregistrées sur cette inscription. \n\nIl est donc impossible de la supprimer !" % len(listeConso), u"Annulation impossible", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close() 
            return
        
        # Recherche si des prestations existent
        req = """SELECT IDprestation, prestations.forfait
        FROM prestations
        WHERE IDactivite=%d AND IDindividu=%d
        ;""" % (IDactivite, IDindividu)
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        listePrestationsForfait = []
        listePrestationsNormales = []
        for IDprestation, forfait in listePrestations :
            if forfait == 2 : 
                if IDprestation not in listePrestationsForfait : 
                    listePrestationsForfait.append(IDprestation)
            else:
                if IDprestation not in listePrestationsNormales : 
                    listePrestationsNormales.append(IDprestation)
        if len(listePrestations) - len(listePrestationsForfait) > 0 :
            dlg = wx.MessageDialog(self, u"Il existe déjà %d prestations enregistrées sur cette inscription. \n\nIl est donc impossible de la supprimer !" % len(listePrestations), u"Annulation impossible", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close() 
            return
        
        DB.Close() 

        # Demande de confirmation
        if len(listePrestationsForfait) == 0 : texteForfait = u""
        elif len(listePrestationsForfait) == 1 : texteForfait = u"\n\n(La prestation associée sera également supprimée)"
        else : texteForfait = u"\n\n(Les %d prestations associées seront également supprimées)" % len(listePrestationsForfait)
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment supprimer cette inscription ?%s" % texteForfait, u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDinscription = self.Selection()[0].IDinscription
            DB = GestionDB.DB()
            DB.ReqDEL("inscriptions", "IDinscription", IDinscription)
            # Suppression des forfaits associés déjà saisis
            for IDprestation in listePrestationsForfait :
                DB.ReqDEL("prestations", "IDprestation", IDprestation)
                DB.ReqDEL("consommations", "IDprestation", IDprestation)
                DB.ReqDEL("deductions", "IDprestation", IDprestation)
                DB.ReqDEL("ventilation", "IDprestation", IDprestation)
            DB.Close() 
            
            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDindividu" : self.IDindividu,
                "IDfamille" : IDfamille,
                "IDcategorie" : 19, 
                "action" : u"Suppression de l'inscription à l'activité '%s'" % nomActivite
                },])
                
            # Actualise l'affichage
            self.MAJ()
        dlg.Destroy()

    def GetCompteFamille(self, IDfamille=None):
        """ Récupère le compte_payeur par défaut de la famille """
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
    
    def GetListeActivites(self):
        """ Retourne la liste des activités sur lesquelles l'individu est inscrit """
        """ Sert pour le ctrl DLG_Individu_inscriptions (saisir d'un forfait daté) """
        listeActivites = []
        for track in self.donnees :
            listeActivites.append(track.IDactivite)
        listeActivites.sort()
        return listeActivites

    def EditerConfirmation(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune inscription dans la liste !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDinscription = self.Selection()[0].IDinscription
        import DLG_Impression_inscription
        dlg = DLG_Impression_inscription.Dialog(self, IDinscription=IDinscription) 
        dlg.ShowModal()
        dlg.Destroy()

        
        
# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher une inscription...")
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh() 



# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, IDindividu=3, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
