#include <map>
#include <string>
#include <vector>
#include "Collection.cc"

using namespace ROOT::VecOps;

/**Unwraps an integer to check for bitwise flags.
 * Checks if the bit of a number is true or false.
 * @param bit Bit to check.
 * @param number Number to check.
 * 
 * @return Bool of whether the bit in the number is 0 or 1 */
bool BitChecker(int bit, int number){
    int result = number & (1 << bit);

    if (result > 0) {return true;}
    else {return false;}
}

/**\class GenParticleObjs
 * Object that stores and manipulates the information for gen particles.
 * Stores all gen particles in the event and member functions can be used to
 * access the gen particles by index. */
class GenParticleObjs {
    private:
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

        Collection GenPartCollection; /** Struct holding maps of values */

        // RVec<float> v_pt; /**< Vector of $\fp_{T}$\f values */
        // RVec<float> v_eta; /**< Vector of $\fp_{eta}$\f values */
        // RVec<float> v_phi; /**< Vector of $\fp_{phi}$\f values */
        // RVec<float> v_m; /**< Vector of $m$\f values */
        // RVec<int> v_pdgId; /**< Vector of PDG IDs */
        // RVec<int> v_status; /**< Vector of gen particle status */
        // RVec<int> v_statusFlagsInt; /**< Vector of gen particle status flags */
        // RVec<int> v_genPartIdxMother; /**< Vector of gen particle mother indexes */

        // Settings for the "set" particle
        int index = -1;
        std::map <std::string, int> statusFlags; /**< Map of status flags for set gen particle  */
        int parentIndex; /**< Parent index  */
        std::vector <int> childIndex; /**< Vector of indices of children  */

        /**Sets the status flags for the current particle.
         * Called by \ref SetIndex. */
        void SetStatusFlags();

    public:
        /* Constructor which takes in all info from the GenPart collection in NanoAOD 
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
        GenParticleObjs( RVec<float> in_pt, 
            RVec<float> in_eta, RVec<float> in_phi, 
            RVec<float> in_m, RVec<int> in_pdgId, 
            RVec<int> in_status, RVec<int> in_statusFlags, 
            RVec<int> in_genPartIdxMother);

        ~GenParticleObjs();
        
        /**Compares set particle to a provided vector 
         * @param vect The vector to compare against the current particle. 
         * @return Map with keys "sameHemisphere" (stored as float but convert
         *         to a bool), "deltaR", "deltaM". */
        std::map <std::string, float> CompareToVector(ROOT::Math::PtEtaPhiMVector vect);

        // ************************ //
        // Physics member functions //
        // ************************ //
        /**Calculates $\f\Delta R$\f between current particle and input vector.
         * @param vect The vector to compare against the current particle. 
         * @return $\f\Delta R$\f value. */
        float DeltaR(ROOT::Math::PtEtaPhiMVector vect);

        // ******************************* //
        // Organizational member functions //
        // ******************************* //
        /**Sets the index of the lookup particle 
         * @param idx The index in the collection 
         * @return None */
        void SetIndex(int idx);   
        /**Returns the bool for the flag name provided
         * @param  flagName*/
        int GetStatusFlag(std::string flagName);
        void AddParent(int idx);
        void AddChild(int idx);
        
};

GenParticleObjs::GenParticleObjs(RVec<float> in_pt, 
                                RVec<float> in_eta, RVec<float> in_phi, 
                                RVec<float> in_m, RVec<int> in_pdgId, 
                                RVec<int> in_status, RVec<int> in_statusFlags, 
                                RVec<int> in_genPartIdxMother) {

    GenPartCollection.RVecInt = { 
        {"pdgId",in_pdgId}
        {"status",in_status},
        {"statusFlags":in_statusFlags},
        {"genPartIdxMother",in_genPartIdxMother}
    }
    GenPartCollection.RVecFloat = { 
        {"pt",in_pt}
        {"eta",in_eta},
        {"phi":in_phi},
        {"m",in_m}
    }
}

GenParticleObjs::~GenParticleObjs(){}


void GenParticleObjs::SetStatusFlags(int particleIndex){
    for (auto it = GenParticleStatusFlags.begin(); it != GenParticleStatusFlags.end(); ++it) {
        statusFlags[it->first] = BitChecker(it->second, v_statusFlagsInt[particleIndex]);
    }
}
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
