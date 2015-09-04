#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import datetime
import sys
import decimal
import DLG_Selection_liste
import FonctionsPerso

import UTILS_Dates
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")



def GetValeursListview(listview=None, format="texte"):
    """ Récupère les valeurs affichées sous forme de liste """
    """ format = "texte" ou "original" """
    # Récupère les labels de colonnes
    listeColonnes = []
    for colonne in listview.columns :
        listeColonnes.append((colonne.title, colonne.align, colonne.width, colonne.valueGetter))
    
    # Récupère les valeurs
    listeValeurs = []
    listeObjects = listview.innerList # listview.GetFilteredObjects()
    for object in listeObjects :
        valeursLigne = []
        for indexCol in range(0, listview.GetColumnCount() ) :
            if format == "texte" :
                valeur = listview.GetStringValueAt(object, indexCol)
            else :
                valeur = listview.GetValueAt(object, indexCol)
            valeursLigne.append(valeur)
        listeValeurs.append(valeursLigne)
        
    return listeColonnes, listeValeurs


def GetValeursGrid(grid=None):
    """ Récupère les valeurs affichées sous forme de liste """
    # Récupère les labels de colonnes
    listeColonnes = [("titre_ligne", None, grid.GetColLabelSize(), "titre_ligne"),]
    for numCol in range(0, grid.GetNumberCols()):
        listeColonnes.append((grid.GetColLabelValue(numCol), None, grid.GetColSize(numCol), grid.GetColLabelValue(numCol)))
                
    # Récupère les valeurs
    listeValeurs = []
    for numLigne in range(0, grid.GetNumberRows()) :
        labelLigne = grid.GetRowLabelValue(numLigne)
        valeursLigne = [labelLigne,]
        for numCol in range(0, grid.GetNumberCols()) :
            valeur = grid.GetCellValue(numLigne, numCol)
            if type(valeur) not in ("str", "unicode") :
                valeur = unicode(valeur)
            valeursLigne.append(valeur)
        listeValeurs.append(valeursLigne)
        
    return listeColonnes, listeValeurs


def ExportTexte(listview=None, grid=None, titre=u"", listeColonnes=None, listeValeurs=None, autoriseSelections=True):
    """ Export de la liste au format texte """
    if (listview != None and len(listview.donnees) == 0) or (grid != None and (grid.GetNumberRows() == 0 or grid.GetNumberCols() == 0)):
        dlg = wx.MessageDialog(None, _(u"Il n'y a aucune donnée dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return

    # Récupération des valeurs
    if listview != None and listeColonnes == None and listeValeurs == None :
        listeColonnes, listeValeurs = GetValeursListview(listview, format="texte")
        
    if grid != None and listeColonnes == None and listeValeurs == None :
        autoriseSelections = False
        listeColonnes, listeValeurs = GetValeursGrid(grid)

    # Selection des lignes
    if autoriseSelections == True :
        dlg = DLG_Selection_liste.Dialog(None, listeColonnes, listeValeurs, type="exportTexte")
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
    
    # Demande à l'utilisateur le nom de fichier et le répertoire de destination
    nomFichier = "ExportTexte_%s.txt" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    wildcard = "Fichier texte (*.txt)|*.txt|" \
                    "All files (*.*)|*.*"
    sp = wx.StandardPaths.Get()
    cheminDefaut = sp.GetDocumentsDir()
    dlg = wx.FileDialog(
        None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
        defaultFile = nomFichier, 
        wildcard = wildcard, 
        style = wx.SAVE
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

    # Création du fichier texte
    texte = ""
    separateur = ";"
    for labelCol, alignement, largeur, code in listeColonnes :
        try :
            if "CheckState" in unicode(code) :
                code = "Coche"
        except :
            pass
        texte += code + separateur
    texte = texte[:-1] + "\n"

    for valeurs in listeValeurs :
        if autoriseSelections == False or int(valeurs[0]) in listeSelections :
            for valeur in valeurs :
                if valeur == None :
                    valeur = u""
                texte += u"%s%s" % (valeur, separateur)
            texte = texte[:-1] + "\n"
    
    # Elimination du dernier saut à la ligne
    texte = texte[:-1]

    # Création du fichier texte
    f = open(cheminFichier, "w")
    f.write(texte.encode("iso-8859-15"))
    f.close()
    
    # Confirmation de création du fichier et demande d'ouverture directe dans Excel
    txtMessage = _(u"Le fichier Texte a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
    dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
    reponse = dlgConfirm.ShowModal()
    dlgConfirm.Destroy()
    if reponse == wx.ID_NO:
        return
    else:
        FonctionsPerso.LanceFichierExterne(cheminFichier)
        

# -------------------------------------------------------------------------------------------------------------------------------


def ExportExcel(listview=None, grid=None, titre=_(u"Liste"), listeColonnes=None, listeValeurs=None, autoriseSelections=True):
    """ Export de la liste au format Excel """
    # Plus de sélection pour éviter les bugs !!!!
    autoriseSelections = False 
    
    # Vérifie si données bien présentes
    if (listview != None and len(listview.donnees) == 0) or (grid != None and (grid.GetNumberRows() == 0 or grid.GetNumberCols() == 0)):
        dlg = wx.MessageDialog(None, _(u"Il n'y a aucune donnée dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
        
    # Récupération des valeurs
    if listview != None and listeColonnes == None and listeValeurs == None :
        listeColonnes, listeValeurs = GetValeursListview(listview, format="original")
        
    if grid != None and listeColonnes == None and listeValeurs == None :
        autoriseSelections = False
        listeColonnes, listeValeurs = GetValeursGrid(grid)
    
    # Selection des lignes
    if autoriseSelections == True :
        dlg = DLG_Selection_liste.Dialog(None, listeColonnes, listeValeurs, type="exportExcel")
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
    
    # Demande à l'utilisateur le nom de fichier et le répertoire de destination
    nomFichier = "ExportExcel_%s.xls" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    wildcard = "Fichier Excel (*.xls)|*.xls|" \
                    "All files (*.*)|*.*"
    sp = wx.StandardPaths.Get()
    cheminDefaut = sp.GetDocumentsDir()
    dlg = wx.FileDialog(
        None, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
        defaultFile = nomFichier, 
        wildcard = wildcard, 
        style = wx.SAVE
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
    import pyExcelerator
    # Création d'un classeur
    wb = pyExcelerator.Workbook()
    # Création d'une feuille
    ws1 = wb.add_sheet(titre)
    # Remplissage de la feuille

    al = pyExcelerator.Alignment()
    al.horz = pyExcelerator.Alignment.HORZ_LEFT
    al.vert = pyExcelerator.Alignment.VERT_CENTER
    
    ar = pyExcelerator.Alignment()
    ar.horz = pyExcelerator.Alignment.HORZ_RIGHT
    ar.vert = pyExcelerator.Alignment.VERT_CENTER

    styleEuros = pyExcelerator.XFStyle()
    styleEuros.num_format_str = '"$"#,##0.00_);("$"#,##'
    styleEuros.alignment = ar

    styleDate = pyExcelerator.XFStyle()
    styleDate.num_format_str = 'DD/MM/YYYY'
    styleDate.alignment = ar

    styleHeure = pyExcelerator.XFStyle()
    styleHeure.num_format_str = "[hh]:mm"
    styleHeure.alignment = ar

    # Création des labels de colonnes
    x = 0
    y = 0
    for labelCol, alignement, largeur, nomChamp in listeColonnes :
        try :
            if "CheckState" in unicode(nomChamp) :
                nomChamp = "Coche"
        except :
            pass
        ws1.write(x, y, nomChamp)
        ws1.col(y).width = largeur*42
        y += 1

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Création des lignes
    def RechercheFormatFromChaine(valeur):
        """ Recherche le type de la chaîne """
        if valeur.endswith(SYMBOLE) :
            # Si c'est un montant en euros
            try :
                if valeur.startswith("- ") :
                    valeur = valeur.replace("- ", "-")
                if valeur.startswith("+ ") :
                    valeur = valeur.replace("+ ", "")
                nbre = float(valeur[:-1]) 
                return (nbre, styleEuros)
            except :
                pass
                
        # Si c'est un nombre
        try :
            if valeur.startswith("- ") :
                valeur = valeur.replace("- ", "-")
            nbre = float(valeur)
            return (nbre, None)
        except :
            pass
        
        # Si c'est une date
        try :
            if len(valeur) == 10 :
                if valeur[2] == "/" and valeur[5] == "/" :
                    return (valeur, styleDate)
        except :
            pass

        # Si c'est une heure
##        try :
##            if len(valeur) > 4 :
##                if valeur[-2] in "0123456789" and valeur[-1] in "0123456789" :
##                    separateur = None
##                    if valeur[-3] == ":" : 
##                        separateur = ":"
##                    if valeur[-3] == "h" : 
##                        separateur = "h"
##                    if separateur != None :
##                        valeur = datetime.timedelta(hours=int(valeur.split(separateur)[0]), minutes=int(valeur.split(separateur)[1]))
##                        return (valeur, styleHeure)
##        except :
##            pass

        return unicode(valeur), None

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def RechercheFormat(valeur):
        """ Recherche le type de la donnée """
        if type(valeur) == decimal.Decimal :
            valeur = float(valeur)
            return (valeur, styleEuros)
                
        if type(valeur) == float :
            return (valeur, None)
                
        if type(valeur) == int :
            return (valeur, None)
        
        if type(valeur) == datetime.date :
            valeur = UTILS_Dates.DateDDEnFr(valeur)
            return (valeur, styleDate)
        
        if type(valeur) in (str, unicode) :
            if len(valeur) == 10 :
                if valeur[2] == "/" and valeur[5] == "/" : return (valeur, styleDate)
                if valeur[4] == "-" and valeur[7] == "-" : return (UTILS_Dates.DateEngFr(valeur), styleDate)
                
        return unicode(valeur), None

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    x = 1
    y = 0
    for valeurs in listeValeurs :
        if autoriseSelections == False or int(valeurs[0]) in listeSelections :
            for valeur in valeurs :
                if valeur == None :
                    valeur = u""
                    
                # Recherche s'il y a un format de nombre ou de montant
                if listview != None :
                    valeur, format = RechercheFormat(valeur) #RechercheFormatFromChaine(valeur)
                else :
                    valeur, format = RechercheFormatFromChaine(valeur)
                        
                # Enregistre la valeur
                if format != None :
                    ws1.write(x, y, valeur, format)
                else:
                    ws1.write(x, y, valeur)

                y += 1
            x += 1
            y = 0
            
    # Finalisation du fichier xls
    try :
        wb.save(cheminFichier)
    except :
        dlg = wx.MessageDialog(None, _(u"Il est impossible d'enregistrer le fichier Excel. Veuillez vérifier que ce fichier n'est pas déjà ouvert en arrière-plan."), "Erreur", wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
    
    # Confirmation de création du fichier et demande d'ouverture directe dans Excel
    txtMessage = _(u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
    dlgConfirm = wx.MessageDialog(None, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
    reponse = dlgConfirm.ShowModal()
    dlgConfirm.Destroy()
    if reponse == wx.ID_NO:
        return
    else:
        FonctionsPerso.LanceFichierExterne(cheminFichier)



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        import OL_Individus
        self.listview = OL_Individus.ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.listview.MAJ() 
        # Test de l'export Texte
        ExportExcel(listview=self.listview)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.listview, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL Test Export")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
