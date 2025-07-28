from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="phd-advisor-backend",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered PhD Advisor Matching Platform Backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/phd-advisor-backend",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "alembic>=1.13.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "email-validator>=2.1.0",
        "pydantic[email]>=2.5.0",
        "redis>=5.0.0",
        "boto3>=1.34.0",
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.4",
        "PyPDF2>=3.0.0",
        "python-docx>=1.1.0",
        "aiohttp>=3.9.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.25.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "isort>=5.12.0",
            "mypy>=1.7.0",
            "pre-commit>=3.6.0",
        ]
    },
)