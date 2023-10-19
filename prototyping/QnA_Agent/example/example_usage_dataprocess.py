from prototyping.QnA_Agent.src import dataProcessor


# Define the URL of the ZIP archive
repo_url = 'https://github.com/singnet/dev-portal/archive/refs/heads/master.zip'

# Create an instance of DataProcessor
processor = dataProcessor.DataProcessor(repo_url)

# The DataProcessor class constructor will automatically download the files,
# process them, save to CSV, and delete the 'dev-portal-master' directory.
