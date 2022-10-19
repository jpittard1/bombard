

from asyncore import write
from distutils.log import error, info
from math import degrees

import numpy as np
import tools
import matplotlib.pyplot as plt
import os
import sys
import matplotlib.animation as animation


#TODO#
#Incoorparte tidying of para files into lint.py
#Generic way to find final and inital files
#Some time evolustion (animation?)
#Graphene run
#Use generic custom dump to dict else where

#use elif in queue and others
#Mkae generic function for reading files so you dont have a massive list of if statements
#Probably store in array or dict. Concerns with dict are keeping the required order in file


def combine_time_steps(file_dicts):
    

    atoms_across_frames = [file_dict['info_array'].shape[0] for file_dict in file_dicts.values()]

    keys = [key for key in file_dicts.keys()]
    all_times = np.zeros([sum(atoms_across_frames), file_dicts[keys[0]]['info_array'].shape[1]])
    low_lim = 0
    high_lim =  0
    for index, file_dict in enumerate(file_dicts.values()): #combining different timestep arrays
        high_lim += atoms_across_frames[index]
        all_times[low_lim:high_lim][:] = file_dict['info_array']
        low_lim += atoms_across_frames[index]

    return dict(frame_timestep = 'all',
                lammps_timestep = 0,
                number_of_atoms = sum(atoms_across_frames),
                column_titles = file_dicts[keys[0]]['column_titles'],
                info_array = all_times)

    return file_dicts

    


def averages(file_dicts, steinhardt_settings, zlims = [10, 25]):
    '''Averages Q values over atoms across timesteps, to be used for references value calculations,
    not useful for bombardment runs. centre_only = True will only average between a specific z
    region (dictated by zlims) to avoid edge effects'''

    zlo, zhi = zlims
    '''
    atoms_across_frames = [array.shape[0] for array in arrays]
    all_times = np.zeros([sum(atoms_across_frames), arrays[0].shape[1]])

    low_lim = 0
    high_lim =  0
    for index, array in enumerate(arrays): #combining different timestep arrays
        high_lim += atoms_across_frames[index]
        all_times[low_lim:high_lim][:] = array
        low_lim += atoms_across_frames[index]

'''
    combined_dict = combine_time_steps(file_dicts=file_dicts)
    all_times = combined_dict['info_array']
    keys = [int(key)  for key in file_dicts.keys()]

    if steinhardt_settings['reference_gen'] == True:
        z_list = list(all_times[:,0])
        remove_from_average = [index for index, z in enumerate(z_list) if z < zlo or z > zhi]
        all_times = np.delete(all_times, remove_from_average, 0)

    avg_str = f'\nValues averaged over {all_times.shape[0]} values calculated from approx. '
    avg_str += f'{int(all_times.shape[0]/len(file_dicts))} atoms and {len(file_dicts)-1} timesteps, between z values of {zlo} and {zhi}.\n\n'
    
    avg_dict = dict()

    for index, degree in enumerate(steinhardt_settings['q_paras']):

        avg, error = tools.avg(all_times[:,index+1])

        avg_str += f"Q{degree}: {avg} ± {error} "
        avg_str += "\n"    

        avg_dict[f"Q{degree}"] = [avg, error]

    avg_str += f'\n\nFinal sampled timestep ({max(keys)}) values: \n\n'

    for index, degree in enumerate(steinhardt_settings['q_paras']):

        avg, error = tools.avg(file_dicts[f'{max(keys)}']['info_array'][:,index+1])

        avg_str += f"Q{degree}: {avg} ± {error} "
        avg_str += "\n"    

       
    return avg_str, avg_dict, all_times

def reference_values(structure, parameter = None, diamond_avg_dict = None, graphene_avg_dict = None):

    diamond_params = dict(Q4 = [0.5180118560360008, 0.02656543017122089],
                            Q6 = [0.598108953668558, 0.07561106471416827 ],
                            Q8 = [0.2567065046761886, 0.0780559032814971],
                            Q10 = [0.6361827569947173, 0.02277826367243237],
                            Q12 = [0.4227865899432596, 0.01188534640561115],)

    graphene_params = dict(Q4 = [0.401032219659714 , 0.0619126714837585 ],
                            Q6 = [0.7195561116669492,  0.0528605607558030], 
                            Q8 = [0.536537533463343 , 0.02897974073377327], 
                            Q10 = [0.4821477786445084,  0.0381652897723078], 
                            Q12 = [0.6722171197501554,  0.0415955301648523])  

    if diamond_avg_dict != None:
        diamond_params = diamond_avg_dict
    if graphene_avg_dict != None:
        graphene_params = graphene_avg_dict

    if structure == 'diamond':
        if parameter == None:
            return diamond_params
        else:
            return diamond_params[parameter]     

    if structure == 'graphene':
        if parameter == None:
            return graphene_params
        else:
            return graphene_params[parameter]     



def depth_profile(file_dicts, path, steinhardt_settings, diamond_avg_dict = None, graphene_avg_dict = None, min_avg_val = 20):

    bin_size = 3.456
    #degrees = settings_dict["steinhardt_degrees"]

    titles = ['z'] + [f"Q{int(degree)}" for degree in steinhardt_settings['q_paras']]
    arrays = [file_dict['info_array'] for file_dict in file_dicts.values()]
    times = [int(key) for key in file_dicts.keys()]
    for column in range(1, arrays[0].shape[1]):

        for frame_index, array in enumerate(arrays):

            zs = list(array[:,0])
            zs.sort()

            z_hi_lim = (min(zs) + bin_size)
            z_lo_lim = (min(zs))

            bins = []
            avgs = []

            #####TODO########
                # Feels like ther must be a neater way of doing this
                # Could order full array in z then cycle trough based off index 

            while z_lo_lim <= max(zs):

                selected_zs = [z for z in zs if z < z_hi_lim and z > z_lo_lim ]
              

                if len(selected_zs) >= min_avg_val:

                    indexes = [list(array[:,0]).index(z) for z in selected_zs]

                    params = [array[index,column] for index in indexes]
                    params = [para for para in params if para != 1 and para != 0]
                    avg = tools.avg(params)

                    bins.append(tools.avg(selected_zs)[0])
                    avgs.append(avg)
            



                z_lo_lim += bin_size
                z_hi_lim += bin_size

            vals = [avg[0] for avg in avgs]
            errs = [avg[1] for avg in avgs]

            plt.errorbar(bins, vals, yerr = errs, label = f'{times[frame_index]}', capsize=5, marker='x')

            print(f"Plotting column {column}, for frame {frame_index}")
            

        diamond_ref = reference_values('diamond', titles[column], diamond_avg_dict = diamond_avg_dict)
        graphene_ref = reference_values('graphene', titles[column], graphene_avg_dict = graphene_avg_dict)

        thickness_conv = 100/0.2
        sigma = 1
        #plt.axhline(y=diamond_ref[0], color='b', linestyle='-', linewidth = diamond_ref[1]*2*thickness_conv*sigma , alpha = 0.5)
        #plt.axhline(y=graphene_ref[0], color='r', linestyle='-', linewidth = diamond_ref[1]*2*thickness_conv*sigma, alpha = 0.5)
        plt.axhline(y=diamond_ref[0], color='b', linestyle='-', linewidth = 1 , alpha = 0.5, label = 'Diamond')
        plt.axhline(y=graphene_ref[0], color='r', linestyle='-', linewidth = 1, alpha = 0.5, label = 'Graphene')

        plt.ylim([-0.1,1])

        plt.xlabel("z position / Å")
        plt.ylabel(f"{titles[column]}")
        
        plt.legend()

        plt.savefig(f"{path}/{titles[column]}.png", dpi=600, bbox_inches = "tight")
        plt.close()

        out = "z, average, error\n"
       
        for index, bin in enumerate(bins):
            out += f"{bin}, {avgs[index][0]}, {avgs[index][1]} \n"

        with open(f"{path}/{titles[column]}.csv", 'w') as fp: 
            fp.write(out) 



  
  

def histogram(file_dicts, path, steinhardt_settings):
    '''Produces Histograms for values across all timesteps. Takes in all timesteps to allow for animation
    which currently aren't used. More useful to produce for each timestep. Refernce dictates whether 
    average occurs over multple timesteps (no bombardment) or single timestep.'''


    if steinhardt_settings['reference_gen'] == True:
        combined_dict = combine_time_steps(file_dicts=file_dicts)
        file_dicts = dict(combined = combined_dict)


    for file_dict in file_dicts.values():
        for index, degree in enumerate(steinhardt_settings['q_paras']):
            diamond_ref = reference_values('diamond', f"Q{degree}", diamond_avg_dict = None)
            graphene_ref = reference_values('graphene', f"Q{degree}", graphene_avg_dict = None)

            plt.hist(file_dict['info_array'][:,int(index+1)], bins = np.arange(0, 1, 0.02))
            plt.axvline(x=diamond_ref[0], color='b', linestyle='-', linewidth = 1 , alpha = 0.5, label = 'Diamond')
            plt.axvline(x=graphene_ref[0], color='r', linestyle='-', linewidth = 1, alpha = 0.5, label = 'Graphene')
            plt.xlabel(f"Q{int(degree)}")
            plt.title(f"Timestep: {file_dict['frame_timestep']}")
            plt.legend()
            plt.savefig(f"{path}/Q{int(degree)}_{int(file_dict['frame_timestep'])}_histogram.png")
            plt.close()

    time_animation = False
    if time_animation == True:

        total_time = max(times) - min(times)
        time_step = times[1] - times[0]

        sampled_indexes = list(range(0, len(times), int(len(times)/100)))

        sampled_times = [times[index] for index in sampled_indexes]

        if max(sampled_times) != max(times):
            sampled_times += [max(times)]

        file_dicts = [tools.custom_to_dict(f"{path}/steinhardt_files/{time}.para") for time in sampled_times]
        file_arrs = [file_dict['info_array'] for file_dict in file_dicts]

        Q6 = [file_arr[:,2] for file_arr in file_arrs]

        def update_hist(num,data):
            plt.cla()
            plt.hist(data[0], bins = np.arange(0, 1, 0.02))

            if num != 0:
                plt.hist(data[num], bins = np.arange(0, 1, 0.02))

            plt.xlabel("Q6")
            plt.ylim([0,1100])
            plt.title(f"Timestep: {file_dicts[num]['timestep']}" )
            plt.legend(['Initial',f'Timestep: {file_dicts[num]["timestep"]}'])

        fig = plt.figure()

        ani = animation.FuncAnimation(fig, update_hist, len(sampled_times), fargs = (Q6, ), interval = 60, repeat = True, repeat_delay = 5000)
        plt.show()
    
        #writervideo = animation.FFMpegWriter(fps=5) 
        #ani.save(f"{path}/steinhardt_restults/", writer=writervideo)
            


def main(path, time_animation = False, times_to_plot = []):

    print("\n\nPROGRESS: Running Steinhardt.py.")

    files = [filenames for (dirpath, dirnames, filenames) in os.walk(f"{path}/steinhardt_files/")][0]

    times = [int(file.split('.')[0]) for file in files]
    times.sort()
  
    times_to_plot = [min(times), max(times)] + times_to_plot
    times_to_plot = [times[i] for i in range(0, len(times), int(len(times)/3))]

    file_dicts = [tools.custom_to_dict(f"{path}/steinhardt_files/{time}.para") for time in times_to_plot]
    file_arrs = [file_dict['info_array'] for file_dict in file_dicts]
    
    #depth_profile(file_arrs, path, settings_dict, times_to_plot)
    
    avg_str, x, y = averages(file_arrs)

    with open(f"{path}/graphene_para_averages.txt", 'w') as fp: #rewriting edited input file
        fp.write(avg_str) 


    


if __name__ == "__main__":

    current_dir = os.path.dirname(os.path.realpath(__file__))

    try:
        dir_name = sys.argv[1]
    except IndexError:
        print("\nERROR: No File Name provided.")

    time_animation = False
    try:    
        if sys.argv[2] == 'True':
            time_animation = True
    except IndexError:
        pass

    #dir_name = 'graphene_para'

    path = current_dir + '/results/' +  dir_name

    main(path, time_animation = time_animation)



