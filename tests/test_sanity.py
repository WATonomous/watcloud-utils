import watcloud_utils

def test_version():
    assert hasattr(watcloud_utils, "__version__") and watcloud_utils.__version__ is not None and watcloud_utils.__version__ == "123"
