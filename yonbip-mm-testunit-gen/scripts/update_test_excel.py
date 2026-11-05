"""
测试用例Excel文件更新工具（整合版）

功能：
1. 从Java源文件解析方法签名，自动更新Excel中的方法定义
2. 自动扩展BASE Sheet表头（arg5, arg6...）
3. 自动创建方法Sheet并包含relatedTask列
4. 【新增】根据PM任务描述生成完整测试用例集（边界测试 + PM场景）
5. 【新增】自动应用Excel样式

使用方式：
简单模式：python update_test_excel.py --simple
完整模式：python update_test_excel.py --complete

作者：yonbip-mm-testunit-gen Skill
版本：v2.3.0 - 整合简单模式和完整模式
"""

import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Set
import sys
import os
import re
import glob

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# 导入test_case_generator中的方法Sheet创建逻辑
try:
    from test_case_generator import ExcelProcessorUtil, MethodInfo, Attr
    HAS_GENERATOR = True
except ImportError:
    HAS_GENERATOR = False
    print("警告: 无法导入test_case_generator模块，方法Sheet创建功能不可用")

# ==================== 工具函数 ====================

def extract_test_class_suffix(excel_path: str) -> str:
    """
    从Excel文件名中提取测试类后缀

    Args:
        excel_path: Excel文件路径

    Returns:
        测试类后缀（A、B、C等），如果没有后缀返回空字符串

    示例：
        ProductionOrderServiceTest.tc.xlsx → ""
        ProductionOrderServiceTestA.tc.xlsx → "A"
        ProductionOrderServiceTestB.tc.xlsx → "B"
    """
    import re
    # 提取文件名（不含路径和扩展名）
    filename = os.path.basename(excel_path)
    filename = filename.replace('.tc.xlsx', '')

    # 匹配Test后缀：TestA, TestB, TestC 等
    # 正则表达式：Test后跟一个大写字母，且是文件名的结尾
    match = re.search(r'Test([A-Z])$', filename)
    if match:
        return match.group(1)

    return ""


# ==================== 核心函数 ====================

@dataclass
class MethodSignature:
    """方法签名"""
    class_name: str
    method_name: str
    result_type: str
    arg_types: List[str]
    modifiers: str = ""

# ==================== 配置区域 ====================

# ===== 简单模式配置 =====

# Excel文件路径（已存在的测试用例文件）
# 格式：mock-data/{子系统}/20_testcase/{模块路径}/{类名}Test.tc.xlsx
# ⚠️ 请替换为您的实际Excel文件路径
EXCEL_PATH = r'D:\unitTestProject\production-order\mock-data\po\20_testcase\common\po.common.ProductionOrderServiceTest.tc.xlsx'
# 示例：r'D:\unitTestProject\production-order\mock-data\po\20_testcase\order\po.order.OrderCheckImplTest.tc.xlsx'

# Java源码根目录（用于解析方法签名）
# ⚠️ 请替换为您的实际Java源码路径
JAVA_SOURCE_ROOT = r'D:\unitTestProject\production-order\src\manufacturing-service\src\main\java'
# 示例：r'D:\unitTestProject\production-order\src\manufacturing-service\src\main\java'

# 目标方法配置
TARGET_METHOD_NAME = "forceCloseWhenQuantityZero"  # 要新增测试的方法名
TARGET_CLASS_NAME = "com.yonyou.biz.mm.mfpo.service.po.common.bizservice.ProductionOrderService"  # 被测试类全限定名

# 子系统标识
# 可选值：PO / IMPSFC / MR / OSM / QMS / QIC / ED / ECN
SUB_ID = "PO"

# 测试用例数量（简单模式使用）
TEST_CASE_COUNT = 11

# ===== 完整模式配置（新增）=====

# PM任务描述（完整模式使用）
# 格式：故事点：XXX-MF-F-XXXX
#       1. 场景描述（断言：预期结果）
#       2. 场景描述（断言：预期结果）
PM_TASK_DESC = """
故事点：YYY-MF-F-2702
1. 引用前置用例：生产订单空白新增（断言：引用成功，获取生产订单）
2. 生产订单查询（断言：查询成功）
3. 保存审核生产订单1（断言：审核成功）
4. 复制生产订单1生成生产订单2（断言：复制成功）
5. 生产订单合并，来源订单=生产订单1，目的订单=生产订单2（断言：合并成功，生产订单1数量=0且状态=已关闭）
"""

# PM问题号（自动填充到relatedTask列）
RELATED_TASK_NUMBER = "YYY-T-24594,YYY-MF-F-2702"

# ===== 通用配置 =====

# 是否自动创建方法Sheet
AUTO_CREATE_METHOD_SHEET = True

# 是否自动应用Excel样式
AUTO_APPLY_STYLE = True

# ==================== PM任务解析功能（新增）====================

class PMTaskParser:
    """解析PM任务描述，提取测试场景"""

    @staticmethod
    def parse_task_scenarios(task_desc: str) -> list:
        """
        解析PM任务描述，提取测试场景

        Args:
            task_desc: PM任务描述文本

        Returns:
            list: [(场景编号, 场景描述, 断言要求), ...]
        """
        scenarios = []
        if not task_desc:
            return scenarios

        lines = task_desc.strip().split('\n')
        for line in lines:
            line = line.strip()
            # 匹配格式：编号. 场景描述（断言：预期结果）
            match = re.match(r'^(\d+)\.\s*(.+?)(?:（断言：(.+?)）)?\s*$', line)
            if match:
                scenario_num = int(match.group(1))
                scenario_desc = match.group(2).strip()
                assertion = match.group(3).strip() if match.group(3) else ""
                scenarios.append((scenario_num, scenario_desc, assertion))

        return scenarios


class BoundaryTestAnalyzer:
    """分析方法源码，识别边界测试场景"""

    @staticmethod
    def analyze_from_code_snippet(method_name: str, code_snippet: str = None):
        """
        从代码片段分析边界测试场景（简化版）

        实际使用时，建议为每个方法单独编写分析方法

        Args:
            method_name: 方法名
            code_snippet: 代码片段（可选）

        Returns:
            list: [(测试编号, 测试描述, 预期行为), ...]
        """
        # 通用边界测试场景（适用于大多数方法）
        boundary_tests = [
            (1, f"{method_name}_参数为空", "直接返回或不抛异常"),
            (2, f"{method_name}_参数边界值", "正常处理"),
            (3, f"{method_name}_异常场景", "抛出异常或返回错误"),
            (4, f"{method_name}_其他场景", "正常处理")
        ]

        return boundary_tests

    @staticmethod
    def analyze_checkCoop_method():
        """
        分析checkCoop方法的边界测试场景（硬编码示例）

        实际使用时，应根据具体方法逻辑编写分析逻辑
        """
        boundary_tests = [
            (1, "orderIds为空", "直接返回（不抛异常）"),
            (2, "orderList为空", "直接返回（不抛异常）"),
            (3, "非协同订单（coopType != 1）", "不抛异常"),
            (4, "不存在协同订单", "不抛异常")
        ]
        return boundary_tests


class CompleteTestCaseGenerator:
    """生成完整的测试用例集（边界测试 + PM场景）"""

    @staticmethod
    def generate_test_cases(boundary_tests, pm_scenarios, related_task_number):
        """
        生成完整的测试用例列表

        Args:
            boundary_tests: 边界测试列表
            pm_scenarios: PM场景列表
            related_task_number: PM任务号

        Returns:
            list: [(用例编号, 用例描述, relatedTask值), ...]
        """
        complete_test_cases = []

        # 1. 边界测试（relatedTask留空）
        for test_num, test_desc, expected_behavior in boundary_tests:
            case_desc = f"边界测试：{test_desc}（预期：{expected_behavior}）"
            complete_test_cases.append((test_num, case_desc, ""))  # relatedTask为空

        # 2. PM场景（relatedTask填充PM任务号）
        for scenario_num, scenario_desc, assertion in pm_scenarios:
            if assertion:
                case_desc = f"场景{scenario_num}：{scenario_desc}（断言：{assertion}）"
            else:
                case_desc = f"场景{scenario_num}：{scenario_desc}"

            complete_test_cases.append(
                (len(boundary_tests) + scenario_num, case_desc, related_task_number)
            )

        return complete_test_cases


# ==================== Java源码解析功能 ====================

def find_java_file(class_name: str, source_root: str) -> Optional[str]:
    """根据类名查找Java源文件路径"""
    relative_path = class_name.replace('.', os.sep) + '.java'
    full_path = os.path.join(source_root, relative_path)

    if os.path.exists(full_path):
        return full_path

    # 尝试模糊匹配
    class_parts = class_name.split('.')
    pattern = os.path.join(source_root, '**', class_parts[-1] + '.java')
    matches = glob.glob(pattern, recursive=True)
    if matches:
        return matches[0]

    return None


def parse_method_signature(method_def: str, class_name: str) -> Optional[MethodSignature]:
    """解析方法定义行，提取方法签名"""
    method_def = re.sub(r'//.*$', '', method_def)
    method_def = re.sub(r'/\*.*?\*/', '', method_def, flags=re.DOTALL)

    pattern = (
        r'(?:((?:public|protected|private|static|abstract|final|synchronized)\s+)*)'
        r'([\w\<\>\[\]]+)\s+'
        r'(\w+)\s*'
        r'\(([^)]*)\)'
    )

    match = re.search(pattern, method_def)
    if not match:
        return None

    modifiers = match.group(1) or ''
    result_type = match.group(2).strip()
    method_name = match.group(3)
    params_str = match.group(4)

    # 解析参数
    arg_types = []
    if params_str.strip():
        param_parts = []
        depth = 0
        current = ''
        for char in params_str:
            if char in '(<[':
                depth += 1
                current += char
            elif char in ')>]':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                param_parts.append(current.strip())
                current = ''
            else:
                current += char
        if current.strip():
            param_parts.append(current.strip())

        for param in param_parts:
            param = param.strip()
            if not param:
                continue
            type_match = re.match(r'(?:@[\w\.]+\s+)*([\w\<\>\[\]]+)', param)
            if type_match:
                arg_types.append(type_match.group(1))
            else:
                parts = param.split()
                if parts:
                    arg_types.append(parts[0])

    return MethodSignature(
        class_name=class_name,
        method_name=method_name,
        result_type=result_type,
        arg_types=arg_types,
        modifiers=modifiers.strip()
    )


def find_method_in_java(java_file: str, method_name: str) -> Optional[MethodSignature]:
    """在Java文件中查找指定方法"""
    if not os.path.exists(java_file):
        return None

    with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    method_pattern = r'\b((?:public|protected|private|static|abstract|final|synchronized)\s+)*' \
                      r'([\w\<\>\[\]]+)\s+' + method_name + r'\s*\('

    match = re.search(method_pattern, content)
    if not match:
        return None

    method_start_pos = match.start()
    search_start = max(0, method_start_pos - 200)
    search_end = min(len(content), match.end() + 500)
    method_region = content[search_start:search_end]

    lines = method_region.split('\n')
    method_def_lines = []

    first_line_match = re.search(r'[\w\s]*' + method_name + r'\s*\(', method_region)
    if not first_line_match:
        return None

    depth = 0
    found_start = False
    for i, line in enumerate(lines):
        for char in line:
            if char == '(':
                depth += 1
                found_start = True
            elif char == ')':
                depth -= 1

        if found_start:
            method_def_lines.append(line)
            if depth == 0:
                break

    if not method_def_lines:
        return None

    method_def = ' '.join(method_def_lines)
    return parse_method_signature(method_def, java_file)


def parse_java_source(java_root: str, class_name: str, method_name: str) -> Optional[MethodSignature]:
    """解析Java源文件获取方法签名"""
    java_file = find_java_file(class_name, java_root)
    if not java_file:
        print(f'未找到Java文件: {class_name}')
        return None

    print(f'找到Java文件: {java_file}')
    return find_method_in_java(java_file, method_name)


# ==================== Excel更新功能 ====================

def extend_base_sheet_header(base, arg_size):
    """扩展BASE Sheet的表头以适应更多参数"""
    if arg_size <= 0:
        return

    max_existing_arg = -1
    for col in range(8, base.max_column + 1):
        val = base.cell(row=2, column=col).value
        if val and 'arg' in str(val):
            max_existing_arg = col - 8

    if arg_size > max_existing_arg + 1:
        print(f'扩展BASE表头: arg{max_existing_arg + 1} 到 arg{arg_size - 1}')
        for i in range(max_existing_arg + 1, arg_size):
            col = 8 + i
            base.cell(row=2, column=col, value=f'arg{i}')
            base.cell(row=3, column=col, value=f'参数{i}编码')
            base.cell(row=4, column=col, value='String')


def update_base_sheet_method_def(base, method_name: str, signature: MethodSignature):
    """更新BASE Sheet中的方法定义"""
    method_row = None
    for row in range(5, base.max_row + 1):
        if base.cell(row=row, column=6).value == method_name:
            method_row = row
            break

    if method_row is None:
        print(f'未在BASE Sheet中找到方法: {method_name}')
        return False

    old_arg_size = int(base.cell(row=method_row, column=7).value or 0)
    new_arg_size = len(signature.arg_types)

    print(f'更新BASE Sheet方法定义: {method_name}')
    print(f'  方法行: {method_row}')
    print(f'  argSize: {old_arg_size} -> {new_arg_size}')

    base.cell(method_row, column=7, value=new_arg_size)

    for i, arg_type in enumerate(signature.arg_types):
        base.cell(method_row, 8 + i, value=arg_type)

    if new_arg_size > old_arg_size:
        extend_base_sheet_header(base, new_arg_size)

    for col in range(8 + new_arg_size, 8 + old_arg_size):
        base.cell(method_row, col, value=None)

    return True


# ==================== 方法Sheet创建功能 ====================

def add_method_sheet_simple(workbook, method_name: str, signature: MethodSignature,
                           sub_id: str, test_case_count: int = 7, related_task_number: str = "",
                           test_class_suffix: str = ""):
    """
    简单模式：创建方法Sheet（包含relatedTask列）

    Args:
        workbook: Excel工作簿对象
        method_name: 方法名
        signature: 方法签名信息
        sub_id: 子系统标识
        test_case_count: 测试用例数量
        related_task_number: PM问题号
        test_class_suffix: 测试类后缀（A、B、C等）
    """
    if not HAS_GENERATOR:
        print("错误: 缺少test_case_generator模块")
        return False

    sheet_name = method_name[:31] if len(method_name) > 31 else method_name

    if sheet_name in workbook.sheetnames:
        print(f"方法Sheet已存在: {sheet_name}")
        return False

    print(f"\n========== 创建方法Sheet（简单模式）==========")
    print(f"  Sheet名称: {sheet_name}")
    print(f"  子系统: {sub_id}")
    print(f"  测试用例数: {test_case_count}")
    if test_class_suffix:
        print(f"  测试类后缀: {test_class_suffix}")
    if related_task_number:
        print(f"  PM问题号: {related_task_number}")

    method_sheet = workbook.create_sheet(title=sheet_name)

    method_info = MethodInfo(
        name=method_name,
        return_type=signature.result_type,
        parameters=[(arg, f"arg{i}") for i, arg in enumerate(signature.arg_types)],
        declaring_class=signature.class_name
    )

    try:
        row_info = ExcelProcessorUtil.fill_blank(
            method_sheet, method_info, sub_id, index=1,
            test_case_count=test_case_count,
            related_task_number=related_task_number,
            test_class_suffix=test_class_suffix
        )

        # 应用样式
        if AUTO_APPLY_STYLE:
            try:
                from excel_style_util import ExcelStyleUtil
                ExcelStyleUtil.style_full_workbook(workbook, test_case_count)
                print(f"  样式应用成功")
            except:
                print(f"  警告: 样式应用失败")

        print(f"✅ 方法Sheet创建成功")
        return True

    except Exception as e:
        print(f"❌ 创建方法Sheet失败: {e}")
        if sheet_name in workbook.sheetnames:
            del workbook[sheet_name]
        return False


def add_method_sheet_complete(workbook, method_name: str, signature: MethodSignature,
                              sub_id: str, boundary_tests: list, pm_scenarios: list,
                              related_task_number: str, test_class_suffix: str = ""):
    """
    完整模式：创建方法Sheet，生成边界测试 + PM场景

    Args:
        workbook: Excel工作簿对象
        method_name: 方法名
        signature: 方法签名信息
        sub_id: 子系统标识
        boundary_tests: 边界测试列表
        pm_scenarios: PM场景列表
        related_task_number: PM任务号
        test_class_suffix: 测试类后缀（A、B、C等）
    """
    if not HAS_GENERATOR:
        print("错误: 缺少test_case_generator模块")
        return False

    # 生成完整测试用例列表
    complete_test_cases = CompleteTestCaseGenerator.generate_test_cases(
        boundary_tests, pm_scenarios, related_task_number
    )

    total_test_count = len(complete_test_cases)

    print(f"\n========== 创建方法Sheet（完整模式）==========")
    print(f"  Sheet名称: {method_name}")
    print(f"  子系统: {sub_id}")
    if test_class_suffix:
        print(f"  测试类后缀: {test_class_suffix}")
    print(f"  边界测试: {len(boundary_tests)}个")
    print(f"  PM场景: {len(pm_scenarios)}个")
    print(f"  总计: {total_test_count}个")

    sheet_name = method_name[:31] if len(method_name) > 31 else method_name

    if sheet_name in workbook.sheetnames:
        print(f"  删除旧Sheet: {sheet_name}")
        del workbook[sheet_name]

    method_sheet = workbook.create_sheet(title=sheet_name)

    method_info = MethodInfo(
        name=method_name,
        return_type=signature.result_type,
        parameters=[(arg, f"arg{i}") for i, arg in enumerate(signature.arg_types)],
        declaring_class=signature.class_name
    )

    try:
        # 创建Sheet结构
        row_info = ExcelProcessorUtil.fill_blank(
            method_sheet, method_info, sub_id, index=1,
            test_case_count=total_test_count,
            related_task_number="",  # 先不填充，后面手动填充
            test_class_suffix=test_class_suffix
        )

        # 填充完整测试用例信息
        print(f"\n  填充测试用例信息:")
        test_case_data_start = row_info['test_case_data_start']

        for i, (case_num, case_desc, related_task) in enumerate(complete_test_cases):
            row_num = test_case_data_start + i

            # 填充memo列（第4列）
            method_sheet.cell(row=row_num, column=4).value = case_desc

            # 填充relatedTask列（第11列）
            method_sheet.cell(row=row_num, column=11).value = related_task

            related_display = related_task if related_task else "(边界测试)"
            print(f"    Row {row_num}: {case_desc[:40]}... | {related_display}")

        # 应用样式
        if AUTO_APPLY_STYLE:
            try:
                from excel_style_util import ExcelStyleUtil
                ExcelStyleUtil.style_full_workbook(workbook, total_test_count)
                print(f"\n  样式应用成功")
            except:
                print(f"\n  警告: 样式应用失败")

        print(f"\n✅ 方法Sheet创建成功")
        print(f"  边界测试用例: {len(boundary_tests)}个 (relatedTask为空)")
        print(f"  PM任务场景: {len(pm_scenarios)}个 (relatedTask: {related_task_number})")
        print(f"  总计: {total_test_count}个")

        return True

    except Exception as e:
        print(f"❌ 创建方法Sheet失败: {e}")
        if sheet_name in workbook.sheetnames:
            del workbook[sheet_name]
        return False


# ==================== 主函数 ====================

def main():
    """主函数"""
    print('=' * 80)
    print('测试用例Excel文件更新工具（整合版）- v2.3.0')
    print('=' * 80)
    print('\n功能:')
    print('  1. 解析Java源文件，更新方法定义')
    print('  2. 扩展BASE Sheet表头')
    print('  3. 自动创建方法Sheet（包含relatedTask列）')
    print('  4. 【新增】根据PM任务描述生成完整测试用例集')
    print('  5. 【新增】自动应用Excel样式')
    print('=' * 80)

    # 检查命令行参数
    use_complete_mode = '--complete' in sys.argv

    # 显示配置信息
    print(f'\n当前配置:')
    print(f'  Excel文件: {EXCEL_PATH}')
    print(f'  目标方法: {TARGET_METHOD_NAME}')
    print(f'  子系统: {SUB_ID}')

    # 解析Java源文件
    signature = parse_java_source(JAVA_SOURCE_ROOT, TARGET_CLASS_NAME, TARGET_METHOD_NAME)
    if not signature:
        print('错误: 无法解析方法签名')
        return

    print(f'\n解析结果:')
    print(f'  返回类型: {signature.result_type}')
    print(f'  参数数量: {len(signature.arg_types)}')
    for i, arg in enumerate(signature.arg_types):
        print(f'    arg{i}: {arg}')

    # ⭐ 提取测试类后缀
    test_class_suffix = extract_test_class_suffix(EXCEL_PATH)
    if test_class_suffix:
        print(f'\n检测到测试类后缀: {test_class_suffix}')

    # 加载Excel文件
    wb = openpyxl.load_workbook(EXCEL_PATH)

    # 更新BASE Sheet
    if 'BASE' in wb.sheetnames:
        print(f'\n========== 更新BASE Sheet ==========')
        base = wb['BASE']
        update_base_sheet_method_def(base, TARGET_METHOD_NAME, signature)

    # 创建方法Sheet
    print(f'\n========== 创建方法Sheet ==========')
    if use_complete_mode:
        # 完整模式：边界测试 + PM场景
        print(f'模式: 完整模式（边界测试 + PM场景）')

        # 解析PM任务
        pm_scenarios = PMTaskParser.parse_task_scenarios(PM_TASK_DESC)
        print(f'PM场景: {len(pm_scenarios)}个')

        # 分析边界测试（使用checkCoop专用方法）
        if TARGET_METHOD_NAME == "checkCoop":
            boundary_tests = BoundaryTestAnalyzer.analyze_checkCoop_method()
        else:
            boundary_tests = BoundaryTestAnalyzer.analyze_from_code_snippet(TARGET_METHOD_NAME)
        print(f'边界测试: {len(boundary_tests)}个')

        # 创建方法Sheet
        add_method_sheet_complete(
            wb, TARGET_METHOD_NAME, signature, SUB_ID,
            boundary_tests, pm_scenarios, RELATED_TASK_NUMBER, test_class_suffix
        )
    else:
        # 简单模式：仅创建方法Sheet
        print(f'模式: 简单模式')
        add_method_sheet_simple(
            wb, TARGET_METHOD_NAME, signature, SUB_ID,
            TEST_CASE_COUNT, RELATED_TASK_NUMBER, test_class_suffix
        )

    # 保存Excel文件
    wb.save(EXCEL_PATH)
    print(f'\n========== Excel已保存 ==========')
    print(f'文件: {EXCEL_PATH}')
    print('\n完成!')


if __name__ == '__main__':
    main()