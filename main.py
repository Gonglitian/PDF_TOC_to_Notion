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
    # 获取PDF文件标题
    paper_title = pdf_path.split('/')[-1].split('.')[0]
    # 获取PDF文件目录
    toc = document.get_toc(simple=False)
    if not toc:
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
    paper_note_template = {
        "title": paper_title,
        "children_blocks": children_blocks,
    }
    return paper_note_template


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


load_dotenv(override=True)
notion = Client(auth=os.environ.get("NOTION_TOKEN"))
DATA_BASE_ID = os.environ.get("DATABASE_ID")
PAPER_DATABASE_ID = os.environ.get("PAPER_DATABASE_ID")

# ADD PAGE TO DATABASE
# pdf_path = 'src_file/doc1.pdf'  # PDF文件路径
# paper_note_template = get_children_blocks(pdf_path)
# add_papers_to_notion_database(os.environ.get(
#     "DATABASE_ID"), paper_note_template)

# PRINT ALL PAGES IN PAPER_DATABASE


PDF_DIR_PATH = r"D:\EdgeDownload"

CNKI_PDF_path_dict = {}
# 对本地文件夹中的pdf文件进行遍历
for file in os.listdir(PDF_DIR_PATH):
    # print(pdf_file)
    if file.endswith(".pdf"):
        pdf_path = os.path.join(PDF_DIR_PATH, file)
        # print(pdf_path)
        # add path to dict
        CNKI_PDF_path_dict[file.split('_')[0]] = pdf_path

print(CNKI_PDF_path_dict)

# 列出数据库中所有页面
response = notion.databases.query(PAPER_DATABASE_ID)
# # 打印每个页面的ID和标题
for page in response['results']:
    # page_id = page['id']
    # page_title = page['properties']['Name']['title'][0]['text']['content']

    print(page['properties']['Title']['rich_text'][0]['text']['content'])

# CNKI_PDF_path_dict = {:PDF_DIR_PATH + ""}
# 初始化Notion客户端

# 查询数据库
# query_response = notion.databases.query(
#     **{
#         "database_id": PAPER_DATABASE_ID,
#         "filter": {
#             "or": [
#                 {"property": "Name", "text": {"contains": "1"}},]}
#     }
# )

# # 检查是否有匹配的页面
# if query_response['results']:
#     # 获取第一个匹配项的页面ID
#     page_id = query_response['results'][0]['id']
#     print(f"Found page ID for the PDF 室外变电站巡检机器人自主导航研究: {page_id}")
# else:
#     print("No page found for the PDF 室外变电站巡检机器人自主导航研究.")
##
