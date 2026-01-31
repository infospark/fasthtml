from data_types import Failure


def test_failure_is_false() -> None:
    assert not Failure("Test failure")
