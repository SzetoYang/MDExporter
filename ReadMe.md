# 嘉诚产品文档导出工具使用说明

## 快速上手 (Windows 平台)


### 导出文档为PDF

将可执行程序置于文档所在目录下，双击执行

## 准备工作

### 文档准备

待处理文档主体为一个目录（及其子目录）下的所有MarkDown文档，并依赖于一个说明各文档之间组织顺序的配置文件。

JSON 配置文件

格式示例

```json
{
  "title": "嘉诚低代码开发平台",
  "version": "V1.0",
  "doc_type": "产品白皮书",
  "copyright": "长春嘉诚信息技术股份有限公司",
  "children": [
    "",
    "快速入门",
    {
      "title": "平台说明",
      "children": [
        "使用手册",
        "实施手册",
        "版本更新说明"
      ]
    },
    {
      "title": "开发手册",
      "children": [
        "开发环境",
        {
          "title": "开发框架",
          "children": [
            "用户中心",
            "业务系统"
          ]
        }
      ]
    }
  ]
}
 ```

### 程序下载及安装

#### Windows 10可执行程序

直接下载 `MDExporter.exe` 于任意位置，不需要额外操作（于Win10 64bit系统构建并测试，其他Windows平台未进行测试）。

#### Python 脚本及环境安装

1. 如未安装 Python 解释器，请先安装 Python 解释器及包管理器 Pip（建议使用 Python 3.8+）

2. 下载`MD2PDF.py` 脚本文件及 `requirements.txt`于本地或直接克隆本项目

3. 安装Python依赖（于 `requirements.txt` 所在目录下）

+ ```pip install -r requirements.txt```
+ 国内建议使用清华Pip源  ```pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple```

4. 安装外部依赖

+ Pandoc
    + Windows： 下载安装程序 [pandoc-2.17.msi](https://github.com/jgm/pandoc/releases/download/2.17.0.1/pandoc-2.17.0.1-windows-x86_64.msi) 并安装
    + MacOS： Terminal 执行 ```brew install pandoc```
    + Ubuntu： Terminal 执行 ```sudo apt install pandoc```
    + ArchLinux：Terminal 执行 ```sudo pacman -S pandoc```

+ wkhtmltopdf
    + Windows： 下载安装程序 [wkhtmltox-0.12.exe](https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe) 并安装
    + MacOS： Terminal 执行```ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" 2> /dev/null & brew install wkhtmltopdf```
    + Ubuntu： Terminal 执行 ```sudo apt install wkhtmltopdf```
    + ArchLinux：Terminal 执行 ```sudo pacman -S wkhtmltopdf```

+ 若是Mac M1芯片，pip install pyMuPDF 时会出错，需要额外安装几个工具
  + brew install mupdf swig freetype
  + 然后： pip3 install https://github.com/pymupdf/PyMuPDF/archive/master.tar.gz
  + 或者： pip3 install --upgrade pyMuPDF
  + 

## 使用

### 参数说明

+ -s/--source_path 指定文档目录 默认 '.'
+ -c/--config_path 指定 json 配置文件的地址 默认当前目录下json文件
+ -t/--export_type 指定要输出的文档的类型，可选项有 `docx`、`pdf`、`both`，默认为`docx`，即输出为 Word文档，后跟 `pdf` 则输出为PDF文件；若要两者都导出，则改为 both 默认 PDF
+ -l/--title_level 指定Word文档中目录编号的等级，可选数字 0-6 (含6) 默认2
+ -o/--target_path 指定导出文件的目录，默认为当前目录下output目录
+ -k/--sidebar_key 指定SideBar的键名
+ -p/--print 运行过程中是否打印目录树，默认不打印，需要打印则添加 -p
+ --doc_sequence 指定文档关联顺序
+ --cover_page 指定封面模板文件
+ --header_page 指定页眉模板文件
+ --statement_page 指定扉页模板文件
+ --logo 指定PNG格式的Logo图像
+ --small_logo 指定PNG格式的Small Logo 图像（用于自带扉页模板）
+ --disable_recurrence 禁用递归，仅处理指定目录，不处理其子目录
+ --disable_statement 不添加扉页
+ --print_item 打印源文档树结构
+ ~~--Debug 调试模式，不清理临时文件~~

#### 文档顺序说明(参数 `doc_sequence`)

在无配置文件的情况下，可以通过参数 `doc_sequence`指定文档之间的衔接顺序，方式如下所示

```shell
./MDExporter.exe  --doc_sequence 数据集成 数据建模 数据开发 数据资源
```

文档衔接顺序同参数后指定的文档顺序，结构如下所示

```
Node('/参数示例')
├── Node('/参数示例/数据集成（嘉诚数据集成管理系统）')
├── Node('/参数示例/数据建模（Chiner）')
├── Node('/参数示例/数据开发管理（嘉诚数据开发管理平台）')
└── Node('/参数示例/数据资源（嘉诚数据资源管理系统）')
```

缩写说明：对文档名的输入，可以仅指定其不具有歧义的前部，将会自动补全

### 模板说明

本工具采用HTML格式的模板文件，目前默认的模板文件如下

+ cover.html 封面模板，其中包含四个可自定义字段
    + title 文档标题
    + doc_type 文档类型，如 `产品白皮书`
    + version 版本号
    + copyright 版权人
+ statement.html 扉页模板，链接 `smalllogo.png` Logo图
+ header.html 目录及正文页眉，链接 `logo.png` Logo图

模板中自定义字段均由配置文件中指定
自定义模板中，可定义任意数量的自定义字段，在配置文件中配置其相应的字段值即可

## 贡献

本工具主要针对于多人协作型项目文档，实现了从模块化文档到产品白皮书式PDF文档的导出，细分功能项如下

+ MarkDown文档合并及规范
    + 缺省标题添加
    + 越级标题处理
    + 标题序号加注
    + 资源路径替换
+ PDF样式规范
+ PDF目录、导航栏生成
+ PDF封面、扉页添加

## 依赖声明

本项目调用`Pandoc`、`wkhtmltopdf`可执行程序进行文档之间的转化，源码中未包含相关开源项目代码。

开源项目地址：

+ [Pandoc](https://github.com/jgm/pandoc)
+ [wkhtmltopdf](https://github.com/wkhtmltopdf/wkhtmltopdf)

## 软件许可

本项目采用MIT许可协议，详见:link:[LICENSE](./LICENSE)  :copyright:[长春嘉诚信息技术股份有限公司](http://www.jiachengnet.com/)
