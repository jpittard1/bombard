


########## REQUIREMENTS AND PLAN ############
# Only needs first and last files, 
# Needs all files if I want some sort of progression 
# Although this would take a while...
# Probably better to try and read xyz files in Pandas rather than line by line
# Cannot use Jmol version, needs atom indexes
# Output histograms of atom displacement, find way of looking at regions
# need to consider the thermal effect of atom movement, maybe just do a thermal run without
# bombardment to see the thermal displacement and use as cut off


#####TODO##########
#DOESNT WORK AS WHOLE SYSTEM SHIFTS SLIGHTLY AS COM CHANGES POSITION
# Remove scale thermal distribution from histogram
# Count vacancies - paper where they took any movemnt beyond some point


import os
from shutil import ExecError
import sys
import tools
import numpy as np
import matplotlib.pyplot as plt

def main(path):

    print("\n\nPROGRESS: Running Damage.py.")
    
    initial = tools.file_proc("%s/initial_indexed.xyz"%path)
    equilibrium = tools.file_proc("%s/equilibrium_indexed.xyz"%path)
    equilibrium_arr = tools.xyz_to_array("%s/equilibrium_indexed.xyz"%path)
    final = tools.file_proc("%s/final_indexed.xyz"%path)


    settings_dict = tools.csv_reader("%s/settings.csv"%path)
    
    loaded = False


    try: #allows code to be used for olded simulations when loaded wasnt in settings
        if settings_dict['loaded'] == "True":
            loaded = True
    except KeyError:
        pass

    implant_ion = settings_dict['atom_type']
    if implant_ion == 't':
        implant_ion_type = 3
    else:
        implant_ion_type = 2

    total_atoms = int(settings_dict['no_bombarding_atoms'] + 6000)



    ########################### Fetching indexes from inital xyz ######################   

    print("\n\nPROGRESS: Fetching atom indices.") 
    
    initial_atoms_arr, region_indexes = tools.region_assign(initial, loaded = loaded)

    loaded_atoms_arr = np.zeros([total_atoms,4])
    indexes = []
    loaded_indexes = []
    for index, atom in enumerate(equilibrium_arr):
        if atom[0] != 1:
                loaded_atoms_arr[index] = np.array([atom[0], atom[1], atom[2], atom[3]]) 
                loaded_indexes.append(index)


    if loaded == True:
        loaded_atoms_arr = loaded_atoms_arr[:max(loaded_indexes)+1, : ]


    ########################### Fetching final atoms ######################  

    final_atoms_arr = np.zeros([total_atoms,4])
    loaded_final_atoms_arr = np.zeros([total_atoms,4])


    indexes = []
    loaded_indexes = []

    for i in final:
        line = i.split()
        if len(line) == 5: #store in array much faster
            index = int(line[0]) - 1 #so atom 1 is at 0th index
            atom_type_no = int(line[1])

            if atom_type_no == 1:
                final_atoms_arr[index] = np.array([atom_type_no, float(line[2]), float(line[3]), float(line[4])]) 
                indexes.append(index)

            elif atom_type_no != implant_ion_type and atom_type_no != 0: #get from settings what the implant ion is

                loaded_final_atoms_arr[index] = np.array([atom_type_no, float(line[2]), float(line[3]), float(line[4])]) 
                loaded_indexes.append(index)


    atoms = max(indexes)
    final_atoms_arr = final_atoms_arr[:atoms+1, :] #trims end but will still have lots of zeros for loaded sim

    if loaded == True:
        loaded_final_atoms_arr = loaded_final_atoms_arr[:max(loaded_indexes)+1, : ]





    ########################### Determing displacements ######################  

    print("\n\nPROGRESS: Calculating atoms displacements.") 


    region_distances = dict()

    diamond_width = (3.57*min(settings_dict['replicate'][:2]))*0.95

    for key, indices in region_indexes.items():
 
        try:
            displacements = [final_atoms_arr[index] - equilibrium_arr[index] for index in indices]
            distances = [tools.magnitude(row[1:]) for row in displacements if tools.magnitude(row[1:]) < diamond_width]

            region_distances[key] = distances
        
        except IndexError:
            pass



    print("\n\nPROGRESS: Generating results.txt and graphs.") 


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

    if loaded == True:

        loaded_displacements = [loaded_final_atoms_arr[index] - loaded_atoms_arr[index] for index in loaded_indexes]
        loaded_distances = [tools.magnitude(row[1:]) for row in loaded_displacements if tools.magnitude(row[1:]) < diamond_width]

        loaded_results = 'Loaded atom distances\n\n'
        loaded_results += str(loaded_distances)

        with open("%s/damage_results/loaded_damage.txt"%path, 'w') as fp: #rewriting edited input file
            fp.write(loaded_results)


        fig = plt.figure()
        plt.hist(loaded_distances, bins = 20)
        plt.xlabel("Loaded Atom Displacement / Å")
        plt.savefig(f"{path}/damage_results/loaded.png")
        plt.close(fig)    



    fig = plt.figure()
    plt.hist(region_distances['diamond_bulk'], bins= 20)
    plt.xlabel("Diamond Bulk Displacment / Å")
    plt.savefig(f"{path}/damage_results/diamond.png")
    plt.close(fig)

    fig = plt.figure()
    plt.hist(region_distances['graphene_all'], bins = 20)
    plt.xlabel("Graphene Atom Displacement / Å")
    plt.savefig(f"{path}/damage_results/graphene.png")
    plt.close(fig)    

 
 
    regions = [key  for key in region_distances]
    averages = [tools.avg(distances)[0] for key, distances in region_distances.items()]
    
    fig = plt.figure()
    plt.bar(regions, averages)
    plt.savefig(f"{path}/damage_results/region_averages.png")
    plt.close(fig)










if __name__ == "__main__":
   
    current_dir = os.path.dirname(os.path.realpath(__file__))

    dir_name = sys.argv[1]

    path = current_dir + '/results/' +  dir_name

    try:
        main(path)
        print("\n\nProgress: damage calculations complete.")
        print("\n", "-"*20, '\n')

    except FileNotFoundError:
        print("\n\n")
        print("-"*60)
        print("\nERROR: damage.py could not find initial_indexed.xyz, equilibrium_indexed.xyz or final_indexed file. "
                "To create these files, run jmol_convert.py")
        print("\nFile path used: %s"%path)
        print("\n")
        print("-"*60)