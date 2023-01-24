


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
import sys
import tools
import numpy as np
import matplotlib.pyplot as plt
import glob


class Damage:

    def __init__(self, path, repeats = False, settings_dict = None):

        self.path = path
        self.repeats = tools.str_to_bool(repeats)
        self.surface_cut_off = -2
        self.thermal_displacement_cut_off = 1

        if self.repeats == False:
            self.settings_dict = tools.csv_reader(f"{self.path}settings.csv")
        else:
            self.settings_dict = settings_dict

        try:
            os.mkdir(f"{self.path}/damage_results/")
        except FileExistsError:
            pass

    def get_arrays(self):

        self.initial_arr = tools.xyz_to_array(f"{self.path}initial_indexed.xyz")
        self.equilibrium_arr = tools.xyz_to_array(f"{self.path}equilibrium_indexed.xyz")
        self.final_arr = tools.xyz_to_array(f"{self.path}final_indexed.xyz")

    def find_repeated_damage(self,repeat_paths):

        values = np.zeros([arr])

        for repeat_path in repeat_paths:

            equilibrium_arr = tools.xyz_to_array(f"{repeat_path}equilibrium_indexed.xyz")
            final_arr = tools.xyz_to_array(f"{repeat_path}final_indexed.xyz")

            self.find_etched_atoms(equilibrium_arr, final_arr)
            self.find_displacements()
            self.find_vancancies()


    def subtract_arrs(self, arr_1, arr_2):
        '''
        Matches size then performs arr_2 - arr_1
        '''
  
        print(arr_1.shape)
        print(arr_2.shape)
        diff =  arr_2.shape[0] - arr_1.shape[0] 
        empties = np.zeros([abs(diff),arr_2.shape[1]], dtype=float)
    
        subtracted_arr = np.zeros(arr_2.shape)
        for i, atom in enumerate(arr_2):
            print(f"{atom} - {arr_1[i]} = {atom - arr_1[i]}")
            subtracted_arr[i] = atom - arr_1[i]

        return subtracted_arr



    def find_etched_atoms(self, array_1 = None, array_2 = None):

        if type(array_1) and type(array_2) == np.ndarray:
            self.displacement_arr = self.subtract_arrs(array_1, array_2)
        else:
            self.displacement_arr = self.subtract_arrs(self.equilibrium_arr, self.final_arr)

        to_delete = []
        for i, atom in enumerate(self.displacement_arr):
            if atom[0] == -1 or atom[0] == 1: # cannot count removed atoms like this
                to_delete.append(i)
         
            #elif atom[-1] < self.surface_cut_off: #Not valid, atom[-1] is z displacement not z
            #    if self.repeats == True:
            #        to_delete.append(i)

        print(self.displacement_arr)
        original_shape = self.displacement_arr.shape
        self.displacement_arr = np.delete(self.displacement_arr, to_delete, 0)
        print(f'OLD SHAPE: {original_shape}, NEW SHAPE: {self.displacement_arr.shape}')
        print(self.displacement_arr)

    

    def frozen_check(self):

        print('initial arr')
        print(self.initial_arr)
        print('equilibrium arr')
        print(self.equilibrium_arr)
        print('final arr')
        print(self.final_arr)


        self.find_etched_atoms()
        self.find_displacements()

        y_shift = np.ones([1,len(self.equilibrium_arr[:,-1])])*30
        blank = np.zeros(self.equilibrium_arr.shape)
        blank[:,-2] = y_shift
        
        equil = self.equilibrium_arr
        equil += blank

        y_shift = np.ones([1,len(self.final_arr[:,-1])])*30
        blank = np.zeros(self.final_arr.shape)
        blank[:,-2] = y_shift

        final = self.final_arr
        final += blank*2
        
        plt.scatter(self.initial_arr[:,-2], self.initial_arr[:,-1], s= 1)
        plt.scatter(equil[:,-2], equil[:,-1], s = 1)
        plt.scatter(final[:,-2], final[:,-1], s = 1)
        plt.ylim([-10,45])

        average_width = 3.567/2
        resolution = 0.2
        z = min(self.displacement_arr[:,-1])
        averages = []
        zs = []

        print(self.displacement_arr[0])
        while z < max(self.displacement_arr[:,-1]):

            zmin = z - average_width/2
            zmax = z + average_width/2

            to_avg = [row[0] for row in self.displacement_arr if row[-1] <= zmax and row[-1] > zmin]


            averages.append(tools.avg(to_avg)[0])
            zs.append(z)

            z += resolution
     
        plt.plot(averages,zs)
       


        plt.show()




    def find_displacements(self):

        x_width, y_width = np.array(self.settings_dict['virtual_replicate'][0:2])*3.567

        for i, atom in enumerate(self.displacement_arr): #correcting for periodicity
            shift = [int(atom[-3]/x_width), int(atom[-2]/y_width)]
            shift = [0,0]

         

            self.displacement_arr[i] = atom + np.array([atom[0], shift[0]*x_width, shift[1]*y_width, 0 ])
            self.displacement_arr[i][0] = tools.magnitude(atom[1:])



    def find_vancancies(self, cut_off = 2):
        self.vacancies = len([displacement for displacement in self.displacement_arr[:,0] if displacement > cut_off])

    def remove_thermal_displacements(self):
        self.movement = [displacement for displacement in self.displacement_arr[:,0] if displacement > self.thermal_displacement_cut_off]

    def publish_histograms(self):

        plt.hist(self.displacement_arr[:,0], bins = 50)
        plt.hist(self.movement, bins = 50)
        plt.show()
        plt.show()

    def publish_txt(self):

        results = f'Damage results for {self.path.split("/")[-1]}\n\n'
        results += f"\nNumber of vacancies (movement beyond 2 A): {self.vacancies}"
        results += f"\nAverage atom displacment: {tools.avg(self.displacement_arr[:,0])[0]}"
        results += f"\nAverage x displacment: {tools.avg(self.displacement_arr[:,1])[0]}"
        results += f"\nAverage y displacment: {tools.avg(self.displacement_arr[:,2])[0]}"
        results += f"\nAverage y displacment: {tools.avg(self.displacement_arr[:,3])[0]}"

        results += f"\n\nRemoving thermal motion (cut off {self.thermal_displacement_cut_off}):"
        results += f"\nAverage atom displacement: {tools.avg(self.movement)[0]}"
   

        results += f"\n\n{self.settings_dict['atom_type']} carbon displacements, x, y, z: "
        results += f'\n{self.displacement_arr}'

        with open(f"{self.path}/damage_results/damage.txt", 'w') as fp: #rewriting edited input file
            fp.write(results)

    def publish_repeat_text(self):

        pass







        


def new_main(args_dict):


    if tools.str_to_bool(args_dict['repeats']) == False:

        damage = Damage(args_dict['path'], args_dict['repeats'])
        damage.get_arrays()
        damage.frozen_check()
        raise KeyError
        damage.find_etched_atoms()
        damage.find_displacements()
        damage.find_vancancies()
        damage.remove_thermal_displacements()
        damage.publish_histograms()
        damage.publish_txt()



    elif tools.str_to_bool(args_dict['repeats']) == True:

        bombard_dir = tools.bombard_directory()
        repeat_dirs_path = glob.glob(f"{bombard_dir}/{args_dict['path']}/*r")

        #need to work out best way to loop through these and combine, need settings
        #for at least one of them. Maybe have settings outside of inidividual repeat files?

        damage = Damage(args_dict['path'], args_dict['repeats'])
        damage.get_arrays()
        damage.find_etched_atoms()
        damage.find_displacements()

        







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

    accepted_args = ['path', 'repeats']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')
       
    new_main(args_dict)



'''
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
'''