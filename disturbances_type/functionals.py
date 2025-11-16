import numpy as np
from typing import List,Optional
from ..SystemDynamicExample.base_sys import BaseSystem
def assert_params(**args):
    def _check_prevs(key : str) -> None:
        if not isinstance(args[key],np.ndarray):
            raise TypeError(f"{key} should of type np.ndarray but got {type(args[key])}")
        if not (np.size(args[key]) == args['disturbance_dim']):
            raise ValueError(f"{key} should be a vector of size {args['disturbance_dim']} rather got {np.size(args[key])}")
        
    if 'horizon' in args:
        if not isinstance(args['horizon'], int):
            raise TypeError(f"horizon is an interger type, but got {type(args['horizon'])}")
    if 'disturbance' in args:
        if not isinstance(args['disturbance_dim'],int):
            raise TypeError(f"disturbance_dim should be of type int but got {type(args['disturbance_dim'])}")
        if args['disturbance_dim'] <= 0:
            raise TypeError(f"disturbance_dim cannot have 0 and negative dimension got disturbance_dim : {args['disturbance_dim']}")
    if 'window' in args:
        if not isinstance(args['window'],list):
            raise TypeError(f"window should be a list but got {type(args['window'])}")
        if len(args['window']) == 0:
            raise ValueError(f"window can not be empty list")
        if not all(isinstance(_, np.ndarray) and np.shape(_)[0] == args['disturbance_dim'] for _ in args['window']):
            raise TypeError(f"elements in window should be of type np.ndarray vector and of length disturbance_dim : {args['disturbance_dim']}")
    if 'prev_ema' in args:
        _check_prevs('prev_ema')        
    if 'prev_real' in args:
        _check_prevs('prev_real')
    if 'alpha' in args:
        if not isinstance(args['alpha'],float):
            raise TypeError(f"alhpa should be of type float but got {type(args['alpha'])}")
        if not args['alpha'] >= 0 and args['alpha'] <= 1:
            raise ValueError(f"alpha should be in range of [0,1] but got {args['alpha']}")
    
    if 'system' in args:
        if not isinstance(args['system'],BaseSystem):
            raise TypeError(f"system type must inhert from type BaseSystem but found type {type(args['system'])}")
        if args['system'].disturbance_type == 'exponential':
            raise ValueError(f"setbased_nominal method cannot be determined with disturbance type : {args['system'].disturbance_type}")
        
def baseline_disturbance(horizon : int,
                         disturbance_dim : int
                         ) -> List[np.ndarray]:
    assert_params(**locals())
    return [np.zeros(shape=(disturbance_dim))\
            for _ in range(horizon)]

def meanbasline_disturbance(horizon: int,
                            window : List[np.ndarray],
                            disturbance_dim : int,
                            ) -> List[np.ndarray]:
    assert_params(**locals())
    means = []
    for _ in range(horizon):
        means_per_dim = []
        for dim in range(disturbance_dim):
            means_per_dim.append(np.mean(window[dim]))
        window.pop()
        window.append(np.array(means_per_dim))
        means.append(np.array(means_per_dim))
    return means

def ema_disturbance(horizon : int,
                    prev_ema : np.ndarray,
                    prev_real : np.ndarray,
                    disturbance_dim : int,
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
