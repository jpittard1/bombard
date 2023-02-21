



import os
import sys
import glob
import box_checker
import data_file_maker as dfm

current_dir = os.path.dirname(os.path.realpath(__file__)).split('/')
sep = '/'
path = sep.join(current_dir[:-1])
print(path)
sys.path.append(path)
import tools




def create_xyz(block_size_dict):

    current_dir = os.path.dirname(os.path.realpath(__file__))
    in_file = tools.file_proc(f'{current_dir}/LAMMPS_files/in.big_diamond')
   
    for index, line in enumerate(in_file):
        line = line.split(' ')
        if line[0] == 'replicate':
            new_line = ['replicate', int(block_size_dict['x']), int(block_size_dict['y']), int(block_size_dict['z'])]
            new_line = [str(i) for i in new_line]
            sep = ' '
            in_file[index] = sep.join(new_line)
            break

    sep = '\n'
    in_file = sep.join(in_file)

    with open(f'{current_dir}/LAMMPS_files/in.big_diamond', 'w') as fp: #rewriting edited input file
        fp.write(str(in_file)) 

    os.system('lmp_serial -in LAMMPS_files/in.big_diamond')


def create_grain(rotated_data_file_name, shift, replicate):

    current_dir = os.path.dirname(os.path.realpath(__file__))
    in_file = tools.file_proc(f'{current_dir}/LAMMPS_files/in.create_grain')

    for index, line in enumerate(in_file):
        line = line.split(' ')
        if line[0] == 'replicate':
            new_line = ['replicate'] + replicate
            new_line = [str(i) for i in new_line]
            sep = ' '
            in_file[index] = sep.join(new_line)

        try:
            if line[0] == 'read_data' and line[2] == 'add':
                path = f'{current_dir}/data.{rotated_data_file_name}_1'
                line[1] = path
                line[-2] = str(-shift -0.5)
                sep = ' '
                in_file[index] = sep.join(line)
                break
        except IndexError:
            pass
            

    sep = '\n'
    in_file = sep.join(in_file)

    with open(f'{current_dir}/LAMMPS_files/in.create_grain', 'w') as fp: #rewriting edited input file
        fp.write(str(in_file)) 

    os.system('lmp_serial -in LAMMPS_files/in.create_grain')




def minimise_grain(data_file_name):

    current_dir = os.path.dirname(os.path.realpath(__file__))
    in_file = tools.file_proc(f'{current_dir}/LAMMPS_files/in.minimise_grain')

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

    with open(f'{current_dir}/LAMMPS_files/in.minimise_grain', 'w') as fp: #rewriting edited input file
        fp.write(str(in_file)) 

    os.system('lmp_serial -in LAMMPS_files/in.minimise_grain')

    full_path = glob.glob(f'{current_dir}/*.xyz')

    xyz_files = [path.split('/')[-1] for path in full_path]
    xyz_files.sort()

    for file in xyz_files:
        try:
            last_file = f"{int(file[:-4])}.xyz"
        except ValueError:
            break

    return last_file

    

def main(desired_final_size, rotation_deg):

    desired_replicate = [int(desired_final_size[1]),int(desired_final_size[0]/2), int(desired_final_size[2])]

    block_size_dict, limits_list = box_checker.main(desired_replicate, rotation_deg)
    block_size_dict = dict(x = 30, y = 30, z = 30)
    create_xyz(block_size_dict)

    data_file_name = dfm.main('0.xyz', desired_replicate, rotation_deg, limits_list, 
                                shift = 'origin', xyz_file_name='rotated_diamond')

    shift = abs(limits_list[1][0] - limits_list[1][1])
    create_grain(data_file_name, shift, desired_replicate)

    data_file_name = dfm.main('0.xyz',[0,0,0], [0,0,0], xyz_file_name='grain', data_file_name = f'grain_{int(rotation[2])}deg')

    last_file = minimise_grain(data_file_name)

    data_file_name = dfm.main(last_file, [0,0,0], [0,0,0], xyz_file_name='min_grain', data_file_name = f'min_grain_{int(rotation[2])}deg')

    dir_name = f'{desired_replicate[0]}_{desired_replicate[1]*2}_{desired_replicate[2]}_{int(rotation[2])}'
    
    os.system(f"rm -r data_files/{dir_name}deg ")
    os.system(f"mkdir xyz_files")
    os.system(f"mv *xyz xyz_files/")
    os.system(f"mkdir {dir_name}deg")
    os.system(f"mv data.* {dir_name}deg")
    os.system(f"mv xyz_files/ {dir_name}deg")
    os.system(f"mv log.lammps {dir_name}deg")
    os.system(f"mv {dir_name}deg data_files/{dir_name}deg")
    
    
if __name__ == '__main__':
    success = False
    try:
        desired_replicate = tools.str_to_list(sys.argv[1], float_vals = True)
        rotation = tools.str_to_list(sys.argv[2], float_vals = True)
        success = True
    except IndexError:
        print('\nERROR: Please give values for desired replicate and rotation:')
        print('eg: python box_checker.py [6,6,8] [0,0,30]')
        print('For a [6,6,8] size crystal rotated 30degs about the z axis.')
        
    if success == True:    
        main(desired_replicate, rotation)