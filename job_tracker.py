
from ast import Index
from calendar import c
import subprocess
import os
import tools
import sys
from datetime import datetime



class Track:

     def __init__(self, file_name, srun_name = 'srun'):

          self.file_name = file_name
          self.srun_name = srun_name
          self.dir_path = os.path.dirname(os.path.realpath(__file__))

          self.job_ids = self.get_ids()
          self.recent_job = max(self.job_ids)

          self.job_str = self.get_job_details()

          self.new_file_check()

          self.publish_details()


     def get_ids(self, time = False):

          current_dir = os.path.dirname(os.path.realpath(__file__))

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

          if time == True:
               times = [vals[5] for vals in jobs_list if vals[0] != "'"]
               return job_ids, times

          else:
               return job_ids

     def get_job_details(self):

          settings_dict = tools.csv_reader(f"{self.dir_path}/results/{self.file_name}/settings.csv")
          settings_str = tools.cvs_maker("", settings_dict, write = False)

          srun_file = tools.file_proc(f"{self.dir_path}/results/{self.file_name}/{self.srun_name}")

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
          job_details_str += f'\nJob ID: {self.recent_job}'
          job_details_str += f'\nFile Name: {self.file_name}'
          job_details_str += f'\n\n{settings_str}'
          job_details_str += f'{srun_str}'

          return job_details_str


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
               os.system(f"mv {self.dir_path}/current_jobs.txt {self.dir_path}/job_history/jobs_{old_month}_{current_year}")

               with open(f"{self.dir_path}/current_jobs.txt", 'w') as fp:
                    fp.write(' ') 





def check_progress(file_name, id):

     
     job_ids, times = Track.get_ids(self = False, time = True)

     try:
          index = job_ids.index(int(id))
          current_time = times[index]
          if current_time == '0:00':
               return 0, 0, current_time
     except ValueError:
          return None, None, None

     log = tools.file_proc(f"{os.path.dirname(os.path.realpath(__file__))}/results/{file_name}/log.lammps", seperator='\n\n')
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



def get_info(job_id):

     success = False
     jobs = tools.file_proc(f"{os.path.dirname(os.path.realpath(__file__))}/current_jobs.txt", seperator= "-"*40) 

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

                    else:
                         time_perc = tools.time_percentage(current_time, total_time)
                         ion_perc = current_ion*100/total_ion

                         current_time_s = tools.time_convert(current_time, time_to_sec=True)
                         time_remaining_s =  (100/ion_perc - 1)*current_time_s
                         time_remaining = tools.time_convert(time_remaining_s, sec_to_time=True)
                         time = datetime.now()
                         finish_time = tools.time_add(time_remaining, time.strftime("%H:%M:%S"), add=True, time_of_day = True)
                         estimated_total_time = tools.time_add(current_time, time_remaining)


               
                         print("\n\n")
                         print(f"On {current_ion} out of {total_ion} ({ion_perc:.3g}%)")
                         print(f'Running for {current_time} out of {total_time} ({time_perc:.3g}%)')
                         
                         bars = int(current_ion*50/total_ion)
                         print('Ions: |','#'*bars,"_"*(50-bars),'|')

                         bars = int(time_perc/2)
                         print('Time: |','#'*bars,"_"*(50-bars),'|')
                         print(f'Estimated total time: {estimated_total_time}')
                         print(f'Estimated time remaining: {time_remaining}')
                         print(f'Estimated finish time: {finish_time}')


              

                    print(job)
                    success = True
                    break
          except IndexError:
               pass
     
     if success == False:
          print(f"\nERROR: Could not find {job_id} in current_jobs.txt.\n")


def run_multi_analysis(last_jobs = None, job_ids = [None], file_names = [None]):

     jobs = tools.file_proc(f"{os.path.dirname(os.path.realpath(__file__))}/current_jobs.txt", seperator= "-"*40)

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
          os.system(f"python lint.py True {file_name}")


     print(f"\n\nAnalysis attempted for: {to_run_file_names}\n\n")
     













   
if __name__ == "__main__":


     if sys.argv[1] == "-help":
          print("\n\nTo get job info, give job ID as arguemnt.")
          print("\nUse -multi followed by -last_jobs, -ids or -names and relevent arguments, to run analysis on multiple files.\n")

     if sys.argv[1] == '-multi':
          if sys.argv[2] == '-last_jobs':
               run_multi_analysis(last_jobs=int(sys.argv[3]))

          if sys.argv[2] == '-ids':
               run_multi_analysis(job_ids = sys.argv[3:])
   
          if sys.argv[2] == '-names':
               run_multi_analysis(file_names = sys.argv[3:])

     elif sys.argv[1] != '-help' and sys.argv[1] != 'multi':
          job_id = sys.argv[1]
          get_info(job_id)


          