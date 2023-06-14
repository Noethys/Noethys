#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-21 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import six
import GestionDB
import datetime
import gzip
import shutil
import base64
import os.path
import wx.propgrid as wxpg
from Ctrl.CTRL_Propertygrid import Propriete_date
from Utils import UTILS_Dates
from Ol import OL_Modes_reglements
from Utils import UTILS_Jvs
import FonctionsPerso
import wx.lib.dialogs as dialogs
from Dlg import DLG_Messagebox
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Utils import UTILS_Facturation
from Utils import UTILS_Organisateur
from Utils import UTILS_Parametres
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Dlg import DLG_Saisie_lot_tresor_public

if 'phoenix' in wx.PlatformInfo:
    from wx.adv import DP_DROPDOWN as DP_DROPDOWN
    from wx.adv import DP_SHOWCENTURY as DP_SHOWCENTURY
else :
    from wx import DP_DROPDOWN as DP_DROPDOWN
    from wx import DP_SHOWCENTURY as DP_SHOWCENTURY



class CTRL_Parametres(DLG_Saisie_lot_tresor_public.CTRL_Parametres):
    def __init__(self, parent, IDlot=None):
        DLG_Saisie_lot_tresor_public.CTRL_Parametres.__init__(self, parent, IDlot=IDlot)
        self.parent = parent

    def Remplissage(self):
        # Bordereau
        self.Append( wxpg.PropertyCategory(_(u"Bordereau")) )
        
        propriete = wxpg.IntProperty(label=_(u"Exercice"), name="exercice", value=datetime.date.today().year)
        propriete.SetHelpString(_(u"Saisissez l'année de l'exercice")) 
        self.Append(propriete)
        self.SetPropertyEditor("exercice", "SpinCtrl")
        
        listeMois = [u"_", _(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")]
        propriete = wxpg.EnumProperty(label=_(u"Mois"), name="mois", labels=listeMois, values=range(0, 13) , value=datetime.date.today().month)
        propriete.SetHelpString(_(u"Sélectionnez le mois")) 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"Objet"), name="objet_dette", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'objet du bordereau (Ex : 'Centre de Loisirs')")) 
        self.Append(propriete)

        # Dates
        self.Append( wxpg.PropertyCategory(_(u"Dates")) )

        propriete = Propriete_date(label=_(u"Date d'émission (JJ/MM/AAAA)"), name="date_emission", value=datetime.date.today())
        self.Append(propriete)

        propriete = Propriete_date(label=_(u"Date du prélèvement (JJ/MM/AAAA)"), name="date_prelevement", value=datetime.date.today())
        self.Append(propriete)

        propriete = Propriete_date(label=_(u"Avis d'envoi (JJ/MM/AAAA)"), name="date_envoi", value=datetime.date.today())
        self.Append(propriete)

        # Collectivité
        self.Append( wxpg.PropertyCategory(_(u"Identification")) )
        
        propriete = wxpg.StringProperty(label=_(u"ID Bordereau"), name="id_bordereau", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'ID du bordereau. Facultatif : Si non renseigné, le bordereau est créé dans le Brouillard"))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Article budgétaire"), name="id_poste", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'article budgétaire (Nature)"))
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"ID Collectivité"), name="id_collectivite", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'ID de la collectivité (Numéro SIRET)"))
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"Code Collectivité"), name="code_collectivite", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code Collectivité")) 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"Code Budget"), name="code_budget", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code Budget")) 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"Code Produit Local"), name="code_prodloc", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code Produit Local")) 
        self.Append(propriete)

        # Libellés
        self.Append( wxpg.PropertyCategory(_(u"Libellés")) )

        propriete = wxpg.StringProperty(label=_(u"Objet de la pièce"), name="objet_piece", value=_(u"FACTURE NUM{NUM_FACTURE} {MOIS_LETTRES} {ANNEE}"))
        propriete.SetHelpString(_(u"Saisissez l'objet de la pièce (en majuscules et sans accents). Vous pouvez personnaliser ce libellé grâce aux mots-clés suivants : {NOM_ORGANISATEUR} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Libellé du prélèvement"), name="prelevement_libelle", value=u"{NOM_ORGANISATEUR} - {OBJET_PIECE}")
        propriete.SetHelpString(_(u"Saisissez le libellé du prélèvement qui apparaîtra sur le relevé de compte de la famille. Vous pouvez personnaliser ce libellé grâce aux mots-clés suivants : {NOM_ORGANISATEUR} {OBJET_PIECE} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Nom de la collectivité"), name="nom_collectivite", value=u"{NOM_ORGANISATEUR}")
        propriete.SetHelpString(_(u"Saisissez le nom de la collectivité. A défaut, c'est le nom de l'organisateur qui sera inséré automatiquement."))
        self.Append(propriete)

        # Règlement automatique
        self.Append( wxpg.PropertyCategory(_(u"Règlement automatique")) )
        
        propriete = wxpg.BoolProperty(label=_(u"Régler automatiquement"), name="reglement_auto", value=False)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys créé un règlement automatiquement pour les prélèvements")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        propriete = wxpg.EnumProperty(label=_(u"Compte à créditer"), name="IDcompte")
        propriete.SetHelpString(_(u"Sélectionnez le compte bancaire à créditer dans le cadre du règlement automatique"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_comptes() 

        propriete = wxpg.EnumProperty(label=_(u"Mode de règlement"), name="IDmode")
        propriete.SetHelpString(_(u"Sélectionnez le mode de règlement à utiliser dans le cadre du règlement automatique"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_modes()



# ---------------------------------------------------------------------------------------------------------------------------------


class Dialog(DLG_Saisie_lot_tresor_public.Dialog):
    def __init__(self, parent, IDlot=None, format=None):
        DLG_Saisie_lot_tresor_public.Dialog.__init__(self, parent, IDlot=IDlot, format=format, ctrl_parametres=CTRL_Parametres)
        self.parent = parent


    def ValidationDonnees(self):
        """ Vérifie que les données saisies sont exactes """
        # Généralités
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de lot (Ex : 'Janvier 2013'...) !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
 
        for caract in nom :
            if caract in ("_",) :
                dlg = wx.MessageDialog(self, _(u"Le caractère '%s' n'est pas autorisé dans le nom du lot !") % caract, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_nom.SetFocus() 
                return False
       
        # Vérifie que le nom n'est pas déjà attribué
        if self.IDlot == None :
            IDlotTemp = 0
        else :
            IDlotTemp = self.IDlot
        DB = GestionDB.DB()
        req = """SELECT IDlot, nom
        FROM pes_lots
        WHERE nom='%s' AND IDlot!=%d;""" % (nom, IDlotTemp)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce nom de lot a déjà été attribué à un autre lot.\n\nChaque lot doit avoir un nom unique. Changez le nom."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
        
        observations = self.ctrl_observations.GetValue()
        
        if self.ctrl_verrouillage.GetValue() == True :
            verrouillage = 1
        else :
            verrouillage = 0

        # Récupération des données du CTRL Paramètres
        exercice = self.ctrl_parametres.GetPropertyValue("exercice")
        mois = self.ctrl_parametres.GetPropertyValue("mois")
        objet_dette = self.ctrl_parametres.GetPropertyValue("objet_dette")
        date_emission = self.ctrl_parametres.GetPropertyValue("date_emission")
        date_prelevement = self.ctrl_parametres.GetPropertyValue("date_prelevement")
        date_envoi = self.ctrl_parametres.GetPropertyValue("date_envoi")
        id_bordereau = self.ctrl_parametres.GetPropertyValue("id_bordereau")
        id_poste = self.ctrl_parametres.GetPropertyValue("id_poste")
        id_collectivite = self.ctrl_parametres.GetPropertyValue("id_collectivite")
        code_collectivite = self.ctrl_parametres.GetPropertyValue("code_collectivite")
        code_budget = self.ctrl_parametres.GetPropertyValue("code_budget")
        code_prodloc = self.ctrl_parametres.GetPropertyValue("code_prodloc")
        # code_etab = self.ctrl_parametres.GetPropertyValue("code_etab")
        reglement_auto = int(self.ctrl_parametres.GetPropertyValue("reglement_auto"))
        IDcompte = self.ctrl_parametres.GetPropertyValue("IDcompte")
        IDmode = self.ctrl_parametres.GetPropertyValue("IDmode")
        
        # Vérification du compte à créditer
        if reglement_auto == 1 :
            if IDcompte == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un compte à créditer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if IDmode == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un mode de règlement pour le règlement automatique !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Vérification des paramètres du bordereau
        listeVerifications = [
            (exercice, "exercice", _(u"l'année de l'exercice")),
            (mois, "mois", _(u"le mois")),
            (objet_dette, "objet_dette", _(u"l'objet de la dette")),
            (date_emission, "date_emission", _(u"la date d'émission")),
            (date_prelevement, "date_prelevement", _(u"la date souhaitée du prélèvement")),
            (date_envoi, "date_envoi", _(u"la date d'envoi")),
            (id_poste, "id_poste", _(u"l'article budgétaire")),
            (id_collectivite, "id_collectivite", _(u"l'ID collectivité")),
            (code_collectivite, "code_collectivite", _(u"le Code Collectivité")),
            (code_budget, "code_budget", _(u"le Code Bugdet")),
            (code_prodloc, "code_prodloc", _(u"le code Produit Local")),
            # (code_etab, "code_etab", _(u"le code Etablissement")),
            ]
            
        for donnee, code, label in listeVerifications :
            if donnee == None or donnee == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir %s dans les paramètres du lot !") % label, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if code == "id_collectivite" :
                try :
                    test = int(donnee) 
                except :
                    dlg = wx.MessageDialog(self, _(u"Vous devez saisir une valeur numérique valide pour le paramètre de bordereau 'ID Collectivité' !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        # Vérification des pièces
        listeErreurs = []
        listeTemp1 = []
        for track in self.ctrl_pieces.GetObjects() :

            if track.analysePiece == False :
                listeErreurs.append(_(u"- Facture n°%s : %s") % (track.IDfacture, track.analysePieceTexte))
                
            # Vérifie qu'un OOFF ou un FRST n'est pas attribué 2 fois à un seul mandat
            if track.prelevement == 1 :
                if track.prelevement_sequence in ("OOFF", "FRST") :
                    key = (track.prelevement_IDmandat, track.prelevement_sequence)
                    if key in listeTemp1 :
                        if track.prelevement_sequence == "OOFF" : 
                            listeErreurs.append(_(u"- Facture n°%s : Le mandat n°%s de type ponctuel a déjà été utilisé une fois !") % (track.IDfacture, track.prelevement_IDmandat))
                        if track.prelevement_sequence == "FRST" : 
                            listeErreurs.append(_(u"- Facture n°%s : Mandat n°%s déjà initialisé. La séquence doit être définie sur 'RCUR' !") % (track.IDfacture, track.prelevement_IDmandat))
                    listeTemp1.append(key)
            
        if len(listeErreurs) > 0 :
            message1 = _(u"Le bordereau ne peut être validé en raison des erreurs suivantes :")
            message2 = "\n".join(listeErreurs)
            dlg = dialogs.MultiMessageDialog(self, message1, caption=_(u"Erreur"), msg2=message2, style = wx.ICON_EXCLAMATION |wx.OK, icon=None, btnLabels={wx.ID_OK : _(u"Ok")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            return False

        return True

    def Memorisation_parametres(self):
        pass

    def OnBoutonFichier(self, event):
        """ Génération d'un fichier normalisé """
        # Validation des données
        if self.ValidationDonnees() == False:
            return False

        # Vérifie que des pièces existent
        if not(self.ctrl_pieces.GetObjects()):
            dlg = wx.MessageDialog(self, _(u"Vous devez ajouter au moins une pièce !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Récupération des infos sur la remise
        remise_nom = DLG_Saisie_lot_tresor_public.Supprime_accent(self.ctrl_nom.GetValue())
        nom_fichier = remise_nom

        nomOrganisateur = UTILS_Organisateur.GetNom()

        # Génération des pièces jointes
        dict_pieces_jointes = False

        # Récupération des transactions à effectuer
        montantTotal = FloatToDecimal(0.0)
        nbreTotal = 0
        listeAnomalies = []
        listePieces = []
        for track in self.ctrl_pieces.GetObjects():
            montant = FloatToDecimal(track.montant)

            if track.analysePiece == False:
                listeAnomalies.append(u"%s : %s" % (track.libelle, track.analysePieceTexte))

            # Objet de la pièce
            objet_piece = self.ctrl_parametres.GetPropertyValue("objet_piece")
            objet_piece = DLG_Saisie_lot_tresor_public.Supprime_accent(objet_piece).upper()
            objet_piece = objet_piece.replace("{NOM_ORGANISATEUR}", nomOrganisateur)
            objet_piece = objet_piece.replace("{NUM_FACTURE}", str(track.numero))
            objet_piece = objet_piece.replace("{LIBELLE_FACTURE}", track.libelle)
            objet_piece = objet_piece.replace("{MOIS}", str(self.ctrl_parametres.GetPropertyValue("mois")))
            objet_piece = objet_piece.replace("{MOIS_LETTRES}", DLG_Saisie_lot_tresor_public.GetMoisStr(self.ctrl_parametres.GetPropertyValue("mois"), majuscules=True, sansAccents=True))
            objet_piece = objet_piece.replace("{ANNEE}", str(self.ctrl_parametres.GetPropertyValue("exercice")))

            # Création du libellé du prélèvement
            prelevement_libelle = self.ctrl_parametres.GetPropertyValue("prelevement_libelle")
            prelevement_libelle = prelevement_libelle.replace("{NOM_ORGANISATEUR}", nomOrganisateur)
            prelevement_libelle = prelevement_libelle.replace("{OBJET_PIECE}", objet_piece)
            prelevement_libelle = prelevement_libelle.replace("{LIBELLE_FACTURE}", track.libelle)
            prelevement_libelle = prelevement_libelle.replace("{NUM_FACTURE}", str(track.numero))
            prelevement_libelle = prelevement_libelle.replace("{MOIS}", str(self.ctrl_parametres.GetPropertyValue("mois")))
            prelevement_libelle = prelevement_libelle.replace("{MOIS_LETTRES}", DLG_Saisie_lot_tresor_public.GetMoisStr(self.ctrl_parametres.GetPropertyValue("mois"), majuscules=True, sansAccents=True))
            prelevement_libelle = prelevement_libelle.replace("{ANNEE}", str(self.ctrl_parametres.GetPropertyValue("exercice")))

            # Création du nom de la collectivité
            nom_collectivite = self.ctrl_parametres.GetPropertyValue("nom_collectivite")
            nom_collectivite = nom_collectivite.replace("{NOM_ORGANISATEUR}", nomOrganisateur)

            dictPiece = {
                "id_piece": str(track.IDfacture),
                "objet_piece": objet_piece,
                "num_dette": str(track.numero),
                "montant": str(montant),
                "sequence": track.prelevement_sequence,
                "prelevement": track.prelevement,
                "prelevement_date_mandat": str(track.prelevement_date_mandat),
                "prelevement_rum": track.prelevement_rum,
                "prelevement_bic": track.prelevement_bic,
                "prelevement_iban": track.prelevement_iban,
                "prelevement_titulaire": track.prelevement_titulaire,
                "prelevement_libelle": prelevement_libelle,
                "titulaire_civilite": track.titulaireCivilite,
                "titulaire_nom": track.titulaireNom,
                "titulaire_prenom": track.titulairePrenom,
                "titulaire_rue": track.titulaireRue,
                "titulaire_cp": track.titulaireCP,
                "titulaire_ville": track.titulaireVille,
                "idtiers_helios": track.idtiers_helios,
                "natidtiers_helios": track.natidtiers_helios,
                "reftiers_helios": track.reftiers_helios,
                "cattiers_helios": track.cattiers_helios,
                "natjur_helios": track.natjur_helios,
                "IDfacture" : track.IDfacture,
                "track": track,
            }
            listePieces.append(dictPiece)
            montantTotal += montant
            nbreTotal += 1

        # Mémorisation de tous les données
        dictDonnees = {
            "nom_fichier": nom_fichier,
            "date_emission": UTILS_Dates.ConvertDateWXenDate(self.ctrl_parametres.GetPropertyValue("date_emission")).strftime("%Y-%m-%d"),
            "date_envoi": UTILS_Dates.ConvertDateWXenDate(self.ctrl_parametres.GetPropertyValue("date_envoi")).strftime("%Y-%m-%d"),
            "date_prelevement": UTILS_Dates.ConvertDateWXenDate(self.ctrl_parametres.GetPropertyValue("date_prelevement")).strftime("%Y-%m-%d"),
            "id_poste": self.ctrl_parametres.GetPropertyValue("id_poste"),
            "id_collectivite": self.ctrl_parametres.GetPropertyValue("id_collectivite"),
            "code_collectivite": self.ctrl_parametres.GetPropertyValue("code_collectivite"),
            "code_budget": self.ctrl_parametres.GetPropertyValue("code_budget"),
            "exercice": str(self.ctrl_parametres.GetPropertyValue("exercice")),
            "mois": str(self.ctrl_parametres.GetPropertyValue("mois")),
            "id_bordereau": self.ctrl_parametres.GetPropertyValue("id_bordereau"),
            "montant_total": str(montantTotal),
            "objet_dette": self.ctrl_parametres.GetPropertyValue("objet_dette"),
            "code_prodloc": self.ctrl_parametres.GetPropertyValue("code_prodloc"),
            # "code_etab": self.ctrl_parametres.GetPropertyValue("code_etab"),
            "nom_collectivite": nom_collectivite,
            "pieces": listePieces,
            "pieces_jointes" : dict_pieces_jointes,
        }

        if len(listeAnomalies) > 0:
            import wx.lib.dialogs as dialogs
            message = "\n".join(listeAnomalies)
            dlg = dialogs.MultiMessageDialog(self, _(u"Le fichier ne peut être généré en raison des anomalies suivantes :"), caption=_(u"Génération impossible"), msg2=message, style=wx.ICON_ERROR | wx.OK, icon=None, btnLabels={wx.ID_OK: _(u"Fermer")})
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Génération du fichier XML
        doc = UTILS_Jvs.GetXML(dictDonnees)
        xml = doc.toprettyxml(encoding="utf-8")

        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        wildcard = "Fichier XML (*.xml)|*.xml| All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message=_(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"),
            defaultDir=cheminDefaut,
            defaultFile=nom_fichier,
            wildcard=wildcard,
            style=wx.FD_SAVE
        )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True:
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), _(u"Attention !"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO:
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Création du fichier texte
        f = open(cheminFichier, "w")
        try:
            if six.PY2:
                f.write(doc.toxml(encoding="ISO-8859-1"))
            else:
                #f.write(doc.toprettyxml(indent="  "))
                f.write(doc.toxml())
        finally:
            f.close()

        # Confirmation de création du fichier et demande d'ouverture directe
        txtMessage = _(u"Le fichier d'export a été créé avec succès.\n\nSouhaitez-vous visualiser son contenu maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)

    def GenerationPiecesJointes(self):
        """ Génération des pièces jointes """
        IDfichier = FonctionsPerso.GetIDfichier()

        listeIDfacture = []
        dictTracks = {}
        for track in self.ctrl_pieces.GetObjects():
            listeIDfacture.append(track.IDfacture)
            dictTracks[track.IDfacture] = track

        # Génération des factures au format PDF
        nomFichierUnique = self.ctrl_parametres.GetPropertyValue("format_nom_fichier")

        facturation = UTILS_Facturation.Facturation()
        resultat = facturation.Impression(listeFactures=listeIDfacture, nomFichierUnique=nomFichierUnique, afficherDoc=False, repertoireTemp=True)
        if resultat == False:
            return False
        dictChampsFusion, dictPieces = resultat

        # Conversion des fichiers en GZIP/base64
        dict_pieces_jointes = {}
        for IDfacture, cheminFichier in dictPieces.items() :

            # Compression GZIP
            cheminFichierGzip = cheminFichier + ".zip"
            with open(cheminFichier, 'rb') as f_in, gzip.open(cheminFichierGzip, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

            # Encodage en base64
            with open(cheminFichierGzip, "rb") as fichier:
                contenu = base64.b64encode(fichier.read())

            # Suppression des fichiers temporaires
            os.remove(cheminFichier)
            os.remove(cheminFichierGzip)

            # Mémorisation des pièces jointes
            NomPJ = os.path.basename(cheminFichier)
            numero_facture = dictTracks[IDfacture].numero
            IdUnique = IDfichier + str(numero_facture)

            dict_pieces_jointes[IDfacture] = {"NomPJ" : NomPJ, "IdUnique" : IdUnique, "contenu" : contenu, "numero_facture" : numero_facture}

        return dict_pieces_jointes







if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDlot=1, format="jvs")
    filtres = [
        {"type": "numero_intervalle", "numero_min": 1983, "numero_max": 2051},
    ]
    dlg.Assistant(filtres=filtres, nomLot="Nom de lot exemple")
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
