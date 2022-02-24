
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


def main(path, time_animation = False, times_to_plot = []):

    print("\n\nPROGRESS: Running Steinhardt.py.")


    files = [filenames for (dirpath, dirnames, filenames) in os.walk(f"{path}/steinhardt_files/")][0]

    times = [int(file[:-5]) for file in files]
    times.sort()

    times_to_plot = [min(times), max(times)] + times_to_plot

    file_dicts = [tools.custom_to_dict(f"{path}/steinhardt_files/{time}.para") for time in times_to_plot]
    file_arr = [file_dict['info_array'] for file_dict in file_dicts]
    
    initial_dict, final_dict = file_dicts[:2]
    initial_arr, final_arr = file_arr[:2]    

    settings_dict = tools.csv_reader("%s/settings.csv"%path)

    try:
        os.mkdir(f"{path}/steinhardt_results/")
    except FileExistsError:
        pass

    for index,degree in enumerate(settings_dict['steinhardt_degrees']):
        
        initial = initial_arr[:,int(index+1)]
        final = final_arr[:,int(index+1)]
        plt.hist(initial, bins = np.arange(0, 1, 0.02))
        plt.hist(final, bins = np.arange(0, 1, 0.02))
        plt.xlabel(f"Q{int(degree)}")
        plt.legend([f"Timestep: {initial_dict['timestep']}", f"Timestep: {final_dict['timestep']}"])
        plt.savefig(f"{path}/steinhardt_results/Q{int(degree)}.png")
        plt.close()


    print(times)
    time_animation = True
    if time_animation == True:

        total_time = max(times) - min(times)
        time_step = times[1] - times[0]

        sampled_indexes = list(range(0, len(times), int(len(times)/10)))

        sampled_times = [times[index] for index in sampled_indexes]

        if max(sampled_times) != max(times):
            sampled_times += [max(times)]

        file_dicts = [tools.custom_to_dict(f"{path}/steinhardt_files/{time}.para") for time in sampled_times]
        file_arrs = [file_dict['info_array'] for file_dict in file_dicts]

        Q2 = [file_arr[:,1] for file_arr in file_arrs]

        def update_hist(num,data):
            plt.cla()
            plt.hist(data[0], bins = np.arange(0, 1, 0.02))

            if num != 0:
                plt.hist(data[num], bins = np.arange(0, 1, 0.02))

            plt.xlabel("Q2")
            plt.ylim([0,850])
            plt.title(f"Timestep: {file_dicts[num]['timestep']}" )
            plt.legend(['Initial',f'Timestep: {file_dicts[num]["timestep"]}'])

        fig = plt.figure()

        ani = animation.FuncAnimation(fig, update_hist, len(sampled_times), fargs = (Q2, ), interval = 600, repeat = True, repeat_delay = 5000)
        plt.show()
            



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

    dir_name = 't_0g_30eV_10_3'
    path = current_dir + '/results/' +  dir_name

    main(path, time_animation = time_animation)