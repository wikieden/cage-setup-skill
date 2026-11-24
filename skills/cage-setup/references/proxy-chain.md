# 配置 Cage 链式代理

## 先还原目标

把请求写成一条有方向的链，例如「Cage → 香港前置 → 美国住宅出口 → 目标网站」。记录目标出口 IP 或用户选择的地区策略。区分“仅新增备用”和“立即设为默认”。前置的 IP 可以变化，固定出口取决于最后一跳。Clash 的代理组和 provider 别名需要解析到具体节点；“添加中转”表示增加串联的一跳。

读取 `proxy.status`、`settings.get`、`status`、`terminals.get`。保留当前 route 的有序 ID、选中出口、原 IP 策略、网络暂停状态和正在执行的作业，以便回退。0.1.8 和 0.2.0 的导入操作都可能重新应用当前代理：即使只加节点，也可能中断网络。涉及活跃终端时沿用用户已有的中断授权，否则先在隔离实例验证候选，将导入安排在允许中断的时间。

## 导入并应用

只读取用户指定的订阅或配置，提取本次涉及的实际节点。使用现有 Clash/Mihomo YAML 的 `proxies` 或该版支持的 `payload`。内联链路可让出口的 `dialer-proxy` 指向同一导入文件内具体前置的唯一名称；跨已导入来源时使用显式 ID 链。Cage 0.2.0 拒绝以宿主回环监听端口作为新节点，此时使用真实前置及出口，通过原生接口应用。

1. 核对本版 `proxy.import` 输入。以下示例将已筛好的私有 YAML 直接送入 CLI，不在终端展示节点参数；上游输出可能含订阅和节点资料，仅打印状态与作业 ID。

   ```sh
   python3 -c 'import json,sys; from pathlib import Path; print(json.dumps({"name":sys.argv[1],"content":Path(sys.argv[2]).read_text()}))' \
     "$SOURCE_NAME" "$PRIVATE_YAML" | \
     "$CAGE" agent call proxy.import --input - --wait 2m | \
     jq '{status,job:.data.id,error:.error.code}'
   ```

2. 再读 `proxy.status`，按来源、名称和协议唯一解析节点 ID，检查跳过项。已存在且配置相同的来源直接复用。仅新增时到此保留原 route；要求启用时才执行下一步。
3. 明确按“第一跳 → 最终出口”传 ID。应用后读回整个 route，而非只看选中节点的显示名。

   ```sh
   jq -n --arg front "$FRONT_ID" --arg exit_id "$EXIT_ID" \
     '{node_ids:[$front,$exit_id]}' | \
     "$CAGE" agent call proxy.route --input - --wait 2m | \
     jq '{status,job:.data.id,error:.error.code}'
   ```

4. 用原生“验证出口”或该版本的探测操作获取真实出口。需要固定 IP 时核对 `settings.get.exit_policy` 中的模式和 IP，修改策略前读取本版 schema 并使用支持的预检。对主线和备用分别采样；Cage 开放业务网络后，用入口文档里的脚本检查当前实例。备用线路只在独立 Mihomo 实例中测过时，注明测试层级。

## 作业失败与回退

- `account_locked`：让用户在应用内解锁。等待期间可以离线筛选用户已指定的来源。
- `job_failed`：先读回 sources、route、VM 和 gate。节点已写入但网络待重启时，跳过重复导入；核对中断授权后用 `environment.stop/start` 恢复。作业冲突时等待正在运行的原作业。
- 实测 IP 不符或关键检查失败时保留关网保护。检查前置、出口和绑定策略。切换未成功且已有原工作链时，按记录的 ID 恢复原 route 与原策略并复测；若新版本拒绝旧链，报告具体阻塞。
- 代理可用与客机浏览器就绪分别检查。只有确实遇到旧版虚拟 Mac 浏览器服务断连时才排查对应客机服务。

## 用户要求自动故障切换时

先检查当前版本能否原生表示多个备选前置。需要外部监控时，只管理用户指定的链。按完整的“候选前置 → 同一最终出口”做小流量 HTTPS 测试；固定 IP 必须与预期值相等。可采用连续两轮失败作为切换阈值，倍率线路按用户偏好排序。切换前重新核对 route、手动暂停、在途作业和候选新鲜度，使用 `proxy.route` 只替换前置 ID。用户手动换出口后停止干预。持续后台运行及重启客机应符合本次授权。

分别验证判定逻辑、隔离实例实际断开第一跳后接续的出口、以及生产 Cage 的实测出口。记录做过哪一级测试。最终出口本身失效时保留固定 IP 约束。[上游网络说明](https://github.com/Lee-xeo/Claude-Cage/blob/main/docs/guide/network.md)
