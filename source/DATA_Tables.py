#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

TABLES_IMPORTATION_OPTIONNELLES = [ 
        [u"P�riodes de vacances", ("vacances",), True],
        [u"Jours f�ri�s", ("jours_feries",), True],
        [u"Vaccins et maladies", ("types_vaccins", "vaccins_maladies", "types_maladies",), True],
        [u"Types de sieste", ("types_sieste",), True],
        [u"Cat�gories socio-professionnelles", ("categories_travail",), True],
        [u"Modes et �metteurs de r�glements", ("modes_reglements", "emetteurs"), True],
        [u"R�gimes d'appartenance", ("regimes",), True],
        [u"Mod�les de documents", ("documents_modeles", "documents_objets"), True],
        [u"Niveaux scolaires", ("niveaux_scolaires",), True],
        [u"Comptes comptables", ("compta_comptes_comptables",), True],
        ] # [Nom Categorie, (liste des tables...,), Selectionn�]

TABLES_IMPORTATION_OBLIGATOIRES = []


DB_DATA = {

    "individus":[               ("IDindividu", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID de la personne"),
                                    ("IDcivilite", "INTEGER", u"Civilit� de la personne"),
                                    ("nom", "VARCHAR(100)", u"Nom de famille de la personne"),
                                    ("nom_jfille", "VARCHAR(100)", u"Nom de jeune fille de la personne"),
                                    ("prenom", "VARCHAR(100)", u"Pr�nom de la personne"),
                                    ("num_secu", "VARCHAR(21)", u"Num�ro de s�curit� sociale de la personne"),
                                    ("IDnationalite", "INTEGER", u"Nationalit� de la personne"),
                                    
                                    ("date_naiss", "DATE", u"Date de naissance de la personne"),
                                    ("IDpays_naiss", "INTEGER", u"ID du Pays de naissance de la personne"),
                                    ("cp_naiss", "VARCHAR(10)", u"Code postal du lieu de naissance de la personne"),
                                    ("ville_naiss", "VARCHAR(100)", u"Ville du lieu de naissance de la personne"),
                                    ("deces", "INTEGER", u"Est d�c�d� (0/1)"),
                                    ("annee_deces", "INTEGER", u"Ann�e de d�c�s"),
                                    
                                    ("adresse_auto", "INTEGER", u"IDindividu dont l'adresse est � reporter"),
                                    ("rue_resid", "VARCHAR(255)", u"Adresse de la personne"),
                                    ("cp_resid", "VARCHAR(10)", u"Code postal de la personne"),
                                    ("ville_resid", "VARCHAR(100)", u"Ville de la personne"), 
                                    ("IDsecteur", "INTEGER", u"Secteur g�ographique"), 
                                    
                                    ("IDcategorie_travail", "INTEGER", u"IDcategorie socio-professionnelle"),
                                    ("profession", "VARCHAR(100)", u"Profession de la personne"),  
                                    ("employeur", "VARCHAR(100)", u"Employeur de la personne"), 
                                    ("travail_tel", "VARCHAR(50)", u"Tel travail de la personne"),  
                                    ("travail_fax", "VARCHAR(50)", u"Fax travail de la personne"),  
                                    ("travail_mail", "VARCHAR(50)", u"Email travail de la personne"),  
                                    
                                    ("tel_domicile", "VARCHAR(50)", u"Tel domicile de la personne"),  
                                    ("tel_mobile", "VARCHAR(50)", u"Tel mobile perso de la personne"),  
                                    ("tel_fax", "VARCHAR(50)", u"Fax perso de la personne"),  
                                    ("mail", "VARCHAR(50)", u"Email perso de la personne"),  
                                    
                                    ("IDmedecin", "INTEGER", u"ID du m�decin traitant de l'individu"),
                                    ("memo", "VARCHAR(2000)", u"M�mo concernant l'individu"),  
                                    ("IDtype_sieste", "INTEGER", u"Type de sieste"),
                                    
                                    ("date_creation", "DATE", u"Date de cr�ation de la fiche individu"),
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
                                    ("date_creation", "DATE", u"Date de cr�ation de la fiche famille"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("IDcaisse", "INTEGER", u"ID de la caisse d'allocation"),
                                    ("num_allocataire", "VARCHAR(100)", u"Num�ro d'allocataire"),
                                    ("allocataire", "INTEGER", u"ID de l'individu allocataire principal"),
                                    ("internet_actif", "INTEGER", u"(0/1) Compte internet actif"),
                                    ("internet_identifiant", "VARCHAR(50)", u"Code identifiant internet"),
                                    ("internet_mdp", "VARCHAR(50)", u"Mot de passe internet"),
                                    ("memo", "VARCHAR(2000)", u"M�mo concernant la famille"),  
                                    ("prelevement_activation", "INTEGER", u"Activation du pr�l�vement"),
                                    ("prelevement_etab", "VARCHAR(50)", u"Pr�l�vement - Code �tab"),
                                    ("prelevement_guichet", "VARCHAR(50)", u"Pr�l�vement - Code guichet"),
                                    ("prelevement_numero", "VARCHAR(50)", u"Pr�l�vement - Num�ro de compte"),
                                    ("prelevement_cle", "VARCHAR(50)", u"Pr�l�vement - Code cl�"),
                                    ("prelevement_banque", "INTEGER", u"Pr�l�vement - ID de la Banque"),
                                    ("prelevement_individu", "INTEGER", u"Pr�l�vement - ID Individu"),
                                    ("prelevement_nom", "VARCHAR(200)", u"Pr�l�vement - nom titulaire"),
                                    ("prelevement_rue", "VARCHAR(400)", u"Pr�l�vement - rue titulaire"),
                                    ("prelevement_cp", "VARCHAR(50)", u"Pr�l�vement - cp titulaire"),
                                    ("prelevement_ville", "VARCHAR(400)", u"Pr�l�vement - ville titulaire"),
                                    ("prelevement_cle_iban", "VARCHAR(10)", u"Pr�l�vement - Cl� IBAN"),
                                    ("prelevement_iban", "VARCHAR(100)", u"Pr�l�vement - Cl� IBAN"),
                                    ("prelevement_bic", "VARCHAR(100)", u"Pr�l�vement - BIC"),
                                    ("prelevement_reference_mandat", "VARCHAR(300)", u"Pr�l�vement - R�f�rence mandat"),
                                    ("prelevement_date_mandat", "DATE", u"Pr�l�vement - Date mandat"),
                                    ("prelevement_memo", "VARCHAR(450)", u"Pr�l�vement - M�mo"),
                                    ("email_factures", "VARCHAR(450)", u"Adresse Email pour envoi des factures"),
                                    ("email_recus", "VARCHAR(450)", u"Adresse Email pour envoi des re�us de r�glements"),
                                    ("email_depots", "VARCHAR(450)", u"Adresse Email pour avis d'encaissement des r�glements"),
                                    ("titulaire_helios", "INTEGER", u"IDindividu du titulaire H�lios"),
                                    ("code_comptable", "VARCHAR(450)", u"Code comptable pour facturation et export logiciels compta"),
                                    ("idtiers_helios", "VARCHAR(300)", u"IDtiers pour H�lios"),
                                    ("natidtiers_helios", "INTEGER", u"Nature IDtiers pour H�lios"),
                                    ("reftiers_helios", "VARCHAR(300)", u"R�f�rence locale du tiers pour H�lios"),
                                    ("cattiers_helios", "INTEGER", u"Cat�gorie de tiers pour H�lios"),
                                    ("natjur_helios", "INTEGER", u"Nature juridique du tiers pour H�lios"),
                                    ], # Les familles
    
    "rattachements":[       ("IDrattachement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID rattachement"),
                                    ("IDindividu", "INTEGER", u"IDindividu sujet du rattachement"),
                                    ("IDfamille", "INTEGER", u"IDfamille objet du rattachement"),
                                    ("IDcategorie", "INTEGER", u"IDcategorie du rattachement (responsable|enfant|contact)"),
                                    ("titulaire", "INTEGER", u"=1 si l'individu est titulaire de la fiche famille"),
                                    ], # Les rattachements � une ou plusieurs familles

    "types_maladies":[     ("IDtype_maladie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type_maladie"),
                                    ("nom", "VARCHAR(100)", u"Nom de la maladie"),
                                    ("vaccin_obligatoire", "INTEGER", u"=1 si vaccin obligatoire"),
                                    ], # Types de maladies

    "types_vaccins":[       ("IDtype_vaccin", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type_vaccin"),
                                    ("nom", "VARCHAR(100)", u"Nom du vaccin"),
                                    ("duree_validite", "VARCHAR(50)", u"Dur�e de validit�"),
                                    ], # Les types de vaccins

    "vaccins_maladies":[  ("IDvaccins_maladies", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID vaccins_maladies"),
                                    ("IDtype_vaccin", "INTEGER", u"IDtype_vaccin"),
                                    ("IDtype_maladie", "INTEGER", u"IDtype_maladie"),
                                    ], # Liens entre les vaccins et les maladies concern�es
    
    "medecins":[              ("IDmedecin", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du m�decin"),
                                    ("nom", "VARCHAR(100)", u"Nom de famille du m�decin"),
                                    ("prenom", "VARCHAR(100)", u"Pr�nom du m�decin"),
                                    ("rue_resid", "VARCHAR(255)", u"Adresse du m�decin"),
                                    ("cp_resid", "VARCHAR(10)", u"Code postal du m�decin"),
                                    ("ville_resid", "VARCHAR(100)", u"Ville du m�decin"),  
                                    ("tel_cabinet", "VARCHAR(50)", u"Tel du cabinet du m�decin"),  
                                    ("tel_mobile", "VARCHAR(50)", u"Tel du mobile du m�decin"),  
                                    ], # Les m�decins

    "vaccins":[                 ("IDvaccin", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du vaccin"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu concern�"),
                                    ("IDtype_vaccin", "INTEGER", u"ID du vaccin concern�"),
                                    ("date", "DATE", u"date du vaccin"),
                                    ], # Les vaccins des individus    

    "problemes_sante":[   ("IDprobleme", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du probleme de sant�"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDtype", "INTEGER", u"ID du type de probl�me"),
                                    ("intitule", "VARCHAR(100)", u"Intitul� du probl�me"),
                                    ("date_debut", "DATE", u"Date de d�but du probl�me"),
                                    ("date_fin", "DATE", u"Date de fin du probl�me"),
                                    ("description", "VARCHAR(2000)", u"Description du probl�me"),
                                    ("traitement_medical", "INTEGER", u"Traitement m�dical (1/0)"),
                                    ("description_traitement", "VARCHAR(2000)", u"Description du traitement m�dical"),
                                    ("date_debut_traitement", "DATE", u"Date de d�but du traitement"),
                                    ("date_fin_traitement", "DATE", u"Date de fin du traitement"),
                                    ("eviction", "INTEGER", u"Eviction (1/0)"),
                                    ("date_debut_eviction", "DATE", u"Date de d�but de l'�viction"),
                                    ("date_fin_eviction", "DATE", u"Date de fin de l'�viction"),
                                    ("diffusion_listing_enfants", "INTEGER", u"Diffusion listing enfants (1/0)"),
                                    ("diffusion_listing_conso", "INTEGER", u"Diffusion listing consommations (1/0)"),
                                    ("diffusion_listing_repas", "INTEGER", u"Diffusion commande des repas (1/0)"),
                                    ], # Les probl�mes de sant� des individus  

    "vacances":[              ("IDvacance", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID periode vacances"),
                                    ("nom", "VARCHAR(100)", u"Nom de la p�riode de vacances"),
                                    ("annee", "INTEGER", u"Ann�e de la p�riode de vacances"),
                                    ("date_debut", "DATE", u"Date de d�but"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ], # Calendrier des jours de vacances

    "jours_feries":[           ("IDferie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID jour f�ri�"),
                                    ("type", "VARCHAR(10)", u"Type de jour f�ri� : fixe ou variable"),
                                    ("nom", "VARCHAR(100)", u"Nom du jour f�ri�"),
                                    ("jour", "INTEGER", u"Jour de la date"),
                                    ("mois", "INTEGER", u"Mois de la date"),
                                    ("annee", "INTEGER", u"Ann�e de la date"),
                                    ], # Calendrier des jours f�ri�s variables et fixes

    "categories_travail":[   ("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID cat�gorie socio-professionnelle"),
                                    ("nom", "VARCHAR(100)", u"Nom de la cat�gorie"),
                                    ], # Cat�gories socio-professionnelles des individus

    "types_pieces":[        ("IDtype_piece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type pi�ce"),
                                    ("nom", "VARCHAR(100)", u"Nom de la pi�ce"),
                                    ("public", "VARCHAR(12)", u"Public (individu ou famille)"),
                                    ("duree_validite", "VARCHAR(50)", u"Dur�e de validit�"),
                                    ("valide_rattachement", "INTEGER", u"(0|1) Valide m�me si individu rattach� � une autre famille"),
                                    ], # Types de pi�ces

    "pieces":[                  ("IDpiece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Pi�ce"),
                                    ("IDtype_piece", "INTEGER", u"IDtype_piece"),
                                    ("IDindividu", "INTEGER", u"IDindividu"),
                                    ("IDfamille", "INTEGER", u"IDfamille"),
                                    ("date_debut", "DATE", u"Date de d�but"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ], # Pi�ces rattach�es aux individus ou familles

    "organisateur":[          ("IDorganisateur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Organisateur"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'organisateur"),
                                    ("rue", "VARCHAR(200)", u"Adresse"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(100)", u"Ville"),  
                                    ("tel", "VARCHAR(50)", u"Tel travail"),  
                                    ("fax", "VARCHAR(50)", u"Fax travail"),  
                                    ("mail", "VARCHAR(100)", u"Email organisateur"),  
                                    ("site", "VARCHAR(100)", u"Adresse site internet"),  
                                    ("num_agrement", "VARCHAR(100)", u"Num�ro d'agr�ment"),  
                                    ("num_siret", "VARCHAR(100)", u"Num�ro SIRET"),  
                                    ("code_ape", "VARCHAR(100)", u"Code APE"),
                                    ("logo", "LONGBLOB", u"Logo de l'organisateur en binaire"),
                                    ("gps", "VARCHAR(200)", u"Coordonn�es GPS au format 'lat;long' "),
                                    ], # Organisateur

    "responsables_activite":[("IDresponsable", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Responsable"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("sexe", "VARCHAR(10)", u"Sexe de l'individu (H/F)"),
                                    ("nom", "VARCHAR(200)", u"Nom du responsable"),
                                    ("fonction", "VARCHAR(200)", u"Fonction"),
                                    ("defaut", "INTEGER", u"(0/1) Responsable s�lectionn� par d�faut"),
                                    ], # Responsables de l'activit�

    "activites":[               ("IDactivite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Activit�"),
                                    ("nom", "VARCHAR(200)", u"Nom complet de l'activit�"),
                                    ("abrege", "VARCHAR(50)", u"Nom abr�g� de l'activit�"),
                                    ("coords_org", "INTEGER", u"(0/1) Coordonn�es identiques � l'organisateur"),
                                    ("rue", "VARCHAR(200)", u"Adresse"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(100)", u"Ville"),  
                                    ("tel", "VARCHAR(50)", u"Tel travail"),  
                                    ("fax", "VARCHAR(50)", u"Fax travail"),  
                                    ("mail", "VARCHAR(100)", u"Email"),  
                                    ("site", "VARCHAR(100)", u"Adresse site internet"),
                                    ("logo_org", "INTEGER", u"(0/1) Logo identique � l'organisateur"),
                                    ("logo", "LONGBLOB", u"Logo de l'activit� en binaire"),
                                    ("date_debut", "DATE", u"Date de d�but de validit�"),
                                    ("date_fin", "DATE", u"Date de fin de validit�"),
                                    ("public", "VARCHAR(20)", u"Liste du public"),
                                    ("vaccins_obligatoires", "INTEGER", u"(0/1) Vaccins obligatoires pour l'individu inscrit"),
                                    ("date_creation", "DATE", u"Date de cr�ation de l'activit�"),
                                    ("nbre_inscrits_max", "INTEGER", u"Nombre d'inscrits max"),
                                    ("code_comptable", "VARCHAR(450)", u"Code comptable pour facturation et export logiciels compta"),
                                    ], # Activit�s

    "agrements":[            ("IDagrement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Agr�ment"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("agrement", "VARCHAR(200)", u"Num�ro d'agr�ment"),
                                    ("date_debut", "DATE", u"Date de d�but de validit�"),
                                    ("date_fin", "DATE", u"Date de fin de validit�"),
                                    ], # Agr�ments de l'activit�

    "groupes":[                ("IDgroupe", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Groupe"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("nom", "VARCHAR(200)", u"Nom du groupe"),
                                    ("abrege", "VARCHAR(100)", u"Nom abr�g� du groupe"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ], # Groupes

    "pieces_activites":[    ("IDpiece_activite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Pi�ce activit�"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("IDtype_piece", "INTEGER", u"ID du type de pi�ce � fournir"),
                                    ], # Pi�ces � fournir pour une activit�

    "cotisations_activites":[("IDcotisation_activite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Cotisation activit�"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("IDtype_cotisation", "INTEGER", u"ID du type de cotisation � fournir"),
                                    ], # Cotisations � avoir pour une activit�

    "renseignements_activites":[("IDrenseignement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Renseignement"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("IDtype_renseignement", "INTEGER", u"ID du type de renseignement � fournir"),
                                    ], # Informations � renseigner par les individus pour une activit�

    "restaurateurs":[        ("IDrestaurateur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Restaurateur"),
                                    ("nom", "VARCHAR(200)", u"Nom du restaurateur"),
                                    ("rue", "VARCHAR(200)", u"Adresse"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(100)", u"Ville"),  
                                    ("tel", "VARCHAR(50)", u"Tel travail"),  
                                    ("fax", "VARCHAR(50)", u"Fax travail"),  
                                    ("mail", "VARCHAR(100)", u"Email"),  
                                    ], # Restaurateurs

    "unites":[                   ("IDunite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Unit�"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'unit�"),
                                    ("abrege", "VARCHAR(50)", u"Nom abr�g�"),
                                    ("type", "VARCHAR(20)", u"Type (unitaire/horaire)"),
                                    ("heure_debut", "DATE", u"Horaire minimum"),
                                    ("heure_debut_fixe", "INTEGER", u"Heure de d�but fixe (0/1)"),
                                    ("heure_fin", "DATE", u"Horaire maximal"),  
                                    ("heure_fin_fixe", "INTEGER", u"Heure de fin fixe (0/1)"),
                                    ("repas", "INTEGER", u"Repas inclus (0/1)"),  
                                    ("IDrestaurateur", "INTEGER", u"IDrestaurateur"),
                                    ("date_debut", "DATE", u"Date de d�but de validit�"),  
                                    ("date_fin", "DATE", u"Date de fin de validit�"),
                                    ("touche_raccourci", "VARCHAR(30)", u"Touche de raccourci pour la grille de saisie"), 
                                    ("largeur", "INTEGER", u"Largeur de colonne en pixels"),
                                    ("coeff", "VARCHAR(50)", u"Coeff pour �tat global"),
                                    ], # Unit�s

    "unites_groupes":[      ("IDunite_groupe", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Unit�_groupe"),
                                    ("IDunite", "INTEGER", u"ID de l'unit� concern�e"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe associ�"),  
                                    ], # Groupes concern�s par l'unit�

    "unites_incompat":[    ("IDunite_incompat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Unit�_incompat"),
                                    ("IDunite", "INTEGER", u"ID de l'unit� concern�e"),
                                    ("IDunite_incompatible", "INTEGER", u"ID de l'unit� incompatible"),  
                                    ], # Unit�s incompatibles entre elles

    "unites_remplissage":[("IDunite_remplissage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Unit�_remplissage"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'unit� de remplissage"),
                                    ("abrege", "VARCHAR(50)", u"Nom abr�g�"),
                                    ("date_debut", "DATE", u"Date de d�but de validit�"),  
                                    ("date_fin", "DATE", u"Date de fin de validit�"),
                                    ("seuil_alerte", "INTEGER", u"Seuil d'alerte de remplissage"),
                                    ("heure_min", "DATE", u"Plage horaire conditionnelle - Heure min"),
                                    ("heure_max", "DATE", u"Plage horaire conditionnelle - Heure max"),  
                                    ("afficher_page_accueil", "INTEGER", u"Afficher dans le cadre Effectifs de la page d'accueil"),
                                    ("afficher_grille_conso", "INTEGER", u"Afficher dans la grille des conso"),
                                    ], # Unit�s de remplissage

    "unites_remplissage_unites":[("IDunite_remplissage_unite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Unit�_remplissage_unite"),
                                    ("IDunite_remplissage", "INTEGER", u"ID de l'unit� de remplissage concern�e"),
                                    ("IDunite", "INTEGER", u"ID de l'unit� associ�e"),  
                                    ], # Unit�s associ�es aux unit�s de remplissage
                                    
    "ouvertures":[             ("IDouverture", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID ouverture"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("IDunite", "INTEGER", u"ID de l'unit� concern�e"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe concern�"),
                                    ("date", "DATE", u"Date de l'ouverture"),  
                                    ], # Jours de fonctionnement des unit�s
                                    
    "remplissage":[          ("IDremplissage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID remplissage"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("IDunite_remplissage", "INTEGER", u"ID de l'unit� de remplissage concern�e"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe concern�"),
                                    ("date", "DATE", u"Date de l'ouverture"),
                                    ("places", "INTEGER", u"Nbre de places"),  
                                    ], # Nbre de places maxi pour chaque unit� de remplissage

    "categories_tarifs":[    ("IDcategorie_tarif", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Cat�gorie de tarif"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("nom", "VARCHAR(200)", u"Nom de la cat�gorie"),
                                    ], # Cat�gories de tarifs

    "categories_tarifs_villes":[("IDville", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Ville"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID de la cat�gorie de tarif concern�e"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("nom", "VARCHAR(100)", u"Nom de la ville"),
                                    ], # Villes rattach�es aux cat�gories de tarifs

    "noms_tarifs":[           ("IDnom_tarif", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID nom tarif"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID categorie_tarif rattach�e"),
                                    ("nom", "VARCHAR(200)", u"Nom du tarif"),
                                    ], # Noms des tarifs

    "tarifs":[                    ("IDtarif", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID tarif"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("type", "VARCHAR(50)", u"Type de tarif"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID categorie_tarif rattach�e"),
                                    ("IDnom_tarif", "INTEGER", u"ID nom du tarif"),
                                    ("date_debut", "DATE", u"Date de d�but de validit�"),
                                    ("date_fin", "DATE", u"Date de fin de validit�"),  
                                    ("condition_nbre_combi", "INTEGER", u""),
                                    ("condition_periode", "VARCHAR(100)", u"Type de tarif (pr�d�fini ou automatique)"),
                                    ("condition_nbre_jours", "INTEGER", u""),
                                    ("condition_conso_facturees", "INTEGER", u""),
                                    ("condition_dates_continues", "INTEGER", u""),
                                    ("forfait_saisie_manuelle", "INTEGER", u"Saisie manuelle du forfait possible (0/1)"),
                                    ("forfait_saisie_auto", "INTEGER", u"Saisie automatique du forfait quand inscription (0/1)"),
                                    ("forfait_suppression_auto", "INTEGER", u"Suppression manuelle impossible (0/1)"),
                                    ("methode", "VARCHAR(50)", u"Code de la m�thode de calcul"),
                                    ("categories_tarifs", "VARCHAR(300)", u"Cat�gories de tarifs rattach�es � ce tarif"),
                                    ("groupes", "VARCHAR(300)", u"Groupes rattach�s � ce tarif"),
                                    ("forfait_duree", "VARCHAR(50)", u"Dur�e du forfait"),
                                    ("forfait_beneficiaire", "VARCHAR(50)", u"B�n�ficiaire du forfait (famille|individu)"),
                                    ("cotisations", "VARCHAR(300)", u"Cotisations rattach�es � ce tarif"),
                                    ("caisses", "VARCHAR(300)", u"Caisses rattach�es � ce tarif"),
                                    ("description", "VARCHAR(450)", u"Description du tarif"),
                                    ("jours_scolaires", "VARCHAR(100)", u"Jours scolaires"),
                                    ("jours_vacances", "VARCHAR(100)", u"Jours de vacances"),
                                    ("options", "VARCHAR(450)", u"Options diverses"),
                                    ("observations", "VARCHAR(450)", u"Observations sur le tarif"),
                                    ("tva", "FLOAT", u"Taux TVA"),
                                    ("code_compta", "VARCHAR(200)", u"Code comptable pour export vers logiciels de compta"),
                                    ("date_facturation", "VARCHAR(450)", u"Date de facturation de la prestation"),
                                    ], # Tarifs

    "combi_tarifs":          [("IDcombi_tarif", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID combinaison de tarif"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("type", "VARCHAR(50)", u"Type de combinaison"),
                                    ("date", "DATE", u"Date si dans forfait"),
                                    ("quantite_max", "INTEGER", u"Quantit� max d'unit�s"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe concern�"),
                                    ], # Combinaisons d'unit�s pour les tarifs

    "combi_tarifs_unites":[("IDcombi_tarif_unite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID combinaison de tarif"),
                                    ("IDcombi_tarif", "INTEGER", u"ID du combi_tarif"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("IDunite", "INTEGER", u"ID de l'unit�"),
                                    ], # Combinaisons d'unit�s pour les tarifs

    "tarifs_lignes":          [("IDligne", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID ligne de tarif"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("code", "VARCHAR(50)", u"Code de la m�thode"),
                                    ("num_ligne", "INTEGER", u"Num�ro de ligne"),
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
                                    ("heure_debut_min", "DATE", u"Heure d�but min pour unit�s horaires"),  
                                    ("heure_debut_max", "DATE", u"Heure d�but max pour unit�s horaires"),  
                                    ("heure_fin_min", "DATE", u"Heure fin min pour unit�s horaires"),  
                                    ("heure_fin_max", "DATE", u"Heure fin max pour unit�s horaires"), 
                                    ("duree_min", "DATE", u"Dur�e min pour unit�s horaires"), 
                                    ("duree_max", "DATE", u"Dur�e min pour unit�s horaires"), 
                                    ("date", "DATE", u"Date conditionnelle"), 
                                    ("label", "VARCHAR(300)", u"Label personnalis� pour la prestation"), 
                                    ("temps_facture", "DATE", u"Temps factur� pour la CAF"), 
                                    ("unite_horaire", "DATE", u"Unit� horaire pour base de calcul selon coefficient"), 
                                    ("duree_seuil", "DATE", u"Dur�e seuil"), 
                                    ("duree_plafond", "DATE", u"Dur�e plafond"), 
                                    ("taux", "FLOAT", u"Taux d'effort"), 
                                    ("ajustement", "FLOAT", u"Ajustement (majoration/d�duction)"), 
                                    ("montant_questionnaire", "INTEGER", u"IDquestion de la table questionnaires"),
                                    ], # Lignes du tableau de calcul de tarifs
                                    
    "inscriptions":[           ("IDinscription", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID inscription"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit�"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID de la cat�gorie de tarif"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur par d�faut"), 
                                    ("date_inscription", "DATE", u"Date de l'inscription"),
                                    ("parti", "INTEGER", u"(0/1) est parti"),
                                    ], # Inscriptions des individus � des activit�s

    "consommations":[    ("IDconso", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID consommation"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDinscription", "INTEGER", u"ID de l'inscription"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit�"),
                                    ("date", "DATE", u"Date de la consommation"),
                                    ("IDunite", "INTEGER", u"ID de l'unit�"),
                                    ("IDgroupe", "INTEGER", u"ID du groupe"),
                                    ("heure_debut", "DATE", u"Heure min pour unit�s horaires"),  
                                    ("heure_fin", "DATE", u"Heure max pour unit�s horaires"),  
                                    ("etat", "VARCHAR(20)", u"Etat"),
                                    ("verrouillage", "INTEGER", u"1 si la consommation est verrouill�e"),
                                    ("date_saisie", "DATE", u"Date de saisie de la consommation"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a fait la saisie"),
                                    ("IDcategorie_tarif", "INTEGER", u"ID de la cat�gorie de tarif"), 
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("IDprestation", "INTEGER", u"ID de la prestation"),
                                    ("forfait", "INTEGER", u"Type de forfait : 0 : Aucun | 1 : Suppr possible | 2 : Suppr impossible"),
                                    ("quantite", "INTEGER", u"Quantit� de consommations"),
                                    ], # Consommations

    "memo_journee":[      ("IDmemo", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID memo"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("date", "DATE", u"Date"),
                                    ("texte", "VARCHAR(200)", u"Texte du m�mo"),
                                    ], # M�mo journ�es

    "prestations":[           ("IDprestation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID prestation"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("date", "DATE", u"Date de la prestation"),
                                    ("categorie", "VARCHAR(50)", u"Cat�gorie de la prestation"),
                                    ("label", "VARCHAR(200)", u"Label de la prestation"),
                                    ("montant_initial", "FLOAT", u"Montant de la prestation AVANT d�ductions"),
                                    ("montant", "FLOAT", u"Montant de la prestation"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit�"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("IDfacture", "INTEGER", u"ID de la facture"),
                                    ("IDfamille", "INTEGER", u"ID de la famille concern�e"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu concern�"),
                                    ("forfait", "INTEGER", u"Type de forfait : 0 : Aucun | 1 : Suppr possible | 2 : Suppr impossible"),
                                    ("temps_facture", "DATE", u"Temps factur� format 00:00"),  
                                    ("IDcategorie_tarif", "INTEGER", u"ID de la cat�gorie de tarif"),
                                    ("forfait_date_debut", "DATE", u"Date de d�but de forfait"),  
                                    ("forfait_date_fin", "DATE", u"Date de fin de forfait"),  
                                    ("reglement_frais", "INTEGER", u"ID du r�glement"),
                                    ("tva", "FLOAT", u"Taux TVA"),
                                    ("code_compta", "VARCHAR(200)", u"Code comptable pour export vers logiciels de compta"),
                                    ("IDcontrat", "INTEGER", u"ID du contrat associ�"),
                                    ], # Prestations

    "comptes_payeurs":[  ("IDcompte_payeur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID compte_payeur"),
                                    ("IDfamille", "INTEGER", u"ID de la famille concern�e"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu concern�"),
                                    ], # Comptes payeurs

    "modes_reglements":[("IDmode", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID mode de r�glement"),
                                    ("label", "VARCHAR(100)", u"Label du mode"),
                                    ("image", "LONGBLOB", u"Image du mode"),
                                    ("numero_piece", "VARCHAR(10)", u"Num�ro de pi�ce (None|ALPHA|NUM)"),
                                    ("nbre_chiffres", "INTEGER", u"Nbre de chiffres du num�ro"),
                                    ("frais_gestion", "VARCHAR(10)", u"Frais de gestion None|LIBRE|FIXE|PRORATA"),
                                    ("frais_montant", "FLOAT", u"Montant fixe des frais"),
                                    ("frais_pourcentage", "FLOAT", u"Prorata des frais"),
                                    ("frais_arrondi", "VARCHAR(20)", u"M�thode d'arrondi"),
                                    ("frais_label", "VARCHAR(200)", u"Label de la prestation"),
                                    ("type_comptable", "VARCHAR(200)", u"Type comptable (banque ou caisse)"),
                                    ("code_compta", "VARCHAR(200)", u"Code comptable pour export vers logiciels de compta"),
                                    ], # Modes de r�glements

    "emetteurs":[             ("IDemetteur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Emetteur"),
                                    ("IDmode", "INTEGER", u"ID du mode concern�"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'�metteur"),
                                    ("image", "LONGBLOB", u"Image de l'emetteur"),
                                    ], # Emetteurs pour les modes de r�glements

    "payeurs":[                ("IDpayeur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Payeur"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur concern�"),
                                    ("nom", "VARCHAR(100)", u"Nom du payeur"),
                                    ], # Payeurs

    "comptes_bancaires":[("IDcompte", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Compte"),
                                    ("nom", "VARCHAR(100)", u"Intitul� du compte"),
                                    ("numero", "VARCHAR(50)", u"Num�ro du compte"),
                                    ("defaut", "INTEGER", u"(0/1) Compte s�lectionn� par d�faut"),
                                    ("raison", "VARCHAR(400)", u"Raison sociale"),
                                    ("code_etab", "VARCHAR(400)", u"Code �tablissement"),
                                    ("code_guichet", "VARCHAR(400)", u"Code guichet"),
                                    ("code_nne", "VARCHAR(400)", u"Code NNE pour pr�l�vements auto."),
                                    ("cle_rib", "VARCHAR(400)", u"Cl� RIB pour pr�l�vements auto."),
                                    ("cle_iban", "VARCHAR(400)", u"Cl� IBAN pour pr�l�vements auto."),
                                    ("iban", "VARCHAR(400)", u"Num�ro IBAN pour pr�l�vements auto."),
                                    ("bic", "VARCHAR(400)", u"Num�ro BIC pour pr�l�vements auto."),
                                    ("code_ics", "VARCHAR(400)", u"Code NNE pour pr�l�vements auto."),
                                    ], # Comptes bancaires de l'organisateur
                                    
    "reglements":[            ("IDreglement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID R�glement"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("date", "DATE", u"Date d'�mission du r�glement"),
                                    ("IDmode", "INTEGER", u"ID du mode de r�glement"),
                                    ("IDemetteur", "INTEGER", u"ID de l'�metteur du r�glement"),
                                    ("numero_piece", "VARCHAR(30)", u"Num�ro de pi�ce"),
                                    ("montant", "FLOAT", u"Montant du r�glement"),
                                    ("IDpayeur", "INTEGER", u"ID du payeur"),
                                    ("observations", "VARCHAR(200)", u"Observations"),
                                    ("numero_quittancier", "VARCHAR(30)", u"Num�ro de quittancier"),
                                    ("IDprestation_frais", "INTEGER", u"ID de la prestation de frais de gestion"),
                                    ("IDcompte", "INTEGER", u"ID du compte bancaire pour l'encaissement"),
                                    ("date_differe", "DATE", u"Date de l'encaissement diff�r�"),
                                    ("encaissement_attente", "INTEGER", u"(0/1) Encaissement en attente"),
                                    ("IDdepot", "INTEGER", u"ID du d�p�t"),
                                    ("date_saisie", "DATE", u"Date de saisie du r�glement"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a fait la saisie"),
                                    ("IDprelevement", "INTEGER", u"ID du pr�l�vement"),
                                    ("avis_depot", "DATE", u"Date de l'envoi de l'avis de d�p�t"),
                                    ("IDpiece", "INTEGER", u"IDpiece pour PES V2 ORMC"),
                                    ], # R�glements

    "ventilation":[             ("IDventilation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Ventilation"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("IDreglement", "INTEGER", u"ID du r�glement"),
                                    ("IDprestation", "INTEGER", u"ID de la prestation"),
                                    ("montant", "FLOAT", u"Montant de la ventilation"),
                                    ], # Ventilation

    "depots":[                  ("IDdepot", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID D�p�t"),
                                    ("date", "DATE", u"Date du d�p�t"),
                                    ("nom", "VARCHAR(200)", u"Nom du d�p�t"),
                                    ("verrouillage", "INTEGER", u"(0/1) Verrouillage du d�p�t"),
                                    ("IDcompte", "INTEGER", u"ID du compte d'encaissement"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("code_compta", "VARCHAR(200)", u"Code comptable pour export vers logiciels de compta"),
                                    ], # D�p�ts

    "quotients":[              ("IDquotient", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Quotient familial"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("date_debut", "DATE", u"Date de d�but de validit�"),
                                    ("date_fin", "DATE", u"Date de fin de validit�"),
                                    ("quotient", "INTEGER", u"Quotient familial"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ], # Quotients familiaux

    "caisses":[                ("IDcaisse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Caisse"),
                                    ("nom", "VARCHAR(255)", u"Nom de la caisse"),
                                    ("IDregime", "INTEGER", u"R�gime social affili�"),
                                    ], # Caisses d'allocations

    "regimes":[                ("IDregime", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID R�gime"),
                                    ("nom", "VARCHAR(255)", u"Nom du r�gime social"),
                                    ], # R�gimes sociaux

    "aides":[                    ("IDaide", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Aide"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit�"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'aide"),
                                    ("date_debut", "DATE", u"Date de d�but de validit�"),
                                    ("date_fin", "DATE", u"Date de fin de validit�"),
                                    ("IDcaisse", "INTEGER", u"ID de la caisse"),
                                    ("montant_max", "FLOAT", u"Montant maximal de l'aide"),
                                    ("nbre_dates_max", "INTEGER", u"Nbre maximal de dates"),
                                    ], # Aides journali�res

    "aides_beneficiaires":[("IDaide_beneficiaire", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID b�n�ficiaire"),
                                    ("IDaide", "INTEGER", u"ID de l'aide"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ], # B�n�ficiaires des aides journali�res

    "aides_montants":[    ("IDaide_montant", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Aide montant"),
                                    ("IDaide", "INTEGER", u"ID de l'aide"),
                                    ("montant", "FLOAT", u"Montant"),
                                    ], # Montants des aides journali�res

    "aides_combinaisons":[("IDaide_combi", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Combinaison"),
                                    ("IDaide", "INTEGER", u"ID de l'aide"),
                                    ("IDaide_montant", "INTEGER", u"ID de l'aide"),
                                    ], # Combinaisons d'unit�s pour les aides journali�res

    "aides_combi_unites":[("IDaide_combi_unite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID unit� pour Combinaison"),
                                    ("IDaide", "INTEGER", u"ID de l'aide"),
                                    ("IDaide_combi", "INTEGER", u"ID de la combinaison"),
                                    ("IDunite", "INTEGER", u"ID de l'unit�"),
                                    ], # Unit�s des combinaisons pour les aides journali�res

    "deductions":[           ("IDdeduction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID d�duction"),
                                    ("IDprestation", "INTEGER", u"ID de la prestation"),
                                    ("IDcompte_payeur", "INTEGER", u"IDcompte_payeur"),
                                    ("date", "DATE", u"Date de la d�duction"),
                                    ("montant", "FLOAT", u"Montant"),
                                    ("label", "VARCHAR(200)", u"Label de la d�duction"),
                                    ("IDaide", "INTEGER", u"ID de l'aide"),
                                    ], # D�ductions pour les prestations

    "types_cotisations":[  ("IDtype_cotisation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type cotisation"),
                                    ("nom", "VARCHAR(200)", u"Nom de la cotisation"),
                                    ("type", "VARCHAR(50)", u"Type de cotisation (individu/famille)"),
                                    ("carte", "INTEGER", u"(0/1) Est une carte d'adh�rent"),
                                    ("defaut", "INTEGER", u"(0/1) Cotisation s�lectionn�e par d�faut"),
                                    ("code_comptable", "VARCHAR(450)", u"Code comptable pour facturation et export logiciels compta"),
                                    ], # Types de cotisations

    "unites_cotisations":[ ("IDunite_cotisation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID unit� cotisation"),
                                    ("IDtype_cotisation", "INTEGER", u"ID du type de cotisation"),
                                    ("date_debut", "DATE", u"Date de d�but de validit�"),
                                    ("date_fin", "DATE", u"Date de fin de validit�"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'unit� de cotisation"),
                                    ("montant", "FLOAT", u"Montant"),
                                    ("label_prestation", "VARCHAR(200)", u"Label de la prestation"),
                                    ("defaut", "INTEGER", u"(0/1) Unit� s�lectionn�e par d�faut"),
                                    ], # Unit�s de cotisation

    "cotisations":[            ("IDcotisation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID cotisation"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDtype_cotisation", "INTEGER", u"ID du type de cotisation"),
                                    ("IDunite_cotisation", "INTEGER", u"ID de l'unit� de cotisation"),
                                    ("date_saisie", "DATE", u"Date de saisie"),
                                    ("IDutilisateur", "INTEGER", u"ID de l'utilisateur"),
                                    ("date_creation_carte", "DATE", u"Date de cr�ation de la carte"),
                                    ("numero", "VARCHAR(50)", u"Num�ro d'adh�rent"),
                                    ("IDdepot_cotisation", "INTEGER", u"ID du d�p�t des cotisations"),
                                    ("date_debut", "DATE", u"Date de d�but de validit�"),
                                    ("date_fin", "DATE", u"Date de fin de validit�"),
                                    ("IDprestation", "INTEGER", u"ID de la prestation associ�e"),
                                    ], # Cotisations

    "depots_cotisations":[("IDdepot_cotisation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID D�p�t Cotisation"),
                                    ("date", "DATE", u"Date du d�p�t"),
                                    ("nom", "VARCHAR(200)", u"Nom du d�p�t"),
                                    ("verrouillage", "INTEGER", u"(0/1) Verrouillage du d�p�t"),
                                    ("observations", "VARCHAR(1000)", u"Observations"),
                                    ], # D�p�ts de cotisations

    "parametres":[           ("IDparametre", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID parametre"),
                                    ("categorie", "VARCHAR(200)", u"Cat�gorie"),
                                    ("nom", "VARCHAR(200)", u"Nom"),
                                    ("parametre", "VARCHAR(30000)", u"Parametre"),
                                    ], # Param�tres

    "types_groupes_activites":[("IDtype_groupe_activite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type groupe activit�"),
                                    ("nom", "VARCHAR(255)", u"Nom"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ], # Types de groupes d'activit�s

    "groupes_activites":[  ("IDgroupe_activite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type groupe activit�"),
                                    ("IDtype_groupe_activite", "INTEGER", u"ID du groupe d'activit�"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit� concern�e"),
                                    ], # Groupes d'activit�s

    "secteurs":[               ("IDsecteur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID secteur g�ographique"),
                                    ("nom", "VARCHAR(255)", u"Nom du secteur g�ographique"),
                                    ], # Secteurs g�ographiques

    "types_sieste":[         ("IDtype_sieste", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID type sieste"),
                                    ("nom", "VARCHAR(255)", u"Nom du type de sieste"),
                                    ], # Types de sieste

    "factures_messages":[("IDmessage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmessage"),
                                    ("titre", "VARCHAR(255)", u"Titre du message"),
                                    ("texte", "VARCHAR(1000)", u"Contenu du message"),
                                    ], # Messages dans les factures

    "factures":[                ("IDfacture", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDfacture"),
                                    ("numero", "INTEGER", u"Num�ro de facture"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("date_edition", "DATE", u"Date d'�dition de la facture"),
                                    ("date_echeance", "DATE", u"Date d'�ch�ance de la facture"),
                                    ("activites", "VARCHAR(500)", u"Liste des IDactivit� s�par�es par ;"),
                                    ("individus", "VARCHAR(500)", u"Liste des IDindividus s�par�es par ;"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a cr�� la facture"),
                                    ("date_debut", "DATE", u"Date de d�but de p�riode"),
                                    ("date_fin", "DATE", u"Date de fin de p�riode"),
                                    ("total", "FLOAT", u"Montant total de la p�riode"),
                                    ("regle", "FLOAT", u"Montant r�gl� pour la p�riode"),
                                    ("solde", "FLOAT", u"Solde � r�gler pour la p�riode"),
                                    ("IDlot", "INTEGER", u"ID du lot de factures"),
                                    ("prestations", "VARCHAR(500)", u"Liste des types de prestations int�gr�es"),
                                    ("etat", "VARCHAR(100)", u"Etat de la facture"),
                                    ], # Factures �dit�es

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
                                    ("numero", "INTEGER", u"Num�ro du rappel"),
                                    ("IDcompte_payeur", "INTEGER", u"ID du compte payeur"),
                                    ("date_edition", "DATE", u"Date d'�dition du rappel"),
                                    ("activites", "VARCHAR(500)", u"Liste des IDactivit� s�par�es par ;"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a cr�� le rappel"),
                                    ("IDtexte", "INTEGER", u"ID du texte de rappel"),
                                    ("date_reference", "DATE", u"Date de r�f�rence"),
                                    ("solde", "FLOAT", u"Solde � r�gler"),
                                    ("date_min", "DATE", u"Date min"),
                                    ("date_max", "DATE", u"Date max"),
                                    ("IDlot", "INTEGER", u"ID du lot de rappels"),
                                    ("prestations", "VARCHAR(500)", u"Liste des types de prestations int�gr�es"),
                                    ], # Rappels �dit�s

    "utilisateurs":[            ("IDutilisateur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDutilisateur"),
                                    ("sexe", "VARCHAR(5)", u"Sexe de l'utilisateur"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'utilisateur"),
                                    ("prenom", "VARCHAR(200)", u"Pr�nom de l'utilisateur"),
                                    ("mdp", "VARCHAR(100)", u"Mot de passe"),
                                    ("profil", "VARCHAR(100)", u"Profil (Administrateur ou utilisateur)"),
                                    ("actif", "INTEGER", u"Utilisateur actif"),
                                    ("image", "VARCHAR(200)", u"Images"),
                                    ], # Utilisateurs

    "messages":[            ("IDmessage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmessage"),
                                    ("type", "VARCHAR(30)", u"Type (instantan� ou programm�)"),
                                    ("IDcategorie", "INTEGER", u"ID de la cat�gorie"),
                                    ("date_saisie", "DATE", u"Date de saisie"),
                                    ("IDutilisateur", "INTEGER", u"ID de l'utilisateur"),
                                    ("date_parution", "DATE", u"Date de parution"),
                                    ("priorite", "VARCHAR(30)", u"Priorit�"),
                                    ("afficher_accueil", "INTEGER", u"Afficher sur la page d'accueil"),
                                    ("afficher_liste", "INTEGER", u"Afficher sur la liste des conso"),
                                    ("rappel", "INTEGER", u"Rappel � l'ouverture du fichier"),
                                    ("IDfamille", "INTEGER", u"IDfamille"),
                                    ("IDindividu", "INTEGER", u"IDindividu"),
                                    ("nom", "VARCHAR(255)", u"Nom de la famille ou de l'individu"),
                                    ("texte", "VARCHAR(500)", u"Texte du message"),
                                    ("afficher_facture", "INTEGER", u"Afficher sur les factures de la famille"),
                                    ], # Messages

    "messages_categories":[("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDcategorie"),
                                    ("nom", "VARCHAR(255)", u"Nom de la cat�gorie"),
                                    ("priorite", "VARCHAR(30)", u"Priorit�"),
                                    ("afficher_accueil", "INTEGER", u"Afficher sur la page d'accueil"),
                                    ("afficher_liste", "INTEGER", u"Afficher sur la liste des conso"),
                                    ], # Cat�gories de messages

    "historique":[              ("IDaction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID de l'action"),
                                    ("date", "DATE", u"Date de l'action"),
                                    ("heure", "DATE", u"Heure de l'action"),
                                    ("IDutilisateur", "INTEGER", u"ID de l'utilisateur"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDcategorie", "INTEGER", u"ID de la cat�gorie d'action"),
                                    ("action", "VARCHAR(500)", u"Action"),
                                    ], # Historique

    "attestations":[           ("IDattestation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDattestation"),
                                    ("numero", "INTEGER", u"Num�ro d'attestation"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("date_edition", "DATE", u"Date d'�dition de l'attestation"),
                                    ("activites", "VARCHAR(450)", u"Liste des IDactivit� s�par�es par ;"),
                                    ("individus", "VARCHAR(450)", u"Liste des IDindividus s�par�es par ;"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a cr�� l'attestation"),
                                    ("date_debut", "DATE", u"Date de d�but de p�riode"),
                                    ("date_fin", "DATE", u"Date de fin de p�riode"),
                                    ("total", "FLOAT", u"Montant total de la p�riode"),
                                    ("regle", "FLOAT", u"Montant r�gl� pour la p�riode"),
                                    ("solde", "FLOAT", u"Solde � r�gler pour la p�riode"),
                                    ], # Attestation de pr�sence �dit�es

    "recus":[                   ("IDrecu", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDrecu"),
                                    ("numero", "INTEGER", u"Num�ro du recu"),
                                    ("IDfamille", "INTEGER", u"ID de la famille"),
                                    ("date_edition", "DATE", u"Date d'�dition du recu"),
                                    ("IDutilisateur", "INTEGER", u"Utilisateur qui a cr�� l'attestation"),
                                    ("IDreglement", "INTEGER", u"ID du r�glement"),
                                    ], # Recus de r�glements

    "adresses_mail":  [    ("IDadresse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("adresse", "VARCHAR(200)", u"Adresse de messagerie"),
                                    ("motdepasse", "VARCHAR(200)", u"Mot de passe si SSL"),
                                    ("smtp", "VARCHAR(200)", u"Adresse SMTP"),
                                    ("port", "INTEGER", u"Num�ro du port"),
                                    ("connexionssl", "INTEGER", u"Connexion ssl (1/0)"),
                                    ("defaut", "INTEGER", u"Adresse utilis�e par d�faut (1/0)"),
                                    ], # Adresses d'exp�diteur de mail

    "listes_diffusion":  [    ("IDliste", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("nom", "VARCHAR(200)", u"Nom de la liste de diffusion"),
                                    ], # Listes de diffusion

    "abonnements":    [    ("IDabonnement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDliste", "INTEGER", u"ID de la liste de diffusion"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu abonn�"),
                                    ], # Abonnements aux listes de diffusion

    "documents_modeles":[("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("nom", "VARCHAR(200)", u"Nom du mod�le"),
                                    ("categorie", "VARCHAR(200)", u"Cat�gorie du mod�le (ex : facture)"),
                                    ("supprimable", "INTEGER", u"Est supprimable (1/0)"),
                                    ("largeur", "INTEGER", u"Largeur en mm"),
                                    ("hauteur", "INTEGER", u"Hauteur en mm"),
                                    ("observations", "VARCHAR(400)", u"Observations"),
                                    ("IDfond", "INTEGER", u"IDfond du mod�le"),
                                    ("defaut", "INTEGER", u"Mod�le utilis� par d�faut (1/0)"),
                                    ], # Mod�les de documents

    "documents_objets":[ ("IDobjet", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDmodele", "INTEGER", u"ID du mod�le rattach�"),
                                    ("nom", "VARCHAR(200)", u"Nom de l'objet"),
                                    ("categorie", "VARCHAR(200)", u"Cat�gorie d'objet (ex : rectangle)"),
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
                                    ("verrouillageLargeur", "INTEGER", u"Hauteur verrouill�e (0/1)"),
                                    ("verrouillageHauteur", "INTEGER", u"Hauteur verrouill�e (0/1)"),
                                    ("verrouillageProportions", "INTEGER", u"Proportion verrouill�e (0/1)"),
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
                                    ("soulignePolice", "INTEGER", u"Texte soulign� (0/1)"),
                                    ("alignement", "VARCHAR(100)", u"Alignement du texte"),
                                    ("largeurTexte", "INTEGER", u"Largeur du bloc de texte"),
                                    ("norme", "VARCHAR(100)", u"Norme code-barres"),
                                    ("afficheNumero", "INTEGER", u"Affiche num�ro code-barres"),
                                    ], # Objets des mod�les de documents

    "questionnaire_categories": [("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("type", "VARCHAR(100)", u"Individu ou Famille"),
                                    ("couleur", "VARCHAR(100)", u"Couleur de la cat�gorie"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ], # Cat�gories des questionnaires

    "questionnaire_questions": [("IDquestion", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDcategorie", "INTEGER", u"ID de la cat�gorie"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ("controle", "VARCHAR(200)", u"Nom du contr�le"),
                                    ("defaut", "VARCHAR(400)", u"Valeur par d�faut"),
                                    ("options", "VARCHAR(400)", u"Options de la question"),
                                    ], # Questions des questionnaires

    "questionnaire_choix": [("IDchoix", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDquestion", "INTEGER", u"ID de la question rattach�e"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ], # Choix de r�ponses des questionnaires

    "questionnaire_reponses": [("IDreponse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDquestion", "INTEGER", u"ID de la question rattach�e"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu rattach�"),
                                    ("IDfamille", "INTEGER", u"ID de la famille rattach�e"),
                                    ("reponse", "VARCHAR(400)", u"R�ponse"),
                                    ], # R�ponses des questionnaires

    "questionnaire_filtres": [("IDfiltre", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDquestion", "INTEGER", u"ID de la question rattach�e"),
                                    ("categorie", "VARCHAR(100)", u"Cat�gorie (ex: 'TARIF')"),
                                    ("choix", "VARCHAR(400)", u"Choix (ex : 'EGAL'"),
                                    ("criteres", "VARCHAR(600)", u"Criteres (ex : '4;5')"),
                                    ("IDtarif", "INTEGER", u"IDtarif rattach�"),
                                    ], # Filtres des questionnaires

    "niveaux_scolaires":  [("IDniveau", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("nom", "VARCHAR(400)", u"Nom du niveau (ex : Cours pr�paratoire)"),
                                    ("abrege", "VARCHAR(200)", u"Abr�g� du niveau (ex : CP)"),
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
                                    ("IDecole", "INTEGER", u"ID de l'�cole"),
                                    ("nom", "VARCHAR(400)", u"Nom de la classe"),
                                    ("date_debut", "DATE", u"Date de d�but de p�riode"),
                                    ("date_fin", "DATE", u"Date de fin de p�riode"),
                                    ("niveaux", "VARCHAR(300)", u"Liste des niveaux scolaires de la classe"),  
                                    ], # Classes

    "scolarite":[               ("IDscolarite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Scolarite"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("date_debut", "DATE", u"Date de d�but de scolarit�"),
                                    ("date_fin", "DATE", u"Date de fin de scolarit�"),
                                    ("IDecole", "INTEGER", u"ID de l'�cole"),
                                    ("IDclasse", "INTEGER", u"ID de la classe"),
                                    ("IDniveau", "INTEGER", u"ID du niveau scolaire"),
                                    ], # Scolarit�

    "transports_compagnies":[("IDcompagnie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Compagnie"),
                                    ("categorie", "VARCHAR(200)", u"Cat�gorie de la compagnie (taxi,train,avion,etc...)"),
                                    ("nom", "VARCHAR(300)", u"Nom de la compagnie"),
                                    ("rue", "VARCHAR(200)", u"Rue"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(200)", u"Ville"),  
                                    ("tel", "VARCHAR(50)", u"T�l"),  
                                    ("fax", "VARCHAR(50)", u"Fax"),  
                                    ("mail", "VARCHAR(100)", u"Email"),  
                                    ], # Compagnies de transport

    "transports_lieux":[    ("IDlieu", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Lieu"),
                                    ("categorie", "VARCHAR(200)", u"Cat�gorie du lieu (gare,aeroport,port,station)"),
                                    ("nom", "VARCHAR(300)", u"Nom du lieu"),
                                    ("cp", "VARCHAR(10)", u"Code postal"),
                                    ("ville", "VARCHAR(200)", u"Ville"),  
                                    ], # Lieux pour les transports

    "transports_lignes":[   ("IDligne", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Ligne"),
                                    ("categorie", "VARCHAR(200)", u"Cat�gorie de la ligne (bus, car, m�tro, etc...)"),
                                    ("nom", "VARCHAR(300)", u"Nom de la ligne"),
                                    ], # Lignes r�guli�res pour les transports

    "transports_arrets":[   ("IDarret", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Arr�t"),
                                    ("IDligne", "INTEGER", u"ID de la ligne"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("nom", "VARCHAR(300)", u"Nom de l'arr�t"),
                                    ], # Arr�ts des lignes r�guli�res pour les transports

    "transports":[            ("IDtransport", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Transport"),
                                    ("IDindividu", "INTEGER", u"ID Individu"),
                                    ("mode", "VARCHAR(100)", u"Mode : TRANSP | PROG | MODELE"),
                                    ("categorie", "VARCHAR(100)", u"Cat�gorie du moyen de locomotion"),
                                    ("IDcompagnie", "INTEGER", u"ID Compagnie"),
                                    ("IDligne", "INTEGER", u"ID Ligne"),
                                    ("numero", "VARCHAR(200)", u"Num�ro du vol ou du train"),
                                    ("details", "VARCHAR(300)", u"D�tails"),
                                    ("observations", "VARCHAR(400)", u"Observations"),
                                    ("depart_date", "DATE", u"Date du d�part"),
                                    ("depart_heure", "DATE", u"Heure du d�part"),
                                    ("depart_IDarret", "INTEGER", u"ID Arr�t du d�part"),
                                    ("depart_IDlieu", "INTEGER", u"ID Lieu du d�part"),
                                    ("depart_localisation", "VARCHAR(400)", u"Localisation du d�part"),
                                    ("arrivee_date", "DATE", u"Date de l'arriv�e"),
                                    ("arrivee_heure", "DATE", u"Heure de l'arriv�e"),
                                    ("arrivee_IDarret", "INTEGER", u"ID Arr�t de l'arriv�e"),
                                    ("arrivee_IDlieu", "INTEGER", u"ID Lieu de l'arriv�e"),
                                    ("arrivee_localisation", "VARCHAR(400)", u"Localisation de l'arriv�e"),
                                    ("date_debut", "DATE", u"Date de d�but"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ("actif", "INTEGER", u"Actif (1/0)"),
                                    ("jours_scolaires", "VARCHAR(100)", u"Jours scolaires"),
                                    ("jours_vacances", "VARCHAR(100)", u"Jours de vacances"),
                                    ("unites", "VARCHAR(480)", u"Liste des unit�s de conso rattach�es"),
                                    ("prog", "INTEGER", u"IDtransport du mod�le de programmation"),
                                    ], # Transports

    "etat_nomin_champs":[("IDchamp", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Champ"),
                                    ("code", "VARCHAR(300)", u"Code du champ"),
                                    ("label", "VARCHAR(400)", u"Nom du champ"),
                                    ("formule", "VARCHAR(450)", u"Formule"),
                                    ("titre", "VARCHAR(400)", u"Titre"),
                                    ], # Champs personnalis�s pour Etat Caisse nominatif

    "etat_nomin_selections":[("IDselection", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID S�lection"),
                                    ("IDprofil", "VARCHAR(400)", u"Nom de profil"),
                                    ("code", "VARCHAR(300)", u"Code du champ"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ], # S�lection des Champs personnalis�s pour Etat Nominatif

    "etat_nomin_profils":[("IDprofil", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Profil"),
                                    ("label", "VARCHAR(400)", u"Nom de profil"),
                                    ], # Profils pour Etat Caisse nominatif

    "badgeage_actions":   [("IDaction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Action"),
                                    ("IDprocedure", "INTEGER", u"IDprocedure"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("condition_activite", "VARCHAR(400)", u"Activit�"),
                                    ("condition_heure", "VARCHAR(400)", u"Heure"),
                                    ("condition_periode", "VARCHAR(400)", u"P�riode"),
                                    ("condition_poste", "VARCHAR(400)", u"Poste r�seau"),
                                    ("condition_questionnaire", "VARCHAR(490)", u"Questionnaire"),
                                    ("action", "VARCHAR(400)", u"Code de l'action"),
                                    ("action_activite", "VARCHAR(450)", u"Activit�"),
                                    ("action_unite", "VARCHAR(450)", u"Unit�s"),
                                    ("action_etat", "VARCHAR(400)", u"Etat de la conso"),
                                    ("action_demande", "VARCHAR(40)", u"Demande si d�but ou fin"),
                                    ("action_heure_debut", "VARCHAR(450)", u"Heure de d�but"),
                                    ("action_heure_fin", "VARCHAR(450)", u"Heure de fin"),
                                    ("action_message", "VARCHAR(450)", u"Message unique"),
                                    ("action_icone", "VARCHAR(400)", u"Icone pour boite de dialogue"),
                                    ("action_duree", "VARCHAR(50)", u"Dur�e d'affichage du message"),
                                    ("action_frequence", "VARCHAR(450)", u"Frequence diffusion message"),
                                    ("action_vocal", "VARCHAR(400)", u"Synthese vocale activation"),
                                    ("action_question", "VARCHAR(450)", u"Question"),
                                    ("action_date", "VARCHAR(450)", u"Date � proposer"),
                                    ("action_attente", "VARCHAR(450)", u"Proposer attente"),
                                    ("action_ticket", "VARCHAR(450)", u"Impression_ticket"),
                                    ], # Badgeage : Actions

    "badgeage_messages":[("IDmessage", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Message"),
                                    ("IDprocedure", "INTEGER", u"IDprocedure"),
                                    ("IDaction", "INTEGER", u"IDaction rattach�e"),
                                    ("message", "VARCHAR(480)", u"Texte du message"),
                                    ], # Badgeage : Messages pour Actions

    "badgeage_procedures":[("IDprocedure", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Proc�dure"),
                                    ("nom", "VARCHAR(450)", u"Nom"),
                                    ("defaut", "INTEGER", u"D�faut (0/1)"),
                                    ("style", "VARCHAR(400)", u"Style interface"),
                                    ("theme", "VARCHAR(400)", u"Th�me interface"),
                                    ("image", "VARCHAR(400)", u"Image personnalis�e pour th�me"),
                                    ("systeme", "VARCHAR(400)", u"Syst�me de saisie"),
                                    ("activites", "VARCHAR(400)", u"Liste ID activites pour saisie par liste d'individus"),
                                    ("confirmation", "INTEGER", u"Confirmation identification (0/1)"),
                                    ("vocal", "INTEGER", u"Activation synth�se vocale (0/1)"),
                                    ("tutoiement", "INTEGER", u"Activation du tutoiement dans les messages (0/1)"),
                                    ], #  Badgeage : Proc�dures

    "badgeage_journal":[ ("IDaction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Action"),
                                    ("date", "DATE", u"Date de l'action"),
                                    ("heure", "VARCHAR(50)", u"Heure"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("individu", "VARCHAR(450)", u"Nom de l'individu"),
                                    ("action", "VARCHAR(450)", u"Action r�alis�e"),
                                    ("resultat", "VARCHAR(450)", u"R�sultat de l'action"),
                                    ], #  Badgeage : Journal

    "badgeage_archives":[ ("IDarchive", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Archive"),
                                    ("date_archivage", "DATE", u"Date de l'archivage"),
                                    ("codebarres", "VARCHAR(200)", u"Code-barres"),
                                    ("date", "DATE", u"Date badg�e"),
                                    ("heure", "VARCHAR(50)", u"Heure badg�e"),
                                    ], #  Badgeage : Archives des importations

    "corrections_phoniques":[("IDcorrection", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Correction"),
                                    ("mot", "VARCHAR(400)", u"Mot � corriger"),
                                    ("correction", "VARCHAR(400)", u"Correction phonique"),
                                    ], # Corrections phoniques pour la synth�se vocale

    "corrections_villes":[("IDcorrection", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Correction"),
                                    ("mode", "VARCHAR(100)", u"Mode de correction"),
                                    ("IDville", "INTEGER", u"ID ville"),
                                    ("nom", "VARCHAR(450)", u"Nom de la ville"),
                                    ("cp", "VARCHAR(100)", u"Code postal"),
                                    ], # Personnalisation des villes et codes postaux

    "modeles_emails":[ ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmodele"),
                                    ("categorie", "VARCHAR(455)", u"Cat�gorie du mod�le"),
                                    ("nom", "VARCHAR(455)", u"Nom du mod�le"),
                                    ("description", "VARCHAR(455)", u"Description du mod�le"),
                                    ("objet", "VARCHAR(455)", u"Texte objet du mail"),
                                    ("texte_xml", "VARCHAR(5000)", u"Contenu du texte version XML"),
                                    ("IDadresse", "INTEGER", u"IDadresse d'exp�dition de mails"),
                                    ("defaut", "INTEGER", u"Mod�le par d�faut (0/1)"),
                                    ], # Mod�les d'Emails

    "banques":[                ("IDbanque", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID de la banque"),
                                    ("nom", "VARCHAR(100)", u"Nom de la banque"),
                                    ("rue_resid", "VARCHAR(255)", u"Adresse de la banque"),
                                    ("cp_resid", "VARCHAR(10)", u"Code postal de la banque"),
                                    ("ville_resid", "VARCHAR(100)", u"Ville de la banque"),  
                                    ], # Les �tablissements bancaires pour le pr�l�vement automatique

    "lots_factures":[         ("IDlot", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID lot de factures"),
                                    ("nom", "VARCHAR(400)", u"Nom du lot"),
                                    ], # Lots de factures

    "lots_rappels":[         ("IDlot", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID lot de rappels"),
                                    ("nom", "VARCHAR(400)", u"Nom du lot"),
                                    ], # Lots de rappels

    "prelevements":[         ("IDprelevement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID pr�l�vement"),
                                    ("IDlot", "INTEGER", u"ID du lot de pr�l�vements"),
                                    ("IDfamille", "INTEGER", u"ID de la famille destinataire"),
                                    ("prelevement_etab", "VARCHAR(50)", u"Pr�l�vement - Code �tab"),
                                    ("prelevement_guichet", "VARCHAR(50)", u"Pr�l�vement - Code guichet"),
                                    ("prelevement_numero", "VARCHAR(50)", u"Pr�l�vement - Num�ro de compte"),
                                    ("prelevement_banque", "INTEGER", u"Pr�l�vement - ID de la Banque"),
                                    ("prelevement_cle", "VARCHAR(50)", u"Pr�l�vement - Code cl�"),
                                    ("prelevement_iban", "VARCHAR(100)", u"Pr�l�vement - Cl� IBAN"),
                                    ("prelevement_bic", "VARCHAR(100)", u"Pr�l�vement - BIC"),
                                    ("prelevement_reference_mandat", "VARCHAR(300)", u"Pr�l�vement - R�f�rence mandat"),
                                    ("prelevement_date_mandat", "DATE", u"Pr�l�vement - Date mandat"),
                                    ("titulaire", "VARCHAR(400)", u"Titulaire du compte"),
                                    ("type", "VARCHAR(400)", u"Type du pr�l�vement"),
                                    ("IDfacture", "INTEGER", u"ID de la facture"),
                                    ("libelle", "VARCHAR(400)", u"Libell� du pr�l�vement"),
                                    ("montant", "FLOAT", u"Montant du pr�l�vement"),
                                    ("statut", "VARCHAR(100)", u"Statut du pr�l�vement"),
                                    ("IDmandat", "INTEGER", u"ID du mandat"),
                                    ("sequence", "VARCHAR(100)", u"S�quence SEPA"),
                                    ], # Pr�l�vement

    "lots_prelevements":[  ("IDlot", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du lot de pr�l�vement"),
                                    ("nom", "VARCHAR(200)", u"Nom du lot de pr�l�vements"),
                                    ("date", "DATE", u"Date du pr�l�vement"),
                                    ("verrouillage", "INTEGER", u"(0/1) Verrouillage du lot"),
                                    ("IDcompte", "INTEGER", u"ID du compte cr�diteur"),
                                    ("IDmode", "INTEGER", u"ID du mode de r�glement"),
                                    ("reglement_auto", "INTEGER", u"R�glement automatique (0/1)"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("type", "VARCHAR(100)", u"Type (national ou SEPA)"),
                                    ], # Lots de pr�l�vements

    "modeles_tickets":[ ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmodele"),
                                    ("categorie", "VARCHAR(455)", u"Cat�gorie du mod�le"),
                                    ("nom", "VARCHAR(455)", u"Nom du mod�le"),
                                    ("description", "VARCHAR(455)", u"Description du mod�le"),
                                    ("lignes", "VARCHAR(5000)", u"lignes du ticket"),
                                    ("defaut", "INTEGER", u"Mod�le par d�faut (0/1)"),
                                    ("taille", "INTEGER", u"Taille de police"),
                                    ("interligne", "INTEGER", u"Hauteur d'interligne"),
                                    ("imprimante", "VARCHAR(455)", u"Nom de l'imprimante"),
                                    ], # Mod�les de tickets

    "sauvegardes_auto":[ ("IDsauvegarde", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDsauvegarde"),
                                    ("nom", "VARCHAR(455)", u"Nom de la proc�dure de sauvegarde auto"),
                                    ("observations", "VARCHAR(455)", u"Observations"),
                                    ("date_derniere", "DATE", u"Date de la derni�re sauvegarde"),
                                    ("sauvegarde_nom", "VARCHAR(455)", u"Sauvegarde Nom"),
                                    ("sauvegarde_motdepasse", "VARCHAR(455)", u"Sauvegarde mot de passe"),
                                    ("sauvegarde_repertoire", "VARCHAR(455)", u"sauvegarde R�pertoire"),
                                    ("sauvegarde_emails", "VARCHAR(455)", u"Sauvegarde Emails"),
                                    ("sauvegarde_fichiers_locaux", "VARCHAR(455)", u"Sauvegarde fichiers locaux"),
                                    ("sauvegarde_fichiers_reseau", "VARCHAR(455)", u"Sauvegarde fichiers r�seau"),
                                    ("condition_jours_scolaires", "VARCHAR(455)", u"Condition Jours scolaires"),
                                    ("condition_jours_vacances", "VARCHAR(455)", u"Condition Jours vacances"),
                                    ("condition_heure", "VARCHAR(455)", u"Condition Heure"),
                                    ("condition_poste", "VARCHAR(455)", u"Condition Poste"),
                                    ("condition_derniere", "VARCHAR(455)", u"Condition Date derni�re sauvegarde"),
                                    ("condition_utilisateur", "VARCHAR(455)", u"Condition Utilisateur"),
                                    ("option_afficher_interface", "VARCHAR(455)", u"Option Afficher interface (0/1)"),
                                    ("option_demander", "VARCHAR(455)", u"Option Demander (0/1)"),
                                    ("option_confirmation", "VARCHAR(455)", u"Option Confirmation (0/1)"),
                                    ("option_suppression", "VARCHAR(455)", u"Option Suppression sauvegardes obsol�tes"),
                                    ], # proc�dures de sauvegardes automatiques

    "droits":[                   ("IDdroit", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDdroit"),
                                    ("IDutilisateur", "INTEGER", u"IDutilisateur"),
                                    ("IDmodele", "INTEGER", u"IDmodele"),
                                    ("categorie", "VARCHAR(200)", u"Cat�gorie de droits"),
                                    ("action", "VARCHAR(200)", u"Type d'action"),
                                    ("etat", "VARCHAR(455)", u"Etat"),
                                    ], # Droits des utilisateurs

    "modeles_droits":[     ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmodele"),
                                    ("nom", "VARCHAR(455)", u"Nom du mod�le"),
                                    ("observations", "VARCHAR(455)", u"Observations"),
                                    ("defaut", "INTEGER", u"Mod�le par d�faut (0/1)"),
                                    ], # Mod�les de droits

    "mandats":[               ("IDmandat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDmandat"),
                                    ("IDfamille", "INTEGER", u"Famille rattach�e"),
                                    ("rum", "VARCHAR(100)", u"RUM du mandat"),
                                    ("type", "VARCHAR(100)", u"Type de mandat (r�current ou ponctuel)"),
                                    ("date", "DATE", u"Date de signature du mandat"),
                                    ("IDbanque", "INTEGER", u"ID de la banque"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("individu_nom", "VARCHAR(400)", u"Nom du titulaire de compte"),
                                    ("individu_rue", "VARCHAR(400)", u"Rue du titulaire de compte"),
                                    ("individu_cp", "VARCHAR(50)", u"CP du titulaire de compte"),
                                    ("individu_ville", "VARCHAR(400)", u"Ville du titulaire de compte"),
                                    ("iban", "VARCHAR(100)", u"IBAN"),
                                    ("bic", "VARCHAR(100)", u"BIC"),
                                    ("memo", "VARCHAR(450)", u"M�mo"),
                                    ("sequence", "VARCHAR(100)", u"Prochaine s�quence"),
                                    ("actif", "INTEGER", u"actif (0/1)"),
                                    ], # Mandats SEPA

    "pes_pieces":[           ("IDpiece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID piece"),
                                    ("IDlot", "INTEGER", u"ID du lot PES"),
                                    ("IDfamille", "INTEGER", u"ID de la famille destinataire"),
                                    ("prelevement", "INTEGER", u"Pr�l�vement activ� (0/1)"),
                                    ("prelevement_iban", "VARCHAR(100)", u"IBAN"),
                                    ("prelevement_bic", "VARCHAR(100)", u"BIC"),
                                    ("prelevement_rum", "VARCHAR(300)", u"R�f�rence Unique Mandat"),
                                    ("prelevement_date_mandat", "DATE", u"Date mandat"),
                                    ("prelevement_IDmandat", "INTEGER", u"ID du mandat"),
                                    ("prelevement_sequence", "VARCHAR(100)", u"S�quence SEPA"),
                                    ("prelevement_titulaire", "VARCHAR(400)", u"Titulaire du compte bancaire"),
                                    ("prelevement_statut", "VARCHAR(100)", u"Statut du pr�l�vement"),
                                    ("titulaire_helios", "INTEGER", u"Tiers Tr�sor public"),
                                    ("type", "VARCHAR(400)", u"Type du pr�l�vement"),
                                    ("IDfacture", "INTEGER", u"ID de la facture"),
                                    ("numero", "INTEGER", u"Num�ro de facture"),
                                    ("libelle", "VARCHAR(400)", u"Libell� de la pi�ce"),
                                    ("montant", "FLOAT", u"Montant du pr�l�vement"),
                                    ], # Pi�ces PESV2 ORMC

    "pes_lots":[               ("IDlot", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du lot"),
                                    ("nom", "VARCHAR(200)", u"Nom du lot"),
                                    ("verrouillage", "INTEGER", u"(0/1) Verrouillage du lot"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("reglement_auto", "INTEGER", u"R�glement automatique (0/1)"),
                                    ("IDcompte", "INTEGER", u"ID du compte cr�diteur"),
                                    ("IDmode", "INTEGER", u"ID du mode de r�glement"),
                                    ("exercice", "INTEGER", u"Exercice"),
                                    ("mois", "INTEGER", u"Num�ro de mois"),
                                    ("objet_dette", "VARCHAR(450)", u"Objet de la dette"),
                                    ("date_emission", "DATE", u"Date d'�mission"),
                                    ("date_prelevement", "DATE", u"Date du pr�l�vement"),
                                    ("date_envoi", "DATE", u"Date d'avis d'envoi"),
                                    ("id_bordereau", "VARCHAR(200)", u"Identifiant bordereau"),
                                    ("id_poste", "VARCHAR(200)", u"Poste comptable"),
                                    ("id_collectivite", "VARCHAR(200)", u"ID budget collectivit�"),
                                    ("code_collectivite", "VARCHAR(200)", u"Code Collectivit�"),
                                    ("code_budget", "VARCHAR(200)", u"Code Budget"),
                                    ("code_prodloc", "VARCHAR(200)", u"Code Produit Local"),
                                    ("prelevement_libelle", "VARCHAR(450)", u"Libell� du pr�l�vement"),
                                    ("objet_piece", "VARCHAR(450)", u"Objet de la pi�ce"),
                                    ], # Lots PESV2 ORMC

    "contrats":[               ("IDcontrat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID contrat"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu"),
                                    ("IDinscription", "INTEGER", u"ID de l'inscription"),
                                    ("date_debut", "DATE", u"Date de d�but"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ], # Contrats

    "modeles_contrats":[ ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID mod�le"),
                                    ("nom", "VARCHAR(450)", u"Nom du mod�le"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit�"),
                                    ("date_debut", "DATE", u"Date de d�but"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ("observations", "VARCHAR(500)", u"Observations"),
                                    ("IDtarif", "INTEGER", u"ID du tarif"),
                                    ("donnees", "LONGBLOB", u"Donn�es en binaire"),
                                    ], # Mod�les de contrats

    "modeles_plannings":[("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID mod�le"),
                                    ("IDactivite", "INTEGER", u"ID de l'activit�s concern�e"),
                                    ("nom", "VARCHAR(450)", u"Nom du mod�le"),
                                    ("donnees", "VARCHAR(900)", u"Donn�es serialis�es"),
                                    ], # Mod�les de plannings

    "compta_operations":[("IDoperation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID op�ration"),
                                    ("type", "VARCHAR(200)", u"Type de donn�es (debit/cr�dit)"),
                                    ("date", "DATE", u"Date de l'op�ration"),
                                    ("libelle", "VARCHAR(400)", u"Libell� de l'op�ration"),
                                    ("IDtiers", "INTEGER", u"ID du tiers"),
                                    ("IDmode", "INTEGER", u"ID du mode de r�glement"),
                                    ("num_piece", "VARCHAR(200)", u"Num�ro de pi�ce"),
                                    ("ref_piece", "VARCHAR(200)", u"R�f�rence de la pi�ce"),
                                    ("IDcompte_bancaire", "INTEGER", u"ID du compte bancaire"),
                                    ("IDreleve", "INTEGER", u"ID du relev� bancaire"),
                                    ("montant", "FLOAT", u"Montant de l'op�ration"),
                                    ("observations", "VARCHAR(450)", u"Observations"),
                                    ("IDvirement", "INTEGER", u"IDvirement associ�"),
                                    ], # Compta : Op�rations

    "compta_virements":[ ("IDvirement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID virement"),
                                    ("IDoperation_debit", "INTEGER", u"ID op�ration d�biteur"),
                                    ("IDoperation_credit", "INTEGER", u"ID op�ration cr�diteur"),
                                    ], # Compta : Virements

    "compta_ventilation":[("IDventilation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID ventilation"),
                                    ("IDoperation", "INTEGER", u"ID de l'op�ration"),
                                    ("IDexercice", "INTEGER", u"ID de l'exercice"),
                                    ("IDcategorie", "INTEGER", u"ID de la cat�gorie"),
                                    ("IDanalytique", "INTEGER", u"ID du poste analytique"),
                                    ("libelle", "VARCHAR(400)", u"Libell� de la ventilation"),
                                    ("montant", "FLOAT", u"Montant de la ventilation"),
                                    ("date_budget", "DATE", u"Date d'impact budg�taire"),
                                    ], # Compta : Ventilation des op�rations
                                    
    "compta_exercices":[("IDexercice", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Exercice"),
                                    ("nom", "VARCHAR(400)", u"Nom de l'exercice"),
                                    ("date_debut", "DATE", u"Date de d�but"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ("defaut", "INTEGER", u"D�faut (0/1)"),
                                    ], # Compta : Exercices

    "compta_analytiques":[("IDanalytique", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Analytique"),
                                    ("nom", "VARCHAR(400)", u"Nom du poste analytique"),
                                    ("abrege", "VARCHAR(200)", u"Abr�g� du poste analytique"),
                                    ("defaut", "INTEGER", u"D�faut (0/1)"),
                                    ], # Compta : Postes analytiques

    "compta_categories":[("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Cat�gorie"),
                                    ("type", "VARCHAR(200)", u"Type de donn�es (debit/cr�dit)"),
                                    ("nom", "VARCHAR(400)", u"Nom de la cat�gorie"),
                                    ("abrege", "VARCHAR(200)", u"Abr�g� de la cat�gorie"),
                                    ("journal", "VARCHAR(200)", u"Code journal"),
                                    ("IDcompte", "INTEGER", u"ID du compte comptable"),
                                    ], # Compta : Cat�gories de ventilation

    "compta_comptes_comptables":[("IDcompte", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDcompte"),
                                    ("numero", "VARCHAR(200)", u"Num�ro"),
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
                                    ("analytiques", "VARCHAR(450)", u"Liste des postes analytiques associ�s"),
                                    ("date_debut", "DATE", u"Date de d�but de p�riode"),
                                    ("date_fin", "DATE", u"Date de fin de p�riode"),
                                    ], # Compta : Budgets

    "compta_categories_budget":[("IDcategorie_budget", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Categorie budget"),
                                    ("IDbudget", "INTEGER", u"ID du budget"),
                                    ("type", "VARCHAR(200)", u"Type de donn�es (debit/cr�dit)"),
                                    ("IDcategorie", "INTEGER", u"ID de la cat�gorie rattach�e"),
                                    ("valeur", "VARCHAR(450)", u"Valeur ou formule"),
                                    ], # Compta : Cat�gories de budget

    "compta_releves":   [("IDreleve", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Relev�"),
                                    ("nom", "VARCHAR(400)", u"Nom du relev�"),
                                    ("date_debut", "DATE", u"Date de d�but"),
                                    ("date_fin", "DATE", u"Date de fin"),
                                    ("IDcompte_bancaire", "INTEGER", u"ID du compte bancaire"),
                                    ], # Compta : Relev�s de comptes

    "compta_operations_budgetaires":[("IDoperation_budgetaire", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID op�ration budg�taire"),
                                    ("type", "VARCHAR(200)", u"Type de donn�es (debit/cr�dit)"),
                                    ("date_budget", "DATE", u"Date d'impact budg�taire"),
                                    ("IDcategorie", "INTEGER", u"ID de la cat�gorie"),
                                    ("IDanalytique", "INTEGER", u"ID du poste analytique"),
                                    ("libelle", "VARCHAR(400)", u"Libell� de la ventilation"),
                                    ("montant", "FLOAT", u"Montant de la ventilation"),
                                    ], # Compta : Ventilation des op�rations

    "nomade_archivage":  [("IDarchive", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID Archive"),
                                    ("nom_fichier", "VARCHAR(400)", u"Nom du fichier"),
                                    ("ID_appareil", "VARCHAR(100)", u"ID de l'appareil"),
                                    ("date", "DATE", u"Date de l'archivage"),
                                    ], # Synchronisation Nomadhys : Archivage des fichiers


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
                                    ("IDpiece", "INTEGER", u"ID de la pi�ce"),
                                    ("IDreponse", "INTEGER", u"ID de la r�ponse du Questionnaire"),
                                    ("document", "LONGBLOB", u"Document converti en binaire"),
                                    ("type", "VARCHAR(50)", u"Type de document : jpeg, pdf..."),
                                    ("label", "VARCHAR(400)", u"Label du document"),
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

    }






if __name__ == "__main__":
    """ Affichage de stats sur les tables """
    nbreChamps = 0
    for nomTable, listeChamps in DB_DATA.iteritems() :
        nbreChamps += len(listeChamps)
    print "Nbre de champs DATA =", nbreChamps
    print "Nbre de tables DATA =", len(DB_DATA.keys())