# PDF_ToC_to_Notion

一个将本地硕博论文PDF的TOC导入Notion数据库中的Python脚本

# 使用
## 1.环境搭建
```bash
git clone https://github.com/Gonglitian/PDF_ToC_to_Notion.git
```

```bash
cd ./PDF_ToC_to_Notion
```

```bash
pip install -r requirements.txt
```
## 2.运行脚本
1. 按照`.env.template`，在项目根目录下创建`.env`文件，填入`NOTION_TOKEN`和`PAPER_DATABASE_ID`
2. 运行main.py