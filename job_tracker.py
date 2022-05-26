
import subprocess
import os
import tools
import sys
from datetime import datetime



class Track:

     def __init__(self, file_name):

          self.file_name = file_name
          self.dir_path = os.path.dirname(os.path.realpath(__file__))

          self.job_ids = self.get_ids()
          self.recent_job = max(self.job_ids)

          self.job_str = self.get_job_details()

          self.publish_details()


     def get_ids(self):

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

          return job_ids

     def get_job_details(self):

          settings_dict = tools.csv_reader(f"{self.dir_path}/results/{self.file_name}/settings.csv")
          settings_str = tools.cvs_maker("", settings_dict, write = False)

          srun_file = tools.file_proc(f"{self.dir_path}/results/{self.file_name}/srun")

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

          old_job_file = open(f"{self.dir_path}/jobs.txt", 'r')
          old_jobs_str = old_job_file.read()

          to_publish = '-'*40
          to_publish += '\n'
          to_publish += self.job_str
          to_publish += '\n'
          to_publish += old_jobs_str

          with open(f"{self.dir_path}/jobs.txt", 'w') as fp: #is this needed still?
               fp.write(to_publish) 




def get_info(job_id):

     success = False
     jobs = tools.file_proc(f"{os.path.dirname(os.path.realpath(__file__))}/jobs.txt", seperator= "-"*40) 

     for job in jobs:
          job_lines = job.split('\n')
          job_lines.remove('')

          try:
               id = job_lines[2].split(' ')[-1]

               if int(job_id) == int(id):
                    print(job)
                    success = True
                    break
          except IndexError:
               pass
     
     if success == False:
          print(f"\nERROR: Could not find {job_id} in jobs.txt.\n")


def run_multi_analysis(last_jobs = None, job_ids = [None], file_names = [None]):

     jobs = tools.file_proc(f"{os.path.dirname(os.path.realpath(__file__))}/jobs.txt", seperator= "-"*40)

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


          