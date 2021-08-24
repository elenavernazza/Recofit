import numpy as np 
import os
import sys
import ROOT
import copy
from array import array

class CombinePlotManager:

    def __init__(self):

        self.n_plot = 0
        self.NLL_lims = [50, -30]
        self.plot_type = "1D"
        self.plotOptions = {}
        self.canvOptions = {"SetTitle": "", "SetGrid": True}
        self.optionals = [] #availeble Draw option
        self.LS1D = {}
        self.NLLlines = {}
        self.NLLtext = {}
        self.NLLtextsize = 0.03
        self.NLLtextfont = 42
        self.LS2D = {}
        self.excludeOps = []
        self.saveName = "outPlot.png"
        self.lumi = "59.74 fb^{-1}"
        self.tev = 13
        self.contours = [2.30, 5.99]
        self.DrawOptions2D = {"Contour": "L", "Graph": "colz", "Histo": "CONT1 LIST SAME", "Min": "P"}
        self.xtit = "x"
        self.ytit = "y"
        self.NoptUpperleft = 0
        self.channel = "WZ VBS"



    def setGradient(self):
        __stops = array('d', [0.00, 1.00])
        #__red   = array('d', [1.00, 0.00, 0.00])
        #__green = array('d', [0.00, 0.00, 0.00])
        #__blue  = array('d', [1.00, 0.00, 0.00])
        __red = array('d', [1.0, 0.0])
        __green  = array('d', [1.0, 0.0])
        __blue  = array('d', [1.0, 1.00])

        #ROOT.TColor.CreateGradientColorTable(3, __stops, __red, __green, __blue, 255)
        ROOT.TColor.CreateGradientColorTable(2, __stops,__red, __green, __blue, 50)
        ROOT.gStyle.SetNumberContours(100)


    def generateCMSBox(self):
        tex = ROOT.TLatex(0.13,0.95,"CMS")
        tex.SetNDC()
        tex.SetTextFont(61)
        tex.SetTextSize(0.05)
        tex.SetLineWidth(2)
        tex.SetTextAlign(13)
        self.optionals.append(tex)

    def generateNopsBox(self, Nop):
        tex = ROOT.TLatex(0.2,0.9 - 0.05 * self.NoptUpperleft,"N ops = {}".format(Nop))
        self.NoptUpperleft += 1
        tex.SetNDC()
        tex.SetTextFont(42)
        tex.SetTextSize(0.03)
        tex.SetLineWidth(2)
        tex.SetTextAlign(31)
        self.optionals.append(tex)

    def generateSystBox(self, nuis):
        tex = ROOT.TLatex(0.2,0.9 - 0.05 * self.NoptUpperleft,"Nuisance = {}%".format(nuis))
        tex.SetNDC()
        tex.SetTextFont(42)
        tex.SetTextSize(0.04)
        tex.SetLineWidth(2)
        tex.SetTextAlign(31)
        self.optionals.append(tex)

    def generatePreliminaryBox(self):
        tex = ROOT.TLatex  (0.25, 0.944, "Preliminary")
        tex.SetNDC()
        tex.SetTextSize(0.76 * 0.05)
        tex.SetTextFont(52)
        tex.SetTextColor(ROOT.kBlack)
        tex.SetTextAlign(13)
        self.optionals.append(tex)

    def generateTeVBox(self):
        tex = ROOT.TLatex(0.882,0.905,"(" + str(self.tev) + " TeV)")
        tex.SetNDC()
        tex.SetTextAlign(31)
        tex.SetTextFont(42)
        tex.SetTextSize(0.04)
        tex.SetLineWidth(2)
        self.optionals.append(tex)

    def generateLumiBox(self):
        tex = ROOT.TLatex(0.72,0.905, self.lumi)
        tex.SetNDC()
        tex.SetTextAlign(31)
        tex.SetTextFont(42)
        tex.SetTextSize(0.04)
        tex.SetLineWidth(2)
        self.optionals.append(tex)
    
    def generateChannelBox(self):
        tex = ROOT.TLatex(0.4, 0.905, self.channel)
        tex.SetNDC()
        tex.SetTextAlign(31)
        tex.SetTextFont(42)
        tex.SetTextSize(0.04)
        tex.SetLineWidth(2)
        self.optionals.append(tex)

    def generateAllBoxes(self):
#        self.generateCMSBox()
#        self.generatePreliminaryBox()
        self.generateChannelBox()
        self.generateTeVBox()
        self.generateLumiBox()


    def exclude(self, op_list):
        self.excludeOps = op_list


    def configureOpPlot(self, op, plot_dict):

        if type(plot_dict) != dict: sys.exit("[ERROR]: plot_dict argument (3) must be a dict")
        self.plotOptions[op] = plot_dict

    def setCanvOptions(self, canv_op):
        self.canvOptions = canv_op


    def createLS1D(self, op, rfile, inclass=None):

        if inclass is None: inclass = op

        f = ROOT.TFile(rfile)
        limit = f.Get("limit")
        
        to_draw = ROOT.TString("2*deltaNLL:{}".format(op))
        n = limit.Draw( to_draw.Data() , "deltaNLL<{} && deltaNLL>{}".format(self.NLL_lims[0], self.NLL_lims[1]), "l")

        x = np.ndarray((n), 'd', limit.GetV2())[1:] #removing first element (0,0)
        y_ = np.ndarray((n), 'd', limit.GetV1())[1:] #removing first element (0,0)

        x, ind = np.unique(x, return_index = True)
        y_ = y_[ind]
        y = np.array([i-min(y_) for i in y_])

        graphScan = ROOT.TGraph(x.size,x,y)

        graphScan.GetYaxis().SetTitle("-2 #Delta LL")
        graphScan.GetXaxis().SetTitle(self.xtit)

        if inclass in self.plotOptions.keys():
            plot_mod = self.plotOptions[inclass]
            #{"SetLineStyle": 1, ...}
            for conf in plot_mod.keys():
                getattr(graphScan, conf)(plot_mod[conf])

        x_val = ROOT.Double()
        y_val = ROOT.Double()

        x_vals = []
        y_vals = []
        
        for i in range(graphScan.GetN()):
            graphScan.GetPoint(i, x_val, y_val)
            y_vals.append(copy.copy(y_val))
            x_vals.append(copy.copy(x_val))

        #x_ = [x for _,x in sorted(zip(ys,xs))]

        #THE FOLLOWING SUPPOSE A PARABOLIC TREND OF THE LL
        # (AT LEAST AT THE HEIGHT OF THE MAXIMUM)
        x_vals, y_vals = zip(*sorted(zip(x_vals, y_vals)))

        
        ymax = max(y_vals)/2
        if ymax > 10: ymax = 10

        x_ = []

        count = 0
        for x,y in zip(x_vals, y_vals):
            if y - ymax <= 0 and count == 0:
                x_.append(copy.copy(x))
                count+=1
            elif y - ymax >= 0 and count == 1:
                x_.append(copy.copy(x))
                break

        if len(x_) != 2 : x_ = [-10,10]

        x_ = sorted(x_)
        
        #graphScan.SetMaximum(ymax)

        #x_min = x_[0] - abs(0.2*x_[0])
        #x_max = x_[1] + abs(0.2*x_[1])
        #graphScan.GetXaxis().SetRangeUser(x_min, x_max)

        x_min = graphScan.GetXaxis().GetXmin(),
        x_max = graphScan.GetXaxis().GetXmax ()
        
        #one and two sigma levels

        o_sigma = ROOT.TLine(x_min, 1, x_max, 1)
        o_sigma.SetLineStyle(7)
        o_sigma.SetLineWidth(2)
        o_sigma.SetLineColor(ROOT.kGray+2)
        t_sigma = ROOT.TLine(x_min, 3.84, x_max, 3.84)
        t_sigma.SetLineStyle(7)
        t_sigma.SetLineWidth(2)
        t_sigma.SetLineColor(ROOT.kGray+2)

        #text for horizontal lines

        x_frac = x_min + abs(0.05*(x_max-x_min))
        self.LS1D[inclass] = copy.deepcopy(graphScan)
        self.NLLlines[inclass] = {"1": copy.deepcopy(o_sigma), "2": copy.deepcopy(t_sigma)}
        self.NLLtext[inclass] = {"1": (x_frac, 1.05), "2": (x_frac, 3.89)}

        f.Close()

    def createLS2D(self, op, rfile, inclass=None, FillHigh=False):
        
        if len(op) != 2: sys.exit("[ERROR] Wrong number of operators")
        if inclass is None: inclass = op

        self.LS2D[inclass] = {}

        f = ROOT.TFile(rfile)
        limit = f.Get("limit")
        to_draw = ROOT.TString("{}:{}:2*deltaNLL".format(op[0], op[1]))
        n = limit.Draw( to_draw.Data() , "deltaNLL<{} && deltaNLL>{}".format(self.NLL_lims[0], self.NLL_lims[1]), "colz")

        x = np.ndarray((n), 'd', limit.GetV1())
        y = np.ndarray((n), 'd', limit.GetV2())
        z = np.ndarray((n), 'd', limit.GetV3())

        graphScan = ROOT.TGraph2D(n,x,y,z)

        graphScan.GetZaxis().SetTitle("-2 #Delta LL")
        graphScan.GetXaxis().SetTitle(self.xtit)
        graphScan.GetYaxis().SetTitle(self.ytit)

        graphScan.GetHistogram().GetZaxis().SetTitle("-2 #Delta LL")
        graphScan.GetHistogram().GetXaxis().SetTitle(self.xtit)
        graphScan.GetHistogram().GetYaxis().SetTitle(self.ytit)

        graphScan.GetZaxis().SetRangeUser(0,9.99)
        graphScan.GetHistogram().GetZaxis().SetRangeUser(0,9.99)

        bin_vals = []

        if FillHigh:
            for i in range(graphScan.GetHistogram().GetSize()):
                bin_vals.append(graphScan.GetHistogram().GetBinContent(i+1))
                if (graphScan.GetHistogram().GetBinContent(i+1) == 0):
                    graphScan.GetHistogram().SetBinContent(i+1, 100)

        c = ROOT.TCanvas("c", "c", 600,600)


        hist = graphScan.GetHistogram().Clone("arb_hist")
        hist.SetContour(len(self.contours), np.array(self.contours))
        hist.Draw("CONT Z LIST")
        ROOT.gPad.Update()

        minbin = hist.GetMinimumBin()
        xx, yy, zz = ROOT.Long(0), ROOT.Long(0), ROOT.Long(0)
        hist.GetBinXYZ(minbin, xx, yy, zz)
        x_min = (hist.GetXaxis()).GetBinCenter(xx)
        y_min = (hist.GetYaxis()).GetBinCenter(yy)
    
        for i, event in enumerate(limit):
            if i == 0:
                x_min = getattr(event, op[0])
                y_min = getattr(event, op[1])

            else: break

        exp = ROOT.TGraph()
        exp.SetPoint(0, x_min, y_min)

        conts = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
        cont_graphs = [conts.At(i).First() for i in range(len(self.contours))]
        for item in cont_graphs:
            item.GetXaxis().SetTitle(self.xtit)
            item.GetYaxis().SetTitle(self.ytit)


        if inclass in self.plotOptions.keys():
            if "Graph" in self.plotOptions[inclass].keys():
                plot_mod = self.plotOptions[inclass]["Graph"]
                #{"SetLineStyle": 1, ...}
                for conf in plot_mod.keys():
                    getattr(graphScan, conf)(plot_mod[conf])

            if "Histo" in self.plotOptions[inclass].keys():
                plot_mod = self.plotOptions[inclass]["Histo"]
                #{"SetLineStyle": 1, ...}
                for conf in plot_mod.keys():
                    getattr(hist, conf)(plot_mod[conf])

            if "Contour" in self.plotOptions[inclass].keys():
                
                plot_mod = self.plotOptions[inclass]["Contour"]
                #{"SetLineStyle": 1, ...}
                for i in range(len(self.contours)):
                    plot = plot_mod[self.contours[i]]
                    for conf in plot.keys():
                        getattr(cont_graphs[i], conf)(plot[conf])

            if "Min" in self.plotOptions[inclass].keys():
                plot_mod = self.plotOptions[inclass]["Min"]
                #{"SetLineStyle": 1, ...}
                for conf in plot_mod.keys():
                    getattr(exp, conf)(plot_mod[conf])


        self.LS2D[inclass]["Contour"] = {}

        for i in range(len(cont_graphs)):
            self.LS2D[inclass]["Contour"][self.contours[i]] = copy.deepcopy(cont_graphs[i])
        
        self.LS2D[inclass]["Min"] = copy.deepcopy(exp)
        self.LS2D[inclass]["Graph"] = copy.deepcopy(graphScan)
        self.LS2D[inclass]["Histo"] = copy.deepcopy(graphScan.GetHistogram())

        f.Close()



    
    def CanvasCreator(self, dims, margins=0.11):
        if len(dims) == 2: self.canvas = ROOT.TCanvas( "c", "c", dims[0], dims[1] )
        elif len(dims) == 4: self.canvas = ROOT.TCanvas( "c", "c", dims[0], dims[1], dims[2], dims[3] )
        else: sys.exit("[ERROR] dims argument (1) either list of len 2 or 4")

        for opt in self.canvOptions.keys():
            getattr(self.canvas, opt)(self.canvOptions[opt])

        ROOT.gPad.SetRightMargin(margins)
        ROOT.gPad.SetLeftMargin(margins)
        ROOT.gPad.SetBottomMargin(margins)
        ROOT.gPad.SetTopMargin(margins)
        ROOT.gPad.SetFrameLineWidth(3)

        self.canvas.Update()


    def createLegend(self, leg_titles, type_="1D", legcoord = (0.89, 0.89, 0.6, 0.7), Bordersize=0):
        if bool(self.LS1D) and bool(self.LS2D): sys.exit("[ERROR] empty graphs, fill them first")
        if type_=="1D": to_draw = self.LS1D
        elif type_=="2D": to_draw = self.LS2D 

        leg = ROOT.TLegend(legcoord[0], legcoord[1], legcoord[2], legcoord[3])
        leg.SetBorderSize(Bordersize)
        if hasattr(self, "legtit"):
            leg.SetHeader(self.legtit)
        
        if not all(i for i in leg_titles.keys() for i in to_draw.keys()): sys.exit("[ERROR]")
        for g in leg_titles.keys():
            if type(leg_titles[g]) != dict:
                n_ = leg_titles[g].split(':')[0]
                t_ = leg_titles[g].split(':')[1]
                leg.AddEntry(to_draw[g], n_, t_)
            else:
                for m in leg_titles[g]:
                    if type(to_draw[g][m]) == dict and type(leg_titles[g][m]) == dict:
                        for tit in leg_titles[g][m]:
                            n_ = leg_titles[g][m][tit].split(':')[0]
                            t_ = leg_titles[g][m][tit].split(':')[1]
                            leg.AddEntry(to_draw[g][m][tit], n_, t_)
                    else:
                        n_ = leg_titles[g][m].split(':')[0]
                        t_ = leg_titles[g][m].split(':')[1]
                        leg.AddEntry(to_draw[g][m], n_, t_)

        self.legend = leg


    def plot1D(self, save=False):
        if not bool(self.LS1D): return

        if not hasattr(self, "canvas"): sys.exit("[ERROR] Canvas not created. Create canvas first")

        draw = False
        lines = []
        text = []
        for op in self.LS1D.keys():
            if op not in self.excludeOps:
                draw_op = "l"
                if not draw: 
                    draw_op = "a" + draw_op
                    draw = True
                    lines.append(self.NLLlines[op]["1"])
                    lines.append(self.NLLlines[op]["2"])
                    text.append(self.NLLtext[op]["1"])
                    text.append(self.NLLtext[op]["2"])

                else: draw_op+= " same"
                if op in self.plotOptions.keys():
                    if "Draw" in self.plotOptions[op].keys(): 
                        draw_op = self.LS1D[op].Draw(self.plotOptions[op]["Draw"])

                self.LS1D[op].Draw(draw_op)

            else: continue
        
        for item in self.optionals:
            item.Draw("same")

        lines[0].Draw("l same")
        lines[1].Draw("l same")
        os = ROOT.TLatex()
        os.SetTextFont(self.NLLtextfont)
        os.SetTextSize(self.NLLtextsize)
        os.DrawLatex( text[0][0], text[0][1], '68%' )
        ts = ROOT.TLatex()
        ts.SetTextFont(self.NLLtextfont)
        ts.SetTextSize(self.NLLtextsize)
        ts.DrawLatex( text[1][0], text[1][1], '95%' )


        if hasattr(self, "legend"): self.legend.Draw("same")

        self.canvas.Draw()
        if save: self.canvas.Print(self.saveName)


    def plot2D(self, save=False, what=[]):
        if not bool(self.LS2D): return

        if not hasattr(self, "canvas"): sys.exit("[ERROR] Canvas not created. Create canvas first")

        draw = False
        for op in self.LS2D.keys():
            if not all(i for i in what for i in self.LS2D[op].keys()): sys.exit("[ERROR] Required not saved info when plotting 2D...")
            if op not in self.excludeOps:
                for g_type in what:
                    to_plot = self.LS2D[op][g_type]
                    if g_type == "Contour":
                        for key in sorted(to_plot.keys(), reverse=True):
                            draw_op = self.DrawOptions2D[g_type]
                            if not draw: 
                                draw_op = "A " + draw_op
                                draw = True
                            else: draw_op+= " same"

                            to_plot[key].Draw(draw_op)

                    else:
                        draw_op = self.DrawOptions2D[g_type]
                        if not draw:  
                            draw = True
                            draw_op = "A " + draw_op
                        else: draw_op+= " same"
                        to_plot.Draw(draw_op)


            else: continue
        
        for item in self.optionals:
            item.Draw("same")

        if hasattr(self, "legend"): self.legend.Draw("same")

        self.canvas.Draw()
        self.canvas.Update()
        if save: self.canvas.Print(self.saveName)







            



