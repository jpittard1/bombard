




import tools
import sys
import glob
import matplotlib.pyplot as plt
import os


class Damage:

    def __init__(self, repeats, path):

        self.repeats = repeats
        self.path = path

        if self.repeats == False:
            self.settings_dict =  tools.csv_reader(f"{self.path}/settings.csv")

        try:
            os.mkdir(f"{self.path}/damage_results/")
        except FileExistsError:
            pass


    def get_repeated_damage_array(self, paths):

        vacancy_zs = []
        max_displacements = []
        etched_atoms = []

        for path in paths:
            dsp_file = tools.file_proc(f"{path}/final.dsp")
       
            try:
                array, titles = tools.custom_to_array(dsp_file)
                etched_atoms.append([row[-1] for row in array if row[-1] < - 2])
                vacancy_zs.append([self.find_original_position(array[i][-3:], array[i][1:4])[-1] for i, dsp in enumerate(array[:,4]) if dsp > 0.5])
                max_displacements.append(max(array[:,4]))
            except UnboundLocalError:
                print(f"Failed path: {path}")
                pass


        self.etched_atoms = [len(etched) for etched in etched_atoms]
        self.etched_atom_zs = sum(etched_atoms,[])
        self.vacancies = [len(vacancy_z) for vacancy_z in vacancy_zs]
        self.all_vancancy_zs = sum(vacancy_zs, [])
        self.max_displacements = max_displacements
        self.no_of_repeats = len(paths)
     



    def find_original_position(self, final, dsp):
        return final - dsp






    
    def publish_repeat_txt(self):
        
        results = f'\nDamage results for {self.path} of {self.no_of_repeats} repeated single bombardments.\n'
        number_with_vancanies = len([x for x in self.vacancies if x > 0])
        results += f'\nRepeats with at least 1 vacancy: {number_with_vancanies*100/self.no_of_repeats:.3g} %\n'

        average, stderr = tools.avg(self.vacancies)
        results += f'\nAverage number of vacancies formed: {average:.6g} ± {stderr:.3g}\n'

        average, stderr = tools.avg(self.all_vancancy_zs)
        results += f'\nVacancies formed at an average depth of: {average:.6g} ± {stderr:.3g}\n'

        number_with_etched = len([x for x in self.etched_atoms if x > 0])
        results += f'\nRepeats with at least 1 etched atom: {number_with_etched*100/self.no_of_repeats:.3g} %\n'

        average, stderr = tools.avg(self.etched_atoms)
        results += f'\nAverage number of etched atoms: {average:.6g} ± {stderr:.3g}\n'

        average, stderr = tools.avg(self.max_displacements)
        results += f'\nAverage maximum displacement: {average:.6g} ± {stderr:.3g}\n'
        results +=f"\nMaximum displacement: {max(self.max_displacements)}\n"

        results += "\nAll vacancies (for avg and hist):\n"
        results += f"{self.vacancies}\n"

        results += "\nAll vacancy inital zs  (for avg and hist):\n"
        results += f"{self.all_vancancy_zs}\n"

        results += "\nAll etched atoms:"
        results += f'\n{self.etched_atoms}\n'

        results += "\nAll etched atom final zs:"
        results += f'\n{self.etched_atom_zs}\n'

        results += "\nMax displacements (for avg and hist):\n"
        results += f"{self.max_displacements}\n"

        with open(f"{self.path}damage_results/damage.txt", 'w') as fp: #rewriting edited input file
            fp.write(results)

        plt.title('Depth of vancancies')
        plt.hist(self.all_vancancy_zs, bins = 30)
        plt.xlabel(f"z / A")
        plt.savefig(f"{self.path}damage_results/depth_of_vacancies.png", dpi = 150)
        plt.close()

        plt.title('Number of vancancies')
        plt.hist(self.vacancies, bins = 30)
        plt.xlabel(f"Number of vacancies")
        plt.savefig(f"{self.path}damage_results/number_of_vacancies.png", dpi = 150)
        plt.close()

        plt.title('Number of Etched Atoms')
        plt.hist(self.etched_atoms, bins = 30)
        plt.xlabel(f"Number of Etched Atoms")
        plt.savefig(f"{self.path}damage_results/number_of_etched_atoms.png", dpi = 150)
        plt.close()

        plt.title('Max Displacements')
        plt.hist(self.max_displacements, bins = 30)
        plt.xlabel(f"z / A")
        plt.savefig(f"{self.path}damage_results/max_displacements.png", dpi = 150)
        plt.close()
        










def main(args_dict):
   
    if args_dict['repeats'] == None:
        args_dict['repeats'] = tools.repeat_check(args_dict['path'])
    else:
        args_dict['repeats'] = tools.str_to_bool(args_dict['repeats'])

    args_dict['path'] = tools.Path(args_dict['path'])

    damage = Damage(args_dict['repeats'], args_dict['path'])

    repeated_paths = glob.glob(f"{tools.bombard_directory()}/{args_dict['path']}/*r/final.dsp")
  
    repeated_paths = [tools.Path(path)[:-1] for path in repeated_paths]

    damage.get_repeated_damage_array(repeated_paths)
    damage.publish_repeat_txt()





if __name__ == "__main__":

    accepted_args = ['repeats', 'path']

    try:
        args_dict = tools.args_to_dict(sys.argv[1:], accepted_args)   
    except IndexError:
        print('\n\nERROR: Please give inputs.\n\n')

    main(args_dict)