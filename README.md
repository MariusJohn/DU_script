# Instructions
1. Replace the string 'PRIVATE_KEY_FILE_HERE' with the location of your private Encord SSH key file.
You can learn how to create the [SSH key here](https://docs.encord.com/admins/settings/public-keys/#set-up-public-key-authentication).

2. Replace the project_hash = 'FILL_ME_IN' section with the project_hash of the project you want to get
labels from. The project hash is the alphanumeric string in the project URL. For example, given the
following project URL: `https://app.encord.com/projects/view/9594ed65-c672-42a7-86fe-ff98425f5853/labels`, 
the project hash is `9594ed65-c672-42a7-86fe-ff98425f5853`

3. use python's virtual env to setup the script environment:
```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

4. run the script!
```
python labels_download_template.py
```
