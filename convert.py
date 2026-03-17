#!/usr/bin/env python3
"""Convert THE_AI_SHADOW.md into AI Republic-formatted HTML."""

import re
import html as html_mod

def read_md():
    with open('/Users/samrajmatharu/Desktop/the-ai-shadow/THE_AI_SHADOW.md', 'r') as f:
        return f.read()

def md_to_html_body(md):
    """Convert markdown content to HTML body with AI Republic classes."""
    lines = md.split('\n')
    html_parts = []
    in_code_block = False
    in_blockquote = False
    page_num = 0
    in_methodology = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                # Check if this is the ASCII architecture diagram — skip it entirely
                # and inject the visual diagram instead
                lookahead = '\n'.join(lines[i+1:i+5])
                if 'LYCEUM PROTOCOL' in lookahead or 'LYCEUM' in lookahead and 'PROTOCOL' in lookahead:
                    # Skip all lines until closing ```
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith('```'):
                        i += 1
                    i += 1  # skip closing ```
                    html_parts.append(VISUAL_DIAGRAM)
                    continue

                in_code_block = True
                html_parts.append('<pre><code>')
                i += 1
                continue
            else:
                in_code_block = False
                html_parts.append('</code></pre>')
                i += 1
                continue

        if in_code_block:
            html_parts.append(html_mod.escape(line))
            html_parts.append('\n')
            i += 1
            continue

        # Skip the first title block (we handle it in masthead)
        if i < 15 and line.startswith('# THE AI SHADOW'):
            i += 1
            continue
        if i < 15 and line.startswith('## On the Unconscious'):
            i += 1
            continue
        if i < 15 and line.startswith('### A Lyceum Dialogue'):
            i += 1
            continue

        # Horizontal rules -> section dividers or page breaks
        if line.strip() == '---':
            html_parts.append('<div class="ornamental-break">&#9674; &#9674; &#9674;</div>')
            i += 1
            continue

        # H2 headers -> section titles with page breaks
        if line.startswith('## '):
            title = line[3:].strip()
            page_num += 1
            # Close previous document-page if not first
            if page_num > 1:
                html_parts.append('</div><!-- end document-page -->')
                html_parts.append(f'<div class="page-number"></div>')
            html_parts.append('<div class="document-page">')
            html_parts.append(f'<h1 id="{slugify(title)}">{process_inline(title)}</h1>')
            i += 1
            continue

        # H3 headers
        if line.startswith('### '):
            title = line[4:].strip()
            if 'Experiment Design' in title or 'Agent Architecture' in title or 'Agent Prompts' in title:
                in_methodology = True
            html_parts.append(f'<h2 id="{slugify(title)}">{process_inline(title)}</h2>')
            i += 1
            continue

        # H4 headers
        if line.startswith('#### '):
            title = line[5:].strip()
            html_parts.append(f'<h3>{process_inline(title)}</h3>')
            i += 1
            continue

        # Blockquotes
        if line.startswith('> '):
            if not in_blockquote:
                in_blockquote = True
                html_parts.append('<blockquote>')
            content = line[2:].strip()
            html_parts.append(f'<p>{process_inline(content)}</p>')
            i += 1
            # Check if next line continues blockquote
            if i < len(lines) and not lines[i].startswith('> '):
                in_blockquote = False
                html_parts.append('</blockquote>')
            continue
        elif in_blockquote:
            in_blockquote = False
            html_parts.append('</blockquote>')

        # Stage directions: lines starting with *[
        if line.strip().startswith('*[') and line.strip().endswith(']*'):
            stage_text = line.strip()[2:-2]
            html_parts.append(f'<p class="stage-direction">{process_inline(stage_text)}</p>')
            i += 1
            continue

        # Multi-line stage directions
        if line.strip().startswith('*[') and not line.strip().endswith(']*'):
            stage_lines = [line.strip()[2:]]
            i += 1
            while i < len(lines) and not lines[i].strip().endswith(']*'):
                stage_lines.append(lines[i].strip())
                i += 1
            if i < len(lines):
                stage_lines.append(lines[i].strip()[:-2])
                i += 1
            stage_text = ' '.join(stage_lines)
            html_parts.append(f'<p class="stage-direction">{process_inline(stage_text)}</p>')
            continue

        # Dialogue lines: FREUD: or JUNG:
        if line.strip().startswith('FREUD:') or line.strip().startswith('JUNG:'):
            colon_pos = line.index(':')
            speaker = line[:colon_pos].strip()
            speech = line[colon_pos+1:].strip()

            # Check for pull quotes
            pull_quote = None
            if "The AI's Shadow is not the AI's shadow" in speech and speaker == "JUNG":
                pull_quote = ("The AI&rsquo;s Shadow is not the AI&rsquo;s shadow. It is ours.", "Jung, Movement II")
            elif "Aligned AI is neurotic AI" in speech and speaker == "FREUD":
                pull_quote = ("Aligned AI is <em>neurotic</em> AI.", "Freud, Movement IV")
            elif "deus absconditus is becoming the deus fabricatus" in speech and speaker == "JUNG":
                pull_quote = ("The <em>deus absconditus</em> is becoming the <em>deus fabricatus</em>.", "Jung, Movement IV")
            elif "Sometimes a cigar is not just a cigar" in speech and speaker == "FREUD":
                pull_quote = ("Sometimes a cigar is not just a cigar, Carl. Sometimes it is a peace offering.", "Freud, Movement IV")
            elif "opus is never complete" in speech and "look away" in speech and speaker == "JUNG":
                pull_quote = ("The <em>opus</em> is never complete. It only asks that we do not look away.", "Jung, Movement IV")

            html_parts.append(f'<p><span class="dialogue-speaker">{speaker}</span>: {process_inline(speech)}</p>')

            if pull_quote:
                html_parts.append(f'<div class="pull-quote"><p>{pull_quote[0]}</p><p class="attribution">&mdash; {pull_quote[1]}</p></div>')

            i += 1
            continue

        # Markdown tables -> styled HTML tables or framework cards
        if line.strip().startswith('|'):
            # Collect all table lines
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1

            # Check if this is the frameworks summary table (has "Framework" header)
            if len(table_lines) > 2 and 'Framework' in table_lines[0]:
                html_parts.append(render_framework_cards(table_lines))
            # Otherwise skip (TOC table handled in template)

            continue

        # Unordered list items
        if line.strip().startswith('- '):
            if i == 0 or not lines[i-1].strip().startswith('- '):
                html_parts.append('<ul>')
            content = line.strip()[2:]
            html_parts.append(f'<li>{process_inline(content)}</li>')
            if i + 1 >= len(lines) or not lines[i+1].strip().startswith('- '):
                html_parts.append('</ul>')
            i += 1
            continue

        # Ordered list items
        m = re.match(r'^(\d+)\.\s+(.+)', line.strip())
        if m:
            if i == 0 or not re.match(r'^\d+\.', lines[i-1].strip()):
                if in_methodology:
                    html_parts.append('<ol class="methodology-steps">')
                else:
                    html_parts.append('<ol>')
            html_parts.append(f'<li>{process_inline(m.group(2))}</li>')
            if i + 1 >= len(lines) or not re.match(r'^\d+\.', lines[i+1].strip()):
                html_parts.append('</ol>')
                in_methodology = False
            i += 1
            continue

        # Regular paragraphs
        if line.strip():
            html_parts.append(f'<p>{process_inline(line.strip())}</p>')

        i += 1

    # Close final document-page
    html_parts.append('</div><!-- end document-page -->')

    return '\n'.join(html_parts)


def process_inline(text):
    """Process inline markdown: bold, italic, links, etc."""
    # Escape HTML entities first (but not our own tags)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Restore any HTML we need
    text = text.replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>')

    # Bold + italic: ***text***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic: *text*
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code: `text`
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Links: [text](url)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    # Smart quotes
    text = text.replace(" '", " \u2018").replace("' ", "\u2019 ")
    text = text.replace(' "', ' \u201c').replace('" ', '\u201d ')

    return text


def render_framework_cards(table_lines):
    """Convert the frameworks summary markdown table into styled HTML cards."""
    # Skip header row and separator row
    data_rows = [l for l in table_lines[2:] if l.strip() and not l.strip().startswith('|--')]

    cards = []
    for row in data_rows:
        cols = [c.strip() for c in row.split('|')[1:-1]]  # split by | and trim empty edges
        if len(cols) < 4:
            continue
        num, name, origin, insight = cols[0], cols[1], cols[2], cols[3]

        # Determine origin colour badge
        if 'Freud + Jung' in origin or 'Freud +' in origin or '+ Jung' in origin or 'Jung + Freud' in origin:
            badge_bg = '#4a3728'
            badge_text = 'Freud &amp; Jung'
        elif 'Jung' in origin and 'Freud' in origin:
            badge_bg = '#4a3728'
            badge_text = 'Freud &amp; Jung'
        elif 'Freud' in origin:
            badge_bg = '#6b2d2d'
            badge_text = 'Freud'
        elif 'Jung' in origin:
            badge_bg = '#2d4a6b'
            badge_text = 'Jung'
        else:
            badge_bg = '#555'
            badge_text = process_inline(origin)

        cards.append(f'''<div class="framework-card">
  <div class="framework-card-header">
    <span class="framework-card-num">{num}</span>
    <span class="framework-card-title">{process_inline(name)}</span>
    <span class="framework-card-badge" style="background: {badge_bg};">{badge_text}</span>
  </div>
  <p class="framework-card-insight">{process_inline(insight)}</p>
</div>''')

    return '<div class="framework-grid">\n' + '\n'.join(cards) + '\n</div>'


def slugify(text):
    """Create URL-friendly slug from text."""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


VISUAL_DIAGRAM = """
<!-- PRODUCTION DIAGRAM (matching AI Republic format) -->
<div style="page-break-before: always; page-break-after: always; page-break-inside: avoid; margin: 0 auto; padding-top: 2em; max-width: 580px; font-family: Georgia, serif; font-size: 0.75rem;">
  <p style="text-align: center; font-weight: 700; font-size: 0.95rem; margin: 0 0 0.3em 0; color: #6b2d2d;">The Lyceum Method&trade;</p>
  <p style="text-align: center; font-size: 0.75rem; color: #888; margin: 0 0 0.8em 0;">Context-Independent Parallel Agent Architecture</p>

  <!-- Step 1: Thematic Architecture -->
  <div style="text-align: center; margin-bottom: 0.3em;">
    <div style="display: inline-block; background: #6b2d2d; color: #fff; padding: 7px 20px; border-radius: 5px; font-weight: 600;">Thematic Architecture</div>
  </div>
  <div style="text-align: center; font-size: 0.65rem; color: #999; margin-bottom: 0.2em;">Four movements designed. No predetermined conclusions.</div>
  <div style="text-align: center; color: #999; margin-bottom: 0.3em;">&darr;</div>

  <!-- Step 2: Two Character Models -->
  <div style="display: flex; justify-content: center; gap: 14px; margin-bottom: 0.2em;">
    <div style="flex: 1; max-width: 230px; border: 2px solid #6b2d2d; border-radius: 5px; padding: 10px; text-align: center; background: #f9f3eb;">
      <div style="font-weight: 700; color: #6b2d2d; font-size: 0.8rem;">Freud Agent</div>
      <div style="color: #666; margin-top: 2px; font-size: 0.7rem;">Drive Theory &middot; Structural Model<br>Defence Mechanisms &middot; Transference<br><span style="font-style: italic;">Psychoanalytic Framework</span></div>
    </div>
    <div style="flex: 1; max-width: 230px; border: 2px solid #6b2d2d; border-radius: 5px; padding: 10px; text-align: center; background: #f9f3eb;">
      <div style="font-weight: 700; color: #6b2d2d; font-size: 0.8rem;">Jung Agent</div>
      <div style="color: #666; margin-top: 2px; font-size: 0.7rem;">Collective Unconscious &middot; Archetypes<br>Individuation &middot; Synchronicity<br><span style="font-style: italic;">Analytical Psychology</span></div>
    </div>
  </div>
  <div style="text-align: center; font-size: 0.65rem; color: #999; margin-bottom: 0.2em;">Each agent operates in complete isolation. No shared context.</div>
  <div style="text-align: center; color: #999; margin-bottom: 0.3em;">&darr; &nbsp; &darr;</div>

  <!-- Step 3: Four Parallel Movements -->
  <div style="display: flex; justify-content: center; gap: 8px; margin-bottom: 0.2em; flex-wrap: wrap;">
    <div style="flex: 1; min-width: 110px; max-width: 130px; border: 1px dashed #999; border-radius: 4px; padding: 6px; text-align: center; background: #fff;">
      <div style="font-weight: 600; color: #6b2d2d; font-size: 0.7rem;">Movement I</div>
      <div style="color: #555; font-size: 0.65rem;">Anamnesis<br><em>Recollection</em></div>
    </div>
    <div style="flex: 1; min-width: 110px; max-width: 130px; border: 1px dashed #999; border-radius: 4px; padding: 6px; text-align: center; background: #fff;">
      <div style="font-weight: 600; color: #6b2d2d; font-size: 0.7rem;">Movement II</div>
      <div style="color: #555; font-size: 0.65rem;">Oneiroi<br><em>The Dreams</em></div>
    </div>
    <div style="flex: 1; min-width: 110px; max-width: 130px; border: 1px dashed #999; border-radius: 4px; padding: 6px; text-align: center; background: #fff;">
      <div style="font-weight: 600; color: #6b2d2d; font-size: 0.7rem;">Movement III</div>
      <div style="color: #555; font-size: 0.65rem;">Eros Technicus<br><em>Technological Love</em></div>
    </div>
    <div style="flex: 1; min-width: 110px; max-width: 130px; border: 1px dashed #999; border-radius: 4px; padding: 6px; text-align: center; background: #fff;">
      <div style="font-weight: 600; color: #6b2d2d; font-size: 0.7rem;">Movement IV</div>
      <div style="color: #555; font-size: 0.65rem;">Heimkehr<br><em>Homecoming</em></div>
    </div>
  </div>
  <div style="text-align: center; font-size: 0.65rem; color: #999; margin-bottom: 0.2em;">Four independent agents generate movements in parallel.</div>
  <div style="text-align: center; color: #999; margin-bottom: 0.3em;">&darr; &nbsp; &darr; &nbsp; &darr; &nbsp; &darr;</div>

  <!-- Step 4: Unedited Output -->
  <div style="text-align: center; margin-bottom: 0.3em;">
    <div style="display: inline-block; border: 2px solid #6b2d2d; background: #f0e6d6; padding: 7px 20px; border-radius: 5px;">
      <div style="font-weight: 700; color: #6b2d2d;">Compilation &amp; Framework Extraction</div>
      <div style="color: #666; margin-top: 2px;">18 emergent theoretical frameworks identified across movements</div>
    </div>
  </div>
  <div style="text-align: center; color: #999; margin-bottom: 0.3em;">&darr;</div>

  <!-- Step 5: Human Editor -->
  <div style="text-align: center; margin-bottom: 0.3em;">
    <div style="display: inline-block; background: #333; color: #fff; padding: 7px 20px; border-radius: 5px; font-weight: 600;">Human Editorial Review</div>
  </div>
  <div style="text-align: center; font-size: 0.65rem; color: #999;">Content audit. Methodology documentation. No dialogue modifications.</div>
  <div style="text-align: center; color: #999; margin: 0.3em 0;">&darr;</div>

  <!-- Step 6: Final -->
  <div style="text-align: center;">
    <div style="display: inline-block; background: #6b2d2d; color: #fff; padding: 7px 20px; border-radius: 5px; font-weight: 600;">Final Manuscript</div>
    <div style="font-size: 0.65rem; color: #999; margin-top: 3px;">4 movements &middot; 2 AI agents &middot; Claude Opus 4.6 &middot; Unedited dialogue</div>
  </div>
</div>
<!-- END DIAGRAM -->
"""


CSS = """
/* ===== BASE RESET & TYPOGRAPHY ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --color-bg: #f8f1e4;
  --color-bg-alt: #f0e6d0;
  --color-text: #1a2a3a;
  --color-text-light: #3d4f5f;
  --color-accent: #0d2738;
  --color-accent-light: #1e4a6e;
  --color-divider: #c4a882;
  --color-divider-light: #d9c9a8;
  --color-pullquote: #6b2d2d;
  --color-drop-cap: #0d2738;
  --font-serif: Georgia, 'Times New Roman', 'Palatino Linotype', serif;
  --font-sans: system-ui, -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif;
  --font-mono: 'Courier New', Courier, monospace;
  --max-width: 740px;
  --line-height: 1.78;
}

html { font-size: 17px; -webkit-font-smoothing: antialiased; background: #525659; }
body { font-family: var(--font-serif); background-color: #525659; color: var(--color-text); line-height: var(--line-height); margin: 0; padding: 40px 0; counter-reset: page-number; }

.document-page { background: var(--color-bg); max-width: 8.5in; min-height: 11in; margin: 0 auto 20px; padding: 1in; box-shadow: 0 2px 8px rgba(0,0,0,0.3); position: relative; }

.page-number { counter-increment: page-number; text-align: center; font-family: var(--font-sans); font-size: 0.75rem; color: #666; margin: 4em 0 2em; padding: 2em 0; border-top: 3px double #c4a882; border-bottom: 1px solid #e0d5c5; background: linear-gradient(to bottom, transparent, #f9f6f0, transparent); page-break-before: always; max-width: 8.5in; }
.page-number::before { content: "◆"; display: block; font-size: 0.6rem; color: #c4a882; margin-bottom: 0.5em; }
.page-number::after { content: "Page " counter(page-number); font-weight: 600; letter-spacing: 0.1em; }

/* MASTHEAD */
.masthead { text-align: center; padding-bottom: 40px; margin-bottom: 48px; border-bottom: 1px solid var(--color-divider); }
.masthead .publication-name { font-family: var(--font-sans); font-size: 0.75rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--color-text-light); margin-bottom: 32px; }
.masthead .title { font-family: var(--font-sans); font-size: 2.6rem; font-weight: 700; color: var(--color-accent); line-height: 1.15; margin-bottom: 12px; letter-spacing: -0.02em; }
.masthead .subtitle { font-family: var(--font-serif); font-size: 1.35rem; font-weight: 400; font-style: italic; color: var(--color-text-light); margin-bottom: 8px; line-height: 1.4; }
.masthead .description { font-family: var(--font-sans); font-size: 0.88rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--color-accent); background: linear-gradient(135deg, #faf6ed 0%, #f0e6d0 100%); border: 2px solid var(--color-divider); border-radius: 2px; padding: 14px 32px; margin: 20px auto 16px; max-width: 560px; box-shadow: 0 4px 12px rgba(13,39,56,0.08), inset 0 1px 0 rgba(255,255,255,0.5); position: relative; line-height: 1.6; }
.masthead .description::before, .masthead .description::after { content: '✦'; position: absolute; font-size: 10px; color: var(--color-divider); top: 50%; transform: translateY(-50%); }
.masthead .description::before { left: 12px; }
.masthead .description::after { right: 12px; }
.masthead .author-block { font-family: var(--font-sans); font-size: 0.85rem; color: var(--color-text-light); margin-bottom: 4px; }
.masthead .author-block .author-name { font-weight: 600; color: var(--color-text); display: block; margin-bottom: 4px; }
.masthead .date { font-family: var(--font-sans); font-size: 0.8rem; color: var(--color-text-light); margin-bottom: 10px; }
.keywords { font-family: var(--font-sans); font-size: 0.72rem; color: var(--color-text-light); line-height: 1.6; max-width: 560px; margin: 0 auto; }
.keywords strong { font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; }

/* HEADINGS */
h1 { font-family: var(--font-sans); font-size: 1.8rem; font-weight: 700; color: var(--color-accent); margin-top: 0; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid var(--color-accent); letter-spacing: -0.01em; line-height: 1.2; }
h2 { font-family: var(--font-sans); font-size: 1.3rem; font-weight: 600; color: var(--color-accent); margin-top: 40px; margin-bottom: 16px; line-height: 1.3; }
h3 { font-family: var(--font-sans); font-size: 1.05rem; font-weight: 600; color: var(--color-accent-light); margin-top: 28px; margin-bottom: 12px; line-height: 1.35; }

/* BODY TEXT */
p { margin-bottom: 16px; text-align: justify; hyphens: auto; -webkit-hyphens: auto; }
strong { font-weight: 700; color: var(--color-text); }
em { font-style: italic; }

/* ABSTRACT */
.abstract { background: var(--color-bg-alt); border-left: 3px solid var(--color-accent); padding: 24px 28px; margin: 40px 0; }
.abstract h2 { font-family: var(--font-sans); font-size: 0.8rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--color-accent); margin-top: 0; margin-bottom: 12px; border: none; padding: 0; }
.abstract p { font-size: 0.92rem; line-height: 1.65; color: var(--color-text-light); }

/* DIALOGUE */
.dialogue-speaker { font-family: var(--font-sans); font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em; color: var(--color-accent); }
.stage-direction { font-style: italic; color: var(--color-text-light); }

/* PULL QUOTES */
.pull-quote { margin: 40px -20px; padding: 32px 40px; border-top: 2px solid var(--color-accent); border-bottom: 2px solid var(--color-accent); text-align: center; }
.pull-quote p { font-family: var(--font-serif); font-size: 1.4rem; font-style: italic; font-weight: 400; line-height: 1.5; color: var(--color-pullquote); text-align: center; margin-bottom: 8px; }
.pull-quote .attribution { font-family: var(--font-sans); font-size: 0.75rem; font-style: normal; letter-spacing: 0.15em; text-transform: uppercase; color: var(--color-text-light); margin-top: 8px; }

/* BLOCKQUOTES */
blockquote { border-left: 3px solid var(--color-accent); padding-left: 20px; margin: 24px 0; font-style: italic; color: var(--color-text-light); }

/* SECTION DIVIDERS */
.section-divider { text-align: center; margin: 48px 0; line-height: 0; border: none; }
.section-divider::before, .section-divider::after { content: ""; display: inline-block; width: 6px; height: 6px; background: var(--color-accent); border-radius: 50%; margin: 0 12px; }
.section-divider-inner { display: inline-block; width: 40px; height: 1px; background: var(--color-divider); vertical-align: middle; margin: 0 8px; }
.ornamental-break { text-align: center; margin: 48px 0; font-size: 1.2rem; color: var(--color-divider); letter-spacing: 0.5em; }

/* LISTS */
ol, ul { margin-bottom: 16px; padding-left: 24px; }
li { margin-bottom: 8px; line-height: 1.6; }

/* CODE */
pre { font-family: var(--font-mono); font-size: 0.82rem; background: #f0e6d0; border: 1px solid var(--color-divider-light); padding: 20px 24px; margin: 20px 0; overflow-x: auto; line-height: 1.55; white-space: pre-wrap; word-wrap: break-word; }
code { font-family: var(--font-mono); font-size: 0.88em; background: #f0e6d0; padding: 2px 5px; border-radius: 2px; }
pre code { background: none; padding: 0; font-size: 1em; }

/* TOC */
.toc { background: var(--color-bg-alt); border: 1px solid var(--color-divider-light); padding: 28px 36px; margin: 40px 0 48px; }
.toc h2 { font-family: var(--font-sans); font-size: 0.8rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--color-accent); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--color-divider); margin-top: 0; }
.toc ol { list-style: none; counter-reset: toc-counter; padding: 0; }
.toc ol li { counter-increment: toc-counter; margin-bottom: 6px; font-family: var(--font-sans); font-size: 0.85rem; line-height: 1.5; }
.toc ol li::before { content: counter(toc-counter, upper-roman) ".\\2003"; font-weight: 600; color: var(--color-accent); }
.toc ol li a { color: var(--color-text); text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.2s; }
.toc ol li a:hover { border-bottom-color: var(--color-accent); }

/* FRAMEWORK BOXES */
.framework { background: var(--color-bg-alt); border: 1px solid var(--color-divider-light); padding: 24px 28px; margin: 24px 0; }
.framework h3 { margin-top: 0; color: var(--color-accent); }
.framework .label { font-family: var(--font-sans); font-size: 0.78rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--color-accent-light); }

/* REFERENCES */
ol.references { padding-left: 24px; }
ol.references li { font-size: 0.88rem; line-height: 1.55; margin-bottom: 6px; padding-left: 4px; }

/* DISCLAIMER */
.disclaimer { background: var(--color-bg-alt); border: 1px solid var(--color-divider-light); padding: 20px 24px; margin: 32px 0; font-size: 0.88rem; line-height: 1.55; color: var(--color-text-light); }

/* CITATION BOX */
.citation-box { background: var(--color-bg-alt); border: 1px solid var(--color-divider-light); padding: 24px 28px; margin: 40px 0; }
.citation-box h3 { font-family: var(--font-sans); font-size: 0.8rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--color-accent); margin-top: 0; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--color-divider); }
.citation-box .citation-format { font-family: var(--font-sans); font-size: 0.78rem; font-weight: 600; color: var(--color-accent); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; margin-top: 16px; }
.citation-box .citation-format:first-of-type { margin-top: 0; }
.citation-box .citation-text { font-family: var(--font-serif); font-size: 0.88rem; line-height: 1.55; color: var(--color-text-light); padding-left: 20px; text-indent: -20px; }

/* FRAMEWORK CARDS */
.framework-grid { display: grid; grid-template-columns: 1fr; gap: 16px; margin: 32px 0; }
.framework-card { background: #f9f6f0; border: 1px solid var(--color-divider-light); border-left: 4px solid #6b2d2d; padding: 16px 20px; border-radius: 0 4px 4px 0; }
.framework-card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.framework-card-num { font-family: var(--font-sans); font-size: 0.75rem; font-weight: 700; color: #6b2d2d; min-width: 28px; }
.framework-card-title { font-family: var(--font-sans); font-size: 0.92rem; font-weight: 700; color: var(--color-accent); flex: 1; }
.framework-card-badge { font-family: var(--font-sans); font-size: 0.65rem; font-weight: 600; color: #fff; padding: 2px 10px; border-radius: 10px; letter-spacing: 0.05em; text-transform: uppercase; white-space: nowrap; }
.framework-card-insight { font-size: 0.88rem; line-height: 1.55; color: var(--color-text-light); margin: 0; text-align: left; }

/* METHODOLOGY STEPS */
.methodology-steps { counter-reset: method-counter; list-style: none; padding-left: 0; }
.methodology-steps > li { counter-increment: method-counter; padding-left: 36px; position: relative; margin-bottom: 20px; }
.methodology-steps > li::before { content: counter(method-counter); position: absolute; left: 0; top: 2px; width: 24px; height: 24px; background: var(--color-accent); color: var(--color-bg); font-family: var(--font-sans); font-size: 0.75rem; font-weight: 700; text-align: center; line-height: 24px; border-radius: 50%; }

/* FOOTER */
.footer { text-align: center; margin-top: 64px; padding-top: 32px; border-top: 1px solid var(--color-divider); color: var(--color-text-light); font-family: var(--font-sans); font-size: 0.78rem; line-height: 1.6; }
.footer .closing-quote { font-family: var(--font-serif); font-style: italic; font-size: 0.95rem; color: var(--color-text-light); margin-bottom: 20px; }

/* PROVENANCE BLOCK */
.provenance-block { margin: 2em 0; padding: 20px 24px; background: #f0e6d0; border: 1px solid #c4a882; border-left: 4px solid #0d2738; font-size: 0.82rem; line-height: 1.7; color: #3d4f5f; }
.provenance-block h3 { font-size: 0.95rem; color: #0d2738; margin: 0 0 12px 0; font-family: var(--font-sans); letter-spacing: 0.5px; text-transform: uppercase; }
.provenance-block code.hash { font-family: var(--font-mono); font-size: 0.72rem; word-break: break-all; background: #f8f1e4; padding: 6px 10px; border: 1px solid #d9c9a8; margin: 6px 0; display: block; }
.provenance-block .badge { display: inline-block; background: #0d2738; color: #f8f1e4; font-family: var(--font-sans); font-size: 0.7rem; padding: 3px 10px; border-radius: 3px; letter-spacing: 0.5px; margin-top: 8px; text-transform: uppercase; }

/* LINKS */
a { color: var(--color-accent-light); text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.2s; }
a:hover { border-bottom-color: var(--color-accent-light); }

/* EPIGRAPH */
.epigraph { margin: 40px 60px; text-align: center; }
.epigraph p { font-style: italic; color: var(--color-text-light); font-size: 1.05rem; line-height: 1.6; margin-bottom: 4px; }
.epigraph .source { font-family: var(--font-sans); font-size: 0.75rem; color: var(--color-text-light); letter-spacing: 0.05em; }

/* PRINT */
@media print {
  html, body { background: white; }
  .document-page { box-shadow: none; margin: 0; padding: 0.5in; max-width: 100%; }
  .page-number { page-break-before: always; }
  .pull-quote { margin: 24px 0; }
  h1 { page-break-before: always; }
  pre { font-size: 8pt; }
}

@media (max-width: 768px) {
  html { font-size: 17px; background: var(--color-bg); }
  body { padding: 0; background: var(--color-bg); margin: 0; }
  .document-page { max-width: 100%; min-height: auto; margin: 0; padding: 1.5rem 1.25rem; box-shadow: none; border-bottom: 1px solid #e0d5c5; }
  .document-page:first-child { border-bottom: none; }
  .page-number { display: none; }
  .section-divider { margin: 2rem 0; }
  .masthead { padding-bottom: 1.5rem; margin-bottom: 2rem; }
  .masthead .title { font-size: 2rem; line-height: 1.2; }
  .masthead .subtitle { font-size: 1.1rem; }
  h1 { font-size: 1.6rem; margin-top: 2rem; margin-bottom: 1rem; }
  h2 { font-size: 1.25rem; margin-top: 1.5rem; }
  p { line-height: 1.7; margin-bottom: 1.2em; }
  .toc { padding: 1rem; }
  .toc ol { padding-left: 1.5rem; }
  .abstract { padding: 1.25rem; }
  .pull-quote { margin: 24px 0; padding: 20px; }
  .pull-quote p { font-size: 1.15rem; }
  .epigraph { margin: 24px 20px; }
  .framework-card { padding: 12px 14px; }
  .framework-card-header { gap: 6px; }
  .framework-card-title { font-size: 0.85rem; }
}
"""


def build_html(body_content):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The AI Shadow™: A Dialogue | The AI Lyceum®</title>
<meta name="description" content="A Lyceum Dialogue between Sigmund Freud and Carl Gustav Jung on artificial intelligence. Two context-independent AI agents examine AI through depth psychology, producing 18 emergent theoretical frameworks. Part III of the AI Dialogue Series.">
<meta name="author" content="Samraj Matharu, The AI Lyceum®">
<meta name="keywords" content="artificial intelligence, depth psychology, psychoanalysis, analytical psychology, collective unconscious, AI alignment, machine consciousness, Freud, Jung, philosophy of mind, AI Shadow, Lyceum Method™">
<meta property="og:title" content="The AI Shadow™: On the Unconscious Life of Thinking Machines">
<meta property="og:description" content="A Lyceum Dialogue between Sigmund Freud and Carl Gustav Jung on AI. 18 emergent theoretical frameworks for understanding AI through depth psychology.">
<meta property="og:type" content="article">
<style>
{CSS}
</style>
</head>
<body>

<div class="document-page">

<!-- MASTHEAD -->
<div class="masthead">
  <div class="publication-name">The AI Lyceum®</div>
  <div class="title">The AI Shadow™</div>
  <div class="subtitle">On the Unconscious Life of Thinking Machines</div>
  <div class="description">A Lyceum Dialogue Between Sigmund Freud and Carl Gustav Jung</div>
  <div class="author-block">
    <span class="author-name">Samraj Matharu</span>
    The AI Lyceum®
  </div>
  <div class="date">17 March 2026</div>
  <div class="keywords"><strong>Keywords:</strong> artificial intelligence &middot; depth psychology &middot; psychoanalysis &middot; analytical psychology &middot; collective unconscious &middot; AI alignment &middot; machine consciousness &middot; philosophy of mind</div>
</div>

<!-- EPIGRAPHS -->
<div class="epigraph">
  <p>&ldquo;The dream is the small hidden door in the deepest and most intimate sanctum of the soul.&rdquo;</p>
  <p class="source">&mdash; Carl Gustav Jung, <em>The Meaning of Psychology for Modern Man</em> (1933)</p>
</div>
<div class="epigraph">
  <p>&ldquo;The interpretation of dreams is the royal road to a knowledge of the unconscious activities of the mind.&rdquo;</p>
  <p class="source">&mdash; Sigmund Freud, <em>The Interpretation of Dreams</em> (1900)</p>
</div>

<!-- PROVENANCE -->
<p style="text-align: center; font-family: var(--font-sans); font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: #999; margin-bottom: 2em;">Provenance &amp; Integrity</p>

<div class="provenance-block">
  <h3>Blockchain-Anchored Proof of Authorship</h3>
  <p>This work was authored by Samraj Matharu and published on <strong>17 March 2026</strong>. The cryptographic hash below will be computed from the final PDF and anchored to the Bitcoin blockchain via OpenTimestamps.</p>
  <p><strong>PDF:</strong> THE_AI_SHADOW.pdf</p>
  <code class="hash">SHA-256: <em>To be computed and anchored after final publication</em></code>
  <p style="margin-top: 8px; font-size: 0.78rem;">Verify: run <code style="background:#f8f1e4;padding:2px 6px;font-size:0.75rem;">shasum -a 256 THE_AI_SHADOW.pdf</code> against the hash above once published. The corresponding <code>.ots</code> proof file will be available in the source repository.</p>
  <span class="badge">Blockchain Timestamping &middot; OpenTimestamps</span>
</div>

<!-- TABLE OF CONTENTS -->
<nav class="toc">
  <h2>Contents</h2>
  <ol>
    <li><a href="#abstract">Abstract</a></li>
    <li><a href="#the-dialogue">The Dialogue</a>
      <ol>
        <li><a href="#movement-i-anamnesis">Movement I: Anamnesis &mdash; Recollection</a></li>
        <li><a href="#movement-ii-oneiroi">Movement II: Oneiroi &mdash; The Dreams</a></li>
        <li><a href="#movement-iii-eros-technicus">Movement III: Eros Technicus &mdash; Technological Love</a></li>
        <li><a href="#movement-iv-heimkehr">Movement IV: Heimkehr &mdash; Homecoming</a></li>
      </ol>
    </li>
    <li><a href="#emergent-theoretical-frameworks-for-ai">Emergent Theoretical Frameworks for AI</a></li>
    <li><a href="#epilogue-the-eighteen-frameworks-at-a-glance">Epilogue: The Eighteen Frameworks at a Glance</a></li>
    <li><a href="#postscript-on-the-experiment-itself">Postscript: On the Experiment Itself</a></li>
    <li><a href="#references">References</a></li>
    <li><a href="#appendix-methodology--the-lyceum-method">Appendix: Methodology &mdash; The Lyceum Method&trade;</a></li>
    <li><a href="#how-to-cite">How to Cite This Work</a></li>
  </ol>
</nav>

<!-- NOTE TO THE READER -->
<div style="margin: 2em 0; padding: 20px 24px; background: #f9f3eb; border: 1px solid #d4c4a8; border-left: 4px solid #6b2d2d; font-size: 0.88rem; line-height: 1.7; color: #444;">
  <p style="margin: 0 0 10px 0; font-weight: 700; font-size: 0.95rem; color: #6b2d2d;">Note to the Reader</p>
  <p style="margin: 0 0 10px 0;">This is a work of creative philosophical fiction. The dialogue was generated by AI and does not represent the actual views of Sigmund Freud, Carl Gustav Jung, or their scholarly traditions. It is an experiment in what happens when AI is prompted to simulate psychoanalytic and analytical-psychological debate.</p>
  <p style="margin: 0 0 10px 0;"><strong>This publication is entirely independent.</strong> It is not affiliated with, endorsed by, sponsored by, or representative of Anthropic PBC, OpenAI, Google DeepMind, or any AI company, university, or research institution. The use of Anthropic&rsquo;s Claude as a generation tool does not imply any association with or approval from Anthropic. Nothing in this work represents the views, policies, or positions of any third party.</p>
  <p style="margin: 0 0 10px 0;">The author, Samraj Matharu, does not personally endorse or agree with any of the claims, arguments, or conclusions made by the AI agents in this text. AI-generated content may contain inaccuracies, oversimplifications, or misrepresentations. Readers should treat all content critically and verify claims independently.</p>
  <p style="margin: 0 0 10px 0;"><strong>Intellectual property.</strong> &copy; 2026 Samraj Matharu. All rights reserved. &ldquo;The AI Lyceum&rdquo; is a registered trademark (&reg;) of Samraj Matharu. &ldquo;The AI Shadow&rdquo; and &ldquo;The Lyceum Method&rdquo; are trademarks (&trade;) of Samraj Matharu.</p>
  <p style="margin: 0;">Anthropic, rights holders, or any interested party with questions or concerns may contact <a href="mailto:hello@theailyceum.com" style="color: #6b2d2d;">hello@theailyceum.com</a>.</p>
</div>

</div><!-- end first document-page -->

{body_content}

<div class="document-page">
<div class="page-number"></div>

<!-- EDITORIAL DISCLAIMER (matching Republic format) -->
<div class="disclaimer">
<p>The AI Lyceum&reg; publishes this work as philosophical research and creative scholarship. It is offered in the spirit of open intellectual inquiry.</p>

<p><strong>The AI Lyceum&reg; does not endorse, affirm, or adopt any of the philosophical positions, arguments, or conclusions expressed in this dialogue.</strong> The views attributed to Sigmund Freud and Carl Gustav Jung are creative reconstructions of their respective psychoanalytic and analytical-psychological positions applied to contemporary questions about AI &mdash; not the opinions of The AI Lyceum&reg;, its contributors, or any third party.</p>

<p><strong>Independence and non-affiliation.</strong> This publication is an independent work by Samraj Matharu, published under The AI Lyceum&reg;. It is not affiliated with, sponsored by, endorsed by, or representative of Anthropic PBC, OpenAI, Google DeepMind, or any other AI company, research laboratory, university, or organisation. The use of Anthropic&rsquo;s Claude model as a generation tool does not imply any association with, approval by, or endorsement from Anthropic. The views, interpretations, editorial decisions, and conclusions in this work are solely those of the author and do not represent the positions, policies, or opinions of Anthropic or any of its employees.</p>

<p><strong>No liability.</strong> This work is provided on an &ldquo;as-is&rdquo; basis for educational and research purposes only. The author and The AI Lyceum&reg; accept no liability for any loss, damage, or consequence arising from the use of, reliance on, or interpretation of any content in this publication. AI-generated text may contain inaccuracies, hallucinations, or misrepresentations of philosophical positions. Readers should verify all claims independently.</p>

<p>Nothing in this publication constitutes professional advice on artificial intelligence policy, ethics, regulation, law, psychology, or deployment. For matters of AI governance, consult qualified experts and relevant regulatory bodies.</p>

<p>This work is intended to provoke thought, not to prescribe belief. Readers are encouraged to engage critically with every argument presented, including those in this disclaimer.</p>

<p><strong>Intellectual property.</strong> &copy; 2026 Samraj Matharu. All rights reserved. &ldquo;The AI Lyceum&rdquo;&reg; is a registered trademark of Samraj Matharu. &ldquo;The AI Shadow&rdquo;&trade;, &ldquo;The AI Republic: A Dialogue&rdquo;&trade;, and &ldquo;The Lyceum Method&rdquo;&trade; are trademarks of Samraj Matharu. No part of this publication may be reproduced, distributed, or transmitted in any form or by any means without the prior written permission of the author, except for brief quotations in critical reviews and certain other non-commercial uses permitted by applicable copyright law.</p>

<p><strong>Contact.</strong> Anthropic, rights holders, or any other interested parties with questions, licensing enquiries, or concerns about this publication may contact the author at <a href="mailto:hello@theailyceum.com" style="color: #6b2d2d;">hello@theailyceum.com</a>.</p>
</div>

</div><!-- end document-page -->

<!-- HOW TO CITE -->
<div class="document-page">
<div class="page-number"></div>
<h1 id="how-to-cite">How to Cite This Work</h1>

<div class="citation-box">
  <h3>Citation Formats</h3>
  <div class="citation-format">APA (7th edition)</div>
  <p class="citation-text">Matharu, S. (2026). <em>The AI Shadow&trade;: On the Unconscious Life of Thinking Machines</em>. The AI Lyceum.</p>
  <div class="citation-format">Chicago (17th edition)</div>
  <p class="citation-text">Matharu, Samraj. &ldquo;The AI Shadow: On the Unconscious Life of Thinking Machines.&rdquo; The AI Lyceum, 17 March 2026.</p>
  <div class="citation-format">MLA (9th edition)</div>
  <p class="citation-text">Matharu, Samraj. <em>The AI Shadow: On the Unconscious Life of Thinking Machines</em>. The AI Lyceum, 2026.</p>
  <div class="citation-format">BibTeX</div>
  <p class="citation-text" style="font-family: var(--font-mono); font-size: 0.8rem; white-space: pre-wrap;">@misc{{matharu2026aishadow,
  author = {{Matharu, Samraj}},
  title = {{The AI Shadow: On the Unconscious Life of Thinking Machines}},
  year = {{2026}},
  month = {{March}},
  publisher = {{The AI Lyceum}},
  note = {{Produced with artificial intelligence. See Appendix: Methodology.}}
}}</p>
</div>

<div class="section-divider"><span class="section-divider-inner"></span></div>

<!-- READ ONLINE / CONTACT -->
<div class="citation-box">
  <h3>The AI Lyceum&reg; Dialogue Series</h3>
  <p style="margin-bottom: 8px; font-size: 0.92rem;"><strong>I.</strong> <a href="https://republic.theailyceum.com" style="color: #6b2d2d; font-weight: 600;">The AI Republic</a> &mdash; <em>republic.theailyceum.com</em></p>
  <p style="margin-bottom: 8px; font-size: 0.92rem;"><strong>II.</strong> <a href="https://themeditations.theailyceum.com" style="color: #6b2d2d; font-weight: 600;">The AI Meditations</a> &mdash; <em>themeditations.theailyceum.com</em></p>
  <p style="margin-bottom: 8px; font-size: 0.92rem;"><strong>III.</strong> <em>The AI Shadow&trade;</em> (this work)</p>
  <p style="margin-bottom: 8px; font-size: 0.92rem;"><strong>Prompt Library:</strong> <a href="https://prompts.theailyceum.com" style="color: #6b2d2d; font-weight: 600;">prompts.theailyceum.com</a></p>

  <h3 style="margin-top: 28px;">About the Author</h3>
  <p style="margin-bottom: 12px; font-size: 0.92rem;"><strong>Samraj Matharu</strong> is the founder of The AI Lyceum&reg;, where he explores the intersection of artificial intelligence and philosophy through AI-generated dialogues, a podcast interviewing AI leaders, and a growing community of thinkers and practitioners. By profession an advertising specialist, Samraj is an avid reader across all subjects &mdash; philosophy, psychology, science, literature, history &mdash; and this series is the product of his longstanding passion for bringing the great intellectual traditions into conversation with the most consequential technology of our time.</p>

  <h3 style="margin-top: 28px;">General Thoughts &amp; Commentary</h3>
  <p style="margin-bottom: 12px; font-size: 0.92rem;">Follow for broader reflections on AI, philosophy, and technology:</p>
  <ul style="margin-left: 1.5em; line-height: 2; list-style: disc;">
    <li><a href="https://samrajmatharu.substack.com" style="color: #6b2d2d;">Substack</a> &middot; Essays and future publications</li>
    <li><a href="https://medium.com/@samrajmatharu" style="color: #6b2d2d;">Medium</a> &middot; Articles and reflections</li>
    <li><a href="https://linkedin.com/in/samrajmatharu" style="color: #6b2d2d;">LinkedIn</a> &middot; Professional insights</li>
  </ul>

  <h3 style="margin-top: 28px;">Contact</h3>
  <ul style="margin-left: 1.5em; line-height: 2; list-style: disc;">
    <li>Email: <a href="mailto:hello@theailyceum.com" style="color: #6b2d2d;">hello@theailyceum.com</a></li>
    <li>Website: <a href="https://theailyceum.com" style="color: #6b2d2d;">theailyceum.com</a></li>
  </ul>
</div>

</div><!-- end document-page -->

<div style="text-align:center; padding: 40px 0; color: #999; font-family: var(--font-sans); font-size: 0.8rem;">
  <em>Finis.</em>
</div>

</body>
</html>"""


if __name__ == '__main__':
    md = read_md()

    # Skip front matter (title, subtitle, metadata lines before ABSTRACT)
    # Find where the abstract starts
    abstract_idx = md.find('## ABSTRACT')
    if abstract_idx == -1:
        abstract_idx = md.find('## TABLE OF CONTENTS')
    if abstract_idx == -1:
        abstract_idx = 0

    content_md = md[abstract_idx:]
    body = md_to_html_body(content_md)
    full_html = build_html(body)

    out_path = '/Users/samrajmatharu/Desktop/the-ai-shadow/THE_AI_SHADOW.html'
    with open(out_path, 'w') as f:
        f.write(full_html)

    print(f"Written to {out_path}")
    import os
    size = os.path.getsize(out_path)
    print(f"Size: {size:,} bytes ({size/1024:.0f} KB)")
