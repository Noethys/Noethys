#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import wx.html as html
import datetime
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
import wx.lib.scrolledpanel as scrolled
from Dlg import DLG_Activite_generalites
from Dlg import DLG_Activite_obligations
from Ctrl import CTRL_Tarification_calcul
from Ctrl import CTRL_Selection_jours
from Dlg.DLG_Ouvertures import Track_tarif


def CreationAbrege(nom=""):
    for i in " 0123456789/*-+.,;:_'()" :
        nom = nom.replace(i, "")
    return nom[:5].upper()


class CTRL(object):
    def __init__(self, parent, *args, **kwds):
        self.parent = parent
        self.code = kwds["code"]
        if "obligatoire" in kwds:
            self.obligatoire = kwds["obligatoire"]
        else :
            self.obligatoire = False
        if "on_reponse" in kwds:
            self.on_reponse = kwds["on_reponse"]
        else :
            self.on_reponse = None
        if "defaut" in kwds:
            self.defaut = kwds["defaut"]
        else :
            self.defaut = None
        if "titre" in kwds:
            self.titre = kwds["titre"]
        else:
            self.titre = ""


    def Validation(self):
        if self.obligatoire == True and self.GetValeur() in (None, "", 0) :
            dlg = wx.MessageDialog(self, _(u"Merci de r�pondre � la question suivante :\n\n%s") % self.titre, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.SetFocus()
            return False

        return True





class CTRL_Texte(CTRL, wx.TextCtrl):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        wx.TextCtrl.__init__(self, parent, id=-1)

    def GetValeur(self):
        return self.GetValue()

    def SetValeur(self, valeur=None):
        if valeur != None :
            self.SetValue(valeur)


class CTRL_Date(CTRL, CTRL_Saisie_date.Date2):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        CTRL_Saisie_date.Date2.__init__(self, parent)

    def GetValeur(self):
        return self.GetDate()

    def SetValeur(self, valeur=None):
        if valeur != None :
            self.SetDate(valeur)


class CTRL_Nombre(CTRL, wx.SpinCtrl):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        wx.SpinCtrl.__init__(self, parent, size=(80, -1), min=0, max=99999)

    def GetValeur(self):
        return self.GetValue()

    def SetValeur(self, valeur=None):
        if valeur != None :
            self.SetValue(valeur)



class CTRL_Nombre(CTRL, wx.Panel):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.ctrl = wx.SpinCtrl(self, size=(100, -1), min=0, max=99999)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.ctrl, 0, 0, 0)
        self.SetSizer(self.sizer)

    def GetValeur(self):
        return self.ctrl.GetValue()

    def SetValeur(self, valeur=None):
        if valeur != None :
            self.ctrl.SetValue(valeur)



class CTRL_Oui_non(CTRL, wx.Panel):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.radio_oui = wx.RadioButton(self, -1, _(u"Oui"), style=wx.RB_GROUP)
        self.radio_non = wx.RadioButton(self, -1, _(u"Non"))

        # Layout
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.radio_oui, 0, wx.RIGHT, 5)
        self.sizer.Add(self.radio_non, 0, 0, 0)
        self.SetSizer(self.sizer)

        # Binds
        if self.on_reponse != None :
            self.Bind(wx.EVT_RADIOBUTTON, self.on_reponse, self.radio_oui)
            self.Bind(wx.EVT_RADIOBUTTON, self.on_reponse, self.radio_non)

        self.SetValeur(self.defaut)

    def GetValeur(self):
        return self.radio_oui.GetValue()

    def SetValeur(self, valeur=None):
        if valeur != None :
            if valeur == True :
                self.radio_oui.SetValue(True)
            else :
                self.radio_non.SetValue(True)



class CTRL_Radio(CTRL, wx.Panel):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        if "choix" in kwds:
            self.choix = kwds["choix"]
        else :
            self.choix = []
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)

        self.listeCtrl = []
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        index = 0
        for code, label in self.choix :
            if index == 0 :
                ctrl = wx.RadioButton(self, -1, label, style=wx.RB_GROUP)
            else :
                ctrl = wx.RadioButton(self, -1, label)
            self.listeCtrl.append(ctrl)
            self.sizer.Add(ctrl, 0, wx.RIGHT, 5)
            index += 1
        self.SetSizer(self.sizer)
        self.SetValeur(self.defaut)

    def GetValeur(self):
        index = 0
        for ctrl in self.listeCtrl :
            if ctrl.GetValue() == True :
                return self.choix[index][0]
            index += 1
        return self.radio_oui.GetValue()

    def SetValeur(self, valeur=None):
        if valeur != None :
            index = 0
            for code, label in self.choix:
                if code == valeur :
                    self.listeCtrl[index].SetValue(True)
                index += 1



class CTRL_Groupes_activite(CTRL, DLG_Activite_generalites.CTRL_Groupes_activite):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        DLG_Activite_generalites.CTRL_Groupes_activite.__init__(self, parent)
        self.SetMinSize((-1, 70))

    def GetValeur(self):
        return self.GetIDcoches()

    def SetValeur(self, valeur=None):
        if valeur != None :
            self.SetIDcoches(valeur)


class CTRL_Jours(CTRL, CTRL_Selection_jours.CTRL):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        CTRL_Selection_jours.CTRL.__init__(self, parent)

    def GetValeur(self):
        return self.GetDonnees()

    def SetValeur(self, valeur=None):
        if valeur != None :
            self.SetDonnees(valeur)


class CTRL_Pieces(CTRL, DLG_Activite_obligations.CheckListBoxPieces):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        DLG_Activite_obligations.CheckListBoxPieces.__init__(self, parent)
        self.SetMinSize((-1, 100))
        self.MAJ()

    def GetValeur(self):
        return self.GetIDcoches()

    def SetValeur(self, valeur=None):
        if valeur != None :
            self.SetIDcoches(valeur)


class CTRL_Cotisations(CTRL, DLG_Activite_obligations.CheckListBoxCotisations):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        DLG_Activite_obligations.CheckListBoxCotisations.__init__(self, parent)
        self.SetMinSize((-1, 60))
        self.MAJ()

    def GetValeur(self):
        return self.GetIDcoches()

    def SetValeur(self, valeur=None):
        if valeur != None :
            self.SetIDcoches(valeur)


class CTRL_Renseignements(CTRL, DLG_Activite_obligations.CheckListBoxRenseignements):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        DLG_Activite_obligations.CheckListBoxRenseignements.__init__(self, parent)
        self.SetMinSize((-1, 180))
        self.MAJ()

    def GetValeur(self):
        return self.GetIDcoches()

    def SetValeur(self, valeur=None):
        if valeur != None :
            self.SetIDcoches(valeur)


class CTRL_Choix(CTRL, wx.Choice):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        if "choix" in kwds:
            self.liste_choix = kwds["choix"]
        else :
            self.liste_choix = []
        if "on_reponse" in kwds:
            on_reponse = kwds["on_reponse"]
        else :
            on_reponse = None
        liste_labels = []
        for code, label in self.liste_choix :
            liste_labels.append(label)
        wx.Choice.__init__(self, parent, id=-1, choices=liste_labels, style=wx.TAB_TRAVERSAL)

        # Binds
        if on_reponse != None :
            self.Bind(wx.EVT_CHOICE, on_reponse, self)

        self.SetValeur(self.defaut)

    def GetValeur(self):
        index = self.GetSelection()
        return self.liste_choix[index][0]

    def SetValeur(self, valeur=None):
        index = 0
        for code, label in self.liste_choix :
            if code == valeur :
                self.SetSelection(index)
            index += 1


class CTRL_Tarif(CTRL, CTRL_Tarification_calcul.Panel):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        track_tarif = Track_tarif()
        filtre_methodes = ("montant_unique", "qf")
        CTRL_Tarification_calcul.Panel.__init__(self, parent, IDactivite=None, IDtarif=None, track_tarif=track_tarif, filtre_methodes=filtre_methodes)
        self.SetMinSize((-1, 220))
        self.MAJ()

    def GetValeur(self):
        self.ctrl_parametres.Sauvegarde()
        return self.ctrl_parametres.track_tarif

    def SetValeur(self, valeur=None):
        if valeur != None:
            self.ctrl_parametres.track_tarif = valeur
            self.ctrl_parametres.Importation()



class CTRL_Html(CTRL, html.HtmlWindow):
    def __init__(self, parent, *args, **kwds):
        CTRL.__init__(self, parent, *args, **kwds)
        if "size" in kwds:
            size = kwds["size"]
        else :
            size = (-1, 100)
        if "texte" in kwds:
            texte = kwds["texte"]
        else :
            texte = ""
        html.HtmlWindow.__init__(self, parent, -1, size=size, style=wx.html.HW_NO_SELECTION)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(5)
        if texte != "" :
            self.SetValeur(texte)

    def SetValeur(self, valeur=""):
        self.SetPage(u"""<BODY'><FONT SIZE=2>%s</FONT></BODY>""" % valeur)
        self.SetBackgroundColour(self.parent.GetBackgroundColour())




# --------------------------------------------------------------------------------------------------------------------

class Page(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.parent = parent
        self.dict_ctrl = {}
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def Ajouter_rubrique(self, titre=None):
        # Titre
        if titre != None :
            ctrl_titre = wx.StaticText(self, -1, titre)
            ctrl_titre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
            self.sizer.Add(ctrl_titre, 0, wx.EXPAND | wx.RIGHT, 5)
            self.sizer.Add((5, 2), 0, 0, 0)

        ctrl_ligne = wx.StaticLine(self, -1)
        self.sizer.Add(ctrl_ligne, 0, wx.EXPAND | wx.RIGHT, 5)

        # Spacer
        self.sizer.Add((5, 10), 0, 0, 0)

        # Initialisation des barres de d�filement
        self.SetupScrolling()

    def Ajouter_question(self, code=None, titre=None, commentaire=None, ctrl=None, *args, **kwds):
        # Titre
        if titre != None :
            ctrl_titre = wx.StaticText(self, -1, titre)
            self.sizer.Add(ctrl_titre, 0, wx.EXPAND | wx.RIGHT, 5)
            self.sizer.Add((5, 7), 0, 0, 0)

        # Saisie
        if ctrl != None :
            ctrl_valeur = ctrl(self, code=code, titre=titre, *args, **kwds)
            if code != None :
                self.dict_ctrl[code] = ctrl_valeur
            self.sizer.Add(ctrl_valeur, 0, wx.EXPAND | wx.RIGHT, 5)
            self.sizer.Add((5, 7), 0, 0, 0)

            # Importation de la valeur
            if code in self.parent.dict_valeurs :
                ctrl_valeur.SetValeur(self.parent.dict_valeurs[code])

        # Commentaire
        if commentaire != None :
            ctrl_commentaire = wx.StaticText(self, -1, commentaire)
            ctrl_commentaire.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ''))
            ctrl_commentaire.SetForegroundColour((120, 120, 120))
            self.sizer.Add(ctrl_commentaire, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)

        # Spacer
        self.sizer.Add((5, 10), 0, 0, 0)

        # Initialisation des barres de d�filement
        self.SetupScrolling()

    def MAJ(self):
        pass

    def Validation(self):
        for code, ctrl in self.dict_ctrl.items() :
            if ctrl.Validation() == False :
                return False

        # if hasattr(self, "Validation_page"):
        #     if self.Validation_page() == False :
        #         return False

        self.Memorise_valeurs()
        return True

    def GetValeurs(self):
        dict_valeurs = {}
        for code, ctrl in self.dict_ctrl.items() :
            dict_valeurs[code] = ctrl.GetValeur()
        return dict_valeurs

    def SetValeurs(self, dict_valeurs={}):
        for code, ctrl in self.dict_ctrl.items():
            if code in dict_valeurs:
                ctrl.SetValeur(dict_valeurs[code])

    def Memorise_valeurs(self):
        for code, valeur in self.GetValeurs().items() :
            self.parent.dict_valeurs[code] = valeur

    def Chercher_position(self, code=""):
        index = 0
        for sizerItem in  self.sizer.GetChildren():
            widget = sizerItem.GetWindow()
            if hasattr(widget, "code"):
                if code == widget.code :
                    return index
            index += 1
        return index



class Page_exemple(Page):
    def __init__(self, parent):
        Page.__init__(self, parent)
        self.Ajouter_question(code="nom", titre=_(u"Quel est le nom du s�jour ?"), commentaire=_(u"Exemple : 'S�jour neige - F�vrier 2018'"), ctrl=CTRL_Texte)
        self.Ajouter_question(code="groupes", titre=_(u"Le s�jour est-il constitu� de groupes d'�ge ?"), commentaire=_(u"Commentaire"), ctrl=CTRL_Oui_non)
        self.Ajouter_question(code="date_debut", titre=_(u"Quelle est la date de d�but du s�jour ?"), commentaire=None, ctrl=CTRL_Date)
        self.Ajouter_rubrique(titre=_(u"Inscriptions"))
        self.Ajouter_question(code="nbre_inscrits_max", titre=_(u"Quel est le nombre maximal d'inscrits ?"), commentaire=_(u"S'il n'y aucune limite, laissez sur 0"), ctrl=CTRL_Nombre)
        self.Ajouter_question(ctrl=CTRL_Html, texte=_(u"Ceci est un texte HTML"), size=(-1, 50))


    def MAJ(self):
        dict_valeurs = {
            "nom" : _(u"S�jour aventure - Juillet 2018"),
            }
        self.SetValeurs(dict_valeurs)

    def Suite(self):
        self.Memorise_valeurs()
        return Page_conclusion


class Page_responsable(Page):
    def __init__(self, parent):
        Page.__init__(self, parent)

        # Recherche du dernier responsable saisi
        DB = GestionDB.DB()
        req = """SELECT sexe, nom, fonction
        FROM responsables_activite
        ORDER BY IDresponsable DESC LIMIT 1;
        """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 and "responsable_nom" not in self.parent.dict_valeurs:
            self.parent.dict_valeurs["responsable_sexe"] = listeDonnees[0][0]
            self.parent.dict_valeurs["responsable_nom"] = listeDonnees[0][1]
            self.parent.dict_valeurs["responsable_fonction"] = listeDonnees[0][2]

        self.Ajouter_rubrique(titre=_(u"Le responsable du s�jour"))
        self.Ajouter_question(code="responsable_nom", titre=_(u"Quel est le nom complet du responsable de l'activit� (Pr�nom et nom) ?"), commentaire=_(u"Exemple : 'Jean-Louis DUPOND'"), ctrl=CTRL_Texte, obligatoire=False)
        self.Ajouter_question(code="responsable_fonction", titre=_(u"Quelle est sa fonction ?"), commentaire=_(u"Exemple : 'Directeur'"), ctrl=CTRL_Texte, obligatoire=False)
        self.Ajouter_question(code="responsable_sexe", titre=_(u"Homme ou femme ?"), choix=[("H", _(u"Homme")), ("F", _(u"Femme"))], ctrl=CTRL_Radio, obligatoire=False)

        texte = _(u"""<IMG SRC="%s">
        Le nom de responsable est utilis� par Noethys comme signataire de certains documents (attestations, re�us...).
        Indiquez par exemple la directrice, la secr�taire, le Maire, etc... Noethys r�cup�re par d�faut le nom de responsable
        de la derni�re activit� saisie.
        """) % Chemins.GetStaticPath("Images/16x16/Astuce.png")
        self.Ajouter_question(ctrl=CTRL_Html, texte=texte, size=(-1, 50))

    def Suite(self):
        pass


class Page_renseignements(Page):
    def __init__(self, parent):
        Page.__init__(self, parent)
        self.Ajouter_rubrique(titre=_(u"Renseignements"))
        self.Ajouter_question(code="pieces", titre=_(u"Quelles sont les pi�ces � fournir par l'individu inscrit ?"), commentaire=_(u"Si la pi�ce souhait�e n'appara�t pas, vous devez d'abord la param�trer dans le menu Param�trage."), ctrl=CTRL_Pieces)
        self.Ajouter_question(code="cotisations", titre=_(u"Si l'individu doit �tre � jour de l'une des cotisations suivantes, cochez-les ci-dessous :"), commentaire=_(u"Si la cotisation souhait�e n'appara�t pas, vous devez d'abord la param�trer dans le menu Param�trage."), ctrl=CTRL_Cotisations)
        self.Ajouter_question(code="renseignements", titre=_(u"Quels renseignements doivent �tre fournis par l'individu inscrit ?"), commentaire=None, ctrl=CTRL_Renseignements)

    def Suite(self):
        pass


class Page_recopier_tarifs(Page):
    def __init__(self, parent):
        Page.__init__(self, parent)
        self.Ajouter_rubrique(titre=_(u"Tarifs"))
        liste_choix = self.parent.dict_valeurs["activites_ressemblantes"]
        self.Ajouter_question(code="recopier_tarifs", titre=_(u"Souhaitez-vous recopier la tarification d'une activit� existante ?"), commentaire=_(u"S�lectionnez une activit� du m�me type dans la liste d�roulante, sa tarification sera r�cup�r�e pour votre nouvelle activit�."), choix=liste_choix, ctrl=CTRL_Choix, defaut=None)

    def Suite(self):
        pass


# --------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, page_introduction=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_assistant_activite", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        self.parent = parent
        self.dict_valeurs = {}

        intro = _(u"Cette fonctionnalit� vous permet de b�n�ficier d'un param�trage semi-automatis� d'une activit� d'un type donn�. Vous n'avez qu'� simplement r�pondre au questionnaire propos� pour g�n�rer facilement votre nouvelle activit�.")
        titre = _(u"Assistant de param�trage d'une activit�")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")

        # Contenu
        self.page_active = page_introduction(self)
        self.liste_pages = [page_introduction,]

        # Bas de page
        self.static_line = wx.StaticLine(self, -1)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        #self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Param�tres avanc�s"), cheminImage="Images/32x32/Configuration2.png")
        self.bouton_retour = CTRL_Bouton_image.CTRL(self, texte=_(u"Retour"), cheminImage="Images/32x32/Fleche_gauche.png")
        self.bouton_suite = CTRL_Bouton_image.CTRL(self, texte=_(u"Suite"), cheminImage="Images/32x32/Fleche_droite.png", margesImage=(0, 0, 4, 0), positionImage=wx.RIGHT)
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        #self.Bind(wx.EVT_BUTTON, self.MenuOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_retour, self.bouton_retour)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_suite, self.bouton_suite)
        self.Bind(wx.EVT_BUTTON, self.Annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.bouton_retour.Enable(False)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        #self.bouton_options.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour acc�der aux param�tres avanc�s")))
        self.bouton_retour.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour revenir � la page pr�c�dente")))
        self.bouton_suite.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour passer � l'�tape suivante")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler")))
        self.SetMinSize((840, 710))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)

        # Contenu
        self.sizer_pages = wx.BoxSizer(wx.VERTICAL)
        self.sizer_pages.Add(self.page_active, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(self.sizer_pages, 1, wx.ALL | wx.EXPAND, 10)

        # Bottom
        grid_sizer_base.Add(self.static_line, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Boutons
        self.grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        self.grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        #self.grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
        self.grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        self.grid_sizer_boutons.Add(self.bouton_retour, 0, 0, 0)
        self.grid_sizer_boutons.Add(self.bouton_suite, 0, 0, 0)
        self.grid_sizer_boutons.Add(self.bouton_annuler, 0, wx.LEFT, 10)
        self.grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(self.grid_sizer_boutons, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()

    def Afficher_page(self, ctrl=None):
        self.Freeze()

        # Affichage de la page
        # self.page_active.Destroy()
        # self.page_active = ctrl(self)
        # self.sizer_pages.Add(self.page_active, 1, wx.EXPAND, 0)
        # self.sizer_pages.Layout()

        self.page_active.Destroy()
        self.page_active = ctrl(self)
        self.sizer_pages.Add(self.page_active, 1, wx.EXPAND, 0)
        self.sizer_pages.Layout()

        # Affichage des boutons
        if ctrl.__name__ == "Page_conclusion" :
            self.bouton_suite.SetImageEtTexte(Chemins.GetStaticPath("Images/32x32/Valider.png"), _(u"Valider"))
        else:
            self.bouton_suite.SetImageEtTexte(Chemins.GetStaticPath("Images/32x32/Fleche_droite.png"), _(u"Suite"))
        self.bouton_retour.Enable(not ctrl.__name__ == "Page_introduction")
        self.grid_sizer_boutons.Layout()
        self.Refresh()

        self.Thaw()

    def Onbouton_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Paramtreruneactivit")

    def Onbouton_retour(self, event):
        # M�morise les valeurs de la page active
        self.page_active.Memorise_valeurs()

        # Supprime l'historique
        self.liste_pages.pop(-1)
        page_precedente = self.liste_pages[-1]

        # Affiche la page pr�c�dente
        self.Afficher_page(ctrl=page_precedente)

    def Onbouton_suite(self, event):
        # Validation de la page active
        if self.page_active.Validation() == False :
            return False

        # Affiche la page suivante
        page_suivante = self.page_active.Suite()
        if page_suivante != False :
            self.Afficher_page(ctrl=page_suivante)
            self.liste_pages.append(page_suivante)

    def OnClose(self, event):
        self.Annuler()

    def Annuler(self, event=None):
        self.EndModal(wx.ID_CANCEL)

    def GetIDactivite(self):
        return self.dict_valeurs["IDactivite"]

    def Sauvegarde_standard(self, DB=None):
        """ Sauvegarde des donn�es """
        nom = self.dict_valeurs["nom"]
        abrege = CreationAbrege(self.dict_valeurs["nom"])
        if "date_debut" in self.dict_valeurs:
            date_debut = self.dict_valeurs["date_debut"]
        else :
            date_debut = datetime.date(1977, 1, 1)
        if "date_fin" in self.dict_valeurs:
            date_fin = self.dict_valeurs["date_fin"]
        else :
            date_fin = datetime.date(2999, 1, 1)

        # Nbre inscrits max
        if "nbre_inscrits_max" not in self.dict_valeurs or self.dict_valeurs["nbre_inscrits_max"] == 0:
            nbre_inscrits_max = None
        else:
            nbre_inscrits_max = self.dict_valeurs["nbre_inscrits_max"]

        # Enregistrement
        listeDonnees = [
            ("date_creation", str(datetime.date.today())),
            ("nom", nom),
            ("abrege", abrege),
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("nbre_inscrits_max", nbre_inscrits_max),
            ("coords_org", 1),
            ("logo_org", 1),
        ]
        IDactivite = DB.ReqInsert("activites", listeDonnees)
        self.dict_valeurs["IDactivite"] = IDactivite

        # Groupes d'activit�s
        if "groupes_activites" in self.dict_valeurs:
            for IDtype_groupe_activite in self.dict_valeurs["groupes_activites"]:
                listeDonnees = [("IDtype_groupe_activite", IDtype_groupe_activite), ("IDactivite", IDactivite)]
                DB.ReqInsert("groupes_activites", listeDonnees)

        # Agr�ment
        if "num_agrement" in self.dict_valeurs and self.dict_valeurs["num_agrement"] != "" :
            listeDonnees = [
                ("IDactivite", IDactivite),
                ("agrement", self.dict_valeurs["num_agrement"]),
                ("date_debut", "1977-01-01"),
                ("date_fin", "2999-01-01"),
                ]
            DB.ReqInsert("agrements", listeDonnees)

        # Responsable d'activit�
        if "responsable_nom" in self.dict_valeurs and self.dict_valeurs["responsable_nom"] != "" :
            listeDonnees = [
                ("IDactivite", IDactivite),
                ("sexe", self.dict_valeurs["responsable_sexe"]),
                ("nom", self.dict_valeurs["responsable_nom"]),
                ("fonction", self.dict_valeurs["responsable_fonction"]),
                ("defaut", 1),
                ]
            DB.ReqInsert("responsables_activite", listeDonnees)

        # Groupes
        listeIDgroupe = []

        if "has_groupes" in self.dict_valeurs:

            # Groupe unique
            if self.dict_valeurs["has_groupes"] == False:
                listeDonnees = [("IDactivite", IDactivite), ("nom", _(u"Groupe unique")), ("ordre", 1), ("abrege", _(u"UNIQ"))]
                IDgroupe = DB.ReqInsert("groupes", listeDonnees)
                listeIDgroupe.append(IDgroupe)

            # Plusieurs groupes
            if self.dict_valeurs["has_groupes"] == True:
                nbreGroupes = self.dict_valeurs["nbre_groupes"]
                for index in range(1, nbreGroupes+1):
                    nom_groupe = self.dict_valeurs["nom_groupe#%d" % index]
                    abrege_groupe = CreationAbrege(nom_groupe)
                    if "capacite_max_groupe#%d" % index in self.dict_valeurs:
                        nbre_inscrits_max_groupe = self.dict_valeurs["capacite_max_groupe#%d" % index]
                    else :
                        nbre_inscrits_max_groupe = None
                    listeDonnees = [("IDactivite", IDactivite), ("nom", nom_groupe), ("ordre", index+1), ("abrege", abrege_groupe), ("nbre_inscrits_max", nbre_inscrits_max_groupe)]
                    IDgroupe = DB.ReqInsert("groupes", listeDonnees)
                    listeIDgroupe.append(IDgroupe)

        self.dict_valeurs["listeIDgroupe"] = listeIDgroupe

        # Pi�ces
        if "pieces" in self.dict_valeurs:
            for IDtype_piece in self.dict_valeurs["pieces"] :
                listeDonnees = [("IDactivite", IDactivite), ("IDtype_piece", IDtype_piece)]
                DB.ReqInsert("pieces_activites", listeDonnees)

        # Cotisations
        if "cotisations" in self.dict_valeurs:
            for IDtype_cotisation in self.dict_valeurs["cotisations"]:
                listeDonnees = [("IDactivite", IDactivite), ("IDtype_cotisation", IDtype_cotisation)]
                DB.ReqInsert("cotisations_activites", listeDonnees)

        # Renseignements
        if "renseignements" in self.dict_valeurs:
            for IDtype_renseignement in self.dict_valeurs["renseignements"]:
                listeDonnees = [("IDactivite", IDactivite), ("IDtype_renseignement", IDtype_renseignement)]
                DB.ReqInsert("renseignements_activites", listeDonnees)

        return True

    def Sauvegarde_tarifs(self, DB=None, listeTarifs=[]):
        # Tarifs
        dict_requetes = {"tarifs" : [], "tarifs_lignes" : []}

        # Recherche des prochains ID
        prochainIDtarif = DB.GetProchainID("tarifs")
        if DB.isNetwork == False:
            req = """SELECT max(IDligne) FROM tarifs_lignes;"""
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            if listeTemp[0][0] == None:
                prochainIDligne = 1
            else:
                prochainIDligne = listeTemp[0][0] + 1

        for track_tarif in listeTarifs :
            track_tarif.MAJ({
                "IDtarif": int(prochainIDtarif),
                })
            prochainIDtarif += 1
            dict_requetes["tarifs"].append(track_tarif)

            for track_ligne in track_tarif.lignes:
                track_ligne.MAJ({
                    "IDtarif": track_tarif.IDtarif,
                    "IDactivite": self.dict_valeurs["IDactivite"],
                    })
                if DB.isNetwork == False:
                    track_ligne.MAJ({"IDligne": int(prochainIDligne)})
                    prochainIDligne += 1
                dict_requetes["tarifs_lignes"].append(track_ligne)

        # Sauvegardes des tarifs et des lignes de tarifs
        for nom_table in list(dict_requetes.keys()) :
            if len(dict_requetes[nom_table]) > 0 :
                listeDonnees = []
                for track in dict_requetes[nom_table] :
                    ligne = track.Get_variables_pour_db()
                    if DB.isNetwork == False and nom_table == "tarifs_lignes":
                        ligne.append(track.IDligne)
                    listeDonnees.append(ligne)

                liste_champs = track.Get_champs_pour_db()
                liste_interro = track.Get_interrogations_pour_db()
                if DB.isNetwork == False and nom_table == "tarifs_lignes":
                    liste_champs += ", IDligne"
                    liste_interro += ", ?"

                DB.Executermany("INSERT INTO %s (%s) VALUES (%s)" % (track.nom_table, liste_champs, liste_interro), listeDonnees, commit=True)

        # Sauvegarde des combinaisons de tarifs
        for track_tarif in listeTarifs:
            if hasattr(track_tarif, "combi_tarifs"):
                # Sauvegarde des combinaisons
                for dict_combi in track_tarif.combi_tarifs :
                    listeDonnees = [("IDtarif", track_tarif.IDtarif), ("type", dict_combi["type"])]
                    IDcombi_tarif = DB.ReqInsert("combi_tarifs", listeDonnees)
                    # Sauvegarde des unit�s de combinaisons
                    for IDunite in dict_combi["unites"]:
                        listeDonnees = [("IDcombi_tarif", IDcombi_tarif), ("IDtarif", track_tarif.IDtarif),("IDunite", IDunite)]
                        DB.ReqInsert("combi_tarifs_unites", listeDonnees)


    def Quitter(self):
        self.EndModal(wx.ID_OK)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
