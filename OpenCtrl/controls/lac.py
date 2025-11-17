import numpy as np
from .control_schema import ControlSchema
from OpenCtrl.verbose_cli.cli import make_table
from OpenCtrl.optim.optimizer_schema import OptimizerSchema
from OpenCtrl.SystemDynamicExample.base_sys import BaseSystem
from typing import List, Tuple,Optional,Literal

def assert_params(**args):
    def _listoflist_(key: str,
                     ) -> None:
        if not isinstance(args[key], list):
            raise TypeError(f"{key} must be a type of list, found {type(args[key])}")
        if not all(isinstance(element, np.ndarray) for element in args[key]):
            raise TypeError(f"Elements in {key} should be of type np.ndarray")
        
    if 'preds' in args:
        _listoflist_('preds')
    if 'manual_nominals' in args and args['manual_nominals'] is not None:
        _listoflist_('manual_nominals')
    if 'manual_window' in args and args['manual_window'] is not None:
        _listoflist_('manual_window')
        if not len(args['manual_window']) == args['window_size']:
            raise ValueError(f"length of manual_window: {len(args['manual_window'])} is not equal to window_size: {args['window_size']}")
    if 'window_auto' in args:
        if not isinstance(args['window_auto'],bool):
            raise TypeError(f"window_auto should be of type bool but got {type(args['window_auto'])}")
    if 'window_init' in args:
        if not isinstance(args['window_init'],(float,int)):
            raise TypeError(f'window_init should be of type int or float but got {type(args['window_init'])}')
    if 'window_size' in args:
        if not isinstance(args['window_size'],int):
            raise TypeError(f"window_size should of type int but got {type(args['window_size'])}")
        if args['window_size'] <= 0:
            raise ValueError(f"window_size should be within rage [1,inf] but got {args['window_size']}")
    if 'warmup_steps' in args:
        if not isinstance(args['warmup_steps'],int):
            raise TypeError(f"warmup_size should be of type int but got {type(args['warmup_steps'])}")
        if not args['warmup_steps'] > 0:
            raise ValueError(f"warmup_steps should be in range [1,inf] but got {args['warmup_steps']}")
    if 'rho' in args:
        if not isinstance(args['rho'],(float,int)):
            raise TypeError(f"rho should be of type float or int but got {type(args['rho'])}")
    if 'beta' in args:
        if not isinstance(args['beta'],float):
            raise TypeError(f"beta should be type float but got type {type(args['beta'])}")
        if not args['beta'] > 0 and args['beta'] < 1:
            raise ValueError(f"beta should be in rage (0,1) but got {args['beta']}")
class LAC(ControlSchema):
    def __init__(self,
                 system: BaseSystem,
                 optimizer: OptimizerSchema,
                 horizon: int = 1,
                 nominal_disturbance: Optional[Literal['baseline',
                                                        'ema',
                                                        'mean_baseline']] = 'baseline',
                 warmup_steps : Optional[int] = 3,
                 rho : Optional[float] = 0.93,
                 beta : Optional[float] = 1e-3
                ) -> None:
        super().__init__(system = system,
                         optimizer = optimizer,
                         horizon = horizon,
                         nominal_disturbance = nominal_disturbance
                         )
        self.system = system
        self.optim = optimizer
        self.horizon = horizon
        self.nominal_disturbance = nominal_disturbance
        self.psi = np.random.uniform(low = 0, high = 1)
        self.error_queue = []
        self.counter = 0
        self.warmup_steps = warmup_steps
        self.rho = rho
        self.beta = beta
        self.window = None
    def tune(self,
             preds: List[np.ndarray],
             manual_nominals : Optional[List[np.ndarray]] = None,
             window_auto : Optional[bool] = True,
             window_init : Optional[float] = 0.0,
             window_size : Optional[int] = 3,
             manual_window : Optional[List[np.ndarray]] = None,
             alpha_ema : Optional[float] = 0.01,
             verbose : Optional[bool] = False
             ) -> Tuple[np.ndarray]:
        assert_params(**locals())
        if not len(preds) == self.horizon:
            raise ValueError(f"horizon: {self.horizon} is not equal with preds : {len(preds)}")
        if all(np.shape(_)[0] != self.system.disturbance_dim  for _ in preds):
            raise ValueError("mismatching in dimension with provided entries in pred with disturbance_dim")
        if manual_nominals:
            if not len(manual_nominals) == self.horizon:
                raise ValueError(f"length mismatch with horizon: {self.horizon} and manual_nominals: {len(manual_nominals)}")
            if not all(len(_) == self.system.sys_dim for _ in manual_nominals):
                raise ValueError(f"dimension of elements in manual_nominals are incorrect should system disturbance_dim : {self.system.sys_dim}")
        blended = []
        if not self.window:
            self.window = [np.array([window_init for _ in range(self.system.sys_dim)]) for _ in range(window_size)] \
                 if window_auto else manual_window
        self.prev_ema = np.zeros(self.system.sys_dim)
        self.prev_real = np.zeros(self.system.sys_dim)
        self.nominal = self._wrapper_disturbance(self.horizon,
                                            self.system.disturbance_dim,
                                            self.window,
                                            self.prev_ema,
                                            self.prev_real,
                                            alpha_ema) if not manual_nominals \
                                            else manual_nominals
        self.counter += 1
        if self.counter >= self.warmup_steps:
            self.dcl()
            self.error_queue.pop()
            self.counter = 0
        
        for _ in range(self.horizon):
            blended.append(self.psi*preds[_] + (1 - self.psi)*self.nominal[_])
        cost,u = self.optim.optimize(blended,
                                 verbose)
        self.system.step(u[0])
        self.error_queue.append([[self.system.phi - preds[0]],
                                [self.system.phi - self.nominal[0]]])
        self.prev_ema = self.nominal[-1]
        self.prev_real = self.system.phi
        self.window.pop(0)
        self.window.append(self.system.phi)
        if verbose:
            display_stack = [[np.round(inp,3),np.round(c,3),np.round(b,3),np.round(n,3),np.round(self.psi,4)] for inp, c, 
                             b,n in zip(u,cost,blended, self.nominal)]
            display_header = ['U','COST','BLENDED','NOMINAL','PSI'] 
            temp = make_table(display_header,display_stack)
            display_stack = [[self.system.x,self.system.phi,temp]]
            display_header = ['X', 'Phi', 'DETAILS'] 
            print(make_table(display_header,display_stack)+'\n')
        return cost,u
    
    def dcl(self) -> None:
        def delta(eML : np.array,
                  eNo : np.array
                 ) -> np.array:
            return eML - eNo
        
        def V(eMl:np.array,
              eNo:np.array
              ) -> np.array:
            T = np.arange(start= 0,
                          stop= self.counter) * np.ones_like(eMl)
            return self.rho * T * (self.psi * delta(eMl,eNo) + eNo)
        eMl = np.array([e for e_ in self.error_queue for e in e_[0]])
        eNo = np.array([e for e_ in self.error_queue for e in e_[1]])
        eMl = np.sum(eMl, axis = 0)
        eNo = np.sum(eNo, axis = 0)
        v = V(eMl,eNo)
        self.psi -= (2 * np.dot(delta(eMl,eNo).T ,v)) / \
                    (np.linalg.norm(v,ord = 2) + 0.03)

        self.psi = np.clip(self.psi, 0 , 1)
