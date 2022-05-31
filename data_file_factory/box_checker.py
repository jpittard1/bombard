
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
            new_points[i] = Rotate.about_z(row, self.rotation_deg['z'], round_dp = 4)

        setattr(self, 'points', new_points)



    def dimension_check(self, minimum_length, rotation_axis):

        theta_rad = self.rotation_deg[rotation_axis]*np.pi/180
        h = minimum_length*np.sin(theta_rad)*np.sin(np.pi/2 - theta_rad)
        return h
    
    def valid_region(self, desired_replicate = [3,3,3]):

        xmax,ymax,zmax = [max(self.points[:,i])  - self.dimension_check(desired_replicate[i]*3.567, 'z') for i in range(0,3)]
        xmin,ymin,zmin = [min(self.points[:,i])  + self.dimension_check(desired_replicate[i]*3.567, 'z') for i in range(0,3)]

        new_points = []
        for point in self.points:
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

        valid_region = self.valid_region(desired_replicate = desired_replicate)

        if valid_region.size == 0:
            return valid_region

        center = [max(valid_region[:,i] - min(valid_region[:,i]))/2 + min(valid_region[:,i]) for i in range(0,3)]

        xmax,ymax,zmax = [center[i] + desired_replicate[i]*3.567/2 for i in range(0,3)]
        xmin,ymin,zmin = [center[i] - desired_replicate[i]*3.567/2 for i in range(0,3)]

        plt.plot([xmin,xmin,xmax,xmax,xmin], [ymin,ymax,ymax,ymin,ymin])
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

    test_replicate = [i for i in desired_replicate]

    for i in range(1, 30):

        cube = Cuboid(test_replicate, rotation=rotation_deg)
        cube.rotate()

        final = cube.get_region(desired_replicate)
        reduced = cube.valid_region

        if final.size != 0:
            if plot != False:
                plt.scatter(cube.points[:,0], cube.points[:,1])
                plt.scatter(reduced[:,0], reduced[:,1])
                plt.scatter(final[:,0], final[:,1])
                plt.xlabel('x')
                plt.ylabel('y')
                plt.axis('square')
                plt.show()
            
            else:
                return cube.replicate, cube.lims
            break

        else:
            print(f'Please use a bigger replication than {cube.replicate}')
            test_replicate[int(i%3)] = test_replicate[int(i%3)] + 1


if __name__ == '__main__':
    try:
        desired_replicate = tools.str_to_list(sys.argv[1], float_vals = True)
        rotation = tools.str_to_list(sys.argv[2], float_vals = True)
        main(desired_replicate, rotation, True)
    except IndexError:
        print('\nERROR: Please give values for desired replicate and rotation:')
        print('eg: python box_checker.py [6,6,8] [0,0,30]')
        print('For a [6,6,8] size crystal rotated 30degs about the z axis.')