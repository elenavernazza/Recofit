#!/usr/bin/env python
import os
import sys
import stat
from glob import glob
import ROOT
import numpy as np
import argparse
import shutil as sh

opr = {
    'cHl3' : [-20,20],
    'cHq3':  [-20,20],
    'cHq1':  [-20,20],
    'cqq11': [-10,10],
    'cqq1' : [-10,10],
    'cqq31': [-10,10],
    'cqq3':  [-10,10],
    'cW':    [-10,10],
}

# BSM
ranges = {
    'cW_cqq1' :     [[-1,1],[-1,1]],
    'cW_cqq11' :    [[-1,1],[-1,1]],
    'cW_cqq3' :     [[-1,1],[-0.5,0.5]],
    'cW_cqq31' :    [[-1,1],[-0.5,0.5]],
    'cqq1_cqq11' :  [[-1.5,1.5],[-1.5,1.5]],
    'cqq1_cqq3' :   [[-1,1],[-0.5,0.5]],
    'cqq11_cqq31' : [[-1,1],[-0.5,0.5]],
    'cqq3_cqq31' :  [[-0.7,0.7],[-0.7,0.7]],
    'cHq3_cW':      [[-3,3],[-1,1]],
    'cHq3_cqq31' :  [[-3,3],[-1,1]],
    'cHq3_cqq3' :   [[-3,3],[-1,1]],
    'cHq3_cqq11' :  [[-3,3],[-1,1]],
    'cHq3_cqq1' :   [[-3,3],[-1,1]],
    'cHq1_cW':      [[-6,6],[-1,1]],
    'cHq1_cqq31' :  [[-6,6],[-0.5,0.5]],
    'cHq1_cqq3' :   [[-6,6],[-0.5,0.5]],
    'cHq1_cqq11' :  [[-6,6],[-1,1]],
    'cHq1_cqq1' :   [[-6,6],[-1,1]],
    'cHq1_cHq3' :   [[-6,6],[-3,3]],
    'cHl3_cW':      [[-30,30],[-1.5,1.5]],
    'cHl3_cqq31' :  [[-30,30],[-1.5,1.5]],
    'cHl3_cqq3' :   [[-30,30],[-1.5,1.5]],
    'cHl3_cqq11' :  [[-30,30],[-2,2]],
    'cHl3_cqq1' :   [[-30,30],[-2,2]],
    'cHl3_cHq3' :   [[-200,200],[-50,50]],
    'cHl3_cHq1' :   [[-200,200],[-200,200]]
}

# # BSM QCD
# ranges = {
#     'cW_cqq1' :     [[-1,1],[-1,1]],
#     'cW_cqq11' :    [[-1,1],[-1,1]],
#     'cW_cqq3' :     [[-1,1],[-0.5,0.5]],
#     'cW_cqq31' :    [[-1,1],[-0.5,0.5]],
#     'cqq1_cqq11' :  [[-1.5,1.5],[-1.5,1.5]],
#     'cqq1_cqq3' :   [[-2.5,2.5],[-1.5,1.5]],
#     'cqq11_cqq31' : [[-3,3],[-1.5,1.5]],
#     'cqq3_cqq31' :  [[-0.5,1.5],[-0.5,1.5]],
#     'cHq3_cW':      [[-2.5,1],[-1,1]],
#     'cHq3_cqq31' :  [[-2.5,1],[-1,1]],
#     'cHq3_cqq3' :   [[-2.5,1],[-1,1]],
#     'cHq3_cqq11' :  [[-2.5,1],[-1,1]],
#     'cHq3_cqq1' :   [[-2.5,1],[-1,1]],
#     'cHq1_cW':      [[-10,10],[-1.5,1]],
#     'cHq1_cqq31' :  [[-8,8],[-1,1]],
#     'cHq1_cqq3' :   [[-8,8],[-1,1]],
#     'cHq1_cqq11' :  [[-9,9],[-1,1]],
#     'cHq1_cqq1' :   [[-9,9],[-1,1]],
#     'cHq1_cHq3' :   [[-10,10],[-10,10]],
#     'cHl3_cW':      [[-20,60],[-15,2]],
#     'cHl3_cqq31' :  [[-5,40],[-3,1]],
#     'cHl3_cqq3' :   [[-5,40],[-3,1]],
#     'cHl3_cqq11' :  [[-8,40],[-10,1]],
#     'cHl3_cqq1' :   [[-8,40],[-10,1]],
#     'cHl3_cHq3' :   [[-10,10],[-10,10]],
#     'cHl3_cHq1' :   [[-10,10],[-10,10]]
# }

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
    f.write('      ops = process.split("' + prefix + '_")[1]\n')
    f.write('      op = ops.split("_")\n')
    f.write('      for cut_ in glob(dir + "/*/"):\n')
    f.write('         cut = cut_.split("/")[-2]\n')
    f.write('         for var_ in glob(cut_ + "/*/"):\n')
    f.write('            var = var_.split("/")[-2]\n')
    f.write('            print("[INFO] Running for op: {}, cut: {}, var: {}".format(op, cut, var))\n')
    f.write('            os.chdir(cut_ + "/" + var)\n')
    to_write = "text2workspace.py  datacard.txt -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative -o combined.root --X-allow-no-signal --PO eftOperators={},{}"
    f.write('            os.system("' + to_write + '".format(op[0],op[1]))\n')

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

    f.write('couples = {}\n\n'.format(couples))
    f.write('if __name__ == "__main__":\n')
    f.write('   npoints = {}\n'.format(npoints))
    f.write('   base_dir = os.getcwd()\n')
    f.write('   for dir in glob(base_dir + "/*/"):\n')
    f.write('      process = dir.split("/")[-2]\n')
    f.write('      ops = process.split("' + prefix + '_")[1]\n')
    f.write('      op = ops.split("_")\n')
    f.write('      for cut_ in glob(dir + "/*/"):\n')
    f.write('         cut = cut_.split("/")[-2]\n')
    f.write('         for var_ in glob(cut_ + "/*/"):\n')
    f.write('            var = var_.split("/")[-2]\n')
    f.write('            print("[INFO] Running for op: {}, cut: {}, var: {}".format(ops, cut, var))\n')
    f.write('            os.chdir(cut_ + "/" + var)\n')
    to_write = "combine -M MultiDimFit combined.root --algo=grid --points {} -m 125 -t -1 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --redefineSignalPOIs k_{},k_{} --freezeParameters r --setParameters r=1 --setParameterRanges k_{}={},{}:k_{}={},{} --verbose -1"
    f.write('            os.system("' + to_write + '".format(npoints, op[0], op[1], op[0], couples[ops][0][0], couples[ops][0][1], op[1], couples[ops][1][0], couples[ops][1][1]))\n')

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
    f.write('text2workspace.py  $1/datacard.txt  -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative -o combined.root --X-allow-no-signal --PO eftOperators=$3,$4\n')
    f.write('#-----------------------------------\n')
    f.write('combine -M MultiDimFit combined.root --algo=grid --points $2 -m 125 -t -1 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --redefineSignalPOIs k_$3,k_$4 --freezeParameters r --setParameters r=1 --setParameterRanges k_$3=$5,$6:k_$4=$7,$8 --verbose -1\n')
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
    f1.write('arguments   = $(dir) {} $(op1) $(op2) $(min_op1) $(max_op1) $(min_op2) $(max_op2)\n'.format(npoints))
    f1.write('output      = $(dir)/submit.out\n')
    f1.write('error       = $(dir)/submit.err\n')
    f1.write('log         = $(dir)/submit.log\n')
    f1.write('queue dir,op1,op2,min_op1,max_op1,min_op2,max_op2 from list.txt\n')
    f1.write('+JobFlavour = "longlunch"\n')

    f1.close()
    #convert to executable
    st = os.stat(file_name_1)
    os.chmod(file_name_1, st.st_mode | stat.S_IEXEC)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--i',      dest='f_input',   help='Input folder',             required=True)
    parser.add_argument('--o',      dest='f_output',  help='Output folder',            required=False, default='Datacard2D')
    parser.add_argument('--op',     dest='op',        help='Operator',                 required=False)
    parser.add_argument('--ignore', dest='ignore',    help='List of ignore variables', required=False, default=',')
    parser.add_argument('--onlyvar',dest='onlyvar',   help='One variable',             required=False)
    parser.add_argument('--range',  dest='range_op',  help='Range of the scan',        required=False)
    parser.add_argument('--cuts',   dest='cuts',      help='Cuts',                     required=False)
    parser.add_argument('--p',      dest='prefix',    help='Prefix',                   required=False, default='Datacard2D')
    parser.add_argument('--np',     dest='np',        help='npoints for fit',          required=False, default='20000')

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

    couples = {}
    c_range = []
    for op0 in op:
        for op1 in op:
            if op1 != op0:
                c = [op0,op1]
                c.sort()
                if "{}_{}".format(c[0],c[1]) not in couples.keys() and "{}_{}".format(c[0],c[1]) not in ["cqq1_cqq31","cqq11_cqq3"]: 
                    c_range.append([opr[c[0]][0],opr[c[0]][1]])
                    c_range.append([opr[c[1]][0],opr[c[1]][1]])
                    # couples["{}_{}".format(c[0],c[1])] = c_range
                    couples["{}_{}".format(c[0],c[1])] = ranges["{}_{}".format(c[0],c[1])]

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
    #makeActivations(outputFolder, args)
    #makeCondor(outputFolder, args)
    makeSubmit(outputFolder)
    l = open(outputFolder + "/list.txt", 'w')

    print(". . . @ @ @ Retrieving folders @ @ @ . . .")

    all_sub_paths = []

    for c_ in couples.keys():

        ops = c_.split("_")
        print("\n\n")
        print(ops[0], ops[1])
        print("\n\n")

        mkdir(outputFolder + "/" + args.prefix + "_" + c_)
        for cut_ in cut:
            print("[INFO] Cut: {}".format(cut_))
            mkdir(outputFolder + "/" + args.prefix + "_" + c_ + "/" + cut_)
            var = []
            if args.onlyvar:
                var = glob(inputFolder + "/" + cut_ + "/" + args.onlyvar)
            else:
                var = glob(inputFolder + "/" + cut_ + "/*")
            for var_ in var:
                var_ = var_.split(cut_ + "/")[1]
                if var_ not in ignore:
                    dst = outputFolder + "/" + args.prefix + "_" + c_ + "/" + cut_
                    dst_var = outputFolder + "/" + args.prefix + "_" + c_ + "/" + cut_ + "/" + var_
                    print("[INFO] Running: {}".format(var_,))
                    src = inputFolder + "/" + cut_ + "/" + var_
                    os.system("cp -rf " + src + " " + dst)

                    # l.write('{} {} {} {} {} {} {}\n'.format(dst_var, ops[0], ops[1], opr[ops[0]][0], opr[ops[0]][1], opr[ops[1]][0], opr[ops[1]][1]))
                    l.write('{} {} {} {} {} {} {}\n'.format(dst_var, ops[0], ops[1], ranges[c_][0][0], ranges[c_][0][1], ranges[c_][1][0], ranges[c_][1][1]))

    l.close()

    print(". . . @ @ @ Done @ @ @ . . .")
