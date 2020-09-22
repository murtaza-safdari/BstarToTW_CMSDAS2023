#include <map>
#include <string>
#include <vector>
#include <algorithm>
#include <numeric>
#include <math.h>
#include <cstdlib>
#include "Collection.cc"
#include "Pythonic.h"

using namespace ROOT::VecOps;

/**Unwraps an integer to check for bitwise flags.
 * Checks if the bit of a number is true or false.
 * @param bit Bit to check.
 * @param number Number to check.
 * 
 * @return Bool of whether the bit in the number is 0 or 1 */
bool BitChecker(const int &bit, int &number){
    int result = number & (1 << bit);

    if (result > 0) {return true;}
    else {return false;}
}

/** Stores identifying features of a particle in the GenPart collection */
class Particle {
    public:
        bool flag; /**< Should always be true unless we need to return a None-like particle */
        int index; /**< Index in collection */
        int* pdgId; /**< PDG ID of particle */
        int* status; /**< Pythia status of particle */
        std::map <std::string, int> statusFlags; /**< Map of status flags for set gen particle  */
        int parentIndex; /**< Parent index  */
        std::vector<int> childIndex; /**< Children indices */
        ROOT::Math::PtEtaPhiMVector vect; /**< Lorentz vector */
        Particle(){};
        void AddParent(int idx){
            parentIndex = idx;
        }
        void AddChild(int idx){
            childIndex.push_back(idx);
        }
};

/**Map of the PDG ID values to the particle names.
 * used for plotting decay structure. */
static const std::map <int, std::string> PDGIds {
    {1,"d"}, {2,"u"}, {3,"s"}, {4,"c"}, {5,"b"}, {6,"t"},
    {11,"e"}, {12,"nu_e"}, {13,"mu"}, {14,"nu_mu"},{ 15,"tau"},
    {16,"nu_tau"}, {21,"g"}, {22,"photon"}, {23,"Z"}, {24,"W"}, {25,"h"}
};

/**Converts flag name to the corresponding bit in the
 * value for statusFlags branch. */
static const std::map <std::string, int> GenParticleStatusFlags {
        {"isPrompt", 0},
        {"isDecayedLeptonHadron", 1},
        {"isTauDecayProduct", 2},
        {"isPromptTauDecayProduct", 3},
        {"isDirectTauDecayProduct", 4},
        {"isDirectPromptTauDecayProduct", 5},
        {"isDirectHadronDecayProduct", 6},
        {"isHardProcess", 7},
        {"fromHardProcess", 8},
        {"isHardProcessTauDecayProduct", 9},
        {"isDirectHardProcessTauDecayProduct", 10},
        {"fromHardProcessBeforeFSR", 11},
        {"isFirstCopy", 12},
        {"isLastCopy", 13},
        {"isLastCopyBeforeFSR", 14}
};

/**\class GenParticleTree
 * Constructs tree by adding particles. Establish relationships
 * between particles (parent, child) and allows you to search
 * for a chain of decays. */
class GenParticleTree
{
    private:
        Collection GenParts;
        std::vector<Particle*> nodes;
        std::vector<Particle*> heads;

        bool MatchParticleToString(Particle* particle, std::string string);
        std::vector<Particle*> RunChain(Particle* node, std::vector<std::string> chain);

        std::vector<int> StoredIndexes();
        Particle NoneParticle;

    public:
        GenParticleTree(Collection GPOColl){
            GenParts = GPOColl;
            NoneParticle.flag = false;
        };

        void AddParticle(Particle* particle);

        std::vector<Particle*> GetParticles() {return nodes;}
        std::vector<Particle*> GetChildren(Particle* particle);
        Particle* GetParent(Particle* particle);
        
        std::vector<std::vector<Particle*>> FindChain(std::string chainstring);
};

/**\class GenParticleObjs
 * Object that stores and manipulates the information for gen particles.
 * Stores all gen particles in the event and member functions can be used to
 * access the gen particles by index. */
class GenParticleObjs {
    private:
        Collection GenPartCollection; /** Struct holding maps of values */

        /**Sets the status flags for the current particle.
         * Called by \ref SetIndex. */
        void SetStatusFlags(int particleIndex);

    public:
        GenParticleObjs(RVec<float> in_pt, 
                        RVec<float> in_eta, RVec<float> in_phi, 
                        RVec<float> in_m, RVec<int> in_pdgId, 
                        RVec<int> in_status, RVec<int> in_statusFlags, 
                        RVec<int> in_genPartIdxMother);

        GenParticleObjs(Collection genParts);   

        Particle particle;

        float DeltaR(ROOT::Math::PtEtaPhiMVector vect);
        std::map< std::string, bool> CompareToVector(ROOT::Math::PtEtaPhiMVector vect);

        Particle SetIndex(int idx);   

        int GetStatusFlag(std::string flagName);
        GenParticleTree BuildTree();
};