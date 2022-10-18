

import os
import pprint
import sys
import numpy as np
from data_file_factory.rotate import Rotate, Shift
import matplotlib.pyplot as plt

#take inputs for file and trimming dimensions


def array_to_datafile(array, file_name = None, path = None):

    counter = 0
    atom_str = ''
    for i in range(0,array.shape[0]):
        counter += 1
        atom_str += f'{counter} {int(array[i][0])} {array[i][1]:.4f} {array[i][2]:.4f} {array[i][3]:.4f}\n'

    output_str = 'LAMMPS data file from restart file: timestep = 1, procs = 1\n\n'
    output_str += f'{counter} atoms\n\n'
    output_str += '3 atom types\n\n'
    output_str += f"{min(array[:,1])*1.01:.4f} {max(array[:,1])*1.01:.4f} xlo xhi\n"
    output_str += f"{min(array[:,2])*1.01:.4f} {max(array[:,2])*1.01:.4f} ylo yhi\n"
    #output_str += f"-5 71.34 zlo zhi\n\n"

    zlo = -50
    zhi = 71.34
    if max(array[:,3]) > 71.34:
        zhi = max(array[:,3])*1.5 
    if min(array[:,3]) < -50:
        zlo = min(array[:,3])*1.5 
  
    output_str += f"{zlo} {zhi} zlo zhi\n\n"
    output_str += 'Masses\n\n1 12.01\n2 2\n3 3\n\n'
    output_str += 'Atoms\n\n'
    output_str += atom_str


    return output_str


def array_to_xyzfile(array, file_name = None, path = None):
    
    counter = 0
    atom_str = ''
    for i in range(0,array.shape[0]):
        counter += 1
        atom_str += f'{int(array[i][-4])} {array[i][-3]:.4f} {array[i][-2]:.4f} {array[i][-1]:.4f}\n'

    output_str = f'{counter}\n'
    output_str += 'Atoms. Timestep. 0.0\n'
    output_str += atom_str

    return output_str
        
        

def save_str(string, path, file_name, replace = False, xyz = False):

    count = 1

    while True:
        if xyz == False:
            new_file_name = f"{path}/{file_name}_{count}"
        else:
            new_file_name = f"{path}/{file_name}_{count}.xyz"

        if replace == False:
            try:
                open(new_file_name, 'r')
                count += 1
            except FileNotFoundError:
                break

        if replace == True:
            break

    with open(new_file_name, 'w') as fp:
        fp.write(string)

  

def trim(array, limits):

    output = np.zeros([array.shape[0],4])
    count = 0
    for line in array:

        if line[-1] > limits[-1][0] and line[-1] < limits[-1][1]: #z
            if line[-2] > limits[-2][0] and line[-2] < limits[-2][1]: #y
                if line[-3] > limits[-3][0] and line[-3] < limits[-3][1]: #x

                    output[count][:] = line
                    count +=1


    to_delete = []
    for i, line in enumerate(output):
        try:
            if float(line[0]) == 0:
                to_delete.append(i)

        except ValueError:
            pass

    output = np.delete(output, to_delete, 0)

    return output





#zlims = 3.567*7

def xyz_to_array(xyz_file, limits = [[-1000,1000],[-1000,1000],[-1000,1000]], shift = None, rotate = [0, 0, 0], atom_types = [1,2,3]):

    xyz_file = xyz_file.split("\n")


    for index, line in enumerate(xyz_file):
        line = line.split(' ')
        try:
            float(line[0])
            if len(line) >= 3:
                start_line = index
                break
        except ValueError:
            pass


    data_array = np.zeros([int(xyz_file[3]), 4])
    counter = 0
    for i, line in enumerate(xyz_file[start_line:]):
        line = line.split(' ')
        
        try:
            line = [float(item) for item in line]

            if line[-4] in atom_types:
                               
                rotated_data = Rotate.about_x(np.array(line[-3:]), rotate[0], round_dp = 4)
        
                rotated_data = Rotate.about_y(np.array(rotated_data), rotate[1], round_dp = 4)
                
                rotated_data = Rotate.about_z(np.array(rotated_data), rotate[2], round_dp = 4)
                
                if rotated_data[-1] > limits[-1][0] and rotated_data[-1] < limits[-1][1]: #z
                    if rotated_data[-2] > limits[-2][0] and rotated_data[-2] < limits[-2][1]: #y
                        if rotated_data[-3] > limits[-3][0] and rotated_data[-3] < limits[-3][1]: #x
                            data_array[i][:] = [line[-4]] + list(rotated_data)
                        
                        

        except ValueError:
            pass

    to_delete = []
    for i, line in enumerate(data_array):
        try:
            if float(line[0]) == 0:
                to_delete.append(i)

        except ValueError:
            pass

    data_array = np.delete(data_array, to_delete, 0)

    if shift == 'center':
        data_array = Shift.centre(data_array, round_dp = 4)
    if shift == 'origin':
        data_array = Shift.origin(data_array, round_dp = 4)

    return data_array

def remove_h(xyz_file, to_save_path, name):

    data_array = xyz_to_array(xyz_file, atom_types=[1])
    data_file = array_to_datafile(data_array)
    xyz_file = array_to_xyzfile(data_array)
    save_str(data_file, to_save_path, name, replace = True)
    save_str(xyz_file, to_save_path, name, replace = True, xyz = True)


def main(xyz_name, desired_replicate, rotation_deg, limits = [[-1000,1000],[-1000,1000],[-1000,1000]], 
        xyz_file_name = 'rotated_diamond', data_file_name = None):

    current_dir = os.path.dirname(os.path.realpath(__file__))
    xyz_file = open(f"{current_dir}/{xyz_name}", 'r')
    xyz_file = xyz_file.read()

    data_array = xyz_to_array(xyz_file, shift = 'origin', rotate=rotation_deg, limits=limits)

    data_file = array_to_datafile(data_array)
    xyz_file = array_to_xyzfile(data_array, current_dir)

    if data_file_name == None:
        replicate_list = [str(int(i)) for i in desired_replicate]
        sep = '_'
        data_file_name = sep.join(replicate_list)
        data_file_name += f'_{int(rotation_deg[2])}deg'

    save_str(data_file, current_dir, f"data.{data_file_name}", replace = True)
    save_str(xyz_file, current_dir, xyz_file_name, replace = True, xyz=True)

    return data_file_name
  
    '''
    xyz_file_name = sys.argv[0]
    xyz_file_name = 'old_grain/2000.xyz'
    rotate = [0,90,0]
    limits = [[-1000,1000], [-1000, 19.9752], [4.05816, 24.969]]


    xyz_file_name = sys.argv[0]
    xyz_file_name = 'grainmin2/10000.xyz'
    rotate = [0,0,0]
    limits = [[-1000,1000], [-1000, 1000], [-1000, 1000]]

    data_array = xyz_to_array(xyz_file_name, limits = limits, recentre=False, rotate=rotate)
    data_array = trim(data_array, [[-5,1000],[1,1000],[-25,1]])
    data_array = Shift.origin(data_array)

    xs = np.linspace(0, data_array.shape[0], data_array.shape[0])


    plt.scatter(data_array[:,1], data_array[:,2])
    plt.title("xy plane")
    plt.axis('square')
    plt.show()

    plt.scatter(data_array[:,1], data_array[:,3])
    plt.title("xz plane")
    plt.axis('square')
    plt.show()


    xyz_file_name = sys.argv[0]
    xyz_file_name = 'LAMMPS_files/minimied/12000.xyz'

    data_array = xyz_to_array(xyz_file_name, recentre=False)
    data_array = Shift.origin(data_array)

    plt.scatter(data_array[:,1], data_array[:,2])
    plt.title("xy plane")
    plt.axis('square')
    plt.show()

    plt.scatter(data_array[:,1], data_array[:,3])
    plt.title("xz plane")
    plt.axis('square')
    plt.show()

    data_file = array_to_datafile(data_array)
    xyz_file = array_to_xyzfile(data_array)
    save_str(xyz_file, current_dir, 'grain', replace = False, xyz = True)
    '''









if __name__ == '__main__':


    main()


