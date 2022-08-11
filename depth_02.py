


##### New version of depth, now using surface.py ######

from surface import Surface_finder
import tools
import numpy as np
import os
import sys
import matplotlib.pylab as plt






def main(path):
    '''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    settings_path = f"{current_dir}/results/testing/size/[12,12,6]/t_0g_30eV_4000_1"
    '''

    try:
        os.mkdir("%s/depth_results/"%path)
    except FileExistsError:
        pass

    surface_finding_method = 'cut_off'
    surface_cut_off = -2
    ion_cut_off = 2


    initial = tools.file_proc(f"{path}/initial_indexed.xyz")
    initial_arr = tools.xyz_to_array(f"{path}/initial_indexed.xyz")
    final_arr = tools.xyz_to_array(f"{path}/final_indexed.xyz")

    settings_dict = tools.csv_reader("%s/settings.csv"%path)

    loaded = False
    try: #allows code to be used for olded simulations when loaded wasnt in settings
        if settings_dict['loaded'] == "True":
            loaded = True
    except KeyError:
        pass

    ########################### Fetching indexes from inital xyz ######################    
    

    ########################### Finding heights of diamond and layers ######################

    print("\n\nPROGRESS: Determining heights of surfaces.") 

   
    initial_carbon_zs = [row[-1] for row in initial_arr if row[-4] == 1]
    initial_carbon_xs = [row[-3] for row in initial_arr if row[-4] == 1]
    initial_carbon_ys = [row[-2] for row in initial_arr if row[-4] == 1]
    final_carbon_zs = [row[-1] for row in final_arr if row[-4] == 1]
    final_carbon_xs = [row[-2] for row in final_arr if row[-4] == 1]
    final_dueterium_zs = [row[-1] for row in final_arr if row[-4] == 2]
    final_dueterium_xs = [row[-2] for row in final_arr if row[-4] == 2]
    final_tritium_zs = [row[-1] for row in final_arr if row[-4] == 3]
    final_tritium_xs = [row[-2] for row in final_arr if row[-4] == 3]

    
    plt.scatter(final_carbon_xs, final_carbon_zs)
    plt.scatter(final_dueterium_xs, final_dueterium_zs)
    plt.ylim(20,-20)
    plt.savefig(f'{path}/depth_results/pos_scatter.png')
    plt.close()
    

    if len(final_dueterium_zs) > len(final_tritium_zs):
        final_ion_zs = final_dueterium_zs
        final_ion_xs = final_dueterium_xs
    else:
        final_ion_zs = final_tritium_zs
        final_ion_xs = final_tritium_xs

  
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



    surface_finder = Surface_finder(final_carbon_zs, surface_area_unit_cells=surface_unit_cells, surface_area=surface_area)
    surface_finder.find_carbon(final_carbon_zs)
    surface_finder.find_surface(surface_cut_off, carbon_density = False)
    surface_finder.find_ions(final_ion_zs)
    surface_finder.initial(initial_carbon_zs)


    surfaces = dict(diamond_surface = [surface_finder.surface, surface_finder.surface_err], graphene_1 = [None,None])

    initial_atoms_arr, region_indexes = tools.region_assign(initial, loaded = loaded)

    for i in range(1,100):

        layer_key = 'graphene_%s'%i

        try:
            layer_zs = [final_arr[index][-1] for index in region_indexes[layer_key]]

            surfaces[layer_key] = tools.avg(layer_zs) 

        except KeyError:
            break

    '''
    side_area = (max(initial_carbon_zs) - min(initial_carbon_zs))*(max(initial_carbon_ys)-min(initial_carbon_ys))
            
    surface_finder_x = Surface_finder(final_carbon_xs, surface_area=side_area, surface_area_unit_cells=None)
    xs_carbon, carbon_densities_x, cut_off_z = surface_finder_x.density(initial_carbon_xs)
    xs_ions, ion_densities_x, cut_off_z = surface_finder_x.density(final_ion_xs)


    plt.plot(xs_carbon, carbon_densities_x)
    plt.plot(xs_ions, ion_densities_x)
    plt.show()

    '''

    
    ########################### Getting Pentration Depths ###########################

    print("\n\nPROGRESS: Getting penetration depths.") 


    zs = [[],[],[],[],[]]
    for atom in final_arr:
        if atom[-1] > surfaces['diamond_surface'][0] - ion_cut_off :
            zs[int(atom[0])].append(atom[-1])

    diamond_pens = [[],[],[],[],[]]
    for atom_type in range(0,5):
        diamond_pens[atom_type] = [z - surfaces['diamond_surface'][0] for z in zs[atom_type]]

    
    for i in range(1,100):
        layer_key = 'graphene_%s'%i

        try:            
            if len(region_indexes[layer_key]) == 0:
                top_layer = 'diamond_surface'
                break


        except KeyError:
            top_layer = 'graphene_%s'%(i-1)
            break


    surface_pens = [[],[],[],[],[]]
    for atom_type in range(0,5):
        surface_pens[atom_type] = [z - surfaces[top_layer][0] for z in zs[atom_type]]


      

    ####################### Getting Regions ##########################

    print("\n\nPROGRESS: Getting Regions.") 

    #creating dicts of counters for different regions and different atoms
    region_counters = []
    for atom_type in range(0,5):
        region_count = dict(diamond_bulk = 0, on_surface = 0 )
    
        for key in surfaces:
            region_count[key] = 0
        
        region_counters.append(region_count)


    #filling counters with atoms in different regions
    for atom_type in range (2,5): 
        for z in zs[atom_type]: 

            if z - surfaces['diamond_surface'][0] > 0:
                region_counters[atom_type]['diamond_bulk'] += 1
            
            elif z - surfaces[top_layer][0] < 0:
                region_counters[atom_type]['on_surface'] += 1

            else:
                for key, surface in surfaces.items():
                    if z - surface[0] > 0:
                        region_counters[atom_type][key] += 1
                        break



     ################# Constructing results text file ####################

    print("\n\nPROGRESS: Generating results.txt and graphs.") 


    results = f'Depth results for {path.split("/")[-1]}\n\n'
    results += f'Diamond surface taken to be at height of {surfaces["diamond_surface"][0]:.6g}±{surfaces["diamond_surface"][1]:.6g}A.\n'
    results += f'The {surface_finding_method} method was used to determine surface height.\n'
    results += f'Carbon atoms beyond {surface_finder.surface_cut_off}A were discounted from surface average.\n'
    results += f'Ions {ion_cut_off}A from the surface were discounted. \n\n'

 
    for atom_type in range (2,5):
        average, stderr = tools.avg(diamond_pens[atom_type])
        results += f'\nIon {atom_type} Average Diamond Pen: '
        results += f'{average:.6g} ± {stderr:.3g}\n'

        average, stderr = tools.avg(surface_pens[atom_type])
        results += f'Ion {atom_type} Average Surface Pen: '
        results += f'{average:.6g} ± {stderr:.3g}\n'


    for atom_type in range(2,5):
        region_count = region_counters[atom_type]
        for key, i in region_count.items():
            if key != 'diamond_surface' and key != 'atom_type':
                results += f'\nIon type {atom_type} locations: {key} - {i} atoms.'
        results += '\n'
        
    results += '\n'
    
    for key in surfaces:
        try:
            results += f"\n{key} height: {surfaces[key][0]:.4g} ± {surfaces[key][1]:.1g}"
        except TypeError:
            pass
    

    for atom_type in range (2,5):
        results += f'\n\nIon {atom_type} diamond pens: '
        results += f'\n{diamond_pens[atom_type]}'

        results += f'\n\nIon {atom_type} surface pens: '
        results += f'\n{surface_pens[atom_type]}'


    ################# Producing Plots and Saving Results #####################

   

    with open("%s/depth_results/depth.txt"%path, 'w') as fp: #rewriting edited input file
        fp.write(results)


    surface_finder.plot("%s/depth_results/"%path)
    surface_finder.publish_txt_file("%s/depth_results/"%path)



if __name__ == '__main__':

    current_dir = os.path.dirname(os.path.realpath(__file__))

    dir_name = sys.argv[1]


    path = current_dir + '/results/' +  dir_name

    try:
        main(path)
        print("\n\nPROGRESS: Depth calculations complete.")
        print("\n", "-"*20, '\n')

    except FileNotFoundError:
        print("\n\n")
        print("-"*60)
        print("\nERROR: Depth.py could not find initial_indexed.xyz or final_indexed file. "
                "To create these file, run jmol_convert.py")
        print("\nFile path used: %s"%path)
        print("\n")
        print("-"*60)

