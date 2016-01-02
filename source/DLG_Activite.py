#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB
import CTRL_Bandeau

from DLG_Activite_generalites import Panel as Page1
from DLG_Activite_agrements import Panel as Page2
from DLG_Activite_groupes import Panel as Page3
from DLG_Activite_obligations import Panel as Page4
from DLG_Activite_unites import Panel as Page5
from DLG_Activite_calendrier import Panel as Page6
from DLG_Activite_tarification import Panel as Page7
from DLG_Activite_etiquettes import Panel as Page8



def Supprimer_activite(IDactivite=None, nouvelleActivite=False):
    """ Processus de suppression d'une activité """
    DB = GestionDB.DB()
    
    # Vérifie si des individus sont déjà inscrits à cette activité
    req = """
    SELECT IDinscription, IDactivite
    FROM inscriptions
    WHERE IDactivite=%d
    """ % IDactivite
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) > 0 :
        dlg = wx.MessageDialog(None, _(u"Vous ne pouvez pas supprimer cette activité car %d individus y sont déjà inscrits.") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        DB.Close()
        return False
            
        
    # Demande de confirmation de la suppression
    dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment supprimer cette activité ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
    if dlg.ShowModal() != wx.ID_YES :
        dlg.Destroy()
        DB.Close() 
        return False
    dlg.Destroy()

    dlg = wx.MessageDialog(None, _(u"Vous êtes vraiment sûr de vouloir supprimer cette activité ?\n\nToute suppression sera irréversible !"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
    if dlg.ShowModal() != wx.ID_YES :
        dlg.Destroy()
        DB.Close() 
        return False
    dlg.Destroy()

    def FormateCondition(listeID):
        if len(listeID) == 0 : return "()"
        elif len(listeID) == 1 : return "(%d)" % listeID[0]
        else : return str(tuple(listeID))

    # Récupération des IDunites
    req = """SELECT IDunite, IDactivite FROM unites WHERE IDactivite=%d""" % IDactivite
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    listeID = []
    for IDunite, IDactivite in listeDonnees :
        listeID.append(IDunite)
    conditionUnites = FormateCondition(listeID)

    # Récupération des IDunite_remplissage
    req = """SELECT IDunite_remplissage, IDactivite FROM unites_remplissage WHERE IDactivite=%d""" % IDactivite
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    listeID = []
    for IDunite_remplissage, IDactivite in listeDonnees :
        listeID.append(IDunite_remplissage)
    conditionUnitesRemplissage = FormateCondition(listeID)

    # Récupération des IDtarif
    req = """SELECT IDtarif, IDactivite FROM tarifs WHERE IDactivite=%d""" % IDactivite
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    listeID = []
    for IDtarif, IDactivite in listeDonnees :
        listeID.append(IDtarif)
    conditionTarifs = FormateCondition(listeID)

    # Suppression de l'activité
    DB.ReqDEL("activites", "IDactivite", IDactivite)
    DB.ReqDEL("groupes_activites", "IDactivite", IDactivite)
    DB.ReqDEL("responsables_activite", "IDactivite", IDactivite)
    DB.ReqDEL("agrements", "IDactivite", IDactivite)
    DB.ReqDEL("groupes", "IDactivite", IDactivite)
    DB.ReqDEL("pieces_activites", "IDactivite", IDactivite)
    DB.ReqDEL("cotisations_activites", "IDactivite", IDactivite)
    DB.ReqDEL("renseignements_activites", "IDactivite", IDactivite)
    DB.ReqDEL("unites", "IDactivite", IDactivite)
    DB.ReqDEL("unites_remplissage", "IDactivite", IDactivite)
    DB.ReqDEL("remplissage", "IDactivite", IDactivite)
    DB.ReqDEL("ouvertures", "IDactivite", IDactivite)
    DB.ReqDEL("categories_tarifs", "IDactivite", IDactivite)
    DB.ReqDEL("noms_tarifs", "IDactivite", IDactivite)
    DB.ReqDEL("tarifs", "IDactivite", IDactivite)
    DB.ReqDEL("tarifs_lignes", "IDactivite", IDactivite)
    DB.ReqDEL("etiquettes", "IDactivite", IDactivite)
    
    # Suppressions spéciales
    DB.ExecuterReq("DELETE FROM combi_tarifs WHERE IDtarif IN %s" % conditionTarifs)
    DB.ExecuterReq("DELETE FROM combi_tarifs_unites WHERE IDtarif IN %s" % conditionTarifs)
    DB.ExecuterReq("DELETE FROM unites_groupes WHERE IDunite IN %s" % conditionUnites)
    DB.ExecuterReq("DELETE FROM unites_incompat WHERE IDunite IN %s" % conditionUnites)
    DB.ExecuterReq("DELETE FROM unites_remplissage_unites WHERE IDunite_remplissage IN %s" % conditionUnitesRemplissage)
    DB.Commit()
    
    DB.Close() 

    return True
    



class ClsParametres():
    def __init__(self, parent, IDactivite=None):
        self.parent = parent
        self.IDactivite = IDactivite
        self.dictDonnees = {}

        # Importation
        if self.IDactivite != None :
            self.Importation()

    def SetValeur(self, code="", valeur=None):
        self.dictDonnees[code] = valeur

    def GetValeur(self, code="", defaut=None):
        if self.dictDonnees.has_key(code):
            return self.dictDonnees[code]
        else :
            return defaut

    def Importation(self):
        """ Importation des données """
        self.dictDonnees = {}
        DB = GestionDB.DB()
        req = """SELECT psu_activation, psu_unite_prevision, psu_unite_presence, psu_tarif_forfait, psu_etiquette_rtt
        FROM activites WHERE IDactivite=%d;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        self.SetValeur("psu_activation", listeDonnees[0][0])
        self.SetValeur("psu_unite_prevision", listeDonnees[0][1])
        self.SetValeur("psu_unite_presence", listeDonnees[0][2])
        self.SetValeur("psu_tarif_forfait", listeDonnees[0][3])
        self.SetValeur("psu_etiquette_rtt", listeDonnees[0][4])

    def Validation(self):
        # Validation
        if self.GetValeur("psu_activation", 0) == 1 :

            psu_unite_prevision = self.GetValeur("psu_unite_prevision", None)
            psu_unite_presence = self.GetValeur("psu_unite_presence", None)
            psu_tarif_forfait = self.GetValeur("psu_tarif_forfait", None)

            # Vérifie que des valeurs ont été saisies
            if psu_unite_prevision == None :
                dlg = wx.MessageDialog(self.parent, _(u"Vous avez sélectionné le mode P.S.U. mais sans sélectionner d'unité de prévision !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if psu_unite_presence == None :
                dlg = wx.MessageDialog(self.parent, _(u"Vous avez sélectionné le mode P.S.U. mais sans sélectionner d'unité de présence !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if psu_tarif_forfait == None :
                dlg = wx.MessageDialog(self.parent, _(u"Vous avez sélectionné le mode P.S.U. mais sans sélectionner de tarif forfait-crédit !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            # Vérifie que les valeurs existent
            DB = GestionDB.DB()

            req = """SELECT IDunite, nom
            FROM unites WHERE IDactivite=%d;""" % self.IDactivite
            DB.ExecuterReq(req)
            listeUnites = DB.ResultatReq()
            for IDunite in [psu_unite_prevision, psu_unite_presence] :
                valide = False
                for IDunite_temp, nom in listeUnites :
                    if IDunite_temp == IDunite :
                        valide = True
                if valide == False :
                    dlg = wx.MessageDialog(self.parent, _(u"Vous avez sélectionné le mode P.S.U. mais l'unité de prévision sélectionnée semble inexistante !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    DB.Close()
                    return False

            req = """SELECT IDtarif, type
            FROM tarifs WHERE IDactivite=%d;""" % self.IDactivite
            DB.ExecuterReq(req)
            listeTarifs = DB.ResultatReq()
            valide = False
            for IDtarif, type_tarif in listeTarifs :
                if psu_tarif_forfait == IDtarif :
                    valide = True
            if valide == False :
                dlg = wx.MessageDialog(self.parent, _(u"Vous avez sélectionné le mode P.S.U. mais le tarif forfait-crédit sélectionné semble inexistant !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                DB.Close()
                return False

            DB.Close()

        return True

    def Sauvegarde(self):
        """ Sauvegarde des paramètres """
        listeDonnees = [
            ("psu_activation", self.GetValeur("psu_activation", 0)),
            ("psu_unite_prevision", self.GetValeur("psu_unite_prevision", None)),
            ("psu_unite_presence", self.GetValeur("psu_unite_presence", None)),
            ("psu_tarif_forfait", self.GetValeur("psu_tarif_forfait", None)),
            ("psu_etiquette_rtt", self.GetValeur("psu_etiquette_rtt", None)),
            ]
        DB = GestionDB.DB()
        DB.ReqMAJ("activites", listeDonnees, "IDactivite", self.IDactivite)
        DB.Close()


class ClsCommune():
    def __init__(self, parent):
        self.parent = parent

    def GetListePages(self):
        listePages = [
            ("generalites", _(u"Généralités"), Page1(self, IDactivite=self.IDactivite, nouvelleActivite=self.nouvelleActivite), "Loupe.png"),
            ("agrements", _(u"Agréments"), Page2(self, IDactivite=self.IDactivite, nouvelleActivite=self.nouvelleActivite), "Etiquette.png"),
            ("groupes", _(u"Groupes"), Page3(self, IDactivite=self.IDactivite, nouvelleActivite=self.nouvelleActivite), "Famille.png"),
            ("obligations", _(u"Renseignements"), Page4(self, IDactivite=self.IDactivite, nouvelleActivite=self.nouvelleActivite), "Femme.png"),
            ("etiquettes", _(u"Etiquettes"), Page8(self, IDactivite=self.IDactivite, nouvelleActivite=self.nouvelleActivite), "Etiquette.png"),
            ("unites", _(u"Unités"), Page5(self, IDactivite=self.IDactivite, nouvelleActivite=self.nouvelleActivite), "Mecanisme.png"),
            ("calendrier", _(u"Calendrier"), Page6(self, IDactivite=self.IDactivite, nouvelleActivite=self.nouvelleActivite), "Calendrier.png"),
            ("tarification", _(u"Tarification"), Page7(self, IDactivite=self.IDactivite, nouvelleActivite=self.nouvelleActivite), "Euro.png"),
            ]
        return listePages

    def MenuOptions(self, event=None):
        # Création du menu Options
        menuPop = wx.Menu()

        id = wx.NewId()
        item = wx.MenuItem(menuPop, id, _(u"Paramètres P.S.U."), _(u"Renseigner les paramètres P.S.U."))
        item.SetBitmap(wx.Bitmap("Images/16x16/Contrat.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ParametresPSU, id=id)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def ParametresPSU(self, event):
        import DLG_Activite_psu
        dlg = DLG_Activite_psu.Dialog(self, self.IDactivite, clsParametres=self.clsParametres)
        dlg.ShowModal()
        dlg.Destroy()

# ---------------------------------------------------------------------------------------------
class Assistant(wx.Dialog, ClsCommune):
    def __init__(self, parent, IDactivite=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_activite", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDactivite = IDactivite
        self.nouvelleActivite = False
        if self.IDactivite == None :
            self.CreateIDactivite()
            self.nouvelleActivite = True
        
        intro = _(u"Vous pouvez ici renseigner tous les paramètres d'une activité. Attention, ce paramétrage est encore complexe pour un utilisateur n'ayant reçu aucune formation spécifique. Vous pouvez faire appel à l'auteur de Noethys pour bénéficier d'une aide gratuite et personnalisée au paramétrage.")
        titre = _(u"Paramétrage d'une activité")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")
        
        #self.listePages = ("Page1", "Page2", "Page3", "Page4", "Page8", "Page5", "Page6", "Page7")
        self.listePages = self.GetListePages()

        self.static_line = wx.StaticLine(self, -1)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Paramètres avancés"), cheminImage="Images/32x32/Configuration2.png")
        self.bouton_retour = CTRL_Bouton_image.CTRL(self, texte=_(u"Retour"), cheminImage="Images/32x32/Fleche_gauche.png")
        self.bouton_suite = CTRL_Bouton_image.CTRL(self, texte=_(u"Suite"), cheminImage="Images/32x32/Fleche_droite.png", margesImage=(0, 0, 4, 0), positionImage=wx.RIGHT)
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.__set_properties()
        self.__do_layout()
                
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.MenuOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_retour, self.bouton_retour)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_suite, self.bouton_suite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.bouton_retour.Enable(False)
        self.nbrePages = len(self.listePages)    
        self.pageVisible = 0
                        
        # Création des pages
        self.Creation_Pages()
            
    def Creation_Pages(self):
        """ Creation des pages """
        self.dictPages = {}
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            self.dictPages[codePage] = ctrlPage
            self.sizer_pages.Add(ctrlPage, 1, wx.EXPAND, 0)
            self.sizer_pages.Layout()
            ctrlPage.Show(False)

        # Chargement des autres paramètres
        self.clsParametres = ClsParametres(self, self.IDactivite)

        # Affichage de la première page
        self.listePages[self.pageVisible][2].Show(True)
        self.sizer_pages.Layout()

    def __set_properties(self):
        self.SetTitle(_(u"Paramétrage d'une activité"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_options.SetToolTipString(_(u"Cliquez ici pour accéder aux paramètres avancés"))
        self.bouton_retour.SetToolTipString(_(u"Cliquez ici pour revenir à la page précédente"))
        self.bouton_suite.SetToolTipString(_(u"Cliquez ici pour passer à l'étape suivante"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez pour annuler"))
        self.SetMinSize((800, 740))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        # Contenu
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.static_line, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_retour, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_suite, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, wx.LEFT, 10)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        
        self.sizer_pages = sizer_pages
    
    def CreateIDactivite(self):
        """ Crée l'activité dans la base de données afin d'obtenir un IDactivité """
        DB = GestionDB.DB()
        date_creation = str(datetime.date.today())
        listeDonnees = [("date_creation", date_creation),]
        self.IDactivite = DB.ReqInsert("activites", listeDonnees)
        DB.Close()

    def Onbouton_aide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Paramtreruneactivit")

    def Onbouton_retour(self, event):
        # rend invisible la page affichée
        pageCible = self.listePages[self.pageVisible][2] #eval("self.page"+str(self.pageVisible))
        pageCible.Show(False)
        # Fait apparaître nouvelle page
        self.pageVisible -= 1
        pageCible = self.listePages[self.pageVisible][2]
        pageCible.Show(True)
        self.sizer_pages.Layout()
        # Si on quitte l'avant-dernière page, on active le bouton Suivant
        if self.pageVisible == self.nbrePages-1 :
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetImage("Images/32x32/Valider.png")
            self.bouton_suite.SetTexte(_(u"Valider"))
        else:
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetImage("Images/32x32/Fleche_droite.png")
            self.bouton_suite.SetTexte(_(u"Suite"))
        # Si on revient à la première page, on désactive le bouton Retour
        if self.pageVisible == 1 :
            self.bouton_retour.Enable(False)
        # On active le bouton annuler
        self.bouton_annuler.Enable(True)

    def Onbouton_suite(self, event):
        # Vérifie que les données de la page en cours sont valides
        validation = self.ValidationPages()
        if validation == False : return
        # Si on est déjà sur la dernière page : on termine
        if self.pageVisible == self.nbrePages-1 :
            self.Terminer()
            return
        # Rend invisible la page affichée
        pageCible = self.listePages[self.pageVisible][2]
        pageCible.Show(False)
        # Fait apparaître nouvelle page
        self.pageVisible += 1
        pageCible = self.listePages[self.pageVisible][2]
        pageCible.Show(True)
        self.sizer_pages.Layout()
        # Si on arrive à la dernière page, on désactive le bouton Suivant
        if self.pageVisible == self.nbrePages :
            self.bouton_suite.SetImage("Images/32x32/Valider.png")
            self.bouton_suite.SetTexte(_(u"Valider"))
            self.bouton_annuler.Enable(False)
        # Si on quitte la première page, on active le bouton Retour
        if self.pageVisible > 0 :
            self.bouton_retour.Enable(True)

    def OnClose(self, event):
        self.Annuler()

    def OnBoutonAnnuler(self, event):
        self.Annuler()

    def Annuler(self):
        """ Annulation des modifications """
        resultat = Supprimer_activite(IDactivite=self.IDactivite, nouvelleActivite=True)
        if resultat == True :
            self.EndModal(wx.ID_CANCEL)

    def ValidationPages(self) :
        """ Validation des données avant changement de pages """
        if self.listePages[self.pageVisible][2].Validation() == False :
            return False

        # Validation des autres paramètres
        if self.clsParametres.Validation() == False :
            return False

        return True
    
    def GetIDactivite(self):
        return self.IDactivite
    
    def Terminer(self):
        # Sauvegarde des données
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            ctrlPage.Sauvegarde()
        # Sauvegardes des autres paramètres
        self.clsParametres.Sauvegarde()
        # Fermeture
        self.EndModal(wx.ID_OK)
        

# ------------------------------------------------------------------------------------------------------------------------------------------


class Notebook(wx.Notebook, ClsCommune):
    def __init__(self, parent, IDactivite=None, nouvelleActivite=False):
        wx.Notebook.__init__(self, parent, id=-1, style= wx.BK_DEFAULT) # | wx.NB_MULTILINE
        self.IDactivite = IDactivite
        self.nouvelleActivite = nouvelleActivite
        self.dictPages = {}
         
        self.listePages = self.GetListePages()

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        self.dictImages = {}
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            self.dictImages[codePage] = il.Add(wx.Bitmap("Images/16x16/%s" % imgPage, wx.BITMAP_TYPE_PNG))
            index += 1
        self.AssignImageList(il)

        # Création des pages
        index = 0
        self.dictPages = {}
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            self.dictPages[codePage] = ctrlPage
            self.AddPage(ctrlPage, labelPage)
            self.SetPageImage(index, self.dictImages[codePage])
            index += 1

        # Chargement des autres paramètres
        self.clsParametres = ClsParametres(self, self.IDactivite)
        
    def GetPage(self, codePage=""):
        return self.dictPages[codePage]
    
    def AffichePage(self, codePage=""):
        index = 0
        for codePageTemp, labelPage, ctrlPage, imgPage in self.listePages :
            if codePage == codePageTemp :
                self.SetSelection(index)
            index += 1

    def ValidationPages(self) :
        # Validation des données des pages
        for codePageTemp, labelPage, ctrlPage, imgPage in self.listePages :
            if ctrlPage.Validation() == False :
                return False
        # Validation des autres paramètres
        if self.clsParametres.Validation() == False :
            return False
        return True

    def Sauvegarde(self):
        # Sauvegarde des pages
        for codePageTemp, labelPage, ctrlPage, imgPage in self.listePages :
            ctrlPage.Sauvegarde()
        # Sauvegardes des autres paramètres
        self.clsParametres.Sauvegarde()
        return True




# ----------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDactivite = IDactivite
        self.nouvelleActivite = False
        if self.IDactivite == None :
            self.CreateIDactivite()
            self.nouvelleActivite = True
            
        titre = _(u"Paramétrage d'une activité")
        intro = _(u"Vous pouvez ici renseigner tous les paramètres d'une activité. Attention, ce paramétrage peut être complexe pour un utilisateur n'ayant reçu aucune formation spécifique. Vous pouvez demander un coup de pouce à la communauté depuis le forum d'entraide sur le site internet de Noethys.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")
        
        self.ctrl_notebook = Notebook(self, IDactivite, nouvelleActivite=self.nouvelleActivite)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_options = CTRL_Bouton_image.CTRL(self, texte=_(u"Paramètres avancés"), cheminImage="Images/32x32/Configuration2.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        
    def __set_properties(self):
        self.SetTitle(_(u"Paramétrage d'une activité"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_options.SetToolTipString(_(u"Cliquez ici pour accéder aux paramètres avancés"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler et fermer"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_notebook, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
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
        self.SetMinSize((800, 740))
        self.CenterOnScreen()
    
    def CreateIDactivite(self):
        """ Crée l'activité dans la base de données afin d'obtenir un IDactivité """
        DB = GestionDB.DB()
        date_creation = str(datetime.date.today())
        listeDonnees = [("date_creation", date_creation),]
        self.IDactivite = DB.ReqInsert("activites", listeDonnees)
        DB.Close()

    def OnClose(self, event):
        self.Annuler()

    def OnBoutonAnnuler(self, event):
        self.Annuler()

    def Annuler(self):
        """ Annulation des modifications """
        self.EndModal(wx.ID_CANCEL) 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Paramtreruneactivit")

    def OnBoutonOptions(self, event):
        self.ctrl_notebook.MenuOptions()

    def OnBoutonOk(self, event):
        # Validation des données
        validation = self.ctrl_notebook.ValidationPages()
        if validation == False :
            return False
        # Sauvegarde
        self.ctrl_notebook.Sauvegarde()
        # Fermeture
        self.EndModal(wx.ID_OK) 
        
        
        
        
        
        
        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    IDactivite = None#43 # <<<<<<<<<<<<<<<< pour les tests
    if IDactivite == None :
        frame_1 = Assistant(None, IDactivite=None)
    else:
        frame_1 = Dialog(None, IDactivite=IDactivite) 
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
