

from asyncore import write
from distutils.log import error
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



def averages(arrays, center_only = False, zlims = None):

    if zlims == None:
        zlo, zhi = [10, 25]
    else:
        zlo, zhi = zlims

    atoms = arrays[0].shape[0]
    all_times = np.zeros([len(arrays)*atoms, arrays[0].shape[1]])

    for index, array in enumerate(arrays):
        all_times[int(atoms*index):int(atoms*(index+1))][:] = array


    if center_only == True:
        z_list = list(all_times[:,0])
        remove_from_average = [index for index, z in enumerate(z_list) if z < zlo or z > zhi]
        all_times = np.delete(all_times, remove_from_average, 0)

    avg_str = f'\nValues averaged over {all_times.shape[0]} values calculated from approx. '
    avg_str += f'{int(all_times.shape[0]/len(arrays))} atoms and {len(arrays)} timesteps, between z values of {zlo} and {zhi}.\n\n'
    
    avg_dict = dict()

    for index in range(1, 6):
        degree = int(index*2 + 2)

        avg, error = tools.avg(all_times[:,index])

        avg_str += f"Q{degree}: {avg} ± {error} "
        avg_str += "\n"    

        avg_dict[f"Q{degree}"] = [avg, error]

       
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



def depth_profile(arrays, path, settings_dict = None, times = None, diamond_avg_dict = None, graphene_avg_dict = None):

    bin_size = 3.456
    #degrees = settings_dict["steinhardt_degrees"]
    degrees = [4,6,8,10,12]
    titles = ['z'] + [f"Q{int(degree)}" for degree in degrees]
    
    for column in range(1, arrays[0].shape[1]):
        print(f"Plotting {titles[column]}...")
        for array in arrays:

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
                print(len(selected_zs))

                if len(selected_zs) >= 20:

                    indexes = [list(array[:,0]).index(z) for z in selected_zs]

                    params = [array[index,column] for index in indexes]
                    params = [para for para in params if para != 1 and para != 0]
                    avg = tools.avg(params)

                    bins.append(tools.avg(selected_zs)[0])
                    avgs.append(avg)
                    print(f"{titles[column]} {avg[0]} ± {avg[1]})")


                z_lo_lim += bin_size
                z_hi_lim += bin_size

            vals = [avg[0] for avg in avgs]
            errs = [avg[1] for avg in avgs]
            plt.plot(bins, vals)
            plt.errorbar(bins, vals, yerr = errs)
            

        diamond_ref = reference_values('diamond', titles[column], diamond_avg_dict = diamond_avg_dict)
        graphene_ref = reference_values('graphene', titles[column], graphene_avg_dict = graphene_avg_dict)

        thickness_conv = 100/0.2
        sigma = 1
        #plt.axhline(y=diamond_ref[0], color='b', linestyle='-', linewidth = diamond_ref[1]*2*thickness_conv*sigma , alpha = 0.5)
        #plt.axhline(y=graphene_ref[0], color='r', linestyle='-', linewidth = diamond_ref[1]*2*thickness_conv*sigma, alpha = 0.5)
        plt.axhline(y=diamond_ref[0], color='b', linestyle='-', linewidth = 1 , alpha = 0.5)
        plt.axhline(y=graphene_ref[0], color='r', linestyle='-', linewidth = 1, alpha = 0.5)
        plt.text(min(bins), (diamond_ref[0]-0.015), 'Diamond')
        plt.text(min(bins), (graphene_ref[0]-0.015), 'Graphene')
        plt.ylim([-0.1,1])

        plt.xlabel("z position / Å")
        plt.ylabel(f"{titles[column]}")
        plt.legend(times)
        #plt.title(f"{int(settings_dict['energy'])}eV, {int(settings_dict['no_bombarding_atoms'])} bombardments")

        plt.savefig(f"{path}/{titles[column]}.png", dpi=600, bbox_inches = "tight")
        plt.close()

        out = "z, average\n"
        for index, bin in (bins):
            out += f"{bin}, {avgs[index][0]}, {avgs[index][1]} \n"

        with open(f"{path}/{titles[column]}.txt", 'w') as fp: 
            fp.write(out) 



  
  

def histogram(array, path):

    degrees = ['Q4','Q6','Q8','Q10','Q12']
    degrees = [2*n +2 for n in range(1,6)]
    for index,degree in enumerate(degrees):
    
        plt.hist(array[:,int(index+1)], bins = np.arange(0, 1, 0.02))
        plt.xlabel(f"Q{int(degree)}")
        plt.savefig(f"{path}/Q{int(degree)}_histogram.png")
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
            
#Goes through all xyz
#For selected timestep (start with just one)
    # Convert to data file
    # Run simulation to get parameters
    # Extract parameters ()


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
    
    avg_str = averages(file_arrs)

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
    print(path)
    main(path, time_animation = time_animation)



