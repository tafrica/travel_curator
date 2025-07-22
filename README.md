# Travel Curator Setup Guide

This project uses the **new OpenAI Python client (>=1.0.0)**, which has a different API than older versions.

---

## 1. **Set Up Your Environment**

### Install Dependencies
Run the following commands:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Ensure your `requirements.txt` includes:
```
openai>=1.0.0
requests>=2.31.0
```

---

## 2. **Set Your API Key**

The new OpenAI client requires the environment variable `OPENAI_API_KEY`.

For example, on macOS/Linux:
```bash
export OPENAI_API_KEY="your_api_key_here"
```

On Windows PowerShell:
```powershell
setx OPENAI_API_KEY "your_api_key_here"
```

---

## 3. **Run the Script**

Run the example script:
```bash
python travel_curator_fixed.py
```

---

## 4. **Troubleshooting**

### ImportError: cannot import name 'OpenAI' from 'openai'
- This means you're still on an old OpenAI package (0.28 or earlier).
- Fix by running:
  ```bash
  pip install --upgrade openai
  ```
- Check version:
  ```bash
  pip show openai | grep Version
  ```
  It should show `Version: 1.x.x` or higher.

### APIRemovedInV1 Error
- This happens if you still use `openai.ChatCompletion.create()` somewhere.
- Update your code to use:
  ```python
  from openai import OpenAI
  client = OpenAI()
  response = client.chat.completions.create(
      model="gpt-4o",
      messages=[{"role": "system", "content": "Hello"}]
  )
  ```

---

## 5. **Next Steps**

- If you're deploying to Streamlit Cloud, ensure your `requirements.txt` matches the one provided in this project.
- Reboot your environment after upgrading the package to ensure the new client is loaded.
