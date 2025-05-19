#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import datetime
from Data import DATA_Tables as Tables
import GestionDB



class DB(GestionDB.DB):
    def __init__(self, *args, **kwds):
        GestionDB.DB.__init__(self, *args, **kwds)

    def Upgrade(self, versionFichier=(0, 0, 0, 0) ) :
        """ Adapte un fichier obsolète à la version actuelle du logiciel """

        # Filtres de conversion

        # =============================================================
        
        versionFiltre = (1, 0, 1, 1)
        if versionFichier < versionFiltre :   
            try :
                self.CreationTable("historique", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 1, 2)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("historique") == False :
                    self.CreationTable("historique", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 1, 3)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("attestations") == False :
                    self.CreationTable("attestations", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 1, 7)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("recus") == False :
                    self.CreationTable("recus", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 2, 1)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("adresses_mail") == False :
                    self.CreationTable("adresses_mail", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
                
        versionFiltre = (1, 0, 3, 3)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("listes_diffusion") == False : self.CreationTable("listes_diffusion", Tables.DB_DATA)
                if self.IsTableExists("abonnements") == False : self.CreationTable("abonnements", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
                
        versionFiltre = (1, 0, 3, 9)
        if versionFichier < versionFiltre :   
            try :
                self.SupprChamp("tarifs_lignes", "heure_max")
                self.SupprChamp("tarifs_lignes", "heure_min")
                self.AjoutChamp("tarifs_lignes", "heure_debut_min", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "heure_debut_max", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "heure_fin_min", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "heure_fin_max", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "duree_min", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "duree_max", "VARCHAR(10)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 4, 2)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("tarifs_lignes", "date", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "label", "VARCHAR(300)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 4, 6)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("documents_modeles") == False : self.CreationTable("documents_modeles", Tables.DB_DATA)
                if self.IsTableExists("documents_objets") == False : self.CreationTable("documents_objets", Tables.DB_DATA)
                self.Importation_valeurs_defaut([[u"", ("documents_modeles", "documents_objets"), True],])
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 4, 8)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("prestations", "temps_facture", "VARCHAR(10)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 4, 9)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("tarifs_lignes", "temps_facture", "VARCHAR(10)")
                self.AjoutChamp("tarifs", "categories_tarifs", "VARCHAR(300)")
                self.AjoutChamp("tarifs", "groupes", "VARCHAR(300)")
                self.AjoutChamp("prestations", "IDcategorie_tarif", "INTEGER")
                from Utils import UTILS_Procedures
                UTILS_Procedures.S1290()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 5, 1)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("questionnaire_questions") == False : self.CreationTable("questionnaire_questions", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_categories") == False : self.CreationTable("questionnaire_categories", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_choix") == False : self.CreationTable("questionnaire_choix", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_reponses") == False : self.CreationTable("questionnaire_reponses", Tables.DB_DATA)
                if self.isNetwork == True :
                    typeChamp = "TEXT(2000)"
                else:
                    typeChamp = "VARCHAR(2000)"
                self.AjoutChamp("familles", "memo", typeChamp)
                from Utils import UTILS_Procedures
                UTILS_Procedures.D1051()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 0, 5, 3)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("tarifs_lignes", "unite_horaire", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "duree_seuil", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "duree_plafond", "VARCHAR(10)")
                self.AjoutChamp("tarifs_lignes", "taux", "FLOAT")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 5, 4)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("tarifs_lignes", "ajustement", "FLOAT")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 5, 5)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("niveaux_scolaires") == False : self.CreationTable("niveaux_scolaires", Tables.DB_DATA)
                if self.IsTableExists("ecoles") == False : self.CreationTable("ecoles", Tables.DB_DATA)
                if self.IsTableExists("classes") == False : self.CreationTable("classes", Tables.DB_DATA)
                if self.IsTableExists("scolarite") == False : self.CreationTable("scolarite", Tables.DB_DATA)
                self.Importation_valeurs_defaut([[u"", ("niveaux_scolaires",), True],])
                self.AjoutChamp("unites_remplissage", "heure_min", "VARCHAR(10)")
                self.AjoutChamp("unites_remplissage", "heure_max", "VARCHAR(10)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 5, 9)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("combi_tarifs", "quantite_max", "INTEGER")
                self.AjoutChamp("tarifs", "forfait_duree", "VARCHAR(50)")
                self.AjoutChamp("tarifs", "forfait_beneficiaire", "VARCHAR(50)")
                self.AjoutChamp("prestations", "forfait_date_debut", "VARCHAR(10)")
                self.AjoutChamp("prestations", "forfait_date_fin", "VARCHAR(10)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 6, 6)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("transports_compagnies") == False : self.CreationTable("transports_compagnies", Tables.DB_DATA)
                if self.IsTableExists("transports_lieux") == False : self.CreationTable("transports_lieux", Tables.DB_DATA)
                if self.IsTableExists("transports_lignes") == False : self.CreationTable("transports_lignes", Tables.DB_DATA)
                if self.IsTableExists("transports_arrets") == False : self.CreationTable("transports_arrets", Tables.DB_DATA)
                if self.IsTableExists("transports") == False : self.CreationTable("transports", Tables.DB_DATA)
                self.AjoutChamp("tarifs", "cotisations", "VARCHAR(300)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 6, 7)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("groupes", "abrege", "VARCHAR(100)")
                self.AjoutChamp("groupes", "ordre", "INTEGER")
                from Utils import UTILS_Procedures
                UTILS_Procedures.G2345()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 6, 8)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("questionnaire_filtres") == False : self.CreationTable("questionnaire_filtres", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 6, 9)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("organisateur", "gps", "VARCHAR(200)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 0)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("familles", "allocataire", "INTEGER")
                if self.IsTableExists("etat_nomin_champs") == False : self.CreationTable("etat_nomin_champs", Tables.DB_DATA)
                if self.IsTableExists("etat_nomin_selections") == False : self.CreationTable("etat_nomin_selections", Tables.DB_DATA)
                if self.IsTableExists("etat_nomin_profils") == False : self.CreationTable("etat_nomin_profils", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 2)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("tarifs", "caisses", "VARCHAR(300)")
                self.AjoutChamp("tarifs", "description", "VARCHAR(450)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 5)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("tarifs", "jours_scolaires", "VARCHAR(100)")
                self.AjoutChamp("tarifs", "jours_vacances", "VARCHAR(100)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 6)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("badgeage_actions") == False : self.CreationTable("badgeage_actions", Tables.DB_DATA)
                if self.IsTableExists("badgeage_messages") == False : self.CreationTable("badgeage_messages", Tables.DB_DATA)
                if self.IsTableExists("badgeage_procedures") == False : self.CreationTable("badgeage_procedures", Tables.DB_DATA)
                if self.IsTableExists("badgeage_journal") == False : self.CreationTable("badgeage_journal", Tables.DB_DATA)
                if self.IsTableExists("corrections_phoniques") == False : self.CreationTable("corrections_phoniques", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 8)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("consommations", "quantite", "INTEGER")
                self.AjoutChamp("documents_objets", "norme", "VARCHAR(100)")
                self.AjoutChamp("documents_objets", "afficheNumero", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 7, 9)
        if versionFichier < versionFiltre :
            try :
                if self.isNetwork == True :
                    self.ExecuterReq("ALTER TABLE documents_objets MODIFY COLUMN image LONGBLOB;")
                    self.Commit()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 0, 8, 0)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("corrections_villes") == False : self.CreationTable("corrections_villes", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 2)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("tarifs", "options", "VARCHAR(450)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 4)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("badgeage_archives") == False : self.CreationTable("badgeage_archives", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 6)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("messages", "afficher_facture", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 7)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("modeles_emails") == False : self.CreationTable("modeles_emails", Tables.DB_DATA)
                self.AjoutChamp("prestations", "reglement_frais", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 8)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("banques") == False : self.CreationTable("banques", Tables.DB_DATA)
                if self.IsTableExists("lots_factures") == False : self.CreationTable("lots_factures", Tables.DB_DATA)
                if self.IsTableExists("lots_rappels") == False : self.CreationTable("lots_rappels", Tables.DB_DATA)
                self.AjoutChamp("factures", "IDlot", "INTEGER")
                self.AjoutChamp("factures", "prestations", "VARCHAR(500)")
                self.AjoutChamp("rappels", "IDlot", "INTEGER")
                self.AjoutChamp("rappels", "prestations", "VARCHAR(500)")
                self.AjoutChamp("rappels", "date_min", "DATE")
                self.AjoutChamp("rappels", "date_max", "DATE")
                self.AjoutChamp("familles", "prelevement_activation", "INTEGER")
                self.AjoutChamp("familles", "prelevement_etab", "VARCHAR(50)")
                self.AjoutChamp("familles", "prelevement_guichet", "VARCHAR(50)")
                self.AjoutChamp("familles", "prelevement_numero", "VARCHAR(50)")
                self.AjoutChamp("familles", "prelevement_cle", "VARCHAR(50)")
                self.AjoutChamp("familles", "prelevement_banque", "INTEGER")
                self.AjoutChamp("familles", "prelevement_individu", "INTEGER")
                self.AjoutChamp("familles", "prelevement_nom", "VARCHAR(200)")
                self.AjoutChamp("familles", "prelevement_rue", "VARCHAR(400)")
                self.AjoutChamp("familles", "prelevement_cp", "VARCHAR(50)")
                self.AjoutChamp("familles", "prelevement_ville", "VARCHAR(400)") 
                self.AjoutChamp("familles", "email_factures", "VARCHAR(450)") 

            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 8, 9)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("prelevements") == False : self.CreationTable("prelevements", Tables.DB_DATA)
                if self.IsTableExists("lots_prelevements") == False : self.CreationTable("lots_prelevements", Tables.DB_DATA)
                self.AjoutChamp("comptes_bancaires", "raison", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "code_etab", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "code_guichet", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "code_nne", "VARCHAR(400)")
                self.AjoutChamp("reglements", "IDprelevement", "INTEGER")

            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)


        # =============================================================

        versionFiltre = (1, 0, 9, 0)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("tarifs", "observations", "VARCHAR(450)")
                self.AjoutChamp("tarifs", "tva", "FLOAT")
                self.AjoutChamp("tarifs", "code_compta", "VARCHAR(200)")
                self.AjoutChamp("prestations", "tva", "FLOAT")
                self.AjoutChamp("prestations", "code_compta", "VARCHAR(200)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 9, 1)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("combi_tarifs", "IDgroupe", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 9, 3)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("modeles_tickets") == False : self.CreationTable("modeles_tickets", Tables.DB_DATA)
                self.AjoutChamp("badgeage_actions", "action_ticket", "VARCHAR(450)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 0, 9, 4)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("modeles_tickets", "taille", "INTEGER")
                self.AjoutChamp("modeles_tickets", "interligne", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 0, 0)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("modeles_tickets", "imprimante", "VARCHAR(450)")
                self.AjoutChamp("unites", "largeur", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 0, 1)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("unites_remplissage", "afficher_page_accueil", "INTEGER")
                self.AjoutChamp("unites_remplissage", "afficher_grille_conso", "INTEGER")
                self.AjoutChamp("tarifs", "date_facturation", "VARCHAR(450)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 0, 2)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("activites", "nbre_inscrits_max", "INTEGER")
                self.AjoutChamp("familles", "email_recus", "VARCHAR(450)")
                self.AjoutChamp("familles", "email_depots", "VARCHAR(450)")
                self.AjoutChamp("reglements", "avis_depot", "DATE")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 0, 6)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("sauvegardes_auto") == False : self.CreationTable("sauvegardes_auto", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 0, 8)
        if versionFichier < versionFiltre :
            try :
                from Utils import UTILS_Procedures
                UTILS_Procedures.A5300()
                UTILS_Procedures.A5400()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 1, 1)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("comptes_bancaires", "cle_rib", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "cle_iban", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "iban", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "bic", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "code_ics", "VARCHAR(400)")
                self.AjoutChamp("familles", "prelevement_cle_iban", "VARCHAR(10)")
                self.AjoutChamp("familles", "prelevement_iban", "VARCHAR(100)")
                self.AjoutChamp("familles", "prelevement_bic", "VARCHAR(100)")
                self.AjoutChamp("familles", "prelevement_reference_mandat", "VARCHAR(300)")
                self.AjoutChamp("familles", "prelevement_date_mandat", "DATE")
                self.AjoutChamp("familles", "prelevement_memo", "VARCHAR(450)")
                self.AjoutChamp("prelevements", "prelevement_iban", "VARCHAR(100)")
                self.AjoutChamp("prelevements", "prelevement_bic", "VARCHAR(100)")
                self.AjoutChamp("prelevements", "prelevement_reference_mandat", "VARCHAR(300)")
                self.AjoutChamp("prelevements", "prelevement_date_mandat", "DATE")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 1, 3)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("droits") == False : self.CreationTable("droits", Tables.DB_DATA)
                if self.IsTableExists("modeles_droits") == False : self.CreationTable("modeles_droits", Tables.DB_DATA)
                if self.IsTableExists("mandats") == False : self.CreationTable("mandats", Tables.DB_DATA)
                self.AjoutChamp("lots_prelevements", "type", "VARCHAR(100)")
                self.AjoutChamp("prelevements", "IDmandat", "INTEGER")
                self.AjoutChamp("prelevements", "sequence", "VARCHAR(100)")
                self.AjoutChamp("utilisateurs", "image", "VARCHAR(200)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 1, 4)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("pes_pieces") == False : self.CreationTable("pes_pieces", Tables.DB_DATA)
                if self.IsTableExists("pes_lots") == False : self.CreationTable("pes_lots", Tables.DB_DATA)
                self.AjoutChamp("reglements", "IDpiece", "INTEGER")
                self.AjoutChamp("familles", "titulaire_helios", "INTEGER")
                self.AjoutChamp("familles", "code_comptable", "VARCHAR(450)")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A7650() # Création auto des titulaires Hélios
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 1, 5)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("pes_lots", "prelevement_libelle", "VARCHAR(450)")
                self.AjoutChamp("modes_reglements", "type_comptable", "VARCHAR(200)")
                self.AjoutChamp("activites", "code_comptable", "VARCHAR(450)")
                self.AjoutChamp("types_cotisations", "code_comptable", "VARCHAR(450)")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A8120() # Création auto type_comptable dans table modes_règlements
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 1, 6)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("pes_lots", "objet_piece", "VARCHAR(450)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 2, 2)
        if versionFichier < versionFiltre :
            try :
                from Utils import UTILS_Export_documents
                UTILS_Export_documents.ImporterDepuisFichierDefaut(IDmodele=12, nom=None, IDfond=0, defaut=1) # import modèle doc reçu don aux oeuvres
                UTILS_Export_documents.ImporterDepuisFichierDefaut(IDmodele=13, nom=None, IDfond=1, defaut=1) # import modèle doc attestation fiscale
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 2, 3)
        if versionFichier < versionFiltre :
            try :
                from Utils import UTILS_Procedures
                UTILS_Procedures.A8260() 
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 2, 7)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("unites", "coeff", "VARCHAR(50)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 2, 8)
        if versionFichier < versionFiltre :   
            try :
                if self.isNetwork == True :
                    self.ExecuterReq("ALTER TABLE parametres MODIFY COLUMN parametre TEXT;")
                    self.Commit()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 2, 9)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("modes_reglements", "code_compta", "VARCHAR(200)")
                self.AjoutChamp("depots", "code_compta", "VARCHAR(200)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 3, 5)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("tarifs_lignes", "montant_questionnaire", "INTEGER")
                self.AjoutChamp("prestations", "IDcontrat", "INTEGER")
                if self.IsTableExists("contrats") == False : self.CreationTable("contrats", Tables.DB_DATA) 
                if self.IsTableExists("modeles_contrats") == False : self.CreationTable("modeles_contrats", Tables.DB_DATA)
                if self.IsTableExists("modeles_plannings") == False : self.CreationTable("modeles_plannings", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 3, 6)
        if versionFichier < versionFiltre :   
            try :
                if self.isNetwork == True :
                    self.ExecuterReq("ALTER TABLE parametres MODIFY COLUMN parametre MEDIUMTEXT;")
                    self.Commit()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 3, 9)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("compta_operations") == False : self.CreationTable("compta_operations", Tables.DB_DATA) 
                if self.IsTableExists("compta_virements") == False : self.CreationTable("compta_virements", Tables.DB_DATA) 
                if self.IsTableExists("compta_ventilation") == False : self.CreationTable("compta_ventilation", Tables.DB_DATA) 
                if self.IsTableExists("compta_exercices") == False : self.CreationTable("compta_exercices", Tables.DB_DATA) 
                if self.IsTableExists("compta_analytiques") == False : self.CreationTable("compta_analytiques", Tables.DB_DATA) 
                if self.IsTableExists("compta_categories") == False : self.CreationTable("compta_categories", Tables.DB_DATA) 
                if self.IsTableExists("compta_comptes_comptables") == False : self.CreationTable("compta_comptes_comptables", Tables.DB_DATA) 
                if self.IsTableExists("compta_tiers") == False : self.CreationTable("compta_tiers", Tables.DB_DATA) 
                if self.IsTableExists("compta_budgets") == False : self.CreationTable("compta_budgets", Tables.DB_DATA) 
                if self.IsTableExists("compta_categories_budget") == False : self.CreationTable("compta_categories_budget", Tables.DB_DATA) 
                if self.IsTableExists("compta_releves") == False : self.CreationTable("compta_releves", Tables.DB_DATA) 
                try :
                    self.Importation_valeurs_defaut([[u"", ("compta_comptes_comptables",), True],])
                except :
                    print("Table 'compta_comptes_comptables' impossible a remplir : Elle a deja ete remplie !")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 4, 0)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("familles", "idtiers_helios", "VARCHAR(200)")
                self.AjoutChamp("familles", "natidtiers_helios", "INTEGER")
                self.AjoutChamp("familles", "reftiers_helios", "VARCHAR(200)")
                self.AjoutChamp("familles", "cattiers_helios", "INTEGER")
                self.AjoutChamp("familles", "natjur_helios", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 4, 2)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("compta_ventilation", "date_budget", "DATE")
                if self.IsTableExists("compta_operations_budgetaires") == False : self.CreationTable("compta_operations_budgetaires", Tables.DB_DATA) 
                self.AjoutChamp("compta_budgets", "date_debut", "DATE")
                self.AjoutChamp("compta_budgets", "date_fin", "DATE")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A8623() 
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 4, 4)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("nomade_archivage") == False : self.CreationTable("nomade_archivage", Tables.DB_DATA) 
                from Utils import UTILS_Procedures
                UTILS_Procedures.A8733() 
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 4, 9)
        if versionFichier < versionFiltre :   
            try :
                from Utils import UTILS_Procedures
                UTILS_Procedures.A8823() 
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 5, 0)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("factures", "etat", "VARCHAR(100)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 5, 1)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("cotisations", "observations", "VARCHAR(1000)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (1, 1, 5, 2)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("cotisations", "activites", "VARCHAR(450)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 5, 4)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("etiquettes") == False : self.CreationTable("etiquettes", Tables.DB_DATA) 
                self.AjoutChamp("consommations", "etiquettes", "VARCHAR(100)")
                self.AjoutChamp("tarifs", "etiquettes", "VARCHAR(450)")
                self.AjoutChamp("tarifs", "etats", "VARCHAR(150)")
                self.AjoutChamp("unites_remplissage", "etiquettes", "VARCHAR(450)")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A8941() 
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 5, 5)
        if versionFichier < versionFiltre :   
            try :
                self.AjoutChamp("etiquettes", "active", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (1, 1, 5, 7)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("unites", "autogen_active", "INTEGER")
                self.AjoutChamp("unites", "autogen_conditions", "VARCHAR(400)")
                self.AjoutChamp("unites", "autogen_parametres", "VARCHAR(400)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 5, 8)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("familles", "autorisation_cafpro", "INTEGER")
                self.AjoutChamp("quotients", "revenu", "FLOAT")
                self.AjoutChamp("tarifs_lignes", "revenu_min", "FLOAT")
                self.AjoutChamp("tarifs_lignes", "revenu_max", "FLOAT")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 5, 9)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("contrats", "IDactivite", "INTEGER")
                self.AjoutChamp("contrats", "type", "VARCHAR(100)")
                self.AjoutChamp("contrats", "nbre_absences_prevues", "INTEGER")
                self.AjoutChamp("contrats", "nbre_heures_regularisation", "INTEGER")
                if self.IsTableExists("contrats_tarifs") == False : self.CreationTable("contrats_tarifs", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 6, 1)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("contrats", "arrondi_type", "VARCHAR(50)")
                self.AjoutChamp("contrats", "arrondi_delta", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 6, 2)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("activites", "psu_activation", "INTEGER")
                self.AjoutChamp("activites", "psu_unite_prevision", "INTEGER")
                self.AjoutChamp("activites", "psu_unite_presence", "INTEGER")
                self.AjoutChamp("activites", "psu_tarif_forfait", "INTEGER")
                self.AjoutChamp("activites", "psu_etiquette_rtt", "INTEGER")
                self.AjoutChamp("contrats", "duree_absences_prevues", "VARCHAR(50)")
                self.AjoutChamp("contrats", "duree_heures_regularisation", "VARCHAR(50)")
                self.AjoutChamp("contrats", "duree_tolerance_depassement", "VARCHAR(50)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 6, 4)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("adresses_mail", "connexionAuthentifiee", "INTEGER")
                self.AjoutChamp("adresses_mail", "startTLS", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 6, 5)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("contrats", "planning", "VARCHAR(900)")
                self.AjoutChamp("groupes", "nbre_inscrits_max", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 6, 6)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("types_quotients") == False : self.CreationTable("types_quotients", Tables.DB_DATA)
                self.AjoutChamp("quotients", "IDtype_quotient", "INTEGER")
                self.AjoutChamp("tarifs", "IDtype_quotient", "INTEGER")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A8971()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 6, 7)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("factures_prefixes") == False : self.CreationTable("factures_prefixes", Tables.DB_DATA)
                self.AjoutChamp("factures", "IDprefixe", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)


        # =============================================================

        versionFiltre = (1, 1, 7, 1)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("portail_periodes") == False : self.CreationTable("portail_periodes", Tables.DB_DATA)
                if self.IsTableExists("portail_unites") == False : self.CreationTable("portail_unites", Tables.DB_DATA)
                self.AjoutChamp("activites", "portail_inscriptions_affichage", "INTEGER")
                self.AjoutChamp("activites", "portail_inscriptions_date_debut", "DATETIME")
                self.AjoutChamp("activites", "portail_inscriptions_date_fin", "DATETIME")
                self.AjoutChamp("activites", "portail_reservations_affichage", "INTEGER")
                self.AjoutChamp("activites", "portail_reservations_limite", "VARCHAR(20)")
                self.AjoutChamp("activites", "portail_reservations_absenti", "VARCHAR(20)")
                self.AjoutChamp("activites", "portail_unites_multiples", "INTEGER")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9001()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 7, 2)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("portail_actions") == False : self.CreationTable("portail_actions", Tables.DB_DATA)
                if self.IsTableExists("portail_reservations") == False : self.CreationTable("portail_reservations", Tables.DB_DATA)
                self.AjoutChamp("activites", "portail_reservations_limite", "VARCHAR(20)")
                self.AjoutChamp("activites", "portail_reservations_absenti", "VARCHAR(20)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 7, 7)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("portail_actions", "reponse", "VARCHAR(450)")
                self.AjoutChamp("portail_reservations", "etat", "INTEGER")
                if self.IsTableExists("portail_messages") == False : self.CreationTable("portail_messages", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 7, 8)
        if versionFichier < versionFiltre :
            try :
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9054()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 7, 9)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("portail_periodes", "IDmodele", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 8, 0)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("portail_actions", "email_date", "DATE")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 8, 1)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("organisateur", "logo_update", "VARCHAR(50)")
                self.ReqMAJ("organisateur", [("logo_update", datetime.datetime.now()), ], "IDorganisateur", 1)
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9061()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 8, 2)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("portail_periodes", "introduction", "VARCHAR(1000)")
                self.AjoutChamp("portail_messages", "affichage_date_debut", "DATETIME")
                self.AjoutChamp("portail_messages", "affichage_date_fin", "DATETIME")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 8, 7)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("utilisateurs", "mdpcrypt", "VARCHAR(200)")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9074()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 9, 0)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("prestations", "date_valeur", "DATE")
                self.ExecuterReq('UPDATE prestations SET date_valeur = date;')
                self.Commit()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 9, 1)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("tarifs", "label_prestation", "VARCHAR(300)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 9, 3)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("profils") == False: self.CreationTable("profils", Tables.DB_DATA)
                if self.IsTableExists("profils_parametres") == False: self.CreationTable("profils_parametres", Tables.DB_DATA)
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 9, 4)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("profils") == False: self.CreationTable("profils", Tables.DB_DATA)
                if self.IsTableExists("profils_parametres") == False: self.CreationTable("profils_parametres", Tables.DB_DATA)
                self.AjoutChamp("profils", "defaut", "INTEGER")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 9, 7)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("inscriptions", "date_desinscription", "DATE")
                self.ReqMAJ("inscriptions", [("date_desinscription", datetime.date.today()), ], "parti", 1)
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 1, 9, 8)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("aides", "jours_scolaires", "VARCHAR(50)")
                self.AjoutChamp("aides", "jours_vacances", "VARCHAR(50)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 0, 0)
        if versionFichier < versionFiltre:
            try:
                if self.isNetwork == True:
                    self.ExecuterReq("ALTER TABLE modeles_emails MODIFY COLUMN texte_xml MEDIUMTEXT;")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 0, 1)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("factures", "IDregie", "INTEGER")
                self.AjoutChamp("activites", "regie", "INTEGER")
                if self.IsTableExists("factures_regies") == False: self.CreationTable("factures_regies", Tables.DB_DATA)
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 0, 2)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("messages", "rappel_famille", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 0, 3)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("adresses_mail", "utilisateur", "VARCHAR(200)")
                self.ExecuterReq('UPDATE adresses_mail SET utilisateur = adresse WHERE connexionAuthentifiee = 1;')
                self.Commit()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 0, 4)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("familles", "autre_adresse_facturation", "VARCHAR(450)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)


        # =============================================================

        versionFiltre = (1, 2, 0, 6)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("unites_cotisations", "duree", "VARCHAR(100)")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 0, 9)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("evenements") == False: self.CreationTable("evenements", Tables.DB_DATA)
                if self.IsTableExists("modeles_prestations") == False: self.CreationTable("modeles_prestations", Tables.DB_DATA)
                self.AjoutChamp("consommations", "IDevenement", "INTEGER")
                self.AjoutChamp("unites_remplissage", "largeur", "INTEGER")
                self.AjoutChamp("tarifs", "IDevenement", "INTEGER")
                self.AjoutChamp("tarifs_lignes", "IDmodele", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 1, 0)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("produits_categories") == False: self.CreationTable("produits_categories", Tables.DB_DATA)
                if self.IsTableExists("produits") == False: self.CreationTable("produits", Tables.DB_DATA)
                if self.IsTableExists("locations") == False: self.CreationTable("locations", Tables.DB_DATA)
                if self.IsTableExists("locations_demandes") == False: self.CreationTable("locations_demandes", Tables.DB_DATA)
                self.AjoutChamp("questionnaire_reponses", "type", "VARCHAR(100)")
                self.AjoutChamp("questionnaire_reponses", "IDdonnee", "INTEGER")
                self.AjoutChamp("questionnaire_filtres", "IDdonnee", "INTEGER")
                self.AjoutChamp("documents_objets", "IDdonnee", "INTEGER")
                self.AjoutChamp("documents_modeles", "IDdonnee", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 1, 1)
        if versionFichier < versionFiltre :
            try :
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9078()
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 1, 5)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("adresses_mail", "nom_adresse", "VARCHAR(200)")
                self.AjoutChamp("individus", "travail_tel_sms", "INTEGER")
                self.AjoutChamp("individus", "tel_domicile_sms", "INTEGER")
                self.AjoutChamp("individus", "tel_mobile_sms", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 1, 6)
        if versionFichier < versionFiltre :
            try :
                self.AjoutChamp("produits", "quantite", "INTEGER")
                self.AjoutChamp("produits", "montant", "FLOAT")
                self.AjoutChamp("tarifs", "IDproduit", "INTEGER")
                self.AjoutChamp("locations", "quantite", "INTEGER")
                self.AjoutChamp("prestations", "IDdonnee", "INTEGER")
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 1, 8)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("portail_renseignements") == False: self.CreationTable("portail_renseignements", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 2, 1)
        if versionFichier < versionFiltre :
            try :
                if self.IsTableExists("periodes_gestion") == False: self.CreationTable("periodes_gestion", Tables.DB_DATA)
            except Exception as err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 2, 4)
        if versionFichier < versionFiltre:
            try:
                if self.isNetwork == True:
                    self.ExecuterReq("ALTER TABLE activites MODIFY COLUMN portail_reservations_limite VARCHAR(100);")
                    self.ExecuterReq("ALTER TABLE activites MODIFY COLUMN portail_reservations_absenti VARCHAR(100);")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 2, 7)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("categories_medicales") == False: self.CreationTable("categories_medicales", Tables.DB_DATA)
                self.Importation_valeurs_defaut([[u"", ("categories_medicales",), True], ])
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9081()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 2, 8)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("modeles_commandes") == False: self.CreationTable("modeles_commandes", Tables.DB_DATA)
                if self.IsTableExists("modeles_commandes_colonnes") == False: self.CreationTable("modeles_commandes_colonnes", Tables.DB_DATA)
                if self.IsTableExists("commandes") == False: self.CreationTable("commandes", Tables.DB_DATA)
                if self.IsTableExists("commandes_valeurs") == False: self.CreationTable("commandes_valeurs", Tables.DB_DATA)
                self.AjoutChamp("messages", "afficher_commande", "INTEGER")
                # Importation du modèle d'emails 'Commande de repas'
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9054()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 3, 6)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("portail_pages") == False: self.CreationTable("portail_pages", Tables.DB_DATA)
                if self.IsTableExists("portail_blocs") == False: self.CreationTable("portail_blocs", Tables.DB_DATA)
                if self.IsTableExists("portail_elements") == False: self.CreationTable("portail_elements", Tables.DB_DATA)
                self.Importation_valeurs_defaut([[u"", ("portail_elements",), True], ])
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 3, 7)
        if versionFichier < versionFiltre:
            try:
                if self.isNetwork == True:
                    self.ExecuterReq("ALTER TABLE familles MODIFY COLUMN internet_identifiant VARCHAR(300);")
                    self.ExecuterReq("ALTER TABLE familles MODIFY COLUMN internet_mdp VARCHAR(300);")
                self.AjoutChamp("utilisateurs", "internet_actif", "INTEGER")
                self.AjoutChamp("utilisateurs", "internet_identifiant", "VARCHAR(300)")
                self.AjoutChamp("utilisateurs", "internet_mdp", "VARCHAR(300)")
                self.AjoutChamp("portail_actions", "IDutilisateur", "INTEGER")
                from Utils import UTILS_Internet
                UTILS_Internet.InitCodesUtilisateurs()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 3, 8)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("menus") == False: self.CreationTable("menus", Tables.DB_DATA)
                if self.IsTableExists("menus_categories") == False: self.CreationTable("menus_categories", Tables.DB_DATA)
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 3, 9)
        if versionFichier < versionFiltre:
            try:
                if self.isNetwork == True:
                    self.ExecuterReq("ALTER TABLE individus MODIFY COLUMN mail VARCHAR(200);")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 4, 1)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("menus_legendes") == False: self.CreationTable("menus_legendes", Tables.DB_DATA)
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 4, 5)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("familles", "etat", "VARCHAR(50)")
                self.AjoutChamp("individus", "etat", "VARCHAR(50)")
                self.CreationIndex("index_familles_etat")
                self.CreationIndex("index_individus_etat")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 4, 9)
        if versionFichier < versionFiltre:
            try:
                if self.isNetwork == True:
                    self.ExecuterReq("ALTER TABLE factures_regies MODIFY COLUMN numclitipi VARCHAR(50);")
                    self.ExecuterReq("ALTER TABLE factures MODIFY COLUMN numero BIGINT;")
                    self.ExecuterReq("ALTER TABLE pes_pieces MODIFY COLUMN numero BIGINT;")
                    self.Commit()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 5, 0)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("inscriptions", "statut", "VARCHAR(100)")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9105()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 5, 1)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("portail_actions", "IDpaiement", "INTEGER")
                self.AjoutChamp("portail_actions", "ventilation", "VARCHAR(5000)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 5, 4)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("portail_periodes", "prefacturation", "INTEGER")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 5, 6)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("consommations", "badgeage_debut", "DATETIME")
                self.AjoutChamp("consommations", "badgeage_fin", "DATETIME")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 5, 7)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("adresses_mail", "moteur", "VARCHAR(200)")
                self.AjoutChamp("adresses_mail", "parametres", "VARCHAR(1000)")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9130()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 7, 0)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("perceptions") == False: self.CreationTable("perceptions", Tables.DB_DATA)
                self.AjoutChamp("comptes_bancaires", "dft_titulaire", "VARCHAR(400)")
                self.AjoutChamp("comptes_bancaires", "dft_iban", "VARCHAR(400)")
                self.AjoutChamp("lots_prelevements", "format", "VARCHAR(200)")
                self.AjoutChamp("lots_prelevements", "encodage", "VARCHAR(200)")
                self.AjoutChamp("lots_prelevements", "IDperception", "INTEGER")
                self.AjoutChamp("lots_prelevements", "motif", "VARCHAR(300)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 7, 5)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("devis") == False: self.CreationTable("devis", Tables.DB_DATA)
                if self.IsTableExists("portail_reservations_locations") == False: self.CreationTable("portail_reservations_locations", Tables.DB_DATA)
                self.AjoutChamp("locations", "IDlocation_portail", "VARCHAR(100)")
                # import modèle doc devis par défaut
                from Utils import UTILS_Export_documents
                UTILS_Export_documents.ImporterDepuisFichierDefaut(IDmodele=14, nom=None, IDfond=1, defaut=1)
                # Importation du modèle d'emails 'Réservation location portail'
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9054()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 7, 6)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("lots_prelevements", "identifiant_service", "VARCHAR(200)")
                self.AjoutChamp("lots_prelevements", "poste_comptable", "VARCHAR(200)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 7, 9)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("pes_lots", "code_etab", "VARCHAR(100)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 8, 0)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("factures", "mention1", "VARCHAR(300)")
                self.AjoutChamp("factures", "mention2", "VARCHAR(300)")
                self.AjoutChamp("factures", "mention3", "VARCHAR(300)")
                self.AjoutChamp("locations", "serie", "VARCHAR(100)")
                self.AjoutChamp("locations", "partage", "INTEGER")
                self.AjoutChamp("produits", "activation_partage", "INTEGER")
                self.AjoutChamp("portail_reservations_locations", "partage", "INTEGER")
                if self.IsTableExists("contacts") == False: self.CreationTable("contacts", Tables.DB_DATA)
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 8, 2)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("historique", "IDdonnee", "INTEGER")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9038()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 8, 5)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("pes_lots", "format", "VARCHAR(100)")
                self.AjoutChamp("pes_lots", "options", "VARCHAR(1000)")
                from Utils import UTILS_Procedures
                UTILS_Procedures.A9045()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 8, 6)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("activites", "code_produit_local", "VARCHAR(200)")
                self.AjoutChamp("prestations", "code_produit_local", "VARCHAR(200)")
                self.AjoutChamp("types_cotisations", "code_produit_local", "VARCHAR(200)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 9, 1)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("activites", "inscriptions_multiples", "INTEGER")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 9, 3)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("pieces", "titre", "VARCHAR(200)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 2, 9, 7)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("locations", "description", "VARCHAR(200)")
                self.AjoutChamp("portail_reservations_locations", "description", "VARCHAR(200)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 3, 0, 5)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("tarifs", "code_produit_local", "VARCHAR(200)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 3, 0, 6)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("memo_journee", "couleur", "VARCHAR(50)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 3, 1, 4)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("familles", "tiers_solidaire", "INTEGER")
                self.AjoutChamp("pes_pieces", "tiers_solidaire", "INTEGER")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 3, 1, 8)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("activites", "code_service", "VARCHAR(200)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 3, 3, 0)
        if versionFichier < versionFiltre:
            try:
                self.AjoutChamp("activites", "code_analytique", "VARCHAR(200)")
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================

        versionFiltre = (1, 3, 3, 6)
        if versionFichier < versionFiltre:
            try:
                if self.isNetwork == True:
                    self.ExecuterReq("ALTER TABLE pes_pieces MODIFY COLUMN numero VARCHAR(400);")
                    self.Commit()
            except Exception as err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================



        return True








if __name__ == "__main__":
    pass