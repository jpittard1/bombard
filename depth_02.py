




from surface import Surface_finder
import tools
import numpy as np
import os
import sys
import matplotlib.pylab as plt
import glob
from tqdm import tqdm

'''
Requirements and Considations
    - Single Atom Bombards
        - Average final depth
        - Average max depth
        - Histograms of depths
        - Path?
    - Multibombard
        - Depth profiles can be given by surface analysis
        - Text file of densities
        - Text file of Average values, penetration depths etc

'''


class Depth:

    def __init__(self, path, repeats = False):

        
        self.surface_finding_method = 'cut_off'
        self.surface_cut_off = -2
        self.ion_cut_off = 2

        self.path = path
        self.repeats = repeats

        if self.repeats == False:
            self.settings_dict =  tools.csv_reader(f"{self.path}/settings.csv")
        else:
            self.settings_dict = tools.csv_reader(f"{self.path}0r/settings.csv")

        try:
            os.mkdir(f"{self.path}/depth_results/")
        except FileExistsError:
            pass

    def get_repeated_final_depths(self, file_paths):

        reflected_atoms = 0
        bombard_zs = []
        implanted_zs = []
        floor_heights = []
       
        for path in tqdm(file_paths, desc = "Running Depth analysis"):

            settings_dict = tools.csv_reader(f"{path[:-1]}settings.csv")  
            floor_heights.append((settings_dict['replicate'][-1]-1)*3.567)    

            repeat_final_arr = tools.xyz_to_array(f"{path}")

            try:
                bombard_atom_index = list(repeat_final_arr[:,0]).index(2)
                bombard_z = float(repeat_final_arr[bombard_atom_index][-1])
                bombard_zs.append(bombard_z)

                if bombard_z < self.surface_cut_off:
                    reflected_atoms += 1
                else:
                    implanted_zs.append(bombard_z)

            except ValueError:
                reflected_atoms += 1


        self.reflected_atoms = reflected_atoms
        self.bombard_zs = bombard_zs
        self.implanted_zs = implanted_zs
        self.no_of_repeats = len(file_paths)
        self.floor_heights = list(dict.fromkeys(floor_heights))

      
        

    def publish_repeat_txt(self):
        
        results = f'\nDepth results for {self.path} of {self.no_of_repeats} repeated single bombardments.\n'
        results += f"\n{self.reflected_atoms}/{self.no_of_repeats} were reflected."
        results += f"\n{len(self.implanted_zs)}/{self.no_of_repeats} were implanted.\n"

        average, stderr = tools.avg(self.implanted_zs)
        results += f'\nAverage final depth: {average:.6g} ± {stderr:.3g}\n'

        results += "\nMax depth measured:\n"
        results += f"{max(self.implanted_zs)}\n"

        results += "\nFrozen Floor depth:\n"
        results += f"{self.floor_heights}\n"

        results += "\nFinal implanted zs (for avg and hist):\n"
        results += f"{self.implanted_zs}\n"

        results += "\nFinal bombard zs:\n"
        results += f"{self.bombard_zs}\n"

        with open(f"{self.path}/depth_results/depth.txt", 'w') as fp: #rewriting edited input file
            fp.write(results)

        plt.hist(self.implanted_zs,bins = 20)
        xmin, xmax, ymin, ymax = plt.axis()

        for height in self.floor_heights:
            plt.vlines(x = height, ymin= ymin, ymax=ymax, colors='b', linestyles='dashed')
            plt.vlines(x = height +3.567, ymin= ymin, ymax=ymax, colors='r', linestyles='dotted')

        plt.xlabel('Depth / A')
        plt.title('Depth of implanted atoms')
        plt.savefig(f'{self.path}/depth_results/depth_histogram.png', dpi = 300)
        plt.close()



      








        

    def get_arrays(self):

        self.initial = tools.file_proc(f"{self.path}/initial_indexed.xyz")
        self.initial_arr = tools.xyz_to_array(f"{self.path}/initial_indexed.xyz")
        self.final_arr = tools.xyz_to_array(f"{self.path}/final_indexed.xyz")


    def get_surfaces(self):

        print("\n\nPROGRESS: Determining heights of surfaces.") 

        initial_carbon_zs = [row[-1] for row in self.initial_arr if row[-4] == 1]
        final_carbon_zs = [row[-1] for row in self.final_arr if row[-4] == 1]
        final_carbon_xs = [row[-2] for row in self.final_arr if row[-4] == 1]
        self.final_bombard_zs = [row[-1] for row in self.final_arr if row[-4] == 2]
        final_bombard_xs = [row[-2] for row in self.final_arr if row[-4] == 2]

        plt.scatter(final_carbon_xs, final_carbon_zs)
        plt.scatter(final_bombard_xs, self.final_bombard_zs)
        plt.ylim(20,-20)
        plt.savefig(f'{self.path}/depth_results/pos_scatter.png')
        plt.close()


        surface_area = self.settings_dict['surface_area']
        surface_unit_cells = surface_area/(3.567**2)

        self.surface_finder = Surface_finder(final_carbon_zs, surface_area_unit_cells=surface_unit_cells, surface_area=surface_area)
        self.surface_finder.find_carbon(final_carbon_zs, cut_off_density_frac=0.5)
        self.surface_finder.find_surface(self.surface_cut_off, ion_cut_off=-2,  carbon_density = True, averaging=False)
        self.surface_finder.find_ions(self.final_bombard_zs)
        self.surface_finder.initial(initial_carbon_zs)


        self.diamond_surface = [self.surface_finder.surface, self.surface_finder.surface_err]



    def get_penetration_depths(self):

        self.zs = [z for z in self.final_bombard_zs if z > self.diamond_surface[0] - self.ion_cut_off]
        self.bombard_penetration_depths = [z - self.diamond_surface[0] for z in self.zs]


    def get_regions(self):

        self.surface_atom_zs = [z for z in self.zs if z <= self.diamond_surface[0]]
        self.bulk_atom_zs = [z for z in self.zs if z > self.diamond_surface[0]]



    def publish_txt(self):

        results = f'Depth results for {self.path.split("/")[-1]}\n\n'
        results += f'Diamond surface taken to be at height of {self.diamond_surface[0]:.6g}±{self.diamond_surface[1]:.6g} A.\n'
        results += f'The {self.surface_finding_method} method was used to determine surface height.\n'
        results += f'Carbon atoms beyond {self.surface_finder.surface_cut_off}A were discounted from surface average.\n'
        results += f'Ions {self.ion_cut_off}A from the surface were discounted. \n\n'
        
        average, stderr = tools.avg(self.bombard_penetration_depths)
        results += f"\n{self.settings_dict['atom_type']} Ion Average Diamond Pen: "
        results += f'{average:.6g} ± {stderr:.3g}\n'

        results += f"\n{self.settings_dict['atom_type']} Ions on surface - {len(self.surface_atom_zs)}"
        results += f"\n{self.settings_dict['atom_type']} Ions on surface - {len(self.bulk_atom_zs)}"

        results += '\n'

        results += f"\n\n{self.settings_dict['atom_type']} ion diamond pens: "
        results += f'\n{self.bombard_penetration_depths}'

        with open(f"{self.path}/depth_results/depth.txt", 'w') as fp: #rewriting edited input file
            fp.write(results)


    def publish_densities(self):
        self.surface_finder.plot(f"{self.path}/depth_results/")
        self.surface_finder.publish_txt_file(f"{self.path}/depth_results/")



def main(args_dict):

    if args_dict['repeats'] == None:
        args_dict['repeats'] = tools.repeat_check(args_dict['path'])
    else:
        args_dict['repeats'] = tools.str_to_bool(args_dict['repeats'])

    if args_dict['ssd'] == None:
        args_dict['ssd'] = False
    else:
        args_dict['ssd'] = tools.str_to_bool(args_dict['repeats'])

    args_dict['path'] = tools.Path(args_dict['path'])

    if args_dict['repeats'] == False:
        depth = Depth(args_dict['path'], args_dict['repeats'])
        depth.get_arrays()
        depth.get_surfaces()
        depth.get_penetration_depths()
        depth.get_regions()
        depth.publish_txt()
        depth.publish_densities()

    if args_dict['repeats'] == True:
        
        bombard_dir = tools.bombard_directory()
        repeat_dirs_path = glob.glob(f"{bombard_dir}{args_dict['path']}*r/final_indexed.xyz")
        repeat_dirs_path = [tools.Path(path) for path in repeat_dirs_path]

        depth = Depth(args_dict['path'], args_dict['repeats'])
        depth.get_repeated_final_depths(repeat_dirs_path)
        depth.publish_repeat_txt()
 




if __name__ == "__main__":

    accepted_args = ['repeats', 'path', 'ssd']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')

    main(args_dict)


