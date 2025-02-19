export PIP_CONFIG_FILE=~/pip.conf
export DIRECTORY='.einvoice'

if [ ! -d "$DIRECTORY" ]; then
	virtualenv --python=/usr/bin/python2 $DIRECTORY
	source $DIRECTORY/bin/activate
	pip install -r requirements.txt
	deactivate
fi

source $DIRECTORY/bin/activate
python __init__.py
