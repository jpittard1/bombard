



from surface import Surface_finder
import os
import tools
import matplotlib.pyplot as plt

def main(path):
    '''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    settings_path = f"{current_dir}/results/testing/size/[12,12,6]/t_0g_30eV_4000_1"
    '''

    try:
        os.mkdir("%s/surface_results/"%path)
    except FileExistsError:
        pass

    surface_density_cutoff = 0.078


    jmol_all = tools.file_proc(f"{path}/jmol_all.xyz", seperator = '\n\n')
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


    for frame in jmol_all[:-1]:

        frame = frame.split('\n')
        time_step = float(frame[1].split()[-1])
        
        carbon_zs = [float(atom_line.split()[-1]) for atom_line in frame[2:] if atom_line.split()[0] == '1']

        surface_finder = Surface_finder(carbon_zs, surface_area_unit_cells=surface_unit_cells, surface_area=surface_area)
        surface_finder.find_carbon(carbon_zs)
        cut_off_heights.append(surface_finder.carbon_densities[2])
        time_steps.append(time_step)

    plt.plot(time_steps, cut_off_heights)
    plt.xlabel("Timesteps")
    plt.ylabel("Surface Height (A)")
    plt.savefig(f"{path}/surface_results/surface_track.png", dpi = 300)
    plt.show()

    results_str = 'time_steps, cut_off_heights'
    for index, time in enumerate(time_steps):
        results_str += f"\n{time}, {cut_off_heights[index]}"
    
    with open("%s/surface_results/surface_track.csv"%path, 'w') as fp: #rewriting edited input file
        fp.write(results_str)



        


current_dir = os.path.dirname(os.path.realpath(__file__))

path = f"{current_dir}/results/fluence/d_0g_30eV_4000_3"

main(path)
      