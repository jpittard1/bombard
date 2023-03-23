

from numpy import array, ones, zeros, average, std, delete, sin, cos, tan, pi
from math import sqrt
from os import path, mkdir
from random import random, randint, uniform
from pprint import pprint
from glob import glob

def file_proc(file, seperator = "\n"):
    """Short function to split text files into a list of lines"""

    opened_file = open(file, 'r')
    opened_file = opened_file.read()
    opened_file = opened_file.split(seperator)
    return opened_file

class Path:

    def __init__(self, path):

        self.path = self.dir_check(f"{path}")

        self.sep = '/'

    def __repr__(self) -> str:
        return self.path

    def __getitem__(self, index):
        if self.path[-1] == '/':
            trimmed_path = self.path.split('/')[:-1][index]
        else:
            trimmed_path = self.path.split('/')[index]
        if type(trimmed_path) == list:
            return Path(self.sep.join(trimmed_path))
        else:
            return trimmed_path
    
    def __add__(self, string):
        return Path(f"{self.path}{string}")

    def dir_check(self, path_arg):
            try:
                split_path_arg = str(path_arg).split('/')
                
                if split_path_arg[-1] != '':
                    split_path_arg[-1].index('.')
                    self.type = 'file'
                
                
            except ValueError:
                path_arg += '/'
                self.type = 'directory'
      
            return path_arg
    
    



class AngleImplant:

    def __init__(self, theta, replicate, z = 3*3.567):
        self.theta_deg = theta
        self.theta_rad = theta*pi/180
        self.replicate = replicate
        self.x_width = replicate[0]*3.567
        self.y_width = replicate[1]*3.567
        self.z = z


    def find_xy(self):

        target_pos = array([uniform(3.567,4*3.567),uniform(3.567,4*3.567),0])
        phi = uniform(0,2*pi)

        self.phi = phi

        x_mov = self.z*cos(phi)/tan(self.theta_rad)
        y_mov = self.z*sin(phi)/tan(self.theta_rad)

        initial_pos = target_pos - array([x_mov, y_mov, self.z])
        initial_pos[0] = initial_pos[0]%self.x_width
        initial_pos[1] = initial_pos[1]%self.y_width

        return initial_pos




        

class Input_files():

    def __init__(self,input_file_path):

        self.path = input_file_path

        self.split_input = file_proc(input_file_path)

        self.input_dict, self.line_index_dict = self.input_to_dict()
        self.input_str = self.dict_to_input()

        self.replicate = [int(i) for i in self.get('replicate')]
    
    def input_to_dict(self):

        full_dict = dict()
        line_index_dict = dict()

        for i, line in enumerate(self.split_input):

            line = line.split()
    
            try:
                full_dict[line[0]].append(line[1:])
                line_index_dict[i] = line[0]

            except KeyError:
                full_dict[line[0]] = [line[1:]]
                line_index_dict[i] = line[0]

            except IndexError:
                pass

        return full_dict, line_index_dict

    def dict_to_input(self):

        output_str = ''
        space = ' '

        #Creating a copy of the input dict
        #Required to ensure repeated command are included in the right order
        input_dict_scrap = dict()

        for key in self.input_dict.keys():
            input_dict_scrap[key] = self.input_dict[key]


        #Looping through line indexes
        for index in self.line_index_dict.keys():
          
            key = self.line_index_dict[index]
   
            if key[0] == '#':
                output_str += '\n\n'

            else:
         
                output_str += f'{key}   {space.join(input_dict_scrap[key][0])}\n'

                input_dict_scrap[key] = input_dict_scrap[key][1:]

        
        self.input_str = output_str
        return output_str

    def publish(self,path = None, overwrite = False):
        if path == None:
            bombard_dir = bombard_directory()
            path = f'{bombard_dir}/in.new_input'
        
        if overwrite == True:
            with open(f"{path}", 'w') as fp: #rewriting edited input file
                fp.write(self.input_str)

        else:
            count = 0
            while count < 10:
                try:
                    open(f"{path}_{count}")
                    count += 1

                except FileNotFoundError:
                    with open(f"{path}_{count}", 'w') as fp: #rewriting edited input file
                        fp.write(self.input_str)
                        break

    def edit(self, command, new_line, occurance = 0, second_val = None):

        new_line_list = new_line.split()
        
        if second_val != None:
            for occurance, line_list in enumerate(self.input_dict[command]):
                if second_val == line_list[0]:
                    break

        self.input_dict[command][occurance] = new_line_list

        self.dict_to_input()

    def update_seeds(self, single_atom, temp = 300):

        self.edit('velocity',  f'cmov create {temp} {int(random()*100000)} rot yes dist gaussian', second_val = 'cmov')

        if single_atom == False:
            self.edit('create_atoms', f'3 random 1 $d{randint(1,9)} box')


    def update_velocity(self, angle, virtual_replicate, velocity):

        angle_implant_obj = AngleImplant(theta=angle, replicate=virtual_replicate)

        initial_position = angle_implant_obj.find_xy()
        velocity_arr = array([sin(pi/2 - angle_implant_obj.theta_rad)*cos(angle_implant_obj.phi), 
                         sin(pi/2 - angle_implant_obj.theta_rad)*sin(angle_implant_obj.phi), 
                         cos(pi/2 - angle_implant_obj.theta_rad)])*velocity

        self.edit('create_atoms', new_line=f'3 single {initial_position[0]} {initial_position[1]} {initial_position[2]}')
        self.edit('set', new_line = f'group newH vx {velocity_arr[0]} vy {velocity_arr[1]} vz {velocity_arr[2]}',occurance=-1)
        


    def get_data_filepaths(self):
        return [file for outer in self.input_dict['read_data'] for file in outer]

    def create_repeats(self, repeats, temp, angle, virtual_replicate, velocity):
        if repeats == 1:
            single_atom = False
        else:
            single_atom = True


        self.repeated_inputs = []
        for repeat in range(repeats):
            self.update_seeds(single_atom=single_atom, temp = temp)
            self.update_velocity(angle, virtual_replicate, velocity)
            self.repeated_inputs.append(self.input_str)


        return self.repeated_inputs

    def get(self, key, occurance = 0, second_val = None, all = False):
        if len(self.input_dict[key]) == 1:
            return self.input_dict[key][0]
       
        elif all == True:
            return self.input_dict[key]

        elif second_val == None:
            return self.input_dict[key][occurance]
        
        elif second_val != None:
            for i, val in enumerate(self.input_dict[key]):
                if val[0] == second_val:
                    return self.input_dict[key][i]


def path_check(path):

    try:
        open(path)
        return True
    except FileNotFoundError:
        return False

class Data_file:

    def __init__(self, data_file_path):

        self.path = data_file_path
        self.name = data_file_path.split('/')[-1]
        self.split_data_file = remove_blanks(file_proc(data_file_path))

        self.atom_lines = None
        self.atom_masses = None
        self.limits = None
        self.number_of_atom_types = None
        self.number_of_atoms = None

        self.data_to_dict()

    def data_to_dict(self):
        data_file_dict = dict()
        line_dict = dict()

        atoms_index = self.split_data_file.index('Atoms')
        self.atom_lines = self.split_data_file[atoms_index:]
        

        for i, line in  enumerate(self.split_data_file[:atoms_index]):
            
            if line != '\n':

                line = line.split()

                if line[-1] == 'atoms':
                    self.number_of_atoms = int(line[0])

                elif line[-1] == 'types':
                    self.number_of_atom_types = int(line[0])

                    lims_dict = dict(x = None,
                                    y = None,
                                    z = None)

                    for item, key in enumerate(lims_dict.keys()):

                        dimension_limit_line = self.split_data_file[i+item+1].split()
                        lims_dict[key] = [float(i) for i in dimension_limit_line[:2]]
                    
                    self.limits = lims_dict


                elif line[0] == 'Masses':
                
                    atom_dict = dict()
                    for item in range(1, self.number_of_atom_types+1):

                        atom_dict[str(item)] = float(self.split_data_file[i+item].split()[-1])
                    
                    self.atom_masses = atom_dict

    def update_masses(self, bombard_atom_mass):

        for i, line in  enumerate(self.split_data_file):

            if line != '\n':
                line = line.split()

                if line[0] == 'Masses':
                    
                    self.split_data_file[i+2] = f'2 {bombard_atom_mass}'
                
                    self.atom_masses['2'] = bombard_atom_mass

                    break

        self.publish()

    def formatting(self):

        sep = ' '

        for i, line in  enumerate(self.split_data_file):

            line = line.split()

            if line[-1] == 'atoms':
                self.split_data_file[i] = '\n' + sep.join(line) + '\n'

            elif line[-1] == 'types':
                self.split_data_file[i] =  sep.join(line) + '\n'

            elif line[-1] == 'Masses':
                self.split_data_file[i] =  '\nMasses\n'

            elif line[-1] == 'Atoms':
                self.split_data_file[i] = '\nAtoms\n'
        
    def publish(self):

        self.formatting()
        
        sep = '\n'
    
        with open(f"{self.path}", 'w') as fp: #rewriting edited input file
            fp.write(sep.join(self.split_data_file))
        



   



def repeat_check(path):
    
    repeats = glob(f"{path}/*r")
    if len(repeats)>0:
        return True
    else:
        return False

    







def remove_blanks(input_list, to_remove = '', replace = None):

    if replace != None:
        for i, val, in enumerate(input_list):
            if val == to_remove:
                input_list[i] = replace
    
    else:
        for i in input_list:
            try:
                input_list.remove(to_remove)
            except ValueError:
                break
    
    return input_list


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
    
    columns = len(string[0].split())
 
    arr = ones([len(string), columns])*111

   
    if string[0].split(' ')[-2][-1] == ',':
        commas = True

    if len(string[0].split(',')) >1:
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
            arr[index,:] = array(line)

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

    output = dict(true = True, false = False)
    try:
        return output[string.lower()]
    except KeyError:
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


def bombard_directory():
    return Path(path.dirname(path.realpath(__file__)))

def time_add(time1_str, time2_str, add = True, subtract = False, time_of_day = False):
    time1 = time_convert(time1_str, time_to_sec=True)
    time2 = time_convert(time2_str, time_to_sec=True)

    if add == True:
        return time_convert(time1+time2, sec_to_time=True, time_of_day=time_of_day)

    if subtract == True:
        return time_convert(time1-time2, sec_to_time=True, time_of_day=time_of_day)


def custom_to_array(split_dump_file):
    """Custom file dump file to array"""
    for i, line in enumerate(split_dump_file):
        line = line.split()
        try:
            if line[1] == "NUMBER":
                no_of_atoms = int(split_dump_file[i+1])

            elif line[0] == "ITEM:" and line[1] == "ATOMS":
                titles = line[2:]
                out_arr = zeros([no_of_atoms,int(len(line)-2)])
                
                for i2, line in enumerate(split_dump_file[i+1:]):
                    line = line.split()

                    out_arr[i2] = array([float(x) for x in line])
        except IndexError:
            pass

    return out_arr, titles






def xyz_to_array(xyz_file_path, line_length = 5):

    xyz_file = file_proc(f"{xyz_file_path}")
    atoms = int(xyz_file[0])
    atoms_arr = zeros([atoms,4])
    indexes = []

    index = -1
    for i in xyz_file:
        line = i.split()
        if len(line) == line_length: #store in array much faster
     
            try:
                index = int(line[-5]) - 1 #so atom 1 is at 0th index
            except IndexError:
                index +=1
            atom_type_no = int(line[-4])
            atoms_arr[index] = array([atom_type_no, float(line[-3]), float(line[-2]), float(line[-1])]) 
            indexes.append(index)

    atoms = max(indexes)
    atoms_arr = atoms_arr[:atoms+1, :]

    return atoms_arr

def make_dir(path):

    try:
        mkdir(path)
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

    info_array = ones([int(number_of_atoms)*2, len(column_titles)])*10000

    for index,line in enumerate(atoms_string[1:]):

        line = line.split(" ")

        try:
            line.remove("")
        except ValueError:
            pass

        line = [float(item) for item in line]
        
        info_array[index] = array(line) 


    to_delete = [index for index,line in enumerate(info_array) if line[0] == 10000]
    
    info_array = delete(info_array, to_delete, 0)


    results_dict = dict(lammps_timestep = timestep,
                    number_of_atoms = number_of_atoms,
                    column_titles = column_titles,
                    info_array = info_array
                    )

    return results_dict


def array_column_select(arr, columns):

    new_arr = zeros([len(columns), arr.shape[1]])

    for i, index in enumerate(columns):
        new_arr[i] = arr[:,index]

    return new_arr

def region_assign(initial):
        
    initial_atoms_arr = zeros([int(initial[0]),4])
    indexes = []

    region_indexes = dict(diamond_surface = [], diamond_bulk = [])

    for line in initial:
        line = line.split()
        if len(line) == 5: #store in array much faster
            
            index = int(line[0]) - 1 #so atom 1 is at 0th index
            initial_atoms_arr[index] = array([int(line[1]), float(line[2]), float(line[3]),  float(line[4])]) 
            indexes.append(index)
        
            if float(line[4]) <= 0:
                region_indexes['diamond_surface'].append(index)

            if float(line[4]) > 0:
                region_indexes['diamond_bulk'].append(index)
            
    
    atoms = max(indexes)
    initial_atoms_arr = initial_atoms_arr[:atoms+1, :]

    return initial_atoms_arr, region_indexes


def magnitude(vector):
    return sqrt((vector[0]**2 + vector[1]**2 + vector[2]**2))

def avg(data):
    return average(data), std(data)

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

def args_to_dict(args, accecpted_args):
    '''Converts command line arguments into a dictionary from standard form.'''

    arg_dict = dict()

    for arg in accecpted_args:
        arg_dict[arg] = None

    for i, arg in enumerate(args):
        if arg[0] == '-':
            key = arg[1:]

            try:
                test = arg_dict[key]
                try:
                    if args[i+1][0] == '-':
                        arg_dict[arg[1:]] = True

                    else:
                        arg_dict[arg[1:]] = args[i+1]

                except IndexError:
                    arg_dict[arg[1:]] = True

            except KeyError:
                print('\nValid arguments: ')
                pprint(arg_dict)
                print('\n')
                raise KeyError(f'{arg[1:]} is not a valid argument.') from None

    return arg_dict
    

 
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



def all_splitter(path, start_end_only = True):

    frames = file_proc(f"{path}all.xyz", seperator='\n\n')

    try:
        mkdir(f'{path}/xyz_files')
    except FileExistsError:
        pass

    if start_end_only == True:
        frames = [frames[0], frames[-2]]

    for i, frame in enumerate(frames):

        split_frame = frame.split('\n')
    
        try:
            timestep = split_frame[1]
 
            with open(f"{path}/xyz_files/{timestep}.xyz", 'w') as fp:
                fp.write(frame)

        except IndexError:
            pass



