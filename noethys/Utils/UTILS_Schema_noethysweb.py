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
Schéma des modèles Noethysweb utilisé pour vérifier les données avant export.

Le fichier core/models.py de Noethysweb est téléchargé depuis le dépôt GitHub officiel
à chaque export puis analysé (analyse syntaxique uniquement : le code n'est jamais exécuté).
"""

import ast, six


URL_MODELS = "https://raw.githubusercontent.com/Noethys/Noethysweb/main/noethysweb/core/models.py"
MODELES_INDISPENSABLES = ("core.Famille", "core.Individu", "core.Depot", "core.Reglement", "core.Activite")

TYPES = {
    "AutoField": "int", "BigAutoField": "int", "IntegerField": "int", "PositiveIntegerField": "int",
    "SmallIntegerField": "int", "PositiveSmallIntegerField": "int", "BigIntegerField": "int",
    "CharField": "str", "TextField": "str", "EmailField": "str", "SlugField": "str", "URLField": "str",
    "DateField": "date", "DateTimeField": "datetime", "TimeField": "time",
    "DecimalField": "decimal", "FloatField": "float", "BooleanField": "bool", "NullBooleanField": "bool",
    "ForeignKey": "fk", "OneToOneField": "fk", "ManyToManyField": "m2m",
    "ImageField": "str", "FileField": "str", "JSONField": "json",
    "ResizedImageField": "str", "MultiSelectField": "autre", "DurationField": "autre",
}

FONCTIONS_TRADUCTION = ("_", "gettext", "gettext_lazy", "ugettext_lazy")


def Texte(valeur):
    """ Convertit une valeur en unicode (Python 2 et 3) """
    if isinstance(valeur, six.binary_type):
        try:
            return valeur.decode("utf-8")
        except UnicodeDecodeError:
            return valeur.decode("cp1252", "replace")
    if isinstance(valeur, six.text_type):
        return valeur
    try:
        return six.text_type(valeur)
    except UnicodeError:
        # Python 2 : exception dont le message contient des caractères accentués
        return Texte(six.binary_type(valeur))


def _Valeur(noeud):
    try:
        valeur = ast.literal_eval(noeud)
        # Python 2 : les chaînes littérales sont lues sous forme d'octets UTF-8
        return Texte(valeur) if isinstance(valeur, six.binary_type) else valeur
    except Exception:
        # Libellé traduit : _("...") / gettext_lazy("...")
        if isinstance(noeud, ast.Call) and getattr(noeud.func, "id", None) in FONCTIONS_TRADUCTION and noeud.args:
            return _Valeur(noeud.args[0])
        if isinstance(noeud, ast.Name):
            return noeud.id
        if isinstance(noeud, ast.Attribute):
            return noeud.attr
        return None


def _Label(texte, defaut):
    texte = Texte(texte) if isinstance(texte, six.string_types) and texte else Texte(defaut)
    return texte[:1].upper() + texte[1:]


def Extraire_schema(source, modeles=None):
    """ Analyse le code source de core/models.py et renvoie le schéma des modèles.
        modeles : liste facultative des modèles à conserver (ex : ["core.Depot"]) """
    if six.PY2:
        # Python 2 : ast.parse attend des octets, la déclaration d'encodage garantit la lecture en UTF-8
        if isinstance(source, six.text_type):
            source = source.encode("utf-8")
        source = b"# -*- coding: utf-8 -*-\n" + source
    arbre = ast.parse(source)
    schema = {}
    for noeud in arbre.body:
        if not isinstance(noeud, ast.ClassDef):
            continue
        nom_modele = u"core." + Texte(noeud.name)
        if modeles is not None and nom_modele not in modeles:
            continue
        champs, meta = {}, {}
        for item in noeud.body:
            if isinstance(item, ast.ClassDef) and item.name == "Meta":
                for m in item.body:
                    if isinstance(m, ast.Assign) and isinstance(m.targets[0], ast.Name):
                        meta[m.targets[0].id] = _Valeur(m.value)
            if not (isinstance(item, ast.Assign) and isinstance(item.value, ast.Call) and isinstance(item.targets[0], ast.Name)):
                continue
            nom = Texte(item.targets[0].id)
            appel, chiffre = item.value, False
            # Champ chiffré : encrypt(models.XField(...))
            if isinstance(appel.func, ast.Name) and appel.func.id == "encrypt" and appel.args and isinstance(appel.args[0], ast.Call):
                appel, chiffre = appel.args[0], True
            nom_type = appel.func.attr if isinstance(appel.func, ast.Attribute) else getattr(appel.func, "id", None)
            if nom_type not in TYPES:
                continue
            type_champ = TYPES[nom_type]
            kw = {k.arg: _Valeur(k.value) for k in appel.keywords if k.arg}
            info = {"type": type_champ, "label": _Label(kw.get("verbose_name"), nom)}
            if type_champ in ("fk", "m2m"):
                cible = _Valeur(appel.args[0]) if appel.args else kw.get("to")
                if not isinstance(cible, six.string_types):
                    continue
                if cible == "self":
                    cible = noeud.name
                info["cible"] = u"core." + Texte(cible).split(".")[-1]
            if kw.get("primary_key"):
                info["pk"] = True
            elif type_champ != "m2m":
                info["null"] = bool(kw.get("null", False))
            if kw.get("max_length") and type_champ == "str" and nom_type != "TextField" and not chiffre:
                info["max_length"] = kw["max_length"]
            if type_champ == "decimal":
                info["max_digits"] = kw.get("max_digits")
                info["decimal_places"] = kw.get("decimal_places")
            if chiffre:
                info["chiffre"] = True
            if kw.get("unique"):
                info["unique"] = True
            champs[nom] = info
        if champs:
            table = meta.get("db_table")
            schema[nom_modele] = {"label": _Label(meta.get("verbose_name"), noeud.name), "table": Texte(table) if table else None, "champs": champs}
    return schema


def Schema_valide(schema):
    return bool(schema) and all(modele in schema for modele in MODELES_INDISPENSABLES)


def Get_schema(timeout=10):
    """ Télécharge et analyse core/models.py depuis GitHub.
        Renvoie (schema, None) ou (None, message d'erreur) """
    try:
        from six.moves.urllib.request import urlopen
        reponse = urlopen(URL_MODELS, timeout=timeout)
        source = reponse.read().decode("utf-8")
        reponse.close()
    except Exception as err:
        return None, u"Impossible de télécharger les modèles Noethysweb depuis GitHub (%s)." % Texte(err)
    try:
        schema = Extraire_schema(source)
    except Exception as err:
        return None, u"Les modèles Noethysweb téléchargés n'ont pas pu être analysés (%s)." % Texte(err)
    if not Schema_valide(schema):
        return None, u"Les modèles Noethysweb téléchargés sont incomplets."
    return schema, None
