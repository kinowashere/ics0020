# How To

## Management

First run (already set, so no need ot do this on lab computer):

```
sudo apt install python3-venv
python3 -m venv ~/ansible-venv
~/ansible-venv/bin/pip install ansible==2.9
~/ansible-venv/bin/ansible --version

~/ansible-venv/bin/ansible-galaxy collection install ansible.windows
~/ansible-venv/bin/pip install "pywinrm>=0.3.0
```

## Windows Managed

First run (already set, so no need ot do this on lab computer):

```
$client = new-object
System.Net.WebClient$client.DownloadFile("https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1","C:\Users\nimda\ConfigureRemotinForAnsible.ps1")

powershell -executionpolicy bypass -File C:\Users\nimda\ConfigureRemotingForAnsible.ps1 -Verbose -EnableCredSSP
```

## Once everything is set...

- cd to the ansible_management directory and run with password kala..11
- cd to the ansible_linux directory and run with password kala..11
- cd to the ansible_windows directory and run with password kala..11

Example command:

```
sudo ~/ansible-venv/bin/ansible-playbook ansible_<name>.yaml -kK
```