#!/usr/bin/env python
# Part of `travis-lazarus` (https://github.com/nielsAD/travis-lazarus)
# License: MIT

import os
import subprocess

OS_NAME = os.environ.get('TRAVIS_OS_NAME') or 'linux'

LAZ_TMP_DIR=os.environ.get('LAZ_TMP_DIR') or 'lazarus_tmp'
LAZ_DEB_DIR=os.environ.get('LAZ_DEB_DIR') or 'http://mirrors.iwi.me/lazarus/releases/Lazarus%%20%(release)s/Lazarus%%20%(version)s'
LAZ_DEB_REL={'linux': 'Linux%20amd64%20DEB', 'osx': 'Mac%20OS%20X%20i386'}

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
	if OS_NAME == 'linux':
		# Use apt-get to install default Lazarus and dependencies
		return os.system('sudo apt-get update -qq && sudo apt-get install -qq lazarus lcl-nogui') == 0
	else:
		return False

def install_lazarus_version(ver):
	# Download directory for specified Lazarus version
	SRC = LAZ_DEB_DIR % {'release': LAZ_DEB_REL[OS_NAME], 'version': ver}
	if os.system('wget -r -q -l1 -T 30 -np -nd -A .deb,.dmg %s -P %s' % (SRC, LAZ_TMP_DIR)) != 0:
		return False

	if OS_NAME == 'linux':
		# Install all .deb files
		process_file = lambda f: (not f.endswith('.deb')) or os.system('sudo dpkg -i %s' % (f)) == 0
	elif OS_NAME == 'osx':
		# Install all .dmg files
		process_file = lambda f: (not f.endswith('.dmg')) or install_osx_dmg(f)
	else:
		return False

	return all(map(lambda f: process_file(os.path.join(LAZ_TMP_DIR, f)), sorted(os.listdir(LAZ_TMP_DIR))))

def install_lazarus(ver=None):
	return install_lazarus_version(ver) if ver else install_lazarus_default()

def main():
	return install_lazarus(os.environ.get('LAZ_VER'))

if __name__ == '__main__':
	main()
