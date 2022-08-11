


import os
import glob
import pprint
import tools
import matplotlib.pyplot as plt
import sys










def copy(all_paths):

    dir_path = os.path.dirname(os.path.realpath(__file__))

    for index, path in enumerate(all_paths):
        file_name = path.split('/')[-2]
        energy = file_name.split('_')[2]
        count = file_name.split('_')[-1]
        family_name = path.split('/')[-3]
        print(f"cp {dir_path}/results/{path}/temp.png {dir_path}/{target}/{family_name}_{energy}_{count}.png")
        os.system(f"cp {dir_path}/results/{path}/temp.png {dir_path}/{target}/{family_name}_{energy}_{count}_{index}.png")
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
            print(save_file_path)


            
          

    def depth(self, carbon_initial = False, carbon_final = False, ions = False):
        
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
        for index, path in enumerate(self.all_paths):
            opened_file = open(f"{dir_path}/results/{path}/depth_results/densities.txt", 'r')

            title = path.split('/')[-2]
            legend.append(title)

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

        sep = '/'
        path_ending = path.split('/')[:-2]
        path_ending = sep.join(path_ending)
        plt.savefig(f"{dir_path}/results/{path_ending}/{file_name}_combined.png", dpi = 300)
        plt.show()
        plt.close()

        column_titles = []
        for name in legend:
            column_titles.append(f"{name}_heights")
            column_titles.append(f"{name}_densities")
        self.lists_to_csv(to_plot_lists, f"{dir_path}/results/{path_ending}/{file_name}_combined.csv", column_titles = column_titles)


    def saturate(self, x = 'bombard_attempts', y = 'd_counter'):

        dir_path = os.path.dirname(os.path.realpath(__file__))
        to_plot_lists = [[] for i in range(len(self.all_paths)*2)]

        
        legend = []
        for index, path in enumerate(self.all_paths):
            opened_file = open(f"{dir_path}/results/{path}/saturate_results/saturate.txt", 'r')

            title = path.split('/')[-2]
            legend.append(title)

            string = opened_file.read()

            for row in string.split('\n'):
                row = row.split(', ')
                if row[0] == 'time':
                    titles = row
                    break

            arr = tools.str_to_arr(string)

            x_index = titles.index(x)
            y_index = titles.index(y)
            print(arr.shape)
            print(x_index, y_index)
            xs = arr[:-1,x_index]
            ys = arr[:-1,y_index]


            plt.plot(xs, ys)
            to_plot_lists[index*2] = xs
            to_plot_lists[index*2 + 1] = ys
        
        plt.show()

        

    def combine(all_paths, method = 'depth'):

        dir_path = os.path.dirname(os.path.realpath(__file__))


        to_plot_arrs = []
        legend = []
        for path in all_paths:
            opened_file = open(f"{dir_path}/results/{path}/densities.txt", 'r')

            title = path.split('/')[-2]
            legend.append(title)


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
target = 'results/energy'
all_paths = []
for i in range(0,10):
    sep = '/*'*i
    #layer = glob.glob(f'{dir_path}/{target}{sep}/atom_densities.png')
    #layer = glob.glob(f'{dir_path}/{target}{sep}/depth_results/densities.txt')
    layer = glob.glob(f'{dir_path}/{target}{sep}/depth_results/densities.txt')

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

combine = Combine(all_paths)
#combine.depth(carbon_final = True)
combine.saturate(y= 'sputt_yield')
