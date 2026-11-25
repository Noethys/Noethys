#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Module :         Tableaux croisés dynamiques statistiques
#-----------------------------------------------------------

import os
import io
import json
import datetime
import calendar
import wx
import GestionDB
from Utils.UTILS_Traduction import _
from Utils import UTILS_Stats_modeles as MODELES
from Utils import UTILS_Stats_rapports as RAPPORTS
from Utils import UTILS_Dates


FICHIER_TABLEAUX_PERSO = os.path.join(RAPPORTS.GetRepertoireRapports(), "tableaux_personnalises.json")

TRANCHES_AGES = [
    ("-60", _(u"Moins de 60 ans")),
    ("60-69", _(u"60 - 69 ans")),
    ("70-79", _(u"70 - 79 ans")),
    ("80-89", _(u"80 - 89 ans")),
    ("90-99", _(u"90 - 99 ans")),
    ("100+", _(u"100 ans et plus")),
    ("inconnu", _(u"Âge non renseigné")),
]

DIMENSIONS_DISPONIBLES = [
    ("tranches_ages", _(u"Tranches d'âge")),
    ("activites", _(u"Activités")),
    ("genres", _(u"Genre (Femme / Homme)")),
    ("villes", _(u"Commune / Ville de résidence")),
    ("mois", _(u"Mois de fréquentation")),
    ("caisses", _(u"Caisse de rattachement")),
    ("qf", _(u"Quotient familial (par tranches de 100€)")),
]

INDICATEURS_DISPONIBLES = [
    ("usagers_uniques", _(u"Nombre d'usagers distincts (ayant consommé au moins 1 fois)")),
    ("total_consommations", _(u"Nombre total de présences / consommations")),
]


def GetCodeTrancheAge(age):
    if age is None:
        return "inconnu"
    try:
        age = int(age)
    except Exception:
        return "inconnu"
    if age < 60:
        return "-60"
    elif 60 <= age <= 69:
        return "60-69"
    elif 70 <= age <= 79:
        return "70-79"
    elif 80 <= age <= 89:
        return "80-89"
    elif 90 <= age <= 99:
        return "90-99"
    else:
        return "100+"


def GetTableauxPersonnalisesSauvegardes():
    """ Charge la liste des tableaux personnalisés enregistrés localement """
    if not os.path.exists(FICHIER_TABLEAUX_PERSO):
        return []
    try:
        with io.open(FICHIER_TABLEAUX_PERSO, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def EnregistrerTableauxPersonnalises(listeTableaux):
    """ Enregistre la liste des tableaux personnalisés dans un fichier JSON """
    try:
        rep = os.path.dirname(FICHIER_TABLEAUX_PERSO)
        if not os.path.exists(rep):
            os.makedirs(rep)
        with io.open(FICHIER_TABLEAUX_PERSO, "w", encoding="utf-8") as f:
            f.write(json.dumps(listeTableaux, cls=RAPPORTS.StatsJSONEncoder, indent=2, ensure_ascii=False))
        return True
    except Exception:
        return False


def SauvegarderNouveauTableauPerso(definition):
    """ Ajoute ou met à jour une définition de tableau personnalisé """
    liste = GetTableauxPersonnalisesSauvegardes()
    code = definition.get("code")
    remplace = False
    for i, t in enumerate(liste):
        if t.get("code") == code:
            liste[i] = definition
            remplace = True
            break
    if not remplace:
        liste.append(definition)
    EnregistrerTableauxPersonnalises(liste)


def SupprimerTableauPerso(code):
    """ Supprime un tableau personnalisé par son code """
    liste = GetTableauxPersonnalisesSauvegardes()
    nouvelle_liste = [t for t in liste if t.get("code") != code]
    EnregistrerTableauxPersonnalises(nouvelle_liste)


class TableauCroiseDynamique(MODELES.Tableau):
    """
    Tableau statistique croisé dynamique créé par l'utilisateur.
    Interroge la BDD en lecture seule selon les dimensions choisies.
    """
    def __init__(self, definition={}):
        MODELES.Tableau.__init__(self)
        self.definition = definition
        self.code = definition.get("code", "custom_tab_%s" % datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        self.nom = definition.get("titre", _(u"Tableau personnalisé"))
        self.rubrique_parent = definition.get("rubrique", "individus")
        self.page_parent = definition.get("page", "individus_nombre")
        self.is_custom = True
        self.indicateur = definition.get("indicateur", "usagers_uniques")
        self.axe_lignes = definition.get("axe_lignes", "tranches_ages")
        self.axe_colonnes = definition.get("axe_colonnes", "aucun")
        self.afficher_total_lignes = definition.get("afficher_total_lignes", True)
        self.afficher_total_colonnes = definition.get("afficher_total_colonnes", True)
        self.afficher_pourcentages = definition.get("afficher_pourcentages", False)
        
        # Initialiser personnalisation par défaut
        noteDefaut = definition.get("note", u"")
        if noteDefaut:
            self.dictPersonnalisation = {"note": noteDefaut}

    def MAJ(self, DB=None, dictParametres={}):
        self.dictParametres = dictParametres
        self.colonnes = []
        self.lignes = []
        self.totaux = []

        date_debut, date_fin = MODELES.GetDatesPeriode(dictParametres)
        conditionsActivites = MODELES.GetConditionActivites(dictParametres)
        conditionArchives = MODELES.GetConditionArchives(dictParametres)
        if conditionsActivites in ("", "()"):
            return

        date_ref = date_fin if str(date_fin) != "2999-01-01" else datetime.date.today()

        # Dictionnaires de référence
        from Data import DATA_Civilites
        dictCivilites = DATA_Civilites.GetDictCivilites()

        dictNomsActivites = dictParametres.get("dictActivites", {})

        # Requête pour adresses des individus si dimension ville utilisée
        dictVillesIndividus = {}
        if "villes" in (self.axe_lignes, self.axe_colonnes):
            req_villes = """SELECT IDindividu, ville_resid FROM individus;"""
            DB.ExecuterReq(req_villes)
            for IDind, v_res in DB.ResultatReq():
                nom_ville = (v_res or u"").strip()
                dictVillesIndividus[IDind] = nom_ville if nom_ville != "" else _(u"Non renseignée")

        # Requête caisses et QF des familles si dimension caisses ou qf utilisée
        dictCaissesFamilles = {}
        dictQFFamilles = {}
        if "caisses" in (self.axe_lignes, self.axe_colonnes) or "qf" in (self.axe_lignes, self.axe_colonnes):
            req_c = """SELECT IDcaisse, nom FROM caisses;"""
            DB.ExecuterReq(req_c)
            dictNomsCaisses = {row[0]: row[1] for row in DB.ResultatReq()}

            req_fam = """SELECT IDfamille, IDcaisse, quotient FROM familles;"""
            DB.ExecuterReq(req_fam)
            for IDfam, IDcaisse, qf in DB.ResultatReq():
                dictCaissesFamilles[IDfam] = dictNomsCaisses.get(IDcaisse, _(u"Caisse inconnue"))
                dictQFFamilles[IDfam] = qf

            # Lien individu -> IDfamille via rattachements
            dictIndividuFamille = {}
            req_rat = """SELECT IDindividu, IDfamille FROM rattachements;"""
            DB.ExecuterReq(req_rat)
            for IDind, IDfam in DB.ResultatReq():
                dictIndividuFamille[IDind] = IDfam

        # Requête principale des consommations de la période
        req = """SELECT consommations.IDconso, consommations.IDindividu, consommations.date, 
                        consommations.IDactivite, individus.date_naiss, individus.IDcivilite
                 FROM consommations
                 LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
                 WHERE consommations.date >= '%s' AND consommations.date <= '%s'
                 AND consommations.etat IN ('reservation', 'present')
                 AND consommations.IDactivite IN %s
                 %s
                 ;""" % (str(date_debut), str(date_fin), conditionsActivites, conditionArchives)
        
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        if not donnees:
            return

        # Fonction helper pour extraire la valeur d'une dimension pour une ligne de conso
        def ExtraireDimension(dimension_nom, IDconso, IDindividu, dateConso, IDactivite, date_naiss, IDcivilite):
            if dimension_nom == "tranches_ages":
                if date_naiss:
                    try:
                        d_naiss = MODELES.DateEngEnDateDD(date_naiss)
                        age = (date_ref.year - d_naiss.year) - int((date_ref.month, date_ref.day) < (d_naiss.month, d_naiss.day))
                    except Exception:
                        age = None
                else:
                    age = None
                code_tr = GetCodeTrancheAge(age)
                # Trouver le label correspondant
                for c_tr, lbl_tr in TRANCHES_AGES:
                    if c_tr == code_tr:
                        return (c_tr, lbl_tr)
                return ("inconnu", _(u"Âge non renseigné"))

            elif dimension_nom == "activites":
                nomAct = dictNomsActivites.get(IDactivite, u"Activité %s" % IDactivite)
                return (IDactivite, nomAct)

            elif dimension_nom == "genres":
                civ = dictCivilites.get(IDcivilite)
                sexe = civ.get("sexe") if civ else None
                if sexe == "F":
                    return ("F", _(u"Femmes / Filles"))
                elif sexe == "M":
                    return ("M", _(u"Hommes / Garçons"))
                else:
                    return ("None", _(u"Non précisé"))

            elif dimension_nom == "villes":
                ville = dictVillesIndividus.get(IDindividu, _(u"Non renseignée"))
                return (ville.lower(), ville)

            elif dimension_nom == "mois":
                try:
                    d = MODELES.DateEngEnDateDD(dateConso)
                    num_mois = d.month
                    nom_mois = "%02d - %s" % (num_mois, MODELES.LISTE_NOMS_MOIS[num_mois - 1])
                    return (num_mois, nom_mois)
                except Exception:
                    return (99, _(u"Inconnu"))

            elif dimension_nom == "caisses":
                IDfam = dictIndividuFamille.get(IDindividu)
                caisse = dictCaissesFamilles.get(IDfam, _(u"Non renseignée"))
                return (caisse.lower(), caisse)

            elif dimension_nom == "qf":
                IDfam = dictIndividuFamille.get(IDindividu)
                quotient = dictQFFamilles.get(IDfam)
                if quotient is None:
                    return (99999, _(u"Sans QF renseigné"))
                tranche_deb = (int(quotient) // 100) * 100
                tranche_fin = tranche_deb + 99
                return (tranche_deb, u"%d€ - %d€" % (tranche_deb, tranche_fin))

            return ("valeur", u"Valeur")

        # Table d'aggrégation : dict[cle_ligne][cle_colonne] = set(individus) ou int(conso)
        matrice = {}
        labels_lignes = {}
        labels_colonnes = {}

        est_croise = (self.axe_colonnes not in ("aucun", "", None))

        for IDconso, IDindividu, dateConso, IDactivite, date_naiss, IDcivilite in donnees:
            cle_ligne, lbl_ligne = ExtraireDimension(self.axe_lignes, IDconso, IDindividu, dateConso, IDactivite, date_naiss, IDcivilite)
            labels_lignes[cle_ligne] = lbl_ligne

            if est_croise:
                cle_col, lbl_col = ExtraireDimension(self.axe_colonnes, IDconso, IDindividu, dateConso, IDactivite, date_naiss, IDcivilite)
                labels_colonnes[cle_col] = lbl_col
            else:
                cle_col = "valeur"
                labels_colonnes[cle_col] = _(u"Effectif")

            if cle_ligne not in matrice:
                matrice[cle_ligne] = {}
            if cle_col not in matrice[cle_ligne]:
                matrice[cle_ligne][cle_col] = set() if self.indicateur == "usagers_uniques" else 0

            if self.indicateur == "usagers_uniques":
                matrice[cle_ligne][cle_col].add(IDindividu)
            else:
                matrice[cle_ligne][cle_col] += 1

        # Tri des lignes et colonnes
        def CleTri(cle, dimension_nom):
            if dimension_nom == "tranches_ages":
                ordre = ["-60", "60-69", "70-79", "80-89", "90-99", "100+", "inconnu"]
                return ordre.index(cle) if cle in ordre else 99
            elif dimension_nom == "genres":
                ordre = ["F", "M", "None"]
                return ordre.index(cle) if cle in ordre else 99
            elif isinstance(cle, (int, float)):
                return cle
            else:
                return str(cle).lower()

        liste_cles_lignes = sorted(labels_lignes.keys(), key=lambda k: CleTri(k, self.axe_lignes))
        liste_cles_cols = sorted(labels_colonnes.keys(), key=lambda k: CleTri(k, self.axe_colonnes)) if est_croise else ["valeur"]

        # Construction des en-têtes de colonnes
        label_col1 = dict(DIMENSIONS_DISPONIBLES).get(self.axe_lignes, _(u"Éléments"))
        self.colonnes = [(label_col1, "30%")]

        for c_col in liste_cles_cols:
            lbl = labels_colonnes[c_col]
            self.colonnes.append((lbl, "auto"))

        if est_croise and self.afficher_total_colonnes:
            self.colonnes.append((_(u"Total"), "auto"))

        if not est_croise and self.afficher_pourcentages:
            self.colonnes.append((_(u"Pourcentage"), "auto"))

        # Calcul des totaux par colonne
        totaux_colonnes = {c: (set() if self.indicateur == "usagers_uniques" else 0) for c in liste_cles_cols}
        total_global = set() if self.indicateur == "usagers_uniques" else 0

        # Lignes de données
        lignes_donnees = []
        for c_lig in liste_cles_lignes:
            lbl_l = labels_lignes[c_lig]
            ligne_vals = [lbl_l]
            total_ligne = set() if self.indicateur == "usagers_uniques" else 0

            for c_col in liste_cles_cols:
                v = matrice.get(c_lig, {}).get(c_col, set() if self.indicateur == "usagers_uniques" else 0)
                if self.indicateur == "usagers_uniques":
                    compte = len(v)
                    total_ligne.update(v)
                    totaux_colonnes[c_col].update(v)
                    total_global.update(v)
                else:
                    compte = v
                    total_ligne += v
                    totaux_colonnes[c_col] += v
                    total_global += v
                ligne_vals.append(compte)

            if est_croise and self.afficher_total_colonnes:
                nb_tot_ligne = len(total_ligne) if self.indicateur == "usagers_uniques" else total_ligne
                ligne_vals.append(nb_tot_ligne)

            lignes_donnees.append(ligne_vals)

        # Calcul du total global pour les pourcentages en 1 dimension
        nb_total_global = len(total_global) if self.indicateur == "usagers_uniques" else total_global
        if not est_croise and self.afficher_pourcentages:
            for l in lignes_donnees:
                val = l[1]
                pct = (float(val) / nb_total_global * 100.0) if nb_total_global > 0 else 0.0
                l.append(u"%.1f %%" % pct)

        self.lignes = lignes_donnees

        # Ligne de totaux
        if self.afficher_total_lignes:
            ligne_tot = [_(u"Total")]
            for c_col in liste_cles_cols:
                v_tot = totaux_colonnes[c_col]
                nb = len(v_tot) if self.indicateur == "usagers_uniques" else v_tot
                ligne_tot.append(nb)

            if est_croise and self.afficher_total_colonnes:
                ligne_tot.append(nb_total_global)

            if not est_croise and self.afficher_pourcentages:
                ligne_tot.append(u"100.0 %" if nb_total_global > 0 else u"0.0 %")

            self.totaux = ligne_tot

    def GetObjetHTML(self, mode="affichage"):
        html = MODELES.Tableau.GetObjetHTML(self, mode=mode)
        if not html:
            return ""

        # En mode affichage, ajouter également le lien de suppression de ce tableau sur-mesure
        if mode == "affichage":
            lien_suppr = u""" &nbsp; <A HREF="suppr_tab:%s" STYLE="text-decoration:none; color:#C0392B;">[🗑 Supprimer]</A>""" % self.code
            pattern = u"""[⚙ Personnaliser]</B></A>"""
            if pattern in html:
                html = html.replace(pattern, pattern + lien_suppr)

        return html
