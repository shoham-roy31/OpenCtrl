import numpy as np
from typing import List,Optional
from OpenCtrl.SystemDynamicExample.base_sys import BaseSystem
def assert_params(**args):
    def _check_prevs(key : str) -> None:
        if not isinstance(args[key],np.ndarray):
            raise TypeError(f"{key} should of type np.ndarray but got {type(args[key])}")
        
    if 'horizon' in args:
        if not isinstance(args['horizon'], int):
            raise TypeError(f"horizon is an interger type, but got {type(args['horizon'])}")
    if 'disturbance' in args:
        if not isinstance(args['window_size'],int):
            raise TypeError(f"window_size should be of type int but got {type(args['window_size'])}")
        if args['window_size'] <= 0:
            raise TypeError(f"window_size cannot have 0 and negative dimension got window_size : {args['window_size']}")
    if 'window' in args:
        if not isinstance(args['window'],list):
            raise TypeError(f"window should be a list but got {type(args['window'])}")
        if len(args['window']) != args['window_size']:
            raise ValueError(f"Size of window is not equal to window_size found : {args['window']} != {args['window_size']} ")
        if not all(isinstance(_, np.ndarray) for _ in args['window']):
            raise TypeError(f"elements in window should be of type np.ndarray vector: {args['window_size']}")
    if 'prev_ema' in args:
        _check_prevs('prev_ema')        
    if 'prev_real' in args:
        _check_prevs('prev_real')
    if 'alpha' in args:
        if not isinstance(args['alpha'],float):
            raise TypeError(f"alhpa should be of type float but got {type(args['alpha'])}")
        if not args['alpha'] >= 0 and args['alpha'] <= 1:
            raise ValueError(f"alpha should be in range of [0,1] but got {args['alpha']}")
    if 'base_line' in args:
        if not isinstance(args['base_line'],(float,int)):
            raise TypeError(f"base_line should be of type float or int but got {type(args['base_line'])}")
    if 'system' in args:
        if not isinstance(args['system'],BaseSystem):
            raise TypeError(f"system type must inhert from type BaseSystem but found type {type(args['system'])}")
        if args['system'].disturbance_type == 'exponential':
            raise ValueError(f"setbased_nominal method cannot be determined with disturbance type : {args['system'].disturbance_type}")
        
def baseline_disturbance(horizon : int,
                         window_size : int,
                         base_line : float = 0.1
                         ) -> List[np.ndarray]:
    assert_params(**locals())
    return [np.full(fill_value = base_line,shape=window_size)\
            for _ in range(horizon)]

def meanbasline_disturbance(horizon: int,
                            window : List[np.ndarray],
                            window_size : int,
                            ) -> List[np.ndarray]:
    assert_params(**locals())
    means = []
    for _ in range(horizon):
        means_per_dim = []
        means_per_dim.append(np.mean(window, axis = 0))
        window.pop()
        window.extend(np.array(means_per_dim))
        means.extend(np.array(means_per_dim))
    return means

def ema_disturbance(horizon : int,
                    prev_ema : np.ndarray,
                    prev_real : np.ndarray,
                    window_size : int,
                    alpha : Optional[float] = 0.01
                    ) -> List[np.ndarray]:
    assert_params(**locals())
    def ema(phi:np.ndarray,
            d : np.ndarray
            )-> np.ndarray:
        if not np.size(phi) == np.size(d):
            raise ValueError(f"dim of prev_ema: {np.size(phi)} not equal to dim of prev_real: {np.size(d)}")
        return alpha*phi + (1-alpha)*d
    avgs = []
    for _ in range(horizon):
        avgs.append(ema(prev_ema,prev_real))
        prev_ema = avgs[-1]
    return avgs
