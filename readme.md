## DataMart 

A minmalist structure-oriented content management system.

- Uses flat-files and file-system to store and organize the content
  - File-based routes: Content is organized in folder-structure
  - Structured content: JSON files are to both;  describe the content (json schema) and persist the data.
  - Arbitrary attachments: Any structured entity could have attachments (binary or otherwise)
  - Version control: Track change history by git 
  
- API layer (REST, JSON-API)
  - Management  : Create/update/delete schema, content, scripts, triggers, users and roles
  - Discovery   : Users, paths, scripts, changes/history, schema and content
  - Consumption : Content/attachments, scripts and submissions   
  
###  Folder hierarchy ...

```
space/
  ├── users/       Users and roles
  ├── schema/      Schema definitions
  ├── content/     Actual content + attachments 
  ├── submissions/ Anonymous/public submissions
  ├── scripts/     Server-side logic executed through Api or triggers
  └── triggers/    Time or event based triggers to inovke a script
```

### Install / usage

#### Requirements

- git
- python 3
- pip

Optional:

- podman
- gzip


#### Clone the code

```
git clone https://github.com/kefahi/datamart.git
cd datamart
```

#### Local / Direct Setup

```
pip install -r backend/requirements.txt

# Create logs folder (path can be configured in sample.env)
mkdir ../logs/

cd backend 

cp sample.env secrets.env
source env.sh

# Unit test
python tests.py

# pytest
pytest

# To run:
python main.py
# or 
./run.sh

# Invoke sample apis using curl
./curl.sh
```

#### Using Podman/Container

```
# Build
podman rmi datamart
podman build -t datamart .

# Run 
podman run --name datamart --rm \
  -p 127.0.0.1:8080:8080/tcp \
  -it datamart \
  /home/backend/run.sh
  
# Command line access inside the container
podman exec -it datamart ash

# The image can be saved to a file for off-line deployement
podman save --quiet datamart | gzip > datamart.tar.gz

# Then loaded at the target system
podman load -i datamart.tar.gz
```
