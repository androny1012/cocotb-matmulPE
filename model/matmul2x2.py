import numpy as np

a = np.array([0,4,1,5],dtype=np.int8).reshape(2,2)
b = np.array([2,3,6,7],dtype=np.int8).reshape(2,2)

c = np.dot(a,b).flatten()
print(c)

data_np = np.hstack([a.T,b]).flatten()
print(data_np)

out1 = np.array([32,38],dtype=np.int16)
out2 = np.array([24,28],dtype=np.int16)

out_hw = np.hstack([out2,out1])
print(out_hw)

print((out_hw == c).all())