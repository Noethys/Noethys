#!/usr/bin/env python
# -*- coding: utf8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
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


COULEUR_DISPONIBLE = (227, 254, 219)
COULEUR_ALERTE = (254, 252, 219)
COULEUR_COMPLET = (247, 172, 178)
COULEUR_GAUGE_FOND = (255, 255, 255)



class CTRL(HTL.HyperTreeList):
    def __init__(self, parent):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.dictEvenements = {}
        self.filtre = None
        self.listeActivites = []
        self.listePeriodes = []
        self.dictImpression = { "entete" : [], "contenu" : [], "total" : [], "coloration" : [] }
        
        self.couleurFond = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        self.SetBackgroundColour(self.couleurFond)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_ROW_LINES | wx.TR_HAS_BUTTONS | TR_COLUMN_LINES | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT )

        # Génération des colonnes
        self.CreationColonnes()

        # Racine
        self.root = self.AddRoot(_(u"Racine"))

    def CreationColonnes(self):
        """ Création des colonnes """
        liste_colonnes = [
            (_(u"Activité / Date / Evènement"), 300, wx.ALIGN_LEFT),
            (_(u"Inscrits"), 80, wx.ALIGN_CENTER),
            (_(u"Places max"), 90, wx.ALIGN_CENTER),
            (_(u"Places libres"), 90, wx.ALIGN_CENTER),
            (_(u"Places attente"), 90, wx.ALIGN_CENTER),
        ]
        index = 0
        for label, largeur, alignement in liste_colonnes :
            self.AddColumn(label)
            self.SetColumnWidth(index, largeur)
            self.SetColumnAlignment(index, alignement)
            self.dictImpression["entete"].append(label)
            index += 1

    def GetSQLdates(self, listePeriodes=[]):
        """ Avec date """
        texteSQL = ""
        for date_debut, date_fin in listePeriodes :
            texteSQL += "(date>='%s' AND date<='%s') OR " % (date_debut, date_fin)
        if len(texteSQL) > 0 :
            texteSQL = "(" + texteSQL[:-4] + ")"
        else:
            texteSQL = "date='3000-01-01'"
        return texteSQL


    def MAJ(self, forcerActualisation=False):
        # Conditions
        conditions = self.GetSQLdates(self.listePeriodes)
        if len(conditions) > 0 :
            conditionDates = " AND %s" % conditions
        else:
            conditionDates = ""

        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))

        # Recherche des évènements
        DB = GestionDB.DB()
        req = """SELECT IDevenement, evenements.IDactivite, evenements.nom, date, heure_debut, heure_fin, capacite_max,
        activites.nom
        FROM evenements
        LEFT JOIN activites ON activites.IDactivite = evenements.IDactivite
        WHERE evenements.IDactivite IN %s %s
        ORDER BY date, heure_debut;""" % (conditionActivites, conditionDates)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictEvenements = {}
        dictDonnees = {}
        for IDevenement, IDactivite, nom, date, heure_debut, heure_fin, capacite_max, nomActivite in listeDonnees :
            if nomActivite == None :
                nomActivite = _(u"Activité inconnue")
            date = UTILS_Dates.DateEngEnDateDD(date)
            dictEvenement = {"nom" : nom, "IDactivite" : IDactivite, "date" : date, "heure_debut" : heure_debut, "heure_fin" : heure_fin, "nomActivite" : nomActivite, "nbre_max" : capacite_max, "nbre_inscrits" : 0, "nbre_attente" : 0}
            dictEvenements[IDevenement] = dictEvenement

            # Filtre
            infos = " ".join([nom, UTILS_Dates.DateEngFr(str(date))])
            if self.filtre == None or (self.filtre.lower() in infos.lower()):

                # Mémorisation de l'évènement
                key = (nomActivite, IDactivite)
                if (key in dictDonnees) == False :
                    dictDonnees[key] = {}
                if (date in dictDonnees[key]) == False :
                    dictDonnees[key][date] = []
                dictDonnees[key][date].append(IDevenement)

        req = """SELECT IDconso, IDevenement, etat
        FROM consommations
        WHERE IDevenement IS NOT NULL AND consommations.etat in ('reservation', 'present', 'attente')
        AND consommations.IDactivite IN %s %s
        ;""" % (conditionActivites, conditionDates)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDconso, IDevenement, etat in listeDonnees :
            if IDevenement in dictEvenements :
                if etat in ("reservation", "present") :
                    dictEvenements[IDevenement]["nbre_inscrits"] += 1
                if etat == "attente" :
                    dictEvenements[IDevenement]["nbre_attente"] += 1

        DB.Close()

        # Vérifie si actualisation nécessaire
        if self.dictEvenements != dictEvenements or forcerActualisation == True :
            self.dictEvenements = dictEvenements
        else :
            return

        # MAJ du contrôle
        self.DeleteChildren(self.root)

        # Préparation pour impression
        self.dictImpression["contenu"] = []
        self.dictImpression["coloration"] = []

        # Tri par activités
        listeActivites = list(dictDonnees.keys())
        listeActivites.sort()

        # Niveau Activité
        for key in listeActivites :
            nomActivite, IDactivite = key
            label = nomActivite.upper()
            niveau_activite = self.AppendItem(self.root, label)
            self.SetItemBackgroundColour(niveau_activite, wx.Colour(221, 221, 221))
            self.dictImpression["contenu"].append([label, ])
            self.dictImpression["coloration"].append((len(self.dictImpression["contenu"]) - 1, "regroup"))

            # Dates
            listeDates = list(dictDonnees[key].keys())
            listeDates.sort()

            for date in listeDates :
                label = UTILS_Dates.DateComplete(date)
                niveau_date = self.AppendItem(niveau_activite, label)
                font = self.GetFont()
                font.SetWeight(wx.BOLD)
                self.SetItemFont(niveau_date, font)

                # Mémorisation ligne pour impression
                self.dictImpression["contenu"].append([label,])

                # Evènements
                for IDevenement in dictDonnees[key][date] :
                    dictEvenement = dictEvenements[IDevenement]
                    label = dictEvenement["nom"]
                    niveau_evenement = self.AppendItem(niveau_date, label)

                    nbre_inscrits = dictEvenement["nbre_inscrits"]
                    if nbre_inscrits == None :
                        nbre_inscrits = 0
                    texte_inscrits = str(nbre_inscrits)
                    self.SetItemText(niveau_evenement, texte_inscrits, 1)

                    nbre_max = dictEvenement["nbre_max"]
                    if nbre_max == None :
                        texte_inscrits_max = ""
                    else :
                        texte_inscrits_max = str(nbre_max)
                    self.SetItemText(niveau_evenement, texte_inscrits_max, 2)

                    if nbre_max != None :
                        nbre_places_libres = nbre_max - nbre_inscrits
                        texte_places_libres = str(nbre_places_libres)
                    else :
                        nbre_places_libres = None
                        texte_places_libres = ""
                    self.SetItemText(niveau_evenement, texte_places_libres, 3)

                    nbre_attente = dictEvenement["nbre_attente"]
                    if nbre_attente in (0, None) :
                        texte_attente = ""
                    else :
                        texte_attente = str(nbre_attente)
                    self.SetItemText(niveau_evenement, texte_attente, 4)

                    # Couleur de la ligne
                    couleur_fond = self.GetCouleurLigne(nbre_places_libres)
                    if couleur_fond != None :
                        self.SetItemBackgroundColour(niveau_evenement, couleur_fond)

                    # Mémorisation ligne activité pour impression
                    self.dictImpression["contenu"].append([u"     %s" % label, texte_inscrits, texte_inscrits_max, texte_places_libres])


        self.ExpandAllChildren(self.root)

    def GetCouleurLigne(self, nbre_places_libres=None):
        if nbre_places_libres == None :
            return wx.Colour(*COULEUR_DISPONIBLE)
        elif nbre_places_libres <= 0 :
            return wx.Colour(*COULEUR_COMPLET)
        # elif nbre_places_libres > 0 and nbre_places_libres <= self.seuil_alerte :
        #     return wx.Colour(*COULEUR_ALERTE)
        else :
            return wx.Colour(*COULEUR_DISPONIBLE)

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
        nomDoc = FonctionsPerso.GenerationNomDoc("EVENEMENTS", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=30, leftMargin=40, rightMargin=40)
        story = []

        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (largeur_page-175, 100) )
        dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Evènements"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        titre = _(u"Evènements")

        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportExcel_%s.xlsx" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        wildcard = "Fichier Excel (*.xlsx)|*.xlsx|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut,
            defaultFile = nomFichier,
            wildcard = wildcard,
            style = wx.FD_SAVE
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
        import xlsxwriter
        classeur = xlsxwriter.Workbook(cheminFichier)
        feuille = classeur.add_worksheet()

        format_money = classeur.add_format({'num_format': '# ##0.00'})
        format_money_titre = classeur.add_format({'num_format': '# ##0.00', 'bold': True, 'bg_color': '#E7EAED'})
        format_titre = classeur.add_format({'align': 'center', 'bold': True, 'bg_color': '#E7EAED'})

        # Création des labels de colonnes
        x = 0
        y = 0
        for valeur in self.dictImpression["entete"] :
            feuille.write(x, y, valeur)
            feuille.set_column(y, y, 15)
            y += 1
        feuille.set_column(0, 0, 50)

        def RechercheFormat(valeur, titre):
            """ Recherche si la valeur est un nombre """
            format = None
            # Si c'est un nombre
            try :
                nbre = float(valeur)
                if titre == True :
                    format = format_titre
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
                    format = format_titre

                # Enregistre la valeur
                if format != None :
                    feuille.write(x, y, valeur, format)
                else:
                    feuille.write(x, y, valeur)

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
                    format = format_titre

                # Enregistre la valeur
                if format != None :
                    feuille.write(x, y, valeur, format)
                else:
                    feuille.write(x, y, valeur)

                y += 1
            premiereLigne = False
            x += 1
            y = 0

        # Finalisation du fichier xlsx
        classeur.close()

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
        self.ctrl_evenements = CTRL(self)
        
        # Commandes
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_export = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_export.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_parametres = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_parametres.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier les paramètres d'affichage")))
        self.bouton_outils = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Outils.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux outils")))

        # Barre de recherche
        self.ctrl_recherche = BarreRecherche(self, ctrl=self.ctrl_evenements)

        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_evenements.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_evenements.ExportExcel, self.bouton_export)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonParametres, self.bouton_parametres)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer.Add(self.ctrl_evenements, 1, wx.EXPAND|wx.TOP|wx.LEFT, 10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_export, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_parametres, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer.Add(grid_sizer_boutons, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 10)
        grid_sizer.Add(self.ctrl_recherche, 1, wx.EXPAND|wx.LEFT|wx.BOTTOM, 10)
        grid_sizer.AddGrowableRow(0)
        grid_sizer.AddGrowableCol(0)
        self.SetSizer(grid_sizer)
        self.Layout()
    
    def MAJ(self):
        dictDonnees = self.GetParent().ctrl_remplissage.dictDonnees
        self.SetDictDonnees(dictDonnees)
        self.ctrl_evenements.MAJ()

    def OnBoutonParametres(self, event):
        from Dlg import DLG_Parametres_remplissage
        dictDonnees = self.GetParent().ctrl_remplissage.dictDonnees
        dlg = DLG_Parametres_remplissage.Dialog(None, dictDonnees, afficheAbregeGroupes=False, afficheLargeurColonneUnite=False, afficheTotaux=False)
        if dlg.ShowModal() == wx.ID_OK:
            newDictDonnees = dlg.GetDictDonnees()
            # Envoi les données au ctrl remplissage
            for key, valeur in newDictDonnees.items() :
                dictDonnees[key] = valeur
            self.GetParent().ctrl_remplissage.SetDictDonnees(dictDonnees)
            # MAJ
            self.MAJ()
        dlg.Destroy()

    def SetDictDonnees(self, dictDonnees={}):
        self.ctrl_evenements.listeActivites = dictDonnees["listeActivites"]
        self.ctrl_evenements.listePeriodes = dictDonnees["listePeriodes"]
        self.ctrl_evenements.MAJ()

    def OnBoutonOutils(self, event):
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

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

    def Actualiser(self, event):
        self.ctrl_evenements.MAJ(forcerActualisation=True)
    
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
        print("Temps MAJ =", time.time() - t1)
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