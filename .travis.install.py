#!/usr/bin/env python
# Part of `travis-lazarus` (https://github.com/nielsAD/travis-lazarus)
# License: MIT

import os
import subprocess

OS_NAME=os.environ.get('TRAVIS_OS_NAME') or 'linux'
OS_PMAN={'linux': 'sudo apt-get', 'osx': 'brew'}[OS_NAME]

LAZ_TMP_DIR=os.environ.get('LAZ_TMP_DIR') or 'lazarus_tmp'
LAZ_REL_DEF=os.environ.get('LAZ_REL_DEF') or {'linux':'amd64', 'osx':'i386', 'wine':'32'}
LAZ_BIN_SRC=os.environ.get('LAZ_BIN_SRC') or 'http://mirrors.iwi.me/lazarus/releases/%(target)s/Lazarus%%20%(version)s'
LAZ_BIN_TGT=os.environ.get('LAZ_BIN_TGT') or {
    'linux': 'Lazarus%%20Linux%%20%(release)s%%20DEB',
    'osx':   'Lazarus%%20Mac%%20OS%%20X%%20%(release)s',
    'wine':  'Lazarus%%20Windows%%20%(release)s%%20bits'
}

def install_osx_dmg(dmg):
    try:
        # Mount .dmg file and parse (automatically determined) target volumes
        res = subprocess.check_output('sudo hdiutil attach %s | grep /Volumes/' % (dmg), shell=True)
        vol = ('/Volumes/' + l.strip().split('/Volumes/')[-1] for l in res.splitlines() if '/Volumes/' in l)
    except:
        return False

    # Install .pkg files with installer
    install_pkg = lambda v, f: os.system('sudo installer -pkg %s/%s -target /' % (v, f)) == 0

    for v in vol:
        try:
            if not all(map(lambda f: (not f.endswith('.pkg')) or install_pkg(v, f), os.listdir(v))):
                return False
        finally:
            # Unmount after installation
            os.system('hdiutil detach %s' % (v))

def install_lazarus_default():
    return os.system('%s update && %s install lazarus lcl-nogui' % (OS_PMAN, OS_PMAN)) == 0

def install_lazarus_version(ver,rel,wine):
    # Download directory for specified Lazarus version
    osn = 'wine' if wine else OS_NAME
    tgt = LAZ_BIN_TGT[osn] % {'release': rel or LAZ_REL_DEF[osn]}
    src = LAZ_BIN_SRC % {'target': tgt, 'version': ver}
    if os.system('wget -r -l1 -T 30 -np -nd -nc -A .deb,.dmg,.exe %s -P %s' % (src, LAZ_TMP_DIR)) != 0:
        return False

    if wine:
        if os.system('%s update && %s install wine' % (OS_PMAN, OS_PMAN)) != 0:
            return False

        # Set wine Path (persistently) to include Lazarus binary directory
        if os.system('%s cmd /C reg add HKEY_CURRENT_USER\\\\Environment /v PATH /t REG_SZ /d %%PATH%%\\;c:\\\\lazarus' % (wine)) != 0:
            return False;

        # Install all .exe files with wine
        process_file = lambda f: (not f.endswith('.exe')) or os.system('%s %s /VERYSILENT /DIR="c:\\lazarus"' % (wine, f)) == 0
    elif OS_NAME == 'linux':
        # Install all .deb files
        process_file = lambda f: (not f.endswith('.deb')) or os.system('sudo dpkg -i %s' % (f)) == 0
    elif OS_NAME == 'osx':
        # Install all .dmg files
        process_file = lambda f: (not f.endswith('.dmg')) or install_osx_dmg(f)
    else:
        return False

    return all(map(lambda f: process_file(os.path.join(LAZ_TMP_DIR, f)), sorted(os.listdir(LAZ_TMP_DIR))))

def install_lazarus(ver=None,rel=None,wine=None):
    return install_lazarus_version(ver,rel,wine) if ver else install_lazarus_default()

def main():
    return install_lazarus(os.environ.get('LAZ_VER'),os.environ.get('LAZ_REL'),os.environ.get('LAZ_WINE'))

if __name__ == '__main__':
    main()
