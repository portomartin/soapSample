export PIP_CONFIG_FILE=~/pip.conf
export DIRECTORY='.afipClient'

if [ ! -d "$DIRECTORY" ]; then
	virtualenv -p python3 $DIRECTORY
	source $DIRECTORY/bin/activate
	pip install -r requirements.txt
	deactivate
fi

source $DIRECTORY/bin/activate
python main.py