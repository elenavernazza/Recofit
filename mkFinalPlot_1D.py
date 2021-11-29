import os
import sys
import ROOT
import argparse
from glob import glob
from copy import deepcopy
import plotter.PlotManager as PM
import numpy as np
from array import array

# RECO EW
color1 = ROOT.TColor.GetFreeColorIndex()
col1 = ROOT.TColor(color1, 48./255., 178./255., 26./255.)
color2 = ROOT.TColor.GetFreeColorIndex()
col2 = ROOT.TColor(color2, 178./255., 236./255., 93./255.)

color0 = ROOT.kGreen+4

# # RECO EW+QCD
# color1 = ROOT.TColor.GetFreeColorIndex()
# col1 = ROOT.TColor(color1, 255./255., 104./255., 31./255.)
# color2 = ROOT.TColor.GetFreeColorIndex()
# col2 = ROOT.TColor(color2, 248./255., 184./255., 120./255.)

# color0 = ROOT.kRed+2

# color1 = ROOT.kOrange
# color2 = ROOT.kGreen+1

# color1 = ROOT.kPink
# color2 = ROOT.kCyan+1

def convertName(name):
    d = {
        "deltaetaWZ" : "#Delta#eta_{WZ}", 
        "deltaphiWZ" : "#Delta#phi_{WZ}", 
        "Philanes" : "#Phi_{planes}",
        "ThetalW" : "#Theta_{lW}",
        "ThetalZ" : "#Theta_{lZ}", 
        "ThetaWZ" : "#Theta_{WZ}",
        "Zlep1" : "Z_{lep1}", 
        "Zlep2" : "Z_{lep2}",
        "dphijj" : "#Delta#phi_{jj}",
        "mZ" : "m_{Z}",
        "mWZ" : "m_{WZ}",
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
        "ptZ" : "p_{T,Z}",
        "ptlll" : "p_{T,3l}",
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
    return d[name]

def mkdir(path):
    try:
        os.mkdir(path)
    except:
        print("Dir already present")

if __name__ == "__main__":

    ROOT.gROOT.SetBatch(1)

    parser = argparse.ArgumentParser(description='Command line parser for model testing')
    parser.add_argument('--baseFolder',     dest='baseFolder',     help='Base folder', required = True)
    parser.add_argument('--graphLimits',     dest='graphLimits',     help='comma separated list of final graph y axis limits, default is 10,10', required = False, default="10,10")
    parser.add_argument('--drawText',     dest='drawText',     help='Plot text of best variables in final plot', required = False, default=True, action = "store_false")

    args = parser.parse_args()

    r1 = float(args.graphLimits.split(",")[0])
    final_plot_y_min = -float(args.graphLimits.split(",")[0])
    final_plot_y_max = float(args.graphLimits.split(",")[1])

    outputFolder = os.getcwd() + "/" + args.baseFolder

    f_in = open(outputFolder + "/results.txt", "r")

    best = {}
    mod = []
    #mod = ["SR_2e_mu","SR_2mu_e","SR_3e","SR_3l","SR_3mu"]
    mod = ["SR_3l"]

    cpm = PM.CombinePlotManager()
    cpm.generateAllBoxes()

    for models in mod:
        best[models] = {}
        best[models]["ops"] = []
        best[models]["best_var"]= []
        best[models]["one_s"] = []
        best[models]["two_s"] = []
        best[models]["best"] = []

    max_ = 0

    for lines in f_in.readlines():
        if "[CUT RESULTS]" in lines:
            model = (lines.split("[CUT RESULTS] ")[1]).split("\n")[0]
        elif "c" in lines:
            scale = 0
            parts = lines.split(" 	 ")

            if "[[" in parts[3] :
                pa = parts[3].split(",")
                p3_inf_1 = float(pa[0].split("[[")[1])
                p3_sup_1 = float(pa[1].split("]")[0])
                p3_inf_2 = float(pa[2].split("[")[1])
                p3_sup_2 = float(pa[3].split("]]")[0])
                if all(abs(l) < r1 for l in [p3_inf_1,p3_sup_1,p3_inf_2,p3_sup_2]): 
                    best[model]["two_s"].append([[p3_inf_1, p3_sup_1],[p3_inf_2, p3_sup_2]])
                    best[model]["ops"].append(parts[0])
                else: 
                    best[model]["two_s"].append([[0.1*p3_inf_1, 0.1*p3_sup_1],[0.1*p3_inf_2, 0.1*p3_sup_2]])
                    best[model]["ops"].append("0.1*{}".format(parts[0]))
                    scale = 1
            else :
                p3_inf = float(parts[3].split(",")[0].split("[")[1])
                p3_sup = float(parts[3].split(",")[1].split("]")[0])
                if all(abs(l) < r1 for l in [p3_inf,p3_sup]):
                    best[model]["two_s"].append([p3_inf, p3_sup])
                    best[model]["ops"].append(parts[0])
                else:
                    best[model]["two_s"].append([0.1*p3_inf, 0.1*p3_sup])
                    best[model]["ops"].append("0.1*{}".format(parts[0]))
                    scale = 1
            
            if "[[" in parts[2] :
                pb = parts[2].split(",")
                p2_inf_1 = float(pb[0].split("[[")[1])
                p2_sup_1 = float(pb[1].split("]")[0])
                p2_inf_2 = float(pb[2].split("[")[1])
                p2_sup_2 = float(pb[3].split("]]")[0])
                if scale == 0 :
                    best[model]["one_s"].append([[p2_inf_1, p2_sup_1],[p2_inf_2, p2_sup_2]])
                elif scale == 1 :
                    best[model]["one_s"].append([[0.1*p2_inf_1, 0.1*p2_sup_1],[0.1*p2_inf_2, 0.1*p2_sup_2]])
            else :
                p2_inf = float(parts[2].split(",")[0].split("[")[1])
                p2_sup = float(parts[2].split(",")[1].split("]")[0])
                if scale == 0 :
                    best[model]["one_s"].append([p2_inf, p2_sup])
                elif scale == 1 :
                    best[model]["one_s"].append([0.1*p2_inf, 0.1*p2_sup])
            
            best[model]["best_var"].append(parts[1].split(" ")[1])
            best[model]["best"].append([0,0])

    for model in best.keys():

        c = ROOT.TCanvas("c", "c", 800, 600)
        c.SetGrid()
        leg = ROOT.TLegend(0.15, 0.85, 0.4, 0.7)

        margins = 0.11
        ROOT.gPad.SetRightMargin(margins)
        ROOT.gPad.SetLeftMargin(margins)
        ROOT.gPad.SetBottomMargin(margins+0.08)
        ROOT.gPad.SetTopMargin(margins)
        ROOT.gPad.SetFrameLineWidth(3)

        vars_ = best[model]["best_var"]
        ops = best[model]["ops"]
        one_s = best[model]["one_s"]
        two_s = best[model]["two_s"]
        best_fit = best[model]["best"]

        two_s, one_s, ops, best_fit, vars_ = zip(*(zip(two_s, one_s, ops, best_fit, vars_)))

        xs = []
        ys = []

        base = 0.5
        for j in range(len(best_fit)):
            xs.append(j+base)
            ys.append(0)

        g1 = ROOT.TGraphAsymmErrors()
        g11 = ROOT.TGraphAsymmErrors()
        g2 = ROOT.TGraphAsymmErrors()
        g21 = ROOT.TGraphAsymmErrors()
        k = 0
        l = 0
        for j in range(len(xs)) :
            ex = 0.16
            if type(one_s[j][0]) == float :
                g1.SetPoint(j, xs[j], ys[j])
                g1.SetPointError(j, ex, ex, abs(one_s[j][0]), abs(one_s[j][1]))
            else :
                if abs(one_s[j][0][0]) < abs(one_s[j][1][0]) :
                    first = 0
                    second = 1
                else :
                    first = 1
                    second = 0
                g1.SetPoint(j, xs[j], ys[j])
                g1.SetPointError(j, ex, ex, abs(one_s[j][first][0]), abs(one_s[j][first][1]))
                c1 = (one_s[j][second][1] + one_s[j][second][0])/2
                g11.SetPoint(k, xs[j], c1)
                g11.SetPointError(k, ex, ex, abs(one_s[j][second][0]-c1), abs(one_s[j][second][1]-c1))
                k = k + 1

            if type(two_s[j][0]) == float :
                g2.SetPoint(j, xs[j], ys[j])
                g2.SetPointError(j, ex, ex, abs(two_s[j][0]), abs(two_s[j][1]))
            else :
                print(two_s[j])
                if abs(two_s[j][0][0]) < abs(two_s[j][1][0]) :
                    first = 0
                    second = 1
                else :
                    first = 1
                    second = 0
                g2.SetPoint(j, xs[j], ys[j])
                g2.SetPointError(j, ex, ex, abs(two_s[j][first][0]), abs(two_s[j][first][1]))
                c2 = (two_s[j][second][1] + two_s[j][second][0])/2
                g21.SetPoint(l, xs[j], c2)
                g21.SetPointError(l, ex, ex, abs(two_s[j][second][0]-c2), abs(two_s[j][second][1]-c2))
                l = l + 1

        g1.SetMinimum(-10)
        g1.SetMaximum(15)
        g1.SetFillColor(color1)
        g1.SetLineColor(color1)
        g1.SetLineWidth(0)
        g1.SetMarkerStyle(24)
        g1.SetMarkerColor(color0)
        g1.SetMarkerSize(1)
        g1.GetYaxis().SetRangeUser(-10,10)

        g11.SetMinimum(-10)
        g11.SetMaximum(15)
        g11.SetFillColor(color1)
        g11.SetLineColor(color1)
        g11.SetLineWidth(0)

        g2.SetFillColor(color2)
        g2.SetLineWidth(0)
        g2.SetMarkerStyle(24)
        g2.SetMarkerColor(color0)
        g2.SetMarkerSize(1)
        g2.GetYaxis().SetRangeUser(-15,15)

        g21.SetMinimum(-10)
        g21.SetMaximum(15)
        g21.SetFillColor(color2)
        g21.SetLineColor(color2)
        g21.SetLineWidth(0)

        leg.AddEntry(g1, "#pm 1#sigma Expected", "F")
        leg.AddEntry(g2, "#pm 2#sigma Expected", "F")
        leg.AddEntry(g1, "Best Fit", "P")
        leg.SetBorderSize(2)

        h = ROOT.TH1F("h_{}".format(model), "h_".format(model), len(xs)+2, -1, len(xs)+1)
        h.SetFillColor(0)
        h.SetCanExtend(ROOT.TH1.kAllAxes)
        h.SetStats(0)
        for idx in  range(h.GetNbinsX()):
            if idx == 0: h.GetXaxis().SetBinLabel(idx + 1, "")
            if idx < len(ops)+1 and idx > 0: h.GetXaxis().SetBinLabel(idx + 1, ops[idx-1])
            else: h.GetXaxis().SetBinLabel(idx + 1, "")
            h.GetXaxis().SetLabelSize(0.05)
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

        g21.Draw("2 same")
        g11.Draw("2 same")

        c.SetTicks()
        leg.Draw()

        for item in cpm.optionals:
            item.Draw("same")

        if args.drawText:
            count = 0
            for x,t in zip(xs,two_s):
                if type(t[1]) == float:
                    y_ = t[1] + 0.7
                else:
                    y_ = max(float(t[1][1]),float(t[0][1])) + 0.7
                #do not plot if the text pass the plot boundaries
                if y_ > final_plot_y_max - 0.1: continue
                var = vars_[count]
                count += 1
                latex = ROOT.TLatex()
                latex.SetTextSize(0.025)
                latex.SetTextAlign(12)
                latex.DrawLatex(x - 0.02*len(convertName(var)),y_,"{}".format(convertName(var)))

        # if args.drawText:
        #     count = 0
        #     for x,t in zip(xs,two_s):
        #         if type(t[0]) == float:
        #             y_ = t[0] - 0.3
        #         else:
        #             y_ = min(float(t[1][0]),float(t[0][0])) - 0.3
        #         #do not plot if the text pass the plot boundaries
        #         if y_ > final_plot_y_max - 0.1: continue
        #         var = vars_[count]
        #         count += 1
        #         latex = ROOT.TLatex()
        #         latex.SetTextSize(0.025)
        #         latex.SetTextAlign(12)
        #         latex.DrawLatex(x-0.14 - 0.02*len(convertName(var)),y_,"{}".format(convertName(var)))


#        c.Draw()
        c.Print(outputFolder + "/{}_final.png".format(model))
        c.Print(outputFolder + "/{}_final.pdf".format(model))

    f_in.close()
  
