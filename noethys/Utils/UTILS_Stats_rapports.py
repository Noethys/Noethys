#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Module :         Gestion et mémorisation des rapports personnalisés de statistiques
# Licence :        Licence GNU GPL
#------------------------------------------------------------------------

import os
import io
import json
import datetime
import wx
import Chemins
from Utils.UTILS_Traduction import _


class StatsJSONEncoder(json.JSONEncoder):
    """ Encodeur JSON pour les dates et objets Noethys """
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        return super(StatsJSONEncoder, self).default(obj)


def GetRepertoireRapports():
    """ Renvoie le chemin du répertoire où sont stockés les rapports personnalisés """
    rep = os.path.join(Chemins.REP_COURANT, "Rapports_stats")
    if not os.path.exists(rep):
        try:
            os.makedirs(rep)
        except Exception:
            pass
    return rep


def GetListeRapports():
    """ Renvoie la liste triée des noms des rapports sauvegardés """
    rep = GetRepertoireRapports()
    if not os.path.exists(rep):
        return []
    liste = []
    for f in os.listdir(rep):
        if f.lower().endswith(".json"):
            nom = os.path.splitext(f)[0]
            liste.append(nom)
    liste.sort(key=lambda x: x.lower())
    return liste


def SauvegarderRapport(nom=u"", dictParametres={}, dictPersonnalisations={}, selectionsCodes=None, listeObjets=None, tableauxPersonnalises=None, organisationsPages=None, ongletsVisibles=None, commentaires=""):
    """ Enregistre les paramètres et personnalisations d'un rapport dans un fichier JSON """
    nomRapport = nom
    if not nomRapport or nomRapport.strip() == "":
        return False, _(u"Veuillez indiquer un nom de rapport valide.")

    rep = GetRepertoireRapports()
    # Nettoyage du nom pour le nom de fichier
    nomFichier = "".join(c for c in nomRapport if c.isalnum() or c in (" ", "_", "-")).strip()
    if not nomFichier:
        nomFichier = "rapport_statistique"
    cheminFichier = os.path.join(rep, "%s.json" % nomFichier)

    # Récupération des personnalisations si listeObjets est fournie
    if not dictPersonnalisations and listeObjets:
        dictPersonnalisations = {}
        for dictRubrique in listeObjets:
            for dictPage in dictRubrique.get("pages", []):
                for objet in dictPage.get("objets", []):
                    if hasattr(objet, "dictPersonnalisation") and objet.dictPersonnalisation:
                        dictPersonnalisations[objet.code] = objet.dictPersonnalisation

    data = {
        "version": 1,
        "nom": nomRapport,
        "date_creation": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "commentaires": commentaires,
        "dictParametres": dictParametres,
        "personnalisations": dictPersonnalisations or {},
        "dictPersonnalisations": dictPersonnalisations or {},
        "selectionsCodes": selectionsCodes or [],
        "tableauxPersonnalises": tableauxPersonnalises or [],
        "organisationsPages": organisationsPages or {},
        "ongletsVisibles": ongletsVisibles or {},
    }

    try:
        with io.open(cheminFichier, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, cls=StatsJSONEncoder, indent=2, ensure_ascii=False))
        return True, cheminFichier
    except Exception as err:
        return False, str(err)


def ChargerRapport(nomOuFichier):
    """ Charge un rapport personnalisé à partir de son nom ou de son fichier """
    rep = GetRepertoireRapports()
    if os.path.isabs(nomOuFichier) and os.path.exists(nomOuFichier):
        chemin = nomOuFichier
    else:
        nomFichier = nomOuFichier if nomOuFichier.lower().endswith(".json") else ("%s.json" % nomOuFichier)
        chemin = os.path.join(rep, nomFichier)

    if not os.path.exists(chemin):
        return None

    try:
        with io.open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Restauration des types datetime.date dans dictParametres
        dictParams = data.get("dictParametres", {})
        if "periode" in dictParams and isinstance(dictParams["periode"], dict):
            p = dictParams["periode"]
            for cle in ("date_debut", "date_fin"):
                if cle in p and isinstance(p[cle], (str, bytes)):
                    try:
                        p[cle] = datetime.datetime.strptime(p[cle][:10], "%Y-%m-%d").date()
                    except Exception:
                        pass

        # Conversion des clés entières de dictActivites
        if "dictActivites" in dictParams and isinstance(dictParams["dictActivites"], dict):
            dictActi = {}
            for k, v in dictParams["dictActivites"].items():
                try:
                    dictActi[int(k)] = v
                except Exception:
                    dictActi[k] = v
            dictParams["dictActivites"] = dictActi

        if "listeActivites" in dictParams and isinstance(dictParams["listeActivites"], list):
            dictParams["listeActivites"] = [int(x) if str(x).isdigit() else x for x in dictParams["listeActivites"]]

        # Harmonisation personnalisations
        if "dictPersonnalisations" not in data and "personnalisations" in data:
            data["dictPersonnalisations"] = data["personnalisations"]

        return data
    except Exception as err:
        return None


def SupprimerRapport(nomOuFichier):
    """ Supprime un rapport personnalisé """
    rep = GetRepertoireRapports()
    nomFichier = nomOuFichier if nomOuFichier.lower().endswith(".json") else ("%s.json" % nomOuFichier)
    chemin = os.path.join(rep, nomFichier)
    if os.path.exists(chemin):
        try:
            os.remove(chemin)
            return True, None
        except Exception as err:
            return False, str(err)
    return False, _(u"Rapport introuvable.")


def ExporterRapport(parent, nomRapport):
    """ Exporte le fichier JSON d'un rapport vers l'emplacement choisi par l'utilisateur """
    rep = GetRepertoireRapports()
    nomFichier = nomRapport if nomRapport.lower().endswith(".json") else ("%s.json" % nomRapport)
    cheminSource = os.path.join(rep, nomFichier)
    if not os.path.exists(cheminSource):
        dlg = wx.MessageDialog(parent, _(u"Le rapport sélectionné n'a pas été trouvé."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return

    wildcard = _(u"Fichier de rapport (*.json)|*.json|Tous les fichiers (*.*)|*.*")
    dlg = wx.FileDialog(parent, message=_(u"Exporter le rapport..."), defaultFile=nomFichier, wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    if dlg.ShowModal() == wx.ID_OK:
        cheminDest = dlg.GetPath()
        dlg.Destroy()
        try:
            with io.open(cheminSource, "r", encoding="utf-8") as fs:
                contenu = fs.read()
            with io.open(cheminDest, "w", encoding="utf-8") as fd:
                fd.write(contenu)
            dlgOk = wx.MessageDialog(parent, _(u"Le rapport a été exporté avec succès."), _(u"Exportation réussie"), wx.OK | wx.ICON_INFORMATION)
            dlgOk.ShowModal()
            dlgOk.Destroy()
        except Exception as err:
            dlgErr = wx.MessageDialog(parent, _(u"Erreur lors de l'exportation : %s") % str(err), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErr.ShowModal()
            dlgErr.Destroy()
    else:
        dlg.Destroy()


def ImporterRapport(parent):
    """ Importe un fichier de rapport JSON dans le répertoire local des rapports """
    wildcard = _(u"Fichier de rapport (*.json)|*.json|Tous les fichiers (*.*)|*.*")
    dlg = wx.FileDialog(parent, message=_(u"Sélectionner un rapport à importer..."), wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if dlg.ShowModal() == wx.ID_OK:
        cheminSource = dlg.GetPath()
        dlg.Destroy()
        nomFichier = os.path.basename(cheminSource)
        rep = GetRepertoireRapports()
        cheminDest = os.path.join(rep, nomFichier)
        try:
            with io.open(cheminSource, "r", encoding="utf-8") as fs:
                data = json.load(fs)
            if "dictParametres" not in data:
                raise ValueError(_(u"Ce fichier JSON n'est pas un rapport statistique valide."))
            with io.open(cheminDest, "w", encoding="utf-8") as fd:
                fd.write(json.dumps(data, cls=StatsJSONEncoder, indent=2, ensure_ascii=False))
            nomRapport = data.get("nom", os.path.splitext(nomFichier)[0])
            return nomRapport
        except Exception as err:
            dlgErr = wx.MessageDialog(parent, _(u"Erreur lors de l'importation : %s") % str(err), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErr.ShowModal()
            dlgErr.Destroy()
            return None
    else:
        dlg.Destroy()
        return None
