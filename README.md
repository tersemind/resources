# TerseMind 构建依赖资源

原始文件按类型放在 `assets/`；每个一级子目录统一生成一个 Release 压缩包。Git 管理清单、许可、文档和打包脚本，资源本体及打包产物作为 Releases 附件保存。

当前快照为 2026-10-09，共 4 类、21 个原始文件：8 个 MODULE HTTP 资源和 13 个 char tokenizer 词典。原始字节保持不变；Bazel 缓存资源匹配 MODULE 的 SHA256，词典匹配 infra 实际源文件。本目录尚未上传，infra 构建仍使用原有资源引用。

## 目录

```text
assets/
  corpus/             MSR 语料
  tokenizers/         DeepSeek、Qwen tokenizer.json
  pdf/                Adobe 原始压缩包、fonttools 字形表
  dictionaries/
    jieba_big.txt
    count_1w.txt
    thuocl/           11 个领域词表
licenses/             上游许可与来源说明
dist/                 按类型生成的上传压缩包
pack.py               统一打包入口（Python 3.9+）
assets.json           原始资源来源、用途和许可记录
bundles.json          自动生成的包哈希、附件地址及逐文件清单
SHA256SUMS            21 个原始文件的校验值
RELEASE_SHA256SUMS    4 个类型包的校验值
DICTIONARIES.md       词典文件清单与 char/POS 接入说明
RELEASE.md            手动发布说明
README.md             本文件
```

`thuocl/` 是词典内部的领域分组，保留供构建脚本读取；不再有 `tokenizer-char-sources/` 包装目录。压缩包内容直接从对应类型目录开始，不添加类型名或其他顶层目录，也不要求 Bazel 配置 `strip_prefix`。PDF 类型中原始上游压缩包保持原样，以保留其原始哈希和许可。

## 类型包

| 类型 | 原始文件数 | 当前上传附件 | 压缩大小 |
| --- | ---: | --- | ---: |
| `corpus` | 1 | [corpus-ab5947391ce6.tar.gz](dist/corpus-ab5947391ce6.tar.gz) | 5.491 MiB |
| `dictionaries` | 13 | [dictionaries-3ebaa990eb35.tar.gz](dist/dictionaries-3ebaa990eb35.tar.gz) | 6.218 MiB |
| `pdf` | 5 | [pdf-d8292e360209.tar.gz](dist/pdf-d8292e360209.tar.gz) | 6.191 MiB |
| `tokenizers` | 2 | [tokenizers-7c48be6322b6.tar.gz](dist/tokenizers-7c48be6322b6.tar.gz) | 3.799 MiB |

类型包名称采用 `<类型>-<内容SHA256前12位>.tar.gz`。新增、删除或修改该类型的任何文件后，重新打包会得到新的包哈希；内容没有变化则文件名和校验值保持一致。每个类型始终对应一个当前包，`dist/` 不保留本脚本生成的旧版本；已发布的历史附件继续保留。

## 原始资源

| 原 Bazel 仓库名 | 本地文件 | 大小 | 用途 |
| --- | --- | ---: | --- |
| `msr_training_corpus` | [msr-training-872a24b0aa82.utf8](assets/corpus/msr-training-872a24b0aa82.utf8) | 16.109 MiB | 构建 tw 中文分词词典 |
| `deepseek_r1_tokenizer` | [deepseek-r1-tokenizer-ecb6f9fc3698.json](assets/tokenizers/deepseek-r1-tokenizer-ecb6f9fc3698.json) | 7.484 MiB | DeepSeek-R1 BPE 词表及分词配置 |
| `qwen3_tokenizer` | [qwen3-0.6b-tokenizer-aeb13307a71a.json](assets/tokenizers/qwen3-0.6b-tokenizer-aeb13307a71a.json) | 10.893 MiB | Qwen3-0.6B BPE 词表及分词配置 |
| `adobe_agl_aglfn` | [adobe-agl-aglfn-4036a9ca80a62f64f9de4f7321a9a045ad0ecfd6.tar.gz](assets/pdf/adobe-agl-aglfn-4036a9ca80a62f64f9de4f7321a9a045ad0ecfd6.tar.gz) | 0.034 MiB | Adobe Glyph List、ZapfDingbats 字形名映射 |
| `adobe_cmap_resources` | [adobe-cmap-resources-f5cf3bca7fdfeaceb77aa82847e974f2306c20b4.tar.gz](assets/pdf/adobe-cmap-resources-f5cf3bca7fdfeaceb77aa82847e974f2306c20b4.tar.gz) | 5.283 MiB | PDF CJK 字符编码映射 CMap |
| `adobe_mapping_resources_pdf` | [adobe-mapping-resources-pdf-2dd5e53fb74a01718b9dfd448a0d1cce6fff2aa5.tar.gz](assets/pdf/adobe-mapping-resources-pdf-2dd5e53fb74a01718b9dfd448a0d1cce6fff2aa5.tar.gz) | 1.482 MiB | PDF CID → Unicode 映射 |
| `adobe_core14_afms` | [adobe-core14-afms-8c892c3c4955.zip](assets/pdf/adobe-core14-afms-8c892c3c4955.zip) | 0.121 MiB | PDF Core 14 字体度量 AFM |
| `fonttools_standard_glyph_order` | [fonttools-standardGlyphOrder-56b543826cb229cb945ea83a61daaca1a61237a1.py](assets/pdf/fonttools-standardGlyphOrder-56b543826cb229cb945ea83a61daaca1a61237a1.py) | 0.006 MiB | TrueType post 表的 258 个标准 Macintosh 字形名 |

其余 13 个词典的逐文件列表见 [DICTIONARIES.md](DICTIONARIES.md)。`assets.json` 记录来源、用途和许可；`bundles.json` 自动记录所有实际文件的当前哈希及其包内路径。没有可核实源码提交的文件以内容哈希标识版本，不将 `master` 当作固定提交。

## 打包与更新

在 resources 仓库根目录执行：

```bash
python3 pack.py                 # 打包 assets/ 下所有一级目录
python3 pack.py dictionaries    # 只更新词典类型
python3 pack.py pdf tokenizers  # 更新指定类型
shasum -a 256 -c SHA256SUMS
```

新文件直接放入对应类型目录。新类型直接创建 `assets/<类型>/`，运行不带类型参数的命令即可自动发现，无需另写打包逻辑或为单个文件生成压缩包。来源及许可信息维护在已有清单和许可目录中。

脚本自动更新 `bundles.json`、`SHA256SUMS` 和 `RELEASE_SHA256SUMS`。指定类型时，其他类型的文件和包必须仍一致，避免发布过期包。`assets.json` 的来源记录由维护者更新，脚本不会凭文件名猜测来源或授予许可。README 的类型表是本次快照的展示，更新版本时按新 `bundles.json` 调整。

## 手动上传

先校验原始文件，再从 `bundles.json` 读取类型包及 SHA256。当前拟用固定 tag：`infra-resources-2026-10-09`；下一批更新先修改 `assets.json.release_tag` 并重新运行打包，保留已发布的旧 tag。

只提交元数据、脚本和文档，资源与 `dist/` 作为附件上传：

```bash
git add README.md DICTIONARIES.md RELEASE.md pack.py assets.json bundles.json \
  SHA256SUMS RELEASE_SHA256SUMS licenses
git commit -m "Organize infra resources by category"
git push origin HEAD
```

在 [Releases 页面](https://github.com/tersemind/resources/releases) 创建草稿，正文使用 `RELEASE.md`，上传 4 个类型压缩包及清单、文档和许可文件。也可以手动执行：

```bash
gh release create infra-resources-2026-10-09 \
  --repo tersemind/resources --draft \
  --title "Infra dependency resources — 2026-10-09" \
  --notes-file RELEASE.md

gh release upload infra-resources-2026-10-09 \
  --repo tersemind/resources \
  dist/*.tar.gz \
  README.md DICTIONARIES.md RELEASE.md assets.json bundles.json \
  SHA256SUMS RELEASE_SHA256SUMS licenses/*
```

附件下载到同一目录后运行 `shasum -a 256 -c RELEASE_SHA256SUMS`。发布前检查附件完整性；启用不可变 Release 时，先上传全部附件再发布。不要把 `assets/` 或 `dist/` 加入 Git 历史。

## Bazel 接入

上传后，每个类型通过一个 `http_archive` 引入，对应 URL 和完整 SHA256 取自 `bundles.json`，不设置 `strip_prefix`。构建目标使用包内相对文件路径；原始文件哈希仍用于审计，类型包的下载校验使用新包哈希。

这次更改了发布形式：原来的 `http_file` 地址不能直接替换为类型压缩包地址。应调整对应 BUILD 标签及脚本输入；PDF 类型还需展开包中原有 Adobe 压缩包，保留各自原始前缀和生成流程。char/POS 的具体配置见 [DICTIONARIES.md](DICTIONARIES.md)。当前先准备附件，上传后再切换 infra 构建。

许可及来源说明见 [licenses/NOTICES.md](licenses/NOTICES.md)，不同资源保留各自条款。MSR 语料的条款记录见 [msr-corpus-terms.md](licenses/msr-corpus-terms.md)。

## 范围

本批不保存生成的词典或 PDF Rust 表，未归档 `bazel_dep` 的传递依赖、Cargo crate 包、前端 npm 包及本机构建工具，因此还不是完整离线构建包。
