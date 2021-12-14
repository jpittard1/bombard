


########## REQUIREMENTS AND PLAN ############
# Only needs first and last files, 
# Needs all files if I want some sort of progression 
# Although this would take a while...
# Probably better to try and read xyz files in Pandas rather than line by line
# Cannot use Jmol version, needs atom indexes
# Output histograms of atom displacement, find way of looking at regions
# need to consider the thermal effect of atom movement, maybe just do a thermal run without
# bombardment to see the thermal displacement and use as cut off


import os
import sys
import tools
import numpy as np
import matplotlib.pyplot as plt

def main(path):
    
    initial = tools.file_proc("%s/initial_indexed.xyz"%path)
    print('initial')
    equilibrium = tools.file_proc("%s/equilibrium_indexed.xyz"%path)
    print('equil')
    final = tools.file_proc("%s/final_indexed.xyz"%path)
    print('final')

    settings_dict = tools.csv_reader("%s/settings.csv"%path)

    ########################### Fetching indexes from inital xyz ######################    
    
    initial_atoms_arr, region_indexes = tools.region_assign(initial)




    equilibrium_atoms_arr = np.zeros([5000,4])
    indexes = []


    for i in equilibrium:
        line = i.split()
        if len(line) == 5: #store in array much faster
            index = int(line[0]) - 1 #so atom 1 is at 0th index
            atom_type_no = int(line[1])
            equilibrium_atoms_arr[index] = np.array([atom_type_no, float(line[2]), float(line[3]), float(line[4])]) 
            indexes.append(index)

    atoms = max(indexes)
    equilibrium_atoms_arr = equilibrium_atoms_arr[:atoms+1, :]




    final_atoms_arr = np.zeros([5000,4])
    indexes = []

    for i in final:
        line = i.split()
        if len(line) == 5: #store in array much faster
            index = int(line[0]) - 1 #so atom 1 is at 0th index
            atom_type_no = int(line[1])

            if atom_type_no == 1:
                final_atoms_arr[index] = np.array([atom_type_no, float(line[2]), float(line[3]), float(line[4])]) 
                indexes.append(index)

    atoms = max(indexes)
    final_atoms_arr = final_atoms_arr[:atoms+1, :]


    region_distances = dict()

    diamond_width = (3.57*min(settings_dict['replicate'][:2]))*0.95
    print(diamond_width)

    for key, indices in region_indexes.items():

        displacements = [final_atoms_arr[index] - equilibrium_atoms_arr[index] for index in indices]
        distances = [tools.magnitude(row[1:]) for row in displacements if tools.magnitude(row[1:]) < diamond_width]

        region_distances[key] = distances

    for key, val in region_distances.items():
        print(f"{key}: {len(val)}")

    results = ''
    for key, distances in region_distances.items():
        results += f'\n\n{key}'
        results += f'\n{distances}'


    try:
        os.mkdir("%s/damage_results/"%path)
    except FileExistsError:
        pass

    with open("%s/damage_results/damage.txt"%path, 'w') as fp: #rewriting edited input file
        fp.write(results)

    fig = plt.figure()
    plt.hist(region_distances['diamond_bulk'], bins= 20)
    plt.xlabel("Diamond Bulk Displacment / Å")
    plt.savefig("%s/damage_results/diamond.png"%path)
    plt.close(fig)

    fig = plt.figure()
    plt.hist(region_distances['graphene_all'], bins = 20)
    plt.xlabel("Graphene Atom Displacement / Å")
    plt.savefig("%s/damage_results/graphene.png"%path)
    plt.close(fig)    

    regions = [key  for key in region_distances]
    averages = [tools.avg(distances)[0] for key, distances in region_distances.items()]
    
    fig = plt.figure()
    plt.bar(regions, averages)
    plt.savefig("%s/damage_results/region_averages.png"%path)
    plt.close(fig)










if __name__ == "__main__":
   
    current_dir = os.path.dirname(os.path.realpath(__file__))

    dir_name = sys.argv[1]

    path = current_dir + '/results/' +  dir_name

    try:
        main(path)

    except FileNotFoundError:
        print("\n\n")
        print("-"*60)
        print("\nERROR: damage.py could not find initial_indexed.xyz, equilibrium_indexed.xyz or final_indexed file. "
                "To create these files, run jmol_convert.py")
        print("\nFile path used: %s"%path)
        print("\n")
        print("-"*60)