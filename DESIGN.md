---
name: Kajatu Weather Design System
description: Premium weather briefing cards with glacier aesthetics
colors:
  primary: "#1E40AF"
  accent-high: "#E11D48"
  accent-low: "#2563EB"
  glacier-bg: "#F0F4F8"
  card-bg: "#FFFFFF"
  ink-dark: "#0F172A"
  border-subtle: "rgba(15, 23, 42, 0.05)"
typography:
  display:
    fontFamily: "Outfit, sans-serif"
    fontSize: "clamp(2rem, 6vw, 4rem)"
    fontWeight: 900
    lineHeight: 1
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Pretendard Variable, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "-0.03em"
rounded:
  sm: "12px"
  md: "24px"
spacing:
  sm: "8px"
  md: "16px"
  lg: "32px"
---

# Design System: Kajatu Weather

## 1. Overview

**Creative North Star: "The Glacier Expedition"**

This design system is tailored for daily and weekly weather briefings delivered to travelers in Kazakhstan. Inspired by the snow-capped mountains of Almaty and the pristine glacier lakes of Kolsay, the aesthetic leverages crisp glacier-blue tints, deep navy ink for high contrast, and a distinct typographic pairing that conveys confidence and readability.

It rejects default, generic SaaS styling in favor of an editorial, high-contrast travel bulletin look.

**Key Characteristics:**
* Glacier Off-White backgrounds (`#F0F4F8`) reflecting alpine fresh air.
* Typographic contrast using `Outfit` for display and `Pretendard` for numeric weather data.
* Elimination of cheap "AI slop" indicators such as thick side-tab card borders.

## 2. Colors

The palette mimics glacier ice, cold stone, and clear skies, utilizing high-contrast ink to maintain accessibility.

### Primary
* **Glacier Deep Blue** (`#1E40AF` / `oklch(45% 0.15 240)`): Used for primary headers, key branding accents, and semantic emphasis.

### Secondary
* **Sun Crimson** (`#E11D48` / `oklch(60% 0.18 25)`): High-temperature color indicator.
* **Ice Blue** (`#2563EB` / `oklch(60% 0.16 230)`): Low-temperature color indicator.

### Neutral
* **Glacier Off-White** (`#F0F4F8` / `oklch(96% 0.005 200)`): Body background color.
* **Pure White** (`#FFFFFF`): Card background surfaces.
* **Abyss Blue-Black** (`#0F172A` / `oklch(25% 0.02 240)`): Primary body text, labels, and numbers.
* **Glacier Gray** (`#94A3B8`): Muted info and icons.

### Named Rules
**The Glacier Contrast Rule.** To ensure maximum readability in high ambient light (e.g. travelers checking phones outdoors), all body text and data labels must achieve a contrast ratio of at least 4.5:1 against their background. No light gray text is permitted on white or light-tinted cards.

## 3. Typography

**Display Font:** Outfit (Google Font)
**Body Font:** Pretendard Variable

### Hierarchy
- **Display 1 (H1)** (Outfit, Bold (900), `text-[64px]`, line-height 1, letter-spacing `-0.02em`): Main briefing headers.
- **Display 2 (H2)** (Outfit, Extralight (200), `text-[42px]`, line-height 1, letter-spacing `-0.02em`): Section eyebrows or secondary subtitles.
- **Title (H3)** (Outfit, Bold (700), `text-[32px]` or `text-[20px]`): Location names and days of the week.
- **Body & Data** (Pretendard, Regular (400) or Light (300), variable size): Timeline hours, temperatures, and descriptions. Max line length: 70ch.

### Named Rules
**The Display Contrast Rule.** Display headings must always use `Outfit` and maintain tighter letter-spacing (`-0.02em` to `-0.03em`) to look intentional, but never exceed `-0.03em` to prevent character overlapping.

## 4. Elevation

Depth is conveyed through a hybrid of very soft ambient shadows and extremely thin, clean borders. Hard outlines and dark heavy shadows are prohibited.

### Shadow Vocabulary
- **Ambient Card Glow** (`box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.02)`): Restful, soft shadow used for card containers.
- **Hero Card Glow** (`box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06), 0 2px 8px rgba(15, 23, 42, 0.03)`): Gives the Almaty hero card additional elevation.

## 5. Components

### Cards / Containers
- **Corner Style**: Rounded corners (`24px` radius) to maintain a modern, friendly touch.
- **Background**: Pure white (`#FFFFFF`).
- **Border**: 1px subtle border (`border: 1px solid rgba(15, 23, 42, 0.05)`) all around.
- **Left/Right Padding**: 1.5rem to 2rem (24px to 32px).

### AI Advice / Callout Box
- **Corner Style**: Rounded corners (`24px` radius).
- **Background**: Soft blue-gray tint (`background: rgba(30, 64, 175, 0.03)`).
- **Border**: Thin full border (`border: 1px solid rgba(30, 64, 175, 0.1)`).

## 6. Do's and Don'ts

### Do:
- **Do** load and pair Google Font `Outfit` for titles with `Pretendard` for numeric values.
- **Do** use `Glacier Off-White` (`#F0F4F8`) as the body background.
- **Do** surround cards with a subtle 1px border instead of thick side accents.
- **Do** highlight extreme temperatures or high rain probability using text weight or high-contrast colors.

### Don't:
- **Don't** use `border-l-8` (side-tab borders) as a shortcut for making cards stand out.
- **Don't** use raw, default Tailwind Slate grays (`bg-slate-200`, `bg-slate-50`).
- **Don't** apply letter-spacing tighter than `-0.03em` to headlines (e.g. avoid Tailwind's default `tracking-tighter` on display sizes).
- **Don't** mix weather icon sets (e.g. using an illustrative umbrella icon next to flat weather icons). Maintain strict icon system integrity.
- **Don't** apply random background highlights to a single day. If highlighting 'Today', it must be consistently applied across all regional cards.
