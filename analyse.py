
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

def path_check(path):

    try:
        open(path)
        return True
    except FileNotFoundError:
        return False


def main(args_dict):
    '''
    Creates all.xyz
    Moves .xyz files to xyz_files/
    Runs jmol_convert.py
    Works for repeats or singles
    '''

    bombard_dir = tools.bombard_directory()

    if args_dict['repeats'] == None:
        args_dict['repeats'] = tools.repeat_check(args_dict['path'])
    else:
        args_dict['repeats'] = tools.str_to_bool(args_dict['repeats'])

    args_dict['path'] = tools.Path(args_dict['path'])

    if args_dict['repeats'] == True:
        repeat_dirs_path = glob.glob(f"{args_dict['path']}/*")
        repeat_dirs_path = [tools.Path(path) for path in repeat_dirs_path]
    else:
        repeat_dirs_path = [tools.Path(args_dict['path'])]
        

    ### Creating xyz_file folder, moving .xyz files, creating all.xyz ###

    for path in tqdm(repeat_dirs_path, desc=f"Running Analysis on {args_dict['path'][-1]}...", ascii= False, ncols=100):

        if path_check(f"{path}/0.dsp") == True:

            dsp_file_paths = glob.glob(f"{path}/*.dsp")
            
            dsp_file_paths = [tools.Path(path) for path in dsp_file_paths]

            try:
                os.mkdir(f"{bombard_dir}/{path}/dsp_files")
            except FileExistsError:
                pass
        
            dsp_time_steps = [int(file_path[-1][:-4]) for file_path in dsp_file_paths if file_path[-1] != 'final.dsp']
            
            #os.system(f"mv {bombard_dir}/{path}/{int(max(dsp_time_steps))}.dsp {bombard_dir}/{path}/final.dsp")
            shutil.move(f"{bombard_dir}/{path}/{int(max(dsp_time_steps))}.dsp", f"{bombard_dir}/{path}/final.dsp")
            
    
            for file_path in dsp_file_paths:
                try:
                    shutil.move(f"mv {file_path}", f"{bombard_dir}/{path}/dsp_files/") 
                except FileNotFoundError:
                    pass
            

        elif path_check(f"{path}/final.dsp") == False and path_check(f"{path}/dsp_files/0.dsp") == True:
            shutil.move(f"{bombard_dir}/{path}/dsp_files/{int(max(dsp_time_steps))}.dsp", "{bombard_dir}/{path}/final.dsp")


        if path_check(f"{path}/0.xyz") == True:

            xyz_file_paths = glob.glob(f"{path}/*.xyz")
            xyz_file_paths = [tools.Path(path) for path in xyz_file_paths]
    
            time_steps = [int(file_path[-1][:-4]) for file_path in xyz_file_paths]
            time_steps.sort()

            os.system(f"mkdir {bombard_dir}/{path}/xyz_files")
            os.system(f"mv {bombard_dir}/{path}/*.xyz {bombard_dir}/{path}/xyz_files/")

            all_xyz = ''
            for time_step in time_steps:

                next_file = open(f"{path}/xyz_files/{time_step}.xyz")
                all_xyz += next_file.read()
                all_xyz += '\n'

                with open (f"{path}/all.xyz", 'w') as fp: 
                    fp.write(all_xyz) 

        
        jmol_convert.main(f"{path}/all.xyz")

    



if __name__ == "__main__":

    accepted_args = ['repeats', 'path']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accecpted_args=accepted_args)   
    except IndexError or KeyError:
        print('\n\nERROR: Please give inputs.\n\n')
        print('Valid inputs: -path -repeats (boolean)')

    main(args_dict)


    