# todo 加入更多block_type常数
import os
from dotenv import load_dotenv
from notion_client import Client
import json
import fitz  # PyMuPDF

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

notion = Client(auth=os.environ.get("NOTION_TOKEN"))


def assemble_page_block_object(block_type, block_content):
    return {
        "object": "block",
        block_type: {
            "rich_text": [{"text": {"content": block_content}}]
        }

    }


def has_children_blocks(page_id):
    page_blocks = notion.blocks.children.list(page_id)["results"]
    # print(json.dumps(page_blocks, indent=4))
    if len(page_blocks) > 0:
        print(f"Page {page_id} already has children blocks.")
        return True
    return False


def add_blocks_to_page(page_id, children_blocks):

    # 检查是否有子块
    if has_children_blocks(page_id):
        return

    # 添加子块
    notion.blocks.children.append(
        block_id=page_id,
        children=children_blocks,
    )
    print(f"Blocks added to page: {page_id}")


def get_children_blocks(pdf_path):
    # 打开PDF文件
    try:
        document = fitz.open(pdf_path)
    except Exception as e:
        print(f"无法打开PDF文件: {e}")
        return None
    # 获取PDF文件目录
    toc = document.get_toc(simple=False)
    if not toc:
        # todo 没有toc则判断为期刊文章，考虑用gpt处理，参考chatpaper
        print("PDF文件没有大纲信息。")
        document.close()
        return None

    children_blocks = []
    for level, title, page, x in toc:
        level = min(level, 3)  # 限制Markdown标题层级在1到3
        heading_type = HEADINGS[level - 1]
        heading_block = assemble_page_block_object(heading_type, title)
        children_blocks.append(heading_block)

    document.close()
    return children_blocks
