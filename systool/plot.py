import systool.helpers.charts as ch


def hist(what, bins=5, lwl=float('-inf'), upl=float('inf'),
         legenda=None, xlabel=None, subtitle='', title='', report_nan=True,
         comentario='', source='', legend_control='%V'):

    """
    Plot a cute histogram based on the source data the user provide.

        Parameters
        ----------
        what: DataFrame or Series
            The data that the user want to be the histogram base.
        bins: integer
            Integer number that represent the number of requisited
            bins that the user want to be in the histogram.
        lwl: float
            Float number to represent the lower limit.
        upl: float
            Float number to represent the upper limit.
        legenda: str
            String value that represents the title of the plot
            legend.
        xlabel: str
            String value responsible for the xlabel title.
        subtitle: str
            String value responsible for the graph subtitle.
        title: str
            String value responsible for the graph title.
        report_nan: bool
            Boolean value responsible to represent if the user
            want or not the column reporting the number of NaN
            values.
        comentario: str
            String value responsible to plot a comment it the bottom
            of the graph.
        source: str
            String value that indicates the source of the data.
        legend_control: str
            String value that indicates the type of graph axis and
            labels displayed.
            V - For just values.
            % - For just percentages.
            V% - For values as labels and percentages as axis.
            %V - For percentages as labels and values as axis.

        Returns
        -------

        fig : Matplotlib figure type.
            Figure containing the results os the histogram plot.

        """

    source = source

    what = ch.check_what(what)
    what_ticks = what.copy()

    fig, ax1, ax2 = ch.create_figure(str(title), str(subtitle), report_nan, source=source, comentario=comentario)

    cols_ref = list(what.columns)
    what, flag_lw, flag_up = ch.clip2plot(what, ch.make_bins(bins, what), lwl, upl)
    bins = ch.make_bins(bins, what)

    stat = ch.get_null_stat(what, legenda)
    what = ch.get_what2plot(what, bins)
    what, legenda = ch.redef_cols(what, cols_ref, legenda)

    if report_nan:
        per = True
        stat.plot.bar(stacked=True, ax=ax2, legend=True,
                      color=['#1C1C1C', '#E6E6E6'])
        ax2.set_xticklabels(stat.index, rotation=0)
        ax2.legend(bbox_to_anchor=(0.326, 1))
        ch.hide_grid(ax2)
        ch.bars_auto_label(ax2, what_ticks, per, decimal=0, pos_above=True)

    if legend_control == '%V':

        per = True

        ax1.patch.set_facecolor('none')
        ax2.patch.set_facecolor('none')
        ax_aux = ax1.twinx()

        what.plot.bar(stacked=True, ax=ax_aux, legend=legenda)
        if xlabel is not None:
            ax_aux.set_xlabel(xlabel, fontweight='bold', fontsize=14, color='#434853')
        ch.hide_grid(ax1)
        ch.bars_auto_label(ax_aux, what_ticks, per, decimal=1, pos_above=not legenda)

        ax_aux.set_ylabel('N° Ocorrências', rotation=0)
        ax_aux.yaxis.set_label_coords(1, 1.06)
        ax_aux.patch.set_facecolor('none')
        ticks = list(ax_aux.get_yticks())
        new_ticks = [tick * what_ticks.shape[0] for tick in ticks]
        ax_ticks = ax1.twinx()
        ax_ticks.set_yticks(new_ticks)

        ax_ticks.grid(color='grey', linestyle='-', linewidth=0.5)
        ax_ticks.set_zorder(ax_ticks.get_zorder() - 1)
        ax_ticks.set_yticklabels(['{:,.0f}'.format(tick) for tick in new_ticks], color='grey')
        ch.hide_grid(ax_aux)

    elif legend_control == '%':

        per = True

        what.plot.bar(stacked=True, ax=ax1, legend=legenda)
        if xlabel is not None:
            ax1.set_xlabel(xlabel, fontweight='bold', fontsize=14, color='#434853')
        ch.hide_grid(ax1)
        ch.bars_auto_label(ax1, what_ticks, per, decimal=1, pos_above=not legenda)

    elif legend_control == 'V':
        per = False
        what.plot.bar(stacked=True, ax=ax1, legend=legenda)
        if xlabel is not None:
            ax1.set_xlabel(xlabel, fontweight='bold', fontsize=14, color='#434853')
        ch.hide_grid(ax1)
        ch.bars_auto_label(ax1, what_ticks, per, decimal=1, pos_above=not legenda)

    elif legend_control == 'V%':

        per = False

        ax1.patch.set_facecolor('none')
        ax2.patch.set_facecolor('none')
        ax_aux = ax1.twinx()

        what.plot.bar(stacked=True, ax=ax_aux, legend=legenda)
        if xlabel is not None:
            ax_aux.set_xlabel(xlabel, fontweight='bold', fontsize=14, color='#434853')
        ch.hide_grid(ax1)
        ch.bars_auto_label(ax_aux, what_ticks, per, decimal=1, pos_above=not legenda)

        ax_aux.set_ylabel('N° Ocorrências', rotation=0)
        ax_aux.yaxis.set_label_coords(1, 1.06)
        ax_aux.patch.set_facecolor('none')

        ax_aux.grid(color='grey', linestyle='-', linewidth=0.5)
        ax_aux.set_zorder(ax_aux.get_zorder() - 1)
        ax_aux.set_yticklabels(['{:.2f}%'.format(tick * 100) for tick in list(ax_aux.get_yticks())], color='grey')

    if bins[1] - bins[0] == 1:
        ch.adjust_xlabel(ax1, bins[:-1], flag_lw, flag_up)
    else:
        ch.adjust_xlabel(ax1, bins, flag_lw, flag_up)
    
    return fig


def mapa():
    # TODO - Pedro colcoar aqui o código que gera mapas novo do PyPass
    # esse código deve ser enxuto, criar módulo helper *maps*
    """
    plota um mapa magicamente
   •	se passar layer de pontos, plota pontos
   •	se passar layer de área, plota áreas
   •	se passar layer de linhas, plota as linhas
   •	parâmetros para colorir as coisas indivisualmente/grupos automático
   •	pensar em como adapatar para ter mapa lado a lado tbm automaticamente
   •	Adapatar para ser feito com matplot OU plotly

    Returns
    -------
    fig: objeto do matplotlib ou plotly

    """

    return None
