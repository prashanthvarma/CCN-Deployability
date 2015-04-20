import numpy as np
import matplotlib.pyplot as plt

#datamin = -5
#datamax = 5
#numbins = 20
#mybins = np.linspace(datamin, datamax, numbins)
#myhist = np.zeros(numbins-1, dtype='int32')
#for i in range(100):
#    d = np.random.randn(1000,1)
#    htemp, jnk = np.histogram(d, mybins)
#    myhist += htemp
#    
#bin_edges = myhist
#hist = myhist


import matplotlib.mlab as mlab

mean = 0
variance = 2.0/3
sigma = np.sqrt(variance)
x = np.linspace(-3,3,100)
plt.plot(x,mlab.normpdf(x,mean,sigma))

plt.show()
#
#
#hist, bin_edges = np.histogram([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.2, 0.3], bins = list(np.linspace(0, 0.5, 5)))
#plt.bar(bin_edges[:-1], hist, width = 0.1)
#plt.xlim(min(bin_edges), max(bin_edges))
#plt.show() 