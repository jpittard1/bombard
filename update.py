

import tools
import sys
import os
import combine_results


def path_check(path1, path2):

    if path1[-1] == path2[-1]:
        print(f"\n Path check complete.")
        return 'y'
    
    else:
        print('\nWarning, paths do not match.')
        print(f"\n {path1[-1]} != {path2[-1]}")
        return tools.input_misc(f"\nDo you wish to continue (y/n)?", ['y', 'n'])




def main(args_dict):

    onedrive_base_path = tools.Path('~/OneDrive\ -\ University\ of\ Bristol/PhD/Computational/Bombard/')
    args_dict['analysis_path'] = tools.Path(args_dict['analysis_path'])
    args_dict['onedrive_path'] = tools.Path(args_dict['onedrive_path'])

    print(f"\nUpdating {onedrive_base_path}{args_dict['onedrive_path']}")
    print(f"With {args_dict['analysis_path']}")

    cont_yn = tools.input_misc(f"\nDo you wish to continue (y/n)?", ['y', 'n'])

    if cont_yn == 'y':
        cont_yn = path_check(args_dict['analysis_path'],args_dict['onedrive_path'])

    if cont_yn == 'y':

        combine_args_dict = dict(path = args_dict['analysis_path'],
                                analysis = 'depth')

        combine_results.main(combine_args_dict)

        combine_args_dict = dict(path = args_dict['analysis_path'],
                                analysis = 'damage')

        combine_results.main(combine_args_dict)

        print(f"cp {tools.bombard_directory()}/{args_dict['analysis_path']}combined_depth.csv {onedrive_base_path}{args_dict['onedrive_path']}")
        os.system(f"cp {tools.bombard_directory()}/{args_dict['analysis_path']}combined_depth.csv {onedrive_base_path}{args_dict['onedrive_path']}")
        os.system(f"cp {tools.bombard_directory()}/{args_dict['analysis_path']}combined_damage.csv {onedrive_base_path}{args_dict['onedrive_path']}")

        print(f"\nUpdate successful.")






if __name__ == "__main__":


    accepted_args = [ 'analysis_path','onedrive_path']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')

    main(args_dict)