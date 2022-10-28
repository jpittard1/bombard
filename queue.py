


import os
import shutil
import random

import graphene_maker as gmak
import tools
import job_tracker

#################################################################################
##################### USER INPUTS, see README file. #############################
#################################################################################

print("\n\nPROGRESS: Running queue.py")

dir_path = os.path.dirname(os.path.realpath(__file__))
lammps_files_path = "%s/LAMMPS_files"%dir_path

#these settings below should all be elsewhere really
#maybe a seperate input file? as there are multiple LAMMPS ones

results_dir_name = 'results'
loaded = False
grain = False
multi_bombard = False
orient = True
energy = 10
test = False
hpc = True
temp = 300

if loaded == True:
    virtual_replicate = ['8','8','6']
    input_file_name = 'in.loaded_multi_bombard'
if grain == True:
    virtual_replicate = ['8','8','12']
    input_file_name = 'in.final_pc'
if orient == True:
    virtual_replicate = ['8','8','6']
    input_file_name = 'in.final_orient'
if multi_bombard == True:
    virtual_replicate = None
    input_file_name = 'in.final_sc'

pre_bomb_run_val = '3000' #this is changed if test == True, so must be changed here
                            #rather than the input file.
bomb_run_val = "10000" #this is automatically increase for slow particles and must be
                    #changed here rather than the input file.
post_bomb_run_val = '100000'
number_of_particles = '4000' #bombarding

if test == True:
    number_of_particles = '5'
    energy = 40
    pre_bomb_run_val = '100'
    bomb_run_val = '100'

##################################################################################



##################################################################################
######################## Reading and Editing Input File ##########################
##################################################################################


in_file = tools.file_proc("%s/%s"%(lammps_files_path, input_file_name))           

paths = []
data_files = ['data.graphite_sheet']
    

#Better way would be to just turn every line into a dict, with the first word the key, then can look up
#Unsure how well a dict would keep the order, or deal with multiple keys
#Maybe an array would be better, would ensure order is preserved, can look up indexes in the first column
#graphene_sheets = in_file_arr.look_up('#number_of_sheets')
#good idea to make array object


class Input_file:
    def __init__(self, path):
        self.path = path


    def open(self):
        setattr(self, "in_file",tools.file_proc(self.path))


    def list_convert(self):

        in_list = []
        commands = []
        for index, line in enumerate(in_file):
            line = line.split(' ')

            new_line = []
            for i in line:
                new_line.extend(i.split("\t"))

            while True:
                try:
                    new_line.remove('')
                except ValueError:
                    break
  
            in_list.append(new_line)
            try:
                commands.append(new_line[0])
            except IndexError:
                commands.append('')



        setattr(self, 'in_list', in_list)
        setattr(self, 'commands', commands)

    def look_up(self, identifiers, out_indices = False):

        if type(identifiers) == list:
            command, identifier = identifiers
        else:
            command = identifiers

        indices = [i for i, x in enumerate(self.commands) if x == command]

        results = [self.in_list[i] for i in indices]

        if len(results) == 1:
            results = results[0]

        if type(identifiers) == list:
            for i in indices:
                try:
                    index = self.in_list[i].index(identifier)

                    if out_indices == False:
                        return self.in_list[i]
                    else:
                        return self.in_list[i], [i]
                except ValueError:
                    pass
        
        else:
            if out_indices == False:
                return results
            else:
                return results, indices


    def add_path(self, identifiers, path = None):

        line_to_edit, indices = self.look_up(identifiers, out_indices=True)
       
    
        if len(indices) > 1:

            lengths = [len(line) for line in line_to_edit]
            index = lengths.index(min(lengths))
          
            line_to_edit = line_to_edit[index]
            main_index = indices[index]
        
        else:
            main_index = indices[0]

        index, file_path = [[i, line] for i, line in enumerate(line_to_edit) if line[0] == '/'][0]

        file_path = file_path.split("/")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        line_to_edit[index] = f"{dir_path}/LAMMPS_files/{file_path[-1]}"

        self.in_list[main_index] = line_to_edit
        
        return line_to_edit[index]



    def edit_line(self, identifiers, indicies, values):

        line_to_edit, main_index = self.look_up(identifiers, out_indices=True)

        for i, index in enumerate(indicies):
            line_to_edit[index] = values[i]

        self.in_list[int(main_index[0])] = line_to_edit

        print(line_to_edit)

'''
            
atom_masses = dict(h = 1.0079, d = 2.0014, t = 3.0160)
unit_conv = 1e-2*(1.602e-19/1.661e-27)**0.5

input_file = Input_file("%s/%s"%(lammps_files_path, input_file_name))
input_file.open()
input_file.list_convert()

graphite_sheets = input_file.look_up("#number_of_sheets")[1]
atom_type = input_file.look_up("#atom_type")[1]
diamond_type = input_file.look_up("#diamond_type")[1]
replicate = input_file.look_up("replicate")[1]

velocity = (2*energy/float(atom_masses[atom_type])**0.5)*unit_conv 

input_file.add_path('read_data')
input_file.add_path(['read_data', 'add'])
input_file.add_path('pair_coeff')

input_file.edit_line('set', [-1], [str(velocity)])


raise ValueError
'''

new = ''
primary_data_file_bool = True
for i in in_file: #goes through the input file line by line both reading and editing
    index = in_file.index(i)
    i = i.split()
    seperator = ' '

    try:

        if i[0] == '#number_of_sheets':
            graphite_sheets = float(i[1])

        elif i[0] == '#atom_type': #either 'h', 'd' or 't'
            atom_type = i[1]

        elif i[0] == '#diamond_type':
            diamond_type = i[1]

        elif i[0] == "variable" and i[2] == "uloop":
            i[-1] = str(number_of_particles)
            in_file[index] = seperator.join(i)     

        elif i[0] == 'read_data':
            
            file_path = i[1].split('/')

            if file_path[-1][:5] == 'data.':
                i[1] = f"{lammps_files_path}/{file_path[-1]}"
                data_files.append(file_path[-1])

        
            in_file[index] = seperator.join(i)

            if primary_data_file_bool == True:

                primary_data_file = tools.file_proc(f"{lammps_files_path}/{file_path[-1]}")

                for line in primary_data_file:
                    line = line.split(" ")

                    if line[-1] == 'xhi':
                        prim_xlo, prim_xhi = [float(item) for item in line[0:2]]

                    if line[-1] == 'yhi':
                        prim_ylo, prim_yhi = [float(item) for item in line[0:2]]

                    if line[-1] == 'zhi':
                        prim_zlo, prim_zhi = [float(item) for item in line[0:2]]

                    if line[0] == "Masses":
                        break

                primary_data_file_bool = False

        elif i[0] == 'pair_coeff':

            i[3] = "%s/CH.rebo"%lammps_files_path #setting file paths for lammps files
            in_file[index] = seperator.join(i)

        elif i[0] == "set" and i[-2] == 'vz': #setting velocity line
    
            if atom_type == 'h':
                atom_mass = 1.0079
            if atom_type == 'd':
                atom_mass = 2.0014
            if atom_type == 't':
                atom_mass = 3.0160
      
            if atom_type != 'h' and atom_type != 't' and atom_type !='d':
                atom_mass = float(atom_type)

            unit_conv = 1e-2*(1.602e-19/1.661e-27)**0.5
            velocity = ((2*energy/atom_mass)**0.5)*unit_conv 

            i[-1] = str(velocity)
            in_file[index] = seperator.join(i)
        
        
        elif i[0] == "replicate":
    
            replicate = i[1:]

            in_file[index] = seperator.join(i)

        elif i[0] == "create_atoms":

            if atom_type == 'd':
                i[1] = '3'

            if atom_type == 't':
                i[1] = '3'
            
            in_file[index] = seperator.join(i)



        elif i[0] == "fix" and len(i[-1]) == 5: #changing random seed for each repeat
            rand = random.randint(10000,99999)
            i[-1] = str(rand)
            i[4] = str(temp)
            i[5] = str(temp)


            in_file[index] = seperator.join(i)

        elif i[0] == 'fix' and i[3] == 'nvt':
            i[-2] = str(temp)
            i[-3] = str(temp)
            in_file[index] = seperator.join(i)

        elif i[0] == "velocity" and i[1] == 'all' and i[2] == 'create': #changing random seed for each repeat
            rand = random.randint(10000,99999)
            i[4] = str(rand)
            i[3] = str(temp)

            in_file[index] = seperator.join(i)

    
        elif i[0] == "compute":
            steinhardt_line = i
            steinhardt_degrees = [4,6,8,10,12]

            try:
                if line[4] == 'degrees':
                    steinhardt_degrees = [float(degree) for degree in line[5:]]

            except IndexError or ValueError:
                pass

            in_file[index] = seperator.join(i)




        #################Makes much more sense to pull these from limits in data file###################
        ######## need to vary both regions not just box TODO
        ##### This was done originally when using the replicate line, so maybe need to include some specification of loaded/single data file/no replicate used
        ##### Or maybe it looks at first data file and takes the values, then have areplicate 1 1 1 lien which multplies it whatever


        elif i[0] == 'region': 

            x_width = abs(prim_xhi - prim_xlo)*float(replicate[0])
            y_width = abs(prim_yhi - prim_ylo)*float(replicate[1])

            x_lo, x_hi = [prim_xlo, prim_xhi*float(replicate[0])]
            y_lo, y_hi = [prim_ylo, prim_yhi*float(replicate[1])]


            if i[1] == 'box':
                graphene_thickness = 3.35
                z_hi = -graphene_thickness*graphite_sheets - 25
                z_lo = z_hi - 30
            elif i[1] == '1':
                z_lo = 0
                z_hi = (float(replicate[2]) + 2)*3.567
            elif i[1] == 'base':
                z_lo = 8 
                z_hi = 70
            else:
                z_lo = i[-2]
                z_hi = i[-1]

            if i[1] == 'top' and orient == True:
                z_low = 0
                z_hi = (int(virtual_replicate[2]) - 1) *3.567
            
            i = seperator.join(i[:3]) + " %s %s %s %s %s %s"%(x_lo, x_hi, y_lo, y_hi, z_lo, z_hi)

            in_file[index] = i



        elif i[0] == 'run':
            if i[2] == "#inbetween": 
                i[1] = bomb_run_val
            elif i[2] == '#prebombardment':
                i[1] = pre_bomb_run_val
            elif i[2] == '#postbombardment':
                i[1] = post_bomb_run_val

            in_file[index] = seperator.join(i)

  


    except IndexError:                                    
        pass

    new += "%s\n"%in_file[index]

with open("%s/%s"%(lammps_files_path,input_file_name), 'w') as fp: #rewriting edited input file
    fp.write(str(new)) 

print("\n\nPROGRESS: New input file generated.")



#########################################################################################


#########################################################################################
################### Creating Graphene Data file and new directorys ######################
#########################################################################################

if multi_bombard == True:
    virtual_replicate = replicate


#writes graphene data sheet for the specific simulation
#returns dictionary containing the number of bulk atoms in each region
#used for lattice displacement calculations

###TODO bulk atoms dict incorrect (need to make it less reliant on replicate)
bulk_atoms_dict = gmak.main(data_file_path = "%s/data.graphite_sheet"%lammps_files_path, no_bombarding_atoms = number_of_particles, 
                            replicate = replicate, no_of_sheets = graphite_sheets, atom_mass = atom_mass)

bulk_atoms_dict =  dict(diamond = 8*int(replicate[0])*int(replicate[1])*int(replicate[2]), graphene = 0)

print("\n\nPROGRESS: Graphene Data file generated.")

count = 1
while True: #creating new directory 
    try:
        if multi_bombard == True:
            new_path = "%s/%s/%s_%sg_%s_%s_%s"%(dir_path, results_dir_name, atom_type, int(graphite_sheets), 
                                            f"{energy}eV", number_of_particles, count)
        elif loaded == True:
            new_path = "%s/%s/%s_loaded_%s_%s_%s"%(dir_path, results_dir_name, atom_type, 
                                            f"{energy}eV", number_of_particles, count)

        elif grain == True:
            new_path = "%s/%s/%s_grain_%s_%s_%s"%(dir_path, results_dir_name, atom_type, 
                                            f"{energy}eV", number_of_particles, count)
        
        elif orient == True:
            new_path = "%s/%s/%s_orient_%s_%s_%s"%(dir_path, results_dir_name, atom_type, 
                                            f"{energy}eV", number_of_particles, count)

        
        os.mkdir(new_path)
        paths.append(new_path)
        break

    except FileExistsError:
        count += 1  

for data_file in data_files:
    shutil.copyfile(f"{lammps_files_path}/{data_file}", f"{new_path}/{data_file}")
    
shutil.copyfile("%s/%s"%(lammps_files_path, input_file_name), "%s/%s"%(new_path, input_file_name))


settings_dict = dict(no_bombarding_atoms = number_of_particles, 
                    replicate = replicate,
                    virtual_replicate = virtual_replicate, 
                    surface_area = float(x_width*y_width),
                    no_of_sheets = graphite_sheets, 
                    atom_mass = atom_mass,
                    diamond_type = diamond_type,
                    bulk_atoms_dict = bulk_atoms_dict,
                    energy = energy,
                    temp = temp,
                    atom_type = atom_type,
                    pre_bombard_time = pre_bomb_run_val,
                    bombard_time = bomb_run_val,
                    post_bombard_time = post_bomb_run_val,
                    loaded = loaded,
                    grain = grain,
                    multi_bombard = multi_bombard,
                    data_files = data_files,
                    steinhardt_degrees = steinhardt_degrees,
                    steinhardt_line = steinhardt_line
                    )

tools.cvs_maker(new_path,settings_dict)

##################################################################################


##################################################################################
############################ RUNNING SIMULTAION ##################################
##################################################################################


if test == True:
    os.chdir(new_path)    
    os.system("lmp_serial -in %s/%s"%(lammps_files_path, input_file_name))


if hpc == True and test == False:         
    shutil.copyfile("LAMMPS_files/srun","%s/srun"%new_path) #copying srun avoids rewritting
    os.chdir(new_path)
    os.system("sbatch %s/srun"%new_path)  #submitted job via slurm

lammps_files_path = "%s/LAMMPS_files"%dir_path

if hpc == False and test == False: 
    os.chdir(new_path)    
    os.system("mpiexec -n 2 lmp_serial -in %s/%s"%(lammps_files_path, input_file_name))

print("\n\nPROGRESS: Simulation job submitted.")

if hpc == True:

    folder_name = new_path.split('/')[-1]
    job_tracker.Track(folder_name)

    print("\n\nPROGRESS: jobs.txt updated.")

###################################################################################




try:
    file_paths = open(f"{dir_path}/results/file_path.txt", 'r')
    file_paths = file_paths.read()

    file_paths = file_paths[1:-1]
  

    file_paths = file_paths.split(",")
  
    file_paths = [file_path.replace("'","") for file_path in file_paths]
    file_paths = [file_path.replace(" ","") for file_path in file_paths]



except FileNotFoundError:
    file_paths = []

file_paths += paths




with open("%s/%s/file_path.txt"%(dir_path, results_dir_name), 'w') as fp: #is this needed still?
    fp.write(str(file_paths)) 





