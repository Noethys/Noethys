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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import copy
import GestionDB

from Ctrl import CTRL_Bandeau

from Ctrl import CTRL_Tarification_generalites
from Ctrl import CTRL_Tarification_conditions
from Ctrl import CTRL_Tarification_type
from Ctrl import CTRL_Tarification_calcul




class Notebook(wx.Notebook):
    def __init__(self, parent, IDactivite=None, IDtarif=None, nouveauTarif=False, choix_pages=None, cacher_dates=False, track_tarif=None):
        wx.Notebook.__init__(self, parent, id=-1, style= wx.BK_DEFAULT) 
        self.dictPages = {}
        
        self.listePages = [
            ("generalites", _(u"Généralités"), "CTRL_Tarification_generalites.Panel(self, IDactivite=IDactivite, IDtarif=IDtarif, cacher_dates=cacher_dates)", "Information.png"),
            ("conditions", _(u"Conditions d'application"), "CTRL_Tarification_conditions.Panel(self, IDactivite=IDactivite, IDtarif=IDtarif)", "Filtre.png"),
            ("type", _(u"Type de tarif"), "CTRL_Tarification_type.Panel(self, IDactivite=IDactivite, IDtarif=IDtarif, nouveauTarif=nouveauTarif)", "Outils.png"),
            ("calcul", _(u"Calcul du tarif"), "CTRL_Tarification_calcul.Panel(self, IDactivite=IDactivite, IDtarif=IDtarif, track_tarif=track_tarif)", "Calculatrice.png"),
            ]
            
        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        dictImages = {}
        for codePage, labelPage, ctrlPage, imgPage in self.listePages :
            dictImages[codePage] =  il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % imgPage), wx.BITMAP_TYPE_PNG))
            index += 1
        self.AssignImageList(il)

        # Création des pages
        index = 0
        for code, label, ctrl, img in self.listePages :
            if choix_pages == None or code in choix_pages :
                exec("ctrl = " + ctrl)
                self.AddPage(ctrl, label)
                self.SetPageImage(index, dictImages[code])
                self.dictPages[code] = {'ctrl' : ctrl, 'index' : index}
                index += 1

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def OnPageChanged(self, event):
        oldIndex = event.GetOldSelection()
        indexPage = event.GetSelection()
        for code, dictPage in self.dictPages.iteritems() :
            if dictPage["index"] == indexPage :
                dictPage["ctrl"].MAJ()

    def GetPage(self, codePage=""):
        if self.dictPages.has_key(codePage):
            return self.dictPages[codePage]["ctrl"]
        else :
            return None
    
    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)

    def ValidationPages(self) :
        # Validation des données des pages
        for code, dictPage in self.dictPages.iteritems() :
            if dictPage["ctrl"].Validation() == False:
                return False
        return True

    def Sauvegarde(self):
        # Sauvegarde des données
        dict_resultats = {}
        for code, dictPage in self.dictPages.iteritems() :
            resultat = dictPage["ctrl"].Sauvegarde()
            dict_resultats[code] = resultat
        return dict_resultats




class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, IDtarif=None, IDnom_tarif=None, nom_tarif=None, choix_pages=None, cacher_dates=False, track_tarif=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_tarification", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif
        self.IDnom_tarif = IDnom_tarif
        self.nouveauTarif = False
        self.track_tarif = track_tarif

        if self.IDtarif == None :
            self.nouveauTarif = True
            if self.track_tarif == None :
                self.CreateIDtarif()

        # Recherche du nom du tarif
        if nom_tarif != None :
            self.nom_tarif = nom_tarif
        else :
            self.nom_tarif = self.GetNomTarif()

        intro = _(u"Renseignez les caractéristiques générales, les conditions d'application, le type de tarif puis le mode de calcul du tarif. Vous pouvez consulter le Guide de démarrage ou le manuel de référence pour en savoir davantage...")
        titre = _(u"Paramétrage du tarif '%s'") % self.nom_tarif
        if self.IDtarif != None :
            titre += u" (ID%d)" % self.IDtarif
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
        
        # ToolBook
        self.toolbook = Notebook(self, IDactivite=self.IDactivite, IDtarif=self.IDtarif, nouveauTarif=self.nouveauTarif, choix_pages=choix_pages, cacher_dates=cacher_dates, track_tarif=track_tarif)
        
        # Boutons de commande
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        
        if self.nouveauTarif == False or self.track_tarif != None :
            self.Importation()
        else :
            self.toolbook.GetPage("generalites").ctrl_date_debut.SetFocus()

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((700, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        # Contenu
        grid_sizer_base.Add(self.toolbook, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
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
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.CenterOnScreen()
            
    def CreateIDtarif(self):
        """ Crée le tarif dans la base de données afin d'obtenir un IDtarif """
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDactivite", self.IDactivite),
            ("IDtarif", self.IDtarif),
            ("IDnom_tarif", self.IDnom_tarif),
            ]
        self.IDtarif = DB.ReqInsert("tarifs", listeDonnees)
        DB.Close()
    
    def GetIDtarif(self):
        return self.IDtarif
    
    def GetNomTarif(self):
        """ Récupère le nom du tarif """
        if self.IDnom_tarif == None : return u""
        db = GestionDB.DB()
        req = """SELECT nom FROM noms_tarifs WHERE IDnom_tarif=%d;""" % self.IDnom_tarif
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) == 0 : return
        nom = listeDonnees[0][0]
        return nom
        
    def Importation(self):
        listeChampsTarif = ["date_debut", "date_fin", "type", "categories_tarifs", "groupes", "etiquettes", "cotisations",
                            "caisses", "description", "jours_scolaires", "jours_vacances", "observations", "tva",
                            "code_compta", "IDtype_quotient", "label_prestation"]

        if self.track_tarif == None :
            DB = GestionDB.DB()

            # Importation du tarif
            req = """SELECT %s FROM tarifs WHERE IDtarif=%d;""" % (", ".join(listeChampsTarif), self.IDtarif)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()

            # Importation des filtres de questionnaire
            req = """SELECT IDfiltre, IDquestion, categorie, choix, criteres, IDtarif FROM questionnaire_filtres WHERE IDtarif=%d;""" % self.IDtarif
            DB.ExecuterReq(req)
            listeFiltres = DB.ResultatReq()

            DB.Close()
            if len(listeDonnees) == 0 : return

            # Mémorisation des données du tarif
            dictTarif = {}
            index = 0
            for donnee in listeDonnees[0] :
                dictTarif[listeChampsTarif[index]] = donnee
                index += 1

        else :

            # Importation des filtres
            listeFiltres = self.track_tarif.GetFiltres()

            # Importation du tarif
            dictTarif = self.track_tarif.GetDictTarif()

        # Date début
        self.toolbook.GetPage("generalites").SetDateDebut(dictTarif["date_debut"])
        
        # Date fin
        self.toolbook.GetPage("generalites").SetDateFin(dictTarif["date_fin"])

        # Description
        self.toolbook.GetPage("generalites").SetDescription(dictTarif["description"])

        # Observations
        self.toolbook.GetPage("generalites").SetObservations(dictTarif["observations"])

        # Catégories de tarifs rattachées
        self.toolbook.GetPage("generalites").SetCategories(dictTarif["categories_tarifs"])

        # Label de prestation
        self.toolbook.GetPage("generalites").SetLabelPrestation(dictTarif["label_prestation"])

        # TVA
        self.toolbook.GetPage("generalites").SetTVA(dictTarif["tva"])

        # Code Comptable
        self.toolbook.GetPage("generalites").SetCodeComptable(dictTarif["code_compta"])

        # CONDITIONS
        page = self.toolbook.GetPage("conditions")
        if page != None:

            # Groupes rattachés
            self.toolbook.GetPage("conditions").SetGroupes(dictTarif["groupes"])

            # Etiquettes rattachées
            self.toolbook.GetPage("conditions").SetEtiquettes(dictTarif["etiquettes"])

            # Cotisations rattachées
            self.toolbook.GetPage("conditions").SetCotisations(dictTarif["cotisations"])

            # Caisses rattachées
            self.toolbook.GetPage("conditions").SetCaisses(dictTarif["caisses"])

            # Filtres de questionnaires
            self.toolbook.GetPage("conditions").SetFiltres(listeFiltres)

            # Périodes rattachées
            self.toolbook.GetPage("conditions").SetPeriodes(dictTarif["jours_scolaires"], dictTarif["jours_vacances"])

        # TYPE DE TARIF
        page = self.toolbook.GetPage("type")
        if page != None :
            page.SetType(dictTarif["type"])

        # Type de quotient
        self.toolbook.GetPage("calcul").SetTypeQuotient(dictTarif["IDtype_quotient"])

        

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Tarification")

    def OnBoutonOk(self, event): 
        # Validation des données
        validation = self.toolbook.ValidationPages()
        if validation == False :
            return
        
        # Sauvegarde du tarif
        etat = self.Sauvegarde()
        if etat == False :
            return

        # Sauvegarde des données
        dict_resultats = self.toolbook.Sauvegarde()
        
        # Fermeture fenêtre
        self.EndModal(wx.ID_OK)
    
    def Sauvegarde(self):
        # Généralités
        date_debut = self.toolbook.GetPage("generalites").GetDateDebut() 
        date_fin = self.toolbook.GetPage("generalites").GetDateFin() 
        description = self.toolbook.GetPage("generalites").GetDescription()
        observations = self.toolbook.GetPage("generalites").GetObservations()
        texteCategories = self.toolbook.GetPage("generalites").GetCategories()
        tva = self.toolbook.GetPage("generalites").GetTVA()
        code_compta = self.toolbook.GetPage("generalites").GetCodeComptable()
        label_prestation = self.toolbook.GetPage("generalites").GetLabelPrestation()
        
        # Conditions
        page = self.toolbook.GetPage("conditions")
        if page != None :
            texteGroupes = page.GetGroupes()
            texteEtiquettes = page.GetEtiquettes()
            texteCotisations = page.GetCotisations()
            texteCaisses = page.GetCaisses()
            listefiltres = page.GetFiltres()
            jours_scolaires, jours_vacances = page.GetPeriodes()
        else :
            texteGroupes = None
            texteEtiquettes = None
            texteCotisations = None
            texteCaisses = None
            listefiltres = []
            jours_scolaires, jours_vacances = None, None

        # Type
        page = self.toolbook.GetPage("type")
        if page != None :
            typeTarif = page.GetType()
        elif self.track_tarif != None :
            typeTarif = "EVENEMENT"
        else :
            typeTarif = None
        
        # Méthode
        codeMethode = self.toolbook.GetPage("calcul").GetCodeMethode()
        tarifsCompatibles = self.toolbook.GetPage("calcul").GetTarifsCompatibles()

        # Type de quotient
        IDtype_quotient = self.toolbook.GetPage("calcul").GetTypeQuotient()

        # Vérifie que la méthode est compatible avec le type de tarif
        if typeTarif != None and typeTarif not in tarifsCompatibles and self.track_tarif == None :
            dlg = wx.MessageDialog(self, _(u"La méthode de calcul sélectionnée n'est pas compatible avec le type de tarif sélectionné !"), _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Sauvegarde du tarif
        listeDonnees = [
            ("type", typeTarif),
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("methode", codeMethode),
            ("categories_tarifs", texteCategories),
            ("groupes", texteGroupes),
            ("etiquettes", texteEtiquettes),
            ("cotisations", texteCotisations),
            ("caisses", texteCaisses),
            ("description", description),
            ("jours_scolaires", jours_scolaires),
            ("jours_vacances", jours_vacances),
            ("observations", observations),
            ("tva", tva),
            ("code_compta", code_compta),
            ("IDtype_quotient", IDtype_quotient),
            ("label_prestation", label_prestation),
            ]

        # Envoi des données au track_tarif
        if self.track_tarif != None :
            self.track_tarif.MAJ(listeDonnees)

        # Sauvegarde
        if self.track_tarif == None :
            DB = GestionDB.DB()
            DB.ReqMAJ("tarifs", listeDonnees, "IDtarif", self.IDtarif)

        # Sauvegarde des filtres
        listeID = []
        liste_filtres = []
        for dictFiltre in listefiltres :
            listeID.append(dictFiltre["IDfiltre"])
            listeDonnees = [
                ("IDquestion", dictFiltre["IDquestion"]),
                ("categorie", "TARIF"),
                ("choix", dictFiltre["choix"]),
                ("criteres", dictFiltre["criteres"]),
                ("IDtarif", self.IDtarif),
                #("type", "tarif"),
                ("IDdonnee", self.IDtarif),
                ]

            # Envoi des filtres au track_tarif
            listeTemp = copy.deepcopy(listeDonnees)
            listeTemp.append(("IDfiltre", dictFiltre["IDfiltre"]))
            liste_filtres.append(listeTemp)

            # Sauvegarde dans DB
            if self.track_tarif == None:
                if dictFiltre["IDfiltre"] == None :
                    IDfiltre = DB.ReqInsert("questionnaire_filtres", listeDonnees)
                else :
                    DB.ReqMAJ("questionnaire_filtres", listeDonnees, "IDfiltre", dictFiltre["IDfiltre"])

        # Envoi des filtres au track_tarif
        if self.track_tarif != None :
            self.track_tarif.SetFiltres(liste_filtres)

        if self.toolbook.GetPage("conditions") != None :
            for dictInitialFiltre in self.toolbook.GetPage("conditions").GetListeInitialeFiltres() :
                if dictInitialFiltre["IDfiltre"] not in listeID :
                    DB.ReqDEL("questionnaire_filtres", "IDfiltre", dictInitialFiltre["IDfiltre"])

        # Fermeture DB
        if self.track_tarif == None :
            DB.Close()

    def GetTrackTarif(self):
        return self.track_tarif

    def OnBoutonAnnuler(self, event): 
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment annuler ?"), _(u"Annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() != wx.ID_YES :
            dlg.Destroy()
            return
        else:
            dlg.Destroy()
        if self.nouveauTarif == True and self.track_tarif == None :
            DB = GestionDB.DB()
            DB.ReqDEL("tarifs", "IDtarif", self.IDtarif)
            DB.ReqDEL("combi_tarifs", "IDtarif", self.IDtarif)
            DB.ReqDEL("combi_tarifs_unites", "IDtarif", self.IDtarif)
            DB.ReqDEL("tarifs_lignes", "IDtarif", self.IDtarif)
            DB.Close() 
        self.EndModal(wx.ID_CANCEL)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = Dialog(None, IDactivite=1, IDtarif=116, nom_tarif=u"Evènement")
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()