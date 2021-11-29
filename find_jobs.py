#!/usr/bin/env python
import os
import sys
import stat
from glob import glob
import ROOT
import numpy as np
import argparse
import shutil as sh

if __name__ == "__main__":
    folder = sys.argv[1]
    ls = glob("{}/Datacard*".format(folder))
    #var = ["deltaetaWZ", "deltaphiWZ", "detajj", "dphijj", "etaj1", "etaj2", "etal1", "etal1Z", "etal2", "etal2Z", "etal3", "etalW", "met", "mjj", "mlll", "mWZ", "mZ", "Philanes", "ptj1", "ptj2", "ptl1", "ptl1Z", "ptl2", "ptl2Z", "ptl3", "ptlW", "ptZ", "ptlll", "ThetalW", "ThetalZ", "ThetaWZ", "Zlep1", "Zlep2"]
    var = ["detajj", "dphijj", "etaj1", "etaj2", "mjj", "mWZ", "ptj1", "ptj2"]
    #var = ["ptj1"]
    #model = ["SR_2e_mu", "SR_2mu_e", "SR_3e", "SR_3l", "SR_3mu"]
    model = ["SR_3l"]
    count = 0
    for i in ls:
        for m in model:
            for v in var:
                # op = i.split("Datacard1D_")[1]
                c = glob(i + "/" + m + "/" + v + "/submit.out")
                if len(c) == 0: 
                    print(i + "/" + m + "/" + v)
                    count += 1

    print(count)