# Cloudflare DNS 优选节点自动化同步系统 - 核心备份文档

这是一份防遗忘的备忘录。用于记录当前 GitHub Actions 自动更新域名的对应关系与数据来源接口。

## 🎯 核心项目信息

- **GitHub 仓库地址**: [worldneedme/cf-mdl](https://github.com/worldneedme/cf-mdl)
- **本地项目路径**: `D:\code\projects\cf-mdl`
- **执行逻辑文件**: `dnscf.py`
- **定时任务触发**: 依靠 `.github/workflows/dns_cf.yml` (配置为每 6 小时自动运行一次 `0 */6 * * *`)
- **部署时间**: 2026年6月17日

---

## 🔗 域名与 API 对应关系 (全网通用配置)

本项目采用双路并行更新机制，每次定时任务触发时，会自动更新以下两个解析记录：

### 1. 域名 `md1.020021.qzz.io`
- **调用 API**: `https://ipdb.api.030101.xyz/?type=bestcf&country=true`
- **获取规则**: 从此 API 中获取全部 10 个纯净 IP 地址（全球优选最优存活）。
- **同步动作**: 清空旧的 `md1` A记录，并自动创建这 10 个新的 A记录负载均衡。

### 2. 域名 `md2.020021.qzz.io`
- **调用 API**: `https://addressesapi.090227.xyz/CloudFlareYes`
- **获取规则**: 从此 API 中获取全部 14 个 IP 地址（无视运营商后缀标签，全盘接收）。
- **同步动作**: 清空旧的 `md2` A记录，并自动创建这 14 个新的 A记录负载均衡。

---

## 🔑 所需的密钥依赖 (GitHub Secrets)

脚本的成功运行依赖于配置在 GitHub 仓库后台 (`Settings -> Secrets and variables -> Actions`) 的以下环境变量：

| Secret 名称 | 作用说明 |
|---|---|
| **CF_API_TOKEN** | Cloudflare 操作授权令牌 (API Token) |
| **CF_ZONE_ID** | Cloudflare 域名站点的唯一防伪码 (Zone ID) |
| **CF_DNS_NAME** | *(旧版预留)*，由于代码已写死 md1 和 md2，此变量当前实际上未被强制调用 |

> **💡 温馨提示：**
> 如果以后您更换了 Cloudflare 的账号或者域名，务必要记得去 GitHub 后台更新 `CF_API_TOKEN` 和 `CF_ZONE_ID` 才能让自动化脚本继续生效！
