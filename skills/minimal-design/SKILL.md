---
name: minimal-design
description: >-
  Use when designing dark minimalist web interfaces, Obsidian Modernism design
  systems, bento grid layouts, glassmorphic elevation tokens, accessible high-contrast
  typography scales, and zero-bloat CSS component architectures.
---

# Obsidian Modernism & Minimal Design System

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Crafting high-converting, aesthetic dark-mode user interfaces and landing pages.
- Implementing the **Obsidian Modernism** visual philosophy (void canvas, subtle borders, luminous accents).
- Structuring CSS design tokens for elevated surfaces, typography hierarchies, and tactile borders.
- Building responsive bento-box feature grids with glassmorphic depth.
- Eliminating heavy UI component library dependencies in favor of pure, performant CSS architecture.

---

## 2. Hard Architectural Rules

1. **Surface Elevation Hierarchy**:
   Never use `#000000` across all layers. True depth requires subtle, staggered elevations:
   - Canvas (Base): `#0a0a0a`
   - Floating Surface / Nav: `#121314`
   - Bento Cards: `#16181b`
   - Card Hover / Active Chips: `#1e2024`

2. **The Alpha Border Rule**:
   Never use solid gray borders (e.g. `#444444` or `#333333`). Solid borders feel chalky and abrupt on dark backgrounds. Always use white alpha channels:
   - Subtle (Default): `rgba(255, 255, 255, 0.08)`
   - Medium (Hover / Interactive): `rgba(255, 255, 255, 0.14)`
   - Active / Focus: `rgba(255, 255, 255, 0.30)`

3. **Strict Typography Color Scale**:
   Never make all text white. Respect typographic contrast to guide the reader's eye:
   - Primary (Headlines): `#ffffff` (Pure white, 100% opacity)
   - Secondary (Body Copy): `#9ea0a6` (Muted neutral, readable)
   - Tertiary (Metadata, Breadcrumbs, Captions): `#6b6d74` (Darker muted)

4. **Accents as Indicators, Not Backgrounds**:
   Accent colors (`#fe5e37` orange, `#10b981` green, `#2563eb` blue) must be used surgically: status badges, interactive pills, and gradient highlights. Never flood large containers with vibrant saturated fills.

---

## 3. The Obsidian Modernism Token Architecture

### CSS Design Tokens (`tokens.css`)

```css
:root {
  /* Surface Layers */
  --bg-canvas: #0a0a0a;
  --bg-surface: #121314;
  --bg-card: #16181b;
  --bg-card-hover: #1e2024;

  /* Borders & Dividers */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-medium: rgba(255, 255, 255, 0.14);
  --border-focus: rgba(255, 255, 255, 0.35);

  /* Typography */
  --text-primary: #ffffff;
  --text-secondary: #9ea0a6;
  --text-tertiary: #6b6d74;

  /* Brand Accents */
  --accent-orange: #fe5e37;
  --accent-blue: #2563eb;
  --accent-green: #10b981;

  /* Spacing Scale */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;

  /* Border Radii */
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-full: 9999px;

  /* Micro-Transitions */
  --transition-fast: 150ms cubic-bezier(0.16, 1, 0.3, 1);
  --transition-smooth: 300ms cubic-bezier(0.16, 1, 0.3, 1);
}
```

---

## 4. Production Component Patterns

### Pattern A: Modern Bento Grid Card
```html
<div class="bento-card">
  <div class="card-badge">
    <span class="status-dot"></span> Active Feed
  </div>
  <h3 class="card-title">Realtime Telemetry</h3>
  <p class="card-desc">Low-latency event streaming directly into isolated collection pools.</p>
</div>

<style>
  .bento-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: var(--space-xl);
    transition: all var(--transition-smooth);
    position: relative;
    overflow: hidden;
  }

  .bento-card:hover {
    background-color: var(--bg-card-hover);
    border-color: var(--border-medium);
    transform: translateY(-2px);
  }

  .card-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-xs);
    font-size: 12px;
    font-weight: 500;
    color: var(--accent-green);
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    padding: 2px 10px;
    border-radius: var(--radius-full);
    margin-bottom: var(--space-md);
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--accent-green);
  }

  .card-title {
    color: var(--text-primary);
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.02em;
    margin: 0 0 var(--space-sm) 0;
  }

  .card-desc {
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
  }
</style>
```

---

### Pattern B: Tactile Action Button
```html
<button class="tactile-btn">
  <span>Explore Systems</span>
  <svg class="btn-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M5 12h14M12 5l7 7-7 7"/>
  </svg>
</button>

<style>
  .tactile-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-sm);
    background-color: var(--text-primary);
    color: #000000;
    font-size: 14px;
    font-weight: 600;
    padding: 10px 20px;
    border-radius: var(--radius-full);
    border: none;
    cursor: pointer;
    transition: transform var(--transition-fast), background-color var(--transition-fast);
  }

  .tactile-btn:hover {
    background-color: #f0f0f0;
    transform: scale(1.02);
  }

  .tactile-btn:active {
    transform: scale(0.98);
  }

  .btn-arrow {
    transition: transform var(--transition-fast);
  }

  .tactile-btn:hover .btn-arrow {
    transform: translateX(3px);
  }
</style>
```

---

## 5. Anti-Patterns & Visual Pitfalls

| Mistake | Visual Defect | Fix |
| :--- | :--- | :--- |
| **Pure black canvas + pure white cards** | Eye strain, stark cutouts | Use `#0a0a0a` canvas with `#16181b` card surfaces |
| **All text 100% white** | Monolithic text block, unreadable | Apply 3-tier hierarchy: `#ffffff`, `#9ea0a6`, `#6b6d74` |
| **Thick 2px solid gray borders** | Looks dated and bulky | Use `1px solid rgba(255, 255, 255, 0.08)` |
| **Saturated neon container backgrounds** | Visual exhaustion | Use dark translucent cards with 1px luminous badges |

---

## 6. Design System Checklist
- [ ] Base Canvas set to `#0a0a0a`.
- [ ] Borders use white alpha channels (`rgba(255,255,255,0.08)`).
- [ ] Typographic contrast verified (WCAG AA 4.5:1 ratio).
- [ ] Interactive elements have tactile hover, active, and focus rings.
