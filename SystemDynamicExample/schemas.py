from typing import Literal, Optional, Union

def assert_inputs(args):
    if 'type' in args:
        if not isinstance(args['type'], str):
            raise TypeError(f"type must be a string but got {type(args['type'])}")
        if args['type'] not in ['random','continuous','discrete']:
            raise ValueError(f"type must be 'continuous' or 'discrete' but got {args['type']}")
    if 'max_value' in args:
        if not isinstance(args['max_value'], (int, float)):
            raise TypeError(f"max_value must be a number but got {type(args['max_value'])}")
    if 'min_value' in args:
        if not isinstance(args['min_value'], (int, float)):
            raise TypeError(f"min_value must be a number but got {type(args['min_value'])}")
    try:
        if 'sampling' in args:
            if not isinstance(args['sampling'], str):
                raise TypeError(f"sampling must be a string but got {type(args['sampling'])}")
            if args['sampling'] not in ['uniform', 'normal']:
                raise ValueError(f"sampling must be 'uniform' or 'normal' but got {args['sampling']}")
    except KeyError:
        pass
    try:
        if 'step' in args:
            if not isinstance(args['step'], (int, float)):
                raise TypeError(f"step must be a number but got {type(args['step'])}")
            if args['step'] <= 0:
                raise ValueError(f"step must be a positive number but got {args['step']}")
    except KeyError:
        pass
        
class InputSpace:
    def __init__(self,
                 type : str,
                 min_value : float,
                 max_value : float
                 ) -> None:
        args = locals()
        assert_inputs(args)
        self.type = type
        self.max_value = max_value
        self.min_value = min_value

class InputSpaceRandom(InputSpace):
    def __init__(self,
                 sampling : Literal['uniform', 'normal'] = 'uniform',
                 min_value : Optional[float] = 1.0,
                 max_value : Optional[float] = 0.0
                 ) -> None:
        super().__init__(type='random', max_value=max_value, min_value=min_value)
        assert_inputs(args = {'sampling' : sampling})
        self.sampling = sampling

class InputSpaceContinuous(InputSpace):
    def __init__(self,
                 min_value : float = 1.0,
                 max_value : float = 0.0
                 ) -> None:
        super().__init__(type='continuous', max_value=max_value, min_value=min_value)
        pass

class InputSpaceDiscrete(InputSpace):
    def __init__(self,
                 min_value : float = 1.0,
                 max_value : float = 0.0,
                 step : Optional[Union[float,int]] = 1
                 ) -> None:
        super().__init__(type='discrete', max_value=max_value, min_value=min_value)
        assert_inputs(args = {'step' : step})
        self.step = step
        pass