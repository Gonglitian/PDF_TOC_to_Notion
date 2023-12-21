# 示例字典树
def get_block(blocks):
    for block in blocks:
        children_block = block.get("children")
        if children_block == None:
            return []
        return [
            {
                "object": "block",
                "bulleted_list_item": {
                    "rich_text": [
                        {
                            "text": {
                                "content": block["content"],
                            },
                        }
                    ],
                    "children": get_block(children_block),
                },
            }
        ]


all_blocks = [
    {
        "content": "1",
        "children": [
            {"content": "1.1", "children": []},
            {"content": "1.2", "children": []},
        ],
    },
    {"content": "bat", "children": []},
]

print(get_block(all_blocks))
