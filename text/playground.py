text = """
Department of Aerospace Engineering

University of Michigan

Ann Arbor, Michigan 48109, USA
"""
text = text.replace(",", "")
text = text.replace("\n", " ")
text = text.replace("-", "")
text = text.replace("  "," ")
print(text)