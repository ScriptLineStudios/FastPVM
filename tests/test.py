def f2(x):
        print("in another func!")
        return x

def f1():
        return f2(55)

print("RESULT")
print(f1()) 