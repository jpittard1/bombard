

import sys
import os
import math
import numpy as np
from grain_maker_02 import Crystal

current_dir = os.path.dirname(os.path.realpath(__file__)).split('/')
sep = '/'
path = sep.join(current_dir[:-1])

sys.path.append(path)
import tools



def rotation_calc(miller_plane_str):
    """Calculates rotations required for desired orientation. Consider as two rotations,
    one about x then one about y. First rotation is simple, but second rotation requires 
    consideration of where the plane intercepts the z axis AFTER the initial rotation 
    abour x. No rotation requied in z as this is simply spinning the incident plane."""

    miller_plane_list = [int(i) for i in list(miller_plane_str)]

    recip_list = []
    for indice in miller_plane_list:
        try:
            recip_list.append(1/indice)
        except ZeroDivisionError:
            recip_list.append(1e30)


    x_rotation = math.atan(recip_list[2]/recip_list[1])
    y_rotation = np.pi/2 - math.atan(recip_list[0]/(recip_list[1]*math.sin(x_rotation)))
    z_rotation = 0 #no rotation for incident axis, might have messy edges?


    return np.array([x_rotation,-y_rotation,z_rotation])*180/np.pi


def main(args_dict):


    if args_dict['orientation'] != 'other':
        args_dict['rotation'] = rotation_calc(args_dict['orientation'])

    target_replicate = args_dict['replicate']
    rotation = args_dict['rotation']

    corner_to_corner = np.sqrt((target_replicate[0]/2)**2 + target_replicate[1]**2+ target_replicate[2]**2)
    replicate = [int(corner_to_corner)+1 for i in range(3)]

    trim = [[-replicate/2,replicate/2] for replicate in target_replicate]
    
    crys = Crystal(replicate = replicate)

    crys.shift('centre')
    crys.rotate(rotation)
    crys.trim(dict(x = trim[0],y = trim[1],z = trim[2]))
    crys.shift('corner')

    name = f"{int(target_replicate[0])}-{int(target_replicate[1])}-{int(target_replicate[2])}"
    name += f"_{args_dict['orientation']}"

    crys.name = name

    crys.publish(f"{os.path.dirname(os.path.realpath(__file__))}/data_files/")
    crys.minimise()
    crys.publish(f"{os.path.dirname(os.path.realpath(__file__))}/data_files/", 
                        f'data.{crys.name}_min', atoms_arr=crys.minimised_atoms_arr)

    crys.clean_up()



    


if __name__ == "__main__":

    accepted_args = ['replicate', 'orientation', 'rotation']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')


    
    try:
        args_dict['replicate'] = tools.str_to_list(args_dict['replicate'], float_vals = True)
    except TypeError:
        print("\n\nERROR: cannot accept replicate argument please input as:")
        print("\n\t\t-replicate '[5,5,4]'\n")
        print('for example.')


    
    if args_dict['orientation'] not in ['110', '111', 'other']:

        print("\n\nERROR: cannot accept orientation argument, accepted arguments are '110', '111' or 'other."
              "\nPlease input as:")
        print('\n\t\t-orientation 110\n')
        print('for example.\n\n')

        raise ValueError('See above description of error.')
    

    if args_dict['orientation'] =='other':
        try:
            args_dict['rotation'] = tools.str_to_list(args_dict['rotation'], float_vals = True)
        except TypeError:
            print("\n\nERROR: cannot accept rotation argument, for orientation = other, please input as:")
            print('\n\t\t-rotation [45,45,45]\n')
            print('for example.')


    main(args_dict)

