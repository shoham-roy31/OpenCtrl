import numpy as np
from typing import Literal, Optional, List, Union, Tuple
from .base_sys import BaseSystem
from .schemas import InputSpaceRandom, InputSpaceContinuous, InputSpaceDiscrete
def assert_inputs(**args):
    if 'sys_type' in args:
        if not isinstance(args['sys_type'], str):
            raise TypeError(f"sys_type must be a string but got {type(args['sys_type'])}")
        if args['sys_type'] not in ['continuous', 'discrete']:
            raise ValueError(f"sys_type must be 'continuous' or 'discrete' but got {args['sys_type']}")
    if 'input_space' in args:
        if not isinstance(args['input_space'], dict):
            raise TypeError(f"input_space must be a dictionary but got {type(args['input_space'])}")
        count = 0
        for _, values in enumerate(args['input_space'].values()):
            count += 1
        if count != args['input_dim'] and count <= args['sys_dim']:
            raise ValueError(f"input_space must have {args['input_dim']} entries but got {count}")
        try:
            for _, v in args['input_space'].items():
                count = 0
                for key, value in v.items():
                    count += 1
                    if key == 'continuous':
                        if not len(value) == 2:
                            raise ValueError(f"input_space['continuous'] must have at least 2 values for min and max but got {len(value)}")
                    elif key == 'random' or key == 'discrete':
                        if len(value) < 2:
                            raise ValueError(f"input_space['{key}'] must have at least 2 values for sampling, min, and max but got {len(value)}")
                    else:
                        raise ValueError(f"input_space must contain 'continuous', 'random', or 'discrete' keys but got {key}")
                    if count > 1:
                        raise ValueError("A single dimension can have one type of input schema, but found multiples")
        except Exception as e:
            raise ValueError("Input Space Schema is improper follow : '{'dim_name : {InputType : [params]}}}'")
                    
    if 'disturbance_dim' in args and args['disturbance_dim'] != 'full':
        if not isinstance(args['disturbance_dim'], (int, str)):
            raise TypeError(f"disturbance_dim must be an integer or 'full' but got {type(args['disturbance_dim'])}")
        if isinstance(args['disturbance_dim'], int) and args['disturbance_dim'] <= 0 and args['disturbance_dim'] <= args['sys_dim']:
            raise ValueError(f"disturbance_dim must be a positive integer and must be smaller or equal to sys_dim but got {args['disturbance_dim']}")
        if isinstance(args['disturbance_dim'], str) and args['disturbance_dim'] != 'full':
            raise ValueError(f"disturbance_dim must be 'full' but got {args['disturbance_dim']}")
    if 'disturbance_params' in args and args['disturbance_params'] is not None:
        if not isinstance(args['disturbance_params'], list):
            raise TypeError(f"disturbance_params must be a list type but got {type(args['disturbance_params'])}")
        if len(args['disturbance_params']) > args['sys_dim']:
            raise ValueError(f"disturbance_params must be a list of length smaller or equal to {args['sys_dim']} but got length {len(args['disturbance_params'])}")
        for param in args['disturbance_params']:
            if not isinstance(param, (int, float)):
                raise TypeError(f"disturbance_params must contain numbers but got {type(param)}")
    if 'disturbance_type' in args:
        if not isinstance(args['disturbance_type'], str):
            raise TypeError(f"disturbance_type must be a string but got {type(args['disturbance_type'])}")
        if args['disturbance_type'] not in ['normal', 'uniform', 'exponential']:
            raise ValueError(f"disturbance_type must be 'normal', 'uniform', or 'exponential' but got {args['disturbance_type']}")

    if 'disturbance_scale' in args:
        if args['disturbance_type'] == 'exponential':
            if not isinstance(args['disturbance_scale'], (int, float)):
                raise TypeError(f"disturbance_scale must be a number for exponential disturbance but got {type(args['disturbance_scale'])}")
        elif args['disturbance_type'] in ['normal', 'uniform']:
            if isinstance(args['disturbance_scale'], (tuple,list)):
                if len(args['disturbance_scale']) != 2:
                    raise ValueError(f"disturbance_scale must be a single number or a tuple of length 2 for min_val and max_val but got length {len(args['disturbance_scale'])}")
            for scale in args['disturbance_scale']:
                if not isinstance(scale, (int, float)):
                    raise TypeError(f"disturbance_scale must contain numbers but got {type(scale)}")
    
class LinearSystem(BaseSystem):
    def __init__(self,
                 sys_dim : int,
                 input_dim : int,
                 input_space : dict[str,int],
                 sys_name : str = "LinearSystem",
                 sys_type : Optional[ Literal['continuous', 'discrete'] ] = 'continuous',
                 disturbance_dim : Optional[Literal['int','full']] = 'full',
                 disturbance_type : Optional[ Literal['normal', 'uniform', 'exponential'] ] = 'normal',
                 disturbance_scale : Optional[Union[Tuple[Union[float,int]],Union[float, int]]] = [0, 1],
                 disturbance_params : Optional[List[Union[float, int]]] = None
                 ) -> None:
        super().__init__(sys_dim = sys_dim,
                         input_dim = input_dim,
                         sys_name = sys_name)
        args = locals()

        assert_inputs(**args)
        self.input_space = input_space
        self.sys_type = sys_type
        self.disturbance_dim = disturbance_dim
        self.disturbance_type = disturbance_type
        self.x = np.zeros(self.sys_dim)
        self.x_o = self.x.copy()
        self._configure_input_space(self.input_space)
        self.disturbance_params = disturbance_params
        self.disturbance_scale = disturbance_scale
        self._get_disturbance()

    def _configure_input_space(self,
                                input_space : dict
                                )-> None:
        self.u = []
        for _, value in input_space.items():
            for k,v in value.items():
                if k == 'continuous':
                    self.u.append(InputSpaceContinuous(min_value = v[0], max_value = v[1]))
                elif k == 'random':
                    if len(v) == 3 and isinstance(v[0], str) and isinstance(v[1], (int, float)) and isinstance(v[2], (int, float)):
                        self.u.append(InputSpaceRandom(sampling = v[0], min_value = v[0], max_value = v[1]))
                    elif len(v) == 2:
                        if isinstance(v[0], str) or isinstance(v[1], str):
                            raise ValueError(f"input_space['random'] if it has 2 values, then first value must be min and second value must be max but got {v}")
                        else:
                            self.u.append(InputSpaceRandom(min_value = v[0], max_value = v[1]))
                    else:
                        raise ValueError(f"input_space['random'] must have a sampling type as the first element and min, max values as the second and third elements but got {v}")
                elif k == 'discrete':
                    if len(v) == 3 and isinstance(v[0], (int, float)) and isinstance(v[1], (int, float)) and isinstance(v[2], (int, float)):
                        self.u.append(InputSpaceDiscrete(min_value = v[0], max_value = v[1], step = v[2]))
                    elif len(v) == 2 and isinstance(v[0], (int, float)) and isinstance(v[1], (int, float)):
                        self.u.append(InputSpaceDiscrete(min_value=v[0], max_value=v[1]))
                    else:
                        raise ValueError(f"input_space['discrete'] must have min, max, and step values but got {v}")
        for _ in range(self.sys_dim - len(self.u)):
            self.u.append(0)
    def step(self, 
             u: np.array
             ) -> None:
        self._get_disturbance()
        self.x += u + self.phi
    
    def mpc_step(self,
                 u : np.array,
                phi : np.array
                ) -> np.array:
        return self.x + u + phi

    def _get_disturbance(self) -> None:
        self.disturbance_dim = self.sys_dim if self.disturbance_dim == 'full'\
                               else self.disturbance_dim
        if self.disturbance_params is None:
            comp_dim = self.sys_dim if self.disturbance_dim == self.sys_dim else self.disturbance_dim
            if self.disturbance_type == 'normal':
                self.phi = np.random.normal(self.disturbance_scale[0], self.disturbance_scale[1], comp_dim)
            elif self.disturbance_type == 'uniform': 
                self.phi = np.random.uniform(self.disturbance_scale[0],self.disturbance_scale[1], comp_dim)
            else:
                self._phi = np.random.exponential(self.disturbance_scale, self.input_dim)
            inactive_dims = []
            for _ in range(self.sys_dim - self.disturbance_dim):
                inactive_dims.append(0)
            self.phi = np.array(self.phi.tolist() + inactive_dims)
        else:
            for _ in range(self.sys_dim - len(self.disturbance_params)):
                self.disturbance_params.append(0)
            self.phi = np.array(self.disturbance_params)    
