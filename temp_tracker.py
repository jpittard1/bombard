
from cmath import log
import os
import tools
import sys
import numpy as np
import matplotlib.pyplot as plt


def gen_arr(log_file, titles):
    final_steps = log_file[-1].split('\n')
    final_step = None

    for line in final_steps:
        line = line.split()
        
        try:
            floated = [float(i) for i in line]
            if len(floated) > 1:
                penultimate_step = final_step
                final_step = floated[0]

        except ValueError:
            if final_step != None:
                break 

    step_diff = final_step - penultimate_step
    array_length = int(final_step/step_diff) + 1

    return np.zeros([array_length, len(titles)]), step_diff



def read_log(log_file, step_diff, array):
    
    for uloop in log_file[1:]:
        uloop = uloop.split('\n')
    
        for line in uloop:
            line = line.split()

            try:
                floated = [float(i) for i in line]
                if len(floated) == len(titles):
                    index = int(floated[0]/(step_diff))
                    array[index] = np.array(floated)

            except ValueError:
                pass 

    to_remove = []
    for index, row in enumerate(array):
        if row[-1] == 0 and row[0] == 0:
            to_remove.append(index)


    array = np.delete(array, to_remove, axis = 0)
    
    return array

def save_results(array, titles, path):
    os.system(f'mkdir {path}/temp_results')

    results_str = str(titles)
    for row in array:
        row = [float(f"{item:.6g}") for item in row]
        results_str += '\n' + str(row)

    with open("%s/temp_results/thermo_array.txt"%path, 'w') as fp: #rewriting edited input file
        fp.write(results_str)

    file_name = path.split('/')[-1]
    title_file_name = path.split('/')[-2]
    title = f"{title_file_name} {file_name}" + ' temperture log'

    fig = plt.figure()
    plt.plot(array[:,0], array[:,2])
    plt.xlabel('Timesteps')
    plt.ylabel('Overall Temperature / K')
    plt.title(title)
    
    plt.savefig(f"{path}/temp_results/temp.png")
    plt.close(fig)

    fig = plt.figure()
    plt.plot(array[:,0], array[:,3])
    plt.xlabel('Timesteps')
    plt.ylabel('Moving Temperature / K')
    plt.title(title)
    
    plt.savefig(f"{path}/temp_results/temp_mov.png")
    plt.close(fig)



print("\n\nPROGRESS: Running temp_tracker.py\n\n")

current_dir = os.path.dirname(os.path.realpath(__file__))
path = f"{current_dir}/results/testing/control/t_0g_30eV_1000_1/bake"
path = f"{current_dir}/results/testing/size/12_12_6/t_0g_30eV_4000_1"
path = f"{current_dir}/results/testing/flux/50%/t_0g_30eV_1000_1"

path = f"{current_dir}/results/{sys.argv[1]}"

titles = 'Step Time Temp c_cmov_temp Press TotEng Volume ' #should fetch these really
log_file = tools.file_proc(f"{path}/log.lammps", seperator = titles)
titles = titles.split()  

array, step_diff = gen_arr(log_file, titles)
full_array = read_log(log_file, step_diff, array)
save_results(full_array,titles,path)








