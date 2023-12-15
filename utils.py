from notion_client import Client


papers = [
    {
        "title": "Paper 1 Title",
        "toc": ["Introduction", "Method", "Results", "Discussion", "Conclusion"]
    },
    {
        "title": "Paper 2 Title",
        "toc": ["Background", "The Study", "Analysis", "Findings", "Summary"]
    },
    # ...更多论文数据
]

# 初始化Notion客户端
notion = Client(auth="secret_uOyI4EWqT2v3Hi2r0LA6N8s7oBArgAaIZbBt9y3Rdzc")


def add_papers_to_notion_database(database_id, papers):
    for paper in papers:
        # 创建Notion数据库页面
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": paper["title"],  # 论文标题
                            },
                        },
                    ],
                },
                # 如果数据库有其他属性，可以在这里添加
            },
            children=[
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": item,  # 目录项
                                },
                            },
                        ],
                    },
                } for item in paper["toc"]  # 为目录中的每一项创建一个列表项
            ],
        )
        print(f"Page for '{paper['title']}' added to the database.")


# 调用函数
database_id = "52ab0b36254d45aabf999e8bc8b02366"  # 替换为你的数据库ID
add_papers_to_notion_database(database_id, papers)
