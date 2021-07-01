# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=['D:\\Programming\\SurfEarner'],
             binaries=[],
             datas=[],
             hiddenimports=['re', 'pyAesCrypt', 'urllib3.exceptions.MaxRetryError', 'urllib3.exceptions.ProtocolError', 'selenium.webdriver', 'selenium.common.exceptions.NoSuchElementException', 'selenium.common.exceptions.StaleElementReferenceException', 'selenium.common.exceptions.WebDriverException', 'selenium.webdriver.common.action_chains.ActionChains', 'selenium.webdriver.common.by.By', 'selenium.webdriver.common.keys.Keys', 'selenium.webdriver.support.expected_conditions', 'selenium.webdriver.support.wait.WebDriverWait'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['os.path', 'os.getcwd', 'os.remove', 'os.system', 'sys.exit', 'time.sleep', 'time.time'],
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
          name='Automatic Chrome',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True, version='version.rc' )
