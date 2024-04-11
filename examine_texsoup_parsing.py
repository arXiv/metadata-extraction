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

# %pip install --force-reinstall --no-deps git+https://github.com/chrisjcameron/TexSoup.git@nested-math
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
import itertools as itr
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
# -

TS.__file__


# + tags=[]
#importlib.reload(TS)

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
    
    tex_names = set(["paper", "main", "ms.", "article"])

    with tarfile.open(tar_path, 'r') as in_tar:
        tex_files = [f for f in in_tar.getnames() if f.endswith('.tex')]
        
        # got one file
        if len(tex_files) == 1:
            return tex_files[0]

        main_files = {}
        for tf in tex_files:
            depth = len(tf.split('/')) - 1
            has_main_name = any(kw in tf for kw in tex_names)
            fp = in_tar.extractfile(tf)
            wrapped_file = io.TextIOWrapper(fp, newline=None, encoding=encoding) #universal newlines
            # does it have a doc class?
            # get the type
            main_files[tf] = find_doc_class(wrapped_file, name_match = has_main_name) - depth 
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


# +
swap = itr.cycle([True, False])

def find_bad(current_text_lines):
    mid = int(len(current_text_lines)/2)
    part_a = current_text_lines[0:mid]
    part_b = current_text_lines[mid:]
    if next(swap):
        part_b, part_a = part_a, part_b
    bad = ""
    try:
        soup = TS.TexSoup("\n".join(part_a), tolerance=tolerance, skip_envs=MATH_ENV_NAMES)
    except KeyboardInterrupt:
        raise
    except:
        return part_a
    try:
        soup = TS.TexSoup("\n".join(part_b), tolerance=tolerance, skip_envs=MATH_ENV_NAMES)
    except KeyboardInterrupt:
        raise
    except:
        return part_b
    return "--"
        


# + tags=[]
def find_bad_lines(tar_path, encoding='utf-8'):
    tex_main = find_main_tex_source_in_tar(tar_path, encoding=encoding)
    with tarfile.open(tar_path, 'r') as in_tar:
        fp = in_tar.extractfile(tex_main)
        wrapped_file = io.TextIOWrapper(fp, newline=None, encoding=encoding) #universal newlines
        source_text = pre_format(wrapped_file.read())
        current_text = source_text.splitlines()

    while len(current_text) > 1:
        bad_half = find_bad(current_text)
        if current_text == bad_half:
            break
        current_text = bad_half
        
    return bad_half
# -

# ## Check a file with parse errors

# + active=""
#

# + tags=[] active=""
# infile_path = "./data/2201_00_all/2201.00001v1.tar.gz" #'./data/2201_samp/2201.00048v1.tar.gz'
#
# text = source_from_tar(infile_path)
# pyperclip.copy(text)
# soup = soup_from_tar(infile_path, tolerance=1)
#
#
# title = soup.find('title')
# if title: print(f"{title.name}: {title.text}")
# for sec in soup.find_all('section'):
#     print(f' {sec.name}: {sec.text}')


# + tags=[]
LOCAL_DATA_PATH = './data/2201_01_all/'
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


# +
infile_path = "./data/2201_00_all/2201.00740v1.tar.gz" #'./data/2201_samp/2201.00048v1.tar.gz'
#infile_path = "./data/2201_01_all/2201.01050v1.tar.gz" #'./data/2201_samp/2201.00048v1.tar.gz'

text = source_from_tar(infile_path)
pyperclip.copy(text)
soup = soup_from_tar(infile_path, tolerance=1)


title = soup.find('title')
if title: print(f"{title.name}: {title.text}")
for sec in soup.find_all('section'):
    print(f' {sec.name}: {sec.text}')

# +
infile_path = "./data/2201_00_all/2201.00489v2.tar.gz" #'./data/2201_samp/2201.00048v1.tar.gz'

bad_text = find_bad_lines(infile_path)
bad_text

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
# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
$1\le k< \frac n2 $ 
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
$O(\n^{-\frac12}) $, 
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')

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
# -


# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
$$[T\tensor*[]{]}{_{\CT}^{\sp}}$$
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=0)
#print(min_example)
# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
$O(\n^{-\frac{1}{2}}) $, 
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
\usepackage{mathtools}
\DeclarePairedDelimiter\ceil{\lceil}{\rceil}

\[
c_{n+1} = m_{n} \text{ and }r_{n+1} = \ceil[\Big]{\frac{f(c_{n+1}) }{t_{n}(c_{n+1} - c_{n}) }}.
\]
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# + tags=[]
#2201.00740v1
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
\begin{equation}
\begin{aligned}[t]
[T\tensor*[]{]}{_{\CT}^{\sp}} \\
\end{aligned}
\end{equation}
 """.strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')

cats = TS.category.categorize(min_example)
tokens = list(TS.tokens.tokenize(cats))

char_codes = list(TS.category.categorize(min_example))

with pd.option_context('display.max.columns', None, 'display.max_colwidth', 0, 'display.max.rows', None):
    pd.DataFrame({'char':char_codes, 'code':(x.category for x in char_codes)}).transpose()
    pd.DataFrame({'tokens':tokens})

buf = TS.reader.Buffer(TS.tokens.tokenize(TS.category.categorize(min_example)))
TS.reader.read_command(buf, n_required_args=-1, mode='mode:math', skip=3, tolerance=1)

buf = TS.reader.Buffer(TS.tokens.tokenize(TS.category.categorize(min_example)))
TS.read(buf, tolerance=0)


# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
\rightarrow	[T\tensor*[]{]}{_{\CT}^{\sp}}
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
try:
    TS.TexSoup(pre_format(min_example), tolerance=0)
except AssertionError as e:
    print(e)
print(TS)
# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""

\begin{equation}
\[
T\tensor[]{]}{_{\CT}} &\longmapsfrom [T\tensor*[]{]}{_{\CT}^{\sp}}
\]
\end{equation} 

""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
try:
    TS.TexSoup(pre_format(min_example), tolerance=0)
except AssertionError as e:
    print(e)
#print(min_example)
# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example1=r"""
%% 
%% Copyright 2007-2019 Elsevier Ltd
%% 
%% This file is part of the 'Elsarticle Bundle'.
%% ---------------------------------------------
%% 
%% It may be distributed under the conditions of the LaTeX Project Public
%% License, either version 1.2 of this license or (at your option) any
%% later version.  The latest version of this license is in
%%    http://www.latex-project.org/lppl.txt
%% and version 1.2 or later is part of all distributions of LaTeX
%% version 1999/12/01 or later.
%% 
%% The list of all files belonging to the 'Elsarticle Bundle' is
%% given in the file `manifest.txt'.
%%
%% $Id: elsdoc.tex 160 2019-01-14 09:25:49Z rishi $
%%
\documentclass[a4paper,12pt]{article}

\usepackage[xcolor,qtwo]{rvdtx}
\usepackage{multicol}
\usepackage{color}
\usepackage{xspace}
\usepackage{pdfwidgets}
\usepackage{enumerate}

\def\ttdefault{cmtt}

\headsep4pc

\makeatletter
\def\bs{\expandafter\@gobble\string\\}
\def\lb{\expandafter\@gobble\string\{}
\def\rb{\expandafter\@gobble\string\}}
\def\@pdfauthor{C.V.Radhakrishnan}
\def\@pdftitle{elsarticle.cls -- A documentation}
\def\@pdfsubject{Document formatting with elsarticle.cls}
\def\@pdfkeywords{LaTeX, Elsevier Ltd, document class}
\def\file#1{\textsf{#1}\xspace}

%\def\LastPage{19}

\DeclareRobustCommand{\LaTeX}{L\kern-.26em%
        {\sbox\z@ T%
         \vbox to\ht\z@{\hbox{\check@mathfonts
           \fontsize\sf@size\z@
           \math@fontsfalse\selectfont
          A\,}%
         \vss}%
        }%
     \kern-.15em%
    \TeX}
\makeatother

\def\figurename{Clip}

\setcounter{tocdepth}{1}

\begin{document}

\def\testa{This is a specimen document. }
\def\testc{\testa\testa\testa\testa}
\def\testb{\testc\testc\testc\testc\testc}
\long\def\test{\testb\par\testb\par\testb\par}

\pinclude{\copy\contbox\printSq{\LastPage}}

\title{elsarticle.cls -- A better way to format your document}

\author{Elsevier Ltd}
\contact{elsarticle@stmdocs.in}

\version{3.2}
\date{\today}
\maketitle

\section{Introduction}

\file{elsarticle.cls} is a thoroughly re-written document class
for formatting \LaTeX{} submissions to Elsevier journals.
The class uses the environments and commands defined in \LaTeX{} kernel
without any change in the signature so that clashes with other
contributed \LaTeX{} packages such as \file{hyperref.sty},
\file{preview-latex.sty}, etc., will be minimal.
\file{elsarticle.cls} is primarily built upon the default
\file{article.cls}.  This class depends on the following packages
for its proper functioning:

\begin{enumerate}
\item \file{natbib.sty} for citation processing;
\item \file{geometry.sty} for margin settings;
\item \file{fleqn.clo} for left aligned equations;
\item \file{graphicx.sty} for graphics inclusion;
\item \file{txfonts.sty} optional font package, if the document is to
  be formatted with Times and compatible math fonts;
\item \file{hyperref.sty} optional packages if hyperlinking is
  required in the document;
%*%
\item \file{endfloat.sty} optional packages if floats to be placed at
 end of the PDF.
\end{enumerate}

All the above packages (except some optional packages) are part of any
standard \LaTeX{} installation. Therefore, the users need not be
bothered about downloading any extra packages.  Furthermore, users are
free to make use of \textsc{ams} math packages such as
\file{amsmath.sty}, \file{amsthm.sty}, \file{amssymb.sty},
\file{amsfonts.sty}, etc., if they want to.  All these packages work in
tandem with \file{elsarticle.cls} without any problems.

\section{Major Differences}

Following are the major differences between \file{elsarticle.cls}
and its predecessor package, \file{elsart.cls}:

\begin{enumerate}[\textbullet]
\item \file{elsarticle.cls} is built upon \file{article.cls}
while \file{elsart.cls} is not. \file{elsart.cls} redefines
many of the commands in the \LaTeX{} classes/kernel, which can
possibly cause surprising clashes with other contributed
\LaTeX{} packages;

\item provides preprint document formatting by default, and
optionally formats the document as per the final
style of models $1+$, $3+$ and $5+$ of Elsevier journals;

\item some easier ways for formatting \verb+list+ and
\verb+theorem+ environments are provided while people can still
use \file{amsthm.sty} package;

\item \file{natbib.sty} is the main citation processing package
  which can comprehensively handle all kinds of citations and
works perfectly with \file{hyperref.sty} in combination with
\file{hypernat.sty};

\item long title pages are processed correctly in preprint and
  final formats.

\end{enumerate}

\section{Installation}

The package is available at author resources page at Elsevier
(\url{http://www.elsevier.com/locate/latex}).
It can also be found in any of the nodes of the Comprehensive
\TeX{} Archive Network (\textsc{ctan}), one of the primary nodes
being
\url{http://tug.ctan.org/tex-archive/macros/latex/contrib/elsarticle/}.
Please download the \file{elsarticle.dtx} which is a composite
class with documentation and \file{elsarticle.ins} which is the
\LaTeX{} installer file. When we compile the
\file{elsarticle.ins} with \LaTeX{} it provides the class file,
\file{elsarticle.cls} by
stripping off all the documentation from the \verb+*.dtx+ file.
The class may be moved or copied to a place, usually,
\verb+$TEXMF/tex/latex/elsevier/+, %$%%%%%%%%%%%%%%%%%%%%%%%%%%%%
or a folder which will be read                   
by \LaTeX{} during document compilation.  The \TeX{} file
database needs updation after moving/copying class file.  Usually,
we use commands like \verb+mktexlsr+ or \verb+texhash+ depending
upon the distribution and operating system.


\section{Usage}\label{sec:usage}
The class should be loaded with the command:

\begin{vquote}
 \documentclass[<options>]{elsarticle}
\end{vquote}

\noindent where the \verb+options+ can be the following:


\begin{description}

\item [{\tt\color{verbcolor} preprint}]  default option which format the
  document for submission to Elsevier journals.

\item [{\tt\color{verbcolor} review}]  similar to the \verb+preprint+
option, but increases the baselineskip to facilitate easier review
process.

\item [{\tt\color{verbcolor} 1p}]  formats the article to the look and
feel of the final format of model 1+ journals. This is always single
column style.

\item [{\tt\color{verbcolor} 3p}] formats the article to the look and
feel of the final format of model 3+ journals. If the journal is a two
column model, use \verb+twocolumn+ option in combination.

\item [{\tt\color{verbcolor} 5p}] formats for model 5+ journals. This
is always of two column style.

\item [{\tt\color{verbcolor} authoryear}] author-year citation style of
\file{natbib.sty}. If you want to add extra options of
\file{natbib.sty}, you may use the options as comma delimited strings
as arguments to \verb+\biboptions+ command. An example would be:
\end{description}

\begin{vquote}
 \biboptions{longnamesfirst,angle,semicolon}
\end{vquote}

\begin{description}
\item [{\tt\color{verbcolor} number}] numbered citation style. Extra options
  can be loaded with\linebreak \verb+\biboptions+ command.

\item [{\tt\color{verbcolor} sort\&compress}] sorts and compresses the
numbered citations. For example, citation [1,2,3] will become [1--3].

\item [{\tt\color{verbcolor} longtitle}] if front matter is unusually long, use
  this option to split the title page across pages with the correct
placement of title and author footnotes in the first page.

\item [{\tt\color{verbcolor} times}] loads \file{txfonts.sty}, if
available in the system to use Times and compatible math fonts.

%*%
\item [{\tt\color{verbcolor} reversenotenum}] Use alphabets as
author--affiliation linking labels and use numbers for author
footnotes. By default, numbers will be used as author--affiliation
linking labels and alphabets for author footnotes. 

\item [{\tt\color{verbcolor} lefttitle}] To move title and
author/affiliation block to flushleft. \verb+centertitle+ is the
default option which produces center alignment.

\item [{\tt\color{verbcolor} endfloat}] To place all floats at the end
of the document.

\item [{\tt\color{verbcolor} nonatbib}] To unload natbib.sty.
%*%

\item [{\tt\color{verbcolor} doubleblind}] To hide author name, 
affiliation, email address etc. for double blind refereeing purpose.
%*%

\item[] All options of \file{article.cls} can be used with this
  document class.

\item[] The default options loaded are \verb+a4paper+, \verb+10pt+,
  \verb+oneside+, \verb+onecolumn+ and \verb+preprint+.

\end{description}

\section{Frontmatter}

There are two types of frontmatter coding:
\begin{enumerate}[(1)]
\item each author is
connected to an affiliation with a footnote marker; hence all
authors are grouped together and affiliations follow;
\pagebreak
\item authors of same affiliations are grouped together and the
relevant affiliation follows this group. 
\end{enumerate}

An example of coding the first type is provided below.

\begin{vquote}
 \title{This is a specimen title\tnoteref{t1,t2}}
 \tnotetext[t1]{This document is the results of the research
    project funded by the National Science Foundation.}
 \tnotetext[t2]{The second title footnote which is a longer 
    text matter to fill through the whole text width and 
    overflow into another line in the footnotes area of the 
    first page.}
\end{vquote}

\begin{vquote}
\author[1]{Jos Migchielsen\corref{cor1}%
  \fnref{fn1}}
\ead{J.Migchielsen@elsevier.com}

\author[2]{CV Radhakrishnan\fnref{fn2}}
\ead{cvr@sayahna.org}

\author[3]{CV Rajagopal\fnref{fn1,fn3}}
\ead[url]{www.stmdocs.in}
\end{vquote}

\begin{vquote}
 \cortext[cor1]{Corresponding author}
 \fntext[fn1]{This is the first author footnote.}
 \fntext[fn2]{Another author footnote, this is a very long 
   footnote and it should be a really long footnote. But this 
   footnote is not yet sufficiently long enough to make two 
   lines of footnote text.}
 \fntext[fn3]{Yet another author footnote.}

 \address[1]{Elsevier B.V., Radarweg 29, 1043 NX Amsterdam, 
   The Netherlands}
 \address[2]{Sayahna Foundations, JWRA 34, Jagathy, 
   Trivandrum 695014, India}
 \address[3]{STM Document Engineering Pvt Ltd., Mepukada,
   Malayinkil, Trivandrum 695571, India}
\end{vquote}

The output of the above \TeX{} source is given in Clips~\ref{clip1} and
\ref{clip2}. The header portion or title area is given in
Clip~\ref{clip1} and the footer area is given in Clip~\ref{clip2}.

\def\rulecolor{blue!70}
\src{Header of the title page.}
\includeclip{1}{130 612 477 707}{1psingleauthorgroup.pdf}%%{elstest-1p.pdf}%single author group
\def\rulecolor{orange}

\def\rulecolor{blue!70}
\src{Footer of the title page.}
\includeclip{1}{93 135 499 255}{1pseperateaug.pdf}%%{elstest-1p.pdf}%single author group
\def\rulecolor{orange}

Most of the commands such as \verb+\title+, \verb+\author+,
\verb+\address+ are self explanatory.  Various components are
linked to each other by a label--reference mechanism; for
instance, title footnote is linked to the title with a footnote
mark generated by referring to the \verb+\label+ string of
the \verb=\tnotetext=.  We have used similar commands
such as \verb=\tnoteref= (to link title note to title);
\verb=\corref= (to link corresponding author text to
corresponding author); \verb=\fnref= (to link footnote text to
the relevant author names).  \TeX{} needs two compilations to
resolve the footnote marks in the preamble part.  
Given below are the syntax of various note marks and note texts.


\begin{vquote}
  \tnoteref{<label(s)>}
  \corref{<label(s)>}
  \fnref{<label(s)>}
  \tnotetext[<label>]{<title note text>}
  \cortext[<label>]{<corresponding author note text>}
  \fntext[<label>]{<author footnote text>}
\end{vquote}

\noindent where \verb=<label(s)>= can be either one or more comma
delimited label strings. The optional arguments to the
\verb=\author= command holds the ref label(s) of the address(es)
to which the author is affiliated while each \verb=\address=
command can have an optional argument of a label. In the same
manner, \verb=\tnotetext=, \verb=\fntext=, \verb=\cortext= will
have optional arguments as their respective labels and note text
as their mandatory argument.

The following example code provides the markup of the second type
of author-affiliation.

\begin{vquote}
\author{Jos Migchielsen\corref{cor1}%
  \fnref{fn1}}
\ead{J.Migchielsen@elsevier.com}
 \address{Elsevier B.V., Radarweg 29, 1043 NX Amsterdam, 
          The Netherlands}

\author{CV Radhakrishnan\fnref{fn2}}
\ead{cvr@sayahna.org}
 \address{Sayahna Foundations, JWRA 34, Jagathy, 
    Trivandrum 695014, India}

\author{CV Rajagopal\fnref{fn1,fn3}}
\ead[url]{www.stmdocs.in}
  \address{STM Document Engineering Pvt Ltd., Mepukada,
    Malayinkil, Trivandrum 695571, India}
\end{vquote}

\vspace*{-.5pc}

\begin{vquote}
\cortext[cor1]{Corresponding author}
\fntext[fn1]{This is the first author footnote.}
\fntext[fn2]{Another author footnote, this is a very long 
  footnote and it should be a really long footnote. But this 
  footnote is not yet sufficiently long enough to make two lines 
  of footnote text.}
\end{vquote}

The output of the above \TeX{} source is given in Clip~\ref{clip3}.

\def\rulecolor{blue!70}
\src{Header of the title page..}
\includeclip{1}{119 563 468 709}{1pseperateaug.pdf}%%{elstest-1p.pdf}%seperate author groups
\def\rulecolor{orange}
\pagebreak

Clip~\ref{clip4} shows the output after giving \verb+doubleblind+ class option. 

\def\rulecolor{blue!70}
\src{Double blind article}
\includeclip{1}{124 567 477 670}{elstest-1pdoubleblind.pdf}%%{elstest-1p.pdf}%single author group%%doubleblind
\def\rulecolor{orange}

\vspace*{-.5pc}
The frontmatter part has further environments such as abstracts and
keywords.  These can be marked up in the following manner:

\begin{vquote}
 \begin{abstract}
  In this work we demonstrate the formation of a new type of 
  polariton on the interface between a ....
 \end{abstract}
\end{vquote} 

\vspace*{-.5pc}
\begin{vquote}
 \begin{keyword}
  quadruple exiton \sep polariton \sep WGM
 \end{keyword}
\end{vquote}

\noindent Each keyword shall be separated by a \verb+\sep+ command.
\textsc{msc} classifications shall be provided in 
the keyword environment with the commands
\verb+\MSC+. \verb+\MSC+ accepts an optional
argument to accommodate future revisions.
eg., \verb=\MSC[2008]=. The default is 2000.\looseness=-1

\subsection{New page}
Sometimes you may need to give a page-break and start a new page after
title, author or abstract. Following commands can be used for this
purpose.

\begin{vquote}
  \newpageafter{title}
  \newpageafter{author}
  \newpageafter{abstract}
\end{vquote}


\begin{itemize}
\leftskip-2pc
\item [] {\tt\color{verbcolor} \verb+\newpageafter{title}+} typeset the title alone on one page.

\item [] {\tt\color{verbcolor} \verb+\newpageafter{author}+}  typeset the title
and author details on one page.

\item [] {\tt\color{verbcolor} \verb+\newpageafter{abstract}+}
typeset the title,
author details and abstract \& keywords one one page.

\end{itemize}

\section{Floats}
{Figures} may be included using the command, \verb+\includegraphics+ in
combination with or without its several options to further control
graphic. \verb+\includegraphics+ is provided by \file{graphic[s,x].sty}
which is part of any standard \LaTeX{} distribution.
\file{graphicx.sty} is loaded by default. \LaTeX{} accepts figures in
the postscript format while pdf\LaTeX{} accepts \file{*.pdf},
\file{*.mps} (metapost), \file{*.jpg} and \file{*.png} formats. 
pdf\LaTeX{} does not accept graphic files in the postscript format. 

The \verb+table+ environment is handy for marking up tabular
material. If users want to use \file{multirow.sty},
\file{array.sty}, etc., to fine control/enhance the tables, they
are welcome to load any package of their choice and
\file{elsarticle.cls} will work in combination with all loaded
packages.

\section[Theorem and ...]{Theorem and theorem like environments}

\file{elsarticle.cls} provides a few shortcuts to format theorems and
theorem-like environments with ease. In all commands the options that
are used with the \verb+\newtheorem+ command will work exactly in the same
manner. \file{elsarticle.cls} provides three commands to format theorem or
theorem-like environments: 

\begin{vquote}
 \newtheorem{thm}{Theorem}
 \newtheorem{lem}[thm]{Lemma}
 \newdefinition{rmk}{Remark}
 \newproof{pf}{Proof}
 \newproof{pot}{Proof of Theorem \ref{thm2}}
\end{vquote}

The \verb+\newtheorem+ command formats a
theorem in \LaTeX's default style with italicized font, bold font
for theorem heading and theorem number at the right hand side of the
theorem heading.  It also optionally accepts an argument which
will be printed as an extra heading in parentheses. 

\begin{vquote}
  \begin{thm} 
   For system (8), consensus can be achieved with 
   $\|T_{\omega z}$
   ...
     \begin{eqnarray}\label{10}
     ....
     \end{eqnarray}
  \end{thm}
\end{vquote}  

Clip~\ref{clip5} will show you how some text enclosed between the
above code\goodbreak \noindent looks like:

\vspace*{6pt}
\def\rulecolor{blue!70}
\src{{\ttfamily\color{verbcolor}\bs newtheorem}}
\includeclip{2}{1 1 453 120}{jfigs.pdf}
\def\rulecolor{orange}

The \verb+\newdefinition+ command is the same in
all respects as its\linebreak \verb+\newtheorem+ counterpart except that
the font shape is roman instead of italic.  Both
\verb+\newdefinition+ and \verb+\newtheorem+ commands
automatically define counters for the environments defined.

\vspace*{6pt}
\def\rulecolor{blue!70}
\src{{\ttfamily\color{verbcolor}\bs newdefinition}}
\includeclip{1}{1 1 453 105}{jfigs.pdf}
\def\rulecolor{orange}

The \verb+\newproof+ command defines proof environments with
upright font shape.  No counters are defined. 

\vspace*{6pt}
\def\rulecolor{blue!70}
\src{{\ttfamily\color{verbcolor}\bs newproof}}
\includeclip{3}{1 1 453 65}{jfigs.pdf}
\def\rulecolor{orange}

Users can also make use of \verb+amsthm.sty+ which will override
all the default definitions described above.

\section[Enumerated ...]{Enumerated and Itemized Lists}
\file{elsarticle.cls} provides an extended list processing macros
which makes the usage a bit more user friendly than the default
\LaTeX{} list macros.   With an optional argument to the
\verb+\begin{enumerate}+ command, you can change the list counter
type and its attributes.

\begin{vquote}
 \begin{enumerate}[1.]
 \item The enumerate environment starts with an optional
   argument `1.', so that the item counter will be suffixed
   by a period.
 \item You can use `a)' for alphabetical counter and '(i)' for
   roman counter.
  \begin{enumerate}[a)]
    \item Another level of list with alphabetical counter.
    \item One more item before we start another.
\end{vquote}

\def\rulecolor{blue!70}
\src{List -- Enumerate}
\includeclip{4}{1 1 453 185}{jfigs.pdf}
\def\rulecolor{orange}

Further, the enhanced list environment allows one to prefix a
string like `step' to all the item numbers.  

\begin{vquote}
 \begin{enumerate}[Step 1.]
  \item This is the first step of the example list.
  \item Obviously this is the second step.
  \item The final step to wind up this example.
 \end{enumerate}
\end{vquote}

\def\rulecolor{blue!70}
\src{List -- enhanced}
\includeclip{5}{1 1 313 83}{jfigs.pdf}
\def\rulecolor{orange}


\section{Cross-references}
In electronic publications, articles may be internally
hyperlinked. Hyperlinks are generated from proper
cross-references in the article.  For example, the words
\textcolor{black!80}{Fig.~1} will never be more than simple text,
whereas the proper cross-reference \verb+\ref{tiger}+ may be
turned into a hyperlink to the figure itself:
\textcolor{blue}{Fig.~1}.  In the same way,
the words \textcolor{blue}{Ref.~[1]} will fail to turn into a
hyperlink; the proper cross-reference is \verb+\cite{Knuth96}+.
Cross-referencing is possible in \LaTeX{} for sections,
subsections, formulae, figures, tables, and literature
references.

\section[Mathematical ...]{Mathematical symbols and formulae}

Many physical/mathematical sciences authors require more
mathematical symbols than the few that are provided in standard
\LaTeX. A useful package for additional symbols is the
\file{amssymb} package, developed by the American Mathematical
Society. This package includes such oft-used symbols as
$\lesssim$ (\verb+\lesssim+), $\gtrsim$ (\verb+\gtrsim+)  or 
$\hbar$ (\verb+\hbar+). Note that your \TeX{}
system should have the \file{msam} and \file{msbm} fonts installed. If
you need only a few symbols, such as $\Box$ (\verb+\Box+), you might try the
package \file{latexsym}.

Another point which would require authors' attention is the
breaking up of long equations.  When you use
\file{elsarticle.cls} for formatting your submissions in the 
\verb+preprint+ mode, the document is formatted in single column
style with a text width of 384pt or 5.3in.  When this document is
formatted for final print and if the journal happens to be a double column
journal, the text width will be reduced to 224pt at for 3+
double column and 5+ journals respectively. All the nifty 
fine-tuning in equation breaking done by the author goes to waste in
such cases.  Therefore, authors are requested to check this
problem by typesetting their submissions in final format as well
just to see if their equations are broken at appropriate places,
by changing appropriate options in the document class loading
command, which is explained in section~\ref{sec:usage},
\nameref{sec:usage}. This allows authors to fix any equation breaking
problem before submission for publication.
\file{elsarticle.cls} supports formatting the author submission
in different types of final format.  This is further discussed in
section \ref{sec:final}, \nameref{sec:final}.


\subsection*{Displayed equations and double column journals}

Many Elsevier journals print their text in two columns. Since
the preprint layout uses a larger line width than such columns,
the formulae are too wide for the line width in print. Here is an
example of an equation  (see equation 6) which is perfect in a
single column preprint format:

\bigskip
\setlength\Sep{6pt}
\src{See equation (6) }
\def\rulecolor{blue!70}
%\includeclip{<page>}{l b scale }{file.pdf}
\includeclip{4}{105 500 500 700}{1psingleauthorgroup.pdf}
\def\rulecolor{orange}
                 	
\noindent When this document is typeset for publication in a
model 3+ journal with double columns, the equation will overlap
the second column text matter if the equation is not broken at
the appropriate location.

\vspace*{6pt}
\def\rulecolor{blue!70}
\src{See equation (6) overprints into second column}
\includeclip{3}{59 421 532 635}{elstest-3pd.pdf}
\def\rulecolor{orange}
\vspace*{6pt}

\noindent The typesetter will try to break the equation which
need not necessarily be to the liking of the author or as it
happens, typesetter's break point may be semantically incorrect.
Therefore, authors may check their submissions for the incidence
of such long equations and break the equations at the correct
places so that the final typeset copy will be as they wish.

\section{Bibliography}

Three bibliographic style files (\verb+*.bst+) are provided ---
\file{elsarticle-num.bst}, \file{elsarticle-num-names.bst} and
\file{elsarticle-harv.bst} --- the first one can be used for the
numbered scheme, second one for numbered with new options of 
\file{natbib.sty}. The third one is for the author year
scheme.

In \LaTeX{} literature, references are listed in the
\verb+thebibliography+ environment.  Each reference is a
\verb+\bibitem+ and each \verb+\bibitem+ is identified by a label,
by which it can be cited in the text:

\verb+\bibitem[Elson et al.(1996)]{ESG96}+ is cited as
\verb+\citet{ESG96}+. 

\noindent In connection with cross-referencing and
possible future hyperlinking it is not a good idea to collect
more that one literature item in one \verb+\bibitem+.  The
so-called Harvard or author-year style of referencing is enabled
by the \LaTeX{} package \file{natbib}. With this package the
literature can be cited as follows:

\begin{enumerate}[\textbullet]
\item Parenthetical: \verb+\citep{WB96}+ produces (Wettig \& Brown, 1996).
\item Textual: \verb+\citet{ESG96}+ produces Elson et al. (1996).
\item An affix and part of a reference:
\verb+\citep[e.g.][Ch. 2]{Gea97}+ produces (e.g. Governato et
al., 1997, Ch. 2).
\end{enumerate}

In the numbered scheme of citation, \verb+\cite{<label>}+ is used,
since \verb+\citep+ or \verb+\citet+ has no relevance in the numbered
scheme.  \file{natbib} package is loaded by \file{elsarticle} with
\verb+numbers+ as default option.  You can change this to author-year
or harvard scheme by adding option \verb+authoryear+ in the class
loading command.  If you want to use more options of the \file{natbib}
package, you can do so with the \verb+\biboptions+ command, which is
described in the section \ref{sec:usage}, \nameref{sec:usage}.  For
details of various options of the \file{natbib} package, please take a
look at the \file{natbib} documentation, which is part of any standard
\LaTeX{} installation.

In addition to the above standard \verb+.bst+ files, there are 10
journal-specific \verb+.bst+ files also available.
Instruction for using these \verb+.bst+ files can be found at 
\href{http://support.stmdocs.in/wiki/index.php?title=Model-wise_bibliographic_style_files}
{http://support.stmdocs.in}

\section{Graphical abstract and highlights}
A template for adding graphical abstract and highlights are available
now. This will appear as the first two pages of the PDF before the
article content begins.

\pagebreak
Please refer below to see how to code them.

\begin{vquote}
....
....

\end{abstract}

%%Graphical abstract
\begin{graphicalabstract}
%\includegraphics{grabs}
\end{graphicalabstract}

%%Research highlights
\begin{highlights}
\item Research highlight 1
\item Research highlight 2
\end{highlights}

\begin{keyword}
%% keywords here, in the form: keyword \sep keyword
....
....
\end{vquote}

\section{Final print}\label{sec:final}

The authors can format their submission to the page size and margins
of their preferred journal.  \file{elsarticle} provides four
class options for the same. But it does not mean that using these
options you can emulate the exact page layout of the final print copy. 


\lmrgn=3em
\begin{description}
\item [\texttt{1p}:] $1+$ journals with a text area of
384pt $\times$ 562pt or 13.5cm $\times$ 19.75cm or 5.3in $\times$
7.78in, single column style only.

\item [\texttt{3p}:] $3+$ journals with a text area of 468pt
$\times$ 622pt or 16.45cm $\times$ 21.9cm or 6.5in $\times$
8.6in, single column style.

\item [\texttt{twocolumn}:] should be used along with 3p option if the
journal is $3+$ with the same text area as above, but double column
style. 

\item [\texttt{5p}:] $5+$ with text area of 522pt $\times$
682pt or 18.35cm $\times$ 24cm or 7.22in $\times$ 9.45in,
double column style only.
\end{description}

Following pages have the clippings of different parts of
the title page of different journal models typeset in final
format.

Model $1+$ and $3+$  will have the same look and
feel in the typeset copy when presented in this document. That is
also the case with the double column $3+$ and $5+$ journal article
pages. The only difference will be wider text width of
higher models.  Therefore we will look at the
different portions of a typical single column journal page and
that of a double column article in the final format.


\begin{center}
\hypertarget{bsc}{}
\hyperlink{sc}{
{\bf [Specimen single column article -- Click here]}
}


\hypertarget{bsc}{}
\hyperlink{dc}{
{\bf [Specimen double column article -- Click here]}
}
\end{center}

\src{}\hypertarget{sc}{}
\def\rulecolor{blue!70}
\hyperlink{bsc}{\includeclip{1}{88 120 514 724}{elstest-1p.pdf}}
\def\rulecolor{orange}

\src{}\hypertarget{dc}{}
\def\rulecolor{blue!70}
\hyperlink{bsc}{\includeclip{1}{27 61 562 758}{elstest-5p.pdf}}
\def\rulecolor{orange}

\end{document}


""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
try:
    TS.TexSoup(pre_format(min_example1), tolerance=1)
except AssertionError as e:
    print(e)
#print(min_example)
# + tags=[]
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example2=r"""
%% 
%% Copyright 2007-2019 Elsevier Ltd
%% 
%% This file is part of the 'Elsarticle Bundle'.
%% ---------------------------------------------
%% 
%% It may be distributed under the conditions of the LaTeX Project Public
%% License, either version 1.2 of this license or (at your option) any
%% later version.  The latest version of this license is in
%%    http://www.latex-project.org/lppl.txt
%% and version 1.2 or later is part of all distributions of LaTeX
%% version 1999/12/01 or later.
%% 
%% The list of all files belonging to the 'Elsarticle Bundle' is
%% given in the file `manifest.txt'.
%%
%% $Id: elsdoc.tex 160 2019-01-14 09:25:49Z rishi $
%%
\documentclass[a4paper,12pt]{article}

\usepackage[xcolor,qtwo]{rvdtx}
\usepackage{multicol}
\usepackage{color}
\usepackage{xspace}
\usepackage{pdfwidgets}
\usepackage{enumerate}

\def\ttdefault{cmtt}

\headsep4pc

\makeatletter
\def\bs{\expandafter\@gobble\string\\}
\def\lb{\expandafter\@gobble\string\{}
\def\rb{\expandafter\@gobble\string\}}
\def\@pdfauthor{C.V.Radhakrishnan}
\def\@pdftitle{elsarticle.cls -- A documentation}
\def\@pdfsubject{Document formatting with elsarticle.cls}
\def\@pdfkeywords{LaTeX, Elsevier Ltd, document class}
\def\file#1{\textsf{#1}\xspace}

%\def\LastPage{19}

\DeclareRobustCommand{\LaTeX}{L\kern-.26em%
        {\sbox\z@ T%
         \vbox to\ht\z@{\hbox{\check@mathfonts
           \fontsize\sf@size\z@
           \math@fontsfalse\selectfont
          A\,}%
         \vss}%
        }%
     \kern-.15em%
    \TeX}
\makeatother

\def\figurename{Clip}

\setcounter{tocdepth}{1}

\begin{document}

\def\testa{This is a specimen document. }
\def\testc{\testa\testa\testa\testa}
\def\testb{\testc\testc\testc\testc\testc}
\long\def\test{\testb\par\testb\par\testb\par}

\pinclude{\copy\contbox\printSq{\LastPage}}

\title{elsarticle.cls -- A better way to format your document}

\author{Elsevier Ltd}
\contact{elsarticle@stmdocs.in}

\version{3.2}
\date{\today}
\maketitle

\section{Introduction}

\file{elsarticle.cls} is a thoroughly re-written document class
for formatting \LaTeX{} submissions to Elsevier journals.
The class uses the environments and commands defined in \LaTeX{} kernel
without any change in the signature so that clashes with other
contributed \LaTeX{} packages such as \file{hyperref.sty},
\file{preview-latex.sty}, etc., will be minimal.
\file{elsarticle.cls} is primarily built upon the default
\file{article.cls}.  This class depends on the following packages
for its proper functioning:

\begin{enumerate}
\item \file{natbib.sty} for citation processing;
\item \file{geometry.sty} for margin settings;
\item \file{fleqn.clo} for left aligned equations;
\item \file{graphicx.sty} for graphics inclusion;
\item \file{txfonts.sty} optional font package, if the document is to
  be formatted with Times and compatible math fonts;
\item \file{hyperref.sty} optional packages if hyperlinking is
  required in the document;
%*%
\item \file{endfloat.sty} optional packages if floats to be placed at
 end of the PDF.
\end{enumerate}

All the above packages (except some optional packages) are part of any
standard \LaTeX{} installation. Therefore, the users need not be
bothered about downloading any extra packages.  Furthermore, users are
free to make use of \textsc{ams} math packages such as
\file{amsmath.sty}, \file{amsthm.sty}, \file{amssymb.sty},
\file{amsfonts.sty}, etc., if they want to.  All these packages work in
tandem with \file{elsarticle.cls} without any problems.

\section{Major Differences}

Following are the major differences between \file{elsarticle.cls}
and its predecessor package, \file{elsart.cls}:

\begin{enumerate}[\textbullet]
\item \file{elsarticle.cls} is built upon \file{article.cls}
while \file{elsart.cls} is not. \file{elsart.cls} redefines
many of the commands in the \LaTeX{} classes/kernel, which can
possibly cause surprising clashes with other contributed
\LaTeX{} packages;

\item provides preprint document formatting by default, and
optionally formats the document as per the final
style of models $1+$, $3+$ and $5+$ of Elsevier journals;

\item some easier ways for formatting \verb+list+ and
\verb+theorem+ environments are provided while people can still
use \file{amsthm.sty} package;

\item \file{natbib.sty} is the main citation processing package
  which can comprehensively handle all kinds of citations and
works perfectly with \file{hyperref.sty} in combination with
\file{hypernat.sty};

\item long title pages are processed correctly in preprint and
  final formats.

\end{enumerate}

\section{Installation}

The package is available at author resources page at Elsevier
(\url{http://www.elsevier.com/locate/latex}).
It can also be found in any of the nodes of the Comprehensive
\TeX{} Archive Network (\textsc{ctan}), one of the primary nodes
being
\url{http://tug.ctan.org/tex-archive/macros/latex/contrib/elsarticle/}.
Please download the \file{elsarticle.dtx} which is a composite
class with documentation and \file{elsarticle.ins} which is the
\LaTeX{} installer file. When we compile the
\file{elsarticle.ins} with \LaTeX{} it provides the class file,
\file{elsarticle.cls} by
stripping off all the documentation from the \verb+*.dtx+ file.
The class may be moved or copied to a place, usually,
\verb+$TEXMF/tex/latex/elsevier/+, %$%%%%%%%%%%%%%%%%%%%%%%%%%%%%
or a folder which will be read                   
by \LaTeX{} during document compilation.  The \TeX{} file
database needs updation after moving/copying class file.  Usually,
we use commands like \verb+mktexlsr+ or \verb+texhash+ depending
upon the distribution and operating system.


\section{Usage}\label{sec:usage}
The class should be loaded with the command:

\begin{vquote}
 \documentclass[<options>]{elsarticle}
\end{vquote}

\noindent where the \verb+options+ can be the following:


\begin{description}

\item [{\tt\color{verbcolor} preprint}]  default option which format the
  document for submission to Elsevier journals.

\item [{\tt\color{verbcolor} review}]  similar to the \verb+preprint+
option, but increases the baselineskip to facilitate easier review
process.

\item [{\tt\color{verbcolor} 1p}]  formats the article to the look and
feel of the final format of model 1+ journals. This is always single
column style.

\item [{\tt\color{verbcolor} 3p}] formats the article to the look and
feel of the final format of model 3+ journals. If the journal is a two
column model, use \verb+twocolumn+ option in combination.

\item [{\tt\color{verbcolor} 5p}] formats for model 5+ journals. This
is always of two column style.

\item [{\tt\color{verbcolor} authoryear}] author-year citation style of
\file{natbib.sty}. If you want to add extra options of
\file{natbib.sty}, you may use the options as comma delimited strings
as arguments to \verb+\biboptions+ command. An example would be:
\end{description}

\begin{vquote}
 \biboptions{longnamesfirst,angle,semicolon}
\end{vquote}

\begin{description}
\item [{\tt\color{verbcolor} number}] numbered citation style. Extra options
  can be loaded with\linebreak \verb+\biboptions+ command.

\item [{\tt\color{verbcolor} sort\&compress}] sorts and compresses the
numbered citations. For example, citation [1,2,3] will become [1--3].

\item [{\tt\color{verbcolor} longtitle}] if front matter is unusually long, use
  this option to split the title page across pages with the correct
placement of title and author footnotes in the first page.

\item [{\tt\color{verbcolor} times}] loads \file{txfonts.sty}, if
available in the system to use Times and compatible math fonts.

%*%
\item [{\tt\color{verbcolor} reversenotenum}] Use alphabets as
author--affiliation linking labels and use numbers for author
footnotes. By default, numbers will be used as author--affiliation
linking labels and alphabets for author footnotes. 

\item [{\tt\color{verbcolor} lefttitle}] To move title and
author/affiliation block to flushleft. \verb+centertitle+ is the
default option which produces center alignment.

\item [{\tt\color{verbcolor} endfloat}] To place all floats at the end
of the document.

\item [{\tt\color{verbcolor} nonatbib}] To unload natbib.sty.
%*%

\item [{\tt\color{verbcolor} doubleblind}] To hide author name, 
affiliation, email address etc. for double blind refereeing purpose.
%*%

\item[] All options of \file{article.cls} can be used with this
  document class.

\item[] The default options loaded are \verb+a4paper+, \verb+10pt+,
  \verb+oneside+, \verb+onecolumn+ and \verb+preprint+.

\end{description}

\section{Frontmatter}

There are two types of frontmatter coding:
\begin{enumerate}[(1)]
\item each author is
connected to an affiliation with a footnote marker; hence all
authors are grouped together and affiliations follow;
\pagebreak
\item authors of same affiliations are grouped together and the
relevant affiliation follows this group. 
\end{enumerate}

An example of coding the first type is provided below.

\begin{vquote}
 \title{This is a specimen title\tnoteref{t1,t2}}
 \tnotetext[t1]{This document is the results of the research
    project funded by the National Science Foundation.}
 \tnotetext[t2]{The second title footnote which is a longer 
    text matter to fill through the whole text width and 
    overflow into another line in the footnotes area of the 
    first page.}
\end{vquote}

\begin{vquote}
\author[1]{Jos Migchielsen\corref{cor1}%
  \fnref{fn1}}
\ead{J.Migchielsen@elsevier.com}

\author[2]{CV Radhakrishnan\fnref{fn2}}
\ead{cvr@sayahna.org}

\author[3]{CV Rajagopal\fnref{fn1,fn3}}
\ead[url]{www.stmdocs.in}
\end{vquote}

\begin{vquote}
 \cortext[cor1]{Corresponding author}
 \fntext[fn1]{This is the first author footnote.}
 \fntext[fn2]{Another author footnote, this is a very long 
   footnote and it should be a really long footnote. But this 
   footnote is not yet sufficiently long enough to make two 
   lines of footnote text.}
 \fntext[fn3]{Yet another author footnote.}

 \address[1]{Elsevier B.V., Radarweg 29, 1043 NX Amsterdam, 
   The Netherlands}
 \address[2]{Sayahna Foundations, JWRA 34, Jagathy, 
   Trivandrum 695014, India}
 \address[3]{STM Document Engineering Pvt Ltd., Mepukada,
   Malayinkil, Trivandrum 695571, India}
\end{vquote}

The output of the above \TeX{} source is given in Clips~\ref{clip1} and
\ref{clip2}. The header portion or title area is given in
Clip~\ref{clip1} and the footer area is given in Clip~\ref{clip2}.

\def\rulecolor{blue!70}
\src{Header of the title page.}
\includeclip{1}{130 612 477 707}{1psingleauthorgroup.pdf}%%{elstest-1p.pdf}%single author group
\def\rulecolor{orange}

\def\rulecolor{blue!70}
\src{Footer of the title page.}
\includeclip{1}{93 135 499 255}{1pseperateaug.pdf}%%{elstest-1p.pdf}%single author group
\def\rulecolor{orange}

Most of the commands such as \verb+\title+, \verb+\author+,
\verb+\address+ are self explanatory.  Various components are
linked to each other by a label--reference mechanism; for
instance, title footnote is linked to the title with a footnote
mark generated by referring to the \verb+\label+ string of
the \verb=\tnotetext=.  We have used similar commands
such as \verb=\tnoteref= (to link title note to title);
\verb=\corref= (to link corresponding author text to
corresponding author); \verb=\fnref= (to link footnote text to
the relevant author names).  \TeX{} needs two compilations to
resolve the footnote marks in the preamble part.  
Given below are the syntax of various note marks and note texts.


\begin{vquote}
  \tnoteref{<label(s)>}
  \corref{<label(s)>}
  \fnref{<label(s)>}
  \tnotetext[<label>]{<title note text>}
  \cortext[<label>]{<corresponding author note text>}
  \fntext[<label>]{<author footnote text>}
\end{vquote}

\noindent where \verb=<label(s)>= can be either one or more comma
delimited label strings. The optional arguments to the
\verb=\author= command holds the ref label(s) of the address(es)
to which the author is affiliated while each \verb=\address=
command can have an optional argument of a label. In the same
manner, \verb=\tnotetext=, \verb=\fntext=, \verb=\cortext= will
have optional arguments as their respective labels and note text
as their mandatory argument.

The following example code provides the markup of the second type
of author-affiliation.

\begin{vquote}
\author{Jos Migchielsen\corref{cor1}%
  \fnref{fn1}}
\ead{J.Migchielsen@elsevier.com}
 \address{Elsevier B.V., Radarweg 29, 1043 NX Amsterdam, 
          The Netherlands}

\author{CV Radhakrishnan\fnref{fn2}}
\ead{cvr@sayahna.org}
 \address{Sayahna Foundations, JWRA 34, Jagathy, 
    Trivandrum 695014, India}

\author{CV Rajagopal\fnref{fn1,fn3}}
\ead[url]{www.stmdocs.in}
  \address{STM Document Engineering Pvt Ltd., Mepukada,
    Malayinkil, Trivandrum 695571, India}
\end{vquote}

\vspace*{-.5pc}

\begin{vquote}
\cortext[cor1]{Corresponding author}
\fntext[fn1]{This is the first author footnote.}
\fntext[fn2]{Another author footnote, this is a very long 
  footnote and it should be a really long footnote. But this 
  footnote is not yet sufficiently long enough to make two lines 
  of footnote text.}
\end{vquote}

The output of the above \TeX{} source is given in Clip~\ref{clip3}.

\def\rulecolor{blue!70}
\src{Header of the title page..}
\includeclip{1}{119 563 468 709}{1pseperateaug.pdf}%%{elstest-1p.pdf}%seperate author groups
\def\rulecolor{orange}
\pagebreak

Clip~\ref{clip4} shows the output after giving \verb+doubleblind+ class option. 

\def\rulecolor{blue!70}
\src{Double blind article}
\includeclip{1}{124 567 477 670}{elstest-1pdoubleblind.pdf}%%{elstest-1p.pdf}%single author group%%doubleblind
\def\rulecolor{orange}

\vspace*{-.5pc}
The frontmatter part has further environments such as abstracts and
keywords.  These can be marked up in the following manner:

\begin{vquote}
 \begin{abstract}
  In this work we demonstrate the formation of a new type of 
  polariton on the interface between a ....
 \end{abstract}
\end{vquote} 

\vspace*{-.5pc}
\begin{vquote}
 \begin{keyword}
  quadruple exiton \sep polariton \sep WGM
 \end{keyword}
\end{vquote}

\noindent Each keyword shall be separated by a \verb+\sep+ command.
\textsc{msc} classifications shall be provided in 
the keyword environment with the commands
\verb+\MSC+. \verb+\MSC+ accepts an optional
argument to accommodate future revisions.
eg., \verb=\MSC[2008]=. The default is 2000.\looseness=-1

\subsection{New page}
Sometimes you may need to give a page-break and start a new page after
title, author or abstract. Following commands can be used for this
purpose.

\begin{vquote}
  \newpageafter{title}
  \newpageafter{author}
  \newpageafter{abstract}
\end{vquote}


\begin{itemize}
\leftskip-2pc
\item [] {\tt\color{verbcolor} \verb+\newpageafter{title}+} typeset the title alone on one page.

\item [] {\tt\color{verbcolor} \verb+\newpageafter{author}+}  typeset the title
and author details on one page.

\item [] {\tt\color{verbcolor} \verb+\newpageafter{abstract}+}
typeset the title,
author details and abstract \& keywords one one page.

\end{itemize}

\section{Floats}
{Figures} may be included using the command, \verb+\includegraphics+ in
combination with or without its several options to further control
graphic. \verb+\includegraphics+ is provided by \file{graphic[s,x].sty}
which is part of any standard \LaTeX{} distribution.
\file{graphicx.sty} is loaded by default. \LaTeX{} accepts figures in
the postscript format while pdf\LaTeX{} accepts \file{*.pdf},
\file{*.mps} (metapost), \file{*.jpg} and \file{*.png} formats. 
pdf\LaTeX{} does not accept graphic files in the postscript format. 

The \verb+table+ environment is handy for marking up tabular
material. If users want to use \file{multirow.sty},
\file{array.sty}, etc., to fine control/enhance the tables, they
are welcome to load any package of their choice and
\file{elsarticle.cls} will work in combination with all loaded
packages.

\section[Theorem and ...]{Theorem and theorem like environments}

\file{elsarticle.cls} provides a few shortcuts to format theorems and
theorem-like environments with ease. In all commands the options that
are used with the \verb+\newtheorem+ command will work exactly in the same
manner. \file{elsarticle.cls} provides three commands to format theorem or
theorem-like environments: 

\begin{vquote}
 \newtheorem{thm}{Theorem}
 \newtheorem{lem}[thm]{Lemma}
 \newdefinition{rmk}{Remark}
 \newproof{pf}{Proof}
 \newproof{pot}{Proof of Theorem \ref{thm2}}
\end{vquote}

The \verb+\newtheorem+ command formats a
theorem in \LaTeX's default style with italicized font, bold font
for theorem heading and theorem number at the right hand side of the
theorem heading.  It also optionally accepts an argument which
will be printed as an extra heading in parentheses. 

\begin{vquote}
  \begin{thm} 
   For system (8), consensus can be achieved with 
   $\|T_{\omega z}$
   ...
     \begin{eqnarray}\label{10}
     ....
     \end{eqnarray}
  \end{thm}
\end{vquote}  

Clip~\ref{clip5} will show you how some text enclosed between the
above code\goodbreak \noindent looks like:

\vspace*{6pt}
\def\rulecolor{blue!70}
\src{{\ttfamily\color{verbcolor}\bs newtheorem}}
\includeclip{2}{1 1 453 120}{jfigs.pdf}
\def\rulecolor{orange}

The \verb+\newdefinition+ command is the same in
all respects as its\linebreak \verb+\newtheorem+ counterpart except that
the font shape is roman instead of italic.  Both
\verb+\newdefinition+ and \verb+\newtheorem+ commands
automatically define counters for the environments defined.

\vspace*{6pt}
\def\rulecolor{blue!70}
\src{{\ttfamily\color{verbcolor}\bs newdefinition}}
\includeclip{1}{1 1 453 105}{jfigs.pdf}
\def\rulecolor{orange}

The \verb+\newproof+ command defines proof environments with
upright font shape.  No counters are defined. 

\vspace*{6pt}
\def\rulecolor{blue!70}
\src{{\ttfamily\color{verbcolor}\bs newproof}}
\includeclip{3}{1 1 453 65}{jfigs.pdf}
\def\rulecolor{orange}

Users can also make use of \verb+amsthm.sty+ which will override
all the default definitions described above.

\section[Enumerated ...]{Enumerated and Itemized Lists}
\file{elsarticle.cls} provides an extended list processing macros
which makes the usage a bit more user friendly than the default
\LaTeX{} list macros.   With an optional argument to the
\verb+\begin{enumerate}+ command, you can change the list counter
type and its attributes.

\begin{vquote}
 \begin{enumerate}[1.]
 \item The enumerate environment starts with an optional
   argument `1.', so that the item counter will be suffixed
   by a period.
 \item You can use `a)' for alphabetical counter and '(i)' for
   roman counter.
  \begin{enumerate}[a)]
    \item Another level of list with alphabetical counter.
    \item One more item before we start another.
\end{vquote}

\def\rulecolor{blue!70}
\src{List -- Enumerate}
\includeclip{4}{1 1 453 185}{jfigs.pdf}
\def\rulecolor{orange}

Further, the enhanced list environment allows one to prefix a
string like `step' to all the item numbers.  

\begin{vquote}
 \begin{enumerate}[Step 1.]
  \item This is the first step of the example list.
  \item Obviously this is the second step.
  \item The final step to wind up this example.
 \end{enumerate}
\end{vquote}

\def\rulecolor{blue!70}
\src{List -- enhanced}
\includeclip{5}{1 1 313 83}{jfigs.pdf}
\def\rulecolor{orange}


\section{Cross-references}
In electronic publications, articles may be internally
hyperlinked. Hyperlinks are generated from proper
cross-references in the article.  For example, the words
\textcolor{black!80}{Fig.~1} will never be more than simple text,
whereas the proper cross-reference \verb+\ref{tiger}+ may be
turned into a hyperlink to the figure itself:
\textcolor{blue}{Fig.~1}.  In the same way,
the words \textcolor{blue}{Ref.~[1]} will fail to turn into a
hyperlink; the proper cross-reference is \verb+\cite{Knuth96}+.
Cross-referencing is possible in \LaTeX{} for sections,
subsections, formulae, figures, tables, and literature
references.

\section[Mathematical ...]{Mathematical symbols and formulae}

Many physical/mathematical sciences authors require more
mathematical symbols than the few that are provided in standard
\LaTeX. A useful package for additional symbols is the
\file{amssymb} package, developed by the American Mathematical
Society. This package includes such oft-used symbols as
$\lesssim$ (\verb+\lesssim+), $\gtrsim$ (\verb+\gtrsim+)  or 
$\hbar$ (\verb+\hbar+). Note that your \TeX{}
system should have the \file{msam} and \file{msbm} fonts installed. If
you need only a few symbols, such as $\Box$ (\verb+\Box+), you might try the
package \file{latexsym}.

Another point which would require authors' attention is the
breaking up of long equations.  When you use
\file{elsarticle.cls} for formatting your submissions in the 
\verb+preprint+ mode, the document is formatted in single column
style with a text width of 384pt or 5.3in.  When this document is
formatted for final print and if the journal happens to be a double column
journal, the text width will be reduced to 224pt at for 3+
double column and 5+ journals respectively. All the nifty 
fine-tuning in equation breaking done by the author goes to waste in
such cases.  Therefore, authors are requested to check this
problem by typesetting their submissions in final format as well
just to see if their equations are broken at appropriate places,
by changing appropriate options in the document class loading
command, which is explained in section~\ref{sec:usage},
\nameref{sec:usage}. This allows authors to fix any equation breaking
problem before submission for publication.
\file{elsarticle.cls} supports formatting the author submission
in different types of final format.  This is further discussed in
section \ref{sec:final}, \nameref{sec:final}.


\subsection*{Displayed equations and double column journals}

Many Elsevier journals print their text in two columns. Since
the preprint layout uses a larger line width than such columns,
the formulae are too wide for the line width in print. Here is an
example of an equation  (see equation 6) which is perfect in a
single column preprint format:

\bigskip
\setlength\Sep{6pt}
\src{See equation (6) }
\def\rulecolor{blue!70}
%\includeclip{<page>}{l b scale }{file.pdf}
\includeclip{4}{105 500 500 700}{1psingleauthorgroup.pdf}
\def\rulecolor{orange}
                 	
\noindent When this document is typeset for publication in a
model 3+ journal with double columns, the equation will overlap
the second column text matter if the equation is not broken at
the appropriate location.

\vspace*{6pt}
\def\rulecolor{blue!70}
\src{See equation (6) overprints into second column}
\includeclip{3}{59 421 532 635}{elstest-3pd.pdf}
\def\rulecolor{orange}
\vspace*{6pt}

\noindent The typesetter will try to break the equation which
need not necessarily be to the liking of the author or as it
happens, typesetter's break point may be semantically incorrect.
Therefore, authors may check their submissions for the incidence
of such long equations and break the equations at the correct
places so that the final typeset copy will be as they wish.

\section{Bibliography}

Three bibliographic style files (\verb+*.bst+) are provided ---
\file{elsarticle-num.bst}, \file{elsarticle-num-names.bst} and
\file{elsarticle-harv.bst} --- the first one can be used for the
numbered scheme, second one for numbered with new options of 
\file{natbib.sty}. The third one is for the author year
scheme.

In \LaTeX{} literature, references are listed in the
\verb+thebibliography+ environment.  Each reference is a
\verb+\bibitem+ and each \verb+\bibitem+ is identified by a label,
by which it can be cited in the text:

\verb+\bibitem[Elson et al.(1996)]{ESG96}+ is cited as
\verb+\citet{ESG96}+. 

\noindent In connection with cross-referencing and
possible future hyperlinking it is not a good idea to collect
more that one literature item in one \verb+\bibitem+.  The
so-called Harvard or author-year style of referencing is enabled
by the \LaTeX{} package \file{natbib}. With this package the
literature can be cited as follows:

\begin{enumerate}[\textbullet]
\item Parenthetical: \verb+\citep{WB96}+ produces (Wettig \& Brown, 1996).
\item Textual: \verb+\citet{ESG96}+ produces Elson et al. (1996).
\item An affix and part of a reference:
\verb+\citep[e.g.][Ch. 2]{Gea97}+ produces (e.g. Governato et
al., 1997, Ch. 2).
\end{enumerate}

In the numbered scheme of citation, \verb+\cite{<label>}+ is used,
since \verb+\citep+ or \verb+\citet+ has no relevance in the numbered
scheme.  \file{natbib} package is loaded by \file{elsarticle} with
\verb+numbers+ as default option.  You can change this to author-year
or harvard scheme by adding option \verb+authoryear+ in the class
loading command.  If you want to use more options of the \file{natbib}
package, you can do so with the \verb+\biboptions+ command, which is
described in the section \ref{sec:usage}, \nameref{sec:usage}.  For
details of various options of the \file{natbib} package, please take a
look at the \file{natbib} documentation, which is part of any standard
\LaTeX{} installation.

In addition to the above standard \verb+.bst+ files, there are 10
journal-specific \verb+.bst+ files also available.
Instruction for using these \verb+.bst+ files can be found at 
\href{http://support.stmdocs.in/wiki/index.php?title=Model-wise_bibliographic_style_files}
{http://support.stmdocs.in}

\section{Graphical abstract and highlights}
A template for adding graphical abstract and highlights are available
now. This will appear as the first two pages of the PDF before the
article content begins.

\pagebreak
Please refer below to see how to code them.

\begin{vquote}
....
....

\end{abstract}

%%Graphical abstract
\begin{graphicalabstract}
%\includegraphics{grabs}
\end{graphicalabstract}

%%Research highlights
\begin{highlights}
\item Research highlight 1
\item Research highlight 2
\end{highlights}

\begin{keyword}
%% keywords here, in the form: keyword \sep keyword
....
....
\end{vquote}

\section{Final print}\label{sec:final}

The authors can format their submission to the page size and margins
of their preferred journal.  \file{elsarticle} provides four
class options for the same. But it does not mean that using these
options you can emulate the exact page layout of the final print copy. 


\lmrgn=3em
\begin{description}
\item [\texttt{1p}:] $1+$ journals with a text area of
384pt $\times$ 562pt or 13.5cm $\times$ 19.75cm or 5.3in $\times$
7.78in, single column style only.

\item [\texttt{3p}:] $3+$ journals with a text area of 468pt
$\times$ 622pt or 16.45cm $\times$ 21.9cm or 6.5in $\times$
8.6in, single column style.

\item [\texttt{twocolumn}:] should be used along with 3p option if the
journal is $3+$ with the same text area as above, but double column
style. 

\item [\texttt{5p}:] $5+$ with text area of 522pt $\times$
682pt or 18.35cm $\times$ 24cm or 7.22in $\times$ 9.45in,
double column style only.
\end{description}

Following pages have the clippings of different parts of
the title page of different journal models typeset in final
format.

Model $1+$ and $3+$  will have the same look and
feel in the typeset copy when presented in this document. That is
also the case with the double column $3+$ and $5+$ journal article
pages. The only difference will be wider text width of
higher models.  Therefore we will look at the
different portions of a typical single column journal page and
that of a double column article in the final format.


\begin{center}
\hypertarget{bsc}{}
\hyperlink{sc}{
{\bf [Specimen single column article -- Click here]}
}


\hypertarget{bsc}{}
\hyperlink{dc}{
{\bf [Specimen double column article -- Click here]}
}
\end{center}

\src{}\hypertarget{sc}{}
\def\rulecolor{blue!70}
\hyperlink{bsc}{\includeclip{1}{88 120 514 724}{elstest-1p.pdf}}
\def\rulecolor{orange}

\src{}\hypertarget{dc}{}
\def\rulecolor{blue!70}
\hyperlink{bsc}{\includeclip{1}{27 61 562 758}{elstest-5p.pdf}}
\def\rulecolor{orange}

\end{document}


""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
try:
    TS.TexSoup(pre_format(min_example2), tolerance=1)
except AssertionError as e:
    print(e)
#print(min_example)
# + tags=[]
import pandas as pd
import numpy as np
pd.DataFrame(np.random.randint(0,100,size=(10, 3)), columns=list('ABC')).to_csv('~/Expire/test_console_upload.csv')
# -
min_example1 == min_example2



