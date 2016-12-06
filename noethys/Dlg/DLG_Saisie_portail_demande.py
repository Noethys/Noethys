#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import wx.html as html
import datetime
import GestionDB
import FonctionsPerso
from Ctrl import CTRL_Bouton_image
from Utils import UTILS_Envoi_email
from Utils import UTILS_Facturation
from Utils import UTILS_Dates
from Utils import UTILS_Texte
from Utils import UTILS_Dialogs
from Dlg import DLG_Badgeage_grille
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")



class CTRL_Html(html.HtmlWindow):
    def __init__(self, parent, texte="", couleurFond=(255, 255, 255), style=wx.SIMPLE_BORDER):
        html.HtmlWindow.__init__(self, parent, -1, style=style)  # , style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        self.texte = ""
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(3)
        self.couleurFond = couleurFond
        font = self.parent.GetFont()
        self.SetFont(font)
        self.SetTexte(texte)

    def SetTexte(self, texte=""):
        self.texte = texte
        self.SetPage(u"""<BODY><FONT SIZE=3 COLOR='#000000'>%s</FONT></BODY>""" % texte)
        self.SetBackgroundColour(self.couleurFond)

    def GetTexte(self):
        return self.texte



class DatePickerCtrl(wx.DatePickerCtrl):
    def __init__(self, parent):
        wx.DatePickerCtrl.__init__(self, parent, -1, style=wx.DP_DROPDOWN)
        self.parent = parent
        self.Bind(wx.EVT_DATE_CHANGED, self.OnDateChanged)
        self.Bind(wx.EVT_CHILD_FOCUS, self.OnFocus)

    def OnFocus(self,event):
        event.Skip(False)       #évite la propagation vers le 'PySwigObject' object

    def SetDate(self, dateDD=None):
        jour = dateDD.day
        mois = dateDD.month-1
        annee = dateDD.year
        date = wx.DateTime()
        date.Set(jour, mois, annee)
        self.SetValue(date)

    def GetDate(self):
        date = self.GetValue()
        dateDD = datetime.date(date.GetYear(), date.GetMonth()+1, date.GetDay())
        return dateDD

    def OnDateChanged(self, event):
        self.GetParent().Sauvegarde()


# -------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Choix_modele(wx.Choice):
    def __init__(self, parent, categorie=None):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.categorie = categorie
        self.defaut = None
        self.MAJ()

    def SetCategorie(self, categorie=""):
        self.categorie = categorie
        self.defaut = None
        self.MAJ()
        self.SetID(self.defaut)

    def MAJ(self):
        selectionActuelle = self.GetID()
        listeItems = self.GetListeDonnees()
        #if len(listeItems) == 0 :
        #    self.Enable(False)
        #else:
        #    self.Enable(True)
        self.SetItems(listeItems)
        # Re-sélection après MAJ
        if selectionActuelle != None :
            self.SetID(selectionActuelle)
        else:
            # Sélection par défaut
            self.SetID(self.defaut)

    def GetListeDonnees(self):
        listeItems = []
        self.dictDonnees = {}
        if self.categorie == None :
            return listeItems

        DB = GestionDB.DB()
        req = """SELECT IDmodele, nom, description, defaut
        FROM modeles_emails
        WHERE categorie='%s'
        ORDER BY nom;""" % self.categorie
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 0
        for IDmodele, nom, description, defaut in listeDonnees :
            listeItems.append(nom)
            self.dictDonnees[index] = {"ID" : IDmodele}
            if defaut == 1 :
                self.defaut = IDmodele
            index += 1
        return listeItems

    def SetID(self, ID=None):
        for index, values in self.dictDonnees.iteritems():
            if values != None and values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]

# -------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Solde(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, id=-1, size=(90, -1), name="panel_solde", style=wx.ALIGN_RIGHT|wx.TE_READONLY)
        self.parent = parent
        font = self.GetFont()
        font.SetWeight(wx.BOLD)
        self.SetFont(font)
        self.SetToolTipString(_(u"Solde du compte de la famille"))

    def MAJ(self, IDfamille=None):
        DB = GestionDB.DB()
        req = """SELECT IDfamille, SUM(montant)
        FROM reglements
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
        WHERE IDfamille=%d
        GROUP BY IDfamille
        ;""" % IDfamille
        DB.ExecuterReq(req)
        listeReglements = DB.ResultatReq()
        dictReglements = {}
        for IDfamille, montant in listeReglements :
            if dictReglements.has_key(IDfamille) == False :
                dictReglements[IDfamille] = FloatToDecimal(0.0)
                dictReglements[IDfamille] += FloatToDecimal(montant)

        # Récupération des prestations
        req = """SELECT IDfamille, SUM(montant)
        FROM prestations
        WHERE IDfamille=%d
        GROUP BY IDfamille
        ;""" % IDfamille
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        dict_soldes = {}
        for IDfamille, montant in listePrestations :
            montant = FloatToDecimal(montant)
            if dictReglements.has_key(IDfamille) == True :
                regle = dictReglements[IDfamille]
            else :
                regle = FloatToDecimal(0.0)
            dict_soldes[IDfamille] = regle - montant

        DB.Close()

        # Affichage du solde
        if dict_soldes.has_key(IDfamille) :
            solde = dict_soldes[IDfamille]
        else :
            solde = FloatToDecimal(0.0)
        self.SetSolde(solde)


    def SetSolde(self, montant=FloatToDecimal(0.0)):
        """ MAJ integrale du controle avec MAJ des donnees """
        if montant > FloatToDecimal(0.0):
            label = u"+ %.2f %s" % (montant, SYMBOLE)
            self.SetBackgroundColour("#C4BCFC")  # Bleu
        elif montant == FloatToDecimal(0.0):
            label = u"0.00 %s" % SYMBOLE
            self.SetBackgroundColour("#5DF020")  # Vert
        else:
            label = u"- %.2f %s" % (-montant, SYMBOLE)
            self.SetBackgroundColour("#F81515")  # Rouge
        self.SetValue(label)
        self.Layout()
        self.Refresh()



# -------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, track=None, tracks=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.track = track
        self.tracks = tracks

        # Bandeau spécial
        self.panel_bandeau = wx.Panel(self, -1)
        self.panel_bandeau.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.ctrl_image = wx.StaticBitmap(self.panel_bandeau, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Calendrier_modifier.png"), wx.BITMAP_TYPE_ANY))
        self.label_action = wx.StaticText(self.panel_bandeau, -1, _(u"Réservation de dates"))
        self.label_action.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.ligne1 = wx.StaticLine(self.panel_bandeau, -1)
        self.label_horodatage = wx.StaticText(self.panel_bandeau, -1, _(u"Mardi 26 juillet a 14h10"))
        self.label_horodatage.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        # Navigation
        self.bouton_premier = wx.BitmapButton(self.panel_bandeau, 10, wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Premier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_precedent = wx.BitmapButton(self.panel_bandeau, 20, wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Precedent.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_precedent.SetMinSize((60, -1))
        self.bouton_suivant = wx.BitmapButton(self.panel_bandeau, 30, wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Suivant.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_suivant.SetMinSize((60, -1))
        self.bouton_dernier = wx.BitmapButton(self.panel_bandeau, 40, wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Dernier.png"), wx.BITMAP_TYPE_ANY))
        self.ligne2 = wx.StaticLine(self.panel_bandeau, -1)

        # Demande
        self.box_demande_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Demande"))

        self.label_famille = wx.StaticText(self, -1, _(u"Famille :"))
        self.ctrl_famille = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY)
        font = self.ctrl_famille.GetFont()
        font.SetWeight(wx.BOLD)
        self.ctrl_famille.SetFont(font)

        self.bouton_famille = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_ANY))

        self.label_solde = wx.StaticText(self, -1, _(u"Solde :"))
        self.ctrl_solde = CTRL_Solde(self)

        self.label_description = wx.StaticText(self, -1, _(u"Description :"))
        self.ctrl_description = CTRL_Html(self, couleurFond=self.GetBackgroundColour())
        self.ctrl_description.SetMinSize((-1, 130))

        self.label_commentaire = wx.StaticText(self, -1, _(u"Commentaire :"))
        self.ctrl_commentaire = CTRL_Html(self, couleurFond=self.GetBackgroundColour())
        self.ctrl_commentaire.SetMinSize((-1, 30))

        # Traitement
        self.box_traitement_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Traitement"))

        self.label_etat = wx.StaticText(self, -1, _(u"Etat :"), style=wx.ALIGN_RIGHT)
        self.radio_attente = wx.RadioButton(self, -1, _(u"En attente"), style=wx.RB_GROUP)
        self.radio_validation = wx.RadioButton(self, -1, _(u"Traité le"))
        self.ctrl_date_validation = DatePickerCtrl(self)

        self.image_email_reponse = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Emails_exp.png"), wx.BITMAP_TYPE_ANY))
        self.label_email_reponse = wx.StaticText(self, -1, "")

        self.label_reponse = wx.StaticText(self, -1, _(u"Réponse :"))
        self.ctrl_reponse = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.ctrl_reponse.SetMinSize((-1, 50))

        # Email
        self.label_email = wx.StaticText(self, -1, _(u"Email :"))
        self.bouton_envoyer = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_editeur = CTRL_Bouton_image.CTRL(self, texte=_(u"Editeur d'Emails"), cheminImage="Images/32x32/Editeur_email.png")
        self.label_modele = wx.StaticText(self, -1, _(u"Modèle :"))
        self.ctrl_modele_email = CTRL_Choix_modele(self, categorie=None)
        self.ctrl_modele_email.SetMinSize((280, -1))
        self.bouton_gestion_modeles = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        # CTRL Grille des conso
        self.ctrl_grille = DLG_Badgeage_grille.CTRL(self)
        self.ctrl_grille.Show(False)

        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_automatique = CTRL_Bouton_image.CTRL(self, texte=_(u"Automatique"), cheminImage="Images/32x32/Magique.png")
        self.bouton_manuel = CTRL_Bouton_image.CTRL(self, texte=_(u"Manuel"), cheminImage="Images/32x32/Edition.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnNavigation, self.bouton_premier)
        self.Bind(wx.EVT_BUTTON, self.OnNavigation, self.bouton_precedent)
        self.Bind(wx.EVT_BUTTON, self.OnNavigation, self.bouton_suivant)
        self.Bind(wx.EVT_BUTTON, self.OnNavigation, self.bouton_dernier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFamille, self.bouton_famille)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioEtat, self.radio_attente)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioEtat, self.radio_validation)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEnvoyer, self.bouton_envoyer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonEditeur, self.bouton_editeur)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModeles, self.bouton_gestion_modeles)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAutomatique, self.bouton_automatique)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonManuel, self.bouton_manuel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Init
        self.Importation()
        self.MAJ()


    def __set_properties(self):
        self.SetTitle(_(u"Traitement des demandes"))
        self.bouton_premier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la première demande de la liste")))
        self.bouton_precedent.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la demande précédente dans la liste")))
        self.bouton_suivant.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la demande suivante dans la liste")))
        self.bouton_dernier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la dernière demande de la liste")))
        self.bouton_famille.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ouvrir la fiche famille")))
        self.radio_attente.SetToolTip(wx.ToolTip(_(u"Demande en attente")))
        self.radio_validation.SetToolTip(wx.ToolTip(_(u"Demande traitée")))
        self.ctrl_date_validation.SetToolTip(wx.ToolTip(_(u"Date de traitement de la demande")))
        self.ctrl_reponse.SetToolTip(wx.ToolTip(_(u"Cette réponse apparaîtra sur le portail et dans l'email de confirmation (si vous utilisez le mot-clé {DEMANDE_REPONSE} dans l'email). Cette réponse est générée automatiquement par Noethys mais vous pouvez la modifier librement.")))
        self.bouton_envoyer.SetToolTipString(_(u"Cliquez ici pour envoyer directement un email de réponse à la famille sans passer par l'éditeur d'Emails."))
        self.bouton_editeur.SetToolTipString(_(u"Cliquez ici pour ouvrir l'éditeur d'Email afin d'envoyer un email de réponse à la famille"))
        self.ctrl_modele_email.SetToolTipString(_(u"Sélectionnez un modèle d'email"))
        self.bouton_gestion_modeles.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des modèles d'emails"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_automatique.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer le traitement automatique de cette demande")))
        self.bouton_manuel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer le traitement manuel de cette demande")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer la fenêtre")))
        self.SetMinSize((800, 670))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)

        # Bandeau
        sizer_bandeau = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_bandeau = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)

        # Image
        grid_sizer_bandeau.Add(self.ctrl_image, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # Titre
        sizer_titre = wx.BoxSizer(wx.VERTICAL)

        sizer_titre.Add(self.label_action, 0, 0, 0)
        sizer_titre.Add(self.ligne1, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 1)
        sizer_titre.Add(self.label_horodatage, 0, 0, 0)
        grid_sizer_bandeau.Add(sizer_titre, 1, wx.EXPAND, 0)

        # Navigation
        grid_sizer_navigation = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_navigation.Add(self.bouton_premier, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_precedent, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_suivant, 0, 0, 0)
        grid_sizer_navigation.Add(self.bouton_dernier, 0, 0, 0)
        grid_sizer_bandeau.Add(grid_sizer_navigation, 1, wx.EXPAND, 0)

        grid_sizer_bandeau.AddGrowableCol(1)
        sizer_bandeau.Add(grid_sizer_bandeau, 1, wx.EXPAND | wx.ALL, 10)
        sizer_bandeau.Add(self.ligne2, 0, wx.EXPAND, 0)
        self.panel_bandeau.SetSizer(sizer_bandeau)
        grid_sizer_base.Add(self.panel_bandeau, 1, wx.EXPAND, 0)

        # Contenu
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        # Demande
        box_demande = wx.StaticBoxSizer(self.box_demande_staticbox, wx.VERTICAL)
        grid_sizer_demande = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)

        # Famille
        grid_sizer_demande.Add(self.label_famille, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)

        grid_sizer_famille = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_famille.Add(self.ctrl_famille, 1, wx.EXPAND, 0)
        grid_sizer_famille.Add(self.bouton_famille, 0, 0, 0)
        grid_sizer_famille.Add( (20, 5), 0, 0, 0)
        grid_sizer_famille.Add(self.label_solde, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_famille.Add(self.ctrl_solde, 0, 0, 0)
        grid_sizer_famille.AddGrowableCol(0)
        grid_sizer_demande.Add(grid_sizer_famille, 1, wx.EXPAND, 0)

        # Description
        grid_sizer_demande.Add(self.label_description, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_demande.Add(self.ctrl_description, 0, wx.EXPAND, 0)

        # commentaire
        grid_sizer_demande.Add(self.label_commentaire, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_demande.Add(self.ctrl_commentaire, 0, wx.EXPAND, 0)

        grid_sizer_demande.AddGrowableRow(1)
        grid_sizer_demande.AddGrowableRow(2)
        grid_sizer_demande.AddGrowableCol(1)

        box_demande.Add(grid_sizer_demande, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_demande, 0, wx.EXPAND, 0)

        # Traitement
        box_traitement = wx.StaticBoxSizer(self.box_traitement_staticbox, wx.VERTICAL)
        grid_sizer_traitement = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)

        # Etat
        grid_sizer_traitement.Add(self.label_etat, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        self.label_etat.SetMinSize((self.label_commentaire.GetSize()[0], -1))

        self.grid_sizer_etat = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        self.grid_sizer_etat.Add(self.radio_attente, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.grid_sizer_etat.Add(self.radio_validation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.grid_sizer_etat.Add(self.ctrl_date_validation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.grid_sizer_etat.Add( (5, 5), 0, wx.EXPAND, 0)
        self.grid_sizer_etat.Add(self.image_email_reponse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.grid_sizer_etat.Add(self.label_email_reponse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.grid_sizer_etat.AddGrowableCol(3)
        grid_sizer_traitement.Add(self.grid_sizer_etat, 1, wx.EXPAND, 0)

        # Réponse
        grid_sizer_traitement.Add(self.label_reponse, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_traitement.Add(self.ctrl_reponse, 0, wx.EXPAND, 0)

        # Email
        grid_sizer_traitement.Add( self.label_email, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_email = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_email.Add(self.bouton_envoyer, 0, wx.EXPAND, 0)
        grid_sizer_email.Add(self.bouton_editeur, 0, wx.EXPAND, 0)
        grid_sizer_email.Add( (5, 5), 0, 0, 0)
        grid_sizer_email.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_email.Add(self.ctrl_modele_email, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_email.Add(self.bouton_gestion_modeles, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        #grid_sizer_email.AddGrowableCol(2)
        grid_sizer_traitement.Add(grid_sizer_email, 1, wx.EXPAND, 0)

        grid_sizer_traitement.AddGrowableRow(1)
        grid_sizer_traitement.AddGrowableCol(1)

        box_traitement.Add(grid_sizer_traitement, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_traitement, 0, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        grid_sizer_base.Add(self.ctrl_grille, 1, wx.ALL | wx.EXPAND, 10)

        # Commandes
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_commandes.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_automatique, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_manuel, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_commandes.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_commandes, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()

    def Importation(self):
        DB = GestionDB.DB()

        # Récupération des unités de réservations
        req = """SELECT IDunite, IDactivite, nom, unites_principales, unites_secondaires, ordre
        FROM portail_unites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictUnites = {}
        for IDunite, IDactivite, nom, unites_principales, unites_secondaires, ordre in listeDonnees :
            unites_principales = UTILS_Texte.ConvertStrToListe(unites_principales)
            unites_secondaires = UTILS_Texte.ConvertStrToListe(unites_secondaires)
            self.dictUnites[IDunite] = {
                "IDactivite" : IDactivite, "nom" : nom, "unites_principales" : unites_principales,
                "unites_secondaires" : unites_secondaires, "ordre" : ordre,
                }

        # Récupération des activités
        req = """SELECT IDactivite, nom, portail_reservations_limite, portail_reservations_absenti
        FROM activites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.dictActivites = {}
        for IDactivite, nom, portail_reservations_limite, portail_reservations_absenti in listeDonnees :
            self.dictActivites[IDactivite] = {
                "nom" : nom, "portail_reservations_limite" : portail_reservations_limite,
                "portail_reservations_absenti" : portail_reservations_absenti,
                }

        DB.Close()

    def OnClose(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.Sauvegarde()
        event.Skip()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.Sauvegarde()
        self.EndModal(wx.ID_CANCEL)

    def OnRadioEtat(self, event=None):
        self.ctrl_date_validation.Enable(self.radio_validation.GetValue())
        self.ctrl_reponse.Enable(self.radio_validation.GetValue())
        self.bouton_envoyer.Enable(self.radio_validation.GetValue())
        self.bouton_editeur.Enable(self.radio_validation.GetValue())
        self.label_modele.Enable(self.radio_validation.GetValue())
        self.ctrl_modele_email.Enable(self.radio_validation.GetValue())
        self.bouton_gestion_modeles.Enable(self.radio_validation.GetValue())
        self.bouton_automatique.Enable(not self.radio_validation.GetValue())
        self.bouton_manuel.Enable(not self.radio_validation.GetValue())

        if self.radio_validation.GetValue() == True :
            self.panel_bandeau.SetBackgroundColour(wx.Colour(220, 255, 220))
        else :
            self.panel_bandeau.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.panel_bandeau.Refresh()

    def OnBoutonModeles(self, event):
        import DLG_Modeles_emails
        dlg = DLG_Modeles_emails.Dialog(self, categorie=self.categorie_email)
        dlg.ShowModal()
        dlg.Destroy()
        ID = self.ctrl_modele_email.GetID()
        self.ctrl_modele_email.MAJ()
        self.ctrl_modele_email.SetID(ID)

    def Sauvegarde(self):
        if self.radio_validation.GetValue() == True :
            etat = "validation"
            if self.ctrl_reponse.GetValue() == "" :
                reponse = None
            else :
                reponse = self.ctrl_reponse.GetValue()
            traitement_date = self.ctrl_date_validation.GetDate()
            self.ctrl_date_validation.Enable(True)
            self.panel_bandeau.SetBackgroundColour(wx.Colour(220, 255, 220))
        else :
            etat = "attente"
            traitement_date = None
            reponse = None
            self.ctrl_date_validation.SetDate(datetime.date.today())
            self.ctrl_date_validation.Enable(False)
            self.panel_bandeau.SetBackgroundColour(wx.Colour(255, 255, 255))

        # MAJ du track
        self.track.reponse = reponse
        self.track.etat = etat
        self.track.traitement_date = traitement_date
        self.panel_bandeau.Refresh()
        self.track.Refresh()

        # Sauvegarde dans la base
        DB = GestionDB.DB()
        DB.ReqMAJ("portail_actions", [("etat", etat), ("reponse", reponse), ("traitement_date", traitement_date), ("email_date", self.track.email_date)], "IDaction", self.track.IDaction)
        DB.Close()

    def SetEtat(self, etat="attente", traitement_date=None):
        if etat == "attente" :
            self.radio_attente.SetValue(True)
        else :
            self.radio_validation.SetValue(True)
            if traitement_date != None :
                self.ctrl_date_validation.SetDate(traitement_date)
        self.OnRadioEtat()

    def MAJ(self):
        if self.track == None :
            return

        # Catégorie de l'action
        self.label_action.SetLabel(self.track.categorie_label)

        # Image de la catégorie
        dict_images = {
            "reglements" : "Reglement.png",
            "factures" : "Facture.png",
            "inscriptions" : "Activite.png",
            "reservations" : "Calendrier_modifier.png",
            }
        self.ctrl_image.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/32x32/%s" % dict_images[self.track.categorie]), wx.BITMAP_TYPE_PNG))

        # Horodatage
        dt = UTILS_Dates.DateEngEnDateDDT(self.track.horodatage)
        self.label_horodatage.SetLabel(dt.strftime("%d/%m/%Y  %H:%M:%S"))

        # Famille
        self.ctrl_famille.SetValue(self.track.famille)
        self.ctrl_solde.MAJ(IDfamille=self.track.IDfamille)

        # Description
        description = self.track.description

        if self.track.categorie == "reservations" :

            # Recherche si d'autres réservations existent pour le même individu et la même période
            liste_demandes_avant = []
            liste_demandes_apres = []
            for track in self.tracks :
                if track.IDfamille == self.track.IDfamille and track.IDindividu == self.track.IDindividu and track.IDperiode == self.track.IDperiode :
                    if track.horodatage < self.track.horodatage :
                        liste_demandes_avant.append(track)
                    if track.horodatage > self.track.horodatage :
                        liste_demandes_apres.append(track)


            if len(liste_demandes_avant) > 1 :
                affiche_s_avant = "s"
            else :
                affiche_s_avant = ""
            if len(liste_demandes_apres) > 1:
                affiche_s_apres = "s"
            else :
                affiche_s_apres = ""

            if len(liste_demandes_avant) > 0 and len(liste_demandes_apres) == 0 :
                texte_autres_demandes = _(u"\n(Remarque : Il existe pour la même période %d réservation%s plus ancienne%s)") % (len(liste_demandes_avant), affiche_s_avant, affiche_s_avant)
            elif len(liste_demandes_avant) == 0 and len(liste_demandes_apres) > 0 :
                texte_autres_demandes = _(u"\n(Remarque : Il existe pour la même période %d réservation%s plus récente%s)") % (len(liste_demandes_apres), affiche_s_apres, affiche_s_apres)
            elif len(liste_demandes_avant) > 0 and len(liste_demandes_apres) > 0 :
                texte_autres_demandes = _(u"\n(Remarque : Il existe pour la même période %d réservation%s plus ancienne%s et %d plus récente%s)") % (len(liste_demandes_avant), affiche_s_avant, affiche_s_avant, len(liste_demandes_apres), affiche_s_apres)
            else :
                texte_autres_demandes = ""

            # Recherche le détail des réservations associées
            DB = GestionDB.DB()
            req = """SELECT IDreservation, date, IDinscription, portail_reservations.IDunite, etat, portail_unites.nom
            FROM portail_reservations
            LEFT JOIN portail_unites ON portail_unites.IDunite = portail_reservations.IDunite
            WHERE IDaction=%d ORDER BY date, portail_reservations.IDunite;""" % self.track.IDaction
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            liste_lignes = []
            for IDreservation, date, IDinscription, IDunite, etat, nom_unite in listeDonnees :
                date = UTILS_Dates.DateEngEnDateDD(date)
                if etat == 1 :
                    action = _(u"Ajout")
                else :
                    action = _(u"Suppression")
                ligne = _(u"<li>%s du %s (%s)</li>") % (action, UTILS_Dates.DateComplete(date), nom_unite)
                liste_lignes.append(ligne)

            description += u" :"

            # Rajout du texte autres demandes
            if len(texte_autres_demandes) > 0 :
                description += u"<br><FONT SIZE=2 COLOR='red'>%s</FONT>" % texte_autres_demandes

            # Rajout du détail des réservations
            description += u"<p><ul>%s</ul></p>" % "".join(liste_lignes)


        self.ctrl_description.SetTexte(description)

        # Commentaire
        if self.track.commentaire != None :
            self.ctrl_commentaire.SetTexte(self.track.commentaire)

        # Etat
        self.SetEtat(self.track.etat, self.track.traitement_date)

        # Réponse
        if self.track.reponse != None :
            reponse = self.track.reponse
        else :
            reponse = ""
        self.ctrl_reponse.SetValue(reponse)

        # Email
        if self.track.categorie == "reservations" : self.categorie_email = "portail_demande_reservation"
        if self.track.categorie == "reglements" : self.categorie_email = "portail_demande_recu_reglement"
        if self.track.categorie == "factures" : self.categorie_email = "portail_demande_facture"
        if self.track.categorie == "inscriptions" : self.categorie_email = "portail_demande_inscription"
        self.ctrl_modele_email.SetCategorie(self.categorie_email)

        self.MAJ_email_date()

        # Sélection du modèle attribué à la période
        if self.track.categorie == "reservations" and self.track.periode_IDmodele != None :
            self.ctrl_modele_email.SetID(self.track.periode_IDmodele)

        # Navigation
        index = self.tracks.index(self.track)
        self.bouton_premier.Enable(index > 0)
        self.bouton_precedent.Enable(index > 0)
        self.bouton_suivant.Enable(index < len(self.tracks)-1)
        self.bouton_dernier.Enable(index < len(self.tracks)-1)

        # Titre de la fenêtre
        self.SetTitle(_(u"Traitement des demandes [%d/%d]") % (index+1, len(self.tracks)))

        # Sélection du track dans le listview
        self.Freeze()
        self.track.Select()
        self.Thaw()

    def MAJ_email_date(self):
        if self.track.email_date != None :
            self.image_email_reponse.Show(True)
            self.label_email_reponse.Show(True)
            self.label_email_reponse.SetLabel(_(u"Email de réponse envoyé le %s") % UTILS_Dates.DateDDEnFr(self.track.email_date))
        else :
            self.image_email_reponse.Show(False)
            self.label_email_reponse.Show(False)
        self.grid_sizer_etat.Layout()

    def OnNavigation(self, event):
        self.Sauvegarde()

        ID = event.GetId()
        index = self.tracks.index(self.track)
        if ID == 10 :
            # Premier
            self.track = self.tracks[0]
        elif ID == 20 :
            # Précédent
            self.track = self.tracks[index-1]
        elif ID == 30 :
            # Suivant
            self.track = self.tracks[index+1]
        elif ID == 40 :
            # Dernier
            self.track = self.tracks[len(self.tracks)-1]

        self.MAJ()

    def OnBoutonFamille(self, event):
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, self.track.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_solde.MAJ(IDfamille=self.track.IDfamille)

    def OnBoutonAutomatique(self, event):
        self.Traitement(mode="automatique")

    def OnBoutonManuel(self, event):
        self.Traitement(mode="manuel")

    def Traitement(self, mode="automatique"):
        traitement = Traitement(parent=self, track=self.track, mode=mode)
        resultat = traitement.Traiter()

        # Sauvegarde de l'état
        if resultat != False :
            if resultat["etat"] == True :

                # La demande a été validée
                self.SetEtat(etat="valide", traitement_date=datetime.date.today())

                # Mémorisation de la réponse
                if resultat.has_key("reponse") and resultat["reponse"] not in (None, "") :
                    self.ctrl_reponse.SetValue(resultat["reponse"])

                # Enregistrement de la demande
                self.Sauvegarde()

        # Réactualise le solde
        self.ctrl_solde.MAJ(IDfamille=self.track.IDfamille)

    def OnBoutonEnvoyer(self, event=None):
        self.Envoyer(visible=False)

    def OnBoutonEditeur(self, event=None):
        self.Envoyer(visible=True)

    def Envoyer(self, visible=True):
        """ Envoyer la réponse par email """
        if self.ctrl_reponse.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune réponse.\n\nSouhaitez-vous tout de même envoyer l'email ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

        IDmodele = self.ctrl_modele_email.GetID()
        if IDmodele == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un modèle d'Email dans la liste proposée !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Envoi par Email
        if self.track.categorie == "reservations" :
            nomDoc = FonctionsPerso.GenerationNomDoc("RESERVATIONS", "pdf")
        else :
            nomDoc = False

        resultat = UTILS_Envoi_email.EnvoiEmailFamille(parent=self, IDfamille=self.track.IDfamille, nomDoc=nomDoc, categorie=self.categorie_email, listeAdresses=[], visible=visible, log=self.track, CreationPDF=self.CreationPDF, IDmodele=IDmodele)

        # Mémorise la date de l'envoi de l'email
        if resultat == True :
            self.track.email_date = datetime.date.today()
            self.MAJ_email_date()

    def CreationPDF(self, nomDoc="", afficherDoc=True):
        """ Création du PDF pour Email """

        # Génération des champs de fusion de la demande
        dict_champs = {}
        dict_champs["{DEMANDE_HORODATAGE}"] = UTILS_Dates.DateEngEnDateDDT(self.track.horodatage).strftime("%d/%m/%Y %Hh%M")
        dict_champs["{DEMANDE_DESCRIPTION}"] = self.track.description
        dict_champs["{DEMANDE_COMMENTAIRE}"] = self.track.commentaire
        dict_champs["{DEMANDE_TRAITEMENT_DATE}"] = UTILS_Dates.DateDDEnFr(self.ctrl_date_validation.GetDate())
        dict_champs["{DEMANDE_REPONSE}"] = self.ctrl_reponse.GetValue()

        # Génération des autres champs de fusion
        if self.track.categorie == "reservations" :
            dict_champs["{PERIODE_NOM}"] = self.track.periode_nom
            dict_champs["{PERIODE_DATE_DEBUT}"] = UTILS_Dates.DateDDEnFr(self.track.periode_date_debut)
            dict_champs["{PERIODE_DATE_FIN}"] = UTILS_Dates.DateDDEnFr(self.track.periode_date_fin)

            # Génération du PDF des réservations
            traitement = Traitement(parent=self, track=self.track)
            traitement.Init_grille(ctrl_grille=self.ctrl_grille)
            dict_champs_reservations = self.ctrl_grille.grille.CreationPDF(nomDoc=nomDoc, afficherDoc=afficherDoc)
            dict_champs.update(dict_champs_reservations)

        # Génération du PDF de la facture
        #facturation = UTILS_Facturation.Facturation()
        #resultat = facturation.Impression(listeFactures=[IDfacture,], nomDoc=nomDoc, afficherDoc=afficherDoc, afficherOptions=self.afficherOptions)
        #if resultat == False :
        #    return False
        #dictChampsFusion, dictPieces = resultat
        #dict_champs = dictChampsFusion[IDfacture]

        return dict_champs


# ----------------------------------------------------------------------------------------------

class Traitement():
    def __init__(self, parent=None, track=None, mode="automatique"):
        """ Mode = automatique ou manuel """
        self.parent = parent
        self.track = track
        self.mode = mode

        # Récupération des paramètres de l'action
        self.dict_parametres = self.GetParametres()

    def EcritLog(self, message="", log_jumeau=None):
        self.track.EcritLog(message)
        if log_jumeau != None :
            log_jumeau.EcritLog(message)

    def GetParametres(self):
        """ Récupération des paramètres de l'action """
        dict_parametres = {}
        if self.track.parametres and len(self.track.parametres) > 0 :
            for donnee in self.track.parametres.split("#") :
                key, valeur = donnee.split("=")
                dict_parametres[key] = valeur
        return dict_parametres

    def Traiter(self):
        """ Traitement des actions en fonction de la catégorie """
        self.EcritLog(_(u"Lancement du traitement de la demande..."))
        resultat = False

        # Traitement des reçus de règlements
        if self.track.categorie == "reglements" :
            resultat = self.Traitement_recus()

        # Traitement des factures
        if self.track.categorie == "factures" :
            resultat = self.Traitement_factures()

        # Traitement des inscriptions
        if self.track.categorie == "inscriptions" :
            resultat = self.Traitement_inscriptions()

        # Traitement des réservations
        if self.track.categorie == "reservations" :
            resultat = self.Traitement_reservations()

        self.EcritLog(_(u"Fin du traitement."))

        # Sélection de l'état 'Traité'
        return resultat

    def Traitement_recus(self):
        # Récupération des paramètres
        IDreglement = int(self.dict_parametres["IDreglement"])

        # Ouverture de la fenêtre d'édition d'un reçu
        from Dlg import DLG_Impression_recu
        dlg_impression = DLG_Impression_recu.Dialog(self.parent, IDreglement=IDreglement)

        # Traitement manuel
        if self.mode == "manuel" :
            self.EcritLog(_(u"Ouverture de la fenêtre d'édition d'un reçu."))
            if self.dict_parametres["methode_envoi"] == "email" :
                self.EcritLog(_(u"Veuillez envoyer ce reçu de règlement par Email."))
                reponse = _(u"Reçu de règlement envoyé par Email.")
            elif self.dict_parametres["methode_envoi"] == "courrier" :
                self.EcritLog(_(u"Veuillez imprimer le reçu de règlement pour un envoi par courrier."))
                reponse = _(u"Reçu de règlement envoyé par courrier.")
            else :
                self.EcritLog(_(u"Veuillez imprimer le reçu de règlement pour un retrait sur site."))
                reponse = _(u"Reçu de règlement disponible au retrait.")
            dlg_impression.ShowModal()
            dlg_impression.Destroy()

            return {"etat" : True, "reponse" : reponse}

        # Traitement automatique
        if self.mode == "automatique" :
            nomDoc = FonctionsPerso.GenerationNomDoc("RECU", "pdf")
            categorie = "recu_reglement"

            # Affichage du PDF pour envoi par courrier ou retrait sur site
            if self.dict_parametres["methode_envoi"] != "email" :
                message = _(u"Le reçu de règlement va être généré au format PDF et ouvert dans votre lecteur de PDF.\n\n")
                if self.dict_parametres["methode_envoi"] == "courrier" :
                    message += _(u"Veuillez l'imprimer et l'envoyer par courrier.")
                else :
                    message += _(u"Veuillez l'imprimer et le conserver pour un retrait sur site.")
                dlg = wx.MessageDialog(self.parent, message, _(u"Impression d'un reçu"), wx.OK|wx.OK_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse == wx.ID_CANCEL :
                    self.EcritLog(_(u"Interruption du traitement par l'utilisateur."))
                    return False

                dictChamps = dlg_impression.CreationPDF(nomDoc=nomDoc, afficherDoc=True)
                if dictChamps == False :
                    dlg_impression.Destroy()
                    self.EcritLog(_(u"[ERREUR] La génération du reçu au format PDF a rencontré une erreur."))
                    return False

                self.EcritLog(_(u"La génération du reçu est terminée."))
                if self.dict_parametres["methode_envoi"] == "courrier" :
                    self.EcritLog(_(u"Veuillez imprimer le reçu de règlement pour un envoi par courrier."))
                    reponse = _(u"Reçu de règlement envoyé par courrier.")
                else :
                    self.EcritLog(_(u"Veuillez imprimer le reçu de règlement pour un retrait sur site."))
                    reponse = _(u"Reçu de règlement disponible au retrait.")

            # Envoi par Email
            if self.dict_parametres["methode_envoi"] == "email" :
                resultat = UTILS_Envoi_email.EnvoiEmailFamille(parent=dlg_impression, IDfamille=self.track.IDfamille, nomDoc=nomDoc, categorie=categorie, visible=False, log=self.track)
                reponse = _(u"Reçu de règlement envoyé par Email.")

            # Mémorisation de l'édition du reçu
            dlg_impression.Sauvegarder(demander=False)
            dlg_impression.Destroy()

            return {"etat" : True, "reponse" : reponse}



    def Traitement_factures(self):
        # Récupération des paramètres
        IDfacture = int(self.dict_parametres["IDfacture"])
        edition = Edition_facture(parent=self.parent, IDfacture=IDfacture, IDfamille=self.track.IDfamille)

        # Traitement manuel
        if self.mode == "manuel" :
            if self.dict_parametres["methode_envoi"] == "email" :
                self.EcritLog(_(u"Veuillez envoyer cette facture par Email."))

                resultat = edition.EnvoyerEmail(visible=True)
                if resultat == False :
                    self.EcritLog(_(u"La facture n'a pas été envoyée par Email."))
                    return False

                reponse = _(u"Facture envoyée par Email.")

            elif self.dict_parametres["methode_envoi"] == "courrier" :
                self.EcritLog(_(u"Veuillez imprimer la facture pour un envoi par courrier."))
                reponse = _(u"Facture envoyée par courrier.")
                edition.Reedition()
            else :
                self.EcritLog(_(u"Veuillez imprimer la facture pour un retrait sur site."))
                reponse = _(u"Facture disponible au retrait.")
                edition.Reedition()

            return {"etat" : True, "reponse" : reponse}

        # Traitement automatique
        if self.mode == "automatique" :

            # Affichage du PDF pour envoi par courrier ou retrait sur site
            if self.dict_parametres["methode_envoi"] != "email" :
                message = _(u"La facture va être générée au format PDF et ouverte dans votre lecteur de PDF.\n\n")
                if self.dict_parametres["methode_envoi"] == "courrier" :
                    message += _(u"Veuillez l'imprimer et l'envoyer par courrier.")
                else :
                    message += _(u"Veuillez l'imprimer et le conserver pour un retrait sur site.")
                dlg = wx.MessageDialog(self.parent, message, _(u"Impression d'une facture"), wx.OK|wx.OK_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse == wx.ID_CANCEL :
                    self.EcritLog(_(u"Interruption du traitement par l'utilisateur."))
                    return False

                edition.Reedition(afficherOptions=False)

                self.EcritLog(_(u"La génération de la facture est terminée."))
                if self.dict_parametres["methode_envoi"] == "courrier" :
                    self.EcritLog(_(u"Veuillez imprimer la facture pour un envoi par courrier."))
                    reponse = _(u"Facture envoyée par courrier.")
                else :
                    self.EcritLog(_(u"Veuillez imprimer la facture pour un retrait sur site."))
                    reponse = _(u"Facture disponible au retrait.")

            # Envoi par Email
            if self.dict_parametres["methode_envoi"] == "email" :
                if len(listeAdresses) == 0 :
                    self.EcritLog(_(u"Aucune adresse Email n'a été sélectionnée."))
                    return False

                resultat = edition.EnvoyerEmail(visible=False)
                if resultat == False :
                    self.EcritLog(_(u"La facture n'a pas été envoyée par Email."))
                    return False

                reponse = _(u"Facture envoyée par Email.")

            return {"etat" : True, "reponse" : reponse}


    def Traitement_inscriptions(self):
        # Récupération des paramètres
        IDactivite = int(self.dict_parametres["IDactivite"])
        IDgroupe = int(self.dict_parametres["IDgroupe"])

        # Traitement manuel ou automatique
        if self.mode == "manuel" or self.mode == "automatique" :

            # Création du texte d'intro
            DB = GestionDB.DB()
            req = """SELECT nom, prenom, date_naiss FROM individus WHERE IDindividu=%d;""" % self.track.IDindividu
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) > 0 :
                nom, prenom, date_naiss = listeDonnees[0]
                if date_naiss != None :
                    date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)
                    today = datetime.date.today()
                    age = _(u"%d ans") % ((today.year - date_naiss.year) - int((today.month, today.day) < (date_naiss.month, date_naiss.day)))
                else :
                    age = _(u"Âge inconnu")
            intro = _(u"Confirmez l'inscription de %s (%s) à l'activité sélectionnée et sur le groupe demandé par la famille." % (prenom, age))

            from Dlg import DLG_Inscription
            dlg = DLG_Inscription.Dialog(self.parent, mode="saisie", IDindividu=self.track.IDindividu, IDfamille=self.track.IDfamille, intro=intro)
            dlg.bouton_activites.Show(False)
            dlg.ctrl_parti.Show(False)
            dlg.ctrl_famille.Enable(False)
            dlg.SetIDactivite(IDactivite)
            dlg.SetIDgroupe(IDgroupe)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_OK :
                self.EcritLog(_(u"Inscription de %s enregistrée.") % prenom)
                reponse = _(u"Inscription de %s confirmée.") % prenom
                return {"etat" : True, "reponse" : reponse}
            else :
                self.EcritLog(_(u"Inscription de %s annulée.") % prenom)
                return False

    def Traitement_reservations(self):
        if self.mode == "manuel" :
            from Dlg import DLG_Portail_reservations
            dlg = DLG_Portail_reservations.Dialog(self, track=self.track)
            reponse_modal = dlg.ShowModal()
            reponse = dlg.GetReponse()
            dlg.Destroy()
            if reponse_modal == wx.ID_OK :
                self.Save_grille(dlg.ctrl_grille)
                self.EcritLog(_(u"Enregistrement des consommations"))
                if reponse == "" :
                    return {"etat" : False, "reponse" : reponse}
                else :
                    return {"etat" : True, "reponse" : reponse}
            else :
                self.EcritLog(_(u"Traitement annulé par l'utilisateur"))
                return {"etat" : False}

        if self.mode == "automatique" :
            ctrl_grille = self.parent.ctrl_grille
            self.Init_grille(ctrl_grille=ctrl_grille)
            reponse = self.Appliquer_reservations(ctrl_grille=ctrl_grille)
            self.Save_grille(ctrl_grille)
            self.EcritLog(_(u"Enregistrement des consommations"))
            if reponse == "":
                return {"etat" : False, "reponse" : reponse}
            else :
                return {"etat" : True, "reponse" : reponse}

    def Init_grille(self, ctrl_grille=None):
        # Récupération des paramètres
        IDactivite = int(self.dict_parametres["IDactivite"])
        date_debut_periode = UTILS_Dates.DateEngEnDateDD(self.dict_parametres["date_debut_periode"])
        date_fin_periode = UTILS_Dates.DateEngEnDateDD(self.dict_parametres["date_fin_periode"])

        # Init de la grille des conso
        ctrl_grille.InitGrille(IDindividu=self.track.IDindividu, IDfamille=self.track.IDfamille, IDactivite=IDactivite, periode=(date_debut_periode, date_fin_periode))

    def Save_grille(self, ctrl_grille=None):
        """ Sauvegarde de la grille des conso """
        ctrl_grille.Sauvegarde()

    def Appliquer_reservations(self, ctrl_grille=None, log_jumeau=None):
        """ Appliquer la saisie ou suppression des réservations """
        # Récupération des paramètres
        IDactivite = int(self.dict_parametres["IDactivite"])
        date_debut_periode = UTILS_Dates.DateEngEnDateDD(self.dict_parametres["date_debut_periode"])
        date_fin_periode = UTILS_Dates.DateEngEnDateDD(self.dict_parametres["date_fin_periode"])

        self.EcritLog(_(u"Traitement des réservations de %s sur la période du %s au %s") % (ctrl_grille.ctrl_titre.GetNom(), UTILS_Dates.DateDDEnFr(date_debut_periode), UTILS_Dates.DateDDEnFr(date_fin_periode)), log_jumeau)

        # Lecture des réservations
        DB = GestionDB.DB()
        req = """SELECT IDreservation, date, IDinscription, portail_reservations.IDunite, etat, portail_unites.nom
        FROM portail_reservations
        LEFT JOIN portail_unites ON portail_unites.IDunite = portail_reservations.IDunite
        WHERE IDaction=%d
        ORDER BY date, etat;""" % self.track.IDaction
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeReservations = []
        dictUnitesResaParDate = {}
        for IDreservation, date, IDinscription, IDunite, etat, nom_unite_reservation in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            listeReservations.append({"IDreservation" : IDreservation, "date" : date, "IDinscription" : IDinscription, "IDunite" : IDunite, "etat" : etat, "nom_unite_reservation" : nom_unite_reservation})

        # Traitement des réservations
        liste_resultats = []
        dict_reponses = {"suppression" : 0, "reservation" : 0, "attente" : 0}

        liste_erreurs = []
        for reservation in listeReservations :
            date = reservation["date"]
            IDunite_resa = reservation["IDunite"]
            dict_unite_resa = self.parent.dictUnites[IDunite_resa]
            liste_unites_conso = dict_unite_resa["unites_principales"] + dict_unite_resa["unites_secondaires"]
            nom_unite_reservation = reservation["nom_unite_reservation"]

            # Suppression de la réservation
            if reservation["etat"] == 0 :

                for IDunite in liste_unites_conso :

                    # Ecrit suppression dans log
                    nomUnite = ctrl_grille.grille.dictUnites[IDunite]["nom"]
                    self.EcritLog(_(u"Suppression de l'unité %s du %s") % (nomUnite, UTILS_Dates.DateDDEnFr(date)), log_jumeau)

                    # Vérifie s'il faut appliquer l'état Absence Injustifiée
                    portail_reservations_absenti = self.parent.dictActivites[IDactivite]["portail_reservations_absenti"]
                    absenti = False
                    if portail_reservations_absenti != None :
                        nbre_jours, heure = portail_reservations_absenti.split("#")
                        dt_limite = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=int(heure[:2]), minute=int(heure[3:])) - datetime.timedelta(days=int(nbre_jours))
                        if self.track.horodatage > dt_limite :
                            absenti = True

                    if absenti == True :
                        ctrl_grille.ModifieEtat(IDunite=IDunite, etat="absenti", date=date)
                    else :
                        ctrl_grille.SupprimeConso(IDunite=IDunite, date=date)

                liste_resultats.append(("suppression", date, nom_unite_reservation))
                dict_reponses["suppression"] += 1


            # Ajout de la réservation
            if reservation["etat"] == 1 :

                # Vérifie s'il y a de la place sur chaque unité de conso associée à l'unité de réservation
                hasPlaces = True
                for IDunite in liste_unites_conso :
                    if ctrl_grille.IsOuvert(IDunite=IDunite, date=date) :
                        if ctrl_grille.GetCase(IDunite, date) != None and ctrl_grille.HasPlacesDisponibles(IDunite=IDunite, date=date) == False :
                            hasPlaces = False

                # Si plus de places, met les unités de conso en mode "attente"
                if hasPlaces == True :
                    mode = "reservation"
                    mode_label = _(u"réservation")
                else :
                    mode = "attente"
                    mode_label = _(u"attente")

                # Saisie les conso
                for IDunite in liste_unites_conso :
                    if ctrl_grille.IsOuvert(IDunite=IDunite, date=date) :

                        nomUnite = ctrl_grille.grille.dictUnites[IDunite]["nom"]
                        texte = _(u"Saisie de l'unité %s du %s en mode %s") % (nomUnite, UTILS_Dates.DateDDEnFr(date), mode_label)
                        self.EcritLog(texte, log_jumeau)

                        resultat = ctrl_grille.SaisieConso(IDunite=IDunite, date=date, mode=mode)
                        if resultat != True :
                            self.EcritLog(_(u"[ERREUR] %s") % resultat, log_jumeau)
                            liste_erreurs.append(u"> %s :\n    %s" % (texte, resultat))

                liste_resultats.append(("saisie", date, nom_unite_reservation, mode))
                if mode == "reservation" :
                    dict_reponses["reservation"] += 1
                if mode == "attente" :
                    dict_reponses["attente"] += 1


        # Création de la réponse
        if len(liste_erreurs) > 0 :

            # Si erreurs
            from Dlg import DLG_Messagebox
            if len(liste_erreurs) == 1 :
                introduction = _(u"Une anomalie a été détectée durant l'application de la demande :")
            else :
                introduction = _(u"%s anomalies ont été détectées durant l'application de la demande :") % len(liste_erreurs)
            detail = "\n".join(liste_erreurs)
            dlg = DLG_Messagebox.Dialog(None, titre=_(u"Avertissement"), introduction=introduction, detail=detail, icone=wx.ICON_EXCLAMATION, boutons=[_(u"Ok"), ])
            dlg.ShowModal()
            dlg.Destroy()
            return ""
        else :

            # Si aucune erreur
            reponse_temp = []

            nbre_suppressions = dict_reponses["suppression"]
            if nbre_suppressions == 1 :
                reponse_temp.append(_(u"1 suppression effectuée"))
            if nbre_suppressions > 1 :
                reponse_temp.append(_(u"%d suppressions effectuées") % nbre_suppressions)

            nbre_reservations = dict_reponses["reservation"]
            if nbre_reservations == 1 :
                reponse_temp.append(_(u"1 réservation validée"))
            if nbre_reservations > 1 :
                reponse_temp.append(_(u"%d réservations validées") % nbre_reservations)

            nbre_attentes = dict_reponses["attente"]
            if nbre_attentes == 1 :
                reponse_temp.append(_(u"1 réservation en attente"))
            if nbre_attentes > 1 :
                reponse_temp.append(_(u"%d réservations en attente") % nbre_attentes)

            # Formatage de la réponse
            if len(reponse_temp) == 0 :
                reponse = _(u"Aucune modification.")
            elif len(reponse_temp) == 1 :
                reponse = reponse_temp[0] + "."
            elif len(reponse_temp) == 2 :
                reponse = _(u" et ").join(reponse_temp) + "."
            else :
                reponse = _(u"%s et %s.") % (u", ".join(reponse_temp[:-1]), reponse_temp[-1])

            self.EcritLog(_(u"Réponse : %s") % reponse, log_jumeau)
            return reponse







class Edition_facture():
    """ Classe spéciale pour l'édition des factures """
    def __init__(self, parent=None, IDfacture=None, IDfamille=None):
        self.parent = parent
        self.IDfacture = IDfacture
        self.IDfamille = IDfamille

    def Reedition(self, afficherOptions=True):
        self.afficherOptions = afficherOptions
        facturation = UTILS_Facturation.Facturation()
        facturation.Impression(listeFactures=[self.IDfacture,], afficherOptions=afficherOptions)

    def EnvoyerEmail(self, visible=True):
        self.afficherOptions = visible
        resultat = UTILS_Envoi_email.EnvoiEmailFamille(parent=self.parent, IDfamille=self.IDfamille, nomDoc=FonctionsPerso.GenerationNomDoc("FACTURE", "pdf"), categorie="facture", visible=visible, CreationPDF=self.CreationPDF)
        return resultat

    def CreationPDF(self, nomDoc="", afficherDoc=True):
        """ Création du PDF pour Email """
        facturation = UTILS_Facturation.Facturation()
        resultat = facturation.Impression(listeFactures=[self.IDfacture,], nomDoc=nomDoc, afficherDoc=afficherDoc, afficherOptions=self.afficherOptions)
        if resultat == False :
            return False
        dictChampsFusion, dictPieces = resultat
        return dictChampsFusion[self.IDfacture]






if __name__ == u"__main__":
    app = wx.App(0)
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
