export DIRECTORY='.afipServer'

if [ ! -d "$DIRECTORY" ]; then
	virtualenv --python=/usr/bin/python2 $DIRECTORY
	source $DIRECTORY/bin/activate
	pip install -r requirements.txt
	deactivate
fi

PORT_NUMBER=5002
lsof -i tcp:${PORT_NUMBER} | awk 'NR!=1 {print $2}' | xargs kill -9

source $DIRECTORY/bin/activate
export testName="tests/main.py"
# export testName="classes/sample.py"
python -B $testName
