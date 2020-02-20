import numpy as np
from pysindy import SINDy
from pysindy.optimizers import STLSQ
from pysindy.feature_library import PolynomialLibrary
from pysindy.differentiation import FiniteDifference
from matplotlib import pyplot as plt

def scalar_POD(Bx_mat,By_mat,Bz_mat,Vx_mat,Vy_mat,Vz_mat, \
    time,threshold,poly_order):
    ## SVD separately
    uBx,sBx,vBx = np.linalg.svd(Bx_mat,full_matrices=False)
    uBy,sBy,vBy = np.linalg.svd(By_mat,full_matrices=False)
    uBz,sBz,vBz = np.linalg.svd(Bz_mat,full_matrices=False)
    uVx,sVx,vVx = np.linalg.svd(Vx_mat,full_matrices=False)
    uVy,sVy,vVy = np.linalg.svd(Vy_mat,full_matrices=False)
    uVz,sVz,vVz = np.linalg.svd(Vz_mat,full_matrices=False)
    bx1 = vBx[0,:]*sBx[0]/np.sqrt(sBx[0]**2+sBx[1]**2+sBx[2]**2)
    bx2 = vBx[1,:]*sBx[1]/np.sqrt(sBx[0]**2+sBx[1]**2+sBx[2]**2)
    bx3 = vBx[2,:]*sBx[2]/np.sqrt(sBx[0]**2+sBx[1]**2+sBx[2]**2)
    by1 = vBy[0,:]*sBy[0]/np.sqrt(sBy[0]**2+sBy[1]**2+sBy[2]**2)
    by2 = vBy[1,:]*sBy[1]/np.sqrt(sBy[0]**2+sBy[1]**2+sBy[2]**2)
    by3 = vBy[2,:]*sBy[2]/np.sqrt(sBy[0]**2+sBy[1]**2+sBy[2]**2)
    bz1 = vBz[0,:]*sBz[0]/np.sqrt(sBz[0]**2+sBz[1]**2+sBz[2]**2)
    bz2 = vBz[1,:]*sBz[1]/np.sqrt(sBz[0]**2+sBz[1]**2+sBz[2]**2)
    bz3 = vBz[2,:]*sBz[2]/np.sqrt(sBz[0]**2+sBz[1]**2+sBz[2]**2)
    vx1 = vVx[0,:]*sVx[0]/np.sqrt(sVx[0]**2+sVx[1]**2+sVx[2]**2)
    vx2 = vVx[1,:]*sVx[1]/np.sqrt(sVx[0]**2+sVx[1]**2+sVx[2]**2)
    vx3 = vVx[2,:]*sVx[2]/np.sqrt(sVx[0]**2+sVx[1]**2+sVx[2]**2)
    vy1 = vVy[0,:]*sVy[0]/np.sqrt(sVy[0]**2+sVy[1]**2+sVy[2]**2)
    vy2 = vVy[1,:]*sVy[1]/np.sqrt(sVy[0]**2+sVy[1]**2+sVy[2]**2)
    vy3 = vVy[2,:]*sVy[2]/np.sqrt(sVy[0]**2+sVy[1]**2+sVy[2]**2)
    vz1 = vVz[0,:]*sVz[0]/np.sqrt(sVz[0]**2+sVz[1]**2+sVz[2]**2)
    vz2 = vVz[1,:]*sVz[1]/np.sqrt(sVz[0]**2+sVz[1]**2+sVz[2]**2)
    vz3 = vVz[2,:]*sVz[2]/np.sqrt(sVz[0]**2+sVz[1]**2+sVz[2]**2)
    x_test = np.transpose([bx1,bx2,bx3,by1,by2,by3,bz1,bz2,bz3, \
        vx1,vx2,vx3,vy1,vy2,vy3,vz1,vz2,vz3])
    plt.figure(2)
    plt.subplot(1,3,1)
    plt.plot(bx1,'r')
    plt.subplot(1,3,2)
    plt.plot(bx2,'r')
    plt.subplot(1,3,3)
    plt.plot(bx3,'r')
    # SINDy now
    model = SINDy(optimizer=STLSQ(threshold=threshold), \
        feature_library=PolynomialLibrary(degree=poly_order), \
        differentiation_method=FiniteDifference(drop_endpoints=True), \
        feature_names=['bx1','bx2','bx3','by1','by2','by3','bz1','bz2','bz3', \
            'vx1','vx2','vx3','vy1','vy2','vy3','vz1','vz2','vz3'])
    print(np.shape(x_test))
    print(np.shape(time))
    model.fit(x_test, t=time)
    model.print()
    print(model.coefficients())
    t_test = time
    x0_test = x_test[0,:]
    x_test_sim = model.simulate(x0_test,t_test)
    x_dot_test_computed = model.differentiate(x_test, t=time)
    x_dot_test_predicted = model.predict(x_test)
    print('Model score: %f' % model.score(x_test, t=time))
    fig, axs = plt.subplots(x_test.shape[1], 1, sharex=True, figsize=(7,9))
    for i in range(x_test.shape[1]):
        axs[i].plot(t_test, x_dot_test_computed[:,i], 'k', label='numerical derivative')
        axs[i].plot(t_test, x_dot_test_predicted[:,i], 'r--', label='model prediction')
        #axs[i].legend()
        axs[i].set(xlabel='t', ylabel='$\dot x_{}$'.format(i))
    fig, axs = plt.subplots(x_test.shape[1], 1, sharex=True, figsize=(7,9))
    for i in range(x_test.shape[1]):
        axs[i].plot(t_test, x_test[:,i], 'k', label='true simulation')
        axs[i].plot(t_test, x_test_sim[:,i], 'r--', label='model simulation')
        #axs[i].set(xlim=(10,120)) #,ylim=(-20,20))
        #axs[i].legend()
        axs[i].set(xlabel='t', ylabel='$x_{}$'.format(i))

    fig = plt.figure(figsize=(10,4.5))
    ax1 = fig.add_subplot(321, projection='3d')
    ax1.plot(x_test[:,0],x_test[:,1],x_test[:,2], 'k')
    ax1.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$B_x$ true simulation')
    ax2 = fig.add_subplot(322, projection='3d')
    ax2.plot(x_test_sim[:,0],x_test_sim[:,1],x_test_sim[:,2], 'r--')
    ax2.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$B_x$ model simulation')
    ax3 = fig.add_subplot(323, projection='3d')
    ax3.plot(x_test[:,3],x_test[:,4],x_test[:,5], 'k')
    ax3.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$B_y$ true simulation')
    ax4 = fig.add_subplot(324, projection='3d')
    ax4.plot(x_test_sim[:,3],x_test_sim[:,4],x_test_sim[:,5], 'r--')
    ax4.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$B_y$ model simulation')
    ax5 = fig.add_subplot(325, projection='3d')
    ax5.plot(x_test[:,6],x_test[:,7],x_test[:,8], 'k')
    ax5.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$B_z$ true simulation')
    ax6 = fig.add_subplot(326, projection='3d')
    ax6.plot(x_test_sim[:,6],x_test_sim[:,7],x_test_sim[:,8], 'r--')
    ax6.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$B_z$ model simulation')
    fig = plt.figure(figsize=(10,4.5))
    ax1 = fig.add_subplot(321, projection='3d')
    ax1.plot(x_test[:,9],x_test[:,10],x_test[:,11], 'k')
    ax1.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$V_x$ true simulation')
    ax2 = fig.add_subplot(322, projection='3d')
    ax2.plot(x_test_sim[:,9],x_test_sim[:,10],x_test_sim[:,11], 'r--')
    ax2.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$V_x$ model simulation')
    ax3 = fig.add_subplot(323, projection='3d')
    ax3.plot(x_test[:,12],x_test[:,13],x_test[:,14], 'k')
    ax3.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$V_y$ true simulation')
    ax4 = fig.add_subplot(324, projection='3d')
    ax4.plot(x_test_sim[:,12],x_test_sim[:,13],x_test_sim[:,14], 'r--')
    ax4.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$V_y$ model simulation')
    ax5 = fig.add_subplot(325, projection='3d')
    ax5.plot(x_test[:,15],x_test[:,16],x_test[:,17], 'k')
    ax5.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$V_z$ true simulation')
    ax6 = fig.add_subplot(326, projection='3d')
    ax6.plot(x_test_sim[:,15],x_test_sim[:,16],x_test_sim[:,17], 'r--')
    ax6.set(xlabel='$x_0$', ylabel='$x_1$', zlabel='$x_2$', title=r'$V_z$ model simulation')