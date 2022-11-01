import data_tp
import plot_tp
import linreg_tp
import geo_tp


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


def test_data_getmaskisin():
    return data_tp.getmaskisin_tp()


def test_plot_hist():
    return plot_tp.hist_tp()


def test_plot_mapa():
    return plot_tp.mapa_tp()


def test_linreg_fitmodel():
    return linreg_tp.fitmodel_tp()


def test_linreg_loopmodel():
    return linreg_tp.loopmodels_tp()


def test_geo_convert2utm():
    return geo_tp.convert2utm_tp()


def test_geo_convert2degree():
    return geo_tp.convert2degree_tp()


def test_geo_convert_dataframe():
    return geo_tp.convert_dataframe_tp()


def test_geo_calc_dist_euclidean():
    return geo_tp.calc_dist_euclidean_tp()


def test_geo_convert2utm():
    return geo_tp.convert2utm_tp()


def test_geo_calc_dist_milepost():
    return geo_tp.calc_dist_milepost_tp()


def test_geo_calc_dist_orthogonal():
    return geo_tp.calc_dist_orthogonal_tp()


def test_geo_flat_geom():
    return geo_tp.flat_geom_tp()
