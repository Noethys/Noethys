#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
"""
IMPORTANT :
J'ai rajoute la ligne 101 de gridlabelrenderer.py dans wxPython mixins :
if rows == [-1] : return
"""

import wx
import wx.grid as gridlib
import wx.lib.wordwrap as wordwrap
import wx.lib.mixins.gridlabelrenderer as glr
import datetime
import FonctionsPerso
import sys
import traceback
import six
import GestionDB
from Utils import UTILS_Organisateur
from Utils import UTILS_Infos_individus
from Utils import UTILS_Dates

LISTE_MOIS = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + LISTE_MOIS[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def FormateMois(donnee):
    if donnee in ("", None):
        return ""
    else:
        annee, mois = donnee
        return u"%s %d" % (LISTE_MOIS[mois-1].capitalize(), annee)
    
def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def HeureStrEnTime(heureStr):
    if heureStr == None or heureStr == "" : return datetime.time(0, 0)
    heures, minutes = heureStr.split(":")
    return datetime.time(int(heures), int(minutes))
    

def FormateValeur(valeur, mode="quantite"):
    if mode == "quantite" :
        return str(valeur)
    if "temps" in mode :
        heures = (valeur.days*24) + (valeur.seconds/3600)
        minutes = valeur.seconds%3600/60
        return "%dh%02d" % (heures, minutes)



def DrawBorder(grid, dc, rect):
    top = rect.top
    bottom = rect.bottom
    left = rect.left
    right = rect.right
    dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
    dc.DrawLine(right, top, right, bottom)
    dc.DrawLine(left, top, left, bottom)
    dc.DrawLine(left, bottom, right, bottom)
    dc.SetPen(wx.WHITE_PEN)
    dc.DrawLine(left + 1, top, left + 1, bottom)
    dc.DrawLine(left + 1, top, right, top)


class LabelColonneRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor=None):
        self._bgcolor = bgcolor

    def Draw(self, grid, dc, rect, col):
        if self._bgcolor != None:
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else:
                dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        texte = grid.GetColLabelValue(col)
        texte = wordwrap.wordwrap(texte, rect.width, dc)
        DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, texte, hAlign, vAlign)




class CTRL(gridlib.Grid, glr.GridWithLabelRenderersMixin): 
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.moveTo = None
        self.GetGridWindow().SetToolTip(wx.ToolTip(""))
        self.CreateGrid(0, 0)
        self.SetRowLabelSize(200)
        self.SetColLabelSize(50)

        # Paramètres par défaut
        self.date_debut = None
        self.date_fin = None
        self.affichage_regroupement = "jour"
        self.affichage_donnees = "quantite"
        self.labelParametres = ""
                

    def MAJ(self, date_debut=None, date_fin=None, listeCategories=[], affichage_donnees="quantite",
                        affichage_regroupement="jour", labelParametres=u""):

        # Chargement des informations individuelles
        if self.date_debut != date_debut :
            self.infosIndividus = UTILS_Infos_individus.Informations(date_reference=date_debut, qf=True, inscriptions=False, messages=False, infosMedicales=False, cotisationsManquantes=False, piecesManquantes=False, questionnaires=True, scolarite=False)
            self.dictInfosFamilles = self.infosIndividus.GetDictValeurs(mode="famille", ID=None, formatChamp=False)

        # Mémorisation des paramètres
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.listeCategories = listeCategories
        self.affichage_donnees = affichage_donnees
        self.affichage_regroupement = affichage_regroupement
        self.labelParametres = labelParametres
        
        # init grid
        try :
            dlgAttente = wx.BusyInfo(_(u"Veuillez patienter durant la recherche des données..."), None)
            if 'phoenix' not in wx.PlatformInfo:
                wx.Yield()
            self.InitGrid() 
            del dlgAttente
        except Exception as err:
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la recherche des données de la synthèse des locations : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def Importation(self):
        DB = GestionDB.DB()

        if len(self.listeCategories) == 0: conditionCategories = "()"
        elif len(self.listeCategories) == 1: conditionCategories = "(%d)" % self.listeCategories[0]
        else: conditionCategories = str(tuple(self.listeCategories))

        # Consommations
        req = """SELECT IDlocation, IDfamille, date_debut, date_fin, locations.IDproduit, produits.nom, produits.IDcategorie, produits_categories.nom
        FROM locations
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE date_debut>='%s' AND date_debut<='%s'
        AND produits.IDcategorie IN %s
        ;""" % (self.date_debut, self.date_fin, conditionCategories)
        DB.ExecuterReq(req)
        listeLocations = DB.ResultatReq()
        DB.Close() 
        
        # Calcul des données
        dictResultats = {}
        listeProduits = []
        for IDlocation, IDfamille, date_debut, date_fin, IDproduit, nom_produit, IDcategorie, nom_categorie in listeLocations :
            date_debut = UTILS_Dates.DateEngEnDateDDT(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDDT(date_fin)
            mois = date_debut.month
            annee = date_debut.year
            
            # Recherche du regroupement
            try :
                if self.affichage_regroupement == "jour" : regroupement = date_debut.date()
                if self.affichage_regroupement == "mois" : regroupement = (annee, mois)
                if self.affichage_regroupement == "annee" : regroupement = annee
                if self.affichage_regroupement == "categorie" : regroupement = nom_categorie
                if self.affichage_regroupement == "ville_residence" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_VILLE"]
                if self.affichage_regroupement == "secteur" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_SECTEUR"]
                if self.affichage_regroupement == "famille" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM"]
                if self.affichage_regroupement == "regime" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM_REGIME"]
                if self.affichage_regroupement == "caisse" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM_CAISSE"]

                # QF
                if self.affichage_regroupement == "qf" :
                    regroupement = None
                    qf = self.dictInfosFamilles[IDfamille]["FAMILLE_QF_ACTUEL_INT"]
                    for x in range(0, 10000, 100) :
                        min, max = x, x+99
                        if qf >= min and qf <= max :
                            regroupement = (min, max)

                # Questionnaires
                if self.affichage_regroupement.startswith("question_") and "famille" in self.affichage_regroupement:
                    regroupement = self.dictInfosFamilles[IDfamille]["QUESTION_%s" % self.affichage_regroupement[17:]]

            except :
                regroupement = None

            if regroupement in ("", None):
                regroupement = _(u"- Non renseigné -")

            if self.affichage_donnees == "quantite":
                valeur = 1
                defaut = 0
            else:
                defaut = datetime.timedelta(hours=0, minutes=0)
                valeur = datetime.timedelta(hours=0, minutes=0)
                if date_fin:
                    valeur = date_fin - date_debut
                else:
                    if date_debut < datetime.datetime.now():
                        valeur = datetime.datetime.now() - date_debut

            # En cas de regroupements multiples :
            if type(regroupement) == list:
                listeRegroupements = regroupement
            else :
                listeRegroupements = [regroupement,]
            
            for regroupement in listeRegroupements :
                if (IDproduit in dictResultats) == False :
                    dictResultats[IDproduit] = {}
                if (regroupement in dictResultats[IDproduit]) == False :
                    dictResultats[IDproduit][regroupement] = defaut
                dictResultats[IDproduit][regroupement] += valeur

            if (nom_produit, IDproduit) not in listeProduits:
                listeProduits.append((nom_produit, IDproduit))

        listeProduits.sort()

        return dictResultats, listeProduits
    
    def ResetGrid(self):
        # Reset grille
        if self.GetNumberRows() > 0 : 
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0 : 
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()
        
    def InitGrid(self):
        self.ResetGrid() 
        
        # Récupération des données
        dictResultats, listeProduits = self.Importation()
        
        if self.affichage_donnees == "quantite":
            defaut = 0
        else :
            defaut = datetime.timedelta(hours=0, minutes=0)

        listeProduitsUtilises = []
        listeRegroupement = []
        dictTotaux = { "lignes" : {}, "colonnes" : {} }
        for IDproduit, dictProduit in dictResultats.items():
            if IDproduit not in listeProduitsUtilises:
                listeProduitsUtilises.append(IDproduit)
            for regroupement, valeur in dictProduit.items():
                if regroupement not in listeRegroupement:
                    listeRegroupement.append(regroupement)

                # Calcul des totaux
                if (IDproduit in dictTotaux["lignes"]) == False :
                    dictTotaux["lignes"][IDproduit] = defaut
                dictTotaux["lignes"][IDproduit] += valeur
                if (regroupement in dictTotaux["colonnes"]) == False :
                    dictTotaux["colonnes"][regroupement] = defaut
                dictTotaux["colonnes"][regroupement] += valeur
        
        # Création des colonnes
        largeur_colonne = 90
        dictColonnes = {}
        self.AppendCols(len(listeProduits))
        index = 0
        for nom_produit, IDproduit in listeProduits:
            self.SetColSize(index, largeur_colonne)
            renderer = LabelColonneRenderer()
            self.SetColLabelRenderer(index, renderer)
            self.SetColLabelValue(index, nom_produit)
            dictColonnes[IDproduit] = index
            index += 1
        
        # Colonne Total
        self.AppendCols(1)
        self.SetColSize(index, largeur_colonne)
        self.SetColLabelValue(index, _(u"TOTAL"))
        dictColonnes["total"] = index

        # Création des lignes
        listeRegroupement.sort()
        self.AppendRows(len(listeRegroupement))
        
        index = 0
        dictLignes = {}
        for regroupement in listeRegroupement:
            if self.affichage_regroupement == "jour":
                label = DateComplete(regroupement)
            elif self.affichage_regroupement == "mois":
                label = FormateMois(regroupement)
            elif self.affichage_regroupement == "annee":
                label = str(regroupement)
            elif self.affichage_regroupement == "qf" and type(regroupement) == tuple:
                label = u"%d-%d" % regroupement
            else :
                label = six.text_type(regroupement)
            
            self.SetRowLabelValue(index, label)
            self.SetRowSize(index, 30)
            dictLignes[regroupement] = index
            index += 1
        
        # Ligne Total
        self.AppendRows(1)
        self.SetRowLabelValue(index, _(u"TOTAL"))
        self.SetRowSize(index, 30)
        dictLignes["total"] = index
        
        # Remplissage des valeurs
        for IDproduit, dictProduit in dictResultats.items():
            for regroupement, valeur in dictProduit.items():
                label = FormateValeur(valeur, self.affichage_donnees)
                numLigne = dictLignes[regroupement]
                numColonne = dictColonnes[IDproduit]
                self.SetCellValue(numLigne, numColonne, label)
                self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetReadOnly(numLigne, numColonne, True)
        
        # Remplissage des totaux        
        for IDproduit, valeur in dictTotaux["lignes"].items() :
            label = FormateValeur(valeur, self.affichage_donnees)
            numLigne = dictLignes["total"]
            numColonne = dictColonnes[IDproduit]
            self.SetCellValue(numLigne, numColonne, label)
            self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetReadOnly(numLigne, numColonne, True)
        
        total_general = defaut
        for regroupement, valeur in dictTotaux["colonnes"].items() :
            total_general += valeur
            label = FormateValeur(valeur, self.affichage_donnees)
            numLigne = dictLignes[regroupement]
            numColonne = dictColonnes["total"]
            self.SetCellValue(numLigne, numColonne, label)
            self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetReadOnly(numLigne, numColonne, True)
        
        # Total général
        label = FormateValeur(total_general, self.affichage_donnees)
        numLigne = dictLignes["total"]
        numColonne = dictColonnes["total"]
        self.SetCellValue(numLigne, numColonne, label)
        self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.SetReadOnly(numLigne, numColonne, True)
        
        # Coloration des TOTAUX
        couleurFond = (240, 240, 240)
        for x in range(0, numLigne+1):
            self.SetCellBackgroundColour(x, numColonne, couleurFond)
        for y in range(0, numColonne):
            self.SetCellBackgroundColour(numLigne, y, couleurFond)
                
    def Apercu(self):
        """ Impression tableau de données """
        if self.GetNumberRows() == 0 or self.GetNumberCols() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a rien à imprimer !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return None

        avecCouleurs = True
        
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        def ConvertCouleur(couleur):
            r, g, b = couleur[0], couleur[1], couleur[2]
            return r/255.0, g/255.0, b/255.0
        
        # Récupération des données du tableau
        tableau = self
        nbreColonnes = tableau.GetNumberCols()
        nbreLignes = tableau.GetNumberRows()
        
        # Initialisation du tableau
        story = []
        dataTableau = []
        listeCouleurs = []
        
        # Création des colonnes
        largeursColonnes = []
        largeurColonne = 45
        largeurColonneLabel = 90
        for col in range(0, nbreColonnes+1) :
            if col == 0 : largeursColonnes.append(largeurColonneLabel)
            else: largeursColonnes.append(largeurColonne)
        
        listeStyles = [
            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
            ('VALIGN', (0, 0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
            ('ALIGN', (0, 0), (-1, 0), 'CENTRE'), # Centre les labels de colonne
            ('ALIGN', (1, 1), (-1,- 1), 'CENTRE'), # Valeurs à gauche
            ('ALIGN', (0, 1), (0, -1), 'CENTRE'), # Colonne Label Ligne centrée
            ('FONT',(0, 0),(-1,-1), "Helvetica", 6), # Donne la police de caract. + taille de police de la ligne de total
            ('FONT',(0, 0),(-1,0), "Helvetica-Bold", 6), # Donne la police de caract. + taille de police de la ligne de total
            ]
        
        # Création de l'entete
        style_label_col = ParagraphStyle(name="label", fontName="Helvetica", alignment=1, fontSize=6, spaceAfter=0, leading=8, spaceBefore=0)
        valeursLigne = ["",]
        for numColonne in range(0, nbreColonnes) :
            labelColonne = tableau.GetColLabelValue(numColonne)
            valeursLigne.append(Paragraph(labelColonne, style_label_col))
        dataTableau.append(valeursLigne)
        
        # Création des lignes
        for numLigne in range(0, nbreLignes) :
            labelLigne = tableau.GetRowLabelValue(numLigne)
            valeursLigne = [labelLigne,]
            for numCol in range(0, nbreColonnes) :
                valeurCase = tableau.GetCellValue(numLigne, numCol)
                couleurCase = tableau.GetCellBackgroundColour(numLigne, numCol)
                if couleurCase != (255, 255, 255, 255) and avecCouleurs == True :
                    r, g, b = ConvertCouleur(couleurCase)
                    listeStyles.append( ('BACKGROUND', (numCol+1, numLigne+1), (numCol+1, numLigne+1), (r, g, b) ) )
                if numLigne == 0 :
                    valeurCase = valeurCase.replace(" ", "\n")
                valeursLigne.append(valeurCase)

            dataTableau.append(valeursLigne)
    
        # Style du tableau
        style = TableStyle(listeStyles)
        
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes,  hAlign='LEFT')
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))
        
        # Calcul du format de la page
        tailleMarge = 20
        if sum(largeursColonnes) > A4[0] - (tailleMarge*2) :
            hauteur, largeur = A4
        else :
            largeur, hauteur = A4

        # Création du titre du document
        dataTableau = []
        largeurContenu = largeur - (tailleMarge*2)
        largeursColonnes = ( (largeurContenu-100, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Synthèse des locations"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        story.insert(0, tableau)
        story.insert(1, Spacer(0, 10))       
        
        # Insertion du label Paramètres
        styleA = ParagraphStyle(name="A", fontName="Helvetica", fontSize=6, spaceAfter=20)
        story.insert(2, Paragraph(self.labelParametres, styleA))       

        # Enregistrement du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("SYNTHESE_LOCATIONS", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur, hauteur), leftMargin=tailleMarge, rightMargin=tailleMarge, topMargin=tailleMarge, bottomMargin=tailleMarge)
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)

    def ExportTexte(self, event=None):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(grid=self, titre=_(u"Synthèse des locations"))
        
    def ExportExcel(self, event=None):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(grid=self, titre=_(u"Synthèse des locations"))


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.grille = CTRL(panel)
        self.grille.MAJ(date_debut=datetime.date(2020, 1, 1), date_fin=datetime.date(2020, 12, 31), listeCategories=[1, 2],
                        affichage_donnees="quantite", affichage_regroupement="jour")
        self.bouton_test = wx.Button(panel, -1, u"Test export Excel")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.grille, 1, wx.EXPAND, 0)
        sizer_2.Add(self.bouton_test, 0, wx.EXPAND, 0)
        panel.SetSizer(sizer_2)
        self.SetSize((750, 400))
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)

    def OnBoutonTest(self, event):
        self.grille.ExportExcel()



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", name="test")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
