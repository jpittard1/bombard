
import numpy as np
import math



def file_proc(file, seperator = "\n"):
    """Short function to split text files into a list of lines"""

    opened_file = open(file, 'r')
    opened_file = opened_file.read()
    opened_file = opened_file.split(seperator)
    return opened_file


def str_to_arr(string):

    string = string.split('\n')

    for index, line in enumerate(string):

        try:
            if line[0] == '[':
                break
        except IndexError:
            pass

        try:
            float(line.split(' ')[0])
            break
        except ValueError:
            try:
                float(line.split(', ')[0])
                break
            except ValueError:
                pass




    string = string[index:]
    
    columns = len(string[0].split(' '))
    arr = np.zeros([len(string), columns])

   
    if string[0].split(' ')[-2][-1] == ',':
        commas = True

    for index, line in enumerate(string):

        try:
            if line[0] == '[':
                line = line[1:]
            if line[-1] == ']':
                line = line [:-1]
        except IndexError:
            pass

        if commas == True:
            line = line.split(', ')
        if commas == False:
            line = line.split(' ')

        if len(line) > 1:
            line = [float(i) for i in line]
            arr[index,:] = np.array(line)

    return arr




def str_to_list(string, float_vals = False):

    if string[0] != '[' or string[-1] != ']':
        raise TypeError(f'{string} is not a list.')
        

    string = string[1:-1]
    out_list = string.split(',')

    if float_vals == True:
        out_list = [float(i) for i in out_list]

    return out_list

def str_to_bool(string):

    if string == 'True' or string == 'False':
        return bool(string)

    else:
        raise TypeError(f'{string} is not a boolean.')

def str_to_float(string):

    try:
        return float(string)
    except ValueError:
        raise TypeError


def closest_to(val, list_):
    abs_vals = [abs(i-val) for i in list_]
    return list_[abs_vals.index(min(abs_vals))]



def time_convert(val, time_to_sec = False, sec_to_time = False, time_of_day = False):
    if time_to_sec == True:
        hh_mm_ss = val.split(':')
        hh_mm_ss.reverse()
        secs = [float(val)*(60**index) for index,val in enumerate(hh_mm_ss)]
        return sum(secs)
    
    if sec_to_time == True:
        if time_of_day == True:
            hh = str(int(val/3600)%24)
        else:
            hh = str(int(val/3600))
        mm = str(int((val%3600)/60))
        ss = str(int((val%3600)%60))

        if len(hh) != 2:
            hh = '0' + hh
        if len(mm) != 2:
            mm = '0' + mm
        if len(ss) != 2:
            ss = '0' + ss

        return f"{hh}:{mm}:{ss}"

def time_add(time1_str, time2_str, add = True, subtract = False, time_of_day = False):
    time1 = time_convert(time1_str, time_to_sec=True)
    time2 = time_convert(time2_str, time_to_sec=True)

    if add == True:
        return time_convert(time1+time2, sec_to_time=True, time_of_day=time_of_day)

    if subtract == True:
        return time_convert(time1-time2, sec_to_time=True, time_of_day=time_of_day)

def xyz_to_array(xyz_file_path):

    xyz_file = file_proc(f"{xyz_file_path}")
    atoms = int(xyz_file[0])
    atoms_arr = np.zeros([atoms,4])
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

def mkdir(path):
    import os

    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def custom_to_dict(dump_path):

    dump_file = file_proc(f"{dump_path}", seperator="ITEM: ")
    dump_file.remove("")

    print(f"\nOpening: {dump_path}")

    timestep = float(dump_file[0].split("\n")[1])
    number_of_atoms = float(dump_file[1].split("\n")[1])

    atoms_string = dump_file[3].split("\n")
    atoms_string.remove("")
    
    column_titles = atoms_string[0].split()[1:]

    info_array = np.ones([int(number_of_atoms)*2, len(column_titles)])*10000

    for index,line in enumerate(atoms_string[1:]):

        line = line.split(" ")

        try:
            line.remove("")
        except ValueError:
            pass

        line = [float(item) for item in line]
        
        info_array[index] = np.array(line) 


    to_delete = [index for index,line in enumerate(info_array) if line[0] == 10000]
    
    info_array = np.delete(info_array, to_delete, 0)


    results_dict = dict(lammps_timestep = timestep,
                    number_of_atoms = number_of_atoms,
                    column_titles = column_titles,
                    info_array = info_array
                    )

    return results_dict


def array_column_select(arr, columns):

    new_arr = np.zeros([len(columns), arr.shape[1]])

    for i, index in enumerate(columns):
        new_arr[i] = arr[:,index]

    return new_arr

def region_assign(initial, loaded = False):
        
    initial_atoms_arr = np.zeros([int(initial[0]),4])
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

 
def cvs_maker(path, dictionary, write = True):
    f = ''

    for key in dictionary:
        f += '%s; %s\n'%(key, dictionary[key])

    if write == True:
        with open ("%s/settings.csv"%path, 'w') as fp: #writing new data file
            fp.write(f) 
    
    else:
        return f
        

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

                try:
                    list_item = [float(subitem) for subitem in item]
                except ValueError:
                    list_item = item

                item = list_item
                break

            break


        settings_dict[key] = item

    return settings_dict

def time_percentage(current, total):

    def convert_to_seconds(time):
       
        times = time.split(':')
        times = [int(time) for time in times]

        if len(times) == 3:
            return times[0]*3600 + times[1]*60 + times[2]
        if len(times) == 2:
            return times[0]*60 + times[1]


    current_s = convert_to_seconds(current)
    total_s = convert_to_seconds(total)

    return current_s*100/total_s