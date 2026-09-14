pktws_check_https_tls12()
{
	# $1 - test function
	# $2 - domain

	# SplitWire-Turkey: alimali54/zapret-win-turkey kaynakli, Turkiye ISS'leri (Turk Telekom,
	# Superonline, Vodafone, Turksat Kablonet, Telekom Mobil, Turkcell Mobil, Vodafone Mobil)
	# icin bilinen calisan teknikler -- bkz. SplitWireTurkey/MainWindow.xaml.cs icindeki
	# _zapret2IspPresets listesi (presets2.txt'ye de ayni sekilde eklendi). Dosya adi "00-" ile
	# basladigindan test_runner() bunu TUM diger standard/ scriptlerinden ONCE calistiriyor --
	# boylece dogru ISS icin dogru teknik zaten ilk birkac saniyede bulunuyor ve blockcheck2'nin
	# geri kalan tum test dosyalarini (10-http-basic.sh, 15-misc.sh, 17-oob.sh, ... 90-quic.sh)
	# calistirmasi hic gerekmiyor -- servis kur/kaldir dongusune hic girmeden, dogrudan winws2
	# ile hizli bir sekilde deneniyor (aynen diger tum standard/ scriptlerinin yaptigi gibi).
	# 7 preset TEK BASINA 3 benzersiz teknige indirgeniyor (bircogu ayni --lua-desync degerini
	# paylasiyor), gereksiz tekrar test yapilmiyor.

	local PAYLOAD="--payload=tls_client_hello" ok

	[ "$NOTEST_TURKEY_PRESETS" = 1 ] && { echo "SKIPPED"; return; }

	# Turk Telekom / Superonline / Turksat Kablonet / Turkcell Mobil / Vodafone Mobil
	pktws_curl_test_update "$1" "$2" $PAYLOAD --lua-desync=multidisorder:pos=2:seqovl=1 && ok=1
	[ "$ok" = 1 -a "$SCANLEVEL" != force ] && return

	# Vodafone
	pktws_curl_test_update "$1" "$2" $PAYLOAD --lua-desync=multisplit:blob=fake_default_tls:ip_ttl=5:pos=2:nodrop:repeats=1 && ok=1
	[ "$ok" = 1 -a "$SCANLEVEL" != force ] && return

	# Telekom Mobil
	pktws_curl_test_update "$1" "$2" $PAYLOAD --lua-desync=fake:blob=0x00000000:ip_ttl=5:repeats=1 && ok=1
}
