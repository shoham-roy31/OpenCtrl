import numpy as np
from typing import Optional,List
from .functionals import (baseline_disturbance,
                          meanbasline_disturbance,
                          ema_disturbance)
from ..SystemDynamicExample.linear_sys import LinearSystem
def _test_all(  horizon: Optional[int] = 2,
                disturbance_dim : Optional[int] = 3,
                window : Optional[List[np.ndarray]] = [np.array([1.0,1.0,3.0]),
                                                     np.array([1.0,1.0,2.0]),
                                                     np.array([1.0,1.0,1.0])],
                prev_ema : Optional[np.ndarray] = np.array([10,22,32]),
                prev_real : Optional[np.ndarray] = np.array([4,5,6])
            ) -> None:
    try:
        res = baseline_disturbance(horizon,
                             disturbance_dim)
        print(f"1.✅ Test Passed baseline: {res}")
    except Exception as e:
        print(f"1.❌ Test Falied baseline: {e}")
    
    try:
        res = meanbasline_disturbance(horizon,
                                window,
                                disturbance_dim)
        print(f"2.✅ Test Passed mean_baseline: {res}")
    except Exception as e:
        print(f"2.❌ Test Failed mean_baseline: {e}")
    try:
        res = ema_disturbance(horizon,
                              prev_ema,
                              prev_real,
                              disturbance_dim)
        print(f"3.✅ Test Passed ema_disturbance: {res}")
    except Exception as e:
        print(f"3.❌ Test Failed ema_disturbance: {e}")

if __name__ == "__main__":
    _test_all()
