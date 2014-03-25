<?php

$rtrn = array();
$output = array();
$success = -1;
$failure = -1;

$ssid = escapeshellcmd($_GET['ssid']);
$psk = escapeshellcmd($_GET['psk']);

$success_msg = '<h3>Network Credentials:</h3>'
	.'Network Name: '.$ssid.'<br/>'
	.'Password: '.$psk.'<br/><br/><br/>'
	.'<h4>Connecting to the wireless network... This page may become unresponsive.</h4>';

$cmd = "/home/pi/audio_streaming/write_interfaces '".$ssid."' '".$psk."' 2>&1";
exec($cmd,$rtrn,$success);

if ($success!=0)
{
	echo "failed to execute ".$cmd."<br/>";
	$failure = 0;
	foreach ($rtrn as $line)
	{
		echo $line."<br/>";
	}
}

if ($failure!=0)
{
	echo $success_msg;
}
else
{
	echo "<h3>An error occured. Please try again.</h3>"
		."<h4>It may be necessary to restart the device before running the wifi utility again.</h4>";

}
?>