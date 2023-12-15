import fitz  # PyMuPDF
from notion_client import Client
from dotenv import load_dotenv
import os


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
            "type": heading_type,
            heading_type: {
                "rich_text": [
                    {
                        "type": "text",
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
    # 创建Notion数据库页面
    new_page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": paper_note_template["title"],  # 论文标题
                        },
                    },
                ],
            },
            "Relation": {
                "relation": [
                    {
                        "id": os.environ.get("RELATION_ID"),  # 关联数据库ID
                    },
                ],
            },
            # 如果数据库有其他属性，可以在这里添加
        },
        children=paper_note_template["children_blocks"],
    )
    print(f"Page for '{paper_note_template['title']}' added to the database.")


# 使用示例
pdf_path = 'src_file/doc1.pdf'  # PDF文件路径
# 调用函数
# READ .ENV FILE
load_dotenv(override=True)

notion = Client(auth=os.environ.get("NOTION_TOKEN"))

paper_note_template = get_children_blocks(pdf_path)

add_papers_to_notion_database(os.environ.get(
    "DATABASE_ID"), paper_note_template)
