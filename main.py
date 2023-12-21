from notion_client import Client
from utils import NotionUploader
import configparser
import os


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    PAPER_DATABASE_ID = config["NOTION"]["PAPER_DATABASE_ID"]
    PDF_DIR_PATH = r"E:\2023Fall\毕业设计\ref\论文"
    notion = Client(auth=config["NOTION"]["NOTION_TOKEN"])
    NotionUploader = NotionUploader(notion)

    CNKI_PDF_path_dict = {}  # {title: path}
    # 对本地文件夹中的pdf文件进行遍历
    for file in os.listdir(PDF_DIR_PATH):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIR_PATH, file)
            # add path to dict
            CNKI_PDF_path_dict[file.split("_")[0]] = pdf_path

    # 列出数据库中所有页面
    response = notion.databases.query(PAPER_DATABASE_ID)
    for page in response["results"]:
        # 获取页面ID和标题
        page_id = page["id"]
        paper_title = page["properties"]["Title"]["rich_text"][0]["text"]["content"]
        # 根据标题找到对应的PDF文件
        pdf_path = CNKI_PDF_path_dict.get(paper_title, None)
        if pdf_path is None:
            print(f"在PDF_DIR_PATH中没有找到`{paper_title}.pdf`")
            continue
        # 获取PDF文件目录
        children_blocks = NotionUploader.get_children_blocks(pdf_path)
        # 如果没有目录，就跳过
        if children_blocks is None:
            continue
        NotionUploader.upload_blocks_to_page(page_id, children_blocks)
