LIST_HTTP="${LIST_HTTP:-$TESTDIR/list_http.txt}"
LIST_HTTPS_TLS12="${LIST_HTTPS_TLS12:-$TESTDIR/list_https_tls12.txt}"
LIST_HTTPS_TLS13="${LIST_HTTPS_TLS13:-$TESTDIR/list_https_tls13.txt}"
LIST_QUIC="${LIST_QUIC:-$TESTDIR/list_quic.txt}"

emptyf()
{
	:
}

check_list()
{
	# $1 - test function
	# $2 - domain
	# $3 - file

	local line ok=0
	[ -f "$3" ] || {
		echo "no strategy file '$3'"
		return 1
	}
	while IFS= read -r line; do
		case "$line" in
			""|\#*) continue ;;
		esac
		line=$(echo "$line" | tr -d "\r\n")
		# dry run eval in subshell. can fail because of unescaped chars or something else
		if (eval emptyf $line); then
			# real run in the current shell. can modify vars
			eval pktws_curl_test_update "$1" "$2" $line && ok=1
		else
			echo >&2 BAD STRATEGY: $line
			echo >&2 "THIS LINE IS PASSED TO eval SHELL FUNCTION. IT'S INTERPRETED AS A SHELL STATEMENT. SPECIAL CHARS MUST BE ESCAPED"
		fi
	done < "$3"

	[ "$ok" = 1 ]
}

pktws_check_http()
{
	# $1 - test function
	# $2 - domain

	check_list "$1" "$2" "$LIST_HTTP"
}

pktws_check_https_tls12()
{
	# $1 - test function
	# $2 - domain

	check_list "$1" "$2" "$LIST_HTTPS_TLS12"
}

pktws_check_https_tls13()
{
	# $1 - test function
	# $2 - domain

	check_list "$1" "$2" "$LIST_HTTPS_TLS13"
}

pktws_check_http3()
{
	# $1 - test function
	# $2 - domain

	check_list "$1" "$2" "$LIST_QUIC"
}
