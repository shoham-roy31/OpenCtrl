import numpy as np
from .vanilla_optim import VanillaOptim
from .optimizer_schema import OptimizerSchema
from SystemDynamicExample.linear_sys import LinearSystem

def test_optimizer_schema():
    try:
        system = LinearSystem(sys_dim = 3 , 
                             input_dim = 1,
                             input_space = {'1':{'continuous': [1.0, 0.0]}},
                             sys_name = "TestSystem",
                             disturbance_dim = 'full',
                             disturbance_type = 'normal',
                             disturbance_scale = [0, 1],
                             disturbance_params = None)
        optimizer = OptimizerSchema(system = system,
                                    horizon = 10,
                                    cost_function = 'quadratic',
                                    optimizer_type = 'gradient',
                                    alpha = 0.01,
                                    max_iterations = 1000,
                                    tolerance = 1e-3,
                                    constraints = None)
        print(" 1. ✅ OptimizerSchema test passed")
    except Exception as e:
        print(f"1. ❌ OptimizerSchema test failed: {e}")
    try:
        optimizer = OptimizerSchema(system = system,
                                    horizon = 10,
                                    cost_function = 'linear',
                                    optimizer_type = 'gradient',
                                    population_size = 50,
                                    cross_over_rate = 0.4,
                                    max_iterations = 50,
                                    tolerance = 1e-4,
                                    constraints= None)
        print("2. ✅ OptimizerSchema genetic optimizer test passed")
    except Exception as e:
        print(f"2. ❌ OptimizerSchema genetic optimizer test failed: {e}")

def test_vanilla_optim():
    try:
        system = LinearSystem(sys_dim = 3,
                              input_dim = 2,
                              input_space = {'1':{'continuous': [-255, 255]}, '2':{ 'continuous':[-255,255]}},
                              sys_name = "TestSystem",
                              disturbance_dim = 'full',
                              disturbance_type = 'normal',
                              disturbance_scale = [0, 65],
                              disturbance_params = None)
        optimizer = VanillaOptim(system = system,
                                 horizon = 8,
                                 cost_function = 'quadratic',
                                 optimizer_type = 'gradient',
                                 alpha = 0.1,
                                 population_size= 1000,
                                 max_iterations = 1000,
                                 tolerance = 2.1,
                                 tolerance_step = 50,
                                 constraints = None)
        print("3. ✅ VanillaOptim test passed")
    except Exception as e:
        print(f"3. ❌ VanillaOptim test failed: {e}")
    # try:
    #     C,U = optimizer.optimize(preds = [np.array([1.0, 2.0, 3.0]),
    #                                 np.array([0.5, 1.5, 2.5])],
    #                                 verbose = True)
    #     print("4. ✅ VanillaOptim optimize method test passed")
    #     print(f"Costs: {C}, Controls: {U}")
    # except Exception as e:
    #     print(f"4. ❌ VanillaOptim optimize method test failed: {e}")
    C,U = optimizer.optimize(preds = [np.array([1.0, 2.0, 3.0]),
                                    np.array([0.5, 1.5, 2.5]),
                                    np.array([ 42., -50., -50.]), 
                                    np.array([189., -50., -50.]),
                                    np.array([11.45334649, -9.08307999, -8.36986692]), 
                                    np.array([-4.69135071, -2.52461901, -3.28346826]),
                                    np.array([ 42., -50., -50.]), 
                                    np.array([189., -50., -50.])
                                    ],
                                    verbose = True)
    print("4. ✅ VanillaOptim optimize method test passed")
    print(f"Costs: {C}, Controls: {U}")
  
  

if __name__ == "__main__":
    test_optimizer_schema()
    test_vanilla_optim()