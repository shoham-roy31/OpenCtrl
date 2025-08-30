from optim.optimizer_schema import OptimizerSchema
from SystemDynamicExample.base_sys import BaseSystem
from disturbances_type.functionals import (baseline_disturbance,
                                           meanbasline_disturbance,
                                           ema_disturbance) 
from typing import Literal,Optional,List
NOMINAL_TYPES = ['baseline','mean_baseline','ema','setbased']
def assert_inputs(**args) -> None:
    if 'system' in args:
        if not isinstance(args['system'], BaseSystem):
            raise TypeError(f"system must be an instance of BaseSystem but got {type(args['system'])}")
    if 'optimizer' in args:
        if not isinstance(args['optimizer'], OptimizerSchema):
            raise TypeError(f"optimizer must be an instance of OptimizerSchema but got {type(args['optimizer'])}")
    if 'horizon' in args:
        if not isinstance(args['horizon'], int):
            raise TypeError(f"horizon must be a type int but found {type(args['horizon'])}")
        if args['horizon'] <= 0:
            raise ValueError(f"horzion should be in range [1, inf) but got {args['horizon']}")
    if 'nominal_disturbance' in args:
        if not isinstance(args['nominal_disturbance'],str):
            raise TypeError(f"nominal_distrubance should of type str but got {type(args['nominal_distrubance'])}")
        if not args['nominal_disturbance'].lower() in NOMINAL_TYPES:
            raise ValueError(f"nominal_disturbance should be within {NOMINAL_TYPES} but got {type(args['nominal_distrubance'])}")
class ControlSchema:
    def __init__(self,
                 system : BaseSystem,
                 optimizer : OptimizerSchema,
                 horizon : int = 1,
                nominal_disturbance : Literal['baseline',
                                              'mean_baseline',
                                              'ema',
                                              'setbased'] = 'baseline' 
                 ) -> None:
        args = locals()
        assert_inputs(**args)
        self.system = system
        self.optimizer = optimizer
        self.horizon = horizon
        self.nominal_disturbance = nominal_disturbance
    def tune(self) -> None:
        raise NotImplementedError("The tune method must be implemented in the subclass.")
    
    def _wrapper_disturbance(self,
                             horizon : int,
                             disturbance_dim : int,
                             window : int,
                             prev_ema : List[float],
                             prev_real : List[float],
                             alpha : Optional[float] = 0.01
                             ) -> callable:
        if self.nominal_disturbance.lower() == 'baseline':
            return baseline_disturbance(horizon,
                                        disturbance_dim)
        elif self.nominal_disturbance.lower() == 'mean_baseline':
            return meanbasline_disturbance(horizon,
                                           window,
                                           disturbance_dim)
        elif self.nominal_disturbance.lower() == 'ema':
            return ema_disturbance(horizon,
                                   prev_ema,
                                   prev_real,
                                   disturbance_dim,
                                   alpha = alpha if not 0.01 else 0.01)
