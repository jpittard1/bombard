



import os
import sys
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
            print(new_line)
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
                line[-1] = str(-shift +0.5)
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


    

def main(desired_replicate, rotation_deg):

    desired_final_size = [6,6,8]

    desired_replicate = [desired_final_size[1],desired_final_size[2],int(desired_final_size[0]/2)]
    desired_replicate = [desired_final_size[1],int(desired_final_size[0]/2), desired_final_size[2]]

    block_size_dict, limits_list = box_checker.main(desired_replicate, rotation_deg)

    create_xyz(block_size_dict)

    data_file_name = dfm.main(desired_replicate, rotation_deg, limits_list)

    shift = abs(limits_list[2][0] - limits_list[2][1])
    create_grain(data_file_name, shift, desired_replicate)

    data_file_name = dfm.main([0,0,0], [0,0,0])
   

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