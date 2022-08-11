
from smtplib import SMTPAuthenticationError
import tools
import os
import matplotlib.pyplot as plt
import numpy as np


class Surface_finder:

    def __init__(self, carbon_zs, surface_area_unit_cells = None, surface_area = None):
        
        self.carbon_zs = carbon_zs

        if surface_area_unit_cells != None:
            self.surface_area_unit_cells = surface_area_unit_cells
            self.surface_area = surface_area_unit_cells*(3.567**2)
        elif surface_area != None:
            self.surface_area_unit_cells = int(round(surface_area/(3.567**2), 0))
            self.surface_area = surface_area
        else:
            print("\n\nERROR in Surface finder: Either surface area or number of surface unit cells must be specified.\n\n")
            raise AttributeError


    def find_surface(self, cutoff, carbon_density = False, averaging = True):

        if carbon_density == True:
            cutoff = self.carbon_densities[2]

        carbon_bulk_zs = [z for z in self.carbon_zs if z > cutoff]

        if averaging == True:
            no_surface_atoms = 2*self.surface_area_unit_cells
            diamond_surface_zs = sorted(carbon_bulk_zs)[0:no_surface_atoms]

            surface = tools.avg(diamond_surface_zs)
        
        else:
            surface = [cutoff, 0]

        setattr(self, 'surface', surface[0])
        setattr(self, 'surface_err', surface[1])
        setattr(self, 'surface_cut_off', cutoff)


    def density(self, zs, average_zone_unit_cells = 0.5, resolution = 0.1, cut_off_density_frac = 0.25):

        zs.sort()

        bottom = min(zs)
        top = max(zs)
        thickness = 3.567*average_zone_unit_cells

        high_lim = top
        low_lim = top - thickness

        heights = []
        densities = []

       
        while low_lim >= bottom:

            section = [atom_z for atom_z in zs if atom_z < high_lim and atom_z > low_lim]
            density = len(section)/(thickness*self.surface_area)
   
            height = (high_lim + low_lim)/2

    
            densities.append(density)
            heights.append(height)

            high_lim += -resolution
            low_lim += -resolution

        try:
            etched_carbon = [rho for rho in densities if rho < cut_off_density_frac*0.175]
            bulk_carbon = [rho for rho in densities if rho > cut_off_density_frac*0.175]
            cut_off_z = heights[densities.index(max(etched_carbon))]
            #top_heights = [z for z in heights if z < 15]
            #cut_off_z = top_heights[densities.index(min(bulk_carbon))]
    
        except ValueError:
            cut_off_z = None


        return heights, densities, cut_off_z
        
  


    def cut_off(self, initial_cutoff = 2):
        return initial_cutoff

    
    def find_carbon(self, carbon_zs):
        heights, densities, cut_off_z = self.density(carbon_zs, cut_off_density_frac=0.448)
        setattr(self, 'carbon_densities', [heights, densities, cut_off_z])


    def find_ions(self, ion_zs):
        heights, densities, cut_off_z = self.density(ion_zs, cut_off_density_frac=0.5)
        setattr(self, 'ion_densities', [heights, densities])



    def initial(self, carbon_zs):
        heights, densities, density_cut_off = self.density(carbon_zs, cut_off_density_frac=0.5)
        setattr(self, 'initial_densities', [heights, densities])



    def plot(self, path = None, carbon = True, ions = True, initial = True, surface = True, ion_cut_off = True):


        fig = plt.figure()
        legend = []
        title = ' '
        try:
            file_name = path.split('/')[-3]
            title_file_name = path.split('/')[-4]
            title = f"{title_file_name} {file_name}"
        except AttributeError:
            pass

        if carbon == True:
            plt.plot(self.carbon_densities[0], self.carbon_densities[1])
            legend.append('Final Carbon')

        if ions == True:
            plt.plot(self.ion_densities[0], self.ion_densities[1])
            legend.append('Ions')

        if initial == True:
            plt.plot(self.initial_densities[0], self.initial_densities[1])
            legend.append('Initial Carbon')

        if surface == True:
            plt.vlines(self.surface , -0.01, max(self.carbon_densities[1]), colors = 'r', linestyles='--')
            legend.append('Surface')

        if ion_cut_off == True:
            plt.vlines(self.surface - 2, -0.01, max(self.carbon_densities[1]), colors = 'r')
            legend.append('Ion Cutoff')
        
        plt.ylim(-0.01)
        plt.ylabel("Atoms density / A^-3")
        plt.xlabel("z / A")
        plt.legend(legend)
        plt.title(title + ' densities.')

        if path == None:
            plt.show()
        
        else:
            plt.savefig(f"{path}/atom_densities.png")
            plt.close(fig)


    def publish_txt_file(self, path, carbon = True, ions = True, initial = True, surface = True, ion_cut_off = True):

        columns = []
        column_titles = []
    

        if carbon == True:
            columns.append(self.carbon_densities[0]) 
            columns.append(self.carbon_densities[1])
            column_titles.append('Final Carbon Heights')
            column_titles.append('Final Carbon Densities')

        if ions == True:
            columns.append(self.ion_densities[0]) 
            columns.append(self.ion_densities[1])
            column_titles.append('Ion Heights')
            column_titles.append('Ion Densities')
            

        if initial == True:
            columns.append(self.initial_densities[0]) 
            columns.append(self.initial_densities[1])
            column_titles.append('Initial Carbon Heights')
            column_titles.append('Initial Carbon Densities')

        lens = [len(l) for l in columns]
        arr = np.ones([max(lens), len(columns)])*111

        for i1, column in enumerate(columns):
            for i2, item in enumerate(column):
                arr[i2,i1] = item

        results_str = ''
        for title in column_titles:
            results_str += title + ', '

        for row in arr:
            row = [float(f"{item:.6g}") for item in row]
            results_str += '\n' + str(row)


        with open("%s/densities.txt"%path, 'w') as fp: #rewriting edited input file
            fp.write(str(results_str))


            

 





    




if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.realpath(__file__))
    settings_path = f"{current_dir}/results/testing/size/12_12_6/t_0g_30eV_4000_1"


    initial = tools.file_proc(f"{settings_path}/initial_indexed.xyz")
    initial_arr = tools.xyz_to_array(f"{settings_path}/initial_indexed.xyz")
    final_arr = tools.xyz_to_array(f"{settings_path}/final_indexed.xyz")

    initial_atoms_arr, region_indexes = tools.region_assign(initial, loaded = False)

    all_carbon_indexes = region_indexes['diamond_bulk'] + region_indexes['diamond_surface']

    initial_carbon_zs = [row[-1] for row in initial_arr if int(row[-4]) == 1]
    final_carbon_zs = [final_arr[index][-1] for index in all_carbon_indexes if final_arr[index][1] == 1]
    final_dueterium_zs = [row[-1] for row in final_arr if int(row[-4]) == 2]
    final_tritium_zs = [row[-1] for row in final_arr if int(row[-4]) == 3]


    surface_finder = Surface_finder(final_carbon_zs, 16)
    surface_finder.find_carbon(final_carbon_zs)
    surface_finder.find_surface(-2, carbon_density = False)
    surface_finder.find_ions(final_tritium_zs)
    surface_finder.initial(initial_carbon_zs)

    surface_finder.plot()





