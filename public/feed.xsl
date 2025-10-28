<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="UTF-8" indent="yes"/>
    <xsl:template match="/">
        <html lang="en">
            <head>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1, interactive-widget=resizes-content"/>
                <meta name="color-scheme" content="light dark"/>
                <link rel="stylesheet" href="/assets/css/style.css"/>
                <title>Feed - This Is A Blog</title>
            </head>
            <body>
                <main id="main" tabindex="-1">
                    <p class="index-intro big">Where I write, think, and ramble, but mostly ramble.</p>
                    <ul class="index-list">
                        <xsl:for-each select="/rss/channel/item">
                            <li>
                                <div class="link">
                                    <a href="{link}"><span><xsl:value-of select="title"/></span></a>
                                </div>
                                <div class="meta" aria-label="Date and category">
                                    <span class="date"><xsl:value-of select="pubDate"/></span>
                                    <span class="category" aria="Category link">
                                        <xsl:value-of select="category"/>
                                    </span>
                                </div>
                                <div class="post-content">
                                    <xsl:value-of select="description" disable-output-escaping="yes"/>
                                </div>
                            </li>
                        </xsl:for-each>
                    </ul>
                </main>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
