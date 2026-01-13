<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:atom="http://www.w3.org/2005/Atom">
    <xsl:output method="html" encoding="UTF-8" indent="yes"/>
    <xsl:template match="/">
        <html lang="en">
            <head>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1, interactive-widget=resizes-content"/>
                <meta name="color-scheme" content="light dark"/>
                <link rel="stylesheet" href="/assets/css/style.css"/>
                <title>Feed - This Is A Blog</title>
                <style>.subscribe{width:max-content;padding:.75rem 1rem;margin-block-start:var(--space-2);margin-block-end:var(--space-2);border:1px solid var(--accent);border-radius:1rem;box-shadow:0 2px 6px rgba(0,0,0,.05);font-family:monospace;font-size:calc(.9rem + .15vw);word-break:break-all;color:var(--background);background:var(--primary);cursor:pointer;transition:background .2s ease}.subscribe:hover{opacity:.6}h1 + p{margin-block-start: var(--space-0)}</style>
            </head>
            <body>
                <header>
                    <a class="skip-link" href="#main">Skip to main content</a>
                    <a class="site-title" href="/">This Is A Blog</a>
                    <nav aria-label="Links">
                        <ul>
                            <li><a aria-label="Max Sheridan main website" href="https://maxsheridan.com">Website</a></li>
                            <li class="separator" aria-hidden="true"></li>
                            <li><button aria-label="Copy email address" id="copyLink" type="button" onclick="copyEmail()">Email</button></li>
                        </ul>
                    </nav>
                </header>
                <main id="main" tabindex="-1">
                    <h1>RSS</h1>
                    <p class="index-intro big">This is an old-school RSS feed. Copy the URL below and paste it into your feed reader and you’re set.
                    Or click on a link to read my latest posts.</p>
                    <p class="subscribe" onclick="copyToClipboard(this)"><xsl:value-of select="/rss/channel/atom:link/@href"/></p>                    
                    <ul class="index-list">
                        <xsl:for-each select="/rss/channel/item">
                            <li>
                                <div class="link">
                                    <a href="{link}"><span><xsl:value-of select="title"/>
                                        <svg class="arrow" aria-hidden="true" viewBox="0 0 40 40" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M0 37.07 36.9.16l2.94 2.93L2.94 40z"/><path d="M35.85 0H40v31.14h-4.15z"/><path d="M8.87 0H40v4.15H8.87z"/></svg>
                                    </span></a>
                                </div>
                                <div class="meta" aria-label="Date and category">
                                    <span class="date">
                                        <xsl:variable name="date" select="pubDate"/>
                                        <xsl:variable name="day" select="substring($date, 6, 2)"/>
                                        <xsl:variable name="month" select="substring($date, 9, 3)"/>
                                        <xsl:variable name="year" select="substring($date, 13, 4)"/>
                                        <xsl:value-of select="normalize-space($day)"/>
                                        <xsl:text> </xsl:text>
                                        <xsl:choose>
                                            <xsl:when test="$month='Jan'">JAN</xsl:when>
                                            <xsl:when test="$month='Feb'">FEB</xsl:when>
                                            <xsl:when test="$month='Mar'">MAR</xsl:when>
                                            <xsl:when test="$month='Apr'">APR</xsl:when>
                                            <xsl:when test="$month='May'">MAY</xsl:when>
                                            <xsl:when test="$month='Jun'">JUN</xsl:when>
                                            <xsl:when test="$month='Jul'">JUL</xsl:when>
                                            <xsl:when test="$month='Aug'">AUG</xsl:when>
                                            <xsl:when test="$month='Sep'">SEP</xsl:when>
                                            <xsl:when test="$month='Oct'">OCT</xsl:when>
                                            <xsl:when test="$month='Nov'">NOV</xsl:when>
                                            <xsl:when test="$month='Dec'">DEC</xsl:when>
                                            <xsl:otherwise><xsl:value-of select="$month"/></xsl:otherwise>
                                        </xsl:choose>
                                        <xsl:text>, </xsl:text>
                                        <xsl:value-of select="$year"/>
                                    </span>
                                    <span class="category" aria-label="Category link">
                                        <a href="{concat('/category-', category)}"><xsl:value-of select="category"/></a>
                                    </span>
                                </div>
                            </li>
                        </xsl:for-each>
                    </ul>
                </main>
                <footer aria-label="Footer info">
                    <a href="/colophon">Colophon</a>
                    <hr aria-hidden="true"/>
                    <p>&#169; <span id="year"></span> Max Sheridan</p>
                </footer>
                <script>
                document.getElementById('year').textContent = new Date().getFullYear();
                function copyEmail() {navigator.clipboard.writeText('your@email.com'); alert('Email copied to clipboard!');}
                function copyToClipboard(element) {var text = element.textContent; navigator.clipboard.writeText(text).then(function() {alert('RSS feed URL copied to clipboard!');}).catch(function(err) {console.error('Failed to copy:', err);});}
                </script>
                </body>
            </html>
        </xsl:template>
    </xsl:stylesheet>
