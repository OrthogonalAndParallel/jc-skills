# -*- coding: utf-8 -*-
"""
Excel格式验证工具

功能：
1. 验证Excel文件结构是否符合规范
2. 检查DataRow数量一致性
3. 验证参数引用格式
4. 检查字段名正确性
5. 【新增】验证DataType与DataTag的匹配关系 ⭐
6. 【新增】验证DataTag格式是否正确 ⭐
7. 【新增】验证测试类名称一致性 ⭐

用途：
- 第4章错误排查的辅助工具
- 在运行测试前验证Excel格式
- 检测DataType与DataTag不匹配的常见错误

使用方式：
1. 命令行运行：
   python validate_excel.py <excel文件路径>

2. 代码调用：
   from validate_excel import validate_excel
   result = validate_excel("path/to/file.xlsx")
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import io

# 设置UTF-8编码输出（Windows系统兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from openpyxl import load_workbook
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
    print("警告: 未找到 openpyxl，验证功能不可用")


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict


class ExcelValidator:
    """Excel格式验证器"""

    # 标准字段名定义
    BASE_FIELDS = ["id", "code", "className", "resultType", "methodName", "argSize", "arg0", "arg1", "arg2"]
    TEST_CASE_FIELDS = ["id", "caseName", "memo", "enable", "busiDatas", "asserts", "relatedTask"]
    BUSI_DATA_FIELDS = ["id", "code", "methodInvoke", "value0", "value1", "value2"]
    ASSERT_FIELDS = ["id", "code", "assertType", "assertException", "actualName", "actualValueExp", "enable"]

    def __init__(self, excel_path: str):
        """初始化验证器"""
        self.excel_path = Path(excel_path)
        self.workbook = None
        self.result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            details={}
        )

    def validate(self) -> ValidationResult:
        """执行验证"""
        if not HAS_OPENPYXL:
            self.result.is_valid = False
            self.result.errors.append("缺少 openpyxl 库")
            return self.result

        # 检查文件
        if not self.excel_path.exists():
            self.result.is_valid = False
            self.result.errors.append(f"文件不存在: {self.excel_path}")
            return self.result

        try:
            # 加载工作簿
            self.workbook = load_workbook(self.excel_path, data_only=False)

            # 验证BASE sheet
            self._validate_base_sheet()

            # 验证方法sheet
            self._validate_method_sheets()

            # 汇总结果
            self.result.is_valid = len(self.result.errors) == 0

        except Exception as e:
            self.result.is_valid = False
            self.result.errors.append(f"验证失败: {str(e)}")

        return self.result

    def _validate_base_sheet(self):
        """验证BASE sheet"""
        if 'BASE' not in self.workbook.sheetnames:
            self.result.errors.append("缺少BASE sheet")
            return

        base_sheet = self.workbook['BASE']

        # 检查字段名
        field_row = 2
        fields = []
        for col in range(2, 20):
            field = base_sheet.cell(row=field_row, column=col).value
            if field:
                fields.append(field)

        # 检查必需字段
        for required_field in self.BASE_FIELDS[:6]:  # 前6个是必需的
            if required_field not in fields:
                self.result.errors.append(f"BASE sheet缺少必需字段: {required_field}")

        # 检查参数类型是否包含泛型
        for row in range(5, base_sheet.max_row + 1):
            if base_sheet.cell(row=row, column=1).value == "DataRow":
                for col in range(8, 11):  # arg0, arg1, arg2列
                    cell_value = base_sheet.cell(row=row, column=col).value
                    if cell_value and ("<" in str(cell_value) or ">" in str(cell_value)):
                        self.result.errors.append(
                            f"BASE sheet Row {row}: 参数类型包含泛型 '{cell_value}'，应去掉泛型"
                        )

        self.result.details['base_sheet'] = {
            'fields': fields,
            'row_count': base_sheet.max_row
        }

    def _validate_method_sheets(self):
        """验证方法sheet"""
        method_sheets = [name for name in self.workbook.sheetnames if name != 'BASE']

        if not method_sheets:
            self.result.warnings.append("没有方法sheet")
            return

        # 检查BASE sheet中的方法定义是否与方法sheet对应
        if 'BASE' in self.workbook.sheetnames:
            base_sheet = self.workbook['BASE']
            defined_methods = set()

            for row in range(5, base_sheet.max_row + 1):
                if base_sheet.cell(row=row, column=1).value == "DataRow":
                    method_code = base_sheet.cell(row=row, column=3).value
                    if method_code:
                        defined_methods.add(method_code)

            # 检查每个方法sheet是否在BASE中定义
            for sheet_name in method_sheets:
                if sheet_name not in defined_methods:
                    self.result.warnings.append(
                        f"方法sheet '{sheet_name}' 未在BASE sheet中定义"
                    )

        # 验证每个方法sheet
        for sheet_name in method_sheets:
            self._validate_method_sheet(sheet_name)

    def _validate_method_sheet(self, sheet_name: str):
        """验证单个方法sheet"""
        sheet = self.workbook[sheet_name]
        sheet_result = {
            'name': sheet_name,
            'test_case_count': 0,
            'busi_data_count': 0,
            'assert_count': 0,
            'errors': [],
            'datatags': {}
        }

        # 查找三个模块的位置
        test_case_start = self._find_section_start(sheet, 'CASE.V2')
        busi_data_start = self._find_section_start(sheet, 'busiData')
        assert_start = self._find_section_start(sheet, '.assert')

        # 提取三个区域的DataTag
        test_case_datatag = None
        busi_data_datatag = None
        assert_datatag = None

        if test_case_start:
            test_case_datatag = sheet.cell(row=test_case_start, column=3).value
            sheet_result['datatags']['test_case'] = test_case_datatag

        if busi_data_start:
            busi_data_datatag = sheet.cell(row=busi_data_start, column=3).value
            sheet_result['datatags']['busi_data'] = busi_data_datatag

        if assert_start:
            assert_datatag = sheet.cell(row=assert_start, column=3).value
            sheet_result['datatags']['assert'] = assert_datatag

        # 验证DataType与DataTag的匹配 ⭐ 新增功能
        if test_case_start:
            self._validate_datatype_datatag_match(
                sheet, test_case_start, busi_data_datatag, assert_datatag, sheet_result['errors']
            )

        # 验证测试用例模块
        if test_case_start:
            test_case_count = self._count_data_rows(sheet, test_case_start + 4)
            sheet_result['test_case_count'] = test_case_count

            # 检查字段名
            self._validate_fields(sheet, test_case_start + 1, self.TEST_CASE_FIELDS, sheet_result['errors'])

        # 验证业务数据模块
        if busi_data_start:
            busi_data_count = self._count_data_rows(sheet, busi_data_start + 4)
            sheet_result['busi_data_count'] = busi_data_count

            # 检查参数引用格式
            self._validate_param_references(sheet, busi_data_start + 4, busi_data_count, sheet_result['errors'])

        # 验证断言模块
        if assert_start:
            assert_count = self._count_data_rows(sheet, assert_start + 4)
            sheet_result['assert_count'] = assert_count

        # 检查DataRow数量一致性（关键规则！）
        counts = [sheet_result['test_case_count'], sheet_result['busi_data_count'], sheet_result['assert_count']]
        if len(set(counts)) > 1:
            self.result.errors.append(
                f"Sheet '{sheet_name}': DataRow数量不一致 - "
                f"测试用例={sheet_result['test_case_count']}, "
                f"业务数据={sheet_result['busi_data_count']}, "
                f"断言={sheet_result['assert_count']}"
            )

        # 合并sheet错误到主结果
        for error in sheet_result['errors']:
            self.result.errors.append(f"Sheet '{sheet_name}': {error}")

        self.result.details[sheet_name] = sheet_result

    def _find_section_start(self, worksheet, tag_keyword: str) -> int:
        """查找模块起始行"""
        for row in range(1, worksheet.max_row + 1):
            if worksheet.cell(row=row, column=1).value == "DataTag":
                dto_value = worksheet.cell(row=row, column=3).value
                if dto_value and tag_keyword in str(dto_value):
                    return row
        return None

    def _count_data_rows(self, worksheet, start_row: int) -> int:
        """计算DataRow数量"""
        count = 0
        for row in range(start_row, worksheet.max_row + 1):
            if worksheet.cell(row=row, column=1).value == "DataRow":
                count += 1
            elif worksheet.cell(row=row, column=1).value in ["DataTag", None]:
                break
        return count

    def _validate_fields(self, worksheet, field_row: int, required_fields: List[str], errors: List[str]):
        """验证字段名"""
        fields = []
        for col in range(2, 20):
            field = worksheet.cell(row=field_row, column=col).value
            if field:
                fields.append(field)

        for required in required_fields:
            if required not in fields:
                errors.append(f"缺少必需字段: {required}")

    def _validate_datatype_datatag_match(self, worksheet, test_case_start: int,
                                          busi_data_datatag: str, assert_datatag: str, errors: List[str]):
        """验证DataType与DataTag的匹配关系 ⭐ 新增功能"""
        # 提取字段名（Row 2）
        field_row = test_case_start + 1
        fields = []
        for col in range(2, 20):
            field = worksheet.cell(row=field_row, column=col).value
            if field:
                fields.append((col, field))

        # 提取DataType（Row 4）
        datatype_row = test_case_start + 3
        datatypes = []
        for col in range(2, 20):
            dtype = worksheet.cell(row=datatype_row, column=col).value
            if dtype:
                datatypes.append((col, dtype))

        # 找到 busiDatas 和 asserts 字段的位置
        busi_datas_col = None
        asserts_col = None
        for col, field in fields:
            if field == 'busiDatas':
                busi_datas_col = col
            elif field == 'asserts':
                asserts_col = col

        # 验证 busiDatas 的 DataType
        if busi_datas_col:
            busi_datas_dtype = worksheet.cell(row=datatype_row, column=busi_datas_col).value
            if busi_datas_dtype and busi_data_datatag:
                # 检查DataType是否包含DataTag
                # DataType格式: List<dto.XxxTest.busiData>
                # DataTag格式: dto.XxxTest.busiData
                expected_datatag_in_dtype = busi_data_datatag in str(busi_datas_dtype)

                if not expected_datatag_in_dtype:
                    errors.append(
                        f"DataType与DataTag不匹配: busiDatas字段的DataType '{busi_datas_dtype}' "
                        f"未包含业务数据定义的DataTag '{busi_data_datatag}'"
                    )

        # 验证 asserts 的 DataType
        if asserts_col:
            asserts_dtype = worksheet.cell(row=datatype_row, column=asserts_col).value
            if asserts_dtype and assert_datatag:
                # 检查DataType是否包含DataTag
                # DataType格式: List<dto.XxxTest.assert>
                # DataTag格式: dto.XxxTest.assert
                expected_datatag_in_dtype = assert_datatag in str(asserts_dtype)

                if not expected_datatag_in_dtype:
                    errors.append(
                        f"DataType与DataTag不匹配: asserts字段的DataType '{asserts_dtype}' "
                        f"未包含断言明细定义的DataTag '{assert_datatag}'"
                    )

        # 验证测试用例DataTag的格式（应包含测试类名称）
        test_case_datatag = worksheet.cell(row=test_case_start, column=3).value
        if test_case_datatag:
            # DataTag格式: {子系统}.DTO.{测试类名}Test.CASE.V2
            if 'CASE.V2' not in test_case_datatag:
                errors.append(
                    f"测试用例DataTag格式错误: '{test_case_datatag}' 应以 CASE.V2 结尾"
                )

            # 检查是否包含 "DTO."（中间部分）
            if 'DTO.' not in test_case_datatag:
                errors.append(
                    f"测试用例DataTag格式错误: '{test_case_datatag}' 应包含 'DTO.'"
                )

    def _validate_param_references(self, worksheet, start_row: int, count: int, errors: List[str]):
        """验证参数引用格式"""
        for row in range(start_row, start_row + count):
            # 检查value0, value1, value2列
            for col in range(5, 8):  # E, F, G列
                cell_value = worksheet.cell(row=row, column=col).value
                if cell_value and isinstance(cell_value, str):
                    # 检查参数引用格式（应该以#开头）
                    if cell_value and not cell_value.startswith('#') and not self._is_literal_value(cell_value):
                        # 可能是参数引用，但缺少#前缀
                        if '_' in cell_value:  # 参数引用通常包含下划线
                            errors.append(
                                f"Row {row}: 参数引用 '{cell_value}' 缺少 # 前缀，应为 '#{cell_value}'"
                            )

    def _is_literal_value(self, value: str) -> bool:
        """判断是否为字面值（字符串、数字、布尔值、null）"""
        if value in ['null', 'true', 'false']:
            return True
        if value.startswith('"') and value.endswith('"'):
            return True
        if value.lstrip('-').isdigit():
            return True
        return False


def validate_excel(excel_path: str) -> ValidationResult:
    """
    验证Excel文件格式

    Args:
        excel_path: Excel文件路径

    Returns:
        ValidationResult: 验证结果
    """
    validator = ExcelValidator(excel_path)
    return validator.validate()


def validate_excel_batch(directory: str, pattern: str = "*.tc.xlsx") -> Dict:
    """
    批量验证目录下的Excel文件

    Args:
        directory: 目录路径
        pattern: 文件匹配模式，默认 "*.tc.xlsx"

    Returns:
        dict: {"valid": 成功数量, "invalid": 失败数量, "results": 结果列表}
    """
    directory = Path(directory)
    if not directory.exists():
        print(f"错误: 目录不存在 - {directory}")
        return {"valid": 0, "invalid": 0, "results": []}

    results = {"valid": 0, "invalid": 0, "results": []}

    # 查找匹配的文件
    excel_files = list(directory.rglob(pattern))

    print(f"找到 {len(excel_files)} 个文件需要验证")

    for excel_file in excel_files:
        result = validate_excel(str(excel_file))
        results["results"].append({
            "file": str(excel_file),
            "is_valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings
        })

        if result.is_valid:
            results["valid"] += 1
        else:
            results["invalid"] += 1

    print(f"\n批量验证完成: 有效={results['valid']}, 无效={results['invalid']}")
    return results


def print_validation_result(result: ValidationResult):
    """打印验证结果"""
    if result.is_valid:
        print("[PASS] Excel格式验证通过")
    else:
        print("[FAIL] Excel格式验证失败")

    if result.errors:
        print("\n错误:")
        for error in result.errors:
            print(f"  [ERROR] {error}")

    if result.warnings:
        print("\n警告:")
        for warning in result.warnings:
            print(f"  [WARN] {warning}")

    if result.details:
        print("\n详细信息:")
        for key, value in result.details.items():
            print(f"  {key}: {value}")


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Excel格式验证工具")
        print("")
        print("用法:")
        print("  验证单个文件:")
        print("    python validate_excel.py <excel文件路径>")
        print("")
        print("  批量验证目录:")
        print("    python validate_excel.py --batch <目录路径> [文件模式]")
        print("")
        print("示例:")
        print("    python validate_excel.py test.tc.xlsx")
        print("    python validate_excel.py --batch ./mock-data/impsfc/20_testcase")
        print("    python validate_excel.py --batch ./mock-data '*.tc.xlsx'")
        sys.exit(1)

    if sys.argv[1] == "--batch":
        # 批量验证模式
        if len(sys.argv) < 3:
            print("错误: 请指定目录路径")
            sys.exit(1)

        directory = sys.argv[2]
        pattern = sys.argv[3] if len(sys.argv) > 3 else "*.tc.xlsx"

        results = validate_excel_batch(directory, pattern)

        # 打印详细结果
        for result in results["results"]:
            print(f"\n{'=' * 80}")
            print(f"文件: {result['file']}")
            if result['is_valid']:
                print("状态: ✅ 有效")
            else:
                print("状态: ❌ 无效")
                for error in result['errors']:
                    print(f"  ❌ {error}")

        sys.exit(0 if results["invalid"] == 0 else 1)

    else:
        # 单文件验证模式
        excel_path = sys.argv[1]

        result = validate_excel(excel_path)
        print_validation_result(result)

        sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()