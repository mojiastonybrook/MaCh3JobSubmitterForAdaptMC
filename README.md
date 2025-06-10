# How to use JobSubmitter on Cedar

An example of running `LetsGo_Adaptive_vGlob.py`

- Set up an environmental variable `OUTDIR`, indicating the directory where you want the outputs of running MaCh3 to be saved. For example,
  ```
  export OUTDIR=/home/mojia/scratch/jointfit/JointFit_detShiSme
  ```
- Go to the MaCh3 install directory and soure the `setup.sh` there to set up the MaCh3 related environmental variables.

- Back in the JobSubmitter directory, check the contents in the subdirectory `SampleConfigs` to find the config cards for the samples. If no files are found, copy the corresponding files from MaCh3 install to this subdirectory.
   
- Load the python module
  ```
  module load python
  ```
- Run the python script and answer the prompt questions
  ```
  python LetsGo_Adaptive_vGlob.py
  ```
- The script would ask sevaral questions for the exact setups of the batch of the parallel chains. Here is an specific example for those settings with some breif explanations. In principle the users could change the settings according to their actual needs.

   1. > Job Name?: 
      >
      > AM3StgBat1
      
      The remote job name appears on slurm.
   2. > How many jobs?:
      >
      > 4
      
      The number of job arrays inside this batch.
      Slurm supports a feature of utilizing job array for repetitive submissions of one SubmitScript. With this, the same one SubmitScript would be handed to the cluster for the same number of times as the job arrays, each time with an automatic changed id for separation.

   3. > How many GPUs per job?:
      >
      > 4
      > 
      > How many execs per job?:
      >
      > 4
      >
      > How many threads per job?:
      >
      > 32

      The compute resource settings for the chains in one job array.

      `execs` means an individual Markov chain. Usually 1 GPU and 8 threads are assigned to one chain. In this example, in one job array there are 4 chains thus 4 GPUs and 32 threads intotal should be provided to this one job array.

   4. > How many steps per chain?:
      >
      > 100000 

   5. > Executable to run? (Given in relative path to MaCh3 Install, e.g. ./bin/jointFit):
      >
      > ./AtmJointFit_Bin/JointAtmFit_Asimov
      
      The executables in MaCh3
      
   6. > Sample Config Direcotry:
      >
      > SampleConfigs

      Subdirectory of the templates for the samples

   7. > Run Script Name:
      >
      > RunScript.sh
      
      Template for the run script. The run script will call the exectuabe above to start the computing process.

   8. > Submit script to run? (Given in relative path to $PWD, e.g. ./SubmitScript.sh):
       >
       > SubmitScript_CC_2d.sh
       
       Template for the submission script. The submission script will ask the cluster the allocate the above computing resources and execute the run script. With job arrays, the submission script would repeat this process automatically.

    9. > Extra label string except for date to distinguish several trials in one day? (eg: trial_n) :
        >
        > batch_0
        
        A certain label to distinguish different batches of chains

    10. > Submit jobs to queue? (1 for yes, 0 for no):

        If yes, then the jobs would be submitted automatically after the files are prepared.

        If no, the files would be prepared but not submitted to the cluster. 

- Check the newly created the subdirectory.

  There should be a new subdirectory named with the date when the users create it. In that directory a subdirectory with the label provided in Step.11 would appear, then further inside it the subdirectories for the iterations. In the SubmitScript subdirectory of a certain iteration directory exist the configuration cards for the chains in this batch, along with the run script and submission script.

  According to the example settings above, in one batch a total of 16 chains should be generated, because we require 4 job arrays and in one array 4 parallel chains.

