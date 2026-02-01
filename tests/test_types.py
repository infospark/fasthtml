from data_types import Failure, Success


def test_failure_is_false() -> None:
    assert not Failure("Test failure")

def test_success_is_true() -> None:
    assert Success("Test success")
