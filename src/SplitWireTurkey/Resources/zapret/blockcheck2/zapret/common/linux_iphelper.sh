get_uevent_devtype()
{
	local DEVTYPE INTERFACE IFINDEX OF_NAME OF_FULLNAME OF_COMPATIBLE_N
	[ -f "/sys/class/net/$1/uevent" ] && {
		. "/sys/class/net/$1/uevent"
		echo -n $DEVTYPE
	}
}
resolve_lower_devices()
{
	# $1 - bridge interface name
	[ -d "/sys/class/net/$1" ] && {
		find "/sys/class/net/$1" -follow -maxdepth 1 -name "lower_*" |
		{
			local l lower lowers
			while read lower; do
				lower="$(basename "$lower")"
				l="${lower#lower_*}"
				[  "$l" != "$lower" ] && append_separator_list lowers ' ' '' "$l"
			done
			printf "$lowers"
		}
	}
}
