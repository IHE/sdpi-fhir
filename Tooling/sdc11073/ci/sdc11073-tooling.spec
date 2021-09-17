# -*- mode: python -*-
import os
import sdc11073


sdc11073dir = os.path.dirname(os.path.abspath(sdc11073.__file__))

a = Analysis(['../Tests/TestRunner.py'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None)

xsd_files = Tree(os.path.join(sdc11073dir, 'xsd'), prefix = 'sdc11073/xsd')
pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=None)
exe = EXE(pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas,
            xsd_files,
            name='TestRunner',
            debug=False,
            strip=False,
            console=True)
