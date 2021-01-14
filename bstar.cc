#define _USE_MATH_DEFINES

#include <cmath>
#include <tuple>
#include "ROOT/RVec.hxx"

//using namespace analyzer;
//namespace analyzer {
/**
    Checks for jets in opposite hemispheres (of phi) that also pass a jetId. 
    Can optionally provide an index that reorders the jets if jet energy
    corrections have altered the pt ordering.
    @param jet_phi \f$\phi\f$ of each jet in the event.
    @param jet_jetId Jet ID of each jet in the event.
    @param index Alternate indexing of the jets if they need to be re-ordered
*/
RVec<int> hemispherize(RVec<float> jet_phi, RVec<int> jet_jetId, RVec<int> index = {}) {
    RVec<int> Jetsh0{};
    RVec<int> Jetsh1{};
    RVec<int> LoopIndex{}; /** Index that we actually want to loop over (ordered in real pt) */
    int nFatJets, first, second;
    std::vector<int> v(jet_phi.size());

    // Determine if a custom index has been input
    if (index.size() > 0) {
        nFatJets = index.size(); // Set nFatJets if using custom index
        LoopIndex = index; // Set loop index to custom
    } else {
        nFatJets = jet_phi.size(); // Set nFatJets if not using custom index
        std::iota (std::begin(v), std::end(v), 0);
        LoopIndex = v; // Set loop index to standard one [0,1,...n]
    }

    int highestPtIdx;
    int thisIdx;
    for (int i = 0; i < nFatJets; ++i) {
        highestPtIdx = LoopIndex[0];
        thisIdx = LoopIndex[i];

        if (abs(ROOT::VecOps::DeltaPhi(jet_phi[highestPtIdx],jet_phi[thisIdx])) > M_PI/2.0) {
            if ( (jet_jetId[thisIdx] & 1) == 0 ){
                if ( (jet_jetId[thisIdx] & 2) == 0 ) {                  
                } else {
                    Jetsh1.push_back(thisIdx);
                }
            } else {Jetsh1.push_back(thisIdx);}

        } else {
            if ( (jet_jetId[thisIdx] & 1) == 0 ){
                if ( (jet_jetId[thisIdx] & 2) == 0 ) {                  
                } else {
                    Jetsh0.push_back(thisIdx);
                }
            } else {Jetsh0.push_back(thisIdx);}
        }
    }

    if ((Jetsh0.size() < 1) || (Jetsh1.size() < 1)) {
        first = -1; second = -1;
    } else {
        first = Jetsh0[0]; second = Jetsh1[0];
    }
    
    RVec<int> jets{first,second};
    return jets;
}

int Wtag(float tau21_val, float tau21_min, float tau21_max, float mass_val, float mass_min, float mass_max) {
    if ( (tau21_min < tau21_val) && (tau21_val < tau21_max) && (mass_min < mass_val) && (mass_val < mass_max) ) {
        return 1;
    } else {return 0;}
}

int TopTag(float tau32_val, float tau32_min, float tau32_max, float subjetbtag_val, float subjetbtag_min, float subjetbtag_max, float mass_val, float mass_min, float mass_max) {
    // If mass is non-zero check for the mass cut
    if ( (tau32_min < tau32_val) && (tau32_val < tau32_max) && (subjetbtag_min < subjetbtag_val) && (subjetbtag_val < subjetbtag_max) && (mass_min < mass_val) && (mass_val < mass_max) ) {
        return 1;
    } else {return 0;}
}

int WtagDeepAK8(float deepAK8W_val, float deepAK8W_min, float deepAK8W_max, float mass_val, float mass_min, float mass_max) {
    if ( (deepAK8W_min < deepAK8W_val) && (deepAK8W_val < deepAK8W_max) && (mass_min < mass_val) && (mass_val < mass_max) ) {
      return 1;
    } else {return 0;}
}

int TopTagDeepAK8(float deepAK8top_val, float deepAK8top_min, float deepAK8top_max, float subjetbtag_val, float subjetbtag_min, float subjetbtag_max, float mass_val, float mass_min, float mass_max) {
    // If mass is non-zero check for the mass cut
    if ( (deepAK8top_min < deepAK8top_val) && (deepAK8top_val < deepAK8top_max) && (subjetbtag_min < subjetbtag_val) && (subjetbtag_val < subjetbtag_max) && (mass_min < mass_val) && (mass_val < mass_max) ) {
      return 1;
    } else {return 0;}
}

const std::tuple<RVec<int>, RVec<float>> HEMreweight(RVec<float> FatJet_phi, RVec<float> FatJet_eta, RVec<float> FatJet_pt){
    int nFatJets = FatJet_phi.size();

    RVec<float> new_pt(nFatJets);
    RVec<int> old_indices(nFatJets);

    float pt_corr;
    for (int j = 0; j < nFatJets; ++j) {
        if ((FatJet_phi[j] > -1.57 && FatJet_phi[j] < -0.87) && (FatJet_phi[j] > -2.5 && FatJet_phi[j] < -1.3)) {
            pt_corr = FatJet_pt[j]*0.8;
        } else if ((FatJet_phi[j] > -1.57 && FatJet_phi[j] < -0.87) && (FatJet_phi[j] > -3.0 && FatJet_phi[j] < -2.5)) {
            pt_corr = FatJet_pt[j]*0.65;
        } else {
            pt_corr = FatJet_pt[j];
        }
        new_pt[j] = pt_corr;
        old_indices[j] = j;
    }

    RVec<int> new_indices = Sort(old_indices, [new_pt](int i1, int i2){return new_pt[i1] > new_pt[i2];});
    return std::make_tuple(new_indices,new_pt);
}

const RVec<int> UnpackHEMpt(std::tuple<RVec<int>, RVec<float>> HEMstuff) {
    return std::get<1>(HEMstuff);
}
const RVec<int> UnpackHEMidx(std::tuple<RVec<int>, RVec<float>> HEMstuff) {
    return std::get<0>(HEMstuff);
}

