
from collections import namedtuple
import sys
import os
import numpy as np
from tools import csv_reader

#Converts all.xyz into form that can be read by Jmol
#Takes 100 frames thorughout the simulation
#Ensures first and last are used
#Originally in DEV_atom_track_multi.py

#TODO Checks:
    #Check number of atoms is correct
    #Make atoms arr the right size

class Frame():

    def __init__(self, time, atoms, atoms_arr):
        self.time  = time
        self.atoms = atoms
        self.atoms_arr = atoms_arr


    def present_arr(self, jmol = False):

        frame = ''
        frame += '%s'%self.atoms
        frame += '\nAtoms. Timestep. %s'%self.time
        
        if jmol == True:
            for atom in range(self.atoms):
                frame += f"\n{int(self.atoms_arr[atom][0])} {self.atoms_arr[atom][1]} {self.atoms_arr[atom][2]} {self.atoms_arr[atom][3]}"

        else:
            for atom in range(self.atoms):
                frame += f"\n{int(atom+1)} {int(self.atoms_arr[atom][0])} {self.atoms_arr[atom][1]} {self.atoms_arr[atom][2]} {self.atoms_arr[atom][3]}"

        frame += '\n\n'

        return frame


def main(all_xyz_file_path):

    print("\n\nPROGRESS: Running jmol_convert.py") 

    try:
        split = sys.argv[2]
    except IndexError:
        split = 100

    print("%s/settings.csv"%all_xyz_file_path[:-8])
    settings_dict = csv_reader("%s/settings.csv"%all_xyz_file_path[:-8])

    frames = []

    all_xyz = open(all_xyz_file_path, 'r')
    all_xyz = all_xyz.read()

    all_xyz = all_xyz.split("ITEM: TIMESTEP")
    all_xyz.remove('')

    
    # Sampling 100 files, can be taken as an argument
    if len(all_xyz) < split:
        time_step_indices = range(0,len(all_xyz) - 1)
    else:
        time_step_indices = np.linspace(0, len(all_xyz) - 1, split)

    
    for i in time_step_indices:

        time_step_data = all_xyz[int(i)]

        time_step_data = time_step_data.split('\n')
        time_step_data.remove('')
 
        time = float(time_step_data[0])
        
        atoms_arr = np.zeros([10000,4])

        indexes = []

        for i in time_step_data:
            line = i.split()
            if len(line) == 5: #store in array much faster
                index = int(line[0]) - 1 #so atom 1 is at 0th index
                atom_type_no = int(line[1])
                atoms_arr[index] = np.array([atom_type_no, float(line[2]), float(line[3]), float(line[4])]) 
 
                indexes.append(index)

   
        atoms = max(indexes) + 1
      
        frame = Frame(time, atoms, atoms_arr)
        frames.append(frame)


   
    times = [frame.time for frame in frames]
    equilibrium_timestep = min(times, key=lambda x:abs(x- settings_dict['pre_bombard_time']))
    equilibrium_index = times.index(equilibrium_timestep)

    jmol_str = ''
    for frame in frames:
        jmol_str += frame.present_arr(jmol=True)

    print("\n\nPROGRESS: Generating xyz files.") 

    with open("%s/jmol_all.xyz"%(all_xyz_file_path[:-7]), 'w') as fp: #rewriting edited input file
        fp.write(jmol_str)
    
    with open("%s/initial.xyz"%(all_xyz_file_path[:-7]), 'w') as fp: #rewriting edited input file
        fp.write(frames[0].present_arr(jmol = True))

    with open("%s/initial_indexed.xyz"%(all_xyz_file_path[:-7]), 'w') as fp: #rewriting edited input file
        fp.write(frames[0].present_arr())

    with open("%s/final.xyz"%(all_xyz_file_path[:-7]), 'w') as fp: #rewriting edited input file
        fp.write(frame.present_arr(jmol = True))

    with open("%s/final_indexed.xyz"%(all_xyz_file_path[:-7]), 'w') as fp: #rewriting edited input file
        fp.write(frame.present_arr())

    with open("%s/equilibrium_indexed.xyz"%(all_xyz_file_path[:-7]), 'w') as fp: #rewriting edited input file
        fp.write(frames[equilibrium_index].present_arr())
    
    




if __name__ == "__main__":
   
    current_dir = os.path.dirname(os.path.realpath(__file__))

    dir_name = sys.argv[1]

    path = current_dir + '/results/' +  dir_name + "/all.xyz"

    try:
        main(path)
        print("\n\nProgress: jmol convert complete.")
        print("\n", "-"*20, '\n')

    except FileNotFoundError:
        print("\n\n")
        print("-"*60)
        print("\nERROR: Could not find all.xyz file.")
        print("\nPlease run lint.py to produce all.xyz.")
        print("\nFile path used: %s"%path)
        print("\n")
        print("-"*60)