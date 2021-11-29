import os
import sys
import ROOT
import argparse
from glob import glob
from copy import deepcopy
import plotter.PlotManager as PM
import numpy as np
from array import array

# # RECO EW
color1_e = ROOT.TColor.GetFreeColorIndex()
col1 = ROOT.TColor(color1_e, 48./255., 178./255., 26./255.)
color2_e = ROOT.TColor.GetFreeColorIndex()
col2 = ROOT.TColor(color2_e, 178./255., 236./255., 93./255.)
color0_e = ROOT.kGreen+4

# RECO EW+QCD
color1_q = ROOT.TColor.GetFreeColorIndex()
col3 = ROOT.TColor(color1_q, 255./255., 104./255., 31./255.)
color2_q = ROOT.TColor.GetFreeColorIndex()
col4 = ROOT.TColor(color2_q, 248./255., 184./255., 120./255.)

color0_q = ROOT.kRed+2

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
    parser.add_argument('--ewk',     dest='ewk',     help='Base folder EWK', required = True)
    parser.add_argument('--qcd',     dest='qcd',     help='Base folder QCD', required = True)
    parser.add_argument('--file',    dest='file',    help='Name of results.txt file', required = True)
    parser.add_argument('--cut',     dest='cut',     help='Cut',             required = True)
    parser.add_argument('--add',     dest='add',     help='Add name',        required = False)
    parser.add_argument('--graphLimits',     dest='graphLimits',     help='comma separated list of final graph y axis limits, default is 12.5,12.5', required = False, default="15,15")
    parser.add_argument('--drawText',     dest='drawText',     help='Plot text of best_ewk variables in final plot', required = False, default=True, action = "store_false")

    args = parser.parse_args()

    r1 = float(args.graphLimits.split(",")[0])

    final_plot_y_min = -float(args.graphLimits.split(",")[0])
    final_plot_y_max = float(args.graphLimits.split(",")[1])

    outputFolder_ewk = os.getcwd() + "/" + args.ewk
    outputFolder_qcd = os.getcwd() + "/" + args.qcd
    results = args.file

    f_in_ewk = open(outputFolder_ewk + "/" + results, "r")

    best = {}
    models = []

    models = args.cut.split(",")

    for model in models:
        best[model] = {}
        best[model]["ops"] = []
        best[model]["best_var_ewk"] = []
        best[model]["best_var_qcd"] = []
        best[model]["one_s_ewk"] = []
        best[model]["one_s_qcd"] = []
        best[model]["two_s_ewk"] = []
        best[model]["two_s_qcd"] = []
        best[model]["best_ewk"] = []
        best[model]["best_qcd"] = []

    for lines in f_in_ewk.readlines():
        if "[CUT RESULTS]" in lines:
            model_ewk = lines.split("[CUT RESULTS] ")[1].split("\n")[0]
        elif "c" in lines:
            scale = 0
            if model_ewk not in models:
                continue
            else:
                p = lines.split(" 	 ")                
                f_in_qcd = open(outputFolder_qcd + "/" + results, "r")
                for lines_qcd in f_in_qcd.readlines():
                    if "[CUT RESULTS]" in lines_qcd:
                        model_qcd = lines_qcd.split("[CUT RESULTS] ")[1].split("\n")[0]
                    elif ("{} ".format(p[0])) in lines_qcd:
                        if model_ewk == model_qcd:
                            p_qcd = lines_qcd.split(" 	 ")
                            best[model_ewk]["best_var_ewk"].append(p[1].split(" ")[1])
                            best[model_ewk]["best_var_qcd"].append(p_qcd[1].split(" ")[1])
                            if "[[" in p[3] :
                                pa_ewk = p[3].split(",")
                                p3_inf_1 = float(pa_ewk[0].split("[[")[1])
                                p3_sup_1 = float(pa_ewk[1].split("]")[0])
                                p3_inf_2 = float(pa_ewk[2].split("[")[1])
                                p3_sup_2 = float(pa_ewk[3].split("]]")[0])
                                if all(abs(l) < r1 for l in [p3_inf_1,p3_sup_1,p3_inf_2,p3_sup_2]): 
                                    best[model_ewk]["two_s_ewk"].append([[p3_inf_1, p3_sup_1],[p3_inf_2, p3_sup_2]])
                                    best[model_ewk]["ops"].append(p[0])
                                else: 
                                    best[model_ewk]["two_s_ewk"].append([[0.1*p3_inf_1, 0.1*p3_sup_1],[0.1*p3_inf_2, 0.1*p3_sup_2]])
                                    best[model_ewk]["ops"].append("0.1*{}".format(p[0]))
                                    scale = 1
                            else : 
                                p3_inf = float(p[3].split(",")[0].split("[")[1])
                                p3_sup = float(p[3].split(",")[1].split("]")[0])
                                if all(abs(l) < r1 for l in [p3_inf,p3_sup]):
                                    best[model_ewk]["two_s_ewk"].append([p3_inf, p3_sup])
                                    best[model_ewk]["ops"].append(p[0])
                                else:
                                    best[model_ewk]["two_s_ewk"].append([0.1*p3_inf, 0.1*p3_sup])
                                    best[model_ewk]["ops"].append("0.1*{}".format(p[0]))
                                    scale = 1

                            if "[[" in p_qcd[3] :
                                pa_qcd = p_qcd[3].split(",")
                                p3_inf_1 = float(pa_qcd[0].split("[[")[1])
                                p3_sup_1 = float(pa_qcd[1].split("]")[0])
                                p3_inf_2 = float(pa_qcd[2].split("[")[1])
                                p3_sup_2 = float(pa_qcd[3].split("]]")[0])
                                if scale == 0 : 
                                    best[model_ewk]["two_s_qcd"].append([[p3_inf_1, p3_sup_1],[p3_inf_2, p3_sup_2]])
                                elif scale == 1: 
                                    best[model_ewk]["two_s_qcd"].append([[0.1*p3_inf_1, 0.1*p3_sup_1],[0.1*p3_inf_2, 0.1*p3_sup_2]])
                            else : 
                                p3_inf = float(p_qcd[3].split(",")[0].split("[")[1])
                                p3_sup = float(p_qcd[3].split(",")[1].split("]")[0])
                                if scale == 0 :
                                    best[model_ewk]["two_s_qcd"].append([p3_inf, p3_sup])
                                else:
                                    best[model_ewk]["two_s_qcd"].append([0.1*p3_inf, 0.1*p3_sup])

                            if "[[" in p[2] :
                                pb_ewk = p[2].split(",")
                                p2_inf_1 = float(pb_ewk[0].split("[[")[1])
                                p2_sup_1 = float(pb_ewk[1].split("]")[0])
                                p2_inf_2 = float(pb_ewk[2].split("[")[1])
                                p2_sup_2 = float(pb_ewk[3].split("]]")[0])
                                if scale == 0 : 
                                    best[model_ewk]["one_s_ewk"].append([[p2_inf_1, p2_sup_1],[p2_inf_2, p2_sup_2]])
                                elif scale == 1 : 
                                    best[model_ewk]["one_s_ewk"].append([[0.1*p2_inf_1, 0.1*p2_sup_1],[0.1*p2_inf_2, 0.1*p2_sup_2]])
                            else : 
                                p2_inf = float(p[2].split(",")[0].split("[")[1])
                                p2_sup = float(p[2].split(",")[1].split("]")[0])
                                if scale == 0 :
                                    best[model_ewk]["one_s_ewk"].append([p2_inf, p2_sup])
                                elif scale == 1 :
                                    best[model_ewk]["one_s_ewk"].append([0.1*p2_inf, 0.1*p2_sup])

                            if "[[" in p_qcd[2] :
                                pb_qcd = p_qcd[2].split(",")
                                p2_inf_1 = float(pb_qcd[0].split("[[")[1])
                                p2_sup_1 = float(pb_qcd[1].split("]")[0])
                                p2_inf_2 = float(pb_qcd[2].split("[")[1])
                                p2_sup_2 = float(pb_qcd[3].split("]]")[0])
                                if scale == 0 : 
                                    best[model_ewk]["one_s_qcd"].append([[p2_inf_1, p2_sup_1],[p2_inf_2, p2_sup_2]])
                                elif scale == 1 : 
                                    best[model_ewk]["one_s_qcd"].append([[0.1*p2_inf_1, 0.1*p2_sup_1],[0.1*p2_inf_2, 0.1*p2_sup_2]])
                            else : 
                                p2_inf = float(p_qcd[2].split(",")[0].split("[")[1])
                                p2_sup = float(p_qcd[2].split(",")[1].split("]")[0])
                                if scale == 0 :
                                    best[model_ewk]["one_s_qcd"].append([p2_inf, p2_sup])
                                elif scale == 1 :
                                    best[model_ewk]["one_s_qcd"].append([0.1*p2_inf, 0.1*p2_sup])                                    
                            best[model_ewk]["best_ewk"].append([0,0])
                            best[model_ewk]["best_qcd"].append([0,0])

    for model in best.keys():

        c = ROOT.TCanvas("c", "c", 800, 600)
        c.SetGrid()
        leg = ROOT.TLegend(0.15, 0.85, 0.4, 0.68)

        margins = 0.11
        ROOT.gPad.SetRightMargin(margins)
        ROOT.gPad.SetLeftMargin(margins)
        ROOT.gPad.SetBottomMargin(margins+0.08)
        ROOT.gPad.SetTopMargin(margins)
        ROOT.gPad.SetFrameLineWidth(3)

        ops = best[model]["ops"]
        vars_e = best[model]["best_var_ewk"]
        one_s_e = best[model]["one_s_ewk"]
        two_s_e = best[model]["two_s_ewk"]
        best_fit_e = best[model]["best_ewk"]
        vars_q = best[model]["best_var_qcd"]
        one_s_q = best[model]["one_s_qcd"]
        two_s_q = best[model]["two_s_qcd"]
        best_fit_q = best[model]["best_qcd"]

        ops, two_s_e, one_s_e, best_fit_e, vars_e, two_s_q, one_s_q, best_fit_q, vars_q = zip(*(zip(ops, two_s_e, one_s_e, best_fit_e, vars_e, two_s_q, one_s_q, best_fit_q, vars_q)))

        for j in range(len(ops)):
            if type(two_s_q[j][1]) == float and type(two_s_e[j][1]) == float:
                ratio = (two_s_q[j][1]-two_s_q[j][0])/(two_s_e[j][1]-two_s_e[j][0])
                print("{} & ${}$ & [{:.2f},{:.2f}] & ${}$ & [{:.2f},{:.2f}] & {:.2f} \\".format(ops[j],vars_q[j],two_s_q[j][0],two_s_q[j][1],vars_e[j],two_s_e[j][0],two_s_e[j][1],ratio))


        xs = []
        ys = []
        xs_qcd = []
        ys_qcd = []        

        base = 0.3
        for j in range(len(best_fit_e)):
            xs.append(j+base)
            ys.append(0)

        base = 0.6
        for j in range(len(best_fit_e)):
            xs_qcd.append(j+base)
            ys_qcd.append(0)

        g1 = ROOT.TGraphAsymmErrors()
        g11 = ROOT.TGraphAsymmErrors()
        g2 = ROOT.TGraphAsymmErrors()
        g21 = ROOT.TGraphAsymmErrors()
        g3 = ROOT.TGraphAsymmErrors()
        g31 = ROOT.TGraphAsymmErrors()
        g4 = ROOT.TGraphAsymmErrors()
        g41 = ROOT.TGraphAsymmErrors()
        k = 0
        l = 0
        k_q = 0
        l_q = 0        

        for j in range(len(xs)) :
            ex = 0.12
            if type(one_s_e[j][0]) == float :
                g1.SetPoint(j, xs[j], ys[j])
                g1.SetPointError(j, ex, ex, abs(one_s_e[j][0]), abs(one_s_e[j][1]))
            else :
                if abs(one_s_e[j][0][0]) < abs(one_s_e[j][1][0]) :
                    first = 0
                    second = 1
                else :
                    first = 1
                    second = 0
                g1.SetPoint(j, xs[j], ys[j])
                g1.SetPointError(j, ex, ex, abs(one_s_e[j][first][0]), abs(one_s_e[j][first][1]))
                c1 = (one_s_e[j][second][1] + one_s_e[j][second][0])/2
                g11.SetPoint(k, xs[j], c1)
                g11.SetPointError(k, ex, ex, abs(one_s_e[j][second][0]-c1), abs(one_s_e[j][second][1]-c1))
                k = k + 1

            if type(two_s_e[j][0]) == float :
                g2.SetPoint(j, xs[j], ys[j])
                g2.SetPointError(j, ex, ex, abs(two_s_e[j][0]), abs(two_s_e[j][1]))
            else :
                if abs(two_s_e[j][0][0]) < abs(two_s_e[j][1][0]) :
                    first = 0
                    second = 1
                else :
                    first = 1
                    second = 0
                g2.SetPoint(j, xs[j], ys[j])
                g2.SetPointError(j, ex, ex, abs(two_s_e[j][first][0]), abs(two_s_e[j][first][1]))
                c2 = (two_s_e[j][second][1] + two_s_e[j][second][0])/2
                g21.SetPoint(l, xs[j], c2)
                g21.SetPointError(l, ex, ex, abs(two_s_e[j][second][0]-c2), abs(two_s_e[j][second][1]-c2))
                l = l + 1

            if type(one_s_q[j][0]) == float :
                g3.SetPoint(j, xs_qcd[j], ys_qcd[j])
                g3.SetPointError(j, ex, ex, abs(one_s_q[j][0]), abs(one_s_q[j][1]))
            else :
                if abs(one_s_q[j][0][0]) < abs(one_s_q[j][1][0]) :
                    first = 0
                    second = 1
                else :
                    first = 1
                    second = 0
                g3.SetPoint(j, xs_qcd[j], ys_qcd[j])
                g3.SetPointError(j, ex, ex, abs(one_s_q[j][first][0]), abs(one_s_q[j][first][1]))
                c1 = (one_s_q[j][second][1] + one_s_q[j][second][0])/2
                g31.SetPoint(k_q, xs_qcd[j], c1)
                g31.SetPointError(k_q, ex, ex, abs(one_s_q[j][second][0]-c1), abs(one_s_q[j][second][1]-c1))
                k_q = k_q + 1

            if type(two_s_q[j][0]) == float :
                g4.SetPoint(j, xs_qcd[j], ys_qcd[j])
                g4.SetPointError(j, ex, ex, abs(two_s_q[j][0]), abs(two_s_q[j][1]))
            else :
                if abs(two_s_q[j][0][0]) < abs(two_s_q[j][1][0]) :
                    first = 0
                    second = 1
                else :
                    first = 1
                    second = 0
                g4.SetPoint(j, xs_qcd[j], ys_qcd[j])
                g4.SetPointError(j, ex, ex, abs(two_s_q[j][first][0]), abs(two_s_q[j][first][1]))
                c2 = (two_s_q[j][second][1] + two_s_q[j][second][0])/2
                g41.SetPoint(l_q, xs_qcd[j], c2)
                g41.SetPointError(l_q, ex, ex, abs(two_s_q[j][second][0]-c2), abs(two_s_q[j][second][1]-c2))
                l_q = l_q + 1


        g1.SetMinimum(-10)
        g1.SetMaximum(15)
        g1.SetFillColor(color1_e)
        g1.SetLineColor(color1_e)
        g1.SetLineWidth(0)
        g1.SetMarkerStyle(24)
        g1.SetMarkerColor(color0_e)
        g1.SetMarkerSize(1)
        g1.GetYaxis().SetRangeUser(-10,10)

        g11.SetMinimum(-10)
        g11.SetMaximum(15)
        g11.SetFillColor(color2_e)
        g11.SetLineColor(color2_e)
        g11.SetLineWidth(0)

        g2.SetFillColor(color2_e)
        g2.SetLineWidth(0)
        g2.SetMarkerStyle(24)
        g2.SetMarkerColor(color0_e)
        g2.SetMarkerSize(1)
        g2.GetYaxis().SetRangeUser(-15,15)

        g21.SetMinimum(-10)
        g21.SetMaximum(15)
        g21.SetFillColor(color2_e)
        g21.SetLineColor(color2_e)
        g21.SetLineWidth(0)

   
        g3.SetMinimum(-10)
        g3.SetMaximum(15)
        g3.SetFillColor(color1_q)
        g3.SetLineColor(color1_q)
        g3.SetLineWidth(0)
        g3.SetMarkerStyle(24)
        g3.SetMarkerColor(color0_q)
        g3.SetMarkerSize(1)
        g3.GetYaxis().SetRangeUser(-10,10)

        g31.SetMinimum(-10)
        g31.SetMaximum(15)
        g31.SetFillColor(color1_q)
        g31.SetLineColor(color1_q)
        g31.SetLineWidth(0)

        g4.SetFillColor(color2_q)
        g4.SetLineWidth(0)
        g4.SetMarkerStyle(24)
        g4.SetMarkerColor(color0_q)
        g4.SetMarkerSize(1)
        g4.GetYaxis().SetRangeUser(-15,15)

        g41.SetMinimum(-10)
        g41.SetMaximum(15)
        g41.SetFillColor(color2_q)
        g41.SetLineColor(color2_q)
        g41.SetLineWidth(0)

        leg.AddEntry(g1, "#pm 1#sigma EWK", "F")
        leg.AddEntry(g2, "#pm 2#sigma EWK", "F")
        leg.AddEntry(g3, "#pm 1#sigma EWK + QCD", "F")
        leg.AddEntry(g4, "#pm 2#sigma EWK + QCD", "F")
        leg.AddEntry(g1, "Best Fit", "P")
        leg.AddEntry(g3, "Best Fit", "P")
        leg.SetBorderSize(2)

        h = ROOT.TH1F("h_{}".format(model), "h_".format(model), len(xs)+2, -1, len(xs)+1)
        h.SetFillColor(0)
        h.SetCanExtend(ROOT.TH1.kAllAxes)
        h.SetStats(0)
        for idx in  range(h.GetNbinsX()):
            if idx == 0: h.GetXaxis().SetBinLabel(idx + 1, "")
            if idx < len(best[model]["ops"])+1 and idx > 0: h.GetXaxis().SetBinLabel(idx + 1, best[model]["ops"][idx-1])
            else: h.GetXaxis().SetBinLabel(idx + 1, "")
            h.GetXaxis().SetLabelSize(.05)
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
        g4.Draw("2 same")
        g3.Draw("2 same")
        g1.Draw("P same")
        g3.Draw("P same")

        g21.Draw("2 same")
        g11.Draw("2 same")
        g41.Draw("2 same")
        g31.Draw("2 same")        

        c.SetTicks()
        leg.Draw()

        cpm = PM.CombinePlotManager()
#        cpm.lumi = str(args.lumi + " fb^{-1}")

        cpm.generateAllBoxes()

        for item in cpm.optionals:
             item.Draw("same")

        if args.drawText:
            for x_e,x_q,y_e,y_q,var_e,var_q in zip(xs, xs_qcd, two_s_e, two_s_q, vars_e, vars_q):
                if type(y_e[1]) == float :
                    y_up = y_e[1] + 1.
                else : 
                    y_up = max(y_e[0][1],y_e[1][1]) + 1.
                if type(y_q[1]) == float :
                    y_do = y_q[0] - 1.
                else :
                    y_do = min(y_q[0][0],y_q[1][0]) - 1.
                #do not plot if the text pass the plot boundaries
                #if y_ > final_plot_y_max - 0.1: continue
                latex = ROOT.TLatex()
                latex.SetTextSize(0.025)
                latex.SetTextAlign(12)
                if y_up < final_plot_y_max :
                    latex.DrawLatex(x_e-0.15 - 0.02*len(convertName(var_e)),y_up,"{}".format(convertName(var_e)))
                if y_do > final_plot_y_min :
                    latex.DrawLatex(x_q+0.005 - 0.02*len(convertName(var_q)),y_do,"{}".format(convertName(var_q)))

        c.Draw()
        if args.add: 
            c.Print(outputFolder_qcd + "/{}_EWK_QCD_{}.png".format(model,args.add))
            c.Print(outputFolder_qcd + "/{}_EWK_QCD_{}.pdf".format(model,args.add))
        else:
            c.Print(outputFolder_qcd + "/{}_EWK_QCD.png".format(model))
            c.Print(outputFolder_qcd + "/{}_EWK_QCD.pdf".format(model))

    f_in_ewk.close()
    f_in_qcd.close()
