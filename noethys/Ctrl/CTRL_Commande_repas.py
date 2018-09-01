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
import datetime
import copy
import wx.grid as gridlib
import wx.lib.mixins.gridlabelrenderer as glr
import GestionDB
from Ctrl import CTRL_Bouton_image
from Utils import UTILS_Dates
from Utils import UTILS_Divers
import wx.lib.wordwrap as wordwrap

if 'phoenix' in wx.PlatformInfo:
    from wx.grid import GridCellRenderer
else:
    from wx.grid import PyGridCellRenderer as GridCellRenderer

COULEUR_CASES_OUVERTES = wx.Colour(255, 255, 255)
COULEUR_CASES_FERMEES = wx.Colour(240, 240, 240)


def DrawBorder(grid, dc, rect):
    top = rect.top
    bottom = rect.bottom
    left = rect.left
    right = rect.right
    dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
    dc.DrawLine(right, top, right, bottom)
    dc.DrawLine(left, top, left, bottom)
    dc.DrawLine(left, bottom, right, bottom)
    dc.SetPen(wx.WHITE_PEN)
    dc.DrawLine(left + 1, top, left + 1, bottom)
    dc.DrawLine(left + 1, top, right, top)


class LabelColonneRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor=None):
        self._bgcolor = bgcolor

    def Draw(self, grid, dc, rect, col):
        if self._bgcolor != None:
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else:
                dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        texte = grid.GetColLabelValue(col)
        texte = wordwrap.wordwrap(texte, rect.width, dc)
        DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, texte, hAlign, vAlign)



class Case():
    def __init__(self, grid=None, numLigne=None, numColonne=None, IDcolonne=None, date=None, categorieColonne=None, ouvert=False, suggestion=None, valeur=None, IDvaleur=None):
        self.grid = grid
        self.numLigne = numLigne
        self.numColonne = numColonne
        self.IDcolonne = IDcolonne
        self.date = date
        self.categorieColonne = categorieColonne
        self.ouvert = ouvert
        self.suggestion = suggestion
        self.valeur_initiale = None

        # Valeur
        self.IDvaleur = IDvaleur
        self.valeur_initiale = copy.copy(valeur)
        self.SetValeur(valeur)

        # Dessin de la case
        self.renderer = CaseRenderer(self)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)

        if "numerique" in categorieColonne:
            self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)

        if "texte" in categorieColonne:
            self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_LEFT, wx.ALIGN_TOP)

        self.grid.SetReadOnly(self.numLigne, self.numColonne, True)

    def GetRect(self):
        return self.grid.CellToRect(self.numLigne, self.numColonne)

    def Refresh(self):
        rect = self.GetRect()
        x, y = self.grid.CalcScrolledPosition(rect.GetX(), rect.GetY())
        rect = wx.Rect(x, y, rect.GetWidth(), rect.GetHeight())
        self.grid.GetGridWindow().Refresh(False, rect)

    def SetValeur(self, valeur=None):
        if "numerique" in self.categorieColonne :
            if valeur == None :
                valeur = 0
            valeur = str(valeur)
        if "texte" in self.categorieColonne :
            if valeur == None :
                valeur = ""
        self.grid.SetCellValue(self.numLigne, self.numColonne, valeur)

    def ImporterSuggestion(self, event=None):
        if self.suggestion != None:
            self.SetValeur(self.suggestion)

    def Plus(self, event=None):
        if "numerique" in self.categorieColonne :
            self.SetValeur(self.GetValeur()+1)

    def Moins(self, event=None):
        if "numerique" in self.categorieColonne and self.GetValeur() > 0 :
            self.SetValeur(self.GetValeur()-1)

    def Copier(self, event=None):
        if "numerique" in self.categorieColonne:
            typeDonnee = "numerique"
        else:
            typeDonnee = "texte"
        self.grid.presse_papiers = {"type": typeDonnee, "valeur": self.GetValeur()}

    def Coller(self, event=None):
        if self.ouvert == True and self.grid.presse_papiers["type"] in self.categorieColonne:
            self.SetValeur(self.grid.presse_papiers["valeur"])

    def RAZ(self, event=None):
        if self.ouvert == True:
            self.SetValeur(None)

    def GetValeur(self):
        valeur = self.grid.GetCellValue(self.numLigne, self.numColonne)
        if "numerique" in self.categorieColonne:
            valeur = int(valeur)
        return valeur

    def GetSuggestion(self):
        return self.suggestion

    def GetTexteToolTip(self):
        valeur = self.grid.GetCellValue(self.numLigne, self.numColonne)
        if valeur == None :
            valeur = u"Aucune valeur"
        texte = unicode(valeur)
        texte = texte.replace("<b>", "")
        texte = texte.replace("</b>", "")
        # Ajoute la suggestion au texte
        if self.suggestion != None :
            texte += u"\n\nValeur suggérée : %s" % self.suggestion
        if self.ouvert == True :
            texte += u"\n\n------- COMMANDES -------"
            texte += u"\n- Double-cliquez pour modifier une case"
            texte += u"\n- Cliquez sur le bouton droit de la souris pour ouvrir le menu contextuel"
            texte += u"\n- Utilisez le copier-coller (Ctrl+C puis Ctrl+V)"
            if "numerique" in self.categorieColonne:
                texte += u"\n- Utilisez les touches - et +"

        # Affiche le menu du jour
        if self.grid.dictDonnees["dict_menus"].has_key(self.date):
            texte += u"\n\n------- MENUS -------\n\n"
            for dictMenu in self.grid.dictDonnees["dict_menus"][self.date]:
                texte += u"%s :\n" % dictMenu["nom_categorie"]
                texte += u"   - %s\n\n" % dictMenu["texte"].replace(u"\n", u"\n   - ")

        return texte







class CaseRenderer(GridCellRenderer):
    def __init__(self, case=None):
        GridCellRenderer.__init__(self)
        self.case = case
        self.grid = None

    def GetCouleur(self):
        if self.case.ouvert == False :
            return COULEUR_CASES_FERMEES
        else :
            return COULEUR_CASES_OUVERTES

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid

        # Dessine le fond
        couleur_fond = self.GetCouleur()
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(couleur_fond, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else:
            dc.DrawRectangleRect(rect)

        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())

        # Ecrit la suggestion
        if self.case.suggestion != None :
            texte = str(self.case.suggestion)

            dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            dc.SetBrush(wx.Brush(wx.Colour(245, 245, 245)))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetTextForeground(wx.Colour(170, 170, 170))

            # Calculs
            largeurTexte, hauteurTexte = dc.GetTextExtent(texte)

            # Rond rouge
            padding = 1
            xRond = rect.x + 3
            yRond = rect.y + 3
            hauteurRond = hauteurTexte + padding * 2
            largeurRond = largeurTexte + padding * 2 + hauteurRond / 2.0
            if largeurRond < hauteurRond:
                largeurRond = hauteurRond

            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRoundedRectangle(wx.Rect(xRond, yRond, largeurRond, hauteurRond), hauteurRond / 2.0)
            else :
                dc.DrawRoundedRectangleRect(wx.Rect(xRond, yRond, largeurRond, hauteurRond), hauteurRond / 2.0)

            # Texte
            xTexte = xRond + largeurRond / 2.0 - largeurTexte / 2.0
            yTexte = yRond + hauteurRond / 2.0 - hauteurTexte / 2.0
            dc.DrawText(texte, xTexte, yTexte)

            # dc.SetTextForeground(wx.Colour(180, 180, 180))
            # dc.DrawText(texte, rect.x + 5, rect.y + 2)

        # Ecrit la valeur
        texte = grid.GetCellValue(row, col)
        texte = texte.replace("<b>", "")
        texte = texte.replace("</b>", "")

        dc.SetTextForeground(wx.Colour(0, 0, 0))

        if "numerique" in self.case.categorieColonne:
            dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            largeurTexte, hauteurTexte = dc.GetTextExtent(texte)
            dc.DrawText(texte, rect.x + rect.width - 10 - largeurTexte, rect.y + rect.height/2.0 - hauteurTexte/2.0)

        if "texte" in self.case.categorieColonne:
            tailleFont = 7
            dc.SetFont(wx.Font(tailleFont, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            texte = wordwrap.wordwrap(texte, rect.width, dc)
            y = rect.y + 2
            hauteurLigne = tailleFont + 3
            listeLignes = texte.split("\n")
            indexLigne = 0
            for ligne in listeLignes:
                dc.DrawText(ligne, rect.x + 3, y)
                y += hauteurLigne
                if (y + hauteurLigne) >= (rect.y + rect.height) :
                    if indexLigne < len(listeLignes) - 1 :
                        dc.DrawText("...", rect.x + rect.width - 10, rect.y + rect.height - 12)
                    break
                indexLigne += 1

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return CaseRenderer()




# ---------------------------------------------------------------------------------------

class CTRL(gridlib.Grid, glr.GridWithLabelRenderersMixin):
    def __init__(self, parent, IDmodele=None, IDcommande=None):
        gridlib.Grid.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.parent = parent
        self.IDmodele = IDmodele
        self.IDcommande = IDcommande

        self.date_debut = None
        self.date_fin = None
        self.date_fin = None

        self.presse_papiers = None
        self.dictCases = {}
        self.dictValeursAnterieures = {}
        self.last_survol = (None, None)
        self.moveTo = None
        self.CreateGrid(1, 1)
        self.SetRowLabelSize(190)
        self.SetColLabelSize(60)

        # Binds
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
        self.GetGridWindow().Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.GetGridWindow().Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDoubleClick)
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnChangeColSize)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def OnMouseMotion(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)

        if (numLigne, numColonne) != self.last_survol :
            self.last_survol = (numLigne, numColonne)
            if numLigne < 0 or numColonne < 0 or self.dictCases.has_key((numLigne, numColonne)) == False :
                self.GetGridWindow().SetToolTip(None)
            else :
                case = self.dictCases[(numLigne, numColonne)]
                texte = case.GetTexteToolTip()
                if self.GetGridWindow().GetToolTip() != texte:
                    tip = wx.ToolTip(texte)
                    tip.SetDelay(800)
                    self.GetGridWindow().SetToolTip(tip)

    def OnChar(self, event):
        numLigne = self.GetGridCursorRow()
        numColonne = self.GetGridCursorCol()
        keycode = event.GetKeyCode()
        if self.dictCases.has_key((numLigne, numColonne)):
            case = self.dictCases[(numLigne, numColonne)]
            # +
            if keycode == 43:
                case.Plus()
            # -
            if keycode == 45:
                case.Moins()
            # Copier
            if keycode == 3 :
                case.Copier()
            # Coller
            if keycode == 22 :
                case.Coller()
            self.CalcTotaux()
        event.Skip()

    def OnCellRightClick(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        if self.dictCases.has_key((numLigne, numColonne)):
            case = self.dictCases[(numLigne, numColonne)]

            menuPop = UTILS_Adaptations.Menu()

            # Importer les suggestions
            id = wx.NewId()
            item = wx.MenuItem(menuPop, id, _(u"Convertir la suggestion"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Magique.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, case.ImporterSuggestion, id=id)
            if case.suggestion == None :
                item.Enable(False)

            menuPop.AppendSeparator()

            # Copier
            id = wx.NewId()
            item = wx.MenuItem(menuPop, id, _(u"Copier\tCtrl+C"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Copier.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, case.Copier, id=id)

            # Coller
            id = wx.NewId()
            item = wx.MenuItem(menuPop, id, _(u"Coller\tCtrl+V"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Coller.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, case.Coller, id=id)
            if self.presse_papiers == None or case.ouvert == False or (self.presse_papiers != None and self.presse_papiers["type"] not in case.categorieColonne):
                item.Enable(False)

            menuPop.AppendSeparator()

            # RAZ
            id = wx.NewId()
            item = wx.MenuItem(menuPop, id, _(u"Vider la donnée"))
            item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Gomme.png"), wx.BITMAP_TYPE_PNG))
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, case.RAZ, id=id)
            if case.ouvert == False :
                item.Enable(False)

            self.PopupMenu(menuPop)
            menuPop.Destroy()

            # Recalcule les totaux
            self.CalcTotaux()


    def Importation(self):
        """ Importation des données """
        dictDonnees = {}
        if self.IDmodele == None or self.date_debut == None or self.date_fin == None :
            return dictDonnees

        DB = GestionDB.DB()

        # Modèle
        req = """SELECT modeles_commandes.nom, modeles_commandes.IDrestaurateur, parametres,
        restaurateurs.nom, restaurateurs.tel, restaurateurs.mail
        FROM modeles_commandes 
        LEFT JOIN restaurateurs ON restaurateurs.IDrestaurateur = modeles_commandes.IDrestaurateur
        WHERE IDmodele=%d;""" % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0:
            nom_modele, IDrestaurateur, parametres, restaurateur_nom, restaurateur_tel, restaurateur_mail = listeDonnees[0]
            if type(parametres) in (str, unicode):
                exec (u"parametres = %s" % parametres)

            dictDonnees["modele_nom"] = nom_modele
            dictDonnees["modele_parametres"] = parametres
            dictDonnees["IDrestaurateur"] = IDrestaurateur
            dictDonnees["restaurateur_nom"] = restaurateur_nom
            dictDonnees["restaurateur_tel"] = restaurateur_tel
            dictDonnees["restaurateur_mail"] = restaurateur_mail

        # Colonnes
        req = """SELECT IDcolonne, ordre, nom, largeur, categorie, parametres
        FROM modeles_commandes_colonnes 
        WHERE IDmodele=%d
        ORDER BY ordre;""" % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictDonnees["liste_colonnes"] = []
        dictDonnees["dict_colonnes"] = {}
        if len(listeDonnees) > 0:
            index = 0
            for IDcolonne, ordre, nom_colonne, largeur, categorie, parametres in listeDonnees:
                if type(parametres) in (str, unicode):
                    exec (u"parametres = %s" % parametres)
                dictColonne = {"IDcolonne": IDcolonne, "ordre": ordre, "nom_colonne": nom_colonne, "largeur": largeur, "categorie": categorie, "parametres": parametres}
                dictDonnees["liste_colonnes"].append(dictColonne)

                dictDonnees["dict_colonnes"][index] = dictColonne
                index += 1

        # Recherche les activités concernées
        listeUnites = []
        for dictColonne in dictDonnees["liste_colonnes"] :
            if dictColonne["parametres"].has_key("unites"):
                for (IDgroupe, IDunite) in dictColonne["parametres"]["unites"] :
                    if IDunite not in listeUnites :
                        listeUnites.append(IDunite)

        if len(listeUnites) == 0 : conditionUnites = "()"
        elif len(listeUnites) == 1 : conditionUnites = "(%d)" % listeUnites[0]
        else : conditionUnites = str(tuple(listeUnites))

        # Ouvertures
        req = """SELECT IDouverture, IDactivite, IDunite, IDgroupe, date
        FROM ouvertures
        WHERE date>='%s' AND date<='%s' AND IDunite IN %s;""" % (self.date_debut, self.date_fin, conditionUnites)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictDonnees["liste_ouvertures"] = []
        dictDonnees["dict_ouvertures"] = {}
        dictDonnees["liste_dates"] = []
        for IDouverture, IDactivite, IDunite, IDgroupe, date in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            dictOuverture = {"IDouverture" : IDouverture, "IDactivite" : IDactivite, "IDunite" : IDunite, "IDgroupe" : IDgroupe, "date" : date}
            dictDonnees["liste_ouvertures"].append(dictOuverture)

            # Mémorisation dans un dict
            dictDonnees["dict_ouvertures"] = UTILS_Divers.DictionnaireImbrique(dictionnaire=dictDonnees["dict_ouvertures"], cles=[date, IDgroupe, IDunite], valeur=True)

            # Mémorisation des dates
            if date not in dictDonnees["liste_dates"] :
                dictDonnees["liste_dates"].append(date)
        dictDonnees["liste_dates"].sort()

        dictDonnees["liste_dates"].append(_(u"Total"))

        # Consommations
        req = """SELECT IDconso, date, IDgroupe, IDunite, IDindividu
        FROM consommations 
        WHERE date>='%s' AND date<='%s' AND IDunite IN %s AND etat IN ('reservation', 'present')
        ;""" % (self.date_debut, self.date_fin, conditionUnites)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictDonnees["dict_conso"] = {}
        dictDonnees["liste_individus"] = []
        dictDonnees["dict_dates"] = {}
        for IDconso, date, IDgroupe, IDunite, IDindividu in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)

            if dictDonnees["dict_conso"].has_key(date) == False:
                dictDonnees["dict_conso"][date] = {}
            if dictDonnees["dict_conso"][date].has_key(IDgroupe) == False:
                dictDonnees["dict_conso"][date][IDgroupe] = {}
            if dictDonnees["dict_conso"][date][IDgroupe].has_key(IDunite) == False:
                dictDonnees["dict_conso"][date][IDgroupe][IDunite] = 0
            dictDonnees["dict_conso"][date][IDgroupe][IDunite] += 1

            if IDindividu not in dictDonnees["liste_individus"] :
                dictDonnees["liste_individus"].append(IDindividu)

            if dictDonnees["dict_dates"].has_key(date) == False :
                dictDonnees["dict_dates"][date] = {}
            if dictDonnees["dict_dates"][date].has_key(IDindividu) == False :
                dictDonnees["dict_dates"][date][IDindividu] = []
            if IDgroupe not in dictDonnees["dict_dates"][date][IDindividu] :
                dictDonnees["dict_dates"][date][IDindividu].append(IDgroupe)


        if len(dictDonnees["liste_individus"]) == 0 : conditionIndividus = "()"
        elif len(dictDonnees["liste_individus"]) == 1 : conditionIndividus = "(%d)" % dictDonnees["liste_individus"][0]
        else : conditionIndividus = str(tuple(dictDonnees["liste_individus"]))


        # Informations médicales
        req = """SELECT IDprobleme, problemes_sante.IDindividu, IDtype, intitule, date_debut, date_fin, description, traitement_medical,
        description_traitement, date_debut_traitement, date_fin_traitement,
        individus.nom, individus.prenom
        FROM problemes_sante 
        LEFT JOIN individus ON individus.IDindividu = problemes_sante.IDindividu
        WHERE diffusion_listing_repas=1 AND problemes_sante.IDindividu IN %s
        ;""" % conditionIndividus
        DB.ExecuterReq(req)
        listeInformations = DB.ResultatReq()
        dictInfosMedicales = {}
        for IDprobleme, IDindividu, IDtype, intitule, date_debut, date_fin, description, traitement_medical, description_traitement, date_debut_traitement, date_fin_traitement, individu_nom, individu_prenom in listeInformations :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)

            if dictInfosMedicales.has_key(IDindividu) == False :
                dictInfosMedicales[IDindividu] = []
            dictTemp = {
                "IDprobleme" : IDprobleme, "IDcategorie" : IDtype, "intitule" : intitule, "date_debut" : date_debut,
                "date_fin" : date_fin, "description" : description, "traitement_medical" : traitement_medical, "description_traitement" : description_traitement,
                "date_debut_traitement" : date_debut_traitement, "date_fin_traitement" : date_fin_traitement,
                "individu_nom" : individu_nom, "individu_prenom" : individu_prenom,
                }
            dictInfosMedicales[IDindividu].append(dictTemp)
        dictDonnees["infos_medicales"] = dictInfosMedicales

        # Messages
        req = """SELECT IDmessage, IDcategorie, priorite,
        messages.IDindividu, texte, individus.nom, individus.prenom
        FROM messages
        LEFT JOIN individus ON individus.IDindividu = messages.IDindividu
        WHERE afficher_commande=1 AND messages.IDindividu IN %s
        ;""" % conditionIndividus
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dictMessages = {}
        for IDmessage, IDcategorie, priorite, IDindividu, texte, individu_nom, individu_prenom in listeDonnees :
            dictTemp = {"IDmessage" : IDmessage, "IDindividu" : IDindividu, "priorite" : priorite, "texte" : texte,
                        "individu_nom" : individu_nom, "individu_prenom" : individu_prenom}
            if dictMessages.has_key(IDindividu) == False :
                dictMessages[IDindividu] = []
            dictMessages[IDindividu].append(dictTemp)
        dictDonnees["messages"] = dictMessages

        # Repas
        dictDonnees["valeurs"] = {}
        if self.IDcommande != None :
            req = """SELECT IDvaleur, date, IDcolonne, valeur
            FROM commandes_valeurs
            WHERE IDcommande=%d
            ;""" % self.IDcommande
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()

            for IDvaleur, date, IDcolonne, valeur in listeDonnees :
                date = UTILS_Dates.DateEngEnDateDD(date)
                if dictDonnees["valeurs"].has_key(date) == False :
                    dictDonnees["valeurs"][date] = {}
                dictDonnees["valeurs"][date][IDcolonne] = {"IDvaleur" : IDvaleur, "valeur" : valeur}

        # Menus
        if dictDonnees.has_key("IDrestaurateur"):
            IDrestaurateur = dictDonnees["IDrestaurateur"]
        else :
            IDrestaurateur = 0
        req = """SELECT IDmenu, menus.IDcategorie, menus_categories.nom, date, texte
        FROM menus
        LEFT JOIN menus_categories ON menus_categories.IDcategorie = menus.IDcategorie
        WHERE date>='%s' AND date<='%s' AND IDrestaurateur=%d
        ORDER BY menus_categories.ordre;""" % (self.date_debut, self.date_fin, IDrestaurateur)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        dict_menus = {}
        for IDmenu, IDcategorie, nom_categorie, date, texte in listeDonnees:
            date = UTILS_Dates.DateEngEnDateDD(date)
            if dict_menus.has_key(date) == False :
                dict_menus[date] = []
            dict_menus[date].append({"IDmenu" : IDmenu, "IDcategorie" : IDcategorie, "nom_categorie" : nom_categorie, "texte" : texte})
        dictDonnees["dict_menus"] = dict_menus

        DB.Close()

        return dictDonnees

    def MAJ(self, date_debut=None, date_fin=None):
        self.date_debut = date_debut
        self.date_fin = date_fin

        # Mémorisation des données existantes
        try :
            for case in self.dictCases.values():
                if case.ouvert == True :
                    self.dictValeursAnterieures[(case.date, case.IDcolonne)] = case.GetValeur()
        except:
            pass

        # Importation
        self.dictDonnees = self.Importation()

        # RAZ de la grid
        if self.GetNumberRows() > 0:
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0:
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()

        if len(self.dictDonnees) == 0 :
            return

        # Création des colonnes
        nbreColonnes = len(self.dictDonnees["liste_colonnes"])
        self.AppendCols(nbreColonnes)

        numColonne = 0
        for dictColonne in self.dictDonnees["liste_colonnes"] :
            nomColonne = dictColonne["nom_colonne"]
            renderer = LabelColonneRenderer()
            self.SetColLabelRenderer(numColonne, renderer)
            self.SetColLabelValue(numColonne, nomColonne)
            self.SetColSize(numColonne, dictColonne["largeur"])
            numColonne += 1

        # Création des lignes
        nbreLignes = len(self.dictDonnees["liste_dates"])
        self.AppendRows(nbreLignes)

        numLigne = 0
        for date in self.dictDonnees["liste_dates"] :
            if type(date) == datetime.date :
                label = UTILS_Dates.DateComplete(date)
            else :
                label = date
            self.SetRowLabelValue(numLigne, label)
            self.SetRowSize(numLigne, 40)
            numLigne += 1

        # Création des cases
        self.dictCases = {}

        numLigne = 0
        for date in self.dictDonnees["liste_dates"]:
            numColonne = 0

            for dictColonne in self.dictDonnees["liste_colonnes"]:

                # Colonne de type NUMERIQUE
                if type(date) == datetime.date : #and dictColonne["categorie"] in ("numerique_avec_suggestion", "numerique_sans_suggestion", "texte_libre") :
                    ouvert = True
                    suggestion = None
                    valeur = None
                    IDvaleur = None

                    # Recherche valeur dans DB
                    try :
                        valeur = self.dictDonnees["valeurs"][date][dictColonne["IDcolonne"]]["valeur"]
                        IDvaleur = self.dictDonnees["valeurs"][date][dictColonne["IDcolonne"]]["IDvaleur"]
                    except :
                        pass

                    # Récupération de la valeur avant MAJ
                    if self.dictValeursAnterieures.has_key((date, dictColonne["IDcolonne"])):
                        valeur = self.dictValeursAnterieures[(date, dictColonne["IDcolonne"])]

                    # Recherche suggestion
                    if dictColonne["categorie"] ==  "numerique_avec_suggestion" :
                        suggestion = 0
                        for (IDgroupe, IDunite) in dictColonne["parametres"]["unites"]:
                            # Recherche si unités ouvertes
                            if self.RechercheOuverture(date, IDgroupe, IDunite) == False :
                                ouvert = False
                            # Recherche le nombre de conso
                            try :
                                suggestion += self.dictDonnees["dict_conso"][date][IDgroupe][IDunite]
                            except :
                                pass

                    # Recherche information
                    if dictColonne["categorie"] == "texte_infos" :
                        ouvert = False
                        liste_infos = []
                        if self.dictDonnees["dict_dates"].has_key(date) :
                            for IDindividu in self.dictDonnees["dict_dates"][date] :
                                valide = True

                                if dictColonne["parametres"].has_key("groupes") :
                                    valide = False
                                    groupes = dictColonne["parametres"]["groupes"]
                                    for IDgroupe in groupes :
                                        if IDgroupe in self.dictDonnees["dict_dates"][date][IDindividu] :
                                            valide = True

                                if valide == True :

                                    # Recherche infos médicales
                                    if dictColonne["parametres"].has_key("infos_medicales"):
                                        if self.dictDonnees["infos_medicales"].has_key(IDindividu) :
                                            for dictInfos in self.dictDonnees["infos_medicales"][IDindividu]:
                                                texte = u"<b>%s %s</b> : %s (%s)" % (dictInfos["individu_prenom"], dictInfos["individu_nom"], dictInfos["intitule"], dictInfos["description"])
                                                liste_infos.append(texte)

                                    # Recherche messages
                                    if dictColonne["parametres"].has_key("messages_individuels"):
                                        if self.dictDonnees["messages"].has_key(IDindividu) :
                                            for dictMessages in self.dictDonnees["messages"][IDindividu]:
                                                texte = u"<b>%s %s</b> : %s" % (dictMessages["individu_prenom"], dictMessages["individu_nom"], dictMessages["texte"])
                                                liste_infos.append(texte)

                        liste_infos.sort()
                        valeur = u"\n".join(liste_infos)

                    # Colonne de type TOTAL
                    if dictColonne["categorie"] == "numerique_total":
                        ouvert = False

                    # Création de la case
                    case = Case(self, numLigne=numLigne, numColonne=numColonne, IDcolonne=dictColonne["IDcolonne"], date=date, categorieColonne=dictColonne["categorie"], ouvert=ouvert, suggestion=suggestion, valeur=valeur, IDvaleur=IDvaleur)
                    self.dictCases[(numLigne, numColonne)] = case

                # Ligne de total
                if type(date) in (str, unicode):

                    # Création de la case
                    case = Case(self, numLigne=numLigne, numColonne=numColonne, IDcolonne=dictColonne["IDcolonne"], date=date, categorieColonne=dictColonne["categorie"], ouvert=False, valeur=None)
                    self.dictCases[(numLigne, numColonne)] = case

                numColonne += 1
            numLigne += 1

        # Envoie les colonnes au OL_Totaux
        listeColonneTotal = []
        numLigneTotal = len(self.dictDonnees["liste_dates"]) - 1
        for numColonne in range(0, len(self.dictDonnees["liste_colonnes"])):
            case = self.dictCases[(numLigneTotal, numColonne)]
            if "numerique" in case.categorieColonne :
                dictColonne = self.dictDonnees["dict_colonnes"][numColonne]
                listeColonneTotal.append({"IDcolonne" : dictColonne["IDcolonne"], "nom_colonne" : dictColonne["nom_colonne"], "valeur" : 0, "isTotal" : "total" in case.categorieColonne})
        try :
            self.GetParent().ctrl_totaux.SetColonnes(listeColonneTotal)
        except:
            pass

        # Calcule les totaux
        self.CalcTotaux()

    def Sauvegarde(self, IDcommande=None):
        """ Sauvegarde """
        self.IDcommande = IDcommande

        listeModifications = []
        listeAjouts = []
        listeSuppressions = []

        # Récupération des valeurs
        if self.dictDonnees.has_key("liste_dates"):
            for numLigne in range(0, len(self.dictDonnees["liste_dates"]) - 1):
                for numColonne in range(0, len(self.dictDonnees["liste_colonnes"])):
                    if self.dictCases.has_key((numLigne, numColonne)):
                        case = self.dictCases[(numLigne, numColonne)]
                        if case.ouvert == True :
                            if unicode(case.GetValeur()) not in ("", "0"):
                                if case.IDvaleur == None :
                                    listeAjouts.append((self.IDcommande, str(case.date), case.IDcolonne, unicode(case.GetValeur())))
                                else :
                                    listeModifications.append((str(case.date), case.IDcolonne, unicode(case.GetValeur()), case.IDvaleur))
                            else :
                                if case.IDvaleur != None :
                                    listeSuppressions.append(case.IDvaleur)

        # Sauvegarde
        DB = GestionDB.DB()

        # Sauvegarde des modifications
        if len(listeModifications) > 0:
            DB.Executermany("UPDATE commandes_valeurs SET date=?, IDcolonne=?, valeur=? WHERE IDvaleur=?", listeModifications, commit=False)

        # Sauvegarde des ajouts
        if len(listeAjouts) > 0:
            DB.Executermany("INSERT INTO commandes_valeurs (IDcommande, date, IDcolonne, valeur) VALUES (?, ?, ?, ?)", listeAjouts, commit=False)

        # Suppression
        if len(listeSuppressions) > 0 :
            if len(listeSuppressions) == 1 :
                conditionSuppression = "(%d)" % listeSuppressions[0]
            else :
                conditionSuppression = str(tuple(listeSuppressions))
            DB.ExecuterReq("DELETE FROM commandes_valeurs WHERE IDvaleur IN %s" % conditionSuppression)

        # Commit
        if len(listeModifications) > 0 or len(listeAjouts) > 0 or len(listeSuppressions) > 0 :
            DB.Commit()

        # Clôture de la base
        DB.Close()

    def OnChangeColSize(self, event):
        numColonne = event.GetRowOrCol()
        largeur = self.GetColSize(numColonne)
        IDcolonne = self.dictDonnees["dict_colonnes"][numColonne]["IDcolonne"]
        DB = GestionDB.DB()
        DB.ReqMAJ("modeles_commandes_colonnes", [("largeur", largeur),], "IDcolonne", IDcolonne)
        DB.Close()

    def RechercheOuverture(self, date, IDgroupe, IDunite):
        if self.dictDonnees["dict_ouvertures"].has_key(date) :
            if self.dictDonnees["dict_ouvertures"][date].has_key(IDgroupe) :
                if self.dictDonnees["dict_ouvertures"][date][IDgroupe].has_key(IDunite) :
                    return self.dictDonnees["dict_ouvertures"][date][IDgroupe][IDunite]
        return None

    def OnLeftDoubleClick(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        if self.dictCases.has_key((numLigne, numColonne)) == False :
            return False
        case = self.dictCases[(numLigne, numColonne)]
        if case.ouvert == False :
            return False
        # DLG demande valeur
        dlg = DLG_Saisie_valeur(self, categorieColonne=case.categorieColonne, valeur=case.GetValeur(), suggestion=case.GetSuggestion())
        if dlg.ShowModal() == wx.ID_OK :
            case.SetValeur(dlg.GetValeur())
            self.CalcTotaux()
        dlg.Destroy()

    def CalcTotaux(self):
        # Calcule les valeurs des colonnes de type TOTAL
        for numLigne in range(0, len(self.dictDonnees["liste_dates"]) - 1):

            # On recherche une colonne de type total
            numColonneTotal = 0
            for dictColonne in self.dictDonnees["liste_colonnes"]:
                if dictColonne["categorie"] == "numerique_total":
                    if dictColonne["parametres"].has_key("colonnes"):
                        listeIDcolonne = dictColonne["parametres"]["colonnes"]
                    else :
                        listeIDcolonne = None

                    # On parcourt les colonnes de la ligne pour calculer le total
                    valeur = 0
                    for numColonne in range(0, len(self.dictDonnees["liste_colonnes"])):
                        if self.dictCases.has_key((numLigne, numColonne)):
                            case = self.dictCases[(numLigne, numColonne)]
                            if (listeIDcolonne == None or case.IDcolonne in listeIDcolonne) and "numerique" in case.categorieColonne and "total" not in case.categorieColonne:
                                valeur += case.GetValeur()

                    # On envoie le total à la case de la colonne TOTAL
                    self.dictCases[(numLigne, numColonneTotal)].SetValeur(valeur)

                numColonneTotal += 1

        # Calcule les totaux des colonnes
        totaux_colonnes = {}
        for numLigne in range(0, len(self.dictDonnees["liste_dates"]) - 1):
            for numColonne in range(0, len(self.dictDonnees["liste_colonnes"])):
                if self.dictCases.has_key((numLigne, numColonne)):
                    case = self.dictCases[(numLigne, numColonne)]
                    if "numerique" in case.categorieColonne:
                        if totaux_colonnes.has_key(numColonne) == False:
                            totaux_colonnes[numColonne] = 0
                        totaux_colonnes[numColonne] += case.GetValeur()

        # Envoie les totaux vers les cases de la ligne de total
        for numColonne, valeur in totaux_colonnes.iteritems():
            numLigne = len(self.dictDonnees["liste_dates"]) - 1
            self.dictCases[(numLigne, numColonne)].SetValeur(valeur)

        # Envoie la ligne TOTAL au OL_Totaux
        dictTotaux = {}
        numLigneTotal = len(self.dictDonnees["liste_dates"]) - 1
        for numColonne in range(0, len(self.dictDonnees["liste_colonnes"])):
            case = self.dictCases[(numLigneTotal, numColonne)]
            if "numerique" in case.categorieColonne :
                dictColonne = self.dictDonnees["dict_colonnes"][numColonne]
                dictTotaux[dictColonne["IDcolonne"]] = case.GetValeur()
        try :
            self.GetParent().ctrl_totaux.SetValeurs(dictTotaux)
        except:
            pass

    def GetDonnees(self):
        dictDonnees = copy.copy(self.dictDonnees)
        dictDonnees["cases"] = copy.copy(self.dictCases)
        return dictDonnees

    def Importer_suggestions(self, event=None):
        for case in self.dictCases.values() :
            case.ImporterSuggestion()
        self.CalcTotaux()

    def RAZ(self, event=None):
        for case in self.dictCases.values():
            case.RAZ()
        self.CalcTotaux()

# -------------------------------------------------------------------------------------------------------

class DLG_Saisie_valeur(wx.Dialog):
    def __init__(self, parent, categorieColonne=None, valeur=None, suggestion=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.suggestion = suggestion

        if "numerique" in categorieColonne :
            self.ctrl_valeur = wx.SpinCtrl(self, -1, min=0, max=99999, style=wx.TE_PROCESS_ENTER)
            self.ctrl_valeur.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            self.ctrl_valeur.SetMinSize((200, -1))
            if valeur == None:
                valeur = 0
            valeur = int(valeur)

        if "texte" in categorieColonne :
            self.ctrl_valeur = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
            self.ctrl_valeur.SetMinSize((320, 90))

        if self.suggestion != None :
            self.label_suggestion = wx.StaticText(self, -1, _(u"Valeur suggérée : %s") % suggestion)
            self.label_suggestion.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            self.label_suggestion.SetForegroundColour(wx.Colour(120, 120, 120))

        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.ctrl_valeur.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)

        # Init
        self.ctrl_valeur.SetValue(valeur)
        self.ctrl_valeur.SetFocus()
        self.ctrl_valeur.SetSelection(0, len(unicode(valeur)))


    def __set_properties(self):
        self.SetTitle(_(u"Modification d'une valeur"))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider ou tapez sur la touche Entrée du clavier")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)

        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_contenu.Add(self.ctrl_valeur, 0, wx.EXPAND, 0)
        if self.suggestion != None :
            grid_sizer_contenu.Add(self.label_suggestion, 0, wx.ALIGN_RIGHT, 0)

        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL | wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnEnter(self, event):
        self.EndModal(wx.ID_OK)

    def OnBoutonOk(self, event=None):
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetValeur(self):
        return self.ctrl_valeur.GetValue()








# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        # Contrôles
        self.ctrl = CTRL(panel, IDmodele=5)
        self.ctrl.MAJ(date_debut = datetime.date(2016, 1, 1), date_fin=datetime.date(2017, 1, 31))

        self.bouton_test = wx.Button(panel, -1, _(u"Bouton de test"))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
    
    def OnBoutonTest(self, event):
        """ Bouton de test """
        self.ctrl.AutoSizeRow(row=2)



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
