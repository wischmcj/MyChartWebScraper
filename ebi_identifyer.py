

from preon.normalization import PrecisionOncologyNormalizer
from preon.drug import store_ebi_drugs, load_ebi_drugs

store_ebi_drugs("compounds.csv")
drug_names, chembl_ids = load_ebi_drugs()
normalizer = PrecisionOncologyNormalizer().fit(drug_names, chembl_ids)


def normalized_med_names(med_dose):
    return [normalizer.query(med) for med in med_dose]