# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:11:32 2022

@author: bcalazans
"""
def text2html(title=False, subtitle=False, text=[]):
    '''
    Transforma strings de texto para formato em HTML

    Parameters
    ----------
    title : STRING, optional
        Texto a ser formatado como título. The default is False.
    subtitle : STRING, optional
        Texto a ser formatado como subtítulo. The default is False.
    text : STRING ou lista de STRINGS, optional
        Textos padrão. Força uma nova linha a cada item da lista. 
        The default is [].

    Returns
    -------
    HTML string
        String de texto contendo os parâmetros passados formatados para HTML.

    '''
    if not isinstance(text, list): text = [text]
    
    html = '<div>'
    if title: html = html + '<h1>'+title + '</h1>'
    if subtitle: html = html + '<h2>'+subtitle + '</h2>'
    # each member list is a new line
    #text = [t +'<br>' for t in text]
    html = html + '<p style="color:#1F1321;font-size:20px;">'+ '<br>'.join(text) + '</p>'  
 
    return html + '</div>'


def save_html(name, list2plot):
    '''
    Salva um HTML com os elementos de list2plot
        
    Parameters
    ----------
    name : STRING
        Caminho e nome completo do arquivo para salvar.
    list2plot : LIST or DICT
        Lista de elementos para salvar no HTML.
        Esses elementos podem ser:
            * uma string já formatada HTML
            * uma figura do plotly em HTML
            * uma figura do matplotlib : rasteriza automaticamente para html
            * uma lista com duas posições de figuras HTML que serão salvas lado a lado
        Caso receba um DICT, cria um HTML com abas em que cada KEY é uma aba.

    Returns
    -------
    None

    '''
    # TODO padronizar para receber o nome separado (path, name)
    # TODO mudar código para poder receber DICT e criar as abas
    html_str_complete = ''
    with open(name, 'w') as file:
        file.write(
             '''
             <!DOCTYPE html>
              <html>
              <div>''')

        for fig in list2plot:
            if isinstance(fig, str):
                # já é um texto
                html_string = fig
            elif isinstance(fig, list): 
                # list of two figures to put side by side in a simple way
                str1= fig[0].to_html(full_html=False, include_plotlyjs='cdn')
                str1 = str1.replace('<div>', '<div style="width: 45%; float:left">')
                
                str2= fig[1].to_html(full_html=False, include_plotlyjs='cdn')
                str2 = str2.replace('<div>', '<div style="width: 45%; float:right">')
                
                html_string = '<div>' + str1 + str2 + '</div'
            else: 
                # é uma figura do plotly, passar para texto html
                html_string = fig.to_html(full_html=False, include_plotlyjs='cdn')
            #html_string = html_string.replace('width:100%','width: 80%, align="center"')
            file.write(html_string)
            html_str_complete = html_str_complete + html_string 
        file.write('</div></html>')   
    return      
  
    
  