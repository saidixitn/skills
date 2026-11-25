---
name: animations
description: >-
  Use when engineering high-performance 60-120fps web animations, GSAP timeline
  orchestration, Lenis smooth scrolling, ScrollTrigger pin/scrub physics,
  anti-FOUC (flash of unstyled content) routing engines, or zero-framework
  magnetic cursor interactions.
---

# Creative Motion & Hardware-Accelerated Physics Engine

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Designing fluid 60fps–120fps web motion without heavy React or Three.js dependencies.
- Synchronizing **Lenis smooth scrolling** with **GSAP ScrollTrigger** inside a single RequestAnimationFrame (RAF) loop.
- Preventing **FOUC (Flash of Unstyled Content)** and navigation lag on multi-page static websites.
- Building tactile micro-interactions: magnetic hover magnets, spring physics, split-text character reveals, and custom inertial cursor physics.
- Optimizing video portfolio performance via speculative link pre-warming and Service Worker range request caching.

---

## 2. Hard Architectural Rules

1. **Hardware Acceleration Only**:
   Animate **only** GPU-composited properties: `transform` (`x`, `y`, `scale`, `rotation`) and `opacity`. Never animate layout-triggering properties (`top`, `left`, `width`, `height`, `margin`, `padding`), which trigger browser layout recalculations and cause stutter/jank.

2. **Unified RAF Loop**:
   Never run independent `requestAnimationFrame` or `setInterval` loops alongside Lenis and GSAP. Always bind Lenis's scroll ticker directly to `gsap.ticker.add()` with lag smoothing disabled.

3. **Synchronous Anti-FOUC Execution**:
   Multi-page static sites must execute an inline routing and theme script synchronously inside `<head>` before the DOM paints to prevent page flashing.

4. **Will-Change Lifecycle Hygiene**:
   Apply `will-change: transform, opacity` immediately before an animation sequence begins, and remove it (`will-change: auto`) once the timeline completes to free GPU memory.

5. **Reduced-Motion Accessibility**:
   Always honor `prefers-reduced-motion: reduce` by disabling inertial smooth scrolling and replacing movement animations with instant opacity transitions.

---

## 3. Step-by-Step Motion Architecture Workflow

```
[ Step 1: Head Inline Anti-FOUC Script ]
       │ 
       ▼
[ Step 2: Initialize Lenis Smooth Scroll Instance ]
       │ 
       ▼
[ Step 3: Bind Lenis to GSAP RAF Ticker ]
       │ 
       ▼
[ Step 4: Register ScrollTrigger & Custom Eases ]
       │ 
       ▼
[ Step 5: Mount Magnetic Elements & Inertial Cursor ]
```

---

## 4. Production Code Patterns

### Pattern A: Synchronous Head Anti-FOUC Router (Darshan Naidu Portfolio Architecture)
Placed at the top of the `<head>` tag to eliminate flash of unstyled content on direct route reloads:

```html
<script>
  // Anti-flash script executed synchronously before DOM paint
  (function () {
    var path = (window.location.pathname || "/").replace(/\/$/, "") || "/";
    var page = path.split("/").pop() || "index";
    document.documentElement.setAttribute("data-current-page", page);

    // Immediate theme / visibility lock
    document.documentElement.classList.add("js-ready");
  })();
</script>
<style>
  /* Prevent layout jump while GSAP calculates dimensions */
  html:not(.js-ready) .animated-hero-title,
  html:not(.js-ready) .magnetic-btn {
    visibility: hidden;
  }
</style>
```

---

### Pattern B: Lenis + GSAP RAF Synchronization (60–120fps Smooth Scroll)
The industry-standard high-fidelity smooth scroll loop with zero ticker drift:

```javascript
import Lenis from '@studio-freight/lenis';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function initSmoothScroll() {
  // Check for reduced motion preference
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) return null;

  const lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // Exponential easeOut
    direction: 'vertical',
    gestureDirection: 'vertical',
    smooth: true,
    mouseMultiplier: 1.0,
    smoothTouch: false,
    touchMultiplier: 2.0
  });

  // Critical: Synchronize Lenis scroll updates with GSAP ScrollTrigger
  lenis.on('scroll', ScrollTrigger.update);

  // Critical: Pipe GSAP's high-precision internal RAF loop into Lenis
  gsap.ticker.add((time) => {
    lenis.raf(time * 1000); // Convert seconds to milliseconds
  });

  // Disable lag smoothing to prevent visual stutter after heavy CPU operations
  gsap.ticker.lagSmoothing(0);

  return lenis;
}
```

---

### Pattern C: Magnetic UI Element Physics (Elastic Micro-Interaction)
Attaches spring-like physics to buttons or pills when the cursor hovers near them:

```javascript
export function initMagneticElements(selector = '.magnetic-el') {
  const elements = document.querySelectorAll(selector);

  elements.forEach((el) => {
    el.addEventListener('mousemove', (e) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      // 0.3 dampening factor for realistic elastic tension
      gsap.to(el, {
        x: x * 0.35,
        y: y * 0.35,
        duration: 0.4,
        ease: 'power2.out',
        overwrite: 'auto'
      });
    });

    el.addEventListener('mouseleave', () => {
      // Snap back to origin with smooth damping
      gsap.to(el, {
        x: 0,
        y: 0,
        duration: 0.7,
        ease: 'elastic.out(1, 0.4)',
        overwrite: 'auto'
      });
    });
  });
}
```

---

### Pattern D: Speculative Link Pre-Warming Engine (`fast-loader.js`)
Prefetches HTML and assets on hover or intent to achieve sub-100ms route transitions:

```javascript
export function initSpeculativePrefetch() {
  const prefetchedUrls = new Set();

  function prefetch(url) {
    if (prefetchedUrls.has(url) || url === window.location.href) return;
    prefetchedUrls.add(url);

    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
  }

  document.querySelectorAll('a[href^="/"]').forEach((anchor) => {
    anchor.addEventListener('mouseenter', () => prefetch(anchor.href), { passive: true });
    anchor.addEventListener('touchstart', () => prefetch(anchor.href), { passive: true });
  });
}
```

---

## 5. Anti-Patterns & Common Pitfalls

| Anti-Pattern | Fatal Symptom | Hardware-Accelerated Fix |
| :--- | :--- | :--- |
| **Animating `top` or `margin-top`** | Dropped frames, layout thrashing (15fps lag) | Animate `y` transform instead: `gsap.to(el, { y: -50 })` |
| **Multiple unlinked RAF loops** | Scroll stutter and desynchronized parallax markers | Always drive Lenis via `gsap.ticker.add()` |
| **Forgetting `ScrollTrigger.refresh()`** | Scroll triggers fire at incorrect positions after dynamic images load | Call `ScrollTrigger.refresh()` after fonts, images, or DOM nodes finish rendering |
| **Heavy CSS filters without GPU promotion** | Fan spins up, mobile browser drains battery | Add `translateZ(0)` or `will-change: transform` to promote animated cards to their own composite layer |

---

## 6. Verification Checklist
- [ ] Hardware acceleration: Zero layout properties animated (`top`, `left`, `margin`).
- [ ] RAF sync: Lenis and ScrollTrigger driven by single `gsap.ticker`.
- [ ] Anti-FOUC: Inline `<head>` script prevents flashes on direct URL reloads.
- [ ] Reduced motion: `prefers-reduced-motion` query tested and respected.
