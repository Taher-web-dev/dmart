## DataMart 

A minimalist structure-oriented content management system that serves as an isolated or independent data layer. 

It can also be called "Content Repository", "Content Registry".

- Generic API that allows dealing with a wide variety of content
- All content is stored in flat json files that can be version controlled
- Able to serve an arbitrary number of application consuming it (crosses the boundaries of applications)
- Time-proof design for maximum data longevity
- This isolated data layer can be used as the single source of truth. 

The main data entity is called *entry*; each entry has:
 - A meta-file (json) that holds *meta* information about the entry; such as name, description, tags, attributes ...etc. 
 - Within the meta file, each entry should have a globally unique UUID and a shortname that must be unique within the parent folder.
 - A payload which could be either embedded in the mata-file or separate json file)
 - Change history (aka Alterations) on that entry.
 - An entry has an arbitrary number of attachments, each attachment has a meta-file and payload. 
   - Alteration: Describing a change
   - Comment 
   - Relationship: A pointer to another entry
   - Media: Binary payload such as images, videos ...etc

- Uses flat-files and file-system to store and organize the content
  - File-based routes: Entries are organized in an arbitrary (free from) folder-structure within a space root folder.
  - Structured content: JSON files are to both;  describe the content (json schema) and persist the data.
  - Arbitrary attachments: Any structured entity could have attachments (binary or otherwise)
  - Version control: Track change history by git 
  
- API layer (REST, JSON-API)
  - Management  : Create/update/delete schema, content, scripts, triggers, users and roles
  - Discovery   : Users, paths, scripts, changes/history, schema and content
  - Consumption : Content/attachments, scripts and submissions   


The primary type of entries is "Content" which is a json data that could be linked with a schema for strict validation.

ACL rules are used to control permissions of users and groups on the space.


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

### Api sets

| Set | Endpoints | Description |
|----|----|----|
| /user | create,login,profile,delete | User account |
| /managed | query,create,delete,update,move,media(create/read) | Users-only apis to manage content |
| /public | query(read),media(read),submission(create) | Public apis for public consumers |


### Additional terminology

| Term | Description |
|----|----|
| space (or space root)| The root directory under which all content exist. All read-write operations must be within the space root| 
| subpath | The path within space root that leads to an entry. e.g. `content/stuff/todo` |
| Locator | A *link* to another entry. |
| payload | The actual content associated with the entry or attachment |
| .dm | a hidden folder used to store meta information and attachments and their payload files |

### Meta and file disposition scheme


| File path | Description |
|----|----|
| `[sub/path]/.dm/meta.folder.json` | The meta file of a Folder |
| `[sub/path]/.dm/[entryshortname]/meta.[entrytype].json` | The meta file of a regular entry |
| `[sub/path]/[entrypayload]` | The optional payload file of the entry. it may not clash with another payload file within that folder|
| `[sub/path]/.dm/[entryshortname]/attachments.[attachementtype]/meta.[attachmentshortname].json` | The meta file of an attachment |
| `[sub/path]/.dm/[entryshortname]/attachments.[attachementtype]/[attachmentpayload]` | The optional attachment payload file. it may not clash with meta.[xxx].json or another payload file within that folder|

With this scheme, when browsing the file system, only proper entry payload files appear to the user. All meta data and attachments data is in the hidden folders.


### Models

![Core models](http://www.plantuml.com/plantuml/proxy?cache=no&fmt=svg&src=https://raw.githubusercontent.com/kefahi/datamart/master/docs/models_core.iuml)
![Api  models](http://www.plantuml.com/plantuml/proxy?cache=no&fmt=svg&src=https://raw.githubusercontent.com/kefahi/datamart/master/docs/models_api.iuml)

### Install / usage

#### Requirements

- git
- python 3
- pip
- redis
- RedisJSON (rejson)
- RediSearch

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

#Code coverage

# Conduct coverage check 
coverage run -m pytest

# Print the report
coverage report -m

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
