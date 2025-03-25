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

# %pip install --force-reinstall --no-deps git+https://github.com/chrisjcameron/TexSoup.git@mixed-args
# #! pip install --editable /Users/cjc73/gits/arxiv/TexSoup/

#import zipfile
import tarfile
import io
import importlib
import os
import regex as re
import glob
import pandas as pd
import itertools as itr
import pprint

import pyperclip   #copy text to clipboard for inspecting

from tqdm.auto import tqdm

from IPython.core.interactiveshell import InteractiveShell
# pretty print all cell's output and not just the last one
InteractiveShell.ast_node_interactivity = "all"

import TexSoup as TS
from TexSoup.tokens import MATH_ENV_NAMES
# -

TS.__file__


TS.__file__

# +
#importlib.reload(TS)
# -

LOCAL_DATA_PATH = './data/2201_00_all/'


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


# +
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


# -

def soup_from_tar(tar_path, encoding='utf-8', tolerance=0):
    tex_main = find_main_tex_source_in_tar(tar_path, encoding=encoding)
    with tarfile.open(tar_path, 'r') as in_tar:
        fp = in_tar.extractfile(tex_main)
        wrapped_file = io.TextIOWrapper(fp, newline=None, encoding=encoding) #universal newlines
        source_text = pre_format(wrapped_file.read())
        soup = TS.TexSoup(source_text, tolerance=tolerance, skip_envs=MATH_ENV_NAMES)
        return soup


def source_from_tar(tar_path, encoding='utf-8'):
    tex_main = find_main_tex_source_in_tar(tar_path, encoding=encoding)
    with tarfile.open(tar_path, 'r') as in_tar:
        fp = in_tar.extractfile(tex_main)
        wrapped_file = io.TextIOWrapper(fp, newline=None, encoding=encoding) #universal newlines
        source_text = pre_format(wrapped_file.read())
        return source_text


# +
swap = itr.cycle((True, False))

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


# +
def show_context(text_path, offset, context_size=50):
    try: 
        with open(text_path, 'r', encoding='utf-8') as file:
            file.seek(offset)
            context = file.read(context_size)
            return context
            # Is it unicode?
    except UnicodeDecodeError as ue:
        pass
    try:
        with open(text_path, 'r', encoding='latin-1') as file:
            file.seek(offset)
            context = file.read(context_size)
            return context
    except: 
        raise

# file_path = 'Ising_v2.tex'
# offset_position = 805
# context = show_context(file_path, offset_position)
# print("Error context at offset 805:", context)


# -

show_context(infile_path, 8584)

# ## Check a file with parse errors

min_example=r"""
{\subsection}
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
try:
    TS.TexSoup(pre_format(min_example), tolerance=0)
except AssertionError as e:
    print(e)
#print(min_example)

min_example=r"""
\renewcommand{\tilde}{\widetilde}
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
try:
    TS.TexSoup(pre_format(min_example), tolerance=0)
except AssertionError as e:
    print(e)
#print(min_example)

# +
infile_path = "./data/2201_00_all/2201.00001v1.tar.gz" #'./data/2201_samp/2201.00048v1.tar.gz'

text = source_from_tar(infile_path)
pyperclip.copy(text)
soup = soup_from_tar(infile_path, tolerance=1)


title = soup.find('title')
if title: print(f"{title.name}: {title.text}")
for sec in soup.find_all('section'):
    print(f' {sec.name}: {sec.text}')
# -




# ## Quick check a folder of tar files

# +
files = glob.glob(f'{LOCAL_DATA_PATH}/*.tar.gz')
files_count = len(files)
utf_count = 0
latin_count = 0 
err_files = {}

TOLERANCE = 0

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
# -


print(f"{files_count} processed, {len(err_files)} failures.")
print(f"UTF8: {utf_count}; Latin1: {latin_count}")
err_files

# ## Scratch below here

show_context(infile_path, 8584)


# +
TOLERANCE = 0
infile_path = "/Volumes/Neptune/scratch/2404/2404.08812v1.tar.gz" #'./data/2201_samp/2201.00048v1.tar.gz'

text = source_from_tar(infile_path)
pyperclip.copy(text)
soup = soup_from_tar(infile_path, tolerance=TOLERANCE)


title = soup.find('title')
if title: print(f"{title.name}: {title.text}")
for sec in soup.find_all('section'):
    print(f' {sec.name}: {sec.text}')
# -

soup.find_all('section')

soup

find_bad_lines(infile_path, encoding='utf-8')



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

main_files

# +
doc_class_pat = re.compile(r"^\s*\\document(?:style|class)")

with tarfile.open(tar_path, 'r', encoding='utf-8') as in_tar:
    #in_tar.getnames()
    fp = in_tar.extractfile('main.tex')
    wrapped_file = io.TextIOWrapper(fp, newline=None, encoding='utf-8') #universal newlines
    for line in wrapped_file:
        if doc_class_pat.search(line):
            print(line)
            break
# -


next(wrapped_file)







# + active=""
# # Discover the file list:
# input_zip = '2201.00007v1.zip'
# infile_path = os.path.join(LOCAL_DATA_PATH, input_zip)
# if True: #False:
#     with zipfile.ZipFile(infile_path, "r") as in_zip:
#         files = in_zip.infolist()
#         for file_info in files:
#             if not '/.' in file_info.filename:
#                 print(file_info.filename)

# + active=""
# main_tex = '2201.00007v1/main.tex'
# with zipfile.ZipFile(infile_path, "r") as in_zip:
#     with in_zip.open('2201.00007v1/main.tex') as in_tex:
#         #print(in_tex.read())
#         wrapped_file = io.TextIOWrapper(in_tex, newline=None, encoding='utf-8') #universal newlines
#         source_text = pre_format(wrapped_file.read())
#         soup = TS.TexSoup(source_text)


# + active=""
# title = soup.find('title')
# print(f"{title.name}: {title.text}")
# for sec in soup.find_all('section'):
#     print(f' {sec.name}: {sec.text}')
#     
#
# -


min_example=r"""
\documentclass{article}
\begin{document}
% \renewcommand{\shorttitle}{Avoiding Catastrophe}
\end{document}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
#print(min_example)
TS.TexSoup(r'\newcommand{\bra}[1]{\left\langle#1\right|}')


TS.TexSoup(r'\def\be{\foo{equation}}')

TS.TexSoup(r'\renewcommand{\shorttitle}{Avoiding Catastrophe}')
min_example = r"\newenvironment{inlinemath}{$}{$}".strip()
TS.TexSoup(pre_format(min_example))
#print(min_example)

min_example = r"In practice, the matrix $\left [ 4 \right]\Inv\M{D}^{(1)}_n $".strip()
TS.TexSoup(pre_format(min_example))
#print(min_example)

# +
min_example = r"In practice, the matrix $\left[ 4 \right]\Inv\M{D}^{(1)}_n $"


cats = TS.category.categorize(min_example)
tokens = list(TS.tokens.tokenize(cats))

char_codes = list(TS.category.categorize(min_example))

buf = TS.reader.Buffer(TS.tokens.tokenize(TS.category.categorize(r'\left[ 4 \right]')))
TS.reader.read_command(buf, n_required_args=-1, mode='mode:math', skip=1 )


# +
min_example=r"""
\renewcommand{\subsection}[1]{{\textit{#1.~}}}""".strip()

cats = TS.category.categorize(min_example)
tokens = list(TS.tokens.tokenize(cats))

char_codes = list(TS.category.categorize(min_example))

with pd.option_context('display.max.columns', None, 'display.max_colwidth', 0):
    pd.DataFrame({'char':char_codes, 'code':(x.category for x in char_codes)}).transpose()
    pd.DataFrame({'tokens':tokens})

print("Cmd Math Mode")
buf = TS.reader.Buffer(TS.tokens.tokenize(TS.category.categorize(min_example)))
rd_cmd = TS.reader.read_command(buf, n_required_args=2, n_optional_args=2, mode='mode:math', tolerance=1)
pprint.pp(rd_cmd)

print("Cmd Non Math")
buf = TS.reader.Buffer(TS.tokens.tokenize(TS.category.categorize(min_example)))
rd_cmd = TS.reader.read_command(buf,  n_required_args=2, n_optional_args=2, tolerance=1)
pprint.pp(rd_cmd)

print("Reader")
buf = TS.reader.Buffer(TS.tokens.tokenize(TS.category.categorize(min_example)))
rd = TS.read(buf, tolerance=1)
pprint.pp(rd)

# +
min_example = r"\subsection[Background Info]{Background}"


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


# +
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
# -


with pd.option_context('display.max.columns', None, 'display.max_colwidth', 0):
    pd.DataFrame({'char':char_codes, 'code':(x.category for x in char_codes)}).transpose()
    pd.DataFrame({'tokens':tokens})

min_example = r"In practice, the matrix $\left [\M{D}^{(1)}_n(\M{D}^{(1)}_n)\Tra\right]\Inv\M{D}^{(1)}_n $"
print(min_example)
TS.TexSoup(pre_format(min_example))
TS.TexSoup(min_example)

min_example=r"""
\documentclass{article}
\begin{document}
% \renewcommand{\shorttitle}{Avoiding Catastrophe}
\end{document}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
#print(min_example)

min_example=r"""
\def\bean {\begin{foo}}  \def\eean {\end{foo}}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
TS.TexSoup(min_example)
print(min_example)
min_example=r"""
we {use $A=8B$ and $s=1$, then the scalar field becomes same with (\Ref{scalarfield}) and
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#TS.TexSoup(min_example)
print(min_example)
print(pre_format(min_example))
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




min_example=r"""
\def\bean {\begin{eqnarray*}}  \def\eean {\end{eqnarray*}}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
#print(min_example)
min_example=r"""
the interval $t\in[0,1)$. 
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example))
#print(min_example)
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
min_example=r"""
\newcommand\const{\operatorname{const}}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
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
min_example=r"""
\[
r_p=d(p,\cdot)\colon \Gamma \to [0,\infty)|~ p \in M\}
\]
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
min_example=r"""
$\bigl[ a \bigr)$
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
min_example=r"""

$\varepsilon\in]0,\varepsilon_\star[$,  

""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
min_example=r"""
\[
i\colon [0,\infty) 
\]
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)


min_example=r"""
\newcommand\1{{\mathds 1}}
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
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
min_example=r"""
 $S \subseteq \{0\} \bigcup [1,\infty) $ if $z^*_2=1$.  
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# two inline math envs next to eachother
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
$\rm{W_{cyc} }\geq 0$$\;\;\square$
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
\verb+$TEXMF/tex/latex/elsevier/+, %$%%%%%%%%%%%%%%%%%%%%%%%%%%%%
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# does not handle missing optional braces around arguments
min_example=r"""
$\sqrt {\frac 3 2} >p >1$
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
&$\rm{N_{Diskbb}}$$(\times 10^4) $
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
$\frac{j+1+\epsilon}{m^{\alpha}}[$
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
$1\le k< \frac n2 $ 
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
\begin{equation}
\begin{aligned}[t]
[T\tensor*[]{]}{_{\CT}^{\sp}} \\
[T]{_{\CT}^{\sp}}
\end{aligned}
\end{equation}
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=1)
#print(min_example)
# +
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
with open('./data/test.txt', 'r') as infile:
    min_example=infile.read().strip()

TS.TexSoup(pre_format(min_example), tolerance=0)
#print(min_example)
# -
# \verb{char}...{char} is also an issue for parser
# !! probably not fixable given the approach used in TexSoup (needs stateful tokenization)
min_example=r"""
\def\f{\frac}
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=0)
#print(min_example)
import pandas as pd
import numpy as np
pd.DataFrame(np.random.randint(0,100,size=(10, 3)), columns=list('ABC')).to_csv('~/Expire/test_console_upload.csv')

min_example=r"""
\renewcommand{\subsection}[1]{{\textit{#1.~}}}
""".strip()#.replace('\\}\\', '\\} \\').replace(')}', ') }')
TS.TexSoup(pre_format(min_example), tolerance=0)
#print(min_example)
