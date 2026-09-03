import os
import shutil
import zipfile
import subprocess

def main():
    print("Creating Lambda deployment package...")

    if os.path.exists("lambda-package"):
        shutil.rmtree("lambda-package")
    if os.path.exists("lambda-deployment.zip"):
        os.remove("lambda-deployment.zip")

    os.makedirs("lambda-package")

    print("Ensuring pip is available in environment...")
    subprocess.run(["uv", "pip", "install", "pip"], check=True)

    print("Installing dependencies using pip for Linux Lambda...")
    subprocess.run(
        [
            "python3",
            "-m",
            "pip",
            "install",
            "--target",
            "lambda-package",
            "-r",
            "requirements.txt",
            "--platform",
            "manylinux2014_x86_64",
            "--python-version",
            "3.12",
            "--implementation",
            "cp",
            "--only-binary=:all:",
            "--upgrade",
        ],
        check=True,
    )

    print("Copying application files...")
    for file in ["server.py", "lambda_handler.py", "context.py", "resources.py"]:
        if os.path.exists(file):
            shutil.copy2(file, "lambda-package/")
    
    if os.path.exists("data"):
        shutil.copytree("data", "lambda-package/data")

    print("Creating zip file...")
    with zipfile.ZipFile("lambda-deployment.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("lambda-package"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "lambda-package")
                zipf.write(file_path, arcname)

    size_mb = os.path.getsize("lambda-deployment.zip") / (1024 * 1024)
    print(f"✓ Created lambda-deployment.zip ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()