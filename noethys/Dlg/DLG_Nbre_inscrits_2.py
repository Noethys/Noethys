#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import sys, os
import datetime
import time
import GestionDB
import FonctionsPerso
from Utils import UTILS_Config
from Utils import UTILS_Interface
from Utils import UTILS_Organisateur
from Utils import UTILS_Dates

import wx.lib.agw.hypertreelist as HTL


COULEUR_DISPONIBLE = "#E3FEDB"
COULEUR_ALERTE = "#FEFCDB"
COULEUR_COMPLET = "#F7ACB2"
COULEUR_GAUGE_FOND = "WHITE"



class CTRL(HTL.HyperTreeList):
    def __init__(self, parent):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.listeActivites = []
        self.filtre = None
        self.dictImpression = { "entete" : [], "contenu" : [], "total" : [], "coloration" : [] }
        
        self.couleurFond = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        self.SetBackgroundColour(self.couleurFond)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_ROW_LINES | wx.TR_HAS_BUTTONS | wx.TR_COLUMN_LINES | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT )

        # Génération des colonnes
        self.CreationColonnes()

        # Racine
        self.root = self.AddRoot(_(u"Racine"))

        # Binds
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)

    def CreationColonnes(self):
        """ Création des colonnes """
        liste_colonnes = [
            (_(u"Activité / Groupe"), 300, wx.ALIGN_LEFT),
            (_(u"Abrégé"), 80, wx.ALIGN_CENTER),
            (_(u"Inscrits"), 80, wx.ALIGN_CENTER),
            (_(u"Places max"), 90, wx.ALIGN_CENTER),
            (_(u"Places libres"), 90, wx.ALIGN_CENTER),
        ]
        index = 0
        for label, largeur, alignement in liste_colonnes :
            self.AddColumn(label)
            self.SetColumnWidth(index, largeur)
            self.SetColumnAlignment(index, alignement)
            self.dictImpression["entete"].append(label)
            index += 1

    def OnContextMenu(self, event):
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Actualiser
        item = wx.MenuItem(menuPop, 10, _(u"Consulter les tarifs de l'activité"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Euro.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirTarifs, id=10)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OnItemActivated(self, event):
        self.OuvrirTarifs()

    def OuvrirTarifs(self, event=None):
        item = self.GetSelection()
        data = self.GetMainWindow().GetItemPyData(item)
        if data == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDactivite = data["IDactivite"]
        import DLG_Liste_tarifs
        dlg = DLG_Liste_tarifs.DLG_Tarifs(self, IDactivite=IDactivite)
        dlg.ShowModal()
        dlg.Destroy()

    def MAJ(self, forcerActualisation=False):
        # Recherche des données
        condition = ""
        listeFiltreGroupesActivites = None

        DB = GestionDB.DB()

        # Recherche des paramètres
        parametres = UTILS_Config.GetParametre("nbre_inscrits_parametre_activites", defaut=None)
        if parametres != None :
            code, liste = parametres.split("###")
            if liste != "" :
                listeID = []
                for ID in liste.split(";") :
                    listeID.append(int(ID))
                if code == "liste_groupes_activites" :
                    listeFiltreGroupesActivites = listeID
                    req = """SELECT IDtype_groupe_activite, IDactivite
                    FROM groupes_activites
                    WHERE IDtype_groupe_activite IN %s
                    ;""" % GestionDB.ConvertConditionChaine(listeID)
                    DB.ExecuterReq(req)
                    listeDonnees = DB.ResultatReq()
                    listeActivites = []
                    for IDtype_groupe_activite, IDactivite in listeDonnees :
                        listeActivites.append(IDactivite)
                    condition = "WHERE activites.IDactivite IN %s" % GestionDB.ConvertConditionChaine(listeActivites)

                if code == "liste_activites" :
                    condition = "WHERE activites.IDactivite IN %s" % GestionDB.ConvertConditionChaine(listeID)

        # Tri
        tri = UTILS_Config.GetParametre("nbre_inscrits_parametre_tri", 3)
        if tri == 0 :
            tri = "activites.nom"
        elif tri == 1 :
            tri = "activites.date_debut"
        elif tri == 2 :
            tri = "activites.date_fin"
        elif tri == 3 :
            tri = "activites.abrege"
        else :
            tri = "activites.nom"
        
        # Sens
        sens = UTILS_Config.GetParametre("nbre_inscrits_parametre_sens", 1)
        if sens == 0 :
            sens = ""
        else :
            sens = "DESC"
        
        # Seuil d'alerte
        self.seuil_alerte = UTILS_Config.GetParametre("nbre_inscrits_parametre_alerte", 5)

        # Regroupement par groupe d'activités
        self.regroupement_groupe_activites = UTILS_Config.GetParametre("nbre_inscrits_parametre_regroup", 0)

        # Récupération des groupes
        condition_partis = ""
        if UTILS_Config.GetParametre("nbre_inscrits_parametre_partis", 1) == 1 :
            if condition == "" :
                condition_partis = "WHERE inscriptions.parti=0"
            else :
                condition_partis = "AND inscriptions.parti=0"

        req = """SELECT groupes.IDgroupe, groupes.IDactivite, groupes.nom, groupes.abrege, groupes.nbre_inscrits_max,
        COUNT(inscriptions.IDinscription) as nbre_inscriptions
        FROM groupes
        LEFT JOIN activites ON activites.IDactivite = groupes.IDactivite
        LEFT JOIN inscriptions ON inscriptions.IDgroupe = groupes.IDgroupe
        %s %s
        GROUP BY groupes.IDgroupe
        ORDER BY groupes.ordre
        ;""" % (condition, condition_partis)
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()

        dictGroupes = {}
        for IDgroupe, IDactivite, nom, abrege, nbre_inscrits_max, nbre_inscrits in listeGroupes :
            if nbre_inscrits == None : nbre_inscrits = 0
            if nom == None : nom = _(u"Sans nom !")
            if abrege == None : abrege = ""

            if nbre_inscrits_max != None :
                nbre_places_libres = nbre_inscrits_max - nbre_inscrits
            else :
                nbre_places_libres = None

            if dictGroupes.has_key(IDactivite) == False :
                dictGroupes[IDactivite] = []
            dictGroupes[IDactivite].append({"IDgroupe" : IDgroupe, "nom" : nom, "abrege" : abrege, "nbre_inscrits_max" : nbre_inscrits_max, "nbre_inscrits" : nbre_inscrits, "nbre_places_libres" : nbre_places_libres, "IDactivite" : IDactivite})

        # Récupération des activités
        activite_ouverte = UTILS_Config.GetParametre("nbre_inscrits_parametre_ouvert", 1)
        if activite_ouverte == 1 :
            if condition == "" :
                condition = "WHERE activites.date_fin>='%s'" % str(datetime.date.today())
            else :
                condition += " AND activites.date_fin>='%s'" % str(datetime.date.today())

        req = """SELECT activites.IDactivite, activites.nom, activites.abrege, activites.nbre_inscrits_max
        FROM activites
        %s
        GROUP BY activites.IDactivite
        ORDER BY %s %s
        ;""" % (condition, tri, sens)
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()

        listeActivitesTemp = []
        listeIDactivite = []
        for IDactivite, nom, abrege, nbre_inscrits_max in listeActivites :
            if nom == None : nom = _(u"Sans nom !")
            if abrege == None : abrege = ""

            liste_groupes = []
            if dictGroupes.has_key(IDactivite) :
                liste_groupes = dictGroupes[IDactivite]
            nbre_inscrits = 0
            liste_infos = [nom,]
            for dictGroupe in liste_groupes :
                nbre_inscrits += dictGroupe["nbre_inscrits"]
                liste_infos.append(dictGroupe["nom"])

            if nbre_inscrits_max != None :
                nbre_places_libres = nbre_inscrits_max - nbre_inscrits
            else :
                nbre_places_libres = None

            listeActivitesTemp.append({"IDactivite" : IDactivite, "nom" : nom, "abrege" : abrege, "nbre_inscrits_max" : nbre_inscrits_max, "nbre_inscrits" : nbre_inscrits, "nbre_places_libres" : nbre_places_libres, "liste_groupes" : liste_groupes, "infos" : " ".join(liste_infos)})
            listeIDactivite.append(IDactivite)

        # Pour éviter l'actualisation de l'affichage si aucune modification des données
        if self.listeActivites != listeActivitesTemp or forcerActualisation == True :
            self.listeActivites = listeActivitesTemp
        else :
            DB.Close()
            return

        # Récupération des groupes d'activités
        if self.regroupement_groupe_activites == 1 :

            req = """SELECT groupes_activites.IDtype_groupe_activite, nom, IDactivite
            FROM groupes_activites
            LEFT JOIN types_groupes_activites ON types_groupes_activites.IDtype_groupe_activite = groupes_activites.IDtype_groupe_activite
            WHERE IDactivite IN %s
            ;""" % GestionDB.ConvertConditionChaine(listeIDactivite)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            dictGroupeParActivite = {}
            dictGroupesActivites = {}
            for IDtype_groupe_activite, nom, IDactivite in listeDonnees :

                if not dictGroupeParActivite.has_key(IDactivite) :
                    dictGroupeParActivite[IDactivite] = []
                dictGroupeParActivite[IDactivite].append(IDtype_groupe_activite)

                if not dictGroupesActivites.has_key(IDtype_groupe_activite) :
                    dictGroupesActivites[IDtype_groupe_activite] = nom

            liste_groupes_activites = []
            for IDtype_groupe_activite, nom in dictGroupesActivites.iteritems() :
                if listeFiltreGroupesActivites == None or IDtype_groupe_activite in listeFiltreGroupesActivites :
                    liste_groupes_activites.append((nom.upper(), IDtype_groupe_activite))
            liste_groupes_activites.sort()

        else :
            liste_groupes_activites = [(None, None),]

        DB.Close()

        # MAJ du contrôle
        self.DeleteChildren(self.root)

        # Préparation pour impression
        self.dictImpression["contenu"] = []
        self.dictImpression["coloration"] = []


        for nom, IDtype_groupe_activite in liste_groupes_activites :
            if nom == None :
                niveau_parent = self.root
            else :
                niveau_regroup = self.AppendItem(self.root, nom)
                self.SetItemBackgroundColour(niveau_regroup, "#DDDDDD")
                self.dictImpression["contenu"].append([nom,])
                self.dictImpression["coloration"].append((len(self.dictImpression["contenu"])-1, "regroup"))
                niveau_parent = niveau_regroup

            for dictActivite in self.listeActivites :

                if self.filtre == None or (self.filtre.lower() in dictActivite["infos"].lower()) :

                    IDactivite = dictActivite["IDactivite"]
                    if self.regroupement_groupe_activites == 0 or (self.regroupement_groupe_activites == 1 and dictGroupeParActivite.has_key(IDactivite) and IDtype_groupe_activite in dictGroupeParActivite[IDactivite]) :

                        # Ligne Activité
                        label = u" " + dictActivite["nom"]
                        niveau_activite = self.AppendItem(niveau_parent, label)
                        font = self.GetFont()
                        font.SetWeight(wx.BOLD)
                        self.SetItemFont(niveau_activite, font)
                        self.SetPyData(niveau_activite, dictActivite)

                        # Abrégé
                        self.SetItemText(niveau_activite, dictActivite["abrege"], 1)

                        # Valeurs
                        nbre_inscrits = dictActivite["nbre_inscrits"]
                        if nbre_inscrits == None :
                            texte_inscrits = ""
                        else :
                            texte_inscrits = str(nbre_inscrits)
                        self.SetItemText(niveau_activite, texte_inscrits, 2)

                        nbre_inscrits_max = dictActivite["nbre_inscrits_max"]
                        if nbre_inscrits_max == None :
                            texte_inscrits_max = ""
                        else :
                            texte_inscrits_max = str(nbre_inscrits_max)
                        self.SetItemText(niveau_activite, texte_inscrits_max, 3)

                        nbre_places_libres = dictActivite["nbre_places_libres"]
                        if nbre_places_libres == None :
                            texte_places_libres = ""
                        else :
                            texte_places_libres = str(nbre_places_libres)
                        self.SetItemText(niveau_activite, texte_places_libres, 4)

                        # Couleur de la ligne
                        couleur_fond = self.GetCouleurLigne(nbre_places_libres)
                        if couleur_fond != None :
                            self.SetItemBackgroundColour(niveau_activite, couleur_fond)

                        # Mémorisation ligne activité pour impression
                        self.dictImpression["contenu"].append([label, dictActivite["abrege"], texte_inscrits, texte_inscrits_max, texte_places_libres])
                        self.dictImpression["coloration"].append((len(self.dictImpression["contenu"])-1, "activite"))

                        # Ligne Groupe
                        for dictGroupe in dictActivite["liste_groupes"] :

                            label = u" " + dictGroupe["nom"]
                            niveau_groupe = self.AppendItem(niveau_activite, label)
                            self.SetPyData(niveau_groupe, dictGroupe)

                            # Abrégé
                            self.SetItemText(niveau_groupe, dictGroupe["abrege"], 1)

                            nbre_inscrits = dictGroupe["nbre_inscrits"]
                            if nbre_inscrits == None :
                                texte_inscrits = ""
                            else :
                                texte_inscrits = str(nbre_inscrits)
                            self.SetItemText(niveau_groupe, texte_inscrits, 2)

                            nbre_inscrits_max = dictGroupe["nbre_inscrits_max"]
                            if nbre_inscrits_max == None :
                                texte_inscrits_max = ""
                            else :
                                texte_inscrits_max = str(nbre_inscrits_max)
                            self.SetItemText(niveau_groupe, texte_inscrits_max, 3)

                            nbre_places_libres = dictGroupe["nbre_places_libres"]
                            if nbre_places_libres == None :
                                texte_places_libres = ""
                            else :
                                texte_places_libres = str(nbre_places_libres)
                            self.SetItemText(niveau_groupe, texte_places_libres, 4)

                            # Couleur de la ligne
                            couleur_fond = self.GetCouleurLigne(nbre_places_libres)
                            if couleur_fond != None :
                                self.SetItemBackgroundColour(niveau_groupe, couleur_fond)

                            # Mémorisation ligne activité pour impression
                            self.dictImpression["contenu"].append([u"     %s" % label, dictGroupe["abrege"], texte_inscrits, texte_inscrits_max, texte_places_libres])


        self.ExpandAllChildren(self.root)

    def GetCouleurLigne(self, nbre_places_libres=None):
        if nbre_places_libres == None :
            return None
        elif nbre_places_libres <= 0 :
            return COULEUR_COMPLET
        elif nbre_places_libres > 0 and nbre_places_libres <= self.seuil_alerte :
            return COULEUR_ALERTE
        else :
            return COULEUR_DISPONIBLE

    def SetFiltre(self, filtre=""):
        self.filtre = filtre
        self.MAJ(forcerActualisation=True)

    def DevelopperTout(self):
        item = self.GetFirstChild(self.root)[0]
        for index in range(0, self.GetChildrenCount(self.root)-1) :
            self.Expand(item)
            item = self.GetNext(item)

    def ReduireTout(self):
        item = self.GetFirstChild(self.root)[0]
        for index in range(0, self.GetChildrenCount(self.root)-1) :
            self.Collapse(item)
            item = self.GetNext(item)

    def Imprimer(self, event=None):
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle

        hauteur_page = A4[1]
        largeur_page = A4[0]

        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("INSCRIPTIONS", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=30, leftMargin=40, rightMargin=40)
        story = []

        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (largeur_page-175, 100) )
        dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Inscriptions"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        story.append(Spacer(0, 10))

        # Intro
        styleA = ParagraphStyle(name="A", fontName="Helvetica", fontSize=6, spaceAfter=20)
        #story.append(Paragraph(self.labelParametres, styleA))

        # Tableau
        dataTableau = []
        largeurColonnesSuivantes = 70
        largeurColonne1 = largeur_page - 80 - 1.0 * (len(self.dictImpression["entete"])-1) * largeurColonnesSuivantes
        largeursColonnes = [largeurColonne1,]
        for x in range(0, len(self.dictImpression["entete"])-1):
            largeursColonnes.append(largeurColonnesSuivantes)

        # Entetes labels
        dataTableau.append(self.dictImpression["entete"])

        # Contenu du tableau
        listeRubriques = ("contenu", "total")
        for rubrique in listeRubriques :
            listeLignes = self.dictImpression[rubrique]

            for ligne in listeLignes :
                dataTableau.append(ligne)

        positionLigneTotal = len(self.dictImpression["contenu"]) + 1
        listeStyles = [
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
            ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police
            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
            ('ALIGN', (1,0), (-1,-1), 'CENTRE'), # Centre les cases
            ('BACKGROUND', (0,0), (-1,0), (0.6, 0.6, 0.6) ), # Donne la couleur de fond du label
            ('BACKGROUND', (0, positionLigneTotal), (-1, positionLigneTotal), (0.8, 0.8, 0.8) ), # Donne la couleur de fond du total
            ]

        # Formatage des lignes "Activités"
        for indexColoration, typeColoration in self.dictImpression["coloration"] :

            if typeColoration == "activite" :
                listeStyles.append( ('FONT', (0, indexColoration+1), (-1, indexColoration+1), "Helvetica-Bold", 7) )
                listeStyles.append( ('BACKGROUND', (0, indexColoration+1), (-1, indexColoration+1), (0.91, 0.91, 0.91)) )

            if typeColoration == "regroup" :
                listeStyles.append( ('FONT', (0, indexColoration+1), (-1, indexColoration+1), "Helvetica-Bold", 7) )
                listeStyles.append( ('TEXTCOLOR', (0, indexColoration+1), (-1, indexColoration+1), (1, 1, 1)) )
                listeStyles.append( ('BACKGROUND', (0, indexColoration+1), (-1, indexColoration+1), (0, 0, 0)) )

        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes, repeatRows=1)
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)
        story.append(Spacer(0,20))

        # Enregistrement du PDF
        doc.build(story)

        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)

    def ExportExcel(self, event=None):
        """ Export Excel """
        titre = _(u"Inscriptions")

        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportExcel_%s.xls" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        wildcard = "Fichier Excel (*.xls)|*.xls|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut,
            defaultFile = nomFichier,
            wildcard = wildcard,
            style = wx.SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Export
        import pyExcelerator
        # Création d'un classeur
        wb = pyExcelerator.Workbook()
        # Création d'une feuille
        ws1 = wb.add_sheet(titre)
        # Remplissage de la feuille

        fntLabel = pyExcelerator.Font()
        fntLabel.name = 'Verdana'
        fntLabel.bold = True

        al = pyExcelerator.Alignment()
        al.horz = pyExcelerator.Alignment.HORZ_LEFT
        al.vert = pyExcelerator.Alignment.VERT_CENTER

        ar = pyExcelerator.Alignment()
        ar.horz = pyExcelerator.Alignment.HORZ_RIGHT
        ar.vert = pyExcelerator.Alignment.VERT_CENTER

        pat = pyExcelerator.Pattern()
        pat.pattern = pyExcelerator.Pattern.SOLID_PATTERN
        pat.pattern_fore_colour = 0x01F

        styleLabel = pyExcelerator.XFStyle()
        styleLabel.alignment = al
        styleLabel.pattern = pat

        styleTotal = pyExcelerator.XFStyle()
        styleTotal.alignment = al
        styleTotal.pattern = pat
        styleTotal.font.bold = True

        styleTotalNbre = pyExcelerator.XFStyle()
        styleTotalNbre.alignment = ar
        styleTotalNbre.pattern = pat
        styleTotalNbre.font.bold = True

        styleEuros = pyExcelerator.XFStyle()
        styleEuros.num_format_str = '"$"#,##0.00_);("$"#,##'
        styleEuros.alignment = ar

        styleTotalEuros = pyExcelerator.XFStyle()
        styleTotalEuros.num_format_str = '"$"#,##0.00_);("$"#,##'
        styleTotalEuros.alignment = ar
        styleTotalEuros.pattern = pat
        styleTotalEuros.font.bold = True

        # Création des labels de colonnes
        x = 0
        y = 0
        for valeur in self.dictImpression["entete"] :
            ws1.write(x, y, valeur)
            ws1.col(y).width = 3000
            y += 1
        ws1.col(0).width = 10000

        def RechercheFormat(valeur, titre):
            """ Recherche si la valeur est un nombre """
            format = None
            # Si c'est un nombre
            try :
                nbre = float(valeur)
                if titre == True :
                    format = styleTotalNbre
                return (nbre, format)
            except :
                pass

            return False, None


        # Contenu
        x = 1
        y = 0
        for ligne in self.dictImpression["contenu"] :
            for valeur in ligne :

                # Recherche si c'est un titre
                if x-1 in self.dictImpression["coloration"] :
                    titre = True
                else:
                    titre = False

                # Recherche s'il y a un format de nombre ou de montant
                nbre, format = RechercheFormat(valeur, titre)
                if nbre != False :
                    valeur = nbre

                if nbre == False and titre == True and format == None :
                    format = styleTotal

                # Enregistre la valeur
                if format != None :
                    ws1.write(x, y, valeur, format)
                else:
                    ws1.write(x, y, valeur)

                y += 1
            x += 1
            y = 0

        # Total
        premiereLigne = True
        for ligne in self.dictImpression["total"] :
            for valeur in ligne :

                # Recherche si c'est un titre
                if premiereLigne == True :
                    titre = True
                else:
                    titre = False

                # Recherche s'il y a un format de nombre ou de montant
                nbre, format = RechercheFormat(valeur, titre)
                if nbre != False :
                    valeur = nbre

                if nbre == False and titre == True and format == None :
                    format = styleTotal

                # Enregistre la valeur
                if format != None :
                    ws1.write(x, y, valeur, format)
                else:
                    ws1.write(x, y, valeur)

                y += 1
            premiereLigne = False
            x += 1
            y = 0

        # Finalisation du fichier xls
        wb.save(cheminFichier)

        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)




# ----------------------------------------------------------------------------------------------------------------------        

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Messages
        self.ctrl_inscriptions = CTRL(self)
        
        # Commandes
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste"))
        self.bouton_export = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_export.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Excel"))
        self.bouton_parametres = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_parametres.SetToolTipString(_(u"Cliquez ici pour modifier les paramètres d'affichage"))
        self.bouton_outils = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Outils.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_outils.SetToolTipString(_(u"Cliquez ici pour accéder aux outils"))
        self.bouton_tarifs = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Euro.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_tarifs.SetToolTipString(_(u"Cliquez ici pour consulter les tarifs de l'activité sélectionnée (ou double-cliquez sur une activité dans la liste)"))

        # Barre de recherche
        self.ctrl_recherche = BarreRecherche(self, ctrl=self.ctrl_inscriptions)

        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_inscriptions.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_inscriptions.ExportExcel, self.bouton_export)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonParametres, self.bouton_parametres)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTarifs, self.bouton_tarifs)

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer.Add(self.ctrl_inscriptions, 1, wx.EXPAND|wx.TOP|wx.LEFT, 10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_export, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_parametres, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_tarifs, 0, 0, 0)
        grid_sizer.Add(grid_sizer_boutons, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 10)
        grid_sizer.Add(self.ctrl_recherche, 1, wx.EXPAND|wx.LEFT|wx.BOTTOM, 10)
        grid_sizer.AddGrowableRow(0)
        grid_sizer.AddGrowableCol(0)
        self.SetSizer(grid_sizer)
        self.Layout()
    
    def MAJ(self):
        self.ctrl_inscriptions.MAJ()

    def OnBoutonParametres(self, event):
        import DLG_Parametres_nbre_inscrits
        dlg = DLG_Parametres_nbre_inscrits.Dialog(self)
        reponse = dlg.ShowModal()
        if reponse == wx.ID_OK :
            self.ctrl_inscriptions.MAJ(forcerActualisation=True) 
        
    def OnBoutonOutils(self, event):
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Actualiser
        item = wx.MenuItem(menuPop, 10, _(u"Actualiser"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser2.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Actualiser, id=10)

        menuPop.AppendSeparator()
        
        item = wx.MenuItem(menuPop, 20, _(u"Aide"), _(u"Aide"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Aide, id=20)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OnBoutonTarifs(self, event=None):
        self.ctrl_inscriptions.OuvrirTarifs()

    def Actualiser(self, event):
        self.ctrl_inscriptions.MAJ(forcerActualisation=True) 
    
    def Aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, ctrl=None):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.ctrl = ctrl
        self.rechercheEnCours = False

        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)

        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

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

    def OnSearch(self, evt):
        self.Recherche()

    def OnCancel(self, evt):
        self.SetValue("")

    def OnDoSearch(self, evt):
        self.Recherche()

    def Recherche(self):
        filtre = self.GetValue()
        self.ShowCancelButton(len(filtre))
        self.ctrl.SetFiltre(filtre)
        self.Refresh()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        t1 = time.time()
        self.ctrl.MAJ()
        print "Temps MAJ =", time.time() - t1
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()