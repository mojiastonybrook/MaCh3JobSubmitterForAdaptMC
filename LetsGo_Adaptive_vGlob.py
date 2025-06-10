import os
import sys
import subprocess
from datetime import datetime

def replaceText(File,oldText,newText):
        with open(File) as f:
            newText=f.read().replace(oldText,newText)
        with open(File,"w") as f:
            f.write(newText)

def read_job_setting():
    print("\n")
    
    WorkDirectory = os.environ['PWD']
    
    try:
        MaCh3Install = os.environ['MACH3']
    except:
        print("MaCh3 install not found. Please source setup.sh in MaCh3 install or export $MACH3=/path/to/MACH3")
        quit()

    if (os.path.exists(MaCh3Install) == False):
        print("MaCh3 install not found. Given:"+MaCh3Install)
        quit()

    try:
        JobName = input("Job Name?: ")
    except:
        JobName = "MaCh3"
        
    try:
        nJobs = int(input("How many jobs?: "))
    except:
        print("Invalid number of jobs")
        quit()

    try:
        nGPUsPerJob = int(input("How many GPUs per job?: "))
    except:
        print("Invalid number of GPUs")
        quit()

    try:
        nExecsPerJob = int(input("How many execs per job?: "))
    except:
        print("Invalid number of execs per job")
        quit()        

    try:
        nThreads = int(input("How many threads per job?: "))
    except:
        print("Invalid number of threads")
        quit()

    try:
        nSteps = int(input("How many steps per chain?: "))
    except:
        print("Invalid number of steps")
        quit()

    if (nThreads == 0):
        print("\tDefaulting to use 1 thread")
        nThreads = 1
           
    ExecName = ""
    try:
        ExecName = input("Executable to run? [Given in relative path to MaCh3 Install, e.g. ./AtmJointFit_Bin/JointAtmFit]: ")
    except:
        print("Invalid executable name")

    if ((os.path.exists(MaCh3Install+"/"+ExecName) == False) or (ExecName == "")):
        
        print("\tExecutable:"+ExecName+" not found in MaCh3 install:"+MaCh3Install)
        ExecName = "./AtmJointFit_Bin/JointAtmFit"
        if (os.path.exists(MaCh3Install+"/"+ExecName) == True):
            print("\tDefaulting to use: "+ExecName)
        else:
            print("Invalid executable name")
            quit()
        
    try:
        SampleConfigDir = input("Sample Config Direcotry:")
    except:
        print("Invalid sample config directory string")
        quit()

    if (os.path.exists(WorkDirectory+"/"+SampleConfigDir) and (SampleConfigDir != '')):
        SampleConfigDir = WorkDirectory+"/"+SampleConfigDir
    else:
        print("SampleConfigDir: "+SampleConfigDir+" not found in current working directory: "+WorkDirectory)
        SampleConfigDir = WorkDirectory+"/SampleConfigs/"

        if (os.path.exists(SampleConfigDir)):
            print("\tDefaulting to use: "+SampleConfigDir)
        else:
            print("Not found valid run script")
            quit()
            
    try:
        RunScriptName = input("Run Script template name:")
    except:
        print("Invalid run script name string")
        quit()

    if (os.path.exists(WorkDirectory+"/"+RunScriptName) and (RunScriptName != '')):
        RunScriptName = WorkDirectory+"/"+RunScriptName
    else:
        print("\tRunScript: "+RunScriptName+" not found in current working directory: "+WorkDirectory)
        RunScriptName = WorkDirectory+"/RunScript.sh"

        if (os.path.exists(RunScriptName)):
            print("\tDefaulting to use: "+RunScriptName)
        else:
            print("Not found valid run script")
            quit()
            
    try:
        SubmitScriptName = input("Submit script template [Given in relative path to $PWD, e.g. ./SubmitScript.sh]: ")
    except:
        print("Invalid submit script name")

    if ((os.path.exists(WorkDirectory+"/"+SubmitScriptName) == False) or (SubmitScriptName == "")):
        print("\tSubmitScript: "+SubmitScriptName+" not found in current working directory: "+WorkDirectory)

        SubmitScriptName = "./SubmitScript.sh"
        if (os.path.exists(WorkDirectory+"/"+SubmitScriptName)):
            print("\tDefaulting to use: "+SubmitScriptName)
        else:
            print("Not found valid SubmitScript")
    else:
        SubmitScriptName = WorkDirectory+"/"+SubmitScriptName


    try:
        ExtraLabel = input("Extra label string except for date to distinguish several trials in one day? [eg: trial_n] : ")
    except:
        print("Invalid answer")
        quit()
        
    if (ExtraLabel == ""):
        print("Setting label to be trial_0")
        ExtraLabel = "trial_0"
        
        
    try:
        OutDirectory = os.environ['OUTDIR']
    except:
        print("Output directory not found. Using current directory. If this is not acceptable, export OUTDIR=/path/to/output")
        OutDirectory = os.environ['PWD']
       
    print("\n\n")
    print("Summary: ---------")
    print("\tMaCh3 Install:"+MaCh3Install)
    print("\tNumber of Jobs:"+str(nJobs))
    print("\tNumber of GPUs per Job:"+str(nGPUsPerJob))
    print("\tNumber of Executables per Job:"+str(nExecsPerJob))
    print("\tNumber of Steps per Job:"+str(nSteps))
    print("\tNumber of Threads per Job:"+str(nThreads))
    print("\tExecutable:"+ExecName)
    print("\tSample Config Directory:"+SampleConfigDir)
    print("\tBase RunScript:"+RunScriptName)
    print("\tBase SubmitScript:"+SubmitScriptName)
    print("\tOutput Directory:"+OutDirectory)

    return {'JobName': JobName,
            'MaCh3Install': MaCh3Install, 
            'JobNumber': nJobs,
            'GPUPerJob': nGPUsPerJob,
            'ExecPerJob': nExecsPerJob,
            'Steps': nSteps,
            'ThreadPerJob': nThreads,
            'Exec': ExecName,
            'SampleCfgDir': SampleConfigDir,
            'RunScriptTemp': RunScriptName,
            'SumbitScriptTemp': SubmitScriptName,
            'Label': ExtraLabel,
            'OutDir': OutDirectory
            }

def prepare_files(chain_setting, adaptive_setting, iStage, iIteration):
    #executable configuration card template for AM
    WorkDirectory = os.environ['PWD']
    #ConfigName = "AtmConfig_adaptiveMC_temp.cfg"
    ConfigName = "AtmConfig_adaptiveMC_temp_GlobalSize.cfg"
    if (os.path.exists(WorkDirectory+"/"+ConfigName) and (ConfigName != '')):
        ConfigName = WorkDirectory+"/"+ConfigName
    else:
        print("\tConfig: "+ConfigName+" not found in current working directory: "+WorkDirectory)
        quit()

    #prepare all files for a job
    now = datetime.now()
    date_waterprint = now.strftime("%m%d%Y")
    
    if (iIteration == 0):
        StartFromFile = False
    else:
        StartFromFile = True

    FileNameBase_iIter = "Iter_"+str(iIteration)
    FileNameBase_m1_iIter = "Iter_"+str(iIteration-1)

    ScriptDir_iIter = WorkDirectory+"/"+date_waterprint+"/"+chain_setting['Label']+"/Stage_"+str(iStage)+"/Script_"+FileNameBase_iIter+"/"
    ScriptDir_Log_iIter = ScriptDir_iIter+"SubmitLog"
    ScriptDir_Error_iIter = ScriptDir_iIter+"SubmitError"
    ScriptDir_Output_iIter = ScriptDir_iIter+"SubmitOutput"
    ScriptDir_Submit_iIter = ScriptDir_iIter+"SubmitScript"

    MkdirCommand  = "mkdir -p "+ScriptDir_iIter
    os.system(MkdirCommand)
    MkdirCommand  = "mkdir -p "+ScriptDir_Log_iIter
    os.system(MkdirCommand)
    MkdirCommand  = "mkdir -p "+ScriptDir_Error_iIter
    os.system(MkdirCommand)
    MkdirCommand  = "mkdir -p "+ScriptDir_Output_iIter
    os.system(MkdirCommand)
    MkdirCommand  = "mkdir -p "+ScriptDir_Submit_iIter
    os.system(MkdirCommand)

    OutDir_iIter = chain_setting['OutDir']+"/"+date_waterprint+"/"+chain_setting['Label']+"/Stage_"+str(iStage)+"/Output_"+FileNameBase_iIter+"/"
    OutDir_m1_iIter = chain_setting['OutDir']+"/"+date_waterprint+"/"+chain_setting['Label']+"/Stage_"+str(iStage)+"/Output_"+FileNameBase_m1_iIter+"/"
    MkdirCommand = "mkdir -p "+OutDir_iIter
    os.system(MkdirCommand)
    #directory holding adaptive covariances
    OutDir_adaptive_cov = chain_setting['OutDir']+"/"+date_waterprint+"/"+chain_setting['Label']+"/Stage_"+str(iStage)+"/adaptive_Covs/"
    MkdirCommand = "mkdir -p "+OutDir_adaptive_cov
    os.system(MkdirCommand)

    JobName_iIter = chain_setting['JobName']+"_Stg_"+str(iStage)+"_Itr_"+str(iIteration)

    RunScriptName_iIter = ScriptDir_Submit_iIter+"/RunScript_Iter_"+str(iIteration)+".sh"
    SubmitScriptName_iIter = ScriptDir_Submit_iIter+"/SubmitScript_Iter_"+str(iIteration)+".sh"
    ScriptDirFileName_Error_iIter = ScriptDir_Error_iIter+"/SubmitError_Iter_"+str(iIteration)+".log"
    ScriptDirFileName_Log_iIter = ScriptDir_Log_iIter+"/SubmitLog_Iter_"+str(iIteration)+".log"

    OutputName_iIter_ID = []
    OutputName_iIter_m1_ID = []
    ConfigName_iIter_ID = []
    ConsoleOutputName_iIter_ID = []

    for iExec in range(chain_setting['ExecPerJob']):
        OutputName_iIter_ID.append(OutDir_iIter+"MaCh3_Job_${ID}_Iter_"+str(iIteration)+"_Exec_"+str(iExec)+".root")
        OutputName_iIter_m1_ID.append(OutDir_m1_iIter+"MaCh3_Job_${ID}_Iter_"+str(iIteration-1)+"_Exec_"+str(iExec)+".root")
        ConfigName_iIter_ID.append(ScriptDir_Submit_iIter+"/Config_Job_${ID}_Iter_"+str(iIteration)+"_Exec_"+str(iExec)+".cfg")
        ConsoleOutputName_iIter_ID.append(ScriptDir_Output_iIter+"/ConsoleOutput_Job_${ID}_Iteration_"+str(iIteration)+"_Exec_"+str(iExec)+".log")

    output_root_job_exec = []
    atmskdet_adaptive_cov_job_exec = []
    skcalib_adaptive_cov_job_exec = []
    skdetbeam_adaptive_cov_job_exec = []
    config_job_exec = []
    for iJob in range(chain_setting['JobNumber']):
        OutputName_iIter = []
        OutputName_iIter_m1 = []
        ConfigName_iIter = []
        ConsoleOutputName_iIter = []
        atmskdet_adaptiveCovName_iIter = []
        skcalib_adaptiveCovName_iIter = []
        skdetbeam_adaptiveCovName_iIter = []

        for iExec in range(chain_setting['ExecPerJob']):
            OutputName_iIter.append(OutDir_iIter+"MaCh3_Job_"+str(iJob+1)+"_Iter_"+str(iIteration)+"_Exec_"+str(iExec)+".root")
            OutputName_iIter_m1.append(OutDir_m1_iIter+"MaCh3_Job_"+str(iJob+1)+"_Iter_"+str(iIteration-1)+"_Exec_"+str(iExec)+".root")
            ConfigName_iIter.append(ScriptDir_Submit_iIter+"/Config_Job_"+str(iJob+1)+"_Iter_"+str(iIteration)+"_Exec_"+str(iExec)+".cfg")
            ConsoleOutputName_iIter.append(ScriptDir_Output_iIter+"/ConsoleOutput_Job_"+str(iJob+1)+"_Iteration_"+str(iIteration)+"_Exec_"+str(iExec)+".log")
            atmskdet_adaptiveCovName_iIter.append(OutDir_adaptive_cov+"covariance_AtmSKDetSyst_adaptive_Job_"+str(iJob+1)+"_Exec_"+str(iExec)+".root")
            skcalib_adaptiveCovName_iIter.append(OutDir_adaptive_cov+"covariance_SKCalibrationSyst_adaptive_Job_"+str(iJob+1)+"_Exec_"+str(iExec)+".root")
            skdetbeam_adaptiveCovName_iIter.append(OutDir_adaptive_cov+"covariance_SKDetBeamSyst_adaptive_Job_"+str(iJob+1)+"_Exec_"+str(iExec)+".root")
            
        output_root_job_exec.append(OutputName_iIter)
        atmskdet_adaptive_cov_job_exec.append(atmskdet_adaptiveCovName_iIter)
        skcalib_adaptive_cov_job_exec.append(skcalib_adaptiveCovName_iIter)
        skdetbeam_adaptive_cov_job_exec.append(skdetbeam_adaptiveCovName_iIter)
        config_job_exec.append(ConfigName_iIter)

        for iExec in range(chain_setting['ExecPerJob']):
            Temp_ConfigName = WorkDirectory+"/Config_Temp.cfg"
            CopyCommand = "cp "+ConfigName+" "+Temp_ConfigName
            os.system(CopyCommand)

            SedCommand = "sed -i 's|OUTPUTNAME.*|OUTPUTNAME = \""+OutputName_iIter[iExec]+"\"|' "+Temp_ConfigName
            os.system(SedCommand)

            if (StartFromFile):
                SedCommand = "sed -i 's|STARTFROMPOS.*|STARTFROMPOS = true|' "+Temp_ConfigName
            else:
                SedCommand = "sed -i 's|STARTFROMPOS.*|STARTFROMPOS = false|' "+Temp_ConfigName
            os.system(SedCommand)

            if (StartFromFile):
                SedCommand = "sed -i 's|POSFILES.*|POSFILES = \""+OutputName_iIter_m1[iExec]+"\"|' "+Temp_ConfigName
                os.system(SedCommand)

            SedCommand = "sed -i 's|NSTEPS.*|NSTEPS = "+str(chain_setting['Steps'])+"|' "+Temp_ConfigName
            os.system(SedCommand)

            SedCommand = "sed -i 's|ATMCONFIGDIR.*|ATMCONFIGDIR = \""+chain_setting['SampleCfgDir']+"\"|' "+Temp_ConfigName
            os.system(SedCommand)

            SedCommand = "sed -i 's|BEAMCONFIGDIR.*|BEAMCONFIGDIR = \""+chain_setting['SampleCfgDir']+"\"|' "+Temp_ConfigName
            os.system(SedCommand)

            #Adaptive setting
            SedCommand = "sed -i 's|ADAPTIONTHRESHOLDS.*|ADAPTIONTHRESHOLDS = [ "+str(adaptive_setting['lower_adapt'])+", "+str(adaptive_setting['upper_adapt'])+" ]|' "+Temp_ConfigName
            os.system(SedCommand)

            SedCommand = "sed -i 's|ADAPTIVEUPDATEINTERVAL.*|ADAPTIVEUPDATEINTERVAL = "+str(adaptive_setting['update_interval'])+"|' "+Temp_ConfigName
            os.system(SedCommand)
             
            SedCommand = "sed -i 's|ADAPTIVEFILENAMEATMSKDET.*|ADAPTIVEFILENAMEATMSKDET = \""+atmskdet_adaptiveCovName_iIter[iExec]+"\"|' "+Temp_ConfigName
            os.system(SedCommand)
            SedCommand = "sed -i 's|ADAPTIVEFILENAMESKCALIB.*|ADAPTIVEFILENAMESKCALIB = \""+skcalib_adaptiveCovName_iIter[iExec]+"\"|' "+Temp_ConfigName
            os.system(SedCommand)
            SedCommand = "sed -i 's|ADAPTIVEFILENAMESKDETBEAM.*|ADAPTIVEFILENAMESKDETBEAM = \""+skdetbeam_adaptiveCovName_iIter[iExec]+"\"|' "+Temp_ConfigName
            os.system(SedCommand)

            #rename
            mvCommand = "mv "+Temp_ConfigName+" "+ConfigName_iIter[iExec]
            print(mvCommand)
            os.system(mvCommand)
    #RUN SCRIPT
    Temp_RunScriptName = WorkDirectory+"/RunScript_Temp.sh"
    CopyCommand = "cp "+chain_setting['RunScriptTemp']+" "+Temp_RunScriptName
    os.system(CopyCommand)
    replaceText(Temp_RunScriptName,"MACH3INSTALL",chain_setting['MaCh3Install'])
    replaceText(Temp_RunScriptName,"NTHREADS",str(int(chain_setting['ThreadPerJob']/chain_setting['ExecPerJob'])))

    for iExec in range(chain_setting['ExecPerJob']):
        iGPU = int(iExec/(chain_setting['ExecPerJob']/chain_setting['GPUPerJob']))
        SedCommand = "sed -i -e '/^#INSERTJOB/abackground_pid_"+str(iExec)+"=$!' "+Temp_RunScriptName
        os.system(SedCommand)
        SedCommand = "sed -i -e '/^#INSERTJOB/a CUDA_VISIBLE_DEVICES=\""+str(iGPU)+"\" "+chain_setting['Exec']+" "+ConfigName_iIter_ID[iExec]+" > "+ConsoleOutputName_iIter_ID[iExec]+" &' "+Temp_RunScriptName
        os.system(SedCommand)

    for iExec in range(chain_setting['ExecPerJob']):
        SedCommand = "sed -i -e '/^#INSERTWAIT/await ${background_pid_"+str(iExec)+"} ' "+Temp_RunScriptName
        os.system(SedCommand)

    mvCommand = "mv "+Temp_RunScriptName+" "+RunScriptName_iIter
    os.system(mvCommand)
    #SUBMIT SCRIPT
    Temp_SubmitScriptName = WorkDirectory+"/SubmitScript_Temp.sh"
    CopyCommand = "cp "+chain_setting['SumbitScriptTemp']+" "+Temp_SubmitScriptName
    os.system(CopyCommand)
    
    cpu_per_task = chain_setting['ThreadPerJob']
    gpu_per_job = chain_setting['GPUPerJob']
    memory = 30*int(chain_setting['ExecPerJob'])

    replaceText(Temp_SubmitScriptName,"JOBNAME",JobName_iIter)
    replaceText(Temp_SubmitScriptName,"EXECUTABLENAME",RunScriptName_iIter)
    replaceText(Temp_SubmitScriptName,"SUBMITSCRIPTOUTPUT",ScriptDirFileName_Log_iIter)
    replaceText(Temp_SubmitScriptName,"ERRORFILE",ScriptDirFileName_Error_iIter)
    replaceText(Temp_SubmitScriptName,"ARRAY","1-"+str(chain_setting['JobNumber']))
    replaceText(Temp_SubmitScriptName,"cpus-per-task=8","cpus-per-task="+str(cpu_per_task))
    replaceText(Temp_SubmitScriptName,"gres=gpu:v100l:1","gres=gpu:v100l:"+str(gpu_per_job))
    replaceText(Temp_SubmitScriptName,"mem=30G","mem="+str(memory)+"G")

    mvCommand = "mv "+Temp_SubmitScriptName+" "+SubmitScriptName_iIter
    os.system(mvCommand)

    return {'output':output_root_job_exec, 
            'atmskdet_cov':atmskdet_adaptive_cov_job_exec,
            'skcalib_cov':skcalib_adaptive_cov_job_exec,
            'skdetbeam_cov':skdetbeam_adaptive_cov_job_exec,
            'config': config_job_exec,
            'script_dir':ScriptDir_Submit_iIter,
            'submit_script':SubmitScriptName_iIter,
            'run_script':RunScriptName_iIter}


def adaption_stage_1(chain_setting):
    print("STAGE 1: ")
    nIterations = 1
    adaptive_setting = {'lower_adapt':1000, 'upper_adapt':100000,'update_interval':100}
    
    files_iter = []
    for iIter in range(nIterations):
        files = prepare_files(chain_setting, adaptive_setting, 1, iIter)
        files_iter.append(files)
    return files_iter

def adaption_stage_2(chain_setting, stage_1_files):
    print("STAGE 2: ")
    nIterations = 2
    #adaptive_setting = {'lower_adapt':110000, 'upper_adapt':300000,'update_interval':1000}
    adaptive_setting = {'lower_adapt':10000, 'upper_adapt':200000,'update_interval':1000}
    
    files_iter = []
    for iIter in range(nIterations):
        print("\n")
        files = prepare_files(chain_setting, adaptive_setting, 2, iIter)
        files_iter.append(files)
        
        configs = files['config']
        if iIter == 0:
            print("Reset adaption...")
            #configs = files['config']
            pre_outputs = stage_1_files['output']
            for ijob,job in enumerate(configs):
                for iexe, exe in enumerate(job):
                    SedCommand = "sed -i 's|STARTFROMPOS.*|STARTFROMPOS = true|' "+configs[ijob][iexe]
                    os.system(SedCommand)
                    SedCommand = "sed -i 's|POSFILES.*|POSFILES = \""+pre_outputs[ijob][iexe]+"\"|' "+configs[ijob][iexe]
                    os.system(SedCommand)
                    SedCommand = "sed -i 's|RESETADAPTION.*|RESETADAPTION = true|' "+configs[ijob][iexe]
                    os.system(SedCommand)
            print("Copy adapted Cov matrix from previous job...")
            pre_atmskdet_cov = stage_1_files['atmskdet_cov']
            pre_skcalib_cov = stage_1_files['skcalib_cov'] 
            pre_skdetbeam_cov = stage_1_files['skdetbeam_cov']
            atmskdet_cov = files['atmskdet_cov']
            skcalib_cov = files['skcalib_cov']
            skdetbeam_cov = files['skdetbeam_cov']
            for ijob,job in enumerate(configs):
                for iexe, exe in enumerate(job):
                    SedCommand = "sed -i -e '/^#COPYCOVMATRIX/acp "+pre_atmskdet_cov[ijob][iexe]+" "+atmskdet_cov[ijob][iexe]+"' "+files['run_script']
                    os.system(SedCommand)
                    SedCommand = "sed -i -e '/^#COPYCOVMATRIX/acp "+pre_skcalib_cov[ijob][iexe]+" "+skcalib_cov[ijob][iexe]+"' "+files['run_script']
                    os.system(SedCommand)
                    SedCommand = "sed -i -e '/^#COPYCOVMATRIX/acp "+pre_skdetbeam_cov[ijob][iexe]+" "+skdetbeam_cov[ijob][iexe]+"' "+files['run_script']
                    os.system(SedCommand)

        #if iIter >= 0:
        #    print("Read previous proposal matrix...")
        #    script_dir = files['script_dir']
        #    atmskdet_cov = stage_1_files['atmskdet_cov']
        #    skcalib_cov = stage_1_files['skcalib_cov'] 
        #    skdetbeam_cov = stage_1_files['skdetbeam_cov']

        #    atmskdet_syst_cfg_temp = chain_setting['MaCh3Install']+"/configs/AtmosphericConfigs/AtmSKDetSyst.cfg"
        #    skcalib_syst_cfg_temp = chain_setting['MaCh3Install']+"/configs/AtmosphericConfigs/SKCalibrationSyst.cfg"
        #    skdetbeam_syst_cfg_temp = chain_setting['MaCh3Install']+"/configs/AtmosphericConfigs/SKDetBeamSyst.cfg"
 
        #    for ijob,job in enumerate(configs):
        #        atmskdet_syst_config = []
        #        skcalib_syst_config = []
        #        skdetbeam_syst_config = []

        #        for iexe, exe in enumerate(job):
        #            atmskdet_syst_config.append(script_dir+"/AtmSKDetSyst_adaptive_Job_"+str(ijob+1)+"_Exec_"+str(iexe)+".cfg") 
        #            skcalib_syst_config.append(script_dir+"/SKCalibrationSyst_adaptive_Job_"+str(ijob+1)+"_Exec_"+str(iexe)+".cfg")
        #            skdetbeam_syst_config.append(script_dir+"/SKDetBeamSyst_adaptive_Job_"+str(ijob+1)+"_Exec_"+str(iexe)+".cfg")

        #        for iexe, exe in enumerate(job):
        #            CopyCommand = "cp "+atmskdet_syst_cfg_temp+" "+atmskdet_syst_config[iexe]
        #            print(CopyCommand)
        #            os.system(CopyCommand)
                     
        #            SedCommand = "sed -i 's|AtmSKDetCovFileName.*|AtmSKDetCovFileName = \""+atmskdet_cov[ijob][iexe]+"\"|' "+atmskdet_syst_config[iexe]
        #            os.system(SedCommand)
        #            SedCommand = "sed -i 's|AtmSKDetCovMatrixName.*|AtmSKDetCovMatrixName = \"AtmSKDet_covariance\"|' "+atmskdet_syst_config[iexe]
        #            os.system(SedCommand)
        #            SedCommand = "sed -i 's|AtmSKDetStepSizeFile.*|AtmSKDetStepSizeFile = \"configs/AtmosphericConfigs/AtmSKDetSyst_StepSizes_Identity.cfg\"|' "+atmskdet_syst_config[iexe]
        #            os.system(SedCommand)

        #            SedCommand = "sed -i 's|ATMSKDETSYSTCFG.*|ATMSKDETSYSTCFG = \""+atmskdet_syst_config[iexe]+"\"|' "+configs[ijob][iexe]
        #            os.system(SedCommand)
        #            #skcalib
        #            CopyCommand = "cp "+skcalib_syst_cfg_temp+" "+skcalib_syst_config[iexe]
        #            print(CopyCommand)
        #            os.system(CopyCommand)
                    
        #            SedCommand = "sed -i 's|SKCalibrationCovFileName.*|SKCalibrationCovFileName = \""+skcalib_cov[ijob][iexe]+"\"|' "+skcalib_syst_config[iexe]
        #            os.system(SedCommand)
        #            SedCommand = "sed -i 's|SKCalibrationCovMatrixName.*|SKCalibrationCovMatrixName = \"skcalib_covariance\"|' "+skcalib_syst_config[iexe]
        #            os.system(SedCommand)
                    
        #            SedCommand = "sed -i 's|SKCALIBSYSTCFG.*|SKCALIBSYSTCFG = \""+skcalib_syst_config[iexe]+"\"|' "+configs[ijob][iexe]
        #            os.system(SedCommand)
        #            #skdetbeam
        #            CopyCommand = "cp "+skdetbeam_syst_cfg_temp+" "+skdetbeam_syst_config[iexe]
        #            print(CopyCommand)
        #            os.system(CopyCommand)
                    
        #            SedCommand = "sed -i 's|SKDetBeamCovFileName.*|SKDetBeamCovFileName = \""+skdetbeam_cov[ijob][iexe]+"\"|' "+skdetbeam_syst_config[iexe]
        #            os.system(SedCommand)
        #            SedCommand = "sed -i 's|SKDetBeamCovMatrixName.*|SKDetBeamCovMatrixName = \"skdetbeam_covariance\"|' "+skdetbeam_syst_config[iexe]
        #            os.system(SedCommand)
                    
        #            SedCommand = "sed -i 's|SKDETBEAMSYSTCFG.*|SKDETBEAMSYSTCFG = \""+skdetbeam_syst_config[iexe]+"\"|' "+configs[ijob][iexe]
        #            os.system(SedCommand)
                    
    return files_iter

def adaption_stage_3(chain_setting, stage_2_files):
    print("STAGE 3: ")
    nIterations = 3
    #adaptive_setting = {'lower_adapt':110000, 'upper_adapt':110001,'update_interval':1000}
    adaptive_setting = {'lower_adapt':10000, 'upper_adapt':10001,'update_interval':1000}
    
    files_iter = []
    for iIter in range(nIterations):
        files = prepare_files(chain_setting, adaptive_setting, 3, iIter)
        files_iter.append(files)

        configs = files['config']
        #pre_atmskdet_adaptiveCov = stage_2_files['atmskdet_cov']
        #pre_skcalib_adaptiveCov = stage_2_files['skcalib_cov']
        #pre_skdetbeam_adaptiveCov = stage_2_files['skdetbeam_cov']
        #
        #for ijob, job in enumerate(configs):
        #    for iexe, exe in enumerate(job):
        #        SedCommand = "sed -i 's|ADAPTIVEFILENAMEATMSKDET.*|ADAPTIVEFILENAMEATMSKDET = \""+pre_atmskdet_adaptiveCov[ijob][iexe]+"\"|' "+configs[ijob][iexe]
        #        os.system(SedCommand)
        #        SedCommand = "sed -i 's|ADAPTIVEFILENAMESKCALIB.*|ADAPTIVEFILENAMESKCALIB = \""+pre_skcalib_adaptiveCov[ijob][iexe]+"\"|' "+configs[ijob][iexe]
        #        os.system(SedCommand)
        #        SedCommand = "sed -i 's|ADAPTIVEFILENAMESKDETBEAM.*|ADAPTIVEFILENAMESKDETBEAM = \""+pre_skdetbeam_adaptiveCov[ijob][iexe]+"\"|' "+configs[ijob][iexe]
        #        os.system(SedCommand)

        if iIter == 0:
            pre_outputs = stage_2_files['output']
            for ijob, job in enumerate(configs):
                for iexe, exe in enumerate(job):
                    SedCommand = "sed -i 's|STARTFROMPOS.*|STARTFROMPOS = true|' "+configs[ijob][iexe]
                    os.system(SedCommand)
                    SedCommand = "sed -i 's|POSFILES.*|POSFILES = \""+pre_outputs[ijob][iexe]+"\"|' "+configs[ijob][iexe]
                    os.system(SedCommand)

            print("Copy adapted Cov matrix from previous job...")
            pre_atmskdet_cov = stage_2_files['atmskdet_cov']
            pre_skcalib_cov = stage_2_files['skcalib_cov'] 
            pre_skdetbeam_cov = stage_2_files['skdetbeam_cov']
            atmskdet_cov = files['atmskdet_cov']
            skcalib_cov = files['skcalib_cov']
            skdetbeam_cov = files['skdetbeam_cov']
            for ijob,job in enumerate(configs):
                for iexe, exe in enumerate(job):
                    SedCommand = "sed -i -e '/^#COPYCOVMATRIX/acp "+pre_atmskdet_cov[ijob][iexe]+" "+atmskdet_cov[ijob][iexe]+"' "+files['run_script']
                    os.system(SedCommand)
                    SedCommand = "sed -i -e '/^#COPYCOVMATRIX/acp "+pre_skcalib_cov[ijob][iexe]+" "+skcalib_cov[ijob][iexe]+"' "+files['run_script']
                    os.system(SedCommand)
                    SedCommand = "sed -i -e '/^#COPYCOVMATRIX/acp "+pre_skdetbeam_cov[ijob][iexe]+" "+skdetbeam_cov[ijob][iexe]+"' "+files['run_script']
                    os.system(SedCommand)

    return files_iter

def submit_to_queue(stage_1,stage_2,stage_3):
    try:
        SubmitJobs = int(input("Submit jobs to queue? [1 for yes, 0 for no]: "))
    except:
        print("Invalid answer")
        quit()

    if (SubmitJobs):
        ID = -1
        total_iter = stage_1+stage_2+stage_3
        for isub, sub in enumerate(total_iter):
            print(sub['submit_script'])
            SubmitCommand = "sbatch "
            if (ID!=-1):
                SubmitCommand += " --dependency=afterany:"+str(ID)+" "
            
            SubmitCommand += sub['submit_script']
            Return = subprocess.getoutput(SubmitCommand)
            ID = (Return.split(" "))[-1]
            print(SubmitCommand)
            #ID = ID+1
        
######################################################################################################
Version = sys.version_info[0]
if (Version != 3):
   print("Python3 required")
   quit()
#read in general settings for chains
general_setting = read_job_setting()

#set Adaption Stage 1
stage1_files = adaption_stage_1(general_setting)
#set Adaption Stage 2
stage2_files = adaption_stage_2(general_setting,stage1_files[-1])
#set Adaption Stage 3
stage3_files = adaption_stage_3(general_setting,stage2_files[-1])
#submit job scripts to queues
submit_to_queue(stage1_files,stage2_files,stage3_files)
