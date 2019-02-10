#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import os, sys

frozen = getattr(sys, 'frozen', '')
if not frozen:
    REP_COURANT = os.path.dirname(os.path.abspath(__file__))
    REP_PARENT = os.path.dirname(REP_COURANT)
else :
    REP_PARENT = os.path.dirname(sys.executable)

if REP_PARENT not in sys.path :
    sys.path.insert(1, REP_PARENT)

for rep in os.listdir(REP_PARENT) :
    chemin = os.path.join(REP_PARENT, rep)
    if os.path.isdir(chemin) and chemin not in sys.path :
        sys.path.insert(2, chemin)

def GetStaticPath(fichier=""):
    """ Retourne le chemin du répertoire Static """
    chemin = os.path.join(REP_PARENT, "Static")
    return os.path.join(chemin, fichier)

def GetMainPath(fichier=""):
    """ Retourne le chemin du répertoire principal """
    return os.path.join(REP_PARENT, fichier)