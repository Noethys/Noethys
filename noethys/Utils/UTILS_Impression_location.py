#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
import datetime
import FonctionsPerso
from Dlg import DLG_Noedoc
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus import PageBreak
from reportlab.platypus.frames import Frame
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import DocAssign, Flowable


TAILLE_PAGE = A4
LARGEUR_PAGE = TAILLE_PAGE[0]
HAUTEUR_PAGE = TAILLE_PAGE[1]
    
DICT_COMPTES = {}
DICT_OPTIONS = {} 



def Template(canvas, doc):
    """ Première page de l'attestation """
    doc.modeleDoc.DessineFond(canvas) 
    doc.modeleDoc.DessineFormes(canvas) 



class MyPageTemplate(PageTemplate):
    def __init__(self, id=-1, pageSize=TAILLE_PAGE, doc=None):
        self.pageWidth = pageSize[0]
        self.pageHeight = pageSize[1]
        
##        # Récupère les coordonnées du cadre principal
##        cadre_principal = doc.modeleDoc.FindObjet("cadre_principal")
##        x, y, l, h = doc.modeleDoc.GetCoordsObjet(cadre_principal)
##        global CADRE_CONTENU
##        CADRE_CONTENU = (x, y, l, h)
        
        x, y, l, h = 0, 0, self.pageWidth, self.pageHeight
        frame1 = Frame(x, y, l, h, id='F1', leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0)
        PageTemplate.__init__(self, id, [frame1], Template) 

    def afterDrawPage(self, canvas, doc):
        IDlocation = doc._nameSpace["IDlocation"]
        dictValeur = DICT_VALEURS[IDlocation]

        canvas.saveState() 
        doc.modeleDoc.DessineImages(canvas, dictChamps=dictValeur)
        doc.modeleDoc.DessineTextes(canvas, dictChamps=dictValeur)
        canvas.restoreState()



class Bookmark(Flowable):
    """ Utility class to display PDF bookmark. """
    def __init__(self, title, key):
        self.title = title
        self.key = key
        Flowable.__init__(self)

    def wrap(self, availWidth, availHeight):
        """ Doesn't take up any space. """
        return (0, 0)

    def draw(self):
        # set the bookmark outline to show when the file's opened
        self.canv.showOutline()
        # step 1: put a bookmark on the 
        self.canv.bookmarkPage(self.key)
        # step 2: put an entry in the bookmark outline
        self.canv.addOutlineEntry(self.title, self.key, 0, 0)
        
        
class Impression():
    def __init__(self, dictValeurs={}, dictOptions={}, IDmodele=None, ouverture=True, nomFichier=None):
        """ Impression """
        global DICT_VALEURS, DICT_OPTIONS
        DICT_VALEURS = dictValeurs
        DICT_OPTIONS = dictOptions
        
        # Initialisation du document
        if nomFichier == None :
            nomDoc = FonctionsPerso.GenerationNomDoc("LOCATIONS", "pdf")
        else :
            nomDoc = nomFichier
        doc = BaseDocTemplate(nomDoc, pagesize=TAILLE_PAGE, showBoundary=False)
        
        # Mémorise le ID du modèle
        modeleDoc = DLG_Noedoc.ModeleDoc(IDmodele=IDmodele)
        doc.modeleDoc = modeleDoc
        
        # Importe le template de la première page
        doc.addPageTemplates(MyPageTemplate(pageSize=TAILLE_PAGE, doc=doc))
        
        story = []
        styleSheet = getSampleStyleSheet()
        h3 = styleSheet['Heading3']
        styleTexte = styleSheet['BodyText'] 
        styleTexte.fontName = "Helvetica"
        styleTexte.fontSize = 9
        styleTexte.borderPadding = 9
        styleTexte.leading = 12
        
        # ----------- Insertion du contenu des frames --------------
        listeLabels = []
        for IDlocation, dictValeur in dictValeurs.items() :
            listeLabels.append((dictValeur["{FAMILLE_NOM}"], IDlocation))
        listeLabels.sort() 
        
        for labelDoc, IDlocation in listeLabels :
            dictValeur = dictValeurs[IDlocation]
            if dictValeur["select"] == True :
                
                story.append(DocAssign("IDlocation", IDlocation))
                nomSansCivilite = dictValeur["{FAMILLE_NOM}"]
                story.append(Bookmark(nomSansCivilite, str(IDlocation)))

                # Saut de page
                story.append(PageBreak())
        
        # Finalisation du PDF
        doc.build(story)
        
        # Ouverture du PDF
        if ouverture == True :
            FonctionsPerso.LanceFichierExterne(nomDoc)





if __name__ == u"__main__":
    Impression()
