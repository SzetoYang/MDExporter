FROM debian

COPY ./requirements.txt /Document/requirements.txt
COPY ./dependencies/wkhtmltox.deb /Document/wkhtmltox.deb
# 由Windows抽取的中文宋体字体，有版权问题
COPY ./fonts/Alibaba-PuHuiTi-Regular.ttf /usr/share/fonts
WORKDIR /Document
ENV DEBIAN_FRONTEND=noninteractive
RUN sed -i "s@http://deb.debian.org@http://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list
RUN sed -i "s@http://security.debian.org@http://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update
RUN apt-get install -y pandoc fontconfig xfonts-75dpi xfonts-base libjpeg62-turbo ca-certificates libx11-6 libxcb1 libxext6 libxrender1 pip locales
RUN localedef -c -f UTF-8 -i zh_CN zh_CN.utf8
ENV LANG zh_CN.utf8
# 此包不可由包管理工具安装，需要手动加入，不然有功能缺陷
RUN dpkg -i wkhtmltox.deb
# 刷新字体缓存
RUN fc-cache -fv
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . /Document
RUN pyinstaller MD2PDF_linux.spec
RUN mv dist/MDExporter /usr/bin/
WORKDIR /tmp
#ENTRYPOINT ["python"]
#
#CMD ["Document.py"]


