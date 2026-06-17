# 重庆房产口播运营 Codex Skills

这个仓库包含两个可复用 Codex skill，用于把重庆房产区域号/总监号的口播运营流程标准化。

## Skills

### `cq-koubo-sop`

中文展示名：重庆区域口播运营落地包

用于生成区域口播运营完整交付框架：

- Word《区域总监自媒体口播落地执行手册》
- Excel《区域总监号运营执行表》
- 数据资料包、客户问题池、竞品拆解表
- 30天选题排期、15条首批脚本卡
- 拍摄通告单、发布复盘表

### `cq-koubo-fengmian`

中文展示名：重庆口播封面生成

用于生成重庆房产口播封面三件套：

- 数据判断型
- 客户问题型
- 实地验证/板块对比型
- 三件套总览图

## Install

复制两个 skill 文件夹到 Codex skill 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R cq-koubo-sop cq-koubo-fengmian "${CODEX_HOME:-$HOME/.codex}/skills/"
```

安装后重启 Codex，让技能列表刷新。

## Dependencies

脚本依赖：

```bash
pip install -r requirements.txt
```

如果你使用 Codex 自带运行时，通常已经包含这些库。

## Quick Test

生成一个礼嘉区域口播运营落地包：

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/cq-koubo-sop/scripts/build_region_koubo_package.py" \
  --region 礼嘉 \
  --output-dir ./礼嘉口播运营落地包 \
  --generate-covers
```

单独生成中央公园封面三件套：

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/cq-koubo-fengmian/scripts/create_cover_templates.py" \
  --region 中央公园 \
  --account-line '中央公园买房参谋｜XX' \
  --output-dir ./封面模板
```

## Notes

- `cq-koubo-sop` 生成的是结构化初稿，正式项目仍需补充真实数据、客户问题和竞品拆解。
- `cq-koubo-fengmian` 默认追求商业海报质感，若生成图中文字不稳定，可用脚本生成可控文字版兜底。
- 房产内容必须遵守合规表达，不承诺涨跌、收益、成交或教育结果。
