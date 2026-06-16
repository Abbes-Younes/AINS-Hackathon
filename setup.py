from setuptools import setup, find_packages

setup(
    name="entrepreneurial-orientation-engine",
    version="0.1.0",
    description="Intelligent Entrepreneurial Orientation Engine — AI-powered diagnostic, scoring, and roadmap platform for Tunisian entrepreneurs",
    author="AINS Hackathon 2026",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.136.0",
        "uvicorn[standard]>=0.30.0",
        "pydantic>=2.0.0",
        "sentence-transformers>=3.0.0",
        "chromadb>=0.5.0",
        "sqlite-utils>=3.37",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
)
