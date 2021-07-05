#!/usr/bin/env python
import os
import sys
import stat
from glob import glob
import ROOT
import numpy as np
import argparse
import shutil as sh

# in order to know where the second minima are
# opr = {
#     'cHl3' : [-100,100],
#     'cHl1' : [-100,100],
#     'cHq3' : [-100,100],
#     'cHq1' : [-100,100],
#     'cll1' : [-100,100],
#     'cHDD' : [-100,100],
#     'cHWB' : [-100,100],
#     'cHW'  : [-100,100],
#     'cqq11': [-30,30],
#     'cqq1' : [-30,30],
#     'cqq31': [-20,20],
#     'cqq3' : [-20,20],
#     'cW'   : [-30,30],
# }

opr = {
    'cHl3' : [-20,20],
    'cHl1' : [-100,100],
    'cHq3' : [-20,20],
    'cHq1' : [-30,30],
    'cll1' : [-50,50],
    'cHDD' : [-60,60],
    'cHWB' : [-30,30],
    'cHW'  : [-80,80],
    'cqq11': [-5,5],
    'cqq1' : [-5,5],
    'cqq31': [-5,5],
    'cqq3' : [-5,5],
    'cW'   : [-10,10],
}

def mkdir(path):
    try:
        os.mkdir(path)
    except:
        print("Dir already present")

def makeActivations(outdir, args):

    prefix = args.prefix

    file_name = outdir + "/runt.py"
    f = open(file_name, 'w')

    f.write("#!/usr/bin/env python\n\n")
    f.write("#-----------------------------------\n")
    f.write("#     Automatically generated       # \n")
    f.write("#        by mkDatacard.py           # \n")
    f.write("#-----------------------------------\n")
    f.write("\n\n\n")

    f.write('from glob import glob\n')
    f.write('import os\n\n')

    f.write('if __name__ == "__main__":\n')
    f.write('   base_dir = os.getcwd()\n')
    f.write('   for dir in glob(base_dir + "/*/"):\n')
    f.write('      process = dir.split("/")[-2]\n')
    f.write('      op = process.split("' + prefix + '_")[1]\n')
    f.write('      for cut_ in glob(dir + "/*/"):\n')
    f.write('         cut = cut_.split("/")[-2]\n')
    f.write('         for var_ in glob(cut_ + "/*/"):\n')
    f.write('            var = var_.split("/")[-2]\n')
    f.write('            print("[INFO] Running for op: {}, cut: {}, var: {}".format(op, cut, var))\n')
    f.write('            os.chdir(cut_ + "/" + var)\n')
    to_write = "text2workspace.py  datacard.txt -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative -o combined.root --X-allow-no-signal --PO eftOperators={}"
    f.write('            os.system("' + to_write + '".format(op))\n')

    f.close()
    #convert to executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)

def makeCondor(outdir, args):

    prefix = args.prefix
    npoints = args.np

    file_name = outdir + "/runc.py"
    f = open(file_name, 'w')

    f.write("#!/usr/bin/env python\n\n")
    f.write("#-----------------------------------\n")
    f.write("#     Automatically generated       # \n")
    f.write("#        by mkDatacard.py           # \n")
    f.write("#-----------------------------------\n")
    f.write("\n\n\n")

    f.write('from glob import glob\n')
    f.write('import os\n\n')

    f.write('opr = {}\n\n'.format(opr))
    f.write('if __name__ == "__main__":\n')
    f.write('   npoints = {}\n'.format(npoints))
    f.write('   base_dir = os.getcwd()\n')
    f.write('   for dir in glob(base_dir + "/*/"):\n')
    f.write('      process = dir.split("/")[-2]\n')
    f.write('      op = process.split("' + prefix + '_")[1]\n')
    f.write('      for cut_ in glob(dir + "/*/"):\n')
    f.write('         cut = cut_.split("/")[-2]\n')
    f.write('         for var_ in glob(cut_ + "/*/"):\n')
    f.write('            var = var_.split("/")[-2]\n')
    f.write('            print("[INFO] Running for op: {}, cut: {}, var: {}".format(op, cut, var))\n')
    f.write('            os.chdir(cut_ + "/" + var)\n')
    to_write = "combine -M MultiDimFit combined.root --algo=grid --points {} -m 125 -t -1 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --redefineSignalPOIs k_{} --freezeParameters r --setParameters r=1 --setParameterRanges k_{}={},{} --verbose -1"
    f.write('            os.system("' + to_write + '".format(npoints, op, op, opr[op][0], opr[op][1]))\n')

    f.close()
    #convert to executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)

def makeSubmit(outdir):

    npoints = args.np

    file_name = outdir + "/submit.sh"
    f = open(file_name, 'w')

    f.write("#!/bin/sh\n\n")
    f.write("#-----------------------------------\n")
    f.write("#     Automatically generated       # \n")
    f.write("#        by mkDatacard.py           # \n")
    f.write("#-----------------------------------\n")
    f.write("\n\n\n")

    f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    f.write('cd $1\n')
    f.write('eval `scram run -sh`\n')
    f.write('cd -\n')
    f.write('cp -r $1 ./\n')
    f.write('text2workspace.py  $1/datacard.txt  -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative -o combined.root --X-allow-no-signal --PO eftOperators=$3\n')
    f.write('#-----------------------------------\n')
    f.write('combine -M MultiDimFit combined.root --algo=grid --points $2 -m 125 -t -1 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --redefineSignalPOIs k_$3 --freezeParameters r --setParameters r=1 --setParameterRanges k_$3=$4,$5 --verbose -1\n')
    f.write('cp combined.root $1\n')
    f.write('cp higgsCombineTest.MultiDimFit.mH125.root $1\n')

    f.close()
    #convert to executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)

    file_name_1 = outdir + "/submit.sub"
    f1 = open(file_name_1, 'w')

    f1.write('Universe    = vanilla\n')
    f1.write('Executable  = submit.sh\n')
    f1.write('arguments   = $(dir) {} $(op1) $(min_op1) $(max_op1)\n'.format(npoints))
    f1.write('output      = $(dir)/submit.out\n')
    f1.write('error       = $(dir)/submit.err\n')
    f1.write('log         = $(dir)/submit.log\n')
    f1.write('queue dir,op1,min_op1,max_op1 from list.txt\n')
    f1.write('+JobFlavour = "espresso"\n')

    f1.close()
    #convert to executable
    st = os.stat(file_name_1)
    os.chmod(file_name_1, st.st_mode | stat.S_IEXEC)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--i',      dest='f_input',   help='Input folder',             required=True)
    parser.add_argument('--o',      dest='f_output',  help='Output folder',            required=False, default='Datacard1D')
    parser.add_argument('--op',     dest='op',        help='Operator',                 required=False)
    parser.add_argument('--ignore', dest='ignore',    help='List of ignore variables', required=False, default=',')
    parser.add_argument('--onlyvar',dest='onlyvar',   help='One variable',             required=False)
    parser.add_argument('--range',  dest='range_op',  help='Range of the scan',        required=False)
    parser.add_argument('--cuts',   dest='cuts',      help='Cuts',                     required=True)
    parser.add_argument('--p',      dest='prefix',    help='Prefix',                   required=False, default='Datacard1D')
    parser.add_argument('--np',     dest='np',        help='npoints for fit',          required=False, default='200')

    args = parser.parse_args()
    ignore = args.ignore.split(",")
    print("Ignore variables: {}".format(ignore))

    f_in = args.f_input
    f_ou = args.f_output
    if args.op:
        op = args.op.split(",")
    else:
        op = opr.keys()

    print(op)
    
    if args.range_op:
        for op_ in opr.keys():
            opr[op_] = [-float(args.range_op.split(",")[0]), float(args.range_op.split(",")[1])]

    cut = []
    if args.cuts:
        cut = args.cuts.split(",")
    else:
        cut_ = glob(f_in + "/*/")
        for c in cut_:
            cut.append(c.split("/")[-2])
    
    base_folder = os.getcwd()

    inputFolder = os.getcwd() + "/" + f_in
    outputFolder = os.getcwd() + "/" + f_ou
    mkdir(outputFolder)
    # makeActivations(outputFolder, args)
    # makeCondor(outputFolder, args)
    makeSubmit(outputFolder)
    l = open(outputFolder + "/list.txt", 'w')

    print(". . . @ @ @ Retrieving folders @ @ @ . . .")

    all_sub_paths = []

    for op_ in op:

        print("\n\n")
        print(op_)
        print("\n\n")

        mkdir(outputFolder + "/" + args.prefix + "_" + op_)
        for cut_ in cut:
            mkdir(outputFolder + "/" + args.prefix + "_" + op_ + "/" + cut_)
            if args.onlyvar:
                var = glob(inputFolder + "/" + cut_ + "/" + args.onlyvar)
            else:
                var = glob(inputFolder + "/" + cut_ + "/*")
            for var_ in var:
                var_ = var_.split(cut_ + "/")[1]
                if var_ not in ignore:
                    dst = outputFolder + "/" + args.prefix + "_" + op_ + "/" + cut_
                    dst_var = outputFolder + "/" + args.prefix + "_" + op_ + "/" + cut_ + "/" + var_
                    print("[INFO] Running: {}".format(var_,))
                    src = inputFolder + "/" + cut_ + "/" + var_
                    print(src)
                    os.system("cp -rf " + src + " " + dst)

                    l.write('{} {} {} {}\n'.format(dst_var, op_, opr[op_][0], opr[op_][1]))

    l.close()

    print(". . . @ @ @ Done @ @ @ . . .")
