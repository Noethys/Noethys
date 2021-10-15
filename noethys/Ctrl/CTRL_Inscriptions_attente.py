#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime
import copy
import sys
import os

import GestionDB
from Ctrl import CTRL_Saisie_euros
import FonctionsPerso
from Utils import UTILS_Organisateur
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Dates
from Utils import UTILS_Divers

COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)


            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, liste_activites=[], mode="attente"):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.liste_activites = liste_activites
        self.mode = mode

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        self.listeTracks = []
        self.listeImpression = []
                
        # Création des colonnes
        listeColonnes = [
            (_(u"Activité/Groupe/Individu"), 250, wx.ALIGN_LEFT),
            (_(u"Date de la réservation"), 200, wx.ALIGN_LEFT),
            (_(u"Catégorie de tarif"), 200, wx.ALIGN_LEFT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        # Création de l'ImageList
        il = wx.ImageList(16, 16)
        self.img_ok = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Ok.png'), wx.BITMAP_TYPE_PNG))
        self.img_pasok = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Interdit.png'), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

        # Binds
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
        
        self.MAJ()

    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()

    def Importation(self):
        # Conditions Activités
        if self.liste_activites == None:
            conditionActivites = "IDactivite > 0"
        else :
            if len(self.liste_activites) == 0 : conditionActivites = "IDactivite IN ()"
            elif len(self.liste_activites) == 1 : conditionActivites = "IDactivite=%d" % self.liste_activites[0]
            else : conditionActivites = "IDactivite IN %s" % str(tuple(self.liste_activites))

        # Importation des inscriptions en attente
        DB = GestionDB.DB()

        req = """
        SELECT IDinscription, date_inscription, categories_tarifs.nom,
        inscriptions.IDindividu, individus.nom, individus.prenom,
        inscriptions.IDactivite, activites.nom, inscriptions.IDgroupe, groupes.nom,
        inscriptions.IDcompte_payeur, inscriptions.IDfamille
        FROM inscriptions
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = inscriptions.IDgroupe
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
        WHERE inscriptions.statut='%s' AND inscriptions.%s
        ORDER BY IDinscription
        ;""" % (self.mode, conditionActivites)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()

        dictInscriptions = {}
        dictGroupes = {}
        for IDinscription, date_inscription, nomCategorie, IDindividu, nomIndividu, prenomIndividu, IDactivite, nomActivite, IDgroupe, nomGroupe, IDcompte_payeur, IDfamille in listeDonnees :
            date_inscription = UTILS_Dates.DateEngEnDateDD(date_inscription)
            if prenomIndividu == None : prenomIndividu = ""
            nom_individu = u"%s %s" % (nomIndividu, prenomIndividu)

            UTILS_Divers.DictionnaireImbrique(dictionnaire=dictInscriptions, cles=[IDactivite, IDgroupe], valeur=[])
            dictTemp = {
                "IDinscription" : IDinscription, "IDindividu" : IDindividu, "nom_individu" : nom_individu, "date_inscription" : date_inscription,
                "IDactivite" : IDactivite, "IDgroupe" : IDgroupe, "IDcompte_payeur" : IDcompte_payeur, "IDfamille" : IDfamille, "nomCategorie" : nomCategorie,
                }
            dictInscriptions[IDactivite][IDgroupe].append(dictTemp)

            # Mémorisation des groupes
            if (IDgroupe in dictGroupes) == False :
                dictGroupes[IDgroupe] = nomGroupe

        # Recherche des places disponibles

        # Recherche des inscriptions existantes
        req = """SELECT IDgroupe, COUNT(IDinscription)
        FROM inscriptions
        WHERE inscriptions.%s AND inscriptions.statut='ok'
        GROUP BY IDgroupe;""" % conditionActivites
        DB.ExecuterReq(req)
        listeInscriptions = DB.ResultatReq()
        dictInscrits = {}
        for IDgroupe, nbre_inscrits in listeInscriptions :
            dictInscrits[IDgroupe] = nbre_inscrits

        dictActivites = {}
        req = """SELECT IDactivite, nom, abrege, date_debut, date_fin, nbre_inscrits_max
        FROM activites
        WHERE activites.%s;""" % conditionActivites
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()
        for IDactivite, nom, abrege, date_debut, date_fin, nbre_inscrits_max in listeActivites :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            dictActivites[IDactivite] = {"nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin, "nbre_inscrits_max" : nbre_inscrits_max, "groupes" : {}}

        # Recherche des groupes
        req = """SELECT IDgroupe, IDactivite, nom, nbre_inscrits_max
        FROM groupes
        WHERE groupes.%s
        ORDER BY ordre;""" % conditionActivites
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()
        for IDgroupe, IDactivite, nom, nbre_inscrits_max in listeGroupes :

            # Recherche le nombre d'inscrits sur chaque groupe
            if IDgroupe in dictInscrits :
                nbre_inscrits = dictInscrits[IDgroupe]
            else :
                nbre_inscrits = 0

            # Recherche du nombre de places disponibles sur le groupe
            if nbre_inscrits_max not in (None, 0) :
                nbre_places_disponibles = nbre_inscrits_max - nbre_inscrits
            else :
                nbre_places_disponibles = None

            # Mémorise le groupe
            try:
                dictActivites[IDactivite]["groupes"][IDgroupe] = {"nom" : nom, "nbre_places_disponibles" : nbre_places_disponibles, "nbre_inscrits" : nbre_inscrits, "nbre_inscrits_max" : nbre_inscrits_max}
            except:
                pass

        for IDactivite in list(dictActivites.keys()):
            # Recherche le nombre d'inscrits total de l'activité
            dictActivites[IDactivite]["nbre_inscrits"] = 0
            for IDgroupe in dictActivites[IDactivite]["groupes"] :
                if IDgroupe in dictInscrits:
                    dictActivites[IDactivite]["nbre_inscrits"] += dictInscrits[IDgroupe]

            # Recherche du nombre de places disponibles sur l'activité
            if dictActivites[IDactivite]["nbre_inscrits_max"] not in (None, 0) :
                dictActivites[IDactivite]["nbre_places_disponibles"] = dictActivites[IDactivite]["nbre_inscrits_max"] - dictActivites[IDactivite]["nbre_inscrits"]
            else :
                dictActivites[IDactivite]["nbre_places_disponibles"] = None

        DB.Close()
        return dictInscriptions, dictActivites, dictGroupes

    def Remplissage(self):
        dictInscriptions, dictActivites, dictGroupes = self.Importation()

        # Mémorisation pour impression
        self.listeImpression = []
        
        # Branches Activités
        listeActivites = list(dictInscriptions.keys())
        listeActivites.sort()
        
        for IDactivite in listeActivites :
            nom_activite = dictActivites[IDactivite]["nom"]
            niveauActivite = self.AppendItem(self.root, nom_activite)
            self.SetPyData(niveauActivite, IDactivite)
            self.SetItemBold(niveauActivite, True)

            # Branches Groupes
            listeImpressionGroupes = []
            listeGroupes = list(dictInscriptions[IDactivite].keys())
            listeGroupes.sort()

            for IDgroupe in listeGroupes :
                nom_groupe = dictGroupes[IDgroupe]
                niveauGroupe = self.AppendItem(niveauActivite, nom_groupe)
                self.SetPyData(niveauGroupe, {"type" : "groupe", "valeur" : IDgroupe})
                self.SetItemBold(niveauGroupe, True)

                # Branches Inscriptions
                num = 1
                listeImpressionIndividus = []
                for dictInscription in dictInscriptions[IDactivite][IDgroupe]:
                    texteIndividu = u"%d. %s" % (num, dictInscription["nom_individu"])
                    niveauIndividu = self.AppendItem(niveauGroupe, texteIndividu)
                    self.SetPyData(niveauIndividu, {"type" : "individu", "nom_individu" : dictInscription["nom_individu"], "IDindividu" : dictInscription["IDinscription"], "IDfamille" : dictInscription["IDfamille"]})

                    texteDateSaisie = UTILS_Dates.DateComplete(dictInscription["date_inscription"])
                    self.SetItemText(niveauIndividu, texteDateSaisie, 1)

                    nomCategorie = dictInscription["nomCategorie"]
                    self.SetItemText(niveauIndividu, nomCategorie, 2)

                    # Recherche si place dispo
                    nbre_places_dispo = self.RechercheSiPlaceDispo(dictActivites[IDactivite], IDgroupe)

                    place_dispo = False
                    if nbre_places_dispo == None or nbre_places_dispo > 0 :
                        place_dispo = True

                        # Modifie le nombre de places disponibles
                        if dictActivites[IDactivite]["nbre_places_disponibles"] != None :
                            dictActivites[IDactivite]["nbre_places_disponibles"] -= 1
                        if dictActivites[IDactivite]["groupes"][IDgroupe]["nbre_places_disponibles"] != None :
                            dictActivites[IDactivite]["groupes"][IDgroupe]["nbre_places_disponibles"] -= 1

                    else :
                        place_dispo = False

                    # Image
                    if place_dispo == True :
                        img = self.img_ok
                    else :
                        img = self.img_pasok
                    self.SetItemImage(niveauIndividu, img, which=wx.TreeItemIcon_Normal)

                    # Mémorisation pour impression
                    listeImpressionIndividus.append({"placeDispo" : place_dispo, "nomIndividu" : dictInscription["nom_individu"], "num" : num, "texteIndividu" : texteIndividu, "texteDateSaisie" : texteDateSaisie, "nomCategorie" : nomCategorie} )

                    num += 1

                # Mémorisation pour impression
                listeImpressionGroupes.append((nom_groupe, listeImpressionIndividus))

            # Mémorisation pour impression
            self.listeImpression.append((nom_activite, listeImpressionGroupes))

        self.ExpandAllChildren(self.root)
    
    def RechercheSiPlaceDispo(self, dictActivite={}, IDgroupe=None):
        nbre_places_disponibles = []

        if dictActivite["nbre_places_disponibles"] != None:
            nbre_places_disponibles.append(dictActivite["nbre_places_disponibles"])

        for IDgroupeTmp, dictGroupe in dictActivite["groupes"].items():
            if IDgroupeTmp == IDgroupe and dictGroupe["nbre_places_disponibles"] != None:
                nbre_places_disponibles.append(dictGroupe["nbre_places_disponibles"])

        if len(nbre_places_disponibles) > 0 :
            return min(nbre_places_disponibles)
        else :
            return None
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        if type != "individu" : return
        nomIndividu = dictItem["nom_individu"]
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille de %s") % nomIndividu)
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)

        menuPop.AppendSeparator()

        item = wx.MenuItem(menuPop, 20, _(u"Imprimer (PDF)"), _(u"Imprimer (PDF)"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=20)

        item = wx.MenuItem(menuPop, 30, _(u"Exporter au format Excel"), _(u"Exporter au format Excel"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=30)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def OuvrirFicheFamille(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        type = dictItem["type"]
        if type != "individu" : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun individu dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDindividu = dictItem["IDindividu"]
        IDfamille = dictItem["IDfamille"]
        
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille=IDfamille)
        dlg.ShowModal()
        dlg.Destroy()

        self.MAJ()

    def Imprimer(self, event=None):
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib import colors
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        
        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("LISTE_ATTENTE", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, topMargin=30, bottomMargin=30)
        story = []
        
        largeurContenu = 520
        
        # Création du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (420, 100) )
            dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
            if self.mode == "attente" :
                titre = _(u"Inscriptions en attente")
            else :
                titre = _(u"Inscriptions refusées")
            dataTableau.append( (titre, _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
            style = TableStyle([
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                    ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                    ('ALIGN', (0,0), (0,0), 'LEFT'), 
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                    ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                    ('FONT',(1,0),(1,0), "Helvetica", 6), 
                    ])
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)
            story.append(Spacer(0,20))       
        
        # Insère un header
        Header() 
                                
        # Un tableau par date
        for nom_activite, listeGroupes in self.listeImpression :
            
            dataTableau = []
            largeursColonnes = [180, 180, 160]
            
            dataTableau.append((nom_activite, "", ""))
            
            # Groupes
            listeIndexGroupes = []
            indexLigne = 0
            for nomGroupe, listeIndividus in listeGroupes :
                indexLigne += 1
                listeIndexGroupes.append(indexLigne)
                
                dataTableau.append( (nomGroupe, "", "") )
                
                # Individus
                for dictIndividu in listeIndividus :
                    placeDispo = dictIndividu["placeDispo"]
                    texteIndividu = dictIndividu["texteIndividu"]
                    texteDateSaisie = _(u"Saisie le %s") % dictIndividu["texteDateSaisie"]
                    nomCategorie = dictIndividu["nomCategorie"]
                    dataTableau.append( (texteIndividu, texteDateSaisie, nomCategorie) )
                    indexLigne += 1
                    
            couleurFond = (0.8, 0.8, 1) # Vert -> (0.5, 1, 0.2)
            
            listeStyles = [
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                    
                    ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                    ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                    ('ALIGN', (0,1), (-1,-1), 'CENTRE'), # Centre les cases
                    
                    ('ALIGN', (0,1), (-1,1), 'CENTRE'), # Ligne de labels colonne alignée au centre
                    ('FONT',(0,1),(-1,1), "Helvetica", 6), # Donne la police de caract. + taille de police des labels
                    
                    ('SPAN',(0,0),(-1,0)), # Fusionne les lignes du haut pour faire le titre du groupe
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", 10), # Donne la police de caract. + taille de police du titre de groupe
                    ('BACKGROUND', (0,0), (-1,0), couleurFond), # Donne la couleur de fond du titre de groupe
                    
                    ]
            
            # Formatage des lignes "Activités"
            for indexGroupe in listeIndexGroupes :
                listeStyles.append( ('SPAN', (0, indexGroupe), (-1, indexGroupe)) )
                listeStyles.append( ('FONT', (0, indexGroupe), (-1, indexGroupe), "Helvetica-Bold", 7) )
                listeStyles.append( ('ALIGN', (0, indexGroupe), (-1, indexGroupe), 'LEFT') ) 
                
            # Création du tableau
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(TableStyle(listeStyles))
            story.append(tableau)
            story.append(Spacer(0,20))
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)


    def ExportExcel(self, event=None):
        """ Export Excel """
        if self.mode == "attente":
            titre = _(u"Inscriptions en attente")
        else:
            titre = _(u"Inscriptions refusées")

        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportExcel_%s.xlsx" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        wildcard = "Fichier Excel (*.xlsx)|*.xlsx|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut,
            defaultFile = nomFichier,
            wildcard = wildcard,
            style = wx.FD_SAVE
            )
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Export
        import xlsxwriter
        classeur = xlsxwriter.Workbook(cheminFichier)
        feuille = classeur.add_worksheet(titre)

        # Entetes et largeurs des colonnes
        colonnes = [
            (_(u"Date"), 20), (_(u"Groupe"), 15), (_(u"Dispo"), 10), (_(u"N°"), 10),
            (_(u"Individu"), 30), (_(u"Date de saisie"), 30), (_(u"Catégorie de tarif"), 30),
            ]
        index = 0
        for label, largeur in colonnes :
            feuille.set_column(index, index, largeur)
            feuille.write(0, index, label)
            index += 1

        # Contenu
        x = 1
        for activite, listeGroupes in self.listeImpression :
            for nomGroupe, listeIndividus in listeGroupes :
                for dictIndividu in listeIndividus :
                    placeDispo = dictIndividu["placeDispo"]
                    if placeDispo == True :
                        placeDispoTxt = _(u"Oui")
                    else :
                        placeDispoTxt = _(u"None")

                    feuille.write(x, 0, activite)
                    feuille.write(x, 1, nomGroupe)
                    feuille.write(x, 2, placeDispoTxt)
                    feuille.write(x, 3, dictIndividu["num"])
                    feuille.write(x, 4, dictIndividu["nomIndividu"])
                    feuille.write(x, 5, dictIndividu["texteDateSaisie"])
                    feuille.write(x, 6, dictIndividu["nomCategorie"])

                    x += 1

        # Finalisation du fichier xlsx
        classeur.close()

        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = CTRL(panel, liste_activites=[1, 2, 3, 4, 5, 6])
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
