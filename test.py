import sys
from io import StringIO
old_stdout = sys.stdout
sys.stdout = StringIO()

print("Hi")
print("Kirmi")
x = sys.stdout.getvalue()

print("xorom")
print("aissala")
y = sys.stdout.getvalue()

print("kheilla")
print("dichos")
print(x)
z = sys.stdout.getvalue()

sys.stdout = old_stdout
print(y)
print(z)