import os
import sys
import argparse
import numpy as np 
import itertools
from glob import glob
import stat
import ROOT
from copy import deepcopy
from array import array
import math
from collections import OrderedDict
from operator import itemgetter

def ConvertOptoLatex(op):

    d = {
        'cHDD': 'Q_{HD}',
        'cHbox': 'Q_{H#Box}',
        'cW': 'Q_{W}',
        'cHB': 'Q_{HB}',
        'cHW': 'Q_{HW}',
        'cHWB': 'Q_{HWB}',
        'cll': 'Q_{ll}',
        'cll1': 'Q_{ll}\'',
        'cqq1': 'Q_{qq}^{(1)}',
        'cqq11': 'Q_{qq}^{(1)}\'',
        'cHl1': 'Q_{Hl}^{(1)}',
        'cHl3': 'Q_{Hl}^{(3)}',
        'cHq1': 'Q_{Hq}^{(1)}',
        'cHq3': 'Q_{Hq}^{(3)}',
        'cHe': 'Q_{He}',
        'cHu': 'Q_{Hu}',
        'cHd': 'Q_{Hd}',
        'cqq3': 'Q_{qq}^{(3)}',
        'cqq31': 'Q_{qq}^{(3)}\'',

    }

    return d[op]

def ConvertProc(proc):

    d = {
        "SSWW": "W^{#pm}W^{#pm}+2j",
        "OSWW_OSWWQCD": "W^{#pm}W^{#mp}+2j",
        "OSWW": "W^{#pm}W^{#mp}+2j",
        "OSWWQCD": "W^{#pm}W^{#mp}+2j",
        "WZ_WZQCD": "W^{#pm}Z+2j",
        "WZ": "W^{#pm}Z+2j",
        "WZQCD": "W^{#pm}Z+2j",
        "inWW": "W^{#pm}W^{#mp}+0j",
        "ZV": "ZV+2j",
        "combined": "Combined",
    }

    if proc in d.keys(): return d[proc]
    else: return proc

def RetrieveCont(operators, op, proc, maxNLL):

    file = operators[op][proc]['path']
    op_ = [operators[op][proc]['op'],op]

    f = ROOT.TFile(file)
    t = f.Get("limit")

    for i, event in enumerate(t):
        if i == 0:
            x_min = getattr(event, "k_" + op_[0])
            y_min = getattr(event, "k_" + op_[1])

        else: break

    exp = ROOT.TGraph()
    exp.SetPoint(0, x_min, y_min)
    exp.SetMarkerSize(3)
    exp.SetMarkerStyle(34)
    exp.SetMarkerColor(ROOT.kGray +2)

    to_draw = ROOT.TString("{}:{}:2*deltaNLL".format("k_" + op_[0], "k_" + op_[1]))
    n = t.Draw( to_draw.Data() , "deltaNLL<{} && deltaNLL>{}".format(float(maxNLL),-30), "l")

    x = np.ndarray((n), 'd', t.GetV1())
    y = np.ndarray((n), 'd', t.GetV2())
    z_ = np.ndarray((n), 'd', t.GetV3())

    z = np.array([i-min(z_) for i in z_]) #shifting likelihood toward 0

    graphScan1 = ROOT.TGraph2D(n,x,y,z)
    # graphScan1.SetNpx(100)
    # graphScan1.SetNpy(100)

    graphScan1.GetZaxis().SetRangeUser(0, float(maxNLL))
    graphScan1.GetHistogram().GetZaxis().SetRangeUser(0, float(maxNLL))

    for i in range(graphScan1.GetHistogram().GetSize()):
        if (graphScan1.GetHistogram().GetBinContent(i+1) == 0):
            graphScan1.GetHistogram().SetBinContent(i+1, 100)

    hist1 = graphScan1.GetHistogram().Clone("arb_hist")
    hist1.SetContour(2, np.array([2.30, 5.99]))
    hist1.Draw("CONT Z LIST")
    ROOT.gPad.Update()

    conts1 = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    cont_graphs1 = [deepcopy(list(conts1.At(i))) for i in range(2)]

    gs = deepcopy(graphScan1)

    f.Close()

    return gs, cont_graphs1, exp

def Retrieve2DLikelihood(operators, op, maxNLL):

    canvas_d = []

    for proc in operators[op].keys():

        gs, cont_graphs1, exp = RetrieveCont(operators, op, proc, maxNLL)

        min_x = 0
        max_x = 0
        min_y = 0
        max_y = 0

        for h in range(len(cont_graphs1[0])):
            min_x_1 = cont_graphs1[0][h].GetXaxis().GetXmin()
            max_x_1 = cont_graphs1[0][h].GetXaxis().GetXmax()
            min_y_1 = cont_graphs1[0][h].GetYaxis().GetXmin()
            max_y_1 = cont_graphs1[0][h].GetYaxis().GetXmax()
            if min_x_1 < min_x: min_x = min_x_1
            if max_x_1 > max_x: max_x = max_x_1
            if min_y_1 < min_y: min_y = min_y_1
            if max_y_1 > max_y: max_y = max_y_1
        
        # print(min_x)
        # print(max_x)
        # print(min_y)
        # print(max_y)
 #       graphs.append([proc, cont_graphs[0], exp, [min_x, max_x],[min_y, max_y]])
        delta = max(abs(min_x),abs(max_x))

        if delta > 5:
            if 5 < delta < 10:
                xscale = 0.5
            elif 10 < delta < 20:
                xscale = 0.1
            elif delta > 20 :
                xscale = 0.01
        else:
            xscale = 1

        file = operators[op][proc]['path']
        op_ = [operators[op][proc]['op'],op]

        f = ROOT.TFile(file)
        t = f.Get("limit")

        # for i, event in enumerate(t):
        #     if i == 0:
        #         x_min = getattr(event, "k_" + op_[0])
        #         y_min = getattr(event, "k_" + op_[1])

        #     else: break

        to_draw = ROOT.TString("{}:{}:2*deltaNLL".format("k_" + op_[0], "k_" + op_[1]))
        n = t.Draw( to_draw.Data() , "deltaNLL<{} && deltaNLL>{}".format(float(maxNLL),-30), "l")

        x = np.ndarray((n), 'd', t.GetV1())
        y = np.ndarray((n), 'd', t.GetV2())
        z_ = np.ndarray((n), 'd', t.GetV3())
 
        z = np.array([i-min(z_) for i in z_]) #shifting likelihood toward 0
        x = np.array([i*xscale for i in x])
        graphScan = ROOT.TGraph2D(n,x,y,z)

        # graphScan.SetNpx(100)
        # graphScan.SetNpy(100)

        graphScan.GetZaxis().SetRangeUser(0, float(maxNLL))
        graphScan.GetHistogram().GetZaxis().SetRangeUser(0, float(maxNLL))

        for i in range(graphScan.GetHistogram().GetSize()):
            if (graphScan.GetHistogram().GetBinContent(i+1) == 0):
                graphScan.GetHistogram().SetBinContent(i+1, 100)

        hist = graphScan.GetHistogram().Clone("arb_hist")
        hist.SetContour(2, np.array([2.30, 5.99]))
        hist.Draw("CONT Z LIST")
        ROOT.gPad.Update()

        conts = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
        cont_graphs = [deepcopy(list(conts.At(i))) for i in range(2)]

        gs = deepcopy(graphScan)

        f.Close()

        extreme = max(abs(min_y),abs(max_y))

        print(operators[op][proc]['op'],op)

        canvas_d.append({
            '1sg' : cont_graphs[0],
            'min' : exp,
            'names' : operators[op][proc]['name'],
            'base_op' : op,
            'n_op' : operators[op][proc]['op'],
            'scale' : xscale,
            'extr' : extreme,
            'range' : [min_y,max_y],
        })

    canvas_d = sorted(canvas_d, key=itemgetter('extr'))

    canvas_ord = {
        '1sg' : [],
        'min' : [],
        'names' : [],
        'base_op' : op,
        'n_op' : [],
        'scale' : [],
        'extr' : [],
        'range' : [],
    }

    for i in range(len(canvas_d)):
        for key in canvas_ord.keys():
            if key is not 'base_op':
                canvas_ord[key].append(canvas_d[i][key])

    return canvas_ord


def Retrieve2DLikelihoodCombined(file, op, maxNLL, xscale, yscale):

    f = ROOT.TFile(file)
    t = f.Get("limit")

    for i, event in enumerate(t):
        if i == 0:
            x_min = getattr(event, "k_" + op[0])
            y_min = getattr(event, "k_" + op[1])

        else: break

    exp = ROOT.TGraph()
    exp.SetPoint(0, x_min, y_min)
    exp.SetMarkerSize(3)
    exp.SetMarkerStyle(34)
    exp.SetMarkerColor(ROOT.kGray +2)

    to_draw = ROOT.TString("{}:{}:2*deltaNLL".format("k_" + op[0], "k_" + op[1]))
    n = t.Draw( to_draw.Data() , "deltaNLL<{} && deltaNLL>{}".format(float(maxNLL),-30), "l")

    x = np.ndarray((n), 'd', t.GetV1())
    y = np.ndarray((n), 'd', t.GetV2())
    z_ = np.ndarray((n), 'd', t.GetV3())

    z = np.array([i-min(z_) for i in z_]) #shifting likelihood toward 0
    x = np.array([i*xscale for i in x])
    y = np.array([i*yscale for i in y])

    graphScan = ROOT.TGraph2D(n,x,y,z)

    # graphScan.SetNpx(100)
    # graphScan.SetNpy(100)

    graphScan.GetZaxis().SetRangeUser(0, float(maxNLL))
    graphScan.GetHistogram().GetZaxis().SetRangeUser(0, float(maxNLL))

    for i in range(graphScan.GetHistogram().GetSize()):
        if (graphScan.GetHistogram().GetBinContent(i+1) == 0):
            graphScan.GetHistogram().SetBinContent(i+1, 100)

    hist = graphScan.GetHistogram().Clone("arb_hist")
    hist.SetContour(2, np.array([2.30, 5.99]))
    hist.Draw("CONT Z LIST")
    ROOT.gPad.Update()

    conts = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    cont_graphs = [deepcopy(list(conts.At(i))) for i in range(2)]

    gs = deepcopy(graphScan)

    f.Close()

    return gs, cont_graphs, exp


def mkdir(path):
    try:
        os.mkdir(path)
    except:
        pass 

if __name__ == "__main__":

    ROOT.gROOT.SetBatch(1)

    parser = argparse.ArgumentParser(description='Command line parser for 2D plotting scans')
    parser.add_argument('--cfg',     dest='cfg',     help='the config file', required = True)
    parser.add_argument('--maxNLL',     dest='maxNLL',     help='Max likelihood', required = False, default = "20")
    parser.add_argument('--outf',     dest='outf',     help='out folder name', required = False, default = "summary2D")
    parser.add_argument('--lumi',     dest='lumi',     help='lumi to plot', required = False, default = "59.74")
    args = parser.parse_args()

    is_combo = False
    operators = OrderedDict()
    plt_options = {}

    execfile(args.cfg)

    mkdir(args.outf)

    if not is_combo:

        for op in operators.keys():

            canvas_d = Retrieve2DLikelihood (operators, op, args.maxNLL)

            #create as many canvas as necessary each containing up to 4 contours
            number = 3
            n_ = math.ceil(float(len(canvas_d['1sg']))/number)

            for idx in range(0,int(n_)):

                num = idx*number

                u1 = len(canvas_d['1sg'])

                c = ROOT.TCanvas("c_{}_{}".format(op, idx), "c_{}_{}".format(op, idx), 1000, 1000)

                margins = 0.13

                ROOT.gPad.SetRightMargin(margins)
                ROOT.gPad.SetLeftMargin(margins)
                ROOT.gPad.SetBottomMargin(margins)
                ROOT.gPad.SetTopMargin(margins)
                ROOT.gPad.SetFrameLineWidth(3)
                ROOT.gPad.SetTicks()

                leg = ROOT.TLegend(0.15, 0.8, 0.85, 0.85)
                leg.SetBorderSize(0)
                leg.SetNColumns(len(canvas_d['1sg'][num : num + number]))
                print(len(canvas_d['1sg'][num : num + number]))
                leg.SetTextSize(0.025)

                # linestyles = [2,7,5,6,4,8,2] * int(n_)
                linestyles = [2,7,5,6] * int(n_)
                # cols = [ROOT.kOrange+8, ROOT.kPink+10, ROOT.kAzure+10, ROOT.kTeal+10, ROOT.kViolet+10, ROOT.kRed]* int(n_)
                
                col1 = ROOT.TColor.GetFreeColorIndex()
                c1 = ROOT.TColor(col1, float(1./255.), float(111./255.), float(185./255.))
                col2 = ROOT.TColor.GetFreeColorIndex()
                c2 = ROOT.TColor(col2, float(255./255.), float(113./255.), float(61./255.)) 
                col3 = ROOT.TColor.GetFreeColorIndex()
                c3 = ROOT.TColor(col3, float(255./255.), float(101./255.), float(255./255.))
                col4 = ROOT.TColor.GetFreeColorIndex()
                c4 = ROOT.TColor(col4, float(134./255.), float(255./255.), float(29./255.))
                col5 = ROOT.TColor.GetFreeColorIndex()
                c5 = ROOT.TColor(col5, float(0./255.), float(226./255.), float(239./255.))                                
                col6 = ROOT.TColor.GetFreeColorIndex()
                c6 = ROOT.TColor(col6, float(127./255.), float(20./255.), float(124./255.))
                col7 = ROOT.TColor.GetFreeColorIndex()
                c7 = ROOT.TColor(col7, float(255./255.), float(62./255.), float(145./255.))
                col8 = ROOT.TColor.GetFreeColorIndex()
                c8 = ROOT.TColor(col8, float(255./255.), float(176./255.), float(12./255.))
                cols = {"cqq1":col1, "cqq11":col2, "cqq3":col3, "cqq31":col4, "cW":col5, "cHq1":col6, "cHq3":col7, "cHl3":col8}

                # ARCOBALENO
                # col1 = ROOT.TColor.GetFreeColorIndex()
                # c1 = ROOT.TColor(col1, float(135./255.), float(77./255.), float(154./255.))
                # col2 = ROOT.TColor.GetFreeColorIndex()
                # c2 = ROOT.TColor(col2, float(228./255.), float(29./255.), float(13./255.)) 
                # col3 = ROOT.TColor.GetFreeColorIndex()
                # c3 = ROOT.TColor(col3, float(255./255.), float(132./255.), float(27./255.))
                # col4 = ROOT.TColor.GetFreeColorIndex()
                # c4 = ROOT.TColor(col4, float(245./255.), float(187./255.), float(0./255.))                                
                # col5 = ROOT.TColor.GetFreeColorIndex()
                # c5 = ROOT.TColor(col5, float(0./255.), float(27./255.), float(255./255.))
                # col6 = ROOT.TColor.GetFreeColorIndex()
                # c6 = ROOT.TColor(col6, float(86./255.), float(186./255.), float(236./255.))
                # col7 = ROOT.TColor.GetFreeColorIndex()
                # c7 = ROOT.TColor(col7, float(59./255.), float(142./255.), float(4./255.))
                # cols = [col1, col2, col3, col4, col5, col6, col7]

                # SCURI MA VISIBILI
                # col1 = ROOT.TColor.GetFreeColorIndex()
                # c1 = ROOT.TColor(col1, float(146./255.), float(0.0), float(124./255.))
                # col2 = ROOT.TColor.GetFreeColorIndex()
                # c2 = ROOT.TColor(col2, float(0.0), float(129./255.), float(255./255.)) 
                # col3 = ROOT.TColor.GetFreeColorIndex()
                # c3 = ROOT.TColor(col3, float(0.0), float(166./255.), float(4./255.))
                # col4 = ROOT.TColor.GetFreeColorIndex()
                # c4 = ROOT.TColor(col4, float(219./255.), float(0.0), float(74./255.))                                
                # col5 = ROOT.TColor.GetFreeColorIndex()
                # c5 = ROOT.TColor(col5, float(1.0), float(131./255.), float(0.0))
                # col6 = ROOT.TColor.GetFreeColorIndex()
                # c6 = ROOT.TColor(col6, float(1.0), float(101./255.), float(1.0))
                # col7 = ROOT.TColor.GetFreeColorIndex()
                # c7 = ROOT.TColor(col7, float(1.0), float(101./255.), float(1.0))
                # cols = [col1, col2, col3, col4, col5, col6, col7]                
                
                c.SetGrid()

                y_min = 0
                y_max = 0
                for u in range(len(canvas_d['1sg'][idx*4: (idx*4) + 4])):
                    y_min_1 = canvas_d['range'][u+idx*4][0]
                    y_max_1 = canvas_d['range'][u+idx*4][1]
                    if y_min_1 < y_min : y_min = y_min_1
                    if y_max_1 > y_max : y_max = y_max_1
                y_min_new = y_min - 0.005*(y_max-y_min)
                y_max_new = y_max + 0.06*(y_max-y_min)

                for i in range(len(canvas_d['1sg'][num])):
                    if canvas_d['n_op'][num] in ["cHl3_cHq1","cHl3_cHq3","cHq1_cHq3"]: continue
                    canvas_d['1sg'][num][i].GetXaxis().SetLimits(-5, 5)
                    canvas_d['1sg'][num][i].GetYaxis().SetRangeUser(y_min_new, y_max_new) #add legend space
                    canvas_d['1sg'][num][i].GetYaxis().SetTitleOffset(1.6)
                    canvas_d['1sg'][num][i].GetYaxis().SetTitle(ConvertOptoLatex(op))
                    canvas_d['1sg'][num][i].GetXaxis().SetTitle("2nd Operator")
                    canvas_d['1sg'][num][i].SetTitle("")
                    canvas_d['1sg'][num][i].SetLineStyle(linestyles[0])
                    canvas_d['1sg'][num][i].SetLineColor(cols["{}".format(canvas_d['n_op'][num])])
                    canvas_d['1sg'][num][i].SetLineWidth(4)
                    if i == 0:
                        canvas_d['1sg'][num][i].Draw("AL")
                    else:
                        canvas_d['1sg'][num][i].Draw("L same")

                canvas_d['min'][num].Draw("P")

                name = ConvertOptoLatex(canvas_d['n_op'][num])
                if canvas_d['scale'][num] != 1: name = str(canvas_d['scale'][num]) + " #times " + name

                leg.AddEntry(canvas_d['1sg'][num][0], name, "L")

                for i,j, n, ls, scale in zip(canvas_d['1sg'][num+1 : num+number], canvas_d['min'][num+1 : num+number], canvas_d['n_op'][num+1 : num+number], linestyles[num+1 : num+number], canvas_d['scale'][num+1 : num+number]):
                    if n in ["cHl3_cHq1","cHl3_cHq3","cHq1_cHq3"]: continue
                    for g in i:
                        g.SetLineStyle(ls)
                        g.SetLineColor(cols["{}".format(n)])
                        g.SetLineWidth(4)
                        g.Draw("L same")
                    j.Draw("P same")
                    name = ConvertOptoLatex(n) 
                    if scale !=1 : name =  str(scale) + " #times " + ConvertOptoLatex(n)
                    leg.AddEntry(i[0], name, "L")

                #Draw fancy

                tex3 = ROOT.TLatex(0.86,.89,"59.74 fb^{-1}   (13 TeV)")
                tex3.SetNDC()
                tex3.SetTextAlign(31)
                tex3.SetTextFont(42)
                tex3.SetTextSize(0.04)
                tex3.SetLineWidth(2)
                tex3.Draw()

                if "process" in plt_options.keys():
                    if 'xpos' not in  plt_options.keys(): xpos = 0.35
                    else: xpos = plt_options['xpos']
                    if 'size' not in  plt_options.keys(): size = 0.04
                    else: size = plt_options['size']
                    if 'font' not in  plt_options.keys(): font = 42
                    else: font = plt_options['font']
                    tex4 = ROOT.TLatex(xpos,.89,plt_options['process'])
                    tex4.SetNDC()
                    tex4.SetTextAlign(31)
                    tex4.SetTextFont(font)
                    tex4.SetTextSize(size)
                    tex4.SetLineWidth(2)
                    tex4.Draw()

                leg.Draw()
                c.Draw()
                c.Print(args.outf + "/" + op + "{}.png".format(idx))
                c.Print(args.outf + "/" + op + "{}.pdf".format(idx))
        
    else:

        for op_pair in operators.keys():

            print("[INFO]: Generating plots for {}".format(op_pair))

            #mkdir(args.outf + "/" + op_pair)

            ops = op_pair.split("_")
            op_x = ops[0]
            op_y = ops[1]

            channels = operators[op_pair].keys()


            graphs = []

            max_x = max_y = min_y = min_x = 0
            
            #cycling on all the channels in the cfg
            for key in channels:
                print("... Retrieving channel {} ...".format(key))

                #extrapolate gs (the full 2d scan), contours (2 graphs [1sigma and 2 sigma])
                # and the minimum (0,0) by construction
                gs, cont_graphs, exp = Retrieve2DLikelihoodCombined(operators[op_pair][key]['path'], 
                                                                [op_x, op_y], args.maxNLL, 1., 1.)
                """
                for j in cont_graphs:
                    for item in j:
                        if item.GetXaxis().GetXmin() < min_x: min_x = item.GetXaxis().GetXmin()
                        if item.GetXaxis().GetXmax() > max_x: max_x = item.GetXaxis().GetXmax()
                        if item.GetYaxis().GetXmin() < min_y: min_y = item.GetYaxis().GetXmin()
                        if item.GetYaxis().GetXmax() > max_y: max_y = item.GetYaxis().GetXmax()
                """

                # min_x, max_x = cont_graphs[0].GetXaxis().GetXmin(), cont_graphs[0].GetXaxis().GetXmax() 
                # min_y, max_y = cont_graphs[0].GetYaxis().GetXmin(), cont_graphs[0].GetYaxis().GetXmax() 

                #set style
                for j in range(len(cont_graphs)):
                    for h in range(len(cont_graphs[j])):
                        cont_graphs[j][h].SetLineWidth(4)

                

                #shaded combination 
                if key == "combined":
                    #for j in range(len(cont_graphs)):
                    for h in range(len(cont_graphs[0])):
                        cont_graphs[0][h].SetLineColorAlpha(int(operators[op_pair][key]['color']), 0.9)
                        cont_graphs[0][h].SetFillStyle(1001) #sollid
                        cont_graphs[0][h].SetFillColorAlpha(int(operators[op_pair][key]['color']), 0.1)
                        if cont_graphs[0][h].GetXaxis().GetXmin() < min_x: min_x = cont_graphs[j][h].GetXaxis().GetXmin()
                        if cont_graphs[0][h].GetXaxis().GetXmax() > max_x: max_x = cont_graphs[j][h].GetXaxis().GetXmax()
                        if cont_graphs[0][h].GetYaxis().GetXmin() < min_y: min_y = cont_graphs[j][h].GetYaxis().GetXmin()
                        if cont_graphs[0][h].GetYaxis().GetXmax() > max_y: max_y = cont_graphs[j][h].GetYaxis().GetXmax()
                        # cont_graphs[0].SetLineColorAlpha(int(operators[op_pair][key]['color']), 0.7)

                    #centering on the combined
                    min_x = 4*min_x
                    max_x = 4*max_x 
                    min_y = 2*min_y 
                    max_y = 2*max_y
                    
                else:
                    for j in range(len(cont_graphs)):
                        for h in range(len(cont_graphs[j])):
                            cont_graphs[j][h].SetLineColor(int(operators[op_pair][key]['color']))
                            cont_graphs[j][h].SetFillStyle(0)
                            cont_graphs[j][h].SetFillColor(0)
                            #cont_graphs[j][h].SetFillColorAlpha(int(operators[op_pair][key]['color']), 0.1)
                            min_x = cont_graphs[j][h].GetXaxis().GetXmin()
                            max_x = cont_graphs[j][h].GetXaxis().GetXmax()
                            min_y = cont_graphs[j][h].GetYaxis().GetXmin()
                            max_y = cont_graphs[j][h].GetYaxis().GetXmax()
                
                for j in range(len(cont_graphs)):
                        for h in range(len(cont_graphs[j])):
                            cont_graphs[j][h].SetLineStyle(int(operators[op_pair][key]['linestyle']))
                
                #print(cont_graphs[0])
                graphs.append([key, cont_graphs[0], exp, [min_x, max_x],[min_y, max_y]])

            #zoomed version
            
            # put the combined graph at first position in the list
            # soit will be plotted first
            combo_id = 0
            for idx, g in enumerate(graphs):
                if g[0] == "combined": combo_id = idx 

            combo = graphs.pop(combo_id)
            graphs.insert(0, combo)
            
            # now plotting for real

            c = ROOT.TCanvas("c_{}".format(op_pair), "c_{}".format(op_pair), 1000, 1000)

            margins = 0.13

            ROOT.gPad.SetRightMargin(margins)
            ROOT.gPad.SetLeftMargin(margins)
            ROOT.gPad.SetBottomMargin(margins)
            ROOT.gPad.SetTopMargin(margins)
            ROOT.gPad.SetFrameLineWidth(3)
            ROOT.gPad.SetTicks()

            leg = ROOT.TLegend(0.5, 0.65, 0.85, 0.85)
            leg.SetBorderSize(0)
            leg.SetNColumns((int(len(graphs) + 1)/2))
            leg.SetTextSize(0.03)

            #c.SetGrid()

            #first graph
            for i in range(len(graphs[0][1])):
                graphs[0][1][i].GetYaxis().SetTitleOffset(1.5)
                graphs[0][1][i].GetXaxis().SetTitleOffset(1.2)
                graphs[0][1][i].GetYaxis().SetTitle(ConvertOptoLatex(op_y))
                graphs[0][1][i].GetXaxis().SetTitle(ConvertOptoLatex(op_x))
                graphs[0][1][i].SetTitle("")
                #graphs[0][1].SetLineStyle(linestyles[0])
                if i == 0:
                    #graphs[0][1][i].GetYaxis().SetRangeUser(graphs[0][1][i].GetYaxis().GetXmin(), graphs[0][1][i].GetYaxis().GetXmax() + 0.2*(graphs[0][1][i].GetYaxis().GetXmax()))
                    graphs[0][1][i].GetYaxis().SetRangeUser(graphs[0][4][0], graphs[0][4][1])
                    graphs[0][1][i].GetXaxis().SetRangeUser(graphs[0][3][0], graphs[0][3][1])
                    if graphs[0][0]  == "combined": graphs[0][1][i].Draw("ALF")
                    else: graphs[0][1][i].Draw("AL")
                else:
                    if graphs[0][0]  == "combined": graphs[0][1][i].Draw("LF same")
                    else: graphs[0][1][i].Draw("L same")
            graphs[0][2].Draw("P same")

            leg.AddEntry(graphs[0][2], "SM", "P")

            name = graphs[0][0]
            #leg.AddEntry(graphs[0][1][0], name, "L")
            leg.AddEntry(graphs[0][1][0], ConvertProc(name), "F")

            for i in graphs[1:]:
                for j in i[1]:
                    if i[0] == "combined": j.Draw("LF same")
                    else: j.Draw("L same")
                i[2].Draw("P same")
                name = i[0]
                #if name == "combined": name = "Combined"
                #if scale!=1 : name =  str(scale) + " #times " + n
                #leg.AddEntry(i[1][0], name, "L")
                leg.AddEntry(i[1][0], ConvertProc(name), "F")

            #Draw fancy

            tex3 = ROOT.TLatex(0.86,.89,"59.74 fb^{-1}   (13 TeV)")
            tex3.SetNDC()
            tex3.SetTextAlign(31)
            tex3.SetTextFont(42)
            tex3.SetTextSize(0.04)
            tex3.SetLineWidth(2)
            tex3.Draw()

            if "process" in plt_options.keys():
                if 'xpos' not in  plt_options.keys(): xpos = 0.35
                else: xpos = plt_options['xpos']
                if 'size' not in  plt_options.keys(): size = 0.04
                else: size = plt_options['size']
                if 'font' not in  plt_options.keys(): font = 42
                else: font = plt_options['font']
                tex4 = ROOT.TLatex(xpos,.89,plt_options['process'])
                tex4.SetNDC()
                tex4.SetTextAlign(31)
                tex4.SetTextFont(font)
                tex4.SetTextSize(size)
                tex4.SetLineWidth(2)
                tex4.Draw()

            leg.Draw()
            c.Draw()
            c.Print(args.outf + "/" + op_pair + ".pdf")
            c.Print(args.outf + "/" + op_pair + ".png")


            #unzoomed version

            lower_x = []
            higher_x = []
            lower_y = []
            higher_y = []

            for i in graphs:
                lower_x.append(i[3][0])
                higher_x.append(i[3][1])
                lower_y.append(i[4][0])
                higher_y.append(i[4][1])
            
            min_x  = min(lower_x)
            max_x  = max(higher_x)
            min_y  = min(lower_y)
            max_y  = max(higher_y)

            c = ROOT.TCanvas("c_{}_unzoomed".format(op_pair), "c_{}_unzoomed".format(op_pair), 1000, 1000)

            margins = 0.13

            ROOT.gPad.SetRightMargin(margins)
            ROOT.gPad.SetLeftMargin(margins)
            ROOT.gPad.SetBottomMargin(margins)
            ROOT.gPad.SetTopMargin(margins)
            ROOT.gPad.SetFrameLineWidth(3)
            ROOT.gPad.SetTicks()

            leg = ROOT.TLegend(0.5, 0.65, 0.85, 0.85)
            leg.SetBorderSize(0)
            leg.SetNColumns(int(len(graphs)/2))
            leg.SetTextSize(0.03)

            #c.SetGrid()

            #first graph
            for i in range(len(graphs[0][1])):
                graphs[0][1][i].GetYaxis().SetRangeUser(min_y, max_y + 0.3*max_y)
                graphs[0][1][i].GetXaxis().SetRangeUser(min_x, max_x)
                graphs[0][1][i].GetYaxis().SetTitleOffset(1.5)
                graphs[0][1][i].GetXaxis().SetTitleOffset(1.2)
                graphs[0][1][i].GetYaxis().SetTitle(ConvertOptoLatex(op_y))
                graphs[0][1][i].GetXaxis().SetTitle(ConvertOptoLatex(op_x))
                graphs[0][1][i].SetTitle("")
                #graphs[0][1].SetLineStyle(linestyles[0])
                if i == 0:
                    graphs[0][1][i].Draw("ALF")
                else:
                    graphs[0][1][i].Draw("LF same")

            graphs[0][2].Draw("P same")
            leg.AddEntry(graphs[0][2], "SM", "P")

            """
            graphs[0][1].GetYaxis().SetRangeUser(min_y, max_y)
            graphs[0][1].GetXaxis().SetRangeUser(min_x, max_x)
            graphs[0][1].GetYaxis().SetTitleOffset(1.5)
            graphs[0][1].GetXaxis().SetTitleOffset(1.2)
            graphs[0][1].GetYaxis().SetTitle(ConvertOptoLatex(op_y))
            graphs[0][1].GetXaxis().SetTitle(ConvertOptoLatex(op_x))
            graphs[0][1].SetTitle("")
            #graphs[0][1].SetLineStyle(linestyles[0])
            graphs[0][1].Draw("AL")
            graphs[0][2].Draw("P same")
            """

            name = graphs[0][0]
            # leg.AddEntry(graphs[0][1][0], name, "L")
            leg.AddEntry(graphs[0][1][0], ConvertProc(name), "F")

            for i in graphs[1:]:
                for j in i[1]:
                    j.Draw("L same")
                i[2].Draw("P same")
                name = i[0]
                if name == "combined": name = "Combined"
                # if scale!=1 : name =  str(scale) + " #times " + n
                leg.AddEntry(i[1][0], ConvertProc(name), "F")
                # leg.AddEntry(i[1][0], name, "L")

            #Draw fancy

            tex3 = ROOT.TLatex(0.86,.89,"300 fb^{-1}   (13 TeV)")
            tex3.SetNDC()
            tex3.SetTextAlign(31)
            tex3.SetTextFont(42)
            tex3.SetTextSize(0.04)
            tex3.SetLineWidth(3)
            tex3.Draw()

            if "process" in plt_options.keys():
                if 'xpos' not in  plt_options.keys(): xpos = 0.35
                else: xpos = plt_options['xpos']
                if 'size' not in  plt_options.keys(): size = 0.04
                else: size = plt_options['size']
                if 'font' not in  plt_options.keys(): font = 42
                else: font = plt_options['font']
                tex4 = ROOT.TLatex(xpos,.89,plt_options['process'])
                tex4.SetNDC()
                tex4.SetTextAlign(31)
                tex4.SetTextFont(font)
                tex4.SetTextSize(size)
                tex4.SetLineWidth(3)
                tex4.Draw()

            leg.Draw()
            c.Draw()
            c.Print(args.outf + "/" + op_pair + "_unzoomed.pdf")
            c.Print(args.outf + "/" + op_pair + "_unzoomed.png")

#    os.system("cp /afs/cern.ch/user/g/gboldrin/index.php " + args.outf)


