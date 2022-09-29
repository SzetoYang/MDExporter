import argparse
import os
import platform
import sys
from traceback import format_exc
from pathlib import Path
from shutil import copyfile
import Style
from md2pdf.md2pdf import MD2PDF


def prepare_resource(resource_list, *args, **kwargs):
    for each in resource_list:
        if Path('./templates/' + each).exists():
            copyfile('./templates/' + each, './temp/' + each)
        elif hasattr(sys, '_MEIPASS') and Path(sys._MEIPASS).joinpath(each).exists():
            copyfile(str(Path(sys._MEIPASS).joinpath(each)), './temp/' + each)
    custom_resource = {
        'cover_page': 'cover.html',
        'statement_page': 'statement.html',
        'logo_page': 'header.html',
        'logo': 'logo.png',
        'small_logo': 'smalllogo.png',
        'style_css': 'style.css'
    }
    for each_key in custom_resource:
        if each_key in kwargs and kwargs[each_key] is not None and Path(kwargs[each_key]).exists():
            copyfile(str(Path(kwargs[each_key])), str(Path('temp').joinpath(custom_resource[each_key])))


def clean_resource():
    for each in Path('./temp').iterdir():
        os.remove(str(each))
    os.rmdir('./temp')


if __name__ == '__main__':
    # 生成参数解析器
    parser = argparse.ArgumentParser(prog="嘉诚平台文档导出工具", usage=Style.USAGE,
                                     description="----嘉诚信息平台产品文档导出工具----")
    parser.add_argument('-s', '--source_path', nargs='?', type=str, help="指定MarkDown文档所在目录")
    parser.add_argument('-c', '--config_path', nargs='?', type=str, help="指定配置文件路径")
    parser.add_argument('-k', '--sidebar_key', nargs='?', type=str, help="根据SideBar的Key指定文档")
    parser.add_argument('-l', '--title_level', nargs='?', type=int, choices=[0, 1, 2, 3, 4, 5, 6], default=2,
                        help="指定目录编号等级")
    parser.add_argument('-t', '--export_type', nargs='?', type=str, choices=['docx', 'pdf', 'both'], default='pdf',
                        help="选择生成文档的类型")
    parser.add_argument('-o', '--target_path', nargs='?', type=str, default='./output', help="指定生成的文件路径")
    # parser.add_argument('-a', '--all', action='store_true', help='是否处理目录下所有文件')
    parser.add_argument('-p', '--print', action='store_true', help="是否打印目录树")
    parser.add_argument('--title', nargs='?', help='指定文档标题')
    parser.add_argument('--version', nargs='?', help='指定版本')
    parser.add_argument('--doc_type', nargs='?', help='指定文档类型，如 产品白皮书')
    parser.add_argument('--copyright', nargs='?', help='指定版权人')
    parser.add_argument('--doc_sequence', nargs='*', help='指定文档关联顺序')
    parser.add_argument('--cover_page', nargs='?', type=str, help='指定首页模板HTML')
    parser.add_argument('--statement_page', nargs='?', type=str, help='指定扉页模板HTML')
    parser.add_argument('--header_page', nargs='?', type=str, help='指定页眉Logo模板HTML')
    parser.add_argument('--logo', nargs='?', type=str, help='指定PNG格式Logo图像')
    parser.add_argument('--small_logo', nargs='?', type=str, help='指定PNG格式Small Logo图像')
    parser.add_argument('--style_css', nargs='?', type=str, help='指定PDF文件样式表')
    parser.add_argument('--disable_recurrence', action='store_true', help='禁用递归，仅处理当前路径')
    parser.add_argument('--disable_statement', action='store_true', help='不添加扉页')
    parser.add_argument('--disable_doc_type', action='store_true', help='禁用文档类型')
    parser.add_argument('--disable_version', action='store_true', help='禁用模板中版本号')
    parser.add_argument('--disable_page_break', action='store_true', help='禁用一级标题分页')
    parser.add_argument('--print_item', action='store_true', help='打印源文档树')
    parser.add_argument('--Debug', action='store_true', help='调试模式，不清理临时文件')
    arguments = parser.parse_args()
    try:
        resource_list = ('highlight.css', 'highlight.js', 'cover.html',
                         'statement.html', 'logo.png', 'style.css',
                         'smalllogo.png', 'header.html')

        if not Path('temp').exists():
            os.mkdir('temp')
        kwargs = vars(arguments)

        # 获取平台
        platform_name = platform.system()
        print(f'当前系统为 {platform_name}')

        # 打包程序运行时，Linux和Windows平台均会创建一个临时路径
        # 临时路径保存在 sys 的 field '_MEIPASS' 中
        # 如果直接运行脚本，则不存在此field
        if hasattr(sys, '_MEIPASS'):
            # Issue Feature: 使用Pathlib拼接路径，避免不同平台路径分隔符不一样的问题
            sys.path.append(str(Path(getattr(sys, '_MEIPASS')).joinpath('bin')))

        kwargs['platform_name'] = platform_name

        resource_kwargs = {
            'cover_page': kwargs.pop('cover_page'),
            'statement_page': kwargs.pop('statement_page'),
            'header_page': kwargs.pop('header_page'),
            'logo': kwargs.pop('logo'),
            'small_logo': kwargs.pop('small_logo'),
            'style_css': kwargs.pop('style_css')
        }
        prepare_resource(resource_list, **resource_kwargs)
        target_path = kwargs['target_path']
        if not Path(target_path).exists():
            os.mkdir(target_path)
        valid_kwargs = {}
        if kwargs['source_path'] is None:
            kwargs['source_path'] = '.'
            if kwargs['config_path'] is None:
                for each_doc in Path('.').iterdir():
                    if each_doc.suffix == '.json':
                        kwargs['config_path'] = each_doc.absolute()
                        break
                    if each_doc.name == '.vuepress':
                        kwargs['config_path'] = each_doc.absolute().joinpath('config.js')
                        break
            kwargs['disable_recurrence'] = True if kwargs['config_path'] is None else False
        for each_key in kwargs:
            if kwargs[each_key] is not None:
                valid_kwargs[each_key] = kwargs[each_key]
        handler = MD2PDF(**valid_kwargs)
        handler.process()

        if not kwargs['Debug']:
            clean_resource()
    except SystemExit:
        pass
    except:
        with open('error.log', 'w', encoding='utf-8') as error_writer:
            error_writer.write(format_exc())
            print(format_exc())
