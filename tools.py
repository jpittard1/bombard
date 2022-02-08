
from asyncore import file_dispatcher
import numpy as np
import math


def file_proc(file):
    """Short function to split text files into a list of lines"""

    opened_file = open(file, 'r')
    opened_file = opened_file.read()
    opened_file = opened_file.split("\n")
    return opened_file



def xyz_to_array(xyz_file_path):

    xyz_file = file_proc(f"{xyz_file_path}")

    atoms_arr = np.zeros([10000,4])
    indexes = []

    for i in xyz_file:
        line = i.split()
        if len(line) == 5: #store in array much faster
     
            index = int(line[0]) - 1 #so atom 1 is at 0th index
            atom_type_no = int(line[1])
            atoms_arr[index] = np.array([atom_type_no, float(line[2]), float(line[3]), float(line[4])]) 
            indexes.append(index)

    atoms = max(indexes)
    atoms_arr = atoms_arr[:atoms+1, :]

    return atoms_arr



def region_assign(initial, loaded = False):
        
    initial_atoms_arr = np.zeros([5000,4])
    indexes = []

    region_indexes = dict(diamond_surface = [], diamond_bulk = [], graphene_all = [],
                        graphene_1 = [])

    for i in initial:
        line = i.split()
        if len(line) == 5: #store in array much faster
            index = int(line[0]) - 1 #so atom 1 is at 0th index
            atom_type_no = int(line[1])
            z = float(line[4])
            initial_atoms_arr[index] = np.array([atom_type_no, float(line[2]), float(line[3]), z]) 
            indexes.append(index)

            if loaded == False:        
                if z == 0:
                    region_indexes['diamond_surface'].append(index)

                if z > 0:
                    region_indexes['diamond_bulk'].append(index)
                
                if z < 0:
                    region_indexes['graphene_all'].append(index)
                    
                    layer = -int((z - 1.675)/3.35)
                    layer_key = 'graphene_%s'%layer

                    try:
                        region_indexes[layer_key].append(index)
                    except KeyError:
                        region_indexes[layer_key] = [index]
            
            else:
                if atom_type_no == 1:
                    region_indexes['diamond_bulk'].append(index)
    
    
    atoms = max(indexes)
    initial_atoms_arr = initial_atoms_arr[:atoms+1, :]

    return initial_atoms_arr, region_indexes


def magnitude(vector):
    return math.sqrt((vector[0]**2 + vector[1]**2 + vector[2]**2))

def avg(data):
    return np.average(data), np.std(data)

def input_misc(message, allowed_values):
    while True:

        option = input(message)

        if allowed_values == None:
            break

        if option in allowed_values or option == 'q':
            break

        else:
            print("\nInvalid Option.")

    return option

 
def cvs_maker(path, dictionary):
    f = ''

    for key in dictionary:
        f += '%s; %s\n'%(key, dictionary[key])

    with open ("%s/settings.csv"%path, 'w') as fp: #writing new data file
        fp.write(f) 
        

def csv_reader(csv_path):
    
    settings_str = file_proc(csv_path)
    settings_dict = dict()

    for i in settings_str:
        try:
            i = i.split('; ')
            key, item = i
        except ValueError:
            break

        while True:

            try:
                item = float(item) 
                break   
            except ValueError:
                pass


            if item[0] == "{":
                dict_item = dict()
                item = item.replace("{", "")
                item = item.replace("}", "")
                item = item.split(', ')
                
                for subitem in item:
                    key, value = subitem.split(': ')
                    dict_item[key] = value

                item = dict_item
                break

            
            if item[-1] == "]":
                list_item = []
                item = item.replace("[", "")
                item = item.replace("]", "")
                item = item.replace("'", "")

                item = item.split(',')

                list_item = [float(subitem) for subitem in item]

                item = list_item
                break

            break


        settings_dict[key] = item

    return settings_dict

