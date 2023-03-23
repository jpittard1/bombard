



import os
import glob
import pprint


dir_path = os.path.dirname(os.path.realpath(__file__))

target = 'results/testing/size/[8,8,6]/t_0g_30eV_1778_1'
target = 'results/testing/fixes/nvt/damp_100'
target = 'results/testing/timestep'
target = 'results/loaded'
target = 'results/orient/111/to_compare/d_orient_30eV*'
target = 'results/orient/111/d_orient_30eV_4000_3'
target = 'results/repeats/'
new_only = False

all_paths = []
for i in range(0,10):
    sep = '/*'*i
    #layer = glob.glob(f'{dir_path}/{target}{sep}/jmol_all.xyz')
    layer = glob.glob(f'{dir_path}/{target}{sep}/*r')
    

    if len(layer) > 0:
        all_paths += layer


to_remove = []
if new_only == True:
    counter = 0
    for path in all_paths: 

        file_path = path.split('/')[:-1]
        sep = '/'
        file_path = sep.join(file_path)
    
        try:  
            with open(f"{file_path}/saturate_02_results/saturate.txt", 'w') as fp: #rewriting edited input file
                print(f"Removing {path}")
                to_remove.append(path)

        except FileNotFoundError:
            print(f'Keeping {path}')
            pass


for file in to_remove:
    all_paths.remove(file)



start_length = len(dir_path.split('/')) + 1
all_paths = [path.split('/')[start_length:-1] for path in all_paths]
sep = '/'
all_paths = [sep.join(path) for path in all_paths]
all_paths = glob.glob(f"{dir_path}/results/repeats/h*")

import tools
all_paths = [tools.Path(path) for path in all_paths]


for path in all_paths:
    #os.system(f"python {dir_path}/lint.py False {path}")
    #os.system(f"python {dir_path}/jmol_convert.py {path}")
  
    os.system(f"python {tools.bombard_directory()}/depth_02.py -path {path} -repeats True")
    #os.system(f"python {dir_path}/saturate.py {path}")
    #os.system(f"python {dir_path}/temp_tracker.py {path}")
    #os.system(f"python {dir_path}/surface_tracker.py {path}")
    #os.system(f"python {dir_path}/steinhardt_freeze.py {path}")
    #os.system(f"rm {dir_path}/results/{path}/steinhardt_files/*.para")
    #os.system(f"rm {dir_path}/results/{path}/OUT")


    

    