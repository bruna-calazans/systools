# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:11:32 2022

@author: bcalazans
"""
import os
import webbrowser


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


def gera_doc_html(list2plot):
    '''
    Dado uma lista de items, gera uma super string formatada em HTML
    
    list2plot : LIST or DICT
        Lista de elementos para salvar no HTML.
        Esses elementos podem ser:
            * uma string já formatada HTML (use a função text2html para isso)
            * uma figura do plotly em HTML
            * uma figura do matplotlib : rasteriza automaticamente para html
            * uma lista com duas posições de figuras HTML que serão salvas lado a lado
    '''
    html_str_complete = '<!DOCTYPE html><html><div>'
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
             
            html_string = '<div>' + str1 + str2 + '</div>'
        else:
            # é uma figura do plotly, passar para texto html
            html_string = fig.to_html(full_html=False, include_plotlyjs='cdn')
            #html_string = html_string.replace('width:100%','width: 80%, align="center"')
        html_str_complete = html_str_complete + html_string 
    html_str_complete + '</div></html>'      
    
    return html_str_complete


def save_html(path, name, list2plot):
    '''
    Salva um HTML com os elementos de list2plot
        
    Parameters
    ----------
    path : STRING
        Caminho onde salvar o arquivo
    name : STRING
        Nome com extensão .html para salvar o arquivo
     
    list2plot: LIST ou DICT
        Caso receba um DICT, cria um HTML com abas em que cada KEY é uma aba.
        {nome_aba:[item1, item2, [item3, item4]]}
        Lista de elementos para salvar no HTML.
        Esses elementos podem ser:
            * uma string já formatada HTML (use a função text2html para isso)
            * uma figura do plotly em HTML
            * uma figura do matplotlib : rasteriza automaticamente para html
            * uma lista com duas posições de figuras HTML que serão salvas lado a lado

    Returns
    -------
    None

    '''
    
    
    html_str= ''
    if isinstance(list2plot, list): 
        html_str = gera_doc_html(list2plot)
    elif isinstance(list2plot, dict):
        html_str+=html_header
        i=0
        for key, items in list2plot.items():
            i+=1
            # html string que define as abas
            html_aba = f'''
            <li>
            <input type="radio" name="tabs" class="rd_tabs" id="tab{i}" checked>
            <label for="tab{i}">{key}</label>
            <div class="content">
            <article>
            '''
            html_str+=html_aba
            # gera string com todos os gráficos            
            html_str+=gera_doc_html(items)
            # fecha divisória das abas
            html_str+='</article></li>'
            #html_str+='</article></div></li>'
        html_str+='</ul></nav></body></html>'
    else:
        raise Exception('list2plot must be a LIST or a DICT where the items are lists')
        
    # open file and write the HTML string        
    filename = os.path.join(path, name)
    with open(filename, 'w') as file:
        file.write(html_str)

    return         
  
    
def open_html(path, name):
    filename = "file:///" + os.path.join(path, name)
    try: webbrowser.open_new_tab(filename)
    except: print (f'ERROR trying to open {name:}')
    return  


html_header = '''
<!DOCTYPE html>
<html>
<head>
<title>Modelos de Regressão</title>
<style>
*{
padding: 0;
}
body{
background-color: #fff;
font-family: Arial;
}
.nav_tabs{
margin: 5px auto;
background-color: #fff;
position: relative;
}
.nav_tabs ul{
list-style: none;
}
.nav_tabs ul li{
float: left;
height: 320px;
width: 165px;
}
.nav_tabs label{
width: 120px;
height: 25px;
padding: 20px;
border-radius: 8px 8px 0 0;
background-color: #363b48;
display: block;
color: #fff;
cursor: pointer;
text-align: center;
}
.rd_tabs:checked ~ label{
background-color: #e54e43;
}
.rd_tabs{
display: none;
}
.content{
border-top: 5px solid #e54e43;
background-color: #fff;
display: none;
position: absolute;
width: 1000px;
left: 0;
}
.rd_tabs:checked ~ .content{
display: block;
}

</style>
</head>
<body>

  <nav class="nav_tabs">
      <ul>
         '''
