



from asyncio import start_unix_server
from tracemalloc import start
from numpy import full
from surface import Surface_finder
import os
import tools
import matplotlib.pyplot as plt
import sys
import time as tm

def main(path, cut_off_density_frac = 0.448, full_analysis = False):
    '''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    settings_path = f"{current_dir}/results/testing/size/[12,12,6]/t_0g_30eV_4000_1"
    '''

    try:
        os.mkdir("%s/surface_results/"%path)
    except FileExistsError:
        pass

    if full_analysis == True:
        try:
            os.system(f"mkdir {path}/surface_tracker_analysis")
        except FileExistsError:
            pass

    surface_density_cutoff = 0.078


  
    jmol_all_xyz = open(f'{path}/jmol_all.xyz', 'r')
    jmol_all_xyz = jmol_all_xyz.read()

    jmol_all_xyz = jmol_all_xyz.split("\n\n")


    initial_arr = tools.xyz_to_array(f"{path}/initial_indexed.xyz")
    final_arr = tools.xyz_to_array(f"{path}/final_indexed.xyz")

    initial_carbon_xs = [row[-3] for row in initial_arr if row[-4] == 1]
    initial_carbon_ys = [row[-2] for row in initial_arr if row[-4] == 1]
   


    settings_dict = tools.csv_reader("%s/settings.csv"%path)

    loaded = False
    try: #allows code to be used for olded simulations when loaded wasnt in settings
        if settings_dict['loaded'] == "True":
            loaded = True
    except KeyError:
        pass

    cut_off_heights = []
    time_steps = []

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

    legend = []

    
    for index, frame in enumerate(jmol_all_xyz[:-1]):
     
        frame = frame.split('\n')
        time_step = float(frame[1].split()[-1])
        
        carbon_zs = [float(atom_line.split()[-1]) for atom_line in frame[2:] if atom_line.split()[0] == '1']
        ion_zs = [float(atom_line.split()[-1]) for atom_line in frame[2:] if atom_line.split()[0] == '2']
        
   
        surface_finder = Surface_finder(carbon_zs, surface_area_unit_cells=surface_unit_cells, surface_area=surface_area)
        surface_finder.find_carbon(carbon_zs, cut_off_density_frac=cut_off_density_frac)
        if len(ion_zs) != 0:
            surface_finder.find_ions(ion_zs)
      
        cut_off_heights.append(surface_finder.carbon_densities[2])
        time_steps.append(time_step)
       
       
        print(f'Timestep:{time_step}, surface: {surface_finder.carbon_densities[2]}')
        
        if full_analysis == True:
            #fig = plt.figure(figsize = (6,9))
            #plt.rcParams['font.size'] = '36'
            sep = '\n'
            joined_frame = sep.join(frame)

            with open(f"{path}/surface_tracker_analysis/{time_step}.xyz", 'w') as fp: #rewriting edited input file
                fp.write(joined_frame)


            plt.plot(surface_finder.carbon_densities[0],surface_finder.carbon_densities[1])
            if len(ion_zs) != 0:
                plt.plot(surface_finder.ion_densities[0],surface_finder.ion_densities[1])
            plt.vlines(surface_finder.carbon_densities[2], 0, 0.175, colors='r')
            plt.vlines(surface_finder.carbon_densities[2] - 2, 0, 0.175, colors='r', linestyles='--')
            #plt.legend(['Carbon', 'Deuterium', 'Surface', 'Ion Cutoff'])
            plt.hlines(cut_off_density_frac*0.175, -60, 40, colors = 'b', linestyles='--')
            #plt.title(path.split('/')[-1])
            #plt.text(-45,0.15, f'{time_step}')
            plt.xlabel('z (A)')
            plt.ylabel('Carbon Density (/A^3)')
            plt.xlim(-20,30)
            plt.ylim(-0.01, 0.185)
            plt.savefig(f"{path}/surface_tracker_analysis/{time_step}.png")
            plt.close()

        
        #print(surface_finder.carbon_densities[1])
    
    if full_analysis == False:
        plt.legend(legend)
        plt.show()

        plt.plot(time_steps, cut_off_heights)
        plt.xlabel("Timesteps")
        plt.ylabel("Surface Height (A)")
        plt.savefig(f"{path}/surface_results/surface_track.png", dpi = 300, figsize = (3,1))
        plt.show()

        results_str = 'time_steps, cut_off_heights'
        for index, time in enumerate(time_steps):
            results_str += f"\n{time}, {cut_off_heights[index]}"
        
        with open("%s/surface_results/surface_track.csv"%path, 'w') as fp: #rewriting edited input file
            fp.write(results_str)

    else:
        plt.plot(time_steps, cut_off_heights)
        plt.xlabel("Timesteps")
        plt.ylabel("Surface Height (A)")
        plt.savefig(f"{path}/surface_tracker_analysis/surface_track.png", dpi = 300)
        plt.show()

        results_str = 'time_steps, cut_off_heights'
        for index, time in enumerate(time_steps):
            results_str += f"\n{time}, {cut_off_heights[index]}"
        
        with open("%s/surface_tracker_analysis/surface_track.csv"%path, 'w') as fp: #rewriting edited input file
            fp.write(results_str)
    


        
if __name__ == "__main__":

    start = tm.perf_counter()

    target_file = sys.argv[1]

    current_dir = os.path.dirname(os.path.realpath(__file__))

    path = f"{current_dir}/results/{target_file}"

    main(path, cut_off_density_frac=0.5,full_analysis=True)

    print(f"Time: {tm.perf_counter() - start}")



      