#!/usr/bin/env python
# Part of `travis-lazarus` (https://github.com/nielsAD/travis-lazarus)
# License: MIT

import sys
import os
import subprocess

OS_NAME=os.environ.get('TRAVIS_OS_NAME') or 'linux'
OS_PMAN={'linux': 'sudo apt-get -q --force-yes', 'osx': 'brew'}[OS_NAME]

LAZ_TMP_DIR=os.environ.get('LAZ_TMP_DIR') or 'lazarus_tmp'
LAZ_REL_DEF=os.environ.get('LAZ_REL_DEF') or {'linux':'amd64', 'qemu-arm':'amd64', 'qemu-arm-static':'amd64', 'osx':'i386', 'wine':'32'}
LAZ_BIN_SRC=os.environ.get('LAZ_BIN_SRC') or 'https://sourceforge.net/projects/lazarus/files/%(target)s/Lazarus%%20%(version)s/'
LAZ_BIN_TGT=os.environ.get('LAZ_BIN_TGT') or {
    'linux':           'Lazarus%%20Linux%%20%(release)s%%20DEB',
    'qemu-arm':        'Lazarus%%20Linux%%20%(release)s%%20DEB',
    'qemu-arm-static': 'Lazarus%%20Linux%%20%(release)s%%20DEB',
    'osx':             'Lazarus%%20Mac%%20OS%%20X%%20%(release)s',
    'wine':            'Lazarus%%20Windows%%20%(release)s%%20bits'
}

def system(cmd):
    print("travis-lazarus: " + cmd)
    return os.system(cmd)

def install_osx_dmg(dmg):
    try:
        # Mount .dmg file and parse (automatically determined) target volumes
        res = subprocess.check_output('sudo hdiutil attach %s | grep /Volumes/' % (dmg), shell=True)
        vol = ('/Volumes/' + l.strip().split('/Volumes/')[-1] for l in res.splitlines() if '/Volumes/' in l)
    except:
        return False

    # Install .pkg files with installer
    install_pkg = lambda v, f: system('sudo installer -pkg %s/%s -target /' % (v, f)) == 0

    for v in vol:
        try:
            if not all(map(lambda f: (not f.endswith('.pkg')) or install_pkg(v, f), os.listdir(v))):
                return False
        finally:
            # Unmount after installation
            system('hdiutil detach %s' % (v))

    return True

def install_lazarus_default():
    if OS_NAME == 'linux':
        # Make sure nogui is installed for headless runs
        pkg = 'lazarus lcl-nogui'
    elif OS_NAME == 'osx':
        # Install brew cask first
        pkg = 'fpc caskroom/cask/brew-cask && %s cask install fpcsrc lazarus' % (OS_PMAN)
    else:
        # Default to lazarus
        pkg = 'lazarus'
    return system('%s install %s' % (OS_PMAN, pkg)) == 0

def install_lazarus_version(ver,rel,env):
    # Download all files in directory for specified Lazarus version
    osn = env or OS_NAME
    tgt = LAZ_BIN_TGT[osn] % {'release': rel or LAZ_REL_DEF[osn]}
    src = LAZ_BIN_SRC % {'target': tgt, 'version': ver}

    if system('wget -w 1 -np -m -A download %s' % (src)) != 0:
        return False

    if system('grep -Rh refresh sourceforge.net/ | grep -o "https://[^\\?]*" > urllist') != 0:
        return False

    if system('while read url; do wget --content-disposition "${url}"  -A .deb,.dmg,"lazarus-*-fpc-3.*.0-win32.exe" -P %s; done < urllist'  % (LAZ_TMP_DIR)) != 0:
        return False

    if osn == 'wine':
        PKG_WINE={'bionic': 'wine32 wine-stable', 'focal': 'wine32 wine-stable'}.get(os.environ.get('TRAVIS_DIST'), 'wine')

        # Install wine and Xvfb
        if system('sudo dpkg --add-architecture i386 && %s update && %s install xvfb %s' % (OS_PMAN, OS_PMAN, PKG_WINE)) != 0:
            return False

        # Initialize virtual display and wine directory
        if system('Xvfb %s & sleep 3 && (wineboot -i || wineboot-stable -i)' % (os.environ.get('DISPLAY') or '')) != 0:
            return False

        # Install basic Wine prerequisites, ignore failure
        system('winetricks -q corefonts')

        # Install all .exe files with wine
        process_file = lambda f: (not f.endswith('.exe')) or system('wine %s /VERYSILENT /DIR="c:\\lazarus"' % (f)) == 0
    elif osn == 'qemu-arm' or osn == 'qemu-arm-static':
        # Install qemu and arm cross compiling utilities
        if system('%s install libgtk2.0-dev qemu-user qemu-user-static binutils-arm-linux-gnueabi gcc-arm-linux-gnueabi libc-dev-armel-cross' % (OS_PMAN)) != 0:
            return False

        # Install all .deb files (for linux) and cross compile later
        process_file = lambda f: (not f.endswith('.deb')) or system('sudo dpkg --force-overwrite -i %s' % (f)) == 0
    elif osn == 'linux':
        # Install dependencies
        if system('%s install libgtk2.0-dev' % (OS_PMAN)) != 0:
            return False

        # Install all .deb files
        process_file = lambda f: (not f.endswith('.deb')) or system('sudo dpkg --force-overwrite -i %s' % (f)) == 0
    elif osn == 'osx':
        # Install all .dmg files
        process_file = lambda f: (not f.endswith('.dmg')) or install_osx_dmg(f)
    else:
        return False

    # Process all downloaded files
    if not all(map(lambda f: process_file(os.path.join(LAZ_TMP_DIR, f)), sorted(os.listdir(LAZ_TMP_DIR)))):
        return False

    if osn == 'wine':
        # Set wine Path (persistently) to include Lazarus binary directory
        if system('wine cmd /C reg add HKEY_CURRENT_USER\\\\Environment /v PATH /t REG_SZ /d "%PATH%\\;c:\\\\lazarus"') != 0:
            return False

        # Redirect listed executables so they execute in wine
        for alias in ('fpc', 'lazbuild', 'lazarus'):
            system('echo "#!/usr/bin/env bash \nwine %(target)s \$@" | sudo tee %(name)s > /dev/null && sudo chmod +x %(name)s' % {
                'target': subprocess.check_output("find $WINEPREFIX -iname '%s.exe' | head -1 " % (alias), shell=True).strip().decode(encoding='UTF-8'),
                'name': '/usr/bin/%s' % (alias)
            })
    elif osn == 'qemu-arm' or osn == 'qemu-arm-static':
        fpcv = subprocess.check_output('fpc -iV', shell=True).strip().decode(encoding='UTF-8')
        gccv = subprocess.check_output('arm-linux-gnueabi-gcc -dumpversion', shell=True).strip().decode(encoding='UTF-8')
        opts = ' '.join([
            'CPU_TARGET=arm',
            'OS_TARGET=linux',
            'BINUTILSPREFIX=arm-linux-gnueabi-',
            # 'CROSSOPT="-CpARMV7A -CfVFPV3_D16"',
            'OPT=-dFPC_ARMEL',
            'INSTALL_PREFIX=/usr'
        ])

        # Compile ARM cross compiler
        if system('cd /usr/share/fpcsrc/%s && sudo make clean crossall crossinstall %s' % (fpcv, opts)) != 0:
            return False
        
        # Symbolic link to update default FPC cross compiler for ARM
        if system('sudo ln -sf /usr/lib/fpc/%s/ppcrossarm /usr/bin/ppcarm' % (fpcv)) != 0:
            return False

        # Update config file with paths to ARM libraries
        config = '\n'.join([
            '#INCLUDE /etc/fpc.cfg',
            '#IFDEF CPUARM',
            '-Xd','-Xt',
            '-XParm-linux-gnueabi-',
            '-Fl/usr/arm-linux-gnueabi/lib',
            '-Fl/usr/lib/gcc/arm-linux-gnueabi/%s' % (gccv),
            '-Fl/usr/lib/gcc-cross/arm-linux-gnueabi/%s' % (gccv),
            # '-CpARMV7A', '-CfVFPV3_D16',
            '#ENDIF',
            ''
        ])
        with open(os.path.expanduser('~/.fpc.cfg'),'w') as f:
            f.write(config)

    return True

def install_lazarus(ver=None,rel=None,env=None):
    return install_lazarus_version(ver,rel,env) if ver else install_lazarus_default()

def main():
    system('%s update' % (OS_PMAN))
    return install_lazarus(os.environ.get('LAZ_VER'),os.environ.get('LAZ_REL'),os.environ.get('LAZ_ENV'))

if __name__ == '__main__':
    sys.exit(int(not main()))
