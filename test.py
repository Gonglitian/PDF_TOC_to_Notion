import fitz  # PyMuPDF
from utils import *
import configparser
import os
from uploader import Md2NotionUploader

pdf_paths = ["./src_file/degree_demo.pdf"]
config = configparser.ConfigParser()
config.read("./config.ini")
# S = Summarizer(config)
# S.start(pdf_paths)
TEST_PAGE_ID = "c8b402d1292645e483600bf5f183ed6f"
N = NotionUploader(config)


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as mdFile:
        with NotionPyRenderer() as renderer:
            a = Document(mdFile)
            out = renderer.render(a)
    return out


filepath = "./result.md"
blocks = read_file("./result.md")
# pprint(blocks)
# N.upload_to_page(TEST_PAGE_ID, content)
# uploader = Md2NotionUploader()
# uploader.local_root = os.path.dirname(filepath)
# num_blocks = len(blocks)
# for i, content in enumerate(blocks):
#     # if i < start_line:
#     #     continue
#     print(f"uploading block {i}/{num_blocks},............", end='\n')
#     uploader.uploadBlock(content, N.notion_client, TEST_PAGE_ID)
#     print('done!')

pprint(N.notion_client.blocks.children.list(TEST_PAGE_ID))
