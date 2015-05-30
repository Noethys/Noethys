#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import sys
import os
import datetime
import wx.lib.colourselect as csel

import GestionDB
import CTRL_Bandeau
import OL_Releve_prestations
import FonctionsPerso
import UTILS_Titulaires
import UTILS_Envoi_email
import UTILS_Organisateur
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

COULEUR_FOND_TITRE = (0.8, 0.8, 1)

LISTE_MOIS = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + u"/" + str(textDate[5:7]) + u"/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def ConvertCouleurWXpourPDF(couleurwx=(0, 0, 0)):
    return (couleurwx[0]/255.0, couleurwx[1]/255.0, couleurwx[2]/255.0)

def ConvertCouleurPDFpourWX(couleurpdf=(0, 0, 0)):
    return (couleurpdf[0]*255.0, couleurpdf[1]*255.0, couleurpdf[2]*255.0)




class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Emetteurs", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDfamille = IDfamille
        
        # Bandeau
        intro = _(u"Vous pouvez éditer ici un état des prestations ou des factures pour la ou les périodes souhaitées.")
        titre = _(u"Edition d'un relevé des prestations")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
                
        # Périodes
        self.staticbox_periodes_staticbox = wx.StaticBox(self, -1, _(u"Périodes"))
        self.ctrl_periodes = OL_Releve_prestations.ListView(self, id=-1, IDfamille=self.IDfamille, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.check_memoriser_parametres = wx.CheckBox(self, -1, _(u"Mémoriser les périodes"))
        self.check_memoriser_parametres.SetValue(True) 
        
        self.checkbox_couleur = wx.CheckBox(self, -1, _(u"Couleur de fond de titre :"))
        self.ctrl_couleur = csel.ColourSelect(self, -1, u"", COULEUR_FOND_TITRE, size=(60, 18))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer par Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCouleur, self.checkbox_couleur)
        self.Bind(wx.EVT_BUTTON, self.OnAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        
        # Init contrôles
        couleur = UTILS_Config.GetParametre("releve_prestations_couleur", defaut=ConvertCouleurPDFpourWX(COULEUR_FOND_TITRE))
        if couleur == False :
            couleur = ConvertCouleurPDFpourWX(COULEUR_FOND_TITRE)
        else :
            self.checkbox_couleur.SetValue(True)
        self.ctrl_couleur.SetColour(couleur)

        listePeriodes = UTILS_Config.GetParametre("releve_prestations_periodes", defaut=[])
        self.ctrl_periodes.MAJ(listePeriodes)
        

    def __set_properties(self):
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter une période"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la période sélectionnée dans la liste"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la période sélectionnée dans la liste"))
        self.checkbox_couleur.SetToolTipString(_(u"Cochez cette case pour insérer une couleur"))
        self.check_memoriser_parametres.SetToolTipString(_(u"Cochez cette case pour mémoriser les périodes"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_email.SetToolTipString(_(u"Cliquez ici pour envoyer ce document par Email"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour créer un aperçu du document PDF"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((650, 400))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Périodes
        staticbox_periodes = wx.StaticBoxSizer(self.staticbox_periodes_staticbox, wx.VERTICAL)
        grid_sizer_periodes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_periodes = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_periodes.Add(self.ctrl_periodes, 1, wx.EXPAND, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_periodes.Add(grid_sizer_boutons_periodes, 1, wx.EXPAND, 0)
        grid_sizer_periodes.AddGrowableRow(0)
        grid_sizer_periodes.AddGrowableCol(0)
        staticbox_periodes.Add(grid_sizer_periodes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_periodes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Options
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=6, vgap=2, hgap=2)
        grid_sizer_options.Add(self.check_memoriser_parametres, 0, wx.EXPAND, 0)
        grid_sizer_options.Add( (20, 10), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.checkbox_couleur, 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.ctrl_couleur, 0, wx.EXPAND, 0)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_email, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnCheckCouleur(self, event): 
        if self.checkbox_couleur.GetValue() == True :
            self.ctrl_couleur.Enable(True)
        else:
            self.ctrl_couleur.Enable(False)

    def OnAjouter(self, event): 
        self.ctrl_periodes.Ajouter(None)

    def OnModifier(self, event): 
        self.ctrl_periodes.Modifier(None)

    def OnSupprimer(self, event): 
        self.ctrl_periodes.Supprimer(None)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Editerunrelevdesprestations")
    
    def OnBoutonOk(self, event): 
        self.CreationPDF()
    
    def CreationPDF(self, nomDoc="Temp/Releve_prestations.pdf", afficherDoc=True):
        dictOptionsImpression = {}
        
        # Création PDF
        listePeriodes = self.ctrl_periodes.GetListePeriodes() 
        if len(listePeriodes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez paramétrer au moins une période dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Récupère couleur fond de titre
        if self.checkbox_couleur.GetValue() == True :
            dictOptionsImpression["couleur"] = self.ctrl_couleur.GetColour()
        else :
            dictOptionsImpression["couleur"] = False
        
        # Impression
        impression = Impression(IDfamille=self.IDfamille, listePeriodes=listePeriodes, dictOptionsImpression=dictOptionsImpression)
        dictChamps = impression.CreationPDF(nomDoc, afficherDoc) 
        return dictChamps

    def OnBoutonAnnuler(self, event): 
        self.MemoriserParametres() 
        self.EndModal(wx.ID_CANCEL)
        
    def MemoriserParametres(self):
        # Couleur
        if self.checkbox_couleur.GetValue() == True :
            couleur = self.ctrl_couleur.GetColour()
        else :
            couleur = False
        UTILS_Config.SetParametre("releve_prestations_couleur", couleur)        
        # Périodes
        if self.check_memoriser_parametres.GetValue() == True :
            listePeriodes = self.ctrl_periodes.GetListePeriodes() 
            UTILS_Config.SetParametre("releve_prestations_periodes", listePeriodes)
        
    def OnBoutonEmail(self, event): 
        """ Envoi par mail """
        UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=self.IDfamille, nomDoc="Temp/Releve_prestations.pdf", categorie="releve_prestations")


class Impression():
    def __init__(self, IDfamille=None, listePeriodes=[], dictOptionsImpression={}) :
        self.IDfamille = IDfamille
        self.listePeriodes = listePeriodes
        self.dictOptionsImpression = dictOptionsImpression
        
        # Récupération des données dans la base
        self.dictTitulaires = self.GetTitulaires() 
        
        self.DB = GestionDB.DB()
        self.dictIndividus = self.GetIndividus()
        self.listePrestations = self.GetPrestations()
        self.listeFactures = self.GetFactures()
        self.DB.Close()

    
    def GetTitulaires(self):
        dictNomsTitulaires = UTILS_Titulaires.GetTitulaires([self.IDfamille,]) 
        return dictNomsTitulaires
        
    def GetIndividus(self):
        """ Récupération des individus de la famille """
        req = """
        SELECT rattachements.IDindividu, IDcivilite, nom, prenom, date_naiss
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE rattachements.IDfamille=%d
        ;""" % self.IDfamille
        self.DB.ExecuterReq(req)
        listeIndividus = self.DB.ResultatReq()  
        dictIndividus = {}
        for IDindividu, IDcivilite, nom, prenom, date_naiss in listeIndividus :
            dictIndividus[IDindividu] = {"IDcivilite":IDcivilite, "nom":nom, "prenom":prenom, "date_naiss":DateEngEnDateDD(date_naiss)}
        return dictIndividus
        
    def GetPrestations(self):
        """ Récupération de toutes les prestations de la famille """
        # Recherche des prestations de la famille
        req = """
        SELECT prestations.IDprestation, prestations.IDcompte_payeur, prestations.date, categorie, 
        label, prestations.montant, 
        prestations.IDactivite, activites.nom, activites.abrege,
        prestations.IDtarif, noms_tarifs.nom, categories_tarifs.nom, IDfacture, 
        prestations.IDindividu, prestations.IDfamille
        FROM prestations
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        LEFT JOIN tarifs ON prestations.IDtarif = tarifs.IDtarif
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        LEFT JOIN categories_tarifs ON tarifs.IDcategorie_tarif = categories_tarifs.IDcategorie_tarif
        WHERE prestations.IDfamille=%d
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date, prestations.IDindividu, prestations.label
        ;""" % self.IDfamille
        self.DB.ExecuterReq(req)
        listePrestationsTemp = self.DB.ResultatReq()  

        # Recherche des consommations de la famille
        req = """
        SELECT consommations.IDconso, consommations.IDprestation, consommations.IDunite, consommations.IDgroupe,
        consommations.heure_debut, consommations.heure_fin,
        unites.nom, unites.abrege
        FROM consommations
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        LEFT JOIN unites ON unites.IDunite = consommations.IDunite
        WHERE comptes_payeurs.IDfamille=%d
        ORDER BY unites.ordre
        ;""" % self.IDfamille
        self.DB.ExecuterReq(req)
        listeConsommationsTemp = self.DB.ResultatReq()  
        dictConsommations = {}
        for IDconso, IDprestation, IDunite, IDgroupe, heure_debut, heure_fin, nomUnite, abregeUnite in listeConsommationsTemp :
            dictTemp = {
                "IDconso" : IDconso, "IDunite" : IDunite, "IDgroupe" : IDgroupe, 
                "heure_debut" : heure_debut, "heure_fin" : heure_fin, 
                "nomUnite" : nomUnite, "abregeUnite" : abregeUnite,
                }
            if dictConsommations.has_key(IDprestation) == False :
                dictConsommations[IDprestation] = []
            dictConsommations[IDprestation].append(dictTemp)
        
        # Recherche de la ventilation des prestations de la famille
        req = """
        SELECT ventilation.IDprestation, SUM(ventilation.montant) AS montant_ventilation
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN activites ON prestations.IDactivite = activites.IDactivite
        WHERE prestations.IDfamille=%d
        GROUP BY prestations.IDprestation
        ORDER BY prestations.date
        ;""" % self.IDfamille
        self.DB.ExecuterReq(req)
        listeVentilationPrestations = self.DB.ResultatReq()  
        dictVentilationPrestations = {}
        for IDprestation, montant_ventilation in listeVentilationPrestations :
            dictVentilationPrestations[IDprestation] = montant_ventilation
        
        listePrestations = []
        for IDprestation, IDcompte_payeur, date, categorie, label, montant, IDactivite, nomActivite, abregeActivite, IDtarif, nomTarif, nomCategorieTarif, IDfacture, IDindividu, IDfamille in listePrestationsTemp :
            
            if dictVentilationPrestations.has_key(IDprestation) :
                montant_ventilation = dictVentilationPrestations[IDprestation]
            else :
                montant_ventilation = 0.0
            
            if dictConsommations.has_key(IDprestation) :
                listeConsommations = dictConsommations[IDprestation]
            else :
                listeConsommations = []
            
            dictTemp = {
                "IDprestation" : IDprestation,
                "IDcompte_payeur" : IDcompte_payeur,
                "date" : DateEngEnDateDD(date),
                "categorie" : categorie,
                "label" : label,
                "montant" : montant,
                "IDactivite" : IDactivite,
                "nomActivite" : nomActivite,
                "abregeActivite" : abregeActivite,
                "IDtarif" : IDtarif,
                "nomTarif" : nomTarif,
                "nomCategorieTarif" : nomCategorieTarif,
                "IDfacture" : IDfacture,
                "IDindividu" : IDindividu,
                "IDfamille" : IDfamille,
                "montant_ventilation" : montant_ventilation,
                "liste_consommations" : listeConsommations,
                }
            listePrestations.append(dictTemp)
            
        return listePrestations
    
    def GetFactures(self):
        """ Récupération des factures de la famille """
        # Récupération des factures
        req = """
        SELECT factures.IDfacture, factures.numero, factures.IDcompte_payeur, 
        factures.date_edition, factures.date_echeance, factures.IDutilisateur,
        factures.date_debut, factures.date_fin, factures.total, factures.regle, factures.solde,
        comptes_payeurs.IDfamille
        FROM factures
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = factures.IDcompte_payeur
        WHERE comptes_payeurs.IDfamille=%d
        ORDER BY factures.date_edition
        ;""" % self.IDfamille
        self.DB.ExecuterReq(req)
        listeFacturesTemp = self.DB.ResultatReq()
                
        listeFactures = []
        for IDfacture, numero, IDcompte_payeur, date_edition, date_echeance, IDutilisateur, date_debut, date_fin, total, regle, solde, IDfamille in listeFacturesTemp :
            if numero == None : numero = 0
            date_edition = DateEngEnDateDD(date_edition) 
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            date_echeance = DateEngEnDateDD(date_echeance)     
            
            # Recherche des prestations de la facture
            totalPrestations = 0.0
            totalVentilation = 0.0
            listePrestations = []
            for dictPrestation in self.listePrestations :
                if dictPrestation["IDfacture"] == IDfacture :
                    listePrestations.append(dictPrestation)
                    totalPrestations += dictPrestation["montant"]
                    totalVentilation += dictPrestation["montant_ventilation"]

            dictTemp = {
                "IDfacture" : IDfacture, "numero" : numero, "IDcompte_payeur" : IDcompte_payeur, "date_edition" : date_edition, "date_echeance" : date_echeance,
                "IDutilisateur" : IDutilisateur, "date_debut" : date_debut, "date_fin" : date_fin, "total" : total, "regle" : regle, "solde" : solde, 
                "totalPrestations" : totalPrestations, "totalVentilation" : totalVentilation, "listePrestations" : listePrestations, "IDfamille" : IDfamille,
                }
            listeFactures.append(dictTemp)
        
        return listeFactures

    def CreationPDF(self, nomDoc="Temp/Releve_prestations.pdf", afficherDoc=True):
        """ Création du PDF """
        from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, NextPageTemplate
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.platypus.frames import Frame, ShowBoundaryValue
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch, cm, mm
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfgen.canvas import Canvas

        TAILLE_PAGE = A4
        LARGEUR_PAGE = TAILLE_PAGE[0]
        HAUTEUR_PAGE = TAILLE_PAGE[1]
        
        # Initialisation du document
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, topMargin=30, bottomMargin=30, pagesize=TAILLE_PAGE, showBoundary=False)
        story = []
        dictChampsFusion = {}
        
        largeurContenu = 520
        
        # Recherche la couleur de titre
        couleur_fond_titre = ConvertCouleurWXpourPDF((255, 255, 255))
        if self.dictOptionsImpression.has_key("couleur") :
            if self.dictOptionsImpression["couleur"] != False :
                couleur_fond_titre = ConvertCouleurWXpourPDF(self.dictOptionsImpression["couleur"])

        paraStyleTitre = ParagraphStyle(name="titre",
                              fontName="Helvetica-Bold",
                              fontSize=12,
                              #leading=7,
                              spaceBefore=0,
                              spaceafter=0,
                            )

        paraStyle = ParagraphStyle(name="compte",
                              fontName="Helvetica",
                              fontSize=9,
                              #leading=7,
                              spaceBefore=5,
                              spaceafter=0,
                            )
        
        titreDocument = Paragraph(_(u"Relevé des prestations"), paraStyleTitre)
        texteTitulaire = Paragraph(u"%s" % self.dictTitulaires[self.IDfamille]["titulairesSansCivilite"], paraStyle)
        
        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (420, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dictChampsFusion["{DATE_EDITION_RELEVE}"] = dateDuJour
        dataTableau.append( ([titreDocument, texteTitulaire], _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        
        # Nom du compte
##        texteTitulaire = Paragraph(_(u"Compte de %s") % self.dictTitulaires[self.IDfamille]["titulairesSansCivilite"], paraStyle)
##        dataTableau = []
##        largeursColonnes = ( (520,) )
##        dataTableau.append([texteTitulaire,])
##        style = TableStyle([
####                ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
##                ('VALIGN', (0,0), (-1,-1), 'TOP'), 
##                ('ALIGN', (0,0), (0,0), 'LEFT'), 
##                ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
##                ('FONT',(0,0),(0,0), "Helvetica", 6), 
##                ])
##        tableau = Table(dataTableau, largeursColonnes)
##        tableau.setStyle(style)
##        story.append(tableau)
##        story.append(Spacer(0,20))       
        
        # Création des périodes
        total_reste_global = 0.0 
        dictPrestationsAffichees = {}
        
        for periode in self.listePeriodes :
            if periode["selection"] == True :
                
                # Récupération des paramètres de la période
                typeDonnees = periode["type"]
                dictPeriode = periode["periode"]
                dictOptions = periode["options"]
                
                date_debut = dictPeriode["date_debut"]
                date_fin = dictPeriode["date_fin"]

                # Impayés
                if dictOptions.has_key("impayes") and dictOptions["impayes"] == True :
                    impayes = True
                else :
                    impayes = False               


                # -------------------------------------------------------------------------------------------------------
                # ----------------------------------------- PRESTATIONS ---------------------------------------
                # -------------------------------------------------------------------------------------------------------
                
                if typeDonnees == "prestations" :
                    
                    # Regroupement
                    modeRegroupement = "date"
                    if dictOptions.has_key("regroupement") and dictOptions["regroupement"] != None :
                        modeRegroupement = dictOptions["regroupement"]
                        detail = False
                    else :
                        detail = True
                        
                    if modeRegroupement == "date" : labelRegroupement = _(u"Date")
                    if modeRegroupement == "mois" : labelRegroupement = _(u"Mois")
                    if modeRegroupement == "annee" : labelRegroupement = _(u"Année")
                    
                    # Affichage des conso
                    if dictOptions.has_key("conso") and dictOptions["conso"] == True :
                        modeConso = True
                    else :
                        modeConso = False
                    
                    # Dessin du tableau de titre pour cette période
                    dataTableau = []
                    if impayes == True :
                        labelTitre = _(u"Prestations impayées - %s") % dictPeriode["label"]
                    else :
                        labelTitre = _(u"Prestations - %s") % dictPeriode["label"]
                    dataTableau.append([labelTitre,])

                    listeStyles = [
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('GRID', (0, 0), (-1,-1), 0.25, colors.black), 
                        ('FONT', (0, 0), (-1, -1), "Helvetica", 9), 
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONT', (0, 1), (-1, -1), "Helvetica", 8), 
                        ('BACKGROUND', (-1, -1), (-1, -1), couleur_fond_titre), 
                        ]

                    tableau_titre = Table(dataTableau, [520,])
                    tableau_titre.setStyle(TableStyle(listeStyles))

                    # Dessin du tableau pour les prestations
                    dataTableau = []
                    if detail == True :
                        largeursColonnes = [60, 190, 120, 50, 50, 50]
                        dataTableau.append([labelRegroupement, _(u"Prestation"), _(u"Individu"), _(u"Total dû"), _(u"Réglé"), _(u"Reste dû")])
                    else :
                        largeursColonnes = [370, 50, 50, 50]
                        dataTableau.append([labelRegroupement, _(u"Total dû"), _(u"Réglé"), _(u"Reste dû")])
                    paraStyle = ParagraphStyle(name="standard",
                              fontName="Helvetica",
                              fontSize=8,
                              leading=10,
                              #spaceBefore=8,
                              spaceAfter=0,
                            )
                    
                    total_du = 0.0
                    total_regle = 0.0
                    total_reste = 0.0
                                        
                    # Regroupement
                    dictRegroupement = {}
                    for dictPrestation in self.listePrestations :
                        valide = True
                        
                        date = dictPrestation["date"]
                        montant = dictPrestation["montant"]
                        montant_ventilation = dictPrestation["montant_ventilation"]
                        reste_du = montant - montant_ventilation
                            
                        # Filtre impayes
                        if impayes == True and reste_du <= 0.0 :
                            valide = False
                        
                        # Filtre Date
                        if date < date_debut or date > date_fin :
                            valide = False
                            
                        if valide == True :
                            # Création de la Key de regroupement
                            if modeRegroupement == "date" :
                                key = date
                            if modeRegroupement == "mois" :
                                key = (date.year, date.month)
                            if modeRegroupement == "annee" :
                                key = date.year
                            
                            # Mémorisation
                            if dictRegroupement.has_key(key) == False :
                                dictRegroupement[key] = []
                            dictRegroupement[key].append(dictPrestation)
                    
                    # Tri des keys
                    listeKeys = dictRegroupement.keys()
                    listeKeys.sort() 
                    
                    # Parcours des éléments
                    for key in listeKeys :
                        listeLigne = []

                        # Key
                        if type(key) == datetime.date : labelKey = DateEngFr(str(key))
                        if type(key) == tuple : labelKey = u"%s %d" % (LISTE_MOIS[key[1]-1], key[0])
                        if type(key) == int : labelKey = _(u"Année %d") % key
                        texteKey = Paragraph(u"<para align='center'>%s</para>" % labelKey, paraStyle)
                        
                        listeLabels = []
                        listeIndividus = []
                        listeTotalDu = []
                        listeTotalRegle = []
                        listeTotalReste = []
                        
                        total_du_groupe = 0.0
                        total_regle_groupe = 0.0
                        total_reste_groupe = 0.0
                        
                        # Détail
                        for dictPrestation in dictRegroupement[key] :
                            
                            # Calcul des montants
                            montant = dictPrestation["montant"]
                            montant_ventilation = dictPrestation["montant_ventilation"]
                            reste_du = montant - montant_ventilation
                                
                            # Label de la prestation
                            labelPrestation = dictPrestation["label"]
                            if modeConso == True :
                                liste_consommations = dictPrestation["liste_consommations"]
                                if len(liste_consommations) > 0 :
                                    listeConsoTemp = []
                                    doublons = False
                                    for dictConso in liste_consommations:
                                        nomUnite = dictConso["abregeUnite"]
                                        if nomUnite in listeConsoTemp :
                                            doublons = True
                                        listeConsoTemp.append(nomUnite)
                                    if len(listeConsoTemp) > 0 and doublons == False :
                                        labelPrestation = u"%s (%s)" % (labelPrestation, u"+".join(listeConsoTemp))
                                    
                            listeLabels.append(Paragraph(labelPrestation, paraStyle))

                            # Individu
                            if dictPrestation["IDindividu"] != None and dictPrestation["IDindividu"] != 0 :
                                texteIndividu = self.dictIndividus[dictPrestation["IDindividu"]]["prenom"]
                            else :
                                texteIndividu = u"-"
                            listeIndividus.append(Paragraph(texteIndividu, paraStyle))

                            # Total dû
                            listeTotalDu.append(Paragraph(u"<para align='right'>%.02f %s</para>" % (montant, SYMBOLE), paraStyle))
                            total_du += montant
                            total_du_groupe += montant

                            # Réglé
                            listeTotalRegle.append(Paragraph(u"<para align='right'>%.02f %s</para>" % (montant_ventilation, SYMBOLE), paraStyle))
                            total_regle += montant_ventilation
                            total_regle_groupe += montant_ventilation
                            
                            # Reste dû
                            listeTotalReste.append(Paragraph(u"<para align='right'>%.02f %s</para>" % (reste_du, SYMBOLE), paraStyle))
                            total_reste += reste_du
                            total_reste_groupe += reste_du
                            total_reste_global += reste_du
                            
                            IDprestation = dictPrestation["IDprestation"]
                            if dictPrestationsAffichees.has_key(IDprestation) == False :
                                dictPrestationsAffichees[IDprestation] = 0
                            dictPrestationsAffichees[IDprestation] += 1
                            
                        # Si détails ou non
                        if detail == True :
                            dataTableau.append([texteKey, listeLabels, listeIndividus, listeTotalDu, listeTotalRegle, listeTotalReste])
                        else :
                            dataTableau.append([
                                    texteKey,
                                    Paragraph(u"<para align='right'>%.02f %s</para>" % (total_du_groupe, SYMBOLE), paraStyle),
                                    Paragraph(u"<para align='right'>%.02f %s</para>" % (total_regle_groupe, SYMBOLE), paraStyle),
                                    Paragraph(u"<para align='right'>%.02f %s</para>" % (total_reste_groupe, SYMBOLE), paraStyle),
                                    ])
                            

                    listeStyles = [
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1,-1), 0.25, colors.black), 
                        ('FONT', (0, 0), (-1, 0), "Helvetica", 6), 
                        ('ALIGN', (0, 0), (-1, 0), 'CENTRE'),
                        ('FONT', (0, 1), (-1, 1), "Helvetica", 8), 
                        ]
                    
                    if len(dataTableau) > 1 :

                        story.append(tableau_titre)

                        tableau = Table(dataTableau, largeursColonnes)
                        tableau.setStyle(TableStyle(listeStyles))
                        story.append(tableau)


                        # Insertion du total par période
                        dataTableau = []
                        listeLigne = [
                            Paragraph(_(u"<para align='right'>Totaux :</para>"), paraStyle),
                            Paragraph(u"<para align='right'>%.02f %s</para>" % (total_du, SYMBOLE), paraStyle),
                            Paragraph(u"<para align='right'>%.02f %s</para>" % (total_regle, SYMBOLE), paraStyle),
                            Paragraph(u"<para align='right'><b>%.02f %s</b></para>" % (total_reste, SYMBOLE), paraStyle),
                            ]
                        dataTableau.append(listeLigne)
                        
                        listeStyles = [
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('FONT', (0, 0), (-1, -1), "Helvetica", 8), 
                                ('GRID', (1, -1), (-1,-1), 0.25, colors.black), 
                                ('ALIGN', (-1, -1), (-1, -1), 'CENTRE'),
                                ('BACKGROUND', (-1, 0), (-1, -1), couleur_fond_titre), 
                                ]
                            
                        # Création du tableau
                        largeursColonnesTotal = [370, 50 , 50, 50]
                        tableau = Table(dataTableau, largeursColonnesTotal)
                        tableau.setStyle(TableStyle(listeStyles))
                        story.append(tableau)
                        story.append(Spacer(0, 12))


                # -------------------------------------------------------------------------------------------------------
                # ----------------------------------------- FACTURES --------------------------------------------
                # -------------------------------------------------------------------------------------------------------

                if typeDonnees == "factures" :                    
                    
                    # Dessin du tableau de titre pour cette période
                    dataTableau = []
                    if impayes == True :
                        labelTitre = _(u"Factures impayées - %s") % dictPeriode["label"]
                    else :
                        labelTitre = _(u"Factures - %s") % dictPeriode["label"]
                    dataTableau.append([labelTitre,])

                    listeStyles = [
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('GRID', (0, 0), (-1,-1), 0.25, colors.black), 
                        ('FONT', (0, 0), (-1, -1), "Helvetica", 9), 
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONT', (0, 1), (-1, -1), "Helvetica", 8), 
                        ('BACKGROUND', (-1, -1), (-1, -1), couleur_fond_titre), 
                        ]

                    tableau_titre = Table(dataTableau, [520,])
                    tableau_titre.setStyle(TableStyle(listeStyles))

                    # Dessin du tableau pour les prestations
                    dataTableau = []
                    largeursColonnes = [60, 110, 200, 50, 50, 50]
                    dataTableau.append([_(u"Date d'édition"), _(u"Numéro"), _(u"Période"), _(u"Total dû"), _(u"Réglé"), _(u"Reste dû")])
                    
                    paraStyle = ParagraphStyle(name="standard",
                              fontName="Helvetica",
                              fontSize=8,
                              leading=10,
                              #spaceBefore=8,
                              spaceAfter=0,
                            )
                    
                    total_du = 0.0
                    total_regle = 0.0
                    total_reste = 0.0
                                        
                    for dictFacture in self.listeFactures :
                        valide = True
                        
                        date = dictFacture["date_edition"]
                        montant = dictFacture["totalPrestations"]
                        montant_ventilation = dictFacture["totalVentilation"]
                        reste_du = montant - montant_ventilation
                            
                        # Filtre impayes
                        if impayes == True and reste_du <= 0.0 :
                            valide = False
                        
                        # Filtre Date
                        if date < date_debut or date > date_fin :
                            valide = False
                            
                        if valide == True :
                            
                            listeLigne = []
                            
                            # Date d'édition
                            listeLigne.append(Paragraph(u"<para align='center'>%s</para>" % DateEngFr(str(date)), paraStyle))

                            # Numéro de facture
                            listeLigne.append(Paragraph(_(u"Facture n°%s") % dictFacture["numero"], paraStyle))

                            # Période facture
                            listeLigne.append(Paragraph(_(u"Du %s au %s") % (DateEngFr(str(dictFacture["date_debut"])), DateEngFr(str(dictFacture["date_fin"]))), paraStyle))

                            # Total dû
                            listeLigne.append(Paragraph(u"<para align='right'>%.02f %s</para>" % (montant, SYMBOLE), paraStyle))
                            total_du += montant

                            # Réglé
                            listeLigne.append(Paragraph(u"<para align='right'>%.02f %s</para>" % (montant_ventilation, SYMBOLE), paraStyle))
                            total_regle += montant_ventilation
                            
                            # Reste dû
                            listeLigne.append(Paragraph(u"<para align='right'>%.02f %s</para>" % (reste_du, SYMBOLE), paraStyle))
                            total_reste += reste_du
                            total_reste_global += reste_du
                            
                            for dictPrestation in dictFacture["listePrestations"] :
                                IDprestation = dictPrestation["IDprestation"]
                                if dictPrestationsAffichees.has_key(IDprestation) == False :
                                    dictPrestationsAffichees[IDprestation] = 0
                                dictPrestationsAffichees[IDprestation] += 1

                            dataTableau.append(listeLigne)

                    listeStyles = [
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1,-1), 0.25, colors.black), 
                        ('FONT', (0, 0), (-1, 0), "Helvetica", 6), 
                        ('ALIGN', (0, 0), (-1, 0), 'CENTRE'),
                        ('FONT', (0, 1), (-1, 1), "Helvetica", 8), 
                        ]
                    
                    if len(dataTableau) > 1 :
                        
                        story.append(tableau_titre)
                        
                        tableau = Table(dataTableau, largeursColonnes)
                        tableau.setStyle(TableStyle(listeStyles))
                        story.append(tableau)


                        # Insertion du total par période
                        dataTableau = []
                        listeLigne = [
                            Paragraph(_(u"<para align='right'>Totaux :</para>"), paraStyle),
                            Paragraph(u"<para align='right'>%.02f %s</para>" % (total_du, SYMBOLE), paraStyle),
                            Paragraph(u"<para align='right'>%.02f %s</para>" % (total_regle, SYMBOLE), paraStyle),
                            Paragraph(u"<para align='right'><b>%.02f %s</b></para>" % (total_reste, SYMBOLE), paraStyle),
                            ]
                        dataTableau.append(listeLigne)
                        
                        listeStyles = [
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('FONT', (0, 0), (-1, -1), "Helvetica", 8), 
                                ('GRID', (1, -1), (-1,-1), 0.25, colors.black), 
                                ('ALIGN', (-1, -1), (-1, -1), 'CENTRE'),
                                ('BACKGROUND', (-1, 0), (-1, -1), couleur_fond_titre), 
                                ]
                            
                        # Création du tableau
                        largeursColonnesTotal = [370, 50 , 50, 50]
                        tableau = Table(dataTableau, largeursColonnesTotal)
                        tableau.setStyle(TableStyle(listeStyles))
                        story.append(tableau)
                        story.append(Spacer(0, 12))


            
        # ---------------------------- Insertion du total du document ---------------------------
        dataTableau = []
        listeLigne = [
            Paragraph(_(u"<para align='right'><b>Reste dû :</b></para>"), paraStyle),
            Paragraph(u"<para align='right'><b>%.02f %s</b></para>" % (total_reste_global, SYMBOLE), paraStyle),
            ]
        dataTableau.append(listeLigne)
        
        dictChampsFusion["{RESTE_DU}"] = u"%.02f %s" % (total_reste_global, SYMBOLE)
        
        listeStyles = [
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONT', (0, 0), (-1, -1), "Helvetica", 8), 
                ('GRID', (1, -1), (-1,-1), 0.25, colors.black), 
                ('ALIGN', (-1, -1), (-1, -1), 'CENTRE'),
                ('BACKGROUND', (-1, 0), (-1, -1), couleur_fond_titre), 
                ]
            
        # Création du tableau
        largeursColonnesTotal = [370, 150]
        tableau = Table(dataTableau, largeursColonnesTotal)
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)
        story.append(Spacer(0, 12))
        
        # Vérifie que des prestations ne sont pas présentes dans plusieurs périodes :
        nbreDoublons = 0
        for IDprestation, nbre in dictPrestationsAffichees.iteritems() :
            if nbre > 1 :
                nbreDoublons += 1
        if nbreDoublons > 0 :
            if nbreDoublons == 1 : 
                texte = _(u"Une prestation apparaît simultanément dans plusieurs périodes. Vérifiez votre paramétrage des périodes !")
            else :
                texte = _(u"%d prestations apparaissent simultanément dans plusieurs périodes. Vérifiez votre paramétrage des périodes !") % nbreDoublons
            dlg = wx.MessageDialog(None, texte, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
            
        
        # Enregistrement et ouverture du PDF
        try :
            doc.build(story)
        except Exception, err :
            print "Erreur dans ouverture PDF :", err
            if "Permission denied" in err :
                dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas créer le PDF.\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."), _(u"Erreur d'édition"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        # Affichage du PDF
        if afficherDoc == True :
            FonctionsPerso.LanceFichierExterne(nomDoc)

        # Renvoie les champs pour fusion Email
        return dictChampsFusion
        
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    
##    imp = Impression(IDfamille=11)
    
    dialog_1 = Dialog(None, IDfamille=5)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
