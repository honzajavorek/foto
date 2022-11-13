foto
====

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
    $ poetry install

Your ``~/.bash_profile``:

.. code:: sh

    alias foto="/Users/honza/.../foto/env/bin/foto"
    export FOTO_GEOCODING_API_KEY='...'

License: ISC
------------

© 2010-2022, Honza Javorek <mail@honzajavorek.cz>

This work is licensed under `ISC
license <https://en.wikipedia.org/wiki/ISC_license>`__.


Credits
-------

- Zuzana Válková
- Martin Javorek
