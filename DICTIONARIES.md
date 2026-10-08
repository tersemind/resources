# Char tokenizer 原始词典归档

从 infra 的 `tokenizer/char/res/sources` 保存 13 个原始词典，共 16,259,265 字节。jieba 用于分词与词性词典，Norvig 和 THUOCL 用于分词词典。原始字节未改动，保留 BOM、CR 分隔符、词频和词性列；清理及归一化仍由 infra 的构建脚本完成。

上传附件：[dictionaries-3ebaa990eb35.tar.gz](dist/dictionaries-3ebaa990eb35.tar.gz)（6,520,187 字节），由 `python3 pack.py dictionaries` 生成。本地原文件直接位于 `assets/dictionaries/`；包内也直接包含 `jieba_big.txt`、`count_1w.txt` 和 `thuocl/`，没有额外顶层目录。许可文件从根 `licenses/` 随发布附上。

## 文件清单

| 文件 | 字节数 | 格式 | 上游 |
| --- | ---: | --- | --- |
| [count_1w.txt](assets/dictionaries/count_1w.txt) | 4,956,242 | 词、次数 | [来源](https://www.norvig.com/ngrams/count_1w.txt) |
| [jieba_big.txt](assets/dictionaries/jieba_big.txt) | 8,583,143 | 词、词频、词性 | [来源](https://raw.githubusercontent.com/fxsjy/jieba/master/extra_dict/dict.txt.big) |
| [thuocl/THUOCL_IT.txt](assets/dictionaries/thuocl/THUOCL_IT.txt) | 308,187 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_IT.txt) |
| [thuocl/THUOCL_animal.txt](assets/dictionaries/thuocl/THUOCL_animal.txt) | 320,553 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_animal.txt) |
| [thuocl/THUOCL_caijing.txt](assets/dictionaries/thuocl/THUOCL_caijing.txt) | 62,296 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_caijing.txt) |
| [thuocl/THUOCL_car.txt](assets/dictionaries/thuocl/THUOCL_car.txt) | 32,492 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_car.txt) |
| [thuocl/THUOCL_chengyu.txt](assets/dictionaries/thuocl/THUOCL_chengyu.txt) | 166,549 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_chengyu.txt) |
| [thuocl/THUOCL_diming.txt](assets/dictionaries/thuocl/THUOCL_diming.txt) | 640,673 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_diming.txt) |
| [thuocl/THUOCL_food.txt](assets/dictionaries/thuocl/THUOCL_food.txt) | 144,749 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_food.txt) |
| [thuocl/THUOCL_law.txt](assets/dictionaries/thuocl/THUOCL_law.txt) | 277,745 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_law.txt) |
| [thuocl/THUOCL_lishimingren.txt](assets/dictionaries/thuocl/THUOCL_lishimingren.txt) | 163,136 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_lishimingren.txt) |
| [thuocl/THUOCL_medical.txt](assets/dictionaries/thuocl/THUOCL_medical.txt) | 308,805 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_medical.txt) |
| [thuocl/THUOCL_poem.txt](assets/dictionaries/thuocl/THUOCL_poem.txt) | 294,695 | 词、DF | [来源](https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_poem.txt) |

每个文件的当前 SHA256 见 `bundles.json` 的 dictionaries 包清单，来源记录见 `assets.json`。在 resources 根目录校验全部原文件：

```bash
shasum -a 256 -c SHA256SUMS
```

版本采用实际使用的文件哈希，不将来源页面的 `master` 推断为某个已知源码提交。jieba 的 MIT、THUOCL 的上游条款和 Norvig 数据来源记录见 [许可说明](licenses/NOTICES.md)。

## 上传及接入顺序

先按根 README 上传完整快照，再校验附件；之后切换 infra 构建引用，最后删除 infra 中的 13 个原始文件。当前仅完成归档，构建仍使用原位置，避免下载未发布的地址。

新增的外部仓库同时服务于 `//tokenizer/char/res:seg_main_dat` 和 `//tokenizer/pos/res:pos_jieba_dat`，不能只改分词构建而遗漏 jieba 的词性构建引用。原始词典放资源仓库；构建时仍生成原有 `.dat` 产物，不改变库的运行时接口。

## MODULE.bazel 配置

上传完成后，在 `http_archive` 定义之后增加：

```python
http_archive(
    name = "char_dictionary_sources",
    sha256 = "3ebaa990eb3517eba32d2eeb2c1c67212d41f08936e44b235da0601fa7715e4d",
    urls = [
        "https://github.com/tersemind/resources/releases/download/infra-resources-2026-10-09/dictionaries-3ebaa990eb35.tar.gz",
    ],
    build_file_content = """
exports_files(["jieba_big.txt"], visibility = ["//visibility:public"])
filegroup(
    name = "sources",
    srcs = glob(["*.txt", "thuocl/*.txt"]),
    visibility = ["//visibility:public"],
)
""",
)
```

这是按 dictionaries 类型生成的固定快照包，没有对应的上游同字节压缩包；不能把 jieba 或 THUOCL 的单独上游 URL 当成该包的备用地址。需要备用源时，上传同一个压缩包到其他镜像。

## 分词与词性构建调整

`tokenizer/char/res/BUILD.bazel` 中 `seg_main_dat.srcs` 的 `glob(["sources/**"])` 改为下面两个外部输入，其余构建输入、工具和输出保持原样：

```python
"@char_dictionary_sources//:sources",
"@char_dictionary_sources//:jieba_big.txt",
```

在现有构建命令前设置词典源路径：

```python
cmd = """SEG_DICT_SRC_DIR="$$(dirname "$(location @char_dictionary_sources//:jieba_big.txt)")" python3 $(location build_seg_dict.py) $(location //tokenizer/char/tests:universal_tokenizer_dict_merge) $(@D)""",
```

`tokenizer/pos/res/BUILD.bazel` 的 `srcs` 和命令中的 jieba 标签改为 `@char_dictionary_sources//:jieba_big.txt`。随后删除 char/res 中导出旧 `sources/jieba_big.txt` 的 `exports_files`，移除主库的 `sources/` 数据，并更新原有来源文档。独立运行 `build_seg_dict.py` 时显式设置 `SEG_DICT_SRC_DIR`，或将其默认路径调整为已下载的快照目录。

## 当前本地使用

在 infra 根目录可以先使用已归档的原文件目录，无需上传或重新下载：

```bash
source bd/paths/paths.sh && infra_load_paths "$PWD"
bazel build //tokenizer/char/tests:universal_tokenizer_dict_merge
SEG_DICT_SRC_DIR="$PWD/resources/assets/dictionaries" \
  python3 tokenizer/char/res/build_seg_dict.py \
  bazel-bin/tokenizer/char/tests/universal_tokenizer_dict_merge \
  "$INFRA_TMP_ROOT/seg_dict/output"
```

切换后构建 `//tokenizer/char/res:seg_main_dat` 和 `//tokenizer/pos/res:pos_jieba_dat`，比较切换前后的输出及分词/词性结果。归档的词典应与原源逐字节一致，不借迁移调整合并权重或过滤逻辑。
