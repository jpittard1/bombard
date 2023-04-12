




import numpy as np
import tools
import glob
from tqdm import tqdm
from pprint import pprint
import sys

def update_settings(paths):

    for path in tqdm(paths):
        settings_dict = tools.csv_reader(f"{path}settings.csv")

        try:
            settings_dict['measured_angle']
            settings_dict['measured_energy']
       
        except KeyError:
            input_file = tools.Input_files(f"{path}in.final_sc")

            velocity_line = input_file.get('set', occurance=-1)

            velocities = [velocity_line[-5], velocity_line[-3], velocity_line[-1]]
            velocity_arr = np.array([float(i) for i in velocities])

            v_mag = np.linalg.norm(velocity_arr)

            angle = np.arcsin(velocity_arr[-1]/v_mag)
            energy = (1.661e-27 * 0.5*settings_dict['atom_mass']*(100*v_mag)**2) / 1.602e-19

            settings_dict['measured_energy'] = f"{energy:.2f}"
            settings_dict['measured_angle'] = f"{(angle*180/np.pi):.2f}"

            tools.cvs_maker(path,settings_dict, write = True)


def update_combined_results(paths, overwrite = False):

    combined_not_found = []
    settings_not_found = []

    for path in tqdm(paths):

        try:
            analysis_files = dict(damage = tools.file_proc(f"{path}combined_damage.csv"),
                                depth = tools.file_proc(f"{path}combined_depth.csv"),
                                ovito = tools.file_proc(f"{path}combined_ovito.csv"))
        except FileNotFoundError:
            combined_not_found.append(path)
            continue
        
        for key in analysis_files.keys():

            try:
                analysis_files[key].remove('')
            except ValueError:
                pass

            analysis = analysis_files[key]

            for i, line in enumerate(analysis):
     
                line = line.split(', ')
                
                if i == 0:
                    angle = 'angle'
                    mass = 'atom_mass'
                    temperature = 'temperature'
                else:
                    try:
                        settings_dict = tools.csv_reader(f"{path}{line[0]}/0r/settings.csv")

                        try:
                            angle = settings_dict['measured_angle']
                            mass = settings_dict['atom_mass']
                            temperature = settings_dict['temp']

                        except KeyError:
                            raise KeyError(f"Update settings in {path}")
                        
                    except FileNotFoundError:
                        settings_not_found.append(path)
                        continue

                line.insert(3, str(angle))
                line.insert(3, str(mass))
                line.insert(3, str(temperature))

                sep = ', '
                analysis[i] = sep.join(line)

            sep = '\n'
            analysis = sep.join(analysis)


            with open(f"{path}/combined_{key}_update.csv", 'w') as fp:
                fp.write(analysis)


    print(f"\n\nCould not find one or more combined files here:\n\n ")
    pprint(combined_not_found)

    print(f"\n\n\nCould not find one or more settings here:\n\n ")
    pprint(settings_not_found)

           



def main(args_dict):

    #Doesnt like * notation as terminal argument, need to have it search through recursive folders to find settings

    args_dict['path'] = tools.bombard_directory() +  tools.Path(args_dict['path'])


    all_paths = []
    for i in range(10):

        paths = [tools.Path(path)[:-1] for path in glob.glob(f"{args_dict['path']}{'*/'*i}settings.csv")]
        print(f"{args_dict['path']}{'*/'*i}settings.csv")
     
        all_paths += paths


    print(all_paths)


    if len(all_paths) == 0:
        raise NameError(f"Could not find {args_dict['path']}settings.csv")

    else:
        update_settings(all_paths)

        paths = [str(path[:-2]) for path in all_paths]
        paths = [tools.Path(path) for path in list(set(all_paths))]

        update_combined_results(all_paths)





if __name__ == "__main__":

    accepted_args = ['path']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')

    main(args_dict)

