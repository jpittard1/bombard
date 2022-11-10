



import os
import sys
import tools
import shutil

def main(paths):

    paths_str = '\n'

    for path in paths:
        paths_str += path + '\n'

    

    print("\n\n")
    print("-"*60)
    print("\nNOTE: This will delete the xyz_files dir and all other .xyz and .para files except "
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
                shutil.rmtree("%s/steinhardt_files"%path) 
            except FileNotFoundError:
                pass
    






if __name__ == "__main__":
   
    current_dir = os.path.dirname(os.path.realpath(__file__))

    dir_names = sys.argv[1:]

    paths = [current_dir + '/results/' +  dir_name for dir_name in dir_names]

    main(paths)
