import fitz  # PyMuPDF
from utils import *

S = Summarizer()
S.pdf = fitz.open("./src_file/degree_demo.pdf")
# S.get_section_content(1, 5)
toc = S.pdf.get_toc(simple=True)

S.summary_degree_papers("./src_file/degree.pdf",
                        toc)
