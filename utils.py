# todo 加入更多block_type常数
from pprint import pprint
from dotenv import load_dotenv
from notion_client import Client
import fitz  # PyMuPDF
from typing import List, Tuple, Any
HEADINGS = ["heading_1", "heading_2", "heading_3"]
PARAGRAPH = "paragraph"
BULLETED_LIST_ITEM = "bulleted_list_item"
NUMBERED_LIST_ITEM = "numbered_list_item"
TO_DO = "to_do"
TOGGLE = "toggle"
CHILD_PAGE = "child_page"
QUOTE = "quote"
CALLOUT = "callout"
CODE = "code"
EMBED = "embed"
IMAGE = "image"
DEBUG = True
TEST_PAGE_ID = "49e7733874fe403c85968ac7cad67919"


def log(func):
    def wrapper(*args, **kwargs):

        if DEBUG:
            func(*args, **kwargs)
        else:
            pass
    return wrapper


print = log(print)


class NotionUploader:
    def __init__(self, notion):
        self.notion_client = notion

    def assemble_page_block_object(self, block_type, block_content):
        # todo 考虑列表类型的block
        return {
            "object": "block",
            block_type: {
                "rich_text": [{"text": {"content": block_content}}]
            }
        }

    def has_children_blocks(self, page_id):
        page_blocks = self.notion_client.blocks.children.list(page_id)[
            "results"]
        # print(json.dumps(page_blocks, indent=4))
        if len(page_blocks) > 0:
            print(f"Page {page_id} already has children blocks.")
            return True
        return False

    def upload_blocks_to_page(self, page_id, children_blocks):
        # 检查是否有子块
        if self.has_children_blocks(page_id):
            return

        # 添加子块
        self.notion_client.blocks.children.append(
            block_id=page_id,
            children=children_blocks,
        )
        print(f"Blocks added to page: {page_id}")

    def add_markdown_to_page(self, markdown_content):
        # todo
        pass


class Summarizer:
    def __init__(self, notion=None):
        self.notion_client = notion
        self.summaries = []  # [{page_title: summary}, ...]
        self.pdf = None

    def generate_markdown_summary(self, pdf_paths: List[str]):
        for pdf_path in pdf_paths:
            # 打开PDF文件
            # note 核心功能
            # todo 加上期刊文章的总结
            # todo 加上硕博论文章节的总结
            try:
                self.pdf = fitz.open(pdf_path)

            except Exception as e:
                print(f"无法打开PDF文件: {e}")
                return None
            # 获取PDF文件目录
            toc: List[Tuple[int, str, int]] = self.pdf.get_toc(simple=True)
            if not toc:
                # todo 没有toc则判断为期刊文章，考虑用gpt处理，参考chatpaper
                self.summary_journals(pdf_path)

            else:
                # todo 有toc则判断为硕博论文，考虑用gpt处理，参考chatpaper
                self.summary_degree_papers(pdf_path, toc)

    def summary_journals(self, pdf_path):
        pass

    def summary_degree_papers(self, pdf_path, toc: List[Tuple[int, str, int]]):
        # 根据toc 获取每个章节的页码
        section_with_content = {}
        toc_info = []
        for level, title, page in toc:
            if title == "参考文献" or title == "致谢":
                break

            if level == 1:
                toc_info.append((title, page))
        print(toc_info)
        last_page_index = 0
        # 遍历toc_info，获取每个章节的内容
        for index, (title, page_index) in enumerate(toc_info):
            # 考虑最后一个章节的情况
            if index == len(toc_info) - 1:
                section_with_content[title] = self.get_section_content(
                    last_page_index, self.pdf.page_count)
                break
            if title == "参考文献" or title == "致谢":
                break
            # 考虑中文学位论文既有双语摘要的情况
            if title == "摘要" and toc_info[index+1][0].upper() == "ABSTRACT":
                continue
            # 如果是摘要摘要只截取2页内容
            if title == "摘要" or title.upper() == "ABSTRACT":
                section_with_content[title] = self.get_section_content(
                    page_index, page_index+1)
                continue
            # 获取两个page_index之间的内容
            section_with_content[title] = self.get_section_content(
                page_index, toc_info[index+1][1])
            last_page_index = page_index
        # note: test
        # pprint(section_with_content["ABSTRACT".lower()])

    def get_section_content(self, start_page_index, end_page_index) -> str:
        # 打开PDF文件
        text = ""
        # 遍历页码范围
        for page_num in range(start_page_index, end_page_index + 1):
            # 获取页面对象
            # print(page_num)
            page = self.pdf.load_page(page_num-1)
            # 提取页面文本
            # print(text)
            text += page.get_text()
        return text
