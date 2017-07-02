foto
====

|PyPI version| |Build Status|

``foto`` is **my personal** photo manager. I don't like tools pretending to be
smarter than me. I like file-system based management and I couldn't find
a folder-based manager which could do couple of simple tasks the way I want.

Development
-----------

Only macOS and Python 3 are supported, beause that's what I currently use.

.. code:: sh

    $ git clone git@github.com:honzajavorek/foto.git
    $ cd foto
    $ cat brew_packages.txt | xargs brew install
    $ python3 -m venv env
    $ . ./env/bin/activate
    (env)$ pip install -e .

Your ``~/.bash_profile``:

.. code:: sh

    alias elk="/Users/honza/.../foto/env/bin/foto"
    export FOTO_GEOCODING_API_KEY='...'

License: ISC
------------

© 2010-? Honza Javorek mail@honzajavorek.cz

This work is licensed under `ISC
license <https://en.wikipedia.org/wiki/ISC_license>`__.

.. |PyPI version| image:: https://badge.fury.io/py/foto.svg
   :target: https://badge.fury.io/py/foto
.. |Build Status| image:: https://travis-ci.org/honzajavorek/foto.svg?branch=master
   :target: https://travis-ci.org/honzajavorek/foto
