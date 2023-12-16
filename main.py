import fitz  # PyMuPDF
from notion_client import Client
from dotenv import load_dotenv
import os

DEBUG = True


def log(func):
    def wrapper(*args, **kwargs):

        if DEBUG:
            func(*args, **kwargs)
        else:
            pass
    return wrapper


print = log(print)


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
        heading_type = "heading_%s" % level
        heading_block = {
            "object": "block",
            # "type": heading_type,
            heading_type: {
                "rich_text": [
                    {
                        # "type": "text",
                        "text": {
                            "content": title,  # 目录项
                        },
                    },
                ],
            },
        }
        children_blocks.append(heading_block)

    document.close()
    return children_blocks


def add_papers_to_notion_database(database_id, paper_note_template):
    # 创建Notion数据库item
    new_page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {
                "title": [
                    {
                        # "type": "text",
                        "text": {
                            "content": "Note",  # 论文标题
                        },
                    },
                ],
            },
            "Title": {
                # "type": "rich_text",
                "rich_text": [
                    {
                        # "type": "text",
                        "text": {
                            # 论文标题
                            "content": paper_note_template["title"],
                        },

                    }
                ],
            },

            # "Relation": {
            #     "relation": [
            #         {
            #             "id": os.environ.get("RELATION_ID"),  # 关联数据库ID
            #         },
            #     ],
            # },
            # 如果数据库有其他属性，可以在这里添加
        },
        children=paper_note_template["children_blocks"],
    )
    print(f"Page for '{paper_note_template['title']}' added to the database.")


def add_blocks_to_page(page_id, children_blocks):
    # 添加子块
    notion.blocks.children.append(
        block_id=page_id,
        children=children_blocks,
    )
    print(f"Blocks added to page: {page_id}")


load_dotenv(override=True)
notion = Client(auth=os.environ.get("NOTION_TOKEN"))
DATA_BASE_ID = os.environ.get("DATABASE_ID")
PAPER_DATABASE_ID = os.environ.get("PAPER_DATABASE_ID")

PDF_DIR_PATH = r"E:\2023Fall\毕业设计\ref\论文"
CNKI_PDF_path_dict = {}
# 对本地文件夹中的pdf文件进行遍历
for file in os.listdir(PDF_DIR_PATH):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(PDF_DIR_PATH, file)
        # add path to dict
        CNKI_PDF_path_dict[file.split('_')[0]] = pdf_path

# 列出数据库中所有页面
response = notion.databases.query(PAPER_DATABASE_ID)
# # 打印每个页面的ID和标题
for page in response['results']:
    # page_id = page['id']
    # page_title = page['properties']['Name']['title'][0]['text']['content']
    # todo 如果page已经有children，就不添加
    # print(page['properties']['Title']['rich_text'][0]['text']['content'])
    Title_of_paper = page['properties']['Title']['rich_text'][0]['text']['content']
    pdf_path = CNKI_PDF_path_dict.get(Title_of_paper, None)
    if pdf_path is None:
        print(f"没有找到{Title_of_paper}的PDF文件")
        continue
    toc_blocks = get_children_blocks(pdf_path)
    print(toc_blocks)
