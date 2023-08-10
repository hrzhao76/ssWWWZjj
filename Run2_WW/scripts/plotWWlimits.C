#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <cmath>
#include <TCutG.h>
#include <TString.h>
#include <TH1.h>
#include <TH2.h>
#include <TGraph.h>
#include <TLegend.h>
#include <TCanvas.h>
#include <TFile.h>
#include <TTree.h>
#include <TStyle.h>
#include <TLatex.h>
#include <TROOT.h>

static const int mFont = 132;

static float thMass[23]  = {200,225,250,275,300,325,350,375,400,425,450,475,500,525,550,600,700,800,900,1000,1500,2000,3000};
static float thWidth[23] = {0.2515,0.3945,0.6847,0.9375,1.4165,1.8087,2.5150,3.0725,4.0425,4.7850,6.0575,7.0125,8.6175,10.0,11.7875,15.6225,25.5250,38.8500,14.0062,19.3937,66.8750,159.8125,160.}; // here keep the width of the 3TeV to be narrow as for the given sh value it becomes too large and would violate unitarity. In any case the model dependent GM limits will go up to 1 TeV while the 3 TeV sample will be used only for xsec*BR model independent limits with narrow width.
static float thSin[23]   = {0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.25,0.25,0.25,0.25,0.25};
static int lenlimit = 23;

// Mass points and cross sections for Sh = 1;
static float thMassGM[23] = {200,225,250,275,300,325,350,375,400,425,450,475,500,525,550,600,700,800,900,1000,1500,2000,3000};
static float thXsecGM[23] = {3.09002E+03,2.84349E+03,2.18168E+03,2.01433E+03,1.62200E+03,1.49903E+03,1.24324E+03,1.15102E+03,9.74661E+02,9.05021E+02,7.77762E+02,7.23610E+02,6.29550E+02,5.75700E+02,5.15480E+02,4.25981E+02,2.98096E+02,2.13284E+02,1.57429E+02,1.17380E+02,3.14662E+01,9.71088E+00,4.13017E+00};

void h2_style(TH2 *h){

   h->SetLabelOffset(0.005,"X");  // D=0.005
   h->SetLabelOffset(0.010,"Y");  // D=0.005
   h->SetTitleOffset(1.0,"X");
   h->SetTitleOffset(1.2,"Y");
   h->SetTitle(0);

}

void leg_style(TLegend *h){

  //  h->SetTextFont(mFont);
  h->SetTextSize(0.035);
  h->SetFillColor(0);
  h->SetFillStyle(0);
  h->SetLineColor(0);
  h->SetBorderSize(0);

}

void setAtlasStyle(){

  TStyle *atlasStyle = new TStyle("ATLAS","Atlas style");

  // use plain black on white colors
  Int_t icol=0; // WHITE
  atlasStyle->SetFrameBorderMode(icol);
  atlasStyle->SetFrameFillColor(icol);
  atlasStyle->SetCanvasBorderMode(icol);
  atlasStyle->SetCanvasColor(icol);
  atlasStyle->SetPadBorderMode(icol);
  atlasStyle->SetPadColor(icol);
  atlasStyle->SetStatColor(icol);
  //atlasStyle->SetFillColor(icol); // don't use: white fill color for *all* objects

  // set the paper & margin sizes
  atlasStyle->SetPaperSize(20,26);

  // set margin sizes
  atlasStyle->SetPadTopMargin(0.05);
  atlasStyle->SetPadRightMargin(0.05);
  atlasStyle->SetPadBottomMargin(0.16);
  atlasStyle->SetPadLeftMargin(0.16);

  // set title offsets (for axis label)
  atlasStyle->SetTitleXOffset(1.4);
  atlasStyle->SetTitleYOffset(1.4);

  // use large fonts
  //Int_t font=72; // Helvetica italics
  Int_t font=42; // Helvetica
  Double_t tsize=0.045;
  atlasStyle->SetTextFont(font);

  atlasStyle->SetTextSize(tsize);
  atlasStyle->SetLabelFont(font,"x");
  atlasStyle->SetTitleFont(font,"x");
  atlasStyle->SetLabelFont(font,"y");
  atlasStyle->SetTitleFont(font,"y");
  atlasStyle->SetLabelFont(font,"z");
  atlasStyle->SetTitleFont(font,"z");

  atlasStyle->SetLabelSize(tsize,"x");
  atlasStyle->SetTitleSize(tsize,"x");
  atlasStyle->SetLabelSize(tsize,"y");
  atlasStyle->SetTitleSize(tsize,"y");
  atlasStyle->SetLabelSize(tsize,"z");
  atlasStyle->SetTitleSize(tsize,"z");

  // use bold lines and markers
  atlasStyle->SetMarkerStyle(20);
  atlasStyle->SetMarkerSize(1.2);
  atlasStyle->SetHistLineWidth(2.);
  atlasStyle->SetLineStyleString(2,"[12 12]"); // postscript dashes

  // get rid of X error bars
  //atlasStyle->SetErrorX(0.001);
  // get rid of error bar caps
  atlasStyle->SetEndErrorSize(0.);

  // do not display any of the standard histogram decorations
  atlasStyle->SetOptTitle(0);
  //atlasStyle->SetOptStat(1111);
  atlasStyle->SetOptStat(0);
  //atlasStyle->SetOptFit(1111);
  atlasStyle->SetOptFit(0);

  // put tick marks on top and RHS of plots
  atlasStyle->SetPadTickX(1);
  atlasStyle->SetPadTickY(1);

  gROOT->SetStyle("ATLAS");
  gROOT->ForceStyle();

}

void plotWWlimits(TString path, bool dosin, bool dobdtfit, bool doAsimov){

  cout << endl;
  cout << " >>> Let's start!" << endl;
  cout << dobdtfit << endl;
  ostringstream histo;

  bool doLog   = 1;
  bool doshade = 0;

  if (dosin){
    doLog = 0;
    doshade = 1;
  }

  setAtlasStyle();

  float yMin = 0.1;
  float yMax = 0;
  float xMin = 5000;
  float xMax = 0;

  bool doGrid  = 0;
  bool doObs   = 0;
  bool doGM    = 0; // Draw GM xsec for sH = 1

  TString nwregion = "BlaBlaBla";

  TString Lumi = "139";

  //////////////////////////////
  //// Theory prediction part //
  //////////////////////////////

  map<double, double> xsec_mass_H5VBS_input_lvlv;

  // Sample cross section values in [fb]
  xsec_mass_H5VBS_input_lvlv[200]  = 81.998;
  xsec_mass_H5VBS_input_lvlv[225]  = 75.456;
  xsec_mass_H5VBS_input_lvlv[250]  = 57.894;
  xsec_mass_H5VBS_input_lvlv[275]  = 53.453;
  xsec_mass_H5VBS_input_lvlv[300]  = 43.042;
  xsec_mass_H5VBS_input_lvlv[325]  = 39.779;
  xsec_mass_H5VBS_input_lvlv[350]  = 32.991;
  xsec_mass_H5VBS_input_lvlv[375]  = 30.544;
  xsec_mass_H5VBS_input_lvlv[400]  = 25.864;
  xsec_mass_H5VBS_input_lvlv[425]  = 24.016;
  xsec_mass_H5VBS_input_lvlv[450]  = 20.639;
  xsec_mass_H5VBS_input_lvlv[475]  = 19.202;
  xsec_mass_H5VBS_input_lvlv[500]  = 16.706;
  xsec_mass_H5VBS_input_lvlv[525]  = 15.277;
  xsec_mass_H5VBS_input_lvlv[550]  = 13.679;
  xsec_mass_H5VBS_input_lvlv[600]  = 11.304;
  xsec_mass_H5VBS_input_lvlv[700]  = 7.9104;
  xsec_mass_H5VBS_input_lvlv[800]  = 5.6598;
  xsec_mass_H5VBS_input_lvlv[900]  = 1.0444;
  xsec_mass_H5VBS_input_lvlv[1000] = 0.77871;
  xsec_mass_H5VBS_input_lvlv[1500] = 0.20875;
  xsec_mass_H5VBS_input_lvlv[2000] = 0.064423;
  xsec_mass_H5VBS_input_lvlv[3000] = 0.0274;

  // Number of bins
  int iGM = 21;

  TString thStringGM = "#sigma^{H^{#pm#pm}}_{GM}, s_{H} = 1";

  ///////////////////////////////
  //// Limit from actual input //
  ///////////////////////////////

  int len1 = 21;

  float *mwp = new float[len1+1];
  float *med = new float[len1+1];
  float *obs = new float[len1+1];

  float *mwp_sigma = new float[2*len1+1];
  float *med1s = new float[2*len1+1];
  float *med2s = new float[2*len1+1];
  TString folder_identifier;
  TString filename;
  if (dobdtfit == 1)
  {
    folder_identifier = "ssWW_bdt_m";
  }
  else{
    folder_identifier = "ssWW_cut_m";
  }
  // std::cout << dobdtfit << std::endl;
  // std::cout << folder_identifier << std::endl;
  // TString folder_identifier = "ssWW_cut_m";
  // std::cout << folder_identifier << std::endl;

  if (doAsimov){
    filename = "myLimit_BLIND_CL95.root";
  }
  else{
    filename = "myLimit_CL95.root";
  }
  // TString filename = "myLimit_BLIND_CL95.root";
  // Loop over TRExFitter output results
  for (unsigned int ipt=1; ipt<=len1; ipt++){

    int mass = thMassGM[ipt-1];

    histo.str("");
    // Preliminar
    //histo << "../../ssWWAnalysis_TRexFitter/ssWW_chargedH/RESULTS_talk_220801_preliminar/Anal_ssWW_interpretation_m" << mass << "/Limits/asymptotics/myLimit_BLIND_CL95.root";
    // Final
    //histo << "../../ssWWAnalysis_TRexFitter/ssWW_chargedH/RESULTS_talk_221005_final/Anal_ssWW_interpretation_m" << mass << "/Limits/asymptotics/myLimit_BLIND_CL95.root";
    // Final - unblinded
    histo << path << "/" << folder_identifier << mass << "/Limits/asymptotics/" << filename;

    TFile* f1 = new TFile(histo.str().c_str());
    TTree* t1 = (TTree*)f1->Get("stats");

    int len0 = t1->GetEntries();
    cout << "\n MassPoint " << mass << "; entries: " << len0 << endl;

    float exp_upperlimit, obs_upperlimit;
    float exp_upperlimit_plus1, exp_upperlimit_minus1;
    float exp_upperlimit_plus2, exp_upperlimit_minus2;
    t1->SetBranchAddress("exp_upperlimit",&exp_upperlimit);
    t1->SetBranchAddress("obs_upperlimit",&obs_upperlimit);
    t1->SetBranchAddress("exp_upperlimit_plus1",&exp_upperlimit_plus1);
    t1->SetBranchAddress("exp_upperlimit_minus1",&exp_upperlimit_minus1);
    t1->SetBranchAddress("exp_upperlimit_plus2",&exp_upperlimit_plus2);
    t1->SetBranchAddress("exp_upperlimit_minus2",&exp_upperlimit_minus2);

    double sigSF = 1;
    double samplesin = 1;

    ////// Reading the tree now
    t1->GetEntry(0);

    if (mass < xMin) xMin = mass;
    if (mass > xMax) xMax = mass;

    if (dosin){
      xMin = 200.1;
      xMax = 1500;
    }

    sigSF = xsec_mass_H5VBS_input_lvlv.count(mass) ? (xsec_mass_H5VBS_input_lvlv[mass] * (1./(0.10614564))) : 0;

    cout << endl;
    cout << " exp_upperlimit_minus2 = " << exp_upperlimit_minus2 << endl;
    cout << " exp_upperlimit_minus1 = " << exp_upperlimit_minus1 << endl;
    cout << " > exp_upperlimit      = " << exp_upperlimit << endl;
    cout << " exp_upperlimit_plus1  = " << exp_upperlimit_plus1 << endl;
    cout << " exp_upperlimit_plus2  = " << exp_upperlimit_plus2 << endl;

    mwp[ipt-1] = mass;

    if (dosin){

      samplesin = 0.5;
      if (mass > 800) samplesin = 0.25;

      med[ipt-1] = sqrt(exp_upperlimit) * samplesin;

      med1s[ipt-1] = sqrt(exp_upperlimit_plus1) * samplesin;
      med1s[2*len1-ipt] = sqrt(exp_upperlimit_minus1) * samplesin;

      med2s[ipt-1] = sqrt(exp_upperlimit_plus2) * samplesin;
      med2s[2*len1-ipt] = sqrt(exp_upperlimit_minus2) * samplesin;

      obs[ipt-1] = sqrt(obs_upperlimit) * samplesin;

    }else{

      // Scale the TRExFitter output ---> xsec * BR(WW->lvlv) limit

      med[ipt-1] = exp_upperlimit * sigSF;

      med1s[ipt-1] = exp_upperlimit_plus1 * sigSF;
      med1s[2*len1-ipt] = exp_upperlimit_minus1 * sigSF;

      med2s[ipt-1] = exp_upperlimit_plus2 * sigSF;
      med2s[2*len1-ipt] = exp_upperlimit_minus2 * sigSF;

      obs[ipt-1] = obs_upperlimit * sigSF;

    }
    mwp_sigma[ipt-1] = mass;
    mwp_sigma[2*len1-ipt] = mass;

    cout << endl;
    cout << " > med2s["<<2*len1-ipt<<"] = " << med2s[2*len1-ipt] << " mass-" <<mwp_sigma[2*len1-ipt] << endl;
    cout << " > med1s["<<2*len1-ipt<<"] = " << med1s[2*len1-ipt] << " mass-" <<mwp_sigma[2*len1-ipt] << endl;
    cout << " > med["<<ipt-1<<"] = " << med[ipt-1] << " mass-" <<mwp_sigma[ipt-1] << endl;
    cout << " > med1s["<<ipt-1<<"] = " << med1s[ipt-1] << " mass-" <<mwp_sigma[ipt-1] << endl;
    cout << " > med2s["<<ipt-1<<"] = " << med2s[ipt-1] << " mass-" <<mwp_sigma[ipt-1] << endl;

    //cout << "\n ipt-1 = " << ipt-1 << endl;
    //cout << " 2*len1-ipt = " << 2*len1-ipt << endl;

    if (exp_upperlimit_plus2*sigSF > yMax) yMax = exp_upperlimit_plus2*sigSF;
    if (doObs && obs_upperlimit*sigSF > yMax) yMax = obs_upperlimit*sigSF;

    if (exp_upperlimit_minus2*sigSF < yMin && exp_upperlimit_minus2>0) yMin = exp_upperlimit_minus2*sigSF;
    if (doObs && obs_upperlimit*sigSF < yMin && obs_upperlimit>0) yMin = obs_upperlimit*sigSF;

  } // Loop over TRExFitter output results

  // Fix y-axis range
  yMax = 2000;
  yMin = 2;

  if (dosin){
    yMin = 0;
    yMax = 1;
  }

  cout << endl;

  printf(" m_{H5} ");
  for(int i=0; i<len1; i++) printf("%.0f ",mwp[i]);
  printf("\n\n");
  printf(" Expected: ");
  for(int i=0; i<len1; i++) printf("%.4f ",med[i]);
  printf("\n");
  if (doObs){
    printf(" Observed: ");
    for(int i=0; i<len1; i++) printf("%.4f ",obs[i]);
    printf("\n");
  }

  // DCM: Fix the last bin (not sure we need this)
  mwp_sigma[2*len1] = mwp_sigma[0];
  med1s[2*len1] = med1s[0];
  med2s[2*len1] = med2s[0];

  TGraph* fact_obs = new TGraph(len1,mwp,obs);
  TGraph* fact_med = new TGraph(len1,mwp,med);
  TGraph* fact_med1s = new TGraph(2*len1+1,mwp_sigma,med1s);
  TGraph* fact_med2s = new TGraph(2*len1+1,mwp_sigma,med2s);

  TCanvas *c1 = new TCanvas("factor","factor");
  c1->SetLeftMargin(0.12);
  c1->SetBottomMargin(0.13);
  c1->SetTopMargin(0.03);
  c1->SetRightMargin(0.04);

  if(doGrid){
    c1->SetGridx();
    c1->SetGridy();
  }

  TH2* h1 = new TH2F("h1","Cross-Section Limit",200,xMin,xMax,100,yMin,yMax);
  h2_style(h1);
  h1->SetTitle("");
  h1->SetStats(kFALSE);

  if (dosin){
    h1->SetYTitle("sin(#theta_{H})");
  }else{
    h1->SetYTitle("#sigma #times B(H^{#pm#pm}_{5} #rightarrow WW) [fb]");
  }
  h1->SetXTitle("m_{H^{#pm#pm}_{5}} [GeV]");

  h1->Draw("");
  h1->GetXaxis()->SetTitleOffset(1.2);
  h1->SetMaximum(yMax);

  fact_med2s->SetFillColor(5);
  fact_med2s->SetLineColor(5);
  fact_med2s->SetMarkerColor(5);
  fact_med2s->Draw("F");

  fact_med1s->SetFillColor(3);
  fact_med1s->SetLineColor(3);
  fact_med1s->SetMarkerColor(3);
  //fact_med1s->SetFillStyle(3001);
  fact_med1s->Draw("F");

  if (doGrid){
    gPad->SetGrid();
    gPad->RedrawAxis("g");
  }

  TGraph* thGraphGM = new TGraph(iGM,thMassGM,thXsecGM);
  thGraphGM->SetLineColor(9);
  thGraphGM->SetLineWidth(3);
  thGraphGM->SetLineStyle(4);
  if (doGM) thGraphGM->Draw("same");

  ////// Draw phase space for which the H5 total width exceeds the 5% (10%) of m_H5, where
  ////// the model is not applicable due to perturbativity and vacuum stability requirements

  float *limit05 = new float[lenlimit];
  for (unsigned int i=0; i<lenlimit; i++){
    for (float j=0.01; j<1; j+=0.01){
      //std::cout << j*j*thWidth[i]/thMass[i]<< std::endl;
      if((j*j*(thWidth[i]/pow(thSin[i],2))/thMass[i]) > 0.05){
	limit05[i]=j;
	break;
      }
      else limit05[i] = 2.;
    }
  }

  float *limit1 = new float[lenlimit];
  for (unsigned int i=0; i<lenlimit; i++){
    for (float j=0.01; j<1; j+=0.01){
      //std::cout << j*j*thWidth[i]/thMass[i]<< std::endl;
      if ((j*j*(thWidth[i]/pow(thSin[i],2))/thMass[i]) > 0.1){
	limit1[i] = j;
	break;
      }
      else limit1[i] = 2.;
    }

    cout << " mass = " <<thMass[i]<< " limit1["<<i<<"] = " <<limit1[i]<< endl;

  }

  TGraph* shade1 = new TGraph(lenlimit, thMass, limit05);
  shade1 -> SetFillStyle(3004);
  shade1 -> SetLineWidth(2501);
  shade1 -> SetLineColor(4);
  shade1 -> SetFillColor(4);
  //if (doshade) shade1->Draw("same");

  TGraph* shade2 = new TGraph(lenlimit, thMass, limit1); // 23, massbins, limit values
  shade2 -> SetFillStyle(3005);
  shade2 -> SetLineWidth(8001);
  shade2 -> SetLineColor(1);
  shade2 -> SetFillColor(1);
  if (doshade) shade2->Draw("same");

  gPad->RedrawAxis("y");
  gPad->RedrawAxis("x");

  fact_med->SetFillColor(0);
  fact_med->SetLineColor(4);
  fact_med->SetLineWidth(3);
  fact_med->SetLineStyle(9);
  fact_med->Draw("L");

  if (doObs){
    fact_obs->SetFillColor(0);
    fact_obs->SetLineWidth(3);
    fact_obs->SetLineStyle(1);
    fact_obs->SetLineColor(1);
    fact_obs->Draw("L");
  }

  // Need only for outside world

  TLatex *tex0 = new TLatex();
  double lx = 0.16, ly = 0.9;

  tex0= new TLatex(lx,ly,"#font[70]{ATLAS} Internal");
  //  tex0= new TLatex(lx,ly,"#font[70]{ATLAS} Preliminary");
  //  tex0= new TLatex(lx,ly,"#font[72]{ATLAS}");

  tex0->SetNDC();
  tex0->SetTextSize(0.05);
  tex0->SetTextColor(1);
  tex0->SetTextFont(42);
  tex0->Draw("same");

  lx = 0.16, ly = 0.83;
  TLatex *lumi = new TLatex();
  lumi= new TLatex(lx-0.005, ly, "#sqrt{s} = 13 TeV, "+Lumi+" fb^{-1}");
  lumi->SetNDC();
  lumi->SetTextFont(42);
  lumi->SetTextSize(0.04);
  lumi->SetTextColor(1);
  lumi->Draw("same");

  // Extra label for selection region
  /*
    TLatex *nwreg = new TLatex();
    nwregion = "#bf{VBF SR}";
    if (dosin) nwreg = new TLatex(lx+0.36, ly-0.33, nwregion);
    else nwreg = new TLatex(lx, ly-0.07, nwregion);
    nwreg->SetNDC();
    nwreg->SetTextFont(42);
    nwreg->SetTextSize(0.04);
    nwreg->SetTextColor(1);
    nwreg->Draw("same");
  */

  TGraph* cl1s = (TGraph*)fact_med1s->Clone("cl1s");
  TGraph* cl2s = (TGraph*)fact_med2s->Clone("cl2s");
  cl1s->SetLineColor(1);
  cl2s->SetLineColor(1);

  TDatime myDate;
  TLatex* tex4= new TLatex(xMin*1.1,yMax*0.6,myDate.AsString());
  tex4->SetTextSize(0.04);
  tex4->SetTextColor(1);
  tex4->SetTextFont(mFont);
  //tex4->Draw();

  TLegend *leg4 = 0;
  if (doshade) leg4 = new TLegend(0.14,0.475,0.59,0.8,NULL,"brNDC");
  else leg4 = new TLegend(0.5,0.65,0.95,0.95,NULL,"brNDC");
  if (doObs) leg4->AddEntry(fact_obs,"Obs. 95% CL upper limit","l");
  leg4->AddEntry(fact_med,"Exp. 95% CL upper limit","l");
  leg4->AddEntry(cl1s,"Expected limit (#pm1#sigma)","f");
  leg4->AddEntry(cl2s,"Expected limit (#pm2#sigma)","f");
  if (doGM) leg4->AddEntry(thGraphGM,thStringGM,"l");
  //if (doshade) leg4->AddEntry(shade1, "#Gamma(H^{#pm#pm}_{5})/m(H^{#pm#pm}_{5}) > 0.05","f");
  if (doshade) leg4->AddEntry(shade2, "#Gamma(H^{#pm#pm}_{5})/m(H^{#pm#pm}_{5}) > 0.1","f");
  leg_style(leg4);
  leg4->Draw("same");

  if(doLog) c1->SetLogy();

  cout << endl;

  histo.str(""); histo << path << "/" << "limits";
  if (dosin) histo << "_sin";
  histo << ".pdf";
  c1->SaveAs( histo.str().c_str() );

  histo.str(""); histo << path << "/" << "limits";
  if (dosin) histo << "_sin";
  histo << ".root";

  TFile *fOutput = new TFile( histo.str().c_str() , "RECREATE" );
  fOutput->cd();
  fact_obs->Write( "obs" );
  fact_med->Write( "exp" );
  fOutput->Close();
  cout << " >>> Saved histograms in: " << histo.str() << endl;

  cout << endl;
  cout << " >>> C'est fini!\n" << endl;

}
