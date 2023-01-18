import dis
from opcodes import *
import types
import sys
import numpy as np
import gc
gc.disable()

functions = {
    "print": print,
    "range": range,
    "len": len,
    "exit": exit
}

cached_functions = {

}

class CallFrame:
    def __init__(self, call_start, stack, code):
        self.call_start = call_start
        self.stack = stack[self.call_start:]
        self.code = code
        self.instructions = dis.get_instructions(self.code)
        self.locals = functions
        self.retval = None
        self.ip = 0

class VirtualMachine:
    def __init__(self, code):
        self.code = code
        self.globals = functions
        self.current_frame_index = 0
        self.frames = [CallFrame(self.current_frame_index, [], self.code)]
        self.current_frame = self.frames[self.current_frame_index]
        self.retval = None
        dis.disassemble(self.code)

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
            print(self.current_frame.stack, self.current_frame.locals)
            self.current_frame.stack.append(self.current_frame.locals[ins.argval])
        elif op == BUILD_TUPLE:
            vals = tuple((self.current_frame.stack.pop() for x in range(ins.arg)))
            self.current_frame.stack.append(tuple(reversed(vals)))
            
        elif op == CALL_FUNCTION:
            args = []
            for i in range(ins.arg):
                args.append(self.current_frame.stack.pop())
            function = self.current_frame.stack[-1]
            self.call_function(function, args)
            self.current_frame.stack.pop()
            self.current_frame.stack.append(self.retval)
        elif op == RETURN_VALUE:
            val = self.frames.pop().stack[-1]
            self.retval = val
            self.current_frame_index -= 1
            if self.current_frame_index < 0:
                self.current_frame.stack.pop()
                exit()
            self.current_frame = self.frames[self.current_frame_index]
            self.current_frame.ip -= 1
           # self.current_frame.stack.append(val)
        elif op == IMPORT_NAME:
            self.current_frame.stack.append(__import__(ins.argval))
        elif op == LOAD_METHOD:
            module = self.current_frame.stack.pop()
            self.current_frame.stack.append(getattr(module, ins.argval))
        elif op == CALL_METHOD:
            args = []
            for i in range(ins.arg):
                args.append(self.current_frame.stack.pop())
            function = self.current_frame.stack[-1]
            self.call_function(function, args)
            self.current_frame.stack.pop()
            self.current_frame.stack.append(self.retval)
        elif op == LOAD_ATTR:
            self.current_frame.stack.append(getattr(self.current_frame.stack.pop(), ins.argval))
        elif op == JUMP_ABSOLUTE:
            self.current_frame.ip = ins.argval//2 - 1
        elif op == BINARY_TRUE_DIVIDE:
            a = self.current_frame.stack.pop()
            b = self.current_frame.stack.pop()
            self.current_frame.stack.append(b / a)
        elif op == INPLACE_ADD:
            a = self.current_frame.stack.pop()
            b = self.current_frame.stack.pop()
            self.current_frame.stack.append(b + a)
        elif op == BINARY_MULTIPLY:
            a = self.current_frame.stack.pop()
            b = self.current_frame.stack.pop()
            self.current_frame.stack.append(b * a)
        elif op == BINARY_ADD:
            a = self.current_frame.stack.pop()
            b = self.current_frame.stack.pop()
            self.current_frame.stack.append(b + a)
        elif op == GET_ITER:
            self.current_frame.stack.append(iter(self.current_frame.stack.pop()))
        elif op == FOR_ITER:
            delta = ins.argval
            iterable = self.current_frame.stack[-1]
            try:
                self.current_frame.stack.append(next(iterable))
            except StopIteration:
                self.current_frame.stack.pop()
                self.current_frame.ip = delta//2 - 1
        elif op == BUILD_LIST:
            vals = list((self.current_frame.stack.pop() for x in range(ins.arg)))
            self.current_frame.stack.append(list(reversed(vals)))
        else:
            print(f"ERROR: {op} ({ins.opname}) not supported yet!")
            exit(1)
    def call_function(self, function, args):
        print(function, args)
        if type(function) == types.CodeType:
            self.current_frame_index += 1
            self.frames.append(CallFrame(self.current_frame.stack.index(function), self.current_frame.stack + args, function))
            self.current_frame = self.frames[self.current_frame_index]
            self.run()
        else:
            try:
                self.retval = function(*args)
            except Exception as e:
                print(e)
                self.retval = function(*(reversed(args)))

    def run(self):
        instructions = list(self.current_frame.instructions).copy()
        while self.current_frame.ip < len(instructions):
            ins = list(instructions)[self.current_frame.ip]
            self.run_ins(ins)
            self.current_frame.ip += 1