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
#import zipfile
import tarfile
import io
import importlib
import os
import regex as re
import glob

# + tags=[]
from tqdm.auto import tqdm

# + tags=[]
from IPython.core.interactiveshell import InteractiveShell
# pretty print all cell's output and not just the last one
InteractiveShell.ast_node_interactivity = "all"

# + tags=[]
import TexSoup as TS
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
    )
    clean_lines = []
    for line in source_text.splitlines(False):
        cleanline = line.strip()
        if cleanline.startswith(r'\newcommand'):
            cleanline = r'%' + cleanline
        elif cleanline.startswith(r'\def'):
            cleanline = r'%' + cleanline
        clean_lines.append(cleanline)
    return '\n'.join(clean_lines)


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
def soup_from_tar(tar_path, encoding='utf-8'):
    tex_main = find_main_tex_source_in_tar(tar_path, encoding=encoding)
    with tarfile.open(tar_path, 'r') as in_tar:
        fp = in_tar.extractfile(tex_main)
        wrapped_file = io.TextIOWrapper(fp, newline=None, encoding=encoding) #universal newlines
        source_text = pre_format(wrapped_file.read())
        soup = TS.TexSoup(source_text)
        return soup


# -

# ## Quick check a folder of tar files

# + tags=[]
files = glob.glob(f'{LOCAL_DATA_PATH}/*.tar.gz')
files_count = len(files)
utf_count = 0
latin_count = 0 
err_files = {}

with tqdm(total=files_count, desc="errors") as err_prog:
    for tar_file in tqdm(files, desc="Progress", display=True):
        # Is it unicode?
        try:
            soup = soup_from_tar(tar_file, encoding='utf-8')
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
            soup = soup_from_tar(tar_file, encoding='latin-1')
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
print(f"UTF8: {utf_count}; Latin1:{latin_count}")
err_files

# + tags=[]



# + tags=[]
infile_path = "./data/2201_samp/2201.00042v1.tar.gz" #'./data/2201_samp/2201.00048v1.tar.gz'

soup = soup_from_tar(infile_path)


title = soup.find('title')
print(f"{title.name}: {title.text}")
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



# + tags=[]
min_example=r"""
\documentclass{article}
\title{Foo}

\begin{document}

\renewcommand{\shorttitle}{Avoiding Catastrophe}

\maketitle

\begin{abstract}
 A key challenge for AI is to build embodied systems.
\end{abstract}

\section{Introduction}

Creating embodied systems that thrive in dynamically changing environments is a fundamental challenge for building intelligent systems. 

\end{document}
""".strip() #.replace('\\}\\', '\\} \\').replace(')}', ') }')
#TS.TexSoup(pre_format(min_example))
TS.TexSoup(min_example)
#print(min_example)
# + tags=[]
print(pre_format(min_example))
# -


