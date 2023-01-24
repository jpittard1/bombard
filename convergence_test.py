

import tools
import sys
import glob
import random
import numpy as np
import damage_02 as damage
import depth_02 as depth
import matplotlib.pyplot as plt
import time


def main(args_dict):


    args_dict['path'] = tools.Path(args_dict['path'])
    args_dict['step_size'] = int(args_dict['step_size'])
    args_dict['average_over'] = int(args_dict['average_over'])

    
    repeat_dirs = glob.glob(f"{tools.bombard_directory()}/{args_dict['path']}/*r")
    repeat_dirs = [tools.Path(repeat_dir) for repeat_dir in repeat_dirs]
    root_dir = repeat_dirs[0][:-1]
    repeats_nums = [int(dir_name[-1][:-1]) for dir_name in repeat_dirs]

    sample_sizes = [10,20,40,70] + [i for i in range(args_dict['step_size'],len(repeat_dirs), args_dict['step_size'])] + [len(repeat_dirs)]
    
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
    for sample_size in sample_sizes:
        
        print(f'Running sample size of {sample_size}...')
        #depth_to_average =  np.zeros([args_dict['average_over'],2])
        #damage_to_average = np.zeros([args_dict['average_over'],4])

        to_average_arr =  np.zeros([args_dict['average_over'],10])

        for repeat in range(args_dict['average_over']):
            sample_dirs = random.sample(repeats_nums, sample_size)
        
            sample_dirs = [tools.Path(f"{root_dir}/{sample_dir}r/") for sample_dir in sample_dirs]
         
            damage_obj = damage.Damage(repeats=True, path=root_dir)
            damage_obj.get_repeated_damage_array(sample_dirs)

            depth_obj = depth.Depth(repeats=True, path=root_dir)
            depth_obj.get_repeated_final_depths(sample_dirs)


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


   
        for i, key in enumerate(averages_dict.keys()):
            avg, err = tools.avg(to_average_arr[:,i])
            averages_dict[key][0].append(avg)
            averages_dict[key][1].append(err)
        
    print(f'\nThis took {(time.time() - start_time):.6g} s')
    
    for key in averages_dict.keys():
        print(f"Plotting {key}...")
        sample_size_log = [np.log10(x) for x in sample_sizes]

        if type(averages_dict[key][0]) == list:
            plt.errorbar(x = sample_size_log, y= averages_dict[key][0], yerr=averages_dict[key][1])
        else:
            plt.plot(x = sample_size_log, y = averages_dict[key])
        plt.xlabel('Log Sample Size')
        plt.ylabel(key)
        plt.savefig(f"{tools.bombard_directory()}/{args_dict['path']}/converge_{key}.png", dpi = 300)
        plt.close()

    sep = ', '
    results = sep.join(averages_dict.keys())
    for row in to_average_arr:
        line = [str(x) for x in row]
        results += f"\n{sep.join(line)}"
    with open(f"{tools.bombard_directory()}/{args_dict['path']}/converge.csv", 'w') as fp: #rewriting edited input file
        fp.write(results)




if __name__ == "__main__":

    accepted_args = ['path', 'step_size', 'average_over']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accecpted_args=accepted_args)   
    except IndexError or KeyError:
        print('\n\nERROR: Please give inputs.\n\n')
        print('Valid inputs: -path -repeats (boolean)')

    main(args_dict)

