# -*- coding: utf-8 -*-

"""本模块根据整体框架设计而对data文件夹的数据进行合并、计算，最终得到指标结果表

"""


FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # program root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative