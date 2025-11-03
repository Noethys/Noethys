#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import os
import wx.lib.agw.hypertreelist as HTL
import datetime
import sys
import FonctionsPerso
from Utils import UTILS_Dates
from Utils import UTILS_Organisateur
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
import GestionDB



            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, IDdepot=None):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.IDdepot = IDdepot

        self.dictImpression = {}
        self.afficher_detail = True
        
        # Importation
        self.dictActivites = self.ImportationActivites()

        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_ROW_LINES | TR_COLUMN_LINES | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER

    def SetIDdepot(self, IDdepot=None):
        self.IDdepot = IDdepot
        self.MAJ()

    def ImportationActivites(self):
        """ Importation des noms d'activités """
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege
        FROM activites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictActivites = {}
        for IDactivite, nom, abrege in listeDonnees :
            dictActivites[IDactivite] = {"nom":nom, "abrege":abrege}
        return dictActivites

    def Importation(self):
        """ Importation des données """
        if self.IDdepot == None:
            return {}

        DB = GestionDB.DB()

        req = """SELECT SUM(montant)
        FROM reglements
        WHERE IDdepot=%d;""" % self.IDdepot
        DB.ExecuterReq(req)
        liste_donnees = DB.ResultatReq()
        montant_depot = liste_donnees[0][0]
        if not montant_depot:
            montant_depot = 0.0

        req = """SELECT 
        ventilation.IDventilation, ventilation.IDprestation, ventilation.montant,
        prestations.label, prestations.IDactivite, prestations.categorie
        FROM ventilation
        LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        WHERE reglements.IDdepot=%d
        ORDER BY ventilation.IDprestation; """ % self.IDdepot
        DB.ExecuterReq(req)
        liste_prestations = DB.ResultatReq()
        DB.Close()
        dict_prestations = {}

        total = 0.0
        for IDventilation, IDprestation, montant, label, IDactivite, categorie in liste_prestations:
            if not montant:
                montant = 0.0

            if categorie == "cotisation":
                IDactivite = 90001
            if categorie == "location":
                IDactivite = 90002

            # Mémorisation par prestation
            if IDactivite not in dict_prestations:
                dict_prestations[IDactivite] = {"prestations" : {}, "quantite": 0, "total": 0.0}
            if label not in dict_prestations[IDactivite]["prestations"]:
                dict_prestations[IDactivite]["prestations"][label] = {"detail": {}, "quantite": 0, "total": 0.0}
            if montant not in dict_prestations[IDactivite]["prestations"][label]["detail"]:
                dict_prestations[IDactivite]["prestations"][label]["detail"][montant] = {"quantite": 0, "total": 0.0}
            dict_prestations[IDactivite]["prestations"][label]["detail"][montant]["quantite"] += 1
            dict_prestations[IDactivite]["prestations"][label]["detail"][montant]["total"] += montant

            # Total par activité
            dict_prestations[IDactivite]["quantite"] += 1
            dict_prestations[IDactivite]["total"] += montant

            # Total par label de prestation
            dict_prestations[IDactivite]["prestations"][label]["quantite"] += 1
            dict_prestations[IDactivite]["prestations"][label]["total"] += montant

            total += montant

        # Recherche des avoirs
        if montant_depot > total:
            montant_avoirs = montant_depot - total
            dict_prestations[80000] = {"prestations": {}, "quantite": 0, "total": montant_avoirs}

        return dict_prestations

    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot()

    def MAJ(self):
        # Importation des données
        dictResultats = self.Importation()

        # Init impression
        self.dictImpression = {"entete": [], "contenu": [], "total": [], "coloration": []}

        # Initialisation du CTRL
        self.RAZ() 

        # Création des colonnes
        liste_colonnes = [
            {"code": u"prestations", "label": _(u"Activité/Prestation"), "largeur": 280, "alignement": wx.ALIGN_LEFT},
            {"code": u"tarif_unitaire", "label": _(u"Tarif unitaire"), "largeur": 100, "alignement": wx.ALIGN_CENTRE},
            {"code": u"quantite", "label": _(u"Quantité"), "largeur": 90, "alignement": wx.ALIGN_CENTRE},
            {"code": u"total", "label": _(u"Total"), "largeur": 100, "alignement": wx.ALIGN_CENTRE},
        ]
        numColonne = 0
        for dict_colonne in liste_colonnes:
            self.AddColumn(dict_colonne["label"])
            self.SetColumnWidth(numColonne, dict_colonne["largeur"])
            self.SetColumnAlignment(numColonne, dict_colonne["alignement"])
            if self.afficher_detail or dict_colonne["code"] != "tarif_unitaire" :
                self.dictImpression["entete"].append(dict_colonne["label"])
            numColonne += 1

        # On cache la colonne Tarif unitaire si souhaité
        if self.afficher_detail == False:
            self.SetColumnWidth(1, 0)

        # Racine
        self.root = self.AddRoot(_(u"Racine"))

        # Branches Activités
        listeLabels = []
        for IDactivite, dictActivite in dictResultats.items():
            if IDactivite in self.dictActivites :
                nomActivite = self.dictActivites[IDactivite]["nom"]
            elif IDactivite == 90001 :
                nomActivite = _(u"Cotisations")
            elif IDactivite == 90002 :
                nomActivite = _(u"Locations")
            elif IDactivite == 80000:
                nomActivite = _(u"Avoirs")
            else :
                nomActivite = _(u"Activité inconnue")
            listeLabels.append((nomActivite, IDactivite, dictActivite))
        listeLabels.sort()

        quantite = 0
        total = 0.0

        # Niveau activité
        for nomActivite, IDactivite, dictActivite in listeLabels :
            niveauActivite = self.AppendItem(self.root, nomActivite)
            self.SetItemText(niveauActivite, str(dictActivite["quantite"]), 2)
            self.SetItemText(niveauActivite, u"%.2f %s" % (dictActivite["total"], SYMBOLE), 3)

            # Mémorise total général
            quantite += dictActivite["quantite"]
            total += dictActivite["total"]

            quantite_activite = dictActivite["quantite"]
            if quantite_activite == 0 :
                quantite_activite = ""

            impression_ligne = [nomActivite, str(quantite_activite), u"%.2f %s" % (dictActivite["total"], SYMBOLE)]
            if self.afficher_detail:
                impression_ligne.insert(1, "")
            self.dictImpression["contenu"].append(impression_ligne)

            self.dictImpression["coloration"].append(len(self.dictImpression["contenu"]) - 1)

            # Niveau prestation
            liste_labels = list(dictActivite["prestations"])
            liste_labels.sort()

            for label in liste_labels:
                dict_label = dictActivite["prestations"][label]

                # Afficher le détail des montants
                if self.afficher_detail == True:

                    liste_montants = list(dict_label["detail"])
                    liste_montants.sort()
                    for montant in liste_montants :
                        dict_montant = dict_label["detail"][montant]

                        niveauPrestation = self.AppendItem(niveauActivite, label or "?")
                        self.SetItemText(niveauPrestation, u"%.2f %s" % (montant or 0.0, SYMBOLE), 1)
                        self.SetItemText(niveauPrestation, str(dict_montant["quantite"]), 2)
                        self.SetItemText(niveauPrestation, u"%.2f %s" % (dict_montant["total"] or 0.0, SYMBOLE), 3)
                        self.SetItemFont(niveauPrestation, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                        self.SetItemTextColour(niveauPrestation, wx.Colour(160, 160, 160))

                        impression_ligne = [label, str(dict_montant["quantite"]), u"%.2f %s" % (dict_montant["total"], SYMBOLE)]
                        if self.afficher_detail:
                            impression_ligne.insert(1, u"%.2f %s" % (montant or 0.0, SYMBOLE))
                        self.dictImpression["contenu"].append(impression_ligne)

                else:

                    niveauPrestation = self.AppendItem(niveauActivite, label)
                    self.SetItemText(niveauPrestation, str(dict_label["quantite"]), 2)
                    self.SetItemText(niveauPrestation, u"%.2f %s" % (dict_label["total"], SYMBOLE), 3)
                    self.SetItemFont(niveauPrestation, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                    self.SetItemTextColour(niveauPrestation, wx.Colour(160, 160, 160))

                    impression_ligne = [label, str(dict_label["quantite"]), u"%.2f %s" % (dict_label["total"], SYMBOLE)]
                    if self.afficher_detail:
                        impression_ligne.insert(1, "")
                    self.dictImpression["contenu"].append(impression_ligne)

        # Ligne total général
        niveauTotal = self.AppendItem(self.root, _(u"Total"))
        self.SetItemBackgroundColour(niveauTotal, wx.Colour(150, 150, 150) )
        self.SetItemTextColour(niveauTotal, wx.Colour(255, 255, 255) )
        self.SetItemText(niveauTotal, str(quantite), 2)
        self.SetItemText(niveauTotal, u"%.2f %s" % (total, SYMBOLE), 3)

        impression_ligne = [_(u"Total"), str(quantite), u"%.2f %s" % (total, SYMBOLE)]
        if self.afficher_detail:
            impression_ligne.insert(1, "")
        self.dictImpression["total"].append(impression_ligne)

        self.ExpandAllChildren(self.root)

    def SetAffichageDetails(self, etat=True):
        self.affichage_details = etat

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

    def GetLabelParametres(self):
        return _(u"Dépôt : %s") % self.GetParent().ctrl_infos.GetLabel()

    def Imprimer(self):
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        
        hauteur_page = A4[1]
        largeur_page = A4[0]
            
        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("depot_prestations", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur_page, hauteur_page), topMargin=30, bottomMargin=30, leftMargin=40, rightMargin=40)
        story = []
        
        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (largeur_page-175, 100) )
        dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Détail des prestations d'un dépôt"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        story.append(Paragraph(self.GetLabelParametres(), styleA))
        
        # Tableau
        dataTableau = []
        largeursColonnes = []
        for x in range(0, len(self.dictImpression["entete"])-1):
            largeursColonnes.append(45*2)
        largeursColonnes.insert(0, largeur_page - 75 - sum(largeursColonnes))
        
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
            ('ALIGN', (0,0), (-1,-1), 'CENTRE'), # Centre les cases
                    
            ('BACKGROUND', (0,0), (-1,0), (0.6, 0.6, 0.6) ), # Donne la couleur de fond du label
            ('BACKGROUND', (0, positionLigneTotal), (-1, positionLigneTotal), (0.6, 0.6, 0.6) ), # Donne la couleur de fond du label
            ]
            
        # Formatage des lignes "Activités"
        for indexColoration in self.dictImpression["coloration"] :
            listeStyles.append( ('FONT', (0, indexColoration+1), (-1, indexColoration+1), "Helvetica-Bold", 7) )
            listeStyles.append( ('BACKGROUND', (0, indexColoration+1), (-1, indexColoration+1), (0.8, 0.8, 0.8)) ) 
                
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)
        story.append(Spacer(0,20))
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
    
    def ExportExcel(self):
        """ Export Excel """
        titre = _(u"Détail des prestations d'un dépôt")
        
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
            if valeur.endswith(SYMBOLE) :
                # Si c'est un montant en euros
                try :
                    nbre = float(valeur[:-1]) 
                    if titre == True :
                        format = format_money_titre
                    else:
                        format = format_money
                    return (nbre, format)
                except :
                    pass
                    
            else:
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

        # Ajout du nom du dépôt
        feuille.write(x + 1, 0, self.GetLabelParametres())

        # Finalisation du fichier xls
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


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.ctrl_stats = CTRL(panel, IDdepot=1)
        self.ctrl_stats.MAJ()
        
        self.bouton_imprimer = wx.BitmapButton(panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_stats, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_imprimer, 0, wx.ALL, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonImprimer(self, event):
        self.ctrl_stats.Imprimer()
        #self.ctrl_stats.ExportExcel()
        

if __name__ == '__main__':    
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
