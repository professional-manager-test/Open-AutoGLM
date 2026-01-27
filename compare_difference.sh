#!/bin/bash

#!/bin/bash

# 脚本名称: compare_branches.sh
# 功能: 比较两个Git分支的差异，包括变化的行数和具体内容

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认分支名
MAIN_BRANCH="main"
FEATURE_BRANCH=""

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -m, --main BRANCH     指定主分支 (默认: main)"
    echo "  -f, --feature BRANCH  指定特性分支 (必需)"
    echo "  -h, --help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -f feature-branch"
    echo "  $0 -m develop -f my-feature"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--main)
            MAIN_BRANCH="$2"
            shift 2
            ;;
        -f|--feature)
            FEATURE_BRANCH="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 检查是否提供了特性分支
if [ -z "$FEATURE_BRANCH" ]; then
    echo -e "${RED}错误: 请指定特性分支${NC}"
    show_help
    exit 1
fi

# 检查当前目录是否为Git仓库
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}错误: 当前目录不是一个Git仓库${NC}"
    exit 1
fi

# 检查分支是否存在
if ! git show-ref --verify --quiet "refs/heads/$MAIN_BRANCH"; then
    echo -e "${RED}错误: 主分支 '$MAIN_BRANCH' 不存在${NC}"
    exit 1
fi

if ! git show-ref --verify --quiet "refs/heads/$FEATURE_BRANCH"; then
    echo -e "${RED}错误: 特性分支 '$FEATURE_BRANCH' 不存在${NC}"
    exit 1
fi

echo -e "${BLUE}=== Git 分支比较工具 ===${NC}"
echo -e "${YELLOW}主分支: $MAIN_BRANCH${NC}"
echo -e "${YELLOW}特性分支: $FEATURE_BRANCH${NC}"
echo ""

# 获取统计信息
echo -e "${BLUE}=== 变更统计 ===${NC}"

# 计算增加和删除的行数
stats=$(git diff --shortstat "$MAIN_BRANCH..$FEATURE_BRANCH")
echo -e "${GREEN}$stats${NC}"

# 更详细的统计
detailed_stats=$(git diff --numstat "$MAIN_BRANCH..$FEATURE_BRANCH")
total_additions=0
total_deletions=0

while IFS= read -r line; do
    if [ -n "$line" ]; then
        additions=$(echo "$line" | awk '{print $1}')
        deletions=$(echo "$line" | awk '{print $2}')
        
        # 将 "—" 转换为空值处理
        additions=${additions:-0}
        deletions=${deletions:-0}
        
        total_additions=$((total_additions + additions))
        total_deletions=$((total_deletions + deletions))
    fi
done <<< "$detailed_stats"

echo -e "${GREEN}总增加行数: $total_additions${NC}"
echo -e "${GREEN}总删除行数: $total_deletions${NC}"
echo ""

# 显示修改的文件列表
echo -e "${BLUE}=== 修改的文件 ===${NC}"
modified_files=$(git diff --name-only "$MAIN_BRANCH..$FEATURE_BRANCH")

if [ -z "$modified_files" ]; then
    echo -e "${GREEN}没有发现文件变更${NC}"
else
    file_count=0
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            file_count=$((file_count + 1))
            echo -e "${YELLOW}$file${NC}"
            
            # 获取每个文件的行数变更
            file_stat=$(git diff --numstat "$MAIN_BRANCH..$FEATURE_BRANCH" -- "$file")
            if [ -n "$file_stat" ]; then
                additions=$(echo "$file_stat" | awk '{print $1}')
                deletions=$(echo "$file_stat" | awk '{print $2}')
                echo -e "  ${GREEN}+${additions}${NC}, ${RED}-${deletions}${NC} 行"
            fi
        fi
    done <<< "$modified_files"
    
    echo ""
    echo -e "${GREEN}总共修改了 $file_count 个文件${NC}"
fi

echo ""
echo -e "${BLUE}=== 具体变更内容 ===${NC}"
echo -e "${YELLOW}以下是具体的代码变更:${NC}"
echo ""

# 显示实际的代码差异
git diff --color=always "$MAIN_BRANCH..$FEATURE_BRANCH" | \
    sed -e "s/^+\(.*\)$/\x1b[32m&\x1b[0m/" \
        -e "s/^-\\(.*\\)$/\x1b[31m&\x1b[0m/"

echo ""
echo -e "${BLUE}=== 总结 ===${NC}"
echo -e "${GREEN}主分支 ($MAIN_BRANCH) -> 特性分支 ($FEATURE_BRANCH) 的变更已显示完成${NC}"
