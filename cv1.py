'''
A

import numpy as np
import sys
n=int(input())
a=np.fliplr(np.tril(np.ones((n, n))*2, 0))
a-=np.fliplr(np.eye(n))
np.savetxt(sys.stdout, a, fmt="%d")

B

import numpy as np
import sys

n = int(input())
a = np.loadtxt(sys.stdin, dtype=int)
b = np.transpose(a)
if np.array_equal(a, b):
    print('yes')
else:
    print('no')

C

import numpy as np
import sys

n, m = map(int, input().split())
a = np.loadtxt(sys.stdin, dtype=int).reshape(n, m)
s = np.max(a, axis = 1)
print(np.sum(s == np.max(a)))

E

import numpy as np
import sys

n, m = map(int, input().split())
a = np.loadtxt(sys.stdin, dtype=int).reshape(n, m)
a = np.rot90(a, k=-1)
print(*a.shape)
np.savetxt(sys.stdout, a, fmt="%d")
'''