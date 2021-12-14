


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

def main(path, prebombard = False):

    initial = tools.file_proc("%s/initial_indexed.xyz"%path)
    final = tools.file_proc("%s/final_indexed.xyz"%path)
    
    settings_dict = tools.csv_reader("%s/settings.csv"%path)

    ########################### Fetching indexes from inital xyz ######################    
    
    initial_atoms_arr, region_indexes = tools.region_assign(initial)

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

    if prebombard == True:
        zs = sorted([final_atoms_arr[i][-1] for i in range(final_atoms_arr.shape[0])])
        diamond_surface_zs = zs[0:100]

        surfaces = dict(diamond_surface = tools.avg(diamond_surface_zs), graphene_1 = [])

    else:
        diamond_surface_zs = [final_atoms_arr[index][-1] for index in region_indexes['diamond_surface']]

        surfaces = dict(diamond_surface = tools.avg(diamond_surface_zs), graphene_1 = [])

        for i in range(1,100):

            layer_key = 'graphene_%s'%i

            try:
                layer_zs = [final_atoms_arr[index][-1] for index in region_indexes[layer_key]]

                surfaces[layer_key] = tools.avg(layer_zs) 

            except KeyError:
                break

    
    ########################### Getting Pentration Depths ###########################

    deuterium_zs = [i[-1] for i in final_atoms_arr if i[0] == 2]
    print(deuterium_zs)
    tritium_zs = [i[-1] for i in final_atoms_arr if i[0] == 3]
    print(tritium_zs)

    d_diamond_pen = [z - surfaces['diamond_surface'][0] for z in deuterium_zs]
    t_diamond_pen = [z - surfaces['diamond_surface'][0] for z in tritium_zs]
    print(d_diamond_pen)

    if prebombard == False:
        for i in range(1,100):
            layer_key = 'graphene_%s'%i

            try:            
                if len(region_indexes[layer_key]) == 0:
                    top_layer = 'diamond_surface'
                    break


            except KeyError:
                top_layer = 'graphene_%s'%(i-1)
                break

    surface_pen = [z - surfaces[top_layer][0] for z in deuterium_zs]
    d_diamond_avg_pen = tools.avg(d_diamond_pen)
    t_diamond_avg_pen = tools.avg(t_diamond_pen)
    surface_avg_pen = tools.avg(surface_pen)
 


    ####################### Getting Regions ##########################

    region_count = dict(diamond_bulk = 0, on_surface = 0 )
    for key in surfaces:
        region_count[key] = 0


    for z in deuterium_zs:

        if z - surfaces['diamond_surface'][0] > 0:
            region_count['diamond_bulk'] += 1
        
        elif z - surfaces[top_layer][0] < 0:
            region_count['on_surface'] += 1

        else:
            for key, surface in surfaces.items():
                if z - surface[0] > 0:
                    region_count[key] += 1
                    break




    results = ''
    results += f'\n\nAverage Surface Pen: {surface_avg_pen[0]:.4g} ± {surface_avg_pen[1]:.1g}'
    results += f'\nAverage Diamond Pen: {diamond_avg_pen[0]:.4g} ± {diamond_avg_pen[1]:.1g}\n'

    for key, i in region_count.items():
        if key != 'diamond_surface':
            results += f'\nAtoms loctions: {key} - {i} atoms.'
        
    results += '\n'
    for key in surfaces:
        results += f"\n{key} height: {surfaces[key][0]:.4g} ± {surfaces[key][1]:.1g}"

    results += '\n\nSurface Pens:\n'
    results += str(surface_pen)
    results += '\n\nDiamond Pens:\n'
    results += str(d_diamond_pen)


   ################# Producing Plots and Saving Results #####################

    try:
        os.mkdir("%s/depth_results/"%path)
    except FileExistsError:
        pass

    with open("%s/depth_results/depth.txt"%path, 'w') as fp: #rewriting edited input file
        fp.write(results)

    fig = plt.figure()
    plt.hist(surface_pen)
    plt.xlabel("Surface Penetration / Å")
    plt.savefig("%s/depth_results/surface.png"%path)
    plt.close(fig)

    fig = plt.figure()
    plt.hist(d_diamond_pen)
    plt.xlim(-1, 2 + max(d_diamond_pen))
    plt.xlabel("Diamond Penetration / Å")
    plt.savefig("%s/depth_results/diamond.png"%path)
    plt.close(fig)    

    regions = [key  for key in region_count]
    counts = [count for key, count in region_count.items()]
    
    fig = plt.figure()
    plt.bar(regions, counts)
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
        main(path, prebombard= prebombard)

    except FileNotFoundError:
        print("\n\n")
        print("-"*60)
        print("\nERROR: Depth.py could not find initial_indexed.xyz or final_indexed file. "
                "To create these file, run jmol_convert.py")
        print("\nFile path used: %s"%path)
        print("\n")
        print("-"*60)



