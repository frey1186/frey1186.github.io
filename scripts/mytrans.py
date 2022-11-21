import tkinter as tk
import re
import time
from googletrans import Translator

translator = Translator(service_urls=['translate.google.cn'])

def preper_source_text(source_text):
    '''
    去掉源端字符串的回车符号
    :param source_text:
    :return:
    '''
    source_text = source_text.replace("\n","")
    return source_text

def trans(source_text):
    source_text_temp = root.clipboard_get()
    if source_text == source_text_temp:
        pass
    else:
        source_text = source_text_temp
    source_text = preper_source_text(source_text)
    target_text = translator.translate(source_text, dest='zh-cn').text
    return target_text

def update_text():
    target_text = trans(source_text)
    t.delete('0.0','end')
    t.insert('end', target_text)
    root.update()
    t.after(1000, update_text)

if __name__ == '__main__':
    root = tk.Tk()
    root.wm_attributes('-topmost', 1)
    root.title("mytrans")
    t = tk.Text(root, height=10, width=80, font=('', 12))
    t.pack()
    source_text = root.clipboard_get()
    target_text = trans(source_text)
    t.after(1000, update_text)
    root.mainloop()







