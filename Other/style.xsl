<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="UTF-8" indent="yes"/>
    
    <xsl:template match="/">
        <html>
        <head>
            <meta charset="UTF-8"/>
            <style>
                body { font-family: sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; border: 1px solid #333; }
                th { background-color: #444; color: white; padding: 10px; text-align: left; }
                td { padding: 8px; border: 1px solid #ccc; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <h2>Каталог из XML</h2>
            <table>
                <tr>
                    <th>Артикул</th>
                    <th>Наименование</th>
                    <th>Цена</th>
                    <th>Кол-во</th>
                    <th>Производитель</th>
                </tr>
                <xsl:for-each select="//record">
                    <tr>
                        <td><xsl:value-of select="Артикул"/></td>
                        <td><strong><xsl:value-of select="Имя_товара"/></strong></td>
                        <td><xsl:value-of select="Цена"/></td>
                        <td><xsl:value-of select="Количество"/></td>
                        <td><xsl:value-of select="Производитель"/></td>
                    </tr>
                </xsl:for-each>
            </table>
        </body>
        </html>
    </xsl:template>
</xsl:stylesheet>