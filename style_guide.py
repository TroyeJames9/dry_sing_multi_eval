# -*- coding: utf-8 -*-

"""模块或程序的一行概述, 以句号结尾.

留一个空行. 接下来应该写模块或程序的总体描述. 也可以选择简要描述导出的类和函数,
和/或描述使用示例.

经典的使用示例:

foo = ClassFoo()
bar = foo.FunctionBar()
"""

import os
import sys
import re
from pathlib import Path
from typing import Union


"""函数文档字符串的示例"""


def fetch_smalltable_rows(
    table_handle: smalltable.Table,
    keys: Sequence[Union[bytes, str]],
    require_all_keys: bool = False,
) -> Mapping[bytes, Tuple[str, ...]]:
    """从 Smalltable 获取数据行.

    从 table_handle 代表的 Table 实例中检索指定键值对应的行. 如果键值是字符串,
    字符串将用 UTF-8 编码.

    参数:
        table_handle(smalltable.Table):
            处于打开状态的 smalltable.Table 实例.
        keys(Sequence[Union[bytes, str]]):
            一个字符串序列, 代表要获取的行的键值. 字符串将用 UTF-8 编码.
        require_all_keys(bool):
            如果为 True, 只返回那些所有键值都有对应数据的行.

    返回:
        一个字典, 把键值映射到行数据上. 行数据是字符串构成的元组. 例如:

        {b'Serak': ('Rigel VII', 'Preparer'),
         b'Zim': ('Irk', 'Invader'),
         b'Lrrr': ('Omicron Persei 8', 'Emperor')}

        返回的键值一定是字节串. 如果字典中没有 keys 参数中的某个键值, 说明
        表格中没有找到这一行 (且 require_all_keys 一定是 false).

    抛出:
        IOError: 访问 smalltable 时出现错误.
    """
    pass


"""类的文档字符串示例"""


class SampleClass(object):
    """这里是类的概述.

    这里是更多信息....
    这里是更多信息....

    属性:
        likes_spam(bool): 布尔值, 表示我们是否喜欢午餐肉.
        eggs(int): 用整数记录的下蛋的数量.
    """

    def __init__(self, likes_spam = False):
        """用某某某初始化 SampleClass."""
        self.likes_spam = likes_spam
        self.eggs = 0

    def public_method(self):
        """执行某某操作."""
        pass


"""↓块注释和行注释的示例"""
# 我们用加权的字典搜索, 寻找 i 在数组中的位置. 我们基于数组中的最大值和数组
# 长度, 推断一个位置, 然后用二分搜索获得最终准确的结果.

if i & (i-1) == 0:  # 如果 i 是 0 或者 2 的整数次幂, 则为真.
    pass
