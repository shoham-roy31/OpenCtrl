import inspect
from OpenCtrl.SystemDynamicExample.base_sys import BaseSystem
from typing import Literal, Optional, Dict, Callable, Union

def assert_inputs(**args) -> None:
    if 'system' in args:
        if not isinstance(args['system'], BaseSystem):
            raise TypeError(f"system must be an instance of BaseSystem but got {type(args['system'])}")
    if 'horizon' in args:
        if not isinstance(args['horizon'], int):
            raise TypeError(f"horizon must be an integer but got {type(args['horizon'])}")
        if args['horizon'] <= 0:
            raise ValueError(f"horizon must be a positive integer but got {args['horizon']}")
    if 'cost_function' in args:
        if not isinstance(args['cost_function'], str):
            raise TypeError(f"cost_function must be a string but got {type(args['cost_function'])}")
        if args['cost_function'] not in ['quadratic', 'linear']:
            raise ValueError(f"cost_function must be 'quadratic' or 'linear' but got {args['cost_function']}")
    if 'optimizer_type' in args:
        if not isinstance(args['optimizer_type'], str):
            raise TypeError(f"optimizer_type must be a string but got {type(args['optimizer_type'])}")
        if args['optimizer_type'] not in ['gradient', 'genetic', 'random']:
            raise ValueError(f"optimizer_type must be 'gradient', 'genetic', or 'random' but got {args['optimizer_type']}")
        if args['optimizer_type'] == 'gradient':
            if 'alpha' in args:
                if not isinstance(args['alpha'], (int, float)):
                    raise TypeError(f"alpha must be a number but got {type(args['alpha'])}")
                if args['alpha'] <= 0:
                    raise ValueError(f"alpha must be a positive number but got {args['alpha']}")
        elif args['optimizer_type'] == 'genetic':
            if 'population_size' in args:
                if not isinstance(args['population_size'], int):
                    raise TypeError(f"population_size must be an integer but got {type(args['population_size'])}")
                if args['population_size'] <= 0:
                    raise ValueError(f"population_size must be a positive integer but got {args['population_size']}")
            if 'cross_over_rate' in args:
                if not isinstance(args['cross_over_rate'], (int, float)):
                    raise TypeError(f"cross_over_rate must be a number but got {type(args['cross_over_rate'])}")
                if not (0 <= args['cross_over_rate'] <= 1):
                    raise ValueError(f"cross_over_rate must be between 0 and 1 but got {args['cross_over_rate']}")
                if 'mutation_rate' in args:
                    if not isinstance(args['mutation_rate'], (int, float)):
                        raise TypeError(f"mutation_rate must be a number but got {type(args['mutation_rate'])}")
                    if not (0 <= args['mutation_rate'] <= 1):
                        raise ValueError(f"mutation_rate must be between 0 and 1 but got {args['mutation_rate']}")
                    if 'cut_off_rate' in args:
                        if not isinstance(args['cut_off_rate'], (int, float)):
                            raise TypeError(f"cut_off_rate must be a number but got {type(args['cut_off_rate'])}")
                        if not (0 <= args['cut_off_rate'] <= 1):
                            raise ValueError(f"cut_off_rate must be between 0 and 1 but got {args['cut_off_rate']}")
    if 'max_iterations' in args:
        if not isinstance(args['max_iterations'], int):
            raise TypeError(f"max_iterations must be an integer but got {type(args['max_iterations'])}")
        if args['max_iterations'] <= 0:
            raise ValueError(f"max_iterations must be a positive integer but got {args['max_iterations']}")
    if 'tolerance_step' in args:
        if not isinstance(args['tolerance_step'], int):
            raise TypeError(f"tolerance_step must be an interger but got {type(args['tolerance_step'])}")
        if not args['tolerance_step'] >= 0 and args['tolerance_step'] > args['max_iterations']:
            raise TypeError(f"tolerance_step should be within [0,max_iterations] but found {args['tolerance_step']}")
    if 'threshold' in args:
        if not isinstance(args['threshold'], float):
            raise TypeError(f"threshold must be an float but got {type(args['threshold'])}")
        if args['threshold'] < 0 or args['threshold'] > 1:
            raise ValueError(f"threshold must be within range [0,1] but got {args['threshold']}") 
    if 'tolerance' in args:
        if not isinstance(args['tolerance'], (int, float)):
            raise TypeError(f"tolerance must be a number but got {type(args['tolerance'])}")
        if args['tolerance'] <= 0:
            raise ValueError(f"tolerance must be a positive number but got {args['tolerance']}")
    if 'constraints' in args and args['constraints'] is not None:
        if not isinstance(args['constraints'], Dict):
            raise TypeError(f"constraints must be a dictionary or none but got {type(args['constraints'])}")
        for key, value in args['constraints'].items():
            if not isinstance(key, str):
                raise TypeError(f"constraint keys must be strings but got {type(key)}")
            if not isinstance(value, Callable):
                raise TypeError(f"constraint values must be an object but got {type(value)}")

class OptimizerSchema:
    def __init__(self,
                system: BaseSystem,
                horizon : int,
                cost_function : Literal['quadratic', 'linear'] = 'quadratic',
                optimizer_type : Literal['gradient', 'genetic', 'random'] = 'gradient',
                alpha : float = 0.01,
                population_size : int = 100,
                cross_over_rate : float = 0.7,
                mutation_rate : float = 0.1,
                cut_off_rate : float = 0.5,
                max_iterations : int = 1000,
                tolerance_step : int = 50,
                threshold : float = 0.005,
                tolerance : float = 1e-3,
                constraints : Optional[Dict[str, Callable]] = None
                ) -> None:
        args = locals()
        assert_inputs(**args)
        self.system = system
        self.horizon = horizon
        self.cost_function = cost_function
        self.optimizer_type = optimizer_type
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.constraints = constraints 
        self.tolerance_step = tolerance_step
        self.threshold = threshold
        if optimizer_type == 'gradient':
            self.alpha = alpha
        if optimizer_type == 'genetic':
            self.population_size = population_size
            self.cross_over_rate = cross_over_rate
            self.mutation_rate = mutation_rate
            self.cut_off_rate = cut_off_rate
        if constraints is not None:
            for k,v in constraints.items():
              sig = inspect.signature(v)
              if len(sig.parameters) != 1:
                raise ValueError(f"Constraint function {k} must take exactly one argument but got {len(sig.parameters)}")
              self.get_attr(sig.parameters)  

    def _get_attr(self, 
                  params : dict,
                  ) -> None:
        for param in params.values():
            if param.name not in self.system.locals() or param.name != 'u':
                raise ValueError(f"Constraint function parameter {param.name} is not a valid attribute of the system or u is not defined in the constraint function")        
    

    def optimize(self) -> None:
        raise NotImplementedError("The optimize method must be implemented in the subclass.")
    
    def quadratic_cost(self) -> float:
        raise NotImplementedError("The quadratic_cost method must be implemented in the subclass.")

    def linear_cost(self) -> float:
        raise NotImplementedError("The linear_cost method must be implemented in the subclass.")
    
    def random_search(self) -> None:
        raise NotImplementedError("The random_search method must be implemented in the subclass.")
    
    def gradient_descent(self) -> None:
        raise NotImplementedError("The gradient_descent method must be implemented in the subclass.")
    
    def genetic_algorithm(self) -> None:
        raise NotImplementedError("The genetic_algorithm method must be implemented in the subclass.")