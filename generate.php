/*
 * Authors: Marcel Breyer, Alexander Van Craen
 * Copyright (C): 2024 Alexander Van Craen, Marcel Breyer, and Dirk Pflüger
 * License: This file is released under the MIT license. See the LICENSE file in the project root for full information.
 */

<?php
$num_particles = intval(htmlspecialchars($_GET["num_particles"]));

function getUserIP() {
    if( array_key_exists('HTTP_X_FORWARDED_FOR', $_SERVER) && !empty($_SERVER['HTTP_X_FORWARDED_FOR']) ) {
        if (strpos($_SERVER['HTTP_X_FORWARDED_FOR'], ',')>0) {
            $addr = explode(",",$_SERVER['HTTP_X_FORWARDED_FOR']);
            return trim($addr[0]);
        } else {
            return $_SERVER['HTTP_X_FORWARDED_FOR'];
        }
    }
    else {
        return $_SERVER['REMOTE_ADDR'];
    }
}

$ip = getUserIP();

if (is_int($num_particles) && $num_particles > 1 && $num_particles < 200001) {
    // log same basic information
    file_put_contents('log.txt', date("Y/m/d H:i:s") . ": " . $_SERVER['PHP_AUTH_USER'] . " (" . $ip .") " . $num_particles . "\n", FILE_APPEND | LOCK_EX);

	system('python3 generate_data.py --output ' . $num_particles . '.csv --num_particles ' . $num_particles);
} else {
    // log error information
    file_put_contents('log.txt', date("Y/m/d H:i:s") . ": " . $_SERVER['PHP_AUTH_USER']  . " (" . $ip .") " . " invalid request\n", FILE_APPEND | LOCK_EX);
    exit(1);
}

?>
