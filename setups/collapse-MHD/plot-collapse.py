import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import f90nml
# place visu_ramses.py from the ramses test suite into this folder to use this plotting script
import visu_ramses
from scipy.interpolate import griddata

# Fundamental constants
MH = 1.6737236e-24 #g                      # hydrogen mass
KB = 1.38064852e-16 #cm^2 g s^-2 K^-1      # Boltzman constant
AU = 1.49597871e13 #cm                     # 1 astronomical unit
kYR = 3.15576000e10 #s

''' Make an image zoomed in on a part of the box '''
def make_image(data, zoom, outname='image.png', center='center', ax=None):

    # gather data
    unit_d = data["data"]["unit_d"]
    unit_t = data["data"]["unit_t"]
    unit_l = data["data"]["unit_l"]
    dx = data["data"]["dx"] * unit_l / AU 
    rho  =  data["data"]["density"] * unit_d

    save=False
    if ax==None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))
        save=True

    #time = data["data"]["time"] * unit_t / kYR
    #ax.set_title(f'{time:.3} kyr')
    dxmin = np.min(dx)
    #print('Max resolution = ', dxmin, 'AU')

    # re-center and convert to AU
    if center=='center':
        x = (data["data"]["x"] - 0.5*data["data"]["boxlen"]) * unit_l / AU
        y = (data["data"]["y"] - 0.5*data["data"]["boxlen"]) * unit_l / AU
        z = (data["data"]["z"] - 0.5*data["data"]["boxlen"]) * unit_l / AU
    elif center=='core':
        index_core = np.where(rho == np.max(rho))[0][0]
        #print('debug', index_core)
        center_x = data["data"]["x"][index_core]
        center_y = data["data"]["y"][index_core]
        center_z = data["data"]["z"][index_core]
        x = (data["data"]["x"] - center_x) * unit_l / AU
        y = (data["data"]["y"] - center_y) * unit_l / AU
        z = (data["data"]["z"] - center_z) * unit_l / AU

    # generate grid points for interpolation
    nx = 2**8
    xpx = np.linspace(-0.5*zoom + 0.5*dxmin, 0.5*zoom - 0.5*dxmin,nx)
    grid_x, grid_y, grid_z = np.meshgrid(xpx,xpx,xpx)
    points = np.transpose([x,y,z])

    # interpolate
    z1 = griddata(points,rho,(grid_x,grid_y, grid_z),method='nearest')

    # project and plot
    rho_proj = np.sum(z1, axis=2) #proj along x-axis
    im1 = ax.imshow(np.log10(rho_proj), origin="lower", aspect='equal', 
                    extent=[-0.5*zoom, 0.5*zoom, -0.5*zoom, 0.5*zoom])

    if save:
        ax.set_xlabel('x [AU]')
        ax.set_ylabel('y [AU]')
        plt.colorbar(im1, ax=ax, label='log(column density)')
        fig.savefig(outname, bbox_inches='tight')
        plt.close(fig)
    #else:
    #    ax.set_axis_off()


''' Temperature - density diagram '''
def rho_temperature_diagram(data, out):

    # gather data
    unit_d = data["data"]["unit_d"]
    unit_t = data["data"]["unit_t"]
    unit_l = data["data"]["unit_l"]
    rho  =  data["data"]["density"] * unit_d

    namelist = f90nml.read(f"output_0000{out}/namelist.txt")
    mu_gas = namelist['cooling_params']['mu_gas']

    p    =  data["data"]["pressure"] * unit_d * unit_l**2 / unit_t**2
    T    = p/rho * mu_gas * MH /KB
    print("DEBUG: min(T) =", np.min(T))

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))

    # histogram bin edges
    dmin = -18.5
    dmax = -3.0
    tmin = 0.5
    tmax = np.log10(max(T)) + 0.5
    nx = 129
    d_edges = np.linspace(dmin,dmax,nx)
    t_edges = np.linspace(tmin,tmax,nx)

    # compute histogram
    za, yedges1, xedges1 = np.histogram2d(np.log10(T),np.log10(rho),bins=(t_edges,d_edges))

    # bin centers
    d_mesh = np.zeros([nx-1])
    t_mesh = np.zeros([nx-1])
    for i in range(nx-1):
        d_mesh[i] = 0.5*(d_edges[i]+d_edges[i+1])
        t_mesh[i] = 0.5*(t_edges[i]+t_edges[i+1])

    # plot contour of histogram
    ax.contour(d_mesh,t_mesh,za,colors='r',levels=[1.0])

    # overplot analytical solution EOS
    polytrope_rho1 = 3.866301516e-15
    polytrope_rho2 = 3.866301516e-10
    polytrope_rho3 = 3.866301516e-05
    polytrope_i1 = 0.4
    polytrope_i2 = -0.3
    polytrope_i3 = 0.56667
    rho_ana = np.logspace(dmin,dmax,100)
    factor1 = np.sqrt(1 + (rho_ana/polytrope_rho1)**(2*polytrope_i1))
    factor2 = (1 + (rho_ana/polytrope_rho2))**polytrope_i2
    factor3 = (1 + (rho_ana/polytrope_rho3))**polytrope_i3
    T_ana = 10 * factor1 * factor2 * factor3
    ax.plot(np.log10(rho_ana), np.log10(T_ana), color='black')

    # layout
    ax.set_xlabel('log(rho)')
    ax.set_ylabel('log(T)')

    fig.savefig(f'collapse_T{out}.png',bbox_inches='tight')
    plt.close(fig)


fig, axes = plt.subplots(nrows=5, ncols=5, figsize=(12, 12))

for out,i in zip([1,6,7,8,9], range(5)):
    data = visu_ramses.load_snapshot(out)

    unit_t = data["data"]["unit_t"]
    time = data["data"]["time"] * unit_t / kYR
    axes[0][i].set_title(f'{time:.3} kyr')

    for zoom,center,j in zip([6000,750,150,20,0.8],['center','center','center','core','core'],range(5)):
        make_image(data, zoom, center=center, ax=axes[j][i])

'''
# Load RAMSES output
data = visu_ramses.load_snapshot(1)
make_image(data, 6000, 't0.png', ax=axes[0][0])

data = visu_ramses.load_snapshot(6)
make_image(data, 6000, 't1.png', ax=axes[0][1])
make_image(data,  750, 't1_zoom.png', ax=axes[1][1])

data = visu_ramses.load_snapshot(7)
make_image(data,  750, 't2.png', ax=axes[1][2])
make_image(data,  150, 't2_zoom.png', ax=axes[2][2])
make_image(data,   20, 't2_core.png', center='core', ax=axes[3][2])
make_image(data,    1, 't2_core_zoom.png', center='core', ax=axes[4][2])

data = visu_ramses.load_snapshot(8)
make_image(data,  750, 't3.png', ax=axes[1][3])
make_image(data,  150, 't3_zoom.png', ax=axes[2][3])
make_image(data,   20, 't3_core.png', center='core', ax=axes[3][3])
make_image(data,    1, 't3_core_zoom.png', center='core', ax=axes[4][3])

data = visu_ramses.load_snapshot(9)
make_image(data,  750, 't4.png', ax=axes[1][4])
make_image(data,  150, 't4.png', ax=axes[2][4])
make_image(data,   20, 't4_core.png', center='core', ax=axes[3][4])
make_image(data,    1, 't4_core_zoom.png', center='core', ax=axes[4][4])

'''

axes[0][0].set_ylabel('6000 AU')
axes[1][0].set_ylabel('750 AU')
axes[2][0].set_ylabel('150 AU')
axes[3][0].set_ylabel('20 AU')
axes[4][0].set_ylabel('0.8 AU')

fig.savefig('collapse.png',bbox_inches='tight')
plt.close(fig)


rho_temperature_diagram(data, 9)