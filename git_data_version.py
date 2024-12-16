import os
import boto3
import git
from git import Repo 
import pandas as pd
import yaml
import json

# Initialize Git repository
def init_git_repo():
    try:
        repo = git.Repo.init(os.getcwd())
        print("Initialized a Git repository.")
        return repo
    except Exception as e:
        print(f"Error initializing Git repository: {e}")

# def configure_git_remote(repo, remote_name, remote_url):
#     try:
#         remote = repo.create_remote(remote_name, remote_url)
#         print(f"Added remote '{remote_name}' with URL '{remote_url}'.")
#     except git.exc.GitCommandError:
#         print(f"Remote '{remote_name}' already exists.")
#         remote = repo.remotes[remote_name]
#     return remote

# Commit changes to Git
def git_commit(repo, message):
    try:
        repo.git.add()  # Add all changes
        repo.index.commit(message)
        print(f"Committed changes with message: '{message}'")
    except Exception as e:
        print(f"Error committing changes: {e}")

# Push changes to Git remote
def git_push(repo, remote_name="origin", branch="master"):
    try:
        if remote_name not in repo.remotes:
            print(f"Remote '{remote_name}' not found. Skipping push.")
            return
        remote = repo.remotes[remote_name]
        remote.push(refspec=branch)
        print(f"Pushed changes to remote '{remote_name}' on branch '{branch}'.")
    except Exception as e:
        print(f"Error pushing changes: {e}")

# Initialize DVC
def init_dvc():
    if not os.path.exists(".dvc"):
        os.system("dvc init")
        print("Initialized DVC.")
    else:
        print("DVC is already initialized.")

# Add data to DVC tracking
def add_data_to_dvc(file_path):
    os.system(f"dvc add {file_path}")
    print(f"Added '{file_path}' to DVC tracking.")

# Configure S3 bucket for DVC remote using Boto3
def configure_s3_dvc_remote(bucket_name, region, remote_name="remotedvcs3"):
    try:
        # Create S3 client
        s3 = boto3.client('s3', region_name=region)
        
        # Check if bucket exists
        response = s3.list_buckets()
        if bucket_name not in [bucket["Name"] for bucket in response["Buckets"]]:
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
            print(f"Created S3 bucket: {bucket_name}")
        else:
            print(f"S3 bucket '{bucket_name}' already exists.")
        
        # Configure DVC remote
        os.system(f"dvc remote add -d {remote_name} s3://{bucket_name}")
        print(f"Configured DVC remote '{remote_name}' with S3 bucket: s3://{bucket_name}")
    except Exception as e:
        print(f"Error configuring S3 bucket: {e}")


# Push data to DVC remote
def push_to_dvc_remote():
    os.system("dvc push")
    print("Pushed data to DVC remote storage.")

# Checkout data to restore a specific version
def dvc_checkout():
    os.system("dvc checkout")
    print("Checked out data to restore the version.")

# Load and preprocess data
def load_data(file_path):
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Data shape: {df.shape}")
    return df

def extract_dvc_metadata(dvc_files):
    dataset_metadata = []
    for dvc_file in dvc_files:
        # Extract dataset name from file name
        dataset_name = os.path.splitext(os.path.basename(dvc_file))[0]

        # Read the .dvc file
        with open(dvc_file, 'r') as file:
            dvc_data = yaml.safe_load(file)

        # Extract md5 hash
        md5_hash = dvc_data['outs'][0]['md5']

        # Append metadata
        dataset_metadata.append({
            "dataset_name": dataset_name,
            "md5": md5_hash
        })
    
    return dataset_metadata

def save_metadata_to_json(metadata, output_file):
   
    with open(output_file, 'w') as json_file:
        json.dump(metadata, json_file, indent=4)


if __name__ == "__main__":
    
    repo = init_git_repo()
    
    init_dvc()

    bucket_name = "myawsdvcs3bucket"
    region = "ap-south-1"  # Replace with your AWS region
    configure_s3_dvc_remote(bucket_name, region)

    
    data_file = "insurance1.csv"
    add_data_to_dvc(data_file)

    git_commit(repo, "Add updated insurance1.csv to DVC")
    push_to_dvc_remote()
    git_push(repo)
    dvc_checkout()   
    #data = load_data(data_file)

    dvc_files = ["Car.csv.dvc","insurance1.csv.dvc"]

    # Output JSON file
    # output_file = "dataset_metadata.json"

    # # Extract metadata and save to JSON
    # try:
    #     metadata = extract_dvc_metadata(dvc_files)
    #     save_metadata_to_json(metadata, output_file)
    #     print(f"Metadata successfully saved to {output_file}")
    # except Exception as e:
    #     print(f"Error: {e}")
