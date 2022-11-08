


from audioop import tostereo
import os
import glob
import pprint
import tools
import matplotlib.pyplot as plt
import sys




def copy(all_paths, file_target):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    for index, path in enumerate(all_paths):
        file_name = path.split('/')[-2]
        energy = file_name.split('_')[2]
        count = file_name.split('_')[-1]
        family_name = path.split('/')[-3]
        print(f"cp {dir_path}/results/{path}/{file_target} {dir_path}/{target}/{family_name}_{energy}_{count}.png")
        os.system(f"cp {dir_path}/results/{path}/{file_target} {dir_path}/{target}/{family_name}_{energy}_{count}_{index}.png")
    #os.system(f"mv {dir_path}/{target}/atom_densities.png"")



class Combine:

    def __init__(self, all_paths):

        self.all_paths = all_paths

    def lists_to_csv(self, lists, save_file_path = None, column_titles = [None]):

       
        if column_titles[0] != None:
            csv_str = str(column_titles)
        else:
            csv_str = ''
        
        lengths = [len(item) for item in lists]
      
        for index in range(0,max(lengths)):
            
            vals = []
            for column in lists:
                try:
                    vals.append(str(column[index]))
                except IndexError:
                    vals.append(' ')
                
            comma = ', '
            csv_str += '\n'
            csv_str += comma.join(vals)
          

        with open(f"{save_file_path}", 'w') as fp: #rewriting edited input file
            fp.write(csv_str)
       


    def steinhardt(self, to_save_path = None):

        current_dir = tools.bombard_directory()
        params = [f"Q{para}" for para in range(4,14,2)]
        to_plot_lists = [[] for i in range(len(self.all_paths)*2)]
        

        for param in params:
            for index, path in enumerate(self.all_paths):
                opened_file = open(f"{dir_path}/results/{path}/steinhardt_results/{param}.csv", 'r')

                string = opened_file.read()

                arr = tools.str_to_arr(string)
            
                xs = arr[:,0]
                ys = arr[:,1]
                y_err = arr[:,2]
                xs = [x for x in xs if x != 111]
                ys = [y for y in ys if y != 111]

                plt.plot(xs, ys, label = path.split('/')[-1])
                
                to_plot_lists[index*2] = xs
                to_plot_lists[index*2 + 1] = ys

            plt.legend()
            plt.xlabel('z / A')
            plt.ylabel(f'{param}')
            plt.ylim(-0.1,1.1)

            file_tree = path.split('/')[:-1]
            sep = '/'
            file_tree = sep.join(file_tree)

            sep = '/'
            path_ending = path.split('/')[:-2]
            path_ending = sep.join(path_ending)

            #to_save_path = f'{dir_path}/results/{file_tree}/{param}'

            plt.savefig(f'{to_save_path}{param}_combined.png', dpi = 300)
            print(f'{to_save_path}{param}_combined.png')
            plt.show()
            plt.close()


            column_titles = []

            for name in [path.split('/')[-1] for path in self.all_paths]:
                column_titles.append(f"{name}_heights")
                column_titles.append(f"{name}_{param}")
            self.lists_to_csv(to_plot_lists, f"{to_save_path}{param}_combined.csv", column_titles = column_titles)
                



          

    def depth(self, carbon_initial = False, carbon_final = False, ions = False, to_save_path = None):
        
        if carbon_final == True:
            file_name = 'carbon_final'
            height_column = 0
            densities_column = 1
        
        elif ions == True:
            file_name = 'ions'
            height_column = 2
            densities_column = 3

        elif carbon_initial == True:
            file_name = 'carbon_initial'
            height_column = 4
            densities_column = 5



        dir_path = os.path.dirname(os.path.realpath(__file__))


        to_plot_lists = [[] for i in range(len(self.all_paths)*2)]
        
        legend = []
        self.all_paths.sort()
        for index, path in enumerate(self.all_paths):
            opened_file = open(f"{dir_path}/results/{path}/depth_results/densities.txt", 'r')

            legend.append(path.split('/')[-1])

            string = opened_file.read()

            arr = tools.str_to_arr(string)
        
            xs = arr[:,height_column]
            ys = arr[:,densities_column]
            xs = [x for x in xs if x != 111]
            ys = [y for y in ys if y != 111]

            plt.plot(xs, ys)
            to_plot_lists[index*2] = xs
            to_plot_lists[index*2 + 1] = ys

        plt.legend(legend)
        plt.xlabel('z / A')
        plt.ylabel('Atom Density / A^-3')

        file_tree = path.split('/')[:-1]
        sep = '/'
        file_tree = sep.join(file_tree)

        sep = '/'
        path_ending = path.split('/')[:-2]
        path_ending = sep.join(path_ending)

        if to_save_path == None:
            to_save_path = f'{dir_path}/results/{file_tree}/{file_name}'

        plt.savefig(f'{to_save_path}{file_name}_combined.png', dpi = 300)
        print(f'{to_save_path}_combined.png')
        plt.show()
        plt.close()

        column_titles = []
        for name in legend:
            column_titles.append(f"{name}_heights")
            column_titles.append(f"{name}_densities")
        self.lists_to_csv(to_plot_lists, f"{to_save_path}{file_name}_combined.csv", column_titles = column_titles)


    def saturate(self, x = 'bombard_attempts', y = 'd_counter', to_save_path = None):

        dir_path = os.path.dirname(os.path.realpath(__file__))
        to_plot_lists = [[] for i in range(len(self.all_paths)*2)]

        
        legend = []
        self.all_paths.sort()
        for index, path in enumerate(self.all_paths):
            opened_file = open(f"{dir_path}/results/{path}/saturate_02_results/saturate.txt", 'r')
 
            string = opened_file.read()

            for row in string.split('\n'):
                row = row.split(', ')
                if row[0] == 'steps' or row[0] == 'time':
                    titles = row
                    break
      
            arr = tools.str_to_arr(string)
        
            x_index = titles.index(x)
            y_index = titles.index(y)

            xs = arr[:-1,x_index]
            ys = arr[:-1,y_index]
            print(f"Legened: {path.split('/')[-2]}")

            legend.append(path.split('/')[-1])

            plt.plot(xs, ys)
            to_plot_lists[index*2] = xs
            to_plot_lists[index*2 + 1] = ys

        file_tree = path.split('/')[:-1]
        sep = '/'
        file_tree = sep.join(file_tree)

        if to_save_path == None:
            to_save_path = f'{dir_path}/results/{file_tree}/{y}_combined.png'
  
        plt.legend(legend)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig(f'{to_save_path}{y}_combined.png', dpi = 300)
        print(f'Path: {to_save_path}{y}_combined.png')
        plt.show()

        column_titles = []
        for name in legend:
            column_titles.append(f"{name}_x")
            column_titles.append(f"{name}_y")
        self.lists_to_csv(to_plot_lists, f'{to_save_path}{y}_combined.csv', column_titles = column_titles)

    


        

    def combine(all_paths, method = 'depth'):

        dir_path = os.path.dirname(os.path.realpath(__file__))


        to_plot_arrs = []
        legend = []
        for path in all_paths:
            opened_file = open(f"{dir_path}/results/{path}/densities.txt", 'r')

            title = path.split('/')[-2]
            legend.append(path.split('/')[-1])


            string = opened_file.read()

            arr = tools.str_to_arr(string)
        
            xs = arr[:,2]
            ys = arr[:,3]
            xs = [x for x in xs if x != 111]
            ys = [y for y in ys if y != 111]

            plt.plot(xs, ys)

        plt.legend(legend)
        plt.xlim([-50,15])
        plt.show()






dir_path = os.path.dirname(os.path.realpath(__file__))

target = 'results/testing/size/[8,8,6]/t_0g_30eV_1778_1'
target = 'results/testing/fixes/nvt/damp_100'
target = 'results/testing/flux'

target = 'results/testing/size/12_12_6'
target = 'results/final/to_compare'
target = 'results/orient/111/to_compare'

all_paths = []
for i in range(0,10):
    sep = '/*'*i
    #layer = glob.glob(f'{dir_path}/{target}{sep}/atom_densities.png')
    #layer = glob.glob(f'{dir_path}/{target}{sep}/depth_results/densities.txt')
    layer = glob.glob(f'{dir_path}/{target}{sep}/depth_results/densities.txt')
    print(f'{dir_path}/{target}{sep}/jmol_all.xyz')


    if len(layer) > 0:
        all_paths += layer



start_length = len(dir_path.split('/')) + 1
all_paths = [path.split('/')[start_length:-2] for path in all_paths]
sep = '/'
all_paths = [sep.join(path) for path in all_paths]

#pprint.pprint(all_paths)
#all_paths = ['4_4_6/t_0g_30eV_444_1', '6_6_6/t_0g_30eV_1000_5', '8_8_6/t_0g_30eV_1778_2', '10_10_6/t_0g_30eV_2778_1', '12_12_6/t_0g_30eV_4000_1']
#all_paths = [f'testing/size/{file}/depth_results' for file in all_paths]

print(all_paths)
to_save_path = f"{dir_path}/{target}"
os.system(f"mkdir {to_save_path}/combined_saturate")
os.system(f"mkdir {to_save_path}/combined_depth")
os.system(f"mkdir {to_save_path}/combined_steinhardt")
combine = Combine(all_paths)
#

combine.steinhardt(to_save_path=f"{to_save_path}/combined_steinhardt/")

combine.depth(ions = True, to_save_path=f"{to_save_path}/combined_depth/")
combine.depth(carbon_final = True, to_save_path=f"{to_save_path}/combined_depth/")
print(f"Saved to: {to_save_path}")
combine.saturate(y= 'ref_yield', to_save_path=f"{to_save_path}/combined_saturate/")
combine.saturate(y= 'sputt_yield', to_save_path=f"{to_save_path}/combined_saturate/")
combine.saturate(y= 'd_counter', to_save_path=f"{to_save_path}/combined_saturate/")
combine.saturate(y= 'c_counter', to_save_path=f"{to_save_path}/combined_saturate/")
combine.saturate(y= 'surface_height', to_save_path=f"{to_save_path}/combined_saturate/")
#copy(all_paths, 'saturate_results/sputting_yield')

