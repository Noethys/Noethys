#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import os
import sys


def AdaptePolice(ctrl):
    """ Adapte la taille de la police du ctrl donné """
    taille = 8
    if "linux" in sys.platform :
        ft = ctrl.GetFont()
        ft.SetPointSize(taille)
        ctrl.SetFont(ft)


def AdaptationsDemarrage():
    """ Adaptations au démarrage de Noethys """
    if sys.path[0] :
        os.chdir(sys.path[0])
    else :
        os.chdir(sys.path[1])
    # Vérifie que les répertoires vides sont bien là
    for rep in ("Temp",) :
        if os.path.isdir(rep) == False :
            try :
                os.mkdir(rep)
            except Exception as err:
                pass




if __name__ == "__main__":
    AdaptationsDemarrage()