from glob import glob 
import os 
import argparse 
import ROOT
import sys


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Command line parser for 2D plotting scans')
    parser.add_argument('--target',     dest='target',     help='target folder with best fits', required = True)
    parser.add_argument('--prefix',     dest='prefix',     help='target folder prefix', required = True)
    parser.add_argument('--process',     dest='process',     help='target folder process name', required = True)
    parser.add_argument('--model',     dest='model',     help='target folder model name', required = True)
    parser.add_argument('--out',     dest='out',     help='output name', required = True)
    args = parser.parse_args()

    ops = ['cqq3', 'cqq31', 'cHl3', 'cqq1', 'cqq11', 'cll1', 'cW', 'cHq3', 'cHbox', 'cHq1', 'cHW', 'cHWB', 'cHDD', 'cHl1', 'cll']

    file_ = open(args.out, 'w')

    colors = [ROOT.kAzure+1, ROOT.kGray+2, ROOT.kViolet-4, ROOT.kSpring+9, ROOT.kOrange+10]
    COLORS = colors * 100 #maybe a waste but repeat the colors 

    #operators
    #file_.write("operators = {\n")
    file_.write("from collections import OrderedDict \n\n\n")
    file_.write("operators = OrderedDict()\n\n\n")

    for op in ops:

        #retireve all dir with that op 
        # avoiding to select like cll1 when searching for cll
        l1 = glob(args.target + "/*_" + op )
        l2 =  glob(args.target + "/*_" + op + "_*" )

        l = l1 + l2

        #reverse list order
        l = l[::-1]

        if len(l) == 0: 
            print("[WARNING] missing interferences with op {}... SKIPPING".format(op))
            continue

        #first op
        file_.write("operators['{}'] = OrderedDict()\n".format(op))

        for idx, path in enumerate(l):

            #retrieve second op
            #strip makes a mess so this hardcoded solution
            ops = path.split("/")[-1]
            ops = ops.split(args.prefix + "_")[1]
            #ops  = ops.split(args.process + "_")[1]
            ops = ops.split("_")

            s_op = [i for i in ops if i != op]

            if idx > 4: idx = idx - 5

            #process second op
            file_.write("operators['{}']['{}'] = OrderedDict()\n".format(op, s_op[0]))

            full_p = glob(path + "/" + args.model + "/ptj1/higgs*.root")
            
            if len(full_p) != 1: print("[ERROR] check you input folder, dif not found any file for the following string: {}".format(path + "/" + args.model + "/*/higgs*.root"))

            #fill the dict accordingly with paths and so on, color is standard
            file_.write("operators['{}']['{}']['path'] =  '{}'\n".format(op, s_op[0], full_p[0]))
            file_.write("operators['{}']['{}']['name'] = '{}'\n".format(op, s_op[0], args.process))
            file_.write("operators['{}']['{}']['op'] = '{}'\n".format(op, s_op[0], s_op[0]))
            file_.write("operators['{}']['{}']['xscale'] = 1\n".format(op, s_op[0]))
            file_.write("operators['{}']['{}']['yscale'] = 1\n".format(op, s_op[0]))
            file_.write("operators['{}']['{}']['linecolor'] = {}\n".format(op, s_op[0], COLORS[idx]))
            file_.write("operators['{}']['{}']['linesize'] = 4\n".format(op, s_op[0]))
            file_.write("\n")

            #second op
            #file_.write("      },\n")
            file_.write("\n\n")

        #first op
        #file_.write("   },\n")
        file_.write("\n\n")

    #operators
    #file_.write("}\n")
    file_.write("\n\n")
            


