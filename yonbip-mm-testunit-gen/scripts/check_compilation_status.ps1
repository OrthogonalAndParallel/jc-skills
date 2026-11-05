# ================================================================================
# 项目编译状态检查脚本（Windows PowerShell版本）
# 功能：检查target目录、时间、源码修改、测试类修改
# 作者：yonbip-mm-testunit-gen 技能
# 更新时间：2026-09-17
# ================================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ModulePath
)

# 颜色定义
function Write-ColorOutput($ForegroundColor) {
    $fc = $ForegroundColor
    $bc = $Host.UI.RawUI.BackgroundColor
    Write-Host -ForegroundColor $fc -BackgroundColor $bc
}

# 获取当前日期
$CurrentDate = Get-Date -Format "yyyy-MM-dd"
$TargetDir = Join-Path $ModulePath "target"

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "  🔍 项目编译状态检测" -ForegroundColor Blue
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Blue

# 步骤1：检查target目录
if (-not (Test-Path $TargetDir)) {
    Write-Host "❌ target目录不存在" -ForegroundColor Red
    Write-Host ""
    Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host "  🎯 编译状态判断" -ForegroundColor Blue
    Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host "状态：未编译" -ForegroundColor Red
    Write-Host ""
    Write-Host "推荐操作：全量编译"
    Write-Host "命令：mvn clean install -DskipTests -T 4"
    Write-Host "预计耗时：~3-5分钟"
    Write-Host ""
    exit 1
}

Write-Host "✅ target目录 存在" -ForegroundColor Green

# 步骤2：检查classes和test-classes
$ClassesDir = Join-Path $TargetDir "classes"
$TestClassesDir = Join-Path $TargetDir "test-classes"

$HasClasses = Test-Path $ClassesDir
$HasTestClasses = Test-Path $TestClassesDir

if ($HasClasses) {
    Write-Host "✅ classes目录（源码编译输出） 存在" -ForegroundColor Green
} else {
    Write-Host "❌ classes目录（源码编译输出） 不存在" -ForegroundColor Red
}

if ($HasTestClasses) {
    Write-Host "✅ test-classes目录（测试类编译输出） 存在" -ForegroundColor Green
} else {
    Write-Host "❌ test-classes目录（测试类编译输出） 不存在" -ForegroundColor Red
}

# 步骤3：检查target时间
$TargetDate = (Get-Item $TargetDir).LastWriteTime.ToString("yyyy-MM-dd")
Write-Host "📅 target目录日期：$TargetDate"
Write-Host "📅 当前日期：$CurrentDate"

$IsToday = ($TargetDate -eq $CurrentDate)
if ($IsToday) {
    Write-Host "✅ target是今天的" -ForegroundColor Green
} else {
    Write-Host "⚠️ target不是今天的（可能过期）" -ForegroundColor Yellow
}

# 步骤4：检查源码修改
$SourceDir = Join-Path $ModulePath "src\main\java"
if ($HasClasses) {
    $ClassesTime = (Get-Item $ClassesDir).LastWriteTime
    $ModifiedSourceFiles = Get-ChildItem -Path $SourceDir -Filter *.java -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $ClassesTime }
    $ModifiedSourceCount = $ModifiedSourceFiles.Count
    Write-Host "📝 源码修改文件数：$ModifiedSourceCount"

    if ($ModifiedSourceCount -gt 0) {
        Write-Host "⚠️ 检测到源码修改" -ForegroundColor Yellow
    } else {
        Write-Host "✅ 无源码修改" -ForegroundColor Green
    }
}

# 步骤5：检查测试类修改
$TestSourceDir = Join-Path $ModulePath "src\test\java"
if ($HasTestClasses) {
    $TestClassesTime = (Get-Item $TestClassesDir).LastWriteTime
    $ModifiedTestFiles = Get-ChildItem -Path $TestSourceDir -Filter *.java -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $TestClassesTime }
    $ModifiedTestCount = $ModifiedTestFiles.Count
    Write-Host "📝 测试类修改文件数：$ModifiedTestCount"

    if ($ModifiedTestCount -gt 0) {
        Write-Host "⚠️ 检测到测试类修改" -ForegroundColor Yellow
    } else {
        Write-Host "✅ 无测试类修改" -ForegroundColor Green
    }
}

# 综合判断
Write-Host ""
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "  🎯 编译状态判断" -ForegroundColor Blue
Write-Host "══════════════════════════════════════════════════════════" -ForegroundColor Blue

if (-not $HasClasses -and -not $HasTestClasses) {
    # 情况1：未编译
    Write-Host "状态：未编译" -ForegroundColor Red
    Write-Host ""
    Write-Host "推荐操作：全量编译"
    Write-Host "命令：mvn clean install -DskipTests -T 4"
    Write-Host "预计耗时：~3-5分钟"

} elseif (-not $HasClasses) {
    # 情况2：缺少classes
    Write-Host "状态：缺少classes" -ForegroundColor Red
    Write-Host ""
    Write-Host "推荐操作：全量编译"
    Write-Host "命令：mvn clean install -DskipTests -T 4"
    Write-Host "预计耗时：~3-5分钟"

} elseif (-not $HasTestClasses) {
    # 情况3：缺少test-classes
    Write-Host "状态：缺少test-classes" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "推荐操作：直接运行测试（Maven自动编译）⚡" -ForegroundColor Green
    Write-Host "命令：mvn test -Dtest=<测试类名>"
    Write-Host "耗时：~30秒（Maven增量编译）"
    Write-Host ""
    Write-Host "💡 说明：Maven会自动检测到缺少test-classes并编译" -ForegroundColor Blue

} elseif ($IsToday -and $ModifiedSourceCount -eq 0 -and $ModifiedTestCount -eq 0) {
    # 情况4：今天的target且无任何修改
    Write-Host "状态：已编译且最新 ⚡" -ForegroundColor Green
    Write-Host ""
    Write-Host "推荐操作：直接运行测试（最快）"
    Write-Host "命令：mvn test -Dtest=<测试类名>"
    Write-Host "预计耗时：~10秒"

} elseif ($IsToday -and $ModifiedSourceCount -gt 0) {
    # 情况5：今天的target但有源码修改
    Write-Host "状态：已编译但有源码修改" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "推荐操作：增量编译"
    Write-Host "命令：mvn compile -DskipTests"
    Write-Host "预计耗时：~30秒"

} elseif ($IsToday -and $ModifiedTestCount -gt 0) {
    # 情况5.2：今天的target但有测试类修改
    Write-Host "状态：已编译但有测试类修改" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "推荐操作：直接运行测试（Maven自动增量编译）⚡" -ForegroundColor Green
    Write-Host "命令：mvn test -Dtest=<测试类名>"
    Write-Host "耗时：~30秒（Maven增量编译）"
    Write-Host ""
    Write-Host "💡 说明：Maven会自动检测到测试类修改并重新编译" -ForegroundColor Blue

} else {
    # 情况6：非今天的target
    Write-Host "状态：已编译但target过期" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "推荐操作：增量编译（优先）或 直接运行测试" -ForegroundColor Green
    Write-Host "命令1：mvn compile -DskipTests （增量编译，推荐）"
    Write-Host "命令2：mvn test -Dtest=<测试类名> （Maven自动编译）"
    Write-Host "耗时：~30秒"
    Write-Host ""
    Write-Host "💡 建议：优先尝试直接运行测试，Maven会自动处理过期问题" -ForegroundColor Blue
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════"