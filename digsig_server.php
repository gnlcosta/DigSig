<?php
// this is only an example... 

date_default_timezone_set("UTC"); 
$id = time();
$id = $id.'-list';
$start_time = array(10, 30, 60);

// $output = print_r($_GET, true);
// file_put_contents('/tmp/get.txt', $output);
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
?>


<adv>
    <id><?php echo $id;?></id>
    <elem>
	    <id>1</id>
	    <type>img</type>
        <url>http://xplico.net/DigSig/Up%20and%20Down%20redux.jpg</url>
        <start><?php echo time()+$start_time[0];?></start>
    </elem>
    <elem>
	    <id>2</id>
	    <type>video</type>
        <url>http://www.quirksmode.org/html5/videos/big_buck_bunny.mp4</url>
        <start><?php echo time()+$start_time[1];?></start>
    </elem>
    <elem>
	    <id>3</id>
	    <type>video</type>
        <url>https://download.blender.org/durian/trailer/sintel_trailer-480p.mp4</url>
        <start><?php echo time()+$start_time[2];?></start>
    </elem>
    <next_req><?php echo $start_time[2];?></next_req>
</adv>
