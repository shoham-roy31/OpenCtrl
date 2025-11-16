import pytest
from typing import Callable
from ..controls.test import _test_lac_1
from ..optim.test import (
    test_optimizer_schema,
    test_vanilla_optim,
)
from ..SystemDynamicExample.test import (
    test_base_system_initialization,
    test_linear_system_initialization
)
from ..disturbances_type.test import _test_all

def call(obj : Callable):
    if isinstance(obj, list):
        try:
            obj()
            assert True, f"{obj.__name__} Passed"
        except Exception as e:
            assert False, f"{obj.__name__} Failed: {e}"
    else:
        assert False, f"{obj} is not callable"

if __name__ == "__main__":
    tests = [
        test_base_system_initialization,
        test_linear_system_initialization,
        _test_all,
        test_optimizer_schema,
        test_vanilla_optim,
        _test_lac_1
    ]
    for test in tests:
        call(test)


