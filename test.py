import fitz  # PyMuPDF
from utils import *
import configparser
pdf_paths = ["./src_file/degree_demo.pdf"]
config = configparser.ConfigParser()
config.read("./config.ini")
S = Summarizer(config)
S.start(pdf_paths)
