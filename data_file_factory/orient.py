

import sys
import os
import pprint
import math
import glob
import numpy as np
from rotate import Rotate
import box_checker as bc
import data_file_maker as dfm
import grain_maker as gm

current_dir = os.path.dirname(os.path.realpath(__file__)).split('/')
sep = '/'
path = sep.join(current_dir[:-1])
print(path)
sys.path.append(path)
import tools


def rotation_calc(miller_plane_str):
    """Calculates rotations required for desired orientation. Consider as two rotations,
    one about x then one about y. First rotation is simple, but second rotation requires 
    consideration of where the plane intercepts the z axis AFTER the initial rotation 
    abour x. No rotation requied in z as this is simply spinning the incident plane."""

    miller_plane_list = [int(i) for i in list(miller_plane_str)]

    recip_list = []
    for indice in miller_plane_list:
        try:
            recip_list.append(1/indice)
        except ZeroDivisionError:
            recip_list.append(1e30)


    x_rotation = math.atan(recip_list[2]/recip_list[1])
    y_rotation = np.pi/2 - math.atan(recip_list[0]/(recip_list[1]*math.sin(x_rotation)))
    z_rotation = 0 #no rotation for incident axis, might have messy edges?


    return np.array([x_rotation,-y_rotation,z_rotation])*180/np.pi




def fit_check(file_name, replicate):
    '''Performs simple comparision of number of atoms in the final trimmed xyz file to
    the number of expected atoms from the desired replicate. Checks for zerolines in xyz_array.
    IF the initial big_block_replicate is too small, then low percentages will be given.'''
    
    current_dir = tools.bombard_directory()
    xyz_arr = tools.xyz_to_array(f'{current_dir}/data_file_factory/{file_name}', line_length=4)

    atom_perc = xyz_arr.shape[0]*100/(8*replicate[0]*replicate[1]*replicate[2])
    
    zero_lines = [1 for line in xyz_arr if line[1] == 0 and line[2] == 2 and line[3] == 0 or line[0] == 0]
    print(f"\n\n{len(zero_lines)} zero lines found.")
    if atom_perc < 90:
        print(f"WARNING: Only {atom_perc:.3g}% of expected atoms where found.")
        print(f"The 'big_block_replicate' may be too small.")
    
    else:
        print(f"{atom_perc:.3g}% ({xyz_arr.shape[0]} out of {int(8*replicate[0]*replicate[1]*replicate[2])} atoms) ",
                "for atoms expected were in the final xyz file.\n\n")
     


    
def lammps_trim(data_file_name):
    """Performs a short lammps simulation with final BCs in all dimensions, this is 
    to remove excess atoms as a result of imperfect limts/rotations."""
    
    current_dir = os.path.dirname(os.path.realpath(__file__))
    in_file = tools.file_proc(f'{current_dir}/LAMMPS_files/in.trim')

    for index, line in enumerate(in_file):
        line = line.split(' ')

        if line[0] == 'read_data':
            path = f'{current_dir}/data.{data_file_name}_1'
            line[1] = path
            sep = ' '
            in_file[index] = sep.join(line)
            break
 
    sep = '\n'
    in_file = sep.join(in_file)

    with open(f'{current_dir}/LAMMPS_files/in.trim', 'w') as fp: #rewriting edited input file
        fp.write(str(in_file)) 

    os.system('lmp_serial -in LAMMPS_files/in.trim')

    full_path = glob.glob(f'{current_dir}/*.xyz')

    xyz_files = [path.split('/')[-1] for path in full_path]
    xyz_files.sort()

    for file in xyz_files:
        try:
            last_file = f"{int(file[:-4])}.xyz"
        except ValueError:
            break

    return last_file


def atom_number_finder(target_atoms):
    '''Used to deal with variabilities with atoms after rotations. After the inititial rotation and trim, a run 
    is done with final BCs (using lammps_trim()), number of atoms gradually decreases during this time. This function
    checks the number of atoms in each xyz file outputting during lammps_trim(), then finds the xyz file closest to
    the desired number of atoms. If multiple files are closest, the last file is taken. Returns name of xyz file
    to be taken forward to next step in data file creation.'''


    bombard_dir = tools.bombard_directory()
    xyz_file_paths = glob.glob(f"{bombard_dir}/data_file_factory/*0.xyz")

    number_of_atoms_dict = dict()
    for xyz_file_path in xyz_file_paths:

        xyz_file = tools.file_proc(xyz_file_path)

        timestep = xyz_file_path.split('/')[-1][:-4]

        number_of_atoms_dict[timestep] = int(xyz_file[3])

    pprint.pprint(number_of_atoms_dict)

    atom_numbers = [val for val in number_of_atoms_dict.values()]
    closest_to = tools.closest_to(target_atoms,atom_numbers)

    valid_timesteps = [int(timestep) for timestep in number_of_atoms_dict.keys() if number_of_atoms_dict[timestep] == closest_to]

    print(f'\nUsing {max(valid_timesteps)}.xyz')
    return f"{max(valid_timesteps)}.xyz"




def main(user_input_dict):

    
    #Calculating required rotation for inputted miller indices.
    rotation_deg = rotation_calc(user_input_dict['orientation'])
   
    #Creating large block to rotate and trim into desired shape/oreintation.
    big_block_replicate = dict(x = 25, y = 25, z = 25)
    gm.create_xyz(big_block_replicate)


    #Rotating the large diamond block previously created and centering. Must be done in two
    #steps as limits are applied before the shift, and needs to be centered before limits can
    #be applied.
    data_file_name = dfm.main('0.xyz', user_input_dict['size'], rotation_deg, shift='centre', 
                            xyz_file_name='big_rotated')
   
    #Calculating limtits wrt the origin. 
    xmin, ymin, zmin = [-user_input_dict['size'][i]*3.567/2 for i in range(3)]
    xmax, ymax, zmax = [user_input_dict['size'][i]*3.567/2 for i in range(3)]

    extra = 0
    limits = [[xmin + extra,xmax - extra],[ymin + extra ,ymax-extra],[zmin,zmax]]
    

    #Trimming down to the desired size.
    data_file_name = dfm.main('big_rotated_1.xyz', user_input_dict['size'], rotation_deg = [0,0,0], 
                            limits=limits, shift='origin', xyz_file_name='trimmed_rotated',
                            box_limits = [[0,3.567*8],[0,3.567*8],[None,None]])

    space = '-'
    size_str = space.join([str(int(i)) for i in user_inputs_dict['size']])
    nothing = ''
    orientation_str = nothing.join([str(int(i)) for i in user_inputs_dict['orientation']])
    dir_name = f"{orientation_str}_{size_str}"

    last_file = lammps_trim(data_file_name)

    target_no_atoms = np.prod(user_input_dict['size'])*8
    target_xyz = atom_number_finder(target_no_atoms)


    data_file_name = dfm.main(target_xyz, [0,0,0], [0,0,0], xyz_file_name=f'final_trim_{dir_name}', 
                            data_file_name = f'final_trim_{dir_name}', extra_xy=[0,0],
                            box_limits = [[0,3.567*8],[0,3.567*8],[None,None]])

    bombard_dir = tools.bombard_directory()
    os.system(f"rm -r {bombard_dir}/data_file_factory/*0.xyz")

    #checking number of atoms in final xyz_file
    fit_check('trimmed_rotated_1.xyz', user_input_dict['size'])



    last_file = gm.minimise_grain(data_file_name)
    
    data_file_name = dfm.main(last_file, [0,0,0], [0,0,0], xyz_file_name=f'min_{dir_name}', 
                            data_file_name = f'min_{dir_name}', extra_xy=[0,0],
                            box_limits = [[0,3.567*8],[0,3.567*8],[None,None]])
    
    fit_check(f'min_{dir_name}_1.xyz', user_input_dict['size'])

    os.system(f"rm -r data_files/{dir_name} ")
    os.system(f"mkdir xyz_files")
    os.system(f"mv *xyz xyz_files/")
    os.system(f"mkdir {dir_name}")
    os.system(f"mv data.* {dir_name}")
    os.system(f"mv xyz_files/ {dir_name}")
    os.system(f"mv log.lammps {dir_name}")
    os.system(f"mv {dir_name} data_files/{dir_name}")
    





if __name__ == '__main__':

    fail = False

    user_inputs_dict = dict(orientation = '111',
                            size = '[8,8,10]')      

    try:
        x = sys.argv[1]
    except IndexError:
        print("\nNOTE: No arguments provided, defaults will be used.")
        print("\nDefault arguments: ")
        pprint.pprint(user_inputs_dict)

    if fail == False:
        for arg in sys.argv[1:]:
            
            arg = arg.split('-')

            if len(arg) == 1:
                print("\nERROR: Input arguments as: frames-4 etc.\n")
                fail = True
                break
            
            try:
                x = user_inputs_dict[arg[0]]
            except KeyError:
                print(f"\nERROR: {arg[0]} is an invalid arguments.")
                print("\nDefault arguments: ")
                pprint.pprint(user_inputs_dict)
                fail = True
                break
            
            
            if arg[0] == 'orientation':

                try:
                    miller_indices =[int(i) for i in arg[1]]

                    if len(miller_indices)>3:
                        int('error')
                    
                    user_inputs_dict['orientation'] = arg[1]

                except TypeError and ValueError:
                    print(f"\nERROR: {arg[0]}:{arg[1]} is an invalid argument.")
                    print("\nDefault arguments: ")
                    pprint.pprint(user_inputs_dict)
                    fail = True
                    break

            if arg[0] == 'size':

                try:
                    size = tools.str_to_list(arg[1], float_vals=True)
                    if len(size)>3:
                        int('error')

                    user_inputs_dict['size'] = arg[1]

                except TypeError and ValueError:
                    print(f"\nERROR: {arg[0]}:{arg[1]} is an invalid argument.")
                    print("\nDefault arguments: ")
                    pprint.pprint(user_inputs_dict)
                    fail = True
                    break


                    

        if fail == False:

            user_inputs_dict['orientation'] =[int(i) for i in user_inputs_dict['orientation']]
            user_inputs_dict['size'] = tools.str_to_list(user_inputs_dict['size'], float_vals=True)

            print(user_inputs_dict)
            main(user_inputs_dict)
            
            print(f"A {user_inputs_dict['size']} block of {user_inputs_dict['orientation']} diamond has been made.\n")

    


