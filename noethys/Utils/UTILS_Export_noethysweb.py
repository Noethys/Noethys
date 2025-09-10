#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
import wx
import six, os, copy, json, datetime, uuid, base64, re, shutil
import GestionDB
from Data.DATA_Tables import DB_DATA as DICT_CHAMPS
from PIL import Image
from Utils import UTILS_Fichiers, UTILS_Cryptage_fichier



def Rgb2hex(texte=""):
    """ Convertit une couleur RGB en HEX """
    try:
        r, g, b = [int(x) for x in texte[1:-1].split(",")]
        return "#{:02x}{:02x}{:02x}".format(r, g, b)
    except:
        return None


class Table():
    def __init__(self, parent=None, nom_table="",
                 nouveau_nom_table="",
                 exclure_champs=[],
                 nouveaux_noms_champs={},
                 dict_types_champs={},
                 nouveaux_champs=[],
                 champs_images=[],
                 condition_sql=None,
                 sql=None):
        self.parent = parent
        self.nom_table = nom_table
        self.nouveau_nom_table = nouveau_nom_table
        self.exclure_champs = exclure_champs
        self.nouveaux_noms_champs = nouveaux_noms_champs
        self.dict_types_champs = dict_types_champs
        self.nouveaux_champs = nouveaux_champs
        self.champs_images = champs_images
        self.condition_sql = condition_sql
        self.sql = sql

        # Recherche des données
        self.liste_objets = self.Get_data()

    def Get_data(self):
        # Liste des champs
        listeChamps = []
        for nom, type_champ, info in DICT_CHAMPS[self.nom_table]:
            listeChamps.append(nom)

        # Lecture table
        if self.sql:
            req = self.sql
        else:
            req = "SELECT %s FROM %s" % (", ".join(listeChamps), self.nom_table)
            if self.condition_sql:
                req += " " + self.condition_sql
        self.parent.DB.ExecuterReq(req)
        liste_donnees = self.parent.DB.ResultatReq()
        liste_objets = []
        for objet in liste_donnees:
            dictTemp = {
                "pk": objet[0],
                "model": self.nouveau_nom_table,
                "fields": {},
            }
            dictData = copy.copy(dictTemp)
            for index, nom_champ in enumerate(listeChamps):
                valeur = objet[index]

                if nom_champ not in self.exclure_champs:

                    # Fonction personnalisée
                    if hasattr(self, nom_champ):
                        valeur = getattr(self, nom_champ)(valeur=valeur, objet=objet)

                    # Changement du nom du champ
                    if nom_champ in self.nouveaux_noms_champs:
                        nom_champ = self.nouveaux_noms_champs[nom_champ]

                    # Changement du type de valeur
                    if nom_champ in self.dict_types_champs:
                        valeur = self.dict_types_champs[nom_champ](valeur)

                    # Si image
                    if valeur and nom_champ in self.champs_images:
                        rep_images = self.nom_table
                        rep_images_complet = os.path.join(self.parent.rep_medias, rep_images)

                        # Création du répertoire images
                        if not os.path.exists(rep_images_complet):
                            os.makedirs(rep_images_complet)

                        # Ouverture de l'image
                        image = Image.open(six.BytesIO(valeur))

                        # Redimmensionnement de l'image
                        largeur_max = 400
                        if image.size[0] > largeur_max:
                            wpercent = (largeur_max / float(image.size[0]))
                            hsize = int((float(image.size[1]) * float(wpercent)))
                            image.resize((largeur_max, hsize), Image.LANCZOS)

                        # Création du nom du fichier image
                        nom_fichier_image = u"%s.%s" % (uuid.uuid4(), image.format.lower())

                        # Sauvegarde de l'image dans le répertoire
                        image.save(os.path.join(rep_images_complet, nom_fichier_image), format=image.format)
                        valeur = rep_images + "/" + nom_fichier_image

                    # Mémorisation de la valeur
                    dictTemp["fields"][nom_champ.lower()] = valeur
                    dictData["fields"][nom_champ.lower()] = valeur

                dictData[nom_champ] = valeur

            # Si nouveaux champs
            for nom_champ in self.nouveaux_champs:
                valeur = None
                if hasattr(self, nom_champ):
                    valeur = getattr(self, nom_champ)(data=dictData)
                dictTemp["fields"][nom_champ.lower()] = valeur

            # Vérifie si la ligne est à incorporer ou non
            ligne_valide = True
            if hasattr(self, "valide_ligne"):
                ligne_valide = getattr(self, "valide_ligne")(data=dictData)

            # Mémorisation de l'objet
            if ligne_valide:
                liste_objets.append(dictTemp)

        return liste_objets

    def Get_objets(self):
        return self.liste_objets


class MyEncoder(json.JSONEncoder):
    def default(self, objet):
        # Si datetime.date
        if isinstance(objet, datetime.date):
            return six.text_type(objet)
        # Si datetime.datetime
        elif isinstance(objet, datetime.datetime):
            return six.text_type(objet)
        return json.JSONEncoder.default(self, objet)


class Export:
    def __init__(self, dlg=None, nom_fichier="", mdp=None, options=None):
        self.dlg = dlg
        self.nom_fichier = nom_fichier
        self.mdp = mdp
        self.options = options
        self.liste_objets = []

        # Création du répertoire de travail
        self.rep = UTILS_Fichiers.GetRepTemp(fichier="noethysweb")
        if not os.path.exists(self.rep):
            os.makedirs(self.rep)

        # Création du répertoire medias
        self.rep_medias = os.path.join(self.rep, "media")
        if not os.path.exists(self.rep_medias):
            os.makedirs(self.rep_medias)

    def Ajouter(self, categorie=None, table=None):
        if not categorie or not self.options or categorie in self.options:
            self.liste_objets.extend(table.Get_objets())

    def Finaliser(self):
        # Création du fichier json
        nom_fichier_json = os.path.join(self.rep, "core.json")
        with open(nom_fichier_json, 'w') as outfile:
            json.dump(self.liste_objets, outfile, indent=4, cls=MyEncoder)

        # Création du ZIP
        fichier_zip = shutil.make_archive(UTILS_Fichiers.GetRepTemp("exportweb"), 'zip', self.rep)

        # Crypte le fichier
        if self.mdp:
            UTILS_Cryptage_fichier.CrypterFichier(fichier_zip, self.nom_fichier, self.mdp, ancienne_methode=False)
        else:
            shutil.copyfile(fichier_zip, self.nom_fichier)

        # Nettoyage
        shutil.rmtree(self.rep)
        os.remove(fichier_zip)

        return True

class Export_all(Export):
    def __init__(self, *args, **kwds):
        Export.__init__(self, *args, **kwds)

        # Ouverture de la DB
        self.DB = GestionDB.DB()

        # Récupération des comptes payeurs
        req = """SELECT IDcompte_payeur, IDfamille FROM comptes_payeurs;"""
        self.DB.ExecuterReq(req)
        self.dictComptesPayeurs = {}
        for IDcompte_payeur, IDfamille in self.DB.ResultatReq():
            self.dictComptesPayeurs[IDcompte_payeur] = IDfamille

        # Tables à exporter
        self.Ajouter(categorie=None, table=Table_structures(self))

        self.Ajouter(categorie=None, table=Table(self, nom_table="categories_medicales", nouveau_nom_table="core.CategorieInformation"))

        self.Ajouter(categorie=None, table=Table(self, nom_table="categories_travail", nouveau_nom_table="core.CategorieTravail"))

        self.Ajouter(categorie=None, table=Table(self, nom_table="perceptions", nouveau_nom_table="core.Perception"))

        self.Ajouter(categorie="facturation", table=Table(self, nom_table="lots_factures", nouveau_nom_table="core.LotFactures"))

        self.Ajouter(categorie="facturation", table=Table(self, nom_table="lots_rappels", nouveau_nom_table="core.LotRappels"))

        self.Ajouter(categorie="facturation", table=Table(self, nom_table="factures_prefixes", nouveau_nom_table="core.PrefixeFacture"))

        self.Ajouter(categorie="facturation", table=Table(self, nom_table="factures_messages", nouveau_nom_table="core.MessageFacture"))

        self.Ajouter(categorie="facturation", table=Table(self, nom_table="comptes_bancaires", nouveau_nom_table="core.CompteBancaire", dict_types_champs={"defaut": bool}))

        self.Ajouter(categorie="facturation", table=Table(self, nom_table="modes_reglements", nouveau_nom_table="core.ModeReglement", champs_images=["image"]))

        self.Ajouter(categorie="facturation", table=Table(self, nom_table="emetteurs", nouveau_nom_table="core.Emetteur", nouveaux_noms_champs={"IDmode": "mode"}, champs_images=["image"]))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="medecins", nouveau_nom_table="core.Medecin"))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="niveaux_scolaires", nouveau_nom_table="core.NiveauScolaire"))

        self.Ajouter(categorie=None, table=Table(self, nom_table="organisateur", nouveau_nom_table="core.Organisateur", champs_images=["logo"]))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="regimes", nouveau_nom_table="core.Regime"))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="caisses", nouveau_nom_table="core.Caisse", nouveaux_noms_champs={"IDregime": "regime"}))

        self.Ajouter(categorie="pieces", table=Table(self, nom_table="types_pieces", nouveau_nom_table="core.TypePiece", dict_types_champs={"valide_rattachement": bool}))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="types_quotients", nouveau_nom_table="core.TypeQuotient"))

        self.Ajouter(categorie=None, table=Table(self, nom_table="vacances", nouveau_nom_table="core.Vacance"))

        self.Ajouter(categorie=None, table=Table(self, nom_table="jours_feries", nouveau_nom_table="core.Ferie"))

        self.Ajouter(categorie=None, table=Table(self, nom_table="secteurs", nouveau_nom_table="core.Secteur"))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="types_maladies", nouveau_nom_table="core.TypeMaladie"))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="types_sieste", nouveau_nom_table="core.TypeSieste"))

        self.Ajouter(categorie="individus", table=Table_types_vaccins(self, nom_table="types_vaccins", nouveau_nom_table="core.TypeVaccin"))

        self.Ajouter(categorie="individus", table=Table_ecoles(self, nom_table="ecoles", nouveau_nom_table="core.Ecole"))

        self.Ajouter(categorie="individus", table=Table_classes(self, nom_table="classes", nouveau_nom_table="core.Classe", nouveaux_noms_champs={"IDecole": "ecole"}))

        self.Ajouter(categorie="cotisations", table=Table(self, nom_table="types_cotisations", nouveau_nom_table="core.TypeCotisation", dict_types_champs={"carte": bool, "defaut": bool}, exclure_champs=["code_analytique"]))

        self.Ajouter(categorie="cotisations", table=Table(self, nom_table="unites_cotisations", nouveau_nom_table="core.UniteCotisation", nouveaux_noms_champs={"IDtype_cotisation": "type_cotisation"}, dict_types_champs={"defaut": bool}))

        self.Ajouter(categorie=None, table=Table(self, nom_table="messages_categories", nouveau_nom_table="core.NoteCategorie", dict_types_champs={"afficher_accueil": bool, "afficher_liste": bool}))

        self.Ajouter(categorie=None, table=Table(self, nom_table="listes_diffusion", nouveau_nom_table="core.ListeDiffusion"))

        self.Ajouter(categorie=None, table=Table(self, nom_table="restaurateurs", nouveau_nom_table="core.Restaurateur"))

        self.Ajouter(categorie=None, table=Table(self, nom_table="menus_categories", nouveau_nom_table="core.MenuCategorie"))

        self.Ajouter(categorie=None, table=Table(self, nom_table="menus_legendes", nouveau_nom_table="core.MenuLegende"))

        self.Ajouter(categorie="activites", table=Table_types_groupes_activites(self, nom_table="types_groupes_activites", nouveau_nom_table="core.TypeGroupeActivite",
                                                   nouveaux_champs=["structure"]))

        self.Ajouter(categorie=None, table=Table(self, nom_table="factures_regies", nouveau_nom_table="core.FactureRegie", nouveaux_noms_champs={"IDcompte_bancaire": "compte_bancaire"}))

        self.Ajouter(categorie="activites", table=Table_activites(self, nom_table="activites", nouveau_nom_table="core.Activite",
                           exclure_champs=["public", "psu_activation", "psu_unite_prevision", "psu_unite_presence", "psu_tarif_forfait", "psu_etiquette_rtt", "portail_unites_multiples",
                                           "portail_reservations_absenti", "code_service", "code_analytique"],
                           dict_types_champs={"coords_org": bool, "logo_org": bool, "vaccins_obligatoires": bool, "portail_inscriptions_affichage": bool,
                                              "portail_reservations_affichage": bool, "portail_unites_multiples": bool, "inscriptions_multiples": bool},
                           nouveaux_champs=["pieces", "groupes_activites", "cotisations", "structure"], champs_images=["logo"]))

        self.Ajouter(categorie="activites", table=Table_responsables_activites(self, nom_table="responsables_activite", nouveau_nom_table="core.ResponsableActivite", nouveaux_noms_champs={"IDactivite": "activite"}, dict_types_champs={"defaut": bool}))

        self.Ajouter(categorie="activites", table=Table(self, nom_table="agrements", nouveau_nom_table="core.Agrement", nouveaux_noms_champs={"IDactivite": "activite"}))

        self.Ajouter(categorie="activites", table=Table_groupes(self, nom_table="groupes", nouveau_nom_table="core.Groupe", nouveaux_noms_champs={"IDactivite": "activite"}))

        self.Ajouter(categorie="activites", table=Table_unites(self, nom_table="unites", nouveau_nom_table="core.Unite", nouveaux_noms_champs={"IDactivite": "activite", "IDrestaurateur": "restaurateur"},
                                  dict_types_champs={"heure_debut_fixe": bool, "heure_fin_fixe": bool, "repas": bool, "autogen_active": bool},
                                  nouveaux_champs=["groupes", "incompatibilites"]))

        self.Ajouter(categorie="activites", table=Table_unites_remplissage(self, nom_table="unites_remplissage", nouveau_nom_table="core.UniteRemplissage", nouveaux_noms_champs={"IDactivite": "activite"},
                                  exclure_champs=["etiquettes"],
                                  dict_types_champs={"afficher_page_accueil": bool, "afficher_grille_conso": bool},
                                  nouveaux_champs=["unites"]))

        self.Ajouter(categorie="activites", table=Table(self, nom_table="categories_tarifs", nouveau_nom_table="core.CategorieTarif", nouveaux_noms_champs={"IDactivite": "activite"}))

        self.Ajouter(categorie="activites", table=Table(self, nom_table="noms_tarifs", nouveau_nom_table="core.NomTarif", nouveaux_noms_champs={"IDactivite": "activite"},
                           exclure_champs=["IDcategorie_tarif"]))

        self.Ajouter(categorie="activites", table=Table_tarifs(self, nom_table="tarifs", nouveau_nom_table="core.Tarif", nouveaux_noms_champs={"IDactivite": "activite", "IDnom_tarif": "nom_tarif", "IDtype_quotient": "type_quotient"},
                                  exclure_champs=["IDcategorie_tarif", "condition_nbre_combi", "condition_periode", "condition_nbre_jours", "condition_conso_facturees",
                                                  "condition_dates_continues", "etiquettes", "IDevenement", "IDproduit", "code_produit_local"],
                                  dict_types_champs={"forfait_saisie_manuelle": bool, "forfait_saisie_auto": bool, "forfait_suppression_auto": bool}))

        self.Ajouter(categorie="activites", table=Table_tarifs_lignes(self, nom_table="tarifs_lignes", nouveau_nom_table="core.TarifLigne", nouveaux_noms_champs={"IDactivite": "activite", "IDtarif": "tarif"},
                                  exclure_champs=["IDmodele"]))

        self.Ajouter(categorie="activites", table=Table_combi_tarifs(self, nom_table="combi_tarifs", nouveau_nom_table="core.CombiTarif", nouveaux_noms_champs={"IDtarif": "tarif", "IDgroupe": "groupe"},
                                        nouveaux_champs=["unites"]))

        self.Ajouter(categorie="activites", table=Table(self, nom_table="ouvertures", nouveau_nom_table="core.Ouverture", condition_sql="WHERE IDgroupe!=0",
                                nouveaux_noms_champs={"IDactivite": "activite", "IDunite": "unite", "IDgroupe": "groupe"}))

        self.Ajouter(categorie="activites", table=Table(self, nom_table="remplissage", nouveau_nom_table="core.Remplissage", nouveaux_noms_champs={"IDactivite": "activite", "IDunite_remplissage": "unite_remplissage", "IDgroupe": "groupe"},
                           sql="SELECT IDremplissage, remplissage.IDactivite, remplissage.IDunite_remplissage, IDgroupe, date, places FROM remplissage LEFT JOIN unites_remplissage on unites_remplissage.IDunite_remplissage = remplissage.IDunite_remplissage WHERE unites_remplissage.IDunite_remplissage IS NOT NULL"))

        self.Ajouter(categorie="individus", table=Table_individus(self, nom_table="individus", nouveau_nom_table="core.Individu", nouveaux_noms_champs={"IDcivilite": "civilite", "IDnationalite": "idnationalite", "IDsecteur": "secteur", "IDcategorie_travail": "categorie_travail", "IDmedecin": "medecin", "IDtype_sieste": "type_sieste"},
                                     exclure_champs=["num_secu"], dict_types_champs={"deces": bool, "travail_tel_sms": bool, "tel_domicile_sms": bool, "tel_mobile_sms": bool},
                                     nouveaux_champs=["photo", "listes_diffusion"]))

        self.Ajouter(categorie="individus", table=Table_scolarite(self, nom_table="scolarite", nouveau_nom_table="core.Scolarite", nouveaux_noms_champs={"IDindividu": "individu", "IDecole": "ecole", "IDclasse": "classe", "IDniveau": "niveau"}))

        self.Ajouter(categorie="individus", table=Table_familles(self, nom_table="familles", nouveau_nom_table="core.Famille",
                            nouveaux_noms_champs={"IDcaisse": "caisse", "code_comptable": "code_compta"},
                           exclure_champs=["IDcompte_payeur", "prelevement_activation", "prelevement_etab", "prelevement_guichet", "prelevement_numero", "prelevement_cle",
                                           "prelevement_banque", "prelevement_individu", "prelevement_nom", "prelevement_rue", "prelevement_cp", "prelevement_ville",
                                           "prelevement_cle_iban", "prelevement_iban", "prelevement_bic", "prelevement_reference_mandat", "prelevement_date_mandat", "prelevement_memo",
                                           "autre_adresse_facturation"],
                            nouveaux_champs=["email_factures_adresses", "email_recus_adresses", "email_depots_adresses"],
                           dict_types_champs={"autorisation_cafpro": bool, "internet_actif": bool}))

        self.Ajouter(categorie="activites", table=Table_evenements(self, nom_table="evenements", nouveau_nom_table="core.Evenement", nouveaux_noms_champs={"IDactivite": "activite", "IDgroupe": "groupe", "IDunite": "unite"}))

        self.Ajouter(categorie="inscriptions", table=Table_inscriptions(self, nom_table="inscriptions",
                           nouveau_nom_table="core.Inscription",
                           nouveaux_noms_champs={"IDindividu": "individu", "IDfamille": "famille", "IDactivite": "activite", "IDgroupe": "groupe", "IDcategorie_tarif": "categorie_tarif",
                                                 "date_inscription": "date_debut", "date_desinscription": "date_fin"},
                           exclure_champs=["IDcompte_payeur", "parti"]))

        self.Ajouter(categorie="consommations", table=Table_consommations(self, nom_table="consommations",
                           nouveau_nom_table="core.Consommation",
                           nouveaux_noms_champs={"IDindividu": "individu", "IDinscription": "inscription", "IDactivite": "activite", "IDunite": "unite", "IDgroupe": "groupe", "IDcategorie_tarif": "categorie_tarif", "IDprestation": "prestation", "IDevenement": "evenement"},
                           exclure_champs=["verrouillage", "IDutilisateur", "IDcompte_payeur", "etiquettes"]))

        self.Ajouter(categorie="individus", table=Table_problemes_sante(self, nom_table="problemes_sante",
                            nouveau_nom_table="core.Information",
                            nouveaux_noms_champs={"IDprobleme": "idinformation", "IDindividu": "individu", "IDtype": "categorie"},
                            dict_types_champs={"traitement_medical": bool, "eviction": bool, "diffusion_listing_enfants": bool, "diffusion_listing_conso": bool, "diffusion_listing_repas": bool}))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="vaccins", nouveau_nom_table="core.Vaccin", nouveaux_noms_champs={"IDindividu": "individu", "IDtype_vaccin": "type_vaccin"}))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="messages", nouveau_nom_table="core.Note", nouveaux_noms_champs={"IDmessage": "idnote", "IDcategorie": "categorie", "IDindividu": "individu", "IDfamille": "famille"},
                           exclure_champs=["IDutilisateur", "nom"],
                           dict_types_champs={"afficher_accueil": bool, "afficher_liste": bool, "rappel": bool, "afficher_facture": bool, "rappel_famille": bool, "afficher_commande": bool}))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="rattachements", nouveau_nom_table="core.Rattachement", nouveaux_noms_champs={"IDindividu": "individu", "IDfamille": "famille", "IDcategorie": "categorie"},
                           dict_types_champs={"titulaire": bool}))

        self.Ajouter(categorie="pieces", table=Table_pieces(self, nom_table="pieces", nouveau_nom_table="core.Piece", nouveaux_noms_champs={"IDindividu": "individu", "IDfamille": "famille", "IDtype_piece": "type_piece"}))

        self.Ajouter(categorie="facturation", table=Table_factures(self, nom_table="factures", nouveau_nom_table="core.Facture", nouveaux_noms_champs={"IDfamille": "famille", "IDregie": "regie", "IDlot": "lot", "IDprefixe": "prefixe"},
                            exclure_champs=["IDcompte_payeur", "IDutilisateur", "mention1", "mention2", "mention3"],
                            nouveaux_champs=["famille"]))

        self.Ajouter(categorie="consommations", table=Table_prestations(self, nom_table="prestations", nouveau_nom_table="core.Prestation", nouveaux_noms_champs={"IDactivite": "activite", "IDtarif": "tarif", "IDfacture": "facture", "IDfamille": "famille",
                           "IDindividu": "individu", "IDcategorie_tarif": "categorie_tarif", "code_comptable": "code_compta"},
                           exclure_champs=["IDcompte_payeur", "reglement_frais", "IDcontrat", "IDdonnee", "code_analytique"], nouveaux_champs=["location"]))

        self.Ajouter(categorie="cotisations", table=Table(self, nom_table="depots_cotisations", nouveau_nom_table="core.DepotCotisations", dict_types_champs={"verrouillage": bool}, nouveaux_noms_champs={"IDdepot_cotisation": "iddepot"})),

        self.Ajouter(categorie="cotisations", table=Table_cotisations(self, nom_table="cotisations", nouveau_nom_table="core.Cotisation", nouveaux_noms_champs={"IDfamille": "famille", "IDindividu": "individu",
                                     "IDtype_cotisation": "type_cotisation", "IDunite_cotisation": "unite_cotisation", "IDdepot_cotisation": "depot_cotisation", "IDprestation": "prestation"},
                                      exclure_champs=["IDutilisateur"]))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="quotients", nouveau_nom_table="core.Quotient", nouveaux_noms_champs={"IDfamille": "famille", "IDtype_quotient": "type_quotient"}))

        self.Ajouter(categorie=None, table=Table_documents_modeles(self, nom_table="documents_modeles", nouveau_nom_table="core.ModeleDocument", exclure_champs=["IDdonnee", "supprimable", "observations"],
                                            nouveaux_noms_champs={"IDfond": "fond"}, dict_types_champs={"defaut": bool}, nouveaux_champs=["objets"]))

        self.Ajouter(categorie="questionnaires", table=Table_questions(self, nom_table="questionnaire_questions", nouveau_nom_table="core.QuestionnaireQuestion", exclure_champs=["defaut"],
                                            nouveaux_noms_champs={"IDcategorie": "categorie"}, dict_types_champs={"visible": bool}, nouveaux_champs=["choix"]))

        self.Ajouter(categorie="questionnaires", table=Table_reponses(self, nom_table="questionnaire_reponses", nouveau_nom_table="core.QuestionnaireReponse", exclure_champs=["type"],
                                            nouveaux_noms_champs={"IDquestion": "question", "IDindividu": "individu", "IDfamille": "famille", "IDdonnee": "donnee"}))

        self.Ajouter(categorie="individus", table=Table_payeurs(self, nom_table="payeurs", nouveau_nom_table="core.Payeur", exclure_champs=["IDcompte_payeur"],
                                        nouveaux_champs=["famille"]))

        self.Ajouter(categorie="facturation", table=Table(self, nom_table="depots", nouveau_nom_table="core.Depot", dict_types_champs={"verrouillage": bool},
                                    nouveaux_noms_champs={"IDcompte": "compte"})),

        self.Ajouter(categorie="facturation", table=Table_reglements(self, nom_table="reglements", nouveau_nom_table="core.Reglement",
                                            exclure_champs=["IDcompte_payeur", "IDprestation_frais", "IDutilisateur", "IDprelevement", "IDpiece"],
                                            nouveaux_noms_champs={"IDmode": "mode", "IDemetteur": "emetteur", "IDpayeur": "payeur", "IDcompte": "compte", "IDdepot": "depot"},
                                            nouveaux_champs=["famille"]))

        self.Ajouter(categorie="facturation", table=Table_ventilation(self, nom_table="ventilation", nouveau_nom_table="core.Ventilation",
                                            exclure_champs=["IDcompte_payeur"],
                                            nouveaux_noms_champs={"IDreglement": "reglement", "IDprestation": "prestation"},
                                            nouveaux_champs=["famille"]))

        self.Ajouter(categorie="facturation", table=Table_recus(self, nom_table="recus", nouveau_nom_table="core.Recu",
                                            exclure_champs=["IDutilisateur"],
                                            nouveaux_noms_champs={"IDfamille": "famille", "IDreglement": "reglement"}))

        self.Ajouter(categorie="facturation", table=Table_attestations(self, nom_table="attestations", nouveau_nom_table="core.Attestation",
                                            exclure_champs=["IDutilisateur"],
                                            nouveaux_noms_champs={"IDfamille": "famille"}))

        self.Ajouter(categorie="facturation", table=Table_devis(self, nom_table="devis", nouveau_nom_table="core.Devis",
                                            exclure_champs=["IDutilisateur"],
                                            nouveaux_noms_champs={"IDfamille": "famille"}))

        self.Ajouter(categorie="facturation", table=Table_textes_rappels(self, nom_table="textes_rappels", nouveau_nom_table="core.ModeleRappel",
                                            exclure_champs=["texte_xml", "texte_pdf"],
                                            nouveaux_champs=["html"]))

        self.Ajouter(categorie="facturation", table=Table_rappels(self, nom_table="rappels", nouveau_nom_table="core.Rappel",
                                            exclure_champs=["IDutilisateur", "IDcompte_payeur"],
                                            nouveaux_noms_champs={"IDtexte": "modele", "IDlot": "lot"},
                                            nouveaux_champs=["famille"]))

        self.Ajouter(categorie="facturation", table=Table_aides(self, nom_table="aides", nouveau_nom_table="core.Aide", nouveaux_noms_champs={"IDfamille": "famille", "IDactivite": "activite", "IDcaisse": "caisse"},
                                 nouveaux_champs=["individus"]))

        self.Ajouter(categorie="facturation", table=Table_combi_aides(self, nom_table="aides_combinaisons", nouveau_nom_table="core.CombiAide", nouveaux_noms_champs={"IDaide": "aide", "IDaide_combi": "idcombi_aide"},
                                 exclure_champs=["IDaide_montant"], nouveaux_champs=["montant", "unites"]))

        self.Ajouter(categorie="facturation", table=Table_deductions(self, nom_table="deductions", nouveau_nom_table="core.Deduction", nouveaux_noms_champs={"IDprestation": "prestation", "IDaide": "aide"},
                                exclure_champs=["IDcompte_payeur"], nouveaux_champs=["famille"]))

        self.Ajouter(categorie=None, table=Table_modeles_emails(self, nom_table="modeles_emails", nouveau_nom_table="core.ModeleEmail",
                                            dict_types_champs={"defaut": bool},
                                            exclure_champs=["IDadresse", "texte_xml"],
                                            nouveaux_champs=["html"]))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="liens", nouveau_nom_table="core.Lien", dict_types_champs={"responsable": bool},
                                            nouveaux_noms_champs={"IDfamille": "famille", "IDindividu_sujet": "individu_sujet", "IDindividu_objet": "individu_objet",
                                                                  "IDtype_lien": "idtype_lien", "IDautorisation": "autorisation"})),

        self.Ajouter(categorie=None, table=Table(self, nom_table="adresses_mail", nouveau_nom_table="core.AdresseMail", dict_types_champs={"use_ssl": bool, "defaut": bool, "use_tls": bool},
                                            nouveaux_noms_champs={"smtp": "hote", "connexionssl": "use_ssl", "startTLS": "use_tls"},
                                            exclure_champs=["connexionAuthentifiee", "defaut"]))

        self.Ajouter(categorie="individus", table=Table(self, nom_table="contacts", nouveau_nom_table="core.Contact"))

        self.Ajouter(categorie="individus", table=Table_mandats(self, nom_table="mandats", nouveau_nom_table="core.Mandat", dict_types_champs={"actif": bool},
                                            nouveaux_noms_champs={"IDfamille": "famille", "IDindividu": "individu"},
                                            exclure_champs=["IDbanque"]))

        self.Ajouter(categorie="transports", table=Table(self, nom_table="transports_lignes", nouveau_nom_table="core.TransportLigne"))

        self.Ajouter(categorie="transports", table=Table(self, nom_table="transports_arrets", nouveau_nom_table="core.TransportArret", nouveaux_noms_champs={"IDligne": "ligne"}))

        self.Ajouter(categorie="transports", table=Table(self, nom_table="transports_compagnies", nouveau_nom_table="core.TransportCompagnie", exclure_champs=["fax"]))

        self.Ajouter(categorie="transports", table=Table(self, nom_table="transports_lieux", nouveau_nom_table="core.TransportLieu"))

        self.Ajouter(categorie="transports", table=Table_transports(self, nom_table="transports", nouveau_nom_table="core.Transport", dict_types_champs={"actif": bool},
                                            nouveaux_noms_champs={"IDindividu": "individu", "IDcompagnie": "compagnie", "IDligne": "ligne", "depart_IDarret": "depart_arret",
                                                                  "depart_IDlieu": "depart_lieu", "arrivee_IDarret": "arrivee_arret", "arrivee_IDlieu": "arrivee_lieu"}))

        self.Ajouter(categorie="prelevements", table=Table_prelevements(self, nom_table="prelevements", nouveau_nom_table="core.Prelevements", nouveaux_champs=["reglement",],
                                            nouveaux_noms_champs={"IDlot": "lot", "IDfamille": "famille", "IDfacture": "facture", "IDmandat": "mandat"},
                                            exclure_champs=["prelevement_etab", "prelevement_guichet", "prelevement_numero", "prelevement_banque", "prelevement_cle", "prelevement_iban", "prelevement_bic", "prelevement_reference_mandat", "prelevement_date_mandat", "titulaire", "libelle"]))

        self.Ajouter(categorie="prelevements", table=Table_modeles_prelevements(self))

        self.Ajouter(categorie="prelevements", table=Table_lots_prelevements(self, nom_table="lots_prelevements", nouveau_nom_table="core.PrelevementsLot",
                                            nouveaux_champs=["modele", "numero_sequence"],
                                            exclure_champs=["IDlot", "verrouillage", "IDcompte", "IDmode", "reglement_auto", "type", "format", "encodage", "IDperception", "identifiant_service", "poste_comptable"]))

        self.Ajouter(categorie="locations", table=Table(self, nom_table="produits_categories", nouveau_nom_table="core.CategorieProduit", champs_images=["image"]))

        self.Ajouter(categorie="locations", table=Table(self, nom_table="produits", nouveau_nom_table="core.Produit", champs_images=["image"],
                                            nouveaux_noms_champs={"IDcategorie": "categorie"}, exclure_champs=["activation_partage",]))

        self.Ajouter(categorie="locations", table=Table_tarifs_produits(self))

        self.Ajouter(categorie="locations", table=Table(self, nom_table="locations", nouveau_nom_table="core.Location",
                                            nouveaux_noms_champs={"IDfamille": "famille", "IDproduit": "produit"},
                                            exclure_champs=["IDlocation_portail", "partage", "description"]))

        self.DB.Close()
        self.Finaliser()


class Table_structures(Table):
    def Get_data(self):
        return [{"model": "core.Structure", "pk": 1, "fields": {"nom": u"Structure par défaut"}},]


class Table_pieces(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Récupération des individus
        req = """SELECT IDindividu, nom FROM individus;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_individus = []
        for IDindividu, nom in self.parent.DB.ResultatReq():
            self.liste_individus.append(IDindividu)

        # Récupération des familles
        req = """SELECT IDfamille, date_creation FROM familles;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_familles = []
        for IDfamille, date_creation in self.parent.DB.ResultatReq():
            self.liste_familles.append(IDfamille)

        Table.__init__(self, parent, **kwds)
        del self.liste_individus
        del self.liste_familles

    def valide_ligne(self, data={}):
        """ Incorpore la ligne uniquement le IDindividu existe"""
        if data["fields"]["individu"] and data["fields"]["individu"] not in self.liste_individus:
            return False
        if data["fields"]["famille"] and data["fields"]["famille"] not in self.liste_familles:
            return False
        return True


class Table_types_vaccins(Table):
    def types_maladies(self, data={}):
        """ Champ ManyToMany"""
        req = """SELECT IDtype_vaccin, IDtype_maladie FROM vaccins_maladies WHERE IDtype_vaccin=%d;""" % data["pk"]
        self.parent.DB.ExecuterReq(req)
        return [IDtype_maladie for IDtype_vaccin, IDtype_maladie in self.parent.DB.ResultatReq()]


class Table_ecoles(Table):
    def secteurs(self, valeur=None, objet=None):
        """ Champ ManyToMany"""
        liste_secteurs = []
        if valeur:
            for IDsecteur in valeur.split(";"):
                liste_secteurs.append(int(IDsecteur))
        return liste_secteurs


class Table_classes(Table):
    def niveaux(self, valeur=None, objet=None):
        """ Champ ManyToMany"""
        liste_niveaux = []
        if valeur:
            for IDniveau in valeur.split(";"):
                liste_niveaux.append(int(IDniveau))
        return liste_niveaux


class Table_types_groupes_activites(Table):
    def structure(self, data=None):
        return 1


class Table_activites(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Récupération des types de groupes d'activités
        req = """SELECT IDtype_groupe_activite, nom FROM types_groupes_activites;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_types_groupes_activites = []
        for IDtype_groupe_activite, nom in self.parent.DB.ResultatReq():
            self.liste_types_groupes_activites.append(IDtype_groupe_activite)

        Table.__init__(self, parent, **kwds)
        del self.liste_types_groupes_activites

    def groupes_activites(self, data={}):
        """ Champ ManyToMany"""
        req = """SELECT IDtype_groupe_activite, IDactivite FROM groupes_activites WHERE IDactivite=%d;""" % data["pk"]
        self.parent.DB.ExecuterReq(req)
        return [IDtype_groupe_activite for IDtype_groupe_activite, IDactivite in self.parent.DB.ResultatReq() if IDtype_groupe_activite in self.liste_types_groupes_activites]

    def pieces(self, data={}):
        """ Champ ManyToMany"""
        req = """SELECT IDactivite, IDtype_piece FROM pieces_activites WHERE IDactivite=%d;""" % data["pk"]
        self.parent.DB.ExecuterReq(req)
        return [IDtype_piece for IDactivite, IDtype_piece in self.parent.DB.ResultatReq()]

    def cotisations(self, data={}):
        """ Champ ManyToMany"""
        req = """SELECT IDactivite, IDtype_cotisation FROM cotisations_activites WHERE IDactivite=%d;""" % data["pk"]
        self.parent.DB.ExecuterReq(req)
        return [IDtype_cotisation for IDactivite, IDtype_cotisation in self.parent.DB.ResultatReq()]

    def inscriptions_multiples(self, valeur=None, objet=None):
        if valeur:
            return True
        return False

    def structure(self, data=None):
        return 1


class Table_unites(Table):
    def groupes(self, data={}):
        """ Champ ManyToMany"""
        req = """SELECT IDunite, IDgroupe FROM unites_groupes WHERE IDunite=%d;""" % data["pk"]
        self.parent.DB.ExecuterReq(req)
        return [IDgroupe for IDunite, IDgroupe in self.parent.DB.ResultatReq()]

    def incompatibilites(self, data={}):
        """ Champ ManyToMany"""
        req = """SELECT IDunite, IDunite_incompatible FROM unites_incompat WHERE IDunite=%d;""" % data["pk"]
        self.parent.DB.ExecuterReq(req)
        return [IDunite_incompatible for IDunite, IDunite_incompatible in self.parent.DB.ResultatReq()]

    def largeur(self, valeur=None, objet=None):
        if not valeur:
            valeur = 50
        return valeur


class Table_unites_remplissage(Table):
    def unites(self, data={}):
        """ Champ ManyToMany"""
        req = """SELECT IDunite_remplissage, IDunite FROM unites_remplissage_unites WHERE IDunite_remplissage=%d;""" % data["pk"]
        self.parent.DB.ExecuterReq(req)
        return [IDunite for IDunite_remplissage, IDunite in self.parent.DB.ResultatReq()]


class Table_tarifs(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Récupération des évènements
        req = """SELECT IDevenement, IDactivite FROM evenements;"""
        self.parent.DB.ExecuterReq(req)
        self.dict_evenements = {IDevenement: IDactivite for IDevenement, IDactivite in self.parent.DB.ResultatReq()}

        Table.__init__(self, parent, **kwds)
        del self.dict_evenements

    def valide_ligne(self, data={}):
        if not data["fields"]["activite"]:
            return False
        return True

    def categories_tarifs(self, valeur=None, objet=None):
        """ Champ ManyToMany"""
        liste_categories = []
        if valeur:
            for IDcategorie_tarif in valeur.split(";"):
                liste_categories.append(int(IDcategorie_tarif))
        return liste_categories

    def groupes(self, valeur=None, objet=None):
        """ Champ ManyToMany"""
        liste_groupes = []
        if valeur:
            for IDgroupe in valeur.split(";"):
                liste_groupes.append(int(IDgroupe))
        return liste_groupes

    def cotisations(self, valeur=None, objet=None):
        """ Champ ManyToMany"""
        liste_cotisations = []
        if valeur:
            for IDcotisation in valeur.split(";"):
                liste_cotisations.append(int(IDcotisation))
        return liste_cotisations

    def caisses(self, valeur=None, objet=None):
        """ Champ ManyToMany"""
        liste_caisses = []
        if valeur:
            for IDcaisse in valeur.split(";"):
                if IDcaisse != "0":
                    liste_caisses.append(int(IDcaisse))
        return liste_caisses

    def etats(self, valeur=None, objet=None):
        if valeur:
            valeur = valeur.replace(";", ",")
        return valeur

    def jours_scolaires(self, valeur=None, objet=None):
        if valeur:
            valeur = valeur.replace(";", ",")
        return valeur

    def jours_vacances(self, valeur=None, objet=None):
        if valeur:
            valeur = valeur.replace(";", ",")
        return valeur

    def IDactivite(self, valeur=None, objet=None):
        if not valeur and objet[-2]:
            valeur = self.dict_evenements.get(objet[-2], None)
        return valeur


class Table_tarifs_lignes(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Récupération des tarifs
        req = """SELECT IDtarif, date_debut FROM tarifs WHERE IDproduit IS NULL;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_tarifs = [IDtarif for IDtarif, date_debut in self.parent.DB.ResultatReq()]

        Table.__init__(self, parent, **kwds)
        del self.liste_tarifs

    def qf_max(self, valeur=None, objet=None):
        if valeur > 9999999:
            return 9999999
        return valeur

    def valide_ligne(self, data={}):
        """ Incorpore la ligne uniquement le tarif existe """
        if data["fields"]["tarif"] and data["fields"]["tarif"] not in self.liste_tarifs:
            print(data)
            return False
        return True


class Table_combi_tarifs(Table):
    def unites(self, data={}):
        """ Champ ManyToMany"""
        req = """SELECT IDcombi_tarif, IDunite FROM combi_tarifs_unites WHERE IDcombi_tarif=%d;""" % data["pk"]
        self.parent.DB.ExecuterReq(req)
        return [IDunite for IDcombi_tarif, IDunite in self.parent.DB.ResultatReq()]


class Table_scolarite(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Récupération des individus
        req = """SELECT IDindividu, nom FROM individus;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_individus = []
        for IDindividu, nom in self.parent.DB.ResultatReq():
            self.liste_individus.append(IDindividu)

        Table.__init__(self, parent, **kwds)
        del self.liste_individus

    def valide_ligne(self, data={}):
        """ Incorpore la ligne uniquement le IDindividu existe"""
        if data["fields"]["individu"] and data["fields"]["individu"] not in self.liste_individus:
            return False
        return True


class Table_familles(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Récupération des allocataires
        req = """SELECT IDindividu, nom FROM individus;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_individus = []
        for IDindividu, nom in self.parent.DB.ResultatReq():
            self.liste_individus.append(IDindividu)

        Table.__init__(self, parent, **kwds)
        del self.liste_individus

    def allocataire(self, valeur=None, objet=None):
        if valeur and valeur in self.liste_individus:
            return valeur
        return None

    def email_factures(self, valeur=None, objet=None):
        if valeur:
            return True
        return False

    def email_recus(self, valeur=None, objet=None):
        if valeur:
            return True
        return False

    def email_depots(self, valeur=None, objet=None):
        if valeur:
            return True
        return False

    def email_factures_adresses(self, data={}):
        return data["email_factures"]

    def email_recus_adresses(self, data={}):
        return data["email_recus"]

    def email_depots_adresses(self, data={}):
        return data["email_depots"]

    def titulaire_helios(self, valeur=None, objet=None):
        if valeur and valeur in self.liste_individus:
            return valeur
        return None


class Table_individus(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent
        # Importation de toutes les photos
        DB_photos = GestionDB.DB(suffixe="PHOTOS")
        req = """SELECT IDindividu, photo FROM photos;"""
        DB_photos.ExecuterReq(req)
        listePhotos = DB_photos.ResultatReq()
        DB_photos.Close()
        self.dictPhotos = {}
        for IDindividu, photo in listePhotos:
            self.dictPhotos[IDindividu] = photo

        # Création du répertoire photos
        self.rep_images = "individus"
        self.rep_images_complet = os.path.join(self.parent.rep_medias, self.rep_images)

        # Création du répertoire images
        if not os.path.exists(self.rep_images_complet):
            os.makedirs(self.rep_images_complet)

        Table.__init__(self, parent, **kwds)
        del self.dictPhotos

    def photo(self, data={}):
        IDindividu = data["pk"]
        if IDindividu in self.dictPhotos:
            image = Image.open(six.BytesIO(self.dictPhotos[IDindividu]))
            nom_fichier_image = u"%s.%s" % (uuid.uuid4(), image.format.lower())
            image.save(os.path.join(self.rep_images_complet, nom_fichier_image), format=image.format)
            valeur = os.path.join(self.rep_images, nom_fichier_image)
            return valeur
        return None

    def listes_diffusion(self, data={}):
        """ Champ ManyToMany"""
        req = """SELECT IDliste, IDindividu FROM abonnements WHERE IDindividu=%d;""" % data["pk"]
        self.parent.DB.ExecuterReq(req)
        return [IDliste for IDliste, IDindividu in self.parent.DB.ResultatReq()]


class Table_inscriptions(Table):
    def statut(self, valeur=None, objet=None):
        if not valeur:
            return "ok"
        return valeur


class Table_factures(Table):
    def famille(self, data={}):
        if data["IDcompte_payeur"] in self.parent.dictComptesPayeurs:
            return self.parent.dictComptesPayeurs[data["IDcompte_payeur"]]
        return None

    def activites(self, valeur=None, objet=None):
        if valeur and len(valeur) > 200:
            valeur = None
        return valeur


class Table_responsables_activites(Table):
    def __init__(self, parent, **kwds):

        # Importe les activités
        req = """SELECT IDactivite, nom FROM activites;"""
        parent.DB.ExecuterReq(req)
        self.dict_activites = {}
        for IDactivite, nom in parent.DB.ResultatReq():
            self.dict_activites[IDactivite] = nom

        Table.__init__(self, parent, **kwds)
        del self.dict_activites

    def valide_ligne(self, data={}):
        """ Incorpore la ligne uniquement l'activité existe"""
        if data["fields"]["activite"] not in self.dict_activites:
            return False
        return True


class Table_prestations(Table):
    def __init__(self, parent, **kwds):

        # Importe les factures
        req = """SELECT IDfacture, date_edition FROM factures;"""
        parent.DB.ExecuterReq(req)
        self.dictFactures = {}
        for IDfacture, date_edition in parent.DB.ResultatReq():
            self.dictFactures[IDfacture] = date_edition

        # Importation les catégories de tarifs
        req = "SELECT IDcategorie_tarif, nom FROM categories_tarifs;"
        parent.DB.ExecuterReq(req)
        self.dict_categories_tarifs = {}
        for IDcategorie_tarif, nom in parent.DB.ResultatReq():
            self.dict_categories_tarifs[IDcategorie_tarif] = nom

        Table.__init__(self, parent, **kwds)
        del self.dictFactures
        del self.dict_categories_tarifs

    def IDindividu(self, valeur=None, objet=None):
        if valeur == 0:
            valeur = None
        return valeur

    def IDfacture(self, valeur=None, objet=None):
        # Vérifie que la facture existe bien
        if valeur and valeur in self.dictFactures:
            return valeur
        return None

    def IDcategorie_tarif(self, valeur=None, objet=None):
        # Vérifie que la catégorie de tarif existe bien
        if valeur and valeur in self.dict_categories_tarifs:
            return valeur
        return None

    def date(self, valeur=None, objet=None):
        if isinstance(valeur, datetime.datetime):
            return valeur.date()
        if isinstance(valeur, six.string_types) and ":" in valeur:
            return valeur[:10]
        return valeur

    def date_valeur(self, valeur=None, objet=None):
        if not valeur:
            return objet[2]
        return valeur

    def montant(self, valeur=None, objet=None):
        if valeur == None:
            return 0
        return valeur

    def montant_initial(self, valeur=None, objet=None):
        if objet[6] and valeur == None:
            return objet[6]
        if valeur == None:
            return 0
        return valeur

    def location(self, data={}):
        if data["categorie"] == "location":
            return data["IDdonnee"]
        return None


class Table_groupes(Table):
    def __init__(self, parent, **kwds):

        # Importe les activités
        req = """SELECT IDactivite, nom FROM activites;"""
        parent.DB.ExecuterReq(req)
        self.dict_activites = {}
        for IDactivite, nom in parent.DB.ResultatReq():
            self.dict_activites[IDactivite] = nom

        Table.__init__(self, parent, **kwds)
        del self.dict_activites

    def valide_ligne(self, data={}):
        """ Incorpore la ligne uniquement l'activité existe"""
        if data["fields"]["activite"] not in self.dict_activites:
            return False
        return True


class Table_consommations(Table):
    def __init__(self, parent, **kwds):
        # Importe les prestations
        req = """SELECT IDprestation, date FROM prestations;"""
        parent.DB.ExecuterReq(req)
        self.dictPrestations = {}
        for IDprestation, date in parent.DB.ResultatReq():
            self.dictPrestations[IDprestation] = date

        # Importe les catégories de tarifs
        req = """SELECT IDcategorie_tarif, nom FROM categories_tarifs;"""
        parent.DB.ExecuterReq(req)
        self.dictCategoriesTarifs = {}
        for IDcategorie_tarif, nom in parent.DB.ResultatReq():
            self.dictCategoriesTarifs[IDcategorie_tarif] = nom

        Table.__init__(self, parent, **kwds)
        del self.dictPrestations
        del self.dictCategoriesTarifs

    def IDprestation(self, valeur=None, objet=None):
        # Vérifie que la prestation existe bien
        if valeur and valeur in self.dictPrestations:
            return valeur
        return None

    def IDcategorie_tarif(self, valeur=None, objet=None):
        # Vérifie que la catégorie de tarifs existe bien
        if valeur and valeur in self.dictCategoriesTarifs:
            return valeur
        return None

    def quantite(self, valeur=None, objet=None):
        return valeur or 1


class Table_evenements(Table):
    def __init__(self, parent, **kwds):
        # Importe les unités de conso
        req = """SELECT IDunite, nom FROM unites;"""
        parent.DB.ExecuterReq(req)
        self.dictUnites = {}
        for IDunite, nom in parent.DB.ResultatReq():
            self.dictUnites[IDunite] = nom
        Table.__init__(self, parent, **kwds)
        del self.dictUnites

    def valide_ligne(self, data={}):
        """ Incorpore la ligne uniquement l'unité associée existe"""
        if data["fields"]["unite"] not in self.dictUnites:
            print("Table evenements : l'unite n'existe pas pour l'evenement ID%d" % data["pk"])
            return False
        return True


class Table_cotisations(Table):
    def __init__(self, parent, **kwds):
        # Importe les prestations
        req = """SELECT IDprestation, date FROM prestations;"""
        parent.DB.ExecuterReq(req)
        self.dictPrestations = {}
        for IDprestation, date in parent.DB.ResultatReq():
            self.dictPrestations[IDprestation] = date

        Table.__init__(self, parent, **kwds)
        del self.dictPrestations

    def activites(self, valeur=None, objet=None):
        """ Champ ManyToMany"""
        liste_activites = []
        if valeur:
            for IDactivite in valeur.split(";"):
                liste_activites.append(int(IDactivite))
        return liste_activites

    def IDprestation(self, valeur=None, objet=None):
        if valeur and valeur in self.dictPrestations:
            return valeur
        return None


class Table_problemes_sante(Table):
    def IDtype(self, valeur=None, objet=None):
        if valeur == None:
            return 1
        return valeur


class Table_aides(Table):
    def individus(self, data={}):
        """ Champ ManyToMany"""
        req = """SELECT IDaide, IDindividu FROM aides_beneficiaires WHERE IDaide=%d;""" % data["pk"]
        self.parent.DB.ExecuterReq(req)
        return [IDindividu for IDaide, IDindividu in self.parent.DB.ResultatReq()]

    def jours_scolaires(self, valeur=None, objet=None):
        if valeur:
            valeur = valeur.replace(";", ",")
        return valeur

    def jours_vacances(self, valeur=None, objet=None):
        if valeur:
            valeur = valeur.replace(";", ",")
        return valeur


class Table_combi_aides(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent
        # Importation des montants
        req = """SELECT IDaide_combi, aides_montants.IDaide_montant, montant FROM aides_montants
        LEFT JOIN aides_combinaisons ON aides_combinaisons.IDaide_montant = aides_montants.IDaide_montant;"""
        self.parent.DB.ExecuterReq(req)
        self.dictMontants = {}
        for IDaide_combi, IDaide_montant, montant in self.parent.DB.ResultatReq():
            self.dictMontants[IDaide_combi] = montant
        # Importation des unités
        req = """SELECT IDaide_combi, IDunite FROM aides_combi_unites;"""
        self.parent.DB.ExecuterReq(req)
        self.dictUnites = {}
        for IDaide_combi, IDunite in self.parent.DB.ResultatReq():
            if IDaide_combi not in self.dictUnites:
                self.dictUnites[IDaide_combi] = []
            self.dictUnites[IDaide_combi].append(IDunite)
        Table.__init__(self, parent, **kwds)
        del self.dictMontants
        del self.dictUnites

    def montant(self, data={}):
        """ Champ ManyToMany"""
        IDaide_combi = data["pk"]
        if IDaide_combi in self.dictMontants:
            return self.dictMontants[IDaide_combi]
        return 0.0

    def unites(self, data={}):
        """ Champ ManyToMany"""
        IDaide_combi = data["pk"]
        if IDaide_combi in self.dictUnites:
            return self.dictUnites[IDaide_combi]
        return []


class Table_deductions(Table):
    def __init__(self, parent, **kwds):
        # Importe les prestations
        req = """SELECT IDprestation, date FROM prestations;"""
        parent.DB.ExecuterReq(req)
        self.dictPrestations = {}
        for IDprestation, date in parent.DB.ResultatReq():
            self.dictPrestations[IDprestation] = date
        Table.__init__(self, parent, **kwds)
        del self.dictPrestations

    def valide_ligne(self, data={}):
        """ Incorpore la ligne uniquement la prestation associée existe"""
        if data["fields"]["prestation"] not in self.dictPrestations:
            return False
        return True

    def famille(self, data={}):
        return self.parent.dictComptesPayeurs[data["IDcompte_payeur"]]


class Table_documents_modeles(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Importation de tous les objets des modèles
        listeChamps = []
        for nom, type_champ, info in DICT_CHAMPS["documents_objets"]:
            listeChamps.append(nom)
        req = "SELECT * FROM documents_objets ORDER BY ordre;"
        self.parent.DB.ExecuterReq(req)
        self.dict_objets = {}
        for objet in self.parent.DB.ResultatReq():
            dict_objet = {}
            for index in range(1, len(listeChamps)):
                nom_champ = listeChamps[index]
                dict_objet[nom_champ] = objet[index]
            if dict_objet["IDmodele"] not in self.dict_objets:
                self.dict_objets[dict_objet["IDmodele"]] = []
            self.dict_objets[dict_objet["IDmodele"]].append(dict_objet)

        Table.__init__(self, parent, **kwds)
        del self.dict_objets

    def IDfond(self, valeur=None, objet=None):
        """ Changement de valeur par défaut """
        if valeur == 0:
            valeur = None
        return valeur

    def objets(self, data={}):
        """ Création d'un champ supplémentaire """
        liste_objets = []
        IDmodele = data["pk"]
        if IDmodele in self.dict_objets:
            for dict_objet in self.dict_objets[IDmodele]:
                objet = None

                # Rectangle
                if dict_objet["categorie"] == "rectangle":
                    objet = json.loads("""{"type":"rect","version":"3.4.0","originX":"left","originY":"top","left":80,"top":123.5,"width":50,"height":50,"fill":"rgba(122,156,255,1)","stroke":"rgba(0,0,0,1)","strokeWidth":0,"strokeDashArray":null,"strokeLineCap":"butt","strokeDashOffset":0,"strokeLineJoin":"miter","strokeMiterLimit":4,"scaleX":1,"scaleY":1,"angle":0,"flipX":false,"flipY":false,"opacity":1,"shadow":null,"visible":true,"clipTo":null,"backgroundColor":"","fillRule":"nonzero","paintFirst":"fill","globalCompositeOperation":"source-over","transformMatrix":null,"skewX":0,"skewY":0,"rx":0,"ry":0,"nom":"Rectangle","categorie":"rectangle"}""")
                    objet = {
                        "type": "rect", "categorie": "rectangle", "nom": dict_objet["nom"],
                        "left": dict_objet["x"], "top": data["fields"]["hauteur"] - dict_objet["y"] - dict_objet["hauteur"], "width": dict_objet["largeur"], "height": dict_objet["hauteur"],
                        "fill": self.ConvertCouleur(dict_objet["coulRemplis"], transparent=dict_objet["largeur"] == 'Transparent'),
                        "strokeWidth": dict_objet["epaissTrait"], "stroke": self.ConvertCouleur(dict_objet["couleurTrait"]),
                        "strokeDashArray": self.ConvertTrait(dict_objet["styleTrait"]),
                    }

                # Cercle
                if dict_objet["categorie"] == "cercle":
                    objet = {
                        "type": "circle", "categorie": "cercle", "nom": dict_objet["nom"],
                        "left": dict_objet["x"], "top": data["fields"]["hauteur"] - dict_objet["y"] - dict_objet["hauteur"], "width": dict_objet["largeur"], "height": dict_objet["hauteur"],
                        "fill": self.ConvertCouleur(dict_objet["coulRemplis"], transparent=dict_objet["largeur"] == 'Transparent'),
                        "strokeWidth": dict_objet["epaissTrait"], "stroke": self.ConvertCouleur(dict_objet["couleurTrait"]),
                        "strokeDashArray": self.ConvertTrait(dict_objet["styleTrait"]),
                    }

                # Ligne
                if dict_objet["categorie"] == "ligne":
                    point1, point2 = dict_objet["points"][:-1].split(";")
                    x1, y1 = point1.split(",")
                    x2, y2 = point2.split(",")
                    top = data["fields"]["hauteur"] - dict_objet["y"]
                    objet = {
                        "type": "line", "categorie": "ligne", "nom": dict_objet["nom"],
                        "left": dict_objet["x"], "top": top, "width": float(x2) - float(x1), "height": top,
                        "fill": self.ConvertCouleur(dict_objet["coulRemplis"]),
                        "strokeWidth": dict_objet["epaissTrait"], "stroke": self.ConvertCouleur(dict_objet["couleurTrait"]),
                        "strokeDashArray": self.ConvertTrait(dict_objet["styleTrait"]),
                        "champ": dict_objet["champ"], "x1": float(x1), "y1": top, "x2": float(x2), "y2": top,
                    }

                # Texte
                if dict_objet["categorie"] == "bloc_texte":
                    top = data["fields"]["hauteur"] - dict_objet["y"]
                    objet = {
                        "type": "textbox", "categorie": "texte", "nom": dict_objet["nom"],
                        "fontFamily": "Arial", "fontSize": dict_objet["taillePolice"],
                        "left": dict_objet["x"], "top": top, "width": 500, "height": dict_objet["hauteur"],
                        "fill": self.ConvertCouleur(dict_objet["couleurTexte"]),
                        "text": dict_objet["texte"], "scaleX": 0.33, "scaleY": 0.33,
                    }

                # Image
                if dict_objet["categorie"] == "image" and dict_objet["typeImage"].startswith("fichier"):
                    try:
                        image = Image.open(six.BytesIO(dict_objet["image"]))
                        taille_image = image.size
                        buffer = six.BytesIO()
                        image.save(buffer, format=image.format)
                        image64 = base64.b64encode(buffer.getvalue())

                        objet = json.loads("""{"type":"image","version":"3.4.0","originX":"left","originY":"top","left":41,"top":84.5,"width":128,"height":128,"fill":"rgb(0,0,0)","stroke":"rgba(0,0,0,0)","strokeWidth":0,"strokeDashArray":null,"strokeLineCap":"butt","strokeDashOffset":0,"strokeLineJoin":"miter","strokeMiterLimit":4,"scaleX":1,"scaleY":1,"angle":0,"flipX":false,"flipY":false,"opacity":1,"shadow":null,"visible":true,"clipTo":null,"backgroundColor":"","fillRule":"nonzero","paintFirst":"fill","globalCompositeOperation":"source-over","transformMatrix":null,"skewX":0,"skewY":0,"crossOrigin":"","cropX":0,"cropY":0,"nom":"Image","categorie":"image","src":"data:image/png;base64,X","filters":[]}""")
                        scaleY = 1.0 * dict_objet["hauteur"] / taille_image[1]
                        top = data["fields"]["hauteur"] - dict_objet["y"] - taille_image[1] * scaleY
                        objet.update({
                            "type": "image", "categorie": "logo", "nom": dict_objet["nom"],
                            "left": dict_objet["x"], "top": top, "width": taille_image[0], "height": taille_image[1],
                            "scaleX": scaleY, "scaleY": scaleY, "fill": self.ConvertCouleur(dict_objet["coulRemplis"]),
                            "strokeWidth": dict_objet["epaissTrait"], "stroke": self.ConvertCouleur(dict_objet["couleurTrait"]),
                            "strokeDashArray": self.ConvertTrait(dict_objet["styleTrait"]),
                            "src": "data:image/png;base64,%s" % image64
                        })
                    except:
                        pass

                # Photo individuelle
                if dict_objet["typeImage"] == "photo":
                    objet = json.loads("""{"type":"image","version":"3.4.0","originX":"left","originY":"top","left":3,"top":3,"width":128,"height":128,"fill":"rgb(0,0,0)","stroke":"rgba(0,0,0,0)","strokeWidth":0,"strokeDashArray":null,"strokeLineCap":"butt","strokeDashOffset":0,"strokeLineJoin":"miter","strokeMiterLimit":4,"scaleX":0.19,"scaleY":0.19,"angle":0,"flipX":false,"flipY":false,"opacity":1,"shadow":null,"visible":true,"clipTo":null,"backgroundColor":"","fillRule":"nonzero","paintFirst":"fill","globalCompositeOperation":"source-over","transformMatrix":null,"skewX":0,"skewY":0,"crossOrigin":"","cropX":0,"cropY":0,"nom":"Photo individuelle","categorie":"photo","src":"/static/images/femme.png","filters":[]}""")
                    scaleY = 1.0 * dict_objet["hauteur"] / 128
                    top = data["fields"]["hauteur"] - dict_objet["y"] - 128 * scaleY
                    objet.update({
                        "type": "image", "categorie": "photo", "nom": dict_objet["nom"],
                        "left": dict_objet["x"], "top": top, "width": 128, "height": 128,
                        "scaleX": scaleY, "scaleY": scaleY,
                        "fill": self.ConvertCouleur(dict_objet["coulRemplis"]),
                        "strokeWidth": dict_objet["epaissTrait"], "stroke": self.ConvertCouleur(dict_objet["couleurTrait"]),
                        "strokeDashArray": self.ConvertTrait(dict_objet["styleTrait"]),
                    })

                # Logo
                if dict_objet["typeImage"] == "logo":
                    req = "SELECT logo FROM organisateur WHERE IDorganisateur=1;"
                    self.parent.DB.ExecuterReq(req)
                    logo = self.parent.DB.ResultatReq()[0][0]
                    if logo != None:
                        io = six.BytesIO(logo)
                        if 'phoenix' in wx.PlatformInfo:
                            img = wx.Image(io, wx.BITMAP_TYPE_ANY)
                        else:
                            img = wx.ImageFromStream(io, wx.BITMAP_TYPE_ANY)
                        taille_logo = img.GetSize()

                        objet = json.loads("""{"type":"image","version":"3.4.0","originX":"left","originY":"top","left":11.49,"top":54.99,"width":500,"height":500,"fill":"rgb(0,0,0)","stroke":"rgba(0,0,0,0)","strokeWidth":0,"strokeDashArray":null,"strokeLineCap":"butt","strokeDashOffset":0,"strokeLineJoin":"miter","strokeMiterLimit":4,"scaleX":0.37,"scaleY":0.37,"angle":0,"flipX":false,"flipY":false,"opacity":1,"shadow":null,"visible":true,"clipTo":null,"backgroundColor":"","fillRule":"nonzero","paintFirst":"fill","globalCompositeOperation":"source-over","transformMatrix":null,"skewX":0,"skewY":0,"crossOrigin":"","cropX":0,"cropY":0,"nom":"Logo organisateur","categorie":"logo","src":"/media/organisateur/logo.png","filters":[]}""")
                        scaleY = 1.0 * dict_objet["hauteur"] / taille_logo[1]
                        top = data["fields"]["hauteur"] - dict_objet["y"] - taille_logo[1] * scaleY
                        objet.update({
                            "type": "image", "categorie": "logo", "nom": dict_objet["nom"],
                            "left": dict_objet["x"], "top": top, "width": taille_logo[0], "height": taille_logo[1],
                            "scaleX": scaleY, "scaleY": scaleY,
                            "fill": self.ConvertCouleur(dict_objet["coulRemplis"]),
                            "strokeWidth": dict_objet["epaissTrait"], "stroke": self.ConvertCouleur(dict_objet["couleurTrait"]),
                            "strokeDashArray": self.ConvertTrait(dict_objet["styleTrait"]),
                        })

                # Spécial
                if dict_objet["categorie"] == "special":
                    objet = {
                        "type": "rect", "categorie": "special", "nom": dict_objet["nom"],
                        "left": dict_objet["x"], "top": data["fields"]["hauteur"] - dict_objet["y"] - dict_objet["hauteur"], "width": dict_objet["largeur"], "height": dict_objet["hauteur"],
                        "fill": self.ConvertCouleur(dict_objet["coulRemplis"]),
                        "strokeWidth": dict_objet["epaissTrait"], "stroke": self.ConvertCouleur(dict_objet["couleurTrait"]),
                        "strokeDashArray": self.ConvertTrait(dict_objet["styleTrait"]),
                        "champ": dict_objet["champ"],
                    }

                # Barcode
                if dict_objet["categorie"] == "barcode":
                    objet = json.loads("""{"type":"image","version":"3.4.0","originX":"left","originY":"top","left":84.21,"top":145.03,"width":462,"height":139,"fill":"rgb(0,0,0)","stroke":"rgba(0,0,0,0)","strokeWidth":0,"strokeDashArray":null,"strokeLineCap":"butt","strokeDashOffset":0,"strokeLineJoin":"miter","strokeMiterLimit":4,"scaleX":0.09,"scaleY":0.05,"angle":0,"flipX":false,"flipY":false,"opacity":1,"shadow":null,"visible":true,"clipTo":null,"backgroundColor":"","fillRule":"nonzero","paintFirst":"fill","globalCompositeOperation":"source-over","transformMatrix":null,"skewX":0,"skewY":0,"crossOrigin":"","cropX":0,"cropY":0,"nom":"Code-barres ID de l'individu","categorie":"barcode","champ":"{CODEBARRES_ID_INDIVIDU}","cb_norme":"Extended39","cb_affiche_numero":false,"src":"/static/images/codebarres.png","filters":[]}""")
                    top = data["fields"]["hauteur"] - dict_objet["y"] - dict_objet["hauteur"]
                    objet.update({
                        "type": "image", "categorie": "barcode", "nom": dict_objet["nom"],
                        "left": dict_objet["x"], "top": top, "width": dict_objet["largeur"] / objet["scaleX"],
                        "height": dict_objet["hauteur"] / objet["scaleY"],
                        "champ": dict_objet["champ"],
                    })

                if objet:
                    liste_objets.append(objet)

        return """%s""" % json.dumps(liste_objets)

    def ConvertCouleur(self, couleur="(0, 0, 0)", transparent=False):
        try:
            couleur = couleur[1:-1].split(",")
            if transparent == True:
                alpha = 0
            else:
                alpha = 1
            return 'rgba(%d,%d,%d,%d)' % (int(couleur[0]), int(couleur[1]), int(couleur[2]), alpha)
        except:
            return couleur

    def ConvertTrait(self, style="Solid"):
        if style == "Solid": return None
        if style == "Dot": return [1,2]
        if style == "LongDash": return [6,3]
        if style == "ShortDash": return [3,6]
        if style == "DotDash": return [6,2,3]
        return None


class Table_questions(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Importation de la table des choix
        req = "SELECT IDchoix, IDquestion, label FROM questionnaire_choix ORDER BY ordre;"
        self.parent.DB.ExecuterReq(req)
        self.dict_choix = {}
        for IDchoix, IDquestion, label in self.parent.DB.ResultatReq():
            if IDquestion not in self.dict_choix:
                self.dict_choix[IDquestion] = []
            self.dict_choix[IDquestion].append(label)

        # Importation de la table des catégories
        req = "SELECT IDcategorie, type, label FROM questionnaire_categories ORDER BY ordre;"
        self.parent.DB.ExecuterReq(req)
        self.dict_categories = {}
        for IDcategorie, type_question, label in self.parent.DB.ResultatReq():
            self.dict_categories[IDcategorie] = type_question

        Table.__init__(self, parent, **kwds)
        del self.dict_choix
        del self.dict_categories

    def IDcategorie(self, valeur=None, objet=None):
        return self.dict_categories[valeur]

    def choix(self, data={}):
        if data["pk"] in self.dict_choix:
            return ";".join(self.dict_choix[data["pk"]])
        return None

    def options(self, valeur=None, objet=None):
        return None


class Table_reponses(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Importation de la table des choix
        req = "SELECT IDchoix, label FROM questionnaire_choix ORDER BY ordre;"
        self.parent.DB.ExecuterReq(req)
        self.dict_choix = {}
        for IDchoix, label in self.parent.DB.ResultatReq():
            self.dict_choix[IDchoix] = label

        # Récupération des individus
        req = """SELECT IDindividu, nom FROM individus;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_individus = []
        for IDindividu, nom in self.parent.DB.ResultatReq():
            self.liste_individus.append(IDindividu)

        # Récupération des familles
        req = """SELECT IDfamille, date_creation FROM familles;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_familles = []
        for IDfamille, date_creation in self.parent.DB.ResultatReq():
            self.liste_familles.append(IDfamille)

        Table.__init__(self, parent, **kwds)
        del self.dict_choix
        del self.liste_individus
        del self.liste_familles

    def valide_ligne(self, data={}):
        """ Incorpore la ligne uniquement le IDindividu existe"""
        valide = True
        if data["fields"]["individu"] and data["fields"]["individu"] not in self.liste_individus:
            valide = False
        if data["fields"]["famille"] and data["fields"]["famille"] not in self.liste_familles:
            valide = False
        return valide

    def reponse(self, valeur=None, objet=None):
        liste_reponse = []
        if valeur and ";" in valeur:
            for IDchoix in valeur.split(";"):
                try:
                    IDchoix = int(IDchoix)
                except:
                    pass
                if IDchoix in self.dict_choix:
                    liste_reponse.append(self.dict_choix[IDchoix])
                else:
                    liste_reponse.append(IDchoix)
            if six.PY3:
                valeur = ";".join([str(reponse) for reponse in liste_reponse])
            else:
                valeur = ";".join([unicode(reponse) for reponse in liste_reponse])
        return valeur


class Table_payeurs(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Récupèration des familles
        req = """select IDpayeur, familles.IDfamille FROM payeurs
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = payeurs.IDcompte_payeur
        LEFT JOIN familles ON familles.IDfamille = comptes_payeurs.IDfamille;"""
        self.parent.DB.ExecuterReq(req)
        self.dict_familles = {}
        for IDpayeur, IDfamille in self.parent.DB.ResultatReq():
            self.dict_familles[IDpayeur] = IDfamille

        Table.__init__(self, parent, **kwds)
        del self.dict_familles

    def valide_ligne(self, data={}):
        """ Incorpore la ligne uniquement le IDfamille existe"""
        valide = True
        if not self.dict_familles.get(data["pk"], None):
            valide = False
        return valide

    def famille(self, data={}):
        return self.parent.dictComptesPayeurs[data["IDcompte_payeur"]]


class Table_reglements(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent

        # Importation de la table des payeurs
        req = "SELECT IDpayeur, IDcompte_payeur FROM payeurs;"
        self.parent.DB.ExecuterReq(req)
        self.liste_payeurs = []
        for IDpayeur, IDcompte_payeur in self.parent.DB.ResultatReq():
            self.liste_payeurs.append(IDpayeur)

        # Importation de la table des dépôts
        req = "SELECT IDdepot, nom FROM depots;"
        self.parent.DB.ExecuterReq(req)
        self.liste_depots = []
        for IDdepot, nom in self.parent.DB.ResultatReq():
            self.liste_depots.append(IDdepot)

        Table.__init__(self, parent, **kwds)
        del self.liste_payeurs
        del self.liste_depots

    def famille(self, data={}):
        return self.parent.dictComptesPayeurs[data["IDcompte_payeur"]]

    def encaissement_attente(self, valeur=None, objet=None):
        if valeur == None:
            return 0
        return valeur

    def IDdepot(self, valeur=None, objet=None):
        if valeur and valeur not in self.liste_depots:
            return None
        return valeur

    def IDpayeur(self, valeur=None, objet=None):
        if valeur not in self.liste_payeurs:
            try:
                # Le payeur n'existe plus, on essaie de trouver un autre payeur de la même famille
                req = "SELECT IDreglement, IDcompte_payeur FROM reglements WHERE IDpayeur=%d;" % valeur
                self.parent.DB.ExecuterReq(req)
                IDreglement, IDcompte_payeur = self.parent.DB.ResultatReq()[0]
                req = "SELECT IDpayeur, IDcompte_payeur FROM payeurs WHERE IDcompte_payeur=%d;" % IDcompte_payeur
                self.parent.DB.ExecuterReq(req)
                IDpayeur, IDcompte_payeur = self.parent.DB.ResultatReq()[0]
                return IDpayeur
            except:
                pass
        return valeur


class Table_ventilation(Table):
    def famille(self, data={}):
        return self.parent.dictComptesPayeurs[data["IDcompte_payeur"]]


class Table_recus(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent
        # Importation de la table des règlements
        req = "SELECT IDreglement, IDcompte_payeur FROM reglements;"
        self.parent.DB.ExecuterReq(req)
        self.liste_reglements = []
        for IDreglement, IDcompte_payeur in self.parent.DB.ResultatReq():
            self.liste_reglements.append(IDreglement)

        # Récupération des familles
        req = """SELECT IDfamille, date_creation FROM familles;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_familles = []
        for IDfamille, date_creation in self.parent.DB.ResultatReq():
            self.liste_familles.append(IDfamille)

        Table.__init__(self, parent, **kwds)
        del self.liste_reglements
        del self.liste_familles

    def valide_ligne(self, data={}):
        if data["fields"]["famille"] not in self.liste_familles:
            return False
        return True

    def IDreglement(self, valeur=None, objet=None):
        if valeur not in self.liste_reglements:
            return None
        return valeur


class Table_attestations(Table):
    def activites(self, valeur=None, objet=None):
        # Suppression de tous les idactivite en double
        valeur = ";".join(list({idactivite: None for idactivite in valeur.split(";")}.keys()))
        return valeur


class Table_devis(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent
        # Récupération des familles
        req = """SELECT IDfamille, date_creation FROM familles;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_familles = []
        for IDfamille, date_creation in self.parent.DB.ResultatReq():
            self.liste_familles.append(IDfamille)

        Table.__init__(self, parent, **kwds)
        del self.liste_familles

    def valide_ligne(self, data={}):
        valide = True
        if data["fields"]["famille"] and data["fields"]["famille"] not in self.liste_familles:
            valide = False
        return valide

    def activites(self, valeur=None, objet=None):
        # Suppression de tous les idactivite en double
        valeur = ";".join(list({idactivite: None for idactivite in valeur.split(";")}.keys()))
        return valeur


class Table_textes_rappels(Table):
    def couleur(self, valeur="", objet=None):
        return Rgb2hex(valeur)

    def html(self, data={}):
        html = data["texte_pdf"]
        html = re.sub('<para.*?>', '<p>', html)
        html = html.replace("""</para>""", "</p>")
        return html


class Table_rappels(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent
        # Importation de la table des lots de rappels
        req = "SELECT IDlot, nom FROM lots_rappels;"
        self.parent.DB.ExecuterReq(req)
        self.lots_rappels = []
        for IDlot, nom in self.parent.DB.ResultatReq():
            self.lots_rappels.append(IDlot)

        Table.__init__(self, parent, **kwds)
        del self.lots_rappels

    def famille(self, data={}):
        return self.parent.dictComptesPayeurs[data["IDcompte_payeur"]]

    def IDlot(self, valeur=None, objet=None):
        if valeur not in self.lots_rappels:
            return None
        return valeur

    def activites(self, valeur=None, objet=None):
        if valeur and len(valeur) > 200:
            valeur = None
        return valeur


class Table_modeles_emails(Table):
    def html(self, data={}):
        texte_xml = data["texte_xml"]
        ctrl_editeur = self.parent.dlg.ctrl_editeur
        html = None
        if texte_xml:
            if six.PY3 and isinstance(texte_xml, str):
                texte_xml = texte_xml.encode("utf8")
            try:
                ctrl_editeur.SetXML(texte_xml)
                html = ctrl_editeur.GetHTML()[0]
            except:
                html = ""
            for balise in ("<html>", "</html>", "<head>", "</head>", "<body>", "</body>", "\r\n", "</font>"):
                html = html.replace(balise, "")
            html = re.sub('<font.*?>', '', html)
        return html


class Table_mandats(Table):
    def sequence(self, valeur=None, objet=None):
        if valeur == "auto":
            return "RCUR"
        return valeur


class Table_transports(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent
        # Liste des transports pour vérifier le champ prog
        req = "SELECT IDtransport, categorie FROM transports;"
        self.parent.DB.ExecuterReq(req)
        self.liste_transports_prog = []
        for IDtransport, categorie in self.parent.DB.ResultatReq():
            self.liste_transports_prog.append(IDtransport)

        # Récupération des individus
        req = """SELECT IDindividu, nom FROM individus;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_individus = []
        for IDindividu, nom in self.parent.DB.ResultatReq():
            self.liste_individus.append(IDindividu)

        # Récupération des compagnies
        req = """SELECT IDcompagnie, nom FROM transports_compagnies;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_compagnies = []
        for IDcompagnie, nom in self.parent.DB.ResultatReq():
            self.liste_compagnies.append(IDcompagnie)

        # Récupération des lignes
        req = """SELECT IDligne, nom FROM transports_lignes;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_lignes = []
        for IDligne, nom in self.parent.DB.ResultatReq():
            self.liste_lignes.append(IDligne)

        # Récupération des arrêts
        req = """SELECT IDarret, nom FROM transports_arrets;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_arrets = []
        for IDarret, nom in self.parent.DB.ResultatReq():
            self.liste_arrets.append(IDarret)

        # Récupération des lieux
        req = """SELECT IDlieu, nom FROM transports_lieux;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_lieux = []
        for IDlieu, nom in self.parent.DB.ResultatReq():
            self.liste_lieux.append(IDlieu)

        # Récupération des unités de conso
        req = """SELECT IDunite, nom FROM unites;"""
        self.parent.DB.ExecuterReq(req)
        self.liste_unites = []
        for IDunite, nom in self.parent.DB.ResultatReq():
            self.liste_unites.append(IDunite)

        Table.__init__(self, parent, **kwds)
        del self.liste_transports_prog
        del self.liste_individus
        del self.liste_compagnies
        del self.liste_lignes
        del self.liste_arrets
        del self.liste_lieux
        del self.liste_unites

    def valide_ligne(self, data={}):
        valide = True
        if data["fields"]["individu"] and data["fields"]["individu"] not in self.liste_individus:
            print("pas de individu pour le transport ID%d" % data["pk"])
            valide = False
        if data["fields"]["compagnie"] and data["fields"]["compagnie"] not in self.liste_compagnies:
            print("pas de compagnie pour le transport ID%d" % data["pk"])
            valide = False
        if data["fields"]["ligne"] and data["fields"]["ligne"] not in self.liste_lignes:
            print("pas de ligne pour le transport ID%d" % data["pk"])
            valide = False
        if data["fields"]["depart_arret"] and data["fields"]["depart_arret"] not in self.liste_arrets:
            print("pas d'arret de depart pour le transport ID%d" % data["pk"])
            valide = False
        if data["fields"]["depart_lieu"] and data["fields"]["depart_lieu"] not in self.liste_lieux:
            print("pas de lieu de depart pour le transport ID%d" % data["pk"])
            valide = False
        if data["fields"]["arrivee_arret"] and data["fields"]["arrivee_arret"] not in self.liste_arrets:
            print("pas d'arret de arrivee pour le transport ID%d" % data["pk"])
            valide = False
        if data["fields"]["arrivee_lieu"] and data["fields"]["arrivee_lieu"] not in self.liste_lieux:
            print("pas de lieu de arrivee pour le transport ID%d" % data["pk"])
            valide = False
        return valide

    def jours_scolaires(self, valeur=None, objet=None):
        if valeur:
            valeur = valeur.replace(";", ",")
        return valeur

    def jours_vacances(self, valeur=None, objet=None):
        if valeur:
            valeur = valeur.replace(";", ",")
        return valeur

    def unites(self, valeur=None, objet=None):
        unites = []
        if valeur:
            for idunite in valeur.split(";"):
                if int(idunite) in self.liste_unites:
                    unites.append(int(idunite))
                else:
                    print("pas d'unite %s" % idunite)
        return unites

    def prog(self, valeur=None, objet=None):
        if valeur and valeur in self.liste_transports_prog:
            return valeur
        return None


class Table_prelevements(Table):
    def __init__(self, parent, **kwds):
        self.parent = parent
        # Importation de la table des règlements
        req = "SELECT IDreglement, IDprelevement FROM reglements;"
        self.parent.DB.ExecuterReq(req)
        self.reglements = {}
        for IDreglement, IDprelevement in self.parent.DB.ResultatReq():
            self.reglements[IDprelevement] = IDreglement
        # Importation de la table des factures
        req = "SELECT IDfacture, numero FROM factures;"
        self.parent.DB.ExecuterReq(req)
        self.factures = []
        for IDfacture, numero in self.parent.DB.ResultatReq():
            self.factures.append(IDfacture)

        Table.__init__(self, parent, **kwds)
        del self.reglements
        del self.factures

    def reglement(self, data={}):
        return self.reglements.get(data["IDprelevement"], None)

    def type(self, valeur=None, objet=None):
        if valeur == "facture" and objet[14] not in self.factures:
            return "manuel"
        return valeur

    def IDfacture(self, valeur=None, objet=None):
        if objet[13] == u"facture" and objet[14] not in self.factures:
            return None
        return valeur


class Table_modeles_prelevements(Table):
    def Get_data(self):
        # Génération de modèles pour les lots de prélèvements
        req = "SELECT IDlot, format, IDcompte, IDmode, reglement_auto, encodage, IDperception, identifiant_service, poste_comptable FROM lots_prelevements;"
        self.parent.DB.ExecuterReq(req)
        liste_modeles = []
        self.parent.dict_modeles_prelevements = {}
        for IDlot, format, IDcompte, IDmode, reglement_auto, encodage, IDperception, identifiant_service, poste_comptable in self.parent.DB.ResultatReq():
            dict_modele = {"format": format or "prive", "compte": IDcompte, "mode": IDmode, "reglement_auto": reglement_auto, "encodage": encodage or "utf-8",
                           "perception": IDperception, "identifiant_service": identifiant_service, "poste_comptable": poste_comptable}
            if dict_modele in liste_modeles:
                IDmodele = liste_modeles.index(dict_modele) + 1
            else:
                liste_modeles.append(dict_modele)
                IDmodele = len(liste_modeles)
            self.parent.dict_modeles_prelevements[IDlot] = IDmodele

        liste_xml = []
        for index, dict_modele in enumerate(liste_modeles, start=1):
            dict_modele["nom"] = u"Mod�le %d" % index
            liste_xml.append({"model": "core.PrelevementsModele", "pk": index, "fields": dict_modele})
        return liste_xml


class Table_lots_prelevements(Table):
    def modele(self, data={}):
        return self.parent.dict_modeles_prelevements[data["IDlot"]]

    def numero_sequence(self, data={}):
        return 1


class Table_tarifs_produits(Table):
    def Get_data(self):
        # Importation des montants des tarifs
        req = """SELECT IDtarif, montant_unique FROM tarifs_lignes;"""
        self.parent.DB.ExecuterReq(req)
        dict_montants = {IDtarif: montant_unique for IDtarif, montant_unique in self.parent.DB.ResultatReq()}
        # Importation des tarifs des produits
        req = """SELECT IDtarif, IDproduit, date_debut, date_fin, description, observations, tva, label_prestation, code_compta, methode
        FROM tarifs WHERE IDproduit IS NOT NULL;"""
        self.parent.DB.ExecuterReq(req)
        liste_xml = []
        index = 1
        for IDtarif, IDproduit, date_debut, date_fin, description, observations, tva, label_prestation, code_compta, methode in self.parent.DB.ResultatReq():
            liste_xml.append({"model": "core.TarifProduit", "pk": index, "fields": {
                "produit": IDproduit, "date_debut": date_debut, "date_fin": date_fin, "description": description, "observations": observations,
                "tva": tva, "label_prestation": label_prestation, "code_compta": code_compta, "methode": methode, "montant": dict_montants.get(IDtarif, 0.0)}})
            index += 1

        del dict_montants
        return liste_xml


def Verifications(parent=None):
    """ Vérifications générales avant export """
    DB = GestionDB.DB()

    # # Forfaits-crédits
    # req = "SELECT IDtarif, type FROM tarifs WHERE type='CREDIT';"
    # DB.ExecuterReq(req)
    # resultats = DB.ResultatReq()
    # if resultats:
    #     dlg = wx.MessageDialog(parent, u"Les forfait-crédits ne sont pas encore disponibles dans Noethysweb. Souhaitez-vous quand même continuer ?", u"Avertissement", wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
    #     reponse = dlg.ShowModal()
    #     dlg.Destroy()
    #     if reponse != wx.ID_YES:
    #         DB.Close()
    #         return False

    # # Méthode selon nbre enfants présents
    # req = "SELECT IDtarif, methode FROM tarifs WHERE methode LIKE 'montant_enfant';"
    # DB.ExecuterReq(req)
    # resultats = DB.ResultatReq()
    # if resultats:
    #     dlg = wx.MessageDialog(parent, u"La méthode tarifaire selon le nombre d'enfants présents ne sont pas encore disponibles dans Noethysweb. Souhaitez-vous quand même continuer ?", u"Avertissement", wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)
    #     reponse = dlg.ShowModal()
    #     dlg.Destroy()
    #     if reponse != wx.ID_YES:
    #         DB.Close()
    #         return False

    DB.Close()
    return True
