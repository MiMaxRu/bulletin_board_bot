import inspect
from app import main


def test_main_defined():
    assert inspect.iscoroutinefunction(main.main)
