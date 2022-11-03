import locale
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def str_format(h, what, per, decimal):
    if per:
        my_str = '{:1.' + str(decimal) + 'f}%'
        return my_str.format(h * 100)
    else:
        label = what.shape[0] * h
        return '{:,.0f}'.format(int(label))


def bars_auto_label(ax, what, per=True, decimal=1, pos_above=False):
    """
    Attach a text label above each bar displaying its height
    """
    # pos is used to divide the height by two
    pos = 1 if pos_above is True else 1  # was 2, acho q está feio no meio
    aux = 0.0005 if pos_above is True else 0.005

    for p in ax.patches:
        if p.get_height() > aux:
            my_text = str_format(p.get_height(), what, per, decimal)
            ax.text(p.get_x() + p.get_width() / 2.,
                    (p.get_y() + p.get_height() / pos),
                    my_text, fontsize=14, ha='center', va='bottom', color='#434853')

    return


def adjust_xlabel(ax, b, flag_lw, flag_up):
    def format_str(val, posi):
        format_num = '%.2f' if (val < 1) and (val > 0.004) else '%d'
        return locale.format(format_num, val, posi)

    xlabels = []
    gap = b[1] - b[0]
    if gap == 1:
        for index, obj in enumerate(b):
            e = format_str(obj, 1)
            xlabels.append(e)

    else:
        for index, obj in enumerate(b):
            e = '[' + format_str(obj, 1) + ', ' \
                + format_str(b[index + 1], 1)
            if index == len(b) - 2:
                # penúltimo item
                e = e + ']'
                xlabels.append(e)
                break
            else:
                e = e + '['
                xlabels.append(e)

    pos = 1 if gap == 1 else 2
    aux = '≤ ' if gap == 1 else '<'
    if flag_lw > 0:
        xlabels[0] = aux + format_str(b[pos - 1], 1)
    if flag_up > 0:
        xlabels[-1] = '≥ ' + format_str(b[-pos], 1)

    # arbitrary delta, bins are always simetric
    # size = (b[2] - b[1]) / 2
    # plt.xticks(b[:-1] + size, np.arange(len(b) - 1))
    ax.set_xticklabels(xlabels, rotation=0, fontsize=12, color='#434853')
    return


def check_what(what):
    if isinstance(what, pd.Series):
        what = pd.DataFrame(what)
    if isinstance(what, pd.DataFrame):
        pass
    else:
        raise Exception('what must be a pd.Series or pd.DataFrame')
    what.columns = [str(w) for w in what.columns]
    what = what.copy(deep=True)
    return what


def make_bins(bins, what):
    # if bins is not a list, make it
    if not (isinstance(bins, list)):
        if isinstance(bins, range):
            bins = list(bins)
        elif isinstance(bins, int):
            # TODO user np.log maybe
            if len(what.columns) > 1:
                i, j = min(what.min()), max(what.max())
                bins = list(np.linspace(start=i, stop=j, num=bins, endpoint=True))
            else:
                s = bins
                val = what.mean()[0]
                bins = []
                for ss in range(s):
                    bins.append(ss * val)
        else:
            raise Exception('bins must be a list, range or integer')
    return bins


def clip2plot(what_df, bins, lwl, upl):
    flag_lw, flag_up = 0, 0
    if lwl < bins[0]: 
        lwl = bins[0]
    if upl > bins[-1]: 
        upl = bins[-1]

    for c in what_df:
        n = what_df.loc[what_df[c].isnull(), c]
        w = what_df.loc[what_df[c].notnull(), c]
        flag_lw = (w < lwl).sum() + flag_lw
        flag_up = (w > upl).sum() + flag_up
        w = np.clip(w, lwl, upl)
        what_df.loc[:, c] = w.append(n)

    return what_df, flag_lw, flag_up


def get_what2plot(what, bins):
    """
    For each column, put value in a given BIN and calc FREQUENCE and (%)
    :param what: dataFrame with series to plot
    :param bins: bins to segregate the data
    :return: dataFrame only with the columns to plot, i.e. PERCENTUAL
    """

    cols2plot = what.columns
    aux = 0
    for c in cols2plot:
        w = what.loc[what[c].notnull(), c]
        mask = what[c].notnull()
        what.loc[mask, 'bin_' + c] = np.digitize(w.astype('float'), bins, right=False)

        # if gap>1:
        # needs to do this...
        what['bin_' + c] = what['bin_' + c] - 1
        what.loc[what[c] == bins[-1], 'bin_' + c] = len(bins) - 1
        aux = -1

        # garantees NaN will be cut out of bins
        mask = what[c].isnull()
        what.loc[mask, 'bin_' + c] = len(bins)
        # calc percentual to plot
        what['frq_' + c] = what.groupby('bin_' + c)['bin_' + c].transform('count')
        what.loc[:, 'per_' + c] = what['frq_' + c] / len(what)

    # organize dataframe to plot
    what2plot = pd.DataFrame(data={'x_pos': list(range(0, len(bins) + aux, 1))})
    for c in cols2plot:
        df = what[['bin_' + c, 'per_' + c]].drop_duplicates()
        df['bin_' + c] = df['bin_' + c].apply(lambda x: x - 1 if x > what2plot.shape[0] - 1 else x)
        what2plot = what2plot.merge(df, left_on='x_pos', right_on='bin_' + c, how='left').fillna(0)
    return what2plot


def redef_cols(what, cols_ref, legenda_txt):
    if (legenda_txt is None) & (len(cols_ref) == 1):
        legenda_bool = False
    else:
        legenda_bool = True

    if legenda_bool:
        if legenda_txt is None:
            legenda_txt = cols_ref
        cols2plot = ['per_' + c for c in cols_ref]
        what = what.rename(columns={cols2plot[0]: legenda_txt})
        cols2plot = legenda_txt
    else:
        cols2plot = ['per_' + c for c in cols_ref]

    return what[cols2plot], legenda_bool


def get_null_stat(what, legenda):
    stat = pd.DataFrame([what.isnull().sum() / len(what), what.notnull().sum() / len(what)])
    if legenda is None: 
        legenda = stat.columns
    stat = stat.rename(columns={stat.columns[0]: legenda})
    stat = stat.T
    stat.columns = ['Ignorados', 'Analisados']
    return stat


def create_figure(title, subtitle, report_nan, source, comentario):
    flatui = ["#C3423F", "#9BC53D", "#fdbf11", "#FDE74C", "#5BC0EB", "#404E4D"]
    sns.set_palette(flatui)
    subtitle = subtitle.capitalize()
    fig = plt.figure(figsize=(14, 7))
    fig.text(0.095, 0.95, title, fontsize=20, **{'fontname': 'Lato'})
    fig.text(0.095, 0.9, subtitle, fontsize=14, **{'fontname': 'Lato'})
    if source != '':
        fig.text(0.095, 0.030, "Fonte: ", weight='bold', fontsize=12, **{'fontname': 'Lato'})
        fig.text(0.145, 0.030, f"{source}", fontsize=12, **{'fontname': 'Lato'})
    else:
        pass
    if comentario != '':
        fig.text(0.095, 0, f"{comentario}", fontsize=12, **{'fontname': 'Lato'})
    else:
        pass

    # config grid and axis
    sns.set_style("whitegrid")

    if report_nan:
        grid_size = (1, 10)
        ax1 = plt.subplot2grid(grid_size, (0, 1), colspan=9)  # plot what
        ax2 = plt.subplot2grid(grid_size, (0, 0), colspan=1)  # plot stat

        ax1.xaxis.grid(False)
        ax2.xaxis.grid(False)
    else:
        ax1 = fig.subplots()  # plot what
        ax1.xaxis.grid(False)
        ax2 = None

    # ax1.axis('off')
    # ax2.axis('off')
    sns.despine(left='False')
    # for item in [fig, ax1, ax2]:
    #    item.patch.set_visible(False)

    return fig, ax1, ax2


def hide_grid(ax):
    ax.yaxis.grid(False)  # horizontal lines
    ax.xaxis.grid(False)  # vertical lines
    ax.set_yticks([])  # to erase y labels
    return
