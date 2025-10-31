"""Test if all required packages are installed."""

packages = [
    'streamlit',
    'PyPDF2',
    'pandas',
    'matplotlib',
    'requests',
    'pytz',
    'openai',
    'streamlit_pdf_viewer',
    'phi',
    're',
    'json',
    'logging',
    'smtplib',
    'email'
]

print("Testing package imports...\n")
for package in packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"✅ {package}")
    except ImportError as e:
        print(f"❌ {package} - NOT INSTALLED")
        print(f"   Install with: pip install {package}")

print("\nIf you see any ❌, run:")
print("pip install [package-name]")
