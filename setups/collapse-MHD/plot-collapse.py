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
MYR = 3.15576000e13 #s

outs = [4,6,7,9]
zooms = [12000, 3000, 750, 81.25]
names = ['collapse_evo_stage1', 'collapse_evo_stage2', 'collapse_evo_stage3', 'collapse_evo_stage4']

t0=0

for out, zoom, name in zip(outs, zooms, names):
    namelist = f90nml.read(f"output_0000{out}/namelist.txt")

    #--------- Centered image ---------------

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))

    # Load RAMSES output
    data = visu_ramses.load_snapshot(out)
    unit_d = data["data"]["unit_d"]
    unit_t = data["data"]["unit_t"]
    unit_l = data["data"]["unit_l"]
    dx = data["data"]["dx"] * unit_l / AU 
    rho  =  data["data"]["density"] * unit_d
    time = int(data["data"]["time"] * unit_l / MYR)
    ax.set_title(f'{time} MYR')

    print('Max resolution = ', dx, 'AU')

    # zoom on the center
    x = (data["data"]["x"] - 0.5*data["data"]["boxlen"]) * unit_l / AU
    y = (data["data"]["y"] - 0.5*data["data"]["boxlen"]) * unit_l / AU
    z = (data["data"]["z"] - 0.5*data["data"]["boxlen"]) * unit_l / AU
    nx = 2**9
    dxmin = np.min(dx)
    # zoom = nx*dxmin
    filt = np.where((abs(x)<zoom)&(abs(y<zoom))&(abs(z<zoom)))

    # generate grid points for interpolation
    xpx = np.linspace(-0.5*zoom + 0.5*dxmin, 0.5*zoom - 0.5*dxmin,nx)
    grid_x, grid_y, grid_z = np.meshgrid(xpx,xpx,xpx)
    points = np.transpose([x,y,z])

    # interpolate
    z1 = griddata(points,rho,(grid_x,grid_y, grid_z),method='nearest')

    # project and plot
    rho_proj = np.sum(z1, axis=2) #proj along x-axis
    im1 = ax.imshow(np.log10(rho_proj), origin="lower", aspect='equal', 
                    extent=[-0.5*zoom, 0.5*zoom, -0.5*zoom, 0.5*zoom])

    plt.colorbar(im1, ax=ax, label='log column density')
    ax.set_xlabel('x [AU]')
    ax.set_ylabel('y [AU]')

    fig.savefig(f'{name}.png',bbox_inches='tight')
    plt.close(fig)

    #--------- Image of 1 core ---------------

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))

    nx = 2**8
    dxmin = np.min(dx)
    zoom = nx*dxmin
    index_core = np.where(rho == np.max(rho))[0][0]
    print('debug', index_core)
    center_x = x[index_core]
    center_y = y[index_core]
    center_z = z[index_core]
    x = (x - center_x)
    y = (y - center_y)
    z = (z - center_z)
    filt = np.where((abs(x)<zoom)&(abs(y<zoom))&(abs(z<zoom)))

    # generate grid points for interpolation
    xpx = np.linspace(-0.5*zoom + 0.5*dxmin, 0.5*zoom - 0.5*dxmin,nx)
    grid_x, grid_y, grid_z = np.meshgrid(xpx,xpx,xpx)
    points = np.transpose([x,y,z])

    # interpolate
    z1 = griddata(points,rho,(grid_x,grid_y, grid_z),method='nearest')

    # project and plot
    rho_proj = np.sum(z1, axis=2) #proj along x-axis
    im1 = ax.imshow(np.log10(rho_proj), origin="lower", aspect='equal', 
                    extent=[-0.5*zoom, 0.5*zoom, -0.5*zoom, 0.5*zoom])

    plt.colorbar(im1, ax=ax, label='log column density')
    ax.set_xlabel('x [AU]')
    ax.set_ylabel('y [AU]')
    ax.set_title('zoom on 2nd core')

    fig.savefig(f'{name}_zoom.png',bbox_inches='tight')
    plt.close(fig)

    #--------- Temperature - density diagram ---------------

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