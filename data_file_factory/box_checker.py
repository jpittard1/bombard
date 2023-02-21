
import numpy as np
import matplotlib.pyplot as plt
from rotate import Rotate
import sys
import os

current_dir = os.path.dirname(os.path.realpath(__file__)).split('/')
sep = '/'
path = sep.join(current_dir[:-1])
print(path)
sys.path.append(path)
import tools

class Cuboid:

    def __init__(self, replicate, rotation = [0,0,0]):

        self.replicate = dict(x = int(replicate[0]),
                        y = int(replicate[1]),
                        z = int(replicate[2]))

        self.dims = dict(x = float(replicate[0]*3.567),
                        y = float(replicate[1]*3.567),
                        z = float(replicate[2]*3.567))

        self.rotation_deg = dict(x = float(rotation[0]),
                        y = float(rotation[1]),
                        z = float(rotation[2]))

        self.unit_cells = int(self.replicate['x']*self.replicate['y']*self.replicate['z'])

        self.points = self.construct()

    def __repr__(self):
        return str(self.points)

    def construct(self):
        '''Contructs an array representing each corner of the unit cells for the desired replicate.'''

        numbers_of_points = int((self.replicate['x']+1)*(self.replicate['y']+1)*(self.replicate['z']+1))
        points = np.zeros([numbers_of_points, 3])
        count = 0

        for i in range(0,self.replicate['x']+1):
            for j in range(0,self.replicate['y']+1):
                for k in range(0,self.replicate['z']+1):
                    points[count] = np.array([i,j,k])*3.567
                    count += 1

        return points

    
    def rotate(self):
        new_points = np.zeros([self.points.shape[0], 3])
        for i, row in enumerate(self.points):
            newrow = Rotate.about_x(row, self.rotation_deg['x'], round_dp = 4)
            newrow = Rotate.about_y(newrow, self.rotation_deg['y'], round_dp = 4)
            new_points[i] = Rotate.about_z(newrow, self.rotation_deg['z'], round_dp = 4)

        setattr(self, 'points', new_points)

    def rotate_gen(self):
        '''Performs general rotation on points array to represent rotated volume of crystal.'''
        angles_deg = [item for item in self.rotation_deg.items()]
        rotation_mtrx = Rotate.general(angles_deg, round_dp = 4)
        
        new_points = np.zeros([self.points.shape[0], 3])
        for i, row in enumerate(self.points):
            new_points[i] = np.dot(rotation_mtrx, row)

        setattr(self, 'points', new_points)



    def dimension_check(self, minimum_length, rotation_axis):
        '''Calculates distance from the extremeties of rotated points, to
        the first point where the width of the rotated crystal would allow
        for the disired replicate to be possible for 1 dimension. '''

        theta_rad = self.rotation_deg[rotation_axis]*np.pi/180
        h = minimum_length*np.sin(theta_rad)*np.sin(np.pi/2 - theta_rad)
       
        return h

    def dimension_check_3D(self, replicate, rotation_axis):
        '''Not working, cannot work out an effiecent way '''
        
        theta_rad = self.rotation_deg[rotation_axis]*np.pi/180

        if rotation_axis == 'z':
            l_sqrd = (replicate[0]*np.sin(theta_rad)*np.sin(np.pi/2 - theta_rad))**2 + (replicate[0]/2)**2
            return l_sqrd**0.5
            
   
    
    def region_check(self, desired_replicate = [3,3,3], axis = 'z', points_arr = np.array([[None]])):
        '''Takes max/min of rotated points array and subtracts/adds the distance from extremeties
        required to allow for the desired replicate. If the desired replicate is too small no points will
        be within the bounds set by this.'''

        axes = ['x','y','z']
        xmax,ymax,zmax = [max(self.points[:,i])  - self.dimension_check(desired_replicate[i]*3.567, rotation_axis=axes[i]) for i in range(0,3)]
        xmin,ymin,zmin = [min(self.points[:,i])  + self.dimension_check(desired_replicate[i]*3.567, rotation_axis=axes[i]) for i in range(0,3)]
   
        new_points = []
        if points_arr[0][0] == None:
            points_arr = self.points

        for point in points_arr:
            if point[0] >= xmin and point[0] <= xmax:
                if point[1] >= ymin and point[1] <= ymax:
                    if point[2] >= zmin and point[2] <= zmax:
                        new_points.append(point)
                        

        if len(new_points) < (desired_replicate[0]+1)*(desired_replicate[1]+1)*(desired_replicate[2]+1):
            setattr(self, 'valid_region', np.array([]))
            return np.array([])

        reduced_arr = np.zeros([len(new_points), 3])
        for i, point in enumerate(new_points):
            reduced_arr[i] = point

        setattr(self, 'valid_region', reduced_arr)

        return reduced_arr

    def get_region(self, desired_replicate = [3,3,3]):
        '''Reduces rotated points array to size included '''

        valid_region = self.region_check(desired_replicate = desired_replicate, axis = 'x')
        
        if valid_region.size == 0:
            return valid_region
     
        center = [max(valid_region[:,i] - min(valid_region[:,i]))/2 + min(valid_region[:,i]) for i in range(0,3)]

        xmax,ymax,zmax = [center[i] + desired_replicate[i]*3.567/2 for i in range(0,3)]
        xmin,ymin,zmin = [center[i] - desired_replicate[i]*3.567/2 for i in range(0,3)]

        lims = [[xmin,xmax],[ymin,ymax],[zmin,zmax]]
        setattr(self, 'lims', lims)

        new_points = []
        for point in self.points:
            if point[0] >= xmin and point[0] <= xmax:
                if point[1] >= ymin and point[1] <= ymax:
                    if point[2] >= zmin and point[2] <= zmax:
                        new_points.append(point)

        reduced_arr = np.zeros([len(new_points), 3])
        for i, point in enumerate(new_points):
            reduced_arr[i] = point

        return reduced_arr
        
def main(desired_replicate, rotation_deg, plot = False):
    plot = False
    test_replicate = [i for i in desired_replicate]

    for i in range(1, 50):

        cube = Cuboid(test_replicate, rotation=rotation_deg)
        cube.rotate()

        final = cube.get_region(desired_replicate) #region to be used (trimmed to size)
        reduced = cube.valid_region #should be full region that could be used

        if final.size != 0:
            if plot != False:
                plt.scatter(cube.points[:,0], cube.points[:,1])
                plt.scatter(reduced[:,0], reduced[:,1])
                plt.scatter(final[:,0], final[:,1])
                plt.xlabel('x')
                plt.ylabel('y')
                plt.axis('square')
                plt.show()

                plt.scatter(cube.points[:,0], cube.points[:,2])
                plt.scatter(reduced[:,0], reduced[:,2])
                plt.scatter(final[:,0], final[:,2])
                plt.xlabel('x')
                plt.ylabel('z')
                plt.axis('square')
                plt.show()

                plt.scatter(cube.points[:,1], cube.points[:,2])
                plt.scatter(reduced[:,1], reduced[:,2])
                plt.scatter(final[:,1], final[:,2])
                plt.xlabel('y')
                plt.ylabel('z')
                plt.axis('square')
                plt.show()
            
            else:
                return cube.replicate, cube.lims
            break

        else:
            print(f'Please use a bigger replication than {cube.replicate}')
            test_replicate[int(i%3)] = test_replicate[int(i%3)] + 5


if __name__ == '__main__':
    try:
        desired_replicate = tools.str_to_list(sys.argv[1], float_vals = True)
        rotation = tools.str_to_list(sys.argv[2], float_vals = True)
        main(desired_replicate, rotation, True)
    except IndexError:
        print('\nERROR: Please give values for desired replicate and rotation:')
        print('eg: python box_checker.py [6,6,8] [0,0,30]')
        print('For a [6,6,8] size crystal rotated 30degs about the z axis.')