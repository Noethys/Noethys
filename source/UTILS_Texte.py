#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import re


def Incrementer(s):
    """ look for the last sequence of number(s) in a string and increment """
    lastNum = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')
    m = lastNum.search(s)
    if m:
        next = str(int(m.group(1))+1)
        start, end = m.span(1)
        s = s[:max(end-len(next), start)] + next + s[end:]
    return s

def T(_):
    print _, ">", Incrementer(_)
if __name__=='__main__':
    T("10dsc_0010.jpg")
    T("10dsc_0099.jpg")
    T("dsc_9.jpg")
    T("0000001.exe")
    T("9999999.exe")
    T("ref-04851")
    T("0000099")
    T("9")