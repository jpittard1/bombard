


########## REQUIREMENTS AND PLAN ############
# First file to get atom indices for each region
# Then first file post equilibrium to get region loactions
# Or just last file and use atom indicies
# Then measure from here
# Output histograms, some progression migth be interested, ie 
# do atoms penetrate further initially then not as far once loaded up


#TODO Checks:
    # Check number of bombarding atoms is less than that in regions
    # or nuumber of boombarding atoms in final is eqaul to total of regions

import os
import sys
import tools
import numpy as np
import matplotlib.pylab as plt

def main(path, loaded = False):

    initial = tools.file_proc("%s/initial_indexed.xyz"%path)
    final = tools.file_proc("%s/final_indexed.xyz"%path)
    
    settings_dict = tools.csv_reader("%s/settings.csv"%path)

    ########################### Fetching indexes from inital xyz ######################    
    
    initial_atoms_arr, region_indexes = tools.region_assign(initial, loaded = loaded)

    ########################### Finding heights of diamond and layers ######################



    final_atoms_arr = np.zeros([10000,4])
    indexes = []

    for i in final:
        line = i.split()
        if len(line) == 5: #store in array much faster
     
            index = int(line[0]) - 1 #so atom 1 is at 0th index
            atom_type_no = int(line[1])
            z = float(line[4])
            final_atoms_arr[index] = np.array([atom_type_no, float(line[2]), float(line[3]), z]) 
            indexes.append(index)

    atoms = max(indexes)
    final_atoms_arr = final_atoms_arr[:atoms+1, :]

    if loaded == False:
        diamond_surface_zs = [final_atoms_arr[index][-1] for index in region_indexes['diamond_surface']]

        surfaces = dict(diamond_surface = tools.avg(diamond_surface_zs), graphene_1 = [])

        for i in range(1,100):

            layer_key = 'graphene_%s'%i

            try:
                layer_zs = [final_atoms_arr[index][-1] for index in region_indexes[layer_key]]

                surfaces[layer_key] = tools.avg(layer_zs) 

            except KeyError:
                break


    else: #averages top 100 atoms for loaded sims
        carbon_zs = [final_atoms_arr[index][-1] for index in region_indexes['diamond_bulk']]

        diamond_surface_zs = sorted(carbon_zs)[0:100]

        surfaces = dict(diamond_surface = tools.avg(diamond_surface_zs), graphene_1 = [None,None])
    

    ########################### Getting Pentration Depths ###########################

  
    zs = [[],[],[],[],[]]
    for atom in final_atoms_arr:
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

    results = ''
   
 
    for atom_type in range (2,5):
        average, stderr = tools.avg(diamond_pens[atom_type])
        results += f'\nIon {atom_type} Average Diamond Pen: '
        results += f'{average:.4g} ± {stderr:.1g}\n'

        average, stderr = tools.avg(surface_pens[atom_type])
        results += f'Ion {atom_type} Average Surface Pen: '
        results += f'{average:.4g} ± {stderr:.1g}\n'


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

    try:
        os.mkdir("%s/depth_results/"%path)
    except FileExistsError:
        pass

    with open("%s/depth_results/depth.txt"%path, 'w') as fp: #rewriting edited input file
        fp.write(results)

    
    fig = plt.figure()
    
    for atom_type in range (2,5):
        plt.hist(surface_pens[atom_type])
        
    plt.legend(["Ion type 2", "Ion type 3", "Ion type 4"])
    plt.xlabel("Surface Penetration / Å")
    plt.savefig("%s/depth_results/surface.png"%path)
    plt.close(fig)
    

    fig = plt.figure()

    for atom_type in range (1,5):
        plt.hist(diamond_pens[atom_type])

    plt.legend(['Carbon', "Ion type 2", "Ion type 3", "Ion type 4"])
    plt.xlabel("Diamond Penetration / Å")
    plt.savefig("%s/depth_results/diamond.png"%path)
    plt.close(fig)    

    
    fig = plt.figure()
    for atom_type in range(2,5):
        region_count = region_counters[atom_type]
        regions = [key  for key in region_count]
        counts = [count for key, count in region_count.items()]
    
        plt.bar(regions, counts)

    plt.legend(["Ion type 2", "Ion type 3", "Ion type 4"])
    plt.savefig("%s/depth_results/regions.png"%path)
    plt.close(fig)

    



if __name__ == "__main__":
   
    current_dir = os.path.dirname(os.path.realpath(__file__))

    dir_name = sys.argv[1]

    try:
        if sys.argv[2] == 'True':
            prebombard = True
    except IndexError:
        print("\n\nNo Tritium.\n")
        prebombard = False


    path = current_dir + '/results/' +  dir_name

    try:
        main(path, loaded = prebombard)

    except FileNotFoundError:
        print("\n\n")
        print("-"*60)
        print("\nERROR: Depth.py could not find initial_indexed.xyz or final_indexed file. "
                "To create these file, run jmol_convert.py")
        print("\nFile path used: %s"%path)
        print("\n")
        print("-"*60)



