


########## REQUIREMENTS AND PLAN ############
# This needs all xyz files, and atom type info, jmol version would be fine
# No surface information required

#TODO Checks
    #Check times add up to final


import sys
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from tools import csv_reader



def bombard_attempts_calc(settings_dict, time, final = False):
    
    bombarding_time = time - settings_dict['pre_bombard_time']

    if bombarding_time > 0:
        
        bombards = int(bombarding_time/settings_dict['bombard_time'])

        correction = 1
        if bombarding_time%settings_dict['bombard_time'] == 0:
            correction = 0

        if bombards + correction > float(settings_dict['no_bombarding_atoms'] ):
            return float(settings_dict['no_bombarding_atoms'])
        
        else:
            return bombards + correction

    else:
        return 0 






def main(path):

    print("\n\nPROGRESS: Running saturate.py.") 

    dir_path = path.split('/')[:-1]

    settings_path = ''
    for i in dir_path:
        settings_path += '/'
        settings_path += i

    
    settings_dict = csv_reader("%s/settings.csv"%settings_path)

    frames = []

    jmol_all_xyz = open(path, 'r')
    jmol_all_xyz = jmol_all_xyz.read()

    jmol_all_xyz = jmol_all_xyz.split("\n\n")

    results_arr = np.zeros([len(jmol_all_xyz) - 1, 4])

    final = False

    print("\n\nPROGRESS: Counting atoms.") 

    for i1, frame in enumerate(jmol_all_xyz):
        
        if i1 == len(jmol_all_xyz) - 1:
            final = True

        try:
            frame = frame.split('\n')
     
            time = frame[1].split(' ')[-1]
            time = float(time)
        
            bombard_attempts = bombard_attempts_calc(settings_dict,time, final = final)

        except IndexError:#required to deal with: ''
            break

        d_counter = 0
        t_counter = 0

        for i2 in range(0,len(frame)):
            line = frame[i2].split(' ')
           
            if line[0] == '2':
                d_counter += 1

            if line[0] == '3':
                t_counter += 1
           

        results_arr[i1] = np.array([time, bombard_attempts, d_counter, t_counter])

    try:
        os.mkdir("%s/saturate_results/"%settings_path)
    except FileExistsError:
        pass

    print("\n\nPROGRESS: Generating results.txt and graphs.") 

    results_str = 'time, bombard_attempts, d_counter, t_counter\n' + str(results_arr)

    with open("%s/saturate_results/saturate.txt"%settings_path, 'w') as fp: #rewriting edited input file
        fp.write(str(results_str))

    times = results_arr[:,0].flatten()
    attempts = results_arr[:,1].flatten()
    deuterium = results_arr[:,2].flatten()
    tritium = results_arr[:,3].flatten()

    plt.plot(attempts, deuterium)
    plt.plot(attempts, tritium)
    plt.ylabel("Bombarding Particles Remaining")
    plt.xlabel("Attempted Bombarding Particles")
    plt.savefig("%s/saturate_results/attempts.png"%settings_path)








if __name__ == "__main__":
   
    current_dir = os.path.dirname(os.path.realpath(__file__))

    dir_name = sys.argv[1]

    path = current_dir + '/results/' +  dir_name + "/jmol_all.xyz"

    try:
        main(path)
        print("\n\nProgress: saturate calculations complete.")
        print("\n", "-"*20, '\n')


    except FileNotFoundError:
        print("\n\n")
        print("-"*60)
        print("\nERROR: Saturate.py could not find jmol_all.xyz file. "
                "To create this file, run jmol_convert.py")
        print("\nFile path used: %s"%path)
        print("\n")
        print("-"*60)
