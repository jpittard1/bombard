



import os
import sys
import tools
import shutil
import glob

def main(paths):

    paths_str = '\n'

    for path in paths:
        paths_str += path + '\n'

    

    print("\n\n")
    print("-"*60)
    print("\nNOTE: This will delete the xyz_files dir, dsp_files dir and all other .xyz and .para files except "
                    "all.xyz and jmol_all.xyz in:")
    print(paths_str)
    cont_yn = tools.input_misc("\nDo you wish to continue (y/n): ", ['y','n'])
    print("\n")


    
    if cont_yn == 'y':

        for path in paths:
            
            try:
                shutil.rmtree("%s/xyz_files"%path) 
            except FileNotFoundError:
                print("\n\n")
                print("-"*60)
                print("\nERROR: This file is already clean or does not exist.")
                print("\nFile path used: %s"%path)
                print("\n")
                
            try:
                shutil.rmtree("%s/dsp_files"%path) 
            except FileNotFoundError:
                print("\n\n")
                print("-"*60)
                print("\nERROR: This file is already clean or does not exist.")
                print("\nFile path used: %s"%path)
                print("\n")
                

            try:
                shutil.rmtree("%s/steinhardt_files"%path) 
            except FileNotFoundError:
                pass
    


 
if __name__ == "__main__":

    bombard_dir = tools.bombard_directory()
    accepted_args = ['repeats', 'path', 'multi_file']


    args_dict = tools.args_to_dict(sys.argv[1:], accecpted_args=accepted_args)   

    if tools.str_to_bool(args_dict['repeats']):
        paths = glob.glob(f"{bombard_dir}/{args_dict['path']}/*r")

    elif args_dict['multi_file']:
        pass


    main(paths=paths)
