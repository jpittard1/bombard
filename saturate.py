


########## REQUIREMENTS AND PLAN ############
# This needs all xyz files, and atom type info, jmol version would be fine
# No surface information required

#TODO Checks
    #Check times add up to final
    #Find reasonable way of dictateing when it is not in the diamond other than just counting particles in the box
    # Would be better to get all of the files read in lint and then fed into each of them? although couldnt run individually, maybe just a tools function


import sys
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import tools



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

    
    settings_dict = tools.csv_reader("%s/settings.csv"%settings_path)

    frames = []

    jmol_all_xyz = open(path, 'r')
    jmol_all_xyz = jmol_all_xyz.read()

    jmol_all_xyz = jmol_all_xyz.split("\n\n")

    results_arr = np.zeros([len(jmol_all_xyz) - 1, 5])

    final = False

    ################# Determining Surface ##################

    print("\n\nPROGRESS: Determining Surface.") 

    initial = tools.file_proc(f"{settings_path}/initial_indexed.xyz")

    final_arr = tools.xyz_to_array(f"{settings_path}/final_indexed.xyz")
    

    loaded = False

    try: #allows code to be used for olded simulations when loaded wasnt in settings
        if settings_dict['loaded'] == "True":
            loaded = True
    except KeyError:
        pass

    initial_atoms_arr, region_indexes = tools.region_assign(initial, loaded = loaded)

    #at the moment takes carbon atoms from final file, need some sense check to remove carbon atoms above
    #Use 0 (initial surface hieght) +1 to account for variation in thermal positiosns
    #Use rebo cut off distcance? (2Ang)

    all_carbon_indexes = region_indexes['diamond_bulk'] + region_indexes['diamond_surface']

    carbon_zs = [final_arr[index][-1] for index in all_carbon_indexes if final_arr[index][-1] > -2]

    no_surface_atoms = int(2*settings_dict['replicate'][0]*settings_dict['replicate'][1])
    diamond_surface_zs = sorted(carbon_zs)[0:no_surface_atoms]

    surfaces = dict(diamond_surface = tools.avg(diamond_surface_zs), graphene_1 = [None,None])

    surface_limit = surfaces["diamond_surface"][0] - 2
    surface_limit_err = surfaces["diamond_surface"][1]


    ##############################################################################


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
        c_counter = 0

        for i2 in range(0,len(frame)):
            line = frame[i2].split(' ')

            if line[0] == '1' and float(line[-1]) > surface_limit:
                c_counter += 1
           
            if line[0] == '2' and float(line[-1]) > surface_limit:
                d_counter += 1

            if line[0] == '3' and float(line[-1]) > surface_limit:
                t_counter += 1
        

        results_arr[i1] = np.array([time, bombard_attempts, d_counter, t_counter, c_counter])

    try:
        os.mkdir("%s/saturate_results/"%settings_path)
    except FileExistsError:
        pass

    print("\n\nPROGRESS: Generating results.txt and graphs.") 

    results_str = f'Saturate results for {path.split("/")[-2]}\n\n'
    results_str += f'Surface limit taken to be at height of {surface_limit}±{surface_limit_err}A.\n\n'
    results_str += 'time, bombard_attempts, d_counter, t_counter, c_counter\n' + str(results_arr)

    with open("%s/saturate_results/saturate.txt"%settings_path, 'w') as fp: #rewriting edited input file
        fp.write(str(results_str))


    times = results_arr[:,0].flatten()
    attempts = results_arr[:,1].flatten()

    try:
        fluence = [i/float(settings_dict['surface_area']) for i in attempts]
        x_title = "Fluence x10^20 ions/m^2"
    except KeyError:
        fluence = attempts
        x_title = "Incident ions"

    deuterium = results_arr[:,2].flatten()
    tritium = results_arr[:,3].flatten()
    carbon = results_arr[:,4].flatten()

    plt.plot(fluence, deuterium)
    plt.plot(fluence, tritium)
    plt.plot(fluence, carbon)
    plt.legend(["Deuterium", "Tritium"])
    plt.ylabel("Particles")
    plt.xlabel(x_title)
    plt.savefig("%s/saturate_results/attempts.png"%settings_path)
    plt.close()

    plt.plot(times, deuterium)
    plt.plot(times, tritium)
    plt.plot(times, carbon)
    plt.legend(["Deuterium", "Tritium"])
    plt.ylabel("Particles")
    plt.xlabel("Time (ps)")
    plt.savefig("%s/saturate_results/time.png"%settings_path)
    plt.close()








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
