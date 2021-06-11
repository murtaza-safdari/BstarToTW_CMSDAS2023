#include "top_sf.h"
#ifndef TIMBERPATH
string TIMBERPATH = "/home/lucas/Projects/RDFanalyzer/TIMBER/TIMBER/";
#endif

#include "Math/Vector4Dfwd.h"
using LVector = ROOT::Math::PtEtaPhiMVector;

TopTaggingSF::TopTaggingSF(int year, string wp, string pruning, 
                           bool btag, bool NoMassCut) {
    if (wp == "tight") {
        workpoint = "wp3";
    } else if (wp == "medium") {
        workpoint = "wp4";
    } else if (wp == "loose") {
        workpoint = "wp5";
    } else {
        throw "Working point not supported";
    }

    string NMC_string, btag_string;
    NoMassCut ? NMC_string = "_NoMassCut" : NMC_string = "";
    btag ? btag_string = "_btag" : btag_string = "";

    filename = TIMBERPATH+"/data/OfficialSFs/20"+to_string(year)+"TopTaggingScaleFactors"+NMC_string+".root";
    histprefix = pruning+"_"+workpoint+btag_string+"/sf_";
    SF_file = TFile::Open(TString(filename));
    
}

vector<float> TopTaggingSF::eval (LVector top_vect, int nGenPart,
                RVec<float> GenPart_pt, RVec<float> GenPart_eta,
                RVec<float> GenPart_phi, RVec<float> GenPart_mass,
                RVec<int> GenPart_pdgId, RVec<int> GenPart_status,
                RVec<int> GenPart_statusFlags, RVec<int> GenPart_genPartIdxMother) {
    
    vector<float> sfs {1,1,1};

    GenParticleObjs GenParticles (GenPart_pt, GenPart_eta,
                                  GenPart_phi, GenPart_mass,
                                  GenPart_pdgId, GenPart_status,
                                  GenPart_statusFlags, GenPart_genPartIdxMother);

    GenParticleTree GPT;

    vector<Particle*> tops, Ws, quarks, prongs; // prongs are final particles we'll check
    // Build the tree and save tops, Ws, quarks
    for (int i = 0; i < nGenPart; i++) {
        GenParticles.SetIndex(i);
        Particle* this_particle = &GenParticles.particle;
        GPT.AddParticle(this_particle);
        
        int this_pdgId = *(this_particle->pdgId);

        if (abs(this_pdgId) == 6 && this_particle->DeltaR(top_vect) < 0.8) {
            tops.push_back(this_particle);
        } else if (abs(this_pdgId) == 24) {
            Ws.push_back(this_particle);
        } else if (abs(this_pdgId) >= 1 && abs(this_pdgId) <= 5) {
            quarks.push_back(this_particle);
        }
    }

    // Loop over Ws
    Particle *W, *this_W, *wChild, *wParent;
    vector<Particle*> this_W_children;
    for (int iW = 0; iW < Ws.size(); iW++) {
        W = Ws[iW];
        wParent = GPT.GetParent(W);
        if (wParent->flag != false) {
            // Make sure parent is top that's in the jet
            if (abs(*(wParent->pdgId)) == 6 && wParent->DeltaR(top_vect) < 0.8) {
                this_W = W;
                this_W_children = GPT.GetChildren(this_W);
                // Make sure the child is not just another W
                if (this_W_children.size() == 1 && this_W_children[0]->pdgId == W->pdgId) {
                    this_W = this_W_children[0];
                    this_W_children = GPT.GetChildren(this_W);
                }
                // Add children as prongs
                for (int ichild = 0; ichild < this_W_children.size(); ichild++) {
                    wChild = this_W_children[ichild];
                    int child_pdgId = *(wChild->pdgId);
                    if (abs(child_pdgId) >= 1 && abs(child_pdgId) <= 5) {
                        prongs.push_back(wChild);
                    }
                } 
            }
        }
    }
    // Get bottom quarks
    Particle *q, *bottom_parent;
    for (int iq = 0; iq < quarks.size(); iq++) {
        q = quarks[iq];
        if (abs(*(q->pdgId)) == 5) { // if bottom
            bottom_parent = GPT.GetParent(q);
            if (bottom_parent->flag != false) { // if has parent
                if (abs(*(bottom_parent->pdgId)) == 6 && bottom_parent->DeltaR(top_vect) < 0.8) { // if parent is a matched top
                    prongs.push_back(q);
                }
            }
        }
    }
    // Check how many of the prongs are merged
    int merged_particles = 0;
    if (prongs.size() != 3) return sfs;

    for (int iprong = 0; iprong < prongs.size(); iprong++) {
        if (prongs[iprong]->DeltaR(top_vect) < 0.8) {
            merged_particles++;
        }
    }

    if (merged_particles == 3) {
        SF_hist_nom = (TH1F*)SF_file->Get(TString(histprefix+"mergedTop_nominal"));
        SF_hist_up = (TH1F*)SF_file->Get(TString(histprefix+"mergedTop_up"));
        SF_hist_down = (TH1F*)SF_file->Get(TString(histprefix+"mergedTop_down"));
    } else if (merged_particles == 2) {
        SF_hist_nom = (TH1F*)SF_file->Get(TString(histprefix+"semimerged_nominal"));
        SF_hist_up = (TH1F*)SF_file->Get(TString(histprefix+"semimerged_up"));
        SF_hist_down = (TH1F*)SF_file->Get(TString(histprefix+"semimerged_down"));
    } else if (merged_particles == 1) {
        SF_hist_nom = (TH1F*)SF_file->Get(TString(histprefix+"notmerged_nominal"));
        SF_hist_up = (TH1F*)SF_file->Get(TString(histprefix+"notmerged_up"));
        SF_hist_down = (TH1F*)SF_file->Get(TString(histprefix+"notmerged_down"));
    } else {
        return sfs;
    }
    
    int sfbin_nom, sfbin_up, sfbin_down;
    if (top_vect.Pt() > 5000) {
        sfbin_nom = SF_hist_nom->GetNbinsX();
        sfbin_up = SF_hist_up->GetNbinsX();
        sfbin_down = SF_hist_down->GetNbinsX();
    } else {
        sfbin_nom = SF_hist_nom->FindFixBin(top_vect.Pt());
        sfbin_up = SF_hist_up->FindFixBin(top_vect.Pt());
        sfbin_down = SF_hist_down->FindFixBin(top_vect.Pt());
    }

    sfs[0] = SF_hist_nom->GetBinContent(sfbin_nom);
    sfs[1] = SF_hist_up->GetBinContent(sfbin_up);
    sfs[2] = SF_hist_down->GetBinContent(sfbin_down);

    return sfs;
} 