#!\\usr\\bin\\env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
#-----------------------------------------------------------

import sys
import os
import glob
import os.path
import zipfile

from distutils.core import setup 
import py2exe
import numpy


manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="Noethys"
    type="win32"
  />
  <description>Noethys</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
            level="asInvoker"
            uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
            type="win32"
            name="Microsoft.VC90.CRT"
            version="9.0.21022.8"
            processorArchitecture="x86"
            publicKeyToken="1fc8b3b9a1e18e3b">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
  </dependency>
</assembly>
"""


import matplotlib as mp
matplotlib_font_afm = glob.glob(os.sep.join([mp.get_data_path(), 'fonts\\afm\\*']))
matplotlib_font_pdfcorefonts = glob.glob(os.sep.join([mp.get_data_path(), 'fonts\\pdfcorefonts\\*']))
matplotlib_font_ttf = glob.glob(os.sep.join([mp.get_data_path(), 'fonts\\ttf\\*']))
matplotlib_images = glob.glob(os.sep.join([mp.get_data_path(), 'images\\*']))


def GetVersion():
    """ Recherche du numéro de version """
    fichierVersion = open("Versions.txt", "r")
    txtVersion = fichierVersion.readlines()[0]
    fichierVersion.close() 
    pos_debut_numVersion = txtVersion.find("n")
    pos_fin_numVersion = txtVersion.find("(")
    numVersion = txtVersion[pos_debut_numVersion+1:pos_fin_numVersion].strip()
    return numVersion
    
VERSION_APPLICATION = GetVersion()


def listdirectory(path):
    listeFichiers = filter(os.path.isfile, glob.glob(path + os.sep + '*'))
    return listeFichiers

def GetFichiersExemples(chemin="Data/"):
    listeFichiersExemples = []
    fichiers = os.listdir(chemin)
    for fichier in fichiers :
        if fichier.startswith("EXEMPLE_") :
            listeFichiersExemples.append(chemin + fichier)
    return listeFichiersExemples
    
    

options = {
    "py2exe": {
        "includes" : [
                "matplotlib.backends",
                "matplotlib.figure", "matplotlib.backends.backend_wxagg", "pylab", "numpy",
                "email", "email.encoders", "email.generator", "email.iterators", "email.utils",
                "email.mime.base", "email.mime.multipart", "email.mime.text",
                "email.mime.image", "email.mime.audio", "email.base64mime",
                "pyttsx.drivers.sapi5", "zope.interface",
                ],
        
         'excludes' : [
                '_gtkagg', '_tkagg', '_agg2', '_cairo', '_cocoaagg',
                '_fltkagg', '_gtk', '_gtkcairo',
                'backend_qt', 'backend_qt4', 'backend_qt4agg',
                'backend_qtagg',
                'backend_cairo', 'backend_cocoaagg',
                'Tkconstants', 'Tkinter', 'tcl',
                "_imagingtk", "PIL._imagingtk", "ImageTk", "PIL.ImageTk", "FixTk",
                ],

        'dll_excludes': [
                "tcl84.dll", "tk84.dll", "wxmsw26uh_vc.dll", "libgdk-win32-2.0-0.dll",
                "libgobject-2.0-0.dll", "UxTheme.dll", "mswsock.dll", "powrprof.dll", "MSVCP90.dll",
                "api-ms-win-core-string-l1-1-0.dll", "api-ms-win-core-registry-l1-1-0.dll",
                "api-ms-win-core-errorhandling-l1-1-1.dll", "api-ms-win-core-string-l2-1-0.dll",
                "api-ms-win-core-profile-l1-1-0.dll", "api-ms-win*.dll",
                "api-ms-win-core-processthreads-l1-1-2.dll", "api-ms-win-core-libraryloader-l1-2-1.dll",
                "api-ms-win-core-file-l1-2-1.dll", "api-ms-win-security-base-l1-2-0.dll",
                "api-ms-win-eventing-provider-l1-1-0.dll", "api-ms-win-core-heap-l2-1-0.dll",
                "api-ms-win-core-libraryloader-l1-2-0.dll", "api-ms-win-core-localization-l1-2-1.dll",
                "api-ms-win-core-sysinfo-l1-2-1.dll", "api-ms-win-core-synch-l1-2-0.dll",
                "api-ms-win-core-heap-l1-2-0.dll", "api-ms-win-core-handle-l1-1-0.dll",
                "api-ms-win-core-io-l1-1-1.dll", "api-ms-win-core-com-l1-1-1.dll",
                "api-ms-win-core-memory-l1-1-2.dll", "api-ms-win-core-version-l1-1-1.dll",
                "api-ms-win-core-version-l1-1-0.dll", "crypt32.dll",
                ],

        "packages": [
                "pytz", "reportlab", "twisted", "twisted.web.resource",
                ],

        "typelibs": [
                ('{C866CA3A-32F7-11D2-9602-00C04F8EE628}', 0, 5, 4), # Pour Pyttsx - Version Windows 7
                ],
                        
        #'compressed' : 1 ,.
        #'optimize': 2,
        }
    }


data_files=[
    
          # Dossiers à importer:
          ('Outils', glob.glob('Outils\\*.*')),
          ('Data', GetFichiersExemples("Data/")),
          
          ('Images\\16x16', listdirectory('Images\\16x16')),
          ('Images\\22x22', listdirectory('Images\\22x22')),
          ('Images\\32x32', listdirectory('Images\\32x32')),
          ('Images\\48x48', listdirectory('Images\\48x48')),
          ('Images\\80x80', listdirectory('Images\\80x80')),
          ('Images\\128x128', listdirectory('Images\\128x128')),
          ('Images\\BoutonsImages', listdirectory('Images\\BoutonsImages')),
          ('Images\\Drapeaux', listdirectory('Images\\Drapeaux')),
          ('Images\\Special', listdirectory('Images\\Special')),
          ('Images\\Badgeage', listdirectory('Images\\Badgeage')),
          ('Images\\Teamword', listdirectory('Images\\Teamword')),
          ('Images\\Avatars\\16x16', listdirectory('Images\\Avatars\\16x16')),
          ('Images\\Avatars\\128x128', listdirectory('Images\\Avatars\\128x128')),
          ('Images\\Interface\\Vert', listdirectory('Images\\Interface\\Vert')),
          ('Images\\Interface\\Bleu', listdirectory('Images\\Interface\\Bleu')),
          ('Images\\Interface\\Noir', listdirectory('Images\\Interface\\Noir')),

          ('Sync', [] ),
          ('Lang', glob.glob('Lang\\*.*')),
          
          # Fichiers à importer :
          ('', ['Versions.txt', 'Licence.txt', 'Geographie.dat', 'Prenoms.dat',
                'Defaut.dat', 'Annonces.dat', 'Textes.dat', 'Icone.ico', 
                'msvcm90.dll', 'msvcp90.dll', 'msvcr90.dll',
                'Microsoft.VC90.CRT.manifest',
                'gdiplus.dll', ]), 
           ]

data_files += mp.get_py2exe_datafiles()


setup(
    name="Noethys",
    version=VERSION_APPLICATION,
    description="Noethys",
    author="Ivan LUCAS",
    options = options, 
    data_files = data_files,
    windows= [
        {
            "script" : "Noethys.py",
            "icon_resources" : [(1, "Icone.ico")],
            "other_resources": [(24,1, manifest)]
        }
        
    ],)

# Insertions manuelles dans le ZIP
z = zipfile.ZipFile(os.path.join("dist/" 'library.zip'), 'a')

# Timezone de pytz :
import pytz
zoneinfo_dir = os.path.join(os.path.dirname(pytz.__file__), 'zoneinfo')
disk_basedir = os.path.dirname(os.path.dirname(pytz.__file__))
for absdir, directories, filenames in os.walk(zoneinfo_dir):
    assert absdir.startswith(disk_basedir), (absdir, disk_basedir)
    zip_dir = absdir[len(disk_basedir):]
    for f in filenames:
      z.write(os.path.join(absdir, f), os.path.join(zip_dir, f))

# Typelibs Microsoft Speech pour Windows XP
nom = "C866CA3A-32F7-11D2-9602-00C04F8EE628x0x5x0.py"
z.write("Outils/%s" % nom, "win32com/gen_py/%s" % nom)

z.close()