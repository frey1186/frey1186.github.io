#!/usr/bin/env python
#
# Version: 0.1
#
import time
import random

class WuXing(object):
    def __init__(self, name, sheng, shengyu, ke, keyu, wang, shuai) -> None:
        self.name = name
        self.sheng = sheng
        self.shengyu = shengyu
        self.ke = ke
        self.keyu = keyu
        self.wang = wang 
        self.shuai = shuai 

Jin  = WuXing("金", "水", "土", "木", "火", "秋", "夏")
Mu   = WuXing("木", "火", "水", "土", "金", "春", "秋")
Shui = WuXing("水", "木", "金", "火", "土", "冬", "四季之月")
Huo  = WuXing("火", "土", "木", "金", "水", "夏", "冬")
Tu   = WuXing("土", "金", "火", "水", "木", "四季之月", "春")

for wx in (Jin, Mu, Shui, Huo, Tu):
    for i,k in {Jin: "金", Mu: "木",Shui: "水",Huo: "火",Tu: "土"}.items():
        if wx.sheng == k: wx.sheng = i
        if wx.shengyu == k: wx.shengyu = i
        if wx.ke == k: wx.ke = i
        if wx.keyu == k: wx.keyu = i

WuXing_sheng = (Jin, Shui, Mu, Huo, Tu)
WuXing_ke = (Jin, Mu, Tu, Shui, Huo)

class Class_Gua8(object):
    def __init__(self, bid, wx, gong, name, grah ) -> None:
        self.bid = bid  # 先天数 // 坤为0
        self.wx = wx # 五行    金 金 火 ...
        self.gong = gong # 八宫  乾 兑 离 ...
        self.name = name # 卦名  天 泽 火 ...
        self.grah = grah # 图，二进制表示，0为断，1为连  乾：111， 兑：011， 离：101 ...

Qian =  Class_Gua8(1, Jin,  "乾", "天", 0b111)
Dui  =  Class_Gua8(2, Jin,  '兑', '泽', 0b011)
Li   =  Class_Gua8(3, Huo,  "离", "火", 0b101)
Zhen =  Class_Gua8(4, Mu,   "震", "雷", 0b001)
Xun  =  Class_Gua8(5, Mu,   "巽", "风", 0b110)
Kan  =  Class_Gua8(6, Shui, "坎", "水", 0b010)
Gen  =  Class_Gua8(7, Tu,   "艮", "山", 0b100)
Kun  =  Class_Gua8(0, Tu,   "坤", "地", 0b000)  # 

# 八卦属性均置于 Gua8 中, 先天数排序
Gua8 = (Kun, Qian, Dui, Li, Zhen, Xun, Kan, Gen)
# 
Gua8_grah = (Kun, Zhen, Kan, Dui, Gen, Li, Xun, Qian)

class Class_Gua64(object):
    def __init__(self, name, up, down, grah) -> None:
        self.name = name
        self.up = up   # 上挂
        self.down = down  # 下挂
        self.grah = grah  # 卦图

Gua64_name_list = {
    11: "乾为天",   0: "坤为地",    64: "水雷屯",   76: "山水蒙",
    61: "水天需",   16: "天水讼",   6: "地水师",    60: "水地比",
    51: "风天小畜", 12: "天泽履",   1: "地天泰",    10: "天地否",
    13: "天火同人", 31: "火天大有", 7: "地山谦",    40: "雷地豫",
    24: "泽雷随",   75: "山风蛊",   2: "地泽临",    50: "风地观",
    34: "火雷噬嗑", 73: "山火贲",   70: "山地剥",   4: "地雷复",
    14: "天雷旡妄", 71: "山天大畜", 74: "山雷颐",   25: "泽风大过",
    66: "坎为水",   33: "离为火",   27: "泽山咸",   45: "雷风恒",
    17: "天山遯",   41: "雷天大壮", 30: "火地晋",   3: "地火明夷",
    53: "风火家人", 32: "火泽睽",   67: "水山蹇",   46: "雷水解",
    72: "山泽损",   54: "风雷益",   21: "泽天夬",   15: "天风姤",
    20: "泽地萃",   5: "地风升",    26: "泽水困",   65: "水风井",
    23: "泽火革",   35: "火风鼎",   44: "震为雷",   77: "艮为山",
    57: "风山渐",   42: "雷泽归妹", 43: "雷火丰",   37: "火山旅",
    55: "巽为风",   22: "兑为泽",   56: "风水涣",   62: "水泽节",
    52: "风泽中孚", 47: "雷山小过",  63: "水火既济", 36: "火水未济"
}

Gua64 = {}

for k in Gua64_name_list:
    up = Gua8[k//10]
    down = Gua8[k%10]
    Gua64[k] = Class_Gua64(Gua64_name_list[k],
                              up, down,
                              (up.grah<<3) + down.grah)

def mk_gua():
    # 使用 随机数+时间 起卦
    h = (time.localtime().tm_hour)//2+2  # 时辰
    r = random.randint(100,899)
    up = r//100
    down = r%100%10+r%100//10
    bian_yao = (up + down + h) % 6 
    if bian_yao ==0 : bian_yao = 6
    up = up % 8
    down = down % 8
    return (up, down, bian_yao)

def get_hu_gua(ben_gua):
    p = ben_gua.grah
    up_gua = Gua8_grah[(p>>2) & 0b111]
    down_gua = Gua8_grah[(p>>1) & 0b111]
    return Gua64[up_gua.bid*10+down_gua.bid]

def get_ben_gua(up,down):
    return Gua64[up*10+down]

def get_bian_gua(ben_gua, bian_yao):
    p = ben_gua.grah
    p = p^(1<< (bian_yao-1)) # 取变卦
    up_gua = Gua8_grah[p>>3 & 0b111]
    down_gua = Gua8_grah[p & 0b111]
    return Gua64[up_gua.bid*10+down_gua.bid]

def pt_gua(up, down, bian_yao):
    ben_gua = get_ben_gua(up, down)
    hu_gua = get_hu_gua(ben_gua)
    bian_gua = get_bian_gua(ben_gua, bian_yao)
    print(f"本卦： %s, %d爻变, 上%s下%s，" % (ben_gua.name, bian_yao, ben_gua.up.wx.name, ben_gua.down.wx.name))
    print(f"互卦： {hu_gua.name}, 上{hu_gua.up.wx.name}下{hu_gua.down.wx.name}" )
    print(f"变卦： {bian_gua.name}, 上{bian_gua.up.wx.name}下{bian_gua.down.wx.name}")

if __name__ == '__main__':
    pt_gua(*mk_gua())


# Changelog
# * version:0.1 2024-08-21
#   - add printing.
