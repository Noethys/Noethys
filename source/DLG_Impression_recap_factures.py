#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import sys
import CTRL_Bouton_image
import GestionDB

import UTILS_Config
import UTILS_Parametres

import CTRL_Bandeau
import CTRL_Propertygrid
import wx.propgrid as wxpg
import copy
import FonctionsPerso
import UTILS_Dates
import datetime
import UTILS_Organisateur

from UTILS_Decimal import FloatToDecimal as FloatToDecimal

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")



def ConvertCouleurWXpourPDF(couleurwx=(0, 0, 0)):
    return (couleurwx[0]/255.0, couleurwx[1]/255.0, couleurwx[2]/255.0)

def ConvertAlignement1(align=wx.ALIGN_LEFT):
    if align == wx.ALIGN_LEFT : return "LEFT"
    if align == wx.ALIGN_RIGHT : return "RIGHT"
    if align == wx.ALIGN_CENTER : return "CENTER"

def ConvertAlignement2(align=wx.ALIGN_LEFT):
    if align == wx.ALIGN_LEFT : return 0
    if align == wx.ALIGN_RIGHT : return 2
    if align == wx.ALIGN_CENTER : return 1


class CTRL_Parametres(CTRL_Propertygrid.CTRL) :
    def __init__(self, parent):
        CTRL_Propertygrid.CTRL.__init__(self, parent)
    
    def Remplissage(self):
        # --------------------------- TYPE DE DOCUMENT------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Type de document")) )
    
        # Type
        propriete = wxpg.EnumProperty(label=_(u"Type"), name="type_document", labels=[_(u"D�taill�"), _(u"Simplifi�"), (u"Totaux")], values=[0, 1, 2], value=0)
        propriete.SetHelpString(_(u"S�lectionnez un type de document")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # --------------------------- COULEURS DE FOND ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Couleurs de fond")) )
        
        # Couleur 1
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond 1"), name="couleur_fond_1", value=wx.Colour(204, 204, 255))
        propriete.SetHelpString(_(u"S�lectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur 2
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond 2"), name="couleur_fond_2", value=wx.Colour(230, 230, 255))
        propriete.SetHelpString(_(u"S�lectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # --------------------------- TITRE ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Titre")) )

        # Texte
        propriete = wxpg.StringProperty(label=_(u"Texte"), name="titre_texte", value=_(u"R�capitulatif des factures"))
        propriete.SetHelpString(_(u"Saisissez un texte"))
        self.Append(propriete)

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="titre_taille_texte", value=16)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (16 par d�faut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("titre_taille_texte", "SpinCtrl")
        
        # Couleur
##        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="titre_couleur", value=wx.BLACK)
##        propriete.SetHelpString(_(u"S�lectionnez une couleur")) 
##        propriete.SetAttribute("obligatoire", True)
##        self.Append(propriete)

        # Alignement
        labels = [_(u"Gauche"), _(u"Centre"), _(u"Droite")]
        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte"), name="titre_alignement", labels=labels, values=[wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_RIGHT] , value=wx.ALIGN_LEFT)
        propriete.SetHelpString(_(u"S�lectionnez le type d'alignement")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # --------------------------- INTRODUCTION ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Introduction")) )

        # Texte
        propriete = wxpg.StringProperty(label=_(u"Texte"), name="intro_texte", value=u"")
        propriete.SetHelpString(_(u"Saisissez un texte"))
        self.Append(propriete)

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="intro_taille_texte", value=7)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (7 par d�faut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("intro_taille_texte", "SpinCtrl")

        # Style
##        labels = [_(u"Normal"), _(u"Light"), "Gras"]
##        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
##        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="intro_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_NORMAL)
##        propriete.SetHelpString(_(u"S�lectionnez un style de texte")) 
##        propriete.SetAttribute("obligatoire", True)
##        self.Append(propriete)
        
        # Couleur
##        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="intro_couleur", value=wx.BLACK)
##        propriete.SetHelpString(_(u"S�lectionnez une couleur")) 
##        propriete.SetAttribute("obligatoire", True)
##        self.Append(propriete)

        # Alignement
        labels = [_(u"Gauche"), _(u"Centre"), _(u"Droite")]
        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte"), name="intro_alignement", labels=labels, values=[wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_RIGHT] , value=wx.ALIGN_LEFT)
        propriete.SetHelpString(_(u"S�lectionnez le type d'alignement")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # --------------------------- CONCLUSION ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Conclusion")) )

        # Texte
        propriete = wxpg.StringProperty(label=_(u"Texte"), name="conclusion_texte", value=_(u"{NBRE_FACTURES} factures | Montant total : {TOTAL_FACTURES}"))
        propriete.SetHelpString(_(u"Saisissez un texte. Vous pouvez utiliser les mots-cl�s suivants : {NBRE_FACTURES}, {TOTAL_FACTURES}"))
        self.Append(propriete)

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="conclusion_taille_texte", value=7)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (7 par d�faut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("conclusion_taille_texte", "SpinCtrl")

        # Style
##        labels = [_(u"Normal"), _(u"Light"), "Gras"]
##        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
##        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="conclusion_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_BOLD)
##        propriete.SetHelpString(_(u"S�lectionnez un style de texte")) 
##        propriete.SetAttribute("obligatoire", True)
##        self.Append(propriete)
        
        # Couleur
##        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="conclusion_couleur", value=wx.BLACK)
##        propriete.SetHelpString(_(u"S�lectionnez une couleur")) 
##        propriete.SetAttribute("obligatoire", True)
##        self.Append(propriete)

        # Alignement
        labels = [_(u"Gauche"), _(u"Centre"), _(u"Droite")]
        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte"), name="conclusion_alignement", labels=labels, values=[wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_RIGHT] , value=wx.ALIGN_LEFT)
        propriete.SetHelpString(_(u"S�lectionnez le type d'alignement")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


    def Validation(self):
        """ Validation des donn�es saisies """
        for nom, valeur in self.GetPropertyValues().iteritems() :
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "obligatoire") == True :
                if valeur == "" or valeur == None :
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le param�tre '%s' !") % nom, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
        return True
        
    def Importation(self):
        """ Importation des valeurs dans le contr�le """
        # R�cup�ration des noms et valeurs par d�faut du contr�le
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        # Recherche les param�tres m�moris�s
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="impression_recap_factures", dictParametres=dictValeurs)
        # Envoie les param�tres dans le contr�le
        for nom, valeur in dictParametres.iteritems() :
            propriete = self.GetPropertyByName(nom)
            ancienneValeur = propriete.GetValue() 
            propriete.SetValue(valeur)
    
    def Sauvegarde(self, forcer=False):
        """ M�morisation des valeurs du contr�le """
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        UTILS_Parametres.ParametresCategorie(mode="set", categorie="impression_recap_factures", dictParametres=dictValeurs)
        
    def GetValeurs(self) :
        return self.GetPropertyValues()


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, dictOptions={}):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Param�tres g�n�raux
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options d'impression"))
        self.ctrl_parametres = CTRL_Parametres(self)
        self.ctrl_parametres.Importation() 
        self.bouton_reinitialisation = CTRL_Propertygrid.Bouton_reinitialisation(self, self.ctrl_parametres)
        self.bouton_sauvegarde = CTRL_Propertygrid.Bouton_sauvegarde(self, self.ctrl_parametres)
        self.ctrl_parametres.SetMinSize((50, 50)) 
        
        self.__do_layout()
                    
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=20)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)

        # Param�tres g�n�raux
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_parametres.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_reinitialisation, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_sauvegarde, 0, 0, 0)

        grid_sizer_parametres.Add(grid_sizer_boutons, 0, 0, 0)
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(0)
        box_options.Add(grid_sizer_parametres, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(box_options, 1, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
            
    def MemoriserParametres(self):
        self.ctrl_parametres.Sauvegarde() 
            
    def GetOptions(self):
        dictOptions = {} 
        
        # R�cup�ration des param�tres
        if self.ctrl_parametres.Validation() == False :
            return False
        for nom, valeur in self.ctrl_parametres.GetValeurs().iteritems()  :
            dictOptions[nom] = valeur

        return dictOptions


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, dictOptions={}, tracks=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   
        self.tracks = tracks

        # Bandeau
        titre = _(u"Impression d'un r�capitulatif des factures")
        intro = _(u"Vous pouvez ici modifier les param�tres d'impression du document. Cliquez sur le bouton 'M�moriser les param�tres' pour r�utiliser les m�mes param�tres pour les impressions suivantes.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")

        # Param�tres
        self.ctrl_parametres = CTRL(self, dictOptions=dictOptions)
                
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aper�u"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        self.bouton_ok.SetFocus() 

    def __set_properties(self):
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((520, 520))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_base.Add(self.ctrl_parametres, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)        
        
    def GetOptions(self):
        return self.ctrl_parametres.GetOptions() 

    def OnBoutonOk(self, event): 
        dictOptions = self.ctrl_parametres.GetOptions() 
        if dictOptions == False :
            return        
        
        # R�cup�ration des param�tres
        listeIDfactures = []
        montantTotal = 0.0 
        for track in self.tracks :
            listeIDfactures.append(track.IDfacture)
            montantTotal += -track.solde

        if len(listeIDfactures) == 0 : conditionFactures = "()"
        elif len(listeIDfactures) == 1 : conditionFactures = "(%d)" % listeIDfactures[0]
        else : conditionFactures = str(tuple(listeIDfactures))

        DB = GestionDB.DB() 
        req = """
        SELECT prestations.IDprestation, prestations.IDfacture, prestations.label, prestations.montant, 
        prestations.IDindividu, individus.nom, individus.prenom,
        prestations.IDactivite, activites.nom
        FROM prestations
        LEFT JOIN individus ON prestations.IDindividu = individus.IDindividu
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        WHERE prestations.IDfacture IN %s
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % conditionFactures
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq() 
        DB.Close() 
        dictPrestations = {}
        dictIndividus = {}
        dictActivites = {}
        dictTotaux = {}
        for IDprestation, IDfacture, label, montant, IDindividu, nom, prenom, IDactivite, nomActivite in listePrestations :

            if dictActivites != None and dictActivites.has_key(IDactivite) == False :
                dictActivites[IDactivite] = nomActivite

            if IDindividu != None and dictIndividus.has_key(IDindividu) == False and prenom != None :
                dictIndividus[IDindividu] = u"%s %s" % (nom, prenom)
            
            if dictPrestations.has_key(IDfacture) == False :
                dictPrestations[IDfacture] = {}
            if dictPrestations[IDfacture].has_key(IDindividu) == False :
                dictPrestations[IDfacture][IDindividu] = {}
            if dictPrestations[IDfacture][IDindividu].has_key(label) == False :
                dictPrestations[IDfacture][IDindividu][label] = {"quantite" : 0, "montant" : 0.0, "IDactivite" : IDactivite}
            
            if dictTotaux.has_key(IDactivite) == False :
                dictTotaux[IDactivite] = {}
            if dictTotaux[IDactivite].has_key(label) == False :
                dictTotaux[IDactivite][label] = {"quantite" : 0, "montant" : 0.0}
            
            dictTotaux[IDactivite][label]["quantite"] += 1
            dictTotaux[IDactivite][label]["montant"] += montant

            dictPrestations[IDfacture][IDindividu][label]["quantite"] += 1
            dictPrestations[IDfacture][IDindividu][label]["montant"] += montant

        # Cr�ation du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        
        # Initialisation du PDF
        PAGE_WIDTH, PAGE_HEIGHT=defaultPageSize
        nomDoc = "Temp/RECAPFACTURES%s.pdf" % FonctionsPerso.GenerationIDdoc() 
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, topMargin=30, bottomMargin=30)
        story = []
        
        largeurContenu = 520
        
        # Cr�ation du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (420, 100) )
            dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
            dataTableau.append( (dictOptions["titre_texte"], _(u"%s\nEdit� le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
            style = TableStyle([
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                    ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                    ('ALIGN', (0,0), (0,0), ConvertAlignement1(dictOptions["titre_alignement"])), 
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", dictOptions["titre_taille_texte"]), 
                    ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                    ('FONT',(1,0),(1,0), "Helvetica", 6), 
                    ])
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)
            story.append(Spacer(0, 20))       
        
        # Ins�re un header
        Header() 
        
        couleurFond1 = ConvertCouleurWXpourPDF(dictOptions["couleur_fond_1"])
        couleurFond2 = ConvertCouleurWXpourPDF(dictOptions["couleur_fond_2"])
        
        styleIntroduction = ParagraphStyle(name="introduction", fontName="Helvetica", alignment=ConvertAlignement2(dictOptions["intro_alignement"]), fontSize=dictOptions["intro_taille_texte"], spaceAfter=0, leading=8, spaceBefore=0)
        styleConclusion = ParagraphStyle(name="conclusion", fontName="Helvetica", alignment=ConvertAlignement2(dictOptions["conclusion_alignement"]), fontSize=dictOptions["conclusion_taille_texte"], spaceAfter=0, leading=8, spaceBefore=0)
        
        styleLabel = ParagraphStyle(name="label", fontName="Helvetica", alignment=1, fontSize=5, spaceAfter=0, leading=8, spaceBefore=0)
        styleTexte = ParagraphStyle(name="label", fontName="Helvetica", alignment=0, fontSize=7, spaceAfter=0, leading=8, spaceBefore=0)
        styleTexte2 = ParagraphStyle(name="label", fontName="Helvetica", alignment=1, fontSize=7, spaceAfter=0, leading=8, spaceBefore=0)
        styleMontant = ParagraphStyle(name="label", fontName="Helvetica", alignment=2, fontSize=7, spaceAfter=0, leading=8, spaceBefore=0)

        # Intro
        story.append(Paragraph(dictOptions["intro_texte"], styleIntroduction))
        story.append(Spacer(0, 20))
        
        # Factures
        if dictOptions["type_document"] in (0, 1) :
            
            for track in self.tracks :
                
                numero = track.numero
                if track.etat == "annulation" :
                    numero = u"%s (Annul�e)" % numero
                
                solde = track.solde
                if solde != 0.0 :
                    solde = -solde
                    
                # Num�ro de facture
                dataTableau = []
                largeursColonnes = [100, 100, largeurContenu-100-100]
                dataTableau.append((
                    _(u"Facture n�%s") % numero, 
                    u"%.2f %s" % (solde, SYMBOLE),
                    _(u"Edit� le %s | Ech�ance le %s | P�riode du %s au %s") % (UTILS_Dates.DateDDEnFr(track.date_edition), UTILS_Dates.DateDDEnFr(track.date_echeance), UTILS_Dates.DateDDEnFr(track.date_debut), UTILS_Dates.DateDDEnFr(track.date_fin)),
                    ))
                tableau = Table(dataTableau, largeursColonnes)
                listeStyles = [
                    ('FONT', (0, 0), (1, -1), "Helvetica-Bold", 7),
                    ('FONT', (2, -1), (2, -1), "Helvetica", 6),
                    ('BACKGROUND', (0, 0), (-1, -1), couleurFond1),
                    ('ALIGN', (2, -1), (2, -1), 'RIGHT'),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ]
                tableau.setStyle(TableStyle(listeStyles))
                story.append(tableau)
                
                # Famille
                if track.prelevement == True :
                    textePrelevement = _(u"N� Compte : %s | Etab : %s | Guichet : %s | Cl� : %s | Titulaire : %s") % (track.prelevement_numero, track.prelevement_etab, track.prelevement_guichet, track.prelevement_cle, track.prelevement_payeur)
                else :
                    textePrelevement = u""
                
                if track.adresse_famille["rue"] != None : rue = track.adresse_famille["rue"]
                else : rue = u""
                if track.adresse_famille["cp"] != None : cp = track.adresse_famille["cp"]
                else : cp = u""
                if track.adresse_famille["ville"] != None : ville = track.adresse_famille["ville"]
                else : ville = u""
                
                dataTableau = [(Paragraph(_(u"Famille"), styleLabel), Paragraph(_(u"Adresse"), styleLabel), Paragraph(_(u"Pr�l�vement bancaire"), styleLabel)),]
                largeursColonnes = [180, 140, largeurContenu-320]
                dataTableau.append((
                    Paragraph(track.nomsTitulaires, styleTexte), 
                    (Paragraph(rue, styleTexte), Paragraph(u"%s %s" % (cp, ville), styleTexte)),
                    Paragraph(textePrelevement, styleTexte),
                    ))
                tableau = Table(dataTableau, largeursColonnes)
                listeStyles = [
                    ('TOPPADDING', (0, 0), (-1, 0), 0), 
                    ('BOTTOMPADDING',(0, 0), (-1, 0), -1), 
                    ('FONT', (0, -1), (-1, -1), "Helvetica", 7),
                    ('GRID', (0, 0), (-1, 0), 0.25, colors.black),
                    ('BOX', (0, 1), (-1, 1), 0.25, colors.black),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, 0), couleurFond2),
                    ]
                tableau.setStyle(TableStyle(listeStyles))
                story.append(tableau)
                
                # D�tail des prestations
                if dictOptions["type_document"] == 0 and dictPrestations.has_key(track.IDfacture) :
                    
                    dataTableau = [(Paragraph(_(u"Individu"), styleLabel), Paragraph(_(u"Activit�"), styleLabel), Paragraph(_(u"Prestation"), styleLabel), Paragraph(_(u"Quantit�"), styleLabel), Paragraph(_(u"Montant total"), styleLabel)),]
                    largeursColonnes = [130, 120, 185, 35, 50]
                    
                    for IDindividu, dictLabels in dictPrestations[track.IDfacture].iteritems() :
                        
                        if dictIndividus.has_key(IDindividu) :
                            labelIndividu = dictIndividus[IDindividu]
                        else :
                            labelIndividu = u""

                        listeActivites = []
                        listeLabels = []
                        listeQuantites = []
                        listeMontants = []
                        for labelPrestation, dictTemp in dictLabels.iteritems() :

                            if dictTemp["IDactivite"] != None and dictActivites.has_key(dictTemp["IDactivite"]) :
                                labelActivite = dictActivites[dictTemp["IDactivite"]]
                            else :
                                labelActivite = u""
                            
                            listeActivites.append(Paragraph(labelActivite[:35], styleTexte2)) 
                            listeLabels.append(Paragraph(labelPrestation[:40], styleTexte2)) 
                            listeQuantites.append(Paragraph(str(dictTemp["quantite"]), styleTexte2)) 
                            listeMontants.append(Paragraph(u"%.2f %s" % (dictTemp["montant"], SYMBOLE), styleMontant))
                        
                        dataTableau.append((
                            Paragraph(labelIndividu, styleTexte2), 
                            listeActivites,
                            listeLabels,
                            listeQuantites,
                            listeMontants,
                            ))
                            
                    tableau = Table(dataTableau, largeursColonnes)
                    listeStyles = [
                        ('TOPPADDING', (0, 0), (-1, 0), 0), 
                        ('BOTTOMPADDING',(0, 0), (-1, 0), -1), 
                        ('FONT', (0, -1), (-1, -1), "Helvetica", 7),
                        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('BACKGROUND', (0, 0), (-1, 0), couleurFond2),
                        ]
                    tableau.setStyle(TableStyle(listeStyles))
                    story.append(tableau)
                    
                story.append(Spacer(0, 10))
        
        # Totaux        
        dataTableau = [
            (_(u"Totaux par activit�s et prestations"), "", "", ""),
            (Paragraph(_(u"Activit�s"), styleLabel), Paragraph(_(u"Prestations"), styleLabel), Paragraph(_(u"Quantit�"), styleLabel), Paragraph(_(u"Montant"), styleLabel)),
            ]
        largeursColonnes = [195, 240, 35, 50]

        for IDactivite, dictLabels in dictTotaux.iteritems() :
            
            if IDactivite == None :
                nomActivite = _(u"Prestations familiales")
            else :
                nomActivite = dictActivites[IDactivite]
                
            listeLabels = []
            listeQuantites = []
            listeMontants = []
            quantiteActivite = 0
            totalActivite = 0.0
            for label, dictTemp in dictLabels.iteritems() :
                listeLabels.append(Paragraph(label, styleTexte2)) 
                listeQuantites.append(Paragraph(str(dictTemp["quantite"]), styleTexte2)) 
                listeMontants.append(Paragraph(u"%.2f %s" % (dictTemp["montant"], SYMBOLE), styleMontant))
                quantiteActivite += dictTemp["quantite"]
                totalActivite += dictTemp["montant"]
            
            listeLabels.append(Paragraph(_(u"<b><i>Total de l'activit�</i></b>"), styleTexte2)) 
            listeQuantites.append(Paragraph("<b><i>%d</i></b>" % quantiteActivite, styleTexte2)) 
            listeMontants.append(Paragraph(u"<b><i>%.2f %s</i></b>" % (totalActivite, SYMBOLE), styleMontant))
            
            dataTableau.append((
                Paragraph(nomActivite, styleTexte2), 
                listeLabels,
                listeQuantites,
                listeMontants,
                ))

        tableau = Table(dataTableau, largeursColonnes)
        listeStyles = [
            ('TOPPADDING', (0, 1), (-1, 1), 0), 
            ('BOTTOMPADDING',(0, 1), (-1, 1), -1), 
            ('FONT', (1, -1), (-1, -1), "Helvetica", 7),
            ('FONT', (0, 0), (0, 0), "Helvetica-Bold", 7),
            ('BOX', (0, 0), (-1, 0), 0.25, colors.black),
            ('GRID', (0, 1), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), couleurFond1),
            ('BACKGROUND', (0, 1), (-1, 1), couleurFond2),
            ]
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)

        story.append(Spacer(0, 10))
        
        # Texte de conclusion
        conclusion_texte = dictOptions["conclusion_texte"]
        conclusion_texte = conclusion_texte.replace("{NBRE_FACTURES}", str(len(self.tracks)))
        conclusion_texte = conclusion_texte.replace("{TOTAL_FACTURES}", u"%.2f %s" % (montantTotal, SYMBOLE))
        story.append(Paragraph(conclusion_texte, styleConclusion))

        # Enregistrement et ouverture du PDF
        try :
            doc.build(story)
        except Exception, err :
            print "Erreur dans ouverture PDF :", err
            if "Permission denied" in err :
                dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas cr�er le PDF.\n\nVeuillez v�rifier qu'un autre PDF n'est pas d�j� ouvert en arri�re-plan..."), _(u"Erreur d'�dition"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        FonctionsPerso.LanceFichierExterne(nomDoc)



if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
