

import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')

import ovito.extensions.pyscript

from ovito.io import *
from ovito.data import *
from ovito.modifiers import *
from ovito.pipeline import *
import numpy as np
import tools
from glob import glob
import sys
from tqdm import tqdm
import matplotlib.pyplot as plt 
import os



class Wigner_Seitz:

    def __init__(self, path, repeats):
        self.path = tools.Path(path)
        self.repeat_dirs_path = [tools.Path(path)[:-1] for path in glob(f"{args_dict['path']}*r/all.xyz")]

        tools.make_dir(f"{path}ovito_results")
       


    def get_array(self):

        results_arr = np.zeros([len(self.repeat_dirs_path), 3])

        vacanies_dict = dict()
        interstitials_dict = dict()
        etched_dict = dict()
      



        for i, path in enumerate(tqdm(self.repeat_dirs_path, desc=f'Running Ovito analysis')):
          
            try:    
                tools.all_splitter(f'{path}', start_end_only=True)
            except IndexError:
                raise IndexError(f"{path}")
         
            xyz_files = glob(f'{path}xyz_files/*.xyz')
    
            pipeline = import_file(f"{path}xyz_files/*.xyz")

            final_raw_data = pipeline.compute(frame=2)

            pipeline.modifiers.append(SelectTypeModifier(
                operate_on = "particles",
                property = "Particle Type",
                types = {2}))

            hydrogen_selected = pipeline.compute(frame=2)

            pipeline.modifiers.append(DeleteSelectedModifier())

            hydrogen_removed = pipeline.compute(frame=2)

            for p_type in  hydrogen_removed.particles['Particle Type'][...]:
                if p_type != 1:
                    raise TypeError("NOT ALL HYDROGEN WAS REMOVED.")

            hydrogen_removed_check = pipeline.compute(frame = 2)

            ws = WignerSeitzAnalysisModifier(
                per_type_occupancies = True,
                affine_mapping = ReferenceConfigurationModifier.AffineMapping.ToReference)
            pipeline.modifiers.append(ws)

            analysis = pipeline.compute(frame=2)

            vacanies = analysis.attributes['WignerSeitz.vacancy_count']
            interstitials = analysis.attributes['WignerSeitz.interstitial_count']
            lost_carbon = vacanies - interstitials

            results_arr[i] = np.array([vacanies, interstitials, lost_carbon])

            repeat = path[-1]

            try:
                vacanies_dict[str(vacanies)].append(repeat)
            except KeyError:
                vacanies_dict[str(vacanies)] = [repeat]

            try:
                interstitials_dict[str(interstitials)].append(repeat)
            except KeyError:
                interstitials_dict[str(interstitials)] = [repeat]

            try:
                etched_dict[str(lost_carbon)].append(repeat)
            except KeyError:
                etched_dict[str(lost_carbon)] = [repeat]


        self.results_arr = results_arr
        self.vacanies_dict = vacanies_dict 
        self.interstitials_dict = interstitials_dict 
        self.etched_dict = etched_dict 



    def publish_results(self):

        results = f'\nWigner Seitz analysis results for {args_dict["path"]} of {len(self.repeat_dirs_path)} repeated single bombardments.\n'

        non_zero_vacancies = [x for x in self.results_arr[:,0] if x > 0]
        number_with_vancanies = len(non_zero_vacancies)
        #results += f'\nRepeats with at least 1 vacancy: {number_with_vancanies*100/len(self.repeat_dirs_path):.3g} %\n'
        results += f'\nvacancy_perc: {number_with_vancanies*100/len(self.repeat_dirs_path):.3g} \n'

        average, stderr = tools.avg(self.results_arr[:,0])
        #results += f'\nAverage number of vacancies formed: {average:.6g} +/- {stderr:.3g}\n'
        results += f'\nvacancies: {average:.6g}'
        results += f'\nvacancies_err: {stderr:.3g}\n'

        non_zero_interstitials = [x for x in self.results_arr[:,1] if x > 0]
        number_with_interstitials = len(non_zero_interstitials)
        #results += f'\nRepeats with at least 1 interstitial: {number_with_interstitials*100/len(self.repeat_dirs_path):.3g} %\n'
        results += f'\ninterstitial_perc: {number_with_interstitials*100/len(self.repeat_dirs_path):.3g}\n'

        non_zero_etched = [x for x in self.results_arr[:,2] if x > 0]
        number_with_etched = len(non_zero_etched)
        #results += f'\nRepeats with at least 1 etched atom: {number_with_etched*100/len(self.repeat_dirs_path):.3g} %\n'
        results += f'\netched_perc: {number_with_etched*100/len(self.repeat_dirs_path):.3g} \n'

        average, stderr = tools.avg(self.results_arr[:,2])
        #results += f'\nAverage number of etched atoms: {average:.6g} +/- {stderr:.3g}\n'
        results += f'\netched: {average:.6g}\n'
        results += f'etched_err: {stderr:.3g}\n'

        average, stderr = tools.avg(self.results_arr[:,1])
        #results += f'\nAverage number of interstitials formed: {average:.6g} +/- {stderr:.3g}\n'
        results += f'\ninterstitials: {average:.6g}\n'
        results += f"interstitals_err: {stderr:.3g}\n"

        average, stderr = tools.avg(non_zero_vacancies)
        results += f'\nvacancies_zerosrem: {average:.6g}\n'
        results += f'vacancies_zerosrem_err: {stderr:.3g}\n'

        average, stderr = tools.avg(non_zero_interstitials)
        results += f'\ninterstitials_zerosrem: {average:.6g}\n'
        results += f'interstitials_zerosrem_err: {stderr:.3g}\n'

        average, stderr = tools.avg(non_zero_etched)
        results += f'\netched_zerosrem: {average:.6g}\n'
        results += f'etched_zerosrem_err: {stderr:.3g}\n'


        results += "\nAll vacancies (for avg and hist):\n"
        results += f"{self.results_arr[:,0]}\n"

        results += "\nAll interstitials (for avg and hist):\n"
        results += f"{self.results_arr[:,1]}\n"

        results += "\nAll etched atoms:"
        results += f'\n{self.results_arr[:,2]}\n'

        results += "\n\nvacancy_sims:"
        for key in self.vacanies_dict.keys():
            results += f"\n{key}_vacancies:"
            results += f'{self.vacanies_dict[key]}\n'

        results += "\n\ninterstitials_sims:"
        for key in self.interstitials_dict.keys():
            results += f"\n{key}_interstitials:"
            results += f'{self.interstitials_dict[key]}\n'

        results += "\n\netched_sims:"
        for key in self.etched_dict.keys():
            results += f"\n{key}_etched:"
            results += f'{self.etched_dict[key]}\n'

        with open(f"{args_dict['path']}ovito_results/ws_analysis.txt", 'w') as fp: #rewriting edited input file
            fp.write(results)

        '''
        plt.title('Vacancies')
        plt.hist(self.results_arr[:,0])
        plt.savefig(f"{args_dict['path']}/ovito_results/vacancies.png", dpi = 300)
        plt.close()

        plt.title('Interstitials')
        plt.hist(self.results_arr[:,1])
        plt.savefig(f"{args_dict['path']}/ovito_results/interstitials.png", dpi = 300)
        plt.close()

        plt.title('Lost Carbon')
        plt.hist(self.results_arr[:,2])
        plt.savefig(f"{args_dict['path']}/ovito_results/lost_carbon.png", dpi = 300)
        plt.close()
        '''



def main(args_dict):

    if args_dict['repeats'] == None:
        args_dict['repeats'] = tools.repeat_check(args_dict['path'])
    else:
        args_dict['repeats'] = tools.str_to_bool(args_dict['repeats'])

    args_dict['path'] = tools.Path(args_dict['path'])



    ws_obj = Wigner_Seitz(args_dict['path'], repeats=args_dict['repeats'])

    ws_obj.get_array()
    ws_obj.publish_results()

if __name__ == "__main__":

    accepted_args = ['repeats', 'path']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')

    main(args_dict)








