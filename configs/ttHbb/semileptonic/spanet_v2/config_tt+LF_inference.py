from pocket_coffea.utils.configurator import Configurator
from pocket_coffea.lib.cut_definition import Cut
from pocket_coffea.lib.columns_manager import ColOut
from pocket_coffea.lib.cut_functions import get_nObj_eq, get_nObj_min, get_HLTsel, get_nBtagMin, get_nPVgood, goldenJson, eventFlags
from pocket_coffea.lib.weights.common.common import common_weights
from pocket_coffea.lib.weights.common.weights_run2_UL import SF_ele_trigger
from pocket_coffea.parameters.cuts import passthrough
from pocket_coffea.parameters.histograms import *

import configs.ttHbb.semileptonic.common.workflows.workflow_spanet as workflow
from configs.ttHbb.semileptonic.common.workflows.workflow_spanet import SpanetInferenceProcessor

import configs.ttHbb.semileptonic.common.cuts.custom_cut_functions as custom_cut_functions
import configs.ttHbb.semileptonic.common.cuts.custom_cuts as custom_cuts
from configs.ttHbb.semileptonic.common.cuts.custom_cut_functions import *
from configs.ttHbb.semileptonic.common.cuts.custom_cuts import *
from configs.ttHbb.semileptonic.common.weights.custom_weights import SF_top_pt, SF_ttlf_calib
from params.axis_settings import axis_settings

import os
localdir = os.path.dirname(os.path.abspath(__file__))

# Define SPANet model path for inference
spanet_model_path = "/pnfs/psi.ch/cms/trivcat/store/user/mmarcheg/ttHbb/models/spanet_v2/multiple_binary_classifiers_btag_LMH/spanet_output/version_epoch62/spanet.onnx"

# Loading default parameters
from pocket_coffea.parameters import defaults
default_parameters = defaults.get_default_parameters()
defaults.register_configuration_dir("config_dir", localdir+"/params")

parameters = defaults.merge_parameters_from_files(default_parameters,
                                                  f"{localdir}/params/object_preselection_semileptonic.yaml",
                                                  f"{localdir}/params/triggers.yaml",
                                                  f"{localdir}/params/lepton_scale_factors.yaml",
                                                  f"{localdir}/params/btagging.yaml",
                                                  f"{localdir}/params/btagSF_calibration.yaml",
                                                  f"{localdir}/params/ttlf_calibration.yaml",
                                                  f"{localdir}/params/plotting_style.yaml",
                                                  f"{localdir}/params/quantile_transformer.yaml",
                                                  update=True)

samples = [
           "TTToSemiLeptonic",
           ]

cfg = Configurator(
    parameters = parameters,
    datasets = {
        "jsons": [f"{localdir}/datasets/datasets_Run2_skim.json",
                  ],
        "filter" : {
            "samples": samples,
            "samples_exclude" : [],
            "year": ["2016_PreVFP",
                     "2016_PostVFP",
                     "2017",
                     "2018"
                     ] #All the years
        },
        "subsamples": {
            'TTToSemiLeptonic' : {
                'TTToSemiLeptonic_tt+LF'   : [get_genTtbarId_100_eq(0)],
                #'TTToSemiLeptonic_tt+C'    : [get_genTtbarId_100_eq([41, 42, 43, 44, 45, 46])],
                #'TTToSemiLeptonic_tt+B'    : [get_genTtbarId_100_eq([51, 52, 53, 54, 55, 56])],
            },
        }
    },

    workflow = SpanetInferenceProcessor,
    workflow_options = {"parton_jet_min_dR": 0.3,
                        "dump_columns_as_arrays_per_chunk": "root://t3dcachedb03.psi.ch:1094//pnfs/psi.ch/cms/trivcat/store/user/mmarcheg/ttHbb/ntuples/spanet_v2/output_columns_spanet_inference_transformed_tt+LF",
                        "spanet_model" : spanet_model_path
                        },
    
    skim = [get_nPVgood(1),
            eventFlags,
            goldenJson,
            get_nObj_min(4, 15., "Jet"),
            get_nBtagMin(3, 15., coll="Jet", wp="M"),
            get_HLTsel(primaryDatasets=["SingleEle", "SingleMuon"])],
    
    preselections = [semileptonic_presel],
    categories = {
        "semilep": [passthrough],
    },

    weights_classes = common_weights + [SF_ele_trigger, SF_top_pt, SF_ttlf_calib],
    weights= {
        "common": {
            "inclusive": [
                "genWeight", "lumi","XS",
                "pileup",
                "sf_ele_reco", "sf_ele_id", "sf_ele_trigger",
                "sf_mu_id", "sf_mu_iso", "sf_mu_trigger",
                "sf_btag", "sf_btag_calib",
                "sf_jet_puId", "sf_top_pt",
            ],
            "bycategory": {},
        },
        "bysample": {
            "TTToSemiLeptonic": {
                "inclusive": [
                    "sf_ttlf_calib"
                ],
            }
        },
    },
    variations = {
        "weights": {
            "common": {
                "inclusive": [],
                "bycategory": {}
            },
            "bysample": {},
        },
        "shape": {
            "common": {
                "inclusive": [],
                "bycategory": {}
            }
        }
    },
    
    variables = {
        **count_hist(name="nLeptons", coll="LeptonGood",bins=3, start=0, stop=3),
        **count_hist(name="nJets", coll="JetGood",bins=10, start=4, stop=14),
        **count_hist(name="nBJets", coll="BJetGood",bins=10, start=0, stop=10),
        **ele_hists(axis_settings=axis_settings),
        **muon_hists(axis_settings=axis_settings),
        **met_hists(coll="MET", axis_settings=axis_settings),
        **jet_hists(coll="JetGood", pos=0, axis_settings=axis_settings),
        **jet_hists(coll="JetGood", pos=1, axis_settings=axis_settings),
        **jet_hists(coll="JetGood", pos=2, axis_settings=axis_settings),
        **jet_hists(coll="JetGood", pos=3, axis_settings=axis_settings),
        **jet_hists(coll="JetGood", pos=4, axis_settings=axis_settings),
        **jet_hists(name="bjet",coll="BJetGood", pos=0, axis_settings=axis_settings),
        **jet_hists(name="bjet",coll="BJetGood", pos=1, axis_settings=axis_settings),
        **jet_hists(name="bjet",coll="BJetGood", pos=2, axis_settings=axis_settings),
        **jet_hists(name="bjet",coll="BJetGood", pos=3, axis_settings=axis_settings),
        **jet_hists(name="bjet",coll="BJetGood", pos=4, axis_settings=axis_settings),
        "jets_Ht" : HistConf(
          [Axis(coll="events", field="JetGood_Ht", bins=25, start=0, stop=2500,
                label="Jets $H_T$ [GeV]")]
        ),
        "bjets_Ht" : HistConf(
          [Axis(coll="events", field="BJetGood_Ht", bins=100, start=0, stop=2500,
                label="B-Jets $H_T$ [GeV]")]
        ),
        "lightjets_Ht" : HistConf(
          [Axis(coll="events", field="LightJetGood_Ht", bins=100, start=0, stop=2500,
                label="Light-Jets $H_T$ [GeV]")]
        ),
        "deltaRbb_min" : HistConf(
            [Axis(coll="events", field="deltaRbb_min", bins=50, start=0, stop=5,
                  label="$\Delta R_{bb}$")]
        ),
        "deltaEtabb_min" : HistConf(
            [Axis(coll="events", field="deltaEtabb_min", bins=50, start=0, stop=5,
                  label="$\Delta \eta_{bb}$")]
        ),
        "deltaPhibb_min" : HistConf(
            [Axis(coll="events", field="deltaPhibb_min", bins=50, start=0, stop=5,
                  label="$\Delta \phi_{bb}$")]
        ),
        "mbb_closest" : HistConf(
            [Axis(coll="events", field="mbb_closest", bins=50, start=0, stop=500,
                    label="$m_{bb}(min \Delta R(bb))$ [GeV]")]
        ),
        "mbb_min" : HistConf(
            [Axis(coll="events", field="mbb_min", bins=50, start=0, stop=500,
                    label="$m_{bb}^{min}$ [GeV]")]
        ),
        "mbb_max" : HistConf(
            [Axis(coll="events", field="mbb_max", bins=50, start=0, stop=500,
                    label="$m_{bb}^{max}$ [GeV]")]
        ),
        "deltaRbb_avg" : HistConf(
            [Axis(coll="events", field="deltaRbb_avg", bins=50, start=0, stop=5,
                  label="$\Delta R_{bb}^{avg}$")]
        ),
        "ptbb_closest" : HistConf(
            [Axis(coll="events", field="ptbb_closest", bins=axis_settings["jet_pt"]["bins"], start=axis_settings["jet_pt"]["start"], stop=axis_settings["jet_pt"]["stop"],
                    label="$p_{T,bb}(min \Delta R(bb))$ [GeV]")]
        ),
        "htbb_closest" : HistConf(
            [Axis(coll="events", field="htbb_closest", bins=25, start=0, stop=2500,
                    label="$H_{T,bb}(min \Delta R(bb))$ [GeV]")]
        ),
        "spanet_tthbb" : HistConf(
            [Axis(coll="spanet_output", field="tthbb", bins=50, start=0, stop=1, label="tthbb SPANet score")],
        ),
        "spanet_tthbb_transformed" : HistConf(
            [Axis(coll="spanet_output", field="tthbb_transformed", bins=50, start=0, stop=1, label="tthbb SPANet transformed score")],
        ),
        "spanet_ttbb" : HistConf(
            [Axis(coll="spanet_output", field="ttbb", bins=50, start=0, stop=1, label="ttbb SPANet score")],
        ),
        "spanet_ttcc" : HistConf(
            [Axis(coll="spanet_output", field="ttcc", bins=50, start=0, stop=1, label="ttcc SPANet score")],
        ),
        "spanet_ttlf" : HistConf(
            [Axis(coll="spanet_output", field="ttlf", bins=50, start=0, stop=1, label="ttlf SPANet score")],
        )
    },
    columns = {
        "common": {
            "inclusive": [],
            "bycategory": {
                    "semilep": [
                        ColOut(
                            "JetGood",
                            ["pt", "eta", "phi", "btagDeepFlavB", "btagDeepFlavCvL", "btagDeepFlavCvB", "btag_L", "btag_M", "btag_H"],
                            flatten=False
                        ),
                        ColOut(
                            "LeptonGood",
                            ["pt","eta","phi", "pdgId", "charge", "mvaTTH"],
                            pos_end=1,
                            flatten=False
                        ),
                        ColOut(
                            "MET",
                            ["phi","pt","significance"],
                            flatten=False
                        ),
                        ColOut(
                            "events",
                            ["JetGood_Ht", "BJetGood_Ht", "LightJetGood_Ht", "deltaRbb_min", "deltaEtabb_min", "deltaPhibb_min", "deltaRbb_avg", "ptbb_closest", "htbb_closest", "mbb_closest", "mbb_min", "mbb_max"],
                            flatten=False
                        ),
                        ColOut(
                            "spanet_output",
                            ["tthbb", "ttbb", "ttcc", "ttlf", "tthbb_transformed"],
                            flatten=False
                        )
                    ]
            }
        },
        "bysample": {
            "TTToSemiLeptonic": {
                "bycategory": {
                    "semilep": [
                        ColOut("JetGoodMatched",
                               ["pt", "eta", "phi", "btagDeepFlavB", "btagDeepFlavCvL", "btagDeepFlavCvB", "btag_L", "btag_M", "btag_H", "dRMatchedJet"],
                               flatten=False
                        ),
                    ]
                }
            }
        },
    },
)

# Registering custom functions
import cloudpickle
cloudpickle.register_pickle_by_value(workflow)
cloudpickle.register_pickle_by_value(custom_cut_functions)
cloudpickle.register_pickle_by_value(custom_cuts)
