import inspect
import numpy as np
import matplotlib.pyplot as plt
from .optimizer_schema import OptimizerSchema
from SystemDynamicExample.base_sys import BaseSystem
from SystemDynamicExample.schemas import InputSpace
from typing import Literal, Dict, Callable, Optional, List, Tuple, Union

def assert_params(**args):
    if 'preds' in args:
        if not len(args['preds']) > 0 and len(args['preds']) == args['horizon']:
            raise ValueError("Predictions must be a non-empty list with length equal to the horizon.")
        if not isinstance(args['preds'], list):
            raise TypeError(f"Predictions must be a list but got {type(args['preds'])}.")
        if not all(isinstance(x, np.ndarray) for x in args['preds']):
            raise TypeError(f"All elements in predictions must a ndarray.")
    if 'x' in args:
        if not isinstance(args['x'], np.ndarray):
            raise TypeError(f"x must be a numpy array but got {type(args['x'])}.")
    if 'phi' in args:
        if not isinstance(args['phi'], np.ndarray):
            raise TypeError(f"phi must be a numpy array but got {type(args['phi'])}.")
    if 'u' in args:
        if not isinstance(args['u'], np.ndarray):
            raise TypeError(f"u must be a numpy array but got {type(args['u'])}.")
    if 'verbose' in args:
        if not isinstance(args['verbose'], bool):
            raise TypeError(f"verbose must be a boolean but got {type(args['verbose'])}.")
        
class VanillaOptim(OptimizerSchema):
    def __init__(self,
                 system : BaseSystem,
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
        super().__init__(system = system, 
                         horizon = horizon, 
                         cost_function = cost_function, 
                         optimizer_type = optimizer_type, 
                         alpha = alpha, 
                         population_size = population_size,
                         cross_over_rate = cross_over_rate,
                         mutation_rate = mutation_rate,
                         cut_off_rate = cut_off_rate,
                         max_iterations = max_iterations, 
                         tolerance_step = tolerance_step,
                         threshold = threshold,
                         tolerance = tolerance, 
                         constraints = constraints)
        self.cost = self.quadratic_cost if self.cost_function == 'quadratic' else self.linear_cost
        self.optim = self.gradient_descent if self.optimizer_type == 'gradient' else (
            self.genetic_algorithm if self.optimizer_type == 'genetic' else self.random_search
        )
        self.input_space_mask = None
        self.bucket = 0

    def optimize(self,
                 preds : List[np.ndarray],
                 verbose : Optional[bool] = False
                ) -> Tuple[List[float], List[np.ndarray]]:
        args = locals()
        assert_params(**args)
        if verbose:
            self.cost_verbose = []
        if len(preds) != self.horizon:
            raise ValueError(f"Predictions must have length equal to the horizon ({self.horizon}) but got {len(preds)}.")
        x = self.system.x
        U = []
        C = []
        for horizon in range(self.horizon):
            x = self.project(x, preds[horizon])
            cost, u = self.optim(x, verbose, horizon)
            x = self.system.mpc_step(u,preds[horizon])
            U.append(u)
            C.append(cost)
        return C,U
    
    def project(self,
                x : np.ndarray,
                phi : np.ndarray
                ) -> np.ndarray:
        args = locals()
        assert_params(**args)
        return x + phi
    
    def quadratic_cost(self,
                       x : np.ndarray,
                       u : np.ndarray
                       ) -> float:
        args = locals()
        assert_params(**args)
        cost = np.linalg.norm((x + u) * self.input_space_mask, ord = 2)
        return cost.item()

    def linear_cost(self,
                    x : np.ndarray,
                    u : np.ndarray
                    ) -> float:
        args = locals()
        assert_params(**args)
        cost = np.linalg.norm(np.abs(x + u) * self.input_space_mask, ord = 1)
        return cost.item()

    def _validate_constraints(self, 
                              u : np.ndarray,
                              x : np.ndarray
                             ) -> np.ndarray:
        for constraint in self.constraints.values():
            sig = inspect.signature(constraint)
            if len(sig.parameters) == 2:
                params = []
                for param in sig.parameters.values():
                    if param.name == 'u':
                        params.append(u)
                    elif param.name == 'x':
                        params.append(x)
                satisfied = constraint(*params)
            elif len(sig.parameters) == 1:
                satisfied = constraint(u if 'u' in sig.parameters else x)
            u -= satisfied
        return u
        
    def _get_random_u(self) -> np.ndarray:
        u = np.array([0 if not isinstance(u, InputSpace) \
                            else (np.random.uniform(u.min_value, u.max_value)\
                                if not hasattr(u, 'step') \
                                else np.random.choice(list(range(u.min_value, u.max_value, u.step))))\
                                                                    for u in self.system.u])
        self.input_space_mask = np.where(u == 0, 0, 1 ).astype(float) if self.input_space_mask is None\
                                else self.input_space_mask
        return u
    
    def _clip_u(self, 
                U : np.ndarray
                ) -> np.ndarray:
        u_clipped = []
        for u, u_obj in zip(U,self.system.u):
            
            if isinstance(u_obj, InputSpace):
                u_clipped.append(np.clip(u,min=u_obj.min_value,max = u_obj.max_value))
            else:
                u_clipped.append(0)
        return np.array(u_clipped)
    def _show_cost_plot(self,
                        cost : float,
                        iter : int,
                        horizon : Optional[Union[int, None]] = None
                        ) -> None:
        self.cost_verbose.append(cost) 
        plt.plot(self.cost_verbose, label = 'Cost over iterations')
        plt.xlabel('Iteration')
        plt.ylabel('Cost')
        if horizon is not None:
            plt.title(f'Cost Minimization - Horizon : {horizon + 1}')
        else:
            plt.title('Cost Minimization')
        plt.draw()
        plt.pause(0.01)
        if iter - 1 != self.max_iterations:
            plt.clf()
    def _check_tolerance(self,
                         prev_cost : float,
                         curr_cost : float
                         ) -> bool:
        if self.tolerance_step == 0 or self.tolerance_step > self.max_iterations * 0.90:
            return False
        if (prev_cost - curr_cost) < self.threshold:
            self.bucket += 1
            return True if self.bucket >= self.tolerance_step else False
        else:
            self.bucket = 0
            return False

    def random_search(self,
                      x : np.ndarray,
                      verbose : Optional[bool] = False,
                      horizon : Optional[Union[int, None]] = None
                      ) -> Tuple[float, np.ndarray]:
        args = locals()
        assert_params(**args)
        cost_min = float('inf')
        best_u = None
        u = self._get_random_u()
        u = self._validate_constraints(u, x) if self.constraints else u
        prev_cost = cost_min
        for _ in range(self.max_iterations):
            cost = self.cost(x, u)
            if cost < self.tolerance:
                return cost, u
            cost_min = min(cost_min, cost)
            best_u = u if cost == cost_min else best_u
            u = self._get_random_u()
            u = self._validate_constraints(u, x) if self.constraints else u
            if verbose:
                self._show_cost_plot(cost, _, horizon)
            if self._check_tolerance(prev_cost,cost):
                break
            prev_cost = cost
        return cost_min, best_u
    
    def gradient_descent(self,
                         x : np.ndarray,
                         verbose : Optional[bool] = False,
                         horizon : Optional[Union[int, None]] = None
                         ) -> Tuple[float, np.ndarray]:
        def _compute_gradient(u : np.ndarray,
                              x : np.ndarray,
                             cost : float
                             ) -> Tuple[float,np.ndarray]:
            if self.cost_function == 'quadratic':
                return (2 * (x.T * np.ones_like(x)) + u ) * self.input_space_mask
            else:
                return cost * ((x + u)/(np.linalg.norm(x + u, ord = 1) + 0.001)) * self.input_space_mask
        args = locals()
        assert_params(**args)
        cost_min = float('inf')
        best_u = None
        u = self._get_random_u().astype(float)
        u = self._validate_constraints(u,x) if self.constraints else u
        prev_cost = cost_min
        for _ in range(self.max_iterations):
            cost = self.cost(x, u)
            if cost < self.tolerance:
                return cost, u
            cost_min = min(cost_min, cost)
            best_u = u if cost == cost_min else best_u
            grad = _compute_gradient(u,x,cost)
            u -= self.alpha * self.input_space_mask * grad
            u = self._clip_u(u)

            u = self._validate_constraints(u, x) * self.input_space_mask if self.constraints\
                else u
            if verbose:
                self._show_cost_plot(cost, _, horizon)
            # if self._check_tolerance(prev_cost,cost):
            #     break
            # prev_cost = cost
        return cost_min, best_u
    
    def genetic_algorithm(self,
                          x : np.ndarray,
                          verbose : Optional[bool] = False,
                          horizon : Optional[Union[int,None]] = None
                          ) -> Tuple[float, np.ndarray]:
        def _crossover(parent1 : np.ndarray,
                       parent2 : np.ndarray
                       ) -> np.ndarray:
            if np.random.rand() < self.cross_over_rate:
                crossover_point = np.random.randint(0, parent1.shape[0])
                child = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
                return child
            else: 
                return parent1 if np.random.rand() < 0.5 else parent2

        def _mutate(u : np.ndarray,
                    ) -> np.ndarray:
            if np.random.rand() < self.mutation_rate:
                return u + (np.random.normal(0, 1, size = u.shape) * self.input_space_mask)
            return u
        args = locals()
        assert_params(**args)
        population = [self._get_random_u() for _ in range(self.population_size)]
        population = [u + self._validate_constraints(u, x)  for u in population] if self.constraints else population
        cost_min = float('inf')
        best_u = None
        prev_cost = cost_min
        for _ in range(self.max_iterations):
            costs = [self.cost(x, u) for u in population]
            if min(costs) < self.tolerance:
                return min(costs), population[costs.index(min(costs))]
            cost_min = min(cost_min, min(costs))
            best_u = population[costs.index(min(costs))] if min(costs) == cost_min else best_u
            next_generation = []
            population = [u for _, u in sorted(zip(costs, population), key = lambda pair: pair[0])]
            population = population[: round(self.population_size * self.cut_off_rate)]
            if verbose:
                self._show_cost_plot(min(costs), _, horizon)
            while len(next_generation) <= self.population_size:
                parent1, parent2 = np.random.choice(list(range(0,len(population))), size = 2, replace= True)
                child = _crossover(population[parent1], population[parent2])
                child = _mutate(child)
                child = self._clip_u(child)
                child = self._validate_constraints(child, x) * self.input_space_mask if self.constraints \
                       else child 
                next_generation.append(child)
            population = next_generation
            if self._check_tolerance(prev_cost,min(costs)):
                break
            prev_cost = min(costs)
        return cost_min, best_u