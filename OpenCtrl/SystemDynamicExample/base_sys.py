def assert_inputs(args):
    if args['sys_dim']:
        if not isinstance(args['sys_dim'], int):
            raise TypeError(f"sys_dim must be an integer but got f{type(args['sys_dim'])}")
        if args['sys_dim'] <= 0:
            raise ValueError(f"sys_dim must be a positive integer but got {args['sys_dim']}")
    if args['input_dim']:
        if not isinstance(args['input_dim'], int):
            raise TypeError(f"input_dim must be an integer but got f{type(args['input_dim'])}")
        if args['input_dim'] <= 0:
            raise ValueError(f"input_dim must be a positive integer but got {args['input_dim']}")
    if args['sys_name']:
        if not isinstance(args['sys_name'], str):
            raise TypeError(f"sys_name must be a string but got f{type(args['sys_name'])}")

class BaseSystem:
    def __init__(self,
                 sys_dim : int,
                 input_dim : int,
                 sys_name : str,
                 ) -> None:
        input_args = locals()
        assert_inputs(input_args)
        self.sys_dim = sys_dim
        self.input_dim = input_dim
        self.sys_name = sys_name

    def step(self) -> None:
        raise NotImplementedError("The step method must be implemented in the subclass.")