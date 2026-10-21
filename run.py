import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Cloud Run passes PORT in environment (defaults to 8080)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
