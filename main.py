import fitz  # PyMuPDF
from notion_client import Client
notion = Client(auth="secret_uOyI4EWqT2v3Hi2r0LA6N8s7oBArgAaIZbBt9y3Rdzc")


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
            # 如果数据库有其他属性，可以在这里添加
        },
        children=paper_note_template["children_blocks"],
    )
    print(f"Page for '{paper_note_template['title']}' added to the database.")

# def save_markdown(markdown_content, output_path):
#     if markdown_content is None:
#         print("没有提取到任何标题，Markdown文件未创建。")
#         return

#     with open(output_path, 'w', encoding='utf-8') as md_file:
#         md_file.write('\n'.join(markdown_content))
#     print(f"Markdown文件已保存到：{output_path}")


# 使用示例
pdf_path = 'src_file\doc1.pdf'  # PDF文件路径
# markdown_output_path = 'thesis_headings.md'  # Markdown输出文件路径
# headings = extract_headings(pdf_path)
# save_markdown(headings, markdown_output_path)
# 调用函数
database_id = "52ab0b36254d45aabf999e8bc8b02366"  # 替换为你的数据库ID
paper_note_template = get_children_blocks(pdf_path)
add_papers_to_notion_database(database_id, paper_note_template)
