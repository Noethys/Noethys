#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB

from Ctrl import CTRL_Bandeau

from Ctrl import CTRL_Tarification_generalites
from Ctrl import CTRL_Tarification_conditions
from Ctrl import CTRL_Tarification_type
from Ctrl import CTRL_Tarification_calcul




class Notebook(wx.Notebook):
    def __init__(self, parent, IDactivite=None, IDtarif=None, nouveauTarif=False):
        wx.Notebook.__init__(self, parent, id=-1, style= wx.BK_DEFAULT) 
        self.dictPages = {}
        
        self.listePages = [
            ("generalites", _(u"Généralités"), CTRL_Tarification_generalites.Panel(self, IDactivite=IDactivite, IDtarif=IDtarif), "Information.png"),
            ("conditions", _(u"Conditions d'application"), CTRL_Tarification_conditions.Panel(self, IDactivite=IDactivite, IDtarif=IDtarif), "Filtre.png"),
            ("type", _(u"Type de tarif"), CTRL_Tarification_type.Panel(self, IDactivite=IDactivite, IDtarif=IDtarif, nouveauTarif=nouveauTarif), "Outils.png"),
            ("calcul", _(u"Calcul du tarif"), CTRL_Tarification_calcul.Panel(self, IDactivite=IDactivite, IDtarif=IDtarif), "Calculatrice.png"),
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
            self.AddPage(ctrl, label)
            self.SetPageImage(index, dictImages[code])
            self.dictPages[code] = {'ctrl' : ctrl, 'index' : index}
            index += 1
        
    def GetPage(self, codePage=""):
        return self.dictPages[codePage]["ctrl"]
    
    def AffichePage(self, codePage=""):
        indexPage = self.dictPages[codePage]["index"]
        self.SetSelection(indexPage)

    def ValidationPages(self) :
        # Validation des données des pages
        for code, label, ctrl, img in self.listePages :
            if ctrl.Validation() == False :
                self.AffichePage(code)
                return False
        return True

    def Sauvegarde(self):
        # Sauvegarde des données
        for code, label, ctrl, img in self.listePages :
            ctrl.Sauvegarde()
        return True




class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, IDtarif=None, IDnom_tarif=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_tarification", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif
        self.IDnom_tarif = IDnom_tarif
        self.nouveauTarif = False
        if self.IDtarif == None :
            self.CreateIDtarif()
            self.nouveauTarif = True
        
        self.nom_tarif = self.GetNomTarif()

        intro = _(u"Renseignez les caractéristiques générales, les conditions d'application, le type de tarif puis le mode de calcul du tarif. Vous pouvez consulter le Guide de démarrage ou le manuel de référence pour en savoir davantage...")
        titre = _(u"Paramétrage du tarif '%s'") % self.nom_tarif
        self.SetTitle(titre + u" (ID%d)" % self.IDtarif)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
        
        # ToolBook
        self.toolbook = Notebook(self, IDactivite=self.IDactivite, IDtarif=self.IDtarif, nouveauTarif=self.nouveauTarif)
        
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
        
        if self.nouveauTarif == False :
            self.Importation()
        else :
            self.toolbook.GetPage("generalites").ctrl_date_debut.SetFocus()

    def __set_properties(self):
##        self.SetTitle(_(u"Saisie d'un paramétrage pour le tarif %s") % self.nom_tarif)
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
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
        # Récupération du IDcategorie_tarif
        req = """SELECT IDcategorie_tarif FROM noms_tarifs WHERE IDnom_tarif=%d;""" % self.IDnom_tarif
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return
        IDcategorie_tarif = listeDonnees[0][0]
        # Sauvegarde du tarif
        date_creation = str(datetime.date.today())
        listeDonnees = [
            ("IDactivite", self.IDactivite),
            ("IDtarif", self.IDtarif),
            ("IDcategorie_tarif", IDcategorie_tarif),
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
        DB = GestionDB.DB()
        
        # Importation du tarif
        req = """SELECT date_debut, date_fin, type, categories_tarifs, groupes, etiquettes, cotisations, caisses, description, jours_scolaires, jours_vacances, observations, tva, code_compta, IDtype_quotient, label_prestation FROM tarifs WHERE IDtarif=%d;""" % self.IDtarif
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        # Importation des filtres de questionnaire
        req = """SELECT IDfiltre, IDquestion, choix, criteres FROM questionnaire_filtres WHERE IDtarif=%d;""" % self.IDtarif
        DB.ExecuterReq(req)
        listeFiltres = DB.ResultatReq()
        
        DB.Close()
        if len(listeDonnees) == 0 : return
        
        date_debut, date_fin, type, categories_tarifs, groupes, etiquettes, cotisations, caisses, description, jours_scolaires, jours_vacances, observations, tva, code_compta, IDtype_quotient, label_prestation = listeDonnees[0]

        # Date début
        self.toolbook.GetPage("generalites").SetDateDebut(date_debut)
        
        # Date fin
        self.toolbook.GetPage("generalites").SetDateFin(date_fin)

        # Description
        self.toolbook.GetPage("generalites").SetDescription(description)

        # Observations
        self.toolbook.GetPage("generalites").SetObservations(observations)

        # Catégories de tarifs rattachées
        self.toolbook.GetPage("generalites").SetCategories(categories_tarifs)

        # Label de prestation
        self.toolbook.GetPage("generalites").SetLabelPrestation(label_prestation)

        # TVA
        self.toolbook.GetPage("generalites").SetTVA(tva)

        # Code Comptable
        self.toolbook.GetPage("generalites").SetCodeComptable(code_compta)

        # Groupes rattachés
        self.toolbook.GetPage("conditions").SetGroupes(groupes)

        # Etiquettes rattachées
        self.toolbook.GetPage("conditions").SetEtiquettes(etiquettes)

        # Cotisations rattachées
        self.toolbook.GetPage("conditions").SetCotisations(cotisations)

        # Caisses rattachées
        self.toolbook.GetPage("conditions").SetCaisses(caisses)
        
        # Filtres de questionnaires
        self.toolbook.GetPage("conditions").SetFiltres(listeFiltres)

        # Périodes rattachées
        self.toolbook.GetPage("conditions").SetPeriodes(jours_scolaires, jours_vacances)

        # Type
        self.toolbook.GetPage("type").SetType(type)

        # Type de quotient
        self.toolbook.GetPage("calcul").SetTypeQuotient(IDtype_quotient)

        

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
        self.toolbook.Sauvegarde()
        
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
        texteGroupes = self.toolbook.GetPage("conditions").GetGroupes()
        texteEtiquettes = self.toolbook.GetPage("conditions").GetEtiquettes()
        texteCotisations = self.toolbook.GetPage("conditions").GetCotisations()
        texteCaisses = self.toolbook.GetPage("conditions").GetCaisses()
        listefiltres = self.toolbook.GetPage("conditions").GetFiltres() 
        jours_scolaires, jours_vacances = self.toolbook.GetPage("conditions").GetPeriodes()
        
        # Type
        typeTarif = self.toolbook.GetPage("type").GetType() 
        
        # Méthode
        codeMethode = self.toolbook.GetPage("calcul").GetCodeMethode()
        tarifsCompatibles = self.toolbook.GetPage("calcul").GetTarifsCompatibles()

        # Type de quotient
        IDtype_quotient = self.toolbook.GetPage("calcul").GetTypeQuotient()

        # Vérifie que la méthode est compatible avec le type de tarif
        if typeTarif not in tarifsCompatibles :
            dlg = wx.MessageDialog(self, _(u"La méthode de calcul sélectionnée n'est pas compatible avec le type de tarif sélectionné !"), _(u"Information"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Sauvegarde
        DB = GestionDB.DB()
        
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
        DB.ReqMAJ("tarifs", listeDonnees, "IDtarif", self.IDtarif)
        
        # Sauvegarde des filtres
        listeID = []
        for dictFiltre in listefiltres :
            listeID.append(dictFiltre["IDfiltre"])
            listeDonnees = [
                ("IDquestion", dictFiltre["IDquestion"]),
                ("categorie", "TARIF"),
                ("choix", dictFiltre["choix"]),
                ("criteres", dictFiltre["criteres"]),
                ("IDtarif", self.IDtarif),
                ]
            if dictFiltre["IDfiltre"] == None :
                IDfiltre = DB.ReqInsert("questionnaire_filtres", listeDonnees)
            else :
                DB.ReqMAJ("questionnaire_filtres", listeDonnees, "IDfiltre", dictFiltre["IDfiltre"])
            
        for dictInitialFiltre in self.toolbook.GetPage("conditions").GetListeInitialeFiltres() :
            if dictInitialFiltre["IDfiltre"] not in listeID :
                DB.ReqDEL("questionnaire_filtres", "IDfiltre", dictInitialFiltre["IDfiltre"])
        
        DB.Close()

    def OnBoutonAnnuler(self, event): 
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment annuler ?"), _(u"Annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() != wx.ID_YES :
            dlg.Destroy()
            return
        else:
            dlg.Destroy()
        if self.nouveauTarif == True :
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
    frame_1 = Dialog(None, IDactivite=1, IDtarif=1)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()