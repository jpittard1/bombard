
import os
import shutil
import subprocess
import tools
import job_tracker
from numpy import array, sin, cos, tan, pi
from tqdm import tqdm

#################################################################################
##################### USER INPUTS, see README file. #############################
#################################################################################



    

def main():

    lammps_files_path =f"{tools.bombard_directory()}LAMMPS_files"

    #these settings below should all be elsewhere really
    #maybe a seperate input file? as there are multiple LAMMPS ones

    energy = 10
    temp = 300
    bombard_atom = 'd'
    repeats = 300
    angle = 45

    test =False
    hpc = True
    loaded = False
    grain = False
    multi_bombard = True
    single_atom = False
    orient = False

    pre_bomb_run_val = '3000' #this is changed if test == True, so must be changed here
                                #rather than the input file.
    bomb_run_val = "10000" #this is automatically increase for slow particles and must be
                        #changed here rather than the input file.
    post_bomb_run_val = '10000'
    number_of_particles = '1' #bombarding

    if loaded == True:  
        input_file_name = 'in.loaded_multi_bombard'
    if grain == True:
        input_file_name = 'in.final_pc'
   
    if multi_bombard == True:
        input_file_name = 'in.final_sc'

        if orient == True:
            input_file_name = 'in.final_orient_multi'
   

    if single_atom == True:
        repeats = 10

    atom_mass_dict = dict(  h = 1.0078,
                            d = 2.0141,
                            t = 3.0160,
                            other = 10,
                            cluster = 2.98*2.0141)

    if test == True:
        repeats = 3
        hpc = False
        number_of_particles = '1'
        energy = 40
        pre_bomb_run_val = 100
        post_bomb_run_val = 100


    ##################################################################################
    ######################## Reading and Editing Input File ##########################
    ##################################################################################


    in_file = tools.file_proc("%s/%s"%(lammps_files_path, input_file_name))  


    paths = []
    #data_files = ['data.graphite_sheet']

    bombard_dir = tools.bombard_directory()
    input_file_obj = tools.Input_files(f'{bombard_dir}/LAMMPS_files/{input_file_name}')
    data_filename= input_file_obj.get_data_filepaths()[0].split('/')[-1]
    input_file_obj.edit('read_data', new_line = f'{bombard_dir}/LAMMPS_files/{data_filename}',occurance=0)


    if orient == True:
        diamond_type = data_filename.split('_')[1]
    else:
        diamond_type = '100'

    data_filepath = input_file_obj.get_data_filepaths()[0]
    data_file_obj = tools.Data_file(data_filepath)
    data_file_obj.update_masses(atom_mass_dict[bombard_atom])

    bombard_atom_type = input_file_obj.input_dict['set'][0][-1]
    bombard_atom_mass = data_file_obj.atom_masses[bombard_atom_type]
    unit_conv = 1e-2*(1.602e-19/1.661e-27)**0.5
    velocity = ((2*energy/bombard_atom_mass)**0.5)*unit_conv 

    x_width = data_file_obj.limits['x'][1]*input_file_obj.replicate[0]
    y_width = data_file_obj.limits['y'][1]*input_file_obj.replicate[1]
    z_length = data_file_obj.limits['z'][1]*input_file_obj.replicate[2] - 3.567

    virtual_replicate = [round(width/3.567) for width in ([x_width,y_width,z_length+3.567])]

    central = True
    if central == True:
        x_lo, y_lo = (array([x_width,y_width]) - 3*3.567)/2
        x_hi, y_hi = (array([x_width,y_width]) + 3*3.567)/2
        
    else:
        x_lo, y_lo = [0, x_width]
        x_hi, y_hi = [0, y_width]

    angleimplant = tools.AngleImplant(theta = angle, replicate=virtual_replicate)

    initial_position = angleimplant.find_xy()
    velocity_arr = array([sin(pi/2 - angleimplant.theta_rad)*cos(angleimplant.phi), 
                         sin(pi/2 - angleimplant.theta_rad)*sin(angleimplant.phi), 
                         cos(pi/2 - angleimplant.theta_rad)])*velocity
    
    if number_of_particles == '1':
        input_file_obj.edit('create_atoms', new_line=f'3 single {initial_position[0]} {initial_position[1]} {initial_position[2]}')

    input_file_obj.edit('region', new_line = f'top block 0 {x_width} 0 {y_width} 0 {z_length}',second_val='top')
    input_file_obj.edit('region', new_line = f'box block {x_lo} {x_hi} {y_lo} {y_hi} -55.0 -25.0',second_val='box')

    input_file_obj.edit('variable', new_line=f'd uloop {number_of_particles}',occurance=0)
    input_file_obj.edit('pair_coeff', new_line=f'* * {bombard_dir}/LAMMPS_files/CH.rebo C H H')

    input_file_obj.edit('set', new_line = f'group newH vx {velocity_arr[0]} vy {velocity_arr[1]} vz {velocity_arr[2]}',occurance=-1)

    input_file_obj.edit('fix', new_line = f'1 all nvt temp {temp} {temp} 0.1',second_val='1')
    input_file_obj.edit('run', new_line=f'{pre_bomb_run_val} #prebombardment', occurance=0)
    input_file_obj.edit('run', new_line=f'{post_bomb_run_val} #postbombardment', occurance=2)

    #input_file_obj.update_seeds(single_atom = single_atom, temp = temp)
    #input_file_obj.publish(path = f'{bombard_dir}/LAMMPS_files/{input_file_name}', overwrite = True)

    input_file_obj.create_repeats(repeats, temp = temp, angle=angle, 
                                  virtual_replicate=virtual_replicate, velocity=velocity)



    count = 1

    while True: #creating new directory 
            try:
                if multi_bombard == True:
                    new_path = f'{bombard_dir}/results/{bombard_atom}_{energy}eV_{number_of_particles}_{repeats}r_{count}'
                elif loaded == True:
                    new_path = f'{bombard_dir}/results/{bombard_atom}_loaded_{energy}eV_{number_of_particles}_{repeats}r_{count}'

                elif grain == True:
                    new_path = f'{bombard_dir}/results/{bombard_atom}_grain_{energy}eV_{number_of_particles}_{repeats}r_{count}'
                
                elif orient == True:
                    new_path = f'{bombard_dir}/results/{bombard_atom}_{diamond_type}_{energy}eV_{number_of_particles}_{repeats}r_{count}'

                elif single_atom == True:
                    new_path = f'{bombard_dir}/results/{bombard_atom}_{energy}eV_{repeats}r_{count}/'

                
                os.mkdir(new_path)
                break

            except FileExistsError:
                count += 1 



    for repeat, repeat_input in enumerate(tqdm(input_file_obj.repeated_inputs, desc= 'Generating result dirs')):

        with open(f"{input_file_obj.path}", 'w') as fp: #rewriting edited input file
            fp.write(repeat_input)

        full_new_path = f"{new_path}/{repeat}r"
        os.mkdir(full_new_path)

        shutil.copyfile(f"{bombard_dir}/LAMMPS_files/{data_file_obj.name}", f"{full_new_path}/{data_file_obj.name}")    
        shutil.copyfile(f"{bombard_dir}/LAMMPS_files/{input_file_name}", f"{full_new_path}/{input_file_name}")

        virtual_replicate = [round(width/3.567) for width in ([x_width,y_width,z_length+3.567])]

        settings_dict = dict(no_bombarding_atoms = number_of_particles, 
                            replicate = input_file_obj.replicate,
                            virtual_replicate = virtual_replicate, 
                            surface_area = float(x_width*y_width),
                            atom_mass = bombard_atom_mass,
                            diamond_type = diamond_type,
                            energy = energy,
                            temp = temp,
                            angle = angle,
                            atom_type = bombard_atom,
                            pre_bombard_time = pre_bomb_run_val,
                            bombard_time = bomb_run_val,
                            post_bombard_time = post_bomb_run_val,
                            loaded = loaded,
                            grain = grain,
                            multi_bombard = multi_bombard,
                            data_file = data_file_obj.name,
                            repeats = repeats
                            )
    
        tools.cvs_maker(full_new_path,settings_dict)
        paths.append(full_new_path)



        ##################################################################################


        ##################################################################################
        ############################ RUNNING SIMULTAION ##################################
        ##################################################################################


    for path in tqdm(paths, desc= 'Sending jobs'):
        if test == True:
            os.chdir(path)    
            os.system(f"lmp_serial -in {path}/{input_file_name}")

        if hpc == True and test == False:         
            shutil.copyfile(f"{bombard_dir}/LAMMPS_files/srun",f"{path}/srun") #copying srun avoids rewritting
            os.chdir(path)
            #os.system(f"sbatch {path}/srun")
            subprocess.run(['sbatch', f'{path}/srun'], stdout=subprocess.DEVNULL)  #submitted job via slurm

        if hpc == False and test == False: 
            os.chdir(path)    
            #os.system(f"mpiexec -n 2 lmp_serial -in {path}/{input_file_name}")
            subprocess(f"lmp_serial -in {path}/{input_file_name}")


    if hpc == True:
        
        folder_name = new_path.split('/')[-1]
        #folder_name = new_path.split('/')[-2:]
        #folder_name = str(folder_name[0]) + '/' + str(folder_name[1])

        if repeats > 1:
            repeat_bool = True
        else:
            repeat_bool = False

        job_tracker.Track(folder_name, repeats=repeat_bool)

    ###################################################################################





if __name__ ==  '__main__':



    main()
