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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Selection_activites
from Ctrl import CTRL_Grille_periode

import FonctionsPerso
import sys
import operator
from Ctrl import CTRL_Photo
from Data import DATA_Civilites as Civilites
from Utils import UTILS_Fichiers

##from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, NextPageTemplate
##from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
##from reportlab.platypus.flowables import ParagraphAndImage, Image
##from reportlab.platypus.frames import Frame, ShowBoundaryValue
##from reportlab.rl_config import defaultPageSize
##from reportlab.lib.pagesizes import A4
##from reportlab.lib.units import inch, cm
##from reportlab.lib.utils import ImageReader
##from reportlab.lib import colors
##from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, NextPageTemplate
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import ParagraphAndImage, Image
from reportlab.platypus.frames import Frame, ShowBoundaryValue
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.platypus.flowables import DocAssign, Flowable

try: import psyco; psyco.full()
except: pass

DICT_CIVILITES = Civilites.GetDictCivilites()
LARGEUR_COLONNE = 158
LISTE_NOMS_MOIS = [_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")]
IMAGE_FOND = None

THEMES = {
    _(u"Plage de cailloux") : "Images/Special/Cailloux.jpg",
    _(u"Gouttes d'eau") : "Images/Special/Eau.jpg",
    _(u"Feuille d'été") : "Images/Special/Feuille.jpg",
    _(u"Ballet de lignes") : "Images/Special/Lignes.jpg",
    _(u"Montgolfières") : "Images/Special/Montgolfiere.jpg",
    _(u"Mosaïque") : "Images/Special/Mosaique.jpg",
    }


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def GetSQLdates(listePeriodes=[]):
    texteSQL = ""
    for date_debut, date_fin in listePeriodes :
        texteSQL += "(date>='%s' AND date<='%s') OR " % (date_debut, date_fin)
    if len(texteSQL) > 0 :
        texteSQL = "(" + texteSQL[:-4] + ")"
    else:
        texteSQL = "date=0"
    return texteSQL

def GetAge(date_naiss=None):
    if date_naiss == None : return None
    datedujour = datetime.date.today()
    age = (datedujour.year - date_naiss.year) - int((datedujour.month, datedujour.day) < (date_naiss.month, date_naiss.day))
    return age

def Template(canvas, doc):
    """ Première page de l'attestation """
    canvas.saveState() 
    # Insertion de l'image de fond de page
    if IMAGE_FOND != None :
        canvas.drawImage(IMAGE_FOND, 0, 0, doc.pagesize[0], doc.pagesize[1], preserveAspectRatio=True)
    canvas.restoreState()


class MyPageTemplate(PageTemplate):
    def __init__(self, id=-1, pageSize=None, rect=None):
        self.pageWidth = pageSize[0]
        self.pageHeight = pageSize[1]
        
        self.hauteurColonne = 700
        self.margeBord = 40
        self.margeInter = 20
        
        x, y, l, h = (self.margeBord, self.margeBord, LARGEUR_COLONNE, self.hauteurColonne)
        frame1 = Frame(x, y, l, h, id='F1', leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0)
        
        x, y, l, h = (self.margeBord+LARGEUR_COLONNE+self.margeInter, self.margeBord, LARGEUR_COLONNE, self.hauteurColonne)
        frame2 = Frame(x, y, l, h, id='F2', leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0)
        
        x, y, l, h = (self.margeBord+(LARGEUR_COLONNE+self.margeInter)*2, self.margeBord, LARGEUR_COLONNE, self.hauteurColonne)
        frame3 = Frame(x, y, l, h, id='F2', leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0)
        
        PageTemplate.__init__(self, id, [frame1, frame2, frame3], Template) 

    def afterDrawPage(self, canvas, doc):
        numMois = doc._nameSpace["numMois"]
        nomMois = LISTE_NOMS_MOIS[numMois-1]
        
        # Affiche le nom du mois en haut de la page
        canvas.saveState() 

        canvas.setLineWidth(0.25)
        canvas.setStrokeColorRGB(0, 0, 0)
        canvas.setFillColorRGB(0.7, 0.7, 1)
        canvas.rect(self.margeBord, self.pageHeight-self.margeBord, self.pageWidth-(self.margeBord*2), -38, fill=1)
        
        canvas.setFont("Helvetica-Bold", 24)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.drawString(self.margeBord+10, self.pageHeight-self.margeBord-26, nomMois)

        canvas.restoreState()
        


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici imprimer la liste des anniversaires des individus inscrits sur les activités cochées et présents sur la période donnée. Il est possible d'inclure un thème graphique et les photos individuelles.")
        titre = _(u"Liste des anniversaires")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Anniversaire.png")
        
        # Périodes
        self.box_periodes_staticbox = wx.StaticBox(self, -1, _(u"Période"))
        self.ctrl_periodes = CTRL_Grille_periode.CTRL(self)
        self.ctrl_periodes.SetMinSize((200, 150))

        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        
        self.check_photos = wx.CheckBox(self, -1, u"")
        self.check_photos.SetValue(True)
        self.label_photos = wx.StaticText(self, -1, _(u"Afficher les photos :"))
        self.ctrl_photos = wx.Choice(self, -1, choices=[_(u"Petite taille"), _(u"Moyenne taille"), _(u"Grande taille")])
        self.ctrl_photos.SetSelection(1)

        self.check_theme = wx.CheckBox(self, -1, u"")
        self.check_theme.SetValue(True)
        self.label_theme = wx.StaticText(self, -1, _(u"Inclure le thème :"))
        self.ctrl_theme = wx.Choice(self, -1, choices=THEMES.keys())
        self.ctrl_theme.SetStringSelection(_(u"Feuille d'été"))
        
        # Activités
        self.box_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckPhotos, self.check_photos)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckTheme, self.check_theme)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)

        # Init Contrôles
        self.OnCheckPhotos(None) 
        self.bouton_ok.SetFocus() 

    def __set_properties(self):
        self.SetTitle(_(u"Liste des anniversaires"))
        self.check_photos.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour utiliser un thème graphique")))
        self.ctrl_photos.SetToolTip(wx.ToolTip(_(u"Selectionnez ici le thème souhaité")))
        self.check_photos.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les photos des individus")))
        self.ctrl_photos.SetToolTip(wx.ToolTip(_(u"Selectionnez ici la taille des photos")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher la liste au format PDF")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((520, 460))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        sizer_activites = wx.StaticBoxSizer(self.box_activites_staticbox, wx.VERTICAL)
        grid_sizer_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        
        box_periodes = wx.StaticBoxSizer(self.box_periodes_staticbox, wx.VERTICAL)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        box_periodes.Add(self.ctrl_periodes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_periodes, 1, wx.EXPAND, 0)
        
        # Photos
        grid_sizer_options.Add(self.check_photos, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_photos = wx.FlexGridSizer(rows=1, cols=2, vgap=2, hgap=2)
        grid_sizer_photos.Add(self.label_photos, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_photos.Add(self.ctrl_photos, 0, 0, 0)
        grid_sizer_options.Add(grid_sizer_photos, 1, wx.EXPAND, 0)

        # Thème
        grid_sizer_options.Add(self.check_theme, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_theme = wx.FlexGridSizer(rows=1, cols=2, vgap=2, hgap=2)
        grid_sizer_theme.Add(self.label_theme, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_theme.Add(self.ctrl_theme, 0, 0, 0)
        grid_sizer_options.Add(grid_sizer_theme, 1, wx.EXPAND, 0)
        
        grid_sizer_options.AddGrowableCol(1)
        box_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(box_options, 1, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        sizer_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(sizer_activites, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnCheckPhotos(self, event): 
        if self.check_photos.GetValue() == True :
            self.ctrl_photos.Enable(True)
        else:
            self.ctrl_photos.Enable(False)

    def OnCheckTheme(self, event): 
        if self.check_theme.GetValue() == True :
            self.ctrl_theme.Enable(True)
        else:
            self.ctrl_theme.Enable(False)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesanniversaires")

    def OnBoutonFermer(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnCheckActivites(self):
        pass

    def OnBoutonOk(self, event): 
        global IMAGE_FOND
        # Récupération des activtés
        if self.ctrl_activites.Validation() == False :
            return
        listeActivites = self.ctrl_activites.GetActivites() 
        # Récupération des périodes
        listePeriodes = self.ctrl_periodes.GetDatesSelections() 
        # Image fond
        if self.check_theme.GetValue() == True :
            IMAGE_FOND = Chemins.GetStaticPath(THEMES[self.ctrl_theme.GetStringSelection()])
        else:
            IMAGE_FOND = None
        # Création du PDF
        self.Impression(listeActivites, listePeriodes)

    def EcritStatusBar(self, texte=u"") :
##        print (texte,)
        try :
            wx.GetApp().GetTopWindow().SetStatusText(texte, 0)
        except : pass

    def Impression(self, listeActivites, listePeriodes):
        # Création du PDF
        self.taille_page = A4
        self.orientation = "PORTRAIT"
        if self.orientation == "PORTRAIT" :
            self.hauteur_page = self.taille_page[1]
            self.largeur_page = self.taille_page[0]
        else:
            self.hauteur_page = self.taille_page[0]
            self.largeur_page = self.taille_page[1]
        
        # Création des conditions pour les requêtes SQL
        conditionsPeriodes = GetSQLdates(listePeriodes)
        
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))
                                    
        # Récupération des individus grâce à leurs consommations
        self.EcritStatusBar(_(u"Recherche des individus..."))
        DB = GestionDB.DB() 
        req = """SELECT individus.IDindividu, IDcivilite, nom, prenom, date_naiss
        FROM consommations 
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        WHERE etat IN ("reservation", "present")
        AND IDactivite IN %s AND %s
        GROUP BY individus.IDindividu
        ORDER BY nom, prenom
        ;""" % (conditionActivites, conditionsPeriodes)
        DB.ExecuterReq(req)
        listeIndividus = DB.ResultatReq()
        DB.Close() 
        if len(listeIndividus) == 0 :
            dlg = wx.MessageDialog(self, _(u"Aucun individu n'a été trouvé avec les paramètres spécifiés !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.EcritStatusBar(u"")
            return

        dictIndividus = {}
        listeIDindividus = []
        
        dictAnniversaires = {} 
        
        self.EcritStatusBar(_(u"Recherche des dates de naissance..."))
        for IDindividu, IDcivilite, nom, prenom, date_naiss in listeIndividus :
            if date_naiss != None : 
                date_naiss = DateEngEnDateDD(date_naiss)
                age = GetAge(date_naiss)
                jour = date_naiss.day
                mois = date_naiss.month
                
                # Mémorisation de l'individu
                dictIndividus[IDindividu] = { 
                    "IDcivilite" : IDcivilite, "nom" : nom, "prenom" : prenom, 
                    "age" : age, "date_naiss" : date_naiss,
                    }
                
                # Mémorisation du IDindividu
                if dictAnniversaires.has_key(mois) == False : 
                    dictAnniversaires[mois] = {} 
                if dictAnniversaires[mois].has_key(jour) == False : 
                    dictAnniversaires[mois][jour] = []
                dictAnniversaires[mois][jour].append(IDindividu)
                
                if IDindividu not in listeIDindividus :
                    listeIDindividus.append(IDindividu) 
                
        # Récupération des photos individuelles
        dictPhotos = {}
        taillePhoto = 128
        if self.ctrl_photos.GetSelection() == 0 : tailleImageFinal = 16
        if self.ctrl_photos.GetSelection() == 1 : tailleImageFinal = 32
        if self.ctrl_photos.GetSelection() == 2 : tailleImageFinal = 64
        if self.check_photos.GetValue() == True :
            index = 0
            for IDindividu in listeIDindividus :
                self.EcritStatusBar(_(u"Recherche des photos... %d/%d") % (index, len(listeIDindividus)))
                IDcivilite = dictIndividus[IDindividu]["IDcivilite"]
                nomFichier = Chemins.GetStaticPath("Images/128x128/%s" % DICT_CIVILITES[IDcivilite]["nomImage"])
                IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDindividu, nomFichier=nomFichier, taillePhoto=(taillePhoto, taillePhoto), qualite=100)
                
                # Création de la photo dans le répertoire Temp
                nomFichier = UTILS_Fichiers.GetRepTemp(fichier="photoTmp%d.jpg" % IDindividu)
                bmp.SaveFile(nomFichier, type=wx.BITMAP_TYPE_JPEG)
                img = Image(nomFichier, width=tailleImageFinal, height=tailleImageFinal)
                dictPhotos[IDindividu] = img
                
                index += 1
            
        # ---------------- Création du PDF -------------------
        self.EcritStatusBar(_(u"Création du PDF...")) 
        
        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("ANNIVERSAIRES", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = BaseDocTemplate(nomDoc, pagesize=(self.largeur_page, self.hauteur_page), topMargin=30, bottomMargin=30, showBoundary=False)
        doc.addPageTemplates(MyPageTemplate(pageSize=(self.largeur_page, self.hauteur_page)))
        story = []
                        
        # Mois
        listeMois = dictAnniversaires.keys()
        listeMois.sort() 
        for numMois in listeMois :
            
            # Mémorise le numéro de mois pour le titre de la page
            nomMois = LISTE_NOMS_MOIS[numMois-1]
            story.append(DocAssign("numMois", numMois))

            # Jours
            dictJours = dictAnniversaires[numMois]
            listeJours = dictJours.keys() 
            listeJours.sort() 
            for numJour in listeJours :                                
                # Initialisation du tableau
                dataTableau = []
                largeursColonnes = []
                                    
                # Recherche des entêtes de colonnes :
                if self.check_photos.GetValue() == True :
                    largeursColonnes.append(tailleImageFinal+6)
                
                # Colonne nom de l'individu
                largeursColonnes.append(LARGEUR_COLONNE-sum(largeursColonnes))
                
                # Label numéro de jour
                ligne = []
                ligne.append(str(numJour))
                if self.check_photos.GetValue() == True :
                    ligne.append(u"")
                dataTableau.append(ligne)
                
                # Individus
                listeIndividus = dictAnniversaires[numMois][numJour]
                
                for IDindividu in listeIndividus :
                    ligne = []
                    
                    # Photo
                    if self.check_photos.GetValue() == True and IDindividu in dictPhotos :
                        img = dictPhotos[IDindividu]
                        ligne.append(img)
                    
                    # Nom
                    nom = dictIndividus[IDindividu]["nom"]
                    prenom = dictIndividus[IDindividu]["prenom"]
                    ligne.append(u"%s %s" % (nom, prenom))
                    
                    # Ajout de la ligne individuelle dans le tableau
                    dataTableau.append(ligne)
             
                couleurFondJour = (0.8, 0.8, 1) # Vert -> (0.5, 1, 0.2)
                couleurFondTableau = (1, 1, 1)
                
                style = TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                        ('BACKGROUND', (0,0), (-1,-1), couleurFondTableau), # Donne la couleur de fond du titre de groupe
                        
                        ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                        ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                        ('ALIGN', (0,1), (-1,-1), 'CENTRE'), # Centre les cases
                        
                        ('SPAN',(0,0),(-1,0)), # Fusionne les lignes du haut pour faire le titre du groupe
                        ('FONT',(0,0),(0,0), "Helvetica-Bold", 10), # Donne la police de caract. + taille de police du titre de groupe
                        ('BACKGROUND', (0,0), (-1,0), couleurFondJour), # Donne la couleur de fond du titre de groupe
                        
                        ])
                    
                # Création du tableau
                tableau = Table(dataTableau, largeursColonnes)
                tableau.setStyle(style)
                story.append(tableau)
                story.append(Spacer(0, 10))
                    
            # Saut de page après un mois
            story.append(PageBreak())
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
        
        self.EcritStatusBar(u"") 
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
