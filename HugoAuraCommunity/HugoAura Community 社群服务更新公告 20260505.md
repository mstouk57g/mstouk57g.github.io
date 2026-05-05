HugoAua Community 社群服务更新公告 (20260505)

各位同学，下午好。

HugoAura Community 相关服务现在均已恢复正常。

同时，这些服务中有一些新的变动。

<img width="10760" height="3564" alt="IMG_3901" src="https://github.com/user-attachments/assets/a15c92e6-b1c8-4383-9818-c3f4bcfda971" />

## 服务运营方面更变与多节点并存

CheckIn 从 2026 年 4 月 25 日开始和希夭管家一齐归到 mstouk57g 侧管理（这个事情好像说过了）

以及，由于（学校的）机房近期所出现的各类安全事件，我完全有理由怀疑学校领导开始严查那个地方。因此，HugoAura 服务继续放置在那里我认为这是对所有同学的不负责任

因此，我于本星期（以日曜日为一星期第一日）将 HugoAura 位于（我所在的学校的）机房的所有服务迁移至我家的一台设备中。所有服务将会拥有 IPv6 公网直接访问，相对于之前将会方便。

同时，CheckIn 服务地址将由先前宣告的 4 个地址变化为以下值：

- 节点一（Cloudflare代理的IPv6源站直接访问）: https://micf-hgck.colchicum.moe/checkIn
- 节点二（Cloudflre Argo Tunnel）: https://agcf-hgck.colchicum.moe/checkIn
- 节点三（LocyanFrp实现公网访问，贼慢）: https://lcfp-hgck.colchicum.moe
- 中转用短链（基于Cloudflare）: https://c.colchicum.moe

另外请注意，先前宣告的所有地址中，包括但不限于下列地址**全部失效**

- 原地址: https://checkin.aurax.tianmiao.fun/checkIn/exam/
- 原地址: https://checkin.hugoaura.tianmiao.fun/checkIn/exam/
- 原短链地址: https://t.tianmiao.fun/checkIn

全部失效指，在本公告发布之后，除非再次声明。即使上述网站仍能访问，仍能答题，所产生的结果将**不被**群机器人所查询和认可，群管理员也**不接受**这些位置的从本公告发布之日后的成绩

另外，新的节点除节点三外（那个太慢了我看不下去）均使用了 Cloudflare 作为代理，请确保答题时网络环境**可以正常访问 Cloudflare**。若不可以请尝试科学上网或联系 mstouk57g&Creeper_awa 获取可以直接连接服务器的答题通道

同时，请注意避免答题答了一半后更换节点的操作，这可能导致您原先的答题结果无效需要重新生成试题。衷心建议一口气把题答完不要答一半跑了。

## 第三方登录临时不可用公告

由于运营方面更换，地址全部更换。之前注册的所有 OAuth 应用程式中，STCN 登录由于暂时不能修改相关应用程式信息，暂时不可使用。

Github 登录由于原先的 OAuth 应用程式属于 TianMiao 而非 HugoAura，因此从本公告发布之日起，将使用隶属于HugoAura 的新 GitHub OAuth 应用。这也意味着，之前的授权将会全部失效，不过重新授权后还可以正常登录到先前绑定的账户中。


另外，由于 GitHub 不能配置多个回源地址，因此在统一回源地址上线之前，Github登录将**仅支持**节点 https://agcf-hgck.colchicum.moe （节点二，这个好像最稳定）。

因此若需要使用 Github 登录 / 授权，请手动访问节点二的地址而不是使用短链跳转。使用其它节点进行授权可能会因为Cookie 不一致而出现一些奇奇怪怪的问题。

本次更改除了登录方面之外并无实质性影响，因为强制第三方账户绑定生成试题已经被关闭。

## 服务状态展示与服务节点优选

短链地址: https://c.colchicum.moe

该地址从本公告发布之日起，在访问后会自动尝试连接群机器人和 CheckIn 服务以确保服务均可用（两个过程并行完成，至于为什么需要检测机器人后续会说），并在确保机器人可用后在收到第一个 CheckIn 检测响应后跳转到对应地址（即自动跳转至测速最快的 CheckIn 服务地址）。

若存在机器人不可用或不存在任意一个可以使用的 CheckIn 服务，短链将会自动跳转到后面所说的服务状态展示地址。

请注意，本功能并不完全准确。虽然短链可能会把你带到状态页上并说明服务不可用，但是你仍然可以通过点击状态页上的地址或直接访问 CheckIn 服务来进入 CheckIn 站点。请相信你自己的结果是最准确的，而不是状态展示页。

状态展示地址: https://c.colchicum.moe/status

访问后将会自动尝试连接机器人和进行所有的 CheckIn 站点测速，并告知结果

点击任意一 CheckIn 服务卡片可以直接跳转到对应的地址。

推荐访问地址（节点二，这个好像最稳定）：https://agcf-hgck.colchicum.moe/checkIn

<img width="10000" height="5676" alt="IMG_3900" src="https://github.com/user-attachments/assets/23b9fd28-fc22-455a-8177-1e94ca0acf4b" />

## 试题生成策略更变

由于多次出现部分用户使用非自己的 QQ 号多次答题撞题库，因此@Creeper_awa为 HugoAura 所使用的 CheckIn 答题系统增加了 QQ 号验证功能。如果你填写的 QQ 号不在 STCN 群或用户群中，则需要根据网页引导，完成验证过程后才可生成试题答题。

具体步骤可以参照下方海报

<img width="10000" height="5676" alt="IMG_3781" src="https://github.com/user-attachments/assets/e426ee62-e73a-4c19-9bfc-5af2fd7eec09" />

另外，请各位管理员注意。由于该试题生成策略需要在答题之前发送入群申请。为防止管理员误操作导致不该放进来的人被放进来，本公告发布之后，除 HugoAura Member（即群聊「雨光之环中央指挥部」的管理员）之外的所有管理员将会被吊销接受入群申请的资格。造成不便，还请理解

该策略并不会立马生效，在权限吊销之前，请不要对任何「雨光之环用户交流群」的入群申请进行批准或拒绝操作。

本次更新内容公告结束，如有任何问题可以找任意一 HugoAura Member 进行询问。

<p align="right">2026 年 5 月 5 日</p>

<p align="right">HugoAura Devs</p>
