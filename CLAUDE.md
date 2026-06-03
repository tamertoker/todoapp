# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## 5. LevelTodo Proje Kuralları

Bu bölüm yukarıdaki dört genel prensibi bu projeye (Seviye Sistemli Görev Takip Sistemi — Python + PyQt6 + lokal saklama) uyarlar.

### 5.1 İletişim (kullanıcı teknik değildir)
- **Her kod yazımından sonra**, kritik kısımları **hiç kod bilmeyen birine anlatır gibi** sade Türkçe ile izah et: bu dosya ne işe yarar, neden böyle yazıldı, kullanıcı açısından ne anlama gelir. Jargon kullanman gerekiyorsa parantez içinde günlük dille açıkla.
- **Soruları da teknik bilmeyen birine sorar gibi sor.** "Hangi ORM?" değil, "veriler bilgisayarda nasıl saklansın" gibi. Seçenekleri sonuç/etki üzerinden anlat, kütüphane adıyla değil.
- Arayüz dili ve kullanıcıya görünen tüm metinler **Türkçe**.

### 5.2 Mimari (Think Before Coding + Simplicity First)
- **Domain ve Application katmanları saf Python kalır; PyQt6 import etmez.** UI'a bağımlılık yalnızca Presentation katmanında.
- Bağımlılık enjeksiyonu için **framework ekleme**; `bootstrap.py` içinde elle constructor injection yeterli.
- `datetime.now()` hiçbir yerde doğrudan çağrılmaz — her zaman `IClock` üzerinden. "Gün" kavramı `DayId` ile, kullanıcının tanımladığı gün-başlangıç saatine göre.
- Yeni bağımlılık eklemeden önce gerçekten gerekli mi diye sor.

### 5.3 Faz disiplini (Surgical Changes + Goal-Driven)
- Her faz **planın faz tablosundaki kapsamla** sınırlı; bir fazın kodu başka fazın işini yapmaz.
- **Her fazın başında** o fazın ölçülebilir başarı kriterlerini net cümlelerle yaz ("çalışır kanıt").
- **Her faz sonunda** doğrulama: `pytest` (domain+application unit + integration) yeşil + Windows'ta manuel smoke senaryosu. Bunlar geçmeden faz "bitti" sayılmaz.
- Faz bitince yeni branch'te commit; push kullanıcı onayıyla.

### 5.4 Asset (görsel/ses) eksikliği
- Mana Seed dosya isimlerini/yapısını **değiştirme**; sadece `manifest.json` ile eşle.
- **Bir özellik için mevcut asset'ler yetersiz kaldığında** (ör. düşman sprite'ı, vizyon-spesifik aksesuar, ses efekti): işi durdurma — **kullanıcıdan iste**. İsterken şunu net ver: (1) tam olarak hangi görsel/ses gerekiyor, (2) boyut/format/stil spesifikasyonu (ör. 64×64 px, şeffaf PNG, pixel-art), (3) **bir yapay zekâ aracıyla nasıl üreteceğine dair adım adım talimat ve örnek prompt**. Kullanıcı üretip ekledikten sonra entegre et.

### 5.5 Test ortamı
- GUI Windows'ta test edilir; domain/application testleri headless çalışır (`QT_QPA_PLATFORM=offscreen`).
- Testler gerçek veri dizinine dokunmaz; geçici DB kullanır.
