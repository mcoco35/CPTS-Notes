"""
Build GitHub Wiki from the scraped markdown files.
- Flattens directory structure into wiki-compatible flat filenames
- Creates _Sidebar.md for navigation
- Creates Home.md as the landing page
- Rewrites all internal links to use wiki page names
"""

import os
import re
import glob
import shutil

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
WIKI_DIR = os.path.join(SOURCE_DIR, 'wiki_temp')

# Mapping from original relative path to wiki page name
path_to_wiki = {}

# Files to skip
SKIP_FILES = {'scrape_gitbook.py', 'cleanup_notes.py', 'fix_headings.py', 
              'build_wiki.py', 'SUMMARY.md', '.gitignore'}
SKIP_DIRS = {'wiki_temp', '.git', '__pycache__', '.gemini'}


def flatten_path_to_wiki_name(rel_path):
    """Convert a relative file path to a flat wiki page name.
    
    Examples:
        README.md -> Home
        pentest-notes.md -> Pentest-Notes
        pentest-notes/protocols-and-services/port-53-dns.md -> Pentest-Notes-Protocols-and-Services-Port-53-DNS
        ctfs/hack-the-box/linux/easy/sauna.md -> CTFs-Hack-The-Box-Linux-Easy-Sauna
    """
    # Normalize path separators
    rel_path = rel_path.replace('\\', '/')
    
    # Special case for README
    if rel_path == 'README.md':
        return 'Home'
    
    # Remove .md extension
    name = rel_path.replace('.md', '')
    
    # Split into parts
    parts = name.split('/')
    
    # Capitalize each part nicely
    wiki_parts = []
    for part in parts:
        # Split by hyphens, capitalize each word, rejoin
        words = part.split('-')
        capitalized = '-'.join(w.capitalize() if w.lower() not in ('and', 'or', 'the', 'of', 'for', 'to', 'in', 'a') 
                               else w.capitalize()  # capitalize anyway for wiki names
                               for w in words)
        wiki_parts.append(capitalized)
    
    return '-'.join(wiki_parts)


def collect_files():
    """Collect all markdown files and build the path mapping."""
    md_files = []
    
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Filter out skip directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for f in files:
            if f.endswith('.md') and f not in SKIP_FILES:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, SOURCE_DIR)
                wiki_name = flatten_path_to_wiki_name(rel_path)
                path_to_wiki[rel_path] = wiki_name
                md_files.append((full_path, rel_path, wiki_name))
    
    return md_files


def rewrite_links_for_wiki(content, current_rel_path):
    """Rewrite all internal links to use wiki page names."""
    
    def replace_link(match):
        link_text = match.group(1)
        link_target = match.group(2)
        
        # Skip external links, anchors, and image links
        if link_target.startswith('http') or link_target.startswith('#'):
            return match.group(0)
        
        # Skip gitbook image references
        if '~gitbook' in link_target:
            return ''
        
        # Resolve relative path to absolute path from source root
        current_dir = os.path.dirname(current_rel_path)
        
        # Handle anchor in link
        anchor = ''
        if '#' in link_target:
            link_target, anchor = link_target.split('#', 1)
            anchor = '#' + anchor
        
        # Resolve the relative path
        if link_target:
            resolved = os.path.normpath(os.path.join(current_dir, link_target))
            resolved = resolved.replace('\\', '/')
            
            # Look up in our mapping
            # Try with .md extension
            if not resolved.endswith('.md'):
                resolved_md = resolved + '.md'
            else:
                resolved_md = resolved
            
            # Try various path formats
            for try_path in [resolved_md, resolved]:
                norm = try_path.replace('/', '\\')
                if norm in path_to_wiki:
                    wiki_name = path_to_wiki[norm]
                    return f'[[{link_text}|{wiki_name}{anchor}]]'
                # Also try forward slash version
                norm2 = try_path.replace('\\', '/')
                for k, v in path_to_wiki.items():
                    if k.replace('\\', '/') == norm2:
                        return f'[[{link_text}|{v}{anchor}]]'
        
        # If we can't resolve, keep the original but try to make it a wiki link
        return match.group(0)
    
    # Replace markdown links [text](target)
    content = re.sub(r'\[([^\]]*)\]\(([^)]+)\)', replace_link, content)
    
    # Remove broken image refs to ~gitbook
    content = re.sub(r'!\[[^\]]*\]\([^)]*~gitbook[^)]*\)', '', content)
    
    return content


def build_sidebar(md_files):
    """Build the _Sidebar.md navigation."""
    
    sidebar = """### [Home](Home)

---

### Pentest Notes
* [[Pentest Notes|Pentest-Notes]]
  * [[Information Gathering|Pentest-Notes-Information-Gathering]]
  * [[Protocols and Services|Pentest-Notes-Protocols-And-Services]]
"""
    
    # Add protocol sub-pages
    protocol_pages = sorted([
        (wiki, rel) for rel, wiki in path_to_wiki.items()
        if 'protocols-and-services' in rel.replace('\\', '/').lower() 
        and rel.replace('\\', '/').count('/') >= 3
    ], key=lambda x: x[0])
    
    for wiki_name, rel_path in protocol_pages:
        # Get a nice display name from the wiki name
        display = wiki_name.split('-', 4)[-1].replace('-', ' ') if wiki_name.count('-') > 3 else wiki_name.replace('-', ' ')
        # Actually, let's extract from the last segment of the original path
        basename = os.path.basename(rel_path).replace('.md', '').replace('-', ' ').title()
        sidebar += f'    * [[{basename}|{wiki_name}]]\n'
    
    sidebar += """  * [[Web Applications|Pentest-Notes-Web-Applications]]
"""
    # Web attack sub-pages
    web_attack_pages = sorted([
        (wiki, rel) for rel, wiki in path_to_wiki.items()
        if 'web-applications/web-attacks/' in rel.replace('\\', '/').lower()
    ], key=lambda x: x[0])
    for wiki_name, _ in web_attack_pages:
        display = wiki_name.rsplit('-', 1)[-1] if '-' in wiki_name else wiki_name
        basename = os.path.basename(_).replace('.md', '').replace('-', ' ').title()
        sidebar += f'    * [[{basename}|{wiki_name}]]\n'
    
    # Web tech sub-pages
    web_tech_pages = sorted([
        (wiki, rel) for rel, wiki in path_to_wiki.items()
        if 'web-applications/web-technologies/' in rel.replace('\\', '/').lower()
    ], key=lambda x: x[0])
    if web_tech_pages:
        sidebar += '  * [[Web Technologies|Pentest-Notes-Web-Applications-Web-Technologies]]\n'
        for wiki_name, rel in web_tech_pages:
            basename = os.path.basename(rel).replace('.md', '').replace('-', ' ').title()
            sidebar += f'    * [[{basename}|{wiki_name}]]\n'
    
    sidebar += """  * [[Active Directory|Pentest-Notes-Active-Directory-Pentesting]]
"""
    ad_pages = sorted([
        (wiki, rel) for rel, wiki in path_to_wiki.items()
        if 'active-directory-pentesting/' in rel.replace('\\', '/').lower()
        and rel.replace('\\', '/') != 'pentest-notes/active-directory-pentesting'
    ], key=lambda x: x[0])
    for wiki_name, rel in ad_pages:
        basename = os.path.basename(rel).replace('.md', '').replace('-', ' ').title()
        indent = '    ' if rel.replace('\\', '/').count('/') <= 2 else '      '
        sidebar += f'{indent}* [[{basename}|{wiki_name}]]\n'
    
    sidebar += """  * [[Linux Privilege Escalation|Pentest-Notes-Linux-Privilege-Escalation]]
"""
    linux_pe_pages = sorted([
        (wiki, rel) for rel, wiki in path_to_wiki.items()
        if 'linux-privilege-escalation/' in rel.replace('\\', '/').lower()
    ], key=lambda x: x[0])
    for wiki_name, rel in linux_pe_pages:
        basename = os.path.basename(rel).replace('.md', '').replace('-', ' ').title()
        sidebar += f'    * [[{basename}|{wiki_name}]]\n'
    
    sidebar += """  * [[Windows Privilege Escalation|Pentest-Notes-Windows-Privilege-Escalation]]
"""
    win_pe_pages = sorted([
        (wiki, rel) for rel, wiki in path_to_wiki.items()
        if 'windows-privilege-escalation/' in rel.replace('\\', '/').lower()
        and 'cpts' not in rel.replace('\\', '/').lower()
    ], key=lambda x: x[0])
    for wiki_name, rel in win_pe_pages:
        basename = os.path.basename(rel).replace('.md', '').replace('-', ' ').title()
        sidebar += f'    * [[{basename}|{wiki_name}]]\n'
    
    sidebar += """  * [[Bug Bounty Hunting|Pentest-Notes-Bug-Bounty-Hunting]]
    * [[Bug Bounty Tools|Pentest-Notes-Bug-Bounty-Hunting-Bug-Bounty-Tools]]
  * [[Utilities, Scripts and Payloads|Pentest-Notes-Utilities-Scripts-And-Payloads]]
"""
    util_pages = sorted([
        (wiki, rel) for rel, wiki in path_to_wiki.items()
        if 'utilities-scripts-and-payloads/' in rel.replace('\\', '/').lower()
    ], key=lambda x: x[0])
    for wiki_name, rel in util_pages:
        basename = os.path.basename(rel).replace('.md', '').replace('-', ' ').title()
        sidebar += f'    * [[{basename}|{wiki_name}]]\n'
    
    sidebar += """
---

### CTFs
* [[CTFs|Ctfs]]
  * [[Hack The Box|Ctfs-Hack-The-Box]]
    * [[Linux|Ctfs-Hack-The-Box-Linux]]
    * [[Windows|Ctfs-Hack-The-Box-Windows]]
  * [[TryHackMe|Ctfs-Tryhackme]]

---

### Certifications
* [[Road to Certification|My-Certifications]]
  * [[eJPT|My-Certifications-Ejpt]]
  * [[CPTS|My-Certifications-Cpts]]
  * [[OSCP|My-Certifications-Oscp]]

---

### Resources
* [[Resources|Resources]]
  * [[Cheat Sheets|Resources-Cheat-Sheets]]
"""
    cheat_pages = sorted([
        (wiki, rel) for rel, wiki in path_to_wiki.items()
        if 'resources/cheat-sheets/' in rel.replace('\\', '/').lower()
    ], key=lambda x: x[0])
    for wiki_name, rel in cheat_pages:
        basename = os.path.basename(rel).replace('.md', '').replace('-', ' ').title()
        sidebar += f'    * [[{basename}|{wiki_name}]]\n'
    
    return sidebar


def build_home():
    """Build the Home.md landing page."""
    return """# 🏠 CPTS Pentest Notes

> Personal penetration testing notes — cloned and adapted from [x3m1sec's GitBook](https://x3m1sec.gitbook.io/notes)

---

## 📝 Pentest Notes
| Topic | Description |
|-------|-------------|
| [[Information Gathering|Pentest-Notes-Information-Gathering]] | Reconnaissance and enumeration techniques |
| [[Protocols and Services|Pentest-Notes-Protocols-And-Services]] | Port-specific enumeration (DNS, SMB, LDAP, etc.) |
| [[Web Applications|Pentest-Notes-Web-Applications]] | Web attacks, technologies, and fuzzing |
| [[Active Directory|Pentest-Notes-Active-Directory-Pentesting]] | AD enumeration, Kerberos attacks, ACL abuse |
| [[Linux Privilege Escalation|Pentest-Notes-Linux-Privilege-Escalation]] | Linux privesc techniques and checklists |
| [[Windows Privilege Escalation|Pentest-Notes-Windows-Privilege-Escalation]] | Windows privesc techniques and checklists |
| [[Bug Bounty Hunting|Pentest-Notes-Bug-Bounty-Hunting]] | Bug bounty methodology and tools |
| [[Utilities & Payloads|Pentest-Notes-Utilities-Scripts-And-Payloads]] | Shells, file transfers, pivoting, password attacks |

## 🎮 CTFs
| Platform | Link |
|----------|------|
| [[Hack The Box|Ctfs-Hack-The-Box]] | Linux and Windows machine writeups |
| [[TryHackMe|Ctfs-Tryhackme]] | TryHackMe walkthroughs |

## 🎓 Certifications
| Cert | Link |
|------|------|
| [[eJPTv2|My-Certifications-Ejpt]] | eLearnSecurity Junior Penetration Tester |
| [[CPTS|My-Certifications-Cpts]] | HackTheBox Certified Penetration Testing Specialist |
| [[OSCP|My-Certifications-Oscp]] | Offensive Security Certified Professional |

## 📚 Resources
| Resource | Link |
|----------|------|
| [[Cheat Sheets|Resources-Cheat-Sheets]] | Reverse shells, Mimikatz, Hashcat, Kerberoast, etc. |
"""


def main():
    print("Collecting markdown files...")
    md_files = collect_files()
    print(f"  Found {len(md_files)} files")
    
    # Clear wiki directory (keep .git)
    for item in os.listdir(WIKI_DIR):
        if item == '.git':
            continue
        path = os.path.join(WIKI_DIR, item)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    
    print("\nProcessing and copying files to wiki...")
    for full_path, rel_path, wiki_name in sorted(md_files, key=lambda x: x[2]):
        # Read content
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rewrite links for wiki format
        content = rewrite_links_for_wiki(content, rel_path)
        
        # Write to wiki directory with flat name
        wiki_file = os.path.join(WIKI_DIR, wiki_name + '.md')
        with open(wiki_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  {rel_path} -> {wiki_name}.md")
    
    # Build and write sidebar
    print("\nBuilding _Sidebar.md...")
    sidebar = build_sidebar(md_files)
    with open(os.path.join(WIKI_DIR, '_Sidebar.md'), 'w', encoding='utf-8') as f:
        f.write(sidebar)
    
    # Build and write Home page
    print("Building Home.md...")
    home = build_home()
    with open(os.path.join(WIKI_DIR, 'Home.md'), 'w', encoding='utf-8') as f:
        f.write(home)
    
    wiki_files = [f for f in os.listdir(WIKI_DIR) if f.endswith('.md')]
    print(f"\nDone! {len(wiki_files)} wiki pages ready in {WIKI_DIR}")


if __name__ == '__main__':
    main()
