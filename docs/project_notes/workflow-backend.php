<?php
/**
 * ChrisCrocker.Solutions - Workflow Manager Backend
 */
 
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');
 
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit(0);
}
 
// Database credentials
define('DB_HOST', 'cpsc-db-01.cropsci.illinois.edu');
define('DB_NAME', 'wormatlas_workflow_dev');
define('DB_USER', 'worm-readwrite');
define('DB_PASS', '2n3ME0W5U5wR'); // ← CHANGE THIS to your actual password
 
function getDB() {
    try {
        $pdo = new PDO(
            "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4",
            DB_USER,
            DB_PASS,
            [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
            ]
        );
        return $pdo;
    } catch (PDOException $e) {
        error_log("DB connection failed: " . $e->getMessage());
        return null;
    }
}
 
function loadData() {
    $pdo = getDB();
    if (!$pdo) {
        return ['success' => false, 'error' => 'Database connection failed'];
    }
    
    try {
        $stmt = $pdo->query("SELECT data FROM project_data WHERE id = 1");
        $row = $stmt->fetch();
        
        if ($row) {
            $data = json_decode($row['data'], true);
            if (!$data) {
                $data = ['team' => [], 'phases' => [], 'activity' => [], 'fileLinks' => []];
            }
            return ['success' => true, 'data' => $data];
        } else {
            return ['success' => false, 'error' => 'No data found'];
        }
    } catch (PDOException $e) {
        error_log("DB read error: " . $e->getMessage());
        return ['success' => false, 'error' => 'Database read failed'];
    }
}
 
function saveData($data) {
    $pdo = getDB();
    if (!$pdo) {
        return ['success' => false, 'error' => 'Database connection failed'];
    }
    
    try {
        $jsonData = json_encode($data);
        if ($jsonData === false) {
            return ['success' => false, 'error' => 'Invalid data format'];
        }
        
        $stmt = $pdo->prepare("
            UPDATE project_data 
            SET data = :data, updated_at = NOW() 
            WHERE id = 1
        ");
        
        $stmt->execute(['data' => $jsonData]);
        return ['success' => true];
        
    } catch (PDOException $e) {
        error_log("DB write error: " . $e->getMessage());
        return ['success' => false, 'error' => 'Database write failed'];
    }
}
 
$method = $_SERVER['REQUEST_METHOD'];
 
if ($method === 'GET') {
    echo json_encode(loadData());
} elseif ($method === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    if ($input && $input['action'] === 'save' && isset($input['data'])) {
        echo json_encode(saveData($input['data']));
    } else {
        echo json_encode(['success' => false, 'error' => 'Invalid request']);
    }
} else {
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
}
?>