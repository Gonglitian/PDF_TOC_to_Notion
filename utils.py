# todo 加入更多block_type常数
from pprint import pprint
from dotenv import load_dotenv
from notion_client import Client
import fitz  # PyMuPDF
from typing import List, Tuple, Any
from constant import *
import openai
from prompt import *


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
    def __init__(self, config):
        self.current_pdf = None
        self.config = config
        self.api_pool = []
        self.current_api_index = 0
        self.summary_model = None
        self.api_init()

    def api_init(self):
        openai.api_base = self.config.get('OpenAI', 'OPENAI_API_BASE')
        self.api_pool = self.config.get('OpenAI', 'OPENAI_API_KEYS')[
            1:-1].replace('\'', '').split(',')

        # prevent short strings from being incorrectly used as API keys.
        self.api_pool = [api.strip()
                         for api in self.api_pool if len(api) > 20]
        self.summary_model = self.config.get('OpenAI', 'CHATGPT_MODEL')

    def get_ai_summary(self, title=None, content: str = None, content_type: str = None) -> str:
        self.switch_api_key()
        # print(content)
        prompt = self.get_prompt(title, content, content_type)
        response = openai.ChatCompletion.create(
            model=self.summary_model,
            # prompt需要用英语替换，少占用token。
            messages=prompt,
        )
        self.show_response_info(response)
        result = ''
        for choice in response.choices:
            result += choice.message.content
        return result

    def get_degree_prompt(self):
        pass

    def get_journal_prompt(self):
        pass

    def switch_api_key(self):
        openai.api_key = self.api_pool[self.current_api_index]
        self.current_api_index += 1
        self.current_api_index = 0 if self.current_api_index >= len(
            self.api_pool) - 1 else self.current_api_index

    def show_response_info(self, response):
        print("prompt_token_used:", response.usage.prompt_tokens,
              "completion_token_used:", response.usage.completion_tokens,
              "total_token_used:", response.usage.total_tokens)
        print("response_time:", response.response_ms / 1000.0, 's')

    def start(self, pdf_paths: List[str] | str):
        content_dict = {}
        for pdf_path in pdf_paths:
            try:
                self.current_pdf = fitz.open(pdf_path)
            except Exception as e:
                print(f"无法打开PDF文件: {e}")
                return None
            # 获取PDF文件目录
            toc: List[Tuple[int, str, int]
                      ] = self.current_pdf.get_toc(simple=True)
            if toc:
                content_dict = self.get_content_by_toc(toc)
            else:
                content_dict = {pdf_path.split(
                    '/')[-1].split('\\')[-1].split('.')[0]: self.get_all_text_in_pdf()}
            markdown_content = self.summary(content_dict)
            self.format_summary(markdown_content)
            self.export_to_markdown(markdown_content)

    def get_all_text_in_pdf(self) -> str:
        return ' '.join([page.get_text()
                         for page in self.current_pdf])

    def get_content_by_toc(self, toc: List[Tuple[int, str, int]]) -> dict:
        # 根据toc 获取每个章节的页码
        toc = [(level, title, page)
               for level, title, page in toc if level == 1]

        section_with_content = {}  # {title: content}
        last_page_index = 0
        # 遍历toc_info，获取每个章节的内容
        for index, (level, title, page_index) in enumerate(toc):
            # 考虑最后一个章节的情况，如果是最后一个章节，则直接截取到最后一页
            if index == len(toc) - 1:
                section_with_content[title] = self.get_section_content(
                    last_page_index, self.current_pdf.page_count)
                break
            # 考虑参考文献和致谢的情况，如果是参考文献或致谢，则跳出循环
            if title == "参考文献" or title == "致谢":
                break
            # 考虑中文学位论文既有双语摘要的情况,如果是摘要，且下一个章节是英文摘要，则跳过
            if title == "摘要" and toc[index+1][1].upper() == "ABSTRACT":
                continue
            # 如果是摘要则只截取2页内容
            if title == "摘要" or title.upper() == "ABSTRACT":
                section_with_content[title] = self.get_section_content(
                    page_index, page_index+1)
                continue
            # 获取两个page_index之间的内容
            section_with_content[title] = self.get_section_content(
                page_index, toc[index+1][2])
            last_page_index = page_index
        # send each item in section_with_content to gpt
        return section_with_content

    def get_section_content(self, start_page_index, end_page_index) -> str:
        # 打开PDF文件
        text = ""
        # 遍历页码范围
        for page_num in range(start_page_index, end_page_index):
            page = self.current_pdf.load_page(page_num-1)
            text += page.get_text()
        return text.replace('\n', ' ')

    def summary(self, cotent_dict: dict) -> list[str]:
        content_type = ''
        summary_list = []
        if len(cotent_dict) == 1:
            content_type = 'journal'
        else:
            content_type = 'degree'
        for i, (title, content) in enumerate(cotent_dict.items()):
            summary = self.get_ai_summary(title, content, content_type)
            summary_list.append(summary)
            # note for test
            # if i == 1:
            #     break
        return summary_list

    def format_summary(self, markdown_content):
        pass

    def get_prompt(self, title: str = None, content: str = None, content_type: str = None) -> str:
        if content_type == 'degree':
            return get_degree_prompt(title, content)
        elif content_type == 'journal':
            return get_paper_prompt(title, content)
        else:
            return get_general_prompt()

    # note for test
    def export_to_markdown(self, text_list: list, file_name="./result_gpt4.md", mode='w'):
        with open(file_name, mode, encoding="utf-8") as f:
            f.write('[TOC]\n')
            f.write('\n'.join(text_list))
            # 定义一个方法，打印出读者信息
