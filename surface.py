

import tools
import os
import matplotlib.pyplot as plt


class Surface_finder:

    def __init__(self, carbon_zs, surface_area_unit_cells):
        
        self.carbon_zs = carbon_zs
        self.surface_area_unit_cells = surface_area_unit_cells

    def find_surface(self, cutoff, carbon_density = False):

        if carbon_density == True:
            cutoff = self.carbon_densities[2]

        carbon_bulk_zs = [z for z in self.carbon_zs if z > cutoff]

        no_surface_atoms = 2*self.surface_area_unit_cells
        diamond_surface_zs = sorted(carbon_bulk_zs)[0:no_surface_atoms]
        print(diamond_surface_zs)

        surface = tools.avg(diamond_surface_zs)

        setattr(self, 'surface', surface[0])


    def density(self, zs, surface_area_unit_cells, average_zone_unit_cells = 0.5, resolution = 0.1, cut_off_density_frac = 0.25):

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
            density = len(section)/(thickness*surface_area_unit_cells*3.567**2)
            height = (high_lim + low_lim)/2
    
            densities.append(density)
            heights.append(height)

            high_lim += -resolution
            low_lim += -resolution

        try:
            etched_carbon = [rho for rho in densities if rho < cut_off_density_frac*0.175]
            cut_off_z = heights[densities.index(max(etched_carbon))]
            print(max(etched_carbon))
            print(cut_off_z)
        except ValueError:
            cut_off_z = None


        return heights, densities, cut_off_z
        
  


    def cut_off(self, initial_cutoff = 2):
        return initial_cutoff

    
    def find_carbon(self, carbon_zs):
        heights, densities, cut_off_z = self.density(carbon_zs, self.surface_area_unit_cells, cut_off_density_frac=0.5)
        setattr(self, 'carbon_densities', [heights, densities, cut_off_z])


    def find_ions(self, ion_zs):
        heights, densities, cut_off_z = self.density(ion_zs, self.surface_area_unit_cells, cut_off_density_frac=0.5)
        setattr(self, 'ion_densities', [heights, densities])



    def initial(self, carbon_zs):
        heights, densities, density_cut_off = self.density(carbon_zs, self.surface_area_unit_cells,cut_off_density_frac=0.5)
        setattr(self, 'initial_densities', [heights, densities])



    def plot(self, carbon = True, ions = True, initial = True, surface = True, ion_cut_off = True):

        if carbon == True:
            plt.plot(self.carbon_densities[0], self.carbon_densities[1])

        if ions == True:
            plt.plot(self.ion_densities[0], self.ion_densities[1])

        if initial == True:
            plt.plot(self.initial_densities[0], self.initial_densities[1])

        if surface == True:
            plt.vlines(self.surface , -0.01, max(self.carbon_densities[1]), colors = 'r', linestyles='--')

        if ion_cut_off == True:
            plt.vlines(self.surface - 2, -0.01, max(self.carbon_densities[1]), colors = 'r')
        
        plt.ylim(-0.01)
        plt.ylabel("Atoms per A^3")
        plt.xlabel("z / A")
        plt.show()


    




if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.realpath(__file__))
    settings_path = f"{current_dir}/results/testing/size/[12,12,6]/t_0g_30eV_4000_1"


    initial = tools.file_proc(f"{settings_path}/initial_indexed.xyz")
    initial_arr = tools.xyz_to_array(f"{settings_path}/initial_indexed.xyz")
    final_arr = tools.xyz_to_array(f"{settings_path}/final_indexed.xyz")

    initial_atoms_arr, region_indexes = tools.region_assign(initial, loaded = False)

    all_carbon_indexes = region_indexes['diamond_bulk'] + region_indexes['diamond_surface']

    initial_carbon_zs = [row[-1] for row in initial_arr if row[-4] == 1]
    final_carbon_zs = [final_arr[index][-1] for index in all_carbon_indexes]
    final_ion_zs = [row[-1] for row in final_arr if row[-4] != 1]



    surface_finder = Surface_finder(final_carbon_zs, 144)
    surface_finder.find_carbon(final_carbon_zs)
    surface_finder.find_surface(-2, carbon_density = False)
    surface_finder.find_ions(final_ion_zs)
    surface_finder.initial(initial_carbon_zs)

    surface_finder.plot()





