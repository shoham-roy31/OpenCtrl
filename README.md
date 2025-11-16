# OpenCtrl
OpenCtrl is an open source library for Control System Dynamics and Optimal Control Alogrithms.
## Table of Contents
 - [About OpenCtrl](#about)
 - [Features](#features)
 - [Installation Guide](#installation-guide)
    - [With Package Manager](#with-package-manager)
    - [Setup With Docker](#setup-with-docker)
    - [Clone The Dev Repo](#clone-the-dev-repo)
 - [Quick Guide](#quick-guide)
    - [Create a Linear System](#create-a-linear-system)
    - [Create an Optimizer](#create-an-optimizer)
    - [Use Control Algorithm](#use-control-algorithm)
 - [Contribute](#contribute)
    - [Repo Setup](#repo-setup)
    - [Run Test](#run-test)
    - [Raise a PR](#raise-a-pr)
 - [Author](#author)


## About
OpenCtrl is a open source python library to develop and study control system and control algorithm. It comes with module to instantiate Linear Systems and emulate its dynamics. **SystemDynamics** templates enable users to extend it into different order of systems for custom needs. **Optim** module provides Vanilla Optimizer to compute optimal system input parameters using 3 optimizing engines as of now, Gradient Descent, Random Search and Genetic Algorithm. Users can use **optim** template to extend different optimization engines. Same with **controls** module which currently consitutes LAC to tune system input parameters, **controls** module can be extended as well.

## Features
The library facilitates:
 - System Objects
 - Control Algorithms
 - Multi-Horizon Optimization
 - Real-time visualization

## Installation Guide

### With Package Manager
Run pip command:<br>
`pip install OpenCtrl`

For specific version *X* use:<br>
`pip install OpenCtrl=X`

### Setup with Docker
Run <br>
`docker pull gabruroy/openctrl:latest`

For spefic version of DEV <br>
`docker pull gabruroy/openctrl:{version}`

### Clone The Dev Repo
Run <br>
`https://github.com/shoham-roy31/OpenCtrl.git`

Create a Virtual Env<br>
`python -m venv OpenCtrl`

Install The Dependencies<br>
`pip install -r requirements.txt`


## Quick Guide

Version Check:<br>
`python -c "import OpenCtrl;print(OpenCtrl.__version__)"`

### Introduction
- OpenCtrl currently contains Linear System Dynamics.
- Vanilla Optimizer with Random Search, Gradient Descent, and Genetic Algorithm Engines.
- LAC-DCL Optimal Control Algorithm to tune systems.
- Nominal Prediction Modules.

### Create a Linear System
This is the beta stage of OpenCtrl, currently provides implementation of *LinearSystem* with *Random*,*Discreet* and *continious* system input and disturbance type of 3 distributions *Normal*, *Uniform* and *Exponential*. <br>
Example : Load up system parameters you want for your Linear System.
```
import numpy as np
from OpenCtrl.SystemDynamicExample import LinearSystem
 ''' define your input space parameters '''
input_space = { '1' : {'discreet' : [0,512]},
                '2' : {'random' : ['unifrom',-128,127]},
                '3' : {'continious' : [-10,10]},
                '3' : {'continious' : [512,1024]},
              }
 ''' Instantiate Linear System Object '''
linear_sys = LinearSystem(sys_dim = 4,
                          input_dim = 4,
                          input_space = input_space,
                          disturbance_type = 'uniform',
                          disturbance_scale = [-255, 255],
                          disturbance_params = full
                          )
''' Info : sys_dim equals input_dim since we considered we can control 4 degrees of freedom, if the case is different like we have 1 degree of freedom then input_space can only have { '1' : {'discreet' : [0,512] } } only. For disturbance_params some degree of freedom can have no impact by disturbance if only 1 degree is impacted the disturbance_params will be 1. '''
u = np.array( [np.random.random(0,512).item(), 
              np.random.uniform(-128,127).item(), 
              np.random.uniform(-10,10).item(), 
              np.random.unifrom(512,1024).item()]
            )
print(linear_sys.step(u))
```
### Create an Optimizer
Currently it is equiped with Vanilla Optimizer Module, with zoo of optimizer engines like *Random Search*, *Gradient Descent* and *Genetic Alogrithm* will facilitate to dervie optimal system input params based on system dynamics with *Multi Horizon* cost estimation.
Example : Let's load up an optimizer for the linear_sys.

```
from OpenCtrl.optim import VanillaOptim
''' Let's create 3 different types of Optimizers '''
cost_func = 'quadratic'
horizon = 5
max_iteration = 50
tolerance_step = 10

def get_predictions(horizon):
    return [u for _ in range(horizon)]

def print_metrics(type,cost,u):
    print(f"For optimizer type {type} \nCost: {cost}\nOptimal Input : {u}")

''' Random Search '''
optimizer_random = VanillaOptim( system = linear_sys,
                                 horizon = horizon,
                                 cost_function = cost_func,
                                 optimizer_type = 'random'
                                 max_iterations = max_iteration,
                                 tolerance_step = tolerance_step
                                )
cost_random, u_random = optimizer_random.optimizer( preds = get_predictions(horizon),
                                                    verbose = True
                                                  )
print_metrics('random',cost_random,u_random)        
''' Gradient Descent '''
optimizer_gradient = VanillaOptim( system = linear_sys,
                                   horizon = 5,
                                   cost_function = 'quadratic',
                                   optimizer_type = 'gradient',
                                   alpha = 1e-3,
                                   max_iterations = max_iteration,
                                   tolerance_step = tolerance_step
                                )
cost_gradient,u_gradient = optimizer_gradient.optimize( preds = get_predictions  (horizon),
verbose = True )
print_metrics('gradient',cost_gradient,u_gradient)
''' Genetic Algorithm '''
optimizer_genetic = VanillaOptim( system = linear_sys,
                                  horiozn = horizon,
                                  cost_function = cost_func,
                                  optimizer_type = 'genetic',
                                  population_size = 1000,
                                  cross_over_rate = 0.42,
                                  mutation_rate = 0.23,
                                  cut_off_rate = 0.5,
                                  max_iterations = max_iteration,
                                  tolerance_step = tolerance_step
                                  )
cost_genetic,u_genetic = optimizer_genetic.optimizer( pred = get_predictios( horizon),
verbose = True )
print_metrics('genetic',cost_genetic,u_genetic)
```
### Use Control Algorithm
The only control algorithm OpenCtrl has right now is *Learning Augmented Control (LAC)* with *Delayed Confidence Learning (DCL)*. **LAC** tunes the system parameters in a competitive ratio of MPC based on data driven Machine Learning and feedback control or nominal standard of tuning. This control algorithm ensures the system sustains near-optimal performance when there are adverserial predictions from Machine Learning models, then the competitive ratio shift towards conventional predictions or feedback inputs, otherwise if the data driven predictions have promising predctions the confidence shift towards it. **LAC** can be relied when the demand is for robust and safe performance. [REFERENCE](https://arxiv.org/pdf/2507.14595)

Example : Loading up LAC in the linear_sys
```
from OpenCtrl.controls import LAC
control_horizon = 10
lac = LAC(system = linear_sys,
          optimizer = optimizer_genetic,
          horizon = horizon,
          nominal_disturbance = 'mean_baseline'
          )
''' nominal_disturbance is a conventional method of predicting disturbance '''
for _ in range(control_horizon):
    cost,u = lac.tune(preds = get_predictions(horzion),
                      verbose = True
                     )
    print_metrics('genetic',cost, u )
```
## Contribute
### Repo Setup
1. Fork the project.

2. Create a new branch.
`git checkout -b feature/new-feature`

### Increment The Version
Increment the package version in __init__.py -> __version__
See the version convention FYI : [Versioning](https://semver.org/spec/v2.0.0.html)
### Run Test
### 1. Unit Test
#### With Shellscript
Run<br>
`./entrypoint.sh test`
#### With Batscript
Run<br>
`.\entrypoint.bat test`

### 2. Integration Test
Run on the parent dir<br>
`pytest`

### Raise A PR
3.Commit your changes.<br>
`git commit -m 'Add some feature'`

4. Push to the branch.<br>
`git push origin feature/new-feature`

5. Open a pull request.

## Author
[LinkedIN](https://www.linkedin.com/in/shoham-roy-b491a2205/)