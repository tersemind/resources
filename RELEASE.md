# Infra dependency resources — 2026-10-09

本批按 `assets/` 的一级类型目录发布 4 个压缩包：corpus（1 文件）、tokenizers（2 文件）、pdf（5 文件）、dictionaries（13 文件），共 21 个原始文件。包内无额外顶层包装目录。

原有 8 个 HTTP 资源保持 MODULE 校验值，13 个词典保持 infra 源目录的原始字节。原始文件校验见 `SHA256SUMS`，类型包校验见 `RELEASE_SHA256SUMS`，完整包索引与内部文件列表见 `bundles.json`。

文件用途和统一打包/更新命令见 `README.md`，char/POS 构建迁移见 `DICTIONARIES.md`。上游许可及来源记录随附，MSR 条款见 `msr-corpus-terms.md`。资源依照各自原始条款使用。

本批未归档 bazel_dep、Cargo、npm 的其他依赖。类型包 URL 在手动发布后生效，infra 构建尚未切换。
