from pocket_coffea.lib.weights.weights import WeightLambda, WeightWrapper, WeightData, WeightDataMultiVariation
import numpy as np
import awkward as ak
import correctionlib

samples_top = ["TTbbSemiLeptonic", "TTToSemiLeptonic", "TTTo2L2Nu"]

SF_top_pt = WeightLambda.wrap_func(
    name="sf_top_pt",
    function=lambda params, metadata, events, size, shape_variations:
            get_sf_top_pt(events, metadata),
    has_variations=False
    )

def get_sf_top_pt(events, metadata):
    if metadata["sample"] in samples_top:
        #print("Computing top pt reweighting for sample: ", metadata["sample"])
        part = events.GenPart
        part = part[~ak.is_none(part.parent, axis=1)]
        part = part[part.hasFlags("isLastCopy")]
        part = part[abs(part.pdgId) == 6]
        part = part[ak.argsort(part.pdgId, ascending=False)]

        arg = {
            "a": 0.103,
            "b": -0.0118, 
            "c": -0.000134,
            "d": 0.973
        }
        top_weight = arg["a"] * np.exp(arg["b"] * part.pt[:,0]) + arg["c"] * part.pt[:,0] + arg["d"]
        antitop_weight = arg["a"] * np.exp(arg["b"] * part.pt[:,1]) + arg["c"] * part.pt[:,1] + arg["d"]
        weight = np.sqrt(ak.prod([top_weight, antitop_weight], axis=0))
        # for i in range(10):
            # print("Top pt: {},   Top SF: {},   AntiTop pt :  {},   AntiTop SF: {}".format(part.pt[i,0], top_weight[i], part.pt[i,1], antitop_weight[i]))
        return weight#, np.zeros(np.shape(weight)), ak.copy(weight)
    else:
        return np.ones(len(events), dtype=np.float64)

def sf_ttlf_calib(params, sample, year, njets, jetsHt):
    '''Correction to tt+LF background computed by correcting tt+LF to data minus the other backgrounds in 2D:
    njets-JetsHT bins. Each year has a different correction stored in the correctionlib format.'''
    cset = correctionlib.CorrectionSet.from_file(
        params.ttlf_calibration[year]["file"]
    )
    corr = cset[params.ttlf_calibration[year]["name"]]
    w = corr.evaluate(ak.to_numpy(njets), ak.to_numpy(jetsHt))
    return w

def sf_ttlf_calib_with_ttcc_variations(params, sample, year, njets, jetsHt, variations):
    '''Correction to tt+LF background computed by correcting tt+LF to data minus the other backgrounds in 2D:
    njets-JetsHT bins. Each year has a different correction stored in the correctionlib format.'''
    cset = correctionlib.CorrectionSet.from_file(
        params.ttlf_calibration[year]["file"]
    )
    corr = cset[params.ttlf_calibration[year]["name"]]
    output = {}
    for variation in variations:
        if variation == 'nominal':
            output[variation] = [corr.evaluate(variation, ak.to_numpy(njets), ak.to_numpy(jetsHt))]
        else:
            nominal = np.ones(ak.num(njets, axis=0))
            output[variation] = [
                nominal,
                corr.evaluate(f"{variation}Up", ak.to_numpy(njets), ak.to_numpy(jetsHt)),
                corr.evaluate(f"{variation}Down", ak.to_numpy(njets), ak.to_numpy(jetsHt)),
            ]
    return output

class SF_ttlf_calib(WeightWrapper):
    name = "sf_ttlf_calib"
    has_variations = False

    def __init__(self, params, metadata):
        super().__init__(params, metadata)
        self.jet_coll = "JetGood"

    def compute(self, events, size, shape_variation):
        jetsHt = ak.sum(events[self.jet_coll].pt, axis=1)
        out = sf_ttlf_calib(self._params,
                            sample=self._metadata["sample"],
                            year=self._metadata["year"],
                            # Assuming n*JetCollection* is defined
                            njets=events[f"n{self.jet_coll}"],
                            jetsHt=jetsHt
                            )
        return WeightData(
            name = self.name,
            nominal = out["nominal"][0]
            )

class SF_ttlf_calib_with_ttcc_variations(WeightWrapper):
    name = "sf_ttlf_calib_with_ttcc_variations"
    has_variations = True

    def __init__(self, params, metadata):
        super().__init__(params, metadata)
        self.jet_coll = "JetGood"
        self._variations = params.systematic_variations.weight_variations.ttlf_calibration[metadata["year"]]

    def compute(self, events, size, shape_variation):
        jetsHt = ak.sum(events[self.jet_coll].pt, axis=1)
        if shape_variation == "nominal":
            out = sf_ttlf_calib_with_ttcc_variations(
                                self._params,
                                sample=self._metadata["sample"],
                                year=self._metadata["year"],
                                # Assuming n*JetCollection* is defined
                                njets=events[f"n{self.jet_coll}"],
                                jetsHt=jetsHt,
                                variations=["nominal"] + self._variations
                                )
            return WeightDataMultiVariation(
                name = self.name,
                nominal = out["nominal"][0],
                variations = self._variations,
                up = [out[var][1] for var in self._variations],
                down = [out[var][2] for var in self._variations]
                )
        else:
            raise NotImplementedError("Only nominal shape variation is implemented for ttlf calibration")
