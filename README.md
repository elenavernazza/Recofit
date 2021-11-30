# Recofit

This folder includes scripts that can be used inside Latinos framework for the extraction of Wilson coefficients C.L. ranges at reco level.

# Instructions

Suppose you have your folder inside Plotsconfiguration contaning: aliases.py, configuration.py, cuts.py, plot.py samples.py, structure.py, variables.py. Once you have run 

`mkShapesMulti.py --pycfg=configuration.py --doBatch=1 --batchSplit=Samples,Files --batchQueue=espresso`
`mkShapesMulti.py --pycfg=configuration.py --doHadd=1 --nThreads=10 --batchSplit=Samples,Files --doNotCleanup`

you should have a folder "rootFile_<your_process_name>" which contains all the root files. Then you can create the datacards by running

`mkDatacards.py --pycfg=configuration.py --inputFile=rootFile_<your_process_name>/plots_<your_process_name>.root`

An output folder "datacards_<your_process_name>" will be created, contaning subfolders for all cuts and variables, where a "datacard.txt" file and the shape histograms can be found. 
From this folder we create another one containing the same files just with a different order, using "mkDatacards1D.py" script:

`python ../Recofit/mkDatacards1D.py --i datacards_<your_process_name> --cuts <list_of_SR_cuts> --ignore <list_of_variables_to_ignore>`

A "Datacard1D" folder will be created, inside it a "submit.sub" file can be used to launch the combine fit on condor via

`condor_submit submit.sub`

When all the jobs are finished, the "Datacard1D" folder will contain many "higgsCombineTest.MultiDimFit.mH125.root" and "combined.root" files containing the results of the fit. To plot the resulting 1D likelihood profile we use "mkPlots1D.py" script:

`python ../Recofit/mkPlots1D.py --i Datacard1D --maxNLL 5 --ignore <list_of_variables_to_ignore>`

A "ScanPlot1D" folder containing the ranges of the different Wilson coefficients for all the variables under study will be produced, together with a "results.txt" file with the best intervals.
To plot the intervals you can run:

`python ../Recofit/mkFinalPlot_1D.py --baseFolder scanPlot1D`


The same can be done for the bi-dimensional case.

`python ../Recofit/mkDatacards2D.py --i datacards_<your_process_name> --cuts <list_of_SR_cuts> --ignore <list_of_variables_to_ignore> --op <list_of_operators_studied>`

`python ../Recofit/mkPlots2D.py --i Datacard2D --maxNLL 5`

`python ../Recofit/mkConfig2D.py --target Datacard2D --prefix Datacard2D --model <SR_cut_name> --out <your_process>_<SR_cut>.cfg --process <prefix_of_your_process>`

`python ../Recofit/mkFinalPlot_2D.py --cfg <your_process>_<SR_cut>.cfg --o scanPlot2D_Summary --maxNLL 20 --lumi 59.74`

For the differential distribution plots of the kinematic variables see 

https://github.com/UniMiBAnalyses/PlotsConfigurations/tree/master/Configurations/VBSlllnu

*Important Note*: all the WZ ntuples are inside the hercules storage at this path (<username>@hercules.mib.infn.it):
`/gwteray/users/govoni/ntuple_WZ`
