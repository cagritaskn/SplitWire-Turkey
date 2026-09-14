standard_mode_nfqws()
{
	# $1 - 1 - run, 0 - stop
	local opt
	[ "$NFQWS2_ENABLE" = 1 ] && check_bad_ws_options $1 "$NFQWS2_OPT" && {
		opt="--qnum=$QNUM $NFQWS2_OPT"
		filter_apply_hostlist_target opt
		do_nfqws $1 1 "$opt"
	}
}
standard_mode_daemons()
{
	# $1 - 1 - run, 0 - stop

	standard_mode_nfqws $1
}
zapret_do_daemons()
{
	# $1 - 1 - run, 0 - stop

	standard_mode_daemons $1
	custom_runner zapret_custom_daemons $1

	return 0
}
zapret_run_daemons()
{
	zapret_do_daemons 1 "$@"
}
zapret_stop_daemons()
{
	zapret_do_daemons 0 "$@"
}
