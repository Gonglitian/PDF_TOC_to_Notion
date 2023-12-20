# todo 加入更多block_type常数
from pprint import pprint
from dotenv import load_dotenv
from notion_client import Client
import fitz  # PyMuPDF
from typing import List, Tuple, Any
from constant import *
import openai
from prompt import *

from mistletoe.block_token import BlockToken, tokenize
import itertools
from mistletoe import span_token
from md2notion.NotionPyRenderer import NotionPyRenderer


class Document(BlockToken):
    """
    文档标记。
    """

    def __init__(self, lines):
        # 如果传入的是字符串，则按行分割为列表
        if isinstance(lines, str):
            lines = lines.splitlines(keepends=True)

        # 确保每行都以换行符结尾
        lines = [line if line.endswith(
            '\n') else '{}\n'.format(line) for line in lines]

        # 在 "$\n" 上方和下方添加换行符
        new_lines = []  # 存储处理后的行列表
        temp_line = None  # 临时存储行的变量
        triggered = False  # 标志变量，表示是否触发了 "$\n"

        for line in lines:
            # 如果行内只包含空格和换行符，则跳过该行
            if not triggered and '$\n' in line:
                temp_line = [None, line, None]  # 用于存储 "$\n" 相关的行
                triggered = True
            elif triggered:
                temp_line[1] += line
                if '$\n' in line:
                    temp_line[2] = '\n'
                    new_lines.append(temp_line)  # 将处理后的行添加到列表中
                    temp_line = None
                    triggered = False
            else:
                new_lines.append([None, line, None])  # 将其他行添加到列表中

        if temp_line is not None:
            new_lines.append(temp_line)  # 处理最后一行

        # 将列表展开为一维，并过滤掉空行
        new_lines = list(itertools.chain(*new_lines))
        new_lines = list(filter(lambda x: x is not None, new_lines))
        new_lines = ''.join(new_lines)  # 将行连接为字符串
        lines = new_lines.splitlines(keepends=True)  # 将字符串按行分割为列表
        lines = [line if line.endswith('\n') else '{}\n'.format(
            line) for line in lines]  # 确保每行都以换行符结尾

        self.footnotes = {}  # 存储脚注的字典
        global _root_node
        _root_node = self  # 设置全局变量 _root_node
        span_token._root_node = self  # 设置 span_token 类的 _root_node
        self.children = tokenize(lines)  # 对行进行标记化处理，生成子标记列表
        span_token._root_node = None  # 清除 span_token 类的 _root_node
        _root_node = None  # 清除全局变量 _root_node





class NotionUploader:
    def __init__(self, config):
        self.config = config
        self.notion_client = None
        self.notion_database_id = None
        self.init_client()

    def init_client(self):
        self.notion_client = Client(auth=self.config.get(
            'Notion', 'NOTION_TOKEN'))
        self.notion_database_id = self.config.get(
            'Notion', 'PAPER_DATABASE_ID')

    def upload_markdown_to_page(self, page_id, children_blocks):
        # 检查是否有子块
        if self.has_children_blocks(page_id):
            return

        # 添加子块
        self.notion_client.blocks.children.append(
            block_id=page_id,
            children=children_blocks,
        )
        print(f"Blocks added to page: {page_id}")

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

    def upload_to_page(self, page_id, markdown_content):
        self.notion_client.blocks.children.append(
            block_id=page_id,
            children=[
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [
                            {
                                'type': 'text',
                                'text': {
                                    'content': markdown_content
                                }
                            }
                        ]
                    }
                }
            ],
        )
        pass

    @staticmethod
    def markdown_to_notion_block():

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
