import copy
import json
import os
import re
import sys
import fitz
import pdfkit
import yaml
import pypandoc
from PyPDF2 import PdfFileMerger
from pathlib import Path
from shutil import copyfile
from lxml import etree, html
from anytree import Node
from anytree import RenderTree


class MD2PDF:
    def __init__(self, *args, **kwargs):
        self.item_root = None
        self.item_tree = None
        self.item_list = []
        self.dir_list = None
        self.title_root = None
        self.title_tree = None
        self.title_list = None
        self.toc = None
        self.path_dict = {}
        self.resource_list = ('highlight.css', 'highlight.js', 'cover.html',
                              'statement.html', 'logo.png', 'style.css', 'smalllogo.png', 'header.html')
        for each_param in kwargs:
            setattr(self, each_param, kwargs[each_param])
        # 此处判断是否是以打包可执行程序运行
        # 如果是 则指定wkhtmltopdf的路径
        if hasattr(sys, '_MEIPASS') and getattr(self, 'platform_name', None) == 'Windows':
            self.wkhtmltopdf_config = pdfkit.configuration(wkhtmltopdf=f'{sys._MEIPASS}\\bin\\wkhtmltopdf.exe')
        self.pdfkit_options = {
            'page-size': 'A4',
            'encoding': "UTF-8",
            'quiet': '',  # 删除默认输出
            'margin-top': '1.2in',
            'margin-right': '1.2in',
            'margin-bottom': '1.2in',
            'margin-left': '1.2in',
            'enable-local-file-access': '--enable-local-file-access',  # 允许本地文件加载其他的本地文件
        }

    def merged_md_to_html(self):
        title = getattr(self, 'title')
        source_path = getattr(self, 'source_path')
        merged_md_path = str(Path('temp').joinpath(title + '.md'))
        output_html_path = str(Path('temp').joinpath(title + '_temp.html'))
        target_html_path = str(Path('temp').joinpath(title + '.html'))
        pypandoc.convert_file(merged_md_path, 'html', format='md', outputfile=output_html_path, encoding='utf-8')
        target_html_content = '<head><meta charset="UTF-8">' \
                              f'<link rel="stylesheet" type="text/css" href="./style.css">' \
                              f'<link href="./highlight.css" rel="stylesheet">' \
                              f'<script src="./highlight.js"></script>' \
                              '<script >hljs.initHighlightingOnLoad();</script></head><body style="font-family: jcfont">'
        
        with open(output_html_path, 'r', encoding='utf-8') as temp_html:
            target_html_content += temp_html.read()
        target_html_content += '</body>'
        # target_html_content = re.sub(r'src=.*/assets',
        #                              'src="' + re.sub(r"\\", '/', str(Path(source_path).absolute())) + "/assets",
        #                              target_html_content)
        target_html_content = re.sub(r'<figcaption.*?figcaption>', '', target_html_content)
        href_list = re.findall(r'<a\shref=\"#.*?>.*\s*</a>', target_html_content)
        for each_href in href_list:
            target_str = re.findall(r'>.*<', each_href)[0][1:-1] if len(re.findall(r'>.*<', each_href)) > 0 else ''
            target_html_content = re.sub(r'<a\shref=\"#.*?>.*</a>', target_str, target_html_content, 1)
        target_html_content = re.sub(r'<a\shref=\"#.*?>.*</a>', '', target_html_content)
        # target_html_content = re.sub(r'</a>', '', target_html_content)
        target_html_content = re.sub(r'size=\'4\'', '', target_html_content)
        target_html_content = re.sub(r'<h1', '<div style="page-break-after:always;"></div><h1', target_html_content)
        if getattr(self, 'disable_page_break', False):
            target_html_content = re.sub(r'page-break-after:always', 'page-break-after:avoid', target_html_content)
        target_html_content = re.sub(r'<img', '<img style="max-width: 100% !important"', target_html_content)
        target_html_content = re.sub(r'(<span id="cb.*?")',
                                     r'\1 style="width: 700px;display: block;word-break: break-word;white-space: normal;"',
                                     target_html_content)
        with open(target_html_path, 'w', encoding='utf-8') as target_html:
            target_html.write(target_html_content)

    def html_to_pdf(self):
        options = {
            'outline': None,  # 为None时表示确定，生成侧边标签导航
            'outline-depth': '5',  # 侧边标签导航层级深度
            'minimum-font-size': 10,  # 最小字体大小
            'header-html': './temp/header.html',  # 引入页眉页面
            'header-right': getattr(self, 'doc_type', '测试文档'),  # 页眉右侧文字
            'header-font-size': 10,  # 页眉字体
            'header-spacing': '10',  # 页眉距离内容宽度
            'footer-font-size': 10,  # 页脚字体
            'header-line': None,  # 为None时表示确定，生成页眉下的线
            'footer-center': '[page]',  # 页脚中间内容为页码
            'disable-smart-shrinking': '--disable-smart-shrinking'
        }
        options.update(self.pdfkit_options)
        title = getattr(self, 'title')
        source_html_path = str(Path('temp').joinpath(title + '.html'))
        output_pdf_path = str(Path('temp').joinpath(title + '_content.pdf'))
        pdfkit.from_file(source_html_path, output_pdf_path, options=options,
                         configuration=getattr(self, 'wkhtmltopdf_config', None))

    def get_content_toc(self):
        title = getattr(self, 'title')
        content_pdf_path = str(Path('temp').joinpath(title + '_content.pdf'))
        temp_document = fitz.open(content_pdf_path)
        # modified by lisj 新版本函数名改了
        # 若老版本有问题的话就升新版本吧
        # temp_ToC = temp_document.getToC()
        temp_ToC = temp_document.get_toc()
        self.toc = temp_ToC
        temp_document.close()
        target_html = f'<head><meta charset="UTF-8"><link rel="stylesheet" type="text/css" href="./style.css"></head>' \
                      '\n<span style="color:rgb(52,90,138);font-size: 40px; font-family: jcfont;">目录</span>'
        temp_title_list = copy.deepcopy(self.title_list)
        # Issue Improvement: 待 增加目录前导符自定义 目前默认 '. '
        point_line = '· ' * 100
        for each_list in temp_ToC:
            # Issue Feature: 标题等级参数作用于PDF目录 并增加缩进 单位20px每级 一级目录不缩进 Done
            # Issue Feature: 固定二级目录改为自定义，默认二级 默认值一般由CLI前端定义
            # Issue Improvement: 待 将固定的样式文本、wk的配置等从业务块中抽出
            if each_list[0] - 1 in range(int(getattr(self, 'title_level', 2))):
                for title_index, each_title in enumerate(temp_title_list):
                    if each_list[1] in each_title:
                        title_content = '<span style="word-break: keep-all;white-space: normal;' \
                                        'margin-top: -28px;margin-left:' \
                                        + str(getattr(self, 'catalog_indent', 25) * (each_list[0]) - 1) \
                                        + 'px;font-size:20px; display:inline; color: ' \
                                          'black;background-color: #ffffff;font-family: jcfont">' \
                                        + each_title + point_line + '</span>'
                        title_content = '<div class="des"><span style="width: 100%;height:30px;overflow: hidden;font-family: jcfont' \
                                        'display: inline-block;margin-top:5px">' \
                                        '<div style="float:right;background-color:' \
                                        'white;margin:5px">{1}</div>{0}</span></div>'. \
                            format(title_content, each_list[2])
                        target_html += title_content
                        temp_title_list.pop(title_index)
                        break
        output_catalog_html_path = str(Path('temp').joinpath(title + '_catalog.html'))
        with open(output_catalog_html_path, 'w', encoding='utf-8') as catalog_writer:
            catalog_writer.write(target_html)
        options = {
            'minimum-font-size': 15,
            'header-html': str(Path('temp').joinpath('header.html')),
            'header-right': getattr(self, 'doc_type', '测试文档'),
            'header-font-size': 10,
            'header-spacing': '10',
            'header-line': None,  # 为None时表示确定，生成页眉下的线
        }
        options.update(self.pdfkit_options)
        pdfkit.from_file('./temp/' + self.item_list[0] + '_catalog.html',
                         './temp/' + self.item_list[0] + '_catalog.pdf', options=options,
                         configuration=getattr(self, 'wkhtmltopdf_config', None))

    def generate_home_page(self):
        options = {
            'minimum-font-size': 15
        }
        options.update(self.pdfkit_options)
        home_page = html.parse(str(Path('temp').joinpath('cover.html')), parser=etree.HTMLParser(encoding='utf-8'))
        # title = getattr(self, 'title', '测试产品白皮书')
        # version = getattr(self, 'version', 'V1.0')
        # doc_type = getattr(self, 'doc_type', '测试文档')
        # copyright = getattr(self, 'copyright', '测试版权所有人')
        # home_page.xpath('//*[@id="title"]')[0].text = self.item_list[0]
        # home_page.xpath('//*[@id="version"]')[0].text = self.version
        with open(Path('temp').joinpath('temp_cover.html'), 'w', encoding='utf-8') as home_page_writer:
            replaced_html_content = etree.tostring(home_page, encoding='utf-8').decode('utf-8')
            # replaced_html_content = re.sub(r'{{title}}', title, replaced_html_content)
            # replaced_html_content = re.sub(r'{{version}}', version, replaced_html_content)
            # replaced_html_content = re.sub(r'{{doc_type}}', doc_type, replaced_html_content)
            # replaced_html_content = re.sub(r'{{copyright}}', copyright, replaced_html_content)
            meta_info_dict = getattr(self, 'meta_info_dict', {})
            for each_key in meta_info_dict:
                old_string = '{{' + str(each_key) + '}}'
                replaced_html_content = replaced_html_content.replace(old_string, meta_info_dict[each_key])
            home_page_writer.write(replaced_html_content)
        target_pdf_name = self.item_list[0] + '_cover.pdf'
        pdfkit.from_file('./temp/temp_cover.html', './temp/' + target_pdf_name, options=options,
                         configuration=getattr(self, 'wkhtmltopdf_config', None))
        if not getattr(self, 'disable_statement', False) and Path('./temp/statement.html').exists():
            print('生成扉页PDF')
            pdfkit.from_file('./temp/statement.html', './temp/' + self.item_list[0] + '_statement.pdf', options=options,
                             configuration=getattr(self, 'wkhtmltopdf_config', None))
        else:
            print('扉页已禁用！')

    def merge_pdf(self):
        product_name = self.item_list[0]
        pdf_list = ['./temp/' + product_name + '_cover.pdf',
                    './temp/' + product_name + '_statement.pdf',
                    './temp/' + product_name + '_catalog.pdf',
                    './temp/' + product_name + '_content.pdf']
        pdf_merger = PdfFileMerger()
        for each_pdf in pdf_list:
            if each_pdf.endswith('_statement.pdf') and getattr(self, 'disable_statement', False):
                continue
            if Path(each_pdf).exists():
                pdf_merger.append(each_pdf, import_bookmarks=False)
        altogether_pdf_name = product_name + '_altogether.pdf'
        pdf_merger.write('./temp/' + altogether_pdf_name)
        pdf_merger.close()

        pdf_without_toc = fitz.open('./temp/' + altogether_pdf_name)
        toc_pdf = fitz.open('./temp/' + product_name + '_catalog.pdf')
        cover_pdf = statement_pdf = None

        if Path('./temp/' + product_name + '_cover.pdf').exists():
            cover_pdf = fitz.open('./temp/' + product_name + '_cover.pdf')
        if Path('./temp/' + product_name + '_statement.pdf').exists() and not getattr(self, 'disable_statement', False):
            statement_pdf = fitz.open('./temp/' + product_name + '_statement.pdf')
        toc_offset = (cover_pdf.pageCount if cover_pdf is not None else 0) + (
            statement_pdf.pageCount if statement_pdf is not None else 0) + toc_pdf.pageCount
        final_toc_list = []
        for each_list in self.toc:
            each_list[2] = each_list[2] + toc_offset
            final_toc_list.append(each_list)

        # modified by lisj 新版本函数名改了
        # 若老版本有问题的话就升新版本吧
        # pdf_without_toc.setToC(final_toc_list)
        pdf_without_toc.set_toc(final_toc_list)
        target = Path(getattr(self, 'target_path')).joinpath(
            product_name + getattr(self, 'version', 'V1.0') + getattr(self, 'doc_type',
                                                                      '测试文档') + '.pdf')
        pdf_without_toc.save(target)
        pdf_without_toc.close()
        toc_pdf.close()
        if cover_pdf is not None:
            cover_pdf.close()
        if statement_pdf is not None:
            statement_pdf.close()

    def get_dir_list(self, current_path):
        if Path(current_path).exists():
            for directory in Path(current_path).iterdir():
                if directory.is_dir() and directory.name != 'assets' and directory.name != 'temp' not in directory.name:
                    self.dir_list.append(directory)
                    self.get_dir_list(directory)

    def copy_temp_file(self):
        source_path = getattr(self, 'source_path')
        self.dir_list = []
        if Path(source_path).exists():
            self.dir_list.append(source_path)
            if not getattr(self, 'disable_recurrence'):
                self.get_dir_list(source_path)
            for each_dir in self.dir_list:
                for item in Path(each_dir).iterdir():
                    if item.name.endswith('.md'):
                        self.path_dict[item.stem] = str(item.absolute().parent.absolute()).replace('\\', '\\\\')
                        copyfile(str(item), './temp/' + item.name)

    def get_title_level(self, root, title, current_level=0):
        if root.name == title:
            return current_level
        elif root.children is not None:
            for child in root.children:
                level = self.get_title_level(child, title, current_level + 1)
                if level is not None:
                    return level

    def merge_md(self):
        source_path = getattr(self, 'source_path')
        target_md_file = Path('temp').joinpath(self.item_root.name + '.md')
        with open(target_md_file, 'w', encoding='utf-8') as md_write:
            for each in self.item_list:
                if each == self.item_list[0]:
                    continue
                source_file = Path("temp/").joinpath(each + '.md')
                file_level = self.get_title_level(self.item_root, each)
                # print(source_file, file_level)
                if not Path(source_file).exists():
                    md_write.write('\n\n' + '#' * file_level + ' ' + each + '\n')
                else:
                    with open(source_file, 'r', encoding='utf-8') as md_read:
                        offset = 1
                        temp_line_counter = 0
                        file_lines = md_read.readlines()
                        ignore_lines = []
                        ignore_flag = False
                        for line_index, each_line in enumerate(file_lines):
                            if line_index > 10:
                                break
                            if each_line.startswith('---'):
                                ignore_lines.append(line_index)
                                ignore_flag = not ignore_flag
                                continue
                            if ignore_flag:
                                ignore_lines.append(line_index)
                                continue
                            if each_line.startswith('#'):
                                offset = len(each_line.split(' ')[0])
                                # if each != each_line.split(' ')[1][:-1]:
                                #     md_write.write('\n\n' + '#' * file_level + ' ' + each + '\n')
                                break
                            temp_line_counter += 1
                        # print(offset)
                        continue_flag = False
                        special_block_flag = False
                        for line_index, each_line in enumerate(file_lines):
                            if line_index in ignore_lines:
                                continue
                            if each_line.startswith('```') or each_line.startswith('~~~'):
                                continue_flag = not continue_flag
                                md_write.write('\n')
                                md_write.write(each_line)
                            elif each_line[0] in ('+', '-', '|', '1') and not special_block_flag:
                                md_write.write('\n')
                                md_write.write(each_line)
                                special_block_flag = not special_block_flag
                            elif special_block_flag and each_line[0] not in ('+', '-', '|', '1'):
                                md_write.write('\n')
                                if each_line.startswith('#'):
                                    md_write.write('#' * (file_level - offset) + each_line)
                                else:
                                    md_write.write(each_line)
                                special_block_flag = not special_block_flag
                            elif each_line.startswith('#') and not continue_flag:
                                md_write.write('\n\n')
                                md_write.write('#' * (file_level - offset) + each_line)
                                md_write.write('\n')
                            elif each_line.startswith('[comment]'):
                                continue
                            else:
                                modified_line = each_line
                                if re.findall(r'!\[.*]\(', each_line):
                                    modified_line = re.sub(r'!\[.*\]\(', r"![](", each_line)
                                    modified_line = modified_line.replace("![](./", f"![]({str(Path(self.path_dict[each]))}/")
                                    modified_line = modified_line.replace("![](../",
                                                                          f"![]({str(Path(self.path_dict[each]))}/../")

                                if re.findall(r'<img src=', each_line):
                                    modified_line = modified_line.replace("<img src=\"./",
                                                                          f"<img src=\"{str(Path(self.path_dict[each]))}/")
                                    modified_line = modified_line.replace("<img src=\"../",
                                                                          f"<img src=\"{str(Path(self.path_dict[each]))}/../")
                                md_write.write(modified_line)
                        md_write.write('\n\n')
        if getattr(self, 'export_type', 'pdf').lower() in ('pdf', 'both', 'all'):
            print(f'MarkDown 转为 HTML')
            self.merged_md_to_html()
        print(f'已合并MarkDown生成标题序号，序号等级为 {getattr(self, "title_level")}')
        self.generate_title_number(target_md_file)

    def generate_title_number(self, file_name):
        self.title_list = []
        previous_level = 0
        self.title_root = Node(self.item_list[0])
        current_node = self.title_root
        continue_flag = False
        title_level = getattr(self, 'title_level', 2)
        with open(file_name, 'r', encoding='utf-8') as temp_file:
            final_content = temp_file.readlines()
        line_counter = 0
        warn_flag = False
        for each_line in final_content:
            if each_line.startswith('```') or each_line.startswith('~~~'):
                continue_flag = not continue_flag
            if continue_flag:
                line_counter += 1
                continue
            if each_line.startswith('#'):
                current_level = len(each_line.split(' ')[0])
                title_name_list = each_line.split(' ')
                if len(title_name_list) == 1:
                    right_line = ''
                    current_level = 0
                    for letter in each_line:
                        if letter == '#':
                            current_level += 1
                            right_line += '#'
                    right_line = right_line + ' ' + each_line[current_level:]
                    final_content[line_counter] = right_line
                title_name = ' '.join(title_name_list[1:])
                title_name = title_name[:-1]
                if previous_level < current_level:
                    if current_level - previous_level > 1:
                        warn_flag = True
                        previous_line = final_content[line_counter]
                        temp_line = ''
                        for i in range(current_level - previous_level - 1):
                            current_node = Node('填充标题', parent=current_node)
                            temp_line = temp_line + '\n' + '#' * (previous_level + i + 1) + ' 填充标题\n'
                        final_content[line_counter] = temp_line + '\n' + previous_line
                    current_node = Node(title_name, parent=current_node)
                elif previous_level == current_level:
                    current_node = Node(title_name, parent=current_node.parent)
                else:
                    temp_parent = current_node.parent
                    for i in range(previous_level - current_level):
                        temp_parent = temp_parent.parent
                    if temp_parent is None:
                        temp_parent = self.title_root
                    current_node = Node(title_name, parent=temp_parent)
                previous_level = current_level
            line_counter += 1
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(''.join(final_content))
        with open(file_name, 'r', encoding='utf-8') as f:
            final_content = f.readlines()
        self.title_tree = RenderTree(self.title_root)
        self.modify_title_tree(title_level, self.title_root.children)
        title_counter = 0
        line_counter = 0
        for each_line in final_content:
            if each_line.startswith('```') or each_line.startswith('~~~'):
                continue_flag = not continue_flag
            if continue_flag:
                line_counter += 1
                continue
            if each_line.startswith('#'):
                if len(each_line.split(' ')[0]) <= title_level:
                    final_content[line_counter] = '\n' + each_line.split(' ')[0] + ' ' + self.title_list[
                        title_counter] + '\n'
                    title_counter += 1
                    # print(each_line[:-1] + '----->' + final_content[line_counter][1:])
            line_counter += 1
        with open(file_name, 'w', encoding='utf-8') as final_md_writer:
            final_md_writer.write(''.join(final_content))
        if getattr(self, 'print_title_flag', False):
            print(self.title_tree)
        if getattr(self, 'export_type', 'pdf').lower() in ('docx', 'both', 'all'):
            print('导出Word文件')
            self.md_to_docx()
        # sys.exit(0)

    def md_to_docx(self):
        title = getattr(self, 'title', '测试')
        source_path = str(Path('temp').joinpath(title + '.md'))
        target_path = str(Path(getattr(self, 'target_path', 'output')).joinpath(title + '.docx'))
        pypandoc.convert_file(source_path, 'docx', format='md', outputfile=target_path, sandbox=False, encoding='utf-8')

    def modify_title_tree(self, max_level, node_list):
        if max_level > 0:
            num = 1
            for each_node in node_list:
                if each_node.parent == self.title_root:
                    each_node.name = str(num) + '. ' + each_node.name
                else:
                    each_node.name = each_node.parent.name.split(' ')[0] + str(num) + '. ' + each_node.name
                num += 1
                self.title_list.append(each_node.name)
                if each_node.children is not None:
                    self.modify_title_tree(max_level - 1, each_node.children)

    def clean_temp(self):
        for each in Path('temp').iterdir():
            # if str(each).split('\\')[1] not in self.resource_list:
            # modified by lisj - Linux/Mac的分隔符与Windows不同
            if os.path.basename(str(each)) not in self.resource_list and os.path.basename(str(each)) != 'font.ttf':
                os.remove(str(each))

    def get_item_list(self, root):
        self.item_list.append(root.name)
        if root.children is not None:
            for child in root.children:
                self.get_item_list(child)

    def get_sidebar_content(self):
        config_path = Path(getattr(self, 'config_path'))
        with Path.open(config_path, mode='r', encoding='utf-8') as f:
            content = f.readlines()
            for each_line in content:
                if len(re.findall(r'//', each_line)) > 0:
                    content.remove(each_line)
            content = ''.join(content)
            content = re.sub(r"'", "\"", content)
            # content = re.sub(r'(?<!")(\w*)(?!"):', r'"\1":', content)
            # modified by lisj - 匹配时连冒号后的空格一起匹配，否则遇到下面的情况会出问题：
            # repo: 'http://gitlab.jcinfo.com/consultation/solution/court/court-mp-solution/',
            content = re.sub(r'(?<!")(\w*)(?!"):\s', r'"\1": ', content)
            content = re.sub(r':.*=>', ':', content)
            # modified by lisj - 不应该是负1呀，把最后的花括号丢掉了
            # js_json = content[content.find('{'):-1]
            js_json = content[content.find('{'):content.rfind('}') + 1]
            js_json = yaml.load(js_json, yaml.FullLoader)
            sidebar_content = js_json['themeConfig']['sidebar']

            # Modified by lisj - 如果取出来的结果是List，需要特殊处理一下
            if isinstance(sidebar_content, list) and len(sidebar_content) > 0:
                setattr(self, 'sidebar_content', sidebar_content[0])
                setattr(self, 'sidebar_type', 'vuepress2')
            else:
                setattr(self, 'sidebar_content', sidebar_content)
                setattr(self, 'sidebar_type', 'vuepress1')
                if not hasattr(self, 'sidebar_key'):
                    self.conjecture_key_from_path()
            # print(sidebar_content)

    def conjecture_key_from_path(self):
        # 对于vuepress 1.x的配置，根据文档路径推测其sidebar_key
        # 以获取其配置内容
        source_path = getattr(self, 'source_path')
        sidebar_content = getattr(self, 'sidebar_content')
        temp_path = str(Path(source_path).absolute()) + '/'
        temp_path = re.sub(r'\\', '/', temp_path)
        for each_key in sidebar_content:
            if each_key == '/':
                continue
            if temp_path.endswith(each_key):
                setattr(self, 'sidebar_key', each_key)
                break
        else:
            # 未能获取sidebar_key
            print(f'source_path {temp_path}')
            print('未能获取sidebar_key')
            pass

    def get_key_from_path(self):
        # Modified by lisj
        # 这里应该不用这么麻烦，sidebar_content是个字典，title+link+children
        # 只有两种情况，title, 和 text
        sidebar_content = getattr(self, 'sidebar_content')
        if 'text' in sidebar_content.keys():
            setattr(self, 'sidebar_key', sidebar_content['text'])
        else:
            setattr(self, 'sidebar_key', sidebar_content['text'])
        # source_path = getattr(self, 'source_path')
        # sidebar_content = getattr(self, 'sidebar_content')
        # temp_path = source_path + '/'
        # temp_path = re.sub(r'\\', '/', temp_path)
        # for each_key in sidebar_content:
        #     # Modified by lisj - 这里应该取字典的值来判断，不应该用key来判断
        #     # if each_key == '/':
        #     each_val = sidebar_content[each_key]
        #     if each_val == '/':
        #         continue
        #     if temp_path.endswith(each_val):
        #         setattr(self, 'sidebar_key', each_val)
        #         break
        # else:
        #     pass

    def parse_config_sidebar(self):
        # Modified by lisj
        # 前面已经处理出干净的sidebar_content了
        sidebar_content = getattr(self, 'sidebar_content')[getattr(self, 'sidebar_key')][0] \
            if getattr(self, 'sidebar_type') == 'vuepress1' \
            else getattr(self, 'sidebar_content')
        meta_info_dict = {}
        for each_key in sidebar_content:
            if each_key == 'children':
                continue
            meta_info_dict[each_key] = sidebar_content[each_key]
            if each_key in ('title', 'doc_type', 'version', 'copyright') and sidebar_content[each_key]:
                setattr(self, each_key, sidebar_content[each_key])
            if each_key == 'text':
                setattr(self, 'title', sidebar_content['text'])
                meta_info_dict['title'] = sidebar_content['text']

        # modified by lisj - 有两种情况：title 和 text
        # if 'title' in sidebar_content.keys():
        #     self.item_root = Node(sidebar_content['title'])
        # elif 'text' in sidebar_content.keys():
        #     self.item_root = Node(sidebar_content['text'])

        self.item_root = Node(getattr(self, 'title'))
        self.get_children_config_sidebar(self.item_root, sidebar_content['children'])
        self.item_tree = RenderTree(self.item_root)
        if not hasattr(self, 'version'):
            setattr(self, 'version', 'V1.0')
        if not hasattr(self, 'doc_type'):
            setattr(self, 'doc_type', '产品白皮书')
        if not hasattr(self, 'copyright'):
            setattr(self, 'copyright', '长春嘉诚信息技术股份有限公司')
        for each_key in ('title', 'doc_type', 'version', 'copyright'):
            meta_info_dict[each_key] = getattr(self, each_key)
        setattr(self, 'meta_info_dict', meta_info_dict)

    def parse_config(self):
        config_path = Path(getattr(self, 'config_path', './config.json'))
        if Path(config_path).exists():
            if Path(config_path).suffix == '.json':
                with Path.open(config_path, mode='r', encoding='utf-8') as config_reader:
                    config = json.load(config_reader)
                    setattr(self, 'config', config)
                    meta_info_dict = {}
                    for each_key in config:
                        if each_key == 'children':
                            continue
                        if each_key in ('title', 'doc_type', 'version', 'copyright'):
                            # Issue Bug: Fixed
                            meta_info_dict[each_key] = config[each_key]
                            if not hasattr(self, each_key):
                                setattr(self, each_key, config[each_key])
                            else:
                                meta_info_dict[each_key] = getattr(self, each_key)
                            continue
                        meta_info_dict[each_key] = config[each_key]
                    setattr(self, 'meta_info_dict', meta_info_dict)
                    self.item_root = Node(getattr(self, 'title', '测试文档'))
                    self.get_children_config_json(self.item_root, config['children'])
                    self.item_tree = RenderTree(self.item_root)

    def get_children_config_sidebar(self, root, children):
        # 此处title指代不带后缀名的FileName, 后续匹配每个文档用
        for each in children:
            if isinstance(each, str):
                if each == "":
                    Node("README", parent=root)
                else:
                    Node(Path(each).stem, parent=root)
            elif isinstance(each, dict):
                # modified by lisj - 逻辑重新梳理一下：
                title = 'title'
                if 'title' in each.keys():
                    title = each['title']
                elif 'text' in each.keys():
                    title = each['text']
                if 'link' in each:
                    if each['link'] != '/':
                        title = Path(each['link']).stem
                    else:
                        title = 'README'
                elif 'path' in each:
                    if each['path'] != '/':
                        title = Path(each['path']).stem
                    else:
                        title = 'README'
                if 'children' in each:
                    head = Node(title, parent=root)
                    self.get_children_config_sidebar(head, each['children'])
                else:
                    Node(title, parent=root)

                # 不一定是'path' 也可能是'link'
                # if 'path' in each:
                #     Node(each['title'], parent=root)
                # elif 'children' in each:
                #     head = Node(each['title'], parent=root)
                #     self.get_children_config_sidebar(head, each['children'])
            elif isinstance(each, list):
                Node(Path(each[0]).stem if each[0] != '' else each[1], root)
                # Node(each[1], root)

    def get_children_config_json(self, root, children):
        for each in children:
            if isinstance(each, str):
                if each == "":
                    Node("README", parent=root)
                else:
                    Node(each, parent=root)
            elif isinstance(each, dict):
                title = 'title'
                if 'title' in each.keys():
                    title = each['title']
                elif 'text' in each.keys():
                    title = each['text']
                if 'link' in each:
                    if each['link'] != '/':
                        title = Path(each['link']).stem
                    else:
                        title = 'README'
                elif 'path' in each:
                    if each['path'] != '/':
                        title = Path(each['path']).stem
                    else:
                        title = 'README'
                if 'children' in each:
                    head = Node(title, parent=root)
                    self.get_children_config_json(head, each['children'])
                else:
                    Node(title, parent=root)

    def fill_name(self, origin_name):
        for each_item in Path('temp').iterdir():
            if each_item.stem.startswith(origin_name):
                return each_item.stem
        return origin_name

    def get_name_level(self, origin_name: str):
        level = 0
        for each in origin_name.split('0'):
            if each == '':
                level += 1
            else:
                return self.fill_name(each), level if level > 0 else 1

    def build_item_tree(self):
        if hasattr(self, 'doc_sequence'):
            doc_sequence = getattr(self, 'doc_sequence')
            doc_sequence = ['README'] if len(doc_sequence) == 0 else doc_sequence
            previous = (self.item_root, 0)
            for each_doc in doc_sequence:
                each_doc, level = self.get_name_level(each_doc)
                previous_level = previous[1]
                if level == previous_level:
                    previous = (previous[0].parent, previous[1])
                elif level > previous_level:
                    for i in range(level - previous_level - 1):
                        previous = (Node('填充标题', previous[0]), previous[1] + 1)
                else:
                    for i in range(previous_level - level + 1):
                        previous = (previous[0].parent, previous[1] - 1)
                previous = (Node(each_doc, previous[0]), level)
        else:
            if Path('temp').joinpath('README.md').exists():
                Node('README', self.item_root)
            for each_item in Path('temp').iterdir():
                if each_item.suffix == '.md' and each_item.name.lower() != 'readme.md':
                    Node(each_item.stem, self.item_root)

    def process(self):
        print(f'开始导出进程\n导出类型为 {getattr(self, "export_type")}\n导出文档保存目录为 {getattr(self, "target_path")}')
        print('清理临时文件')
        self.clean_temp()
        print(f'准备资源文件及各个文档')
        self.copy_temp_file()
        config_path = None
        if hasattr(self, 'config_path'):
            config_path = getattr(self, 'config_path')
        if config_path is not None and Path(config_path).exists():
            if Path(config_path).suffix == '.json':
                setattr(self, 'config_type', 'json')
                self.parse_config()
            elif Path(config_path).suffix == '.js':
                setattr(self, 'config_type', 'vuepress')
                self.get_sidebar_content()

                self.parse_config_sidebar()
            print(f'开始解析配置文件，配置文件类型为 {getattr(self, "config_type", "json").upper()}')
        else:
            title = getattr(self, 'title', '测试文档')
            setattr(self, 'title', title)
            self.item_root = Node(title)
            self.item_tree = RenderTree(self.item_root)
            self.build_item_tree()
            meta_info_default = {
                'title': '测试文档',
                'version': 'V1.0',
                'doc_type': '产品白皮书',
                'copyright': '长春嘉诚信息技术股份有限公司'
            }
            meta_info_dict = {}
            for each_key in meta_info_default:
                setattr(self, each_key, getattr(self, each_key, meta_info_default[each_key]))
                meta_info_dict[each_key] = getattr(self, each_key)
            setattr(self, 'meta_info_dict', meta_info_dict)

        if not hasattr(self, "title"):
            setattr(self, "title", "测试文档")

        print(f'文档标题：《{getattr(self, "title")}》')
        if getattr(self, 'print_item', False):
            print(self.item_tree)
        print(f'获取文档列表')
        self.get_item_list(self.item_root)
        print(f'开始合并 MarkDown')
        self.merge_md()
        if getattr(self, 'export_type', 'pdf').lower() in ('pdf', 'both', 'all'):
            print('导出正文PDF')
            self.html_to_pdf()
            print('生成目录页PDF')
            self.get_content_toc()
            print('生成PDF封面')
            self.generate_home_page()
            print('合并所有的PDF')
            self.merge_pdf()
        print('导出完成！')
        if not getattr(self, 'Debug', False):
            print('清理临时文件')
            self.clean_temp()
        else:
            print('>>>调试模式，不清理临时文件！<<<')
