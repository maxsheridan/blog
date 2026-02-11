import os
import shutil
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import markdown
import re
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

class BlogBuilder:
    def copy_feed_xsl(self):
        """Copy feed.xsl from assets to public folder"""
        src = self.assets_dir / 'feed.xsl'
        dst = self.output_dir / 'feed.xsl'
        if src.exists():
            shutil.copy2(src, dst)
            print(f"Copied {src} to {dst}")
        else:
            print(f"Warning: {src} does not exist. Skipping feed.xsl copy.")
    
    def __init__(self):
        self.root = Path(__file__).parent
        self.content_dir = self.root / 'content'
        self.templates_dir = self.root / 'templates'
        self.output_dir = self.root / 'public'
        self.posts_dir = self.content_dir / 'posts'
        self.pages_dir = self.content_dir / 'pages'
        self.assets_dir = self.root / 'assets'
        
        # Configuration
        self.posts_per_page = 10
        self.site_url = 'https://blog.maxsheridan.com'
        self.site_title = 'This Is A Blog'
        self.site_description = 'Where I write, think, and ramble, but mostly ramble.'
        
        # Setup Jinja2
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.env.filters['format_date'] = self.format_date
        self.env.filters['slugify'] = self.slugify
        self.env.globals['current_year'] = datetime.now().year
        
        self.posts = []
        self.categories = {}
    
    def format_date(self, date_str):
        """Convert YYYY-MM-DD to 'Oct 23, 2025' format"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%b %d, %Y')
    
    def slugify(self, text):
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    def parse_frontmatter(self, content):
        """Extract YAML frontmatter from markdown content.
        More robust version that handles quoted values."""
        frontmatter = {}
        lines = content.split('\n')
        
        if lines[0].strip() == '---':
            i = 1
            while i < len(lines) and lines[i].strip() != '---':
                line = lines[i].strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"')
                i += 1
            
            content_start = i + 1
            remaining_content = '\n'.join(lines[content_start:]).strip()
            return frontmatter, remaining_content
        
        return {}, content
    
    def wrap_images_with_captions(self, html_content):
        """Convert <img><em>caption</em> patterns to <figure><img><figcaption>"""
        # Pattern: <p><img...><em class="with-caption">caption</em></p>
        pattern = r'<p>(<img[^>]+>)<em class="with-caption">([^<]+)</em></p>'
        replacement = r'<figure class="with-caption">\n    \1\n    <figcaption>\2</figcaption>\n</figure>'
        html_content = re.sub(pattern, replacement, html_content)
        
        # Also handle without class (fallback for any img+em pattern)
        pattern = r'<p>(<img[^>]+>)<em>([^<]+)</em></p>'
        def replace_fn(match):
            # Only replace if not already in a figure
            return f'<figure>\n    {match.group(1)}\n    <figcaption>{match.group(2)}</figcaption>\n</figure>'
        html_content = re.sub(pattern, replace_fn, html_content)
        
        return html_content
    
    def format_html_elements(self, html_content):
        """Format HTML elements with proper indentation for readability"""
        # Format paragraphs: <p>text</p> -> <p>\n    text\n</p>
        html_content = re.sub(r'<p>([^<]+)</p>', r'<p>\n    \1\n</p>', html_content)
        
        # Format list items: <li>text</li> -> <li>\n    text\n</li>
        html_content = re.sub(r'<li>([^<]+)</li>', r'<li>\n    \1\n</li>', html_content)
        
        # Format headings: <h2>text</h2> -> <h2>\n    text\n</h2>
        html_content = re.sub(r'<h2>([^<]+)</h2>', r'<h2>\n    \1\n</h2>', html_content)
        html_content = re.sub(r'<h3>([^<]+)</h3>', r'<h3>\n    \1\n</h3>', html_content)
        
        return html_content
    
    def load_posts(self):
        """Load all posts from content/posts directory"""
        if not self.posts_dir.exists():
            print(f"Warning: {self.posts_dir} does not exist")
            return
        
        for md_file in sorted(self.posts_dir.glob('*.md'), reverse=True):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter, body = self.parse_frontmatter(content)
            html_content = markdown.markdown(body, extensions=['attr_list'])
            html_content = self.wrap_images_with_captions(html_content)
            html_content = self.format_html_elements(html_content)
            
            post = {
                'title': frontmatter.get('title', 'Untitled'),
                'subtitle': frontmatter.get('subtitle', ''),
                'date': frontmatter.get('date', ''),
                'category': frontmatter.get('category', 'Uncategorized'),
                'content': html_content,
                'slug': md_file.stem,
                'url': f'/posts/{md_file.stem}/',
                'full_url': f'{self.site_url}/posts/{md_file.stem}/'
            }
            
            self.posts.append(post)
            
            # Group by category
            category = post['category']
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(post)
    
    def paginate(self, items, per_page=10):
        """Split items into pages"""
        pages = []
        for i in range(0, len(items), per_page):
            pages.append(items[i:i + per_page])
        return pages
    
    def build_posts(self):
        """Generate individual post pages"""
        template = self.env.get_template('post.html')
        
        count = 0
        total_posts = len(self.posts)
        for i, post in enumerate(self.posts):
            # Calculate post numbers (reversed since posts are sorted newest first)
            current_number = str(total_posts - i).zfill(2)
            
            # Determine previous and next posts
            prev_post = self.posts[i + 1] if i < len(self.posts) - 1 else None
            next_post = self.posts[i - 1] if i > 0 else None
            
            # Add post numbers to prev/next posts
            if prev_post:
                prev_post = dict(prev_post)
                prev_post['number'] = str(total_posts - (i + 1)).zfill(2)
            if next_post:
                next_post = dict(next_post)
                next_post['number'] = str(total_posts - (i - 1)).zfill(2)
            
            html = template.render(
                post=post,
                prev_post=prev_post,
                next_post=next_post,
                page_title=f"{post['title']} - Max Sheridan",
                canonical_url=post['full_url']
            )
            
            # Write to output
            output_path = self.output_dir / 'posts' / post['slug']
            output_path.mkdir(parents=True, exist_ok=True)
            
            with open(output_path / 'index.html', 'w', encoding='utf-8') as f:
                f.write(self.indent_html(html))
            count += 1

        print(f"✓ Built {count} post pages")
    
    def build_index(self):
        """Generate homepage index with pagination"""
        template = self.env.get_template('index.html')
        pages = self.paginate(self.posts, self.posts_per_page)
        
        for page_num, page_posts in enumerate(pages, 1):
            pagination = {
                'current': page_num,
                'total': len(pages),
                'has_prev': page_num > 1,
                'has_next': page_num < len(pages),
                'prev_url': '/index.html' if page_num == 2 else f'/page-{page_num - 1}.html',
                'next_url': f'/page-{page_num + 1}.html'
            }
            
            # Determine page title and canonical URL
            if page_num == 1:
                page_title = "This Is A Blog"
                canonical_url = self.site_url
            else:
                page_title = f"This Is A Blog - Page {page_num}"
                canonical_url = f"{self.site_url}/page-{page_num}.html"
            
            html = template.render(
                intro="Where I write, think, and ramble, but mostly ramble.",
                posts=page_posts,
                title="Home",
                pagination=pagination,
                page_title=page_title,
                canonical_url=canonical_url
            )
            
            if page_num == 1:
                output_file = self.output_dir / 'index.html'
            else:
                output_file = self.output_dir / f'page-{page_num}.html'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(self.indent_html(html))
        # Report how many index pages were written (homepage + paginated pages)
        print(f"✓ Built {len(pages)} index page(s)")
    
    def build_category_pages(self):
        """Generate category index pages with pagination"""
        template = self.env.get_template('index.html')
        
        total = 0
        for category, posts in self.categories.items():
            category_slug = self.slugify(category)
            pages = self.paginate(posts, self.posts_per_page)
            
            for page_num, page_posts in enumerate(pages, 1):
                pagination = {
                    'current': page_num,
                    'total': len(pages),
                    'has_prev': page_num > 1,
                    'has_next': page_num < len(pages),
                    'prev_url': f'/category-{category_slug}/' if page_num == 2 else f'/category-{category_slug}-page-{page_num - 1}/',
                    'next_url': f'/category-{category_slug}-page-{page_num + 1}/'
                }
                
                # Determine page title and canonical URL
                if page_num == 1:
                    page_title = f"{category} - This Is A Blog"
                    canonical_url = f"{self.site_url}/category-{category_slug}/"
                else:
                    page_title = f"{category} - Page {page_num} - This Is A Blog"
                    canonical_url = f"{self.site_url}/category-{category_slug}-page-{page_num}/"
                
                html = template.render(
                    intro=f"Posts in {category}",
                    posts=page_posts,
                    title=category,
                    is_category=True,
                    pagination=pagination,
                    page_title=page_title,
                    canonical_url=canonical_url
                )
                
                if page_num == 1:
                    output_file = self.output_dir / f'category-{category_slug}' / 'index.html'
                else:
                    output_file = self.output_dir / f'category-{category_slug}-page-{page_num}' / 'index.html'
                
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(self.indent_html(html))
                total += 1
        # Report how many category pages were written in total
        print(f"✓ Built {total} category page(s)")

    def build_pages(self):
        """Generate static pages from content/pages"""
        if not self.pages_dir.exists():
            print(f"Warning: {self.pages_dir} does not exist")
            return
        
        template = self.env.get_template('page.html')
        count = 0
        
        for md_file in self.pages_dir.glob('*.md'):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter, body = self.parse_frontmatter(content)
            html_content = markdown.markdown(body, extensions=['attr_list'])
            html_content = self.wrap_images_with_captions(html_content)
            html_content = self.format_html_elements(html_content)
            
            page = {
                'title': frontmatter.get('title', md_file.stem.title()),
                'content': html_content
            }
            
            page_title = f"{page['title']} - This Is A Blog"
            canonical_url = f"{self.site_url}/{md_file.stem}.html"
            
            html = template.render(
                page=page,
                page_title=page_title,
                canonical_url=canonical_url
            )
            
            with open(self.output_dir / f'{md_file.stem}.html', 'w', encoding='utf-8') as f:
                f.write(self.indent_html(html))
            
            count += 1
        
        print(f"✓ Built {count} static pages")
    
    def indent_html(self, content):
        """Add indentation to HTML content"""
        import re
        lines = content.split('\n')
        indent = 0
        result = []
        in_pre = False
        
        # List of HTML void elements
        void_elements = {'meta', 'link', 'img', 'br', 'hr', 'input', 'area', 'base', 'col', 'embed', 'param', 'source', 'track', 'wbr'}
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result.append('')
                continue
            
            # Check if we're entering or leaving a pre block
            if '<pre' in stripped.lower():
                in_pre = True
            elif '</pre>' in stripped.lower():
                in_pre = False
            
            # Don't process pre blocks
            if in_pre:
                result.append('    ' * indent + stripped)
                continue
            
            # Don't indent doctype
            if stripped.startswith('<!DOCTYPE'):
                result.append(stripped)
                continue
            
            # Process closing tags at the start of line
            if stripped.startswith('</'):
                indent = max(0, indent - 1)
            
            # Apply current indentation
            result.append('    ' * indent + stripped)
            
            # Process all tags for next line's indentation
            tags = re.findall(r'<[^>]+>', stripped)
            for tag in tags:
                tag_lower = tag.lower()
                
                # Handle closing tags
                if tag.startswith('</'):
                    if not stripped.startswith('</'):  # Already handled at start of line
                        indent = max(0, indent - 1)
                # Handle self-closing or void elements
                elif '/>' in tag or any(f'<{elem}' in tag_lower for elem in void_elements):
                    continue
                # Handle opening tags
                elif tag.startswith('<') and not tag.startswith('<!'):
                    indent += 1
        
        return '\n'.join(result)
    
    def build_rss(self):
        """Generate RSS feed"""
        rss = Element('rss', version='2.0', attrib={
            'xmlns:atom': 'http://www.w3.org/2005/Atom'
        })
        channel = SubElement(rss, 'channel')
        
        # Channel info
        SubElement(channel, 'title').text = self.site_title
        SubElement(channel, 'link').text = self.site_url
        SubElement(channel, 'description').text = self.site_description
        SubElement(channel, 'language').text = 'en-us'
        SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        
        # Self link
        SubElement(channel, 'atom:link', href=f'{self.site_url}/feed.xml', rel='self', type='application/rss+xml')
        
        # Add posts (last 20)
        for post in self.posts[:20]:
            item = SubElement(channel, 'item')
            SubElement(item, 'title').text = post['title']
            SubElement(item, 'link').text = post['full_url']
            SubElement(item, 'guid', isPermaLink='true').text = post['full_url']
            SubElement(item, 'category').text = post['category']
            
            # Format date for RSS (RFC 822)
            if post['date']:
                date_obj = datetime.strptime(post['date'], '%Y-%m-%d')
                SubElement(item, 'pubDate').text = date_obj.strftime('%a, %d %b %Y 00:00:00 +0000')
        
        # Pretty print XML
        xml_str = minidom.parseString(tostring(rss)).toprettyxml(indent='  ')
        # Insert xml-stylesheet processing instruction after XML declaration
        lines = xml_str.splitlines()
        if lines and lines[0].startswith('<?xml'):
            lines.insert(1, f'<?xml-stylesheet type="text/xsl" href="{self.site_url}/feed.xsl"?>')
        xml_str = '\n'.join(lines)
        with open(self.output_dir / 'feed.xml', 'w', encoding='utf-8') as f:
            f.write(xml_str)
        print("✓ Built RSS feed")
    
    def build_sitemap(self):
        """Generate sitemap.xml"""
        urlset = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # Homepage
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = self.site_url
        SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
        SubElement(url, 'priority').text = '1.0'
        SubElement(url, 'changefreq').text = 'daily'
        
        # Posts
        for post in self.posts:
            url = SubElement(urlset, 'url')
            SubElement(url, 'loc').text = post['full_url']
            if post['date']:
                SubElement(url, 'lastmod').text = post['date']
            SubElement(url, 'priority').text = '0.8'
            SubElement(url, 'changefreq').text = 'monthly'
        
        # Category pages
        for category in self.categories.keys():
            category_slug = self.slugify(category)
            url = SubElement(urlset, 'url')
            SubElement(url, 'loc').text = f"{self.site_url}/category-{category_slug}/"
            SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
            SubElement(url, 'priority').text = '0.6'
            SubElement(url, 'changefreq').text = 'weekly'
        
        # Static pages
        if self.pages_dir.exists():
            for md_file in self.pages_dir.glob('*.md'):
                url = SubElement(urlset, 'url')
                SubElement(url, 'loc').text = f"{self.site_url}/{md_file.stem}.html"
                SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
                SubElement(url, 'priority').text = '0.5'
                SubElement(url, 'changefreq').text = 'monthly'
        
        # Pretty print XML
        xml_str = minidom.parseString(tostring(urlset)).toprettyxml(indent='  ')
        # Remove extra blank lines
        xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])
        
        with open(self.output_dir / 'sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        print("✓ Built sitemap")
    
    def clean_output(self):
        """Remove old build files"""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def copy_static_assets(self):
        """Copy the assets directory into the public folder and ensure favicons at site root.

        - Copies `assets/` -> `public/assets/` so templates can reference `/assets/...`.
        - If a `favicon.ico` exists at project root or in `assets/favicons/`, copy it to `public/favicon.ico`.
        - If a `favicon.svg` exists at project root or in `assets/favicons/`, copy it to `public/favicon.svg`.
        """
        src = self.root / 'assets'
        dst = self.output_dir / 'assets'
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

        # Ensure favicon.ico at site root if available
        # Prefer project root, then assets/favicons
        candidates = [self.root / 'favicon.ico', self.root / 'assets' / 'favicons' / 'favicon.ico']
        for cand in candidates:
            if cand.exists():
                shutil.copy2(cand, self.output_dir / 'favicon.ico')
                break

        # Also copy svg favicon if present
        svg_candidates = [self.root / 'favicon.svg', self.root / 'assets' / 'favicons' / 'favicon.svg']
        for cand in svg_candidates:
            if cand.exists():
                shutil.copy2(cand, self.output_dir / 'favicon.svg')
                break
    
    def build_cname(self):
        """Create CNAME file for GitHub Pages custom domain"""
        cname_path = self.output_dir / 'CNAME'
        with open(cname_path, 'w', encoding='utf-8') as f:
            f.write('blog.maxsheridan.com')
    
    def build(self):
        """Main build process"""
        print("🔨 Starting build...\n")
        
        self.clean_output()
        # Copy static assets (CSS, images, favicons) into the output directory
        self.copy_static_assets()
        self.load_posts()
        self.build_posts()
        self.build_index()
        self.build_category_pages()
        self.build_pages()
        self.build_rss()
        self.build_sitemap()
        self.build_cname()
        
        self.copy_feed_xsl()
        print("\n✨ Build complete!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📡 RSS feed: {self.output_dir}/feed.xml")
        print(f"🗺️  Sitemap: {self.output_dir}/sitemap.xml")

if __name__ == '__main__':
    builder = BlogBuilder()
    builder.build()