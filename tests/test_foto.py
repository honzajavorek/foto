import os
import importlib

import foto


def test_sets_geocoding_api_key_on_import():
    os.environ['FOTO_GEOCODING_API_KEY'] = 'xyz'
    importlib.reload(foto)
    assert foto.config['geocoding']['key'] == 'xyz'
