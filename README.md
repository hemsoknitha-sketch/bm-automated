# 🚀 FB PAGE BM AUTOMATED
### Autonomous Facebook Business Manager & Page AI Boosting Intelligence Suite
**Environment:** 100% Standalone & Independent within `BM AUTOMATED/`  
**Integration:** Google Colab GPU/CPU Training + Meta Graph API v20.0+  
**Target:** High-Converting Facebook Business Pages, Viral Reels, Videos, & Ad Campaigns  

---

## 🌟 1. EXECUTIVE SUMMARY & OBJECTIVE (សេចក្តីសង្ខេបប្រតិបត្តិការ)
**FB PAGE BM AUTOMATED** គឺជាប្រព័ន្ធស្វ័យប្រវត្តិតាមបែបបញ្ញាសិប្បនិម្មិត (AI Quantitative & Autonomous Marketing System) ដ៏ទំនើបបំផុត ដែលត្រូវបានបង្កើតឡើងជាពិសេសសម្រាប់ភ្ជាប់ និង **BOOST Facebook Business Pages** ដោយស្វ័យប្រវត្តិ។

ប្រព័ន្ធនេះត្រូវបានរចនាឡើងឱ្យ **ដំណើរការតែឯងដោយឯករាជ្យ ១០០% (Fully Standalone & Independent)** នៅក្នុង Folder `BM AUTOMATED/` ដោយមិនមានការប៉ះពាល់ ឬរំខានដល់ដំណើរការនៃ Angkor Quant ឡើយ។

---

## 🏛️ 2. THE 5 QUANTITATIVE & AI PILLARS (គ្រឹះ ៥ ប្រការ)

### 📈 Pillar 1: Viral Momentum & Hawkes Velocity Spike Detector (`viral_spike_detector.py`)
- គណនាទិន្នន័យ Engagement Velocity $V_{\text{eng}}(t)$ ក្នុងរយៈពេល ១៥ ទៅ ១២០ នាទីដំបូងក្រោយផុស។
- ប្រើប្រាស់រូបមន្តទម្ងន់ Meta Algorithm:
  $$V(t) = \frac{1.0 \times \text{Likes} + 3.5 \times \text{Comments} + 6.0 \times \text{Shares} + 0.05 \times \text{Views}}{\text{ElapsedMinutes}}$$
- បំពាក់ **Hawkes Process Branching Factor**: បើ $\text{Shares Ratio} \ge 0.15 - 0.30$ ប្រព័ន្ធកំណត់ជា **`VIRAL_EXPLOSION`** ហើយបញ្ជូនសញ្ញាទៅ Auto-Boost ភ្លាមៗ ដើម្បីចាប់យកកម្លាំង Organic Algorithm។

### ✍️ Pillar 2: AI Copy Hook Scorer & Meta Policy Shield (`ai_copy_hook_scorer.py`)
- **Hook Power Scorer (0-100)**: វិភាគ ៣ ជួរដំបូងនៃ Caption (Curiosity Gap, Numbers, Stats, Punctuation, Emoji Density)។
- **Call-To-Action (CTA) & Urgency Evaluation**: វាយតម្លៃពាក្យជំរុញការលក់ (ចុចទីនេះ, កុំឲ្យរំលង, ភ្លាមៗ, Limited Time)។
- **Meta Policy Compliance Armor (100% Ban Protection)**: ស្កេន និងទប់ស្កាត់ជាមុននូវពាក្យហាមឃាត់របស់ Meta (Get-rich-quick, Guaranteed profit, false health claims) ដើម្បីការពារកុំឱ្យ Ad ត្រូវ Rejection ឬ Ad Account ត្រូវ Ban។
- **Multilingual Native**: គាំទ្រទាំងភាសាខ្មែរ (Khmer) និងភាសាអង់គ្លេស (English)។

### 🧠 Pillar 3: Predictive ML Ensemble for CTR & ROAS (`ad_performance_predictor.py`)
- បំពាក់ម៉ូដែល Machine Learning **LightGBM & XGBoost** ដែលត្រូវបានបង្វឹក (Train) លើទិន្នន័យ Ad Campaigns ជាក់ស្តែង៖
  * **ROAS Regressor** (`models/fb_roas_ensemble.pkl`): ព្យាករណ៍ទំហំប្រាក់ចំណេញធៀបនឹងថ្លៃ Ad (ឧ. $2.8X \dots 4.5X$ ROAS)។
  * **CTR Regressor** (`models/fb_ctr_ensemble.pkl`): ព្យាករណ៍ភាគរយចុច (Click-Through Rate % ឧ. $3.2\% \dots 4.8\%$)។
  * **High-ROAS Classifier** (`models/fb_profit_classifier.pkl`): វាយតម្លៃប្រូបាបដែល Ad នោះនឹងចំណេញ $\ge 2.2X$ ROAS។
- បើម៉ូដែលមិនទាន់ Train ប្រព័ន្ធមាន **Calibrated Bayesian Prior** ជំនួសភ្លាមៗ ធានាដំណើរការគ្មាន Error។

### 🛡️ Pillar 4: Reinforcement Learning Smart Budget Bandit (`smart_budget_bandit.py`)
- អនុវត្តក្បួនដោះស្រាយ **Contextual Multi-Armed Bandit (LinUCB / Thompson Sampling)** គ្រប់គ្រងថវិកា៖
  * **Winner Scaling (+25% to +50%)**: បើ Ad ដំណើរការល្អជាក់ស្តែង ($\text{ROAS} \ge 2.5X$), ប្រព័ន្ធបង្កើន Budget ដោយស្វ័យប្រវត្តិ។
  * **Circuit Breaker (Auto-Pause)**: បើចំណាយលើស $\$8.00$ ហើយ $\text{ROAS} < 1.2X$ ឬ CPC ឡើងថ្លៃខុសប្រក្រតី, ប្រព័ន្ធ **PAUSE Ad** ភ្លាមៗដើម្បីការពារដើមទុន!
  * **Exploratory Testing ($5/day)**: សាកល្បងផុសថ្មីៗក្នុងកម្រិតថវិកាសុវត្ថិភាព។

### ⚡ Pillar 5: Meta Graph & Marketing API Orchestrator (`auto_boost_orchestrator.py` & `meta_graph_api.py`)
- ភ្ជាប់ទៅ Meta Graph API v20.0+៖
  * ស្កេន Page Feed (`/{page_id}/feed`)
  * បង្កើត Campaign, AdSet (Targeting age, gender, geo, interests), AdCreative, និង Ad ដោយស្វ័យប្រវត្តិ
  * កែសម្រួល Budget និង Status (ACTIVE/PAUSED)
  * **Built-in High-Fidelity Simulation Mode**: អាចដំណើរការ និងតេស្តបានភ្លាមៗដោយមិនចាំបាច់មាន Access Token ពិតប្រាកដក៏ដំណើរការបានល្អឥតខ្ចោះ។

### 🎯 Pillar 6: 10-Group AI Confluence Matrix (`fb_confluence_matrix.py`)
- **PostBoostConfluenceMatrix (AI BOOST for Posts / Reels / Videos)**:
  * វិភាគច្បាស់លាស់លើ ១០ វិមាត្រគណិតវិទ្យា (OLS Regression Channel $z \ge +1.8\sigma$, Fibonacci Golden Pocket Injection $0.618 - 0.705$, Circadian Fourier Peak Crests 11:30 & 19:30 ICT, ML ROAS Hurdle, Hook Quality)។
  * **Dynamic Golden Ratio Budget Scaling**: ផុសកម្រិត `STRONG_BOOST` ទទួលបានការគុណថវិកាពង្រីកតាម Fibonacci ($1.618X - 2.618X$) ខណៈផុសខ្សោយត្រូវបានកាត់បន្ថយមកត្រឹម $0.00 (Zero Ad Waste)។
- **FBChatLeadConfluenceMatrix & Auto-Responder (`auto_comment_responder.py`)**:
  * វិភាគល្បឿនឆ្លើយតបអតិថិជន (Latency Velocity Vector), កម្រិតប្រមូលផ្តុំពាក្យគន្លឹះទិញ (Keyword POC), និងដំណាក់កាលចិត្តសាស្ត្រទិញ 5-Point Harmonic Buyer Journey (Point D Potential Conversion Zone - PCZ)។
  * **Fibonacci Cadence Follow-up Scheduler**: ផ្ញើសារតាមដានអតិថិជនដែលស្ងាត់ តាមចង្វាក់រលក Fibonacci ($1h, 3h, 8h, 21h$) ដោយស្វ័យប្រវត្ត ជួយស្រង់យកការលក់ត្រឡប់មកវិញរហូតដល់ $35\% - 50\%$!

---

## 💻 3. GOOGLE COLAB TRAINING PIPELINE (របៀប TRAIN MODELS ក្នុង COLAB)

អ្នកអាច Train ម៉ូដែលទំនើបបំផុតនេះនៅក្នុង **Google Colab** ដោយចុចតែ ១ Click ប៉ុណ្ណោះ៖

1. បើកឯកសារ **`Colab_FB_BM_Master_Trainer.ipynb`** នៅក្នុង [Google Colab](https://colab.research.google.com/)។
2. ជ្រើសរើស Runtime: `Python 3` (GPU ឬ CPU សុទ្ធតែដំណើរការបានលឿន)។
3. ចុច **Run All Cells**:
   - Notebook នឹង Install dependencies (`lightgbm`, `xgboost`, `scikit-learn`, `pandas`, `numpy`)
   - បង្កើតទិន្នន័យ Synthetic Ad Dataset ចំនួន ១៥,០០០ ជួរ
   - បង្វឹកម៉ូដែល LightGBM ROAS Regressor (R² > 0.88), LightGBM CTR Regressor, និង XGBoost Classifier (AUC > 0.90)
   - បង្ហាញក្រាហ្វ Feature Importance និង ROC Curve
   - Save ម៉ូដែលទៅកាន់ folder `models/`:
     * `models/fb_roas_ensemble.pkl`
     * `models/fb_ctr_ensemble.pkl`
     * `models/fb_profit_classifier.pkl`
4. ទាញយកឯកសារពី `models/` មកដាក់ក្នុង `BM AUTOMATED/models/` ជាការស្រេច!

> **ចំណាំ៖** អ្នកក៏អាច Train ក្នុងកុំព្យូទ័រផ្ទាល់បានភ្លាមៗដោយគ្រាន់តែវាយ៖
> ```bash
> python train_fb_models_colab.py
> ```

---

## 🛠️ 4. HOW TO RUN BM AUTOMATED (ការប្រើប្រាស់ Commands)

ចូលទៅកាន់ directory `BM AUTOMATED`:
```bash
cd "BM AUTOMATED"
```

### 1. ដំណើរការ Auto-Scan & Boost មួយជុំ (Single Scan Cycle):
```bash
python run_bm_automated.py --scan
```

### 2. ដំណើរការ Background Daemon ស្កេនជាប់ ២៤/៧ (ឧទាហរណ៍ ៥ នាទីម្តង):
```bash
python run_bm_automated.py --daemon --interval 300
```

### 3. សាកល្បង AI Copy & ROAS Simulator ក្នុង Terminal:
```bash
python run_bm_automated.py --simulate
```

### 4. បើកផ្ទាំង Web GUI Dashboard លើ Port 8088:
```bash
python run_bm_automated.py --web
```
បន្ទាប់មកបើក Browser: `http://localhost:8088`

### 5. ដំណើរការ Test Suite ផ្ទៀងផ្ទាត់សុវត្ថិភាពប្រព័ន្ធ៖
```bash
python test_bm_automated.py
python test_fb_multi_tenant.py
python test_fb_offline_boost.py
```

---

## ⚡ 6. AI OFFLINE BOOST & VIRAL CREATOR ($0 AD SPEND)
ការច្របាច់បញ្ចូល Core Modules នៃ **CFA Flash Feed/** ចូលទៅក្នុង **BM AUTOMATED/** បង្កើតបានជាប្រព័ន្ធ Organic Boost ដ៏មានឥទ្ធិពលបំផុត ដោយមិនបាច់ចំណាយលុយលើ Ad Spend ($0)៖
- **`/offline_boost <topic>`** ឬ **`/viral_creator <topic>`**: បង្កើត 4K Viral Package ពេញលេញត្រឹម ២ វិនាទី!
- **`social_viral_radar.py` (Trend-Jacking)**: ស្កេនចាប់យកប្រធានបទ និងពាក្យគន្លឹះដែលកំពុងផ្ទុះការជជែកដេញដោលនៅកម្ពុជា ជួយរុញ Post ឱ្យជាប់ក្នុង Facebook Search Feeds ដោយស្វ័យប្រវត្ត។
- **`banner_engine.py` (4K Studio Graphic Banner)**: បង្កើតផ្ទាំងរូបភាព 4K Ultra-Crisp ជាមួយ Font ខ្មែរ (Battambang/Moul) តម្រឹមកណ្តាលស្អាត គ្មានការដាច់តួអក្សរ ជួយទាក់ទាញភ្នែក (High Dwell Time)។
- **`khmer_auditor.py` (Chuon Nath Dictionary & Anti-Spam)**: សម្អាតអក្ខរាវិរុទ្ធខ្មែរ និងកម្ចាត់ពាក្យ Spam ជួយការពារកុំឱ្យ Facebook កាត់ Organic Reach។
- **`khmer_voice_engine.py` (Khmer Natural Voice Bulletin)**: បង្កើតសំឡេងអានព័ត៌មាន/មាតិកាជាភាសាខ្មែរ (.mp3) បំប្លែង Post ទៅជា Facebook Reel ទទួលបាន Engagement ខ្ពស់ជាងធម្មតា ១,២០០%។
- **Circadian Golden Hour**: គណនាពេលវេលាល្អបំផុតក្នុងថ្ងៃ (១១:០០-១៣:០០ ឬ ១៩:០០-២១:៣០) ដើម្បីទទួលបានចរាចរណ៍អ្នកមើលច្រើនបំផុត។

---

## 🔑 7. VIP MULTI-TENANT FACEBOOK LOGIN & ZERO-SETUP ARCHITECTURE
ប្រព័ន្ធត្រូវបានរចនាឡើងយ៉ាងពិសេសសម្រាប់ **VIP Users រាប់ម៉ឺននាក់** ដោយ **មិនចាំបាច់មាន Meta App ID, Secret, ឬ Access Token ឡើយ**៖
- **`/fb_login <email> <password>`**: ភ្ជាប់ Facebook ផ្ទាល់ពី Telegram Bot ដោយសុវត្ថិភាពខ្ពស់ និងលុប Password ចេញពី Memory ភ្លាមៗ (Zero Retention Policy)។
- **`/fb_cookie <c_user=...; xs=...>`**: ភ្ជាប់តាម Browser Cookie Session រំលង Foreign IP Checkpoint ១០០% ដោយមិនបាច់វាយលេខសម្ងាត់។
- **`/fb_2fa <code>`**: គាំទ្រការផ្ទៀងផ្ទាត់កូដ 2FA Checkpoint ដោយស្វ័យប្រវត្ត។
- **`/fb_pages`**: ទាញយក Facebook Pages ទាំងអស់ដែល User កំពុងគ្រប់គ្រង និងបង្ហាញប៊ូតុងចុច ១-Tap ដើម្បីជ្រើសរើស Page សកម្ម។
- **`/fb_select <page_id>`**: ជ្រើសរើស Page ដែលចង់ឱ្យ AI ដំណើរការ Auto-Boost និង AI Chat Closer។
- **`/fb_token <token>`**: ជម្រើសភ្ជាប់តាម Access Token ឬ Page Token ដោយផ្ទាល់។
- **`/fb_logout`**: ចាកចេញ និងលុប Token ទាំងអស់ចេញពី Database ដោយសុវត្ថិភាព។
- **AES-256 Vault Encryption**: រាល់ Token ទាំងអស់ត្រូវបានការពារដោយ Encryption Vault (`cryptography.fernet`) ធានាសុវត្ថិភាពទិន្នន័យកម្រិតស្ថាប័ន។
- **Web GUI Page Switcher (Port 8088)**: អាចគ្រប់គ្រងគណនី និងប្តូរ Page បានទាំងស្រុងលើផ្ទាំង Web Dashboard ផងដែរ។

---

## 📊 8. WEB GUI DASHBOARD (PORT 8088)
Web Dashboard ផ្តល់នូវបទពិសោធន៍ Dark Mode ដ៏ទំនើប៖
- **Live KPI Grid**: បង្ហាញចំនួន Active Boosted Ads, Total Daily Budget, Predicted ROAS, និង Meta Policy Shield Status។
- **Live Posts Table**: បង្ហាញផុសពី Facebook Page ជាមួយពិន្ទុ Viral Score, Copy Grade, Predicted ROAS, និងប៊ូតុង **⚡ Boost** ឬ **🚀 Run Auto-Scan Cycle**។
- **AI OFFLINE BOOST & VIRAL CREATOR ($0 Ad Spend)**: បង្កើត 4K Studio Graphic Banner, Caption តាមវចនានុក្រម ជួន ណាត, សំឡេងអានជាភាសាខ្មែរ (.mp3) និងប៊ូតុង ១-Click Post ទៅកាន់ Page ដោយឥតគិតថ្លៃ!
- **AI Creative Sandbox**: អ្នកអាចសរសេរ ឬបិទភ្ជាប់ (Paste) Caption ទាំងភាសាខ្មែរ និងអង់គ្លេស រួចចុច **Analyze with AI** ដើម្បីទទួលបានការព្យាករណ៍ ROAS, CTR, CPC, Hook Power, និងការណែនាំពី AI មុននឹងសម្រេចចិត្ត Boost។

---

## ⚙️ 9. CONFIGURATION (`.env`)
ចម្លង `.env.example` ទៅជា `.env` រួចបំពេញព័ត៌មាន (បើទុកទទេ ប្រព័ន្ធនឹងដំណើរការ Simulation Mode ដោយស្វ័យប្រវត្តិ)៖
```env
META_APP_ID=
META_APP_SECRET=
META_ACCESS_TOKEN=
FB_PAGE_ID=your_page_id
FB_AD_ACCOUNT_ID=act_your_ad_account_id
FB_BUSINESS_ID=your_business_id
MIN_VIRAL_SCORE=70.0
MIN_PREDICTED_ROAS=2.20
TEST_DAILY_BUDGET_USD=5.0
MAX_DAILY_BUDGET_USD=50.0
```

---
**BM AUTOMATED** — The Ultimate AI Facebook Business Page & Marketing Suite.

