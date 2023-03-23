
import tools
import sys
import matplotlib.pylab as plt



def csv_reader(path):

    csv = tools.file_proc(f"{path}")

    


def main(args_dict):
    
    args_dict['path'] = tools.Path(args_dict['path'])

    csv = csv_reader(tools.Path(f"{args_dict['path']}/combined_{args_dict['analysis']}.csv"))
    



if __name__ == "__main__":

    accepted_args = ['path', 'analysis']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')

    main(args_dict)

