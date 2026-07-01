<?php
/**
 * database.example.php
 * Template for database configuration — copy this file to
 * config/database.php and fill in your actual credentials.
 * NEVER commit config/database.php to the repository.
 *
 * Part of the WormAtlas CMS
 * wormatlas.org
 */

// How to set this up:
// 1. Copy this file:  cp config/database.example.php config/database.php
// 2. Fill in the values below with real credentials
// 3. config/database.php is listed in .gitignore — it will never be committed

define('DB_HOST', 'your-database-host-here');        // e.g. cpsc-db-01.cropsci.illinois.edu
define('DB_NAME', 'your-database-name-here');        // e.g. wormatlas_dev
define('DB_USER', 'your-database-user-here');        // e.g. worm-readwrite
define('DB_PASS', 'your-database-password-here');    // your actual password
define('DB_CHARSET', 'utf8mb4');
