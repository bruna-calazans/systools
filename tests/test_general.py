from tests import data_tp


def test_data_dataframe2numeric():
    return data_tp.dataframe2numeric_tp()


def test_data_openfile():
    return data_tp.openfile_tp()


def test_data_savefile():
    return data_tp.savefile_tp()


def test_data_getcols():
    return data_tp.getcols_tp()


def test_data_removeduplicatessafe():
    return data_tp.removeduplicatessafe_tp()


def test_data_flattenhierarchicalcol():
    return data_tp.flattenhierarchicalcol_tp()


def test_getmaskisin():
    return data_tp.getmaskisin_tp()
