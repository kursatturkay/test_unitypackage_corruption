import gzip
import shutil
import os
import tarfile

def extract_gzip(gzip_path):
    """Extracts a GZIP file and returns the extracted file path."""
    try:
        # Generate the output filename for the extracted file
        extracted_file = gzip_path + ".unzipped"
        
        # Open the GZIP file and extract it
        with gzip.open(gzip_path, 'rb') as f_in:
            with open(extracted_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        print(f"Successfully extracted GZIP: {gzip_path} -> {extracted_file}")
        return extracted_file
    except Exception as e:
        print(f"Error extracting {gzip_path}: {e}")
        return None

def check_tar(unitypackage_path):
    """Check if the extracted file is a valid TAR file."""
    if tarfile.is_tarfile(unitypackage_path):
        print(f"{unitypackage_path} is a valid TAR file.")
        return True
    else:
        print(f"{unitypackage_path} is not a valid TAR file.")
        return False

def extract_tar(tar_path):
    """Extracts a TAR file and returns the extracted files."""
    try:
        with tarfile.open(tar_path, 'r') as tar:
            tar.extractall(path=tar_path + ".extracted")
            print(f"Successfully extracted TAR: {tar_path}")
            return tar_path + ".extracted"
    except Exception as e:
        print(f"Error extracting TAR: {tar_path}: {e}")
        return None

def check_unitypackage(unitypackage_path):
    """Check if the extracted file is a valid unitypackage."""
    if not os.path.exists(unitypackage_path):
        print(f"File {unitypackage_path} does not exist.")
        return False
    
    try:
        # Try opening the file in binary mode to see if it's a valid unitypackage
        with open(unitypackage_path, 'rb') as f:
            # Typically, unitypackage files start with a certain pattern or structure
            header = f.read(4)  # Read the first 4 bytes to check for basic structure
            if header == b"PK\x03\x04":
                print(f"{unitypackage_path} is a valid unitypackage file.")
                return True
            else:
                print(f"{unitypackage_path} does not start with the expected header.")
                return False
    except Exception as e:
        print(f"Error checking {unitypackage_path}: {e}")
        return False

def extract_and_check_unitypackage(gzip_path):
    """Extract GZIP, check for TAR, then check if the resulting file is a valid unitypackage."""
    extracted_file = extract_gzip(gzip_path)
    if extracted_file:
        # Check if the extracted file is a valid TAR
        if check_tar(extracted_file):
            # Extract the TAR file
            extracted_tar_dir = extract_tar(extracted_file)
            if extracted_tar_dir:
                # Now check for any unitypackage inside the TAR
                for root, dirs, files in os.walk(extracted_tar_dir):
                    for file in files:
                        if file.endswith('.unitypackage'):
                            unitypackage_path = os.path.join(root, file)
                            check_unitypackage(unitypackage_path)
        else:
            # If it's not a TAR, just check it as a unitypackage
            check_unitypackage(extracted_file)

def check_all_unitypackages_in_directory(directory):
    """Checks all unitypackage files in a directory."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.unitypackage'):
                unitypackage_path = os.path.join(root, file)
                print(f"\nChecking file: {unitypackage_path}")
                extract_and_check_unitypackage(unitypackage_path)

if __name__ == "__main__":
    # Get the current directory of the script
    current_directory = os.path.dirname(os.path.realpath(__file__))
    check_all_unitypackages_in_directory(current_directory)
