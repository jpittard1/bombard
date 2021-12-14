

import os
import shutil
import sys

class Reader:
    """Reads log, input and data file"""

    def __init__(self, path, log_file_path = None, data_file_path = None, in_file_path = None):
        self.path = path
        self.input_obj = Inputs()
        self.data_obj = Data()

        if log_file_path != None:
            self.log_file_path = log_file_path

        if in_file_path != None:
            self.in_file_path = in_file_path

        if data_file_path != None:
            self.data_file_path = data_file_path
        
    def log(self): #not currently being used

        if self.log_file_path != None:

            try:
                log_file = open(self.log_file_path, 'r')
                setattr(self.data_obj, "success", True)
            except FileNotFoundError:
                setattr(self.data_obj, "success", False)

            if self.data_obj.success == True:
                log_file = log_file.read()

                d_string = str(log_file)
                df = d_string.split("\n")
                df = list(filter(None, df))

                rows = []
                i = 0
                data = False
                titles = ["blank"]

                while i<len(df):

                    row = str(df[i])
                    row = row.split()

                    if row[0] == "Per":
                        titles = str(df[i+1])
                        titles = titles.split()
                        setattr(self.data_obj, "titles", titles)

                    if row[0] == "Loop":
                        data = False

                    if data == True:
                        try:
                            for item in row:
                                check = float(item)

                            rows.append(row)
                        except ValueError:
                            data = False
                            print(f"Could not read row: \n{row}")
                            
                        

                    if row[0] == titles[0]:
                        data = True
                    

                    i += 1

                if data == True:
                    setattr(self.data_obj, "complete", False)

                outputs = []

                for title in titles:      

                    index = titles.index(title)

                    variable = [float(row[index]) for row in rows if len(row) == len(titles)]
                    
                    self.data_obj.new_variable(title, variable)

        else:
            print("\nERROR: No log file found.\n")

    def data(self):

        if self.data_file_path != None:
            data_file = open(self.data_file_path, 'r')
            data_file = data_file.read()

            df = data_file.split("\n")
            df = list(filter(None, df))

            i = 0
            masses = []
            mass_data = False
            atom_data = False
            unit_mass = 0

            for row in df:

                row = str(row)
                row = row.split()

                if row[-1] == "atoms":
                    try:
                        no_of_atoms = float(row[0])
                    except ValueError:
                        print("ERROR: Could not read data file.")
                        setattr(self.data_obj, "data_file", False)
                        break

                if row[-1] == 'xhi':
                    xlo = float(row[0])
                    xhi = float(row[1])
                if row[-1] == 'yhi':
                    ylo = float(row[0])
                    yhi = float(row[1])
                if row[-1] == 'zhi':
                    zlo = float(row[0])
                    zhi = float(row[1])

                try:
                    volume = (xhi-xlo)*(yhi-ylo)*(zhi-zlo)
                except NameError:
                    volume = None
                    pass

                if atom_data == True:
                    try:
                        for atom in range(0,int(no_of_atoms)):
                            atom_type = int(row[1])
                            unit_mass += masses[atom_type-1]
                        
                        atom_data = False
                    
                    except ValueError:
                        print("ERROR: Could not read data file.")
                        setattr(self.data_obj, "data_file", False)

                if row[0] == "Atoms":
                    mass_data = False
                    atom_data = True

                if mass_data == True:
                    try:
                        masses.append(float(row[1]))
                    except ValueError:
                        print("ERROR: Could not read data file.")
                        setattr(self, "data_file", False)
                        break


                if row[0] == "Masses":
                    mass_data = True

            if unit_mass != 0:
                density = volume/unit_mass
            else:
                density = None

            setattr(self.data_obj, 'no_of_atoms', no_of_atoms)
            setattr(self.data_obj, 'masses', masses)
            setattr(self.data_obj, 'unit_mass', unit_mass)
            setattr(self.data_obj, 'box_volume', volume)
            setattr(self.data_obj, 'box_density', density)

        else:
            print("\nERROR: No data file found.\n")
    
    def input(self):

        if self.in_file_path != None:

            in_file = open(self.in_file_path, "r")
            in_file = in_file.read()

            in_ = str(in_file)
            in_ = in_.split("\n")
            in_ = list(filter(None, in_))

            i = 0

            data_files = 0

            run_list = []

            for i in in_:

                if i[0:8] == 'variable':
                    multi_bombard = True
                    setattr(self.input_obj, 'multi_bombard', multi_bombard)
                    
                if i[0:7] == "thermo ":
                    i = i.split()
                    thermo = i[1]
                    setattr(self.input_obj, "thermo", thermo)

                if i[0:8] == "velocity":
                    velocity_line = i
                    i = i.split()
                    setattr(self.input_obj, "velocity_line", velocity_line)

                if i[0:3] == "fix":
                    fix_line = i
                    i = i.split()
                    setattr(self.input_obj, "fix_line", fix_line)

                if i[0:9] == "read_data":
                    data_files += 1
                    data_line = i.split()
                    setattr(self.data_obj, "data_file", data_line[1])


                if i[0:9] == "replicate":
                    i = i.split()
                    no_of_unit_cells = float(i[1])*float(i[2])*float(i[3])
                    surface_unit_cells = float(i[1])*float(i[2])
                    setattr(self.data_obj, "surface_unit_cells", surface_unit_cells)
                    setattr(self.data_obj, "no_of_unit_cells", no_of_unit_cells)

                if i[0:4] == "dump":
                    i = i.split()
                    try:
                        dump = int(i[4])
                    except ValueError:
                        dump = None
                    setattr(self.data_obj, "dump", dump)

                if i[0:3] == 'set':
                    i = i.split()
                    vz = float(i[-1])
                    vz_si = vz*1e-10*1e12
                    bomb_energy_si = 0.5*1*1.66e-27*(vz_si**2)
                    bomb_energy_ev = bomb_energy_si/1.6e-19

                    setattr(self.input_obj, 'bombarded_atom_energy_ev', bomb_energy_ev)

            setattr(self.input_obj, "no_of_data_files", data_files)

            input_file_name = 'in.' + str(self.in_file_path.split('/in.')[-1])

            setattr(self.input_obj, "input_file_name", input_file_name)


        else:
            print("\nERROR: No input file found.\n")

    def read_all(self):
        
        self.data()
        self.input()
        self.log()

    def unpack(self):
        return self.data_obj, self.input_obj


class User_control:
    """Class containing user inputs. """

    def __init__(self, remote = False, path = None, in_file = None, data_file = None, reduce_size = False):

        self.reduce_size = reduce_size
        remote = True

        if remote == True:
            self.test = False
            self.path = path
            self.in_file = in_file
            self.data_file = data_file
            self.log_file = "%s/log.lammps"%path
            self.graphs = True
            if reduce_size == True:
                self.graphs = False



class Data(object):
    """
    Class that holds the sorted data from the model.
    This class also produces averages of model if a equilibrium is achieved.
    Reads data file in order to calculate density.
    """

    def __init__(self):

        self.average_string = "\n\nOUTPUT, EQUILIBRIUM AVERAGES"
        self.equilibrium_check = False
        self.equilibrium = False
        self.equilibrium_index = None
        self.no_of_atoms = None
        self.Temp_avg_err = [0,0]


    def new_variable(self, name, values):
        """
        Attributes list numerical values to the Data object.
        Checks the first field (ignoring "Step") for equilibirum.
        This check is based of the standard deviation of that field.
        A section of 20 data points is taken and if the standard deviation 
        of these is less than 20% of the average, then it is considered to be
        at equilbirium for all point after. Averages are then taken for data
        after this point. If that condition is not fulfilled, the next set of data
        points is considered until the condition is fulfilled or the end is reached.
        """

        setattr(self, name, values)
            

    
class Inputs(object):
    """Class contains sorted data from input file. """

    def __init__(self):

        self.thermo = None
        self.velocity_line = None
        self.fix_line = None
        self.no_of_atoms = None

    def present_string(self):
        """Presents relevant parts of input file as a string."""

        string = "\nINPUTS"
        for attr in vars(self):
            string += "\n%s : %s"%(attr, vars(self)[attr])

        return string


class XYZ():
    """
    Class used for moving and compiling of .xyz files.
    Requires file path (from User_Control) and the sorted data in
    Data object.
    """
    def __init__(self, data_obj, user_options):

        path = user_options.path
        self.data_obj = data_obj
        self.user_options = user_options
        
        self.move_compile()
        
        

    def move_compile(self):
        """
        Function compiles all .xyz files into one (named all.xyz)
        for use in Jmol animation. It also creates a directory (xyz files)
        and moves all the individual xyz files into it.
        """
        
        dump = self.data_obj.dump #could be the issue with missing files, ie looking at wrong dump?
        steps = self.data_obj.Step
        print(steps[0:10])
        print(len(steps))
        print(steps[-1])
   
        path = self.user_options.path

        os.mkdir("%s/xyz_files"%path)

        upper_lim = steps[-1] #maybe this?

        rem = upper_lim%dump
        last_whole_step = upper_lim - rem #mayeb this is wrong?
        print(f"Upperlim: {upper_lim}")
        print(f"rem: {rem}")
        print(f"last_whiole_step: {last_whole_step}")

        data = ''
        files_found = False

        for i in range (0,int(last_whole_step+dump),dump):
            print(f"{i} out of {last_whole_step}")
            try:
                next_file = open("%s/%s.xyz"%(path,i), "r")
                files_found = True
            except FileNotFoundError:
                pass
            else:
                next_data = next_file.read()

                data += next_data
                data += "\n"

                if self.user_options.test == True:
                    shutil.copyfile("%s/%s.xyz"%(path,i), "%s/xyz_files/%s.xyz"%(path,i))
                if self.user_options.reduce_size == True:
                    os.remove("%s/%s.xyz"%(path,i))
                else:
                    shutil.move("%s/%s.xyz"%(path,i), "%s/xyz_files/%s.xyz"%(path,i))
        
    
        if rem != 0:
            try:
                final_file = open("%s/%s.xyz"%(path,int(upper_lim)), "r")
                final_data = final_file.read()
                data += final_data
                data += "\n"
                if self.user_options.test == True:
                    shutil.copyfile("%s/%s.xyz"%(path,int(upper_lim)), "%s/xyz_files/%s.xyz"%(path,int(upper_lim)))
                if self.user_options.reduce_size == True:
                    os.remove("%s/%s.xyz"%(path,i))
                else:
                    shutil.move("%s/%s.xyz"%(path,int(upper_lim)), "%s/xyz_files/%s.xyz"%(path,int(upper_lim)))
            except FileNotFoundError:
                pass

        if files_found == True:
            with open ('%s/all.xyz'%path, 'w') as fp: 
                fp.write(data) 
        else:
            print("\nERROR: xyz compiler could not find files.")


########################################################################

def main(path = None, in_file = None, data_file = None, variable = None, reduce_size = False):
    
    user_options = User_control(remote = True, path = path, in_file = in_file, data_file = data_file, reduce_size = reduce_size)
    
    reader = Reader(user_options.path, log_file_path = user_options.log_file, data_file_path = user_options.data_file, in_file_path = user_options.in_file)
    reader.read_all()

    data_obj, input_obj = reader.unpack()

    if data_obj.success == False:
 
        with open ('%s/FAIL.txt'%path, 'w') as fp: 
            fp.write('FAILED') 

    else:

        data_out = input_obj.present_string()
        data_out += data_obj.average_string

        material_file = user_options.in_file.split(".")
        material = material_file[-1]
    
        XYZ(data_obj, user_options) #moving and compiling xyz files

        #moving relevent files into the new directory

        print("\nComplete.\n")
        print("Directory Name: %s"%user_options.path)

    dir_name = user_options.path.split('/')[-1]
    os.system("echo '%s' | pbcopy" % dir_name)


if __name__ == "__main__":
    #add commandline vairables for path in here
    #just open the file_paths.txt
    #maybe have an arguement to run another

    dir_path = os.path.dirname(os.path.realpath(__file__))

    paths_txt = open("%s/results/file_path.txt"%dir_path, 'r')
    paths_txt = paths_txt.read()
    paths_txt = paths_txt[2:-2]
    paths_list = paths_txt.split("', '")

    path = paths_list[0]

    try:
        path = "%s/results/%s"%(dir_path, sys.argv[1])
    except IndexError:
        pass


    dir_list = os.listdir(path)
    for file_name in dir_list:
        if file_name[0:3] == "in.":
            in_file = file_name
            break


    main(path = path, in_file="%s/%s"%(path, in_file), data_file = "%s/data.graphite_sheet"%path,
        reduce_size= False)

 