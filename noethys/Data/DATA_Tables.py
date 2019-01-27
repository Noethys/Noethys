#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

TABLES_IMPORTATION_OPTIONNELLES = [ 
        [u"Périodes de vacances", ("vacances",), True],
        [u"Jours fériés", ("jours_feries",), True],
        [u"Vaccins et maladies", ("types_vaccins", "vaccins_maladies", "types_maladies",), True],
        [u"Types de sieste", ("types_sieste",), True],
        [u"Catégories socio-professionnelles", ("categories_travail",), True],
        [u"Modes et émetteurs de règlements", ("modes_reglements", "emetteurs"), True],
        [u"Régimes d'appartenance", ("regimes",), True],
        [u"Modèles de documents", ("documents_modeles", "documents_objets"), True],
        [u"Modèles d'Emails", ("modeles_emails",), True],
        [u"Niveaux scolaires", ("niveaux_scolaires",), True],
        [u"Comptes comptables", ("compta_comptes_comptables",), True],
        [u"Types de quotients", ("types_quotients",), True],
        [u"Catégories médicales", ("categories_medicales",), True],
        [u"Eléments de pages du portail", ("portail_elements",), True],
        ] # [Nom Categorie, (liste des tables...,), Selectionné]

TABLES_IMPORTATION_OBLIGATOIRES = []


DB_DATA = {

    "individus":[               ("IDindividu", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID de la personne"),
                                    ("IDcivilite", "INTEGER", u"Civilité de la personne"),
                                    ("nom", "VARCHAR(100)", u"Nom de famille de la personne"),
                                    ("nom_jfille", "VARCHAR(100)", u"Nom de jeune fille de la personne"),
                                    ("prenom", "VARCHAR(100)", u"Prénom de la personne"),
                                    ("num_secu", "VARCHAR(21)", u"Numéro de sécurité sociale de la personne"),
                                    ("IDnationalite", "INTEGER", u"Nationalité de la personne"),
                                    
                                    ("date_naiss", "DATE", u"Date de naissance de la personne"),
                                    ("IDpays_naiss", "INTEGER", u"ID du Pays de naissance de la personne"),
                                    ("cp_naiss", "VARCHAR(10)", u"Code postal du lieu de naissance de la personne"),
                                    ("ville_naiss", "VARCHAR(100)", u"Ville du lieu de naissance de la personne"),
                                    ("deces", "INTEGER", u"Est décédé (0/1)"),
                                    ("annee_deces", "INTEGER", u"Année de décès"),
                                    
                                    ("adresse_auto", "INTEGER", u"IDindividu dont l'adresse est à reporter"),
                                    ("rue_resid", "VARCHAR(255)", u"Adresse de la personne"),
                                    ("cp_resid", "VARCHAR(10)", u"Code postal de la personne"),
                                    ("ville_resid", "VARCHAR(100)", u"Ville de la personne"), 
                                    ("IDsecteur", "INTEGER", u"Secteur géographique"), 
                                    
                                    ("IDcategorie_travail", "INTEGER", u"IDcategorie socio-professionnelle"),
                                    ("profession", "VARCHAR(100)", u"Profession de la personne"),  
                                    ("employeur", "VARCHAR(100)", u"Employeur de la personne"), 
                                    ("travail_tel", "VARCHAR(50)", u"Tel travail de la personne"),  
                                    ("travail_fax", "VARCHAR(50)", u"Fax travail de la personne"),  
                                    ("travail_mail", "VARCHAR(50)", u"Email travail de la personne"),  
                                    
                                    ("tel_domicile", "VARCHAR(50)", u"Tel domicile de la personne"),  
                                    ("tel_mobile", "VARCHAR(50)", u"Tel mobile perso de la personne"),  
                                    ("tel_fax", "VARCHAR(50)", u"Fax perso de la personne"),  
                                    ("mail", "VARCHAR(200)", u"Email perso de la personne"),

                                    ("travail_tel_sms", "INTEGER", u"SMS autorisé (0/1)"),
                                    ("tel_domicile_sms", "INTEGER", u"SMS autorisé (0/1)"),
                                    ("tel_mobile_sms", "INTEGER", u"SMS autorisé (0/1)"),

                                    ("IDmedecin", "INTEGER", u"ID du médecin traitant de l'individu"),
                                    ("memo", "VARCHAR(2000)", u"Mémo concernant l'individu"),  
                                    ("IDtype_sieste", "INTEGER", u"Type de sieste"),
                                    
                                    ("date_creation", "DATE", u"Date de création de la fiche individu"),
                                    ("etat", "VARCHAR(50)", u"Etat"),
                                    ], # Les individus
    
    
    "liens":[                     ("IDlien", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du lien"),
                                    ("IDfamille", "INTEGER", u"IDfamille"),
                                    ("IDindividu_sujet", "INTEGER", u"IDindividu sujet du lien"),
                                    ("IDtype_lien", "INTEGER", u"IDtype_lien"),
                                    ("IDindividu_objet", "INTEGER", u"IDindividu objet du lien"),
                                    ("responsable", "INTEGER", u"=1 si l'individu SUJET est responsable de l'individu objet"),
                                    ("IDautorisation", "INTEGER", u"ID autorisation"),
                                    ], # Les liens entre les individus
    
    "familles":[                ("IDfamille", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID de la famille"),
                                    ("date_creation", "DATE", u"Date de création de la fiche famille"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("IDcaisse", "INTEGER", u"ID de la caisse d'allocation"),
                                    ("num_allocataire", "VARCHAR(100)", u"Numéro d'allocataire"),
                                    ("allocataire", "INTEGER", u"ID de l'individu allocataire principal"),
                                    ("internet_actif", "INTEGER", u"(0/1) Compte internet actif"),
                                    ("internet_identifiant", "VARCHAR(300)", u"Code identifiant internet"),
                                    ("internet_mdp", "VARCHAR(300)", u"Mot de passe internet"),
                                    ("memo", "VARCHAR(2000)", u"Mémo concernant la famille"),  
                                    ("prelevement_activation", "INTEGER", u"Activation du prélèvement"),
                                    ("prelevement_etab", "VARCHAR(50)", u"Prélèvement - Code étab"),
                                    ("prelevement_guichet", "VARCHAR(50)", u"Prélèvement - Code guichet"),
                                    ("prelevement_numero", "VARCHAR(50)", u"Prélèvement - Numéro de compte"),
                                    ("prelevement_cle", "VARCHAR(50)", u"Prélèvement - Code clé"),
                                    ("prelevement_banque", "INTEGER", u"Prélèvement - ID de la Banque"),
                                    ("prelevement_individu", "INTEGER", u"Prélèvement - ID Individu"),
                                    ("prelevement_nom", "VARCHAR(200)", u"Prélèvement - nom titulaire"),
                                    ("prelevement_rue", "VARCHAR(400)", u"Prélèvement - rue titulaire"),
                                    ("prelevement_cp", "VARCHAR(50)", u"Prélèvement - cp titulaire"),
                                    ("prelevement_ville", "VARCHAR(400)", u"Prélèvement - ville titulaire"),
                                    ("prelevement_cle_iban", "VARCHAR(10)", u"Prélèvement - Clé IBAN"),
                                    ("prelevement_iban", "VARCHAR(100)", u"Prélèvement - Clé IBAN"),
                                    ("prelevement_bic", "VARCHAR(100)", u"Prélèvement - BIC"),
                                    ("prelevement_reference_mandat", "VARCHAR(300)", u"Prélèvement - Référence mandat"),
                                    ("prelevement_date_mandat", "DATE", u"Prélèvement - Date mandat"),
                                    ("prelevement_memo", "VARCHAR(450)", u"Prélèvement - Mémo"),
                                    ("email_factures", "VARCHAR(450)", u"Adresse Email pour envoi des factures"),
                                    ("email_recus", "VARCHAR(450)", u"Adresse Email pour envoi des reçus de règlements"),
                                    ("email_depots", "VARCHAR(450)", u"Adresse Email pour avis d'encaissement des règlements"),
                                    ("titulaire_helios", "INTEGER", u"IDindividu du titulaire Hélios"),
                                    ("code_comptable", "VARCHAR(450)", u"Code comptable pour facturation et export logiciels compta"),
                                    ("idtiers_helios", "VARCHAR(300)", u"IDtiers pour Hélios"),
                                    ("natidtiers_helios", "INTEGER", u"Nature IDtiers pour Hélios"),
                                    ("reftiers_helios", "VARCHAR(300)", u"Référence locale du tiers pour Hélios"),
                                    ("cattiers_helios", "INTEGER", u"Catégorie de tiers pour Hélios"),
                                    ("natjur_helios", "INTEGER", u"Nature juridique du tiers pour Hélios"),
                                    ("autorisation_cafpro", "INTEGER", u"Autorisation de consultation CAFPRO (0/1)"),
                                    ("autre_adresse_facturation", "VARCHAR(450)", u"Autre adresse de facturation"),
                                    ("etat", "VARCHAR(50)", u"Etat"),
                                    ], # Les familles
    
    "rattachements":[       ("IDrattachement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID rattachement"),
                                    ("IDindividu", "INTEGER", u"IDindividu sujet du rattachement"),
                                    ("IDfamille", "INTEGER", u"IDfamille objet du rattachement"),
                                    ("IDcategorie", "INTEGER", u"IDcategorie du rattachement (responsable|enfant|contact)"),
                                    ("titulaire", "INTEGER", u"=1 si l'individu est titulaire de la fiche famille"),
                                    ], # Les rattachements à une ou plusieurs familles

    "types_maladies":[     ("IDtype_maladie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type_maladie"),
                                    ("nom", "VARCHAR(100)", u"Nom de la maladie"),
                                    ("vaccin_obligatoire", "INTEGER", u"=1 si vaccin obligatoire"),
                                    ], # Types de maladies

    "types_vaccins":[       ("IDtype_vaccin", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type_vaccin"),
                                    ("nom", "VARCHAR(100)", u"Nom du vaccin"),
                                    ("duree_validite", "VARCHAR(50)", u"Durée de validité"),
                                    ], # Les types de vaccins

    "vaccins_maladies":[  ("IDvaccins_maladies", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID vaccins_maladies"),
                                    ("IDtype_vaccin", "INTEGER", u"IDtype_vaccin"),
                                    ("IDtype_maladie", "INTEGER", u"IDtype_maladie"),
                                    ], # Liens entre les vaccins et les maladies concernées
    
    "medecins":[              ("IDmedecin", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du médecin"),
                                    ("nom", "VARCHAR(100)", u"Nom de famille du médecin"),
                                    ("prenom", "VARCHAR(100)", u"Prénom du médecin"),
                                    ("rue_resid", "VARCHAR(255)", u"Adresse du médecin"),
                                    ("cp_resid", "VARCHAR(10)", u"Code postal du médecin"),
                                    ("ville_resid", "VARCHAR(100)", u"Ville du médecin"),  
                                    ("tel_cabinet", "VARCHAR(50)", u"Tel du cabinet du médecin"),  
                                    ("tel_mobile", "VARCHAR(50)", u"Tel du mobile du médecin"),  
                                    ], # Les médecins

    "vaccins":[                 ("IDvaccin", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du vaccin"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu concerné"),
                                    ("IDtype_vaccin", "INTEGER", u"ID du vaccin concerné"),
                                    ("date", "DATE", u"date du vaccin"),
                                    ], # Les vaccins des individus    

    "problemes_sante":[   ("IDprobleme", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du probleme de santé"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDtype", "INTEGER", u"ID du type de problème"),
                                    ("intitule", "VARCHAR(100)", u"Intitulé du problème"),
                                    ("date_debut", "DATE", u"Date de début du problème"),
                                    ("date_fin", "DATE", u"Date de fin du problème"),
                                    ("description", "VARCHAR(2000)", u"Description du problème"),
                                    ("traitement_medical", "INTEGER", u"Traitement médical (1/0)"),
                                    ("description_traitement", "VARCHAR(2000)", u"Description du traitement médical"),
                                    ("date_debut_traitement", "DATE", u"Date de début du traitement"),
                                    ("date_fin_traitement", "DATE", u"Date de fin du traitement"),
                                    ("eviction", "INTEGER", u"Eviction (1/0)"),
                                    ("date_debut_eviction", "DATE", u"Date de début de l'éviction"),
                                    ("date_fin_eviction", "DATE", u"Date de fin de l'éviction"),
                                    ("diffusion_listing_enfants", "INTEGER", u"Diffusion listing enfants (1/0)"),
                                    ("diffusion_listing_conso", "INTEGER", u"Diffusion listing consommations (1/0)"),
                                    ("diffusion_listing_repas", "INTEGER", u"Diffusion commande des repas (1/0)"),
                                    ], # Les problèmes de santé des individus  

    "vacances":[              ("IDvacance", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID periode vacances"),
                                    ("nom", "VARCHAR(100)", u"Nom de la période de vacances"),
                                    ("annee", "INTEGER", u"Année de la période de vacances"),
                                    ("date_debut", "DATE", u"Date de début"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ], # Calendrier des jours de vacances

    "jours_feries":[           ("IDferie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID jour férié"),
                                    ("type", "VARCHAR(10)", u"Type de jour férié : fixe ou variable"),
                                    ("nom", "VARCHAR(100)", u"Nom du jour férié"),
                                    ("jour", "INTEGER", u"Jour de la date"),
                                    ("mois", "INTEGER", u"Mois de la date"),
                                    ("annee", "INTEGER", u"Année de la date"),
                                    ], # Calendrier des jours fériés variables et fixes

    "categories_travail":[   ("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID catégorie socio-professionnelle"),
                                    ("nom", "VARCHAR(100)", u"Nom de la catégorie"),
                                    ], # Catégories socio-professionnelles des individus

    "types_pieces":[        ("IDtype_piece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type pièce"),
                                    ("nom", "VARCHAR(100)", u"Nom de la pièce"),
                                    ("public", "VARCHAR(12)", u"Public (individu ou famille)"),
                                    ("duree_validite", "VARCHAR(50)", u"Durée de validité"),
                                    ("valide_rattachement", "INTEGER", u"(0|1) Valide même si individu rattaché à une autre famille"),
                                    ], # Types de pièces

    "pieces":[                  ("IDpiece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Pièce"),
                                    ("IDtype_piece", "INTEGER", u"IDtype_piece"),
                                    ("IDindividu", "INTEGER", u"IDindividu"),
                                    ("IDfamille", "INTEGER", u"IDfamille"),
                                    ("date_debut", "DATE", u"Date de début"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ], # Pièces rattachées aux individus ou familles

    "organisateur":[          ("IDorganisateur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Organisateur"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'organisateur"),
                                    ("rue", "VARCHAR(200)", u"Adresse"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(100)", u"Ville"),  
                                    ("tel", "VARCHAR(50)", u"Tel travail"),  
                                    ("fax", "VARCHAR(50)", u"Fax travail"),  
                                    ("mail", "VARCHAR(100)", u"Email organisateur"),  
                                    ("site", "VARCHAR(100)", u"Adresse site internet"),  
                                    ("num_agrement", "VARCHAR(100)", u"Numéro d'agrément"),  
                                    ("num_siret", "VARCHAR(100)", u"Numéro SIRET"),  
                                    ("code_ape", "VARCHAR(100)", u"Code APE"),
                                    ("logo", "LONGBLOB", u"Logo de l'organisateur en binaire"),
                                    ("gps", "VARCHAR(200)", u"Coordonnées GPS au format 'lat;long' "),
                                    ("logo_update", "VARCHAR(50)", u"Horodatage de la dernière modification du logo"),
                                    ], # Organisateur

    "responsables_activite":[("IDresponsable", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Responsable"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("sexe", "VARCHAR(10)", u"Sexe de l'individu (H/F)"),
                                    ("nom", "VARCHAR(200)", u"Nom du responsable"),
                                    ("fonction", "VARCHAR(200)", u"Fonction"),
                                    ("defaut", "INTEGER", u"(0/1) Responsable sélectionné par défaut"),
                                    ], # Responsables de l'activité

    "activites":[               ("IDactivite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Activité"),
                                    ("nom", "VARCHAR(200)", u"Nom complet de l'activité"),
                                    ("abrege", "VARCHAR(50)", u"Nom abrégé de l'activité"),
                                    ("coords_org", "INTEGER", u"(0/1) Coordonnées identiques à l'organisateur"),
                                    ("rue", "VARCHAR(200)", u"Adresse"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(100)", u"Ville"),  
                                    ("tel", "VARCHAR(50)", u"Tel travail"),  
                                    ("fax", "VARCHAR(50)", u"Fax travail"),  
                                    ("mail", "VARCHAR(100)", u"Email"),  
                                    ("site", "VARCHAR(100)", u"Adresse site internet"),
                                    ("logo_org", "INTEGER", u"(0/1) Logo identique à l'organisateur"),
                                    ("logo", "LONGBLOB", u"Logo de l'activité en binaire"),
                                    ("date_debut", "DATE", u"Date de début de validité"),
                                    ("date_fin", "DATE", u"Date de fin de validité"),
                                    ("public", "VARCHAR(20)", u"Liste du public"),
                                    ("vaccins_obligatoires", "INTEGER", u"(0/1) Vaccins obligatoires pour l'individu inscrit"),
                                    ("date_creation", "DATE", u"Date de création de l'activité"),
                                    ("nbre_inscrits_max", "INTEGER", u"Nombre d'inscrits max"),
                                    ("code_comptable", "VARCHAR(450)", u"Code comptable pour facturation et export logiciels compta"),
                                    ("psu_activation", "INTEGER", u"Mode PSU : Activation"),
                                    ("psu_unite_prevision", "INTEGER", u"Mode PSU : IDunite prévision"),
                                    ("psu_unite_presence", "INTEGER", u"Mode PSU : IDunite présence"),
                                    ("psu_tarif_forfait", "INTEGER", u"Mode PSU : IDtarif forfait-crédit"),
                                    ("psu_etiquette_rtt", "INTEGER", u"Mode PSU : IDetiquette Absences RTT"),
                                    ("portail_inscriptions_affichage", "INTEGER", u"Inscriptions autorisées sur le portail (0/1)"),
                                    ("portail_inscriptions_date_debut", "DATETIME", u"Inscriptions autorisées - début d'affichage"),
                                    ("portail_inscriptions_date_fin", "DATETIME", u"Inscriptions autorisées - fin d'affichage"),
                                    ("portail_reservations_affichage", "INTEGER", u"Réservations autorisées sur le portail (0/1)"),
                                    ("portail_reservations_limite", "VARCHAR(100)", u"Date limite de modification d'une réservation"),
                                    ("portail_reservations_absenti", "VARCHAR(100)", u"Application d'une absence injustifiée"),
                                    ("portail_unites_multiples", "INTEGER", u"Sélection multiple d'unités autorisée (0/1)"),
                                    ("regie", "INTEGER", u"ID de la régie associée"),
                                    ], # Activités

    "agrements":[            ("IDagrement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Agrément"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("agrement", "VARCHAR(200)", u"Numéro d'agrément"),
                                    ("date_debut", "DATE", u"Date de début de validité"),
                                    ("date_fin", "DATE", u"Date de fin de validité"),
                                    ], # Agréments de l'activité

    "groupes":[                ("IDgroupe", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Groupe"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("nom", "VARCHAR(200)", u"Nom du groupe"),
                                    ("abrege", "VARCHAR(100)", u"Nom abrégé du groupe"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("nbre_inscrits_max", "INTEGER", u"Nombre d'inscrits max"),
                                    ], # Groupes

    "pieces_activites":[    ("IDpiece_activite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Pièce activité"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("IDtype_piece", "INTEGER", u"ID du type de pièce à fournir"),
                                    ], # Pièces à fournir pour une activité

    "cotisations_activites":[("IDcotisation_activite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Cotisation activité"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("IDtype_cotisation", "INTEGER", u"ID du type de cotisation à fournir"),
                                    ], # Cotisations à avoir pour une activité

    "renseignements_activites":[("IDrenseignement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Renseignement"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("IDtype_renseignement", "INTEGER", u"ID du type de renseignement à fournir"),
                                    ], # Informations à renseigner par les individus pour une activité

    "restaurateurs":[        ("IDrestaurateur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Restaurateur"),
                                    ("nom", "VARCHAR(200)", u"Nom du restaurateur"),
                                    ("rue", "VARCHAR(200)", u"Adresse"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(100)", u"Ville"),  
                                    ("tel", "VARCHAR(50)", u"Tel travail"),  
                                    ("fax", "VARCHAR(50)", u"Fax travail"),  
                                    ("mail", "VARCHAR(100)", u"Email"),  
                                    ], # Restaurateurs

    "unites":[                   ("IDunite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Unité"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'unité"),
                                    ("abrege", "VARCHAR(50)", u"Nom abrégé"),
                                    ("type", "VARCHAR(20)", u"Type (unitaire/horaire)"),
                                    ("heure_debut", "DATE", u"Horaire minimum"),
                                    ("heure_debut_fixe", "INTEGER", u"Heure de début fixe (0/1)"),
                                    ("heure_fin", "DATE", u"Horaire maximal"),  
                                    ("heure_fin_fixe", "INTEGER", u"Heure de fin fixe (0/1)"),
                                    ("repas", "INTEGER", u"Repas inclus (0/1)"),  
                                    ("IDrestaurateur", "INTEGER", u"IDrestaurateur"),
                                    ("date_debut", "DATE", u"Date de début de validité"),  
                                    ("date_fin", "DATE", u"Date de fin de validité"),
                                    ("touche_raccourci", "VARCHAR(30)", u"Touche de raccourci pour la grille de saisie"), 
                                    ("largeur", "INTEGER", u"Largeur de colonne en pixels"),
                                    ("coeff", "VARCHAR(50)", u"Coeff pour état global"),
                                    ("autogen_active", "INTEGER", u"Autogénération activée (0/1)"),
                                    ("autogen_conditions", "VARCHAR(400)", u"Conditions de l'autogénération"),
                                    ("autogen_parametres", "VARCHAR(400)", u"Paramètres de l'autogénération"),
                                    ], # Unités

    "unites_groupes":[      ("IDunite_groupe", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Unité_groupe"),
                                    ("IDunite", "INTEGER", u"ID de l'unité concernée"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe associé"),  
                                    ], # Groupes concernés par l'unité

    "unites_incompat":[    ("IDunite_incompat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Unité_incompat"),
                                    ("IDunite", "INTEGER", u"ID de l'unité concernée"),
                                    ("IDunite_incompatible", "INTEGER", u"ID de l'unité incompatible"),  
                                    ], # Unités incompatibles entre elles

    "unites_remplissage":[("IDunite_remplissage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Unité_remplissage"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'unité de remplissage"),
                                    ("abrege", "VARCHAR(50)", u"Nom abrégé"),
                                    ("date_debut", "DATE", u"Date de début de validité"),  
                                    ("date_fin", "DATE", u"Date de fin de validité"),
                                    ("seuil_alerte", "INTEGER", u"Seuil d'alerte de remplissage"),
                                    ("heure_min", "DATE", u"Plage horaire conditionnelle - Heure min"),
                                    ("heure_max", "DATE", u"Plage horaire conditionnelle - Heure max"),  
                                    ("afficher_page_accueil", "INTEGER", u"Afficher dans le cadre Effectifs de la page d'accueil"),
                                    ("afficher_grille_conso", "INTEGER", u"Afficher dans la grille des conso"),
                                    ("etiquettes", "VARCHAR(450)", u"Etiquettes associées"),
                                    ("largeur", "INTEGER", u"Largeur de colonne en pixels"),
                                    ], # Unités de remplissage

    "unites_remplissage_unites":[("IDunite_remplissage_unite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Unité_remplissage_unite"),
                                    ("IDunite_remplissage", "INTEGER", u"ID de l'unité de remplissage concernée"),
                                    ("IDunite", "INTEGER", u"ID de l'unité associée"),  
                                    ], # Unités associées aux unités de remplissage
                                    
    "ouvertures":[             ("IDouverture", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID ouverture"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("IDunite", "INTEGER", u"ID de l'unité concernée"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe concerné"),
                                    ("date", "DATE", u"Date de l'ouverture"),  
                                    ], # Jours de fonctionnement des unités
                                    
    "remplissage":[          ("IDremplissage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID remplissage"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("IDunite_remplissage", "INTEGER", u"ID de l'unité de remplissage concernée"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe concerné"),
                                    ("date", "DATE", u"Date de l'ouverture"),
                                    ("places", "INTEGER", u"Nbre de places"),  
                                    ], # Nbre de places maxi pour chaque unité de remplissage

    "categories_tarifs":[    ("IDcategorie_tarif", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Catégorie de tarif"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("nom", "VARCHAR(200)", u"Nom de la catégorie"),
                                    ], # Catégories de tarifs

    "categories_tarifs_villes":[("IDville", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Ville"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID de la catégorie de tarif concernée"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("nom", "VARCHAR(100)", u"Nom de la ville"),
                                    ], # Villes rattachées aux catégories de tarifs

    "noms_tarifs":[           ("IDnom_tarif", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID nom tarif"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID categorie_tarif rattachée"),
                                    ("nom", "VARCHAR(200)", u"Nom du tarif"),
                                    ], # Noms des tarifs

    "tarifs":[                    ("IDtarif", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID tarif"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("type", "VARCHAR(50)", u"Type de tarif"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID categorie_tarif rattachée"),
                                    ("IDnom_tarif", "INTEGER", u"ID nom du tarif"),
                                    ("date_debut", "DATE", u"Date de début de validité"),
                                    ("date_fin", "DATE", u"Date de fin de validité"),  
                                    ("condition_nbre_combi", "INTEGER", u""),
                                    ("condition_periode", "VARCHAR(100)", u"Type de tarif (prédéfini ou automatique)"),
                                    ("condition_nbre_jours", "INTEGER", u""),
                                    ("condition_conso_facturees", "INTEGER", u""),
                                    ("condition_dates_continues", "INTEGER", u""),
                                    ("forfait_saisie_manuelle", "INTEGER", u"Saisie manuelle du forfait possible (0/1)"),
                                    ("forfait_saisie_auto", "INTEGER", u"Saisie automatique du forfait quand inscription (0/1)"),
                                    ("forfait_suppression_auto", "INTEGER", u"Suppression manuelle impossible (0/1)"),
                                    ("methode", "VARCHAR(50)", u"Code de la méthode de calcul"),
                                    ("categories_tarifs", "VARCHAR(300)", u"Catégories de tarifs rattachées à ce tarif"),
                                    ("groupes", "VARCHAR(300)", u"Groupes rattachés à ce tarif"),
                                    ("forfait_duree", "VARCHAR(50)", u"Durée du forfait"),
                                    ("forfait_beneficiaire", "VARCHAR(50)", u"Bénéficiaire du forfait (famille|individu)"),
                                    ("cotisations", "VARCHAR(300)", u"Cotisations rattachées à ce tarif"),
                                    ("caisses", "VARCHAR(300)", u"Caisses rattachées à ce tarif"),
                                    ("description", "VARCHAR(450)", u"Description du tarif"),
                                    ("jours_scolaires", "VARCHAR(100)", u"Jours scolaires"),
                                    ("jours_vacances", "VARCHAR(100)", u"Jours de vacances"),
                                    ("options", "VARCHAR(450)", u"Options diverses"),
                                    ("observations", "VARCHAR(450)", u"Observations sur le tarif"),
                                    ("tva", "FLOAT", u"Taux TVA"),
                                    ("code_compta", "VARCHAR(200)", u"Code comptable pour export vers logiciels de compta"),
                                    ("date_facturation", "VARCHAR(450)", u"Date de facturation de la prestation"),
                                    ("etiquettes", "VARCHAR(450)", u"Etiquettes rattachées à ce tarif"),
                                    ("etats", "VARCHAR(150)", u"Etats de consommations rattachés à ce tarif"),
                                    ("IDtype_quotient", "INTEGER", u"ID du type de quotient"),
                                    ("label_prestation", "VARCHAR(300)", u"Label de la prestation"),
                                    ("IDevenement", "INTEGER", u"ID de l'évènement associé"),
                                    ("IDproduit", "INTEGER", u"ID du produit associé"),
                                    ], # Tarifs

    "combi_tarifs":          [("IDcombi_tarif", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID combinaison de tarif"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("type", "VARCHAR(50)", u"Type de combinaison"),
                                    ("date", "DATE", u"Date si dans forfait"),
                                    ("quantite_max", "INTEGER", u"Quantité max d'unités"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe concerné"),
                                    ], # Combinaisons d'unités pour les tarifs

    "combi_tarifs_unites":[("IDcombi_tarif_unite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID combinaison de tarif"),
                                    ("IDcombi_tarif", "INTEGER", u"ID du combi_tarif"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("IDunite", "INTEGER", u"ID de l'unité"),
                                    ], # Combinaisons d'unités pour les tarifs

    "tarifs_lignes":          [("IDligne", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID ligne de tarif"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("code", "VARCHAR(50)", u"Code de la méthode"),
                                    ("num_ligne", "INTEGER", u"Numéro de ligne"),
                                    ("tranche", "VARCHAR(10)", u"Nom de tranche"),
                                    ("qf_min", "FLOAT", u"Montant QF min"),
                                    ("qf_max", "FLOAT", u"Montant QF max"),
                                    ("montant_unique", "FLOAT", u"Montant unique"),
                                    ("montant_enfant_1", "FLOAT", u"Montant pour 1 enfant"),
                                    ("montant_enfant_2", "FLOAT", u"Montant pour 2 enfants"),
                                    ("montant_enfant_3", "FLOAT", u"Montant pour 3 enfants"),
                                    ("montant_enfant_4", "FLOAT", u"Montant pour 4 enfants"),
                                    ("montant_enfant_5", "FLOAT", u"Montant pour 5 enfants"),
                                    ("montant_enfant_6", "FLOAT", u"Montant pour 6 enfants et plus"),
                                    ("nbre_enfants", "INTEGER", u"Nbre d'enfants pour le calcul par taux d'effort"),
                                    ("coefficient", "FLOAT", u"Coefficient"),
                                    ("montant_min", "FLOAT", u"Montant mini pour le calcul par taux d'effort"),
                                    ("montant_max", "FLOAT", u"Montant maxi pour le calcul par taux d'effort"),
                                    ("heure_debut_min", "DATE", u"Heure début min pour unités horaires"),  
                                    ("heure_debut_max", "DATE", u"Heure début max pour unités horaires"),  
                                    ("heure_fin_min", "DATE", u"Heure fin min pour unités horaires"),  
                                    ("heure_fin_max", "DATE", u"Heure fin max pour unités horaires"), 
                                    ("duree_min", "DATE", u"Durée min pour unités horaires"), 
                                    ("duree_max", "DATE", u"Durée min pour unités horaires"), 
                                    ("date", "DATE", u"Date conditionnelle"), 
                                    ("label", "VARCHAR(300)", u"Label personnalisé pour la prestation"), 
                                    ("temps_facture", "DATE", u"Temps facturé pour la CAF"), 
                                    ("unite_horaire", "DATE", u"Unité horaire pour base de calcul selon coefficient"), 
                                    ("duree_seuil", "DATE", u"Durée seuil"), 
                                    ("duree_plafond", "DATE", u"Durée plafond"), 
                                    ("taux", "FLOAT", u"Taux d'effort"), 
                                    ("ajustement", "FLOAT", u"Ajustement (majoration/déduction)"), 
                                    ("montant_questionnaire", "INTEGER", u"IDquestion de la table questionnaires"),
                                    ("revenu_min", "FLOAT", u"Montant revenu min"),
                                    ("revenu_max", "FLOAT", u"Montant revenu max"),
                                    ("IDmodele", "INTEGER", u"IDmodele de prestation"),
                                    ], # Lignes du tableau de calcul de tarifs
                                    
    "inscriptions":[           ("IDinscription", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID inscription"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID de la catégorie de tarif"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur par défaut"), 
                                    ("date_inscription", "DATE", u"Date de l'inscription"),
                                    ("parti", "INTEGER", u"(0/1) est parti"),
                                    ("date_desinscription", "DATE", u"Date de désinscription"),
                                    ("statut", "VARCHAR(100)", u"Statut de l'inscription"),
                                    ], # Inscriptions des individus à des activités

    "consommations":[    ("IDconso", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID consommation"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDinscription", "INTEGER", u"ID de l'inscription"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité"),
                                    ("date", "DATE", u"Date de la consommation"),
                                    ("IDunite", "INTEGER", u"ID de l'unité"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe"),
                                    ("heure_debut", "DATE", u"Heure min pour unités horaires"),  
                                    ("heure_fin", "DATE", u"Heure max pour unités horaires"),  
                                    ("etat", "VARCHAR(20)", u"Etat"),
                                    ("verrouillage", "INTEGER", u"1 si la consommation est verrouillée"),
                                    ("date_saisie", "DATE", u"Date de saisie de la consommation"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a fait la saisie"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID de la catégorie de tarif"), 
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("IDprestation", "INTEGER", u"ID de la prestation"),
                                    ("forfait", "INTEGER", u"Type de forfait : 0 : Aucun | 1 : Suppr possible | 2 : Suppr impossible"),
                                    ("quantite", "INTEGER", u"Quantité de consommations"),
                                    ("etiquettes", "VARCHAR(50)", u"Etiquettes"),
                                    ("IDevenement", "INTEGER", u"ID de l'évènement"),
                                    ("badgeage_debut", "DATETIME", u"Date et heure de badgeage du début"),
                                    ("badgeage_fin", "DATETIME", u"Date et heure de badgeage de fin"),
                                    ], # Consommations

    "memo_journee":[      ("IDmemo", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID memo"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("date", "DATE", u"Date"),
                                    ("texte", "VARCHAR(200)", u"Texte du mémo"),
                                    ], # Mémo journées

    "prestations":[           ("IDprestation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID prestation"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("date", "DATE", u"Date de la prestation"),
                                    ("categorie", "VARCHAR(50)", u"Catégorie de la prestation"),
                                    ("label", "VARCHAR(200)", u"Label de la prestation"),
                                    ("montant_initial", "FLOAT", u"Montant de la prestation AVANT déductions"),
                                    ("montant", "FLOAT", u"Montant de la prestation"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("IDfacture", "INTEGER", u"ID de la facture"),
                                    ("IDfamille", "INTEGER", u"ID de la famille concernée"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu concerné"),
                                    ("forfait", "INTEGER", u"Type de forfait : 0 : Aucun | 1 : Suppr possible | 2 : Suppr impossible"),
                                    ("temps_facture", "DATE", u"Temps facturé format 00:00"),  
                                    ("IDcategorie_tarif", "INTEGER", u"ID de la catégorie de tarif"),
                                    ("forfait_date_debut", "DATE", u"Date de début de forfait"),  
                                    ("forfait_date_fin", "DATE", u"Date de fin de forfait"),  
                                    ("reglement_frais", "INTEGER", u"ID du règlement"),
                                    ("tva", "FLOAT", u"Taux TVA"),
                                    ("code_compta", "VARCHAR(200)", u"Code comptable pour export vers logiciels de compta"),
                                    ("IDcontrat", "INTEGER", u"ID du contrat associé"),
                                    ("date_valeur", "DATE", u"Date de valeur comptable de la prestation"),
                                    ("IDdonnee", "INTEGER", u"ID d'une donnée associée"),
                                    ], # Prestations

    "comptes_payeurs":[  ("IDcompte_payeur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID compte_payeur"),
                                    ("IDfamille", "INTEGER", u"ID de la famille concernée"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu concerné"),
                                    ], # Comptes payeurs

    "modes_reglements":[("IDmode", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID mode de règlement"),
                                    ("label", "VARCHAR(100)", u"Label du mode"),
                                    ("image", "LONGBLOB", u"Image du mode"),
                                    ("numero_piece", "VARCHAR(10)", u"Numéro de pièce (None|ALPHA|NUM)"),
                                    ("nbre_chiffres", "INTEGER", u"Nbre de chiffres du numéro"),
                                    ("frais_gestion", "VARCHAR(10)", u"Frais de gestion None|LIBRE|FIXE|PRORATA"),
                                    ("frais_montant", "FLOAT", u"Montant fixe des frais"),
                                    ("frais_pourcentage", "FLOAT", u"Prorata des frais"),
                                    ("frais_arrondi", "VARCHAR(20)", u"Méthode d'arrondi"),
                                    ("frais_label", "VARCHAR(200)", u"Label de la prestation"),
                                    ("type_comptable", "VARCHAR(200)", u"Type comptable (banque ou caisse)"),
                                    ("code_compta", "VARCHAR(200)", u"Code comptable pour export vers logiciels de compta"),
                                    ], # Modes de règlements

    "emetteurs":[             ("IDemetteur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Emetteur"),
                                    ("IDmode", "INTEGER", u"ID du mode concerné"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'émetteur"),
                                    ("image", "LONGBLOB", u"Image de l'emetteur"),
                                    ], # Emetteurs pour les modes de règlements

    "payeurs":[                ("IDpayeur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Payeur"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur concerné"),
                                    ("nom", "VARCHAR(100)", u"Nom du payeur"),
                                    ], # Payeurs

    "comptes_bancaires":[("IDcompte", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Compte"),
                                    ("nom", "VARCHAR(100)", u"Intitulé du compte"),
                                    ("numero", "VARCHAR(50)", u"Numéro du compte"),
                                    ("defaut", "INTEGER", u"(0/1) Compte sélectionné par défaut"),
                                    ("raison", "VARCHAR(400)", u"Raison sociale"),
                                    ("code_etab", "VARCHAR(400)", u"Code établissement"),
                                    ("code_guichet", "VARCHAR(400)", u"Code guichet"),
                                    ("code_nne", "VARCHAR(400)", u"Code NNE pour prélèvements auto."),
                                    ("cle_rib", "VARCHAR(400)", u"Clé RIB pour prélèvements auto."),
                                    ("cle_iban", "VARCHAR(400)", u"Clé IBAN pour prélèvements auto."),
                                    ("iban", "VARCHAR(400)", u"Numéro IBAN pour prélèvements auto."),
                                    ("bic", "VARCHAR(400)", u"Numéro BIC pour prélèvements auto."),
                                    ("code_ics", "VARCHAR(400)", u"Code NNE pour prélèvements auto."),
                                    ], # Comptes bancaires de l'organisateur
                                    
    "reglements":[            ("IDreglement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Règlement"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("date", "DATE", u"Date d'émission du règlement"),
                                    ("IDmode", "INTEGER", u"ID du mode de règlement"),
                                    ("IDemetteur", "INTEGER", u"ID de l'émetteur du règlement"),
                                    ("numero_piece", "VARCHAR(30)", u"Numéro de pièce"),
                                    ("montant", "FLOAT", u"Montant du règlement"),
                                    ("IDpayeur", "INTEGER", u"ID du payeur"),
                                    ("observations", "VARCHAR(200)", u"Observations"),
                                    ("numero_quittancier", "VARCHAR(30)", u"Numéro de quittancier"),
                                    ("IDprestation_frais", "INTEGER", u"ID de la prestation de frais de gestion"),
                                    ("IDcompte", "INTEGER", u"ID du compte bancaire pour l'encaissement"),
                                    ("date_differe", "DATE", u"Date de l'encaissement différé"),
                                    ("encaissement_attente", "INTEGER", u"(0/1) Encaissement en attente"),
                                    ("IDdepot", "INTEGER", u"ID du dépôt"),
                                    ("date_saisie", "DATE", u"Date de saisie du règlement"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a fait la saisie"),
                                    ("IDprelevement", "INTEGER", u"ID du prélèvement"),
                                    ("avis_depot", "DATE", u"Date de l'envoi de l'avis de dépôt"),
                                    ("IDpiece", "INTEGER", u"IDpiece pour PES V2 ORMC"),
                                    ], # Règlements

    "ventilation":[             ("IDventilation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Ventilation"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("IDreglement", "INTEGER", u"ID du règlement"),
                                    ("IDprestation", "INTEGER", u"ID de la prestation"),
                                    ("montant", "FLOAT", u"Montant de la ventilation"),
                                    ], # Ventilation

    "depots":[                  ("IDdepot", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Dépôt"),
                                    ("date", "DATE", u"Date du dépôt"),
                                    ("nom", "VARCHAR(200)", u"Nom du dépôt"),
                                    ("verrouillage", "INTEGER", u"(0/1) Verrouillage du dépôt"),
                                    ("IDcompte", "INTEGER", u"ID du compte d'encaissement"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("code_compta", "VARCHAR(200)", u"Code comptable pour export vers logiciels de compta"),
                                    ], # Dépôts

    "quotients":[              ("IDquotient", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Quotient familial"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("date_debut", "DATE", u"Date de début de validité"),
                                    ("date_fin", "DATE", u"Date de fin de validité"),
                                    ("quotient", "INTEGER", u"Quotient familial"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("revenu", "FLOAT", u"Montant du revenu"),
                                    ("IDtype_quotient", "INTEGER", u"Type de quotient"),
                                    ], # Quotients familiaux

    "caisses":[                ("IDcaisse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Caisse"),
                                    ("nom", "VARCHAR(255)", u"Nom de la caisse"),
                                    ("IDregime", "INTEGER", u"Régime social affilié"),
                                    ], # Caisses d'allocations

    "regimes":[                ("IDregime", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Régime"),
                                    ("nom", "VARCHAR(255)", u"Nom du régime social"),
                                    ], # Régimes sociaux

    "aides":[                    ("IDaide", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Aide"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'aide"),
                                    ("date_debut", "DATE", u"Date de début de validité"),
                                    ("date_fin", "DATE", u"Date de fin de validité"),
                                    ("IDcaisse", "INTEGER", u"ID de la caisse"),
                                    ("montant_max", "FLOAT", u"Montant maximal de l'aide"),
                                    ("nbre_dates_max", "INTEGER", u"Nbre maximal de dates"),
                                    ("jours_scolaires", "VARCHAR(50)", u"Jours scolaires"),
                                    ("jours_vacances", "VARCHAR(50)", u"Jours de vacances"),
                                    ], # Aides journalières

    "aides_beneficiaires":[("IDaide_beneficiaire", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID bénéficiaire"),
                                    ("IDaide", "INTEGER", u"ID de l'aide"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ], # Bénéficiaires des aides journalières

    "aides_montants":[    ("IDaide_montant", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Aide montant"),
                                    ("IDaide", "INTEGER", u"ID de l'aide"),
                                    ("montant", "FLOAT", u"Montant"),
                                    ], # Montants des aides journalières

    "aides_combinaisons":[("IDaide_combi", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Combinaison"),
                                    ("IDaide", "INTEGER", u"ID de l'aide"),
                                    ("IDaide_montant", "INTEGER", u"ID de l'aide"),
                                    ], # Combinaisons d'unités pour les aides journalières

    "aides_combi_unites":[("IDaide_combi_unite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID unité pour Combinaison"),
                                    ("IDaide", "INTEGER", u"ID de l'aide"),
                                    ("IDaide_combi", "INTEGER", u"ID de la combinaison"),
                                    ("IDunite", "INTEGER", u"ID de l'unité"),
                                    ], # Unités des combinaisons pour les aides journalières

    "deductions":[           ("IDdeduction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID déduction"),
                                    ("IDprestation", "INTEGER", u"ID de la prestation"),
                                    ("IDcompte_payeur", "INTEGER", u"IDcompte_payeur"),
                                    ("date", "DATE", u"Date de la déduction"),
                                    ("montant", "FLOAT", u"Montant"),
                                    ("label", "VARCHAR(200)", u"Label de la déduction"),
                                    ("IDaide", "INTEGER", u"ID de l'aide"),
                                    ], # Déductions pour les prestations

    "types_cotisations":[  ("IDtype_cotisation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type cotisation"),
                                    ("nom", "VARCHAR(200)", u"Nom de la cotisation"),
                                    ("type", "VARCHAR(50)", u"Type de cotisation (individu/famille)"),
                                    ("carte", "INTEGER", u"(0/1) Est une carte d'adhérent"),
                                    ("defaut", "INTEGER", u"(0/1) Cotisation sélectionnée par défaut"),
                                    ("code_comptable", "VARCHAR(450)", u"Code comptable pour facturation et export logiciels compta"),
                                    ], # Types de cotisations

    "unites_cotisations":[ ("IDunite_cotisation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID unité cotisation"),
                                    ("IDtype_cotisation", "INTEGER", u"ID du type de cotisation"),
                                    ("date_debut", "DATE", u"Date de début de validité"),
                                    ("date_fin", "DATE", u"Date de fin de validité"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'unité de cotisation"),
                                    ("montant", "FLOAT", u"Montant"),
                                    ("label_prestation", "VARCHAR(200)", u"Label de la prestation"),
                                    ("defaut", "INTEGER", u"(0/1) Unité sélectionnée par défaut"),
                                    ("duree", "VARCHAR(100)", u"Durée de validité"),
                                    ], # Unités de cotisation

    "cotisations":[            ("IDcotisation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID cotisation"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDtype_cotisation", "INTEGER", u"ID du type de cotisation"),
                                    ("IDunite_cotisation", "INTEGER", u"ID de l'unité de cotisation"),
                                    ("date_saisie", "DATE", u"Date de saisie"),
                                    ("IDutilisateur", "INTEGER", u"ID de l'utilisateur"),
                                    ("date_creation_carte", "DATE", u"Date de création de la carte"),
                                    ("numero", "VARCHAR(50)", u"Numéro d'adhérent"),
                                    ("IDdepot_cotisation", "INTEGER", u"ID du dépôt des cotisations"),
                                    ("date_debut", "DATE", u"Date de début de validité"),
                                    ("date_fin", "DATE", u"Date de fin de validité"),
                                    ("IDprestation", "INTEGER", u"ID de la prestation associée"),
                                    ("observations", "VARCHAR(1000)", u"Observations"),
                                    ("activites", "VARCHAR(450)", u"Liste d'activités associées"),
                                    ], # Cotisations

    "depots_cotisations":[("IDdepot_cotisation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Dépôt Cotisation"),
                                    ("date", "DATE", u"Date du dépôt"),
                                    ("nom", "VARCHAR(200)", u"Nom du dépôt"),
                                    ("verrouillage", "INTEGER", u"(0/1) Verrouillage du dépôt"),
                                    ("observations", "VARCHAR(1000)", u"Observations"),
                                    ], # Dépôts de cotisations

    "parametres":[           ("IDparametre", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID parametre"),
                                    ("categorie", "VARCHAR(200)", u"Catégorie"),
                                    ("nom", "VARCHAR(200)", u"Nom"),
                                    ("parametre", "VARCHAR(30000)", u"Parametre"),
                                    ], # Paramètres

    "types_groupes_activites":[("IDtype_groupe_activite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type groupe activité"),
                                    ("nom", "VARCHAR(255)", u"Nom"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ], # Types de groupes d'activités

    "groupes_activites":[  ("IDgroupe_activite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type groupe activité"),
                                    ("IDtype_groupe_activite", "INTEGER", u"ID du groupe d'activité"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité concernée"),
                                    ], # Groupes d'activités

    "secteurs":[               ("IDsecteur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID secteur géographique"),
                                    ("nom", "VARCHAR(255)", u"Nom du secteur géographique"),
                                    ], # Secteurs géographiques

    "types_sieste":[         ("IDtype_sieste", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type sieste"),
                                    ("nom", "VARCHAR(255)", u"Nom du type de sieste"),
                                    ], # Types de sieste

    "factures_messages":[("IDmessage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmessage"),
                                    ("titre", "VARCHAR(255)", u"Titre du message"),
                                    ("texte", "VARCHAR(1000)", u"Contenu du message"),
                                    ], # Messages dans les factures

    "factures":[                ("IDfacture", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDfacture"),
                                    ("numero", "BIGINT", u"Numéro de facture"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("date_edition", "DATE", u"Date d'édition de la facture"),
                                    ("date_echeance", "DATE", u"Date d'échéance de la facture"),
                                    ("activites", "VARCHAR(500)", u"Liste des IDactivité séparées par ;"),
                                    ("individus", "VARCHAR(500)", u"Liste des IDindividus séparées par ;"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a créé la facture"),
                                    ("date_debut", "DATE", u"Date de début de période"),
                                    ("date_fin", "DATE", u"Date de fin de période"),
                                    ("total", "FLOAT", u"Montant total de la période"),
                                    ("regle", "FLOAT", u"Montant réglé pour la période"),
                                    ("solde", "FLOAT", u"Solde à régler pour la période"),
                                    ("IDlot", "INTEGER", u"ID du lot de factures"),
                                    ("prestations", "VARCHAR(500)", u"Liste des types de prestations intégrées"),
                                    ("etat", "VARCHAR(100)", u"Etat de la facture"),
                                    ("IDprefixe", "INTEGER", u"ID du préfixe"),
                                    ("IDregie", "INTEGER", u"ID de la régie"),
                                    ], # Factures éditées

    "textes_rappels":[      ("IDtexte", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDtexte"),
                                    ("label", "VARCHAR(255)", u"Label du texte"),
                                    ("couleur", "VARCHAR(50)", u"Couleur"),
                                    ("retard_min", "INTEGER", u"Minimum retard"),
                                    ("retard_max", "INTEGER", u"Maximum retard"),
                                    ("titre", "VARCHAR(255)", u"Titre du rappel"),
                                    ("texte_xml", "VARCHAR(5000)", u"Contenu du texte version XML"),
                                    ("texte_pdf", "VARCHAR(5000)", u"Contenu du texte version PDF"),
                                    ], # Textes pour les lettres de rappel

    "rappels":[                 ("IDrappel", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDrappel"),
                                    ("numero", "INTEGER", u"Numéro du rappel"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("date_edition", "DATE", u"Date d'édition du rappel"),
                                    ("activites", "VARCHAR(500)", u"Liste des IDactivité séparées par ;"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a créé le rappel"),
                                    ("IDtexte", "INTEGER", u"ID du texte de rappel"),
                                    ("date_reference", "DATE", u"Date de référence"),
                                    ("solde", "FLOAT", u"Solde à régler"),
                                    ("date_min", "DATE", u"Date min"),
                                    ("date_max", "DATE", u"Date max"),
                                    ("IDlot", "INTEGER", u"ID du lot de rappels"),
                                    ("prestations", "VARCHAR(500)", u"Liste des types de prestations intégrées"),
                                    ], # Rappels édités

    "utilisateurs":[            ("IDutilisateur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDutilisateur"),
                                    ("sexe", "VARCHAR(5)", u"Sexe de l'utilisateur"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'utilisateur"),
                                    ("prenom", "VARCHAR(200)", u"Prénom de l'utilisateur"),
                                    ("mdp", "VARCHAR(100)", u"Mot de passe"),
                                    ("profil", "VARCHAR(100)", u"Profil (Administrateur ou utilisateur)"),
                                    ("actif", "INTEGER", u"Utilisateur actif"),
                                    ("image", "VARCHAR(200)", u"Images"),
                                    ("mdpcrypt", "VARCHAR(200)", u"Mot de passe crypté"),
                                    ("internet_actif", "INTEGER", u"(0/1) Compte internet actif"),
                                    ("internet_identifiant", "VARCHAR(300)", u"Code identifiant internet"),
                                    ("internet_mdp", "VARCHAR(300)", u"Mot de passe internet"),
                                    ], # Utilisateurs

    "messages":[            ("IDmessage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmessage"),
                                    ("type", "VARCHAR(30)", u"Type (instantané ou programmé)"),
                                    ("IDcategorie", "INTEGER", u"ID de la catégorie"),
                                    ("date_saisie", "DATE", u"Date de saisie"),
                                    ("IDutilisateur", "INTEGER", u"ID de l'utilisateur"),
                                    ("date_parution", "DATE", u"Date de parution"),
                                    ("priorite", "VARCHAR(30)", u"Priorité"),
                                    ("afficher_accueil", "INTEGER", u"Afficher sur la page d'accueil"),
                                    ("afficher_liste", "INTEGER", u"Afficher sur la liste des conso"),
                                    ("afficher_commande", "INTEGER", u"Afficher sur la commande des repas"),
                                    ("rappel", "INTEGER", u"Rappel à l'ouverture du fichier"),
                                    ("IDfamille", "INTEGER", u"IDfamille"),
                                    ("IDindividu", "INTEGER", u"IDindividu"),
                                    ("nom", "VARCHAR(255)", u"Nom de la famille ou de l'individu"),
                                    ("texte", "VARCHAR(500)", u"Texte du message"),
                                    ("afficher_facture", "INTEGER", u"Afficher sur les factures de la famille"),
                                    ("rappel_famille", "INTEGER", u"Rappel à l'ouverture de la fiche famille"),
                                    ], # Messages

    "messages_categories":[("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDcategorie"),
                                    ("nom", "VARCHAR(255)", u"Nom de la catégorie"),
                                    ("priorite", "VARCHAR(30)", u"Priorité"),
                                    ("afficher_accueil", "INTEGER", u"Afficher sur la page d'accueil"),
                                    ("afficher_liste", "INTEGER", u"Afficher sur la liste des conso"),
                                    ], # Catégories de messages

    "historique":[              ("IDaction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID de l'action"),
                                    ("date", "DATE", u"Date de l'action"),
                                    ("heure", "DATE", u"Heure de l'action"),
                                    ("IDutilisateur", "INTEGER", u"ID de l'utilisateur"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDcategorie", "INTEGER", u"ID de la catégorie d'action"),
                                    ("action", "VARCHAR(500)", u"Action"),
                                    ], # Historique

    "attestations":[           ("IDattestation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDattestation"),
                                    ("numero", "INTEGER", u"Numéro d'attestation"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("date_edition", "DATE", u"Date d'édition de l'attestation"),
                                    ("activites", "VARCHAR(450)", u"Liste des IDactivité séparées par ;"),
                                    ("individus", "VARCHAR(450)", u"Liste des IDindividus séparées par ;"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a créé l'attestation"),
                                    ("date_debut", "DATE", u"Date de début de période"),
                                    ("date_fin", "DATE", u"Date de fin de période"),
                                    ("total", "FLOAT", u"Montant total de la période"),
                                    ("regle", "FLOAT", u"Montant réglé pour la période"),
                                    ("solde", "FLOAT", u"Solde à régler pour la période"),
                                    ], # Attestation de présence éditées

    "recus":[                   ("IDrecu", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDrecu"),
                                    ("numero", "INTEGER", u"Numéro du recu"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("date_edition", "DATE", u"Date d'édition du recu"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a créé l'attestation"),
                                    ("IDreglement", "INTEGER", u"ID du règlement"),
                                    ], # Recus de règlements

    "adresses_mail":  [    ("IDadresse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("adresse", "VARCHAR(200)", u"Adresse de messagerie"),
                                    ("nom_adresse", "VARCHAR(200)", u"Nom d'affichage de l'adresse de messagerie"),
                                    ("motdepasse", "VARCHAR(200)", u"Mot de passe si SSL"),
                                    ("smtp", "VARCHAR(200)", u"Adresse SMTP"),
                                    ("port", "INTEGER", u"Numéro du port"),
                                    ("connexionssl", "INTEGER", u"Connexion ssl (1/0) - N'est plus utilisé !"),
                                    ("defaut", "INTEGER", u"Adresse utilisée par défaut (1/0)"),
                                    ("connexionAuthentifiee", "INTEGER", u"Authentification activée (1/0)"),
                                    ("startTLS", "INTEGER", u"startTLS activé (1/0)"),
                                    ("utilisateur", "VARCHAR(200)", u"Nom d'utilisateur"),
                                    ("moteur", "VARCHAR(200)", u"Moteur d'envoi"),
                                    ("parametres", "VARCHAR(1000)", u"Autres paramètres"),
                                    ], # Adresses d'expéditeur de mail

    "listes_diffusion":  [    ("IDliste", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("nom", "VARCHAR(200)", u"Nom de la liste de diffusion"),
                                    ], # Listes de diffusion

    "abonnements":    [    ("IDabonnement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDliste", "INTEGER", u"ID de la liste de diffusion"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu abonné"),
                                    ], # Abonnements aux listes de diffusion

    "documents_modeles":[("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("nom", "VARCHAR(200)", u"Nom du modèle"),
                                    ("categorie", "VARCHAR(200)", u"Catégorie du modèle (ex : facture)"),
                                    ("supprimable", "INTEGER", u"Est supprimable (1/0)"),
                                    ("largeur", "INTEGER", u"Largeur en mm"),
                                    ("hauteur", "INTEGER", u"Hauteur en mm"),
                                    ("observations", "VARCHAR(400)", u"Observations"),
                                    ("IDfond", "INTEGER", u"IDfond du modèle"),
                                    ("defaut", "INTEGER", u"Modèle utilisé par défaut (1/0)"),
                                    ("IDdonnee", "INTEGER", u"Donnée associée au document"),
                                    ], # Modèles de documents

    "documents_objets":[ ("IDobjet", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDmodele", "INTEGER", u"ID du modèle rattaché"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'objet"),
                                    ("categorie", "VARCHAR(200)", u"Catégorie d'objet (ex : rectangle)"),
                                    ("champ", "VARCHAR(200)", u"Champ"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("obligatoire", "INTEGER", u"Est obligatoire (0/1)"),
                                    ("nbreMax", "INTEGER", u"Nbre max d'objets dans le document"),
                                    ("texte", "VARCHAR(600)", u"Texte"),
                                    ("points", "VARCHAR(600)", u"Points de lignes ou de polygones"),
                                    ("image", "LONGBLOB", u"Image"),
                                    ("typeImage", "VARCHAR(100)", u"Type de l'image (logo, fichier)"),
                                    ("x", "INTEGER", u"Position x"),
                                    ("y", "INTEGER", u"Position y"),
                                    ("verrouillageX", "INTEGER", u"Verrouillage X (0/1)"),
                                    ("verrouillageY", "INTEGER", u"Verrouillage Y (0/1)"),
                                    ("Xmodifiable", "INTEGER", u"Position X est modifiable (0/1)"),
                                    ("Ymodifiable", "INTEGER", u"Position Y est modifiable (0/1)"),
                                    ("largeur", "INTEGER", u"Largeur de l'objet"),
                                    ("hauteur", "INTEGER", u"Hauteur de l'objet"),
                                    ("largeurModifiable", "INTEGER", u"Largeur modifiable (0/1)"),
                                    ("hauteurModifiable", "INTEGER", u"Hauteur modifiable (0/1)"),
                                    ("largeurMin", "INTEGER", u"Largeur min"),
                                    ("largeurMax", "INTEGER", u"Largeur max"),
                                    ("hauteurMin", "INTEGER", u"Hauteur min"),
                                    ("hauteurMax", "INTEGER", u"Hauteur max"),
                                    ("verrouillageLargeur", "INTEGER", u"Hauteur verrouillée (0/1)"),
                                    ("verrouillageHauteur", "INTEGER", u"Hauteur verrouillée (0/1)"),
                                    ("verrouillageProportions", "INTEGER", u"Proportion verrouillée (0/1)"),
                                    ("interditModifProportions", "INTEGER", u"Modification proportions interdite (0/1)"),
                                    ("couleurTrait", "VARCHAR(100)", u"Couleur du trait"),
                                    ("styleTrait", "VARCHAR(100)", u"Style du trait"),
                                    ("epaissTrait", "FLOAT", u"Epaisseur du trait"),
                                    ("coulRemplis", "VARCHAR(100)", u"Couleur du remplissage"),
                                    ("styleRemplis", "VARCHAR(100)", u"Style du remplissage"),
                                    ("couleurTexte", "VARCHAR(100)", u"Couleur du texte"),
                                    ("couleurFond", "VARCHAR(100)", u"Couleur du fond"),
                                    ("padding", "FLOAT", u"Padding du texte"),
                                    ("interligne", "FLOAT", u"Interligne"),
                                    ("taillePolice", "INTEGER", u"Taille de la police"),
                                    ("nomPolice", "VARCHAR(100)", u"Nom de la police"),
                                    ("familyPolice", "INTEGER", u"Famille de la police"),
                                    ("stylePolice", "INTEGER", u"Style de la police"),
                                    ("weightPolice", "INTEGER", u"weight de la police"),
                                    ("soulignePolice", "INTEGER", u"Texte souligné (0/1)"),
                                    ("alignement", "VARCHAR(100)", u"Alignement du texte"),
                                    ("largeurTexte", "INTEGER", u"Largeur du bloc de texte"),
                                    ("norme", "VARCHAR(100)", u"Norme code-barres"),
                                    ("afficheNumero", "INTEGER", u"Affiche numéro code-barres"),
                                    ("IDdonnee", "INTEGER", u"Donnée associée pour zone interactive"),
                                    ], # Objets des modèles de documents

    "questionnaire_categories": [("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("type", "VARCHAR(100)", u"Individu ou Famille"),
                                    ("couleur", "VARCHAR(100)", u"Couleur de la catégorie"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ], # Catégories des questionnaires

    "questionnaire_questions": [("IDquestion", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDcategorie", "INTEGER", u"ID de la catégorie"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ("controle", "VARCHAR(200)", u"Nom du contrôle"),
                                    ("defaut", "VARCHAR(400)", u"Valeur par défaut"),
                                    ("options", "VARCHAR(400)", u"Options de la question"),
                                    ], # Questions des questionnaires

    "questionnaire_choix": [("IDchoix", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDquestion", "INTEGER", u"ID de la question rattachée"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ], # Choix de réponses des questionnaires

    "questionnaire_reponses": [("IDreponse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDquestion", "INTEGER", u"ID de la question rattachée"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu rattaché"),
                                    ("IDfamille", "INTEGER", u"ID de la famille rattachée"),
                                    ("reponse", "VARCHAR(400)", u"Réponse"),
                                    ("type", "VARCHAR(100)", u"Type : Individu ou Famille, etc..."),
                                    ("IDdonnee", "INTEGER", u"ID de la donnée rattachée (IDindividu, IDfamille, etc...)"),
                                    ], # Réponses des questionnaires

    "questionnaire_filtres": [("IDfiltre", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDquestion", "INTEGER", u"ID de la question rattachée"),
                                    ("categorie", "VARCHAR(100)", u"Catégorie (ex: 'TARIF')"),
                                    ("choix", "VARCHAR(400)", u"Choix (ex : 'EGAL'"),
                                    ("criteres", "VARCHAR(600)", u"Criteres (ex : '4;5')"),
                                    ("IDtarif", "INTEGER", u"IDtarif rattaché"),
                                    ("IDdonnee", "INTEGER", u"ID de la donnée rattachée)"),
                                    ], # Filtres des questionnaires

    "niveaux_scolaires":  [("IDniveau", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("nom", "VARCHAR(400)", u"Nom du niveau (ex : Cours préparatoire)"),
                                    ("abrege", "VARCHAR(200)", u"Abrégé du niveau (ex : CP)"),
                                    ], # Niveaux scolaires

    "ecoles":[                  ("IDecole", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Ecole"),
                                    ("nom", "VARCHAR(300)", u"Nom du restaurateur"),
                                    ("rue", "VARCHAR(200)", u"Adresse"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(200)", u"Ville"),  
                                    ("tel", "VARCHAR(50)", u"Tel"),  
                                    ("fax", "VARCHAR(50)", u"Fax"),  
                                    ("mail", "VARCHAR(100)", u"Email"),  
                                    ("secteurs", "VARCHAR(200)", u"Liste des IDsecteur"),  
                                    ], # Ecoles

    "classes":[                ("IDclasse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Classe"),
                                    ("IDecole", "INTEGER", u"ID de l'école"),
                                    ("nom", "VARCHAR(400)", u"Nom de la classe"),
                                    ("date_debut", "DATE", u"Date de début de période"),
                                    ("date_fin", "DATE", u"Date de fin de période"),
                                    ("niveaux", "VARCHAR(300)", u"Liste des niveaux scolaires de la classe"),  
                                    ], # Classes

    "scolarite":[               ("IDscolarite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Scolarite"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("date_debut", "DATE", u"Date de début de scolarité"),
                                    ("date_fin", "DATE", u"Date de fin de scolarité"),
                                    ("IDecole", "INTEGER", u"ID de l'école"),
                                    ("IDclasse", "INTEGER", u"ID de la classe"),
                                    ("IDniveau", "INTEGER", u"ID du niveau scolaire"),
                                    ], # Scolarité

    "transports_compagnies":[("IDcompagnie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Compagnie"),
                                    ("categorie", "VARCHAR(200)", u"Catégorie de la compagnie (taxi,train,avion,etc...)"),
                                    ("nom", "VARCHAR(300)", u"Nom de la compagnie"),
                                    ("rue", "VARCHAR(200)", u"Rue"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(200)", u"Ville"),  
                                    ("tel", "VARCHAR(50)", u"Tél"),  
                                    ("fax", "VARCHAR(50)", u"Fax"),  
                                    ("mail", "VARCHAR(100)", u"Email"),  
                                    ], # Compagnies de transport

    "transports_lieux":[    ("IDlieu", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Lieu"),
                                    ("categorie", "VARCHAR(200)", u"Catégorie du lieu (gare,aeroport,port,station)"),
                                    ("nom", "VARCHAR(300)", u"Nom du lieu"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(200)", u"Ville"),  
                                    ], # Lieux pour les transports

    "transports_lignes":[   ("IDligne", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Ligne"),
                                    ("categorie", "VARCHAR(200)", u"Catégorie de la ligne (bus, car, métro, etc...)"),
                                    ("nom", "VARCHAR(300)", u"Nom de la ligne"),
                                    ], # Lignes régulières pour les transports

    "transports_arrets":[   ("IDarret", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Arrêt"),
                                    ("IDligne", "INTEGER", u"ID de la ligne"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("nom", "VARCHAR(300)", u"Nom de l'arrêt"),
                                    ], # Arrêts des lignes régulières pour les transports

    "transports":[            ("IDtransport", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Transport"),
                                    ("IDindividu", "INTEGER", u"ID Individu"),
                                    ("mode", "VARCHAR(100)", u"Mode : TRANSP | PROG | MODELE"),
                                    ("categorie", "VARCHAR(100)", u"Catégorie du moyen de locomotion"),
                                    ("IDcompagnie", "INTEGER", u"ID Compagnie"),
                                    ("IDligne", "INTEGER", u"ID Ligne"),
                                    ("numero", "VARCHAR(200)", u"Numéro du vol ou du train"),
                                    ("details", "VARCHAR(300)", u"Détails"),
                                    ("observations", "VARCHAR(400)", u"Observations"),
                                    ("depart_date", "DATE", u"Date du départ"),
                                    ("depart_heure", "DATE", u"Heure du départ"),
                                    ("depart_IDarret", "INTEGER", u"ID Arrêt du départ"),
                                    ("depart_IDlieu", "INTEGER", u"ID Lieu du départ"),
                                    ("depart_localisation", "VARCHAR(400)", u"Localisation du départ"),
                                    ("arrivee_date", "DATE", u"Date de l'arrivée"),
                                    ("arrivee_heure", "DATE", u"Heure de l'arrivée"),
                                    ("arrivee_IDarret", "INTEGER", u"ID Arrêt de l'arrivée"),
                                    ("arrivee_IDlieu", "INTEGER", u"ID Lieu de l'arrivée"),
                                    ("arrivee_localisation", "VARCHAR(400)", u"Localisation de l'arrivée"),
                                    ("date_debut", "DATE", u"Date de début"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ("actif", "INTEGER", u"Actif (1/0)"),
                                    ("jours_scolaires", "VARCHAR(100)", u"Jours scolaires"),
                                    ("jours_vacances", "VARCHAR(100)", u"Jours de vacances"),
                                    ("unites", "VARCHAR(480)", u"Liste des unités de conso rattachées"),
                                    ("prog", "INTEGER", u"IDtransport du modèle de programmation"),
                                    ], # Transports

    "etat_nomin_champs":[("IDchamp", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Champ"),
                                    ("code", "VARCHAR(300)", u"Code du champ"),
                                    ("label", "VARCHAR(400)", u"Nom du champ"),
                                    ("formule", "VARCHAR(450)", u"Formule"),
                                    ("titre", "VARCHAR(400)", u"Titre"),
                                    ], # Champs personnalisés pour Etat Caisse nominatif

    "etat_nomin_selections":[("IDselection", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Sélection"),
                                    ("IDprofil", "VARCHAR(400)", u"Nom de profil"),
                                    ("code", "VARCHAR(300)", u"Code du champ"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ], # Sélection des Champs personnalisés pour Etat Nominatif

    "etat_nomin_profils":[("IDprofil", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Profil"),
                                    ("label", "VARCHAR(400)", u"Nom de profil"),
                                    ], # Profils pour Etat Caisse nominatif

    "badgeage_actions":   [("IDaction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Action"),
                                    ("IDprocedure", "INTEGER", u"IDprocedure"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("condition_activite", "VARCHAR(400)", u"Activité"),
                                    ("condition_heure", "VARCHAR(400)", u"Heure"),
                                    ("condition_periode", "VARCHAR(400)", u"Période"),
                                    ("condition_poste", "VARCHAR(400)", u"Poste réseau"),
                                    ("condition_questionnaire", "VARCHAR(490)", u"Questionnaire"),
                                    ("action", "VARCHAR(400)", u"Code de l'action"),
                                    ("action_activite", "VARCHAR(450)", u"Activité"),
                                    ("action_unite", "VARCHAR(450)", u"Unités"),
                                    ("action_etat", "VARCHAR(400)", u"Etat de la conso"),
                                    ("action_demande", "VARCHAR(40)", u"Demande si début ou fin"),
                                    ("action_heure_debut", "VARCHAR(450)", u"Heure de début"),
                                    ("action_heure_fin", "VARCHAR(450)", u"Heure de fin"),
                                    ("action_message", "VARCHAR(450)", u"Message unique"),
                                    ("action_icone", "VARCHAR(400)", u"Icone pour boite de dialogue"),
                                    ("action_duree", "VARCHAR(50)", u"Durée d'affichage du message"),
                                    ("action_frequence", "VARCHAR(450)", u"Frequence diffusion message"),
                                    ("action_vocal", "VARCHAR(400)", u"Synthese vocale activation"),
                                    ("action_question", "VARCHAR(450)", u"Question"),
                                    ("action_date", "VARCHAR(450)", u"Date à proposer"),
                                    ("action_attente", "VARCHAR(450)", u"Proposer attente"),
                                    ("action_ticket", "VARCHAR(450)", u"Impression_ticket"),
                                    ], # Badgeage : Actions

    "badgeage_messages":[("IDmessage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Message"),
                                    ("IDprocedure", "INTEGER", u"IDprocedure"),
                                    ("IDaction", "INTEGER", u"IDaction rattachée"),
                                    ("message", "VARCHAR(480)", u"Texte du message"),
                                    ], # Badgeage : Messages pour Actions

    "badgeage_procedures":[("IDprocedure", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Procédure"),
                                    ("nom", "VARCHAR(450)", u"Nom"),
                                    ("defaut", "INTEGER", u"Défaut (0/1)"),
                                    ("style", "VARCHAR(400)", u"Style interface"),
                                    ("theme", "VARCHAR(400)", u"Thème interface"),
                                    ("image", "VARCHAR(400)", u"Image personnalisée pour thème"),
                                    ("systeme", "VARCHAR(400)", u"Système de saisie"),
                                    ("activites", "VARCHAR(400)", u"Liste ID activites pour saisie par liste d'individus"),
                                    ("confirmation", "INTEGER", u"Confirmation identification (0/1)"),
                                    ("vocal", "INTEGER", u"Activation synthèse vocale (0/1)"),
                                    ("tutoiement", "INTEGER", u"Activation du tutoiement dans les messages (0/1)"),
                                    ], #  Badgeage : Procédures

    "badgeage_journal":[ ("IDaction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Action"),
                                    ("date", "DATE", u"Date de l'action"),
                                    ("heure", "VARCHAR(50)", u"Heure"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("individu", "VARCHAR(450)", u"Nom de l'individu"),
                                    ("action", "VARCHAR(450)", u"Action réalisée"),
                                    ("resultat", "VARCHAR(450)", u"Résultat de l'action"),
                                    ], #  Badgeage : Journal

    "badgeage_archives":[ ("IDarchive", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Archive"),
                                    ("date_archivage", "DATE", u"Date de l'archivage"),
                                    ("codebarres", "VARCHAR(200)", u"Code-barres"),
                                    ("date", "DATE", u"Date badgée"),
                                    ("heure", "VARCHAR(50)", u"Heure badgée"),
                                    ], #  Badgeage : Archives des importations

    "corrections_phoniques":[("IDcorrection", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Correction"),
                                    ("mot", "VARCHAR(400)", u"Mot à corriger"),
                                    ("correction", "VARCHAR(400)", u"Correction phonique"),
                                    ], # Corrections phoniques pour la synthèse vocale

    "corrections_villes":[("IDcorrection", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Correction"),
                                    ("mode", "VARCHAR(100)", u"Mode de correction"),
                                    ("IDville", "INTEGER", u"ID ville"),
                                    ("nom", "VARCHAR(450)", u"Nom de la ville"),
                                    ("cp", "VARCHAR(100)", u"Code postal"),
                                    ], # Personnalisation des villes et codes postaux

    "modeles_emails":[ ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmodele"),
                                    ("categorie", "VARCHAR(455)", u"Catégorie du modèle"),
                                    ("nom", "VARCHAR(455)", u"Nom du modèle"),
                                    ("description", "VARCHAR(455)", u"Description du modèle"),
                                    ("objet", "VARCHAR(455)", u"Texte objet du mail"),
                                    ("texte_xml", "VARCHAR(50000)", u"Contenu du texte version XML"),
                                    ("IDadresse", "INTEGER", u"IDadresse d'expédition de mails"),
                                    ("defaut", "INTEGER", u"Modèle par défaut (0/1)"),
                                    ], # Modèles d'Emails

    "banques":[                ("IDbanque", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID de la banque"),
                                    ("nom", "VARCHAR(100)", u"Nom de la banque"),
                                    ("rue_resid", "VARCHAR(255)", u"Adresse de la banque"),
                                    ("cp_resid", "VARCHAR(10)", u"Code postal de la banque"),
                                    ("ville_resid", "VARCHAR(100)", u"Ville de la banque"),  
                                    ], # Les établissements bancaires pour le prélèvement automatique

    "lots_factures":[         ("IDlot", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID lot de factures"),
                                    ("nom", "VARCHAR(400)", u"Nom du lot"),
                                    ], # Lots de factures

    "lots_rappels":[         ("IDlot", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID lot de rappels"),
                                    ("nom", "VARCHAR(400)", u"Nom du lot"),
                                    ], # Lots de rappels

    "prelevements":[         ("IDprelevement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID prélèvement"),
                                    ("IDlot", "INTEGER", u"ID du lot de prélèvements"),
                                    ("IDfamille", "INTEGER", u"ID de la famille destinataire"),
                                    ("prelevement_etab", "VARCHAR(50)", u"Prélèvement - Code étab"),
                                    ("prelevement_guichet", "VARCHAR(50)", u"Prélèvement - Code guichet"),
                                    ("prelevement_numero", "VARCHAR(50)", u"Prélèvement - Numéro de compte"),
                                    ("prelevement_banque", "INTEGER", u"Prélèvement - ID de la Banque"),
                                    ("prelevement_cle", "VARCHAR(50)", u"Prélèvement - Code clé"),
                                    ("prelevement_iban", "VARCHAR(100)", u"Prélèvement - Clé IBAN"),
                                    ("prelevement_bic", "VARCHAR(100)", u"Prélèvement - BIC"),
                                    ("prelevement_reference_mandat", "VARCHAR(300)", u"Prélèvement - Référence mandat"),
                                    ("prelevement_date_mandat", "DATE", u"Prélèvement - Date mandat"),
                                    ("titulaire", "VARCHAR(400)", u"Titulaire du compte"),
                                    ("type", "VARCHAR(400)", u"Type du prélèvement"),
                                    ("IDfacture", "INTEGER", u"ID de la facture"),
                                    ("libelle", "VARCHAR(400)", u"Libellé du prélèvement"),
                                    ("montant", "FLOAT", u"Montant du prélèvement"),
                                    ("statut", "VARCHAR(100)", u"Statut du prélèvement"),
                                    ("IDmandat", "INTEGER", u"ID du mandat"),
                                    ("sequence", "VARCHAR(100)", u"Séquence SEPA"),
                                    ], # Prélèvement

    "lots_prelevements":[  ("IDlot", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du lot de prélèvement"),
                                    ("nom", "VARCHAR(200)", u"Nom du lot de prélèvements"),
                                    ("date", "DATE", u"Date du prélèvement"),
                                    ("verrouillage", "INTEGER", u"(0/1) Verrouillage du lot"),
                                    ("IDcompte", "INTEGER", u"ID du compte créditeur"),
                                    ("IDmode", "INTEGER", u"ID du mode de règlement"),
                                    ("reglement_auto", "INTEGER", u"Règlement automatique (0/1)"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("type", "VARCHAR(100)", u"Type (national ou SEPA)"),
                                    ], # Lots de prélèvements

    "modeles_tickets":[ ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmodele"),
                                    ("categorie", "VARCHAR(455)", u"Catégorie du modèle"),
                                    ("nom", "VARCHAR(455)", u"Nom du modèle"),
                                    ("description", "VARCHAR(455)", u"Description du modèle"),
                                    ("lignes", "VARCHAR(5000)", u"lignes du ticket"),
                                    ("defaut", "INTEGER", u"Modèle par défaut (0/1)"),
                                    ("taille", "INTEGER", u"Taille de police"),
                                    ("interligne", "INTEGER", u"Hauteur d'interligne"),
                                    ("imprimante", "VARCHAR(455)", u"Nom de l'imprimante"),
                                    ], # Modèles de tickets

    "sauvegardes_auto":[ ("IDsauvegarde", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDsauvegarde"),
                                    ("nom", "VARCHAR(455)", u"Nom de la procédure de sauvegarde auto"),
                                    ("observations", "VARCHAR(455)", u"Observations"),
                                    ("date_derniere", "DATE", u"Date de la dernière sauvegarde"),
                                    ("sauvegarde_nom", "VARCHAR(455)", u"Sauvegarde Nom"),
                                    ("sauvegarde_motdepasse", "VARCHAR(455)", u"Sauvegarde mot de passe"),
                                    ("sauvegarde_repertoire", "VARCHAR(455)", u"sauvegarde Répertoire"),
                                    ("sauvegarde_emails", "VARCHAR(455)", u"Sauvegarde Emails"),
                                    ("sauvegarde_fichiers_locaux", "VARCHAR(455)", u"Sauvegarde fichiers locaux"),
                                    ("sauvegarde_fichiers_reseau", "VARCHAR(455)", u"Sauvegarde fichiers réseau"),
                                    ("condition_jours_scolaires", "VARCHAR(455)", u"Condition Jours scolaires"),
                                    ("condition_jours_vacances", "VARCHAR(455)", u"Condition Jours vacances"),
                                    ("condition_heure", "VARCHAR(455)", u"Condition Heure"),
                                    ("condition_poste", "VARCHAR(455)", u"Condition Poste"),
                                    ("condition_derniere", "VARCHAR(455)", u"Condition Date dernière sauvegarde"),
                                    ("condition_utilisateur", "VARCHAR(455)", u"Condition Utilisateur"),
                                    ("option_afficher_interface", "VARCHAR(455)", u"Option Afficher interface (0/1)"),
                                    ("option_demander", "VARCHAR(455)", u"Option Demander (0/1)"),
                                    ("option_confirmation", "VARCHAR(455)", u"Option Confirmation (0/1)"),
                                    ("option_suppression", "VARCHAR(455)", u"Option Suppression sauvegardes obsolètes"),
                                    ], # procédures de sauvegardes automatiques

    "droits":[                   ("IDdroit", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDdroit"),
                                    ("IDutilisateur", "INTEGER", u"IDutilisateur"),
                                    ("IDmodele", "INTEGER", u"IDmodele"),
                                    ("categorie", "VARCHAR(200)", u"Catégorie de droits"),
                                    ("action", "VARCHAR(200)", u"Type d'action"),
                                    ("etat", "VARCHAR(455)", u"Etat"),
                                    ], # Droits des utilisateurs

    "modeles_droits":[     ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmodele"),
                                    ("nom", "VARCHAR(455)", u"Nom du modèle"),
                                    ("observations", "VARCHAR(455)", u"Observations"),
                                    ("defaut", "INTEGER", u"Modèle par défaut (0/1)"),
                                    ], # Modèles de droits

    "mandats":[               ("IDmandat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmandat"),
                                    ("IDfamille", "INTEGER", u"Famille rattachée"),
                                    ("rum", "VARCHAR(100)", u"RUM du mandat"),
                                    ("type", "VARCHAR(100)", u"Type de mandat (récurrent ou ponctuel)"),
                                    ("date", "DATE", u"Date de signature du mandat"),
                                    ("IDbanque", "INTEGER", u"ID de la banque"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("individu_nom", "VARCHAR(400)", u"Nom du titulaire de compte"),
                                    ("individu_rue", "VARCHAR(400)", u"Rue du titulaire de compte"),
                                    ("individu_cp", "VARCHAR(50)", u"CP du titulaire de compte"),
                                    ("individu_ville", "VARCHAR(400)", u"Ville du titulaire de compte"),
                                    ("iban", "VARCHAR(100)", u"IBAN"),
                                    ("bic", "VARCHAR(100)", u"BIC"),
                                    ("memo", "VARCHAR(450)", u"Mémo"),
                                    ("sequence", "VARCHAR(100)", u"Prochaine séquence"),
                                    ("actif", "INTEGER", u"actif (0/1)"),
                                    ], # Mandats SEPA

    "pes_pieces":[           ("IDpiece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID piece"),
                                    ("IDlot", "INTEGER", u"ID du lot PES"),
                                    ("IDfamille", "INTEGER", u"ID de la famille destinataire"),
                                    ("prelevement", "INTEGER", u"Prélèvement activé (0/1)"),
                                    ("prelevement_iban", "VARCHAR(100)", u"IBAN"),
                                    ("prelevement_bic", "VARCHAR(100)", u"BIC"),
                                    ("prelevement_rum", "VARCHAR(300)", u"Référence Unique Mandat"),
                                    ("prelevement_date_mandat", "DATE", u"Date mandat"),
                                    ("prelevement_IDmandat", "INTEGER", u"ID du mandat"),
                                    ("prelevement_sequence", "VARCHAR(100)", u"Séquence SEPA"),
                                    ("prelevement_titulaire", "VARCHAR(400)", u"Titulaire du compte bancaire"),
                                    ("prelevement_statut", "VARCHAR(100)", u"Statut du prélèvement"),
                                    ("titulaire_helios", "INTEGER", u"Tiers Trésor public"),
                                    ("type", "VARCHAR(400)", u"Type du prélèvement"),
                                    ("IDfacture", "INTEGER", u"ID de la facture"),
                                    ("numero", "BIGINT", u"Numéro de facture"),
                                    ("libelle", "VARCHAR(400)", u"Libellé de la pièce"),
                                    ("montant", "FLOAT", u"Montant du prélèvement"),
                                    ], # Pièces PESV2 ORMC

    "pes_lots":[               ("IDlot", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du lot"),
                                    ("nom", "VARCHAR(200)", u"Nom du lot"),
                                    ("verrouillage", "INTEGER", u"(0/1) Verrouillage du lot"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("reglement_auto", "INTEGER", u"Règlement automatique (0/1)"),
                                    ("IDcompte", "INTEGER", u"ID du compte créditeur"),
                                    ("IDmode", "INTEGER", u"ID du mode de règlement"),
                                    ("exercice", "INTEGER", u"Exercice"),
                                    ("mois", "INTEGER", u"Numéro de mois"),
                                    ("objet_dette", "VARCHAR(450)", u"Objet de la dette"),
                                    ("date_emission", "DATE", u"Date d'émission"),
                                    ("date_prelevement", "DATE", u"Date du prélèvement"),
                                    ("date_envoi", "DATE", u"Date d'avis d'envoi"),
                                    ("id_bordereau", "VARCHAR(200)", u"Identifiant bordereau"),
                                    ("id_poste", "VARCHAR(200)", u"Poste comptable"),
                                    ("id_collectivite", "VARCHAR(200)", u"ID budget collectivité"),
                                    ("code_collectivite", "VARCHAR(200)", u"Code Collectivité"),
                                    ("code_budget", "VARCHAR(200)", u"Code Budget"),
                                    ("code_prodloc", "VARCHAR(200)", u"Code Produit Local"),
                                    ("prelevement_libelle", "VARCHAR(450)", u"Libellé du prélèvement"),
                                    ("objet_piece", "VARCHAR(450)", u"Objet de la pièce"),
                                    ], # Lots PESV2 ORMC

    "contrats":[               ("IDcontrat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID contrat"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDinscription", "INTEGER", u"ID de l'inscription"),
                                    ("date_debut", "DATE", u"Date de début"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité"),
                                    ("type", "VARCHAR(100)", u"Type de contrat"),
                                    ("nbre_absences_prevues", "INTEGER", u"Nombre d'absences prévues PSU"),
                                    ("nbre_heures_regularisation", "INTEGER", u"Nombre d'heures de régularisation PSU"),
                                    ("arrondi_type", "VARCHAR(50)", u"Type d'arrondi sur les heures"),
                                    ("arrondi_delta", "INTEGER", u"Delta en minutes de l'arrondi sur les heures"),
                                    ("duree_absences_prevues", "VARCHAR(50)", u"Temps d'absences prévues PSU"),
                                    ("duree_heures_regularisation", "VARCHAR(50)", u"Temps de régularisation PSU"),
                                    ("duree_tolerance_depassement", "VARCHAR(50)", u"Temps de tolérance dépassements PSU"),
                                    ("planning", "VARCHAR(900)", u"Données de planning serialisées"),
                                    ], # Contrats

    "modeles_contrats":[ ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID modèle"),
                                    ("nom", "VARCHAR(450)", u"Nom du modèle"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité"),
                                    ("date_debut", "DATE", u"Date de début"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("donnees", "LONGBLOB", u"Données en binaire"),
                                    ], # Modèles de contrats

    "modeles_plannings":[("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID modèle"),
                                    ("IDactivite", "INTEGER", u"ID de l'activités concernée"),
                                    ("nom", "VARCHAR(450)", u"Nom du modèle"),
                                    ("donnees", "VARCHAR(900)", u"Données serialisées"),
                                    ], # Modèles de plannings

    "compta_operations":[("IDoperation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID opération"),
                                    ("type", "VARCHAR(200)", u"Type de données (debit/crédit)"),
                                    ("date", "DATE", u"Date de l'opération"),
                                    ("libelle", "VARCHAR(400)", u"Libellé de l'opération"),
                                    ("IDtiers", "INTEGER", u"ID du tiers"),
                                    ("IDmode", "INTEGER", u"ID du mode de règlement"),
                                    ("num_piece", "VARCHAR(200)", u"Numéro de pièce"),
                                    ("ref_piece", "VARCHAR(200)", u"Référence de la pièce"),
                                    ("IDcompte_bancaire", "INTEGER", u"ID du compte bancaire"),
                                    ("IDreleve", "INTEGER", u"ID du relevé bancaire"),
                                    ("montant", "FLOAT", u"Montant de l'opération"),
                                    ("observations", "VARCHAR(450)", u"Observations"),
                                    ("IDvirement", "INTEGER", u"IDvirement associé"),
                                    ], # Compta : Opérations

    "compta_virements":[ ("IDvirement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID virement"),
                                    ("IDoperation_debit", "INTEGER", u"ID opération débiteur"),
                                    ("IDoperation_credit", "INTEGER", u"ID opération créditeur"),
                                    ], # Compta : Virements

    "compta_ventilation":[("IDventilation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID ventilation"),
                                    ("IDoperation", "INTEGER", u"ID de l'opération"),
                                    ("IDexercice", "INTEGER", u"ID de l'exercice"),
                                    ("IDcategorie", "INTEGER", u"ID de la catégorie"),
                                    ("IDanalytique", "INTEGER", u"ID du poste analytique"),
                                    ("libelle", "VARCHAR(400)", u"Libellé de la ventilation"),
                                    ("montant", "FLOAT", u"Montant de la ventilation"),
                                    ("date_budget", "DATE", u"Date d'impact budgétaire"),
                                    ], # Compta : Ventilation des opérations
                                    
    "compta_exercices":[("IDexercice", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Exercice"),
                                    ("nom", "VARCHAR(400)", u"Nom de l'exercice"),
                                    ("date_debut", "DATE", u"Date de début"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ("defaut", "INTEGER", u"Défaut (0/1)"),
                                    ], # Compta : Exercices

    "compta_analytiques":[("IDanalytique", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Analytique"),
                                    ("nom", "VARCHAR(400)", u"Nom du poste analytique"),
                                    ("abrege", "VARCHAR(200)", u"Abrégé du poste analytique"),
                                    ("defaut", "INTEGER", u"Défaut (0/1)"),
                                    ], # Compta : Postes analytiques

    "compta_categories":[("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Catégorie"),
                                    ("type", "VARCHAR(200)", u"Type de données (debit/crédit)"),
                                    ("nom", "VARCHAR(400)", u"Nom de la catégorie"),
                                    ("abrege", "VARCHAR(200)", u"Abrégé de la catégorie"),
                                    ("journal", "VARCHAR(200)", u"Code journal"),
                                    ("IDcompte", "INTEGER", u"ID du compte comptable"),
                                    ], # Compta : Catégories de ventilation

    "compta_comptes_comptables":[("IDcompte", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDcompte"),
                                    ("numero", "VARCHAR(200)", u"Numéro"),
                                    ("nom", "VARCHAR(400)", u"Nom du code"),
                                    ], # Compta : Comptes comptables

    "compta_tiers":         [("IDtiers", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Tiers"),
                                    ("nom", "VARCHAR(400)", u"Nom du tiers"),
                                    ("observations", "VARCHAR(450)", u"Observations"),
                                    ("IDcode_comptable", "INTEGER", u"ID du code comptable"),
                                    ], # Compta : Tiers

    "compta_budgets":    [("IDbudget", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Budget"),
                                    ("IDexercice", "INTEGER", u"ID de l'exercice"),
                                    ("nom", "VARCHAR(400)", u"Nom du budget"),
                                    ("observations", "VARCHAR(200)", u"Observations sur le budget"),
                                    ("analytiques", "VARCHAR(450)", u"Liste des postes analytiques associés"),
                                    ("date_debut", "DATE", u"Date de début de période"),
                                    ("date_fin", "DATE", u"Date de fin de période"),
                                    ], # Compta : Budgets

    "compta_categories_budget":[("IDcategorie_budget", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Categorie budget"),
                                    ("IDbudget", "INTEGER", u"ID du budget"),
                                    ("type", "VARCHAR(200)", u"Type de données (debit/crédit)"),
                                    ("IDcategorie", "INTEGER", u"ID de la catégorie rattachée"),
                                    ("valeur", "VARCHAR(450)", u"Valeur ou formule"),
                                    ], # Compta : Catégories de budget

    "compta_releves":   [("IDreleve", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Relevé"),
                                    ("nom", "VARCHAR(400)", u"Nom du relevé"),
                                    ("date_debut", "DATE", u"Date de début"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ("IDcompte_bancaire", "INTEGER", u"ID du compte bancaire"),
                                    ], # Compta : Relevés de comptes

    "compta_operations_budgetaires":[("IDoperation_budgetaire", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID opération budgétaire"),
                                    ("type", "VARCHAR(200)", u"Type de données (debit/crédit)"),
                                    ("date_budget", "DATE", u"Date d'impact budgétaire"),
                                    ("IDcategorie", "INTEGER", u"ID de la catégorie"),
                                    ("IDanalytique", "INTEGER", u"ID du poste analytique"),
                                    ("libelle", "VARCHAR(400)", u"Libellé de la ventilation"),
                                    ("montant", "FLOAT", u"Montant de la ventilation"),
                                    ], # Compta : Ventilation des opérations

    "nomade_archivage":  [("IDarchive", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Archive"),
                                    ("nom_fichier", "VARCHAR(400)", u"Nom du fichier"),
                                    ("ID_appareil", "VARCHAR(100)", u"ID de l'appareil"),
                                    ("date", "DATE", u"Date de l'archivage"),
                                    ], # Synchronisation Nomadhys : Archivage des fichiers

    "etiquettes":              [("IDetiquette", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Etiquette"),
                                    ("label", "VARCHAR(300)", u"Label de l'étiquette"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité"),
                                    ("parent", "INTEGER", u"Parent de l'étiquette"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("couleur", "VARCHAR(30)", u"Couleur de l'étiquette"),
                                    ("active", "INTEGER", u"Etiquette active (0/1)"),
                                    ], # Etiquettes de consommations

    "contrats_tarifs":              [("IDcontrat_tarif", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID contrat tarif"),
                                    ("IDcontrat", "INTEGER", u"ID du contrat"),
                                    ("date_debut", "DATE", u"Date de début de validité"),
                                    ("revenu", "FLOAT", u"Revenu de la famille"),
                                    ("quotient", "INTEGER", u"Quotient familial de la famille"),
                                    ("taux", "FLOAT", u"Taux d'effort"),
                                    ("tarif_base", "FLOAT", u"Montant du tarif de base"),
                                    ("tarif_depassement", "FLOAT", u"Montant du tarif de dépassement"),
                                    ], # Tarifs de contrats

    "types_quotients":              [("IDtype_quotient", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Type quotient"),
                                    ("nom", "VARCHAR(255)", u"Nom du type de quotient"),
                                    ], # Types de quotients

    "factures_prefixes":            [("IDprefixe", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID préfixe facture"),
                                    ("nom", "VARCHAR(450)", u"Nom du préfixe"),
                                    ("prefixe", "VARCHAR(100)", u"Préfixe de facture"),
                                    ], # Préfixes de factures

    "factures_regies":              [("IDregie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID régie de facturation"),
                                    ("nom", "VARCHAR(450)", u"Nom de la régie"),
                                    ("numclitipi", "VARCHAR(50)", u"Numéro de client TIPI"),
                                    ("email_regisseur", "VARCHAR(100)", u"email du régisseur"),
                                    ("IDcompte_bancaire", "INTEGER", u"ID du compte bancaire associé"),
                                    ], # RÃ©gies de facturation

    "portail_periodes":             [("IDperiode", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID période"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité"),
                                    ("nom", "VARCHAR(300)", u"Nom de la période"),
                                    ("date_debut", "DATE", u"Date de début de la période"),
                                    ("date_fin", "DATE", u"Date de fin de la période"),
                                    ("affichage", "INTEGER", u"Affiché sur le portail (0/1)"),
                                    ("affichage_date_debut", "DATETIME", u"Date et heure de début d'affichage"),
                                    ("affichage_date_fin", "DATETIME", u"Date et heure de fin d'affichage"),
                                    ("IDmodele", "INTEGER", u"IDmodele d'email rattaché à la période"),
                                    ("introduction", "VARCHAR(1000)", u"Texte d'introduction"),
                                    ("prefacturation", "INTEGER", u"Préfacturation (0/1)"),
                                    ], # Périodes de réservations pour le portail

    "portail_unites":               [("IDunite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID unité"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité"),
                                    ("nom", "VARCHAR(300)", u"Nom de l'unité de réservation"),
                                    ("unites_principales", "VARCHAR(300)", u"Unités de consommation principales"),
                                    ("unites_secondaires", "VARCHAR(300)", u"Unités de consommation secondaires"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ], # Unités de réservations pour le portail

    "portail_actions":              [("IDaction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID action"),
                                    ("horodatage", "DATETIME", u"Horodatage de l'action"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDutilisateur", "INTEGER", u"ID de l'utilisateur"),
                                    ("categorie", "VARCHAR(50)", u"Catégorie de l'action"),
                                    ("action", "VARCHAR(50)", u"Nom de l'action"),
                                    ("description", "VARCHAR(300)", u"Description de l'action"),
                                    ("commentaire", "VARCHAR(300)", u"Commentaire de l'action"),
                                    ("parametres", "VARCHAR(300)", u"Paramètres de l'action"),
                                    ("etat", "VARCHAR(50)", u"Etat de l'action"),
                                    ("traitement_date", "DATE", u"Date du traitement de l'action"),
                                    ("IDperiode", "INTEGER", u"ID de la période"),
                                    ("ref_unique", "VARCHAR(50)", u"Référence unique de l'action"),
                                    ("reponse", "VARCHAR(450)", u"Réponse à l'action"),
                                    ("email_date", "DATE", u"Date de l'envoi de l'email de réponse"),
                                    ("IDpaiement", "INTEGER", u"ID du paiement en ligne"),
                                    ("ventilation", "VARCHAR(5000)", u"Ventilation du paiement"),
                                    ], # Actions enregistrées sur le portail

    "portail_reservations":         [("IDreservation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID réservation"),
                                    ("date", "DATE", u"Date de la consommation"),
                                    ("IDinscription", "INTEGER", u"ID de l'inscription"),
                                    ("IDunite", "INTEGER", u"ID de l'unité"),
                                    ("IDaction", "INTEGER", u"ID de l'action"),
                                    ("etat", "INTEGER", u"Ajout ou suppression de la réservation (1/0)"),
                                    ], # Réservations enregistrées sur le portail

    "portail_renseignements":       [("IDrenseignement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID renseignement"),
                                     ("champ", "VARCHAR(255)", u"Nom du champ"),
                                     ("valeur", "VARCHAR(255)", u"Valeur du renseignement"),
                                     ("IDaction", "INTEGER", u"ID de l'action"),
                                     ],  # Renseignements enregistrés sur le portail


    "portail_messages":             [("IDmessage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmessage"),
                                    ("titre", "VARCHAR(255)", u"Titre du message"),
                                    ("texte", "VARCHAR(1000)", u"Contenu du message"),
                                    ("affichage_date_debut", "DATETIME", u"Date et heure de début d'affichage"),
                                    ("affichage_date_fin", "DATETIME", u"Date et heure de fin d'affichage"),
                                     ], # Messages pour la page d'accueil du portail

    "profils":                      [("IDprofil", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Profil"),
                                    ("label", "VARCHAR(400)", u"Nom de profil"),
                                    ("categorie", "VARCHAR(200)", u"Catégorie du profil"),
                                    ("defaut", "INTEGER", u"(0/1) Profil sélectionné par défaut"),
                                    ],  # Profils de paramètres

    "profils_parametres":           [("IDparametre", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID parametre"),
                                    ("IDprofil", "INTEGER", u"ID du profil"),
                                    ("nom", "VARCHAR(200)", u"Nom"),
                                    ("parametre", "VARCHAR(30000)", u"Parametre"),
                                    ("type_donnee", "VARCHAR(200)", u"Type de données"),
                                    ],  # Paramètres des profils

    "evenements":                  [("IDevenement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID évènement"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité associée"),
                                    ("IDunite", "INTEGER", u"ID de l'unité de conso associée"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe associé"),
                                    ("date", "DATE", u"Date de l'évènement"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'évènement"),
                                    ("description", "VARCHAR(1000)", u"Description de l'évènement"),
                                    ("capacite_max", "INTEGER", u"Nombre d'inscrits max sur l'évènement"),
                                    ("heure_debut", "DATE", u"Heure de début de l'évènement"),
                                    ("heure_fin", "DATE", u"Heure de fin de l'évènement"),
                                    ("montant", "FLOAT", u"Montant fixe de la prestation"),
                                    ],  # Evènements

      "modeles_prestations":        [("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID prestation"),
                                    ("categorie", "VARCHAR(50)", u"Catégorie de la prestation"),
                                    ("label", "VARCHAR(200)", u"Label de la prestation"),
                                    ("IDactivite", "INTEGER", u"ID de l'activité"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID de la catégorie de tarif"),
                                    ("tva", "FLOAT", u"Taux TVA"),
                                    ("code_compta", "VARCHAR(200)", u"Code comptable pour export vers logiciels de compta"),
                                    ("public", "VARCHAR(50)", u"Type de public : famille ou individu"),
                                    ("IDtype_quotient", "INTEGER", u"ID du type de quotient"),
                                     ],  # Modèles de prestations


        "produits_categories":     [("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Catégorie de produits"),
                                    ("nom", "VARCHAR(200)", u"Nom de la catégorie"),
                                    ("observations", "VARCHAR(1000)", u"Observations sur la catégorie"),
                                    ("image", "LONGBLOB", u"Image de la catégorie en binaire"),
                                    ],  # Catégories de produits

        "produits":                 [("IDproduit", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Produit"),
                                    ("IDcategorie", "INTEGER", u"ID de la catégorie associée"),
                                    ("nom", "VARCHAR(200)", u"Nom du produit"),
                                    ("observations", "VARCHAR(1000)", u"Observations sur le produit"),
                                    ("image", "LONGBLOB", u"Image du produit en binaire"),
                                    ("quantite", "INTEGER", u"Quantité du produit"),
                                    ("montant", "FLOAT", u"Montant fixe de la prestation"),
                                    ],  # Produits

        "locations":                [("IDlocation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID location"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("IDproduit", "INTEGER", u"ID du produit"),
                                    ("observations", "VARCHAR(1000)", u"Observations sur la location"),
                                    ("date_saisie", "DATE", u"Date de saisie de la location"),
                                    ("date_debut", "DATETIME", u"Date et heure de début de location"),
                                    ("date_fin", "DATETIME", u"Date et heure de fin de location"),
                                    ("quantite", "INTEGER", u"Quantité du produit"),
                                    ],  # Locations


        "locations_demandes":       [("IDdemande", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Demande"),
                                    ("date", "DATETIME", u"Date et heure de la demande"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("observations", "VARCHAR(1000)", u"Observations sur la location"),
                                    ("categories", "VARCHAR(1000)", u"liste ID categories souhaitées"),
                                    ("produits", "VARCHAR(1000)", u"liste ID produits souhaités"),
                                    ("statut", "VARCHAR(100)", u"Statut de la demande"),
                                    ("motif_refus", "VARCHAR(1000)", u"Motif du refus"),
                                    ("IDlocation", "INTEGER", u"ID de la location attribuée"),
                                    ],  # Demandes de locations

    "periodes_gestion":             [("IDperiode", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Période"),
                                    ("date_debut", "DATE", u"Date de début de la période"),
                                    ("date_fin", "DATE", u"Date de fin de la période"),
                                    ("observations", "VARCHAR(1000)", u"Observations"),
                                    ("verrou_consommations", "INTEGER", u"Verrouillage"),
                                    ("verrou_prestations", "INTEGER", u"Verrouillage"),
                                    ("verrou_factures", "INTEGER", u"Verrouillage"),
                                    ("verrou_reglements", "INTEGER", u"Verrouillage"),
                                    ("verrou_depots", "INTEGER", u"Verrouillage"),
                                    ("verrou_cotisations", "INTEGER", u"Verrouillage"),
                                    ],  # Périodes de gestion

    "categories_medicales":         [("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Catégorie"),
                                    ("nom", "VARCHAR(300)", u"Nom de la catégorie"),
                                    ],  # Catégories médicales

    "modeles_commandes":            [("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID modèle"),
                                    ("nom", "VARCHAR(300)", u"Nom du modèle"),
                                    ("IDrestaurateur", "INTEGER", u"ID du restaurateur"),
                                    ("parametres", "VARCHAR(8000)", u"Parametres"),
                                    ("defaut", "INTEGER", u"(0/1) Modèle par défaut"),
                                    ],  # Modèles de commandes de repas

    "modeles_commandes_colonnes":   [("IDcolonne", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID colonne"),
                                    ("IDmodele", "INTEGER", u"ID du modèle de commande"),
                                    ("ordre", "INTEGER", u"Ordre de la colonne"),
                                    ("nom", "VARCHAR(300)", u"Nom de la colonne"),
                                    ("largeur", "INTEGER", u"Largeur de la colonne en pixels"),
                                    ("categorie", "VARCHAR(100)", u"Catégorie de la colonne"),
                                    ("parametres", "VARCHAR(8000)", u"Parametres"),
                                    ],  # Colonnes des modèles de commandes de repas

    "commandes":                    [("IDcommande", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID commande"),
                                    ("IDmodele", "INTEGER", u"ID du modèle de commande"),
                                    ("nom", "VARCHAR(300)", u"Nom de la commande"),
                                    ("date_debut", "DATE", u"Date de début de la période"),
                                    ("date_fin", "DATE", u"Date de fin de la période"),
                                    ("observations", "VARCHAR(1000)", u"Observations"),
                                    ],  # Commandes de repas

    "commandes_valeurs":           [("IDvaleur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID valeur"),
                                    ("IDcommande", "INTEGER", u"ID de la commande"),
                                    ("date", "DATE", u"Date"),
                                    ("IDcolonne", "INTEGER", u"ID de la colonne"),
                                    ("valeur", "VARCHAR(1000)", u"Valeur"),
                                    ],  # Valeurs des commandes de repas

    "portail_pages":               [("IDpage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDpage"),
                                   ("titre", "VARCHAR(300)", u"Titre de la page"),
                                   ("couleur", "VARCHAR(100)", u"Couleur"),
                                   ("ordre", "INTEGER", u"Ordre de la page"),
                                   ],  # Pages personnalisées pour le portail

    "portail_blocs":              [("IDbloc", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDbloc"),
                                    ("IDpage", "INTEGER", u"ID de la page parente"),
                                    ("titre", "VARCHAR(300)", u"Titre de la page"),
                                    ("couleur", "VARCHAR(100)", u"Couleur"),
                                    ("categorie", "VARCHAR(200)", u"Type de contrôle"),
                                    ("ordre", "INTEGER", u"Ordre de la page"),
                                    ("parametres", "VARCHAR(5000)", u"Paramètres divers"),
                                    ],  # Blocs pour les pages personnalisées du portail

    "portail_elements":            [("IDelement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDelement"),
                                    ("IDbloc", "INTEGER", u"ID du bloc parent"),
                                    ("ordre", "INTEGER", u"Ordre de l'élément"),
                                    ("titre", "VARCHAR(300)", u"Titre de l'élément"),
                                    ("categorie", "VARCHAR(200)", u"Catégorie de l'élément"),
                                    ("date_debut", "DATETIME", u"Date et heure de début"),
                                    ("date_fin", "DATETIME", u"Date et heure de fin"),
                                    ("parametres", "VARCHAR(5000)", u"Paramètres divers"),
                                    ("texte_xml", "VARCHAR(5000)", u"Contenu du texte version XML"),
                                    ("texte_html", "VARCHAR(5000)", u"Contenu du texte version HTML"),
                                    ],  # Elements pour les pages du portail

    "menus":                        [("IDmenu", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmenu"),
                                    ("IDrestaurateur", "INTEGER", u"ID du restaurateur"),
                                    ("IDcategorie", "INTEGER", u"ID de la catégorie"),
                                    ("date", "DATE", u"Date"),
                                    ("texte", "VARCHAR(1000)", u"Texte du menu"),
                                    ],  # Menus

    "menus_categories":             [("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDcategorie"),
                                    ("nom", "VARCHAR(300)", u"Nom de la catégorie"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ],  # Catégories des menus

    "menus_legendes":               [("IDlegende", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDlegende"),
                                     ("nom", "VARCHAR(300)", u"Nom de la légende"),
                                     ("couleur", "VARCHAR(100)", u"Couleur"),
                                     ],  # Légendes des menus




}


# ----------------------------------------------------------------------------------------------------------------------------------------------------------

DB_PHOTOS = {

    "photos":[                  ("IDphoto", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID de la photo"),
                                    ("IDindividu", "INTEGER", u"ID de la personne"),
                                    ("photo", "BLOB", u"Photo individu en binaire"),
                                    ], # BLOB photos
    }

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

DB_DOCUMENTS = {

    "documents":[            ("IDdocument", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du document"),
                                    ("IDpiece", "INTEGER", u"ID de la pièce"),
                                    ("IDreponse", "INTEGER", u"ID de la réponse du Questionnaire"),
                                    ("IDtype_piece", "INTEGER", u"ID du type de pièce"),
                                    ("document", "LONGBLOB", u"Document converti en binaire"),
                                    ("type", "VARCHAR(50)", u"Type de document : jpeg, pdf..."),
                                    ("label", "VARCHAR(400)", u"Label du document"),
                                    ("last_update", "VARCHAR(50)", u"Horodatage de la dernière modification du document"),
                                    ], # BLOB documents
                                    
    }

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

DB_INDEX = {

    "index_photos_IDindividu" : {"table" : "photos", "champ" : "IDindividu"},
    "index_liens_IDfamille" : {"table" : "liens", "champ" : "IDfamille"},
    "index_familles_IDcompte_payeur" : {"table" : "familles", "champ" : "IDcompte_payeur"},
    "index_rattachements_IDfamille" : {"table" : "rattachements", "champ" : "IDfamille"},
    "index_pieces_IDfamille" : {"table" : "pieces", "champ" : "IDfamille"},
    "index_pieces_IDindividu" : {"table" : "pieces", "champ" : "IDindividu"},
    "index_ouvertures_IDactivite" : {"table" : "ouvertures", "champ" : "IDactivite"},
    "index_ouvertures_date" : {"table" : "ouvertures", "champ" : "date"},
    "index_remplissage_IDactivite" : {"table" : "remplissage", "champ" : "IDactivite"},
    "index_remplissage_date" : {"table" : "remplissage", "champ" : "date"},
    "index_inscriptions_IDindividu" : {"table" : "inscriptions", "champ" : "IDindividu"},
    "index_inscriptions_IDfamille" : {"table" : "inscriptions", "champ" : "IDfamille"},
    "index_consommations_IDcompte_payeur" : {"table" : "consommations", "champ" : "IDcompte_payeur"},
    "index_consommations_IDindividu" : {"table" : "consommations", "champ" : "IDindividu"},
    "index_consommations_IDactivite" : {"table" : "consommations", "champ" : "IDactivite"},
    "index_consommations_date" : {"table" : "consommations", "champ" : "date"},
    "index_prestations_IDfamille" : {"table" : "prestations", "champ" : "IDfamille"},
    "index_prestations_IDcompte_payeur" : {"table" : "prestations", "champ" : "IDcompte_payeur"},
    "index_prestations_date" : {"table" : "prestations", "champ" : "date"},
    "index_prestations_IDactivite" : {"table" : "prestations", "champ" : "IDactivite"},
    "index_comptes_payeurs_IDfamille" : {"table" : "comptes_payeurs", "champ" : "IDfamille"},
    "index_reglements_IDcompte_payeur" : {"table" : "reglements", "champ" : "IDcompte_payeur"},
    "index_ventilation_IDcompte_payeur" : {"table" : "ventilation", "champ" : "IDcompte_payeur"},
    "index_ventilation_IDprestation" : {"table" : "ventilation", "champ" : "IDprestation"},
    "index_factures_IDcompte_payeur" : {"table" : "factures", "champ" : "IDcompte_payeur"},
    "index_familles_etat" : {"table" : "familles", "champ" : "etat"},
    "index_individus_etat" : {"table" : "individus", "champ" : "etat"},
    }






if __name__ == "__main__":
    """ Affichage de stats sur les tables """
    nbreChamps = 0
    for nomTable, listeChamps in DB_DATA.iteritems() :
        nbreChamps += len(listeChamps)
    print "Nbre de champs DATA =", nbreChamps
    print "Nbre de tables DATA =", len(DB_DATA.keys())