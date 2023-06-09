


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
from surface import Surface_finder



def bombard_attempts_calc(settings_dict, time, final = False):
    #Flawed with new timing issues?
    
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

def read_log(path):
    '''Reads log file instead of relying on an equal number of timesteps between
    bombardments - not always the case with a variable timestep. Out puts a dictionary
    where keys correspond to each timestep, items are another dict of actual time and
    number of attemped bombards'''

    atoms = tools.file_proc(f"{path}/log.lammps", seperator= 'Created 1 atoms')
    #Splits when each D/T atoms is created.

    bombard_attempts_dict = dict()

    for atom_no, atom in enumerate(atoms):
        #Splits to easily access thermo data
        timechecks = atom.split("Step Time")
        lines = timechecks[-1].split('\n')
        first_dump_line = lines[1].split()

        bombard_attempts_dict[first_dump_line[0]] = dict(time = first_dump_line[1],
                                                        attempts = atom_no)
  
    keys = [key for key in bombard_attempts_dict.keys()]
  
    print(f"First: {bombard_attempts_dict[keys[0]]}")
    print(f"Second: {bombard_attempts_dict[keys[1]]}")
    print(f"Last: {bombard_attempts_dict[keys[-1]]}")

    return bombard_attempts_dict






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

    results_arr = np.zeros([len(jmol_all_xyz) - 1, 9])

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

    initial_arr, region_indexes = tools.region_assign(initial, loaded = loaded)

    initial_carbon_xs = [row[-3] for row in initial_arr if row[-4] == 1]
    initial_carbon_ys = [row[-2] for row in initial_arr if row[-4] == 1]
    final_carbon_zs = [row[-1] for row in final_arr if row[-4] == 1]    

    if all([int(i) for i in settings_dict['replicate']]) == 1:
        try:
            surface_unit_cells = int(settings_dict['virtual_replicate'][0]*settings_dict['virtual_replicate'][1])
            surface_area = None
        except KeyError:
            surface_area = (max(initial_carbon_xs) - min(initial_carbon_xs))*(max(initial_carbon_ys)-min(initial_carbon_ys))
            surface_unit_cells = None
    else:
        surface_unit_cells = int(settings_dict['replicate'][0]*settings_dict['replicate'][1])
        surface_area = None



    surface_cut_off = 0
    


    ##############################################################################


    print("\n\nPROGRESS: Counting atoms.") 
    surfaces = []

    bombard_attempts_dict = read_log(f"{settings_path}")

    for i1, frame in enumerate(jmol_all_xyz):
        
        if i1 == len(jmol_all_xyz) - 1:
            final = True

        try:
            frame = frame.split('\n')
     
            step = frame[1].split(' ')[-1]
            step = float(step)
        
            #bombard_attempts = bombard_attempts_calc(settings_dict,step, final = final)

        except IndexError:#required to deal with: ''
            break

        #d_counter = 0
        #t_counter = 0
        #c_counter = 0


        #carbon_zs = []
        #for i2 in range(0,len(frame)):
        #    line = frame[i2].split(' ')

        #    if line[0] == '1' and float(line[-1]) >= surface_finder.surface:
        #        c_counter += 1
        #        carbon_zs.append(float(line[-1]))
           
        #    if line[0] == '2' and float(line[-1]) >= ion_limit:
        #        d_counter += 1

        #    if line[0] == '3' and float(line[-1]) >= ion_limit:
        #        t_counter += 1

        #carbon_zs = [float(frame[i2].split()[-1]) for i2 in range(0,len(frame)) ]
        available_steps = [int(key) for key in bombard_attempts_dict.keys()]
        target_step = tools.closest_to(int(step), available_steps)
        bombard_attempts = bombard_attempts_dict[str(int(target_step))]['attempts']
        time = bombard_attempts_dict[str(int(target_step))]['time']

        carbon_zs = [float(line.split()[-1]) for line in frame if line.split()[0] == '1']
        d_zs = [float(line.split()[-1]) for line in frame if line.split()[0] == '2']
        t_zs = [float(line.split()[-1]) for line in frame if line.split()[0] == '3']

        if bombard_attempts < (len(d_zs) + len(t_zs)):
            raise ValueError("Error in counting, more counted D/T than attempted implants.")


        surface_finder = Surface_finder(carbon_zs, surface_area_unit_cells=surface_unit_cells, surface_area=surface_area)
        surface_finder.find_carbon(carbon_zs, cut_off_density_frac=0.5)
        surface_finder.find_surface(surface_cut_off, ion_cut_off=-2, carbon_density = True, averaging = False)
        ion_limit = surface_finder.surface - 2


        valid_carbon_zs = [val for val in carbon_zs if val >= surface_finder.surface]
        valid_d_zs = [val for val in d_zs if val >= ion_limit]
        valid_t_zs = [val for val in t_zs if val >= ion_limit]
        c_counter = len(valid_carbon_zs)
        d_counter = len(valid_d_zs)
        t_counter = len(valid_t_zs)


        if i1 == 0:
            c_counter = len(carbon_zs)
            initial_c = c_counter
         
        
        if bombard_attempts !=  0:
            sputt_yield = (initial_c - c_counter)/(bombard_attempts)
        else:
            sputt_yield = 0

        if bombard_attempts !=  0:
            ref_yield = (bombard_attempts - (d_counter+t_counter))/(bombard_attempts)
        else:
            ref_yield = 1


        results_arr[i1] = np.array([step, time, bombard_attempts, d_counter, t_counter, c_counter, sputt_yield, ref_yield, surface_finder.surface])
  

    try:
        os.mkdir("%s/saturate_02_results/"%settings_path)
    except FileExistsError:
        pass

    print("\n\nPROGRESS: Generating results.txt and graphs.") 

    results_str = f'Saturate results for {path.split("/")[-2]}\n\n'
    results_str += f'Surface limit taken to be at height of {surface_finder.surface}±{surface_finder.surface_err}A.\n\n'
    results_str += 'steps, time, bombard_attempts, d_counter, t_counter, c_counter, sputt_yield, ref_yield, surface_height\n' 
    comma = ', '
    for row in results_arr:
        row_list = [str(i) for i in row]
        results_str += comma.join(row_list)
        results_str += '\n'
        

    with open("%s/saturate_02_results/saturate.txt"%settings_path, 'w') as fp: #rewriting edited input file
        fp.write(str(results_str))


    steps = results_arr[:,0].flatten()
    times = results_arr[:,1].flatten()
    attempts = results_arr[:,2].flatten()

    try:
        fluence = [i/float(settings_dict['surface_area']) for i in attempts]
        x_title = "Fluence x10^20 ions/m^2"
    except KeyError:
        fluence = attempts
        x_title = "Incident ions"

    
    deuterium = results_arr[:,3].flatten()
    tritium = results_arr[:,4].flatten()
    carbon = results_arr[:,5].flatten()
    sputt = results_arr[:,6].flatten()
    reflect = results_arr[:,7].flatten()
    surface = results_arr[:,8].flatten()

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()

    ax1.plot(fluence, deuterium, label = 'Deuterium')
    ax1.plot(fluence, tritium, label = 'Tritium')
    ax1.plot(fluence, carbon, label = 'Carbon')
    ax1.legend()
    ax1.set_ylabel("Particles")
    ax1.set_xlabel(x_title)

    ticks = np.linspace(min(fluence), max(fluence), 6)

    def tick_function(ticks):
        return [str(int(tick*float(settings_dict['surface_area']))) for tick in ticks]
            
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_xticks(ticks)
    ax2.set_xticklabels(tick_function(ticks))
    ax2.set_xlabel(f"Bombard Attempts")


    plt.savefig("%s/saturate_02_results/attempts.png"%settings_path)
    plt.close()

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()

    ax1.plot(fluence, sputt)
    ax1.plot(fluence, reflect)
    ax1.legend(["Sputtering", "Reflection"])
    ax1.set_ylabel("Yield")
    ax1.set_xlabel(x_title)

    ticks = np.linspace(min(fluence), max(fluence), 6)

    ax2.set_xlim(ax1.get_xlim())
    ax2.set_xticks(ticks)
    ax2.set_xticklabels(tick_function(ticks))
    ax2.set_xlabel(f"Bombard Attempts")


    plt.savefig("%s/saturate_02_results/sputtering_yield.png"%settings_path, dpi = 300)
    plt.close()

    plt.plot(times, deuterium)
    plt.plot(times, tritium)
    plt.plot(times, carbon)
    plt.legend(["Deuterium", "Tritium", "Carbon"])
    plt.ylabel("Particles")
    plt.xlabel("Time (ps)")
    plt.savefig("%s/saturate_02_results/time.png"%settings_path)
    plt.close()

    plt.plot(fluence,surface)
    plt.ylabel("Surface Height (A)")
    plt.xlabel("Fluence)")
    plt.savefig("%s/saturate_02_results/surface_height.png"%settings_path)
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

    read_log(f"{current_dir}/results/{dir_name}")