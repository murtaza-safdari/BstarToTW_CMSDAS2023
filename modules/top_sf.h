#include "GenMatching.cc"
#include "TString.h"
#include "TFile.h"
#include "TH1F.h"

using namespace ROOT::VecOps;
using namespace std;

class TopTaggingSF {
private:
    string workpoint, histprefix, filename;
    TFile* SF_file;
    TH1F *SF_hist_nom, *SF_hist_up, *SF_hist_down;

public:
    TopTaggingSF(int year, string wp, string pruning, 
                 bool btag, bool NoMassCut);
    ~TopTaggingSF();
    vector<float> eval(ROOT::Math::PtEtaPhiMVector jet, int nGenPart,
                RVec<float> GenPart_pt, RVec<float> GenPart_eta,
                RVec<float> GenPart_phi, RVec<float> GenPart_mass,
                RVec<int> GenPart_pdgId, RVec<int> GenPart_status,
                RVec<int> GenPart_statusFlags, RVec<int> GenPart_genPartIdxMother);
};
