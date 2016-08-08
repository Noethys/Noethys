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
import datetime
import GestionDB
import FonctionsPerso
from Ctrl import CTRL_Bouton_image
from Utils import UTILS_Envoi_email
from Utils import UTILS_Facturation
from Utils import UTILS_Dates
from Utils import UTILS_Texte

from Dlg import DLG_Badgeage_grille


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

        # Contenu
        self.label_famille = wx.StaticText(self, -1, _(u"Famille :"))
        self.ctrl_famille = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY)
        self.bouton_famille = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_ANY))

        self.label_description = wx.StaticText(self, -1, _(u"Description :"))
        self.ctrl_description = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY | wx.TE_MULTILINE)

        self.label_commentaire = wx.StaticText(self, -1, _(u"Commentaire :"))
        self.ctrl_commentaire = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY | wx.TE_MULTILINE)

        self.label_etat = wx.StaticText(self, -1, _(u"Etat :"))
        self.radio_attente = wx.RadioButton(self, -1, _(u"En attente"), style=wx.RB_GROUP)
        self.radio_validation = wx.RadioButton(self, -1, _(u"Traité le"))
        self.ctrl_date_validation = DatePickerCtrl(self)

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
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAutomatique, self.bouton_automatique)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonManuel, self.bouton_manuel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Init
        self.dictUnites = self.GetUnitesReservations()
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
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_automatique.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer le traitement automatique de cette demande")))
        self.bouton_manuel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer le traitement manuel de cette demande")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer la fenêtre")))
        self.SetMinSize((600, 400))

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
        grid_sizer_contenu = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)

        # Famille
        grid_sizer_contenu.Add(self.label_famille, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)

        grid_sizer_famille = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_famille.Add(self.ctrl_famille, 1, wx.EXPAND, 0)
        grid_sizer_famille.Add(self.bouton_famille, 0, 0, 0)
        grid_sizer_famille.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_famille, 1, wx.EXPAND, 0)

        # Description
        grid_sizer_contenu.Add(self.label_description, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_contenu.Add(self.ctrl_description, 0, wx.EXPAND, 0)

        # commentaire
        grid_sizer_contenu.Add(self.label_commentaire, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_contenu.Add(self.ctrl_commentaire, 0, wx.EXPAND, 0)

        # Etat
        grid_sizer_contenu.Add(self.label_etat, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)

        grid_sizer_etat = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_etat.Add(self.radio_attente, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_etat.Add(self.radio_validation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_etat.Add(self.ctrl_date_validation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(grid_sizer_etat, 1, 0, 0)
        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_contenu.AddGrowableRow(2)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL | wx.EXPAND, 10)

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
        self.CenterOnScreen()

    def GetUnitesReservations(self):
        DB = GestionDB.DB()
        req = """SELECT IDunite, IDactivite, nom, unites_principales, unites_secondaires, ordre
        FROM portail_unites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictUnites = {}
        for IDunite, IDactivite, nom, unites_principales, unites_secondaires, ordre in listeDonnees :
            unites_principales = UTILS_Texte.ConvertStrToListe(unites_principales)
            unites_secondaires = UTILS_Texte.ConvertStrToListe(unites_secondaires)
            dictUnites[IDunite] = {
                "IDactivite" : IDactivite, "nom" : nom, "unites_principales" : unites_principales,
                "unites_secondaires" : unites_secondaires, "ordre" : ordre,
                }
        return dictUnites

    def OnClose(self, event):
        #self.Sauvegarde()
        event.Skip()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonFermer(self, event):
        #self.Sauvegarde()
        self.EndModal(wx.ID_CANCEL)

    def OnRadioEtat(self, event=None):
        self.ctrl_date_validation.Enable(self.radio_validation.GetValue())
        self.bouton_automatique.Enable(not self.radio_validation.GetValue())
        self.bouton_manuel.Enable(not self.radio_validation.GetValue())
        self.Sauvegarde()

    def Sauvegarde(self):
        if self.radio_validation.GetValue() == True :
            etat = "validation"
            traitement_date = self.ctrl_date_validation.GetDate()
            self.ctrl_date_validation.Enable(True)
            self.panel_bandeau.SetBackgroundColour(wx.Colour(220, 255, 220))
        else :
            etat = "attente"
            traitement_date = None
            self.ctrl_date_validation.SetDate(datetime.date.today())
            self.ctrl_date_validation.Enable(False)
            self.panel_bandeau.SetBackgroundColour(wx.Colour(255, 255, 255))

        # MAJ du track
        self.track.etat = etat
        self.track.traitement_date = traitement_date
        self.panel_bandeau.Refresh()
        self.track.Refresh()

        # Sauvegarde dans la base
        DB = GestionDB.DB()
        DB.ReqMAJ("portail_actions", [("etat", etat), ("traitement_date", traitement_date)], "IDaction", self.track.IDaction)
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
        self.label_horodatage.SetLabel(self.track.horodatage.strftime("%d/%m/%Y  %H:%M:%S"))

        # Famille
        self.ctrl_famille.SetValue(self.track.famille)

        # Description
        self.ctrl_description.SetValue(self.track.description)

        # Commentaire
        if self.track.commentaire != None :
            self.ctrl_commentaire.SetValue(self.track.commentaire)

        # Etat
        self.SetEtat(self.track.etat, self.track.traitement_date)

        # Navigation
        index = self.tracks.index(self.track)
        self.bouton_premier.Enable(index > 0)
        self.bouton_precedent.Enable(index > 0)
        self.bouton_suivant.Enable(index < len(self.tracks)-1)
        self.bouton_dernier.Enable(index < len(self.tracks)-1)

        # Titre de la fenêtre
        self.SetTitle(_(u"Traitement des demandes [%d/%d]") % (index+1, len(self.tracks)))

        # Sélection du track dans le listview
        self.track.Select()

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
        self.Sauvegarde()

    def OnBoutonFamille(self, event):
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, self.track.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonAutomatique(self, event):
        self.Traitement(mode="automatique")

    def OnBoutonManuel(self, event):
        self.Traitement(mode="manuel")

    def Traitement(self, mode="automatique"):
        traitement = Traitement(parent=self, track=self.track, mode=mode)
        resultat = traitement.Traiter()

        # Sauvegarde de l'état
        if resultat == True :
            self.SetEtat(etat="valide", traitement_date=datetime.date.today())
            self.Sauvegarde()








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
        listeAdresses = UTILS_Envoi_email.GetAdresseFamille(self.track.IDfamille)

        # Ouverture de la fenêtre d'édition d'un reçu
        from Dlg import DLG_Impression_recu
        dlg_impression = DLG_Impression_recu.Dialog(self.parent, IDreglement=IDreglement)
        dlg_impression.listeAdresses = listeAdresses

        # Traitement manuel
        if self.mode == "manuel" :
            self.EcritLog(_(u"Ouverture de la fenêtre d'édition d'un reçu."))
            if self.dict_parametres["methode_envoi"] == "email" :
                self.EcritLog(_(u"Veuillez envoyer ce reçu de règlement par Email."))
            elif self.dict_parametres["methode_envoi"] == "courrier" :
                self.EcritLog(_(u"Veuillez imprimer le reçu de règlement pour un envoi par courrier."))
            else :
                self.EcritLog(_(u"Veuillez imprimer le reçu de règlement pour un retrait sur site."))
            dlg_impression.ShowModal()
            dlg_impression.Destroy()

            return True

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
                else :
                    self.EcritLog(_(u"Veuillez imprimer le reçu de règlement pour un retrait sur site."))

            # Envoi par Email
            if self.dict_parametres["methode_envoi"] == "email" :
                resultat = UTILS_Envoi_email.EnvoiEmailFamille(parent=dlg_impression, IDfamille=self.track.IDfamille, nomDoc=nomDoc, categorie=categorie, listeAdresses=listeAdresses, visible=False, log=self.track)

            # Mémorisation de l'édition du reçu
            dlg_impression.Sauvegarder(demander=False)
            dlg_impression.Destroy()

            return True



    def Traitement_factures(self):
        # Récupération des paramètres
        IDfacture = int(self.dict_parametres["IDfacture"])
        listeAdresses = UTILS_Envoi_email.GetAdresseFamille(self.track.IDfamille)
        edition = Edition_facture(parent=self.parent, IDfacture=IDfacture, IDfamille=self.track.IDfamille)

        # Traitement manuel
        if self.mode == "manuel" :
            if self.dict_parametres["methode_envoi"] == "email" :
                self.EcritLog(_(u"Veuillez envoyer cette facture par Email."))
                edition.EnvoyerEmail(visible=True)
            elif self.dict_parametres["methode_envoi"] == "courrier" :
                self.EcritLog(_(u"Veuillez imprimer la facture pour un envoi par courrier."))
                edition.Reedition()
            else :
                self.EcritLog(_(u"Veuillez imprimer la facture pour un retrait sur site."))
                edition.Reedition()

            return True

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
                else :
                    self.EcritLog(_(u"Veuillez imprimer la facture pour un retrait sur site."))

            # Envoi par Email
            if self.dict_parametres["methode_envoi"] == "email" :
                resultat = edition.EnvoyerEmail(visible=False)

            return True


    def Traitement_inscriptions(self):
        # Récupération des paramètres
        IDindividu = int(self.dict_parametres["IDindividu"])
        IDactivite = int(self.dict_parametres["IDactivite"])
        IDgroupe = int(self.dict_parametres["IDgroupe"])

        # Traitement manuel ou automatique
        if self.mode == "manuel" or self.mode == "automatique" :

            # Création du texte d'intro
            DB = GestionDB.DB()
            req = """SELECT nom, prenom, date_naiss FROM individus WHERE IDindividu=%d;""" % IDindividu
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
            dlg = DLG_Inscription.Dialog(self.parent, mode="saisie", IDindividu=IDindividu, IDfamille=self.track.IDfamille, intro=intro)
            dlg.bouton_activites.Show(False)
            dlg.ctrl_parti.Show(False)
            dlg.ctrl_famille.Enable(False)
            dlg.SetIDactivite(IDactivite)
            dlg.SetIDgroupe(IDgroupe)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_OK :
                self.EcritLog(_(u"Inscription de %s enregistrée.") % prenom)
                return True
            else :
                self.EcritLog(_(u"Inscription de %s annulée.") % prenom)
                return False

    def Traitement_reservations(self):
        if self.mode == "manuel" :
            from Dlg import DLG_Portail_reservations
            dlg = DLG_Portail_reservations.Dialog(self, track=self.track)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_OK :
                self.Save_grille(dlg.ctrl_grille)
                self.EcritLog(_(u"Enregistrement des consommations"))
                return True
            else :
                self.EcritLog(_(u"Traitement annulé par l'utilisateur"))
                return False

        if self.mode == "automatique" :
            ctrl_grille = self.parent.ctrl_grille
            self.Init_grille(ctrl_grille=ctrl_grille)
            self.Appliquer_reservations(ctrl_grille=ctrl_grille)
            self.Save_grille(ctrl_grille)
            self.EcritLog(_(u"Enregistrement des consommations"))
            return True

    def Init_grille(self, ctrl_grille=None):
        # Récupération des paramètres
        IDactivite = int(self.dict_parametres["IDactivite"])
        IDindividu = int(self.dict_parametres["IDindividu"])
        date_debut_periode = UTILS_Dates.DateEngEnDateDD(self.dict_parametres["date_debut_periode"])
        date_fin_periode = UTILS_Dates.DateEngEnDateDD(self.dict_parametres["date_fin_periode"])

        # Init de la grille des conso
        ctrl_grille.InitGrille(IDindividu=IDindividu, IDfamille=self.track.IDfamille, IDactivite=IDactivite, periode=(date_debut_periode, date_fin_periode))

    def Save_grille(self, ctrl_grille=None):
        """ Sauvegarde de la grille des conso """
        ctrl_grille.Sauvegarde()

    def Appliquer_reservations(self, ctrl_grille=None, log_jumeau=None):
        """ Appliquer la saisie ou suppression des réservations """
        # Récupération des paramètres
        date_debut_periode = UTILS_Dates.DateEngEnDateDD(self.dict_parametres["date_debut_periode"])
        date_fin_periode = UTILS_Dates.DateEngEnDateDD(self.dict_parametres["date_fin_periode"])

        # Init de la grille des conso
        # ctrl_grille.InitGrille(IDindividu=IDindividu, IDfamille=self.track.IDfamille, IDactivite=IDactivite, periode=(date_debut_periode, date_fin_periode))

        self.EcritLog(_(u"Traitement des réservations de %s sur la période du %s au %s") % (ctrl_grille.ctrl_titre.GetNom(), UTILS_Dates.DateDDEnFr(date_debut_periode), UTILS_Dates.DateDDEnFr(date_fin_periode)), log_jumeau)

        # Lecture des consommations à réserver
        DB = GestionDB.DB()
        req = """SELECT IDreservation, date, IDinscription, IDunite
        FROM portail_reservations WHERE IDaction=%d;""" % self.track.IDaction
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeReservations = []
        dictUnitesResaParDate = {}
        for IDreservation, date, IDinscription, IDunite in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            listeReservations.append({"IDreservation" : IDreservation, "date" : date, "IDinscription" : IDinscription, "IDunite" : IDunite})

            dict_unite_resa = self.parent.dictUnites[IDunite]
            liste_unites_conso = dict_unite_resa["unites_principales"] + dict_unite_resa["unites_secondaires"]

            if dictUnitesResaParDate.has_key(date) == False :
                dictUnitesResaParDate[date] = []

            for IDunite_conso in liste_unites_conso :
                if  IDunite_conso not in dictUnitesResaParDate[date] :
                    dictUnitesResaParDate[date].append(IDunite_conso)

        # Récupération de la liste des unités de conso par date
        dictUnitesConsoParDate = {}
        for numLigne, ligne in ctrl_grille.grille.dictLignes.iteritems() :
            for numColonne, case in ligne.dictCases.iteritems() :
                if case.typeCase == "consommation" :
                    if case.etat != None :
                        if dictUnitesConsoParDate.has_key(ligne.date) == False :
                            dictUnitesConsoParDate[ligne.date] = []
                        dictUnitesConsoParDate[ligne.date].append(case.IDunite)

        # Suppression des conso non souhaitées
        for date, liste_unites in dictUnitesConsoParDate.iteritems() :
            for IDunite in liste_unites :
                if not dictUnitesResaParDate.has_key(date) or IDunite not in dictUnitesResaParDate[date] :
                    nomUnite = ctrl_grille.grille.dictUnites[IDunite]["nom"]
                    self.EcritLog(_(u"Suppression de l'unité %s du %s") % (nomUnite, UTILS_Dates.DateDDEnFr(date)), log_jumeau)
                    ctrl_grille.SupprimeConso(IDunite=IDunite, date=date)


        # Saisie les nouvelles consommations
        for reservation in listeReservations :

            date = reservation["date"]
            IDunite_resa = reservation["IDunite"]
            dict_unite_resa = self.parent.dictUnites[IDunite_resa]
            liste_unites_conso = dict_unite_resa["unites_principales"] + dict_unite_resa["unites_secondaires"]

            # Vérifie s'il y a de la place sur chaque unité de conso associée à l'unité de réservation
            hasPlaces = True
            for IDunite in liste_unites_conso :
                if ctrl_grille.IsOuvert(IDunite=IDunite, date=date) :
                    if ctrl_grille.GetCase(IDunite, date) == None and ctrl_grille.HasPlacesDisponibles(IDunite=IDunite, date=date) == False :
                        hasPlaces = False

            # Si plus de places, met les unités de conso en mode "attente"
            if hasPlaces == True :
                mode = "reservation"
            else :
                mode = "attente"

            # Saisie les conso
            for IDunite in liste_unites_conso :
                if ctrl_grille.IsOuvert(IDunite=IDunite, date=date) :

                    nomUnite = ctrl_grille.grille.dictUnites[IDunite]["nom"]
                    self.EcritLog(_(u"Saisie de l'unité %s du %s") % (nomUnite, UTILS_Dates.DateDDEnFr(date)), log_jumeau)

                    resultat = ctrl_grille.SaisieConso(IDunite=IDunite, date=date, mode=mode)
                    if resultat != True :
                        self.EcritLog(_(u"[ERREUR] %s") % resultat, log_jumeau)

        return True



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