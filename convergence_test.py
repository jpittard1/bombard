

import tools
import sys
import glob
import random
import numpy as np
import damage_02 as damage
import depth_02 as depth
import ovito_analysis as wigner_seitz_analyis
import matplotlib.pyplot as plt
import time
from tqdm import tqdm
import pprint

###TODO###
#Fundemental error in this method, will always converge to the larger value as you are just sampling more of it.
#Instead need to samples UNIQUE sets, then standard deviation of these sets should given and indication of how far off it is
#Due to this limitation, go up to sample size of 380 and repeat this 5 times (for unique sets)

def main(args_dict):


    args_dict['path'] = tools.Path(args_dict['path'])
    args_dict['step_size'] = int(args_dict['step_size'])
    args_dict['average_over'] = int(args_dict['average_over'])

    
    repeat_dirs = glob.glob(f"{tools.bombard_directory()}{args_dict['path']}*r")
    repeat_dirs = [tools.Path(repeat_dir) for repeat_dir in repeat_dirs]
    root_dir = repeat_dirs[0][:-1]
    repeats_nums = [int(dir_name[-1][:-1]) for dir_name in repeat_dirs]

    max_sample_size = int(len(repeat_dirs)/args_dict['average_over'])

    if max_sample_size <= 100:
        raise ValueError('Cannot calculate convergence for these values, please input a smaller average_over.')

    sample_sizes = [10,20,40,70] + [i for i in range(args_dict['step_size'],len(repeat_dirs), args_dict['step_size'])] + [len(repeat_dirs)]
    sample_sizes = [10,20,40,70] + [i for i in range(100,max_sample_size, args_dict['step_size'])] + [max_sample_size]

    
    averages_dict = dict(average_depth = [[],[]],
                        average_depth_err = [[],[]],
                        perc_with_vacancies = [[],[]],
                        no_of_vacancies = [[],[]],
                        no_of_vacancies_err = [[],[]],
                        vacancy_depth = [[],[]],
                        vacancy_depth_err = [[],[]],
                        perc_with_etched = [[],[]],
                        no_of_etched  = [[],[]],
                        no_of_etched_err = [[],[]]
                        ) 

    start_time = time.time()
    results_arr = np.zeros([len(sample_sizes),21])

    for sample_size_index, sample_size in enumerate(tqdm(sample_sizes, desc=f'Overall', ascii=False, ncols = 100)):
        
        to_average_arr =  np.zeros([args_dict['average_over'],10])

        shuffled_dirs = random.sample(repeats_nums, args_dict['average_over']*sample_size)
        sample_sets = [shuffled_dirs[i*sample_size:(i+1)*sample_size] for i in range(args_dict['average_over'])]
 


        for repeat_index, repeat in enumerate(tqdm(range(args_dict['average_over']), desc=f'Sample size - {sample_size}', ascii=False, ncols = 100)):
            #sample_dirs = random.sample(repeats_nums, sample_size)
            sample_dirs = sample_sets[repeat_index]
        
            sample_dirs = [tools.Path(f"{root_dir}{sample_dir}r") for sample_dir in sample_dirs]
         
            damage_obj = damage.Damage(repeats=True, path=root_dir)
            damage_obj.get_repeated_damage_array(sample_dirs)

            depth_obj = depth.Depth(repeats=True, path=root_dir)
            depth_obj.get_repeated_final_depths(sample_dirs)

            ws_obj = wigner_seitz_analyis.Wigner_Seitz(path = root_dir, repeats=True)
            ws_obj.get_array()



            to_average_arr[repeat] = np.array([
                tools.avg(depth_obj.implanted_zs)[0],
                tools.avg(depth_obj.implanted_zs)[1],
                len([x for x in damage_obj.vacancies if x > 0])*100/damage_obj.no_of_repeats,
                tools.avg(damage_obj.vacancies)[0],
                tools.avg(damage_obj.vacancies)[1],
                tools.avg(damage_obj.all_vancancy_zs)[0],
                tools.avg(damage_obj.all_vancancy_zs)[1],
                len([x for x in damage_obj.etched_atoms if x > 0])*100/damage_obj.no_of_repeats,
                tools.avg(damage_obj.etched_atoms)[0],
                tools.avg(damage_obj.etched_atoms)[1]
                ])


        
        results_arr[sample_size_index][0] = sample_size
        for i, key in enumerate(averages_dict.keys()):
            avg, err = tools.avg(to_average_arr[:,i])
            averages_dict[key][0].append(avg)
            averages_dict[key][1].append(err)

            results_arr[sample_size_index][2*i + 1] = avg
            results_arr[sample_size_index][2*i + 2] = err


        
    print(f'\nThis took {(time.time() - start_time):.6g} s')
    
    for key in averages_dict.keys():
        print(f"Plotting {key}...")
        sample_size_log = [np.log10(x) for x in sample_sizes]

        if type(averages_dict[key][0]) == list:
            plt.errorbar(x = sample_size_log, y = averages_dict[key][0], yerr=averages_dict[key][1])
        else:
            plt.plot(x = sample_size_log, y = averages_dict[key])
        plt.xlabel('Log Sample Size')
        plt.ylabel(key)
        plt.savefig(f"{tools.bombard_directory()}{args_dict['path']}converge_{key}.png", dpi = 300)
        plt.close()

    sep = ', err, '
    results = 'sample_size, ' + sep.join(averages_dict.keys())
    sep = ', '

    for row in results_arr:
        line = [str(x) for x in row]
        results += f"\n{sep.join(line)}"
    with open(f"{tools.bombard_directory()}{args_dict['path']}converge.csv", 'w') as fp: #rewriting edited input file
        fp.write(results)




if __name__ == "__main__":

    accepted_args = ['path', 'step_size', 'average_over']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accecpted_args=accepted_args)   
    except IndexError or KeyError:
        print('\n\nERROR: Please give inputs.\n\n')
        print('Valid inputs: -path -repeats (boolean)')

    main(args_dict)

