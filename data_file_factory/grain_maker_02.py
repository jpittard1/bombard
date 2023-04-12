

import numpy as np
import matplotlib.pyplot as plt
from rotate import Rotate, Shift
from data_file_maker import array_to_datafile, xyz_to_array
import os
import sys
import glob
current_dir = os.path.dirname(os.path.realpath(__file__)).split('/')
sep = '/'
path = sep.join(current_dir[:-1])

sys.path.append(path)
import tools


class BoxChecker:

    def __init__(self, target_replicate, rotation):
        self.target = target_replicate
        self.rotation = rotation

    
    def height_check(self, angle, a, b):
        return 2*a*np.sin((angle)*np.pi/180) + np.sqrt(a**2 + b**2)*np.sin((45-angle)*np.pi/180)
    
    def width_check(self, angle, a,b):
        return np.sqrt(a**2 + b**2)*np.cos((45-angle)*np.pi/180)
    
    def find_size(self):
    
        x_lims, y_lims, z_lims = [[],[],[]]

        x_lims.append(self.width_check(self.rotation[2], self.target[0], self.target[1]))
        x_lims.append(self.width_check(self.rotation[1], self.target[0], self.target[2]))

        y_lims.append(self.height_check(self.rotation[2], self.target[0], self.target[1]))
        y_lims.append(self.height_check(self.rotation[0], self.target[2], self.target[1]))

        z_lims.append(self.width_check(self.rotation[0], self.target[2], self.target[1]))
        z_lims.append(self.height_check(self.rotation[1], self.target[0], self.target[2]))

        print([max(x_lims), max(y_lims), max(z_lims)])
        return [max(x_lims), max(y_lims), max(z_lims)]
    

    def simple_size(self,a,b,c):
        return

        


class Crystal:

    def __init__(self, replicate):
        self.replicate = np.array(replicate)
        self.unit_atom_coords =  np.array([[0.0000000000 ,0.0000000000 ,0.0000000000],
                                    [0.0000000000, 1.7835000000, 1.7835000000],
                                    [1.7835000000, 0.0000000000, 1.7835000000],
                                    [1.7835000000, 1.7835000000, 0.0000000000],
                                    [0.8917500000, 0.8917500000, 0.8917500000],
                                    [0.8917500000, 2.6752500000, 2.6752500000],
                                    [2.6752500000, 0.8917500000, 2.6752500000],
                                    [2.6752500000, 2.6752500000, 0.8917500000]])
        self.latt_const = 3.567
        self.unit_cells = replicate[0]*replicate[1]*replicate[2]
        self.history_dict = dict()
        self.atoms = self.create()


    def create(self):
        all_atoms = np.zeros([self.unit_cells*8,3])
        unit_count = 0
        for x in range(self.replicate[0]):
            for y in range(self.replicate[1]):
                for z in range(self.replicate[2]):
             
                    shift = np.ones([8,3])
                    shift[:,0] *= x*self.latt_const
                    shift[:,1] *= y*self.latt_const
                    shift[:,2] *= z*self.latt_const
                 
                    all_atoms[unit_count*8:(unit_count+1)*8] += shift + self.unit_atom_coords
                    unit_count += 1
                    
        self.history_dict['create_replicate'] = self.replicate
        return all_atoms

    def minimise(self):
        
        current_dir = os.path.dirname(os.path.realpath(__file__))
        in_file = tools.file_proc(f'{current_dir}/LAMMPS_files/in.minimise_grain')

        for index, line in enumerate(in_file):
            line = line.split(' ')

            if line[0] == 'read_data':
                path = f'{self.dir}/data.initial_grain'
                line[1] = path
                sep = ' '
                in_file[index] = sep.join(line)
                break


        sep = '\n'
        in_file = sep.join(in_file)

        with open(f'{current_dir}/LAMMPS_files/in.minimise_grain', 'w') as fp: #rewriting edited input file
            fp.write(str(in_file)) 
    
        os.system(f'lmp_serial -in LAMMPS_files/in.minimise_grain')
        
        xyz_times = []
        for path in [tools.Path(path) for path in glob.glob(f'{current_dir}/*.xyz')]:
            try:
                xyz_times.append(int(path[-1][:-4]))
            except ValueError:
                pass
        
        minimised_file = f"{max(xyz_times)}.xyz"
      
        minimised_file = tools.file_proc(f"{current_dir}/{minimised_file}")
        number_of_atoms = None

        for i, line in enumerate(minimised_file):
            if line == 'ITEM: NUMBER OF ATOMS':
                number_of_atoms = int(minimised_file[i+1])
                atom_arr = np.zeros([number_of_atoms, 3])

            elif line == 'ITEM: ATOMS id type x y z':
                for j, coords in enumerate(minimised_file[i+1:-1]):
                    atom_arr[j] = np.array([float(x) for x in coords.split()[-3:]])
                   
                break
        
    
        self.minimised_atoms_arr = atom_arr

 
            









    def publish(self, path, name = 'data.initial_grain', atoms_arr = np.array([[None],[None]])):
        
        path = f"{path}{self.get_name()}"
        try:
            os.mkdir(f"{path}")
        except FileExistsError:
            pass

        self.dir = path


        if atoms_arr[0][0] == None:
            atoms_arr = self.atoms

        arr_with_index = np.ones([atoms_arr.shape[0], 4])
        arr_with_index[:,1:] = atoms_arr
        data_str = array_to_datafile(arr_with_index)

        with open(f'{path}/{name}', 'w') as fp:
            fp.write(data_str)


    def get_name(self):

        ref_rotates = []
        for i in range(10):
            try:
                ref_rotates.append(self.history_dict[f'rotate_{i}'])
                
            except KeyError:
                break
            
        additional_crystals = []
        for i in range(10):
            try:
                additional_crystals.append(self.history_dict[f'combine_{i}'])
            except KeyError:
                break

        x_rot, y_rot, z_rot = additional_crystals[0]['rotate_0']
        print(x_rot, y_rot, z_rot)
        if x_rot == 0 and y_rot == 0 and z_rot !=0:
            rot = f"tilt_{z_rot}"

        elif x_rot != 0 and y_rot == 0 and z_rot ==0:
            rot = f"twist_{x_rot}"

        else:
            rot =f"{x_rot}-{y_rot}-{z_rot}"


        name = f"{int(self.replicate[0])}-{int(self.replicate[1])}-{int(self.replicate[2])}"
        name += f"_100_{rot}"

        self.name = name
        return name


        

    def rotate(self, rotate_arr):
        rotation_mtrx = Rotate.general(rotate_arr) 

        for i, atom in enumerate(self.atoms):
            atom = atom.reshape(3,1)
            rotated_data = np.dot(rotation_mtrx, atom)
            rotated_data = rotated_data.reshape(1,3)
            self.atoms[i] = rotated_data

     
        for i in range(10):
            try:
                self.history_dict[f'rotate_{i}']
            except KeyError:
                self.history_dict[f'rotate_{i}'] = rotate_arr
                break



    def trim(self, limits):
        
        trimmed = np.zeros(self.atoms.shape)
        i = 0
        for atom in self.atoms:
            if limits['x'][0]*self.latt_const <= atom[0] < limits['x'][1]*self.latt_const:
                if limits['y'][0]*self.latt_const <= atom[1] < limits['y'][1]*self.latt_const:
                    if limits['z'][0]*self.latt_const <= atom[2] < limits['z'][1]*self.latt_const:
                        trimmed[i] = atom
                        i += 1

        self.atoms = trimmed[:i]
        self.replicate = np.array([abs(limits['x'][1] - limits['x'][0]),
                                   abs(limits['y'][1] - limits['y'][0]),
                                   abs(limits['z'][1] - limits['z'][0])]) 
        
        for i in range(10):
            try:
                self.history_dict[f'trim_{i}']
            except KeyError:
                self.history_dict[f'trim_{i}'] = limits
                break


    def shift(self, set = 'centre'):

        shift = np.ones(self.atoms.shape)

        if set == 'centre':
            shift[:,0] *= -self.replicate[0]*self.latt_const/2
            shift[:,1] *= -self.replicate[1]*self.latt_const/2
            shift[:,2] *= -self.replicate[2]*self.latt_const/2
            

        elif set == 'corner':
            shift[:,0] *= -min(self.atoms[:,0])
            shift[:,1] *= -min(self.atoms[:,1])
            shift[:,2] *= -min(self.atoms[:,2])

        elif set == 'ref_grain':
            shift[:,0] *= - 0.5 -max(self.atoms[:,0])
            shift[:,1] *= 0 
            shift[:,2] *= 0
        
        elif set == 'new_crystal':
            shift[:,0] *= 0.5 - min(self.atoms[:,0])
            shift[:,1] *= 0
            shift[:,2] *= 0
                
        self.atoms += shift 

        for i in range(10):
            try:
                self.history_dict[f'shift_{i}']
            except KeyError:
                self.history_dict[f'shift_{i}'] = shift[0]
                break



    def combine(self, crystal_2):

        self.shift('ref_grain')
     
        crystal_2.shift('new_crystal')
     
        new_arr = np.zeros([self.atoms.shape[0]+crystal_2.atoms.shape[0],3])

        new_arr[:self.atoms.shape[0]] = self.atoms
        new_arr[self.atoms.shape[0]:] = crystal_2.atoms

        self.atoms = new_arr
        self.replicate[0] += crystal_2.replicate[0]

        for i in range(10):
            try:
                self.history_dict[f'combine_{i}']
            except KeyError:
                self.history_dict[f'combine_{i}'] = crystal_2.history_dict
                break

    def plot_3d(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(self.atoms[:,0], self.atoms[:,1], self.atoms[:,2], alpha=0.1)      

        print(f"x: {min(self.atoms[:,0])} {max(self.atoms[:,0])}")
        print(f"y: {min(self.atoms[:,1])} {max(self.atoms[:,1])}")
        print(f"z: {min(self.atoms[:,2])} {max(self.atoms[:,2])}")  
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        ax.plot([0,0],[0,0],[-30,30])
        ax.plot([-30,30],[0,0],[0,0])
        ax.plot([0,0],[-30,30],[0,0])

        plt.show()

    def plot(self):
        plt.scatter(self.atoms[:,0], self.atoms[:,1])
        plt.xlabel('x')
        plt.ylabel('y')
        plt.show()
        plt.scatter(self.atoms[:,0], self.atoms[:,2])
        plt.xlabel('x')
        plt.ylabel('z')
        plt.show()
        plt.scatter(self.atoms[:,1], self.atoms[:,2])
        plt.xlabel('y')
        plt.ylabel('z')
        plt.show()

    def clean_up(self):

        tools.make_dir(f"{self.dir}/xyz_files")
        os.system(f" mv *.xyz {self.dir}/xyz_files/ ")
        os.system(f"mv log.lammps {self.dir}/ ")
            


def main(args_dict):

    target_replicate = [16,16,16]
    target_replicate = args_dict['replicate']
    rotation = [54.75,0,45]
    rotation = args_dict['rotation']
    corner_to_corner = np.sqrt((target_replicate[0]/2)**2 + target_replicate[1]**2+ target_replicate[2]**2)
    replicate = [int(corner_to_corner)+1 for i in range(3)]

    trim = [[-replicate/2,replicate/2] for replicate in target_replicate]
    trim[0] = [trim[0][0]/2, trim[0][1]/2]

    ref_crystal = Crystal(replicate=replicate)
    ref_crystal.shift('centre')
    ref_crystal.trim(dict(x = trim[0],y = trim[1],z = trim[2]))

    crystal_2 = Crystal(replicate=replicate)
    crystal_2.shift('centre')
    crystal_2.rotate(rotation)
    crystal_2.trim(dict(x = trim[0],y = trim[1],z = trim[2]))
    crystal_2.shift('new_crystal')
    ref_crystal.combine(crystal_2=crystal_2)
    ref_crystal.shift('corner')

    ref_crystal.get_name()

    ref_crystal.publish(f"{os.path.dirname(os.path.realpath(__file__))}/data_files/")
    
    ref_crystal.minimise()

    ref_crystal.publish(f"{os.path.dirname(os.path.realpath(__file__))}/data_files/", 
                        f'data.{ref_crystal.get_name()}_min', atoms_arr=ref_crystal.minimised_atoms_arr)

    ref_crystal.clean_up()


if __name__ == "__main__":


    accepted_args = ['replicate', 'type','rotation']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')

    
    try: 
        args_dict['rotation']
    except KeyError:
        print("\n\nERROR: cannot accept rotation argument, please input as:")
        print('\n\t\t-type other -rotation [45,45,45]\n')
        print('\t\t-type tilt -rotation 45\n')
        print('for example.')
    
    try:
        args_dict['replicate'] = tools.str_to_list(args_dict['replicate'], float_vals = True)
    except TypeError:
        print("\n\nERROR: cannot accept replicate argument, please input as:")
        print('\n\t\t-replicate [5,5,5]\n')
        print('for example.')

    if args_dict['type'] not in ['tilt', 'twist', 'other']:
        print("\n\nERROR: cannot accept type argument, accepted arguments are 'tilt' 'twist' or 'other'."
              "\nPlease input as:")
        print('\n\t\t-type tilt\n')
        print('for example.\n\n')

        raise ValueError('See above description of error.')

    
    if args_dict['type'] =='other':
        try:
            args_dict['rotation'] = tools.str_to_list(args_dict['rotation'], float_vals = True)
        except TypeError:
            print("\n\nERROR: cannot accept rotation argument, for type = other, please input as:")
            print('\n\t\t-rotation [45,45,45]\n')
            print('for example.')

    else:
        try:
            if args_dict['type'] =='tilt':
                args_dict['rotation'] = [0,0,float(args_dict['rotation'])]
            
            elif args_dict['type'] =='twist':
                args_dict['rotation'] = [float(args_dict['rotation']),0, 0]

        except ValueError:
            print("\n\nERROR: cannot accept rotation argument, for type = tilt or twist, please input as:")
            print('\n\t\t-rotation 45\n')
            print('for example.')
            print("This will perform the rotation about the axis needed to achieve desired tilt or twist rotation.")
            print("To input a custom rotation, please use -type other.")








    main(args_dict)

