# PDF_TOC_to_Notion

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
按照`.env.template`，在项目根目录下创建`.env`文件，填入你的`NOTION_TOKEN`和`PAPER_DATABASE_ID`
## 2.运行main.py

# TODO
- [x] 期刊文章用ChatGPT提取主要内容
- [x] 硕博论文对于每一章用ChatGPT提取主要内容(每一章当成一篇期刊论文)
- [ ] 整理代码
  - [ ] 串联总结功能和上传功能
  - [ ] `uploader.py`代码优化，建议重构
  - [ ] 函数注释，类型
  - [ ] 更新`requirements.txt`
