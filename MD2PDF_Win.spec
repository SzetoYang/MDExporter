# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['MD2PDF.py'],
             pathex=[],
             binaries=[('C:\Program Files\Pandoc\pandoc.exe','bin'),('C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe','bin')],
             datas=[('.\\templates\highlight.js','.'),
                    ('.\\templates\highlight.css','.'),
                    ('.\\templates\cover.html','.'),
                    ('.\\templates\statement.html','.'),
                    ('.\\templates\style.css','.'),
                    ('.\\templates\logo.png','.'),
                    ('.\\templates\smalllogo.png','.'),
                    ('.\\templates\header.html','.'),
                    ('.\\templates\icon.ico','.')
             ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='MDExporter',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          icon='./templates/icon.ico',
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
