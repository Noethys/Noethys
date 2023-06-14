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
import GestionDB
from Ctrl import CTRL_Assistant_base as Assistant
from Utils import UTILS_Export_tables
from Utils import UTILS_Dates
from Ctrl import CTRL_Selection_jours

# ----------------------------------------
# GENERATION D'UNE ACTIVITE ANNUELLE
# ----------------------------------------


class Page_introduction(Assistant.Page):
    def __init__(self, parent):
        Assistant.Page.__init__(self, parent)
        self.Ajouter_question(titre=_(u"Bienvenue dans l'assistant de g�n�ration d'une activit� annuelle de type culturelle ou sportive (gym, yoga, art floral, foot, etc...)"))
        self.Ajouter_question(titre=_(u"Cliquez sur le bouton Suite pour commencer la saisie des donn�es..."))

    def Suite(self):
        return Page_generalites



class Page_generalites(Assistant.Page):
    def __init__(self, parent):
        Assistant.Page.__init__(self, parent)
        self.Ajouter_rubrique(titre=_(u"G�n�ralit�s"))
        self.Ajouter_question(code="nom", titre=_(u"Quel est le nom de l'activit� ?"), commentaire=_(u"Exemple : 'Yoga - Saison 2017-18'"), ctrl=Assistant.CTRL_Texte, obligatoire=True)
        self.Ajouter_question(code="date_debut", titre=_(u"Quelle est la date de d�but de l'activit� ?"), commentaire=None, ctrl=Assistant.CTRL_Date, obligatoire=True)
        self.Ajouter_question(code="date_fin", titre=_(u"Quelle est la date de fin de l'activit� ?"), commentaire=None, ctrl=Assistant.CTRL_Date, obligatoire=True)
        self.Ajouter_question(code="nbre_inscrits_max", titre=_(u"Quel est le nombre maximal d'inscrits sur la saison ?"), commentaire=_(u"S'il n'y aucune limitation du nombre d'inscrits global, conservez la valeur 0."), ctrl=Assistant.CTRL_Nombre)
        self.Ajouter_question(code="groupes_activites", titre=_(u"Cochez les groupes d'activit�s associ�s � cette activit� :"), commentaire=_(u"Les groupes d'activit�s permettent une s�lection plus rapide dans certaines fen�tres de Noethys."), ctrl=Assistant.CTRL_Groupes_activite)

    def Suite(self):
        # Validation des dates du s�jour
        if self.parent.dict_valeurs["date_debut"] > self.parent.dict_valeurs["date_fin"]:
            dlg = wx.MessageDialog(self, _(u"La date de fin de l'activit� doit �tre sup�rieure � la date du d�but !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        return Page_responsable


class Page_responsable(Assistant.Page_responsable):
    def __init__(self, parent):
        Assistant.Page_responsable.__init__(self, parent)

    def Suite(self):
        return Page_groupes



class Page_groupes(Assistant.Page):
    def __init__(self, parent):
        Assistant.Page.__init__(self, parent)
        self.Ajouter_rubrique(titre=_(u"Groupes"))
        self.Ajouter_question(code="has_groupes", titre=_(u"Cette activit� est-elle compos�e de plusieurs groupes ou plusieurs s�ances ?"), commentaire=_(u"Exemples : Groupe du 'lundi soir', 'jeudi 18h15', 'S�niors', etc..."), ctrl=Assistant.CTRL_Oui_non, defaut=False)
        self.Ajouter_question(code="has_consommations", titre=_(u"Souhaitez-vous pouvoir faire du pointage � chaque s�ance ?"), commentaire=_(u"Noethys enregistrera alors des consommations pour chaque s�ance. Si vous ne savez pas, s�lectionnez Non."), ctrl=Assistant.CTRL_Oui_non, defaut=False)

    def Suite(self):
        # Si pointage demand�, v�rifie que les vacances ont bien �t� param�tr�es
        if self.parent.dict_valeurs["has_consommations"] == True:
            if (self.parent.dict_valeurs["date_fin"] - self.parent.dict_valeurs["date_debut"]).days > 50 :
                DB = GestionDB.DB()
                req = """SELECT date_debut, date_fin
                FROM vacances 
                WHERE date_debut<='%s' AND date_fin>='%s'
                ORDER BY date_debut;""" % (self.parent.dict_valeurs["date_fin"], self.parent.dict_valeurs["date_debut"])
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                DB.Close()
                if len(listeDonnees) == 0 :
                    dlg = wx.MessageDialog(self, _(u"Attention, il semblerait que les p�riodes de vacances n'aient pas �t� param�tr�es !\n\nSouhaitez-vous quand m�me continuer ? \n\nSinon, cliquez sur Non et allez dans Menu Param�trage > Calendrier > Vacances."), _(u"Avertissement"), wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_EXCLAMATION)
                    reponse = dlg.ShowModal()
                    dlg.Destroy()
                    if reponse != wx.ID_YES:
                        return False

        if self.parent.dict_valeurs["has_groupes"] == True :
            return Page_groupes_nombre
        else :
            if self.parent.dict_valeurs["has_consommations"] == True:
                return Page_jours
            else :
                return Page_renseignements


class Page_jours(Assistant.Page):
    def __init__(self, parent):
        Assistant.Page.__init__(self, parent)
        self.Ajouter_rubrique(titre=_(u"Groupes ou s�ances"))
        self.Ajouter_question(code="jours_groupe#1", titre=_(u"La s�ance a lieu quel jour de la semaine ?"), commentaire=_(u"Noethys va cr�er des consommations sur chaque jour d'ouverture de la s�ance durant toute la dur�e de l'activit�."), ctrl=Assistant.CTRL_Jours, obligatoire=False)

    def Suite(self):
        return Page_renseignements


class Page_groupes_nombre(Assistant.Page):
    def __init__(self, parent):
        Assistant.Page.__init__(self, parent)
        self.Ajouter_rubrique(titre=_(u"Groupes ou s�ances"))
        self.Ajouter_question(code="nbre_groupes", titre=_(u"Quel est le nombre de groupes ou de s�ances ?"), commentaire=None, ctrl=Assistant.CTRL_Nombre, obligatoire=True)

    def Suite(self):
        return Page_groupes_liste


class Page_groupes_liste(Assistant.Page):
    def __init__(self, parent):
        Assistant.Page.__init__(self, parent)
        self.Ajouter_rubrique(titre=_(u"Groupes"))
        for index in range(1, self.parent.dict_valeurs["nbre_groupes"]+1) :
            self.Ajouter_question(code="nom_groupe#%d" % index, titre=_(u"Quel est le nom du groupe ou de la s�ances n�%d ?") % index, commentaire=_(u"Exemples : 'Lundi 18h15', 'Samedi 10h', 'S�niors', etc..."), ctrl=Assistant.CTRL_Texte, obligatoire=True)
            self.Ajouter_question(code="capacite_max_groupe#%d" % index, titre=_(u"Quel est le nombre d'inscrits maximal du groupe ou de la s�ance n�%d ?") % index, commentaire=_(u"S'il n'y aucune limitation du nombre d'inscrits sur le groupe ou la s�ance, conservez la valeur 0."), ctrl=Assistant.CTRL_Nombre, obligatoire=False)
            if self.parent.dict_valeurs["has_consommations"] == True:
                self.Ajouter_question(code="jours_groupe#%d" % index, titre=_(u"La s�ance n�%d a lieu quel jour de la semaine ?") % index, commentaire=_(u"Noethys va cr�er des consommations sur chaque jour d'ouverture de la s�ance durant toute la dur�e de l'activit�."), ctrl=Assistant.CTRL_Jours, obligatoire=False)

    def Suite(self):
        return Page_renseignements


class Page_renseignements(Assistant.Page_renseignements):
    def __init__(self, parent):
        Assistant.Page_renseignements.__init__(self, parent)

    def Suite(self):
        # Recherche des activites ressemblantes pour le recopiage de tarification
        DB = GestionDB.DB()
        req = """SELECT activites.IDactivite, activites.nom, activites.date_debut, activites.date_fin
        FROM activites
        LEFT JOIN tarifs ON tarifs.IDactivite = activites.IDactivite
        WHERE type='FORFAIT' AND forfait_saisie_auto=1 AND forfait_suppression_auto=1 AND activites.date_debut IS NOT NULL and activites.date_fin IS NOT NULL
        GROUP BY activites.IDactivite
        ORDER BY activites.date_debut DESC;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            liste_activites = [(None, _(u"Non")),]
            for IDactivite, nom, date_debut, date_fin in listeDonnees :
                if date_debut != None: date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
                if date_fin != None: date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
                label = u"%s - Du %s au %s" % (nom, UTILS_Dates.DateDDEnFr(date_debut), UTILS_Dates.DateDDEnFr(date_fin))
                liste_activites.append((IDactivite, label))
            self.parent.dict_valeurs["activites_ressemblantes"] = liste_activites
            return Page_recopier_tarifs

        self.parent.dict_valeurs["recopier_tarifs"] = None
        return Page_categories_tarifs


class Page_recopier_tarifs(Assistant.Page_recopier_tarifs):
    def __init__(self, parent):
        Assistant.Page_recopier_tarifs.__init__(self, parent)

    def Suite(self):
        if self.parent.dict_valeurs["recopier_tarifs"] == None :
            return Page_categories_tarifs
        else :
            return Page_conclusion


class Page_categories_tarifs(Assistant.Page):
    def __init__(self, parent):
        Assistant.Page.__init__(self, parent)
        self.Ajouter_rubrique(titre=_(u"Tarifs"))
        self.Ajouter_question(code="gratuit", titre=_(u"Cette activit� est-elle gratuite ?"), ctrl=Assistant.CTRL_Oui_non, defaut=False)
        self.Ajouter_question(code="has_categories_tarifs", titre=_(u"Avez-vous plusieurs cat�gories de tarifs ?"), commentaire=_(u"On retrouve par exemple souvent 'Commune' et 'Hors commune'."), ctrl=Assistant.CTRL_Oui_non, defaut=False)

    def Suite(self):
        if self.parent.dict_valeurs["gratuit"] == True:
            self.parent.dict_valeurs["has_categories_tarifs"] = False
            return Page_conclusion
        if self.parent.dict_valeurs["has_categories_tarifs"] == True :
            return Page_categories_tarifs_nombre
        else :
            return Page_tarifs


class Page_categories_tarifs_nombre(Assistant.Page):
    def __init__(self, parent):
        Assistant.Page.__init__(self, parent)
        self.Ajouter_rubrique(titre=_(u"Tarifs"))
        self.Ajouter_question(code="nbre_categories_tarifs", titre=_(u"Quel est le nombre de cat�gories de tarifs ?"), commentaire=None, ctrl=Assistant.CTRL_Nombre, obligatoire=True)

    def Suite(self):
        if self.parent.dict_valeurs["nbre_categories_tarifs"] < 2 :
            dlg = wx.MessageDialog(self, _(u"Le nombre de cat�gories doit �tre sup�rieur � 1 !\n\nSinon s�lectionnez Non � la question pr�c�dente."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        return Page_tarifs


class Page_tarifs(Assistant.Page):
    def __init__(self, parent):
        Assistant.Page.__init__(self, parent)

        # Si une seule cat�gorie de tarif
        if self.parent.dict_valeurs["has_categories_tarifs"] == False :
            self.Ajouter_rubrique(titre=_(u"Tarif"))
            self.Ajouter_question(code="tarif", titre=_(u"Quel est le tarif � appliquer ?"), commentaire=_(u"S�lectionnez une m�thode puis saisissez les param�tres demand�s."), ctrl=Assistant.CTRL_Tarif)
        # Si plusieurs cat�gories de tarifs
        else :
            for index in range(1, self.parent.dict_valeurs["nbre_categories_tarifs"]+1):
                self.Ajouter_rubrique(titre=_(u"Tarif n�%d") % index)
                self.Ajouter_question(code="nom_categorie_tarif#%d" % index, titre=_(u"Quel est le nom de la cat�gorie de tarifs n�%d ?") % index, commentaire=_(u"Exemples : 'Commune' ou 'Hors commune'."), ctrl=Assistant.CTRL_Texte, obligatoire=False)
                self.Ajouter_question(code="tarif#%d" % index, titre=_(u"Quel est le tarif � appliquer � la cat�gorie n�%d ?") % index, commentaire=_(u"S�lectionnez une m�thode puis saisissez les param�tres demand�s."), ctrl=Assistant.CTRL_Tarif)

    def Suite(self):
        return Page_conclusion


class Page_conclusion(Assistant.Page):
    def __init__(self, parent):
        Assistant.Page.__init__(self, parent)
        self.Ajouter_question(titre=_(u"F�licitations, vous avez termin� de param�trer votre activit� annuelle !"))
        self.Ajouter_question(titre=_(u"Cliquez maintenant sur le bouton Valider pour g�n�rer cette activit�."))

    def Suite(self):
        DB = GestionDB.DB()
        self.parent.Sauvegarde_standard(DB)
        IDactivite = self.parent.dict_valeurs["IDactivite"]

        # Consommations
        if self.parent.dict_valeurs["has_consommations"] == True:

            # Unit�s de consommation
            listeIDunite = []
            listeDonnees = [
                ("IDactivite", IDactivite),
                ("nom", _(u"S�ance")),
                ("abrege", _(u"SEANCE")),
                ("type", "Unitaire"),
                ("date_debut", "1977-01-01"),
                ("date_fin", "2999-01-01"),
                ("repas", 0),
                ("ordre", 1)
                ]
            IDunite = DB.ReqInsert("unites", listeDonnees)
            listeIDunite.append(IDunite)

            # Unit� de remplissage
            listeIDuniteRemplissage = []
            listeDonnees = [
                ("IDactivite", IDactivite),
                ("nom", _(u"S�ance")),
                ("abrege", _(u"SEANCE")),
                ("seuil_alerte", 5),
                ("date_debut", "1977-01-01"),
                ("date_fin", "2999-01-01"),
                ("afficher_page_accueil", 1),
                ("afficher_grille_conso", 1),
                ("ordre", 1),
                ]
            IDunite_remplissage = DB.ReqInsert("unites_remplissage", listeDonnees)
            listeIDuniteRemplissage.append(IDunite_remplissage)

            listeDonnees = [("IDunite_remplissage", IDunite_remplissage), ("IDunite", IDunite),]
            DB.ReqInsert("unites_remplissage_unites", listeDonnees)

            # Ouvertures
            listeAjouts = []
            index_groupe = 1
            for IDgroupe in self.parent.dict_valeurs["listeIDgroupe"]:
                jours = self.parent.dict_valeurs["jours_groupe#%d" % index_groupe]
                listeDates = CTRL_Selection_jours.GetDates(jours=jours, date_min=self.parent.dict_valeurs["date_debut"], date_max=self.parent.dict_valeurs["date_fin"])
                for date in listeDates :
                    for IDunite in listeIDunite :
                        listeAjouts.append((IDactivite, IDunite, IDgroupe, date))
                index_groupe += 1

            if len(listeAjouts) > 0 :
                DB.Executermany("INSERT INTO ouvertures (IDactivite, IDunite, IDgroupe, date) VALUES (?, ?, ?, ?)", listeAjouts, commit=False)



        # Recopiage d'un tarification
        if self.parent.dict_valeurs["recopier_tarifs"] != None :
            IDactivite_modele = self.parent.dict_valeurs["recopier_tarifs"]
            # Exportation
            exportation = Exporter(dict_valeurs=self.parent.dict_valeurs)
            exportation.Ajouter(ID=IDactivite_modele)
            contenu = exportation.GetContenu()
            # Importation
            importation = UTILS_Export_tables.Importer(contenu=contenu)
            importation.Ajouter(index=0, dictID={"IDactivite": {IDactivite_modele: IDactivite}})

        # Saisie d'une tarification
        if self.parent.dict_valeurs["recopier_tarifs"] == None :
            # Nom de tarif
            if self.parent.dict_valeurs["gratuit"] == False:
                nom_tarif = self.parent.dict_valeurs["nom"]
                listeDonnees = [("IDactivite", IDactivite), ("nom", nom_tarif)]
                IDnom_tarif = DB.ReqInsert("noms_tarifs", listeDonnees)

            # Cat�gories de tarifs
            listeCategoriesEtTarifs = []

            # Si cat�gorie unique
            if self.parent.dict_valeurs["has_categories_tarifs"] == False:
                listeDonnees = [("IDactivite", IDactivite), ("nom", _(u"Cat�gorie unique"))]
                IDcategorie_tarif = DB.ReqInsert("categories_tarifs", listeDonnees)
                if self.parent.dict_valeurs["gratuit"] == False:
                    track_tarif = self.parent.dict_valeurs["tarif"]
                    listeCategoriesEtTarifs.append((IDcategorie_tarif, track_tarif))

            # Si plusieurs cat�gories
            if self.parent.dict_valeurs["has_categories_tarifs"] == True :
                nbre_categories_tarifs = self.parent.dict_valeurs["nbre_categories_tarifs"]
                for index in range(1, nbre_categories_tarifs+1):
                    nom_categorie_tarif = self.parent.dict_valeurs["nom_categorie_tarif#%d" % index]
                    listeDonnees = [("IDactivite", IDactivite), ("nom", nom_categorie_tarif)]
                    IDcategorie_tarif = DB.ReqInsert("categories_tarifs", listeDonnees)
                    track_tarif = self.parent.dict_valeurs["tarif#%d" % index]
                    listeCategoriesEtTarifs.append((IDcategorie_tarif, track_tarif))

            # Cr�ation de conso ?
            if self.parent.dict_valeurs["has_consommations"] == True:
                options = "calendrier"
            else :
                options = None

            # Tarifs
            if self.parent.dict_valeurs["gratuit"] == False:
                listeTarifs = []
                for IDcategorie_tarif, track_tarif in listeCategoriesEtTarifs :
                    track_tarif.MAJ({
                        "IDactivite": IDactivite,
                        "IDnom_tarif": IDnom_tarif,
                        "type": "FORFAIT",
                        "date_debut" : self.parent.dict_valeurs["date_debut"],
                        "categories_tarifs" : str(IDcategorie_tarif),
                        "forfait_saisie_manuelle" : 0,
                        "forfait_saisie_auto" : 1,
                        "forfait_suppression_auto" : 1,
                        "label_prestation" : "nom_tarif",
                        "options": options,
                        })
                    listeTarifs.append(track_tarif)
                self.parent.Sauvegarde_tarifs(DB, listeTarifs)

            DB.Close()

        # Fermeture
        self.parent.Quitter()
        return False


class Exporter(UTILS_Export_tables.Exporter):
    def __init__(self, categorie="activite", dict_valeurs={}):
        UTILS_Export_tables.Exporter.__init__(self, categorie)
        self.dict_valeurs = dict_valeurs

    def Exporter(self, ID=None):
        # Tarifs
        self.ExporterTable("categories_tarifs", "IDactivite=%d" % ID)
        self.ExporterTable("categories_tarifs_villes", self.FormateCondition("IDcategorie_tarif", self.dictID["categories_tarifs"]))
        self.ExporterTable("noms_tarifs", "IDactivite=%d" % ID, remplacement=("nom", self.dict_valeurs["nom"]))
        self.ExporterTable("tarifs", "IDactivite=%d" % ID, [("categories_tarifs", "IDcategorie_tarif", ";"), ("groupes", "IDgroupe", ";")], remplacement = ("date_debut", self.dict_valeurs["date_debut"]))
        self.ExporterTable("combi_tarifs", self.FormateCondition("IDtarif", self.dictID["tarifs"]))
        self.ExporterTable("combi_tarifs_unites", self.FormateCondition("IDtarif", self.dictID["tarifs"]))
        self.ExporterTable("tarifs_lignes", "IDactivite=%d" % ID)
        self.ExporterTable("questionnaire_filtres", self.FormateCondition("IDtarif", self.dictID["tarifs"]))







class Dialog(Assistant.Dialog):
    def __init__(self, parent):
        Assistant.Dialog.__init__(self, parent, page_introduction=Page_introduction)



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
