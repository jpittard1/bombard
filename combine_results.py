


import tools
import sys
import glob




def depth_reader(file):

    split_file = tools.file_proc(file)
    depth_results_dict = dict()

    for i, line in enumerate(split_file):

        line = line.split()
        if len(line)>0:
            if line[0] == 'Depth':
                dir_name = line[3].split('/')[-2]
                depth_results_dict['dir_name'] = dir_name
                print(f'depth dirname : {dir_name}')
                depth_results_dict['atom_type'] = dir_name.split('_')[0]
                depth_results_dict['energy'] = dir_name.split('_')[1][:-2]
                depth_results_dict['repeats'] = line[5]

            elif line[-1] == 'reflected.':
                top, bottom = line[0].split('/')
                depth_results_dict['reflected'] = str(float(top)*100/float(bottom))

            elif line[-1] == 'implanted.':
                top, bottom = line[0].split('/')
                depth_results_dict['implanted'] = str(float(top)*100/float(bottom))

            elif line[0] == 'Average':
                depth_results_dict['average'] = line[-3]
                depth_results_dict['average_err'] = line[-1]
                
            elif line[0] == 'Max':
                depth_results_dict['max'] = str(float(split_file[i+1]))
            
            elif line[0] == 'Frozen':
                depth_results_dict['floor'] = str(min(tools.str_to_list(split_file[i+1], float_vals=True)))
                return depth_results_dict

            

def new_ovito_reader(file):

    split_file = tools.file_proc(file)
    ovito_results_dict = dict()

    for line in split_file:

        line = line.split()
        if len(line) > 0:
            if line[0] == 'Wigner':
                dir_name = line[5].split('/')[-2]
                ovito_results_dict['dir_name'] = dir_name
               
                ovito_results_dict['atom_type'] = dir_name.split('_')[0]
                ovito_results_dict['energy'] = dir_name.split('_')[1][:-2]
                ovito_results_dict['repeats'] = line[7]
            
            elif len(line) == 2:
                sep = ' '
                line = sep.join(line)
                line = line.split(': ')
           
                ovito_results_dict[line[0]] = line[1]

    return ovito_results_dict



def ovito_reader(file):

    split_file = tools.file_proc(file)
    ovito_results_dict = dict()

    for line in split_file:

        line = line.split()
        if len(line)>0:
            print(f"LINE: {line}")
            if line[0] == 'Wigner':
                dir_name = line[5].split('/')[-2]
                ovito_results_dict['dir_name'] = dir_name
                ovito_results_dict['atom_type'] = dir_name.split('_')[0]
                ovito_results_dict['energy'] = dir_name.split('_')[1][:-2]
                ovito_results_dict['repeats'] = line[7]

            elif line[-3] == 'vacancy:':
                ovito_results_dict['vacancy_perc'] = line[-2]

            elif line[3] == 'vacancies':
                ovito_results_dict['vacancies'] = line[-3]
                ovito_results_dict['vacancies_err'] = line[-1]

            elif line[-3] == 'interstitial:':
                ovito_results_dict['interstitial_perc'] = line[-2]

            elif line[3] == 'interstitials':
                ovito_results_dict['interstitials'] = line[-3]
                ovito_results_dict['interstitials_err'] = line[-1]

            elif line[-3] == 'atom:':
                ovito_results_dict['etched_perc'] = line[-2]

            elif line[3] == 'etched':
                ovito_results_dict['etched'] = line[-3]
                ovito_results_dict['etched_err'] = line[-1]

            elif line[5] == 'zeros(':
               
                if line[3] == 'etched':
                    ovito_results_dict['etched_zerosrem'] = line[-3]
                    ovito_results_dict['etched_zerosrem_err'] = line[-1]
                    print('here')
                    break

                elif line[3] == 'interstitials':
                    ovito_results_dict['interstitials_zerosrem'] = line[-3]
                    ovito_results_dict['interstitials_zerosrem_err'] = line[-1]

                elif line[3] == 'vacancies':
                    ovito_results_dict['vacancies_zerosrem'] = line[-3]
                    ovito_results_dict['vacancies_zerosrem_err'] = line[-1]


                return ovito_results_dict



def damage_reader(file):

    split_file = tools.file_proc(file)
    damage_results_dict = dict()

    for line in split_file:

        line = line.split()
        try:
            if line[0] == 'Damage':
                dir_name = line[3].split('/')[-2]
                damage_results_dict['dir_name'] = dir_name

                damage_results_dict['atom_type'] = dir_name.split('_')[0]
                damage_results_dict['energy'] = dir_name.split('_')[1][:-2]
                damage_results_dict['repeats'] = line[5]

            elif line[-3] == 'vacancy:':
                damage_results_dict['vacancy_perc'] = line[-2]

            elif line[-4] == 'formed:':
                damage_results_dict['average_vacancies'] = line[-3]
                damage_results_dict['average_vacancies_err'] = line[-1]

            elif line[-4] == 'of:':
                damage_results_dict['average_vacancy_depth'] = line[-3]
                damage_results_dict['average_vacancy_depth_err'] = line[-1]

            elif line[-3] == 'atom:':
                damage_results_dict['etched_perc'] = line[-2]

            elif line[-4] == 'atoms:':
                damage_results_dict['averaged_etched'] = line[-3]
                damage_results_dict['averaged_etched_err'] = line[-1]

            elif line[-4] == 'displacement:' and line[0] == 'Average':
                damage_results_dict['average_max_displacement'] = line[-3]
                damage_results_dict['average_max_dsiplacement_err'] = line[-1]

            elif line[0] == 'Maximum':
                damage_results_dict['max_displacement'] = line[-1]
                print(damage_results_dict)

            
        except IndexError:
            pass

    return damage_results_dict






def main(args_dict):
    
    if args_dict['analysis'] == 'depth':
        target = 'depth_results/depth.txt'
    elif args_dict['analysis'] == 'damage':
        target = 'damage_results/damage.txt'
    elif args_dict['analysis'] == 'ovito':
        target = 'ovito_results/ws_analysis.txt'
    else:
        raise ValueError('Please input analysis method (damage or depth)')

    star = '*/'
    count = 0
    while True:
        valid_files = glob.glob(f"{args_dict['path']}{star}{target}")
        if len(valid_files) > 0:
            break
        else:
            star += '*/'

        if count > 10:
            break
        count += 1


    analysis_dicts = dict()
    sep = ', '

    valid_files.sort()
 
    for i, file in enumerate(valid_files):

        if args_dict['analysis'] == 'depth':
            analysis_dict = depth_reader(file)
        elif args_dict['analysis'] == 'damage':
            analysis_dict = damage_reader(file)
        elif args_dict['analysis'] == 'ovito':
            analysis_dict = new_ovito_reader(file)

        analysis_dicts[analysis_dict['energy']] = analysis_dict

    energies = [int(energy) for energy in list(analysis_dicts.keys())]
    energies.sort()


    for i, energy in enumerate(energies):

        if i == 0:
            titles =  analysis_dict.keys()
            out_str = sep.join(titles) + '\n'

        out_str += sep.join(analysis_dicts[str(energy)].values()) + '\n'

    with open(f"{args_dict['path']}combined_{args_dict['analysis']}.csv", 'w') as fp: #rewriting edited input file
        fp.write(out_str)

    






if __name__ == "__main__":

    accepted_args = ['analysis', 'path']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')

    main(args_dict)