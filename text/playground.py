text = """
Department of Aerospace Engineering

Univ. of Michigan

Ann Arbor, Michigan 48109, USA
"""
text = text.replace(",", "")
text = text.replace("\n", " ")
text = text.replace("-", "")
text = text.replace("  "," ")
text = text.replace("Univ.","University")
print(text)