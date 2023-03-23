




import numpy as np
import tools
import glob
from tqdm import tqdm


path_ = tools.bombard_directory() +  tools.Path('results/repeats/')
paths = [tools.Path(path) for path in glob.glob(f"{path_}*/*/*r")]
mass_u = 2.0141

for path in tqdm(paths):
    input_file = tools.Input_files(f"{path}in.final_sc")

    velocity_line = input_file.get('set', occurance=-1)

    velocities = [velocity_line[-5], velocity_line[-3], velocity_line[-1]]
    velocity_arr = np.array([float(i) for i in velocities])

    v_mag = np.linalg.norm(velocity_arr)

    angle = np.arcsin(velocity_arr[-1]/v_mag)
    energy = (1.661e-27 * 0.5* mass_u*(100*v_mag)**2) / 1.602e-19

    settings_dict = tools.csv_reader(f"{path}settings.csv")

    settings_dict['measured_energy'] = f"{energy:.2f}"
    settings_dict['measured_angle'] = f"{(angle*180/np.pi):.2f}"

    tools.cvs_maker(path,settings_dict)


