# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + tags=[]
import zipfile
import io
import importlib
import os

# + tags=[]
from IPython.core.interactiveshell import InteractiveShell
# pretty print all cell's output and not just the last one
InteractiveShell.ast_node_interactivity = "all"

# + tags=[]
import TexSoup as TS
#importlib.reload(TS)
# -

LOCAL_DATA_PATH = './data'


# + tags=[]
def pre_format(text):
    '''Apply some substititions to make LaTeX easier to parse'''
    source_text = (
        text
        .replace('\\}\\', '\\} \\')  # Due to escape rules \\ is equivalent to \
        .replace(')}', ') }')
        .replace(')$', ') $')
    )
    return source_text


# -

infile_path

# + tags=[]
# Discover the file list:
input_zip = '2201.00007v1.zip'
infile_path = os.path.join(LOCAL_DATA_PATH, input_zip)
if True: #False:
    with zipfile.ZipFile(infile_path, "r") as in_zip:
        files = in_zip.infolist()
        for file_info in files:
            if not '/.' in file_info.filename:
                print(file_info.filename)

# + tags=[]
main_tex = '2201.00007v1/main.tex'
with zipfile.ZipFile(infile_path, "r") as in_zip:
    with in_zip.open('2201.00007v1/main.tex') as in_tex:
        #print(in_tex.read())
        wrapped_file = io.TextIOWrapper(in_tex, newline=None, encoding='utf-8') #universal newlines
        source_text = pre_format(wrapped_file.read())
        soup = TS.TexSoup(source_text)


# + tags=[]
title = soup.find('title')
print(f"{title.name}: {title.text}")
for sec in soup.find_all('section'):
    print(f' {sec.name}: {sec.text}')
    



# + tags=[]
min_example=r"""
% Template for ICASSP-2021 paper; to be used with:
%          spconf.sty  - ICASSP/ICIP LaTeX style file, and
%          IEEEbib.bst - IEEE bibliography style file.
% --------------------------------------------------------------------------
\documentclass{article}
\usepackage{spconf,amsmath,graphicx,booktabs,multirow,float,amssymb,amsfonts}

% Example definitions.
% --------------------
\def\x{{\mathbf x}}
\def\L{{\cal L}}


\mbox{Average Improvement}=$\frac{1}{n}\sum_{i}^{n}\left(Acc_{\mathrm{CA-MKD}}^{i}-Acc_{\mathrm{EBKD}}^{i}\right) $),

$iota(p)$

%Table~\ref{table:MKD} shows the top-1 accuracy comparison on CIFAR-100. 
%We also include the results of teacher ensemble with the majority voting strategy. 
%We can find that CA-MKD surpasses all competitors cross various architectures. 
%Specifically, compared to the second best method (EBKD), CA-MKD outperforms it with 
%0.81\% average improvement
%\footnote{
%\mbox{Average Improvement}=$\frac{1}{n}\sum_{i}^{n}\left(Acc_{\mathrm{CA-MKD}}^{i}-Acc_{\mathrm{EBKD}}^{i}\right)$,
%where the accuracies of CA-MKD, 
%EBKD in the $i$-th teacher-student combination are denoted as $Acc_{\mathrm{CA-MKD}}^{i}$, $Acc_{\mathrm{EBKD}}^{i}$, respectively.},
%and achieves 1.66\% absolute accuracy improvement in the best case. 



\end{document}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
#print(min_example)
# -


