
import tools
import sys
import matplotlib.pylab as plt
import glob
import numpy as np
import combine_results
from pprint import pprint
from tqdm import tqdm


class DataReader:

    def __init__(path) -> None:
        self.path = path

    def getSettings(self):

        settings_dict = tools.csv_reader(f"{self.path}/0r/settings.cvs")

        variable_dict = dict(angle = settings_dict['measured_angle'],
                             energy = settings_dict['energy'],
                             temperature = settings_dict['temperature'],
                             mass = settings_dict['atom_mass'])
        
        self.variable_dict = variable_dict
        return variable_dict

    def getDepth(self):
        pass

    def getOvito(self):
        self.ovito_dict = combine_results.new_ovito_reader(f"{self.path}/ovito_results/ws_analysis.txt")
        return self.ovito_dict



class CombinedData:

    def __init__(self, path) -> None:
        self.path = path
        self.analysis = path[-1][9:-4]

        self.combined_file = tools.file_proc(f"{self.path}")

        try:
            self.combined_file.remove('')
        except ValueError:
            pass

        self.column_index = self.getColumnIndex()
        self.column_data = self.getColumnData()
        self.row_data, self.row_data_index = self.getRowData()
       


    def getColumnIndex(self):

        column_titles = self.combined_file[0].split(', ')

        column_index = dict()
        for i, title in enumerate(column_titles):
            column_index[title] = i

        return column_index
 
    def getColumnData(self):

        data_dict = dict()

        for title in self.column_index.keys():
            data_dict[title] = []


        for line in self.combined_file[1:]:
            line = line.split(', ')
      
            for title in self.column_index.keys():
                if title == 'dir_name' or title == 'atom_type':
                    data_dict[title].append(line[self.column_index[title]])
                else:
                    data_dict[title].append(float(line[self.column_index[title]]))


        return data_dict
    
    def getRowData(self):

        data_dict = dict()

        for line in self.combined_file[1:]:
            line = line.split(', ')
            data_dict[line[0]] = [float(x) for x in line[2:]],
        
        adjusted_column_index = self.column_index

        for key in adjusted_column_index.keys():
            adjusted_column_index[key] -= 2

        return data_dict, adjusted_column_index



        
        


class Dataset2:

    def __init__(self, measureable) -> None:
        self.measureable = measureable

    def setPaths(self, path):
        paths = glob.glob(path)

    def getVairables(self):

        data_objs = []

        for path in self.paths:
            data = DataReader(path) 
            data.getSettings()
            data_objs.append(data)

        energies = set([data.variable_dict['energy'] for data in data_objs])
        angles = set([data.variable_dict['angle'] for data in data_objs])
        masses = set([data.variable_dict['mass'] for data in data_objs])
        temperatures = set([data.variable_dict['temperature'] for data in data_objs])

        self.data_pbjs = data_objs

        return dict(energies = energies,
                    angles = angles,
                    masses = masses,
                    temperatures = temperatures)

            

    def getCombinedData(self):

        combined_results = tools.file_proc(f"{self.path}/combined_{self.measureable}.csv")

        column_titles = line[0].split(', ')

        data_dict = dict()
        for title in column_titles:
            data_dict[title] = []

        for line in combined_results[1:]:
            for i, title in column_titles:
                data_dict[title].append(line[i])

    def getOriginalData(self):

        try:
            self.data_obj
        except NameError:
            self.getVairables()

        for data_obj in self.data_objs:
            pass


        

    def generate_array(self):

        variables_dict = self.getVairables()

        array = np.ones([len(variables_dict['energies']), len(variables_dict['angles']), 
                         len(variables_dict['masses']), len(variables_dict['temperatures'])])*111
        
        index_dicts = dict()
        for i, key in enumerate(variables_dict.keys()):

            new_dict = dict()
            for j, val in enumerate(variables_dict[key]):
                new_dict['val'] = [i, j]
            
            index_dicts[key] = new_dict

        #syntax should be index_dict['angles']['10'] = 0, 1 (index and axis)

        #should get all data form simulation at once rather than looping thourh again


        for i, energy in enumerate(variables_dict['energies']):
            for j, angle in enumerate(variables_dict['angles']):
                for k, mass in enumerate(variables_dict['masses']):
                    for l, temperature in enumerate(variables_dict['temperatures)']):
                        array[i][j][k][l] = self.getData()

                        index_dicts['energy'][energy] = i 
                        index_dicts['angle'][angle] = j 
                        index_dicts['mass'][mass] = k 
                        index_dicts['temperature'][temperature] = l 


        for file in combined_data_files:

            for line in file[1:]:

                file.column_titles['']
        
  

class Dataset:

    def __init__(self) -> None:
        self.combined_data_objs = []
        self.variables = ['energy', 'angle', 'temperature', 'atom_mass']

    def addCombinedData(self, combined_data_obj):
        self.combined_data_objs.append(combined_data_obj)

    def getVariables(self):

        variable_dict = dict()
        for variable in self.variables:
            variable_dict[variable] = []

        for combined_data in self.combined_data_objs:
            for key in variable_dict.keys():
                variable_dict[key] += combined_data.column_data[key]
                variable_dict[key] = list(set(variable_dict[key]))

        self.variable_dict = variable_dict
        return variable_dict
        


    def generateArray(self):
        
        array = np.ones([len(self.variable_dict['energy']), len(self.variable_dict['angle']), 
                         len(self.variable_dict['atom_mass']), len(self.variable_dict['temperature'])])*111

        variable_index_dict = dict()
        for key in self.variable_dict.keys():
            index_dict = dict()
            for i, item in enumerate(self.variable_dict[key]):
                index_dict[str(item)] = i
            variable_index_dict[key] = index_dict

     
        for combined_data in tqdm(self.combined_data_objs):

            indexes = combined_data.row_data_index
            
            for row in combined_data.row_data.values():
                
                angle = row[0][indexes['angle']]
                energy= row[0][indexes['energy']]
                atom_mass = row[0][indexes['atom_mass']]
                temperature = row[0][indexes['temperature']]

                angle_arr_index = variable_index_dict['angle'][str(angle)]
                energy_arr_index = variable_index_dict['energy'][str(energy)]
                atom_mass_arr_index = variable_index_dict['atom_mass'][str(atom_mass)]
                temperature_arr_index = variable_index_dict['temperature'][str(temperature)]

                array[energy_arr_index][angle_arr_index][atom_mass_arr_index][temperature_arr_index] = row[0][indexes['vacancies']]


        angle_arr_index = variable_index_dict['angle']['90.0']
        energy_arr_index = variable_index_dict['energy']['30.0']
        atom_mass_arr_index = variable_index_dict['atom_mass']['2.0141']
        temperature_arr_index = variable_index_dict['temperature']['300.0']
        
        pprint(variable_index_dict)
        pprint(array.shape)
        pprint(array[:][angle_arr_index][atom_mass_arr_index][temperature_arr_index])






            

                        

        





def main(args_dict):
    
    args_dict['path'] = tools.Path(args_dict['path'])

    csv = csv_reader(tools.Path(f"{args_dict['path']}/combined_{args_dict['analysis']}.csv"))
    

    #Want a way of combining all dat ain one big data base and so can polt whatever against whatever for various datasets
    #Overall plan
        #Have multiple big multi dimensional arrays, one for each measureable, ie, depth
        #Each vairable (angle, energy, mass, temperature) has its own axis on array
        #Each axis/variable will have a look up dictionary, dictionary key is desired value of variable, returns index for that value
        #Need a way of defining y-axis, x-axis, sets to compare, and values to plot (ie all energies or just sepcific ones)
        #Save the big arrays somewhere? or regenerate each time? If saving need some update function.


    #instead open combined results csv and pull all data from that.
    #add angle, temperature, mass etc to combined cvs. although this will fuck the origin plotting if I still want to use that 


paths = glob.glob('/Volumes/Seagate/repeats/d_*/*/combined_ovito_update.csv')

combined_datas = [CombinedData(path) for path in paths]

dataset = Dataset()

for combined_data in combined_datas:

    dataset.addCombinedData(combined_data)

print(combined_data.row_data)


dataset.getVariables()
dataset.generateArray()


'''
if __name__ == "__main__":

    accepted_args = ['path', 'analysis']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')

    main(args_dict)
'''
