# --------------------------
# log
# --------------------------
function log2 () {

	export datetime=$(date '+%d/%m/%Y %H:%M:%S');
	export message=$1
	export sl=$2
	export module=$3
		
	# echo $2
	
	if [[ $sl == "sl" ]]; then
		printf "\r%s\033[42m\033[30m%-25s\033[0m [%-10s] %s" "$(tput el)" "$datetime" "$module" "$message" 
		sleep .2
	else
		printf "\r\n\033[42m\033[30m%-25s\033[0m [%-10s] %s" "$datetime" "$module" "$message" 
	fi;

	if [[ $sl == "pl" ]]; then
		printf "\r\n" 
	fi;
	
	
}

function log () {

	export datetime=$(date '+%d/%m/%Y %H:%M:%S');
	export message=$1
	export sl=$2
	export module=$3
		
	# echo $2
	
	if [[ $sl == "sl" ]]; then
		printf "\r%s [%-19s] [%-10s] %s" "$(tput el)" "$datetime" "$module" "$message" 
		sleep .2
	else
		printf "\r\n [%-19s] [%-10s] %s" "$datetime" "$module" "$message" 
	fi;

	if [[ $sl == "pl" ]]; then
		printf "\r\n" 
	fi;
	
	
}

# request
# --------------------------
function request () {
	
	NEWLINE=$'\n'
	
	export method=$1
	export uri=$2
	export intro=$3
	export data=$4
	
	
	if [[ $data != "" ]]; then
		export mdata="--data @$4"
	fi;
	
	printf "%s \r\n" 
	printf "> Test: %s \r\n" "$intro"
	printf "> uri: %s %s\r\n" "$method" "$uri"
	
	if [[ $data != "" ]]; then

		printf "\r\n" 
		printf "[%s]\r\n" "Request" 
		value=$(<$data)
		printf "$value" | jq .	

	fi;
	
	printf "\r\n" 
	printf "[%s]\r\n" "Response" 
	curl -s -X $method -H "Content-Type: application/json" $mdata $SERVER_IP$uri | jq .	
	
	
}

