#include "GenMatching.h"
#include "Math/VectorUtil.h"

/**Calculates $\f\Delta R$\f between current particle and input vector.
 * @param vect The vector to compare against the current particle. 
 * @return $\f\Delta R$\f value. */
float Particle::DeltaR(LVector input_vector) {
    return ROOT::Math::VectorUtil::DeltaR(vect,input_vector);
};

/**Constructor which takes in all info from the GenPart collection in NanoAOD 
 * Just assigns the inputs to internal variables.
 * @param in_pt $\f p_{T} $\f
 * @param in_eta $\f \eta $\f
 * @param in_phi $\f \phi $\f
 * @param in_m $\f m $\f
 * @param in_pdgId PDG ID
 * @param in_status Pythia status
 * @param in_statusFlags Status flags
 * @param in_genPartIdxMother Mother indices
 * */
GenParticleObjs::GenParticleObjs(RVec<float> in_pt, 
                RVec<float> in_eta, RVec<float> in_phi, 
                RVec<float> in_m, RVec<int> in_pdgId, 
                RVec<int> in_status, RVec<int> in_statusFlags, 
                RVec<int> in_genPartIdxMother) {

    GenPartCollection.RVecInt = { 
        {"pdgId",&in_pdgId},
        {"status",&in_status},
        {"statusFlags",&in_statusFlags},
        {"genPartIdxMother",&in_genPartIdxMother}
    };
    GenPartCollection.RVecFloat = { 
        {"pt",&in_pt},
        {"eta",&in_eta},
        {"phi",&in_phi},
        {"m",&in_m}
    };

    // Settings for the "set" particle
    particle.index = -1;

}

/**Constructor which takes in a pre-built collection.
 * @param genParts @ref Collection object filled with GenPart branches from NanoAOD.
 */
GenParticleObjs::GenParticleObjs(Collection genParts) {
    GenPartCollection = genParts;
};

/**Sets the status flags for the current particle.
 * Called by \ref SetIndex. */
void GenParticleObjs::SetStatusFlags(int particleIndex){
    for (auto it = GenParticleStatusFlags.begin(); it != GenParticleStatusFlags.end(); ++it) {
        particle.statusFlags[it->first] = BitChecker(it->second, GenPartCollection.RVecInt["statusFlags"]->at(particleIndex));
    }
}

// ************************ //
// Physics member functions //
// ************************ //


/**Compares set particle to a provided vector 
 * @param vect The vector to compare against the current particle. 
 * @return Map with keys "sameHemisphere" (phi<pi), "deltaR" 
 * (deltaR < 0.8), "deltaM" (|delta m|/m_gen < 0.05) which 
 * all return bools. */
std::map< std::string, bool> 
    GenParticleObjs::CompareToVector(LVector vect) {
    std::map< std::string, bool> out;
    out["sameHemisphere"] = (ROOT::Math::VectorUtil::DeltaPhi(particle.vect,vect) < M_PI);
    out["deltaR"] = (particle.DeltaR(vect) < 0.8);
    out["deltaM"] = (std::abs(vect.M() - particle.vect.M())/particle.vect.M() < 0.05);
    return out;
};

// ******************************* //
// Organizational member functions //
// ******************************* //
/**Sets the index of the lookup particle 
 * @param idx The index in the collection 
 * @return None */
Particle GenParticleObjs::SetIndex(int idx) {
    particle.index = idx;
    particle.pdgId = &GenPartCollection.RVecInt["pdgId"]->at(idx);
    SetStatusFlags(idx);
    particle.parentIndex = GenPartCollection.RVecInt["genPartIdxMother"]->at(idx);
    particle.vect.SetCoordinates(
        GenPartCollection.RVecFloat["pt"]->at(idx),
        GenPartCollection.RVecFloat["eta"]->at(idx),
        GenPartCollection.RVecFloat["phi"]->at(idx),
        GenPartCollection.RVecFloat["m"]->at(idx)
        );

    return particle;
};   
/**Returns the bool for the flag name provided
 * @param  flagName*/
int GenParticleObjs::GetStatusFlag(std::string flagName){
    return particle.statusFlags[flagName];
};

//////////////////////////////////////
// GenParticleTree Member Functions //
//////////////////////////////////////
std::vector<int> GenParticleTree::StoredIndexes(){
    std::vector<int> current_idxs {};
    for (int i = 0; i < nodes.size(); i++) {
        current_idxs.push_back(nodes.at(i)->index);
    }
    return current_idxs;
}

void GenParticleTree::AddParticle(Particle* particle) {
    Particle* staged_node = particle;

    // First check if current heads don't have new parents and 
    // remove them from heads if they do
    std::vector<int> heads_to_delete {};
    for (int i = 0; i < heads.size(); i++) {
        if (heads.at(i)->parentIndex == staged_node->index) {
            heads_to_delete.push_back(i);
        }
    }
    // Need to delete indices in reverse order so as not to shift 
    // indices after a deletion
    for (int ih = heads_to_delete.size(); ih >= 0; ih--) {
        heads.erase(heads.begin()+ih);
    }
   
    // Next identify staged node has no parent (heads)
    // If no parent, no other infor we can get from this particle
    std::vector<int> indexes = StoredIndexes();
    if (FindInList(staged_node->parentIndex, indexes)) {
        heads.push_back(staged_node);
        nodes.push_back(staged_node);
    } else {
        for (int inode = 0; inode < nodes.size(); inode++) {
            if (staged_node->parentIndex == nodes[inode]->index){
                staged_node->AddParent(inode);
                nodes.at(inode)->AddChild(nodes.size());
                nodes.push_back(staged_node);
            }
        }        
    }
};

std::vector<Particle*> GenParticleTree::GetChildren(Particle* particle){
    std::vector<Particle*> children {};
    for (int i = 0; i < particle->childIndex.size(); i++) {
        children.push_back(nodes[particle->childIndex.at(i)]);
    }
    return children;
}

Particle* GenParticleTree::GetParent(Particle* particle) {
    if (nodes.size() > particle->parentIndex){
        return nodes.at(particle->parentIndex);
    } else {
        return &NoneParticle;
    }
    
}

bool GenParticleTree::MatchParticleToString(Particle* particle, std::string string){
    std::vector<int> pdgIds {}; 
    if (FindInString(":",string)) {
        int startId = std::stoi( string.substr(0,string.find(':')) );
        int stopId  = std::stoi( string.substr(1,string.find(':')) );
        pdgIds = range(startId, stopId);
    } else if (FindInString(",",string)) {
        auto splits = split(string,',');
        for (int istr = 0; istr < splits.size(); istr++) {
            pdgIds.push_back( std::stoi(splits.at(istr)) );
        }
    }

    bool out;
    if (pdgIds.size() == 0) {
        if (std::abs(*particle->pdgId) == std::stoi(string)) {
            out = true;
        } else {out = false;}
    } else {
        if (FindInList(std::abs(*particle->pdgId), pdgIds)) {
            out = true;
        } else {out = false;}
    }

    return out;
}

std::vector<Particle*> GenParticleTree::RunChain(Particle* node, std::vector<std::string> chain) {
    std::vector<Particle*> nodechain {node};
    Particle* parent = GetParent(node);
    std::vector<std::string> chain_minus_first = {chain.begin()+1,chain.end()};
    
    if (chain.size() == 0) {
        return nodechain;
    } else if (parent->flag == false) {
        nodechain.push_back(&NoneParticle);
    } else if (MatchParticleToString(parent, chain.at(0))) {
        Extend(nodechain, RunChain(parent,chain_minus_first));
    } else if (parent->pdgId == node->pdgId) {
        Extend(nodechain, RunChain(parent, chain));
    } else {
        nodechain.push_back(&NoneParticle);
    }

    return nodechain;
}

std::vector<std::vector<Particle*>> GenParticleTree::FindChain(std::string chainstring) {
    std::vector<std::string> reveresed_chain = split(chainstring,'>');
    std::reverse(reveresed_chain.begin(), reveresed_chain.end());

    std::vector<std::string> reveresed_chain_minus_first = {reveresed_chain.begin()+1,reveresed_chain.end()};

    std::vector<Particle*> chain_result;
    std::vector<std::vector<Particle*>> out;

    for (int inode = 0; inode < nodes.size(); inode++) {
        Particle* n = nodes[inode];
        if (MatchParticleToString(n, reveresed_chain.at(0))) {
            chain_result = RunChain(n,reveresed_chain_minus_first);
            bool no_NoneParticle = true;
            for (int icr = 0; icr < chain_result.size(); icr++) {
                if (chain_result[icr]->flag == false) {
                    no_NoneParticle = false;
                    break;
                }
            }
            if (no_NoneParticle) {out.push_back(chain_result);}
        } 
    }
    return out;
}