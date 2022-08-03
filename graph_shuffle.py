


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

    def
def combine(all_paths, method = 'depth', columns):

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
target = 'results/grain/30eV_angles'

all_paths = []
for i in range(0,10):
    sep = '/*'*i
    #layer = glob.glob(f'{dir_path}/{target}{sep}/atom_densities.png')
    #layer = glob.glob(f'{dir_path}/{target}{sep}/depth_results/densities.txt')
    layer = glob.glob(f'{dir_path}/{target}{sep}/depth_results/densities.txt')

    if len(layer) > 0:
        all_paths += layer



start_length = len(dir_path.split('/')) + 1
all_paths = [path.split('/')[start_length:-1] for path in all_paths]
sep = '/'
all_paths = [sep.join(path) for path in all_paths]

#pprint.pprint(all_paths)
#all_paths = ['4_4_6/t_0g_30eV_444_1', '6_6_6/t_0g_30eV_1000_5', '8_8_6/t_0g_30eV_1778_2', '10_10_6/t_0g_30eV_2778_1', '12_12_6/t_0g_30eV_4000_1']
#all_paths = [f'testing/size/{file}/depth_results' for file in all_paths]

print(all_paths)

combine(all_paths)
