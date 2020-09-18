#include <map>
#include <string>
#include <vector>
#include <math.h>
#include "Collection.cc"

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
struct Particle {
    int index; /**< Index in collection */
    int* pdgId; /**< PDG ID of particle */
    int* status; /**< Pythia status of particle */
    std::map <std::string, int> statusFlags; /**< Map of status flags for set gen particle  */
    int* parentIndex; /**< Parent index  */
    ROOT::Math::PtEtaPhiMVector vect; /**< Lorentz vector */
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

/**\class GenParticleObjs
 * Object that stores and manipulates the information for gen particles.
 * Stores all gen particles in the event and member functions can be used to
 * access the gen particles by index. */
class GenParticleObjs {
    private:
        Collection GenPartCollection; /** Struct holding maps of values */

        /**Sets the status flags for the current particle.
         * Called by \ref SetIndex. */
        void SetStatusFlags(int particleIndex){
            for (auto it = GenParticleStatusFlags.begin(); it != GenParticleStatusFlags.end(); ++it) {
                particle.statusFlags[it->first] = BitChecker(it->second, GenPartCollection.RVecInt["statusFlags"]->at(particleIndex));
            }
        }

    public:
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
        GenParticleObjs(RVec<float> in_pt, 
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
        GenParticleObjs(Collection genParts) {
            GenPartCollection = genParts;
        };

        /** Destructor */
        ~GenParticleObjs();      

        Particle particle;

        // ************************ //
        // Physics member functions //
        // ************************ //
        /**Calculates $\f\Delta R$\f between current particle and input vector.
         * @param vect The vector to compare against the current particle. 
         * @return $\f\Delta R$\f value. */
        float DeltaR(ROOT::Math::PtEtaPhiMVector vect) {
            return ROOT::Math::VectorUtil::DeltaR(particle.vect,vect);
        };

        /**Compares set particle to a provided vector 
         * @param vect The vector to compare against the current particle. 
         * @return Map with keys "sameHemisphere" (phi<pi), "deltaR" 
         * (deltaR < 0.8), "deltaM" (|delta m|/m_gen < 0.05) which 
         * all return bools. */
        std::map< std::string, bool> 
          CompareToVector(ROOT::Math::PtEtaPhiMVector vect) {
            std::map< std::string, bool> out;
            out["sameHemisphere"] = (ROOT::Math::VectorUtil::DeltaPhi(particle.vect,vect) < M_PI);
            out["deltaR"] = (DeltaR(vect) < 0.8);
            out["deltaM"] = (std::abs(vect.M() - particle.vect.M())/particle.vect.M() < 0.05);
            return out;
        };

        // ******************************* //
        // Organizational member functions //
        // ******************************* //
        /**Sets the index of the lookup particle 
         * @param idx The index in the collection 
         * @return None */
        void SetIndex(int idx) {
            particle.index = idx;
            particle.pdgId = &GenPartCollection.RVecInt["pdgId"]->at(idx);
            SetStatusFlags(idx);
            particle.parentIndex = &GenPartCollection.RVecInt["genPartIdxMother"]->at(idx);
            particle.vect.SetCoordinates(
                GenPartCollection.RVecFloat["pt"]->at(idx),
                GenPartCollection.RVecFloat["eta"]->at(idx),
                GenPartCollection.RVecFloat["phi"]->at(idx),
                GenPartCollection.RVecFloat["m"]->at(idx)
                );
        };   
        /**Returns the bool for the flag name provided
         * @param  flagName*/
        int GetStatusFlag(std::string flagName){
            return particle.statusFlags[flagName];
        };
};


/////////////////////////
/////////////////////////
// class GenParticleTree
// {
//     private:
//         std::vector nodes;
//         std::vector heads;
//     public:
//         GenMatching(/* args */);
//         ~GenMatching();

//         void AddParticle();

// };

// GenMatching::GenMatching(/* args */)
// {
// }

// GenMatching::~GenMatching()
// {
// }

// GenMatching::AddParticle(genpart) {

// }
