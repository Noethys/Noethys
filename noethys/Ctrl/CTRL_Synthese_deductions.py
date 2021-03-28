#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-21 Ivan LUCAS
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
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal


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
        self.affichage_regroupement = "individu"
        self.affichage_caisse = None
        self.labelParametres = ""
                

    def MAJ(self, date_debut=None, date_fin=None, listeActivites=[], affichage_regroupement="jour", affichage_caisse=None, labelParametres=u""):

        # Chargement des informations individuelles
        if self.date_debut != date_debut :
            self.infosIndividus = UTILS_Infos_individus.Informations(date_reference=date_debut, qf=True, inscriptions=False, messages=False, infosMedicales=False, cotisationsManquantes=False, piecesManquantes=False, questionnaires=True, scolarite=False)
            self.dictInfosFamilles = self.infosIndividus.GetDictValeurs(mode="famille", ID=None, formatChamp=False)

        # Mémorisation des paramètres
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.listeActivites = listeActivites
        self.affichage_regroupement = affichage_regroupement
        self.affichage_caisse = affichage_caisse
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
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré dans la recherche des données de la synthèse des déductions : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def Importation(self):
        DB = GestionDB.DB()

        if len(self.listeActivites) == 0: conditionActivites = "()"
        elif len(self.listeActivites) == 1: conditionActivites = "(%d)" % self.listeActivites[0]
        else: conditionActivites = str(tuple(self.listeActivites))

        if self.affichage_caisse:
            conditionsCaisse = "AND aides.IDcaisse=%d" % self.affichage_caisse
        else:
            conditionsCaisse = ""

        # Déductions
        req = """SELECT 
        IDdeduction, deductions.IDprestation, deductions.IDcompte_payeur, deductions.date, deductions.montant, deductions.label, deductions.IDaide, 
        individus.nom, individus.prenom, individus.date_naiss,
        prestations.label, prestations.montant, prestations.montant_initial, prestations.IDfamille, prestations.IDactivite, activites.abrege, prestations.IDindividu, prestations.date, prestations.IDfacture,
        familles.IDcaisse, familles.num_allocataire, caisses.nom, aides.nom
        FROM deductions
        LEFT JOIN prestations ON prestations.IDprestation = deductions.IDprestation
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        LEFT JOIN familles ON familles.IDfamille = prestations.IDfamille
        LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
        LEFT JOIN aides ON aides.IDaide = deductions.IDaide
        WHERE deductions.date>='%s' AND deductions.date<='%s' AND prestations.IDactivite IN %s
        %s;""" % (self.date_debut, self.date_fin, conditionActivites, conditionsCaisse)
        DB.ExecuterReq(req)
        listeDeductions = DB.ResultatReq()
        DB.Close()

        # Calcul des données
        dictResultats = {}
        listePrestations = []
        for IDdeduction, IDprestation, IDcompte_payeur, date, montant, label, IDaide, nomIndividu, prenomIndividu, date_naiss, labelPrestation, montantPrestation, montantInitialPrestation, IDfamille, IDactivite, abregeActivite, IDindividu, datePrestation, IDfacture, IDcaisse, num_allocataire, nomCaisse, nomAide in listeDeductions:
            date = UTILS_Dates.DateEngEnDateDD(date)
            datePrestation = UTILS_Dates.DateEngEnDateDD(datePrestation)
            date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)
            mois = date.month
            annee = date.year
            nom_complet_individu = u"%s %s" % (nomIndividu, prenomIndividu)
            montantInitialPrestation = FloatToDecimal(montantInitialPrestation)
            montant = FloatToDecimal(montant)
            montantPrestation = FloatToDecimal(montantPrestation)

            # Recherche du regroupement
            try :
                if self.affichage_regroupement == "jour" : regroupement = date
                if self.affichage_regroupement == "mois" : regroupement = (annee, mois)
                if self.affichage_regroupement == "annee" : regroupement = annee
                if self.affichage_regroupement == "montant_deduction": regroupement = montant
                if self.affichage_regroupement == "nom_aide" : regroupement = nomAide
                if self.affichage_regroupement == "nom_deduction": regroupement = label
                if self.affichage_regroupement == "ville_residence" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_VILLE"]
                if self.affichage_regroupement == "secteur" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_SECTEUR"]
                if self.affichage_regroupement == "famille" : regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM"]
                if self.affichage_regroupement == "individu": regroupement = IDindividu
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

            # Colonne
            if labelPrestation not in listePrestations:
                listePrestations.append(labelPrestation)

            # Regroupement
            if regroupement not in dictResultats:
                dictResultats[regroupement] = {
                    "caisse": nomCaisse, "num_allocataire": num_allocataire, "prestations": {},
                    "montant_initial": FloatToDecimal(0), "montant_deduction": FloatToDecimal(0), "montant_final": FloatToDecimal(0),
                    "liste_dates": [], "individu": nom_complet_individu, "famille": self.dictInfosFamilles[IDfamille]["FAMILLE_NOM"],
                }
            dictResultats[regroupement]["montant_initial"] += montantInitialPrestation
            dictResultats[regroupement]["montant_deduction"] += montant
            dictResultats[regroupement]["montant_final"] += montantPrestation
            if date not in dictResultats[regroupement]["liste_dates"]:
                dictResultats[regroupement]["liste_dates"].append(date)

            # Prestations
            if labelPrestation not in dictResultats[regroupement]["prestations"]:
                dictResultats[regroupement]["prestations"][labelPrestation] = {
                    "nbre": 0, "liste_dates": [], "montant_initial": montantInitialPrestation,
                    "montant_deduction": montant, "montant_final": montantPrestation,
                }
            dictResultats[regroupement]["prestations"][labelPrestation]["nbre"] += 1
            if date not in dictResultats[regroupement]["prestations"][labelPrestation]["liste_dates"]:
                dictResultats[regroupement]["prestations"][labelPrestation]["liste_dates"].append(date)
            dictResultats[regroupement]["prestations"][labelPrestation]["montant_initial"] += montantInitialPrestation
            dictResultats[regroupement]["prestations"][labelPrestation]["montant_deduction"] += montant
            dictResultats[regroupement]["prestations"][labelPrestation]["montant_final"] += montantPrestation

        return dictResultats, listePrestations
    
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
        dictResultats, listePrestations = self.Importation()

        # Préparation des colonnes
        listeColonnes = [
            ("montant_initial", _(u"Total initial")),
            ("montant_deduction", _(u"Total déduit")),
            ("montant_final", _(u"Total final")),
            ("date_min", _(u"Date min")),
            ("date_max", _(u"Date max")),
            ("nbre_dates", _(u"Nbre dates")),
        ]
        if self.affichage_regroupement == "individu":
            listeColonnes.insert(0, ("num_allocataire", _(u"N° Allocataire")))
            listeColonnes.insert(0, ("famille", _(u"Famille")))
        if self.affichage_regroupement == "famille":
            listeColonnes.insert(0, ("num_allocataire", _(u"N° Allocataire")))
        for label_prestation in listePrestations:
            listeColonnes.append(("prestation", label_prestation))

        # Création des colonnes
        largeur_colonne = 100
        dictColonnes = {}
        self.AppendCols(len(listeColonnes))
        index = 0
        for code_colonne, label_colonne in listeColonnes:
            self.SetColSize(index, largeur_colonne)
            renderer = LabelColonneRenderer()
            self.SetColLabelRenderer(index, renderer)
            self.SetColLabelValue(index, label_colonne)
            dictColonnes[code_colonne] = index
            index += 1

        # Création des lignes
        listeRegroupement = dictResultats.keys()
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
            elif self.affichage_regroupement == "individu":
                label = dictResultats[regroupement]["individu"]
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
        dict_totaux = {}
        for numLigne, (regroupement, valeurs) in enumerate(dictResultats.items()):
            for numColonne, (code_colonne, label_colonne) in enumerate(listeColonnes):
                valeur = ""
                dict_totaux.setdefault(numColonne, 0)
                if code_colonne == "num_allocataire": valeur = valeurs["num_allocataire"]
                if code_colonne == "famille": valeur = valeurs["famille"]
                if code_colonne == "montant_initial": valeur = valeurs["montant_initial"]
                if code_colonne == "montant_deduction": valeur = valeurs["montant_deduction"]
                if code_colonne == "montant_final": valeur = valeurs["montant_final"]
                if code_colonne == "date_min": valeur = UTILS_Dates.DateDDEnFr(min(valeurs["liste_dates"]))
                if code_colonne == "date_max": valeur = UTILS_Dates.DateDDEnFr(max(valeurs["liste_dates"]))
                if code_colonne == "nbre_dates": valeur = len(valeurs["liste_dates"])
                if code_colonne == "prestation":
                    try:
                        valeur = valeurs["prestations"][label_colonne]["nbre"]
                    except:
                        pass
                try:
                    dict_totaux[numColonne] += valeur
                except:
                    pass
                self.SetCellValue(numLigne, numColonne, str(valeur))
                self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetReadOnly(numLigne, numColonne, True)

        # Remplissage des totaux
        numLigne = len(listeRegroupement)
        for numColonne, (code_colonne, label_colonne) in enumerate(listeColonnes):
            valeur = dict_totaux.get(numColonne, "")
            if not valeur: valeur = ""
            self.SetCellValue(numLigne, numColonne, str(valeur))
            self.SetCellAlignment(numLigne, numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetReadOnly(numLigne, numColonne, True)
            self.SetCellBackgroundColour(numLigne, numColonne, (240, 240, 240))

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
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Centre verticalement toutes les cases
            ('ALIGN', (0, 0), (-1, 0), 'CENTRE'), # Centre les labels de colonne
            ('ALIGN', (1, 1), (-1, - 1), 'CENTRE'), # Valeurs à gauche
            ('ALIGN', (0, 1), (0, -1), 'CENTRE'), # Colonne Label Ligne centrée
            ('FONT', (0, 0), (-1, -1), "Helvetica", 6), # Donne la police de caract. + taille de police de la ligne de total
            ('FONT', (0, 0), (-1, 0), "Helvetica-Bold", 6), # Donne la police de caract. + taille de police de la ligne de total
            ]
        
        # Création de l'entete
        style_label_col = ParagraphStyle(name="label", fontName="Helvetica", alignment=1, fontSize=6, spaceAfter=0, leading=8, spaceBefore=0)
        valeursLigne = ["",]
        for numColonne in range(0, nbreColonnes) :
            labelColonne = tableau.GetColLabelValue(numColonne)
            valeursLigne.append(Paragraph(labelColonne, style_label_col))
        dataTableau.append(valeursLigne)
        
        # Création des lignes
        styleA = ParagraphStyle(name="A", fontName="Helvetica", alignment=1, fontSize=6, leading=7, spaceAfter=0)

        for numLigne in range(0, nbreLignes) :
            labelLigne = tableau.GetRowLabelValue(numLigne)
            valeursLigne = [labelLigne,]
            for numCol in range(0, nbreColonnes) :
                valeurCase = tableau.GetCellValue(numLigne, numCol)
                couleurCase = tableau.GetCellBackgroundColour(numLigne, numCol)
                if couleurCase != (255, 255, 255, 255) and avecCouleurs == True :
                    r, g, b = ConvertCouleur(couleurCase)
                    listeStyles.append( ('BACKGROUND', (numCol+1, numLigne+1), (numCol+1, numLigne+1), (r, g, b) ) )
                # if numLigne == 0 :
                #     valeurCase = valeurCase.replace(" ", "\n")
                # valeursLigne.append(valeurCase)
                valeursLigne.append(Paragraph(valeurCase, styleA))

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
        dataTableau.append( (_(u"Synthèse des déductions"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        nomDoc = FonctionsPerso.GenerationNomDoc("SYNTHESE_DEDUCTIONS", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur, hauteur), leftMargin=tailleMarge, rightMargin=tailleMarge, topMargin=tailleMarge, bottomMargin=tailleMarge)
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)

    def ExportTexte(self, event=None):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(grid=self, titre=_(u"Synthèse des déductions"))
        
    def ExportExcel(self, event=None):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(grid=self, titre=_(u"Synthèse des déductions"))


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.grille = CTRL(panel)
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
