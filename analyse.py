
"""
Replacement for lint.py. Needs to function for both repeated single measurements and larger single simulations.
Main jobs/considerations:
    - create and move files to xyz_files
    - have some way of running multiple analysis
    - incorporate jmol_all?
    - check for .xyz files
    - takes path as command line argument
"""

import sys
import tools
import jmol_convert
import glob
import os
from tqdm import tqdm
import shutil




def main(args_dict):
    '''
    Creates all.xyz
    Moves .xyz files to xyz_files/
    Runs jmol_convert.py
    Works for repeats or singles
    '''

    bombard_dir = tools.bombard_directory()

    if args_dict['repeats'] == None:
        args_dict['repeats'] = tools.repeat_check(f"{bombard_dir}{args_dict['path']}")
        print(args_dict['repeats'])
    else:
        args_dict['repeats'] = tools.str_to_bool(args_dict['repeats'])

    if args_dict['hpc'] == None:
        args_dict['hpc'] == False
    else:
        args_dict['hpc'] = tools.str_to_bool(args_dict['hpc'])

    args_dict['path'] = tools.Path(args_dict['path'])

    if args_dict['repeats'] == True:
        repeat_dirs_path = glob.glob(f"{bombard_dir}{args_dict['path']}/*r")
        repeat_dirs_path = [tools.Path(path) for path in repeat_dirs_path]
    else:
        repeat_dirs_path = [tools.Path(args_dict['path'])]


    if args_dict['hpc'] == True:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        cores = comm.Get_size()

        print(type(rank))
        print(cores)

        chunk_size = int(len(repeat_dirs_path)/cores)
        remainder = len(repeat_dirs_path)%cores

        print(chunk_size)
        print(remainder)

        selection = repeat_dirs_path[rank*chunk_size:(rank+1)*chunk_size]

        if rank + 1 == cores:
            selection += repeat_dirs_path[(rank+1)*chunk_size:(rank+1)*chunk_size+remainder]

        print(f"I'm rank {rank}, and I have {len(selection)} dirs")

        repeat_dirs_path = selection


   
    ### Creating xyz_file folder, moving .xyz files, creating all.xyz ###

    for path in tqdm(repeat_dirs_path, desc=f"Running Analysis of {args_dict['path'][-1]}"):

        if tools.path_check(f"{path}/0.dsp") == True:

            dsp_file_paths = glob.glob(f"{path}/*.dsp")

            
            dsp_file_paths = [tools.Path(path) for path in dsp_file_paths]

            try:
                os.mkdir(f"{path}dsp_files/")
            except FileExistsError:
                pass
        
            dsp_time_steps = [int(file_path[-1][:-4]) for file_path in dsp_file_paths if file_path[-1] != 'final.dsp']
            
            #os.system(f"mv {bombard_dir}/{path}/{int(max(dsp_time_steps))}.dsp {bombard_dir}/{path}/final.dsp")
            shutil.move(f"{path}{int(max(dsp_time_steps))}.dsp", f"{path}final.dsp")
            
    
            for file_path in dsp_file_paths:
                try:
                    shutil.move(f"{file_path}", f"{path}dsp_files/") 
                except FileNotFoundError:
                    pass
            

        elif tools.path_check(f"{path}/final.dsp") == False and tools.path_check(f"{path}/dsp_files/0.dsp") == True:
            dsp_file_paths = glob.glob(f"{path}/dsp_files/*.dsp")
            dsp_file_paths = [tools.Path(path) for path in dsp_file_paths]
            dsp_time_steps = [int(file_path[-1][:-4]) for file_path in dsp_file_paths if file_path[-1] != 'final.dsp']
            shutil.move(f"{path}dsp_files/{int(max(dsp_time_steps))}.dsp", f"{path}final.dsp")


        if tools.path_check(f"{path}/0.xyz") == True:

            xyz_file_paths = glob.glob(f"{path}/*.xyz")
            xyz_file_paths = [tools.Path(path) for path in xyz_file_paths]
    
            time_steps = [int(file_path[-1][:-4]) for file_path in xyz_file_paths]
            time_steps.sort()

            tools.make_dir( f"{path}xyz_files")
            os.system(f"mv {path}*.xyz {path}xyz_files/")

            all_xyz = ''
            for time_step in time_steps:

                next_file = open(f"{path}xyz_files/{time_step}.xyz")
                all_xyz += next_file.read()
                all_xyz += '\n'

                with open (f"{path}/all.xyz", 'w') as fp: 
                    fp.write(all_xyz) 

            
            jmol_convert.main(f"{path}all.xyz")


    print('Analysis complete.')
    



if __name__ == "__main__":

    accepted_args = ['repeats', 'path', 'hpc']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accecpted_args=accepted_args)   
    except IndexError or KeyError:
        print('\n\nERROR: Please give inputs.\n\n')
        print('Valid inputs: -path -repeats (boolean)')

    main(args_dict)


    