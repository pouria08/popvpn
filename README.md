<div dir="rtl" align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=180&color=0:0f172a,50:7c3aed,100:06b6d4&text=POPVPN&fontColor=ffffff&fontSize=58&fontAlignY=38&desc=Smart%20VPN%20Subscription%20Pipeline&descAlignY=63&descSize=18&animation=fadeIn" width="100%" alt="POPVPN" />

# ⚡ POPVPN

### 🚀 جمع‌آوری، پاک‌سازی، دسته‌بندی و انتشار خودکار Subscription های VPN

<p>
<img src="https://img.shields.io/badge/AUTO--UPDATE-EVERY%20HOUR-7c3aed?style=for-the-badge&logo=githubactions&logoColor=white" alt="Auto Update" />
<img src="https://img.shields.io/badge/HIDDIFY-COMPATIBLE-06b6d4?style=for-the-badge" alt="Hiddify" />
<img src="https://img.shields.io/badge/VLESS-READY-8b5cf6?style=for-the-badge" alt="VLESS" />
<img src="https://img.shields.io/badge/VMESS-READY-3b82f6?style=for-the-badge" alt="VMess" />
<img src="https://img.shields.io/badge/TROJAN-READY-f97316?style=for-the-badge" alt="Trojan" />
<img src="https://img.shields.io/badge/SHADOWSOCKS-READY-22c55e?style=for-the-badge" alt="Shadowsocks" />
</p>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=900&color=7C3AED&center=true&vCenter=true&width=900&lines=POPVPN+%E2%80%94+Auto+Updated+Every+Hour;VLESS+%7C+VMess+%7C+Trojan+%7C+Shadowsocks;Hiddify+Friendly+Subscription;Clean+%7C+Deduplicated+%7C+Ready+to+Use" alt="POPVPN animated text" />

<br />

**یک Pipeline سبک و خودکار برای تبدیل چندین منبع Subscription به خروجی‌های تمیز، دسته‌بندی‌شده و آماده استفاده در کلاینت‌های VPN.**

<br />

[📥 Subscription کامل](https://raw.githubusercontent.com/pouria08/popvpn/main/base64.txt) • [📊 آمار](https://raw.githubusercontent.com/pouria08/popvpn/main/stats.txt) • [⚙️ Actions](https://github.com/pouria08/popvpn/actions) • [📂 Outputs](https://github.com/pouria08/popvpn/tree/main/outputs)

</div>

---

## ✨ درباره POPVPN

POPVPN منابع تعریف‌شده در `links.txt` را به‌صورت خودکار دریافت می‌کند، محتوای Plain/Base64 را تشخیص می‌دهد، HTML Entity های خراب مانند `&amp;` را اصلاح می‌کند، کانفیگ‌های تکراری را حذف می‌کند و خروجی‌های استاندارد برای VLESS، VMess، Trojan و Shadowsocks می‌سازد.

فرآیند آپدیت توسط **GitHub Actions** به‌صورت خودکار هر ساعت اجرا می‌شود و در صورت تغییر خروجی‌ها، Commit جدید ایجاد می‌کند.

### 💎 قابلیت‌ها

| قابلیت | وضعیت |
|---|:---:|
| 🔄 آپدیت خودکار ساعتی | ✅ |
| 🧹 حذف کانفیگ‌های تکراری | ✅ |
| 🧼 اصلاح HTML Entity مثل `&amp;` | ✅ |
| 🗂 تفکیک VLESS / VMess / Trojan / SS | ✅ |
| 🔐 خروجی Base64 | ✅ |
| 📄 خروجی Plain Text | ✅ |
| 📊 فایل آمار | ✅ |
| 🟦 سازگاری با Hiddify | ✅ |
| ♾️ نمایش حجم نامحدود | ✅ |
| ♾️ نمایش زمان نامحدود | ✅ |
| 🏷️ برند POPVPN در Subscription | ✅ |
| 🤖 GitHub Actions | ✅ |

---

# 🔥 لینک‌های آماده Subscription

> **برای Hiddify و اکثر کلاینت‌ها، پیشنهاد اصلی POPVPN نسخه `base64.txt` است.**

## 🏆 Subscription کامل — Base64

```text
https://raw.githubusercontent.com/pouria08/popvpn/main/base64.txt
```

👉 [افزودن Subscription کامل به کلاینت](https://raw.githubusercontent.com/pouria08/popvpn/main/base64.txt)

## 📄 Subscription کامل — Plain Text

```text
https://raw.githubusercontent.com/pouria08/popvpn/main/working_configs.txt
```

👉 [مشاهده Subscription کامل](https://raw.githubusercontent.com/pouria08/popvpn/main/working_configs.txt)

---

# 🎯 لینک‌های تفکیک‌شده بر اساس پروتکل

| پروتکل | Plain | Base64 |
|---|---|---|
| 🟣 VLESS | [`vless_configs.txt`](https://raw.githubusercontent.com/pouria08/popvpn/main/outputs/vless_configs.txt) | [`vless_base64.txt`](https://raw.githubusercontent.com/pouria08/popvpn/main/outputs/vless_base64.txt) |
| 🔵 VMess | [`vmess_configs.txt`](https://raw.githubusercontent.com/pouria08/popvpn/main/outputs/vmess_configs.txt) | [`vmess_base64.txt`](https://raw.githubusercontent.com/pouria08/popvpn/main/outputs/vmess_base64.txt) |
| 🟠 Trojan | [`trojan_configs.txt`](https://raw.githubusercontent.com/pouria08/popvpn/main/outputs/trojan_configs.txt) | [`trojan_base64.txt`](https://raw.githubusercontent.com/pouria08/popvpn/main/outputs/trojan_base64.txt) |
| 🟢 Shadowsocks | [`shadowsocks_configs.txt`](https://raw.githubusercontent.com/pouria08/popvpn/main/outputs/shadowsocks_configs.txt) | [`shadowsocks_base64.txt`](https://raw.githubusercontent.com/pouria08/popvpn/main/outputs/shadowsocks_base64.txt) |

---

# 🌐 منبع Subscription ها

## 🔎 منابع اصلی

تمام Subscription های ورودی پروژه در فایل **[`links.txt`](./links.txt)** نگهداری می‌شوند. Pipeline در هر اجرای Workflow این URLها را می‌خواند و داده‌های جدید را دریافت می‌کند.

> 📌 **نکته مهم:** این‌ها منابع ورودی POPVPN هستند؛ خروجی نهایی پس از پردازش، Deduplicate، پاک‌سازی و دسته‌بندی توسط خود POPVPN تولید می‌شود.

| # | منبع | وضعیت |
|---:|---|:---:|
| 01 | [`RKPchannel/RKP_bypass_configs`](https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/whitelist.txt) | 🟢 فعال |
| 02 | [`patterniha/Free-Configs`](https://raw.githubusercontent.com/patterniha/Free-Configs/main/configs.txt) | 🟢 فعال |
| 03 | [`pouria08/popvip`](https://raw.githubusercontent.com/pouria08/popvip/refs/heads/master/Eternity.txt) | 🟢 فعال |
| 04 | [`Javad Ghoreyshi Worker Feed`](https://9dz4quexuuos.javad-ghoreyshi11.workers.dev/feed/pouria2) | 🟢 فعال |
| 05 | [`vlessforu`](https://sub.vlessfo.ru/vlessforu/working_configs.txt) | 🟢 فعال |

### 🧩 فایل مرکزی منابع

```text
links.txt
```

هر URL که داخل این فایل قرار بگیرد، در اجرای بعدی Pipeline به‌عنوان Source دریافت می‌شود.

اگر منبعی از کار بیفتد، POPVPN آن را در آمار همان اجرا ناموفق ثبت می‌کند و در صورتی که هیچ کانفیگ جدیدی از تمام منابع دریافت نشود، خروجی قبلی را برای جلوگیری از حذف ناگهانی حفظ می‌کند.

---

# 🔄 سیستم آپدیت خودکار

Workflow اصلی در این مسیر قرار دارد:

```text
.github/workflows/update.yml
```

### ⏰ زمان‌بندی

```yaml
schedule:
  - cron: '17 * * * *'
```

یعنی Pipeline هر ساعت در دقیقه `17` اجرا می‌شود. انتخاب دقیقه غیررأس‌ساعت برای کاهش احتمال تأخیرهای ناشی از شلوغی Schedule های GitHub انجام شده است.

### ⚙️ مسیر پردازش

```text
        ⏰ GitHub Actions
                │
                ▼
        📥 Checkout Repository
                │
                ▼
          🐍 Run main.py
                │
                ▼
       🌐 Download Sources
                │
                ▼
       🧼 Decode + Clean URLs
                │
                ▼
        🧹 Remove Duplicates
                │
                ▼
        🗂 Detect Protocols
          ╱      │      ╲
       VLESS   VMess   Trojan   SS
          ╲      │      ╱
                ▼
       📄 Generate Outputs
                │
                ▼
          📊 Update Stats
                │
                ▼
          💾 Git Commit
                │
                ▼
          🚀 Ready for Users
```

---

# 🧠 پردازش هوشمند کانفیگ‌ها

### 01 — دریافت

تمام URLهای `links.txt` دریافت می‌شوند.

### 02 — Decode

اگر Source به صورت Base64 باشد، Pipeline تلاش می‌کند آن را Decode کند.

### 03 — پاک‌سازی

مواردی مانند HTML Entity های ناخواسته اصلاح می‌شوند:

```text
&amp;  →  &
```

این مرحله برای جلوگیری از خراب شدن URLهایی که در بعضی Sourceها به شکل HTML ذخیره شده‌اند اهمیت دارد.

### 04 — Deduplicate

کانفیگ‌های تکراری حذف می‌شوند تا خروجی نهایی تمیزتر باشد.

### 05 — Protocol Detection

پروتکل‌ها با Prefix خود شناسایی می‌شوند:

```text
vless://
vmess://
trojan://
ss://
shadowsocks://
```

### 06 — Naming

کانفیگ‌ها با نام برنددار و قابل تشخیص منتشر می‌شوند:

```text
POPVPN | VLESS | 1
POPVPN | VLESS | 2
POPVPN | VMESS | 1
POPVPN | TROJAN | 1
```

---

# 🟦 Hiddify

POPVPN برای Subscription Metadata مورد استفاده Hiddify نیز خروجی تولید می‌کند.

در خروجی Subscription موارد زیر درج می‌شوند:

```text
#profile-title: POPVPN
#profile-update-interval: 1
#subscription-userinfo: upload=0; download=0; total=10737418240000000; expire=2546249531
```

بنابراین در کلاینت سازگار، پروفایل با نام **POPVPN** و وضعیت حجم/زمان بدون سقف نمایش داده می‌شود.

### 📌 لینک پیشنهادی Hiddify

```text
https://raw.githubusercontent.com/pouria08/popvpn/main/base64.txt
```

> ⚠️ «نامحدود» در Metadata به معنی نمایش بدون سقف در Subscription است و محدودیت واقعی سرور، منبع یا شبکه را تغییر نمی‌دهد.

---

# 📱 راهنمای استفاده

## Android — Hiddify / v2rayNG / NekoBox

1. یکی از لینک‌های Subscription را کپی کنید.
2. در بخش Subscription برنامه وارد شوید.
3. URL را Paste کنید.
4. Update / Refresh را بزنید.
5. کانفیگ موردنظر را انتخاب کنید.

**پیشنهاد:**

```text
https://raw.githubusercontent.com/pouria08/popvpn/main/base64.txt
```

## 🪟 Windows — Hiddify / v2rayN

1. Subscription را اضافه کنید.
2. لینک بالا را وارد کنید.
3. Update را اجرا کنید.
4. کانفیگ POPVPN را انتخاب کنید.
5. Connect را بزنید.

## 🍎 iOS / iPadOS

در کلاینت‌های سازگار، لینک Subscription را در قسمت Subscribe / Subscription وارد کنید و Update را اجرا کنید.

---

# 📊 آمار آخرین اجرا

آخرین وضعیت Pipeline در فایل زیر نوشته می‌شود:

```text
https://raw.githubusercontent.com/pouria08/popvpn/main/stats.txt
```

👉 [📈 مشاهده آخرین آمار](https://raw.githubusercontent.com/pouria08/popvpn/main/stats.txt)

نمونه اطلاعات:

```text
Total Active: ...
VLESS: ...
VMESS: ...
TROJAN: ...
SHADOWSOCKS: ...
Brand: POPVPN
Traffic: Unlimited
Expiry: Unlimited
Hiddify: Compatible
```

---

# 🗂 ساختار پروژه

```text
popvpn/
│
├── .github/
│   └── workflows/
│       └── update.yml       # اجرای خودکار ساعتی
│
├── outputs/
│   ├── vless_configs.txt
│   ├── vless_base64.txt
│   ├── vmess_configs.txt
│   ├── vmess_base64.txt
│   ├── trojan_configs.txt
│   ├── trojan_base64.txt
│   ├── shadowsocks_configs.txt
│   └── shadowsocks_base64.txt
│
├── links.txt                # منابع ورودی
├── main.py                  # موتور پردازش
├── requirements.txt         # وابستگی‌های Python
├── working_configs.txt      # خروجی کامل Plain
├── base64.txt               # خروجی کامل Base64
├── stats.txt                # آخرین آمار
└── README.md
```

---

# 🛠️ اجرای محلی

```bash
git clone https://github.com/pouria08/popvpn.git
cd popvpn
pip install -r requirements.txt
python main.py
```

پس از اجرا، خروجی‌ها در Root و پوشه `outputs/` ساخته می‌شوند.

---

# 🤖 GitHub Actions

برای اجرای دستی:

1. وارد تب **Actions** شوید.
2. Workflow با نام **Auto Update Subscriptions** را انتخاب کنید.
3. روی **Run workflow** بزنید.

Workflow به‌صورت خودکار:

- Repository را دریافت می‌کند.
- Python را آماده می‌کند.
- Dependencies را نصب می‌کند.
- `main.py` را اجرا می‌کند.
- خروجی‌ها را بررسی می‌کند.
- در صورت تغییر، Commit و Push انجام می‌دهد.

---

# 🛡️ رفتار ایمن در خطا

اگر یک Source موقتاً از دسترس خارج شود، Pipeline منابع دیگر را همچنان پردازش می‌کند.

اگر **هیچ کانفیگی از تمام منابع دریافت نشود**، خروجی سالم قبلی حذف نمی‌شود تا یک قطعی موقت Source باعث خراب شدن Subscription کاربران نشود.

---

# 📜 نکات و مسئولیت استفاده

این Repository صرفاً یک Pipeline برای پردازش و انتشار داده‌های Subscription است. کاربران باید قوانین سرویس‌ها، شبکه و کشور محل استفاده خود را رعایت کنند.

منابع ورودی ممکن است در طول زمان تغییر کنند، حذف شوند یا در دسترس نباشند. POPVPN مالک یا تضمین‌کننده محتوای Source های شخص ثالث نیست.

---

<div align="center" dir="rtl">

<img src="https://capsule-render.vercel.app/api?type=rect&height=80&color=0:06b6d4,50:7c3aed,100:0f172a&text=POPVPN%20%E2%80%94%20Updated%20Every%20Hour&fontColor=ffffff&fontSize=24&animation=twinkling" width="100%" alt="POPVPN footer" />

### ⚡ POPVPN
**Clean • Fast • Automated • Hourly**

[⭐ Repository](https://github.com/pouria08/popvpn) · [⚙️ Actions](https://github.com/pouria08/popvpn/actions) · [📂 Outputs](https://github.com/pouria08/popvpn/tree/main/outputs)

</div>
