import numpy as np
from SystemDynamicExample.linear_sys import LinearSystem
from optim.vanilla_optim import VanillaOptim
from .lac import LAC

def _test_lac_1() -> None:
    system = LinearSystem(sys_dim = 3, input_dim = 1,
                          input_space = {'1':{'continuous': [0.0, 1.0]}},
                          sys_name = "LinearSys",
                          disturbance_type = 'normal', 
                          disturbance_scale = [0, 1],
                          disturbance_params = None)
    optimizer = VanillaOptim(system = system,
                                    horizon = 5,
                                    cost_function = 'quadratic',
                                    optimizer_type = 'genetic',
                                    alpha = 0.01,
                                    max_iterations = 10,
                                    tolerance = 1e-3,
                                    constraints = None)
    lac = LAC(system = system,
              optimizer = optimizer,
              horizon = 5,
              nominal_disturbance= 'mean_baseline')
    
    for _ in range(10):
        cost,u = lac.tune(preds =[np.array([1.0, 0.0, 0.0]),
                                    np.array([1.0, 0.0, 0.0]),
                                    np.array([1.0, 0.0, 0.0]),
                                    np.array([1.0, 0.0, 0.0]),
                                    np.array([1.0, 0.0, 0.0])],
                          verbose= True)
        print("__________________".center(50))
        print(f"For {_} Cost: {cost} \n u: {u} \n")

if __name__ == "__main__":
    _test_lac_1()


# [np.array([1.0, 2.0, 3.0]),
#                                     np.array([0.5, 1.5, 2.5]),
#                                     np.array([ 42., -50., -50.]),
#                                     np.array([ 42., -50., -50.]),
#                                     np.array([ 42., -50., -50.])]