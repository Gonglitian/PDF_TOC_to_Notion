from notion_client import Client
from dotenv import load_dotenv
import os
from utils import add_blocks_to_page, assemble_page_block_object


if __name__ == '__main__':
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
        page_id = page['id']
        # todo 如果page已经有children，就不添加
        Title_of_paper = page['properties']['Title']['rich_text'][0]['text']['content']
        pdf_path = CNKI_PDF_path_dict.get(Title_of_paper, None)
        if pdf_path is None:
            print(f"没有找到{Title_of_paper}的PDF文件")
            continue
        children_blocks = get_children_blocks(pdf_path)
        print(children_blocks)
        pass
