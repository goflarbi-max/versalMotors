# Sidebar theme and hamburger regression diagnosis

Date: 2026-10-22

## Scope and method

This is a read-only diagnosis of the application code. No application, data, analytics, AI, authentication-verification, or test file was changed during this investigation.

Evidence gathered:

- Read `docs/project_brief.md` and `docs/.agent/rules/project-rules.md`. The rules file is under `docs/.agent/`; there is no root `.agent/rules/project-rules.md` in this checkout.
- Reviewed `git log --oneline`, relevant commit diffs, current line numbers, and `git blame`.
- Compared the last committed revision (`b000c1f`) with the current uncommitted working tree.
- Ran `pip show streamlit` and inspected the installed Streamlit 1.64.0 frontend bundle for the actual sidebar-control markup.
- Exercised the theme toggle with `streamlit.testing.v1.AppTest` in a clean test session.
- Checked the current hamburger CSS against a faithful copy of the Streamlit 1.64 control markup in a clean headless Chrome session.
- Confirmed all four local Inter files return HTTP 200 through Streamlit static serving.

## Relevant history

| Change | Commit | Finding |
|---|---|---|
| Sidebar redesign | `705cc12` — Improve sidebar and dark mode readability | Created `src/ui/sidebar.py` and moved the shared sidebar, runtime palette, and theme toggle there. |
| Theme toggle | `705cc12` | Introduced the session-state toggle plus the browser `localStorage`/`StorageEvent` bridge. This is the origin of regression 1. |
| Sidebar default changed from expanded to auto | `df10107` — Add responsive landing page and theme-aware branding | Changed `initial_sidebar_state="expanded"` to `"auto"`. This does not initiate the theme bug, but it makes a sidebar remount able to return collapsed at narrower widths. |
| Initial light login/default | `2d6a5bd` — Default to light theme and use light login background | Added the authentication UI and the first forced-light login implementation. |
| Login made unconditionally light | `148318d` — Polish summary cards and enforce light login theme | Added the session-state reset to light and rewrote the native active-theme local-storage value on the login route. |
| Dark main background changed to `#0F172A` | `148318d` | Changed both `.streamlit/config.toml` and `RUNTIME_THEME`; the value itself is correct and is not the cause of the partial switch. |
| Hamburger and Inter work | **No commit** | These changes are currently uncommitted after `b000c1f`. They appear in `.streamlit/config.toml`, `src/ui/theme.py`, `src/ui/sidebar.py`, `src/ui/charts.py`, `static/fonts/`, and related documentation/test working-tree changes. |

For the theme regression, the last revision before the problematic theme bridge is `c8fb79b`, the parent of `705cc12`. For the hamburger/Inter regression, `b000c1f` is the committed baseline; the feature itself has not yet been committed.

## Bug 1: partial dark mode and disappearing switch

### Root cause

There are two competing theme controllers:

1. The app theme stored in `st.session_state["sidebar_dark_mode"]` and rendered through custom CSS.
2. Streamlit's native theme stored internally in path-specific browser keys such as `stActiveTheme-/overview-v2` and exposed to Python as `st.context.theme.type`.

The toggle updates the session-state value correctly. On that rerun, `render_sidebar()` applies the dark custom CSS and later page components read the same session-state value, so cards, tables, and charts select their dark palettes. However, the same run then calls `_request_streamlit_theme()`, which directly rewrites Streamlit's private local-storage key and manually dispatches a `StorageEvent`. That unsupported bridge causes Streamlit's front end to reconfigure/remount its native theme and sidebar after the Python-rendered sidebar and main-page CSS were emitted. Later-rendered page components still use the dark session value, explaining the exact mixed result: dark cards on a light native page, with the sidebar control recreated or collapsed.

The mismatch test is also unstable:

- `context_dark_mode` comes from `st.context.theme.type` at `src/ui/sidebar.py:534`.
- The widget value comes from `st.session_state` at lines 535-537 and 560-570.
- When they differ, lines 571-573 invoke the browser bridge.
- `sidebar_theme_context` is written at line 572 but is never read anywhere. It therefore cannot suppress a second bridge call or prove that the browser has caught up.

The Python interaction itself produces one normal rerun. In AppTest the state moved from `False` to `True`, the toggle stayed present, and no exception occurred. The extra disruption is therefore in the browser-side local-storage event, not in the widget's Python state update.

### File and lines

- `src/ui/sidebar.py:413-498`: custom runtime CSS is emitted before the native-theme bridge.
- `src/ui/sidebar.py:501-528`: writes Streamlit's private `stActiveTheme-*` keys and dispatches a synthetic `StorageEvent`.
- `src/ui/sidebar.py:531-574`: mixes `st.context.theme.type` with the session-state widget value.
- `app.py:22`: `initial_sidebar_state="auto"`; a native remount can recalculate the sidebar as collapsed.
- `src/ui/theme.py:565-610`: tables, Overview cards/charts, summary cards, and runtime helpers correctly prefer `sidebar_dark_mode`, which is why those components can turn dark independently of the native page.
- `.streamlit/config.toml:1-6,41-71`: native light/dark themes are valid, but they form a second theme source alongside the custom runtime CSS.

### Commit attribution

Introduced by `705cc12` in commit-local `src/ui/sidebar.py` lines 236-396, especially `_request_streamlit_theme()` and the comparison between session state and `st.context.theme.type`.

`148318d` did not introduce this bridge, but it increased coupling by adding another private local-storage writer on the login page and by setting the `#0F172A` dark palette in both config and custom dictionaries.

### Confidence

**High (90%).** The state transition was reproduced with AppTest, the browser bridge is visible in source, the write-only context key was confirmed by repository search, and the execution order explains the reported mixed styling precisely.

### Smallest proposed fix

Use one source of truth. Keep `sidebar_dark_mode` as the app toggle state and remove `_request_streamlit_theme()` plus the comparison to `st.context.theme.type` after initialization. Render all main, sidebar, card, table, and chart colours from that one session value. Initialize it once from the light default, and use an `on_change` callback only if a deliberate rerun is needed. Do not write or dispatch Streamlit's private `stActiveTheme-*` storage events.

If native Streamlit theme switching must be retained, remove the custom toggle instead and rely only on the supported native Settings theme. Mixing both systems is the fragile part.

## Bug 2: native `>>` remains instead of a hamburger

### Root cause

The committed sidebar CSS targets a control that does not exist in the installed Streamlit version:

```css
[data-testid="stSidebarCollapsedControl"] button
```

Streamlit 1.64.0 actually renders:

- Collapsed/open control: `button[kind="headerNoPadding"][data-testid="stExpandSidebarButton"]`, containing the Material icon `keyboard_double_arrow_right`.
- Expanded/close control: `div[data-testid="stSidebarCollapseButton"]` containing a `button[kind="headerNoPadding"]`, with `keyboard_double_arrow_left`.

The installed frontend bundle contains no `stSidebarCollapsedControl` marker for these controls. Because the selector misses, the native Material double-arrow is never hidden and the hamburger pseudo-elements are never attached.

The present working tree contains uncommitted attempts at broader selectors in `src/ui/sidebar.py:220-389`. Those current selectors include the correct 1.64 test IDs and work against an isolated copy of the 1.64 DOM: the native child becomes hidden and the three-line pseudo-element is visible. They have not been committed or deployed. In the full app, the native-theme remount described in bug 1 can also recreate the toolbar/sidebar after the early CSS is mounted, so bug 1 should be removed before judging the final hamburger styling.

Generated emotion classes are not a safe alternative: they are build-specific. The stable 1.64 attributes are the two `data-testid` values and `kind="headerNoPadding"` noted above.

### File and lines

- Committed baseline `src/ui/sidebar.py` at `b000c1f`, lines 210-213: only `stSidebarCollapsedControl` is targeted.
- Current uncommitted `src/ui/sidebar.py:220-389`: hamburger selectors and pseudo-elements.
- Current uncommitted `src/ui/theme.py:122-149`: hamburger colour tokens.
- Installed Streamlit bundle `index.CcFifQPt.js`: `stExpandSidebarButton` uses `keyboard_double_arrow_right`; `stSidebarCollapseButton` wraps the left-arrow close button.

### Commit attribution

There is no introducing commit for the hamburger feature. It is an uncommitted working-tree change made after `b000c1f`. The stale committed selector originally came from `705cc12`, but that commit only enlarged the native control; it did not implement a hamburger.

On the hosted app, the reason is conclusive: uncommitted hamburger/Inter changes cannot be present until committed and deployed. Locally, the initial selector mismatch and the theme remount are the two relevant causes.

### Confidence

**Very high (95%)** for the selector mismatch and hosted behavior; **medium-high (80%)** that the remaining local persistence symptom is coupled to the native theme remount/stale loaded CSS.

### Smallest proposed fix

After removing the unsupported native-theme remount, scope one CSS rule to the exact 1.64 controls:

- `button[data-testid="stExpandSidebarButton"]`
- `[data-testid="stSidebarCollapseButton"] > button`

Hide only their native icon child and draw the hamburger/X with CSS on the real native button, preserving the native click behavior and focus semantics. Keep the native icon visible as a fallback if the custom selector fails. Avoid hashed class names and remove obsolete `stSidebarCollapsedControl` selectors.

## Theme-state trace by surface

| Surface | Current source | Result |
|---|---|---|
| Main page/background/text | `_apply_runtime_theme(selected_dark_mode)` in `src/ui/sidebar.py` | Correct palette selected, but vulnerable to the subsequent native front-end remount. |
| Sidebar | `_apply_sidebar_css(selected_dark_mode)` | Reads the same session value; likewise emitted before the browser bridge. |
| Overview cards/charts | `active_overview_theme()` | Correctly prefers `sidebar_dark_mode`. |
| Summary cards | `active_summary_card_theme()` | Correctly prefers `sidebar_dark_mode`. |
| Tables | `active_table_theme()` | Correctly prefers `sidebar_dark_mode`. |
| Ask-the-Business controls | `active_runtime_theme()` | Correctly prefers `sidebar_dark_mode`. |
| Plotly charts | shared chart helper calls `active_overview_theme()` | Correct theme source; Inter addition only changes font metadata. |
| Login | `apply_login_theme()` | Intentionally resets the two theme keys to `False`, but only when the login page executes. |
| Sign out | `_logout_to_light()` | Intentionally clears auth/session and restores light. |

No protected page writes `sidebar_dark_mode=False`. The login reset is route-specific in Python and is not the trigger when switching theme on an authenticated Overview page.

## Login force-light scoping

The current uncommitted change scopes the rules that hide the sidebar/header to `body:has(.st-key-login_shell)`, which is appropriate. However, several light-login rules remain global within the login style element:

- `src/ui/theme.py:1149-1154` changes root theme variables globally.
- `src/ui/theme.py:1165-1186` styles `.stApp`, the main view, header, and `body` without a login-shell qualifier.

Normally Streamlit removes the old page elements on navigation, but these selectors can cause a light flash and are unnecessarily dependent on delta cleanup timing. They are fragile, though the authenticated toggle regression is primarily caused by the storage-event bridge, not these rules.

## Dark background and config review

- `#0F172A` is consistently present in `RUNTIME_THEME["dark"]["background"]` and `.streamlit/config.toml [theme.dark].backgroundColor`.
- Dark secondary surfaces use `#1E293B`, text uses `#F1F5F9`, and borders use `#334155`; contrast is adequate.
- `[theme] base="light"` correctly sets the default and does not prohibit the declared `[theme.dark]` variant.
- The problem is not insufficient selector specificity in the `#0F172A` rule: `_apply_runtime_theme` uses `!important` on `.stApp`, `stAppViewContainer`, and `stMain`. The later native front-end theme remount is the failure point.

## Font review

The Inter work does not set page colour or background:

- `src/ui/theme.py:6-93` defines font family, weights, sizes, smoothing, tabular figures, and restores the Material Symbols font for icons.
- `.streamlit/config.toml:7-39` registers Inter 400/500/600/700.
- All four font files are served successfully with HTTP 200 and total about 97 KB, excluding the licence.
- No failed external stylesheet can block rendering because the font is self-hosted.

The font change is therefore correlated in time but is not a root cause of either regression.

## Clean-session reproduction and execution order

The Python portion was reproduced in a clean AppTest session:

1. First run: `st.context.theme.type` resolves light, `sidebar_dark_mode` is initialized to `False`, light runtime/sidebar CSS is emitted, and the toggle renders off.
2. Toggle interaction: Streamlit updates the keyed widget and performs one Python rerun.
3. Second Python run: `sidebar_dark_mode=True`; dark runtime/sidebar CSS is emitted; all component helpers read `True`; the toggle remains present and reads `True`.
4. Because native `st.context.theme.type` is still light during that run, `_request_streamlit_theme(True)` is emitted.
5. In a real browser, that script rewrites the path-specific native theme key and dispatches `StorageEvent`. Streamlit's front end reconfigures its native theme/sidebar independently of the completed Python rerun. With `initial_sidebar_state="auto"`, the recreated sidebar may be collapsed. Earlier global CSS is lost or superseded while later component CSS remains dark.
6. The collapsed toolbar then exposes Streamlit's native `keyboard_double_arrow_right`. In committed code, the only selector is for nonexistent `stSidebarCollapsedControl`, so `>>` remains visible.

A clean Selenium login attempt exposed a separate existing automation issue: visible email/password DOM values were not committed to Streamlit widget state before the Sign In button event, so the protected browser route could not be reached in that new automated session. This did not affect the state diagnosis above; AppTest verified the server rerun/state sequence, and the installed frontend bundle plus an isolated Chrome DOM verified the exact sidebar markup and CSS match behavior.

## Other fragile areas

- `requirements.txt` permits any `streamlit>=1.57,<2.0`; internal `data-testid` markup can change across minor releases. The installed version is 1.64.0.
- `stActiveTheme-*` is a private, versioned, path-specific key. Application code should not manipulate it.
- Theme state has three representations: native context, session state, and a write-only `sidebar_theme_context` key.
- Theme CSS is split across the app shell, sidebar, and page-level components, making ordering significant.
- `initial_sidebar_state="auto"` is responsive but should not be treated as persistent app state after a frontend remount.
- Login CSS still has globally scoped root/main/body rules, even though its hide rules are now route-scoped.
- The current broader hamburger CSS is large and duplicates selectors many times; a small exact selector set would be easier to test and maintain.
- The native expand control in Streamlit 1.64 has an empty `aria-label` in the rendered button. Pure CSS cannot correct that accessibility property.

## Regression prevention

1. Choose one supported theme controller; do not combine a custom toggle with private native local-storage events.
2. Add an AppTest asserting one toggle interaction preserves the current route, session key, and sidebar widget.
3. Add a browser DOM smoke test pinned to the supported Streamlit version for the expand/collapse controls and computed hamburger styles.
4. Pin Streamlit to a tested minor range, or run the DOM smoke test before accepting an upgrade.
5. Keep login light-theme selectors fully scoped to the login shell.
6. Test both expanded and collapsed sidebar states at 375, 768, and 1280 px after every navigation/theme change.
7. Assert that every component palette helper and the shell use the same theme state key.
8. Avoid write-only synchronization flags; either use them to gate a transition or remove them.

## Recommended approval scope

The smallest repair should touch only `src/ui/sidebar.py` and, if fully scoping login CSS is included, the affected selectors in `src/ui/theme.py`. It should not require changes to data, analytics, AI, authentication verification, metrics, or existing business-page logic.
