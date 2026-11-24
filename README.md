# Claude-Cage 安装配置助手

供 Codex 使用的社区技能，帮助安装或接续配置 [Claude-Cage](https://github.com/Lee-xeo/Claude-Cage)，用自己的节点建立「前置 → 最终出口」链路，并检查客机网络和实际出口 IP。

## 一句话安装并配置

在可以访问本机文件的 Codex 聊天中粘贴下面这段话，替换方括号中的内容。订阅密钥和节点密码保存在本地配置文件里即可。

> 请用 skill-installer 从 https://github.com/wikieden/cage-setup-skill 的 skills/cage-setup 目录安装 cage-setup。若已安装就复用。安装后直接读取该技能的 SKILL.md，继续检查本机 Cage，按需安装。我的 Clash/Mihomo YAML 在「[本地文件路径]」；请将「[前置节点名] → [最终出口节点名]」设为 Cage 默认链路。先保留原路由，以便失败时恢复。如需中断正在使用的终端，先告诉我。最后从运行中的客机核对链路顺序、联网检查和实际出口 IP，并报告结果。

若有固定 IP，可追加“预期出口为 [IP]，请核对是否一致”。安装后，后续对话可用 `$cage-setup` 调用。[技能说明](skills/cage-setup/SKILL.md) · [链式代理操作手册](skills/cage-setup/references/proxy-chain.md)
