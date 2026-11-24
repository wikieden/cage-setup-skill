---
name: cage-setup
description: 安装、接续配置或诊断 Lee-xeo/Claude-Cage；适用于 Cage 客机初始化、导入节点、配置前置与最终出口、固定 IP、代理故障切换及联网验收。
---

# 安装与配置 Claude-Cage

## 确认实际安装

从正在使用的 Cage 应用定位后台 CLI。macOS 检查应用包内的 `Contents/Resources/cage`，包括用户自定义安装目录；Linux 和 Windows 参照发行版安装说明。下文的 `$CAGE` 指该可执行文件的绝对路径。先读取版本、`agent capabilities` 和 `agent doctor`，核对配置路径、账户、服务、客机和当前作业。只记录本次需要的字段。CLI 或操作缺失时查同一发行标签的文档和桌面入口。

- **已有安装**：沿用原 profile、存储位置、虚拟磁盘和账户。新版本无法接管旧客机时，先说明兼容性和迁移选项，保留原数据。
- **首次安装**：确定系统和 CPU 架构，从官方 Release 获取匹配的稳定包及同标签校验清单，核对 SHA-256。macOS 在只读挂载的 DMG 中核对签名与 Gatekeeper，再安装应用。其他平台按该标签的安装说明验证签名或安装包并安装。安装后再次从实际安装目录探测 CLI。[官方发行包](https://github.com/Lee-xeo/Claude-Cage/releases) · [安装与 Agent 指南](https://github.com/Lee-xeo/Claude-Cage/blob/main/docs/guide/agent.md)

## 接续初始化

1. 真正缺少配置时运行 `agent init`；后台缺失时运行 `agent service.start`。用 `agent call account.status` 区分新建与解锁；密码在 Cage 本机界面输入。
2. 查看 `guest.options`、`storage.get` 和 `initialization.status`。首次选择本构建支持的客机和存储位置；已有环境沿用原选择。确认用户需要共享的目录后再打开项目。若网络是安装前置条件，先完成下一节中的代理配置。
3. 按能力清单调用 `environment.start`。首次安装传所选 `guest_system`，接续时复用现有配置。遇到 `accepted` 或等待超时，查询原作业 ID。用户处理许可或系统授权后，重新读取实际状态。
4. 若旧版 macOS 客机报告 macFUSE 检测失败，先看客机内两个扩展开关和只读卷的实际挂载、读取结果。挂载成功而 SSH 读取返回 `Operation not permitted` 时再查客机卷访问权限。扩大远程用户磁盘权限需要用户明确同意，记录原值，验证无效时恢复。
5. 按目标验收客机、网络与初始化。首次引导在所有条件满足时用界面或本版支持的 `initialization.set` 完成。Claude Desktop 或 Claude Code 的账号登录在客机内单独验证。

## 链式代理与验收

配置节点、切换出口、恢复失败链路或启用自动切换时，读取 [链式代理操作手册](references/proxy-chain.md)。其中包含私有文件导入、按节点 ID 应用链路、失败后的状态核对和恢复。

在本 skill 目录运行下面的只读检查。把示例名称和地址替换为本次实际目标；每个 `--hop` 按流量顺序给出。只检查环境时可省略预期值。

```sh
python3 scripts/check_cage.py --cli "$CAGE" \
  --hop '前置节点名称' --hop '最终出口名称' --expect-ip 203.0.113.10
```

脚本返回 0 表示客机运行、代理与网络门已开放、关键检查全部通过且已匹配指定目标。未提供预期值时只报告实测链路。汇报时区分已保存、已放行、已核对出口和已实测切换；仅添加候选时保留原活动链。
