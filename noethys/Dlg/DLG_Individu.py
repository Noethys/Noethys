#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import wx.html as html
import GestionDB
from Utils import UTILS_Historique
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Config
import datetime

from Ctrl import CTRL_Photo
from Dlg import DLG_Individu_informations
from Dlg import DLG_Individu_identite
from Dlg import DLG_Individu_coords
from Dlg import DLG_Individu_liens
from Dlg import DLG_Individu_pieces
from Dlg import DLG_Individu_medical
from Dlg import DLG_Individu_inscriptions
from Dlg import DLG_Individu_questionnaire
from Dlg import DLG_Individu_scolarite
from Dlg import DLG_Individu_transports



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
        
        self.listePages = [
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

        # Pages à afficher obligatoirement
        self.pagesObligatoires = ["informations", "identite", "coords"]

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            setattr(self, "img%d" % index, il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/%s') % imgPage, wx.BITMAP_TYPE_PNG)))
            index += 1
        self.AssignImageList(il)

        # Création des pages
        dictParametres = self.GetParametres()

        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            if dictParametres[codePage] == True:
                setattr(self, "page%s" % index, eval(ctrlPage))
                self.AddPage(getattr(self, "page%s" % index), labelPage)
                self.SetPageImage(index, getattr(self, "img%d" % index))
                self.dictPages[codePage] = {'ctrl': getattr(self, "page%d" % index), 'index': index}
                index += 1

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
    def GetPageAvecCode(self, codePage=""):
        if codePage in self.dictPages:
            return self.dictPages[codePage]["ctrl"]
        else:
            return None
    
    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)

    def OnPageChanged(self, event):
        """ Quand une page du notebook est sélectionnée """
        if event.GetOldSelection()==-1: return
        indexPage = event.GetSelection()
        page = self.GetPage(indexPage)
        self.Freeze()
        wx.CallLater(1, page.MAJ)
        self.Thaw()
        event.Skip()

    def GetParametres(self):
        parametres = UTILS_Config.GetParametre("fiche_individu_pages", defaut={})
        dictParametres = {}
        for codePage, labelPage, ctrlPage, imgPage in self.listePages:
            if codePage in parametres:
                afficher = parametres[codePage]
            else :
                afficher = True
            dictParametres[codePage] = afficher
        return dictParametres

    def SelectionParametresPages(self):
        # Préparation de l'affichage des pages
        dictParametres = self.GetParametres()
        listeLabels = []
        listeSelections = []
        listeCodes = []
        index = 0
        for codePage, labelPage, ctrlPage, imgPage in self.listePages:
            if codePage not in self.pagesObligatoires :
                listeLabels.append(labelPage)
                if codePage in dictParametres:
                    if dictParametres[codePage] == True :
                        listeSelections.append(index)
                listeCodes.append(codePage)
                index += 1

        # Demande la sélection des pages
        dlg = wx.MultiChoiceDialog( self, _(u"Cochez ou décochez les onglets à afficher ou à masquer :"), _(u"Afficher/masquer des onglets"), listeLabels)
        dlg.SetSelections(listeSelections)
        dlg.SetSize((300, 350))
        dlg.CenterOnScreen()
        reponse = dlg.ShowModal()
        selections = dlg.GetSelections()
        dlg.Destroy()
        if reponse != wx.ID_OK :
            return False

        # Mémorisation des pages cochées
        dictParametres = {}
        index = 0
        for codePage in listeCodes:
            if index in selections :
                dictParametres[codePage] = True
            else :
                dictParametres[codePage] = False
            index += 1
        UTILS_Config.SetParametre("fiche_individu_pages", dictParametres)

        # Info
        dlg = wx.MessageDialog(self, _(u"Fermez cette fiche pour appliquer les modifications demandées !"), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()






class Dialog(wx.Dialog):
    def __init__(self, parent, IDindividu=None, dictInfosNouveau={}):
        wx.Dialog.__init__(self, parent, id=-1, name="fiche_individu", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.IDindividu = IDindividu
        self.dictInfosNouveau = dictInfosNouveau
        self.nouvelleFiche = False

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
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
        self.ctrl_photo.SetPhoto(IDindividu=None, nomFichier=Chemins.GetStaticPath("Images/128x128/Personne.png"), taillePhoto=(128, 128), qualite=100)
        self.ctrl_notebook = Notebook(self, IDindividu=self.IDindividu, dictFamillesRattachees=self.dictFamillesRattachees)

        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Options"), cheminImage="Images/32x32/Configuration2.png")
        self.bouton_outils = CTRL_Bouton_image.CTRL(self, texte=_(u"Outils"), cheminImage="Images/32x32/Configuration.png")
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Importation des données
##        if self.nouvelleFiche == False :
##            listePages = ("identite", "coords")
##            for codePage in listePages :
##                self.ctrl_notebook.GetPage(codePage).MAJ()

        self.ctrl_notebook.GetPageAvecCode("identite").MAJ()
        self.ctrl_notebook.GetPageAvecCode("coords").MAJ()

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
##            listePages = ("liens", "coords")
##            for codePage in listePages :
##                page = self.ctrl_notebook.GetPageAvecCode(codePage)
##                page.MAJ() 
##                page.majEffectuee = True
                
        # Mise à jour du header
        self.MAJtexteRattachementHeader() 
        
        # MAJ de l'onglet Informations
        self.ctrl_notebook.GetPageAvecCode("informations").MAJ() 
        
        
        
    def __set_properties(self):
        if self.IDindividu != None :
            self.SetTitle(_(u"Fiche individuelle n°%d") % self.IDindividu)
        self.ctrl_ID.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.ctrl_nom.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.ctrl_photo.SetToolTip(wx.ToolTip(_(u"Cliquez sur le bouton droit de la souris\npour accéder aux outils photo")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_options.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux options")))
        self.bouton_outils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder aux outils")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer la fiche")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler la\nsaisie et fermer la fiche")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
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
        grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_outils, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        grid_sizer_base.Fit(self)
        self.SetMinSize((710, self.GetSize()[1]))
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
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Laficheindividuelle")

    def OnBoutonAnnuler(self, event):
        self.Annuler()

    def OnBoutonOptions(self, event):
        self.ctrl_notebook.SelectionParametresPages()

    def OnBoutonOutils(self, event):
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Edition d'étiquettes et de badges
        item = wx.MenuItem(menuPop, 30, _(u"Edition d'étiquettes et de badges"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Etiquette2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuEditionEtiquettes, id=30)
        
        menuPop.AppendSeparator() 

        # Item Historique
        item = wx.MenuItem(menuPop, 10, _(u"Historique"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Historique.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuHistorique, id=10)

        # Item Chronologie
        item = wx.MenuItem(menuPop, 20, _(u"Chronologie"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Timeline.png"), wx.BITMAP_TYPE_PNG)
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
            if page != None and page.majEffectuee == True and page.ValidationData() == False :
                self.ctrl_notebook.AffichePage(codePage)
                return
        # Sauvegarde des données
        for codePage in listePages :
            page = self.ctrl_notebook.GetPageAvecCode(codePage)
            if page != None and page.majEffectuee == True :
                page.Sauvegarde()
        # Fermeture de la fenêtre
        try :
            self.EndModal(wx.ID_OK)
        except :
            pass

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
        if len(dictFamilles) == 1 : condition = "(%d)" % list(dictFamilles.keys())[0]
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
            for IDfamille, dictFamille in self.dictFamillesRattachees.items() :
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
        from Dlg import DLG_Impression_etiquettes
        dlg = DLG_Impression_etiquettes.Dialog(self, IDindividu=self.IDindividu)
        dlg.ShowModal() 
        dlg.Destroy()        

    def MenuHistorique(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_historique", "consulter") == False : return
        from Dlg import DLG_Historique
        dlg = DLG_Historique.Dialog(self, IDindividu=self.IDindividu)
        dlg.ShowModal() 
        dlg.Destroy()

    def MenuChronologie(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_chronologie", "consulter") == False : return
        from Dlg import DLG_Chronologie
        dlg = DLG_Chronologie.Dialog(self, IDindividu=self.IDindividu)
        dlg.ShowModal() 
        dlg.Destroy()


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    import time
    heure_debut = time.time()
    fiche_individu = Dialog(None, IDindividu=45)
    app.SetTopWindow(fiche_individu)
    print("Temps de chargement fiche individuelle =", time.time() - heure_debut)
    fiche_individu.ShowModal()
    app.MainLoop()
