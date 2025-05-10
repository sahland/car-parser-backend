from parsers.che168 import parse_che168_with_browser
import json

data = parse_che168_with_browser()
print(json.dumps(data, indent=2, ensure_ascii=False))
