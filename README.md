Travis CI integration for FPC / Lazarus
=======================================

[![Build Status](https://travis-ci.org/nielsAD/travis-lazarus.svg?branch=master)](https://travis-ci.org/nielsAD/travis-lazarus)

[Travis CI](https://travis-ci.org/) currently has no official support for [FreePascal](http://freepascal.org/). This repository demonstrates how FPC and [Lazarus](http://www.lazarus-ide.org/) projects can be used in combination with Travis. There is support for compilation with several release versions on both `Linux (Ubuntu)` and `Mac OSX` platforms.

Files
-----
`./.travis.install.py` Sets up the environment by downloading and installing the proper FreePascal and Lazarus versions.

`./.travis.yml` Custom Travis setup. Refer to their [documentation](http://docs.travis-ci.com/user/customizing-the-build/) for more information.
