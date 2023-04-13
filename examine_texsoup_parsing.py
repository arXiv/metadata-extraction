# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# ! pip install --force-reinstall --no-deps git+https://github.com/chrisjcameron/TexSoup.git@develop
# #! pip install --editable /Users/cjc73/gits/arxiv/TexSoup/

# + tags=[]
#import zipfile
import tarfile
import io
import importlib
import os
import regex as re
import glob
import pandas as pd
# -

import pyperclip   #copy text to clipboard for inspecting

# + tags=[]
from tqdm.auto import tqdm

# + tags=[]
from IPython.core.interactiveshell import InteractiveShell
# pretty print all cell's output and not just the last one
InteractiveShell.ast_node_interactivity = "all"

# + tags=[]
import TexSoup as TS
from TexSoup.tokens import MATH_ENV_NAMES

# + tags=[]
#importlib.reload(TS)

# + tags=[]
LOCAL_DATA_PATH = './data/2201_samp/'


# + tags=[]
def pre_format(text):
    '''Apply some substititions to make LaTeX easier to parse'''
    source_text = (
        text
        .replace('\\}\\', '\\} \\')  # Due to escape rules \\ is equivalent to \
        .replace(')}', ') }')
        .replace(')$', ') $')
        #.replace(r'\left [', r'\left[ ')
        #.replace(r'\left (', r'\left( ')
        #.replace(r'\left \{', r'\left\{ ')
    )
    return source_text
    #clean_lines = []
    #for line in source_text.splitlines(False):
    #    cleanline = line.strip()
    #    if cleanline.startswith(r'\newcommand'):
    #        cleanline = r'%' + cleanline
    #    elif cleanline.startswith(r'\def'):
    #        cleanline = r'%' + cleanline
    #    clean_lines.append(cleanline)
    #return '\n'.join(clean_lines)


# + tags=[]
def find_doc_class(wrapped_file, name_match=False):
    '''Search for document class related lines in a file  and return a code to represent the type'''
    doc_class_pat = re.compile(r"^\s*\\document(?:style|class)")
    sub_doc_class = re.compile(r"^\s*\\document(?:style|class).*(?:\{standalone\}|\{subfiles\})")

    for line in wrapped_file:
        if doc_class_pat.search(line):
            if name_match:
                # we can miss if there are two or more lines with documentclass 
                # and the first one is not the one that has standalone/subfile
                if sub_doc_class.search(line):
                    return -99999
                return 1 #main_files[tf] = 1
            
    return 0 #main_files[tf] = 0


def find_main_tex_source_in_tar(tar_path, encoding='uft-8'):
    '''Identify the main Tex file in a tarfile.
    
    Args:
        tar_path: A gzipped tar archive of a directory containing tex source and support files.
    '''
    
    tex_names = set(["paper.tex", "main.tex", "ms.tex", "article.tex"])

    with tarfile.open(tar_path, 'r') as in_tar:
        tex_files = [f for f in in_tar.getnames() if f.endswith('.tex')]
        
        # got one file
        if len(tex_files) == 1:
            return tex_files[0]

        main_files = {}
        for tf in tex_files:
            has_main_name = tf in tex_names
            fp = in_tar.extractfile(tf)
            wrapped_file = io.TextIOWrapper(fp, newline=None, encoding=encoding) #universal newlines
            # does it have a doc class?
            # get the type
            main_files[tf] = find_doc_class(wrapped_file, name_match = has_main_name)
            wrapped_file.close() 
        
        # got one file with doc class
        if len(main_files) == 1:
            return(main_files.keys()[0])
        
        # account for multi-file submissions
        return(max(main_files, key=main_files.get))


# + tags=[]
def soup_from_tar(tar_path, encoding='utf-8', tolerance=0):
    tex_main = find_main_tex_source_in_tar(tar_path, encoding=encoding)
    with tarfile.open(tar_path, 'r') as in_tar:
        fp = in_tar.extractfile(tex_main)
        wrapped_file = io.TextIOWrapper(fp, newline=None, encoding=encoding) #universal newlines
        source_text = pre_format(wrapped_file.read())
        soup = TS.TexSoup(source_text, tolerance=tolerance, skip_envs=MATH_ENV_NAMES)
        return soup


# + tags=[]
def source_from_tar(tar_path, encoding='utf-8'):
    tex_main = find_main_tex_source_in_tar(tar_path, encoding=encoding)
    with tarfile.open(tar_path, 'r') as in_tar:
        fp = in_tar.extractfile(tex_main)
        wrapped_file = io.TextIOWrapper(fp, newline=None, encoding=encoding) #universal newlines
        source_text = pre_format(wrapped_file.read())
        return source_text


# -

# ## Check a file with parse errors

# + active=""
#

# + tags=[]
infile_path = "./data/2201_01_all/2201.01980v1.tar.gz" #'./data/2201_samp/2201.00048v1.tar.gz'

text = source_from_tar(infile_path)
pyperclip.copy(text)
soup = soup_from_tar(infile_path, tolerance=1)


title = soup.find('title')
if title: print(f"{title.name}: {title.text}")
for sec in soup.find_all('section'):
    print(f' {sec.name}: {sec.text}')
# -





# ## Quick check a folder of tar files

# + tags=[]
files = glob.glob(f'{LOCAL_DATA_PATH}/*.tar.gz')
files_count = len(files)
utf_count = 0
latin_count = 0 
err_files = {}

TOLERANCE = 1

with tqdm(total=files_count, desc="errors") as err_prog:
    for tar_file in tqdm(files, desc="Progress", display=True):
        # Is it unicode?
        try:
            soup = soup_from_tar(tar_file, encoding='utf-8', tolerance=TOLERANCE)
            utf_count += 1
            continue
        except EOFError as eof:
            err_files[tar_file] = type(eof)
            _ = err_prog.update(1)
            continue
        except UnicodeDecodeError as ue:
            pass
        except KeyboardInterrupt as KB_err:
            break
        except Exception as e:
            err_files[tar_file] = type(e)
            _ = err_prog.update(1)
            continue

        # Is it something else?
        try:
            soup = soup_from_tar(tar_file, encoding='latin-1', tolerance=TOLERANCE)
            latin_count += 1
            continue
        except KeyboardInterrupt as KB_err:
            break
        except Exception as e:
            err_files[tar_file] = type(e)
            _ = err_prog.update(1)
            pass


# + tags=[]
print(f"{files_count} processed, {len(err_files)} failures.")
print(f"UTF8: {utf_count}; Latin1: {latin_count}")
err_files

# + [markdown] tags=[]
# ## Scratch below here


# + tags=[]
infile_path = "./data/2201_01_all/2201.01514v1.tar.gz" #'./data/2201_samp/2201.00048v1.tar.gz'

text = source_from_tar(infile_path)
pyperclip.copy(text)
soup = soup_from_tar(infile_path)


title = soup.find('title')
if title: print(f"{title.name}: {title.text}")
for sec in soup.find_all('section'):
    print(f' {sec.name}: {sec.text}')

# + tags=[]
tar_path = "./data/2201_samp/2201.00008v2.tar.gz"
encoding = "utf-8"
with tarfile.open(tar_path, 'r') as in_tar:
    tex_files = [f for f in in_tar.getnames() if f.endswith('.tex')]

    # got one file
    if len(tex_files) == 1:
        pass #return tex_files[0]

    main_files = {}
    for tf in tex_files:
        fp = in_tar.extractfile(tf)
        wrapped_file = io.TextIOWrapper(fp, newline=None, encoding=encoding) #universal newlines
        # does it have a doc class?
        # get the type
        main_files[tf] = find_doc_class(wrapped_file)
        wrapped_file.close() 

    # got one file with doc class
    if len(main_files) == 1:
        pass #return(main_files.keys()[0])

    # account for multi-file submissions
    #return(max(main_files, key=main_files.get))

# + tags=[]
main_files

# + tags=[]
doc_class_pat = re.compile(r"^\s*\\document(?:style|class)")

with tarfile.open(tar_path, 'r', encoding='utf-8') as in_tar:
    #in_tar.getnames()
    fp = in_tar.extractfile('main.tex')
    wrapped_file = io.TextIOWrapper(fp, newline=None, encoding='utf-8') #universal newlines
    for line in wrapped_file:
        if doc_class_pat.search(line):
            print(line)
            break


# + tags=[]
next(wrapped_file)

# + tags=[]

# -





# + tags=[] active=""
# # Discover the file list:
# input_zip = '2201.00007v1.zip'
# infile_path = os.path.join(LOCAL_DATA_PATH, input_zip)
# if True: #False:
#     with zipfile.ZipFile(infile_path, "r") as in_zip:
#         files = in_zip.infolist()
#         for file_info in files:
#             if not '/.' in file_info.filename:
#                 print(file_info.filename)

# + tags=[] active=""
# main_tex = '2201.00007v1/main.tex'
# with zipfile.ZipFile(infile_path, "r") as in_zip:
#     with in_zip.open('2201.00007v1/main.tex') as in_tex:
#         #print(in_tex.read())
#         wrapped_file = io.TextIOWrapper(in_tex, newline=None, encoding='utf-8') #universal newlines
#         source_text = pre_format(wrapped_file.read())
#         soup = TS.TexSoup(source_text)


# + tags=[] active=""
# title = soup.find('title')
# print(f"{title.name}: {title.text}")
# for sec in soup.find_all('section'):
#     print(f' {sec.name}: {sec.text}')
#     
#


# + tags=[]
min_example=r"""
\documentclass{article}
\begin{document}
% \renewcommand{\shorttitle}{Avoiding Catastrophe}
\end{document}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
#print(min_example)
# + tags=[]
TS.TexSoup(r'\newcommand{\bra}[1]{\left\langle#1\right|}')


# + tags=[]
TS.TexSoup(r'\def\be{\foo{equation}}')

# + tags=[]
TS.TexSoup(r'\renewcommand{\shorttitle}{Avoiding Catastrophe}')
# -
min_example = r"\newenvironment{inlinemath}{$}{$}".strip()
TS.TexSoup(pre_format(min_example))
#print(min_example)

min_example = r"In practice, the matrix $\left [ 4 \right]\Inv\M{D}^{(1)}_n $".strip()
TS.TexSoup(pre_format(min_example))
#print(min_example)

# + tags=[]
min_example = r"In practice, the matrix $\left[ 4 \right]\Inv\M{D}^{(1)}_n $"


cats = TS.category.categorize(min_example)
tokens = list(TS.tokens.tokenize(cats))

char_codes = list(TS.category.categorize(min_example))

buf = TS.reader.Buffer(TS.tokens.tokenize(TS.category.categorize(r'\left[ 4 \right]')))
TS.reader.read_command(buf, n_required_args=-1, mode='mode:math', skip=1 )


# + tags=[]
min_example = r"$ t \in [0,1] $$ t \in [0,1] $"


cats = TS.category.categorize(min_example)
tokens = list(TS.tokens.tokenize(cats))

char_codes = list(TS.category.categorize(min_example))

with pd.option_context('display.max.columns', None, 'display.max_colwidth', 0):
    pd.DataFrame({'char':char_codes, 'code':(x.category for x in char_codes)}).transpose()
    pd.DataFrame({'tokens':tokens})

buf = TS.reader.Buffer(TS.tokens.tokenize(TS.category.categorize(min_example)))
TS.reader.read_command(buf, n_required_args=-1, mode='mode:math', skip=3, tolerance=1)

buf = TS.reader.Buffer(TS.tokens.tokenize(TS.category.categorize(min_example)))
TS.read(buf, tolerance=1)


# + tags=[]
with pd.option_context('display.max.columns', None, 'display.max_colwidth', 0):
    pd.DataFrame({'char':char_codes, 'code':(x.category for x in char_codes)}).transpose()
    pd.DataFrame({'tokens':tokens})

# + tags=[]
min_example = r"In practice, the matrix $\left [\M{D}^{(1)}_n(\M{D}^{(1)}_n)\Tra\right]\Inv\M{D}^{(1)}_n $"
print(min_example)
TS.TexSoup(pre_format(min_example))
TS.TexSoup(min_example)

# + tags=[]
min_example=r"""
\documentclass{article}
\begin{document}
% \renewcommand{\shorttitle}{Avoiding Catastrophe}
\end{document}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
#print(min_example)

# + tags=[]
min_example=r"""
\def\bean {\begin{foo}}  \def\eean {\end{foo}}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
TS.TexSoup(min_example)
print(min_example)
# + tags=[]
min_example=r"""
we {use $A=8B$ and $s=1$, then the scalar field becomes same with (\Ref{scalarfield}) and
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#TS.TexSoup(min_example)
print(min_example)
# + tags=[]
print(pre_format(min_example))
# + tags=[]
BRACKETS_DELIMITERS = {
    '(', ')', '<', '>', '[', ']', '{', '}', r'\{', r'\}', '.' '|', r'\langle',
    r'\rangle', r'\lfloor', r'\rfloor', r'\lceil', r'\rceil', r'\ulcorner',
    r'\urcorner', r'\lbrack', r'\rbrack'
}
# TODO: looks like left-right do have to match
SIZE_PREFIX = ('left', 'right', 'big', 'Big', 'bigg', 'Bigg')
PUNCTUATION_COMMANDS = {command + opt_space + bracket
                        for command in SIZE_PREFIX
                        for opt_space in {'', ' '}
                        for bracket in BRACKETS_DELIMITERS.union({'|', '.'})}
PUNCTUATION_COMMANDS
# -




# + tags=[]
min_example=r"""
\def\bean {\begin{eqnarray*}}  \def\eean {\end{eqnarray*}}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
#print(min_example)
# + tags=[]
min_example=r"""
the interval $t\in[0,1)$. 
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
#print(min_example)
# + tags=[]
min_example=r"""







\beq
[\chF,\chG\}=\{\partial\chF,\chG\}.
\eeq

derivation $\CA\mapsto [\CB,\CA]$. 







The following characterizations of UAL chains are all equivalent:
\begin{itemize}
    \item[(1)] A skew-symmetric function $\cha:\Lambda^{q+1}\ra\mfkdal$ defines an element of $C_{q}(\mfkdal) $ if $\|\cha\|_{\alpha}<\infty$ for any $\alpha \in \NN$.
    \item[(2)] A skew-symmetric function $\cha:\Lambda^{q+1}\ra\mfkdal$ defines an element of $C_{q}(\mfkdal) $ if there is a function $b(r) \in \Orf$  such that for any $j_0,...,j_q$ the observable $\cha_{j_0...j_q}$ is $b$-localized at $j_a$ for any $a \in \{0,1,...,q\}$.
    \item[(3)] $C_{q}(\mfkdal) $ is the completion of $C_q(\mfkdl) $ with respect to the norms $\|\cdot\|_{\alpha}$.
\end{itemize}
\end{lemma}





""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
min_example=r"""
\newcommand\const{\operatorname{const}}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
min_example=r"""
\newcommand{\beq}{\begin{equation}}
\newcommand{\eeq}{\end{equation}}
\newcommand{\chF}{{\mathsf f}}
\newcommand{\chG}{{\mathsf g}}
\beq  
[\chF,\chG\}=\{\partial\chF,\chG\}.
\eeq
derivation $\CA\mapsto [\CB,\CA]$. 
""".strip().replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
min_example=r"""
\[
r_p=d(p,\cdot)\colon \Gamma \to [0,\infty)|~ p \in M\}
\]
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
min_example=r"""
$\bigl[ a \bigr)$
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
min_example=r"""

$\varepsilon\in]0,\varepsilon_\star[$,  

""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
min_example=r"""
\[
i\colon [0,\infty) 
\]
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)


# + tags=[]
min_example=r"""
\newcommand\1{{\mathds 1}}
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
# !! This bug was specific to my fork
min_example=r"""
\newcommand{\linebreakand}{%
    \end{@IEEEauthorhalign}
    \hfill\mbox{}\par
    \mbox{}\hfill\begin{@IEEEauthorhalign}
    }
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
min_example=r"""
 $S \subseteq \{0\} \bigcup [1,\infty) $ if $z^*_2=1$.  
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
# two inline math envs next to eachother
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
$\rm{W_{cyc} }\geq 0$$\;\;\square$
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
\verb+$TEXMF/tex/latex/elsevier/+, %$%%%%%%%%%%%%%%%%%%%%%%%%%%%%
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
# does not handle missing optional braces around arguments
min_example=r"""
$\sqrt {\frac 3 2} >p >1$
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
&$\rm{N_{Diskbb}}$$(\times 10^4) $
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
$\frac{j+1+\epsilon}{m^{\alpha}}[$
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# -

