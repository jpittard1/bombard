



import os
import sys
import tools
import shutil

def main(path):


    print("\n\n")
    print("-"*60)
    print("\nNOTE: This will delete the xyz_files dir and all other .xyz files except "
                    "all.xyz and jmol_all.xyz in: \n%s\n\n"%path)
    cont_yn = tools.input_misc("Do you wish to continue (y/n): ", ['y','n'])
    print("\n")

    
    if cont_yn == 'y':
        
        try:
            shutil.rmtree("%s/xyz_files"%path) 
        except FileNotFoundError:
            pass
 








if __name__ == "__main__":
   
    current_dir = os.path.dirname(os.path.realpath(__file__))

    dir_name = sys.argv[1]

    path = current_dir + '/results/' +  dir_name


    try:
        main(path)

    except FileNotFoundError:
        print("\n\n")
        print("-"*60)
        print("\nERROR: This file is already clean.")
        print("\nFile path used: %s"%path)
        print("\n")
    
