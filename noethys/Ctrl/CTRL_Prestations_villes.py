#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import sys
import FonctionsPerso
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB
from Utils import UTILS_Titulaires
from Utils import UTILS_Organisateur
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")
from Utils import UTILS_Utilisateurs
from Data import DATA_Civilites
DICT_CIVILITES = DATA_Civilites.GetDictCivilites() 
import FonctionsPerso

try: import psyco; psyco.full()
except: pass

COULEUR_FOND_REGROUPEMENT = (220, 220, 220)

            
def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    if dateEng == None : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
def PeriodeComplete(mois, annee):
    listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete


            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.listeImpression = []
        
        # Récupère les noms et adresses de tous les titulaires
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        
        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)
                
        # Création des colonnes
        listeColonnes = [
            ( _(u"Famille/Individu/Prestations"), 250, wx.ALIGN_LEFT),
            ( _(u"Détail"), 250, wx.ALIGN_LEFT),
            ( _(u"Montant"), 70, wx.ALIGN_RIGHT),
            ( _(u"Qté"), 60, wx.ALIGN_CENTER),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | TR_COLUMN_LINES |wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

        # Binds
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
                
    def Importation(self, listeActivites=[], presents=None, listeVilles=None):
        """ Importation """
        # Conditions Activites
        if listeActivites == None or listeActivites == [] :
            conditionActivites = ""
        else:
            if len(listeActivites) == 1 :
                conditionActivites = " AND prestations.IDactivite=%d" % listeActivites[0]
            else:
                conditionActivites = " AND prestations.IDactivite IN %s" % str(tuple(listeActivites))

        # Conditions Présents
        if presents == None :
            conditionPresents = ""
        else:
            conditionPresents = " AND (prestations.date>='%s' AND prestations.date<='%s')" % (str(presents[0]), str(presents[1]))
                
        # Importation des prestations
        DB = GestionDB.DB()
        req = """
        SELECT 
        prestations.IDprestation, prestations.date, prestations.categorie, prestations.label, 
        prestations.montant, prestations.IDactivite, prestations.IDfamille, prestations.IDindividu, 
        prestations.IDcategorie_tarif, individus.nom, individus.prenom, individus.date_naiss,
        activites.nom, individus.IDcivilite
        FROM prestations
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        WHERE IDprestation>0 %s %s
        ;""" % (conditionPresents, conditionActivites)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     

        # Recherche des quantités de conso
        req = """
        SELECT IDconso, consommations.IDindividu, quantite, IDprestation
        FROM consommations
        WHERE IDconso>0 %s %s
        ;""" % (conditionPresents.replace("prestations", "consommations"), conditionActivites.replace("prestations", "consommations"))
        DB.ExecuterReq(req)
        listeConso = DB.ResultatReq()  
        dictConso = {}   
        for IDconso, IDindividu, quantite, IDprestation in listeConso :
            if quantite != None :
                if dictConso.has_key(IDprestation) == False :
                    dictConso[IDprestation] = 0
                dictConso[IDprestation] += quantite
        
        DB.Close() 
        dictResultats = {}
        dictStats = {"montant":0.0, "nombre":0, "familles":0, "individus":0, "prestations":{} }
        for IDprestation, date, categorie, label, montant, IDactivite, IDfamille, IDindividu, IDcategorie_tarif, nom, prenom, date_naiss, nomActivite, IDcivilite in listeDonnees :
            date = DateEngEnDateDD(date)
            if nomActivite == None : nomActivite = _(u"Nom d'activité inconnu")
            
            if self.dictTitulaires.has_key(IDfamille) :
                
                dictTitulaire = self.dictTitulaires[IDfamille]
                nomTitulaires = dictTitulaire["titulairesSansCivilite"]
                rue = dictTitulaire["adresse"]["rue"]
                cp = dictTitulaire["adresse"]["cp"]
                ville = dictTitulaire["adresse"]["ville"]
                if ville == None : ville = u""
                
                if listeVilles == None or ville.upper() in listeVilles :
                
                    # Famille
                    if dictResultats.has_key(IDfamille) == False :
                        dictResultats[IDfamille] = {"nom":nomTitulaires, "rue":rue, "cp":cp, "ville":ville, "individus":{}, "montant":0.0, "nombre":0}
                        dictStats["familles"] += 1
                        
                    # Individu
                    if dictResultats[IDfamille]["individus"].has_key(IDindividu) == False :
                        dictResultats[IDfamille]["individus"][IDindividu] = {"nom":nom, "prenom":prenom, "date_naiss":date_naiss, "IDcivilite":IDcivilite, "prestations":{} }
                        dictStats["individus"] += 1
                        
                    # Prestation
                    if dictResultats[IDfamille]["individus"][IDindividu]["prestations"].has_key(label) == False :
                        dictResultats[IDfamille]["individus"][IDindividu]["prestations"][label] = {"montant":0.0, "nombre":0}
                    
                    # Quantité
                    if dictConso.has_key(IDprestation) : 
                        quantite = dictConso[IDprestation]
                    else :
                        quantite = 1                    
                    
                    # Mémorisation des valeurs
                    dictResultats[IDfamille]["individus"][IDindividu]["prestations"][label]["montant"] += montant
                    dictResultats[IDfamille]["individus"][IDindividu]["prestations"][label]["nombre"] += quantite
                    dictResultats[IDfamille]["individus"][IDindividu]["prestations"][label]["nomActivite"] = nomActivite
                    dictResultats[IDfamille]["montant"] += montant
                    dictResultats[IDfamille]["nombre"] += quantite
                    
                    # Stats
                    dictStats["montant"] += montant
                    dictStats["nombre"] += quantite
                    
                    if dictStats["prestations"].has_key(label) == False :
                        dictStats["prestations"][label] = {"montant":0.0, "nombre":0, "nomActivite":nomActivite}
                    dictStats["prestations"][label]["montant"] += montant
                    dictStats["prestations"][label]["nombre"] += quantite
                
        return dictResultats, dictStats
    
    def MAJ(self, listeActivites=[], presents=None, listeVilles=None, labelParametres=""):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage(listeActivites, presents, listeVilles)
        self.labelParametres = labelParametres

    def Remplissage(self, listeActivites=[], presents=None, listeVilles=None):
        dictResultats, dictStats = self.Importation(listeActivites, presents, listeVilles) 
    
        # Mémorisation pour impression
        self.listeImpression = {"donnees" : [], "totaux": []}
        
        # Tri par nom de titulaires de famille
        listeFamilles = []
        for IDfamille, dictFamille in dictResultats.iteritems() :
            nomTitulaires = dictFamille["nom"]
            listeFamilles.append((nomTitulaires, IDfamille))
        listeFamilles.sort() 
        
        for nomTitulaires, IDfamille in listeFamilles :
            
            # Niveau famille
            niveauFamille = self.AppendItem(self.root, nomTitulaires)
            self.SetPyData(niveauFamille, {"type" : "famille", "valeur" : IDfamille})
            self.SetItemBold(niveauFamille, True)
            self.SetItemBackgroundColour(niveauFamille, wx.Colour(*COULEUR_FOND_REGROUPEMENT))
            adresse = u"%s %s %s" % (dictResultats[IDfamille]["rue"], dictResultats[IDfamille]["cp"], dictResultats[IDfamille]["ville"])
            montantStr = u"%.2f %s" % (dictResultats[IDfamille]["montant"], SYMBOLE)
            self.SetItemText(niveauFamille, adresse, 1)
            self.SetItemText(niveauFamille, montantStr, 2)
            self.SetItemText(niveauFamille, str(dictResultats[IDfamille]["nombre"]), 3)
            
            # Pour impression
            impressionTempFamille = {"nom":nomTitulaires, "adresse":adresse, "montant":montantStr, "nombre":dictResultats[IDfamille]["nombre"], "individus":[]}
            
            for IDindividu, dictIndividu in dictResultats[IDfamille]["individus"].iteritems() :
                
                # Niveau individu
                nomIndividu = u"%s %s" % (dictIndividu["nom"], dictIndividu["prenom"])
                if dictIndividu["date_naiss"] == None :
                    datenaiss_str = _(u"Sans date de naissance")
                else:
                    if DICT_CIVILITES[dictIndividu["IDcivilite"]]["sexe"] == "M" :
                        datenaiss_str = _(u"né le %s") % DateEngFr(dictIndividu["date_naiss"])
                    else:
                        datenaiss_str = _(u"née le %s") % DateEngFr(dictIndividu["date_naiss"])
                
                if dictIndividu["nom"] != None :
                    labelIndividu = u"%s (%s)" % (nomIndividu, datenaiss_str)
                else :
                    labelIndividu = _(u"Prestations familiales")
                niveauIndividu = self.AppendItem(niveauFamille, labelIndividu)
                self.SetPyData(niveauIndividu, {"type" : "individu", "valeur" : IDindividu})
                
                # Pour impression
                impressionTempIndividu = {"nom":nomIndividu, "date_naiss":datenaiss_str, "prestations":[]}
                
                # Tri par label
                listeLabels = []
                for label, dictPrestation in dictResultats[IDfamille]["individus"][IDindividu]["prestations"].iteritems() :
                    listeLabels.append((label, dictPrestation))
                listeLabels.sort() 
                
                for label, dictPrestation in listeLabels :
                    
                    # Niveau Prestation
                    niveauPrestation = self.AppendItem(niveauIndividu, label)
                    self.SetPyData(niveauPrestation, {"type" : "prestation", "valeur" : label})
                    self.SetItemFont(niveauPrestation, wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL))
                    
                    montantStr = u"%.2f %s" % (dictPrestation["montant"], SYMBOLE)
                    self.SetItemText(niveauPrestation, dictPrestation["nomActivite"], 1)
                    self.SetItemText(niveauPrestation, montantStr, 2)
                    self.SetItemText(niveauPrestation, str(dictPrestation["nombre"]), 3)
                    
                    # Pour impression
                    dictTemp = {"label":label, "nomActivite": dictPrestation["nomActivite"], "montant":montantStr, "nombre":dictPrestation["nombre"]}
                    impressionTempIndividu["prestations"].append(dictTemp)
                
                impressionTempFamille["individus"].append(impressionTempIndividu)
            
            self.listeImpression["donnees"].append(impressionTempFamille)
            
        # Stats
        niveauStats = self.AppendItem(self.root, _(u"TOTAL"))
        self.SetPyData(niveauStats, {"type" : "stats", "valeur" : None})
        self.SetItemBold(niveauStats, True)
        self.SetItemBackgroundColour(niveauStats, wx.Colour(*COULEUR_FOND_REGROUPEMENT))
        
        detail = _(u"%d familles et %s individus") % (dictStats["familles"], dictStats["individus"])
        montantStr = u"%.2f %s" % (dictStats["montant"], SYMBOLE)
        self.SetItemText(niveauStats, detail, 1)
        self.SetItemText(niveauStats, montantStr, 2)
        self.SetItemText(niveauStats, str(dictStats["nombre"]), 3)
        
        self.listeImpression["totaux"].append((_(u"TOTAL"), detail, montantStr, dictStats["nombre"]))
        
        # Tri par label
        listeLabels = []
        for label, dictPrestation in dictStats["prestations"].iteritems() :
            listeLabels.append((label, dictPrestation))
        listeLabels.sort() 
        
        for label, dictPrestation in listeLabels :
            niveauStats = self.AppendItem(self.root, label)
            self.SetPyData(niveauStats, {"type" : "stats", "valeur" : None})
            montantStr = u"%.2f %s" % (dictPrestation["montant"], SYMBOLE)
            self.SetItemText(niveauStats, dictPrestation["nomActivite"], 1)
            self.SetItemText(niveauStats, montantStr, 2)
            self.SetItemText(niveauStats, str(dictPrestation["nombre"]), 3)        
            
            self.listeImpression["totaux"].append((label, dictPrestation["nomActivite"], montantStr, dictPrestation["nombre"]))
                
        self.ExpandAllChildren(self.root)
        
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
        if type != "famille" : return
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Famille.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        if dictItem == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune famille dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        type = dictItem["type"]
        if type != "famille" : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune famille dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = dictItem["valeur"]
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, IDfamille=IDfamille)
        dlg.ShowModal()
        dlg.Destroy()
        self.MAJ() 
        
    
    def Imprimer(self, event=None):
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
    
        # Initialisation du PDF
        PAGE_HEIGHT=defaultPageSize[1]
        PAGE_WIDTH=defaultPageSize[0]
        nomDoc = FonctionsPerso.GenerationNomDoc("LISTE_PRESTATIONS_", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, topMargin=30, bottomMargin=30, leftMargin=40, rightMargin=40)
        story = []
        
        largeurContenu = 520
        
        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (420, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Liste des prestations"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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
        story.append(Spacer(0, 10))       
        
        # Intro
        styleA = ParagraphStyle(name="A", fontName="Helvetica", fontSize=6, spaceAfter=20)
        story.append(Paragraph(self.labelParametres, styleA))       
        
        # Famille
        for dictFamille in self.listeImpression["donnees"] :

            # Init tableau
            dataTableau = []
            largeursColonnes = [220, 220, 40, 40]

            dataTableau.append( (dictFamille['nom'], dictFamille['adresse'], dictFamille['montant'], dictFamille['nombre']) )
            
            # Individu
            for dictIndividu in dictFamille["individus"] :
                dataTableau.append( (u"     %s (%s)" % (dictIndividu["nom"], dictIndividu["date_naiss"]), "", "", "") )
                
                # Prestations
                for dictPrestation in dictIndividu["prestations"] :
                    dataTableau.append( (u"                 " + dictPrestation["label"], dictPrestation["nomActivite"], dictPrestation["montant"], dictPrestation["nombre"]) )
                    
            couleurFond = (0.8, 0.8, 1)
            listeStyles = [
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                    ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                    ('BOX', (0, 1), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                    ('ALIGN', (2, 0), (-1, -1), 'CENTRE'), # Ligne de labels colonne alignée au centre
                    ('BOX', (0, 0), (-1,0), 0.25, colors.black), # Crée la bordure noire du nom de famille
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", 8), # Donne la police de caract. + taille de police du titre de groupe
                    ('BACKGROUND', (0,0), (-1,0), couleurFond), # Donne la couleur de fond du titre de groupe
                    ('TOPPADDING',(0,0),(-1,-1), 1), 
                    ('BOTTOMPADDING',(0,0),(-1,-1), 1), 
                    ]
                
            # Création du tableau
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(TableStyle(listeStyles))
            story.append(tableau)
            story.append(Spacer(0, 6))
        
        # TOTAUX
        dataTableau = []
        largeursColonnes = [220, 220, 40, 40]

        for ligne in self.listeImpression["totaux"] :
            dataTableau.append(ligne) 

        couleurFond = (0.8, 0.8, 0.8)
        listeStyles = [
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                ('BOX', (0, 1), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                ('ALIGN', (2, 0), (-1, -1), 'CENTRE'), # Ligne de labels colonne alignée au centre
                ('BOX', (0, 0), (-1,0), 0.25, colors.black), # Crée la bordure noire du nom de famille
                ('FONT',(0,0),(0,0), "Helvetica-Bold", 8), # Donne la police de caract. + taille de police du titre de groupe
                ('BACKGROUND', (0,0), (-1,0), couleurFond), # Donne la couleur de fond du titre de groupe
                ('TOPPADDING',(0,0),(-1,-1), 1), 
                ('BOTTOMPADDING',(0,0),(-1,-1), 1), 
                ]
            
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(TableStyle(listeStyles))
        story.append(tableau)

        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.myOlv = CTRL(panel)
        self.myOlv.MAJ(listeActivites=[6,], 
            presents=None,
            listeVilles=["LANNILIS",],
            )
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
