

import steinhardt
import tools
import data_file_maker

import os
import sys
import matplotlib.pyplot as plt


class Steinhardt_Frame:

    def __init__(self, xyz_file):
        self.xyz_file = xyz_file
        self.time = int(float(xyz_file.split('\n')[1].split(" ")[-1]))
        

    def convert_to_datafile(self, path, name):
        data_file_maker.remove_h(self.xyz_file, path, name)

    def generate_paras(self, path, current_dir):
        os.chdir(path)
        os.system("lmp_serial -in in.steinhardt_calc")
        os.chdir(current_dir)


def main(file, steinhardt_settings_dict):

    current_dir = os.path.dirname(os.path.realpath(__file__))

    file = 'results/' + file
 
    path = f"{current_dir}/{file}/steinhardt_results"
    tools.mkdir(path)


    all_xyz = tools.file_proc(f"{current_dir}/{file}/jmol_all.xyz", seperator= "\n\n")
    xyz_files = [file.split("\n") for file in all_xyz] 
    xyz_files = [xyz_file for xyz_file in xyz_files if len(xyz_file) != 1]

    times = [float(xyz_file[1].split(' ')[-1]) for xyz_file in xyz_files]

    timestep_indexes = [i for i in range(1, len(times), int(len(times)/4))]

    times_to_plot = [times[i] for i in timestep_indexes]
    xyz_files_to_plot = [all_xyz[i] for i in timestep_indexes]

    frames = [Steinhardt_Frame(xyz_file) for xyz_file in xyz_files_to_plot]

    for frame in frames:

        frame.convert_to_datafile(f"{current_dir}/LAMMPS_files", 'data.frozen')

        os.system(f"cp {current_dir}/LAMMPS_files/in.steinhardt_calc {path}/in.steinhardt_calc")
        os.system(f"cp {current_dir}/LAMMPS_files/data.frozen_1 {path}/data.frozen_1")
        os.system(f"mv {current_dir}/LAMMPS_files/data.frozen_1.xyz {path}/{frame.time}.xyz")

        frame.generate_paras(path, current_dir)

        os.system(f"mv {path}/data.frozen_1 {path}/data.{frame.time}")
        os.system(f"mv {path}/new.para {path}/{frame.time}.para")


    file_dicts = [tools.custom_to_dict(f"{path}/{frame.time}.para") for frame in frames]
    file_arrs = [file_dict['info_array'] for file_dict in file_dicts]

    #avg_str, avg_dict, full_array = steinhardt.averages(file_arrs, center_only= True, zlims = [-20,0]) 
    #avg_str, avg_dict, full_array = steinhardt.averages(file_arrs, center_only= True) 
    avg_str, avg_dict, full_array = steinhardt.averages(file_arrs)

    steinhardt.histogram(full_array, path)

    array_str = 'z, Q4, Q6, Q8, Q10, Q12\n\n'
    for line in full_array:
        array_str += "\n" + str(line)


    with open(f"{path}/diamond_para_averages.txt", 'w') as fp:
        fp.write(avg_str) 

    with open(f"{path}/array.txt", 'w') as fp: 
        fp.write(array_str) 


    steinhardt.depth_profile(file_arrs, path, times = times_to_plot)


    tools.mkdir(f"{path}/graphs")
    tools.mkdir(f"{path}/xyz_files")
    tools.mkdir(f"{path}/lammps_files")


    os.system(f"mv {path}/*.xyz {path}/xyz_files/")
    os.system(f"mv {path}/*.png {path}/graphs/")
    os.system(f"mv {path}/*.para {path}/lammps_files/")
    os.system(f"mv {path}/data.* {path}/lammps_files/")
    os.system(f"mv {path}/in* {path}/lammps_files/")
    os.system(f"mv {path}/log* {path}/lammps_files/")



if __name__ == '__main__':

    steinhardt_settings_dict = dict(file = None,
                                    frames = 4,
                                    timesteps = [],
                                    line_plots = True,
                                    histograms = False)


    try:
        file = sys.argv[1]
    except IndexError:
        print("ERROR: No Filename Provided.")

    for arg in sys.argv:
        arg = arg.split('-')

        if arg[0] == 'frames':
            steinhardt_settings_dict['frames'] = float(arg[1])

        if arg[0] == 'timesteps':
            steinhardt_settings_dict['frames'] = float(arg[1])

        steinhardt_settings_dict[arg[0]] = arg[1]


    main(file)


####TODO######
#Sort out this cluster fuck
    #Get the steinhart stuff in one file and in a reasonable structure
    # Errors on most recent values seem too big considering the number of atoms it averaging over
    # Very similar values across the times, suggests large varience in single timestep
    #                                  




