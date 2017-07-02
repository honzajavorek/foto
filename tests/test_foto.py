import os


def test_sets_geocoding_api_key_on_import():
    os.environ['FOTO_GEOCODING_API_KEY'] = 'xyz'
    import foto
    assert foto.config['geocoding']['key'] == 'xyz'
