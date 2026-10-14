# AI-Mediated Personal Infrastructure (AMPI)

**Omica Chow · Version 0.1 · Concept note / position statement · Not peer reviewed**

**Version 0.1 release copy.** Prepared on 14 October 2026. The draft date is distinct from public publication. Verified release timestamps and identifiers are recorded in the version history and citation metadata. No DOI has been assigned.

Public repository: [omicachow/AI-Mediated-Personal-Infrastructure](https://github.com/omicachow/AI-Mediated-Personal-Infrastructure).

The future personal computing environment may be an AI coordination layer over existing software. AMPI organizes specialized tools around a person's goals through semantic interpretation, tool invocation, persistent state, and verifiable execution. Conventional components preserve evidence and artifacts, enforce scoped authority, and support recovery. AI should know which existing system should do the work; it need not perform every step itself.

- [Read the concept note](paper/AMPI-v0.1.md)
- [Read the PDF](paper/AMPI-v0.1.pdf)
- [View the original reference architecture](assets/architecture.svg)
- [Citation metadata](CITATION.cff), [CSL-JSON](citation/AMPI-v0.1.csl.json), and [BibTeX](citation/AMPI-v0.1.bib)
- [Version history](CHANGELOG.md) and [file checksums](SHA256SUMS)

AcademicWorkspace is a private implementation-informed case. This document repository contains a sanitized conceptual account and original publication materials. It contains no private engineering source, course materials, operational records, or personal messages. The contribution is the author's specific synthesis, design choices, implementation and use, and explicit formulation. Related work is cited; general effectiveness and historical priority are not established.

## 中文入口

**AMPI：AI 中介式个人基础设施。** 核心是保留现有软件各自的专业能力，让 AI 判断资料的含义以及哪些事情交给哪个系统完成；由常规程序维护持久状态、授权执行、结果校验和恢复。个人任务与真实成果跨越软件边界持续存在。GUI Agent 是可选通道，直接接口和现有命令可优先复用。

正文为英文，附有实质内容的中文摘要，并专节讨论与 OS-level GUI Agents（含豆包手机助手官方说明）的关系。AcademicWorkspace 案例已脱敏。稿件性质是未经同行评议的概念说明。真实公开时间与永久标识以版本记录和引用元数据为准；2026-10-14 是草稿日期，不能据此倒签发表时间。

## Citation and reuse

Cite the concept note using `preferred-citation` in `CITATION.cff` or the supplied CSL-JSON/BibTeX, rather than classifying the private implementation as published software or the note as a journal article. Publication dates and permanent identifiers are recorded only after verification. The immutable release files remain the reference copy; later verified identifiers may be added to the repository citation metadata without changing those files.

Original materials are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), with the author's approval. See [LICENSE](LICENSE) for scope. Referenced third-party works retain their own rights; no private AcademicWorkspace code is licensed by this package.

## Rebuild the PDF

The Markdown manuscript is the sole text source. The original SVG is the editable figure source. With Python 3.12 and the dependencies in [requirements-build.txt](requirements-build.txt), run:

```text
python scripts/build.py
```

The build reads the manuscript and local SVG only. It does not access AcademicWorkspace, log into a service, or publish anything. Fonts are supplied by the build machine and embedded in the PDF; no font binaries are distributed here. The tested Windows build uses Georgia, Calibri, Microsoft YaHei, and the SVG renderer's Arial fallback from the operating system. On another machine, supply licensed fonts through `AMPI_SERIF`, `AMPI_SERIF_BOLD`, `AMPI_SERIF_ITALIC`, `AMPI_SANS`, `AMPI_SANS_BOLD`, and `AMPI_CJK`; verify the SVG renderer's font substitution as well. A rebuild may produce different bytes with different fonts or a different build timestamp; compare the release's recorded SHA256 for file identity.

The build also regenerates citation files from the manuscript front matter. For citation after publication, retain the supplied metadata or restore verified publication fields from the public record. A PDF rebuild does not create a new publication.
