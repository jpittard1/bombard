



import sys
import tools
import shutil
import glob
from tqdm import tqdm





def main(args_dict):

    if args_dict['repeats'] == None:
        args_dict['repeats'] = tools.repeat_check(args_dict['path'])
    else:
        args_dict['repeats'] = tools.str_to_bool(args_dict['repeats'])

    args_dict['path'] = tools.Path(args_dict['path']) 

    if args_dict['repeats']:
        print(f"{bombard_dir}{args_dict['path']}*r")
        paths = glob.glob(f"{bombard_dir}{args_dict['path']}*r")
        print(len(paths))

    elif args_dict['multi_file']:
        pass

    else:
        paths = args_dict['path']


    if args_dict['hpc'] == True:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        cores = comm.Get_size()

        print(type(rank))
        print(cores)

        chunk_size = int(len(paths)/cores)
        remainder = len(paths)%cores

        print(chunk_size)
        print(remainder)

        selection = paths[rank*chunk_size:(rank+1)*chunk_size]

        if rank + 1 == cores:
            selection += paths[(rank+1)*chunk_size:(rank+1)*chunk_size+remainder]

        print(f"I'm rank {rank}, and I have {len(selection)} dirs")

        paths= selection
        cont_yn = 'y'


    else:

        paths_str = '\n'

        for path in tqdm(paths, desc='Fetching paths'):
            paths_str += path + '\n'
        

        print("\n\n")
        print("-"*60)
        print("\nNOTE: This will delete the xyz_files dir, dsp_files dir and all other .xyz and .para files except "
                        "all.xyz and jmol_all.xyz in:")
        print(paths_str)
        cont_yn = tools.input_misc("\nDo you wish to continue (y/n): ", ['y','n'])
        print("\n")


    
    if cont_yn == 'y':

        
        for path in tqdm(paths, desc= 'Cleaning paths'):
            
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
    accepted_args = ['repeats', 'path', 'multi_file', 'hpc']


    args_dict = tools.args_to_dict(sys.argv[1:], accecpted_args=accepted_args)  
    args_dict['hpc'] = tools.str_to_bool(args_dict['hpc'])

    main(args_dict)
