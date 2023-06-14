#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
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
import os, calendar
import six
import GestionDB
import datetime
import gzip
import shutil
import base64
import os.path
import wx.propgrid as wxpg
from Ctrl.CTRL_Propertygrid import Propriete_date
from Utils import UTILS_Dates, UTILS_Fichiers, UTILS_Corail
import FonctionsPerso
import wx.lib.dialogs as dialogs
from Dlg import DLG_Messagebox
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
from Utils import UTILS_Facturation, UTILS_Organisateur, UTILS_Parametres, UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

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
        propriete.SetHelpString(_(u"Saisissez l'ann�e de l'exercice")) 
        self.Append(propriete)
        self.SetPropertyEditor("exercice", "SpinCtrl")
        
        listeMois = [u"_", _(u"Janvier"), _(u"F�vrier"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Ao�t"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"D�cembre")]
        propriete = wxpg.EnumProperty(label=_(u"Mois"), name="mois", labels=listeMois, values=range(0, 13) , value=datetime.date.today().month)
        propriete.SetHelpString(_(u"S�lectionnez le mois")) 
        self.Append(propriete)
        
        propriete = wxpg.StringProperty(label=_(u"Objet"), name="objet_dette", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'objet du bordereau (Ex : 'Centre de Loisirs')")) 
        self.Append(propriete)

        # Dates
        self.Append( wxpg.PropertyCategory(_(u"Dates")) )

        propriete = Propriete_date(label=_(u"Date d'�mission (JJ/MM/AAAA)"), name="date_emission", value=datetime.date.today())
        self.Append(propriete)

        propriete = Propriete_date(label=_(u"Date du pr�l�vement (JJ/MM/AAAA)"), name="date_prelevement", value=datetime.date.today())
        self.Append(propriete)

        # Collectivit�
        self.Append( wxpg.PropertyCategory(_(u"Identification")) )
        
        propriete = wxpg.StringProperty(label=_(u"Article budg�taire"), name="id_poste", value=u"")
        propriete.SetHelpString(_(u"Saisissez l'article budg�taire (Nature)"))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Fonction"), name="fonction", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code de la fonction."))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Code analytique 1"), name="code_analytique_1", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code analytique 1."))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Code analytique 2"), name="code_analytique_2", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code analytique 2."))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Code Produit Local"), name="code_prodloc", value=u"")
        propriete.SetHelpString(_(u"Saisissez le code Produit Local")) 
        self.Append(propriete)

        # Options
        self.Append(wxpg.PropertyCategory(_(u"Options")))

        propriete = wxpg.BoolProperty(label=_(u"Inclure le d�tail des factures"), name="inclure_detail", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys int�gre le d�tail des prestations de chaque facture"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        propriete = wxpg.BoolProperty(label=_(u"Inclure les factures au format PDF"), name="inclure_pieces_jointes", value=True)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys int�gre les factures au format PDF"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Libell�s
        self.Append( wxpg.PropertyCategory(_(u"Libell�s")) )

        propriete = wxpg.StringProperty(label=_(u"Objet de la pi�ce"), name="objet_piece", value=_(u"FACTURE NUM{NUM_FACTURE} {MOIS_LETTRES} {ANNEE}"))
        propriete.SetHelpString(_(u"Saisissez l'objet de la pi�ce (en majuscules et sans accents). Vous pouvez personnaliser ce libell� gr�ce aux mots-cl�s suivants : {NOM_ORGANISATEUR} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE} {DATE_EMISSION}."))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Libell� de la prestation"), name="prestation_libelle", value=_(u"{INDIVIDU_PRENOM} - {PRESTATION_LABEL}"))
        propriete.SetHelpString(_(u"Saisissez le libell� de la prestation (d�tail ASAP). Vous pouvez personnaliser ce libell� gr�ce aux mots-cl�s suivants : {PRESTATION_LABEL} {PRESTATION_DATE} {INDIVIDU_PRENOM} {INDIVIDU_NOM} {MOIS} {MOIS_LETTRES} {ANNEE} {DATE_EMISSION} {OBJET}."))
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Libell� du pr�l�vement"), name="prelevement_libelle", value=u"{NOM_ORGANISATEUR} - {OBJET_PIECE}")
        propriete.SetHelpString(_(u"Saisissez le libell� du pr�l�vement qui appara�tra sur le relev� de compte de la famille. Vous pouvez personnaliser ce libell� gr�ce aux mots-cl�s suivants : {NOM_ORGANISATEUR} {OBJET_PIECE} {NUM_FACTURE} {LIBELLE_FACTURE} {MOIS} {MOIS_LETTRES} {ANNEE}.")) 
        self.Append(propriete)

        propriete = wxpg.StringProperty(label=_(u"Nom de la collectivit�"), name="nom_collectivite", value=u"{NOM_ORGANISATEUR}")
        propriete.SetHelpString(_(u"Saisissez le nom de la collectivit�. A d�faut, c'est le nom de l'organisateur qui sera ins�r� automatiquement."))
        self.Append(propriete)

        # R�glement automatique
        self.Append( wxpg.PropertyCategory(_(u"R�glement automatique")) )
        
        propriete = wxpg.BoolProperty(label=_(u"R�gler automatiquement"), name="reglement_auto", value=False)
        propriete.SetHelpString(_(u"Cochez cette case si vous souhaitez que Noethys cr�� un r�glement automatiquement pour les pr�l�vements")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)
        
        propriete = wxpg.EnumProperty(label=_(u"Compte � cr�diter"), name="IDcompte")
        propriete.SetHelpString(_(u"S�lectionnez le compte bancaire � cr�diter dans le cadre du r�glement automatique"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_comptes() 

        propriete = wxpg.EnumProperty(label=_(u"Mode de r�glement"), name="IDmode")
        propriete.SetHelpString(_(u"S�lectionnez le mode de r�glement � utiliser dans le cadre du r�glement automatique"))
        propriete.SetEditor("EditeurComboBoxAvecBoutons")
        self.Append(propriete)
        self.MAJ_modes()

        # Pr�f�rences
        self.SetPropertyValue("fonction", UTILS_Parametres.Parametres(mode="get", categorie="export_corail", nom="fonction", valeur=""))
        self.SetPropertyValue("code_analytique_1", UTILS_Parametres.Parametres(mode="get", categorie="export_corail", nom="code_analytique_1", valeur=""))
        self.SetPropertyValue("code_analytique_2", UTILS_Parametres.Parametres(mode="get", categorie="export_corail", nom="code_analytique_2", valeur=""))
        self.SetPropertyValue("inclure_pieces_jointes", UTILS_Parametres.Parametres(mode="get", categorie="export_corail", nom="inclure_pieces_jointes", valeur=True))
        self.SetPropertyValue("inclure_detail", UTILS_Parametres.Parametres(mode="get", categorie="export_corail", nom="inclure_detail", valeur=True))
        self.SetPropertyValue("prestation_libelle", UTILS_Parametres.Parametres(mode="get", categorie="export_corail", nom="prestation_libelle", valeur=u"{INDIVIDU_PRENOM} - {PRESTATION_LABEL}"))


# ---------------------------------------------------------------------------------------------------------------------------------


class Dialog(DLG_Saisie_lot_tresor_public.Dialog):
    def __init__(self, parent, IDlot=None, format=None):
        DLG_Saisie_lot_tresor_public.Dialog.__init__(self, parent, IDlot=IDlot, format=format, ctrl_parametres=CTRL_Parametres)
        self.parent = parent


    def ValidationDonnees(self):
        """ V�rifie que les donn�es saisies sont exactes """
        # G�n�ralit�s
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de lot (Ex : 'Janvier 2013'...) !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
 
        for caract in nom :
            if caract in ("_",) :
                dlg = wx.MessageDialog(self, _(u"Le caract�re '%s' n'est pas autoris� dans le nom du lot !") % caract, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_nom.SetFocus() 
                return False
       
        # V�rifie que le nom n'est pas d�j� attribu�
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
            dlg = wx.MessageDialog(self, _(u"Ce nom de lot a d�j� �t� attribu� � un autre lot.\n\nChaque lot doit avoir un nom unique. Changez le nom."), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus() 
            return False
        
        observations = self.ctrl_observations.GetValue()
        
        if self.ctrl_verrouillage.GetValue() == True :
            verrouillage = 1
        else :
            verrouillage = 0

        # R�cup�ration des donn�es du CTRL Param�tres
        exercice = self.ctrl_parametres.GetPropertyValue("exercice")
        mois = self.ctrl_parametres.GetPropertyValue("mois")
        objet_dette = self.ctrl_parametres.GetPropertyValue("objet_dette")
        date_emission = self.ctrl_parametres.GetPropertyValue("date_emission")
        date_prelevement = self.ctrl_parametres.GetPropertyValue("date_prelevement")
        id_poste = self.ctrl_parametres.GetPropertyValue("id_poste")
        fonction = self.ctrl_parametres.GetPropertyValue("fonction")
        code_analytique_1 = self.ctrl_parametres.GetPropertyValue("code_analytique_1")
        code_analytique_2 = self.ctrl_parametres.GetPropertyValue("code_analytique_2")
        code_prodloc = self.ctrl_parametres.GetPropertyValue("code_prodloc")
        reglement_auto = int(self.ctrl_parametres.GetPropertyValue("reglement_auto"))
        IDcompte = self.ctrl_parametres.GetPropertyValue("IDcompte")
        IDmode = self.ctrl_parametres.GetPropertyValue("IDmode")
        
        # V�rification du compte � cr�diter
        if reglement_auto == 1 :
            if IDcompte == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un compte � cr�diter !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            if IDmode == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un mode de r�glement pour le r�glement automatique !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # V�rification des param�tres du bordereau
        listeVerifications = [
            (exercice, "exercice", _(u"l'ann�e de l'exercice")),
            (mois, "mois", _(u"le mois")),
            (objet_dette, "objet_dette", _(u"l'objet de la dette")),
            (date_emission, "date_emission", _(u"la date d'�mission")),
            (date_prelevement, "date_prelevement", _(u"la date souhait�e du pr�l�vement")),
            (id_poste, "id_poste", _(u"l'article budg�taire")),
            (code_prodloc, "code_prodloc", _(u"le code Produit Local")),
            ]
            
        for donnee, code, label in listeVerifications :
            if donnee == None or donnee == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir %s dans les param�tres du lot !") % label, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if code == "id_collectivite" :
                try :
                    test = int(donnee) 
                except :
                    dlg = wx.MessageDialog(self, _(u"Vous devez saisir une valeur num�rique valide pour le param�tre de bordereau 'ID Collectivit�' !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        # V�rification des pi�ces
        listeErreurs = []
        listeTemp1 = []
        for track in self.ctrl_pieces.GetObjects() :

            if track.analysePiece == False :
                listeErreurs.append(_(u"- Facture n�%s : %s") % (track.IDfacture, track.analysePieceTexte))
                
            # V�rifie qu'un OOFF ou un FRST n'est pas attribu� 2 fois � un seul mandat
            if track.prelevement == 1 :
                if track.prelevement_sequence in ("OOFF", "FRST") :
                    key = (track.prelevement_IDmandat, track.prelevement_sequence)
                    if key in listeTemp1 :
                        if track.prelevement_sequence == "OOFF" : 
                            listeErreurs.append(_(u"- Facture n�%s : Le mandat n�%s de type ponctuel a d�j� �t� utilis� une fois !") % (track.IDfacture, track.prelevement_IDmandat))
                        if track.prelevement_sequence == "FRST" : 
                            listeErreurs.append(_(u"- Facture n�%s : Mandat n�%s d�j� initialis�. La s�quence doit �tre d�finie sur 'RCUR' !") % (track.IDfacture, track.prelevement_IDmandat))
                    listeTemp1.append(key)
            
        if len(listeErreurs) > 0 :
            message1 = _(u"Le bordereau ne peut �tre valid� en raison des erreurs suivantes :")
            message2 = "\n".join(listeErreurs)
            dlg = dialogs.MultiMessageDialog(self, message1, caption=_(u"Erreur"), msg2=message2, style = wx.ICON_EXCLAMATION |wx.OK, icon=None, btnLabels={wx.ID_OK : _(u"Ok")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            return False

        return True

    def Memorisation_parametres(self):
        # M�morisation des pr�f�rences
        for code in ("fonction", "code_analytique_1", "code_analytique_2", "inclure_detail", "inclure_pieces_jointes", "prestation_libelle"):
            UTILS_Parametres.Parametres(mode="set", categorie="export_corail", nom=code, valeur=self.ctrl_parametres.GetPropertyValue(code))

    def OnBoutonFichier(self, event):
        """ G�n�ration d'un fichier normalis� """
        # Validation des donn�es
        if self.ValidationDonnees() == False:
            return False

        # V�rifie que des pi�ces existent
        if not(self.ctrl_pieces.GetObjects()):
            dlg = wx.MessageDialog(self, _(u"Vous devez ajouter au moins une pi�ce !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # R�cup�ration des infos sur la remise
        remise_nom = DLG_Saisie_lot_tresor_public.Supprime_accent(self.ctrl_nom.GetValue())
        nom_fichier = remise_nom

        nomOrganisateur = UTILS_Organisateur.GetNom()

        # Cr�ation d'un r�pertoire temporaire
        rep_temp = UTILS_Fichiers.GetRepTemp("export_corail")
        if os.path.isdir(rep_temp):
            shutil.rmtree(rep_temp)
        os.mkdir(rep_temp)

        # G�n�ration des pi�ces jointes
        dict_pieces_jointes = {}
        if self.ctrl_parametres.GetPropertyValue("inclure_pieces_jointes") == True :
            dict_pieces_jointes = self.GenerationPiecesJointes(repertoire=rep_temp)
            if not dict_pieces_jointes:
                return False

        # R�cup�ration des transactions � effectuer
        montantTotal = FloatToDecimal(0.0)
        nbreTotal = 0
        listeAnomalies = []
        listePieces = []
        for track in self.ctrl_pieces.GetObjects():
            montant = FloatToDecimal(track.montant)

            if track.analysePiece == False:
                listeAnomalies.append(u"%s : %s" % (track.libelle, track.analysePieceTexte))

            # Objet de la pi�ce
            objet_piece = self.ctrl_parametres.GetPropertyValue("objet_piece")
            objet_piece = DLG_Saisie_lot_tresor_public.Supprime_accent(objet_piece).upper()
            objet_piece = objet_piece.replace("{NOM_ORGANISATEUR}", nomOrganisateur)
            objet_piece = objet_piece.replace("{NUM_FACTURE}", str(track.numero))
            objet_piece = objet_piece.replace("{LIBELLE_FACTURE}", track.libelle)
            objet_piece = objet_piece.replace("{MOIS}", str(self.ctrl_parametres.GetPropertyValue("mois")))
            objet_piece = objet_piece.replace("{MOIS_LETTRES}", DLG_Saisie_lot_tresor_public.GetMoisStr(self.ctrl_parametres.GetPropertyValue("mois"), majuscules=True, sansAccents=True))
            objet_piece = objet_piece.replace("{ANNEE}", str(self.ctrl_parametres.GetPropertyValue("exercice")))
            objet_piece = objet_piece.replace("{DATE_EMISSION}", UTILS_Dates.ConvertDateWXenDate(self.ctrl_parametres.GetPropertyValue("date_emission")).strftime("%d/%m/%Y"))

            # Cr�ation du libell� du pr�l�vement
            prelevement_libelle = self.ctrl_parametres.GetPropertyValue("prelevement_libelle")
            prelevement_libelle = prelevement_libelle.replace("{NOM_ORGANISATEUR}", nomOrganisateur)
            prelevement_libelle = prelevement_libelle.replace("{OBJET_PIECE}", objet_piece)
            prelevement_libelle = prelevement_libelle.replace("{LIBELLE_FACTURE}", track.libelle)
            prelevement_libelle = prelevement_libelle.replace("{NUM_FACTURE}", str(track.numero))
            prelevement_libelle = prelevement_libelle.replace("{MOIS}", str(self.ctrl_parametres.GetPropertyValue("mois")))
            prelevement_libelle = prelevement_libelle.replace("{MOIS_LETTRES}", DLG_Saisie_lot_tresor_public.GetMoisStr(self.ctrl_parametres.GetPropertyValue("mois"), majuscules=True, sansAccents=True))
            prelevement_libelle = prelevement_libelle.replace("{ANNEE}", str(self.ctrl_parametres.GetPropertyValue("exercice")))

            # Cr�ation du nom de la collectivit�
            nom_collectivite = self.ctrl_parametres.GetPropertyValue("nom_collectivite")
            nom_collectivite = nom_collectivite.replace("{NOM_ORGANISATEUR}", nomOrganisateur)

            dictPiece = {
                "id_piece": str(track.IDfacture),
                "objet_piece": objet_piece,
                "num_dette": str(track.numero),
                "montant": str(montant),
                "sequence": track.prelevement_sequence,
                "prelevement": track.prelevement,
                "prelevement_date_mandat": str(track.prelevement_date_mandat).replace("-", "") if track.prelevement_date_mandat else "",
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
                "tiersSolidaire_civilite": track.tiersSolidaireCivilite,
                "tiersSolidaire_nom": track.tiersSolidaireNom,
                "tiersSolidaire_prenom": track.tiersSolidairePrenom,
                "tiersSolidaire_rue": track.tiersSolidaireRue,
                "tiersSolidaire_cp": track.tiersSolidaireCP,
                "tiersSolidaire_ville": track.tiersSolidaireVille,
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

        # M�morisation de toutes les donn�es
        dictDonnees = {
            "nom_fichier": nom_fichier,
            "date_emission": UTILS_Dates.ConvertDateWXenDate(self.ctrl_parametres.GetPropertyValue("date_emission")).strftime("%Y%m%d"),
            "date_prelevement": UTILS_Dates.ConvertDateWXenDate(self.ctrl_parametres.GetPropertyValue("date_prelevement")).strftime("%Y%m%d"),
            "id_poste": self.ctrl_parametres.GetPropertyValue("id_poste"),
            "fonction": self.ctrl_parametres.GetPropertyValue("fonction"),
            "code_analytique_1": self.ctrl_parametres.GetPropertyValue("code_analytique_1"),
            "code_analytique_2": self.ctrl_parametres.GetPropertyValue("code_analytique_2"),
            "inclure_detail": self.ctrl_parametres.GetPropertyValue("inclure_detail"),
            "inclure_pieces_jointes": self.ctrl_parametres.GetPropertyValue("inclure_pieces_jointes"),
            "exercice": str(self.ctrl_parametres.GetPropertyValue("exercice")),
            "mois": str(self.ctrl_parametres.GetPropertyValue("mois")),
            "montant_total": str(montantTotal),
            "objet_dette": self.ctrl_parametres.GetPropertyValue("objet_dette"),
            "code_prodloc": self.ctrl_parametres.GetPropertyValue("code_prodloc"),
            "nom_collectivite": nom_collectivite,
            "prestation_libelle": self.ctrl_parametres.GetPropertyValue("prestation_libelle"),
            "pieces": listePieces,
            "pieces_jointes" : dict_pieces_jointes,
        }

        if len(listeAnomalies) > 0:
            import wx.lib.dialogs as dialogs
            message = "\n".join(listeAnomalies)
            dlg = dialogs.MultiMessageDialog(self, _(u"Le fichier ne peut �tre g�n�r� en raison des anomalies suivantes :"), caption=_(u"G�n�ration impossible"), msg2=message, style=wx.ICON_ERROR | wx.OK, icon=None, btnLabels={wx.ID_OK: _(u"Fermer")})
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Calcul des dates extr�mes du mois
        nbreJoursMois = calendar.monthrange(int(dictDonnees["exercice"]), int(dictDonnees["mois"]))[1]
        dictDonnees["date_min"] = datetime.date(int(dictDonnees["exercice"]), int(dictDonnees["mois"]), 1)
        dictDonnees["date_max"] = datetime.date(int(dictDonnees["exercice"]), int(dictDonnees["mois"]), nbreJoursMois)

        # R�cup�ration du d�tail des factures
        detail_factures, dict_prestations_factures = self.Get_detail_pieces(dictDonnees)
        dictDonnees["detail"] = detail_factures
        dictDonnees["prestations"] = dict_prestations_factures

        # G�n�ration du fichier XML
        doc = UTILS_Corail.GetXML(dictDonnees)
        f = open(os.path.join(rep_temp, nom_fichier + ".xml"), "w")
        try:
            f.write(doc.toprettyxml(indent="  ", encoding="UTF-8"))
        finally:
            f.close()

        # Demande � l'utilisateur le nom de fichier et le r�pertoire de destination
        wildcard = "Fichier ZIP (*.zip)|*.zip| All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message=_(u"Veuillez s�lectionner le r�pertoire de destination et le nom du fichier"),
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

        # Le fichier de destination existe d�j� :
        if os.path.isfile(cheminFichier) == True:
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe d�j�. \n\nVoulez-vous le remplacer ?"), _(u"Attention !"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO:
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Cr�ation du fichier ZIP
        shutil.make_archive(cheminFichier.replace(".zip", ""), "zip", rep_temp)

        # Confirmation de cr�ation du fichier
        dlg = wx.MessageDialog(self, _(u"Le fichier a �t� cr�� avec succ�s.\n\nPensez � d�compresser ce fichier avant l'import dans Corail."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def Get_detail_pieces(self, dict_donnees={}):
        listeIDfacture = [piece["IDfacture"] for piece in dict_donnees["pieces"]]

        if len(listeIDfacture) == 0: conditionFactures = "()"
        elif len(listeIDfacture) == 1: conditionFactures = "(%d)" % listeIDfacture[0]
        else: conditionFactures = str(tuple(listeIDfacture))

        DB = GestionDB.DB()
        req = """SELECT 
        prestations.IDprestation, prestations.date, prestations.montant, prestations.IDfacture, prestations.label,
        prestations.IDindividu, individus.nom, individus.prenom,
        SUM(ventilation.montant) AS montant_ventilation,
        prestations.code_compta, prestations.code_produit_local,
        activites.code_comptable, activites.code_produit_local
        FROM prestations
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        LEFT JOIN ventilation ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        WHERE prestations.IDfacture IN %s
        GROUP BY prestations.IDprestation
        ;""" % conditionFactures
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dict_resultats = {}
        dict_prestations_factures = {}
        for IDprestation, date, montant, IDfacture, label, IDindividu, nom, prenom, montant_ventilation, code_compta, code_produit_local, activite_code_compta, activite_code_produit_local in listeDonnees:
            montant = FloatToDecimal(montant)

            # Recherche le code compta et le code prod local
            id_poste = dict_donnees["id_poste"]
            code_prodloc = dict_donnees["code_prodloc"]
            if activite_code_compta: id_poste = activite_code_compta
            if activite_code_produit_local: code_prodloc = activite_code_produit_local
            if code_compta: id_poste = code_compta
            if code_produit_local: code_prodloc = code_produit_local

            if IDfacture not in dict_prestations_factures:
                dict_prestations_factures[IDfacture] = []
            dict_prestations_factures[IDfacture].append({"IDprestation": IDprestation, "label": label, "montant": montant, "id_poste": id_poste, "code_prodloc": code_prodloc})

            # D�finit le label
            prestation_libelle = dict_donnees["prestation_libelle"]
            prestation_libelle = prestation_libelle.replace("{PRESTATION_LABEL}", label)
            prestation_libelle = prestation_libelle.replace("{PRESTATION_DATE}", UTILS_Dates.DateEngFr(date))
            prestation_libelle = prestation_libelle.replace("{INDIVIDU_PRENOM}", prenom or "")
            prestation_libelle = prestation_libelle.replace("{INDIVIDU_NOM}", nom or "")
            prestation_libelle = prestation_libelle.replace("{MOIS}", str(self.ctrl_parametres.GetPropertyValue("mois")))
            prestation_libelle = prestation_libelle.replace("{MOIS_LETTRES}", DLG_Saisie_lot_tresor_public.GetMoisStr(self.ctrl_parametres.GetPropertyValue("mois"), majuscules=True, sansAccents=True))
            prestation_libelle = prestation_libelle.replace("{ANNEE}", str(self.ctrl_parametres.GetPropertyValue("exercice")))
            prestation_libelle = prestation_libelle.replace("{DATE_EMISSION}", UTILS_Dates.ConvertDateWXenDate(self.ctrl_parametres.GetPropertyValue("date_emission")).strftime("%d/%m/%Y"))
            prestation_libelle = prestation_libelle.replace("{OBJET}", dict_donnees["objet_dette"])

            libelle = (prestation_libelle, montant)

            if IDfacture not in dict_resultats:
                dict_resultats[IDfacture] = {}
            if IDindividu not in dict_resultats[IDfacture]:
                dict_resultats[IDfacture][IDindividu] = {}
            if libelle not in dict_resultats[IDfacture][IDindividu]:
                dict_resultats[IDfacture][IDindividu][libelle] = 0
            dict_resultats[IDfacture][IDindividu][libelle] += 1

        dict_resultats2 = {}
        for IDfacture, dict_facture in dict_resultats.items():
            if IDfacture not in dict_resultats2:
                dict_resultats2[IDfacture] = []
            for IDindividu, dict_individu in dict_facture.items():
                for (libelle, montant), quantite in dict_individu.items():
                    dict_resultats2[IDfacture].append({"libelle": libelle, "quantite": quantite, "montant": montant})
                dict_resultats2[IDfacture].sort(key=lambda x: x["libelle"])

        return dict_resultats2, dict_prestations_factures

    def GenerationPiecesJointes(self, repertoire=""):
        """ G�n�ration des pi�ces jointes """
        IDfichier = FonctionsPerso.GetIDfichier()

        listeIDfacture = []
        dictTracks = {}
        for track in self.ctrl_pieces.GetObjects():
            listeIDfacture.append(track.IDfacture)
            dictTracks[track.IDfacture] = track

        # Cr�ation du r�pertoire
        repertoire_pj = os.path.join(UTILS_Fichiers.GetRepTemp("export_corail"), "PJ")
        if not os.path.isdir(repertoire_pj):
            os.mkdir(repertoire_pj)

        # G�n�ration des factures au format PDF
        nomFichierUnique = u"F{NUM_FACTURE}_{NOM_TITULAIRES_MAJ}"

        facturation = UTILS_Facturation.Facturation()
        resultat = facturation.Impression(listeFactures=listeIDfacture, nomFichierUnique=nomFichierUnique, afficherDoc=False, repertoireTemp=True)
        if resultat == False:
            return False
        dictChampsFusion, dictPieces = resultat

        # Conversion des fichiers en GZIP/base64
        dict_pieces_jointes = {}
        for IDfacture, cheminFichier in dictPieces.items() :
            NomPJ = os.path.basename(cheminFichier)
            numero_facture = dictTracks[IDfacture].numero
            IdUnique = IDfichier + str(numero_facture)
            shutil.move(cheminFichier, os.path.join(repertoire_pj, NomPJ))

            dict_pieces_jointes[IDfacture] = {"NomPJ": NomPJ, "IdUnique": IdUnique, "numero_facture": numero_facture}

        return dict_pieces_jointes






if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDlot=1, format="corail")
    filtres = [
        {"type": "numero_intervalle", "numero_min": 1983, "numero_max": 2051},
    ]
    dlg.Assistant(filtres=filtres, nomLot="Nom de lot exemple")
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
