def cleanup(messysheet):
    messysheet = messysheet.reset_index()
    ncc = messysheet[(messysheet['timepoint_[min]'] == 'NCC')].index
    messysheet.drop(ncc, inplace=True)
    nsc = messysheet[(messysheet['timepoint_[min]'] == 'NSC')].index
    messysheet.drop(nsc, inplace=True)
    return messysheet.sort_values(by=['timepoint_[min]'])