import os


def test_sets_geocoding_api_key_on_import():
    os.environ['ELK_GEOCODING_API_KEY'] = 'xyz'
    import elk
    assert elk.config['geocoding']['key'] == 'xyz'
