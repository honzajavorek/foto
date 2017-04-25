Elk
===

Elk is **my personal** photo manager. I don't like tools pretending to be
smarter than me. I like file-system based management and I couldn't find
a folder-based manager which could do couple of simple tasks the way I want.

Installation
------------

Only macOS and Python 3 are supported, beause that's what I currently use.

:: code:: sh

    $ git clone git@github.com:honzajavorek/elk.git
    $ cd elk
    $ cat brew_packages.txt | xargs brew install
    $ python3 -m venv env
    $ . ./env/bin/activate
    (env)$ pip install -e .

Put ``.../env/bin/elk`` into your ``~/.bash_profile`` as an alias and you're done:

:: code:: sh

    $ echo 'alias elk=".../env/bin/elk"' >> ~/.bash_profile

Why Elk?
--------

Because it is a lovely short word. Short enough to be typed often into
my terminal. And because I lived in Finland for a while.

License: ISC
------------

© 2010-? Honza Javorek mail@honzajavorek.cz

This work is licensed under `ISC
license <https://en.wikipedia.org/wiki/ISC_license>`__.
