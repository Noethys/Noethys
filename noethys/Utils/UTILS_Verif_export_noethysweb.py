#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-20 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------
"""
Contrôle des données avant la création du fichier d'export vers Noethysweb.

Les objets générés par UTILS_Export_noethysweb (format fixture Django) sont confrontés
au schéma des modèles Noethysweb (voir UTILS_Schema_noethysweb) afin de détecter
en amont ce qui ferait échouer le "loaddata" côté Noethysweb :
    - champ obligatoire vide (NOT NULL),
    - date, heure, nombre ou montant mal formé,
    - texte trop long pour le champ de destination,
    - référence vers un élément inexistant (clé étrangère orpheline),
    - doublon sur un identifiant ou un champ unique.
"""

import datetime, decimal, re, six
from Utils.UTILS_Schema_noethysweb import Texte


ERREUR = "erreur"
AVERTISSEMENT = "avertissement"

RE_DATE = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")
RE_HEURE = re.compile(r"^(\d{1,2}):(\d{1,2})(?::(\d{1,2})(?:[.,]\d{1,6})?)?$")
RE_DATETIME = re.compile(r"^(\d{4}-\d{1,2}-\d{1,2})(?:[T ](\d{1,2}:\d{1,2}(?::\d{1,2}(?:[.,]\d{1,6})?)?)\s*(?:Z|[+-]\d{2}(?::?\d{2})?)?)?$")

# Champs utilisés pour donner un nom lisible à un objet
CHAMPS_NOM = ("nom", "label", "intitule", "titre", "numero")


class Anomalie(object):
    def __init__(self, gravite=ERREUR, modele="", pk=None, champ=None, message=u"", element=u"", contexte=u"", label_modele=u"", table=u""):
        self.gravite = gravite
        self.label_modele = label_modele or modele
        self.table = table or u""
        self.modele = modele
        self.pk = pk
        self.champ = champ
        self.message = message
        self.element = element
        self.contexte = contexte

    def __repr__(self):
        return "<Anomalie %s %s ID%s %s>" % (self.gravite, self.modele, self.pk, self.champ)


def Tronquer(texte, longueur=40):
    return texte if len(texte) <= longueur else texte[:longueur] + u"..."


def Date_valide(texte):
    m = RE_DATE.match(texte)
    if not m:
        return False
    try:
        datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return True
    except ValueError:
        return False


def Heure_valide(texte):
    m = RE_HEURE.match(texte)
    if not m:
        return False
    return int(m.group(1)) < 24 and int(m.group(2)) < 60 and (m.group(3) is None or int(m.group(3)) < 60)


def Datetime_valide(texte):
    m = RE_DATETIME.match(texte)
    if not m:
        return False
    return Date_valide(m.group(1)) and (m.group(2) is None or Heure_valide(m.group(2)))


class Verificateur(object):
    def __init__(self, liste_objets=[], modeles_exportes=None, schema=None, max_anomalies=5000):
        self.schema = schema or {}
        self.liste_objets = liste_objets
        # Modèles effectivement inclus dans l'export (selon les catégories cochées)
        self.modeles_exportes = set(modeles_exportes) if modeles_exportes is not None else set(o["model"] for o in liste_objets)
        self.max_anomalies = max_anomalies
        self.anomalies = []
        self.avertissements_signales = set()

        # Index des clés primaires par modèle
        self.dict_pk = {}
        for objet in liste_objets:
            self.dict_pk.setdefault(objet["model"], set()).add(self.Normaliser_id(objet["pk"]))

        # Libellés des individus et des familles pour rendre les messages lisibles
        self.dict_individus = {}
        titulaires = {}
        for objet in liste_objets:
            if objet["model"] == "core.Individu":
                f = objet["fields"]
                nom = u" ".join([Texte(x) for x in (f.get("nom"), f.get("prenom")) if x])
                self.dict_individus[objet["pk"]] = Tronquer(nom) or u"ID%s" % objet["pk"]
            elif objet["model"] == "core.Rattachement" and objet["fields"].get("titulaire"):
                titulaires.setdefault(objet["fields"].get("famille"), []).append(objet["fields"].get("individu"))
        self.dict_familles = {}
        for IDfamille, individus in titulaires.items():
            noms = [self.dict_individus[i] for i in individus if i in self.dict_individus]
            if noms:
                self.dict_familles[IDfamille] = u" et ".join(noms)

    # ------------------------------------------------------------------
    @staticmethod
    def Normaliser_id(valeur):
        try:
            return int(valeur)
        except (TypeError, ValueError):
            return valeur

    def Get_label_famille(self, IDfamille):
        if IDfamille in self.dict_familles:
            return u"Famille %s (ID%s)" % (self.dict_familles[IDfamille], IDfamille)
        return u"Famille ID%s" % IDfamille

    def Get_label_individu(self, IDindividu):
        if IDindividu in self.dict_individus:
            return u"%s (ID%s)" % (self.dict_individus[IDindividu], IDindividu)
        return u"Individu ID%s" % IDindividu

    def Get_element(self, objet):
        """ Description lisible de l'objet : 'Dépôt ID12 « Chèques mars »' """
        label = self.schema.get(objet["model"], {}).get("label", objet["model"])
        texte = u"%s ID%s" % (label, objet["pk"])
        for champ in CHAMPS_NOM:
            valeur = objet["fields"].get(champ)
            if valeur and isinstance(valeur, six.string_types):
                texte += u" « %s »" % Tronquer(Texte(valeur))
                break
        return texte

    def Get_contexte(self, objet):
        fields = objet["fields"]
        if objet["model"] == "core.Famille":
            return self.Get_label_famille(objet["pk"])
        if objet["model"] == "core.Individu":
            return self.Get_label_individu(objet["pk"])
        contexte = []
        if fields.get("famille"):
            contexte.append(self.Get_label_famille(fields["famille"]))
        if fields.get("individu"):
            contexte.append(self.Get_label_individu(fields["individu"]))
        return u" - ".join(contexte)

    def Ajouter(self, gravite, objet, champ, message):
        if len(self.anomalies) >= self.max_anomalies:
            if not self.liste_tronquee:
                self.liste_tronquee = True
                self.anomalies.append(Anomalie(gravite=AVERTISSEMENT, element=u"-",
                    message=u"Liste limitée aux %d premières anomalies : corrigez-les puis relancez l'export pour voir les suivantes." % self.max_anomalies))
            return
        self.anomalies.append(self.Creer_anomalie(gravite=gravite, modele=objet["model"], pk=objet["pk"], champ=champ, message=message,
                                                  element=self.Get_element(objet), contexte=self.Get_contexte(objet)))

    def Creer_anomalie(self, modele="", **kwds):
        info = self.schema.get(modele, {})
        return Anomalie(modele=modele, label_modele=info.get("label", modele), table=info.get("table"), **kwds)

    # ------------------------------------------------------------------
    def Verifier(self):
        self.anomalies = []
        self.liste_tronquee = False
        pk_vus = {}
        uniques_vus = {}

        for objet in self.liste_objets:
            modele = objet["model"]
            if modele not in self.schema:
                continue
            schema_champs = self.schema[modele]["champs"]

            # Doublon de clé primaire
            cle = (modele, self.Normaliser_id(objet["pk"]))
            if cle in pk_vus:
                self.Ajouter(ERREUR, objet, None, u"Identifiant en double : cet élément apparaît plusieurs fois dans l'export.")
            pk_vus[cle] = True

            for nom_champ, valeur in objet["fields"].items():
                info = schema_champs.get(nom_champ)
                if not info:
                    continue
                self.Verifier_champ(objet, nom_champ, info, valeur, uniques_vus)

        return self.anomalies

    def Verifier_champ(self, objet, nom_champ, info, valeur, uniques_vus):
        label = info.get("label", nom_champ)
        type_champ = info["type"]

        # Champ ManyToMany : liste d'identifiants
        if type_champ == "m2m":
            for id_cible in (valeur or []):
                self.Verifier_reference(objet, nom_champ, info, id_cible)
            return

        # Valeur vide
        if valeur is None:
            if not info.get("null", True) and not info.get("pk"):
                self.Ajouter(ERREUR, objet, nom_champ, u"Le champ « %s » est obligatoire mais n'est pas renseigné." % label)
            return

        # Formats
        if type_champ == "date" and not isinstance(valeur, datetime.date):
            if not Date_valide(Texte(valeur).strip()):
                self.Ajouter(ERREUR, objet, nom_champ, u"Le champ « %s » contient une date invalide : '%s'." % (label, Texte(valeur)))
        elif type_champ == "datetime" and not isinstance(valeur, datetime.datetime):
            if not Datetime_valide(Texte(valeur).strip()):
                self.Ajouter(ERREUR, objet, nom_champ, u"Le champ « %s » contient une date/heure invalide : '%s'." % (label, Texte(valeur)))
        elif type_champ == "time" and not isinstance(valeur, datetime.time):
            if not Heure_valide(Texte(valeur).strip()):
                self.Ajouter(ERREUR, objet, nom_champ, u"Le champ « %s » contient une heure invalide : '%s'." % (label, Texte(valeur)))
        elif type_champ in ("int", "fk"):
            if isinstance(valeur, bool) or not isinstance(valeur, six.integer_types):
                try:
                    int(Texte(valeur).strip())
                except ValueError:
                    self.Ajouter(ERREUR, objet, nom_champ, u"Le champ « %s » doit contenir un nombre entier : '%s'." % (label, Texte(valeur)))
                    return
        elif type_champ == "float":
            try:
                float(valeur)
            except (TypeError, ValueError):
                self.Ajouter(ERREUR, objet, nom_champ, u"Le champ « %s » doit contenir un nombre : '%s'." % (label, Texte(valeur)))
        elif type_champ == "decimal":
            self.Verifier_decimal(objet, nom_champ, info, valeur)
        elif type_champ == "str" and info.get("max_length"):
            longueur = len(Texte(valeur))
            if longueur > info["max_length"]:
                self.Ajouter(ERREUR, objet, nom_champ, u"Le champ « %s » est trop long (%d caractères pour %d autorisés)." % (label, longueur, info["max_length"]))

        # Clé étrangère
        if type_champ == "fk":
            self.Verifier_reference(objet, nom_champ, info, valeur)

        # Unicité
        if info.get("unique") and valeur != u"":
            cle = (objet["model"], nom_champ, valeur)
            if cle in uniques_vus:
                self.Ajouter(ERREUR, objet, nom_champ, u"La valeur '%s' du champ « %s » est déjà utilisée par l'élément ID%s alors qu'elle doit être unique." % (Texte(valeur), label, uniques_vus[cle]))
            else:
                uniques_vus[cle] = objet["pk"]

    def Verifier_decimal(self, objet, nom_champ, info, valeur):
        label = info.get("label", nom_champ)
        try:
            montant = decimal.Decimal(Texte(valeur).strip())
            if not montant.is_finite():
                raise decimal.InvalidOperation
        except (decimal.InvalidOperation, ValueError):
            self.Ajouter(ERREUR, objet, nom_champ, u"Le champ « %s » doit contenir un montant : '%s'." % (label, Texte(valeur)))
            return
        max_digits, decimal_places = info.get("max_digits"), info.get("decimal_places")
        if max_digits and decimal_places is not None:
            limite = decimal.Decimal(10) ** (max_digits - decimal_places)
            if abs(montant) >= limite:
                self.Ajouter(ERREUR, objet, nom_champ, u"Le montant du champ « %s » est trop grand : %s." % (label, Texte(valeur)))

    def Verifier_reference(self, objet, nom_champ, info, id_cible):
        cible = info.get("cible")
        if cible not in self.schema:
            # Modèle cible jamais exporté par Noethys (données propres à Noethysweb)
            return
        label = info.get("label", nom_champ)
        if cible not in self.modeles_exportes:
            # Catégorie décochée : un seul avertissement par champ
            cle = (objet["model"], nom_champ)
            if cle not in self.avertissements_signales:
                self.avertissements_signales.add(cle)
                self.anomalies.append(self.Creer_anomalie(gravite=AVERTISSEMENT, modele=objet["model"], champ=nom_champ,
                    element=u"%s (tous)" % self.schema[objet["model"]]["label"],
                    message=u"Le champ « %s » fait référence à des éléments « %s » qui ne sont pas inclus dans l'export. Vérifiez les données à transférer cochées." % (label, self.schema[cible]["label"])))
            return
        if self.Normaliser_id(id_cible) not in self.dict_pk.get(cible, set()):
            self.Ajouter(ERREUR, objet, nom_champ, u"Le champ « %s » fait référence à un élément « %s » ID%s qui n'existe pas (ou plus)." % (label, self.schema[cible]["label"], id_cible))


def Verifier(liste_objets=[], modeles_exportes=None, schema=None):
    """ Renvoie la liste des anomalies détectées """
    return Verificateur(liste_objets=liste_objets, modeles_exportes=modeles_exportes, schema=schema).Verifier()
