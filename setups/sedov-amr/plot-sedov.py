import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import visu_ramses
from scipy.interpolate import griddata

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(7, 3.5))

# Load RAMSES output
data = visu_ramses.load_snapshot(2)
x      = data["data"]["x"]
y      = data["data"]["y"]
z      = data["data"]["z"]
dx     = data["data"]["dx"]
rho    = data["data"]["density"]
l      = data["data"]["level"]

xmin = np.amin(x-0.5*dx)
xmax = np.amax(x+0.5*dx)
ymin = np.amin(y-0.5*dx)
ymax = np.amax(y+0.5*dx)
zmin = np.amin(z-0.5*dx)
zmax = np.amax(z+0.5*dx)

nx  = 2**8
dpx = (xmax-xmin)/float(nx)
dpy = (ymax-ymin)/float(nx)
dpz = (zmax-zmin)/float(nx)
xpx = np.linspace(xmin+0.5*dpx,xmax-0.5*dpx,nx)
ypx = np.linspace(ymin+0.5*dpy,ymax-0.5*dpy,nx)
zpx = np.linspace(zmin+0.5*dpz,zmax-0.5*dpz,nx)
grid_x, grid_y, grid_z = np.meshgrid(xpx,ypx,zpx)
points = np.transpose([x,y,z])
z1 = griddata(points,rho,(grid_x,grid_y, grid_z),method='nearest')
zl = griddata(points,l,(grid_x,grid_y, grid_z),method='nearest')

rho_proj3 = np.sum(z1, axis=2) #proj along z-axis
l_proj3 = np.max(zl, axis=2) #proj along z-axis

im3 = ax[0].imshow(rho_proj3, origin="lower", aspect='equal', extent=[xmin, xmax, ymin, ymax])
im9 = ax[1].imshow(l_proj3, origin="lower", aspect='equal', extent=[xmin, xmax, ymin, ymax])

cb = []

cb.append(plt.colorbar(im3, ax=ax[0], label='density'))
cb.append(plt.colorbar(im9, ax=ax[1], label='level'))

for i in [0,1]:
    ax[i].set_xlabel('x')
    ax[i].set_ylabel('y')

for c in cb:
    c.ax.yaxis.set_label_coords(-1.1, 0.5)

fig.savefig('sedov.png',bbox_inches='tight')

