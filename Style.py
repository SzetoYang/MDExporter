PREVIOUS_USAGE = '''
            WNWMMMMMMMMMMMMWNKOkdolcccclodkOKNWMMMMMMMMMMMMMMM
            Kook0XWWMMMWNKkdl:;;;;;;;;;;;;;;:codkO0XNWWMMMMMMM
            Kl;;:coddxdoc:;;;;;;;;;;;;;;;;;;;;;;;;:cddcloodxkX
            Kl;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;o:......'k
            Kl;;;;;;;;;;;;;;;;;;:cloooolc:;;;;;;;;;;o:......'k
            Kl;;;;;;;;;;;;;:loddddddddddddddolc:;;;;o:......'k
            Kl;;;;;;;::clddddoc:;;;;;;;;;;:coodddddoxc......'k
            Kl;;;;;;cdddolc;;;;;;;;;;;;;;;;;;;;;:cloxc......'k
            Kl;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;o:......'k
            Kl;;;;;;;;;;;;;;;;;cloodddddolc:;;;;;;;;o:......'k
            Xxl:;;;;;;;;;;:looolcc:;;;;:ccloodolc:;;o:......'k
            0cclooollllooolc:'..............';clloodxc......'k
            O,...;cclllc;'.........................,,.......'k
            0;.................';cloddddoc;'................'k
            NOc'..........';ldOKNWMMMMMMMWNKOdl:,...........'k
            MMWKxl:;,;:ldkKNWMMMMMMMMMMMMMMMMMMWXKOxolc;,''.,O
                           ------使用示例--------

    . (单个点) 代表当前目录   .. (两个点) 代表上级目录

    1、处理单个产品文档

    ./MDExporter.exe -s ./docs/platform/JCLCDP -c ./docs/.vuepress/config.js -l 3 -t docx -p

    -s ./docs/platform/JCLCDP        产品文档目录
    -c ./docs/.vuepress/config.js    配置文件(config.js)位置
    -l 3                             给文档中 1、2、3(<=3)级目录打标号
    -p                               带上此参数会打印目录树
    -t docx                          导出为Word(docx)文档


    2、处理所有产品文档

    ./平台文档导出工具.exe -s ./docs/ -c ./docs/.vuepress/config.js -o ./output -l 2 -t both -a

    -o ./output  输出的docx文档在当前目录(.)的output目录下
    -a           带上此参数表示处理所有文档  故 -s 应为 ./docs目录
    -l 2         给1级、2级目录加上标号
    -t both      同时导出PDF和Word文档
                                                                           Author: Data Dept.
    '''

USAGE = '''
            WNWMMMMMMMMMMMMWNKOkdolcccclodkOKNWMMMMMMMMMMMMMMM
            Kook0XWWMMMWNKkdl:;;;;;;;;;;;;;;:codkO0XNWWMMMMMMM
            Kl;;:coddxdoc:;;;;;;;;;;;;;;;;;;;;;;;;:cddcloodxkX
            Kl;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;o:......'k
            Kl;;;;;;;;;;;;;;;;;;:cloooolc:;;;;;;;;;;o:......'k
            Kl;;;;;;;;;;;;;:loddddddddddddddolc:;;;;o:......'k
            Kl;;;;;;;::clddddoc:;;;;;;;;;;:coodddddoxc......'k
            Kl;;;;;;cdddolc;;;;;;;;;;;;;;;;;;;;;:cloxc......'k
            Kl;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;o:......'k
            Kl;;;;;;;;;;;;;;;;;cloodddddolc:;;;;;;;;o:......'k
            Xxl:;;;;;;;;;;:looolcc:;;;;:ccloodolc:;;o:......'k
            0cclooollllooolc:'..............';clloodxc......'k
            O,...;cclllc;'.........................,,.......'k
            0;.................';cloddddoc;'................'k
            NOc'..........';ldOKNWMMMMMMMWNKOdl:,...........'k
            MMWKxl:;,;:ldkKNWMMMMMMMMMMMMMMMMMMWXKOxolc;,''.,O
                           ------使用示例--------

    . (单个点) 代表当前目录   .. (两个点) 代表上级目录

    1、处理单个文档

    ./MDExporter.exe -s ./docs/platform/JCLCDP -c ./docs/.vuepress/config.js -l 3 -t docx -p

    -s ./docs/platform/JCLCDP        产品文档目录
    -c ./docs/.vuepress/config.js    配置文件(config.js)位置
    -l 3                             给文档中 1、2、3(<=3)级目录打标号
    -p                               带上此参数会打印目录树
    -t docx                          导出为Word(docx)文档
                                                                           Author: Data Dept.
    '''