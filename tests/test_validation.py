
from fitgator.services.validation import valid_profile_fields

def test_valid_profile_fields():
    assert valid_profile_fields(25, 80.0, 178.0)
    assert not valid_profile_fields(8, 80.0, 178.0)
    assert not valid_profile_fields(25, 10.0, 178.0)
    assert not valid_profile_fields(25, 80.0, 90.0)
