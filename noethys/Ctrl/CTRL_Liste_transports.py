#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import sys
import FonctionsPerso
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB

from Utils import UTILS_Transports
from Utils import UTILS_Organisateur
from Utils import UTILS_Utilisateurs
from Data import DATA_Civilites
DICT_CIVILITES = DATA_Civilites.GetDictCivilites() 
from Data.DATA_Tables import DB_DATA as DICT_TABLES
from CTRL_Saisie_transport import DICT_CATEGORIES

COULEUR_FOND_REGROUPEMENT = (220, 220, 220)

            
def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
def PeriodeComplete(mois, annee):
    listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete








class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.dictImpression = {}
        self.dictIndexColonnes = {}
        
        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        # Création de l'ImageList
        self.dictImages = {
            "ligne" : {"img" : wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Ligne.png'), wx.BITMAP_TYPE_PNG), "index" : None, "nomFichier":"Ligne"},
            "arret" : {"img" : wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Drapeau.png'), wx.BITMAP_TYPE_PNG), "index" : None, "nomFichier":"Drapeau"},
            }
        for code, valeurs in DICT_CATEGORIES.items() :
            self.dictImages[code] = {"img" : wx.Bitmap(Chemins.GetStaticPath('Images/16x16/%s.png' % valeurs["image"]), wx.BITMAP_TYPE_PNG), "index" : None, "nomFichier":valeurs["image"]}
        
        il = wx.ImageList(16, 16)
        index =0
        for code, dictImage in self.dictImages.items() :
            il.Add(dictImage["img"])
            dictImage["index"] = index
            index += 1
        self.AssignImageList(il)
        
        # Style
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | TR_COLUMN_LINES |wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

        # Binds
##        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
    
    def MAJ(self, listeDates=[], dictFiltres={}):
        """ Met à jour (redessine) tout le contrôle """
        # Mémorisation pour impression
        self.dictImpression = {"donnees" : [], "dates": listeDates}
        # MAJ
        self.DeleteAllItems()
        self.SupprimeColonnes() 
        self.CreationColonnes(listeDates) 
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage(listeDates, dictFiltres)
        
    def SupprimeColonnes(self):
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        
    def CreationColonnes(self, listeDates=[]):
        # Création des colonnes
        listeColonnes = [(u"", 300, wx.ALIGN_LEFT),]
        
        self.dictIndexColonnes = {}
        index = 1
        for date in listeDates :
            label = DateEngFr(str(date))
            listeColonnes.append((label, 80, wx.ALIGN_CENTER))
            self.dictIndexColonnes[date] = index
            index += 1
        
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1

    def Remplissage(self, listeDates=[], dictFiltres={}):        
        # Importation des données
        DB = GestionDB.DB()
        
        # Création de la condition
        if len(listeDates) == 0 : 
            conditionDates = "depart_date='2999-01-01' "
        elif len(listeDates) == 1 : 
            conditionDates = "(depart_date='%s' OR arrivee_date='%s')" % (listeDates[0], listeDates[0])
        else : 
            listeTmp = []
            for dateTmp in listeDates :
                listeTmp.append(str(dateTmp))
            conditionDates = "(depart_date IN %s OR arrivee_date IN %s)" % (str(tuple(listeTmp)), str(tuple(listeTmp)))
        
        # Récupération des lignes
        req = """SELECT IDligne, categorie, nom
        FROM transports_lignes;""" 
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        dictLignes = {}
        for IDligne, categorie, nom in listeValeurs :
            dictLignes[IDligne] = nom
            
        # Récupération des arrêts
        req = """SELECT IDarret, IDligne, nom
        FROM transports_arrets
        ORDER BY ordre;""" 
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        dictArrets = {}
        for IDarret, IDligne, nom in listeValeurs :
            dictArrets[IDarret] = {"IDligne":IDligne, "nom":nom}
            
        # Récupération des lieux
        req = """SELECT IDlieu, categorie, nom
        FROM transports_lieux;""" 
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        dictLieux = {}
        for IDlieu, categorie, nom in listeValeurs :
            dictLieux[IDlieu] = nom

        # Récupération des individus
        req = """SELECT IDindividu, nom, prenom
        FROM individus;""" 
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        dictIndividus = {}
        for IDindividu, nom, prenom in listeValeurs :
            dictIndividus[IDindividu] = u"%s %s" % (nom, prenom)

        # Récupération des transports
        listeChamps = []
        for nom, type, info in DICT_TABLES["transports"] :
            listeChamps.append(nom)
        DB = GestionDB.DB()
        req = """SELECT %s
        FROM transports 
        WHERE %s;""" % (", ".join(listeChamps), conditionDates)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        
        listeTransports = []
        for ligne in listeDonnees :
            index = 0
            dictTemp = {}
            for valeur in ligne :
                nomChamp = listeChamps[index]
                if "date" in nomChamp : 
                    valeur = DateEngEnDateDD(valeur)
                dictTemp[nomChamp] = valeur
                index += 1
            listeTransports.append(dictTemp)
        
        def VerifieFiltre(rubrique, code):
            if rubrique in dictFiltres :
                if code in dictFiltres[rubrique] or code == None :
                    return True
            return False
            
        # Tri des transports dans des dictionnaires
        dictDonnees = {}
        for dictTransport in listeTransports :
            
            categorie = dictTransport["categorie"]
            if VerifieFiltre("categories", categorie) == True :
            
                # Catégorie
                if (categorie in dictDonnees) == False :
                    dictDonnees[categorie] = {"lignes":{}, "lieux":{}, "localisations":{}}
                
                typeTransports = DICT_CATEGORIES[categorie]["type"]
                
                for prefixe in ("depart", "arrivee") :
                    
                    if dictTransport["%s_date" % prefixe] in listeDates :
                            
                        dictIndividu = {"IDtransport" : dictTransport["IDtransport"], "IDindividu" : dictTransport["IDindividu"], "sens":prefixe}
                        
                        # ------------ Lignes ----------------
                        if typeTransports == "lignes" :

                            # Lignes
                            IDligne = dictTransport["IDligne"]
                            if VerifieFiltre("lignes", IDligne) == True :

                                if IDligne not in dictDonnees[categorie]["lignes"] :
                                    dictDonnees[categorie]["lignes"][IDligne] = {}

                                # Arrets
                                IDarret = dictTransport["%s_IDarret" % prefixe]
                                if VerifieFiltre("arrets", IDarret) == True :
                                    
                                    if IDarret not in dictDonnees[categorie]["lignes"][IDligne] :
                                        dictDonnees[categorie]["lignes"][IDligne][IDarret] = {}
                                    
                                    # Heures
                                    heure = dictTransport["%s_heure" % prefixe]
                                    if heure not in dictDonnees[categorie]["lignes"][IDligne][IDarret] :
                                        dictDonnees[categorie]["lignes"][IDligne][IDarret][heure] = {}
                                    
                                    # Dates
                                    date = dictTransport["%s_date" % prefixe]
                                    if date not in dictDonnees[categorie]["lignes"][IDligne][IDarret][heure] :
                                        dictDonnees[categorie]["lignes"][IDligne][IDarret][heure][date] = []
                                    
                                    # Ajout de l'individu
                                    dictDonnees[categorie]["lignes"][IDligne][IDarret][heure][date].append(dictIndividu)
                        
                        
                        # -------------- Lieux --------------
                        if typeTransports == "lieux" :
                            
                            IDlieu = dictTransport["%s_IDlieu" % prefixe]
                            if VerifieFiltre("lieux", IDlieu) == True :
                                
                                if IDlieu not in dictDonnees[categorie]["lieux"] :
                                    dictDonnees[categorie]["lieux"][IDlieu] = {}
                                    
                                # Heures
                                heure = dictTransport["%s_heure" % prefixe]
                                if heure not in dictDonnees[categorie]["lieux"][IDlieu] :
                                    dictDonnees[categorie]["lieux"][IDlieu][heure] = {}
                                
                                # Dates
                                date = dictTransport["%s_date" % prefixe]
                                if date not in dictDonnees[categorie]["lieux"][IDlieu][heure] :
                                    dictDonnees[categorie]["lieux"][IDlieu][heure][date] = []
                                
                                # Ajout de l'individu
                                dictDonnees[categorie]["lieux"][IDlieu][heure][date].append(dictIndividu)
                        
                        
                        # -------------- Localisation --------------
                        if typeTransports == "localisations" :
                            
                            localisation = dictTransport["%s_localisation" % prefixe]
                            if localisation not in dictDonnees[categorie]["localisations"] :
                                dictDonnees[categorie]["localisations"][localisation] = {}
                                
                            # Heures
                            heure = dictTransport["%s_heure" % prefixe]
                            if heure not in dictDonnees[categorie]["localisations"][localisation] :
                                dictDonnees[categorie]["localisations"][localisation][heure] = {}
                            
                            # Dates
                            date = dictTransport["%s_date" % prefixe]
                            if date not in dictDonnees[categorie]["localisations"][localisation][heure] :
                                dictDonnees[categorie]["localisations"][localisation][heure][date] = []
                            
                            # Ajout de l'individu
                            dictDonnees[categorie]["localisations"][localisation][heure][date].append(dictIndividu)
        
        
        # ------------------ Remplissage ---------------------
        self.listeBranches = []
        modLocalisation = UTILS_Transports.AnalyseLocalisation() 
        
        # -----------------------------------------------------------------------------------------------------
        
        def InsertionBranchesHeures(dictDonnees, niveauParent, marge=0):
            # Heures
            listeheures = []
            for heure, dictHeure in dictDonnees.items() :
                listeheures.append((heure, dictHeure))
            listeheures.sort() 
            
            for heure, dictHeure in listeheures :
                if heure != None :
                    label = heure.replace(":", "h")
                else :
                    label = _(u"Heure inconnue")
                niveauHeure = self.AppendItem(niveauParent, label)
                self.SetPyData(niveauHeure, {"type":"heures", "code":heure})
                
                # Totaux par heure
                dictImpressionColonnes = {}
                for date, listeIndividus in dictHeure.items() :
                    indexColonne = self.dictIndexColonnes[date]
                    labelTotal = str(len(listeIndividus))
                    self.SetItemText(niveauHeure, labelTotal, indexColonne)
                    dictImpressionColonnes[indexColonne] = labelTotal
                    
                dictImpressionTemp["elements"].append({"type":"heures", "texte":label, "marge":marge, "colonnes":dictImpressionColonnes})
                
                # Individus
                dictIndividusTemp = {}
                for date, listeIndividus in dictHeure.items() :
                    for dictIndividu in listeIndividus :
                        IDindividu = dictIndividu["IDindividu"]
                        sens = dictIndividu["sens"]
                        if (IDindividu in dictIndividusTemp) == False :
                            dictIndividusTemp[IDindividu] = {}
                        dictIndividusTemp[IDindividu][date] = sens
                
                listeIndividusTemp = []
                for IDindividu, dictDates in dictIndividusTemp.items() :
                    if IDindividu in dictIndividus :
                        label = dictIndividus[IDindividu]
                    else :
                        label = _(u"Individu inconnu")
                    listeIndividusTemp.append((label, IDindividu, dictDates))
                listeIndividusTemp.sort() 
                
                for label, IDindividu, dictDates in listeIndividusTemp :
                    labelIndividu = label
                    niveauIndividu = self.AppendItem(niveauHeure, labelIndividu)
                    self.SetPyData(niveauIndividu, {"type":"individus", "code":IDindividu})
                    
                    # Dates
                    dictImpressionColonnes = {}
                    for date, sens in dictDates.items() :
                        # Recherche la colonne date
                        if date in self.dictIndexColonnes :
                            indexColonne = self.dictIndexColonnes[date]
                            if sens == "depart" : label = _(u"Départ")
                            elif sens == "arrivee" : label = _(u"Arrivée")
                            else : label = u""
                            self.SetItemText(niveauIndividu, label, indexColonne)
                            dictImpressionColonnes[indexColonne] = label
                    
                    dictImpressionTemp["elements"].append({"type":"individus", "texte":labelIndividu, "marge":marge+1, "colonnes":dictImpressionColonnes})
        
        # -----------------------------------------------------------------------------------------------------
        
        
        listeCategories = []
        if len(dictDonnees) > 0 :
            listeCategories = list(dictDonnees.keys()) 
        listeCategories.sort() 

        # Remplissage
        for categorie in listeCategories :
            
            # Catégories
            label = DICT_CATEGORIES[categorie]["label"]
            brancheCategorie = self.AppendItem(self.root, label)
            self.SetPyData(brancheCategorie, {"type":"categories", "code":categorie})
            self.SetItemBold(brancheCategorie)
            self.SetItemBackgroundColour(brancheCategorie, wx.Colour(*COULEUR_FOND_REGROUPEMENT))
            self.SetItemImage(brancheCategorie, self.dictImages[categorie]["index"])
            
            dictImpressionTemp = {"texte":label, "img":self.dictImages[categorie]["nomFichier"], "elements":[]}
            
            # Lignes
            listeLignes = []
            for IDligne, dictLigne in dictDonnees[categorie]["lignes"].items() :
                if IDligne in dictLignes :
                    label = dictLignes[IDligne]
                else :
                    label = _(u"Ligne inconnue")
                listeLignes.append((label, IDligne))
            listeLignes.sort() 

            for label, IDligne in listeLignes :
                niveauLigne = self.AppendItem(brancheCategorie, label)
                self.SetPyData(niveauLigne, {"type":"lignes", "code":IDligne})
                dictImpressionTemp["elements"].append({"type":"lignes", "texte":label, "marge":1})
                
                # Arrêts
                listeArrets = []
                for IDarret, dictArret in dictDonnees[categorie]["lignes"][IDligne].items() :
                    if IDarret in dictArrets :
                        label = dictArrets[IDarret]["nom"]
                    else :
                        label = _(u"Arrêt inconnu")
                    listeArrets.append((label, IDarret, dictArret))
                listeArrets.sort() 
                
                for label, IDarret, dictArret in listeArrets :
                    niveauArret = self.AppendItem(niveauLigne, label)
                    self.SetPyData(niveauArret, {"type":"arrets", "code":IDarret})
                    dictImpressionTemp["elements"].append({"type":"arrets", "texte":label, "marge":2})
                    
                    # Insertion des branches Heures et Individus
                    InsertionBranchesHeures(dictArret, niveauArret, marge=3)
                       
            
            # Lieux
            listeLieux = []
            for IDlieu, dictLieu in dictDonnees[categorie]["lieux"].items() :
                if IDlieu in dictLieux :
                    label = dictLieux[IDlieu]
                else :
                    label = _(u"Lieu inconnu")
                listeLieux.append((label, IDlieu, dictLieu))
            listeLieux.sort() 
            
            for label, IDlieu, dictLieu in listeLieux :
                niveauLieu = self.AppendItem(brancheCategorie, label)
                self.SetPyData(niveauLieu, {"type":"lieux", "code":IDlieu})
                dictImpressionTemp["elements"].append({"type":"lieux", "texte":label, "marge":1})
                
                # Insertion des branches Heures et Individus
                InsertionBranchesHeures(dictLieu, niveauLieu, marge=2)

            # Localisations
            listeLocalisations = []
            for localisation, dictLocalisation in dictDonnees[categorie]["localisations"].items() :
                label = modLocalisation.Analyse(localisation=localisation)
                listeLocalisations.append((label, localisation, dictLocalisation))
            listeLocalisations.sort() 
            
            for label, localisation, dictLocalisation in listeLocalisations :
                niveauLocalisation = self.AppendItem(brancheCategorie, label)
                self.SetPyData(niveauLocalisation, {"type":"localisations", "code":localisation})
                dictImpressionTemp["elements"].append({"type":"localisations", "texte":label, "marge":1})
                
                # Insertion des branches Heures et Individus
                InsertionBranchesHeures(dictLocalisation, niveauLocalisation, marge=2)

            
            # Mémorisation du bloc catégorie pour impression PDF
            self.dictImpression["donnees"].append(dictImpressionTemp)
            
        self.ExpandAllChildren(self.root)
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        categorie = dictItem["categorie"]
        if categorie != "individus" : return
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDindividu = dictItem["code"]
        print(IDindividu) # Fonction pas terminée ici
##        from Dlg import DLG_Famille
##        dlg = DLG_Famille.Dialog(self, IDfamille=IDfamille)
##        dlg.ShowModal()
##        dlg.Destroy()
##        self.MAJ() 
        
    
    def Imprimer(self, event=None):
        listeDates = self.dictImpression["dates"]
        if len(listeDates) > 26 :
            dlg = wx.MessageDialog(self, _(u"Désolé mais vous ne pouvez pas imprimer plus de 26 jours sur une feuille !"), _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        
        # Recherche le format de la page à appliquer
        largeurPremiereColonne = 140
        largeurColonnesDates = 24
        largeurMax = largeurPremiereColonne + (largeurColonnesDates*len(listeDates))
        
        if largeurMax <= 520 :
            # Format Portrait
            largeurPage, hauteurPage = defaultPageSize
            largeurContenu = 520
        else :
            # Format Paysage
            hauteurPage, largeurPage = defaultPageSize
            largeurContenu = 770

        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("LISTE_TRANSPORTS", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeurPage, hauteurPage), topMargin=30, bottomMargin=30)
        story = []
        
        # Création du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (largeurContenu-100, 100) )
            dateDuJour = DateEngFr(str(datetime.date.today()))
            dataTableau.append( (_(u"Liste des transports"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        
        # Insère un header
        Header() 
        
        # Contenu
        for dictCategorie in self.dictImpression["donnees"] :
            label = dictCategorie["texte"]
            img = dictCategorie["img"]
            elements = dictCategorie["elements"]
            
            dataTableau = []
            largeursColonnes = [largeurPremiereColonne,]
            
            # Création de la ligne de date
            paraStyle = ParagraphStyle(name="categorie",
                      fontName="Helvetica-Bold",
                      fontSize=9,
                      leading=8,
                      spaceAfter=2,)

            ligne = [ParagraphAndImage(Paragraph(label, paraStyle), Image(Chemins.GetStaticPath("Images/32x32/%s.png" % img), width=8, height=8), xpad=1, ypad=0, side="left"),]
            for date in listeDates :
                ligne.append(u"%02d/%02d\n%04d" % (date.day, date.month, date.year))
                largeursColonnes.append(largeurColonnesDates)
            dataTableau.append(ligne)
        
            # Création des lignes
            listeExtraStyles = []
            index = 1
            for element in elements :
                
                # Décoration de la ligne
                if element["type"] in ("lieux", "lignes", "localisations") :
                    listeExtraStyles.append(('BACKGROUND', (0, index), (-1, index), (0.8, 0.8, 1) ))

                if element["type"] == "arrets" :
                    listeExtraStyles.append(('BACKGROUND', (0, index), (-1, index), (0.9, 0.9, 1) ))

                if element["type"] == "heures" :
                    listeExtraStyles.append(('FONT',(0, index), (0, index), "Helvetica-Bold", 6),)
                    listeExtraStyles.append(('FONT',(1, index), (-1, index), "Helvetica", 5),)
                    listeExtraStyles.append(('TEXTCOLOR',(1, index), (-1, index), (0.6, 0.6, 0.6)),)

                if element["type"] == "individus" :
                    listeExtraStyles.append(('ALIGN', (0, index), (0, index), 'RIGHT'))
                    listeExtraStyles.append(('GRID', (1, index), (-1, index), 0.25, colors.black))
                    listeExtraStyles.append(('FONT',(1, index), (-1, index), "Helvetica", 6),)

                # Ajout d'une marge
                label = element["texte"]
                if "marge" in element :
                    label = u"%s%s" % ((element["marge"]-1) * "      ", label)
                ligne = [label,]
                
                # Ajout des colonnes
                for indexColonne in range(1, len(largeursColonnes)) :
                    label = u""
                    if "colonnes" in element:
                        if indexColonne in element["colonnes"] :
                            label = element["colonnes"][indexColonne]
                    ligne.append(label)
                
                dataTableau.append(ligne)
                index += 1
        
            # Style du tableau
            listeStyles = [
                    ('VALIGN', (0, 0), (-1,-1), 'MIDDLE'), 
                    ('ALIGN', (1, 0), (-1, -1), 'CENTRE'),
                    ('FONT',(0, 0), (-1,-1), "Helvetica", 7), 
                    ('FONT',(0, 0), (0, 0), "Helvetica-Bold", 8),
                    ('BOX', (0, 1), (-1, -1), 0.25, colors.black), 
                    ('GRID', (1, 0), (-1, 0), 0.25, colors.black), 
                    ]
            
            for extraStyle in listeExtraStyles :
                listeStyles.append(extraStyle)
                
            # Création du tableau
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(TableStyle(listeStyles))
            story.append(tableau)
            story.append(Spacer(0, 15))
        
##        # TOTAUX
##        dataTableau = []
##        largeursColonnes = [220, 220, 40, 40]
##
##        for ligne in self.listeImpression["totaux"] :
##            dataTableau.append(ligne) 
##
##        couleurFond = (0.8, 0.8, 0.8)
##        listeStyles = [
##                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
##                ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
##                ('BOX', (0, 1), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
##                ('ALIGN', (2, 0), (-1, -1), 'CENTRE'), # Ligne de labels colonne alignée au centre
##                ('BOX', (0, 0), (-1,0), 0.25, colors.black), # Crée la bordure noire du nom de famille
##                ('FONT',(0,0),(0,0), "Helvetica-Bold", 8), # Donne la police de caract. + taille de police du titre de groupe
##                ('BACKGROUND', (0,0), (-1,0), couleurFond), # Donne la couleur de fond du titre de groupe
##                ('TOPPADDING',(0,0),(-1,-1), 1), 
##                ('BOTTOMPADDING',(0,0),(-1,-1), 1), 
##                ]
##            
##        # Création du tableau
##        tableau = Table(dataTableau, largeursColonnes)
##        tableau.setStyle(TableStyle(listeStyles))
##        story.append(tableau)

        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.myOlv = CTRL(panel)
        self.myOlv.MAJ(
            listeDates=[datetime.date(2012, 5, 22),], 
            dictFiltres={"lignes":[8,], "lieux":[5, 6, 4, 1], "categories":["avion", "taxi", "train", "bus",], "arrets":[1, 2]}
            )
        boutonTest = wx.Button(panel, -1, _(u"Test d'impression PDF"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, boutonTest)
    
    def OnBoutonTest(self, event):
        self.myOlv.Imprimer() 
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
