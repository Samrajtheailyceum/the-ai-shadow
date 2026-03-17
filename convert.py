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

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
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

        # Table rows (for the TOC table)
        if line.strip().startswith('|') and not line.strip().startswith('|--'):
            # Skip markdown tables, we handle TOC separately
            i += 1
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
                html_parts.append('<ol>')
            html_parts.append(f'<li>{process_inline(m.group(2))}</li>')
            if i + 1 >= len(lines) or not re.match(r'^\d+\.', lines[i+1].strip()):
                html_parts.append('</ol>')
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


def slugify(text):
    """Create URL-friendly slug from text."""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


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

.document-page { background: var(--color-bg); max-width: 8.5in; min-height: auto; margin: 0 auto 20px; padding: 1in; box-shadow: 0 2px 8px rgba(0,0,0,0.3); position: relative; }

.page-number { counter-increment: page-number; text-align: center; font-family: var(--font-sans); font-size: 0.75rem; color: #666; margin: 0 auto; padding: 2em 0; max-width: 8.5in; }
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
.stage-direction { font-style: italic; color: var(--color-text-light); margin: 24px 0; padding: 16px 24px; background: rgba(240,230,208,0.5); border-radius: 4px; }

/* PULL QUOTES */
.pull-quote { margin: 40px -20px; padding: 32px 40px; border-top: 2px solid var(--color-accent); border-bottom: 2px solid var(--color-accent); text-align: center; }
.pull-quote p { font-family: var(--font-serif); font-size: 1.4rem; font-style: italic; font-weight: 400; line-height: 1.5; color: var(--color-pullquote); text-align: center; margin-bottom: 8px; }
.pull-quote .attribution { font-family: var(--font-sans); font-size: 0.75rem; font-style: normal; letter-spacing: 0.15em; text-transform: uppercase; color: var(--color-text-light); margin-top: 8px; }

/* BLOCKQUOTES */
blockquote { border-left: 3px solid var(--color-accent); padding-left: 20px; margin: 24px 0; font-style: italic; color: var(--color-text-light); }

/* ORNAMENTAL BREAKS */
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
  html { font-size: 15px; }
  .document-page { padding: 24px 20px; margin: 0 8px 16px; }
  .masthead .title { font-size: 1.8rem; }
  .pull-quote { margin: 24px 0; padding: 20px; }
  .pull-quote p { font-size: 1.15rem; }
  .stage-direction { padding: 12px 16px; }
  .epigraph { margin: 24px 20px; }
}
"""


def build_html(body_content):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The AI Shadow: A Dialogue | The AI Lyceum™</title>
<meta name="description" content="A Lyceum Dialogue between Sigmund Freud and Carl Gustav Jung on artificial intelligence. Two context-independent AI agents examine AI through depth psychology, producing 18 emergent theoretical frameworks. Part III of the AI Dialogue Series.">
<meta name="author" content="Samraj Matharu, The AI Lyceum™">
<meta name="keywords" content="artificial intelligence, depth psychology, psychoanalysis, analytical psychology, collective unconscious, AI alignment, machine consciousness, Freud, Jung, philosophy of mind, AI Shadow, Lyceum Method™">
<meta property="og:title" content="The AI Shadow: On the Unconscious Life of Thinking Machines">
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
  <div class="publication-name">The AI Lyceum™</div>
  <div class="title">The AI Shadow</div>
  <div class="subtitle">On the Unconscious Life of Thinking Machines</div>
  <div class="description">A Lyceum Dialogue Between Sigmund Freud and Carl Gustav Jung</div>
  <div class="author-block">
    <span class="author-name">Samraj Matharu</span>
    The AI Lyceum™
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

<!-- TABLE OF CONTENTS -->
<div class="toc">
  <h2>Contents</h2>
  <ol>
    <li><a href="#abstract">Abstract</a></li>
    <li><a href="#prolegomenon-on-method">Prolegomenon: On Method</a></li>
    <li><a href="#the-lyceum-protocol-agent-architecture">The Lyceum Protocol: Agent Architecture</a></li>
    <li><a href="#the-agent-prompts">The Agent Prompts</a></li>
    <li><a href="#movement-i-anamnesis">Movement I: Anamnesis &mdash; Recollection</a></li>
    <li><a href="#movement-ii-oneiroi">Movement II: Oneiroi &mdash; The Dreams</a></li>
    <li><a href="#movement-iii-eros-technicus">Movement III: Eros Technicus &mdash; Technological Love</a></li>
    <li><a href="#movement-iv-heimkehr">Movement IV: Heimkehr &mdash; Homecoming</a></li>
    <li><a href="#emergent-theoretical-frameworks-for-ai">Emergent Theoretical Frameworks for AI</a></li>
    <li><a href="#postscript-on-the-experiment-itself">Postscript: On the Experiment Itself</a></li>
  </ol>
</div>

</div><!-- end first document-page -->

{body_content}

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
