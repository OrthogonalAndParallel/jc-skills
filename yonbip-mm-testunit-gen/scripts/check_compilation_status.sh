#!/bin/bash
# ================================================================================
# 项目编译状态检查脚本（增强版）
# 功能：检查target目录、时间、源码修改、测试类修改
# 作者：yonbip-mm-testunit-gen 技能
# 更新时间：2026-09-17
# ================================================================================

# 使用说明
usage() {
    echo "使用方法："
    echo "  $0 <项目模块路径>"
    echo ""
    echo "示例："
    echo "  $0 D:/unitTestProject/production-order/src/manufacturing-service"
    echo ""
    echo "功能："
    echo "  1. 检查target目录是否存在"
    echo "  2. 检查classes和test-classes目录"
    echo "  3. 检查target目录的日期（是否今天）"
    echo "  4. 检查源码是否有修改"
    echo "  5. 检查测试类是否有修改"
    echo "  6. 根据综合判断，推荐最优的编译方式"
    exit 1
}

# 参数检查
if [ -z "$1" ]; then
    usage
fi

MODULE_PATH="$1"
TARGET_DIR="$MODULE_PATH/target"

# 获取当前日期（格式：YYYY-MM-DD）
# Linux/Mac
CURRENT_DATE=$(date +"%Y-%m-%d")
# Windows Git Bash: 使用 date +"%Y-%m-%d"
# Windows PowerShell: 使用 Get-Date -Format 'yyyy-MM-dd'

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印标题
print_title() {
    echo ""
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
}

# 函数：检查目录是否存在
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ $2 存在${NC}"
        return 0
    else
        echo -e "${RED}❌ $2 不存在${NC}"
        return 1
    fi
}

# 函数：获取目录日期
get_dir_date() {
    if [ -d "$1" ]; then
        # Linux/Mac
        stat -c "%y" "$1" 2>/dev/null | cut -d' ' -f1
        # Windows Git Bash: stat 命令可能不可用
        # Windows PowerShell: (Get-Item '$1').LastWriteTime.ToString('yyyy-MM-dd')
    else
        echo "N/A"
    fi
}

# 函数：检查源码修改
check_source_modified() {
    local classes_dir="$1"
    local source_dir="$MODULE_PATH/src/main/java"

    if [ ! -d "$classes_dir" ]; then
        echo "N/A"
        return
    fi

    # 查找比classes更新的源码文件
    # Linux/Mac
    local count=$(find "$source_dir" -type f -name "*.java" -newer "$classes_dir" 2>/dev/null | wc -l)
    # Windows PowerShell: (Get-ChildItem -Path '$source_dir' -Filter *.java -Recurse | Where-Object { $_.LastWriteTime -gt (Get-Item '$classes_dir').LastWriteTime }).Count
    echo "$count"
}

# 函数：检查测试类修改
check_test_modified() {
    local test_classes_dir="$1"
    local test_source_dir="$MODULE_PATH/src/test/java"

    if [ ! -d "$test_classes_dir" ]; then
        echo "N/A"
        return
    fi

    # 查找比test-classes更新的测试类文件
    local count=$(find "$test_source_dir" -type f -name "*.java" -newer "$test_classes_dir" 2>/dev/null | wc -l)
    echo "$count"
}

# 开始检查
print_title "🔍 项目编译状态检测"

# 步骤1：检查target目录
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}❌ target目录不存在${NC}"
    echo ""
    print_title "🎯 编译状态判断"
    echo -e "状态：${RED}未编译${NC}"
    echo ""
    echo "推荐操作：全量编译"
    echo "命令：mvn clean install -DskipTests -T 4"
    echo "预计耗时：~3-5分钟"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ target目录 存在${NC}"

# 步骤2：检查classes和test-classes
CLASSES_DIR="$TARGET_DIR/classes"
TEST_CLASSES_DIR="$TARGET_DIR/test-classes"

check_dir "$CLASSES_DIR" "classes目录（源码编译输出）"
HAS_CLASSES=$?

check_dir "$TEST_CLASSES_DIR" "test-classes目录（测试类编译输出）"
HAS_TEST_CLASSES=$?

# 步骤3：检查target时间
TARGET_DATE=$(get_dir_date "$TARGET_DIR")
echo "📅 target目录日期：$TARGET_DATE"
echo "📅 当前日期：$CURRENT_DATE"

IS_TODAY=false
if [ "$TARGET_DATE" = "$CURRENT_DATE" ]; then
    IS_TODAY=true
    echo -e "${GREEN}✅ target是今天的${NC}"
else
    echo -e "${YELLOW}⚠️ target不是今天的（可能过期）${NC}"
fi

# 步骤4：检查源码修改
MODIFIED_SOURCE_COUNT=$(check_source_modified "$CLASSES_DIR")
echo "📝 源码修改文件数：$MODIFIED_SOURCE_COUNT"

HAS_MODIFIED_SOURCE=false
if [ "$MODIFIED_SOURCE_COUNT" != "N/A" ] && [ "$MODIFIED_SOURCE_COUNT" -gt 0 ]; then
    HAS_MODIFIED_SOURCE=true
    echo -e "${YELLOW}⚠️ 检测到源码修改${NC}"
else
    echo -e "${GREEN}✅ 无源码修改${NC}"
fi

# 步骤5：检查测试类修改
MODIFIED_TEST_COUNT=$(check_test_modified "$TEST_CLASSES_DIR")
echo "📝 测试类修改文件数：$MODIFIED_TEST_COUNT"

HAS_MODIFIED_TEST=false
if [ "$MODIFIED_TEST_COUNT" != "N/A" ] && [ "$MODIFIED_TEST_COUNT" -gt 0 ]; then
    HAS_MODIFIED_TEST=true
    echo -e "${YELLOW}⚠️ 检测到测试类修改${NC}"
else
    echo -e "${GREEN}✅ 无测试类修改${NC}"
fi

# 综合判断
echo ""
print_title "🎯 编译状态判断"

if [ $HAS_CLASSES -ne 0 ] && [ $HAS_TEST_CLASSES -ne 0 ]; then
    # 情况1：未编译
    echo -e "状态：${RED}未编译${NC}"
    echo ""
    echo "推荐操作：全量编译"
    echo "命令：mvn clean install -DskipTests -T 4"
    echo "预计耗时：~3-5分钟"

elif [ $HAS_CLASSES -ne 0 ]; then
    # 情况2：缺少classes
    echo -e "状态：${RED}缺少classes${NC}"
    echo ""
    echo "推荐操作：全量编译"
    echo "命令：mvn clean install -DskipTests -T 4"
    echo "预计耗时：~3-5分钟"

elif [ $HAS_TEST_CLASSES -ne 0 ]; then
    # 情况3：缺少test-classes
    echo -e "状态：${YELLOW}缺少test-classes${NC}"
    echo ""
    echo -e "推荐操作：${GREEN}直接运行测试（Maven自动编译）⚡${NC}"
    echo "命令：mvn test -Dtest=<测试类名>"
    echo "耗时：~30秒（Maven增量编译）"
    echo ""
    echo -e "${BLUE}💡 说明：Maven会自动检测到缺少test-classes并编译${NC}"

elif $IS_TODAY && ! $HAS_MODIFIED_SOURCE && ! $HAS_MODIFIED_TEST; then
    # 情况4：今天的target且无任何修改
    echo -e "状态：${GREEN}已编译且最新 ⚡${NC}"
    echo ""
    echo "推荐操作：直接运行测试（最快）"
    echo "命令：mvn test -Dtest=<测试类名>"
    echo "预计耗时：~10秒"

elif $IS_TODAY && $HAS_MODIFIED_SOURCE; then
    # 情况5：今天的target但有源码修改
    echo -e "状态：${YELLOW}已编译但有源码修改${NC}"
    echo ""
    echo "推荐操作：增量编译"
    echo "命令：mvn compile -DskipTests"
    echo "预计耗时：~30秒"

elif $IS_TODAY && $HAS_MODIFIED_TEST; then
    # 情况5.2：今天的target但有测试类修改
    echo -e "状态：${YELLOW}已编译但有测试类修改${NC}"
    echo ""
    echo -e "推荐操作：${GREEN}直接运行测试（Maven自动增量编译）⚡${NC}"
    echo "命令：mvn test -Dtest=<测试类名>"
    echo "耗时：~30秒（Maven增量编译）"
    echo ""
    echo -e "${BLUE}💡 说明：Maven会自动检测到测试类修改并重新编译${NC}"

else
    # 情况6：非今天的target
    echo -e "状态：${YELLOW}已编译但target过期${NC}"
    echo ""
    echo -e "推荐操作：${GREEN}增量编译（优先）或 直接运行测试${NC}"
    echo "命令1：mvn compile -DskipTests （增量编译，推荐）"
    echo "命令2：mvn test -Dtest=<测试类名> （Maven自动编译）"
    echo "耗时：~30秒"
    echo ""
    echo -e "${BLUE}💡 建议：优先尝试直接运行测试，Maven会自动处理过期问题${NC}"
fi

echo ""
echo "══════════════════════════════════════════════════════════"