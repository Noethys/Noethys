#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Profil
import FonctionsPerso
import sys
import datetime
from Ctrl import CTRL_Photo
from Ctrl import CTRL_Bandeau
import GestionDB
from Utils import UTILS_Fichiers
from Utils import UTILS_Dates
from Data import DATA_Civilites as Civilites
from Ctrl import CTRL_Selection_inscrits_presents

from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus import Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import Image
from reportlab.platypus.frames import Frame
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus.flowables import DocAssign

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


def GetAge(date_naiss=None):
    if date_naiss == None: return None
    datedujour = datetime.date.today()
    age = (datedujour.year - date_naiss.year) - int((datedujour.month, datedujour.day) < (date_naiss.month, date_naiss.day))
    return age


def GetSQLdates(listePeriodes=[]):
    texteSQL = ""
    for date_debut, date_fin in listePeriodes :
        texteSQL += "(date>='%s' AND date<='%s') OR " % (date_debut, date_fin)
    if len(texteSQL) > 0 :
        texteSQL = "(" + texteSQL[:-4] + ")"
    else:
        texteSQL = "date=0"
    return texteSQL


def Template(canvas, doc):
    """ Première page de l'attestation """
    canvas.saveState()
    # Insertion de l'image de fond de page
    if IMAGE_FOND != None:
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

        x, y, l, h = (self.margeBord + LARGEUR_COLONNE + self.margeInter, self.margeBord, LARGEUR_COLONNE, self.hauteurColonne)
        frame2 = Frame(x, y, l, h, id='F2', leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0)

        x, y, l, h = (self.margeBord + (LARGEUR_COLONNE + self.margeInter) * 2, self.margeBord, LARGEUR_COLONNE, self.hauteurColonne)
        frame3 = Frame(x, y, l, h, id='F2', leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0)

        PageTemplate.__init__(self, id, [frame1, frame2, frame3], Template)

    def afterDrawPage(self, canvas, doc):
        numMois = doc._nameSpace["numMois"]
        nomMois = LISTE_NOMS_MOIS[numMois - 1]

        # Affiche le nom du mois en haut de la page
        canvas.saveState()

        canvas.setLineWidth(0.25)
        canvas.setStrokeColorRGB(0, 0, 0)
        canvas.setFillColorRGB(0.7, 0.7, 1)
        canvas.rect(self.margeBord, self.pageHeight - self.margeBord, self.pageWidth - (self.margeBord * 2), -38, fill=1)

        canvas.setFont("Helvetica-Bold", 24)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.drawString(self.margeBord + 10, self.pageHeight - self.margeBord - 26, nomMois)

        canvas.restoreState()


class CTRL_profil_perso(CTRL_Profil.CTRL):
    def __init__(self, parent, categorie="", dlg=None):
        CTRL_Profil.CTRL.__init__(self, parent, categorie=categorie)
        self.dlg = dlg

    def Envoyer_parametres(self, dictParametres={}):
        """ Envoi des paramètres du profil sélectionné à la fenêtre """
        self.dlg.SetParametres(dictParametres)

    def Recevoir_parametres(self):
        """ Récupération des paramètres pour la sauvegarde du profil """
        dictParametres = self.dlg.GetParametres()
        self.Enregistrer(dictParametres)




class Page_Generalites(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_parametres = CTRL_Selection_inscrits_presents.CTRL(self)

        # Layout
        sizer_base = wx.BoxSizer()
        sizer_base.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.sizer_base = sizer_base

    def GetParametres(self):
        return self.ctrl_parametres.GetParametres()

    def SetParametres(self, dictParametres={}):
        if "mode" in dictParametres:
            self.ctrl_parametres.SetModePresents(dictParametres["mode"] == "presents")


class Page_Options(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.check_photos = wx.CheckBox(self, -1, u"")
        self.check_photos.SetValue(True)
        self.label_photos = wx.StaticText(self, -1, _(u"Afficher les photos :"))
        self.ctrl_photos = wx.Choice(self, -1, choices=[_(u"Petite taille"), _(u"Moyenne taille"), _(u"Grande taille")])
        self.ctrl_photos.SetSelection(1)

        self.check_theme = wx.CheckBox(self, -1, u"")
        self.check_theme.SetValue(True)
        self.label_theme = wx.StaticText(self, -1, _(u"Inclure le thème :"))
        self.ctrl_theme = wx.Choice(self, -1, choices=list(THEMES.keys()))
        self.ctrl_theme.SetStringSelection(_(u"Feuille d'été"))

        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckPhotos, self.check_photos)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckTheme, self.check_theme)

        # Propriétés
        self.check_photos.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour utiliser un thème graphique")))
        self.ctrl_photos.SetToolTip(wx.ToolTip(_(u"Selectionnez ici le thème souhaité")))
        self.check_photos.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les photos des individus")))
        self.ctrl_photos.SetToolTip(wx.ToolTip(_(u"Selectionnez ici la taille des photos")))

        # Layout
        sizer_base = wx.BoxSizer()
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)

        # Photos
        grid_sizer_base.Add(self.check_photos, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_photos = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_photos.Add(self.label_photos, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_photos.Add(self.ctrl_photos, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_photos, 1, wx.EXPAND, 0)

        # Thème
        grid_sizer_base.Add(self.check_theme, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_theme = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_theme.Add(self.label_theme, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_theme.Add(self.ctrl_theme, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_theme, 1, wx.EXPAND, 0)

        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

        # Init Contrôles
        self.OnCheckPhotos(None)

    def OnCheckPhotos(self, event=None):
        if self.check_photos.GetValue() == True :
            self.ctrl_photos.Enable(True)
        else:
            self.ctrl_photos.Enable(False)

    def OnCheckTheme(self, event=None):
        if self.check_theme.GetValue() == True :
            self.ctrl_theme.Enable(True)
        else:
            self.ctrl_theme.Enable(False)

    def GetParametres(self):
        dictParametres = {}

        # Thème
        if self.check_theme.GetValue() == True :
            dictParametres["theme"] = self.ctrl_theme.GetStringSelection()
        else :
            dictParametres["theme"] = None

        # Photo
        photo = 0
        if self.check_photos.GetValue() == True:
            if self.ctrl_photos.GetSelection() == 0 : photo = 16
            if self.ctrl_photos.GetSelection() == 1 : photo = 32
            if self.ctrl_photos.GetSelection() == 2 : photo = 64
        dictParametres["taille_photo"] = photo

        return dictParametres

    def SetParametres(self, dictParametres={}):
        # Thème
        if "theme" in dictParametres:
            if dictParametres["theme"] != None :
                self.ctrl_theme.SetStringSelection(dictParametres["theme"])
            self.check_theme.SetValue(dictParametres["theme"] != None)
            self.OnCheckTheme()

        # Photo
        if "taille_photo" in dictParametres:
            if dictParametres["taille_photo"] != 0 :
                if dictParametres["taille_photo"] == 16 : self.ctrl_photos.SetSelection(0)
                if dictParametres["taille_photo"] == 32 : self.ctrl_photos.SetSelection(1)
                if dictParametres["taille_photo"] == 64 : self.ctrl_photos.SetSelection(2)
            self.check_photos.SetValue(dictParametres["taille_photo"] != 0)
            self.OnCheckPhotos()



# ----------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT | wx.NB_MULTILINE)
        self.dictPages = {}

        self.listePages = [
            {"code": "generalites", "ctrl": Page_Generalites(self), "label": _(u"Paramètres"), "image": "Calendrier.png"},
            {"code": "options", "ctrl": Page_Options(self), "label": _(u"Options"), "image": "Options.png"},
        ]

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        for dictPage in self.listePages:
            self.dictImages[dictPage["code"]] = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % dictPage["image"]), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Création des pages
        self.dictPages = {}
        index = 0
        for dictPage in self.listePages:
            self.AddPage(dictPage["ctrl"], dictPage["label"])
            self.SetPageImage(index, self.dictImages[dictPage["code"]])
            self.dictPages[dictPage["code"]] = dictPage["ctrl"]
            index += 1

    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]

    def AffichePage(self, codePage=""):
        index = 0
        for dictPage in self.listePages:
            if dictPage["code"] == codePage:
                self.SetSelection(index)
            index += 1

    def GetParametres(self):
        dictParametres = {}
        for dictPage in self.listePages:
            dictParametres.update(dictPage["ctrl"].GetParametres())
        return dictParametres

    def SetParametres(self, dictParametres={}):
        for dictPage in self.listePages:
            dictPage["ctrl"].SetParametres(dictParametres)


# ----------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Anniversaires", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici imprimer la liste des anniversaires des individus inscrits sur les activités cochées et présents sur la période donnée. Il est possible d'inclure un thème graphique et les photos individuelles.")
        titre = _(u"Liste des anniversaires")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Anniversaire.png")

        # Profil de configuration
        self.staticbox_profil_staticbox = wx.StaticBox(self, -1, _(u"Profil de configuration"))
        self.ctrl_profil = CTRL_profil_perso(self, categorie="impression_anniversaires", dlg=self)

        # Notebook
        self.ctrl_notebook = CTRL_Parametres(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init Contrôles
        self.ctrl_profil.SetOnDefaut()
        self.bouton_ok.SetFocus()


    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((650, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Profil
        staticbox_profil = wx.StaticBoxSizer(self.staticbox_profil_staticbox, wx.VERTICAL)
        staticbox_profil.Add(self.ctrl_profil, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_base.Add(staticbox_profil, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        grid_sizer_base.Add(self.ctrl_notebook, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesanniversaires")

    def GetPage(self, code=""):
        """ Retourne le ctrl page du notebook selon le code page """
        return self.ctrl_notebook.GetPageAvecCode(code)

    def GetParametres(self):
        """ Récupération des paramètres """
        return self.ctrl_notebook.GetParametres()

    def SetParametres(self, dictParametres={}):
        """ Importation des paramètres """
        if dictParametres != None :
            self.ctrl_notebook.SetParametres(dictParametres)

    def EcritStatusBar(self, texte=u""):
        try:
            wx.GetApp().GetTopWindow().SetStatusText(texte, 0)
        except:
            pass

    def OnBoutonOk(self, event):
        dictParametres = self.ctrl_notebook.GetParametres()

        # Récupération et vérification des données
        listeActivites = dictParametres["liste_activites"]
        if len(listeActivites) == 0 :
            self.ctrl_notebook.AffichePage("generalites")
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Récupération et vérification des données
        listeGroupes = dictParametres["liste_groupes"]
        if len(dictParametres["liste_groupes"]) == 0 :
            self.ctrl_notebook.AffichePage("generalites")
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un groupe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Thème
        global IMAGE_FOND
        if dictParametres["theme"] != None :
            IMAGE_FOND = Chemins.GetStaticPath(THEMES[dictParametres["theme"]])
        else:
            IMAGE_FOND = None

        # Création du PDF
        self.taille_page = A4
        self.orientation = "PORTRAIT"
        if self.orientation == "PORTRAIT":
            self.hauteur_page = self.taille_page[1]
            self.largeur_page = self.taille_page[0]
        else:
            self.hauteur_page = self.taille_page[0]
            self.largeur_page = self.taille_page[1]

        # Création des conditions pour les requêtes SQL
        conditionsPeriodes = GetSQLdates(dictParametres["liste_periodes"])

        if len(listeActivites) == 0: conditionActivites = "()"
        elif len(listeActivites) == 1: conditionActivites = "(%d)" % listeActivites[0]
        else: conditionActivites = str(tuple(listeActivites))

        if len(listeGroupes) == 0: conditionGroupes = "()"
        elif len(listeGroupes) == 1: conditionGroupes = "(%d)" % listeGroupes[0]
        else: conditionGroupes = str(tuple(listeGroupes))

        # Récupération des noms des groupes
        dictGroupes = dictParametres["dict_groupes"]

        DB = GestionDB.DB()

        # Récupération des individus grâce à leurs consommations
        self.EcritStatusBar(_(u"Recherche des individus..."))

        # ------------ MODE PRESENTS ---------------------------------

        if dictParametres["mode"] == "presents":

            # Récupération de la liste des groupes ouverts sur cette période
            req = """SELECT IDouverture, IDactivite, IDunite, IDgroupe
            FROM ouvertures 
            WHERE ouvertures.IDactivite IN %s AND %s
            AND IDgroupe IN %s
            ; """ % (conditionActivites, conditionsPeriodes, conditionGroupes)
            DB.ExecuterReq(req)
            listeOuvertures = DB.ResultatReq()
            dictOuvertures = {}
            for IDouverture, IDactivite, IDunite, IDgroupe in listeOuvertures:
                if (IDactivite in dictOuvertures) == False:
                    dictOuvertures[IDactivite] = []
                if IDgroupe not in dictOuvertures[IDactivite]:
                    dictOuvertures[IDactivite].append(IDgroupe)

            # Récupération des individus grâce à leurs consommations
            req = """SELECT individus.IDindividu, IDcivilite, nom, prenom, date_naiss
            FROM consommations 
            LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
            WHERE consommations.etat IN ("reservation", "present")
            AND IDactivite IN %s AND %s
            GROUP BY individus.IDindividu
            ORDER BY nom, prenom
            ;""" % (conditionActivites, conditionsPeriodes)
            DB.ExecuterReq(req)
            listeIndividus = DB.ResultatReq()

        # ------------ MODE INSCRITS ---------------------------------

        if dictParametres["mode"] == "inscrits":

            dictOuvertures = {}
            for IDgroupe, dictGroupe in dictGroupes.items():
                IDactivite = dictGroupe["IDactivite"]
                if (IDactivite in dictOuvertures) == False:
                    dictOuvertures[IDactivite] = []
                if IDgroupe not in dictOuvertures[IDactivite]:
                    dictOuvertures[IDactivite].append(IDgroupe)

            # Récupération des individus inscrits
            req = """SELECT individus.IDindividu, IDcivilite, nom, prenom, date_naiss
            FROM individus 
            LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
            WHERE inscriptions.statut='ok' AND IDactivite IN %s
            GROUP BY individus.IDindividu
            ORDER BY nom, prenom
            ;""" % conditionActivites
            DB.ExecuterReq(req)
            listeIndividus = DB.ResultatReq()

        DB.Close()

        if len(listeIndividus) == 0:
            dlg = wx.MessageDialog(self, _(u"Aucun individu n'a été trouvé avec les paramètres spécifiés !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.EcritStatusBar(u"")
            return

        dictIndividus = {}
        listeIDindividus = []

        dictAnniversaires = {}

        self.EcritStatusBar(_(u"Recherche des dates de naissance..."))
        for IDindividu, IDcivilite, nom, prenom, date_naiss in listeIndividus:
            if date_naiss != None:
                date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)
                age = GetAge(date_naiss)
                jour = date_naiss.day
                mois = date_naiss.month

                # Mémorisation de l'individu
                dictIndividus[IDindividu] = {
                    "IDcivilite": IDcivilite, "nom": nom, "prenom": prenom,
                    "age": age, "date_naiss": date_naiss,
                }

                # Mémorisation du IDindividu
                if (mois in dictAnniversaires) == False:
                    dictAnniversaires[mois] = {}
                if (jour in dictAnniversaires[mois]) == False:
                    dictAnniversaires[mois][jour] = []
                dictAnniversaires[mois][jour].append(IDindividu)

                if IDindividu not in listeIDindividus:
                    listeIDindividus.append(IDindividu)

                    # Récupération des photos individuelles
        dictPhotos = {}
        taillePhoto = 128
        if dictParametres["taille_photo"] != 0 :
            index = 0
            for IDindividu in listeIDindividus:
                self.EcritStatusBar(_(u"Recherche des photos... %d/%d") % (index, len(listeIDindividus)))
                IDcivilite = dictIndividus[IDindividu]["IDcivilite"]
                nomFichier = Chemins.GetStaticPath("Images/128x128/%s" % DICT_CIVILITES[IDcivilite]["nomImage"])
                IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDindividu, nomFichier=nomFichier, taillePhoto=(taillePhoto, taillePhoto), qualite=100)

                # Création de la photo dans le répertoire Temp
                nomFichier = UTILS_Fichiers.GetRepTemp(fichier="photoTmp%d.jpg" % IDindividu)
                bmp.SaveFile(nomFichier, type=wx.BITMAP_TYPE_JPEG)
                img = Image(nomFichier, width=dictParametres["taille_photo"], height=dictParametres["taille_photo"])
                dictPhotos[IDindividu] = img

                index += 1

        # ---------------- Création du PDF -------------------
        self.EcritStatusBar(_(u"Création du PDF..."))

        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("ANNIVERSAIRES", "pdf")
        if sys.platform.startswith("win"): nomDoc = nomDoc.replace("/", "\\")
        doc = BaseDocTemplate(nomDoc, pagesize=(self.largeur_page, self.hauteur_page), topMargin=30, bottomMargin=30, showBoundary=False)
        doc.addPageTemplates(MyPageTemplate(pageSize=(self.largeur_page, self.hauteur_page)))
        story = []

        # Mois
        listeMois = list(dictAnniversaires.keys())
        listeMois.sort()
        for numMois in listeMois:

            # Mémorise le numéro de mois pour le titre de la page
            nomMois = LISTE_NOMS_MOIS[numMois - 1]
            story.append(DocAssign("numMois", numMois))

            # Jours
            dictJours = dictAnniversaires[numMois]
            listeJours = list(dictJours.keys())
            listeJours.sort()
            for numJour in listeJours:
                # Initialisation du tableau
                dataTableau = []
                largeursColonnes = []

                # Recherche des entêtes de colonnes :
                if dictParametres["taille_photo"] != 0 :
                    largeursColonnes.append(dictParametres["taille_photo"] + 6)

                # Colonne nom de l'individu
                largeursColonnes.append(LARGEUR_COLONNE - sum(largeursColonnes))

                # Label numéro de jour
                ligne = []
                ligne.append(str(numJour))
                if dictParametres["taille_photo"] != 0 :
                    ligne.append(u"")
                dataTableau.append(ligne)

                # Individus
                listeIndividus = dictAnniversaires[numMois][numJour]

                for IDindividu in listeIndividus:
                    ligne = []

                    # Photo
                    if dictParametres["taille_photo"] != 0 and IDindividu in dictPhotos:
                        img = dictPhotos[IDindividu]
                        ligne.append(img)

                    # Nom
                    nom = dictIndividus[IDindividu]["nom"]
                    prenom = dictIndividus[IDindividu]["prenom"]
                    ligne.append(u"%s %s" % (nom, prenom))

                    # Ajout de la ligne individuelle dans le tableau
                    dataTableau.append(ligne)

                couleurFondJour = (0.8, 0.8, 1)  # Vert -> (0.5, 1, 0.2)
                couleurFondTableau = (1, 1, 1)

                style = TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Centre verticalement toutes les cases
                    ('BACKGROUND', (0, 0), (-1, -1), couleurFondTableau),  # Donne la couleur de fond du titre de groupe

                    ('FONT', (0, 0), (-1, -1), "Helvetica", 7),  # Donne la police de caract. + taille de police
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.black),  # Crée la bordure noire pour tout le tableau
                    ('ALIGN', (0, 1), (-1, -1), 'CENTRE'),  # Centre les cases

                    ('SPAN', (0, 0), (-1, 0)),  # Fusionne les lignes du haut pour faire le titre du groupe
                    ('FONT', (0, 0), (0, 0), "Helvetica-Bold", 10),  # Donne la police de caract. + taille de police du titre de groupe
                    ('BACKGROUND', (0, 0), (-1, 0), couleurFondJour),  # Donne la couleur de fond du titre de groupe

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
