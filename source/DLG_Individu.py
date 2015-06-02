#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.html as html
import GestionDB
import UTILS_Historique
import UTILS_Utilisateurs
import datetime

import CTRL_Photo
import DLG_Individu_informations
import DLG_Individu_identite
import DLG_Individu_coords
import DLG_Individu_liens
import DLG_Individu_pieces
import DLG_Individu_medical
import DLG_Individu_inscriptions
import DLG_Individu_questionnaire
import DLG_Individu_scolarite
import DLG_Individu_transports


##import wx.html

##class ResumeHtml(wx.html.HtmlWindow):
##    def __init__(self, parent, id=-1):
##        wx.html.HtmlWindow.__init__(self, parent, id)
##        if "gtk2" in wx.PlatformInfo:
##            self.SetStandardFonts()
##        # Fond transparent
##        self.couleurFond = wx.SystemSettings.GetColour(30)
##        self.SetBackgroundColour(self.couleurFond)
##    
##    def SetContenuHtml(self, texte=""):
##        self.SetPage(texte)
##        self.SetBackgroundColour(self.couleurFond)
##
##    def OnLinkClicked(self, link):
##        print link.GetHref()


class CTRL_header_rattachement(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=32,  couleurFond=(255, 255, 255)):
        html.HtmlWindow.__init__(self, parent, -1)#, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        self.couleurFond = couleurFond
        font = self.parent.GetFont()
        self.SetFont(font)
        self.SetLabel(texte)
    
    def SetLabel(self, texte=""):
        self.SetPage(u"""<BODY TEXT='#B2B2B2' LINK='#B2B2B2' VLINK='#B2B2B2' ALINK='#B2B2B2'><FONT SIZE=1 COLOR='#B2B2B2'>%s</FONT></BODY>""" % texte)
        self.SetBackgroundColour(self.couleurFond)
    
    def OnLinkClicked(self, linkinfo):
        IDfamille = int(linkinfo.GetHref())



class Notebook(wx.Notebook):
    def __init__(self, parent, id=-1, IDindividu=None, dictFamillesRattachees=[]):
        wx.Notebook.__init__(self, parent, id, name="notebook_individu", style= wx.BK_DEFAULT | wx.NB_MULTILINE) 
        self.IDindividu = IDindividu
        self.dictFamillesRattachees = dictFamillesRattachees
        self.dictPages = {}
        
        listePages = [
            ("informations", _(u"Informations"), u"DLG_Individu_informations.Panel(self, IDindividu=IDindividu, dictFamillesRattachees=dictFamillesRattachees)", "Information.png"),
            ("identite", _(u"Identité"), u"DLG_Individu_identite.Panel_identite(self, IDindividu=IDindividu)", "Identite.png"),
            ("liens", _(u"Liens"), u"DLG_Individu_liens.Panel_liens(self, IDindividu=IDindividu)", "Famille.png"),
            ("questionnaire", _(u"Questionnaire"), u"DLG_Individu_questionnaire.Panel(self, IDindividu=IDindividu)", "Questionnaire.png"),
            ("coords", _(u"Coordonnées"), u"DLG_Individu_coords.Panel_coords(self, IDindividu=IDindividu)", "Maison.png"),
            ("activites", _(u"Activités"), u"DLG_Individu_inscriptions.Panel(self, IDindividu=IDindividu, dictFamillesRattachees=dictFamillesRattachees)", "Activite.png"),
            ("scolarite", _(u"Scolarité"), u"DLG_Individu_scolarite.Panel(self, IDindividu=IDindividu, dictFamillesRattachees=dictFamillesRattachees)", "Classe.png"),
            ("pieces", _(u"Pièces"), u"DLG_Individu_pieces.Panel(self, IDindividu=IDindividu, dictFamillesRattachees=dictFamillesRattachees)", "Dupliquer.png"),
            ("transports", _(u"Transports"), u"DLG_Individu_transports.Panel(self, IDindividu=IDindividu, dictFamillesRattachees=dictFamillesRattachees)", "Transport.png"),
            ("medical", _(u"Médical"), u"DLG_Individu_medical.Panel(self, IDindividu=IDindividu)", "Medical.png"),
            ]
            
        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in listePages :
            exec("self.img%d = il.Add(wx.Bitmap('Images/16x16/%s', wx.BITMAP_TYPE_PNG))" % (index, imgPage))
            index += 1
        self.AssignImageList(il)

        # Création des pages
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in listePages :
            exec("self.page%d = %s" % (index, ctrlPage))
            exec("self.AddPage(self.page%d, u'%s')" % (index, labelPage))
            exec("self.SetPageImage(%d, self.img%d)" % (index, index))
            exec("self.dictPages['%s'] = {'ctrl' : self.page%d, 'index' : %d}" % (codePage, index, index))
            index += 1
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]["ctrl"]
    
    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)

    def OnPageChanged(self, event):
        """ Quand une page du notebook est sélectionnée """
        if event.GetOldSelection()==-1: return
        indexPage = event.GetSelection()
        page = self.GetPage(indexPage)
        self.Freeze()
        page.MAJ() 
        self.Thaw()
        event.Skip()



class Dialog(wx.Dialog):
    def __init__(self, parent, IDindividu=None, dictInfosNouveau={}):
        wx.Dialog.__init__(self, parent, id=-1, name="fiche_individu", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.IDindividu = IDindividu
        self.dictInfosNouveau = dictInfosNouveau
        self.nouvelleFiche = False

        # Adapte taille Police pour Linux
        import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        if IDindividu == None and len(self.dictInfosNouveau) > 0 :
            self.nouvelleFiche = True
            # Création de l'IDindividu
            self.CreateIDindividu()
            # Création du rattachement à la famille
            self.RattacherIndividu(self.dictInfosNouveau["IDfamille"], self.dictInfosNouveau["IDcategorie"], self.dictInfosNouveau["titulaire"])
        
        # Recherche des familles rattachées
        if self.IDindividu != None :
            self.dictFamillesRattachees = self.GetFamillesRattachees()
        else:
            self.dictFamillesRattachees = {}
        
        self.ctrl_ID = wx.StaticText(self, -1, _(u"Rattaché à aucune famille | ID : %d") % self.IDindividu)
        self.ctrl_ligne = wx.StaticLine(self, -1)
        self.ctrl_nom = wx.StaticText(self, -1, _(u"NOM, Prénom"))
        self.ctrl_datenaiss = wx.StaticText(self, -1, _(u"Date de naissance inconnue"))
        self.ctrl_adresse = wx.StaticText(self, -1, _(u"Lieu de résidence inconnu"))
        couleurFond = self.ctrl_adresse.GetBackgroundColour() #wx.SystemSettings.GetColour(30)
        self.ctrl_liens = CTRL_header_rattachement(self, couleurFond=couleurFond) #wx.StaticText(self, -1, _(u"Aucun rattachement"))
        self.ctrl_photo = CTRL_Photo.CTRL_Photo(self, style=wx.SUNKEN_BORDER)
        self.ctrl_photo.SetPhoto(IDindividu=None, nomFichier="Images/128x128/Personne.png", taillePhoto=(128, 128), qualite=100)
        self.ctrl_notebook = Notebook(self, IDindividu=self.IDindividu, dictFamillesRattachees=self.dictFamillesRattachees)

        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
##        # Importation des données
##        if self.nouvelleFiche == False :
##            listePages = ("identite", "coords")
##            for codePage in listePages :
##                self.ctrl_notebook.GetPage(codePage).MAJ()
        
        # Saisie des infos par défaut pour la nouvelle fiche
        if self.nouvelleFiche == True :
            pageIdentite = self.ctrl_notebook.GetPageAvecCode("identite")
            pageIdentite.SetValeursDefaut(
                self.dictInfosNouveau["nom"],
                self.dictInfosNouveau["prenom"],
                self.dictInfosNouveau["IDcategorie"],
                )
            pageIdentite.majEffectuee = True
            # Si c'est un nouveau contact, on se met sur adresse manuelle
            if self.dictInfosNouveau["IDcategorie"] == 3 : 
                pageCoords = self.ctrl_notebook.GetPageAvecCode("coords")
                pageCoords.radio_adresse_manuelle.SetValue(True)
                pageCoords.OnRadioAdresse(None)
            # On met à jour les pages spéciales autre que "Identité"
            listePages = ("liens", "coords")
            for codePage in listePages :
                page = self.ctrl_notebook.GetPageAvecCode(codePage)
                page.MAJ() 
                page.majEffectuee = True
        
##        # Remplissage de la page des liens
##        self.ctrl_notebook.GetPageAvecCode("liens").MAJ()
        
        self.ctrl_notebook.GetPageAvecCode("identite").MAJ()
        
        # Mise à jour du header
        self.MAJtexteRattachementHeader() 
        
        # MAJ de l'onglet Informations
        self.ctrl_notebook.GetPageAvecCode("informations").MAJ() 
        
        
        
    def __set_properties(self):
        if self.IDindividu != None :
            self.SetTitle(_(u"Fiche individuelle n°%d") % self.IDindividu)
        self.ctrl_ID.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.ctrl_nom.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.ctrl_photo.SetToolTipString(_(u"Cliquez sur le bouton droit de la souris\npour accéder aux outils photo"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_outils.SetToolTipString(_(u"Cliquez ici pour accéder aux outils"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider et fermer la fiche"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler la\nsaisie et fermer la fiche"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_header = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_header_gauche = wx.FlexGridSizer(rows=7, cols=1, vgap=0, hgap=0)
        grid_sizer_header_gauche.Add(self.ctrl_ID, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_header_gauche.Add(self.ctrl_ligne, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        grid_sizer_header_gauche.Add(self.ctrl_nom, 0, wx.EXPAND|wx.BOTTOM, 10)
        grid_sizer_header_gauche.Add(self.ctrl_datenaiss, 0, wx.EXPAND, 0)
        grid_sizer_header_gauche.Add(self.ctrl_adresse, 0, wx.EXPAND, 0)
        grid_sizer_header_gauche.Add((5, 10), 0, wx.EXPAND, 0)
        grid_sizer_header_gauche.Add(self.ctrl_liens, 0, wx.EXPAND, 0)
        grid_sizer_header_gauche.AddGrowableCol(0)
        grid_sizer_header.Add(grid_sizer_header_gauche, 1, wx.EXPAND, 0)
        grid_sizer_header.Add(self.ctrl_photo, 0, 0, 0)
        grid_sizer_header.AddGrowableRow(0)
        grid_sizer_header.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_header, 1, wx.RIGHT|wx.LEFT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_notebook, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        grid_sizer_base.Fit(self)
        self.SetMinSize(self.GetSize())
        self.CentreOnScreen()

    def Set_Header(self, nomLigne="", texte=""):
        """ Met à jour les lignes du header """
        # nomLigne = ID | nom | datenaiss | adresse | liens
        if nomLigne == "ID" : self.ctrl_ID.SetLabel(texte)
        if nomLigne == "nom" : self.ctrl_nom.SetLabel(texte)
        if nomLigne == "datenaiss" : self.ctrl_datenaiss.SetLabel(texte)
        if nomLigne == "adresse" : self.ctrl_adresse.SetLabel(texte)
        if nomLigne == "liens" : self.ctrl_liens.SetLabel(texte)
    
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Laficheindividuelle")

    def OnBoutonAnnuler(self, event):
        self.Annuler()

    def OnBoutonOutils(self, event):
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Edition d'étiquettes et de badges
        item = wx.MenuItem(menuPop, 30, _(u"Edition d'étiquettes et de badges"))
        bmp = wx.Bitmap("Images/16x16/Etiquette2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuEditionEtiquettes, id=30)
        
        menuPop.AppendSeparator() 

        # Item Historique
        item = wx.MenuItem(menuPop, 10, _(u"Historique"))
        bmp = wx.Bitmap("Images/16x16/Historique.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuHistorique, id=10)

        # Item Chronologie
        item = wx.MenuItem(menuPop, 20, _(u"Chronologie"))
        bmp = wx.Bitmap("Images/16x16/Timeline.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuChronologie, id=20)
                
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def OnClose(self, event):
        self.Annuler()

    def OnBoutonOk(self, event):
        # Validation des données avant sauvegarde
        listePages = ("identite", "liens", "questionnaire", "coords")
        for codePage in listePages :
            page = self.ctrl_notebook.GetPageAvecCode(codePage)
            if page.majEffectuee == True and page.ValidationData() == False : 
                self.ctrl_notebook.AffichePage(codePage)
                return
        # Sauvegarde des données
        for codePage in listePages :
            page = self.ctrl_notebook.GetPageAvecCode(codePage)
            if page.majEffectuee == True :
                page.Sauvegarde()
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetFamillesRattachees(self):
        # Recherche des familles rattachées
        db = GestionDB.DB()
        req = """SELECT IDrattachement, rattachements.IDfamille, IDcategorie, titulaire, IDcompte_payeur
        FROM rattachements 
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = rattachements.IDfamille
        WHERE rattachements.IDindividu=%d
        ORDER BY IDcategorie;""" % self.IDindividu
        db.ExecuterReq(req)
        listeRattachements = db.ResultatReq()
        dictFamilles = {}
        for IDrattachement, IDfamille, IDcategorie, titulaire, IDcompte_payeur in listeRattachements :
            if IDcategorie == 1 : nomCategorie = _(u"représentant")
            if IDcategorie == 2 : nomCategorie = _(u"enfant")
            if IDcategorie == 3 : nomCategorie = _(u"contact")
            dictFamilles[IDfamille] = {"nomsTitulaires" : u"", "listeNomsTitulaires" : [], "IDcategorie" : IDcategorie, "nomCategorie" : nomCategorie, "IDcompte_payeur" : IDcompte_payeur }
        # Recherche des noms des titulaires
        if len(dictFamilles) == 0 : condition = "()"
        if len(dictFamilles) == 1 : condition = "(%d)" % dictFamilles.keys()[0]
        else : condition = str(tuple(dictFamilles))
        req = """SELECT IDrattachement, individus.IDindividu, IDfamille, IDcategorie, titulaire, nom, prenom
        FROM rattachements 
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE IDfamille IN %s AND titulaire=1;""" % condition
        db.ExecuterReq(req)
        listeTitulaires = db.ResultatReq()
        db.Close()
        for IDrattachement, IDindividu, IDfamille, IDcategorie, titulaire, nom, prenom in listeTitulaires :
            nomIndividu = u"%s %s" % (nom, prenom)
            dictFamilles[IDfamille]["listeNomsTitulaires"].append(nomIndividu)
            nbreTitulaires = len(dictFamilles[IDfamille]["listeNomsTitulaires"])
            if nbreTitulaires == 1 : 
                dictFamilles[IDfamille]["nomsTitulaires"] = nomIndividu
            if nbreTitulaires == 2 : 
                dictFamilles[IDfamille]["nomsTitulaires"] = _(u"%s et %s") % (dictFamilles[IDfamille]["listeNomsTitulaires"][0], dictFamilles[IDfamille]["listeNomsTitulaires"][1])
            if nbreTitulaires > 2 :
                texteNoms = ""
                for nomTitulaire in dictFamilles[IDfamille]["listeNomsTitulaires"][:-1] :
                    texteNoms += u"%s, " % nomTitulaire
                texteNoms = _(u"%s et %s") % (dictFamilles[IDfamille]["listeNomsTitulaires"][-2], dictFamilles[IDfamille]["listeNomsTitulaires"][-1])
                dictFamilles[IDfamille]["nomsTitulaires"] = texteNoms
        return dictFamilles
    
    def MAJtexteRattachementHeader(self):
        if len(self.dictFamillesRattachees) == 0 :
            texte = _(u"Aucun rattachement")
        else:
            nbreFamilles = len(self.dictFamillesRattachees)
            texte = u""
            for IDfamille, dictFamille in self.dictFamillesRattachees.iteritems() :
                nomsTitulaires = dictFamille["nomsTitulaires"]
                nomCategorie = dictFamille["nomCategorie"]
                texte += _(u"Est rattaché à la famille de <A HREF='%s'>%s</A> en tant que %s.<BR>") % (str(IDfamille), nomsTitulaires, nomCategorie)
            if nbreFamilles > 0 :
                texte = texte[:-4]
        # Envoie du texte au header
        self.Set_Header("liens", texte)
    
        # MAJ du header ID
        if len(self.dictFamillesRattachees) == 0 :
            texteID = _(u"Rattaché à aucune famille | ID : %d") % self.IDindividu
        if len(self.dictFamillesRattachees) == 1 :
            texteID = _(u"Rattaché à 1 famille | ID : %d") % self.IDindividu
        if len(self.dictFamillesRattachees) > 1 :
            texteID = _(u"Rattaché à %d familles | ID : %d") % (len(self.dictFamillesRattachees), self.IDindividu)
        self.Set_Header("ID", texteID)
            
                
        
    def CreateIDindividu(self):
        """ Crée la fiche individu dans la base de données afin d'obtenir un IDindividu """
        DB = GestionDB.DB()
        date_creation = str(datetime.date.today())
        listeDonnees = [
            ("date_creation", date_creation), 
            ("nom", self.dictInfosNouveau["nom"]), 
            ("prenom", self.dictInfosNouveau["prenom"]), 
            ]
        self.IDindividu = DB.ReqInsert("individus", listeDonnees)
        DB.Close()
        # Mémorise l'action dans l'historique
        UTILS_Historique.InsertActions([{
                "IDindividu" : self.IDindividu,
                "IDcategorie" : 11, 
                "action" : _(u"Création de l'individu ID%d") % self.IDindividu,
                },])
                
    def RattacherIndividu(self, IDfamille=None, IDcategorie=None, titulaire=0):
        # Saisie dans la base
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDindividu", self.IDindividu),
            ("IDfamille", IDfamille),
            ("IDcategorie", IDcategorie),
            ("titulaire", titulaire),
            ]
        IDrattachement = DB.ReqInsert("rattachements", listeDonnees)
        DB.Close()
        # Mémorise l'action dans l'historique
        if IDcategorie == 1 : labelCategorie = _(u"représentant")
        if IDcategorie == 2 : labelCategorie = _(u"enfant")
        if IDcategorie == 3 : labelCategorie = _(u"contact")
        UTILS_Historique.InsertActions([{
                "IDindividu" : self.IDindividu,
                "IDfamille" : IDfamille,
                "IDcategorie" : 13, 
                "action" : _(u"Rattachement de l'individu ID%d à la famille ID%d en tant que %s") % (self.IDindividu, IDfamille, labelCategorie),
                },])
        return True
        
    def Annuler(self):
        """ Annulation des modifications """
        if self.nouvelleFiche == True and self.IDindividu != None :
            
            # Vérifie si des informations non supprimables
            DB = GestionDB.DB()
        
            # Vérifie si des pièces n'existent pas
            req = """
            SELECT IDpiece, IDtype_piece
            FROM pieces
            WHERE IDindividu=%d
            """ % self.IDindividu
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas détacher cette fiche car %d pièce(s) existent déjà pour cet individu sur cette fiche famille.\n\nSupprimez les pièces avant la suppression de l'individu !") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                DB.Close()
                return False

            # Vérifie si des cotisations n'existent pas
            req = """
            SELECT IDcotisation, IDfamille
            FROM cotisations
            WHERE IDindividu=%d
            """ % self.IDindividu
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas détacher cette fiche car %d cotisation(s) individuelle(s) existe(nt) déjà pour cet individu sur cette fiche famille.\n\nSupprimez les cotisations avant la suppression de l'individu !") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                DB.Close()
                return False
            
            # Vérifie si des inscriptions n'existent pas
            req = """
            SELECT IDinscription, IDactivite
            FROM inscriptions
            WHERE IDindividu=%d
            """ % self.IDindividu
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas détacher cette fiche car cet individu est déjà inscrit à %d activité(s) sur cette fiche famille.\n\nSupprimez l'inscription avant la suppression de l'individu !") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                DB.Close()
                return False
                        
            DB.Close()
            
            # Demande de confirmation
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment annuler la création de cette nouvelle fiche ?"), _(u"Annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_YES :
                # Efface de la base la fiche individu 
                DB = GestionDB.DB()
                DB.ReqDEL("individus", "IDindividu", self.IDindividu)
                DB.ReqDEL("rattachements", "IDindividu", self.IDindividu)
                DB.ReqDEL("liens", "IDindividu_sujet", self.IDindividu)
                DB.ReqDEL("liens", "IDindividu_objet", self.IDindividu)
                DB.ReqDEL("vaccins", "IDindividu", self.IDindividu)
                DB.ReqDEL("problemes_sante", "IDindividu", self.IDindividu)
                DB.ReqDEL("questionnaire_reponses", "IDindividu", self.IDindividu)
                DB.ReqDEL("messages", "IDindividu", self.IDindividu)
                DB.ReqDEL("scolarite", "IDindividu", self.IDindividu)
                DB.ReqDEL("transports", "IDindividu", self.IDindividu)
                DB.Close() 
                # Suppression de la photo 
                DB = GestionDB.DB(suffixe="PHOTOS")
                DB.ReqDEL("photos", "IDindividu", self.IDindividu)
                DB.Close()
                dlg.Destroy()
                # Ferme la fenêtre
                self.Destroy()
            else:
                # annulation de la fermeture
                dlg.Destroy()
                return
        else:
            # Ferme la fenêtre
            try :
                self.Destroy()
            except :
                pass

    def MenuEditionEtiquettes(self, event):
        import DLG_Impression_etiquettes
        dlg = DLG_Impression_etiquettes.Dialog(self, IDindividu=self.IDindividu)
        dlg.ShowModal() 
        dlg.Destroy()        

    def MenuHistorique(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_historique", "consulter") == False : return
        import DLG_Historique
        dlg = DLG_Historique.Dialog(self, IDindividu=self.IDindividu)
        dlg.ShowModal() 
        dlg.Destroy()

    def MenuChronologie(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_chronologie", "consulter") == False : return
        import DLG_Chronologie
        dlg = DLG_Chronologie.Dialog(self, IDindividu=self.IDindividu)
        dlg.ShowModal() 
        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    fiche_individu = Dialog(None, IDindividu=45)
    app.SetTopWindow(fiche_individu)
    fiche_individu.ShowModal()
    app.MainLoop()
