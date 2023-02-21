




import time
from tqdm import tqdm
import tools
import glob
import sys


def main(args_dict):

    args_dict['path'] = tools.Path(args_dict['path'])

    file_name = args_dict['path'][-1]

    repeats_expected = int(file_name.split('_')[-2][:-1])

    already_found = len(glob.glob(f"{args_dict['path']}*r/data.diamond"))

    for i in tqdm(range(repeats_expected), desc='Repeats Found'):

        while True:
            
            if len(glob.glob(f"{args_dict['path']}*r/data.diamond")) >= (i + 1):
                break

            time.sleep(5)

    
if __name__ == "__main__":

    accepted_args = ['path']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')

    main(args_dict)


