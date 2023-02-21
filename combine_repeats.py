

import tools
import sys
import glob
import os
from datetime import datetime
import shutil



def main(args_dict):

    args_dict['master_dir'] = tools.Path(args_dict['master_dir'])
    args_dict['branch_dir'] = tools.Path(args_dict['branch_dir'])

    branch_dirs = [tools.Path(path) for path in glob.glob(f"{tools.bombard_directory()}{args_dict['branch_dir']}*r")]
    master_dirs = [tools.Path(path) for path in glob.glob(f"{tools.bombard_directory()}{args_dict['master_dir']}*r")]

    branch_repeats = [int(branch_dir[-1][:-1]) for branch_dir in branch_dirs]
    master_repeats = [int(master_dir[-1][:-1]) for master_dir in master_dirs]

    if len(branch_dirs) == 0 or len(master_dirs) == 0:
        raise FileNotFoundError("One or both of the directories don't include repeat files.")

    if str(args_dict['master_dir']) == str(args_dict['branch_dir']):
        raise FileExistsError("Master dir and branch dir are the same.")


    #root_dirs = list(dict.fromkeys([dir.split('/')[-2] for dir in dirs]))

    print(f"\nYou are about to merge {len(branch_dirs) + len(master_dirs)} files in to 1 folder.")
    print(f"Folders to be combined: {args_dict['branch_dir']} >>> {args_dict['master_dir']}")

    continue_yn = tools.input_misc('Do you wish to continue (y/n)?: ', ['y','n'])
    '''
    if continue_yn == 'y':

        target_dir = args_dict['path'].split('/')[-2]
        name = dirs[0].split('/')[-2]
        name = name.split('_')
        new_dir_name = f"{name[0]}_{name[1]}_{name[2]}_{len(dirs)}r"

        count = 0
        while True:
            try:
                new_dir_name_full = f"{tools.bombard_directory()}/results/{target_dir}/{new_dir_name}_{count}"
                os.mkdir(f"{new_dir_name_full}")
                break
            except FileExistsError:
                count += 1

        count = 0
        for dir in dirs:

            os.system(f'mv -r {dir} {new_dir_name_full}')
    '''        
    
    try:
        record = open(f"{tools.bombard_directory()}{args_dict['master_dir']}/record.txt")
        record = record.read()

    except FileNotFoundError:
        record = ''

    record += "-"*40
    now = datetime.now()
    now = now.strftime("%d/%m/%Y %H:%M:%S")
    record += f"\n{now}"
    if continue_yn == 'y':

        for i, dir in enumerate(branch_dirs):
            
            new_repeat_dir_name = tools.Path(f"{dir[:-1]}/{max(master_repeats) + len(branch_repeats) - i}r")
            target = tools.Path(f"{tools.bombard_directory()}{args_dict['master_dir']}")

            print(f"\n\nmv {dir} to {new_repeat_dir_name}\n\n")

            shutil.move(f"{dir}", f"{new_repeat_dir_name}")
            shutil.move(f"{new_repeat_dir_name}", f"{target}")

            #os.system(f"mv {dir} {new_repeat_dir_name}")
            #os.system(f"mv {new_repeat_dir_name} {target}")

            record += f"\n{dir} >>> {target}/{len(master_dirs) + i}r"

        old_master_name = args_dict['master_dir'][-1]
        old_master_name = old_master_name.split('_')
        old_master_name[-2] = f"{len(branch_dirs) + len(master_dirs)}r"
     
        sep = '_'
        new_master_name = sep.join(old_master_name)
      
        new_path = str(target[:-1]) + '/' + new_master_name

        os.system(f"mv {target} {new_path}")

        record += f"\n\n {target} >>> {new_path}"
        print(f"mv {target} {new_path}")
        print(record)

        with open(f"{new_path}/record.txt", 'w') as fp: #rewriting edited input file
            fp.write(record)

















if __name__ == "__main__":

    accepted_args = ['master_dir', 'branch_dir', 'all_sets']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accecpted_args=accepted_args)   
    except IndexError or KeyError:
        print('\n\nERROR: Please give inputs.\n\n')
        print('Valid inputs: -master_dir -branch_dir -all_sets (boolean)')

    main(args_dict)
