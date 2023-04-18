class TkinterOpener:
    def __init__(self) -> None:
        self.function = None
        self.args = None
        self.timer = 0

    def update(self) -> None:
        # handle tkinter window opening events that need to wait for some time before openign
        if self.timer == 20:
            self._execute_func()

            # reset
            self.function = None
            self.args = None
            self.timer = 0  

        if not self.function is None:
            self.timer += 1

    def queue_function(self, function, args=None) -> None:
        """Add the tkinter opening function to the queue to open, if no other function is already queued"""
        if self.function is None:
            self.function = function
            self.args = args

    def _execute_func(self):
        if not self.args: # no args
            self.function()
            return
        
        if not isinstance(self.args, tuple): #if not tuple = no args
            self.function(self.args) # only one arg
            return
        
        # multiple args
        self.function(*self.args)
            

        


tkinter_opener_instance = TkinterOpener()