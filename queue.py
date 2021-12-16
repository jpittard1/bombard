


import os 
import time
import shutil
import random

import graphene_maker as gmak
import tools

#################################################################################
##################### USER INPUTS, see README file. #############################
#################################################################################


dir_path = os.path.dirname(os.path.realpath(__file__))
lammps_files_path = "%s/LAMMPS_files"%dir_path
results_dir_name = 'results'
loaded = True
energy = 100
test = True
hpc = True  

if loaded == True:
    replicate = ['8','8','6']
    input_file_name = 'in.loaded_multi_bombard'
else:
    input_file_name = 'in.multi_bombard'

pre_bomb_run_val = '3000' #this is changed if test == True, so must be changed here
                            #rather than the input file.
bomb_run_val = "100" #this is automatically increase for slow particles and must be
                    #changed here rather than the input file.
number_of_particles = '375' #bombarding

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
data_files = []
    
new = ''
for i in in_file: #goes through the input file line by line both reading and editing
    index = in_file.index(i)
    i = i.split()
    seperator = ' '

    try:

        if i[0] == '#number_of_sheets':
            graphite_sheets = float(i[1])

        if i[0] == '#atom_type': #either 'h', 'd' or 't'
            atom_type = i[1]

        if i[0] == '#diamond_type':
            diamond_type = i[1]

        if i[0] == "variable":
            i[-1] = str(number_of_particles)
            in_file[index] = seperator.join(i)     

        if i[0] == 'read_data':
            
            file_path = i[1].split('/')

            if file_path[-1][:5] == 'data.':
                i[1] = f"{lammps_files_path}/{file_path[-1]}"
                data_files.append(file_path[-1])

            #if file_path[-1] == 'data.diamond':
            #    i[1] = "%s/data.diamond"%lammps_files_path
                
            #if file_path[-1] == 'data.graphite_sheet':
            #    i[1] = "%s/data.graphite_sheet"%lammps_files_path
                
        
            in_file[index] = seperator.join(i)

        

        if i[0] == 'pair_coeff':

            i[3] = "%s/CH.rebo"%lammps_files_path #setting file paths for lammps files
            in_file[index] = seperator.join(i)

        if i[0] == "set": #setting velocity line
    
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
        
        
        if i[0] == "replicate":
            replicate = i[1:]

            in_file[index] = seperator.join(i)



        if i[0] == "fix" and len(i[-1]) == 5: #changing random seed for each repeat
            rand = random.randint(10000,99999)
            i[-1] = str(rand)
            in_file[index] = seperator.join(i)

        if i[0] == "velocity" and i[1] == 'all' and i[2] == 'create': #changing random seed for each repeat
            rand = random.randint(10000,99999)
            i[4] = str(rand)
            in_file[index] = seperator.join(i)

        if i[0] == 'region' and i[1] == 'box': #creating region for bombardment atom to be created
            central = True                      #this is adjusted for number of graphene sheets
            diamond_size = 3.567
            graphene_thickness = 3.35

            if central == True:
                xlo, ylo = [float(replicate[i])*diamond_size*(-1) for i in range(0,2)]
                xhi, yhi = [(float(replicate[i]) + 1)*diamond_size for i in range(0,2)]

            else:
                xlo = 0
                xhi = float(replicate[0])*diamond_size
                ylo = 0
                yhi = float(replicate[1])*diamond_size

            zhi = -graphene_thickness*graphite_sheets - 25
            zlo = zhi - 30
            
            i = seperator.join(i[:3]) + " %s %s %s %s %s %s"%(xlo, xhi, ylo ,yhi,zlo,zhi)

            in_file[index] = i

        if i[0] == 'run' and i[2] == "#inbetween": 
            
            i[1] = bomb_run_val

            in_file[index] = seperator.join(i)

        if i[0] == 'run' and i[2] == '#prebombardment':

            i[1] = pre_bomb_run_val

            in_file[index] = seperator.join(i)

        #elif i[0] == 'run' and len(i) == 2:

         #   print(i)
          #  print(len(i))


           # post_bomb_val = i[1]
            #in_file[index] = seperator.join(i)

    except IndexError:                                    
        pass

    new += "%s\n"%in_file[index]

with open("%s/%s"%(lammps_files_path,input_file_name), 'w') as fp: #rewriting edited input file
    fp.write(str(new)) 

    print("NEW IN FILE: %s/%s"%(lammps_files_path,input_file_name))


#########################################################################################







#########################################################################################
################### Creating Graphene Data file and new directorys ######################
#########################################################################################


if atom_type == 'h':
    atom_mass = 1.0079
if atom_type == 'd':
    atom_mass = 2.0014
if atom_type == 't':
    atom_mass = 3.0160

#writes graphene data sheet for the specific simulation
#returns dictionary containing the number of bulk atoms in each region
#used for lattice displacement calculations


bulk_atoms_dict = gmak.main(data_file_path = "%s/data.graphite_sheet"%lammps_files_path, no_bombarding_atoms = number_of_particles, 
                            replicate = replicate, no_of_sheets = graphite_sheets, atom_mass = atom_mass)


count = 1
while True: #creating new directory 
    try:
        new_path = "%s/%s/%s_%sg_%s_%s_%s"%(dir_path, results_dir_name, atom_type, int(graphite_sheets), 
                                            f"{energy}eV", number_of_particles, count)
        os.mkdir(new_path)
        paths.append(new_path)
        #if count == 1:
        #    progress_markers_paths.append(new_path)
        break

    except FileExistsError:
        count += 1  

for data_file in data_files:
    shutil.copyfile(f"{lammps_files_path}/{data_file}", f"{new_path}/{data_file}")
    
shutil.copyfile("%s/%s"%(lammps_files_path, input_file_name), "%s/%s"%(new_path, input_file_name))


settings_dict = dict(no_bombarding_atoms = number_of_particles, 
                    replicate = replicate, 
                    no_of_sheets = graphite_sheets, 
                    atom_mass = atom_mass,
                    diamond_type = diamond_type,
                    bulk_atoms_dict = bulk_atoms_dict,
                    energy = energy,
                    atom_type = atom_type,
                    pre_bombard_time = pre_bomb_run_val,
                    bombard_time = bomb_run_val,
                    loaded = loaded
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

###################################################################################








with open("%s/%s/file_path.txt"%(dir_path, results_dir_name), 'w') as fp: #is this needed still?
    fp.write(str(paths)) 





