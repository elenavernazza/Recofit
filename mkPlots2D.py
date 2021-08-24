#!/usr/bin/env python
import os
import sys
import stat
from glob import glob
import ROOT
import numpy as np
import argparse
import shutil as sh
from array import array

def mkdir(path):
    try:
        os.mkdir(path)
    except:
        print("Dir already present")

def convertName(name):
    d = {
        "dphijj" : "#Delta#phi_{jj}",
        "mll" : "m_{ll}",
        "mlll" : "m_{lll}",
        "mjj" : "m_{jj}",
        "met" : "MET",
        "phi_j1" : "#phi_{j1}",
        "phi_j2" : "#phi_{j2}",
        "ptj1" : "p_{T,j1}",
        "ptj2" : "p_{T,j2}",
        "ptl1" : "p_{T,l1}",
        "ptl2" : "p_{T,l2}",
        "ptl3" : "p_{T,l3}",
        "ptl1Z" : "p_{T,l1} Z",
        "ptl2Z" : "p_{T,l2} Z",
        "ptlW" : "p_{T,l} W",
        "ptll" : "p_{T,ll}",
        "detajj": "#Delta#eta_{jj}",
        "etaj1" : "#eta_{j1}",
        "etaj2" : "#eta_{j2}",
        "etal1" : "#eta_{l1}",
        "etal2" : "#eta_{l2}",
        "etal3" : "#eta_{l3}",
        "etal1Z" : "#eta_{l1} Z",
        "etal2Z" : "#eta_{l2} Z",
        "etalW" : "#eta_{l} W",
        "nJet"  : "n_{jet}",
        " ": None
    }

    if name in d.keys():
        if "_" in name:
            name = name.split("_")
            l = [convertName(i) for i in name]
            return ":".join(i for i in l)

        else:
            return d[name]
            
    else:
        return name

def getAreaWithinCL (histo, threshold):

    area = 0.
    for i  in range(1, histo.GetNbinsX() + 1):
        for j  in range(1, histo.GetNbinsY () + 1):
            if histo.GetBinContent (i,j) < threshold: area+=1

    area *= histo.GetXaxis ().GetBinWidth (1) * histo.GetYaxis ().GetBinWidth (1)

    return area

if __name__ == "__main__":

    ROOT.gROOT.SetBatch(1)

    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser()
    parser.add_argument('--i',          dest='f_input',    help='Input folder',     required=True)
    parser.add_argument('--o',          dest='f_output',   help='Output folder',    required=False, default='scanPlot2D')
    parser.add_argument('--ignore',     dest='ignore',     help='comma sep list of ignore variables', required = False, default="")
    parser.add_argument('--maxNLL',     dest='maxNLL',     help='NLL maximum sets precision of computation of intervals', required = False, default="100")
    parser.add_argument('--prefix',     dest='prefix',     help='prefix of the subfolders, prefix_op', required = False, default="Datacard2D")
    parser.add_argument('--saveLL',     dest='saveLL',     help='Save likelihood plots or not, default is true', required = False, default=True, action = "store_false")
    parser.add_argument('--graphLimit', dest='graphLimit', help='comma separated list of final graph y axis limits, default is 2,2', required = False, default="10,10")
    parser.add_argument('--drawText',   dest='drawText',   help='Plot text of best variables in final plot', required = False, default=True, action = "store_false")

    args = parser.parse_args()
    ignore = args.ignore.split(",")

    ops = []
    limits = {}
    best = {}
    # cuts = []
    # for cuts_ in glob(args.f_input + "/*/*/"):
    #     cuts.append(cuts_.split("/")[-2])
    cuts = ["SR_3l"]

    for cut in cuts:
        best[cut] = {}
        best[cut]["ops"] = []
        best[cut]["best_var"]= []
        best[cut]["one_s"] = []
        best[cut]["two_s"] = []
        best[cut]["best"] = []

    __stops = array('d', [0.00, 1.00])
    __red = array('d', [1.0, 0.0])
    __green  = array('d', [1.0, 0.0])
    __blue  = array('d', [1.0, 1.00])

    ROOT.TColor.CreateGradientColorTable(2, __stops,__red, __green, __blue, 50, 0.8)
    ROOT.gStyle.SetNumberContours(200)

    outputFolder = os.getcwd() + "/" + args.f_output
    mkdir(outputFolder)

    final_plot_y_min = -float(args.graphLimit.split(",")[0])
    final_plot_y_max = float(args.graphLimit.split(",")[1])

    for dir in glob(args.f_input + "/*/"):
        process = dir.split("/")[-2]
        couples = process.split(args.prefix + "_")[1]
        ops.append(couples)
        op = couples.split("_")
        print(process)

        print("\n\n")
        print("{} {}".format(op[0],op[1]))
        print("\n\n")

        # mkdir(outputFolder + "/" + couples)

        for cut_ in cuts:
            print(cut_)

            one_inf = []
            one_sup = []
            two_inf = []
            two_sup = []
            best_x = []
            best_y = []
            var = []
            x_counter = 0.5

            # mkdir(outputFolder + "/" + couples + "/" + cut_)
            # if args.saveLL: mkdir(outputFolder + "/" + couples + "/" + cut_ + "/LLscans")            
            
            for j,vars_ in enumerate(glob(dir + "/" + cut_ + "/*/")) :

                var_ = vars_.split("/")[-2]
                print(var_)
                if var in ignore:
                    print("@ @ @ Skipping {} @ @ @".format(var_))
                    continue

                ls_file = vars_ + "higgsCombineTest.MultiDimFit.mH125.root"
                #if not os.path.isfile(ls_file): sys.exit("[ERROR] no fit for {}".format(vars_))
                if not os.path.isfile(ls_file): continue

                f = ROOT.TFile(ls_file)
                t = f.Get("limit")

                print("@Retrieving likelihood...")
                to_draw = ROOT.TString("{}:{}:2*deltaNLL".format("k_" + op[0], "k_" + op[1]))
                n = t.Draw(to_draw.Data(), "deltaNLL<{} && deltaNLL>{}".format(float(args.maxNLL), -30), "l")

                if n <= 1:
                    print("[ATTENTION] no likelihood for {}".format(vars_))
                    print(np.ndarray((n), 'd', t.GetV2())[1:]) #removing first element (0,0)
                    continue

                x = np.ndarray((n), 'd', t.GetV1())
                y = np.ndarray((n), 'd', t.GetV2())
                z_ = np.ndarray((n), 'd', t.GetV3())

                z = np.array([i-min(z_) for i in z_]) #shifting likelihood toward 0
                graphScan = ROOT.TGraph2D(n,x,y,z)

                graphScan.GetZaxis().SetTitle("-2 #Delta LL")
                graphScan.GetXaxis().SetTitle(op[0])
                graphScan.GetYaxis().SetTitle(op[1])
                graphScan.SetTitle(var_)
                graphScan.SetLineColor(ROOT.kRed)
                graphScan.SetLineWidth(2)
                graphScan.SetNpx(100)
                graphScan.SetNpy(100)                

                graphScan.GetZaxis().SetRangeUser(0, float(args.maxNLL))
                graphScan.GetHistogram().GetZaxis().SetRangeUser(0, float(args.maxNLL))

                for i in range(graphScan.GetHistogram().GetSize()):
                    if (graphScan.GetHistogram().GetBinContent(i+1) == 0):
                        graphScan.GetHistogram().SetBinContent(i+1, 100)

                hist = graphScan.GetHistogram().Clone("arb_hist")
                hist.SetContour(2, np.array([2.30, 5.99]))
                hist.Draw("CONT Z LIST")
                ROOT.gPad.Update()

                for i, event in enumerate(t):
                    if i == 0:
                        x_min = getattr(event, "k_" + op[0])
                        y_min = getattr(event, "k_" + op[1])

                    else: break

                if args.saveLL:
                    
                    cs = ROOT.TCanvas("c_" + op[0] + "_" + op[1] + "_" + var_, "cs", 900, 800)
                    margins = 0.11

                    ROOT.gPad.SetRightMargin(0.15)
                    ROOT.gPad.SetLeftMargin(margins)
                    ROOT.gPad.SetBottomMargin(margins)
                    ROOT.gPad.SetTopMargin(margins)
                    ROOT.gPad.SetFrameLineWidth(3)

                    exp = ROOT.TGraph()
                    exp.SetPoint(0, x_min, y_min)
                    exp.SetMarkerStyle(34)
                    exp.SetMarkerSize(2)
                    exp.SetMarkerColor(ROOT.kRed)

                    conts = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
                    # The following will be cont_graphs =  [ROOT.TList, ROOT.TList]
                    # wheree 2 is defined by the two levels (2.3, 5.99). Each TList
                    # contains a bunch of TGraphs corresponding to the isoleveel curves (maybe more than 1)
                    cont_graphs = [conts.At(i) for i in range(len(conts))]

                    colors = [ROOT.kRed, ROOT.kRed]
                    linestyle = [1, 7]

                    graphScan.GetHistogram().Draw("colz")
                    graphScan.GetHistogram().GetXaxis().SetTitle(op[0])
                    graphScan.GetHistogram().GetXaxis().SetTitleSize(0.04)
                    graphScan.GetHistogram().GetYaxis().SetTitle(op[1])
                    graphScan.GetHistogram().GetYaxis().SetTitleSize(0.04)
                    graphScan.GetHistogram().GetYaxis().SetTitleOffset(1)
                    graphScan.GetHistogram().GetZaxis().SetTitle("-2#Delta LL")
                    graphScan.GetHistogram().GetZaxis().SetTitleSize(0.04)
                    graphScan.GetHistogram().SetTitle("")
                    cs.Modified()
                    cs.Update()

                    leg = ROOT.TLegend(0.82, 0.85, 0.67, 0.7)
                    leg.AddEntry(exp, "Best Fit", "P")

                    for i, item_ in enumerate(cont_graphs):
                        # item_ here is a TList
                        l = list(item_)
                        for item in l:
                            try:
                                item.SetLineColor(colors[i])
                                item.GetXaxis().SetTitle(op[0])
                                item.GetYaxis().SetTitle(op[1])
                                item.SetLineStyle(linestyle[i])
                                item.SetLineWidth(2)
                                item.Draw("L same")
                            except:
                                continue
                        #only add one legend entry, arbitrary
                        if len(l) > 0:
                            leg.AddEntry(l[0], "#pm {}#sigma".format(i+1), "L")

                    exp.Draw("P same")
                    leg.Draw()

                    cs.Draw()
                    cs.Print(outputFolder + "/" + op[0] + "_" + op[1] + "_" + cut_ + "_" + var_ + "_LLscan.png")
                    cs.Print(outputFolder + "/" + op[0] + "_" + op[1] + "_" + cut_ + "_" + var_ + "_LLscan.pdf")


                print("68 for {}".format(vars_))
                x_sixeight = getAreaWithinCL(hist, 2.3)
                print("95 for {}".format(vars_))
                x_nintyfive = getAreaWithinCL(hist, 5.99)

                
                one_inf.append(abs(x_sixeight/2))
                one_sup.append(abs(x_sixeight/2))
                two_inf.append(abs(x_nintyfive/2))
                two_sup.append(abs(x_nintyfive/2))
                best_x.append(x_counter)
                best_y.append(0)
                var.append(vars_.split("/")[-2])

                x_counter += 1

                f.Close()


            c = ROOT.TCanvas("c", "c", 800, 600)
            c.SetGrid()
            leg = ROOT.TLegend(0.15, 0.85, 0.4, 0.7)

            margins = 0.11
            ROOT.gPad.SetRightMargin(margins)
            ROOT.gPad.SetLeftMargin(margins)
            ROOT.gPad.SetBottomMargin(margins)
            ROOT.gPad.SetTopMargin(margins)
            ROOT.gPad.SetFrameLineWidth(3)

            if not len(best_x)  > 0 or not len(best_y) > 0: continue

            g1 = ROOT.TGraphAsymmErrors(len(best_x), array('d', best_x), array('d', best_y), array('d', [0.16]*len(best_x)), array('d', [0.16]*len(best_x)),  array('d', one_inf), array('d', one_sup))
        
            g1.SetMinimum(-10)
            g1.SetMaximum(15)
            g1.SetFillColor(ROOT.kOrange)
            g1.SetLineColor(ROOT.kOrange)
            g1.SetLineWidth(0)
            g1.SetMarkerStyle(24)
            g1.SetMarkerColor(ROOT.kBlue+1)
            g1.SetMarkerSize(2)
            g1.GetYaxis().SetRangeUser(-10,10)


            g2 = ROOT.TGraphAsymmErrors(len(best_x), array('d', best_x), array('d', best_y), array('d', [0.16]*len(best_x)), array('d', [0.16]*len(best_x)),  array('d', two_inf), array('d', two_sup))
            g2.SetFillColor(ROOT.kGreen+1)
            g2.SetLineWidth(0)
            g2.SetMarkerStyle(24)
            g2.SetMarkerColor(ROOT.kBlue+1)
            g2.SetMarkerSize(2)
            g2.GetYaxis().SetRangeUser(-15,15)

            leg.AddEntry(g1, "#pm 1#sigma Expected", "F")
            leg.AddEntry(g2, "#pm 2#sigma Expected", "F")
            leg.AddEntry(g1, "Best Fit", "P")
            leg.SetHeader("Operator: " + op[0] + " " + op[1])
            leg.SetBorderSize(2)

            h = ROOT.TH1F("h", "h", len(best_x)+2, -1, len(best_x)+1)
            h.SetFillColor(0)
            h.SetCanExtend(ROOT.TH1.kAllAxes)
            h.SetStats(0)
    
            for idx in  range(-1, h.GetNbinsX()):
                if idx == 0: h.GetXaxis().SetBinLabel(idx + 1, "")
                if idx < len(var)+1 and idx > 0: h.GetXaxis().SetBinLabel(idx + 1, convertName(var[idx - 1]))
                else: h.GetXaxis().SetBinLabel(idx + 1, "")
            h.GetYaxis().SetTitle(op[0] + " " + op[1] + " 2D Area")

            ROOT.gStyle.SetLabelSize(.05, "XY")

            max_ = max(two_sup)
            min_ = -max(two_inf)

            best_v = 1e9
            best_index = 0
            count = 0
            #best variable in 68% range + 95% range / 2
            # for k,z,l,m in zip(one_inf, one_sup, two_inf, two_sup):
            #     if (k+z+l+m)/2 < best_v:
            #         best_v = (k+z+l+m)/2
            #         best_index = count
            #     count += 1
            for k in one_inf:
                if k < best_v:
                    best_v = k
                    best_index = count
                count += 1

            best[cut_]["ops"].append(op[0] + " " + op[1])
            best[cut_]["best_var"].append(var[best_index])
            best[cut_]["one_s"].append([one_inf[best_index], one_sup[best_index]])
            best[cut_]["two_s"].append([two_inf[best_index], two_sup[best_index]])
            best[cut_]["best"].append([0,0])
            print(best[cut_]["one_s"])
            #print("@[INFO] Best Var: {} for cut: {}".format(var[best_index], cut_))

            h.LabelsDeflate("X")
            h.LabelsDeflate("Y")
            h.LabelsOption("v")

            ROOT.gStyle.SetLabelSize(.04, "XY")

            h.GetYaxis().SetRangeUser(1.5*min_,2*max_)
            g1.SetHistogram(h)


            ROOT.gStyle.SetOptStat(0)
            

            h.Draw("AXIS")
            c.SetGrid()
            ROOT.gPad.RedrawAxis("g")
            g2.Draw("2 same")
            g1.Draw("2 same")
            g1.Draw("P same")

            c.SetTicks()
            leg.Draw()

            c.Draw()
            c.Print(outputFolder + "/" + op[0] + "_" + op[1] + "_" + cut_ + "_sensitivity.png")
            c.Print(outputFolder + "/" + op[0] + "_" + op[1] + "_" + cut_ + "_sensitivity.pdf")
    
    #open txt file to store results
    f_out = open(outputFolder + "/results.txt", "w")
    for cut_ in best.keys():

        c = ROOT.TCanvas("c", "c", 800, 600)
        c.SetGrid()
        leg = ROOT.TLegend(0.15, 0.85, 0.4, 0.7)

        margins = 0.11
        ROOT.gPad.SetRightMargin(margins)
        ROOT.gPad.SetLeftMargin(margins)
        ROOT.gPad.SetBottomMargin(margins)
        ROOT.gPad.SetTopMargin(margins)
        ROOT.gPad.SetFrameLineWidth(3)

        vars_ = best[cut_]["best_var"]
        ops = best[cut_]["ops"]
        one_s = best[cut_]["one_s"]
        two_s = best[cut_]["two_s"]
        best_fit = best[cut_]["best"]

        print(two_s, one_s, ops, best_fit, vars_)

        two_s, one_s, ops, best_fit, vars_ = zip(*sorted(zip(two_s, one_s, ops, best_fit, vars_)))

         #saving results to txt
        print("[CUR RESULTS] {}".format(cut_))
        f_out.write("[CUT RESULTS] {}\n".format(cut_))
        f_out.write("op \t best var \t 1 sigma \t 2 sigma\n")
        for v, o, os, ts in zip(vars_, ops, one_s, two_s):
            print("{} \t  {} \t [{:.3f},{:.3f}] \t [{:.3f},{:.3f}]".format(o,v,-os[0],os[1],-ts[0],ts[1]))
            f_out.write("{} \t  {} \t [{:.3f},{:.3f}] \t [{:.3f},{:.3f}]\n".format(o,v,-os[0],os[1],-ts[0],ts[1]))
        
        f_out.write("\n\n")     

        xs = []
        ys = []
        one_inf = []
        one_sup = []
        two_inf = []
        two_sup = []

        base = 0.5
        for j in range(len(best_fit)):
            xs.append(j+base)
            ys.append(0)

        for m,n in zip(one_s, two_s):
            one_inf.append(m[0])
            one_sup.append(m[1])
            two_inf.append(n[0])
            two_sup.append(n[1])


        max_ = max(two_sup)
        min_ = -max(two_inf)  

        
        g1 = ROOT.TGraphAsymmErrors(len(xs), array('d', xs), array('d', ys), array('d', [0.16]*len(xs)), array('d', [0.16]*len(xs)),  array('d', one_inf), array('d', one_sup))
    
        g1.SetMinimum(-10)
        g1.SetMaximum(15)
        g1.SetFillColor(ROOT.kOrange)
        g1.SetLineColor(ROOT.kOrange)
        g1.SetLineWidth(0)
        g1.SetMarkerStyle(24)
        g1.SetMarkerColor(ROOT.kBlue+1)
        g1.SetMarkerSize(1)
        g1.GetYaxis().SetRangeUser(-10,10)


        g2 = ROOT.TGraphAsymmErrors(len(xs), array('d', xs), array('d', ys), array('d', [0.16]*len(xs)), array('d', [0.16]*len(xs)),  array('d', two_inf), array('d', two_sup))
        g2.SetFillColor(ROOT.kGreen+1)
        g2.SetLineWidth(0)
        g2.SetMarkerStyle(24)
        g2.SetMarkerColor(ROOT.kBlue+1)
        g2.SetMarkerSize(1)
        g2.GetYaxis().SetRangeUser(-15,15)

        leg.AddEntry(g1, "#pm 1#sigma Expected", "F")
        leg.AddEntry(g2, "#pm 2#sigma Expected", "F")
        leg.AddEntry(g1, "Best Fit", "P")
        leg.SetBorderSize(2)

        h = ROOT.TH1F("h_{}".format(cut_), "h_".format(cut_), len(xs)+2, -1, len(xs)+1)
        h.SetFillColor(0)
        h.SetCanExtend(ROOT.TH1.kAllAxes)
        h.SetStats(0)
        for idx in  range(h.GetNbinsX()):
            if idx == 0: h.GetXaxis().SetBinLabel(idx + 1, "")
            if idx < len(ops)+1 and idx > 0: h.GetXaxis().SetBinLabel(idx + 1, ops[idx-1])
            else: h.GetXaxis().SetBinLabel(idx + 1, "")
        h.GetYaxis().SetTitle("Best Confidence Interval")

        h.LabelsDeflate("X")
        h.LabelsDeflate("Y")
        h.LabelsOption("v")

        ROOT.gStyle.SetLabelSize(.05, "XY")

        h.GetYaxis().SetRangeUser(final_plot_y_min,final_plot_y_max)
        g1.SetHistogram(h)


        ROOT.gStyle.SetOptStat(0)
        

        h.Draw("AXIS")
        c.SetGrid()
        ROOT.gPad.RedrawAxis("g")
        g2.Draw("2 same")
        g1.Draw("2 same")
        g1.Draw("P same")

        c.SetTicks()
        leg.Draw()

        if args.drawText:
            count = 0
            for x,y in zip(xs, two_sup):
                y_ = y + 0.5
                #do not plot if the text pass the plot boundaries
                if y_ > final_plot_y_max - 0.1: continue
                var = vars_[count]
                count += 1
                latex = ROOT.TLatex()
                latex.SetTextSize(0.025)
                latex.SetTextAlign(12)
                latex.DrawLatex(x-0.14 - 0.02*len(convertName(var)),y_,"{}".format(convertName(var)))


        c.Draw()
        c.Print(outputFolder + "/" + "{}.pdf".format(cut_))
        c.Print(outputFolder + "/" + "{}.png".format(cut_))
    f_out.close()