import pytest


@pytest.fixture
def test_wallet_keys() -> dict:
    return {
        'private': '4252c4abbdb595c08ff042f1af78b019c49792b881c9730cde832815570cf8d7',
        'public': '02bfc63dd13b7f9ed08f7804470b2a10d039583e2de21a92c8ff4bc0f0e29e4506'
    }
