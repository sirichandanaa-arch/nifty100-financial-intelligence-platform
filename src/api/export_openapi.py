import json
from src.api.main import app
from src.common import DOCS_DIR

def main():
    """Export the FastAPI OpenAPI specification."""; DOCS_DIR.mkdir(exist_ok=True); (DOCS_DIR/'openapi.json').write_text(json.dumps(app.openapi(),indent=2),encoding='utf-8')
if __name__=='__main__': main()
