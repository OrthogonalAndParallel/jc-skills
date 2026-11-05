# -*- coding: utf-8 -*-
"""
单元测试用例生成工具 - Python版本
功能：根据Java类和方法信息自动生成单元测试Excel文件和Java测试类代码

使用方式：
1. 修改下方配置参数（subId, className, methodName）
2. 运行脚本：python test_case_generator.py

依赖：
- openpyxl: Excel文件处理
"""

import os
import sys
import io
import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path

# 导入样式工具
try:
    from excel_style_util import ExcelStyleUtil
    HAS_STYLE_UTIL = True
except ImportError:
    HAS_STYLE_UTIL = False

# 设置UTF-8编码输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# ============== 数据类定义（必须放在前面） ==============
@dataclass
class Attr:
    """生成属性配置"""
    gen_java: bool = True
    gen_xlsx: bool = True
    xlsx_eg_value: bool = True
    xlsx_eg_assert: bool = True
    java_mock_method: bool = True
    auto_ext_param: bool = True  # 自动生成@ExtParam方法
    auto_init_mock: bool = True  # 自动生成initMock方法
    test_case_count: int = 7  # 测试用例数量（动态可配置）
    related_task_number: str = ""  # PM问题号（自动填充到relatedTask列）✨

@dataclass
class MethodInfo:
    """方法信息"""
    name: str
    return_type: str
    parameters: List[Tuple[str, str]]
    declaring_class: str
    throws: List[str] = field(default_factory=list)  # 异常类型列表 ✨

@dataclass
class FieldInfo:
    """字段信息（用于mock）"""
    name: str
    type_name: str
    has_annotation: bool = False

@dataclass
class MockCallInfo:
    """Mock方法调用信息"""
    field_name: str  # 字段名（如 commonOperation）
    method_name: str  # 方法名（如 preProcessFilter）
    return_type: str = ""  # 返回类型
    params: List[str] = field(default_factory=list)  # 参数类型列表

@dataclass
class StaticCallInfo:
    """静态方法调用信息"""
    class_name: str  # 类名（如 BillInfoUtils）
    full_class_name: str  # 全限定类名
    method_name: str  # 方法名
    params: List[str] = field(default_factory=list)  # 参数列表


# ============== Import分析器 ==============
class ImportAnalyzer:
    """Java import依赖分析器 - 确保生成的代码包含完整的import语句 ✨"""

    # 框架必需的import（测试框架核心依赖）
    FRAMEWORK_IMPORTS = {
        'MFUnitTest': [
            'org.junit.jupiter.api.BeforeEach',
            'org.junit.jupiter.api.Test',
            'org.mockito.InjectMocks',
            'org.mockito.Mock',
            'org.mockito.MockedStatic',
            'org.mockito.Mockito',
            'com.yonyou.biz.mm.common.ut.base.Asserts',
            'com.yonyou.biz.mm.common.ut.meta.MetaDatasource',
            'com.yonyou.biz.mm.common.ut.mock.MetaDatasourceMock',
            'com.yonyou.biz.mm.common.ut.tools.annotation.ExtParam',
            'com.yonyou.biz.mm.common.ut.tools.constants.VersionConstant',
        ]
    }

    # Java常用类型（无需import）
    JAVA_LANG_TYPES = {
        'String', 'Integer', 'Long', 'Boolean', 'Double', 'Float',
        'Byte', 'Short', 'Character', 'Object', 'Class', 'Exception',
        'RuntimeException', 'Throwable', 'Override'
    }

    # 常用集合类型（需要import）
    COLLECTION_TYPES = {
        'List': 'java.util.List',
        'Map': 'java.util.Map',
        'Set': 'java.util.Set',
        'ArrayList': 'java.util.ArrayList',
        'HashMap': 'java.util.HashMap',
        'HashSet': 'java.util.HashSet',
    }

    # 常用日期类型
    DATE_TYPES = {
        'Date': 'java.util.Date',
        'LocalDate': 'java.time.LocalDate',
        'LocalDateTime': 'java.time.LocalDateTime',
    }

    @staticmethod
    def analyze_imports(
        target_class: str,
        methods: List[MethodInfo],
        mock_fields: List[FieldInfo],
        static_calls: List[StaticCallInfo],
        sub_id: str
    ) -> Set[str]:
        """
        分析所有需要的import语句

        Args:
            target_class: 被测类全限定名
            methods: 方法信息列表
            mock_fields: Mock字段列表
            static_calls: 静态方法调用列表
            sub_id: 子系统标识

        Returns:
            完整的import集合（已去重）
        """
        imports = set()

        # 1. 框架必需import
        imports.update(ImportAnalyzer.FRAMEWORK_IMPORTS['MFUnitTest'])

        # 2. 被测类的import（解析被测类源码）
        source_imports = ImportAnalyzer._analyze_source_class_imports(target_class)
        imports.update(source_imports)

        # 3. 方法签名相关的import
        method_imports = ImportAnalyzer._analyze_method_signatures(methods)
        imports.update(method_imports)

        # 4. Mock字段的import
        mock_imports = ImportAnalyzer._analyze_mock_fields(mock_fields)
        imports.update(mock_imports)

        # 5. 静态方法调用的import
        static_imports = ImportAnalyzer._analyze_static_calls(static_calls)
        imports.update(static_imports)

        # 6. 子系统基类的import
        base_import = ImportAnalyzer._get_base_class_import(sub_id)
        if base_import:
            imports.add(base_import)

        # 7. 额外的必需import
        extra_imports = ImportAnalyzer._analyze_extra_imports(methods, mock_fields)
        imports.update(extra_imports)

        # 过滤掉java.lang包的类型（无需import）
        imports = ImportAnalyzer._filter_java_lang(imports)

        return imports

    @staticmethod
    def _analyze_source_class_imports(target_class: str) -> Set[str]:
        """解析被测类的import语句"""
        imports = set()

        java_file = JavaSourceParser.find_java_file(target_class)
        if not java_file:
            return imports

        content = java_file.read_text(encoding='utf-8')

        # 提取import语句
        import_pattern = r'import\s+([\w.]+)\s*;'
        for match in re.finditer(import_pattern, content):
            import_stmt = match.group(1)
            # 排除java.lang包
            if not import_stmt.startswith('java.lang.'):
                imports.add(import_stmt)

        return imports

    @staticmethod
    def _analyze_method_signatures(methods: List[MethodInfo]) -> Set[str]:
        """分析方法签名相关的import（参数、返回值、异常）"""
        imports = set()

        for method in methods:
            # 参数类型
            for param_type, _ in method.parameters:
                full_type = ImportAnalyzer._get_full_type_name(param_type)
                if full_type:
                    imports.add(full_type)

            # 返回值类型
            if method.return_type and method.return_type != 'void':
                full_type = ImportAnalyzer._get_full_type_name(method.return_type)
                if full_type:
                    imports.add(full_type)

            # 异常类型
            for exception_type in method.throws:
                full_type = ImportAnalyzer._get_full_type_name(exception_type)
                if full_type:
                    imports.add(full_type)

        return imports

    @staticmethod
    def _analyze_mock_fields(mock_fields: List[FieldInfo]) -> Set[str]:
        """分析Mock字段的import"""
        imports = set()

        for field in mock_fields:
            full_type = ImportAnalyzer._get_full_type_name(field.type_name)
            if full_type:
                imports.add(full_type)

        return imports

    @staticmethod
    def _analyze_static_calls(static_calls: List[StaticCallInfo]) -> Set[str]:
        """分析静态方法调用的import"""
        imports = set()

        for call in static_calls:
            if call.full_class_name:
                imports.add(call.full_class_name)

        # 静态Mock插件
        if static_calls:
            imports.add('com.yonyou.biz.mm.mfpo.ut.sfc.plugins.BillInfoUtilsPlugin')

        return imports

    @staticmethod
    def _get_base_class_import(sub_id: str) -> Optional[str]:
        """获取子系统基类的import"""
        base_class_map = {
            "PO": "com.yonyou.biz.mm.mfpo.ut.po.POTestable",
            "IMPSFC": "com.yonyou.biz.mm.mfpo.ut.sfc.SFCTestable",
            "MR": "com.yonyou.biz.mm.common.ut.tools.MFTestable",
            "OSM": "com.yonyou.biz.mm.common.ut.tools.MFTestable",
            "QMS": "com.yonyou.biz.mm.common.ut.tools.MFTestable",
            "QIC": "com.yonyou.biz.mm.common.ut.tools.MFTestable",
            "ED": "com.yonyou.biz.mm.common.ut.tools.MFTestable",
            "ECN": "com.yonyou.biz.mm.common.ut.tools.MFTestable"
        }
        return base_class_map.get(sub_id)

    @staticmethod
    def _analyze_extra_imports(methods: List[MethodInfo], mock_fields: List[FieldInfo]) -> Set[str]:
        """分析额外的必需import（基于常见使用场景）"""
        imports = set()

        # 分析@ExtParam方法中可能用到的类型
        for method in methods:
            for param_type, param_name in method.parameters:
                # BillContext相关
                if 'BillContext' in param_type or 'billContext' in param_name.lower():
                    imports.add('com.yonyou.ucf.mdd.ext.model.BillContext')

                # BillDataDto相关
                if 'BillDataDto' in param_type or 'Map' in param_type:
                    imports.add('com.yonyou.ucf.mdd.ext.bill.dto.BillDataDto')
                    imports.add('com.yonyou.ucf.mdd.core.utils.vo.QueryPagerVo')

        # 常用的数据类型
        imports.add('java.util.HashMap')
        imports.add('java.util.Map')
        imports.add('java.io.InputStream')

        return imports

    @staticmethod
    def _get_full_type_name(type_name: str) -> Optional[str]:
        """
        获取类型的全限定名

        Args:
            type_name: 类型名（可能是简单名或全限定名）

        Returns:
            全限定名，如果是基本类型则返回None
        """
        # 移除泛型部分
        if '<' in type_name:
            type_name = type_name[:type_name.index('<')]

        # 移除数组标记
        type_name = type_name.replace('[]', '').strip()

        # 基本类型和void无需import
        basic_types = {
            'void', 'int', 'long', 'boolean', 'double', 'float',
            'byte', 'short', 'char'
        }
        if type_name.lower() in basic_types or type_name in basic_types:
            return None

        # Java lang类型无需import
        if type_name in ImportAnalyzer.JAVA_LANG_TYPES:
            return None

        # 已经是全限定名
        if '.' in type_name:
            # 排除java.lang包
            if type_name.startswith('java.lang.'):
                return None
            return type_name

        # 集合类型
        if type_name in ImportAnalyzer.COLLECTION_TYPES:
            return ImportAnalyzer.COLLECTION_TYPES[type_name]

        # 日期类型
        if type_name in ImportAnalyzer.DATE_TYPES:
            return ImportAnalyzer.DATE_TYPES[type_name]

        # 简单类型名，无法确定包名，返回None（让调用者从被测类import中查找）
        return None

    @staticmethod
    def _filter_java_lang(imports: Set[str]) -> Set[str]:
        """过滤掉java.lang包的类型"""
        return {imp for imp in imports if not imp.startswith('java.lang.')}

    @staticmethod
    def sort_imports(imports: Set[str]) -> List[str]:
        """
        对import语句排序（按照java.* -> com.* -> org.* -> 其他）

        Args:
            imports: import集合

        Returns:
            排序后的import列表
        """
        java_imports = []
        com_imports = []
        org_imports = []
        other_imports = []

        for imp in imports:
            if imp.startswith('java.'):
                java_imports.append(imp)
            elif imp.startswith('com.'):
                com_imports.append(imp)
            elif imp.startswith('org.'):
                org_imports.append(imp)
            else:
                other_imports.append(imp)

        # 每组内部排序
        java_imports.sort()
        com_imports.sort()
        org_imports.sort()
        other_imports.sort()

        # 合并返回
        result = []
        result.extend(java_imports)
        result.extend(com_imports)
        result.extend(org_imports)
        result.extend(other_imports)

        return result

    @staticmethod
    def detect_missing_imports(java_code: str, required_types: Set[str]) -> List[str]:
        """
        检测Java代码中缺失的import

        Args:
            java_code: Java代码
            required_types: 需要import的类型集合

        Returns:
            缺失的import列表
        """
        # 提取已有的import
        import_pattern = r'import\s+([\w.]+)\s*;'
        existing_imports = set()
        for match in re.finditer(import_pattern, java_code):
            existing_imports.add(match.group(1))

        # 检测缺失的import
        missing = []
        for type_name in required_types:
            # 如果不是java.lang，且未import
            if not type_name.startswith('java.lang.') and type_name not in existing_imports:
                missing.append(type_name)

        return missing


# ============== Java源码解析器 ==============
class JavaSourceParser:
    """解析Java源代码文件，提取类信息（模拟Java反射）"""

    @staticmethod
    def find_java_file(class_name: str) -> Optional[Path]:
        """根据类全限定名查找Java源文件"""
        project_root = GenerateNameUtil.get_project_root()
        # 将类名转换为文件路径
        relative_path = class_name.replace('.', os.sep) + ".java"

        # 在多种可能的项目结构中查找
        search_paths = [
            # 标准Maven项目结构: src/manufacturing-service/src/main/java
            project_root / "src" / "manufacturing-service" / "src" / "main" / "java" / relative_path,
            # 直接src/main/java
            project_root / "src" / "main" / "java" / relative_path,
            # production-order子目录结构
            project_root / "production-order" / "src" / "manufacturing-service" / "src" / "main" / "java" / relative_path,
        ]

        for path in search_paths:
            if path.exists():
                return path

        return None

    @staticmethod
    def parse_java_file(file_path: Path) -> Dict:
        """解析Java文件，提取类信息"""
        if not file_path or not file_path.exists():
            return {"fields": [], "methods": [], "package": "", "class_name": "", "imports": {}}

        content = file_path.read_text(encoding='utf-8')

        # 提取import语句，构建简单类名到完整类名的映射
        imports = JavaSourceParser.extract_imports(content)

        result = {
            "package": JavaSourceParser.extract_package(content),
            "class_name": JavaSourceParser.extract_class_name(content),
            "fields": JavaSourceParser.extract_fields(content, imports),
            "methods": [],
            "imports": imports
        }

        return result

    @staticmethod
    def extract_imports(content: str) -> Dict[str, str]:
        """提取import语句，返回 {简单类名: 完整类名} 映射"""
        imports = {}
        # 匹配 import xxx.xxx.ClassName;
        pattern = r'import\s+([\w.]+\.(\w+))\s*;'
        for full_name, simple_name in re.findall(pattern, content):
            imports[simple_name] = full_name
        return imports

    @staticmethod
    def extract_package(content: str) -> str:
        """提取包名"""
        match = re.search(r'package\s+([\w.]+)\s*;', content)
        return match.group(1) if match else ""

    @staticmethod
    def extract_class_name(content: str) -> str:
        """提取类名"""
        match = re.search(r'(?:public\s+)?class\s+(\w+)', content)
        return match.group(1) if match else ""

    @staticmethod
    def extract_fields(content: str, imports: Dict[str, str] = None) -> List[Dict]:
        """提取带有依赖注入注解的字段

        支持的注解：
        - @Autowired (Spring)
        - @Inject (JSR-330)
        - @Resource (JSR-250, javax.annotation.Resource)
        """
        fields = []
        if imports is None:
            imports = {}

        # 匹配带有依赖注入注解的字段
        # 支持以下格式：
        # @Autowired
        # private Type name;
        #
        # @Resource
        # private Type name;
        #
        # @Resource(name = "xxx")
        # private Type name;
        pattern = r'@(?:Autowired|Inject|Resource)(?:\([^)]*\))?\s*(?:\n\s*)?(?:private\s+)?(\w+(?:\.\w+)*)\s+(\w+)\s*;'
        matches = re.findall(pattern, content)

        for type_name, field_name in matches:
            # 过滤基本类型
            simple_types = ['String', 'Integer', 'Long', 'Boolean', 'Double', 'Float', 'Byte', 'Short', 'Character']
            simple_name = type_name.split('.')[-1]
            if simple_name in simple_types:
                continue

            # 如果类型名是简单名称，尝试通过import获取完整类名
            if '.' not in type_name and simple_name in imports:
                full_type_name = imports[simple_name]
            else:
                full_type_name = type_name

            fields.append({
                "name": field_name,
                "type": full_type_name,
                "has_annotation": True
            })

        return fields

    @staticmethod
    def extract_method_info(content: str, method_name: str, imports: Dict[str, str] = None) -> List[Dict]:
        """提取指定方法的信息（返回类型、参数、异常类型）✨"""
        methods = []

        # 匹配方法定义: 返回类型 方法名(参数列表) [throws 异常列表]
        # 先移除 @Override 等注解，简化匹配
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('@') and not stripped.startswith('@Autowired') and not stripped.startswith('@Inject') and not stripped.startswith('@Resource'):
                continue
            cleaned_lines.append(line)
        cleaned_content = '\n'.join(cleaned_lines)

        # 匹配方法定义（包含throws子句）
        # 格式: [修饰符] 返回类型 方法名(参数列表) [throws 异常1, 异常2]
        pattern = rf'(?:public|private|protected)?\s+(?:static\s+)?(?:final\s+)?([\w.<>,\s\[\]?]+)\s+{re.escape(method_name)}\s*\(([^)]*)\)(?:\s+throws\s+([\w\s,.<>]+))?'

        for match in re.finditer(pattern, cleaned_content):
            return_type = match.group(1).strip()
            params_str = match.group(2).strip()
            throws_str = match.group(3).strip() if match.group(3) else ""

            # 过滤非返回类型的关键字
            if return_type in ['if', 'for', 'while', 'switch', 'catch', 'class', 'interface']:
                continue

            # 清理返回类型前的修饰符
            modifiers = ['public ', 'private ', 'protected ', 'static ', 'final ', 'synchronized ']
            for mod in modifiers:
                if return_type.startswith(mod):
                    return_type = return_type[len(mod):].strip()

            # 解析参数（正确处理泛型）
            parameters = JavaSourceParser._parse_params(params_str, imports)

            # 解析异常类型 ✨
            throws = []
            if throws_str:
                # 分割异常列表
                exception_names = [e.strip() for e in throws_str.split(',')]
                for exc_name in exception_names:
                    if exc_name:
                        # 转换为全限定类名
                        full_name = JavaSourceParser._resolve_type_name(exc_name, imports)
                        throws.append(full_name)

            methods.append({
                "name": method_name,
                "return_type": return_type,
                "parameters": parameters,
                "throws": throws  # ✨ 新增异常类型
            })

        return methods

    @staticmethod
    def _parse_params(params_str: str, imports: Dict[str, str] = None) -> List[Tuple[str, str]]:
        """解析参数列表，正确处理泛型中的逗号

        例如: 'BillContext billContext, Map<String, Object> paramMap'
        返回: [('com.yonyou.ucf.mdd.ext.model.BillContext', 'billContext'), ('java.util.Map', 'paramMap')]

        注意：返回的类型是全限定类名，不带泛型（与Java反射行为一致）
        """
        if imports is None:
            imports = {}

        parameters = []
        if not params_str.strip():
            return parameters

        # 使用括号匹配来正确分割参数
        current = ''
        depth = 0
        for char in params_str:
            if char == '<':
                depth += 1
                current += char
            elif char == '>':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                # 参数分割点
                if current.strip():
                    param_type, param_name = JavaSourceParser._parse_single_param(current.strip(), imports)
                    if param_type and param_name:
                        parameters.append((param_type, param_name))
                current = ''
            else:
                current += char

        # 处理最后一个参数
        if current.strip():
            param_type, param_name = JavaSourceParser._parse_single_param(current.strip(), imports)
            if param_type and param_name:
                parameters.append((param_type, param_name))

        return parameters

    @staticmethod
    def _parse_single_param(param_str: str, imports: Dict[str, str]) -> Tuple[str, str]:
        """解析单个参数，返回(全限定类型名, 参数名)

        类型名处理规则（与Java反射一致）：
        1. 移除泛型部分（Map<String, Object> → Map）
        2. 转换为全限定类名（BillContext → com.xxx.BillContext）
        """
        tokens = param_str.split()
        if len(tokens) < 2:
            return '', ''

        # 最后一个是名称，前面都是类型
        param_type = ' '.join(tokens[:-1])
        param_name = tokens[-1]

        # 移除泛型部分（保留基础类型名）
        if '<' in param_type:
            param_type = param_type[:param_type.index('<')]

        # 移除数组标记（处理成Java反射格式）
        array_suffix = ''
        if '[]' in param_type:
            array_suffix = '[]'
            param_type = param_type.replace('[]', '')

        # 转换为全限定类名
        simple_name = param_type.split('.')[-1]  # 如果已经是全限定名，取最后一部分

        # 常见类型的全限定名映射
        common_types = {
            'String': 'java.lang.String',
            'Integer': 'java.lang.Integer',
            'Long': 'java.lang.Long',
            'Boolean': 'java.lang.Boolean',
            'Double': 'java.lang.Double',
            'Float': 'java.lang.Float',
            'Byte': 'java.lang.Byte',
            'Short': 'java.lang.Short',
            'Character': 'java.lang.Character',
            'Object': 'java.lang.Object',
            'Map': 'java.util.Map',
            'List': 'java.util.List',
            'Set': 'java.util.Set',
            'Date': 'java.util.Date',
        }

        if simple_name in common_types:
            param_type = common_types[simple_name]
        elif '.' not in param_type and simple_name in imports:
            # 通过import获取全限定类名
            param_type = imports[simple_name]
        # 如果已经是全限定名（包含.），保持不变

        return param_type + array_suffix, param_name

    @staticmethod
    def _resolve_type_name(type_name: str, imports: Dict[str, str] = None) -> str:
        """
        解析类型名，转换为全限定类名

        Args:
            type_name: 类型名（可能是简单名或全限定名）
            imports: import映射 {简单类名: 完整类名}

        Returns:
            全限定类名
        """
        if imports is None:
            imports = {}

        # 移除泛型部分
        if '<' in type_name:
            type_name = type_name[:type_name.index('<')]

        # 移除数组标记
        type_name = type_name.replace('[]', '').strip()

        # 常见类型的全限定名映射
        common_types = {
            'String': 'java.lang.String',
            'Integer': 'java.lang.Integer',
            'Long': 'java.lang.Long',
            'Boolean': 'java.lang.Boolean',
            'Double': 'java.lang.Double',
            'Float': 'java.lang.Float',
            'Byte': 'java.lang.Byte',
            'Short': 'java.lang.Short',
            'Character': 'java.lang.Character',
            'Object': 'java.lang.Object',
            'Exception': 'java.lang.Exception',
            'RuntimeException': 'java.lang.RuntimeException',
            'Map': 'java.util.Map',
            'List': 'java.util.List',
            'Set': 'java.util.Set',
            'Date': 'java.util.Date',
        }

        simple_name = type_name.split('.')[-1]

        if simple_name in common_types:
            return common_types[simple_name]
        elif '.' not in type_name and simple_name in imports:
            # 通过import获取全限定类名
            return imports[simple_name]
        else:
            # 如果已经是全限定名（包含.），保持不变
            return type_name

    @staticmethod
    def analyze_class(class_name: str, method_names: List[str] = None) -> Tuple[List[FieldInfo], List[MethodInfo]]:
        """分析Java类，返回Mock字段和方法信息

        Args:
            class_name: 类全限定名
            method_names: 要分析的方法名列表

        Returns:
            (mock_fields, method_infos)
        """
        java_file = JavaSourceParser.find_java_file(class_name)

        if not java_file:
            print(f"警告: 未找到Java源文件: {class_name}")
            return [], []

        print(f"解析Java源文件: {java_file}")
        parsed = JavaSourceParser.parse_java_file(java_file)

        # 提取Mock字段
        mock_fields = []
        for f in parsed["fields"]:
            mock_fields.append(FieldInfo(
                name=f["name"],
                type_name=f["type"],
                has_annotation=f["has_annotation"]
            ))

        # 提取方法信息
        method_infos = []
        if method_names:
            content = java_file.read_text(encoding='utf-8')
            for method_name in method_names:
                methods = JavaSourceParser.extract_method_info(content, method_name, parsed["imports"])
                for m in methods:
                    method_infos.append(MethodInfo(
                        name=m["name"],
                        return_type=m["return_type"],
                        parameters=m["parameters"],
                        declaring_class=class_name,
                        throws=m.get("throws", [])  # ✨ 传入异常类型
                    ))

        return mock_fields, method_infos

    @staticmethod
    def analyze_method_calls(class_name: str, method_name: str, mock_fields: List[FieldInfo]) -> Tuple[List[MockCallInfo], List[StaticCallInfo]]:
        """分析方法中的依赖调用和静态方法调用

        Args:
            class_name: 类全限定名
            method_name: 方法名
            mock_fields: Mock字段列表

        Returns:
            (mock_calls, static_calls)
        """
        java_file = JavaSourceParser.find_java_file(class_name)
        if not java_file:
            return [], []

        content = java_file.read_text(encoding='utf-8')

        # 提取目标方法体
        method_body = JavaSourceParser._extract_method_body(content, method_name)
        if not method_body:
            return [], []

        # 获取字段名集合
        field_names = {f.name for f in mock_fields}

        # 分析依赖方法调用
        mock_calls = JavaSourceParser._extract_mock_calls(method_body, field_names)

        # 分析静态方法调用
        static_calls = JavaSourceParser._extract_static_calls(method_body)

        return mock_calls, static_calls

    @staticmethod
    def _extract_method_body(content: str, method_name: str) -> str:
        """提取方法体"""
        # 找到方法定义的起始位置
        pattern = rf'(?:public|private|protected)?\s+(?:static\s+)?(?:final\s+)?[\w.<>,\s\[\]?]+\s+{re.escape(method_name)}\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{{'
        match = re.search(pattern, content)
        if not match:
            return ""

        start = match.end() - 1  # 包含第一个 {

        # 找到匹配的 }
        depth = 0
        i = start
        while i < len(content):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    return content[start:i+1]
            i += 1
        return ""

    @staticmethod
    def _extract_mock_calls(method_body: str, field_names: Set[str]) -> List[MockCallInfo]:
        """提取依赖方法调用"""
        calls = []
        seen = set()

        for field_name in field_names:
            # 匹配 field.method(...) 或 field.method()
            pattern = rf'{re.escape(field_name)}\.(\w+)\s*\('
            for match in re.finditer(pattern, method_body):
                method = match.group(1)
                key = (field_name, method)
                if key not in seen:
                    seen.add(key)
                    calls.append(MockCallInfo(
                        field_name=field_name,
                        method_name=method
                    ))
        return calls

    @staticmethod
    def _extract_static_calls(method_body: str) -> List[StaticCallInfo]:
        """提取静态方法调用"""
        calls = []
        seen = set()

        # 已知的静态工具类映射
        static_class_map = {
            'BillInfoUtils': 'com.yonyou.ucf.mdd.ext.bill.rule.util.BillInfoUtils',
            'BillBiz': 'com.yonyou.ucf.mdd.ext.bill.rule.util.BillBiz',
            'SFCUtil': 'com.yonyou.biz.mm.mfpo.utils.sfc.SFCUtil',
            'CommonRuleUtils': 'com.yonyou.biz.mm.mfpo.billrule.sfc.common.CommonRuleUtils',
            'MetaDaoHelper': 'com.yonyou.ucf.mdd.ext.dao.MetaDaoHelper',
            'AppContext': 'com.yonyou.ucf.mdd.ext.context.AppContext',
            'InvocationInfoProxy': 'com.yonyou.ucf.mdd.ext.context.InvocationInfoProxy',
            'IdManager': 'com.yonyou.ucf.mdd.ext.util.IdManager',
            'SpringBeanUtil': 'com.yonyou.ucf.mdd.ext.util.SpringBeanUtil',
        }

        for simple_name, full_name in static_class_map.items():
            # 匹配 ClassName.method(...)
            pattern = rf'{simple_name}\.(\w+)\s*\('
            for match in re.finditer(pattern, method_body):
                method = match.group(1)
                key = (simple_name, method)
                if key not in seen:
                    seen.add(key)
                    calls.append(StaticCallInfo(
                        class_name=simple_name,
                        full_class_name=full_name,
                        method_name=method
                    ))
        return calls

# ============== 常量定义 ==============
class ExcelConstant:
    BASE_TEMPLATE_URL = "mock-data/impsfc/30_debug/testcaseV2.xlsx"
    BASE_SHEET_NAME = "BASE"
    METHOD_SHEET_NAME = "testMethod"
    EG_SHEET_NAME = "Tips"

    METHOD_INDEX = 11
    ASSERT_INDEX = 18
    START_BLANK = 21

    MAP_START_INDEX = 15
    MAP_END_INDEX = 26
    MAP_BLANK = 15

    OBJECT_START_INDEX = 31
    OBJECT_END_INDEX = 35
    OBJECT_BLANK = 7

    NUMBERS_TYPE = [
        "java.lang.Integer", "int", "java.lang.Long", "long",
        "java.lang.Double", "double", "java.lang.Float", "float",
        "java.lang.Byte", "byte", "java.lang.Short", "short",
        "java.math.BigDecimal"
    ]

class TestCaseConstant:
    EXT_PARAM_TAG = "#"
    DISTINCT_TAG = "V"
    SPLIT = ":"
    CUSTOM_ARR_L = "[L"
    SUPPORTED_PRIMITIVE = [
        "java.lang.String", "java.lang.Integer", "int",
        "java.lang.Long", "long", "java.lang.Double", "double",
        "java.lang.Float", "float", "java.lang.Boolean", "boolean",
        "java.lang.Byte", "byte", "java.lang.Short", "short",
        "java.math.BigDecimal", "java.util.Date"
    ]

SUBID_LIMIT = ["PO", "IMPSFC", "MR", "OSM", "QMS", "QIC", "ED", "ECN"]

# ============== 路径生成工具 ==============
class GenerateNameUtil:
    """生成文件名和路径的工具类"""

    # 缓存的项目根目录（由配置项设置）
    _project_root_cache = None

    @staticmethod
    def set_project_root(project_root: str):
        """设置项目根目录（由配置项指定）"""
        GenerateNameUtil._project_root_cache = Path(project_root)

    @staticmethod
    def get_project_root() -> Path:
        """获取项目根目录

        优先级：
        1. 配置项指定的路径（set_project_root）
        2. 当前工作目录（如果在项目目录中运行）
        3. 从脚本位置向上查找 mock-data 目录
        4. 使用环境变量 PROJECT_ROOT
        """
        # 优先使用配置项设置的路径
        if GenerateNameUtil._project_root_cache:
            return GenerateNameUtil._project_root_cache

        # 方法2: 从当前工作目录查找
        cwd = Path.cwd()
        current = cwd
        while current != current.parent:
            if (current / "mock-data").exists():
                return current
            current = current.parent

        # 方法3: 从脚本位置向上查找
        script_dir = Path(__file__).parent.resolve()
        current = script_dir
        while current != current.parent:
            if (current / "mock-data").exists():
                return current
            current = current.parent

        # 方法4: 使用环境变量
        if os.environ.get("PROJECT_ROOT"):
            return Path(os.environ.get("PROJECT_ROOT"))

        # 如果找不到，返回默认路径
        print("警告: 未找到项目根目录，请确保在项目目录中运行脚本或设置 project_root 配置项")
        return cwd

    @staticmethod
    def get_template_path() -> str:
        """获取模板文件的绝对路径"""
        project_root = GenerateNameUtil.get_project_root()
        template_path = project_root / "mock-data" / "impsfc" / "30_debug" / "testcaseV2.xlsx"
        return str(template_path)

    @staticmethod
    def generate_root_path(sub_id: str, package_name: str) -> str:
        """生成测试用例文件的根路径（绝对路径）"""
        path_suffix = package_name
        # 替换规则：保留功能模块层级（billrule、service、repository、billplugin等）
        # 只去除应用编码前缀和冗余的中间层级
        replacements = [
            ("com.yonyou.biz.mm.mfpo.", ""),
            ("com.yonyou.biz.mm.qms.", ""),
            ("com.yonyou.biz.mm.qic.", ""),
            ("com.yonyou.biz.mm.mr.", ""),
            ("com.yonyou.biz.mm.osm.", ""),
            ("com.yonyou.biz.mm.ed.", ""),
            ("com.yonyou.biz.mm.ecn.", ""),
            ("apiimpl.", ""),
            (".api", ""),
            ("gatewayimpl.", ""),
            ("sfc.", ""),
            ("po.", ""),
            ("mr.", ""),
            ("osm.", ""),
            ("qms.", ""),  # 包名中间的qms层级去除，但保留 billrule.qms 结构
            ("qic.", ""),  # 包名中间的qic层级去除，但保留 billrule.qic 结构
            ("ed.", ""),   # 包名中间的ed层级去除，但保留 billrule.ed 结构
            ("ecn.", ""),  # 包名中间的ecn层级去除，但保留 billrule.ecn 结构
            ("mobile.", ""),
            (".impl", ""),
            (".bizservice", ""),
            (".service.service", ".service"),  # 去除重复的service层级
            (".repository.repository", ".repository"),  # 去除重复的repository层级
        ]
        for old, new in replacements:
            path_suffix = path_suffix.replace(old, new)
        path_suffix = path_suffix.replace(".", "/")

        # 子系统路径前缀映射
        prefix_map = {
            "PO": "po/20_testcase",
            "IMPSFC": "impsfc/20_testcase",
            "MR": "mr/20_testcase",
            "OSM": "osm/20_testcase",
            "QMS": "qms/20_testcase",
            "QIC": "qic/20_testcase",
            "ED": "ed/20_testcase",
            "ECN": "ecn/20_testcase"
        }
        prefix = prefix_map.get(sub_id, "impsfc/20_testcase")

        # 根据子系统决定Excel文件路径
        # QMS/QIC项目使用 src/test/resources/mock-data 目录（classpath加载）
        # 其他子系统使用项目根目录下的 mock-data 目录
        if sub_id in ["QMS", "QIC"]:
            root_path = GenerateNameUtil.get_project_root() / "src" / "manufacturing-service" / "src" / "test" / "resources" / "mock-data" / prefix / path_suffix
        else:
            root_path = GenerateNameUtil.get_project_root() / "mock-data" / prefix / path_suffix
        return str(root_path)

    @staticmethod
    def generate_file_name(sub_id: str, declaring_class: str, method_name: str, test_class_suffix: str = "") -> Tuple[str, str]:
        """生成测试用例文件名，返回(绝对路径, 相对路径用于Java引用)

        Args:
            sub_id: 子系统标识
            declaring_class: 被测试类全限定名
            method_name: 测试方法名
            test_class_suffix: 测试类后缀（A、B、C等）
        """
        package_name = declaring_class[:declaring_class.rfind('.')]
        root_path = GenerateNameUtil.generate_root_path(sub_id, package_name)
        simple_class_name = declaring_class[declaring_class.rfind('.') + 1:]

        # 子系统文件名前缀映射
        file_prefix_map = {
            "PO": "po.",
            "IMPSFC": "sfc.",
            "MR": "mr.",
            "OSM": "osm.",
            "QMS": "qms.",
            "QIC": "qic.",
            "ED": "ed.",
            "ECN": "ecn."
        }
        prefix = file_prefix_map.get(sub_id, "sfc.")
        dir_name = Path(root_path).name

        # Excel文件名：如果有后缀则添加，否则使用标准命名
        if test_class_suffix:
            file_name = f"{prefix}{dir_name}.{simple_class_name}Test{test_class_suffix}.tc.xlsx"
        else:
            file_name = f"{prefix}{dir_name}.{simple_class_name}Test.tc.xlsx"

        # 绝对路径
        abs_path = str(Path(root_path) / file_name)
        # 相对路径（用于Java引用，需要包含mock-data前缀）
        # 子系统路径前缀映射
        path_prefix_map = {
            "PO": "po/20_testcase",
            "IMPSFC": "impsfc/20_testcase",
            "MR": "mr/20_testcase",
            "OSM": "osm/20_testcase",
            "QMS": "qms/20_testcase",
            "QIC": "qic/20_testcase",
            "ED": "ed/20_testcase",
            "ECN": "ecn/20_testcase"
        }
        prefix_dir = path_prefix_map.get(sub_id, "impsfc/20_testcase")
        relative_path = f"mock-data/{prefix_dir}/{Path(root_path).name}/{file_name}"

        return abs_path, relative_path

# ============== Java测试类生成 ==============
class JavaProcessorUtil:

    @staticmethod
    def first_char_to_lower_case(s: str) -> str:
        if not s:
            return s
        return s[0].lower() + s[1:]

    @staticmethod
    def generate_test_class(
        sub_id: str,
        methods: List[MethodInfo],
        excel_file_path: str,
        java_file_path: str,
        attr: Attr,
        mock_fields: List[FieldInfo],
        mock_calls: List[MockCallInfo] = None,
        static_calls: List[StaticCallInfo] = None
    ) -> str:
        """生成测试类Java代码

        Args:
            sub_id: 子系统ID (PO/IMPSFC)
            methods: 方法信息列表
            excel_file_path: Excel文件路径
            java_file_path: Java文件路径
            attr: 生成属性
            mock_fields: Mock字段列表
            mock_calls: Mock方法调用列表
            static_calls: 静态方法调用列表
        """
        if not methods:
            return ""

        if mock_calls is None:
            mock_calls = []
        if static_calls is None:
            static_calls = []

        target_class = methods[0].declaring_class
        package_name = target_class[:target_class.rfind('.')]
        simple_class_name = target_class[target_class.rfind('.') + 1:]

        # ✨ 打印import分析信息
        print(f"✓ 开始分析import依赖...")

        code_lines = []

        # Package声明
        code_lines.append(f"package {package_name};")
        code_lines.append("")

        # ✨ 使用ImportAnalyzer分析所有需要的import
        all_imports = ImportAnalyzer.analyze_imports(
            target_class=target_class,
            methods=methods,
            mock_fields=mock_fields,
            static_calls=static_calls,
            sub_id=sub_id
        )

        # 排序import（java.* -> com.* -> org.* -> 其他）
        sorted_imports = ImportAnalyzer.sort_imports(all_imports)

        # ✨ 打印import分析结果
        print(f"✓ 分析完成：共 {len(sorted_imports)} 个import语句")
        print(f"  - java.*: {len([i for i in sorted_imports if i.startswith('java.')])} 个")
        print(f"  - com.*: {len([i for i in sorted_imports if i.startswith('com.')])} 个")
        print(f"  - org.*: {len([i for i in sorted_imports if i.startswith('org.')])} 个")

        # 输出import语句
        current_package = None
        for imp in sorted_imports:
            # 判断包名
            if imp.startswith('java.'):
                pkg = 'java'
            elif imp.startswith('com.'):
                pkg = 'com'
            elif imp.startswith('org.'):
                pkg = 'org'
            else:
                pkg = 'other'

            # 包名变化时插入空行
            if current_package and current_package != pkg:
                code_lines.append("")
            current_package = pkg

            code_lines.append(f"import {imp};")

        code_lines.append("")
        code_lines.append("")

        # 类定义
        # 获取基类名称
        base_class_map = {
            "PO": "POTestable",
            "IMPSFC": "SFCTestable",
            "MR": "MFTestable",
            "OSM": "MFTestable",
            "QMS": "MFTestable",
            "QIC": "MFTestable",
            "ED": "MFTestable",
            "ECN": "MFTestable"
        }
        base_class = base_class_map.get(sub_id, "MFTestable")

        test_class_name = java_file_path[java_file_path.rfind('/') + 1:java_file_path.rfind('.')]
        code_lines.append(f"/**")
        code_lines.append(f" * {simple_class_name} 单元测试")
        for method in methods:
            params_str = ", ".join([f"{t.split('.')[-1]} {n}" for t, n in method.parameters])
            code_lines.append(f" * 被测试方法: {method.name}({params_str})")
        code_lines.append(f" */")
        code_lines.append(f"public class {test_class_name} extends {base_class} {{")
        code_lines.append("")
        code_lines.append(f"    private static final String TEST_PATH = \"{excel_file_path}\";")
        code_lines.append("")
        code_lines.append("    @InjectMocks")
        code_lines.append(f"    private {simple_class_name} {JavaProcessorUtil.first_char_to_lower_case(simple_class_name)};")
        code_lines.append("")

        # Mock字段
        for field in mock_fields:
            simple_type = field.type_name[field.type_name.rfind('.') + 1:]
            code_lines.append("    @Mock")
            code_lines.append(f"    private {simple_type} {field.name};")

        if mock_fields:
            code_lines.append("")

        # setUp方法
        code_lines.append("    @BeforeEach")
        code_lines.append("    public void setUp() {")
        code_lines.append("    }")
        code_lines.append("")

        # execute方法 - 根据是否有静态Mock生成不同版本
        code_lines.append("    @Override")
        code_lines.append("    public void execute(Asserts asserts) throws Exception {")
        code_lines.append("        initMock();")

        if static_calls:
            # 有静态方法调用，生成静态Mock模板
            code_lines.append("        try (MockedStatic billInfoUtilsPlugin = BillInfoUtilsPlugin.of(datasource)) {")
            code_lines.append("            asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));")
            code_lines.append("        }")
        else:
            code_lines.append("        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));")

        code_lines.append("    }")
        code_lines.append("")

        # asserts方法
        code_lines.append("    @Override")
        code_lines.append("    public Asserts asserts() {")
        code_lines.append("        return Asserts.of(this.getClass().getName());")
        code_lines.append("    }")
        code_lines.append("")

        # loadDatasource方法
        code_lines.append("    @Override")
        code_lines.append("    public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {")
        code_lines.append("        super.loadDatasource(loader, ds);")
        code_lines.append("        InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);")
        code_lines.append("        if (is != null) {")
        code_lines.append("            loader.loadDataFromExcel(ds, is);")
        code_lines.append("        }")
        code_lines.append("        registry.register(this);")
        code_lines.append("    }")
        code_lines.append("")

        # getMockBean方法
        code_lines.append("    @Override")
        code_lines.append("    public Object getMockBean() {")
        code_lines.append(f"        return {JavaProcessorUtil.first_char_to_lower_case(simple_class_name)};")
        code_lines.append("    }")
        code_lines.append("")

        # initMock方法 - 自动生成Mock逻辑
        code_lines.append("    public void initMock() throws Exception {")
        if mock_calls:
            # 按字段分组生成Mock
            field_calls = {}
            for call in mock_calls:
                if call.field_name not in field_calls:
                    field_calls[call.field_name] = []
                field_calls[call.field_name].append(call)

            for field_name, calls in field_calls.items():
                for call in calls:
                    code_lines.append(f"        // Mock {field_name}.{call.method_name}()")
                    code_lines.append(f"        Mockito.lenient().when({field_name}.{call.method_name}(Mockito.any()))")
                    code_lines.append(f"            .thenAnswer(invocation -> {{")
                    code_lines.append(f"                // TODO: 实现返回值逻辑")
                    code_lines.append(f"                return null;")
                    code_lines.append(f"            }});")
        else:
            code_lines.append("        // 根据方法的具体实现添加mock逻辑")
        code_lines.append("    }")
        code_lines.append("")

        # @ExtParam方法 - 根据方法参数和test_case_count自动生成
        code_lines.append("    // ==================== @ExtParam methods ====================")
        code_lines.append("")

        # 获取测试用例数量
        case_count = attr.test_case_count if attr else 7

        # 遍历方法，method_index是方法索引（从1开始）
        for method_index, method in enumerate(methods, 1):
            for param_idx, (param_type, param_name) in enumerate(method.parameters):
                # 跳过基本类型
                if param_type in [
                    'java.lang.String', 'java.lang.Integer', 'int',
                    'java.lang.Long', 'long', 'java.lang.Double', 'double',
                    'java.lang.Float', 'float', 'java.lang.Boolean', 'boolean',
                    'java.lang.Byte', 'byte', 'java.lang.Short', 'short',
                    'java.math.BigDecimal', 'java.util.Date'
                ]:
                    continue

                simple_type = param_type.split('.')[-1]

                # 根据test_case_count生成对应数量的@ExtParam方法
                # case_id格式与Excel一致：method_index * 1000 + case_idx + 1
                # 例如第一个方法：1001, 1002, 1003...
                # 第二个方法：2001, 2002, 2003...
                for case_idx in range(case_count):
                    case_id = f"{method_index}00{case_idx + 1}"
                    ext_param_name = f"{param_name}_{case_id}"

                    # 场景描述
                    scenario_hint = f"场景{case_idx + 1}"
                    if case_idx == 0:
                        scenario_hint = "正常场景"
                    elif case_idx == case_count - 1:
                        scenario_hint = "边界/异常场景"

                    code_lines.append(f"    /**")
                    code_lines.append(f"     * 创建 {simple_type} 参数 - {scenario_hint}")
                    code_lines.append(f"     * 用例ID: {case_id}")
                    code_lines.append(f"     */")
                    code_lines.append(f"    @ExtParam(\"{ext_param_name}\")")
                    code_lines.append(f"    public {simple_type} {ext_param_name}() {{")

                    if param_type == 'com.yonyou.ucf.mdd.ext.model.BillContext':
                        code_lines.append(f"        BillContext billContext = new BillContext();")
                        code_lines.append(f"        // TODO: 设置单据信息")
                        code_lines.append(f"        // billContext.setBillnum(\"billnum_value\");")
                        code_lines.append(f"        return billContext;")
                    elif param_type == 'java.util.Map' or 'Map' in param_type:
                        code_lines.append(f"        Map<String, Object> paramMap = new HashMap<>();")
                        code_lines.append(f"        BillDataDto billDataDto = new BillDataDto();")
                        code_lines.append(f"        // 设置分页参数")
                        code_lines.append(f"        QueryPagerVo page = new QueryPagerVo();")
                        code_lines.append(f"        page.setPageIndex(1);")
                        code_lines.append(f"        page.setPageSize(10);")
                        code_lines.append(f"        page.setTotalCount(-1);")
                        code_lines.append(f"        billDataDto.setPage(page);")
                        code_lines.append(f"        paramMap.put(\"param\", billDataDto);")
                        code_lines.append(f"        // TODO: 添加其他参数")
                        code_lines.append(f"        return paramMap;")
                    elif param_type == 'java.util.List' or 'List' in param_type:
                        # List类型使用ArrayList实例化
                        code_lines.append(f"        java.util.List param = new java.util.ArrayList<>();")
                        code_lines.append(f"        // TODO: 添加列表元素")
                        code_lines.append(f"        return param;")
                    elif param_type == 'java.util.Set' or 'Set' in param_type:
                        # Set类型使用HashSet实例化
                        code_lines.append(f"        java.util.Set param = new java.util.HashSet<>();")
                        code_lines.append(f"        // TODO: 添加集合元素")
                        code_lines.append(f"        return param;")
                    else:
                        # 其他复杂类型，使用简单类名实例化
                        code_lines.append(f"        {simple_type} param = new {simple_type}();")
                        code_lines.append(f"        // TODO: 设置参数属性")
                        code_lines.append(f"        return param;")

                    code_lines.append("    }")
                    code_lines.append("")

        code_lines.append("}")
        code_lines.append("")

        return "\n".join(code_lines)

    @staticmethod
    def build_test_class_path(target_class_name: str, test_class_suffix: str = "") -> Tuple[Optional[Path], str]:
        """构建测试类文件路径

        Args:
            target_class_name: 目标类全限定名
            test_class_suffix: 测试类后缀（A、B、C等），为空表示不使用后缀

        Returns:
            (Path, str): 文件路径和文件名
        """
        package_path = target_class_name.replace('.', os.sep)
        last_sep_index = package_path.rfind(os.sep)
        package_dir = package_path[:last_sep_index]
        simple_class_name = package_path[last_sep_index + 1:]

        # 使用项目根目录计算正确路径
        project_root = GenerateNameUtil.get_project_root()

        # 构建测试类根目录
        test_java_root = project_root / "src" / "manufacturing-service" / "src" / "test" / "java"

        # 构建测试类名称：如果有后缀则添加，否则使用标准命名
        if test_class_suffix:
            test_class_name = f"{simple_class_name}Test{test_class_suffix}"
        else:
            test_class_name = f"{simple_class_name}Test"

        test_class_path = test_java_root / package_dir / f"{test_class_name}.java"

        # 创建目录
        test_class_path.parent.mkdir(parents=True, exist_ok=True)

        return test_class_path, test_class_path.name

    @staticmethod
    def find_next_available_test_class_suffix(target_class_name: str) -> str:
        """查找下一个可用的测试类后缀（A、B、C...）

        当测试类已存在时，自动查找下一个可用的后缀

        Args:
            target_class_name: 目标类全限定名

        Returns:
            str: 下一个可用的后缀（A、B、C...），如果基础测试类不存在则返回空字符串
        """
        package_path = target_class_name.replace('.', os.sep)
        last_sep_index = package_path.rfind(os.sep)
        simple_class_name = package_path[last_sep_index + 1:]

        project_root = GenerateNameUtil.get_project_root()
        test_java_root = project_root / "src" / "manufacturing-service" / "src" / "test" / "java"
        package_dir = package_path[:last_sep_index]

        # 1. 首先检查基础测试类是否存在（无后缀）
        base_test_class = test_java_root / package_dir / f"{simple_class_name}Test.java"
        if not base_test_class.exists():
            # 基础测试类不存在，返回空字符串
            return ""

        # 2. 基础测试类已存在，查找下一个可用后缀（A、B、C...）
        # ASCII码：A=65, Z=90
        for i in range(65, 91):  # A到Z
            suffix = chr(i)
            test_class_path = test_java_root / package_dir / f"{simple_class_name}Test{suffix}.java"
            if not test_class_path.exists():
                return suffix

        # 3. 如果A-Z都已用完，返回AA（但这种情况极少见）
        return "AA"

    @staticmethod
    def save_as_new_file(
        methods: List[MethodInfo],
        sub_id: str,
        attr: Attr,
        excel_file_path: str,
        mock_fields: List[FieldInfo]
    ) -> str:
        """保存生成的Java测试类文件

        Returns:
            str: 生成的文件路径
        """
        if not attr or not attr.gen_java:
            return ""

        if not methods:
            return ""

        declaring_class = methods[0].declaring_class

        # ⭐ 新逻辑：查找下一个可用的测试类后缀（A、B、C...）
        test_class_suffix = JavaProcessorUtil.find_next_available_test_class_suffix(declaring_class)

        if test_class_suffix:
            print(f"检测到测试类已存在，自动使用后缀: {test_class_suffix}")
            print(f"将创建测试类: {declaring_class.split('.')[-1]}Test{test_class_suffix}.java")
        else:
            print(f"将创建基础测试类: {declaring_class.split('.')[-1]}Test.java")

        # 使用后缀生成Excel文件路径
        if not excel_file_path:
            abs_path, excel_file_path = GenerateNameUtil.generate_file_name(
                sub_id, declaring_class, methods[0].name, test_class_suffix
            )

        # 使用后缀构建测试类路径
        test_class_path, file_name = JavaProcessorUtil.build_test_class_path(declaring_class, test_class_suffix)

        # 分析方法调用和静态方法调用
        mock_calls = []
        static_calls = []
        if attr.auto_init_mock:
            mock_calls, static_calls = JavaSourceParser.analyze_method_calls(
                declaring_class, methods[0].name, mock_fields
            )
            if mock_calls:
                print(f"自动解析到 {len(mock_calls)} 个依赖方法调用")
            if static_calls:
                print(f"自动解析到 {len(static_calls)} 个静态方法调用")

        code = JavaProcessorUtil.generate_test_class(
            sub_id, methods, excel_file_path, file_name, attr, mock_fields,
            mock_calls, static_calls
        )

        test_class_path.write_text(code, encoding='utf-8')
        print(f"Java测试类已生成: {test_class_path}")

        return str(test_class_path)

# ============== Excel测试用例生成 ==============
class ExcelProcessorUtil:

    @staticmethod
    def get_primitive_value(type_name: str) -> str:
        """获取基本类型的示例值"""
        if type_name == "java.lang.String":
            return "abc"
        if type_name in ExcelConstant.NUMBERS_TYPE:
            return "0"
        if type_name == "java.util.Date":
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if type_name in ["java.lang.Boolean", "boolean"]:
            return "false"
        return ""

    @staticmethod
    def generate_new_file_name(method: MethodInfo, sub_id: str, test_class_suffix: str = "") -> Tuple[Optional[str], str]:
        """生成Excel文件名，返回(绝对路径, 相对路径用于Java引用)

        Args:
            method: 方法信息
            sub_id: 子系统标识
            test_class_suffix: 测试类后缀（A、B、C等）

        Returns:
            (str, str): 文件路径和相对路径
            (None, ""): 如果文件已存在，返回 None 表示跳过生成
        """
        declaring_class = method.declaring_class
        package_name = declaring_class[:declaring_class.rfind('.')]
        root_path = GenerateNameUtil.generate_root_path(sub_id, package_name)

        # 创建目录
        Path(root_path).mkdir(parents=True, exist_ok=True)

        abs_path, relative_path = GenerateNameUtil.generate_file_name(sub_id, declaring_class, method.name, test_class_suffix)

        # 如果文件已存在，返回 None 表示跳过生成
        if Path(abs_path).exists():
            return None, ""

        return abs_path, relative_path

    @staticmethod
    def save_as_new_file(
        methods: List[MethodInfo],
        sub_id: str,
        attr: Attr,
        template_path: str = None,
        test_class_suffix: str = ""
    ) -> Tuple[str, str]:
        """保存生成的Excel测试用例文件，返回(绝对路径, 相对路径用于Java引用)"""
        if not attr or not attr.gen_xlsx:
            return "", ""

        if not methods:
            return "", ""

        # 检查文件是否已存在
        new_file_path, relative_path = ExcelProcessorUtil.generate_new_file_name(methods[0], sub_id, test_class_suffix)

        if new_file_path is None:
            declaring_class = methods[0].declaring_class
            print(f"Excel测试用例已存在，跳过生成")
            print("如需重新生成，请先删除现有Excel文件")
            return "", ""

        # 查找模板文件（使用绝对路径）
        if not template_path:
            template_path = GenerateNameUtil.get_template_path()

        # 如果模板不存在，创建简化版本
        if not Path(template_path).exists():
            print(f"警告: 模板文件不存在 {template_path}")
            print("将生成简化版本的Excel文件")
            return ExcelProcessorUtil.create_simple_excel(methods, sub_id, attr, test_class_suffix)

        try:
            from openpyxl import load_workbook
        except ImportError:
            print("需要安装openpyxl: pip install openpyxl")
            return ExcelProcessorUtil.create_simple_excel(methods, sub_id, attr, test_class_suffix)

        try:
            workbook = load_workbook(template_path)
            base_sheet = workbook[ExcelConstant.BASE_SHEET_NAME]

            # 处理BASE sheet
            method_invoke_map = ExcelProcessorUtil.deal_base_sheet(base_sheet, methods, test_class_suffix)

            # 复制模板sheet到方法sheet
            eg_sheet = workbook[ExcelConstant.EG_SHEET_NAME]

            method_index = 1
            for method in methods:
                sheet_name = method_invoke_map.get(hash(str(method)), method.name)
                sheet_name = sheet_name[:31] if len(sheet_name) > 31 else sheet_name

                method_sheet = workbook.copy_worksheet(workbook[ExcelConstant.METHOD_SHEET_NAME])
                method_sheet.title = sheet_name

                ExcelProcessorUtil.deal_method_sheet(
                    method_sheet, eg_sheet, method, sub_id, attr, method_index, test_class_suffix
                )
                method_index += 1

            # 删除模板sheet
            if ExcelConstant.METHOD_SHEET_NAME in workbook.sheetnames:
                del workbook[ExcelConstant.METHOD_SHEET_NAME]
            if ExcelConstant.EG_SHEET_NAME in workbook.sheetnames:
                del workbook[ExcelConstant.EG_SHEET_NAME]

            # 应用样式
            if HAS_STYLE_UTIL:
                ExcelStyleUtil.style_full_workbook(workbook, attr.test_case_count)

            workbook.save(new_file_path)
            print(f"Excel测试用例已生成: {new_file_path}")
            return new_file_path, relative_path

        except Exception as e:
            print(f"处理Excel时出错: {e}")
            return ExcelProcessorUtil.create_simple_excel(methods, sub_id, attr, test_class_suffix)

    @staticmethod
    def deal_base_sheet(base_sheet, methods: List[MethodInfo], test_class_suffix: str = "") -> Dict[int, str]:
        """处理BASE sheet - 按照Java Main方法的格式

        Args:
            test_class_suffix: 测试类后缀（A、B、C等）
        """
        method_invoke_map = {}

        if not methods:
            return method_invoke_map

        declaring_class = methods[0].declaring_class
        simple_class_name = declaring_class[declaring_class.rfind('.') + 1:]

        # ⭐ 构建测试类名称（包含后缀）
        test_class_name = f"{simple_class_name}Test{test_class_suffix}" if test_class_suffix else f"{simple_class_name}Test"

        # 设置方法调用URI (C3单元格)
        base_sheet.cell(row=1, column=3).value = f"dto.{test_class_name}.methodInvoke"

        method_names = []
        for i, method in enumerate(methods):
            row_index = 5 + i  # 从第5行开始 (Java中是4+i，Excel行号+1)

            # B列: 序号
            base_sheet.cell(row=row_index, column=2).value = f"100{i + 1}"

            # C列: 方法别名（处理重载）
            method_name = method.name
            if method_name in method_names:
                count = sum(1 for n in method_names if n == method_name)
                method_name = f"{method.name}{count + 1}"
            method_names.append(method.name)

            base_sheet.cell(row=row_index, column=3).value = method_name
            method_invoke_map[hash(str(method))] = method_name

            # D列: 类名
            base_sheet.cell(row=row_index, column=4).value = declaring_class

            # E列: 返回类型
            base_sheet.cell(row=row_index, column=5).value = method.return_type

            # F列: 方法名
            base_sheet.cell(row=row_index, column=6).value = method.name

            # G列: 参数数量
            base_sheet.cell(row=row_index, column=7).value = len(method.parameters)

            # H列开始: 参数类型
            for j, (param_type, _) in enumerate(method.parameters):
                base_sheet.cell(row=row_index, column=8 + j).value = param_type

        return method_invoke_map

    @staticmethod
    def deal_method_sheet(
        method_sheet, eg_sheet, method: MethodInfo,
        sub_id: str, attr: Attr, index: int, test_class_suffix: str = ""
    ):
        """处理方法sheet - 使用@ExtParam引用格式

        Args:
            test_class_suffix: 测试类后缀（A、B、C等）
        """
        declaring_class = method.declaring_class
        simple_class_name = declaring_class[declaring_class.rfind('.') + 1:]

        # 从attr获取测试用例数量
        test_case_count = attr.test_case_count

        # 填充基础信息并获取行位置
        row_info = ExcelProcessorUtil.fill_blank(method_sheet, method, sub_id, index, test_case_count, attr.related_task_number, test_class_suffix)

        if not attr.xlsx_eg_value:
            return

        # 为每个测试用例的业务数据DataRow填充参数值
        for case_idx in range(row_info['test_case_count']):
            case_id = f"{index}00{case_idx + 1}"
            param_row = row_info['busi_data_start'] + case_idx

            for j, (param_type, param_name) in enumerate(method.parameters):
                cell_col = 5 + j  # 参数从E列开始

                # 处理基本类型 - 直接填值
                if param_type in TestCaseConstant.SUPPORTED_PRIMITIVE:
                    method_sheet.cell(row=param_row, column=cell_col).value = \
                        ExcelProcessorUtil.get_primitive_value(param_type)
                    continue

                # 处理复杂类型 - 使用@ExtParam引用格式
                # 格式: #paramName_caseId (每个DataRow引用对应的@ExtParam)
                ext_param_name = f"{param_name}_{case_id}"
                method_sheet.cell(row=param_row, column=cell_col).value = \
                    f"#{ext_param_name}"

        # 填充断言
        if attr.xlsx_eg_assert:
            if method.return_type != "void":
                # 为每个测试用例的断言设置断言类型
                for i in range(row_info['test_case_count']):
                    assert_row = row_info['assert_data_start'] + i
                    # D列: 断言类型
                    if "List" in method.return_type or "Collection" in method.return_type:
                        method_sheet.cell(row=assert_row, column=4).value = "AssertNotEmpty"
                    else:
                        method_sheet.cell(row=assert_row, column=4).value = "AssertNotNull"
                    # F列: 实际值表达式
                    method_sheet.cell(row=assert_row, column=6).value = "returnObj"
                    # G列: 取值表达式
                    method_sheet.cell(row=assert_row, column=7).value = "."
                    # H列: enable（与断言表头定义一致，第8列）
                    method_sheet.cell(row=assert_row, column=8).value = 1

    @staticmethod
    def fill_blank(method_sheet, method: MethodInfo, sub_id: str, index: int, test_case_count: int = 7, related_task_number: str = "", test_class_suffix: str = ""):
        """
        填充方法sheet的基础信息

        Args:
            method_sheet: 工作表对象
            method: 方法信息
            sub_id: 子系统标识
            index: 方法索引（用于生成id）
            test_case_count: 测试用例数量，默认7个
            related_task_number: PM问题号（自动填充到relatedTask列）✨
            test_class_suffix: 测试类后缀（A、B、C等）
        """
        declaring_class = method.declaring_class
        simple_class_name = declaring_class[declaring_class.rfind('.') + 1:]
        sheet_name = method_sheet.title

        # ⭐ 构建测试类名称（包含后缀）
        test_class_name = f"{simple_class_name}Test{test_class_suffix}" if test_class_suffix else f"{simple_class_name}Test"

        # 清除可能存在的旧数据（从模板复制时会有示例数据）
        for row in range(1, method_sheet.max_row + 1):
            for col in range(1, 15):
                method_sheet.cell(row=row, column=col).value = None

        # 计算行位置（支持多个测试用例）
        # 测试用例模块: Row 1-4表头 + Row 5开始DataRow
        test_case_header_end = 4
        test_case_data_start = 5
        test_case_data_end = test_case_data_start + test_case_count - 1

        # 业务数据模块: 空行分隔 + 表头 + DataRow
        busi_data_gap = 1  # Row 12空行
        busi_data_header_start = test_case_data_end + busi_data_gap + 1  # Row 13
        busi_data_header_end = busi_data_header_start + 3  # Row 16
        busi_data_start = busi_data_header_end + 1  # Row 17
        busi_data_end = busi_data_start + test_case_count - 1  # Row 23

        # 断言模块: 空行分隔 + 表头 + DataRow
        assert_gap = 1  # Row 24空行
        assert_header_start = busi_data_end + assert_gap + 1  # Row 25
        assert_header_end = assert_header_start + 3  # Row 28
        assert_data_start = assert_header_end + 1  # Row 29

        # ===== 测试用例区域 (Row 1-4表头 + Row 5~多行DataRow) =====
        # Row 1: DataTag
        method_sheet.cell(row=1, column=1).value = "DataTag"
        method_sheet.cell(row=1, column=2).value = "DTO"
        # ⭐ 使用带后缀的测试类名称
        method_sheet.cell(row=1, column=3).value = f"{sub_id}.DTO.{test_class_name}.CASE.V2"

        # Row 2: DataField
        method_sheet.cell(row=2, column=1).value = "DataField"
        fields = ["id", "caseName", "memo", "enable", "busiDatas", "asserts", "execStatus", "resultStatus", "execTime", "relatedTask"]
        for col, field in enumerate(fields, start=2):
            method_sheet.cell(row=2, column=col).value = field

        # Row 3: DataTitle
        method_sheet.cell(row=3, column=1).value = "DataTitle"
        titles = ["编号", "测试用例名", "备注", "是否有效", "业务数据", "断言明细", "待执行", "测试通过", "执行时间", "关联故事任务号，多个用逗号分开"]
        for col, title in enumerate(titles, start=2):
            method_sheet.cell(row=3, column=col).value = title

        # Row 4: DataType
        method_sheet.cell(row=4, column=1).value = "DataType"
        # ⭐ 使用带后缀的测试类名称，确保与DataTag一致
        types = ["Long", "String", "String", "Boolean",
                 f"List<dto.{test_class_name}.busiData>",
                 f"List<dto.{test_class_name}.assert>",
                 "String", "String", "String", "String"]
        for col, dtype in enumerate(types, start=2):
            method_sheet.cell(row=4, column=col).value = dtype

        # Row 5~: DataRow - 多个测试用例
        # 定义测试场景模板（覆盖不同代码行）
        test_scenarios = [
            ("正常场景", "覆盖基本流程"),
            ("边界条件", "测试边界值"),
            ("异常处理", "测试异常情况"),
            ("空值处理", "测试null输入"),
            ("数据为空", "测试空集合"),
            ("条件不满足", "测试条件分支"),
            ("其他场景", "补充测试")
        ]

        for i in range(test_case_count):
            row_num = test_case_data_start + i
            case_id = f"{index}00{i + 1}"
            scenario = test_scenarios[i] if i < len(test_scenarios) else test_scenarios[0]

            method_sheet.cell(row=row_num, column=1).value = "DataRow"
            method_sheet.cell(row=row_num, column=2).value = case_id
            # ⭐ 使用带后缀的测试类名称
            method_sheet.cell(row=row_num, column=3).value = f"{test_class_name}_{sheet_name}_{case_id}"
            method_sheet.cell(row=row_num, column=4).value = scenario[1]
            method_sheet.cell(row=row_num, column=5).value = 1
            method_sheet.cell(row=row_num, column=6).value = f"{sheet_name}_{case_id}"
            method_sheet.cell(row=row_num, column=7).value = f"{sheet_name}_assert_{case_id}"
            # H-I-J列：execStatus, resultStatus, execTime（框架自动填充）
            method_sheet.cell(row=row_num, column=8).value = ""  # execStatus
            method_sheet.cell(row=row_num, column=9).value = ""  # resultStatus
            method_sheet.cell(row=row_num, column=10).value = ""  # execTime
            # K列（column=11）：relatedTask - PM问题号自动填充 ✨
            method_sheet.cell(row=row_num, column=11).value = related_task_number

        # ===== 业务数据区域 =====
        # DataTag
        method_sheet.cell(row=busi_data_header_start, column=1).value = "DataTag"
        method_sheet.cell(row=busi_data_header_start, column=2).value = "DTO"
        # ⭐ 使用带后缀的测试类名称
        method_sheet.cell(row=busi_data_header_start, column=3).value = f"dto.{test_class_name}.busiData"

        # DataField
        method_sheet.cell(row=busi_data_header_start + 1, column=1).value = "DataField"
        busi_fields = ["id", "code", "methodInvoke", "value0", "value1", "value2"]
        for col, field in enumerate(busi_fields, start=2):
            method_sheet.cell(row=busi_data_header_start + 1, column=col).value = field

        # DataTitle
        method_sheet.cell(row=busi_data_header_start + 2, column=1).value = "DataTitle"
        busi_titles = ["编号", "编码", "方法调用code", "值0", "值1", "值2"]
        for col, title in enumerate(busi_titles, start=2):
            method_sheet.cell(row=busi_data_header_start + 2, column=col).value = title

        # DataType
        method_sheet.cell(row=busi_data_header_start + 3, column=1).value = "DataType"
        # ⭐ 使用带后缀的测试类名称
        busi_types = ["Long", "String", f"dto.{test_class_name}.methodInvoke", "String", "String", "String"]
        for col, dtype in enumerate(busi_types, start=2):
            method_sheet.cell(row=busi_data_header_start + 3, column=col).value = dtype

        # DataRow - 多个业务数据（参数值由调用方设置）
        for i in range(test_case_count):
            row_num = busi_data_start + i
            case_id = f"{index}00{i + 1}"

            method_sheet.cell(row=row_num, column=1).value = "DataRow"
            method_sheet.cell(row=row_num, column=2).value = case_id
            method_sheet.cell(row=row_num, column=3).value = f"{sheet_name}_{case_id}"
            method_sheet.cell(row=row_num, column=4).value = sheet_name

        # ===== 断言区域 =====
        # DataTag
        method_sheet.cell(row=assert_header_start, column=1).value = "DataTag"
        method_sheet.cell(row=assert_header_start, column=2).value = "DTO"
        # ⭐ 使用带后缀的测试类名称
        method_sheet.cell(row=assert_header_start, column=3).value = f"dto.{test_class_name}.assert"

        # DataField
        method_sheet.cell(row=assert_header_start + 1, column=1).value = "DataField"
        assert_fields = ["id", "code", "assertType", "assertException", "actualName", "actualValueExp", "enable"]
        for col, field in enumerate(assert_fields, start=2):
            method_sheet.cell(row=assert_header_start + 1, column=col).value = field

        # DataTitle
        method_sheet.cell(row=assert_header_start + 2, column=1).value = "DataTitle"
        assert_titles = ["编号", "编码", "断言类型", "断言异常", "实际值名", "取值表达式", "是否有效"]
        for col, title in enumerate(assert_titles, start=2):
            method_sheet.cell(row=assert_header_start + 2, column=col).value = title

        # DataType
        method_sheet.cell(row=assert_header_start + 3, column=1).value = "DataType"
        assert_types = ["Long", "String", "String", "String", "String", "String", "Boolean"]
        for col, dtype in enumerate(assert_types, start=2):
            method_sheet.cell(row=assert_header_start + 3, column=col).value = dtype

        # DataRow - 断言（为每个测试用例生成对应的断言）
        for i in range(test_case_count):
            row_num = assert_data_start + i
            case_id = f"{index}00{i + 1}"

            method_sheet.cell(row=row_num, column=1).value = "DataRow"
            method_sheet.cell(row=row_num, column=2).value = case_id
            method_sheet.cell(row=row_num, column=3).value = f"{sheet_name}_assert_{case_id}"

        # 返回关键行位置供后续填充参数
        return {
            'test_case_data_start': test_case_data_start,
            'test_case_data_end': test_case_data_end,
            'busi_data_start': busi_data_start,
            'busi_data_end': busi_data_end,
            'assert_data_start': assert_data_start,
            'test_case_count': test_case_count
        }
    def create_simple_excel(methods: List[MethodInfo], sub_id: str, attr: Attr, test_class_suffix: str = "") -> Tuple[str, str]:
        """创建简化版本的Excel文件（无模板时使用），返回(绝对路径, 相对路径用于Java引用)"""
        try:
            from openpyxl import Workbook
        except ImportError:
            print("需要安装openpyxl: pip install openpyxl")
            return "", ""

        new_file_path, relative_path = ExcelProcessorUtil.generate_new_file_name(methods[0], sub_id, test_class_suffix)

        # 如果文件已存在，跳过生成
        if new_file_path is None:
            print("Excel测试用例已存在，跳过生成")
            return "", ""

        workbook = Workbook()

        # 创建BASE sheet
        base_sheet = workbook.active
        base_sheet.title = "BASE"

        if methods:
            declaring_class = methods[0].declaring_class
            simple_class_name = declaring_class[declaring_class.rfind('.') + 1:]

            # ⭐ 构建测试类名称（包含后缀）
            test_class_name = f"{simple_class_name}Test{test_class_suffix}" if test_class_suffix else f"{simple_class_name}Test"

            # BASE sheet 表头
            base_sheet.cell(row=1, column=1).value = "DataTag"
            base_sheet.cell(row=1, column=2).value = "DTO"
            # ⭐ 使用带后缀的测试类名称
            base_sheet.cell(row=1, column=3).value = f"dto.{test_class_name}.methodInvoke"

            base_sheet.cell(row=2, column=1).value = "DataField"
            fields = ["id", "code", "className", "resultType", "methodName", "argSize", "arg0", "arg1", "arg2"]
            for col, field in enumerate(fields, start=2):
                base_sheet.cell(row=2, column=col).value = field

            base_sheet.cell(row=3, column=1).value = "DataTitle"
            titles = ["编号", "编码", "类名", "返回类型", "方法名", "参数个数", "参数0", "参数1", "参数2"]
            for col, title in enumerate(titles, start=2):
                base_sheet.cell(row=3, column=col).value = title

            base_sheet.cell(row=4, column=1).value = "DataType"
            types = ["Long", "String", "String", "String", "String", "Int", "String", "String", "String"]
            for col, dtype in enumerate(types, start=2):
                base_sheet.cell(row=4, column=col).value = dtype

            # 方法定义行
            for i, method in enumerate(methods):
                row = 5 + i
                base_sheet.cell(row=row, column=1).value = "DataRow"
                base_sheet.cell(row=row, column=2).value = f"100{i + 1}"
                base_sheet.cell(row=row, column=3).value = method.name
                base_sheet.cell(row=row, column=4).value = declaring_class
                base_sheet.cell(row=row, column=5).value = method.return_type
                base_sheet.cell(row=row, column=6).value = method.name
                base_sheet.cell(row=row, column=7).value = len(method.parameters)
                # 参数类型
                for j, (param_type, _) in enumerate(method.parameters):
                    base_sheet.cell(row=row, column=8 + j).value = param_type

        # 为每个方法创建sheet
        for i, method in enumerate(methods):
            sheet_name = method.name[:31] if len(method.name) > 31 else method.name
            method_sheet = workbook.create_sheet(title=sheet_name)

            index = i + 1
            # 调用fill_blank并获取行位置信息
            row_info = ExcelProcessorUtil.fill_blank(method_sheet, method, sub_id, index, attr.test_case_count, attr.related_task_number)

            # 为每个测试用例的业务数据DataRow填充参数值
            for case_idx in range(row_info['test_case_count']):
                case_id = f"{index}00{case_idx + 1}"
                param_row = row_info['busi_data_start'] + case_idx

                for j, (param_type, param_name) in enumerate(method.parameters):
                    cell_col = 5 + j  # value0, value1, value2 列
                    if param_type in TestCaseConstant.SUPPORTED_PRIMITIVE:
                        method_sheet.cell(row=param_row, column=cell_col).value = \
                            ExcelProcessorUtil.get_primitive_value(param_type)
                    else:
                        # 使用@ExtParam引用格式: #paramName_caseId (每个DataRow引用对应的@ExtParam)
                        ext_param_name = f"{param_name}_{case_id}"
                        method_sheet.cell(row=param_row, column=cell_col).value = f"#{ext_param_name}"

            # 断言行 - 为每个测试用例生成断言
            if attr.xlsx_eg_assert and method.return_type != "void":
                for i in range(row_info['test_case_count']):
                    assert_row = row_info['assert_data_start'] + i
                    method_sheet.cell(row=assert_row, column=4).value = "AssertNotNull"
                    method_sheet.cell(row=assert_row, column=6).value = "returnObj"
                    method_sheet.cell(row=assert_row, column=10).value = 1

        # 应用样式
        if HAS_STYLE_UTIL:
            ExcelStyleUtil.style_full_workbook(workbook, attr.test_case_count)

        workbook.save(new_file_path)
        print(f"简化Excel已生成: {new_file_path}")
        return new_file_path, relative_path

# ============== 测试用例生成器 ==============
class TestCaseGenerator:

    @staticmethod
    def run(
        sub_id: str,
        class_name: str,
        method_names: List[str],
        project_root: str = None,
        attr: Attr = None,
        mock_fields: List[FieldInfo] = None,
        method_infos: List[MethodInfo] = None
    ):
        """执行生成逻辑

        Args:
            project_root: 项目根目录路径，如果指定则使用该路径，否则自动检测
        """
        if not attr or (not attr.gen_xlsx and not attr.gen_java):
            print("无生成任务")
            return

        if not sub_id or not class_name or not method_names:
            print("参数不完整")
            return

        if sub_id not in SUBID_LIMIT:
            print(f"subId必须是 PO, IMPSFC, MR, OSM, QMS, QIC, ED 或 ECN")
            return

        if '.' not in class_name:
            print("className必须是全限类名")
            return

        # 设置项目根目录（优先使用配置项）
        if project_root:
            GenerateNameUtil.set_project_root(project_root)
            print(f"使用配置的项目根目录: {project_root}")

        print(f"开始生成相关文件, 目标方法: {class_name}#{','.join(method_names)}")
        start_time = datetime.now()

        # 自动解析Java源文件获取方法信息和Mock字段（模拟Java反射）
        if not method_infos or not mock_fields:
            auto_fields, auto_methods = JavaSourceParser.analyze_class(class_name, method_names)
            if not method_infos and auto_methods:
                method_infos = auto_methods
                print(f"自动解析到 {len(method_infos)} 个方法")
            if not mock_fields and auto_fields:
                mock_fields = auto_fields
                print(f"自动解析到 {len(mock_fields)} 个Mock字段")

        # 如果仍然没有method_infos，生成默认信息
        if not method_infos:
            method_infos = []
            for name in method_names:
                method_infos.append(MethodInfo(
                    name=name,
                    return_type="void",
                    parameters=[],
                    declaring_class=class_name
                ))
            print("警告: 未能解析方法信息，使用默认值")

        # 如果仍然没有mock_fields，使用空列表
        if not mock_fields:
            mock_fields = []

        # 处理重载方法选择
        # 当找到多个同名方法时，自动选择参数最多的方法（通常是主要的业务方法）
        if len(method_infos) > 1:
            # 按方法名分组
            method_groups = {}
            for m in method_infos:
                if m.name not in method_groups:
                    method_groups[m.name] = []
                method_groups[m.name].append(m)

            # 对于每个方法名，选择参数最多的方法
            selected_methods = []
            for name in method_names:
                if name in method_groups:
                    methods = method_groups[name]
                    if len(methods) > 1:
                        # 选择参数最多的方法
                        methods.sort(key=lambda x: len(x.parameters), reverse=True)
                        selected = methods[0]
                        print(f"自动选择方法: {selected.return_type} {selected.name}({len(selected.parameters)}个参数)")
                        selected_methods.append(selected)
                    else:
                        selected_methods.append(methods[0])
                else:
                    # 方法名不存在，创建默认方法
                    selected_methods.append(MethodInfo(
                        name=name,
                        return_type="void",
                        parameters=[],
                        declaring_class=class_name
                    ))
            method_infos = selected_methods

        # ⭐ 关键修改：先查找下一个可用的测试类后缀
        test_class_suffix = JavaProcessorUtil.find_next_available_test_class_suffix(class_name)
        if test_class_suffix:
            print(f"✓ 检测到测试类已存在，自动使用后缀: {test_class_suffix}")
            print(f"✓ 将创建测试类: {class_name.split('.')[-1]}Test{test_class_suffix}.java")
        else:
            print(f"✓ 将创建基础测试类: {class_name.split('.')[-1]}Test.java")

        # 使用后缀生成Excel和Java文件
        abs_path, relative_path = ExcelProcessorUtil.save_as_new_file(method_infos, sub_id, attr, None, test_class_suffix)
        JavaProcessorUtil.save_as_new_file(method_infos, sub_id, attr, relative_path, mock_fields)

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        print(f"生成相关文件结束, 耗时: {elapsed:.0f} ms")

    @staticmethod
    def print_banner(methods: List[MethodInfo]):
        """打印方法选择提示（与Java版本相同的格式）"""
        print("\n" + "#" * 60 + "\n")
        print("请选择要进行测试的方法:\n")
        for i, method in enumerate(methods):
            params_str = ", ".join([t for t, n in method.parameters])
            print(f"{i + 1}. {method.return_type}#{method.name}({params_str})\n")
        print("0. Exit\n")
        print("#" * 60 + "\n")

# ============== 主函数入口 ==============
def main():
    """
    主函数入口
    配置参数并执行生成

    现在支持自动解析Java源文件，只需配置4个必填项：
    1. sub_id: 子系统标识 (PO / IMPSFC / MR / OSM / QMS / QIC / ED / ECN)
    2. class_name: 类全限定名
    3. method_names: 方法名列表
    4. project_root: 项目根目录路径

    Mock字段和方法签名会自动从Java源文件中解析
    """
    # ========== 必填配置 ==========

    # 子系统标识: PO / IMPSFC / MR / OSM / QMS / QIC / ED / ECN
    # PO: 生产管理 → 继承 POTestable (项目特定基类)
    # IMPSFC: 车间管理 → 继承 SFCTestable (项目特定基类)
    # MR: 物料需求 → 继承 MFTestable (公共模块基类)
    # OSM: 外协管理 → 继承 MFTestable (公共模块基类)
    # QMS: 质量管理 → 继承 MFTestable (公共模块基类)
    # QIC: 质检中心 → 继承 MFTestable (公共模块基类)
    # ED: 工程数据 → 继承 MFTestable (公共模块基类)
    # ECN: 工程变更 → 继承 MFTestable (公共模块基类)
    sub_id = "PO"

    # 测试方法所在类的全限类名
    class_name = "com.yonyou.biz.mm.mfpo.service.po.common.bizservice.ProductionOrderService"

    # 测试方法名称，多个方法用列表
    method_names = ["forceCloseWhenQuantityZero"]

    # 项目根目录路径（必填，用于确定Excel和Java文件生成位置）
    # 请替换为您的实际项目路径
    # 例如: "D:/unitTestProject/production-order" (Windows)
    #       "/home/user/unitTestProject/production-order" (Linux)
    project_root = "D:\\unitTestProject\\production-order"  # ⚠️ 请替换为实际路径

    # ========== 可选配置 ==========

    # 生成属性配置（通常不需要修改）
    attr = Attr(
        gen_java=True,           # 生成Java测试类文件
        java_mock_method=True,   # 是否生成Mock方法框架
        gen_xlsx=True,           # 是否生成Excel测试用例文件
        xlsx_eg_value=True,      # 是否生成示例参数值
        xlsx_eg_assert=True,     # 是否生成示例断言
        test_case_count=8,       # 测试用例数量：3个PM场景 + 5个边界测试
        related_task_number="YYY-T-24594,YYY-MF-F-2702"   # PM问题号
    )

    # 以下配置会自动从Java源文件解析，无需手动填写
    # 如果需要覆盖自动解析的结果，可以取消注释并填写

    # mock_fields = []  # 自动解析@Autowired字段
    # method_infos = [] # 自动解析方法签名

    # ========== 执行生成 ==========
    # 自动解析Java源文件，无需手动指定方法信息

    TestCaseGenerator.run(
        sub_id=sub_id,
        class_name=class_name,
        method_names=method_names,
        project_root=project_root,
        attr=attr
    )


if __name__ == "__main__":
    main()