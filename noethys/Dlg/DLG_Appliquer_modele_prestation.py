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
import datetime
from Ctrl import CTRL_Bouton_image
import GestionDB
from Ctrl import CTRL_Saisie_euros
from Utils import UTILS_Identification
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Utils import UTILS_Dates
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Ctrl.CTRL_Tarification_calcul import CHAMPS_TABLE_LIGNES
from Dlg.DLG_Saisie_prestation import Choix_individu
from Utils import UTILS_Questionnaires


class CTRL_Modeles(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, id=-1, choices=[])
        self.parent = parent
        self.MAJ()

    def MAJ(self):
        self.listeDonnees = []
        self.Importation()
        listeItems = []
        if len(self.listeDonnees) > 0 :
            for dictValeurs in self.listeDonnees :
                listeItems.append(dictValeurs["label"])
        self.Set(listeItems)
        if len(listeItems) > 0 :
            self.Select(0)

    def Importation(self):
        DB = GestionDB.DB()

        # Importation des lignes de tarifs
        req = """SELECT %s FROM tarifs_lignes WHERE IDmodele IS NOT NULL ORDER BY num_ligne;""" % ", ".join(CHAMPS_TABLE_LIGNES)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictLignes = {}
        for ligne in listeDonnees:
            dictLigne = {}
            index = 0
            for valeur in ligne:
                dictLigne[CHAMPS_TABLE_LIGNES[index]] = valeur
                index += 1
            IDmodele = dictLigne["IDmodele"]
            if (IDmodele in dictLignes) == False :
                dictLignes[IDmodele] = []
            dictLignes[IDmodele].append(dictLigne)

        # Importation des modèles
        req = """SELECT IDmodele, categorie, label, IDactivite, IDtarif, IDcategorie_tarif, code_compta, tva, public, IDtype_quotient
        FROM modeles_prestations
        ORDER BY label; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDmodele, categorie, label, IDactivite, IDtarif, IDcategorie_tarif, code_compta, tva, public, IDtype_quotient in listeDonnees :

            if IDmodele in dictLignes :
                liste_lignes = dictLignes[IDmodele]
                methode = liste_lignes[0]["code"]
            else :
                liste_lignes = []
                methode = None

            valeurs = {
                "IDmodele" : IDmodele, "categorie" : categorie, "label" : label, "IDactivite" : IDactivite,
                "IDtarif": IDtarif, "IDcategorie_tarif": IDcategorie_tarif, "code_compta": code_compta,
                "tva": tva, "public": public, "IDtype_quotient": IDtype_quotient,
                "lignes" : liste_lignes, "methode" : methode,
                }
            self.listeDonnees.append(valeurs)

    def SetID(self, ID=None):
        index = 0
        for dictValeurs in self.listeDonnees :
            if ID == dictValeurs["IDmodele"] :
                self.SetSelection(index)
                return
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        ID = self.listeDonnees[index]["IDmodele"]
        return ID

    def GetDictValeurs(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeDonnees[index]


# -------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDprestation = None

        titre = _(u"Saisir une prestation à partir d'un modèle")
        intro = _(u"Cette fonctionnalité vous permet de créer rapidement une prestation en fonction d'un modèle prédéfini.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")

        # Généralités
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))

        self.label_modele = wx.StaticText(self, -1, _(u"Modèle :"))
        self.ctrl_modele = CTRL_Modeles(self)
        self.ctrl_modele.SetMinSize((300, -1))
        self.bouton_modeles = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.label_individu = wx.StaticText(self, -1, _(u"Individu :"))
        self.ctrl_individu = Choix_individu(self, IDfamille=self.IDfamille)

        self.label_date = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.ctrl_date.SetDate(datetime.date.today())

        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"))
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixModele, self.ctrl_modele)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModeles, self.bouton_modeles)

        # Init
        self.OnChoixModele()

    def __set_properties(self):
        self.ctrl_modele.SetToolTip(wx.ToolTip(_(u"Sélectionnez le modèle à appliquer")))
        self.ctrl_individu.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'individu à associer à cette prestation")))
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Sélectionnez la date de la prestation (aujourd'hui par défaut)")))
        self.ctrl_montant.SetToolTip(wx.ToolTip(_(u"Le montant de la prestation est proposé automatiquement mais vous pouvez le modifier librement")))
        self.bouton_modeles.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter, modifier ou supprimer des modèles de prestations")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Généralités
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)

        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)

        grid_sizer_generalites.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_modele = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_modele.Add(self.ctrl_modele, 0, wx.EXPAND, 0)
        grid_sizer_modele.Add(self.bouton_modeles, 0, wx.EXPAND, 0)
        grid_sizer_modele.AddGrowableCol(0)
        grid_sizer_generalites.Add(grid_sizer_modele, 0, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_individu, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_individu, 0, wx.EXPAND, 0)

        grid_sizer_generalites.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_date = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_date.Add(self.ctrl_date, 0, wx.EXPAND, 0)
        grid_sizer_date.Add( (30, 5), 0, wx.EXPAND, 0)
        grid_sizer_date.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date.Add(self.ctrl_montant, 0, wx.EXPAND, 0)
        grid_sizer_date.AddGrowableCol(1)
        grid_sizer_generalites.Add(grid_sizer_date, 0, wx.EXPAND, 0)

        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(staticbox_generalites, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonModeles(self, event):
        IDmodele = self.ctrl_modele.GetID()
        from Dlg import DLG_Modeles_prestations
        dlg = DLG_Modeles_prestations.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_modele.MAJ()
        self.ctrl_modele.SetID(IDmodele)
        self.OnChoixModele()

    def OnChoixModele(self, event=None):
        dictModele = self.ctrl_modele.GetDictValeurs()

        # Active le ctrl_individu
        if dictModele == None or dictModele["public"] == "famille":
            self.ctrl_individu.Enable(False)
        else:
            self.ctrl_individu.Enable(True)
            if self.ctrl_individu.GetID() == None :
                self.ctrl_individu.Select(0)

        if dictModele != None :

            # recherche le montant à appliquer
            montant = 0.0

            # Recherche du montant du tarif : MONTANT UNIQUE
            if dictModele["methode"] == "montant_unique":
                lignes_calcul = dictModele["lignes"]
                montant = lignes_calcul[0]["montant_unique"]
                # Tarif questionnaire
                if montant in (None, 0.0):
                    montant_questionnaire = self.GetQuestionnaire(lignes_calcul[0]["montant_questionnaire"], self.IDfamille, None)
                    if montant_questionnaire not in (None, 0.0):
                        montant = montant_questionnaire

            # Recherche du montant à appliquer : QUOTIENT FAMILIAL
            if dictModele["methode"] == "qf":
                listeQFfamille = self.GetQuotientsFamiliaux()
                lignes_calcul = dictModele["lignes"]
                for ligneCalcul in lignes_calcul:
                    qf_min = ligneCalcul["qf_min"]
                    qf_max = ligneCalcul["qf_max"]
                    montant = ligneCalcul["montant_unique"]

                    date = self.ctrl_date.GetDate()
                    QFfamille = self.RechercheQF(listeQFfamille, self.IDfamille, dictModele, date)
                    if QFfamille != None:
                        if QFfamille >= qf_min and QFfamille <= qf_max:
                            break

            # Attribue le montant
            self.ctrl_montant.SetMontant(montant)

    def GetQuestionnaire(self, IDquestion=None, IDfamille=None, IDindividu=None):
        if IDquestion in (None, "", 0):
            return None
        q = UTILS_Questionnaires.Questionnaires()
        reponse = q.GetReponse(IDquestion, IDfamille, IDindividu)
        return reponse

    def RechercheQF(self, listeQFfamille=[], IDfamille=None, dictModele=None, date=None):
        """ Recherche du QF de la famille """
        # Si la famille a un QF :
        for date_debut, date_fin, quotient, IDtype_quotient in listeQFfamille :
            if date >= date_debut and date <= date_fin and (dictModele["IDtype_quotient"] == None or dictModele["IDtype_quotient"] == IDtype_quotient) :
                return quotient

        # Si la famille n'a pas de QF, on attribue le QF le plus élevé :
        listeQF = []
        for ligneCalcul in dictModele["lignes"] :
            listeQF.append(ligneCalcul["qf_max"])
        listeQF.sort()
        if len(listeQF) > 0 :
            if listeQF[-1] != None :
                return listeQF[-1]
        return None

    def GetQuotientsFamiliaux(self):
        listeQF = []
        DB = GestionDB.DB()
        req = """SELECT IDquotient, IDfamille, date_debut, date_fin, quotient, IDtype_quotient
        FROM quotients
        WHERE IDfamille=%d
        ORDER BY date_debut;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDquotient, IDfamille, date_debut, date_fin, quotient, IDtype_quotient in listeDonnees :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            listeQF.append((date_debut, date_fin, quotient, IDtype_quotient))
        return listeQF


    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Prestations")

    def OnBoutonOk(self, event):
        # Récupération et vérification des données saisies
        dictModele = self.ctrl_modele.GetDictValeurs()

        if dictModele == None:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un modèle dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        categorie = dictModele["categorie"]
        label = dictModele["label"]
        IDactivite = dictModele["IDactivite"]
        IDcategorie_tarif = dictModele["IDcategorie_tarif"]
        IDtarif = dictModele["IDtarif"]
        code_comptable = dictModele["code_compta"]
        if code_comptable == "":
            code_comptable = None
        tva = dictModele["tva"]
        if tva == 0.0:
            tva = None

        montant = self.ctrl_montant.GetMontant()
        if montant == None:
            dlg = wx.MessageDialog(self, _(u"Le montant que vous avez saisi ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return

        if self.ctrl_individu.IsEnabled() == True :
            IDindividu = self.ctrl_individu.GetID()
            if IDindividu == None:
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un individu !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_individu.SetFocus()
                return
        else:
            IDindividu = None

        date = self.ctrl_date.GetDate()
        if self.ctrl_date.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"La date ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return

        # Récupération du IDcompte_payeur
        DB = GestionDB.DB()
        req = "SELECT IDcompte_payeur FROM familles WHERE IDfamille=%d" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        IDcompte_payeur = listeDonnees[0][0]

        # Sauvegarde de la prestation
        listeDonnees = [
            ("IDcompte_payeur", IDcompte_payeur),
            ("date", date),
            ("categorie", categorie),
            ("label", label),
            ("montant_initial", montant),
            ("montant", montant),
            ("IDactivite", IDactivite),
            ("IDtarif", IDtarif),
            ("IDfamille", self.IDfamille),
            ("IDindividu", IDindividu),
            ("temps_facture", None),
            ("IDcategorie_tarif", IDcategorie_tarif),
            ("code_compta", code_comptable),
            ("tva", tva),
            ]
        listeDonnees.append(("date_valeur", str(datetime.date.today())))
        self.IDprestation = DB.ReqInsert("prestations", listeDonnees)
        DB.Close()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetIDprestation(self):
        return self.IDprestation


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=399)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
