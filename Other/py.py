import os
import re
from lxml import etree

INPUT_DIR = "xmlRAW"
OUTPUT_DIR = "htmlOUT"
XSLT_FILE = "style.xsl"

def clean_xml_tags(xml_data):
    # Убираем пробелы внутри тегов, чтобы XSLT их понимал
    # Например: <Имя товара> станет <Имя_товара>
    def replace_tag(match):
        return match.group(0).replace(' ', '_')
    
    cleaned_data = re.sub(r'<[^>]+>', replace_tag, xml_data)
    return cleaned_data

def convert():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Загружаем XSLT один раз
    with open(XSLT_FILE, 'rb') as f:
        xslt_tree = etree.XML(f.read())
        transform = etree.XSLT(xslt_tree)

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".xml"):
            print(f"Обработка {filename}...")
            
            # Читаем как текст для очистки тегов
            with open(os.path.join(INPUT_DIR, filename), 'r', encoding='utf-8') as f:
                raw_xml = f.read()
            
            cleaned_xml = clean_xml_tags(raw_xml)
            
            # Парсим очищенный XML
            xml_tree = etree.fromstring(cleaned_xml.encode('utf-8'))
            
            # Трансформация
            result = transform(xml_tree)
            
            # Сохранение
            output_path = os.path.join(OUTPUT_DIR, filename.replace(".xml", ".html"))
            with open(output_path, "wb") as f:
                f.write(etree.tostring(result, pretty_print=True, method="html", encoding="utf-8"))

    print("Готово! Проверьте папку htmlOUT.")

if __name__ == "__main__":
    convert()