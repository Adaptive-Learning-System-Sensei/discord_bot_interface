# Discord Bot Documentation

Welcome to the internal technical documentation for the Discord Bot project. This system is designed as a modular Discord automation helper featuring structural **Cogs**, localized API wrappers, and background web keep-alive capabilities.

## 🚀 Fast Track Setup

Ensure you have your Python virtual environment activated:

```bash
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Key Functional Areas
* **Features:** Modular discord extensions (Greetings, General management, LeetCode fetching tracking).
* **Keep-Alive Server:** Native containerized web micro-layer to maintain active status across persistent hosting platforms.
* **Testing:** Modular `pytest` suite validating background domain actions and event responses.
