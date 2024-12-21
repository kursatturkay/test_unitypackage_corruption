import gzip
import shutil
import os
import tarfile

error_report = []  
temp_unzipped_files = []  

def extract_gzip(gzip_path):
    """Extracts a GZIP file and returns the extracted file path."""
    try:
        extracted_file = gzip_path + ".unzipped"
        with gzip.open(gzip_path, 'rb') as f_in:
            with open(extracted_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"Successfully extracted GZIP: {gzip_path} -> {extracted_file}")
        temp_unzipped_files.append(extracted_file)  
        return extracted_file
    except Exception as e:
        print(f"Error extracting {gzip_path}: {e}")
        error_report.append(gzip_path)
        temp_unzipped_files.append(gzip_path + ".unzipped")  
        return None

def check_tar(unitypackage_path):
    """Check if the extracted file is a valid TAR file."""
    if tarfile.is_tarfile(unitypackage_path):
        print(f"{unitypackage_path} is a valid TAR file.")
        return True
    else:
        print(f"{unitypackage_path} is not a valid TAR file.")
        error_report.append(unitypackage_path)
        return False

def extract_tar(tar_path):
    """Extracts a TAR file and returns the extracted directory."""
    try:
        extracted_dir = tar_path + ".extracted"
        with tarfile.open(tar_path, 'r') as tar:
            tar.extractall(path=extracted_dir)
            print(f"Successfully extracted TAR: {tar_path}")
            return extracted_dir
    except Exception as e:
        print(f"Error extracting TAR: {tar_path}: {e}")
        error_report.append(tar_path)
        return None

def check_unitypackage(unitypackage_path):
    """Check if the extracted file is a valid unitypackage."""
    if not os.path.exists(unitypackage_path):
        print(f"File {unitypackage_path} does not exist.")
        error_report.append(unitypackage_path)
        return False
    try:
        with open(unitypackage_path, 'rb') as f:
            header = f.read(4)
            if header == b"PK\x03\x04":
                print(f"{unitypackage_path} is a valid unitypackage file.")
                return True
            else:
                print(f"{unitypackage_path} does not start with the expected header.")
                error_report.append(unitypackage_path)
                return False
    except Exception as e:
        print(f"Error checking {unitypackage_path}: {e}")
        error_report.append(unitypackage_path)
        return False

def extract_and_check_unitypackage(gzip_path):
    """Extract GZIP, check for TAR, then check if the resulting file is a valid unitypackage."""
    extracted_file = extract_gzip(gzip_path)
    if extracted_file:
        if check_tar(extracted_file):
            extracted_tar_dir = extract_tar(extracted_file)
            if extracted_tar_dir:
                for root, dirs, files in os.walk(extracted_tar_dir):
                    for file in files:
                        if file.endswith('.unitypackage'):
                            unitypackage_path = os.path.join(root, file)
                            check_unitypackage(unitypackage_path)
                shutil.rmtree(extracted_tar_dir)
                print(f"Removed extracted TAR directory: {extracted_tar_dir}")
        else:
            check_unitypackage(extracted_file)

def check_all_unitypackages_in_directory(directory):
    """Checks all unitypackage files in a directory."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.unitypackage'):
                unitypackage_path = os.path.join(root, file)
                print(f"\nChecking file: {unitypackage_path}")
                extract_and_check_unitypackage(unitypackage_path)

def clean_up_unzipped_files():
    """Remove all unzipped files at the end of the process."""
    for path in temp_unzipped_files:
        if os.path.isfile(path):
            try:
                os.remove(path)
                print(f"Removed temporary unzipped file: {path}")
            except Exception as e:
                print(f"Error removing file {path}: {e}")

def move_corrupted_files():
    """Move all corrupted files to a 'corrupted' directory."""
    corrupted_dir = os.path.join(os.getcwd(), "corrupted")
    os.makedirs(corrupted_dir, exist_ok=True)
    for path in error_report:
        if os.path.isfile(path):
            try:
                shutil.move(path, corrupted_dir)
                print(f"Moved corrupted file to: {os.path.join(corrupted_dir, os.path.basename(path))}")
            except Exception as e:
                print(f"Error moving file {path} to corrupted directory: {e}")

def report_errors():
    """Report all the errors found during the check."""
    if error_report:
        print("\n--- Error Report ---")
        for path in error_report:
            print(f"Error with: {path}")
    else:
        print("\nNo errors found!")

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.realpath(__file__))
    check_all_unitypackages_in_directory(current_directory)
    clean_up_unzipped_files()  
    move_corrupted_files()  
    report_errors()
