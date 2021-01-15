#!/bin/bash

dir16="/eos/uscms/store/user/cmantill/bstar_select_tau21_16/"
dir17="/eos/uscms/store/user/cmantill/bstar_select_tau21_17/"
dir18="/eos/uscms/store/user/cmantill/bstar_select_tau21_18/"

#dir16="/eos/uscms/store/user/cmantill/bstar_select_tau21_16/"
#dir17="/eos/uscms/store/user/cmantill/bstar_select_tau21_17/"
#dir18="/eos/uscms/store/user/cmantill/bstar_select_tau21_18/"

odir="/eos/uscms/store/user/cmantill/bstar_inputs/"
wp="tau32medium_default"

hadd $odir/TWpreselectionRun2_data_${wp}.root ${dir16}/*data*.root ${dir17}/*data*.root ${dir18}/*data*.root

cp ${dir16}/Presel_ttbar_bstar16.root $odir/TWpreselection16_ttbar_${wp}.root
cp ${dir17}/Presel_ttbar_bstar17.root $odir/TWpreselection17_ttbar_${wp}.root
cp ${dir18}/Presel_ttbar_bstar18.root $odir/TWpreselection18_ttbar_${wp}.root

cp ${dir17}/Presel_ttbar-semilep_bstar17.root $odir/TWpreselection17_ttbar-semilep_${wp}.root
cp ${dir18}/Presel_ttbar-semilep_bstar18.root $odir/TWpreselection18_ttbar-semilep_${wp}.root

cp ${dir16}/Presel_singletop_tW_bstar16.root $odir/TWpreselection16_singletop_tW_${wp}.root
cp ${dir17}/Presel_singletop_tW_bstar17.root $odir/TWpreselection17_singletop_tW_${wp}.root
cp ${dir18}/Presel_singletop_tW_bstar18.root $odir/TWpreselection18_singletop_tW_${wp}.root

cp ${dir16}/Presel_singletop_tWB_bstar16.root $odir/TWpreselection16_singletop_tWB_${wp}.root
cp ${dir17}/Presel_singletop_tWB_bstar17.root $odir/TWpreselection17_singletop_tWB_${wp}.root
cp ${dir18}/Presel_singletop_tWB_bstar18.root $odir/TWpreselection18_singletop_tWB_${wp}.root

for m in {1400..4200..600}
do
    cp ${dir16}/Presel_signalLH${m}_bstar16.root $odir/TWpreselection16_signalLH${m}_${wp}.root
    cp ${dir17}/Presel_signalLH${m}_bstar17.root $odir/TWpreselection17_signalLH${m}_${wp}.root
    cp ${dir18}/Presel_signalLH${m}_bstar18.root $odir/TWpreselection18_signalLH${m}_${wp}.root
done
