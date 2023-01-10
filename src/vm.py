import dis
from opcodes import *
import types

functions = {
    "print": print
}

class CallFrame:
    def __init__(self, call_start, stack, code):
        #dis.disassemble(code)
        self.call_start = call_start
        self.stack = stack[self.call_start:]
        self.code = code
        self.instructions = dis.get_instructions(self.code)
        self.locals = functions
        self.retval = None
        #print(f"Initializing call frame: {self.stack}")


class VirtualMachine:
    def __init__(self, code):
        self.code = code
        self.globals = functions
        self.current_frame_index = 0
        self.frames = [CallFrame(self.current_frame_index, [], self.code)]
        self.current_frame = self.frames[self.current_frame_index]
        self.retval = None

    def run_ins(self, ins):
        op = ins.opcode

        if op == LOAD_CONST:
            self.current_frame.stack.append(ins.argval)
            # print(f"loading const {self.current_frame.stack}")
        elif op == MAKE_FUNCTION:
            name = self.current_frame.stack.pop()
            func = self.current_frame.stack.pop()
            self.current_frame.stack.append(func)
            # print(f"made a function! {self.current_frame.stack}")
        elif op == STORE_NAME:
            self.current_frame.locals[ins.argval] = self.current_frame.stack.pop()
            # print(f"stored name! {self.current_frame.stack, self.current_frame.locals}")
        elif op == POP_TOP:
            self.current_frame.stack.pop()
            # print(f"popping top! {self.current_frame.stack}")
        elif op == LOAD_NAME:
            self.current_frame.stack.append(self.current_frame.locals[ins.argval])
            # print(f"loaded name! {self.current_frame.stack, self.current_frame.locals}")
        elif op == LOAD_GLOBAL:
            #print(f"loading global: {self.globals[ins.argval]}")
            self.current_frame.stack.append(self.globals[ins.argval])
            # print(f"loaded global! {self.current_frame.stack}")
        elif op == LOAD_FAST:
            self.current_frame.locals[ins.argval] = self.current_frame.stack[ins.arg+1]
        elif op == BUILD_TUPLE:
            vals = tuple((self.current_frame.stack.pop() for x in range(ins.arg)))
            self.current_frame.stack.append(vals)
            
        elif op == CALL_FUNCTION:
            args = []
            for i in range(ins.arg):
                args.append(self.current_frame.stack.pop())
            function = self.current_frame.stack[-1]
            self.call_function(function, args)
            self.current_frame.stack.pop()
            self.current_frame.stack.append(self.retval)
            #print(f"stack after call = {self.current_frame.stack}")
        elif op == RETURN_VALUE:
            val = self.frames.pop().stack[-1]
            self.retval = val
            self.current_frame_index -= 1
            if self.current_frame_index < 0:
                self.current_frame.stack.pop()
                #print(f"final return! bye! {self.current_frame.stack}")
                exit()
            self.current_frame = self.frames[self.current_frame_index]
           # self.current_frame.stack.append(val)
    
    def call_function(self, function, args):
        if type(function) == types.CodeType:
            self.current_frame_index += 1
            self.frames.append(CallFrame(self.current_frame.stack.index(function), self.current_frame.stack + args, function))
            self.current_frame = self.frames[self.current_frame_index]
            self.run()
        else:
            function(*args)
        
    def run(self):
        for ins in self.current_frame.instructions:
            self.run_ins(ins)
        

