export PIP_CONFIG_FILE=~/pip.conf
export DIRECTORY='.silika_fe_test'

if [ ! -d "$DIRECTORY" ]; then
	virtualenv --python=/usr/bin/python2 $DIRECTORY
	source $DIRECTORY/bin/activate
	pip install -r requirements.txt
	deactivate
fi

source $DIRECTORY/bin/activate
python main.py

