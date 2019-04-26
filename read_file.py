import chardet
def code(path):
    f = open(path, 'rb')
    f_read = f.read()
    f_charInfo = chardet.detect(f_read)
    return f_charInfo

def read(file):
    c=code(file)
    if c['encoding'].lower()=="gb2312":
        c['encoding']="GB18030"
    print(c['encoding'])
    with open(file, mode="r",encoding=c['encoding']) as f:
        html = f.read()
        return html

if __name__=="__main__":
    print(read(r'E:\PycharmProjects\教学\zhuge\html_201903\软工17_201706014208_李晓帆\unzip\李晓帆201706014208王勇201706014218\马克斯·普朗克.html'))