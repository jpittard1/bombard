

import subprocess
from os import path as os_path
import tools
from sys import argv
from datetime import datetime
from glob import glob
from tqdm import tqdm
import shutil


class Track:

     def __init__(self, file_name, srun_name = 'srun', repeats = False):

          self.file_name = file_name
          self.srun_name = srun_name
          self.dir_path = os_path.dirname(os_path.realpath(__file__))
          self.repeats = repeats
          if self.repeats == False:

               self.job_ids = self.get_ids()
               self.recent_job = max(self.job_ids)

               self.job_str = self.get_job_details()

          
          elif self.repeats == True:
               
               
               self.recent_job =  self.get_ids_for_repeats()

               self.job_str = self.get_job_details()


          self.new_file_check()
          self.publish_details()

 


     def get_ids(self, time = False):

          current_dir = os_path.dirname(os_path.realpath(__file__))

          proc = subprocess.Popen(["squeue -u jp17358", current_dir], stdout=subprocess.PIPE, shell=True) 

          (out, err) = proc.communicate() 
          out = str(out)
          out = out.split("\\n")
          jobs = out[1:]

          jobs_lines = [item.split(' ') for item in jobs]


          jobs_list = []
          for job_line in jobs_lines:
               job_line = [item for item in job_line if item != '']
               jobs_list.append(job_line)

          job_ids = [vals[0] for vals in jobs_list if vals[0] != "'"]
          job_ids = [int(i) for i in job_ids]

          print(f'\n\n{len(job_ids)} jobs in queue.\n\n')

          if time == True:
               times = [vals[5] for vals in jobs_list if vals[0] != "'"]
               return job_ids, times

          else:
               return job_ids

     def check_for_new_id(self):

          job_file = tools.file_proc(f"{self.dir_path}/current_jobs.txt", seperator="-"*40)

        
          for line in job_file[1].split('\n'):
               line = line.split(' ')
     
               if line[0] == 'Job':
                    last_id = line[2]
                    return last_id
          

     def get_ids_for_repeats(self):
          all_ids = self.get_ids()
          last_id = self.check_for_new_id()

          all_ids.sort(reverse=True)
   
          
          try:
               new_ids = all_ids[:all_ids.index(int(last_id))]

          except ValueError:
               new_ids = all_ids


          

          out_str = ''

          id_list_of_lists = []

          differences = [int(id_str) - int(new_ids[i+1])  for i, id_str in enumerate(new_ids[:-1])]
          gap_indexes = [i for i, difference in enumerate(differences) if difference != 1]
  
          if len(gap_indexes) == 0:
               id_list_of_lists = [new_ids]
          else:
               start = 0
               for i2, index in enumerate(gap_indexes):
                    id_list_of_lists.append(new_ids[start:index+1])
                    start = index+1

          output_str = ''
          for id_list in id_list_of_lists:
               if len(id_list) > 2:
                    output_str += f"{max(id_list)} - {min(id_list)}, "
               elif len(id_list) == 2:
                    output_str += f"{max(id_list)}, {min(id_list)}, "
               else:
                    output_str += f"{max(id_list)}, "


          return output_str




     def get_job_details(self):

          if self.repeats == True:
               file_name = f'{self.file_name}/0r'
          else:
               file_name = self.file_name

          settings_dict = tools.csv_reader(f"{self.dir_path}/results/{file_name}/settings.csv")
          settings_str = tools.cvs_maker("", settings_dict, write = False)

          srun_file = tools.file_proc(f"{self.dir_path}/results/{file_name}/{self.srun_name}")

          srun_str = ''
          node_info = False
          for line in srun_file:
               
               if line == '#! Mail to user if job aborts':
                    break


               if node_info == True:
                    line = line.split("--")
                    srun_str += f"\n{line[-1]}"


               if line == '## For BC4:':
                    node_info = True

          now = datetime.now()
          now = now.strftime("%d/%m/%Y %H:%M:%S")

          job_details_str = f'\n{now}'
          job_details_str += f'\nJob ID(s): {self.recent_job}'
          job_details_str += f'\nFile Name: {self.file_name}'

          if self.repeats == True:
               job_details_str += f"\nRepeats: {len(glob(f'{self.dir_path}/results/{self.file_name}/*r'))}"

          job_details_str += f'\n\n{settings_str}'
          job_details_str += f'{srun_str}'

          return job_details_str

     def current_jobs_names_dict(self):

          current_jobs_names_dict = dict()
          jobs = tools.file_proc(f"{tools.bombard_directory()}/current_jobs.txt", seperator= "-"*40) 

          for job in tqdm(jobs, 'Reading current_jobs.txt'):
               for line in job.split('\n'):
                    line = line.split(': ')

                    if line[0] == 'Job ID(s)':
                         ids = line[-1]

                    elif line[0] == 'File Name':
                         current_jobs_names_dict[line[-1]] = ids
                         break 

          return current_jobs_names_dict


     def publish_details(self):

          old_job_file = open(f"{self.dir_path}/current_jobs.txt", 'r')
          old_jobs_str = old_job_file.read()

          to_publish = '-'*40
          to_publish += '\n'
          to_publish += self.job_str
          to_publish += '\n'
          to_publish += old_jobs_str

          with open(f"{self.dir_path}/current_jobs.txt", 'w') as fp: 
               fp.write(to_publish) 

     def new_file_check(self):
          job_file = tools.file_proc(f"{self.dir_path}/current_jobs.txt", seperator="-"*40)
          now = datetime.now()
          
          try: 
               date = job_file[-2].split('\n')[2]
               date = date.split(' ')[0]
               old_month = date.split('/')[1]
          except IndexError:
               old_month = now.strftime("%m")


          current_month = now.strftime("%m")
          current_year = now.strftime("%Y")


          if old_month != current_month:
               shutil.move(f'{self.dir_path}/current_jobs.txt', f'{self.dir_path}/job_history/jobs_{old_month}_{current_year}')

               with open(f"{self.dir_path}/current_jobs.txt", 'w') as fp:
                    fp.write(' ') 



def all_jobs_progress():

     job_ids, times = Track.get_ids(self = False, time = True)

     for id in job_ids:
          get_info(id, only_progress = True)


def analysis_check(file_name):

     bombard_dir = tools.bombard_directory()
     file_exists = False
     failed = False
     analysis_performed = False
     cleanup_performed = True

     try:
          open(f"{bombard_dir}/results/{file_name}/OUT")
          file_exists = True

          open(f"{bombard_dir}/results/{file_name}/jmol_all.xyz")
          analysis_performed = True

          open(f"{bombard_dir}/results/{file_name}/xyz_files/0.xyz")
          cleanup_performed = False

     except FileNotFoundError:
          if analysis_performed == False:
               try:
                    open(f"{bombard_dir}/results/{file_name}/0.xyz")
               except FileNotFoundError:
                    failed = True


     return file_exists, failed, analysis_performed, cleanup_performed
          

def check_repeat_progress(args_dict):
     bombard_dir = tools.bombard_directory()
     path = args_dict['path']
     repeat_paths = glob(f"{bombard_dir}{path}/*r")
     print(f"Checking current_jobs.txt")
     current_job_names = Track.current_jobs_names_dict(self=None)
     
     running_sims = 0
     failed_sims = 0
     complete_sims = 0
     analysed_sims = 0
     clean_dirs = 0
     failed_sims_list = []
     analysis_started  = False





     for path in tqdm(repeat_paths, desc = 'Reading files'):
          
          analysis_check = tools.path_check(f'{path}/all.xyz')
      
          if analysis_check == True:
               analysis_started = True
               analysed_sims += 1
               complete_sims += 1
               running_sims += 1

               clean_check = tools.path_check(f'{path}/xyz_files/0.xyz')
               if clean_check == False:
                    clean_dirs += 1

          elif analysis_started == False:
               running_check = tools.path_check(f'{path}/0.xyz')

               if running_check == True:
                    running_sims += 1

                    out_files = tools.file_proc(f'{path}/OUT')
                    out_files.reverse()

                    for line in out_files[:50]:
                         line = line.split(':')

                         if line[0] == 'Total wall time':
                              complete_sims += 1
                              break

                         elif line[0] == 'slurmstepd':
                              failed_sims += 1
                              failed_sims_list.append(path.split('/')[-1])
                              break


     try:
          running_perc = running_sims*100/len(repeat_paths)
          complete_perc = complete_sims*100/len(repeat_paths)
          analysed_perc = analysed_sims*100/len(repeat_paths)
          clean_perc = clean_dirs*100/len(repeat_paths)
     except ZeroDivisionError:
          raise FileNotFoundError(f'Could not find repeats in {bombard_dir}/{path}/*r')

     file_name = path.split('/')[-2]

     ids = current_job_names[file_name]

     print(f"\nJob ID(s): {ids}")
     print(f"File name: {file_name}")
     print(f"Failed simulations detected: {failed_sims}/{len(repeat_paths)}")

     if analysis_started == False:
          print(f'Repeats Running: {running_sims}/{len(repeat_paths)} ({running_perc:.3g}%)')
          print(f"Repeats Complete: {complete_sims}/{len(repeat_paths)} ({complete_perc:.3g}%)")

     print(f"Repeats Analysed: {analysed_sims}/{len(repeat_paths)} ({analysed_perc:.3g}%)")
     print(f"Clean directories: {clean_dirs}/{len(repeat_paths)} ({clean_perc:.3g}%)")

     if analysis_started == False:
          bars = int(running_sims*50/len(repeat_paths))
          print('Repeats Running:  |','#'*bars,"_"*(50-bars),'|')
          bars = int(complete_sims*50/len(repeat_paths))
          print('Repeats Complete: |','#'*bars,"_"*(50-bars),'|')

     bars = int(analysed_sims*50/len(repeat_paths))
     print('Repeats Analysed: |','#'*bars,"_"*(50-bars),'|')
     bars = int(clean_dirs*50/len(repeat_paths))
     print('Clean directories: |','#'*bars,"_"*(50-bars),'|')

     if failed_sims != 0:
          out = 'Failed simulation directories:\n'
          for fail_dir in failed_sims_list:
               out += f"{fail_dir}, "
          print(out)
               
          remove_yn = tools.input_misc('Remove all failed directories (y/n)? ', ['y','n'])

          if remove_yn == 'y':
               print("This will delete:")
               for fail_dir in failed_sims_list:
                    print(f'   {bombard_dir}/{args_dict["path"]}/{fail_dir}')

               cont_yn = tools.input_misc('Do you wish to continue (y/n)? ', ['y','n'])

               if cont_yn == 'y':

                    for fail_dir in tqdm(failed_sims_list, desc = 'Deleting', ascii= False, ncols=100):
                         shutil.rmtree(f'{bombard_dir}/{args_dict["path"]}/{fail_dir}')



     return running_sims, len(repeat_paths)



def recent_jobs():
     
     jobs = tools.file_proc(f"{os_path.dirname(os_path.realpath(__file__))}/current_jobs.txt", seperator= "-"*40)
     jobs.remove('')
     print(f"Last Completed Jobs:")
     completed_jobs = []
     job_ids, times = Track.get_ids(self = False, time = True)


     id_lists_dict = dict(no_dirs = [],
                         queue = [],
                         running = [],
                         failed_sims = [],
                         needs_analysis = [],
                         needs_cleaning = [],
                         complete = [])

     file_name_lists_dict = dict(no_dirs = [],
                         queue = [],
                         running = [],
                         failed_sims = [],
                         needs_analysis = [],
                         needs_cleaning = [],
                         complete = [])

     for job in jobs:

          job_lines = job.split('\n')
          job_lines.remove('')

          date_time = job_lines[1]
          id = job_lines[2].split(' ')[-1]
          file_name = job.split('\n')[4][11:]

          file_found, failed, analysis_performed, cleanup_performed = analysis_check(file_name)


          if file_found == False:
               if int(id) in job_ids:
                    status = 'In the queue.'
                    id_lists_dict['queue'].append(id)
                    file_name_lists_dict['queue'].append(file_name)

               else:
                    status = 'Directory not found.'
                    id_lists_dict['no_dirs'].append(id)
                    file_name_lists_dict['no_dirs'].append(file_name)

          elif failed == True:
               status = 'Simulation Failed.'
               id_lists_dict['failed_sims'].append(id)
               file_name_lists_dict['failed_sims'].append(file_name)

          elif analysis_performed == False:
               if int(id) in job_ids:
                    status = 'Running.'
                    id_lists_dict['running'].append(id)
                    file_name_lists_dict['running'].append(file_name)

               else:
                    status = 'Needs analysis.'
                    id_lists_dict['needs_analysis'].append(id)
                    file_name_lists_dict['needs_analysis'].append(file_name)

          elif cleanup_performed == False:
               status = 'Analysis complete, needs cleaning.'
               id_lists_dict['needs_cleaning'].append(id)
               file_name_lists_dict['needs_cleaning'].append(file_name)

          elif cleanup_performed == True:
               status = 'Analysis and clean up complete.'
               id_lists_dict['complete'].append(id)
               file_name_lists_dict['complete'].append(file_name)

      
          print(f'{file_name} ({id}) - {date_time}, {status} ')
               

          if len(completed_jobs) == 10:
               break
     
  
     sep = ' '

     print("\nIn queue:")
     print(f"{sep.join(id_lists_dict['queue'])}")
     print(f"{sep.join(file_name_lists_dict['queue'])}")

     print("\nRunning:")
     print(f"{sep.join(id_lists_dict['running'])}")
     print(f"{sep.join(file_name_lists_dict['running'])}")
     
     print("\nNot found:")
     print(f"{sep.join(id_lists_dict['no_dirs'])}")
     print(f"{sep.join(file_name_lists_dict['no_dirs'])}")

     print("\nFailed:")
     print(f"{sep.join(id_lists_dict['failed_sims'])}")
     print(f"{sep.join(file_name_lists_dict['failed_sims'])}")

     print("\nNeeds analysis:")
     print(f"{sep.join(id_lists_dict['needs_analysis'])}")
     print(f"{sep.join(file_name_lists_dict['needs_analysis'])}")

     print("\nNeeds cleaning:")
     print(f"{sep.join(id_lists_dict['needs_cleaning'])}")
     print(f"{sep.join(file_name_lists_dict['needs_cleaning'])}")

     print("\nComplete and clean:")
     print(f"{sep.join(id_lists_dict['complete'])}")
     print(f"{sep.join(file_name_lists_dict['complete'])}\n\n")


     

def check_progress(file_name, id):
     
     job_ids, times = Track.get_ids(self = False, time = True)

     try:
          index = job_ids.index(int(id))
          current_time = times[index]
          if current_time == '0:00':
               return 0, 0, current_time
     except ValueError:
          return None, None, None

     log = tools.file_proc(f"{os_path.dirname(os_path.realpath(__file__))}/results/{file_name}/log.lammps", seperator='\n\n')
     log = [i for i in log if i != '']

     start = log[0].split('\n')
     total_loop = int(start[-1].split(' ')[-1])

    

     for index in range(len(log), 0, -1):
          try:
               line = log[index].split()
               if line[0] == 'next' and line[1] == 'd':
                    section = log[index].split('\n')
                    section = section[2].split(' ') 
                    current_ions = int(section[4]) - 1
         
                    return current_ions, total_loop, current_time   
          except IndexError:
               pass

     return 0,  total_loop, current_time



def get_info(job_id, only_progress = False):

     success = False
     jobs = tools.file_proc(f"{os_path.dirname(os_path.realpath(__file__))}/current_jobs.txt", seperator= "-"*40) 

     for job in jobs:
          job_lines = job.split('\n')
          job_lines.remove('')

          try:
               id = job_lines[2].split(' ')[-1]

               if int(job_id) == int(id):

                    file_name = job.split('\n')[4][11:]
                    total_time = job.split('\n')[-4][5:]
                  
                    current_ion, total_ion, current_time = check_progress(file_name, job_id)

                    if current_time == None:

                         print("\n\nSimulation Complete.")

                    
                    elif current_time == '0:00':

                         print("\n\nSimulation yet to start.")

                    elif current_ion == 0:

                         print("\n\nNo ion bombardments yet.")

                    else:
                         time_perc = tools.time_percentage(current_time, total_time)
                         ion_perc = current_ion*100/total_ion

                         current_time_s = tools.time_convert(current_time, time_to_sec=True)
                         time_remaining_s =  (100/ion_perc - 1)*current_time_s
                         time_remaining = tools.time_convert(time_remaining_s, sec_to_time=True)
                         time = datetime.now()
                         finish_time = tools.time_add(time_remaining, time.strftime("%H:%M:%S"), add=True, time_of_day = True)
                         estimated_total_time = tools.time_add(current_time, time_remaining)


               
                         if only_progress == True:
                     
                              print(f"\n{id} - {file_name}")
                              print(f'Time: {current_time}/{total_time} ({time_perc:.3g}%), Ions: {current_ion}/{total_ion} ({ion_perc:.3g}%)')
                              bars = int(current_ion*50/total_ion)
                              print('Ions: |','#'*bars,"_"*(50-bars),'|')
                              print(f'Estimated finish time: {finish_time}\n')
             

                         else:
                              print('\n')
                              print(f"On {current_ion} out of {total_ion} ({ion_perc:.3g}%)")
                              print(f'Running for {current_time} out of {total_time} ({time_perc:.3g}%)')
                              
                              bars = int(current_ion*50/total_ion)
                              print('Ions: |','#'*bars,"_"*(50-bars),'|')

                              
                              bars = int(time_perc/2)
                              print('Time: |','#'*bars,"_"*(50-bars),'|')

                              print(f'Estimated total time: {estimated_total_time}')
                              print(f'Estimated time remaining: {time_remaining}')
                              print(f'Estimated finish time: {finish_time}')


              
                    if only_progress == False:
                         print(job)

                    success = True
                    break
          except IndexError:
               pass
     
     if success == False:
          print(f"\nERROR: Could not find {job_id} in current_jobs.txt.\n")





def run_multi_analysis(last_jobs = None, job_ids = [None], file_names = [None]):

     jobs = tools.file_proc(f"{os_path.dirname(os_path.realpath(__file__))}/current_jobs.txt", seperator= "-"*40)

     to_run_file_names = []

     if last_jobs != None:
          jobs = jobs[:int(last_jobs+1)]

          for job in jobs:
               job_lines = job.split('\n')
               job_lines.remove('')

               try:
                    to_run_file_names.append(job_lines[3].split(' ')[-1])

               except IndexError:
                    pass

     elif job_ids[0] != None:

          for job in jobs:
               job_lines = job.split('\n')
               job_lines.remove('')

               try:
                    if job_lines[2].split(' ')[-1] in job_ids:
                         to_run_file_names.append(job_lines[3].split(' ')[-1])

               except IndexError:
                    pass

     
     elif file_names[0] != None:
          to_run_file_names = file_names

     
     for file_name in to_run_file_names:
          subprocess.run(['python', 'lint.py', 'True', f'{file_name}'])

     print(f"\n\nAnalysis attempted for: {to_run_file_names}\n\n")
     



def main(args_dict):

     if tools.str_to_bool(args_dict['repeats']) == True:
          check_repeat_progress(args_dict)

     elif tools.str_to_bool(args_dict['recent']) == True:
          recent_jobs()

     elif tools.str_to_bool(args_dict['multi']):
          if tools.str_to_bool(args_dict['last_jobs']) == True:
               run_multi_analysis(last_jobs=int(argv[3]))

          if tools.str_to_bool(args_dict['ids']) == True:
               run_multi_analysis(job_ids = argv[3:])

          if tools.str_to_bool(args_dict['names']) == True:
               run_multi_analysis(file_names = argv[3:])

     else:
          job_id = argv[1]
          get_info(job_id)









   
if __name__ == "__main__":

     accepted_args = ['repeats', 'multi', 'ids', 'names', 'last_names', 'recent', 'path']

     if len(argv) == 1:
          all_jobs_progress()

     elif argv[1] == "-help":
          print("\n\nTo get job info, give job ID as arguemnt.")
          print("\nUse -multi followed by -last_jobs, -ids or -names and relevent arguments, to run analysis on multiple files.\n")

     else: 
          args_dict = tools.args_to_dict(argv[1:], accepted_args)   
          main(args_dict)


          


          