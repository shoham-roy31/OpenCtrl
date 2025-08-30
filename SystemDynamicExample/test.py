import numpy as np
from .base_sys import BaseSystem
from .linear_sys import LinearSystem
from .schemas import InputSpaceRandom, InputSpaceContinuous, InputSpaceDiscrete


def test_base_system_initialization():
    # Test with valid inputs
    try:
        sys = BaseSystem(sys_dim=3, input_dim=2, sys_name="TestSystem")
        assert sys.sys_dim == 3
        assert sys.input_dim == 2
        assert sys.sys_name == "TestSystem"
        print("✅ Test passed: Valid inputs")
    except Exception as e:
        print(f"❌ Test failed with valid inputs: {e}")

    # Test with invalid sys_dim type
    try:
        BaseSystem(sys_dim="three", input_dim=2, sys_name="TestSystem")
        print(f"❌ Test failed with invalid sys_dim type")
    except TypeError as e:
        print(f"✅ Test passed: {e}")

    # Test with invalid input_dim type
    try:
        BaseSystem(sys_dim=3, input_dim="two", sys_name="TestSystem")
        print(f"❌ Test failed with invalid input_dim type")
    except TypeError as e:
        print(f"✅ Test passed: {e}")

    # Test with negative sys_dim
    try:
        BaseSystem(sys_dim=-1, input_dim=2, sys_name="TestSystem")
        print(f"❌ Test failed with negative sys_dim")
    except ValueError as e:
        print(f"✅ Test passed: {e}")

    # Test with negative input_dim
    try:
        BaseSystem(sys_dim=3, input_dim=-2, sys_name="TestSystem")
        print(f"❌ Test failed with negative input_dim")
    except ValueError as e:
        print(f"✅ Test passed: {e}")

def test_linear_system_initialization():
    # Test with valid inputs
    linear_sys = LinearSystem(sys_dim=3, input_dim=1, 
                                  input_space={ '1' : {'continuous': [1.0, 0.0]}},
                                    sys_name="LinearSys")
    # try:
    #     linear_sys = LinearSystem(sys_dim=3, input_dim=1, 
    #                               input_space={ '1' : {'continuous': [1.0, 0.0]}},
    #                                 sys_name="LinearSys")
    #     assert linear_sys.sys_dim == 3, \
    #     f"❌ Test failed with valid inputs for LinearSystem: linear_sys_dim = {linear_sys.sys_dim} != 3"
    #     assert linear_sys.input_dim == 1,\
    #     f"❌ Test failed with valid inputs for LinearSystem: linear_sys.input_dim = {linear_sys.input_dim} != 1"
    #     assert linear_sys.sys_name == "LinearSys",\
    #     f"❌ Test failed with valid inputs for LinearSystem: linear_sys.sys_name = {linear_sys.sys_name} != 'LinearSys'"
    #     print("✅ Test passed: Valid inputs for LinearSystem")
    # except Exception as e:
    #     print(f"❌ Test failed with valid inputs for LinearSystem: {e}")

    # Test with invalid disturbance_type
    try:
        LinearSystem(sys_dim=3, input_dim=1, 
                     input_space={'1':{'continuous': [1.0, 0.0]}}, 
                     sys_name="LinearSys", 
                     disturbance_type='invalid')
        print(f"❌ Test failed with invalid disturbance_type")
    except ValueError as e:
        print(f"✅ Test passed: {e}")
    
    # Test with input_space configuraiton
    try:
        system = LinearSystem(sys_dim = 3, input_dim = 1,
                      input_space = {'1':{'continuous': [1.0, 0.0]}},
                        sys_name = "LinearSys",
                          disturbance_type = 'normal', 
                          disturbance_scale = [0, 1],
                          disturbance_params = [1])
        assert type(system.u[0]) == InputSpaceContinuous,\
         f"❌ Test failed with valid inputs for LinearSystem: type(system.u[0]) = {type(system.u[0])} != InputSpaceContinuous"
        assert system.u[1] == 0,\
         f"❌ Test failed with valid inputs for LinearSystem: system.u[1] = {system.u[1]} != 0"
        assert system.u[-1] == 0,\
        f"❌ Test failed with valid inputs for LinearSystem: system.u[2] = {system.u[-1]} != 0"
        print(f"✅ Test passed: InputSpaceContinuous initialized correctly")
    except Exception as e:
        print(f'Here : {e}')
    
    # Test with step function
    try:
        print(f"phi : {system.phi}")
        system.step(np.array([0.5, 0 , 0]))
        print(f"system.phi : {system.phi}")
        assert np.all(system.x == np.array([1.5, 0, 0])),\
         f"❌ Test failed with step function: system.x = {system.x} != [0.5, 0, 0]"
        print("✅ Test passed: Step function works correctly")
    except Exception as e:
        print(f'here: {e}')
    

if __name__ == "__main__":
    test_base_system_initialization()
    test_linear_system_initialization()