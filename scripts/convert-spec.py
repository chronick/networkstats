#!/usr/bin/env python3
"""
convert-spec.py

Splits each markdown file in a directory into logical subfiles by H2 (##) sections.
Output is placed in <output-dir>/<basename>/<section>.md

Usage:
    python scripts/convert-spec.py [OPTIONS]

Options:
    --output-dir PATH   Output directory (default: docs/spec)
    --pattern PATTERN   Glob pattern for input files (default: *.md)
    --skip NAME         Filename to skip (default: index.md)
    --dry-run           Print what would be written, don't write files
    --verbose           Print extra output

Example:
    python scripts/convert-spec.py --output-dir docs/spec --dry-run --verbose
"""
import sys
import os
import re
import click
import glob
from pathlib import Path
from markdown_it import MarkdownIt
import yaml  # For future YAML frontmatter support
import copy


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def promote_heading_token(token, in_section=False):
    """Promote heading level by one. H3->H2, H2->H1, H1->H1 (or H2 if in section)."""
    t = copy.deepcopy(token)
    if t.type in ("heading_open", "heading_close"):
        level = int(t.tag[1])
        if level == 1:
            # Only promote H1 if inside a section (not the doc's main H1)
            new_level = 2 if in_section else 1
        else:
            new_level = max(1, level - 1)
        t.tag = f"h{new_level}"
    return t

def split_markdown(input_path, output_dir, dry_run=False, verbose=False):
    input_path = Path(input_path)
    base = input_path.stem
    outdir = Path(output_dir) / base
    if not dry_run:
        outdir.mkdir(exist_ok=True)
    with input_path.open('r', encoding='utf-8') as f:
        content = f.read()
    md = MarkdownIt()
    tokens = md.parse(content)
    # Find H1 for context
    h1_title = None
    for t in tokens:
        if t.type == 'heading_open' and t.tag == 'h1':
            idx = tokens.index(t)
            h1_title = tokens[idx+1].content.strip()
            break
    # Split by H2
    sections = []
    current = []
    current_title = None
    for i, t in enumerate(tokens):
        if t.type == 'heading_open' and t.tag == 'h2':
            if current:
                sections.append((current_title, current))
            current = [t]
            current_title = tokens[i+1].content.strip()
        elif current is not None:
            current.append(t)
    if current:
        sections.append((current_title, current))
    # Write each section
    for title, toks in sections:
        if not title:
            continue
        slug = slugify(title)
        outpath = outdir / f"{slug}.md"
        # Compose new H1 for the section
        if h1_title:
            new_h1 = f"# {h1_title}: {title}\n\n"
        else:
            new_h1 = f"# {title}\n\n"
        # Render tokens to markdown, promoting headings
        section_md = new_h1
        skip_next = False
        for t in toks:
            if skip_next:
                skip_next = False
                continue
            if t.type == 'heading_open' and t.tag == 'h2':
                skip_next = True
                continue
            # Promote headings inside section
            t_promoted = promote_heading_token(t, in_section=True)
            if t_promoted.type == 'heading_open':
                section_md += f"{'#' * int(t_promoted.tag[1])} "
            if hasattr(t_promoted, 'content') and t_promoted.content:
                section_md += t_promoted.content
            if t_promoted.type == 'heading_close':
                section_md += '\n\n'
            elif t_promoted.type == 'paragraph_close':
                section_md += '\n\n'
            elif t_promoted.type == 'softbreak':
                section_md += '\n'
            elif t_promoted.type == 'hardbreak':
                section_md += '\n\n'
            elif t_promoted.type == 'fence':
                # Code block
                info = t_promoted.info or ''
                section_md += f"\n```{info}\n{t_promoted.content}\n```\n\n"
        if dry_run or verbose:
            click.echo(f"Would write {outpath}" if dry_run else f"Writing {outpath}")
        if not dry_run:
            with open(outpath, 'w', encoding='utf-8') as f:
                f.write(section_md.strip() + '\n')
    # Special: also write an index.md for the H1 and intro (before first H2)
    intro = []
    for t in tokens:
        if t.type == 'heading_open' and t.tag == 'h2':
            break
        intro.append(t)
    if intro:
        outpath = outdir / 'index.md'
        section_md = ''
        for t in intro:
            # Promote headings in intro (but H1 stays H1)
            t_promoted = promote_heading_token(t, in_section=False)
            if t_promoted.type == 'heading_open':
                section_md += f"{'#' * int(t_promoted.tag[1])} "
            if t_promoted.type == 'heading_open' and t_promoted.tag == 'h1':
                section_md += f"{h1_title}: Overview\n\n"
                continue
            if hasattr(t_promoted, 'content') and t_promoted.content:
                section_md += t_promoted.content
            if t_promoted.type == 'heading_close':
                section_md += '\n\n'
            elif t_promoted.type == 'paragraph_close':
                section_md += '\n\n'
            elif t_promoted.type == 'softbreak':
                section_md += '\n'
            elif t_promoted.type == 'hardbreak':
                section_md += '\n\n'
            elif t_promoted.type == 'fence':
                info = t_promoted.info or ''
                section_md += f"\n```{info}\n{t_promoted.content}\n```\n\n"
        if dry_run or verbose:
            click.echo(f"Would write {outpath}" if dry_run else f"Writing {outpath}")
        if not dry_run:
            with open(outpath, 'w', encoding='utf-8') as f:
                f.write(section_md.strip() + '\n')

@click.command()
@click.option('--output-dir', default='docs/spec', show_default=True, help='Output directory')
@click.option('--pattern', default='*.md', show_default=True, help='Glob pattern for input files')
@click.option('--skip', default='index.md', show_default=True, help='Filename to skip')
@click.option('--dry-run', is_flag=True, help="Print what would be written, don't write files")
@click.option('--verbose', is_flag=True, help='Print extra output')
def main(output_dir, pattern, skip, dry_run, verbose):
    """Split markdown spec files into logical subfiles by H2 sections."""
    input_dir = Path(output_dir)
    files = sorted(glob.glob(str(input_dir / pattern)))
    for f in files:
        if Path(f).name == skip:
            if verbose:
                click.echo(f"Skipping {f}")
            continue
        click.echo(f"Processing {f} ...")
        split_markdown(f, output_dir, dry_run=dry_run, verbose=verbose)

if __name__ == '__main__':
    main() 