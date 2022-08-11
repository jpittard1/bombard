


import sys
import os
import tools
import random
import job_tracker

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f"{current_dir}/data_file_factory")
import data_file_maker as dfm




def generate_data_file(path):

    #os.system(f'cp {path}/final.xyz {current_dir}/data_file_factory/')    
    
    xyz_file = open(f"{path}/final.xyz", 'r')
    xyz_file = xyz_file.read()
    final_arr = dfm.xyz_to_array(xyz_file)
    out_str = dfm.array_to_datafile(final_arr)
    dfm.save_str(out_str, f'{path}/bake', 'data.final', replace = True)
    os.system(f'mv {path}/bake/data.final_1 {path}/bake/data.final')  




    #os.system(f'mv {current_dir}/data_file_factory/data.6_6_8_0deg_1 {path}/data.final')

def edit_input(path, temp):

    input_file = tools.file_proc(f"{path}/bake/in.bake")

    for index, line in enumerate(input_file):
        line = line.split()

        if len(line)> 0:
            if line[0] == 'read_data':
                line[-1] = f"{path}/bake/data.final"

            elif line[0] == 'pair_coeff':
                line[-4] = f"{current_dir}/LAMMPS_files/CH.rebo"

            elif line[0] == 'velocity':
                line[3] = str(temp)
                line[4] = str(random.randint(10000,99999))

            elif line[0] == 'fix':
                line[-2] = str(temp)
                line[-3] = str(temp)
            
        sep = ' '
        input_file[index] = sep.join(line)

    sep = '\n'
    input_file = sep.join(input_file)

    with open(f"{path}/bake/in.bake", 'w') as fp: #rewriting edited input file
        fp.write(str(input_file))     


def bake_until_ready(path, hpc = False):
    current_dir = os.path.dirname(os.path.realpath(__file__))

    try:
        os.mkdir(f'{path}/bake')
    except FileExistsError:
        pass
    
    generate_data_file(path)

    os.system(f'mv {path}/data.final {path}/bake')
    os.system(f'cp {current_dir}/LAMMPS_files/in.bake {path}/bake')
    os.system(f'cp {path}/settings.csv {path}/bake')
    os.system(f'cp {path}/data.graphite_sheet {path}/bake')

    edit_input(path, 1000)

    if hpc == False:
        os.chdir(f"{path}/bake")
        os.system(f"lmp_serial -in in.bake ")
        os.chdir(current_dir)
    elif hpc == True:  
        os.system(f"cp LAMMPS_files/srun_bake {path}/bake/srun_bake") #copying srun avoids rewritting
        os.chdir(f"{path}/bake")
        os.system(f"sbatch {path}/bake/srun_bake")

def check_if_cooked(path):

    path_ending = path.split('results/')[-1]
    os.system(f'python lint.py False {path_ending}/bake')
    os.system(f'python jmol_convert.py {path_ending}/bake')
    #os.system(f'python cleanup.py {path}/bake')
    os.system(f'python depth_02.py {path_ending}/bake')
    os.system(f'python saturate.py {path_ending}/bake')



def main():

    current_dir = os.path.dirname(os.path.realpath(__file__))
    path = f'{current_dir}/results/testing/control/t_0g_30eV_1000_1'

    terminal = True
    hpc = True
    try:
        sys.argv[1]
    except IndexError:
        terminal = False

    if terminal == True:
        path = f'{current_dir}/results/{sys.argv[1]}'
        if sys.argv[1] == '-help' or sys.argv[2] == '-help':
            print('\nPlease select target file followed by to "-bake" to run bake out simulation, or "-analyse" to analyse results from this.\n' )
        elif sys.argv[2] == '-bake':
            bake_until_ready(path, hpc = hpc)

            if hpc == True:
                folder_name = f"{path.split('/')[-1]}/bake"
                job_tracker.Track(folder_name, 'srun_bake')
                print("\n\nPROGRESS: jobs.txt updated.")

        elif sys.argv[2] == '-analyse':
            check_if_cooked(path)


    else:
        bake_until_ready(path, hpc = hpc)
        check_if_cooked(path)



if __name__ == '__main__':
    main()