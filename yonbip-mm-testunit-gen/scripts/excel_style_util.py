# -*- coding: utf-8 -*-
"""
Excel样式支持模块
为单元测试Excel文件添加标准样式
支持动态DataRow数量
"""

from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter


class ExcelStyleUtil:
    """Excel样式工具类"""

    # ==================== 样式定义 ====================

    # 字体样式
    FONT_HEADER = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
    FONT_TITLE = Font(name='微软雅黑', size=11, bold=True, color='000000')
    FONT_NORMAL = Font(name='微软雅黑', size=10, color='000000')
    FONT_TAG = Font(name='微软雅黑', size=10, bold=True, color='FFFFFF')

    # 对齐样式
    ALIGN_CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ALIGN_LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # 边框样式
    THIN_BORDER = Border(
        left=Side(style='thin', color='B4B4B4'),
        right=Side(style='thin', color='B4B4B4'),
        top=Side(style='thin', color='B4B4B4'),
        bottom=Side(style='thin', color='B4B4B4')
    )

    # 填充颜色
    # DataTag行 - 深蓝色
    FILL_TAG = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    # DataField行 - 浅蓝色
    FILL_FIELD = PatternFill(start_color='D6DCE4', end_color='D6DCE4', fill_type='solid')
    # DataTitle行 - 浅灰色
    FILL_TITLE = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')
    # DataType行 - 白色
    FILL_TYPE = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
    # DataRow行 - 浅绿色
    FILL_ROW = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')

    # ==================== 行类型常量 ====================

    ROW_TYPE_TAG = 'DataTag'
    ROW_TYPE_FIELD = 'DataField'
    ROW_TYPE_TITLE = 'DataTitle'
    ROW_TYPE_TYPE = 'DataType'
    ROW_TYPE_DATA = 'DataRow'
    ROW_TYPE_FOREIGN = 'ForeignKey'

    @classmethod
    def apply_row_style(cls, worksheet, row_number: int, row_type: str, max_col: int = 15):
        """
        为指定行应用样式

        Args:
            worksheet: 工作表对象
            row_number: 行号
            row_type: 行类型 (DataTag/DataField/DataTitle/DataType/DataRow)
            max_col: 最大列数
        """
        if row_type == cls.ROW_TYPE_TAG:
            font = cls.FONT_TAG
            fill = cls.FILL_TAG
            alignment = cls.ALIGN_CENTER
        elif row_type == cls.ROW_TYPE_FIELD:
            font = cls.FONT_TITLE
            fill = cls.FILL_FIELD
            alignment = cls.ALIGN_CENTER
        elif row_type == cls.ROW_TYPE_TITLE:
            font = cls.FONT_NORMAL
            fill = cls.FILL_TITLE
            alignment = cls.ALIGN_CENTER
        elif row_type == cls.ROW_TYPE_TYPE:
            font = cls.FONT_NORMAL
            fill = cls.FILL_TYPE
            alignment = cls.ALIGN_CENTER
        elif row_type == cls.ROW_TYPE_DATA:
            font = cls.FONT_NORMAL
            fill = cls.FILL_ROW
            alignment = cls.ALIGN_LEFT
        else:
            return

        for col in range(1, max_col + 1):
            cell = worksheet.cell(row=row_number, column=col)
            cell.font = font
            cell.fill = fill
            cell.alignment = alignment
            cell.border = cls.THIN_BORDER

    @classmethod
    def find_section_rows(cls, worksheet) -> dict:
        """
        基于DataTag动态检测各区域的起始行

        通过扫描第一列的DataTag标记，确定各模块的实际位置，
        避免依赖固定的空行数量。

        Args:
            worksheet: 工作表对象

        Returns:
            dict: {'test_case': row, 'busi_data': row, 'assert': row}
        """
        sections = {}
        for row in range(1, worksheet.max_row + 1):
            if worksheet.cell(row=row, column=1).value == cls.ROW_TYPE_TAG:
                # 获取DTO列的值（第3列）
                dto_value = worksheet.cell(row=row, column=3).value
                if dto_value:
                    dto_str = str(dto_value)
                    if 'CASE.V2' in dto_str or '测试列表' in str(worksheet.cell(row=row, column=4).value or ''):
                        sections['test_case'] = row
                    elif 'busiData' in dto_str or '业务数据' in str(worksheet.cell(row=row, column=4).value or ''):
                        sections['busi_data'] = row
                    elif '.assert' in dto_str or '断言' in str(worksheet.cell(row=row, column=4).value or ''):
                        sections['assert'] = row
        return sections

    @classmethod
    def apply_module_style(cls, worksheet, tag_row: int) -> int:
        """
        为一个模块应用样式（从DataTag行开始）

        Args:
            worksheet: 工作表对象
            tag_row: DataTag所在行号

        Returns:
            int: DataRow的数量
        """
        # 应用表头样式: DataTag, DataField, DataTitle, DataType
        cls.apply_row_style(worksheet, tag_row, cls.ROW_TYPE_TAG)
        cls.apply_row_style(worksheet, tag_row + 1, cls.ROW_TYPE_FIELD)
        cls.apply_row_style(worksheet, tag_row + 2, cls.ROW_TYPE_TITLE)
        cls.apply_row_style(worksheet, tag_row + 3, cls.ROW_TYPE_TYPE)

        # 计算并应用DataRow样式
        data_row_start = tag_row + 4
        data_row_count = cls.count_data_rows_in_module(worksheet, data_row_start)

        for row in range(data_row_start, data_row_start + data_row_count):
            cls.apply_row_style(worksheet, row, cls.ROW_TYPE_DATA)

        return data_row_count

    @classmethod
    def apply_sheet_style_dynamic(cls, worksheet, test_case_count: int = None):
        """
        为整个sheet应用样式 - 基于DataTag动态检测（稳健方案）

        不依赖固定的空行数量，而是扫描实际的DataTag位置来应用样式。

        Args:
            worksheet: 工作表对象
            test_case_count: 测试用例数量（仅用于向后兼容，实际会自动检测）
        """
        # 动态检测各区域位置
        sections = cls.find_section_rows(worksheet)

        # 应用测试用例模块样式
        if 'test_case' in sections:
            cls.apply_module_style(worksheet, sections['test_case'])

        # 应用业务数据模块样式
        if 'busi_data' in sections:
            cls.apply_module_style(worksheet, sections['busi_data'])

        # 应用断言模块样式
        if 'assert' in sections:
            cls.apply_module_style(worksheet, sections['assert'])

    @classmethod
    def apply_sheet_style(cls, worksheet, has_busi_data: bool = True, has_assert: bool = True):
        """
        为整个sheet应用样式 - 固定格式（向后兼容）

        标准格式包含3个模块：
        1. 测试用例模块 (Row 1-5)
        2. 业务数据模块 (Row 8-12)
        3. 断言明细模块 (Row 15-19)
        """
        # ===== 模块1: 测试用例 (Row 1-5) =====
        cls.apply_row_style(worksheet, 1, cls.ROW_TYPE_TAG)
        cls.apply_row_style(worksheet, 2, cls.ROW_TYPE_FIELD)
        cls.apply_row_style(worksheet, 3, cls.ROW_TYPE_TITLE)
        cls.apply_row_style(worksheet, 4, cls.ROW_TYPE_TYPE)
        cls.apply_row_style(worksheet, 5, cls.ROW_TYPE_DATA)

        if has_busi_data:
            # ===== 模块2: 业务数据 (Row 8-12) =====
            cls.apply_row_style(worksheet, 8, cls.ROW_TYPE_TAG)
            cls.apply_row_style(worksheet, 9, cls.ROW_TYPE_FIELD)
            cls.apply_row_style(worksheet, 10, cls.ROW_TYPE_TITLE)
            cls.apply_row_style(worksheet, 11, cls.ROW_TYPE_TYPE)
            cls.apply_row_style(worksheet, 12, cls.ROW_TYPE_DATA)

        if has_assert:
            # ===== 模块3: 断言明细 (Row 15-19) =====
            cls.apply_row_style(worksheet, 15, cls.ROW_TYPE_TAG)
            cls.apply_row_style(worksheet, 16, cls.ROW_TYPE_FIELD)
            cls.apply_row_style(worksheet, 17, cls.ROW_TYPE_TITLE)
            cls.apply_row_style(worksheet, 18, cls.ROW_TYPE_TYPE)
            cls.apply_row_style(worksheet, 19, cls.ROW_TYPE_DATA)

    @classmethod
    def apply_base_sheet_style(cls, worksheet, row_count: int = 5):
        """
        为BASE sheet应用样式
        BASE sheet只有一行DataTag/Field/Title/Type，然后是DataRow
        """
        cls.apply_row_style(worksheet, 1, cls.ROW_TYPE_TAG)
        cls.apply_row_style(worksheet, 2, cls.ROW_TYPE_FIELD)
        cls.apply_row_style(worksheet, 3, cls.ROW_TYPE_TITLE)
        cls.apply_row_style(worksheet, 4, cls.ROW_TYPE_TYPE)

        for row in range(5, row_count + 1):
            cls.apply_row_style(worksheet, row, cls.ROW_TYPE_DATA)

    @classmethod
    def set_column_width(cls, worksheet, widths: list = None):
        """
        设置列宽

        Args:
            worksheet: 工作表对象
            widths: 列宽列表，如 [15, 20, 40, ...]
        """
        if widths is None:
            # 默认列宽
            widths = [12, 15, 30, 40, 10, 30, 30, 30, 30, 30, 30, 30]

        for i, width in enumerate(widths, 1):
            worksheet.column_dimensions[get_column_letter(i)].width = width

    @classmethod
    def count_data_rows_in_module(cls, worksheet, start_row: int) -> int:
        """
        计算从start_row开始的连续DataRow数量

        Args:
            worksheet: 工作表对象
            start_row: 开始行号

        Returns:
            DataRow数量
        """
        count = 0
        for row in range(start_row, worksheet.max_row + 1):
            cell_value = worksheet.cell(row=row, column=1).value
            if cell_value == 'DataRow':
                count += 1
            elif cell_value in ['DataTag', 'DataField', 'DataTitle', 'DataType', None]:
                # 遇到新模块或空行，停止计数
                break
        return count

    @classmethod
    def style_full_workbook(cls, workbook, test_case_count: int = None):
        """
        为整个工作簿应用样式

        Args:
            workbook: 工作簿对象
            test_case_count: 测试用例数量，如果为None则自动检测
        """
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]

            if sheet_name == 'BASE':
                # BASE sheet - 计算DataRow数量
                row_count = cls.count_data_rows_in_module(worksheet, 5) + 4
                cls.apply_base_sheet_style(worksheet, row_count)
            else:
                # 方法sheet - 使用动态样式
                if test_case_count is None:
                    # 自动检测DataRow数量（从Row 5开始）
                    test_case_count = cls.count_data_rows_in_module(worksheet, 5)
                cls.apply_sheet_style_dynamic(worksheet, test_case_count)

            # 设置列宽
            cls.set_column_width(worksheet)